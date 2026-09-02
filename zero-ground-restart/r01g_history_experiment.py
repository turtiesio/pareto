#!/usr/bin/env python3
"""Deterministic falsification experiment for the frozen H11 seed.

This program is a finite oracle/checker, never a storage architecture.  Its L
and S routines are logical encodings in one source file and deliberately do not
claim the independent-build evidence required by the seed.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Optional, Sequence


SEED_PATH = "/root/pareto/zero-ground-restart/HISTORY-SEED-R01G.md"
EXPECTED_SEED_SHA256 = (
    "9fcf79f7544e3fe7d11f0830e224635758921f199e4478bb4180ada991629008"
)

M = (
    b"\x00",
    b"\x01",
    b"\x10",
    b"\x11",
    b"\x20",
    b"\x30",
    b"\x40",
    b"\x50",
    b"\x60",
    b"\xfe",
    b"\x30\x00",
)
MESSAGE_NAME = {
    b"\x00": "observe_zero",
    b"\x01": "observe_one",
    b"\x10": "author_I",
    b"\x11": "author_N",
    b"\x20": "retire",
    b"\x30": "query",
    b"\x40": "action",
    b"\x50": "evolve",
    b"\x60": "identity",
    b"\xfe": "unknown",
    b"\x30\x00": "malformed_query",
}
MUTATOR_OPCODES = frozenset((b"\x00", b"\x01", b"\x10", b"\x11", b"\x20", b"\x50"))
REJECTION_CODES = (b"\xe0\x01", b"\xe0\x02", b"\xe0\x03", b"\xe0\x04", b"\xe0\x05", b"\xe0\x06")
D0 = b"\x00\x40\xa0"
D1 = b"\x01\x40\xa1"

assert len(M) == 11 and len(set(M)) == 11 and all(M)
assert M[-1] == b"\x30\x00" and M[5] == b"\x30"
assert D0 == bytes.fromhex("00 40 a0")
assert D1 == bytes.fromhex("01 40 a1")
assert b"\x86\x03" + D0 == bytes.fromhex("86 03 00 40 a0")
assert b"\x86\x03" + D1 == bytes.fromhex("86 03 01 40 a1")


@dataclass(frozen=True, order=True)
class State:
    revision: int = 0
    table: int = 0  # 0 absent, 1 I, 2 N
    observation: int = 0  # 0 absent, 1 bit zero, 2 bit one


@dataclass(frozen=True)
class Step:
    state: State
    outputs: tuple[tuple[str, bytes], ...]
    successful_mutator: bool
    semantic_change: bool


@dataclass(frozen=True)
class CrashOutcome:
    directive: str
    outputs: tuple[tuple[str, bytes], ...]
    state: State


def packed_class(state: State) -> int:
    return 9 * state.revision + 3 * state.table + state.observation


def state_from_class(value: int) -> State:
    if not 0 <= value <= 17:
        raise ValueError("packed H11 class is outside 00..11 hexadecimal")
    revision, remainder = divmod(value, 9)
    table, observation = divmod(remainder, 3)
    return State(revision, table, observation)


ALL_STATES = tuple(State(r, t, o) for r in range(2) for t in range(3) for o in range(3))
assert tuple(packed_class(state) for state in ALL_STATES) == tuple(range(18))
assert all(state_from_class(packed_class(state)) == state for state in ALL_STATES)


def table_result(state: State) -> int:
    if state.table == 0:
        raise ValueError("no active table")
    if state.observation == 0:
        raise ValueError("no observation")
    bit = state.observation - 1
    return bit if state.table == 1 else 1 - bit


def identity_bytes(state: State) -> bytes:
    descriptor = D1 if state.revision else D0
    return b"\x86\x03" + descriptor


def oracle_step(state: State, message: bytes) -> Step:
    if message not in MESSAGE_NAME:
        raise ValueError("message is outside the exact eleven-message alphabet")
    if message == b"\x00":
        next_state = State(state.revision, state.table, 1)
        return Step(next_state, (("R", b"\x80\x00"),), True, next_state != state)
    if message == b"\x01":
        next_state = State(state.revision, state.table, 2)
        return Step(next_state, (("R", b"\x80\x01"),), True, next_state != state)
    if message == b"\x10":
        next_state = State(state.revision, 1, state.observation)
        return Step(next_state, (("R", b"\x81\x10"),), True, next_state != state)
    if message == b"\x11":
        next_state = State(state.revision, 2, state.observation)
        return Step(next_state, (("R", b"\x81\x11"),), True, next_state != state)
    if message == b"\x20":
        if state.table == 0:
            return Step(state, (("R", b"\xe0\x05"),), False, False)
        next_state = State(state.revision, 0, state.observation)
        return Step(next_state, (("R", b"\x82"),), True, True)
    if message == b"\x30":
        if state.table == 0:
            return Step(state, (("R", b"\xe0\x03"),), False, False)
        if state.observation == 0:
            return Step(state, (("R", b"\xe0\x04"),), False, False)
        return Step(state, (("R", bytes((0x83, table_result(state)))),), False, False)
    if message == b"\x40":
        if state.table == 0:
            return Step(state, (("R", b"\xe0\x03"),), False, False)
        if state.observation == 0:
            return Step(state, (("R", b"\xe0\x04"),), False, False)
        prefix = 0xA1 if state.revision else 0xA0
        return Step(
            state,
            (("D", bytes((prefix, table_result(state)))), ("R", b"\x84")),
            False,
            False,
        )
    if message == b"\x50":
        if state.revision == 1:
            return Step(state, (("R", b"\xe0\x06"),), False, False)
        next_state = State(1, state.table, state.observation)
        return Step(next_state, (("R", b"\x85\x01"),), True, True)
    if message == b"\x60":
        return Step(state, (("R", identity_bytes(state)),), False, False)
    if message == b"\xfe":
        return Step(state, (("R", b"\xe0\x01"),), False, False)
    assert message == b"\x30\x00"
    return Step(state, (("R", b"\xe0\x02"),), False, False)


def full_crossings(state: State, message: bytes) -> tuple[tuple[str, bytes], ...]:
    return (("C", message),) + oracle_step(state, message).outputs


def fold_word(word: Sequence[bytes], initial: State = State()) -> State:
    state = initial
    for message in word:
        state = oracle_step(state, message).state
    return state


@lru_cache(maxsize=None)
def cached_fold(word: tuple[bytes, ...]) -> State:
    return fold_word(word)


def project_word(state: State, word: Sequence[bytes]) -> tuple[tuple[str, bytes], ...]:
    outputs: list[tuple[str, bytes]] = []
    for message in word:
        step = oracle_step(state, message)
        outputs.extend(step.outputs)
        state = step.state
    return tuple(outputs)


def words_through(depth: int) -> tuple[tuple[bytes, ...], ...]:
    return tuple(
        word
        for length in range(depth + 1)
        for word in itertools.product(M, repeat=length)
    )


CUT_HISTORIES = words_through(2)
FUTURE_WORDS = words_through(3)
assert len(CUT_HISTORIES) == 133
assert len(FUTURE_WORDS) == 1464


def json_crossings(crossings: Iterable[tuple[str, bytes]]) -> list[dict[str, str]]:
    return [{"channel": channel, "bytes_hex": raw.hex()} for channel, raw in crossings]


def history_hex(word: Sequence[bytes]) -> list[str]:
    return [message.hex() for message in word]


def canonical_word(state: State) -> tuple[bytes, ...]:
    result: list[bytes] = []
    if state.revision:
        result.append(b"\x50")
    if state.table == 1:
        result.append(b"\x10")
    elif state.table == 2:
        result.append(b"\x11")
    if state.observation == 1:
        result.append(b"\x00")
    elif state.observation == 2:
        result.append(b"\x01")
    return tuple(result)


def canonical_encoding(state: State) -> bytes:
    word = canonical_word(state)
    return bytes((len(word),)) + b"".join(word) + b"\xff" * (3 - len(word))


def decode_canonical(raw: bytes) -> State:
    if len(raw) != 4 or raw[0] > 3:
        raise ValueError("canonical representative encoding must be four bytes")
    length = raw[0]
    body = raw[1 : 1 + length]
    padding = raw[1 + length :]
    if padding != b"\xff" * (3 - length):
        raise ValueError("noncanonical representative padding")
    word = tuple(bytes((value,)) for value in body)
    if any(message not in MUTATOR_OPCODES for message in word):
        raise ValueError("noncanonical representative opcode")
    state = fold_word(word)
    if canonical_encoding(state) != raw:
        raise ValueError("word is not the unique canonical representative")
    return state


def probe_signature(state: State) -> bytes:
    table = (0x02, 0x00, 0x01)[state.table]
    observation = (0x02, 0x00, 0x01)[state.observation]
    return bytes((state.revision, table, observation))


def decode_probe(raw: bytes) -> State:
    if len(raw) != 3 or raw[0] not in (0, 1):
        raise ValueError("invalid probe signature")
    reverse = {0x02: 0, 0x00: 1, 0x01: 2}
    if raw[1] not in reverse or raw[2] not in reverse:
        raise ValueError("invalid probe signature")
    return State(raw[0], reverse[raw[1]], reverse[raw[2]])


def encode_L(word: Sequence[bytes]) -> bytes:
    state = State()
    log: list[int] = []
    for message in word:
        step = oracle_step(state, message)
        if step.successful_mutator:
            if len(message) != 1 or message not in MUTATOR_OPCODES:
                raise AssertionError("successful mutator is not an L opcode")
            log.append(message[0])
        state = step.state
    if len(log) > 5:
        raise ValueError("L capacity exceeded")
    return bytes(log) + b"\xff" * (5 - len(log))


def decode_L(image: bytes) -> State:
    if len(image) != 5:
        raise ValueError("L image must have five cells")
    prefix: list[bytes] = []
    saw_ff = False
    for value in image:
        if value == 0xFF:
            saw_ff = True
            continue
        if saw_ff or bytes((value,)) not in MUTATOR_OPCODES:
            raise ValueError("invalid L prefix/opcode")
        prefix.append(bytes((value,)))
    state = State()
    for message in prefix:
        step = oracle_step(state, message)
        if not step.successful_mutator:
            raise ValueError("replay-invalid L sequence")
        state = step.state
    return state


def encode_S(word: Sequence[bytes]) -> bytes:
    return bytes((packed_class(fold_word(word)),))


def decode_S(image: bytes) -> State:
    if len(image) != 1:
        raise ValueError("S image must be one byte")
    return state_from_class(image[0])


def append_L(image: bytes, message: bytes) -> bytes:
    if message not in MUTATOR_OPCODES or len(message) != 1:
        raise ValueError("not an L mutator")
    try:
        index = image.index(0xFF)
    except ValueError as error:
        raise ValueError("L capacity exceeded") from error
    return image[:index] + message + image[index + 1 :]


def run_L(word: Sequence[bytes]) -> tuple[State, bytes, tuple[tuple[str, bytes], ...]]:
    image = b"\xff" * 5
    outputs: list[tuple[str, bytes]] = []
    for message in word:
        state = decode_L(image)
        step = oracle_step(state, message)
        outputs.extend(step.outputs)
        if step.successful_mutator:
            image = append_L(image, message)
    return decode_L(image), image, tuple(outputs)


def run_S(word: Sequence[bytes]) -> tuple[State, bytes, tuple[tuple[str, bytes], ...]]:
    image = b"\x00"
    outputs: list[tuple[str, bytes]] = []
    for message in word:
        state = decode_S(image)
        step = oracle_step(state, message)
        outputs.extend(step.outputs)
        if step.semantic_change:
            image = bytes((packed_class(step.state),))
    return decode_S(image), image, tuple(outputs)


RESTART_OUTPUT = (("R", b"\x88"),)


def crash_variants(state: State, message: bytes) -> tuple[CrashOutcome, ...]:
    """Only exact crash clauses whose public order is uniquely stated."""
    step = oracle_step(state, message)
    variants: list[CrashOutcome] = []
    if step.successful_mutator:
        variants.append(CrashOutcome("byte-old", RESTART_OUTPUT, state))
        variants.append(CrashOutcome("byte-new", RESTART_OUTPUT, step.state))
        variants.append(
            CrashOutcome("after-reply", step.outputs + RESTART_OUTPUT, step.state)
        )
    elif message == b"\x40" and step.outputs and step.outputs[0][0] == "D":
        delivery = (step.outputs[0],)
        variants.append(CrashOutcome("before-D", RESTART_OUTPUT, state))
        variants.append(CrashOutcome("after-D", delivery + RESTART_OUTPUT, state))
        variants.append(
            CrashOutcome("after-R", step.outputs + RESTART_OUTPUT, state)
        )
    else:
        variants.append(CrashOutcome("before-reply", RESTART_OUTPUT, state))
        variants.append(CrashOutcome("after-reply", step.outputs + RESTART_OUTPUT, state))
    # Collapse duplicate exact behavior but retain the first directive in the
    # seed's order (boundary, old, new is separately reported as ambiguous for
    # multiple boundary gaps).
    unique: dict[tuple[Any, ...], CrashOutcome] = {}
    for variant in variants:
        unique.setdefault((variant.outputs, variant.state), variant)
    return tuple(unique.values())


def full_crash_trace(message: bytes, outcome: CrashOutcome) -> tuple[tuple[str, bytes], ...]:
    if not outcome.outputs or outcome.outputs[-1] != ("R", b"\x88"):
        raise ValueError("crash outcome lacks completed restart reply")
    before_restart = outcome.outputs[:-1]
    return (
        (("C", message),)
        + before_restart
        + (("K", b"CRASH"), ("K", b"RESTART"), ("R", b"\x88"))
    )


def residual_partition_ids(max_depth: int = 3) -> dict[tuple[int, bool], dict[State, int]]:
    """Bottom-up exact alternating residual structures with one optional crash."""
    result: dict[tuple[int, bool], dict[State, int]] = {}

    def intern(signatures: dict[State, tuple[Any, ...]]) -> dict[State, int]:
        unique = sorted(set(signatures.values()), key=repr)
        ids = {signature: index for index, signature in enumerate(unique)}
        return {state: ids[signature] for state, signature in signatures.items()}

    base_false = {state: ("STOP",) for state in ALL_STATES}
    result[(0, False)] = intern(base_false)
    base_true = {
        state: (
            "STOP",
            ("crash-gap", RESTART_OUTPUT, result[(0, False)][state]),
        )
        for state in ALL_STATES
    }
    result[(0, True)] = intern(base_true)

    for depth in range(1, max_depth + 1):
        false_signatures: dict[State, tuple[Any, ...]] = {}
        for state in ALL_STATES:
            branches = []
            for message in M:
                step = oracle_step(state, message)
                branches.append(
                    (
                        message,
                        (("no-crash", step.outputs, result[(depth - 1, False)][step.state]),),
                    )
                )
            false_signatures[state] = ("STOP", tuple(branches))
        result[(depth, False)] = intern(false_signatures)

        true_signatures: dict[State, tuple[Any, ...]] = {}
        for state in ALL_STATES:
            branches = []
            for message in M:
                step = oracle_step(state, message)
                choices: list[tuple[Any, ...]] = [
                    (
                        "no-crash",
                        step.outputs,
                        result[(depth - 1, True)][step.state],
                    )
                ]
                for crash in crash_variants(state, message):
                    choices.append(
                        (
                            crash.directive,
                            crash.outputs,
                            result[(depth - 1, False)][crash.state],
                        )
                    )
                branches.append((message, tuple(choices)))
            true_signatures[state] = (
                "STOP",
                ("crash-gap", RESTART_OUTPUT, result[(depth, False)][state]),
                tuple(branches),
            )
        result[(depth, True)] = intern(true_signatures)
    return result


def first_difference(
    left: Sequence[tuple[str, bytes]], right: Sequence[tuple[str, bytes]]
) -> dict[str, Any]:
    for index in range(max(len(left), len(right))):
        left_value = left[index] if index < len(left) else None
        right_value = right[index] if index < len(right) else None
        if left_value != right_value:
            return {
                "index": index,
                "left": None
                if left_value is None
                else {"channel": left_value[0], "bytes_hex": left_value[1].hex()},
                "right": None
                if right_value is None
                else {"channel": right_value[0], "bytes_hex": right_value[1].hex()},
            }
    raise ValueError("projections are equal")


@lru_cache(maxsize=None)
def shortest_state_witness(left: State, right: State) -> tuple[tuple[bytes, ...], dict[str, Any]]:
    if left == right:
        raise ValueError("equal states have no separating future")
    for length in range(1, 4):
        for word in itertools.product(M, repeat=length):
            left_projection = project_word(left, word)
            right_projection = project_word(right, word)
            if left_projection != right_projection:
                return word, first_difference(left_projection, right_projection)
    raise AssertionError("depth-three future failed to separate unequal H11 classes")


class Findings:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(self, identifier: str, status: str, summary: str, **evidence: Any) -> None:
        if status not in ("PASS", "FAIL", "UNKNOWN"):
            raise ValueError("bad status")
        finding: dict[str, Any] = {"id": identifier, "status": status, "summary": summary}
        if evidence:
            finding["evidence"] = evidence
        self.items.append(finding)

    def test(
        self,
        identifier: str,
        condition: bool,
        pass_summary: str,
        fail_summary: str,
        **evidence: Any,
    ) -> None:
        self.add(
            identifier,
            "PASS" if condition else "FAIL",
            pass_summary if condition else fail_summary,
            **evidence,
        )


def expect_raises(callable_object: Any) -> bool:
    try:
        callable_object()
    except (ValueError, AssertionError):
        return True
    return False


def shortest_history_for_state(state: State, depth: int = 5) -> tuple[bytes, ...]:
    for word in words_through(depth):
        if cached_fold(word) == state:
            return word
    raise AssertionError("state is unreachable within requested horizon")


def class_witness_report(states: Sequence[State]) -> list[dict[str, Any]]:
    report = []
    for left_index, left in enumerate(states):
        for right in states[left_index + 1 :]:
            word, difference = shortest_state_witness(left, right)
            report.append(
                {
                    "left_class": packed_class(left),
                    "right_class": packed_class(right),
                    "future": history_hex(word),
                    "future_length": len(word),
                    "first_difference": difference,
                }
            )
    return report


def field_delete_witness(field: str) -> dict[str, Any]:
    def key(state: State) -> tuple[int, ...]:
        values = {
            "revision": state.revision,
            "table": state.table,
            "observation": state.observation,
        }
        del values[field]
        return tuple(values[name] for name in ("revision", "table", "observation") if name in values)

    for left_index, left in enumerate(ALL_STATES):
        for right in ALL_STATES[left_index + 1 :]:
            if key(left) == key(right):
                future, difference = shortest_state_witness(left, right)
                return {
                    "deleted": field,
                    "left_class": packed_class(left),
                    "right_class": packed_class(right),
                    "future": history_hex(future),
                    "first_difference": difference,
                }
    raise AssertionError("deletion produced no collision")


def logical_LS_checks() -> tuple[bool, dict[str, Any]]:
    checked_scripts = 0
    first_failure: Optional[dict[str, Any]] = None
    for cut in CUT_HISTORIES:
        for future in FUTURE_WORDS:
            word = cut + future
            reference = cached_fold(word)
            reference_outputs = project_word(State(), word)
            try:
                l_state, l_image, l_outputs = run_L(word)
                s_state, s_image, s_outputs = run_S(word)
            except ValueError as error:
                first_failure = {"word": history_hex(word), "error": str(error)}
                return False, {"checked_scripts": checked_scripts, "first_failure": first_failure}
            checked_scripts += 1
            if (
                l_state != reference
                or s_state != reference
                or l_outputs != reference_outputs
                or s_outputs != reference_outputs
            ):
                first_failure = {
                    "word": history_hex(word),
                    "reference": repr(reference),
                    "L": repr(l_state),
                    "S": repr(s_state),
                    "reference_outputs": json_crossings(reference_outputs),
                    "L_outputs": json_crossings(l_outputs),
                    "S_outputs": json_crossings(s_outputs),
                    "L_image": l_image.hex(),
                    "S_image": s_image.hex(),
                }
                return False, {"checked_scripts": checked_scripts, "first_failure": first_failure}

    crash_cases = 0
    prefixes = words_through(4)
    for prefix in prefixes:
        state = cached_fold(prefix)
        l_old = encode_L(prefix)
        s_old = encode_S(prefix)
        for message in M:
            step = oracle_step(state, message)
            if not step.successful_mutator:
                continue
            l_new = append_L(l_old, message)
            l_states = {decode_L(l_old), decode_L(l_new)}
            if step.semantic_change:
                s_new = bytes((packed_class(step.state),))
                s_states = {decode_S(s_old), decode_S(s_new)}
            else:
                s_states = {decode_S(s_old)}
            reference_states = {state, step.state}
            crash_cases += 1
            if l_states != reference_states or s_states != reference_states:
                return False, {
                    "checked_scripts": checked_scripts,
                    "crash_cases": crash_cases,
                    "first_failure": {
                        "prefix": history_hex(prefix),
                        "message": message.hex(),
                        "reference": sorted(map(repr, reference_states)),
                        "L": sorted(map(repr, l_states)),
                        "S": sorted(map(repr, s_states)),
                    },
                }
    return True, {
        "checked_scripts": checked_scripts,
        "crash_cases": crash_cases,
        "first_failure": first_failure,
        "scope": "two logical encoders/decoders in one source; not independent builds",
    }


def run_checks(seed_sha256: str) -> dict[str, Any]:
    findings = Findings()
    findings.test(
        "FROZEN_SHA256",
        seed_sha256 == EXPECTED_SEED_SHA256,
        "Frozen H11 SHA-256 matches.",
        "Frozen H11 SHA-256 mismatch; semantic execution is unauthorized.",
        actual=seed_sha256,
        expected=EXPECTED_SEED_SHA256,
    )

    anchor_ok = (
        full_crossings(State(), b"\x00") == (("C", b"\x00"), ("R", b"\x80\x00"))
        and full_crossings(State(), b"\x01") == (("C", b"\x01"), ("R", b"\x80\x01"))
        and full_crossings(State(), b"\x10") == (("C", b"\x10"), ("R", b"\x81\x10"))
        and full_crossings(State(), b"\x11") == (("C", b"\x11"), ("R", b"\x81\x11"))
        and full_crossings(State(table=1), b"\x20") == (("C", b"\x20"), ("R", b"\x82"))
        and full_crossings(State(), b"\xfe") == (("C", b"\xfe"), ("R", b"\xe0\x01"))
        and full_crossings(State(), b"\x30\x00") == (("C", b"\x30\x00"), ("R", b"\xe0\x02"))
        and full_crossings(State(), b"\x60")[-1] == ("R", bytes.fromhex("86 03 00 40 a0"))
        and full_crossings(State(revision=1), b"\x60")[-1]
        == ("R", bytes.fromhex("86 03 01 40 a1"))
    )
    findings.test(
        "FAULT_FREE_EXACT_BYTES",
        anchor_ok,
        "Exact fault-free request/reply bytes and both identity descriptors match.",
        "A fault-free anchor byte sequence differs from Section 2.",
    )
    fault_free_vectors = [
        {
            "class": packed_class(state),
            "message_hex": message.hex(),
            "next_class": packed_class(oracle_step(state, message).state),
            "outputs": json_crossings(oracle_step(state, message).outputs),
            "successful_mutator": oracle_step(state, message).successful_mutator,
        }
        for state in ALL_STATES
        for message in M
    ]
    fault_free_vector_bytes = json.dumps(
        fault_free_vectors, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    findings.test(
        "FAULT_FREE_TOTAL_ORACLE_198",
        len(fault_free_vectors) == 18 * 11,
        "The complete fault-free oracle contains one deterministic transition for each of 18 classes by 11 messages.",
        "The total fault-free oracle is incomplete.",
        vector_count=len(fault_free_vectors),
        vectors_sha256=hashlib.sha256(fault_free_vector_bytes).hexdigest(),
    )

    rejection_actual = {
        "unknown": oracle_step(State(), b"\xfe").outputs,
        "malformed": oracle_step(State(), b"\x30\x00").outputs,
        "no_interpreter_query": oracle_step(State(), b"\x30").outputs,
        "no_observation_query": oracle_step(State(table=1), b"\x30").outputs,
        "retire_none": oracle_step(State(), b"\x20").outputs,
        "evolve_final": oracle_step(State(revision=1), b"\x50").outputs,
    }
    rejection_ok = tuple(value[0][1] for value in rejection_actual.values()) == REJECTION_CODES
    findings.test(
        "SIX_REJECTION_BYTES_AND_PRECEDENCE",
        rejection_ok,
        "All six exact rejection codes are reachable with the declared precedence.",
        "A rejection code or validation precedence differs.",
        cases={name: json_crossings(value) for name, value in rejection_actual.items()},
    )

    i0 = State(table=1, observation=1)
    i1 = State(table=1, observation=2)
    n0 = State(table=2, observation=1)
    n1 = State(table=2, observation=2)
    tables_ok = [table_result(state) for state in (i0, i1, n0, n1)] == [0, 1, 1, 0]
    action_ok = (
        oracle_step(i0, b"\x40").outputs == (("D", b"\xa0\x00"), ("R", b"\x84"))
        and oracle_step(State(1, 1, 1), b"\x40").outputs
        == (("D", b"\xa1\x00"), ("R", b"\x84"))
    )
    findings.test(
        "TABLE_QUERY_ACTION_ORACLE",
        tables_ok and action_ok,
        "I/N tables, query results, and revision-specific D-before-R action order are exact.",
        "A table cell, query result, or action crossing is wrong.",
    )

    stop_suite = (
        (("C_DOWN", b""), ("R", b"\x87")),
        full_crossings(State(), b"\xfe"),
        full_crossings(State(), b"\x30\x00"),
        full_crossings(State(), b"\x30") + full_crossings(State(), b"\x00"),
    )
    stop_bytes_ok = stop_suite[3] == (
        ("C", b"\x30"),
        ("R", b"\xe0\x03"),
        ("C", b"\x00"),
        ("R", b"\x80\x00"),
    )
    findings.test(
        "STOP_FRAMING_ANCHOR_BYTES",
        stop_bytes_ok,
        "The four displayed STOP/framing histories have their exact crossings.",
        "A STOP/framing anchor differs.",
        histories=[json_crossings(history) for history in stop_suite],
    )
    findings.add(
        "CONTRADICTION_STOP_SUITE_EMPTY_DESCRIPTION",
        "FAIL",
        "Section 3 says the four displayed histories include an empty submission, but they are C_DOWN, one-byte fe, one two-byte 3000 message, and two one-byte messages. Section 2 explicitly says an empty datagram is unsupported and is not C_DOWN.",
        displayed_client_forms=["C_DOWN", "fe", "3000", "30_then_00"],
    )

    cut_states = [cached_fold(history) for history in CUT_HISTORIES]
    class_counter = Counter(packed_class(state) for state in cut_states)
    actual_table = dict(sorted(class_counter.items()))
    expected_table = {
        0: 45,
        1: 15,
        2: 15,
        3: 14,
        4: 2,
        5: 2,
        6: 14,
        7: 2,
        8: 2,
        9: 14,
        10: 2,
        11: 2,
        12: 2,
        15: 2,
    }
    findings.test(
        "CUT_TABLE_133_AND_14_CLASSES",
        len(CUT_HISTORIES) == 133 and actual_table == expected_table,
        "All 133 cut histories reproduce the fourteen-row Section 5.1 table.",
        "The enumerated cut table differs from Section 5.1.",
        actual=actual_table,
    )

    stated_multiset = sorted([45, 15, 15, 14, 14, 14, 14] + [2] * 7, reverse=True)
    actual_multiset = sorted(class_counter.values(), reverse=True)
    findings.test(
        "SECTION11_CLASS_SIZE_MULTISET",
        actual_multiset == stated_multiset,
        "The Section 11 class-size multiset matches the enumerated table.",
        "Section 11 lists four size-14 and seven size-2 classes, summing to 145; the exact table has three size-14 and eight size-2 classes, summing to 133.",
        stated=stated_multiset,
        stated_sum=sum(stated_multiset),
        actual=actual_multiset,
        actual_sum=sum(actual_multiset),
    )

    reachable_five = {cached_fold(word) for word in words_through(5)}
    shortest_representatives: dict[State, tuple[bytes, ...]] = {}
    for word in words_through(3):
        shortest_representatives.setdefault(cached_fold(word), word)
    assert set(shortest_representatives) == set(ALL_STATES)
    findings.test(
        "FULL_HORIZON_18_CLASSES",
        reachable_five == set(ALL_STATES),
        "All eighteen quotient states are reachable within five messages.",
        "The five-message horizon does not reach exactly eighteen states.",
        count=len(reachable_five),
    )

    residual_ids = residual_partition_ids(3)
    full_residual_count = len(set(residual_ids[(3, True)].values()))
    cut_residual_count = len(
        {residual_ids[(3, True)][state] for state in set(cut_states)}
    )
    findings.test(
        "DEPTH3_COMMON_FUTURE_PARTITION",
        full_residual_count == 18 and cut_residual_count == 14,
        "Exact depth-three residual structures yield eighteen full and fourteen cut classes, including one optional crash.",
        "The depth-three common-future partition count differs.",
        full=full_residual_count,
        cut=cut_residual_count,
    )

    full_witnesses = class_witness_report(ALL_STATES)
    max_future = max(item["future_length"] for item in full_witnesses)
    cut_classes = tuple(state_from_class(value) for value in sorted(class_counter))
    cut_witnesses = class_witness_report(cut_classes)
    findings.test(
        "ALL_CLASS_MERGES_AND_SHORTEST_WITNESSES",
        len(full_witnesses) == 153
        and len(cut_witnesses) == 91
        and max_future == 2,
        "All 153 full and 91 cut class merges have lexicographically first no-crash witnesses of length at most two.",
        "A class merge lacks a depth-three witness or exceeds the stated two-message maximum.",
        full_pairs=len(full_witnesses),
        cut_pairs=len(cut_witnesses),
        maximum_future=max_future,
    )

    history_pairs = 0
    equivalent_history_pairs = 0
    separated_history_pairs = 0
    for left_index, left_history in enumerate(CUT_HISTORIES):
        left_state = cut_states[left_index]
        for right_index in range(left_index + 1, len(CUT_HISTORIES)):
            right_state = cut_states[right_index]
            history_pairs += 1
            if left_state == right_state:
                equivalent_history_pairs += 1
            else:
                future, _ = shortest_state_witness(left_state, right_state)
                if project_word(left_state, future) != project_word(right_state, future):
                    separated_history_pairs += 1
    findings.test(
        "ALL_133_HISTORY_PAIRS",
        history_pairs == 133 * 132 // 2
        and equivalent_history_pairs + separated_history_pairs == history_pairs,
        "Every unordered pair of the 133 cuts is assigned to one state class or has its cached shortest common future.",
        "A cut-history pair was neither merged nor separated.",
        total_pairs=history_pairs,
        equivalent_pairs=equivalent_history_pairs,
        separated_pairs=separated_history_pairs,
    )

    revision_pair = (State(), State(revision=1))
    table_pair = (State(), State(table=1))
    revision_first = shortest_state_witness(*revision_pair)[0]
    table_first = shortest_state_witness(*table_pair)[0]
    claimed_revision = (b"\x60",)
    claimed_table = (b"\x30",)
    findings.test(
        "SECTION5_SHORTEST_TIE_BREAKS",
        revision_first == claimed_revision and table_first == claimed_table,
        "The displayed revision and interpreter-presence witnesses are first under the declared message ordering.",
        "The displayed witnesses are length-minimal but not first under the declared tie-break: 50 precedes 60 for revision, and 20 precedes 30 for absent versus I.",
        actual_revision=history_hex(revision_first),
        displayed_revision=history_hex(claimed_revision),
        actual_interpreter=history_hex(table_first),
        displayed_interpreter=history_hex(claimed_table),
    )

    encodings = {
        "packed": {bytes((packed_class(state),)) for state in ALL_STATES},
        "canonical": {canonical_encoding(state) for state in ALL_STATES},
        "probe": {probe_signature(state) for state in ALL_STATES},
    }
    encoding_ok = (
        all(len(values) == 18 for values in encodings.values())
        and all(state_from_class(packed_class(state)) == state for state in ALL_STATES)
        and all(decode_canonical(canonical_encoding(state)) == state for state in ALL_STATES)
        and all(decode_probe(probe_signature(state)) == state for state in ALL_STATES)
    )
    findings.test(
        "THREE_ENCODINGS_INJECTIVE",
        encoding_ok,
        "Packed byte, padded canonical word, and probe signature are injective over all eighteen classes.",
        "A proposed quotient encoding collides or fails round-trip.",
        encodings={name: sorted(value.hex() for value in values) for name, values in encodings.items()},
    )

    delete_witnesses = [
        field_delete_witness("revision"),
        field_delete_witness("table"),
        field_delete_witness("observation"),
    ]
    findings.test(
        "DELETE_SURVIVING_RESPONSIBILITIES",
        all(witness["future"] for witness in delete_witnesses),
        "Deleting revision, table, or observation creates a witnessed merge.",
        "A claimed surviving responsibility was deletable.",
        witnesses=delete_witnesses,
    )

    no_cache_fields = tuple(State.__dataclass_fields__) == ("revision", "table", "observation")
    derivation_ok = all(
        identity_bytes(state) == b"\x86\x03" + (D1 if state.revision else D0)
        and fold_word(canonical_word(state)) == state
        and state_from_class(packed_class(state)) == state
        for state in ALL_STATES
    )
    findings.test(
        "DERIVE_OUTPUTS_AND_NO_CACHES",
        no_cache_fields and derivation_ok,
        "Identity, representatives, probes, and outputs derive from the three responsibilities; no explanation/latest-response cache exists.",
        "A derived value required an extra saved field.",
    )

    handler_pairs = 0
    indistinguishable_handlers: list[list[str]] = []
    for left_index, left in enumerate(M):
        for right in M[left_index + 1 :]:
            handler_pairs += 1
            separated = any(
                (
                    oracle_step(state, left).outputs,
                    oracle_step(state, left).state,
                )
                != (
                    oracle_step(state, right).outputs,
                    oracle_step(state, right).state,
                )
                for state in ALL_STATES
            )
            if not separated:
                indistinguishable_handlers.append([left.hex(), right.hex()])
    findings.test(
        "MERGE_INPUT_HANDLERS_AND_REJECTIONS",
        handler_pairs == 55
        and not indistinguishable_handlers
        and len(set(REJECTION_CODES)) == 6,
        "All 55 input-handler and 15 rejection-code merges lose an exact behavior distinction.",
        "At least one required handler/rejection merge was not separated.",
        handler_pairs=handler_pairs,
        rejection_pairs=15,
        indistinguishable=indistinguishable_handlers,
    )

    inflight_witnesses = []
    for state in ALL_STATES:
        for message in MUTATOR_OPCODES:
            step = oracle_step(state, message)
            if step.successful_mutator and step.state != state:
                future, difference = shortest_state_witness(state, step.state)
                inflight_witnesses.append(
                    {
                        "old": packed_class(state),
                        "new": packed_class(step.state),
                        "message": message.hex(),
                        "future": history_hex(future),
                        "first_difference": difference,
                    }
                )
    findings.test(
        "MERGE_INFLIGHT_OLD_NEW",
        bool(inflight_witnesses) and all(item["future"] for item in inflight_witnesses),
        "Every distinct old/new mutator recovery pair has a shortest future witness.",
        "An old/new recovery distinction merged without a witness.",
        pairs=len(inflight_witnesses),
    )

    exact_history_classes = len(set(CUT_HISTORIES))
    negative_left: tuple[bytes, ...] = ()
    negative_right = (b"\x30",)
    same_reduction = cached_fold(negative_left) == cached_fold(negative_right)
    characteristic_outputs = (
        int(negative_left == negative_left),
        int(negative_right == negative_left),
    )
    findings.test(
        "EXACT_HISTORY_NEGATIVE_CONTROL",
        exact_history_classes == 133
        and same_reduction
        and characteristic_outputs == (1, 0),
        "An unrestricted characteristic interpreter restores the identity quotient over all 133 exact cut histories.",
        "The exact-history negative control failed.",
        collision_under_H11=[history_hex(negative_left), history_hex(negative_right)],
        characteristic_results=list(characteristic_outputs),
        identity_classes=exact_history_classes,
    )

    ls_ok, ls_stats = logical_LS_checks()
    findings.test(
        "LOGICAL_L_S_ENCODINGS",
        ls_ok,
        "Logical L replay and S packed recovery match the oracle over every split script and every local mutator old/new outcome.",
        "A logical L/S encoding disagrees with the history oracle.",
        **ls_stats,
    )
    findings.add(
        "INDEPENDENT_PHYSICAL_REALIZATIONS",
        "UNKNOWN",
        "L and S were modeled as two logical encodings in this one falsifier, not independently authored physical builds; REALIZE evidence remains absent.",
    )

    action_state = State(0, 1, 1)
    action_crashes = crash_variants(action_state, b"\x40")
    action_expected = (
        ("before-D", RESTART_OUTPUT),
        ("after-D", (("D", b"\xa0\x00"),) + RESTART_OUTPUT),
        (
            "after-R",
            (("D", b"\xa0\x00"), ("R", b"\x84")) + RESTART_OUTPUT,
        ),
    )
    action_crash_ok = tuple(
        (outcome.directive, outcome.outputs) for outcome in action_crashes
    ) == action_expected
    action_full_traces = {
        outcome.directive: full_crash_trace(b"\x40", outcome)
        for outcome in action_crashes
    }
    action_full_ok = (
        action_full_traces["before-D"]
        == (
            ("C", b"\x40"),
            ("K", b"CRASH"),
            ("K", b"RESTART"),
            ("R", b"\x88"),
        )
        and action_full_traces["after-D"]
        == (
            ("C", b"\x40"),
            ("D", b"\xa0\x00"),
            ("K", b"CRASH"),
            ("K", b"RESTART"),
            ("R", b"\x88"),
        )
        and action_full_traces["after-R"]
        == (
            ("C", b"\x40"),
            ("D", b"\xa0\x00"),
            ("R", b"\x84"),
            ("K", b"CRASH"),
            ("K", b"RESTART"),
            ("R", b"\x88"),
        )
    )
    findings.test(
        "UNIQUE_ACTION_CRASH_PROJECTIONS",
        action_crash_ok and action_full_ok,
        "The three uniquely stated action crash projections have exact D/R/88 order and no retry.",
        "An action crash projection differs or retries.",
        outcomes=[
            {
                "directive": outcome.directive,
                "projection": json_crossings(outcome.outputs),
                "full_trace": json_crossings(action_full_traces[outcome.directive]),
            }
            for outcome in action_crashes
        ],
    )

    mutator_crashes = crash_variants(State(), b"\x10")
    read_crashes = crash_variants(State(), b"\x60")
    mutator_crash_ok = tuple(
        (outcome.directive, outcome.outputs, outcome.state)
        for outcome in mutator_crashes
    ) == (
        ("byte-old", RESTART_OUTPUT, State()),
        ("byte-new", RESTART_OUTPUT, State(table=1)),
        (
            "after-reply",
            (("R", b"\x81\x10"), ("R", b"\x88")),
            State(table=1),
        ),
    )
    read_crash_ok = tuple(
        (outcome.directive, outcome.outputs, outcome.state)
        for outcome in read_crashes
    ) == (
        ("before-reply", RESTART_OUTPUT, State()),
        (
            "after-reply",
            (("R", bytes.fromhex("86 03 00 40 a0")), ("R", b"\x88")),
            State(),
        ),
    )
    findings.test(
        "UNIQUE_MUTATOR_AND_READ_CRASH_CLAUSES",
        mutator_crash_ok and read_crash_ok,
        "Mutator byte-old/new and rejected/read-only discard/after-reply clauses preserve exact state and emit no delayed interrupted reply.",
        "A uniquely stated mutator/read crash clause differs.",
        mutator=[
            {
                "directive": outcome.directive,
                "trace": json_crossings(full_crash_trace(b"\x10", outcome)),
                "class": packed_class(outcome.state),
            }
            for outcome in mutator_crashes
        ],
        read_only=[
            {
                "directive": outcome.directive,
                "trace": json_crossings(full_crash_trace(b"\x60", outcome)),
                "class": packed_class(outcome.state),
            }
            for outcome in read_crashes
        ],
    )
    findings.add(
        "CRASH_BOUNDARY_TIE_ORDER",
        "UNKNOWN",
        "Section 5 orders 'boundary gap' before byte-old/new but does not order the multiple before/after-crossing boundary gaps. This does not affect the no-crash shortest class witnesses, which all have length at most two.",
    )
    findings.add(
        "STOP_SUITE_CRASH_SCOPE",
        "UNKNOWN",
        "The STOP/framing suite is declared terminal and separate, while the global crossing rule permits crash before/after any crossing; no exact crash continuation for C_DOWN is stated, so none is invented.",
    )
    findings.test(
        "SECOND_CRASH_UNSUPPORTED",
        (3, False) in residual_ids and (3, True) in residual_ids,
        "Residual exploration removes every crash branch after the sole crash and models no recovery fault.",
        "The residual model permits a second crash.",
        post_crash_mode="crash_used=True / no further crash branches",
    )

    deliberate_negatives = {
        "packed_12_hex_rejected": expect_raises(lambda: state_from_class(0x12)),
        "canonical_bad_padding_rejected": expect_raises(
            lambda: decode_canonical(bytes.fromhex("00 ff ff 00"))
        ),
        "probe_bad_symbol_rejected": expect_raises(
            lambda: decode_probe(bytes.fromhex("00 03 02"))
        ),
        "L_gap_rejected": expect_raises(
            lambda: decode_L(bytes.fromhex("10 ff 00 ff ff"))
        ),
        "L_replay_invalid_rejected": expect_raises(
            lambda: decode_L(bytes.fromhex("20 ff ff ff ff"))
        ),
        "unsupported_message_rejected": expect_raises(
            lambda: oracle_step(State(), b"\x02")
        ),
    }
    findings.test(
        "DELIBERATE_NEGATIVE_CHECKS",
        all(deliberate_negatives.values()),
        "Invalid packed/canonical/probe/L images and unsupported input are rejected closed.",
        "A deliberate invalid encoding or unsupported input was accepted.",
        cases=deliberate_negatives,
    )

    # Every numerical prediction in Section 11 is calculated independently of
    # its prose value and reported even when another prediction fails.
    revision_one = sum(state.revision for state in cut_states)
    revision_zero = len(cut_states) - revision_one
    future_word_count = sum(11**length for length in range(4))
    split_scripts = len(CUT_HISTORIES) * future_word_count
    max_writes = 3
    max_crossing_gaps = 3 * 3 + 1
    schedules = 1 + 2 * max_writes + max_crossing_gaps
    runs_one = split_scripts * schedules
    runs_both = 2 * runs_one
    l_images_bound = sum(6**length for length in range(6))
    pair_nodes_bound = (18 * 19 // 2) * 4 * 2
    section11_counts = [
        ("S11_ALPHABET", len(M), 11),
        ("S11_MALFORMED_SAMPLES", 2, 2),
        ("S11_PRE_CUT_HISTORIES", len(CUT_HISTORIES), 133),
        ("S11_PRE_CUT_CLASSES", len(class_counter), 14),
        ("S11_FULL_CLASSES", len(reachable_five), 18),
        ("S11_MAX_DISTINGUISHING_FUTURE", max_future, 2),
        ("S11_REVISION0_IDENTITIES", revision_zero, 111),
        ("S11_REVISION1_IDENTITIES", revision_one, 22),
        ("S11_FUTURE_WORDS", future_word_count, 1464),
        ("S11_SPLIT_SCRIPTS", split_scripts, 194712),
        ("S11_MAX_POSTCUT_WRITES", max_writes, 3),
        ("S11_MAX_PUBLIC_GAPS", max_crossing_gaps, 10),
        ("S11_SCHEDULE_BOUND", schedules, 17),
        ("S11_RUNS_ONE", runs_one, 3310104),
        ("S11_RUNS_BOTH", runs_both, 6620208),
        ("S11_L_IMAGES_BOUND", l_images_bound, 9331),
        ("S11_S_IMAGES", len(ALL_STATES), 18),
        ("S11_PAIR_NODES_BOUND", pair_nodes_bound, 1368),
        ("S11_L_BYTES", len(encode_L(())), 5),
        ("S11_L_MAX_RECOVERY_READS", len(encode_L(())), 5),
        ("S11_S_BYTES", len(encode_S(())), 1),
        ("S11_S_RECOVERY_READS", len(encode_S(())), 1),
    ]
    for identifier, actual, expected in section11_counts:
        findings.test(
            identifier,
            actual == expected,
            f"Section 11 value is exactly {expected}.",
            f"Section 11 expected {expected} but computed {actual}.",
            actual=actual,
            expected=expected,
        )

    # The action/recovery bullets in Section 11 are non-count invariants.
    action_no_crash = oracle_step(action_state, b"\x40").outputs
    findings.test(
        "S11_ACTION_INVARIANTS",
        action_no_crash == (("D", b"\xa0\x00"), ("R", b"\x84"))
        and action_crash_ok,
        "Section 11's no-crash, before-D, and after-D action invariants are exact.",
        "A Section 11 action invariant differs.",
    )

    summary = {status: 0 for status in ("PASS", "FAIL", "UNKNOWN")}
    for finding in findings.items:
        summary[finding["status"]] += 1

    with open(__file__, "rb") as source_file:
        source_sha256 = hashlib.sha256(source_file.read()).hexdigest()

    strongest = [
        {
            "id": "section11_multiset",
            "stated": stated_multiset,
            "stated_sum": sum(stated_multiset),
            "actual": actual_multiset,
            "actual_sum": sum(actual_multiset),
        },
        {
            "id": "revision_shortest_tie",
            "histories": [[], ["50"]],
            "stated_future": ["60"],
            "actual_first_future": history_hex(revision_first),
            "outputs": [
                json_crossings(project_word(State(), revision_first)),
                json_crossings(project_word(State(revision=1), revision_first)),
            ],
        },
        {
            "id": "interpreter_presence_shortest_tie",
            "histories": [[], ["10"]],
            "stated_future": ["30"],
            "actual_first_future": history_hex(table_first),
            "outputs": [
                json_crossings(project_word(State(), table_first)),
                json_crossings(project_word(State(table=1), table_first)),
            ],
        },
        {
            "id": "stop_suite_missing_empty",
            "claim": "no displayed suite member is an empty datagram; C_DOWN is explicitly distinct",
        },
        {
            "id": "exact_history_negative",
            "histories": [[], ["30"]],
            "same_H11_class": packed_class(cached_fold(())),
            "characteristic_results": [1, 0],
        },
    ]

    return {
        "artifact": {
            "seed_path": SEED_PATH,
            "seed_sha256": seed_sha256,
            "expected_seed_sha256": EXPECTED_SEED_SHA256,
            "instrument_path": os.path.abspath(__file__),
            "instrument_sha256": source_sha256,
            "standard_library_only": True,
        },
        "checks": findings.items,
        "cut_partition": {
            "history_count": len(CUT_HISTORIES),
            "class_count": len(class_counter),
            "class_sizes": {str(key): value for key, value in actual_table.items()},
            "actual_multiset": actual_multiset,
            "stated_section11_multiset": stated_multiset,
        },
        "depth_three": {
            "cut_classes": cut_residual_count,
            "full_classes": full_residual_count,
            "full_pair_witness_count": len(full_witnesses),
            "cut_pair_witness_count": len(cut_witnesses),
            "maximum_shortest_future": max_future,
        },
        "shortest_witnesses": {
            "cut_class_pairs": cut_witnesses,
            "full_class_pairs": full_witnesses,
            "shortest_class_representatives": {
                str(packed_class(state)): history_hex(shortest_representatives[state])
                for state in ALL_STATES
            },
        },
        "logical_encoding_note": (
            "L and S are same-source logical encoders used for falsification only; "
            "they are not the independent builds required by Section 8."
        ),
        "measurement_note": (
            "Runtime/RSS are excluded from canonical JSON as nondeterministic. "
            "Measure externally; report stdout SHA-256 externally to avoid self-reference."
        ),
        "section11": {
            "counts": {
                identifier: {"actual": actual, "expected": expected}
                for identifier, actual, expected in section11_counts
            },
            "class_multiset_actual": actual_multiset,
            "class_multiset_stated": stated_multiset,
        },
        "strongest_minimized_witnesses": strongest,
        "summary": summary,
    }


def emit_canonical(value: Any) -> None:
    sys.stdout.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> int:
    try:
        with open(SEED_PATH, "rb") as seed_file:
            seed_bytes = seed_file.read()
    except OSError as error:
        emit_canonical({"fatal": "FROZEN_SEED_UNREADABLE", "reason": str(error)})
        return 2
    actual_sha256 = hashlib.sha256(seed_bytes).hexdigest()
    if actual_sha256 != EXPECTED_SEED_SHA256:
        emit_canonical(
            {
                "actual_sha256": actual_sha256,
                "expected_sha256": EXPECTED_SEED_SHA256,
                "fatal": "FROZEN_SEED_SHA256_MISMATCH",
                "semantic_checks_executed": False,
            }
        )
        return 2
    report = run_checks(actual_sha256)
    emit_canonical(report)
    return 1 if report["summary"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
