#!/usr/bin/env python3
"""Executable falsifier for the frozen CF-1 contract frontier.

This is deliberately a bounded reference instrument, not an implementation
architecture.  It reads no repository artifact other than the frozen contract
and its own source, uses only the Python standard library, and emits one line of
canonical JSON.  A FAIL is a finding about the frozen seed, not an invitation to
repair or reinterpret it.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from dataclasses import dataclass, replace
from typing import Any, Callable, Iterable, Optional, Sequence


CONTRACT_PATH = "/root/pareto/zero-ground-restart/CONTRACT-FRONTIER-R01F.md"
EXPECTED_CONTRACT_SHA256 = (
    "f9fce4d2f0fd43594553f06ab05403d90b088b3f2fd50b7c3f883be7f7b03445"
)

CT1 = (
    b"name=CF-1\n"
    b"version=1\n"
    b"create=10 o q a x i\n"
    b"retire=11\n"
    b"observe=20\n"
    b"query=21\n"
    b"action=30 n\n"
    b"explain=40\n"
    b"interpret=50\n"
    b"update=60 u16be(length) contract-text\n"
    b"identify=70\n"
    b"bit-bytes=00,01\n"
)

CT2 = (
    b"name=CF-1\n"
    b"version=2\n"
    b"create=10 o q a x i\n"
    b"retire=11\n"
    b"observe=20\n"
    b"query=21\n"
    b"query2=22\n"
    b"action=30 n\n"
    b"explain=40\n"
    b"interpret=50\n"
    b"update=60 u16be(length) contract-text\n"
    b"identify=70\n"
    b"bit-bytes=00,01\n"
)

BIT = (0x00, 0x01)
NONCE = (0x00, 0x01)
OPCODES = (0x10, 0x11, 0x20, 0x21, 0x22, 0x30, 0x40, 0x50, 0x60, 0x70)

RULE = {
    "FRAME_PREFIX": 0x01,
    "FRAME_SHORT": 0x02,
    "FRAME_EXCESS": 0x03,
    "OPCODE_MISSING": 0x04,
    "OPCODE_UNKNOWN": 0x05,
    "ARITY": 0x06,
    "BIT_VALUE": 0x07,
    "NONCE_VALUE": 0x08,
    "UPDATE_HEADER": 0x09,
    "UPDATE_LENGTH": 0x0A,
    "CONTRACT_TEXT": 0x0B,
    "CREATE_NOT_VIRGIN": 0x20,
    "NOT_LIVE": 0x21,
    "QUERY2_REQUIRES_V2": 0x22,
    "NONCE_USED": 0x23,
    "CT2_NO_DOWNGRADE": 0x24,
}

RULE_NAME = {value: name for name, value in RULE.items()}
MANIFESTS = (
    b"CF-1|A=coarse|B=atomic\n",
    b"CF-1|A=coarse|B=power\n",
    b"CF-1|A=detailed|B=atomic\n",
    b"CF-1|A=detailed|B=power\n",
)


def u16be(number: int) -> bytes:
    if not 0 <= number <= 0xFFFF:
        raise ValueError("u16be input is outside 0..65535")
    return bytes((number // 256, number % 256))


def envelope(payload: bytes) -> bytes:
    return u16be(len(payload)) + payload


def hx(raw: bytes) -> str:
    return raw.hex()


# Static byte facts from Sections 2--5, 8--10, and 19.  These assertions are
# intentionally import-time assertions: a transcription error prevents the
# instrument from presenting any semantic verdict.
assert len(CT1) == 172 and u16be(len(CT1)) == b"\x00\xac"
assert len(CT2) == 182 and u16be(len(CT2)) == b"\x00\xb6"
assert CT1.endswith(b"\n") and CT2.endswith(b"\n")
assert b"\r" not in CT1 + CT2
assert CT2 == CT1.replace(b"version=1\n", b"version=2\n").replace(
    b"query=21\n", b"query=21\nquery2=22\n"
)
assert envelope(bytes.fromhex("10 00 00 00 00 00")) == bytes.fromhex(
    "00 06 10 00 00 00 00 00"
)
assert envelope(b"\x11") == bytes.fromhex("00 01 11")
assert envelope(b"\x30\x00") == bytes.fromhex("00 02 30 00")
assert envelope(b"\x60" + u16be(len(CT1)) + CT1).startswith(
    bytes.fromhex("00 af 60 00 ac")
)
assert envelope(b"\x60" + u16be(len(CT2)) + CT2).startswith(
    bytes.fromhex("00 b9 60 00 b6")
)
assert len(envelope(b"\x60" + u16be(len(CT1)) + CT1)) == 177
assert len(envelope(b"\x60" + u16be(len(CT2)) + CT2)) == 187
assert envelope(b"A0\x00\x00") == bytes.fromhex("00 04 41 30 00 00")
assert envelope(b"AE\x00\x00") == bytes.fromhex("00 04 41 45 00 00")
assert envelope(b"A2\x00") == bytes.fromhex("00 03 41 32 00")
assert envelope(b"A1\x00\x00") == bytes.fromhex("00 04 41 31 00 00")
assert envelope(b"A1\x00\x01") == bytes.fromhex("00 04 41 31 00 01")
assert envelope(b"I0\x00") == bytes.fromhex("00 03 49 30 00")
assert envelope(b"I1\x00\x01") == bytes.fromhex("00 04 49 31 00 01")
assert envelope(b"\xff") == bytes.fromhex("00 01 ff")
assert envelope(b"F0") == bytes.fromhex("00 02 46 30")
assert envelope(b"F1") == bytes.fromhex("00 02 46 31")
assert envelope(b"\x20") == bytes.fromhex("00 01 20")
assert envelope(b"\x21") == bytes.fromhex("00 01 21")
assert envelope(b"\x22") == bytes.fromhex("00 01 22")
assert envelope(b"\x40") == bytes.fromhex("00 01 40")
assert envelope(b"\x50") == bytes.fromhex("00 01 50")
assert envelope(b"\x70") == bytes.fromhex("00 01 70")
assert envelope(b"\x80") == bytes.fromhex("00 01 80")
assert envelope(b"\x82") == bytes.fromhex("00 01 82")
assert envelope(b"\x83\x01\x00") == bytes.fromhex("00 03 83 01 00")
assert envelope(b"\x90\x00") == bytes.fromhex("00 02 90 00")
assert envelope(b"\x91\x00") == bytes.fromhex("00 02 91 00")
assert envelope(b"\x92\x00") == bytes.fromhex("00 02 92 00")
assert envelope(b"\x93\x00") == bytes.fromhex("00 02 93 00")
assert envelope(b"\x95\x00") == bytes.fromhex("00 02 95 00")
assert envelope(b"\x95\x01") == bytes.fromhex("00 02 95 01")
assert envelope(b"\x94\x01\x00\xac" + CT1).startswith(
    bytes.fromhex("00 b0 94 01 00 ac")
)
assert envelope(b"\x94\x02\x00\xb6" + CT2).startswith(
    bytes.fromhex("00 ba 94 02 00 b6")
)
assert MANIFESTS == tuple(
    f"CF-1|A={a}|B={b}\n".encode("ascii")
    for a in ("coarse", "detailed")
    for b in ("atomic", "power")
)


@dataclass(frozen=True, order=True)
class Rejection:
    rule: int
    offset: int


@dataclass(frozen=True, order=True)
class Parsed:
    opcode: int
    fields: tuple[Any, ...] = ()


@dataclass(frozen=True, order=True)
class Detail:
    rule: int
    offset: int
    length: bytes
    raw: bytes


@dataclass(frozen=True, order=True)
class State:
    version: int = 1
    lifecycle: str = "virgin"
    # Raw retained bits intentionally survive RETIRE in this model.  The direct
    # canonicalizer, rather than the transition implementation, is what drops
    # them, so normalization claims can actually be falsified.
    bits: Optional[tuple[int, int, int, int, int]] = None
    used_mask: int = 0
    provenance: Any = None


@dataclass(frozen=True)
class Outcome:
    choice: str
    trace: tuple[tuple[str, bytes], ...]
    state: State


def contract_text_offense(text: bytes) -> int:
    candidates = [CT1, CT2]
    position = 0
    while True:
        submitted_next: Optional[int]
        submitted_next = text[position] if position < len(text) else None
        retained = []
        for candidate in candidates:
            candidate_next = candidate[position] if position < len(candidate) else None
            if candidate_next == submitted_next:
                retained.append(candidate)
        if not retained:
            return position
        candidates = retained
        position += 1


def derive_offset_from_rule_raw(rule: int, raw: bytes) -> int:
    syntactic = validate(raw)
    if isinstance(syntactic, Rejection):
        if syntactic.rule != rule:
            raise ValueError("raw validation rule differs from retained rule")
        return syntactic.offset
    semantic_offsets = {
        RULE["CREATE_NOT_VIRGIN"]: 2,
        RULE["NOT_LIVE"]: 2,
        RULE["QUERY2_REQUIRES_V2"]: 2,
        RULE["NONCE_USED"]: 3,
        RULE["CT2_NO_DOWNGRADE"]: 5,
    }
    if rule not in semantic_offsets:
        raise ValueError("not a CF-1 rejection rule for the supplied raw")
    return semantic_offsets[rule]


def validate(raw: bytes) -> Parsed | Rejection:
    if len(raw) < 2:
        return Rejection(RULE["FRAME_PREFIX"], len(raw))
    declared = int.from_bytes(raw[:2], "big")
    actual = len(raw) - 2
    if actual < declared:
        return Rejection(RULE["FRAME_SHORT"], len(raw))
    if actual > declared:
        return Rejection(RULE["FRAME_EXCESS"], 2 + declared)
    if declared == 0:
        return Rejection(RULE["OPCODE_MISSING"], 2)

    payload = raw[2:]
    opcode = payload[0]
    if opcode not in OPCODES:
        return Rejection(RULE["OPCODE_UNKNOWN"], 2)

    if opcode != 0x60:
        required = 6 if opcode == 0x10 else 2 if opcode == 0x30 else 1
        if declared < required:
            return Rejection(RULE["ARITY"], len(raw))
        if declared > required:
            return Rejection(RULE["ARITY"], 2 + required)

        if opcode == 0x10:
            fields = tuple(payload[1:])
            for index, value in enumerate(fields):
                if value not in BIT:
                    return Rejection(RULE["BIT_VALUE"], 3 + index)
            return Parsed(opcode, fields)
        if opcode == 0x30:
            nonce = payload[1]
            if nonce not in NONCE:
                return Rejection(RULE["NONCE_VALUE"], 3)
            return Parsed(opcode, (nonce,))
        return Parsed(opcode)

    if declared < 3:
        return Rejection(RULE["UPDATE_HEADER"], len(raw))
    embedded = int.from_bytes(payload[1:3], "big")
    text = payload[3:]
    if len(text) < embedded:
        return Rejection(RULE["UPDATE_LENGTH"], len(raw))
    if len(text) > embedded:
        return Rejection(RULE["UPDATE_LENGTH"], 5 + embedded)
    if text not in (CT1, CT2):
        return Rejection(RULE["CONTRACT_TEXT"], 5 + contract_text_offense(text))
    return Parsed(opcode, (1 if text == CT1 else 2,))


def save_rejection(state: State, profile: str, raw: bytes, rejection: Rejection) -> State:
    if profile == "coarse":
        provenance: Any = True
    elif profile == "detailed":
        provenance = Detail(rejection.rule, rejection.offset, u16be(len(raw)), raw)
    else:
        raise ValueError("profile must be coarse or detailed")
    return replace(state, provenance=provenance)


def rejection_payload(profile: str, rejection: Rejection) -> bytes:
    if profile == "coarse":
        return b"\x82"
    return bytes((0x83, rejection.rule, rejection.offset))


def explain_payload(state: State, profile: str) -> bytes:
    if not state.provenance:
        return b"\x95\x00"
    if profile == "coarse":
        return b"\x95\x01"
    detail = state.provenance
    assert isinstance(detail, Detail)
    return bytes((0x95, detail.rule, detail.offset)) + detail.length + detail.raw


def semantic_rejection(state: State, parsed: Parsed) -> Optional[Rejection]:
    opcode = parsed.opcode
    if opcode == 0x22 and state.version == 1:
        return Rejection(RULE["QUERY2_REQUIRES_V2"], 2)
    if opcode == 0x10 and state.lifecycle != "virgin":
        return Rejection(RULE["CREATE_NOT_VIRGIN"], 2)
    if opcode in (0x11, 0x20, 0x21, 0x30, 0x50) and state.lifecycle != "live":
        return Rejection(RULE["NOT_LIVE"], 2)
    if opcode == 0x22 and state.lifecycle != "live":
        return Rejection(RULE["NOT_LIVE"], 2)
    if opcode == 0x30:
        nonce = parsed.fields[0]
        if state.used_mask & (1 << nonce):
            return Rejection(RULE["NONCE_USED"], 3)
    if opcode == 0x60 and parsed.fields[0] == 1 and state.version == 2:
        return Rejection(RULE["CT2_NO_DOWNGRADE"], 5)
    return None


def run_request(
    state: State,
    raw: bytes,
    profile: str,
    *,
    table: tuple[int, int] = (0, 0),
    acknowledgment: str = "direct",
) -> Outcome:
    trace: list[tuple[str, bytes]] = [("C->S", raw)]
    parsed_or_rejection = validate(raw)
    if isinstance(parsed_or_rejection, Rejection):
        next_state = save_rejection(state, profile, raw, parsed_or_rejection)
        trace.append(("S->C", envelope(rejection_payload(profile, parsed_or_rejection))))
        return Outcome("fixed", tuple(trace), next_state)

    parsed = parsed_or_rejection
    rejection = semantic_rejection(state, parsed)
    if rejection is not None:
        next_state = save_rejection(state, profile, raw, rejection)
        trace.append(("S->C", envelope(rejection_payload(profile, rejection))))
        return Outcome("fixed", tuple(trace), next_state)

    opcode = parsed.opcode
    next_state = state
    if opcode == 0x10:
        bits = tuple(int(value) for value in parsed.fields)
        assert len(bits) == 5
        next_state = replace(state, lifecycle="live", bits=bits, used_mask=0)
        trace.append(("S->C", envelope(b"\x80")))
    elif opcode == 0x11:
        next_state = replace(state, lifecycle="retired")
        trace.append(("S->C", envelope(b"\x80")))
    elif opcode == 0x20:
        assert state.bits is not None
        trace.append(("S->C", envelope(bytes((0x90, state.bits[0])))))
    elif opcode == 0x21:
        assert state.bits is not None
        trace.append(("S->C", envelope(bytes((0x91, state.bits[1])))))
    elif opcode == 0x22:
        assert state.bits is not None and state.version == 2
        trace.append(("S->C", envelope(bytes((0x93, state.bits[3])))))
    elif opcode == 0x30:
        assert state.bits is not None
        nonce = parsed.fields[0]
        action = state.bits[2]
        trace.append(("S->A", envelope(b"A0" + bytes((action, nonce)))))
        trace.append(("A->W", envelope(b"AE" + bytes((action, nonce)))))
        if acknowledgment == "timeout":
            trace.append(("T->S", envelope(b"\xff")))
            trace.append(("S->A", envelope(b"A2" + bytes((nonce,)))))
        elif acknowledgment != "direct":
            raise ValueError("acknowledgment must be direct or timeout")
        trace.append(("A->S", envelope(b"A1" + bytes((nonce, 0x00)))))
        next_state = replace(state, used_mask=state.used_mask | (1 << nonce))
        trace.append(("S->C", envelope(b"\x80")))
    elif opcode == 0x40:
        trace.append(("S->C", envelope(explain_payload(state, profile))))
    elif opcode == 0x50:
        assert state.bits is not None
        t0, t1 = table
        if t0 not in BIT or t1 not in BIT:
            raise ValueError("truth table bytes must be BIT values")
        interpretation_bit = state.bits[4]
        trace.append(("S->I", envelope(b"I0" + bytes((interpretation_bit,)))))
        trace.append(("I->S", envelope(b"I1" + bytes((t0, t1)))))
        result = t0 if interpretation_bit == 0 else t1
        trace.append(("S->C", envelope(bytes((0x92, result)))))
    elif opcode == 0x60:
        next_state = replace(state, version=parsed.fields[0])
        trace.append(("S->C", envelope(b"\x80")))
    elif opcode == 0x70:
        text = CT1 if state.version == 1 else CT2
        trace.append(
            (
                "S->C",
                envelope(bytes((0x94, state.version)) + u16be(len(text)) + text),
            )
        )
    else:  # pragma: no cover - validate has closed this set
        raise AssertionError("validated unknown opcode")
    return Outcome("fixed", tuple(trace), next_state)


TRUTH_TABLES = ((0, 0), (0, 1), (1, 0), (1, 1))


def transition_state(state: State, raw: bytes, profile: str) -> State:
    """State-only form of run_request for bounded reachability exploration."""
    parsed_or_rejection = validate(raw)
    if isinstance(parsed_or_rejection, Rejection):
        return save_rejection(state, profile, raw, parsed_or_rejection)
    parsed = parsed_or_rejection
    rejection = semantic_rejection(state, parsed)
    if rejection is not None:
        return save_rejection(state, profile, raw, rejection)
    if parsed.opcode == 0x10:
        return replace(
            state,
            lifecycle="live",
            bits=tuple(int(value) for value in parsed.fields),
            used_mask=0,
        )
    if parsed.opcode == 0x11:
        return replace(state, lifecycle="retired")
    if parsed.opcode == 0x30:
        return replace(state, used_mask=state.used_mask | (1 << parsed.fields[0]))
    if parsed.opcode == 0x60:
        return replace(state, version=parsed.fields[0])
    return state


def request_outcomes(state: State, raw: bytes, profile: str) -> tuple[Outcome, ...]:
    parsed = validate(raw)
    if isinstance(parsed, Parsed) and semantic_rejection(state, parsed) is None:
        if parsed.opcode == 0x50:
            return tuple(
                replace(run_request(state, raw, profile, table=table), choice=f"table:{table[0]}{table[1]}")
                for table in TRUTH_TABLES
            )
        if parsed.opcode == 0x30:
            return tuple(
                replace(
                    run_request(state, raw, profile, acknowledgment=schedule),
                    choice=f"ack:{schedule}",
                )
                for schedule in ("direct", "timeout")
            )
    return (run_request(state, raw, profile),)


def canonical_state(state: State, profile: str) -> tuple[Any, ...]:
    if state.lifecycle == "virgin":
        semantic: tuple[Any, ...] = (state.version, "virgin")
    elif state.lifecycle == "retired":
        semantic = (state.version, "retired")
    else:
        assert state.lifecycle == "live" and state.bits is not None
        o, q, action, x, interpretation = state.bits
        retained_action: Optional[int] = None if state.used_mask == 0b11 else action
        semantic = (
            state.version,
            "live",
            o,
            q,
            x,
            interpretation,
            retained_action,
            state.used_mask,
        )
    provenance = bool(state.provenance) if profile == "coarse" else state.provenance
    return semantic + (provenance,)


def create_frame(bits: Sequence[int]) -> bytes:
    if len(bits) != 5:
        raise ValueError("CREATE needs five bits")
    return envelope(b"\x10" + bytes(bits))


RETIRE = envelope(b"\x11")
OBSERVE = envelope(b"\x20")
QUERY = envelope(b"\x21")
QUERY2 = envelope(b"\x22")
ACTION0 = envelope(b"\x30\x00")
ACTION1 = envelope(b"\x30\x01")
EXPLAIN = envelope(b"\x40")
INTERPRET = envelope(b"\x50")
UPDATE1 = envelope(b"\x60" + u16be(len(CT1)) + CT1)
UPDATE2 = envelope(b"\x60" + u16be(len(CT2)) + CT2)
IDENTIFY = envelope(b"\x70")

P_FRAMES = tuple(
    sorted(
        [create_frame(bits) for bits in itertools.product(BIT, repeat=5)]
        + [ACTION0, ACTION1]
        + [RETIRE, OBSERVE, QUERY, QUERY2, EXPLAIN, INTERPRET, IDENTIFY]
        + [UPDATE1, UPDATE2],
        key=lambda raw: (len(raw), raw),
    )
)
assert len(P_FRAMES) == 43 and len(set(P_FRAMES)) == 43
assert all(isinstance(validate(raw), Parsed) for raw in P_FRAMES)


# One shortest member for each validation rule, supplemented only where a rule
# has genuinely different short/excess or prefix/end offset logic.
INVALID_REP_EXPECTED = (
    (b"", "FRAME_PREFIX", 0),
    (b"\x00", "FRAME_PREFIX", 1),
    (b"\x00\x01", "FRAME_SHORT", 2),
    (b"\x00\x00\x00", "FRAME_EXCESS", 2),
    (envelope(b""), "OPCODE_MISSING", 2),
    (envelope(b"\x00"), "OPCODE_UNKNOWN", 2),
    (envelope(b"\x10"), "ARITY", 3),
    (envelope(b"\x11\x00"), "ARITY", 3),
    (envelope(b"\x10\xff\x00\x00\x00\x00"), "BIT_VALUE", 3),
    (envelope(b"\x10\x00\xff\x00\x00\x00"), "BIT_VALUE", 4),
    (envelope(b"\x30\xff"), "NONCE_VALUE", 3),
    (envelope(b"\x60"), "UPDATE_HEADER", 3),
    (envelope(b"\x60\x00"), "UPDATE_HEADER", 4),
    (envelope(b"\x60\x00\x01"), "UPDATE_LENGTH", 5),
    (envelope(b"\x60\x00\x00\x00"), "UPDATE_LENGTH", 5),
    (envelope(b"\x60\x00\x00"), "CONTRACT_TEXT", 5),
    (envelope(b"\x60\x00\x01n"), "CONTRACT_TEXT", 6),
    (envelope(b"\x60\x00\x01x"), "CONTRACT_TEXT", 5),
    (
        envelope(b"\x60" + u16be(len(CT1) + 1) + CT1 + b"\x00"),
        "CONTRACT_TEXT",
        5 + len(CT1),
    ),
    (
        envelope(b"\x60" + u16be(len(CT2) - 1) + CT2[:-1]),
        "CONTRACT_TEXT",
        5 + len(CT2) - 1,
    ),
)

INVALID_REPS = tuple(
    sorted({item[0] for item in INVALID_REP_EXPECTED}, key=lambda raw: (len(raw), raw))
)
REP_ALPHABET = tuple(sorted(set(P_FRAMES + INVALID_REPS), key=lambda raw: (len(raw), raw)))


def run_sequence(
    frames: Sequence[bytes],
    profile: str,
    *,
    tables: Optional[Sequence[tuple[int, int]]] = None,
    acknowledgments: Optional[Sequence[str]] = None,
) -> tuple[State, tuple[tuple[str, bytes], ...]]:
    state = State()
    trace: list[tuple[str, bytes]] = []
    table_iter = iter(tables or ())
    ack_iter = iter(acknowledgments or ())
    for raw in frames:
        parsed = validate(raw)
        table = (0, 0)
        acknowledgment = "direct"
        if isinstance(parsed, Parsed) and semantic_rejection(state, parsed) is None:
            if parsed.opcode == 0x50:
                table = next(table_iter, (0, 0))
            elif parsed.opcode == 0x30:
                acknowledgment = next(ack_iter, "direct")
        outcome = run_request(
            state,
            raw,
            profile,
            table=table,
            acknowledgment=acknowledgment,
        )
        state = outcome.state
        trace.extend(outcome.trace)
    return state, tuple(trace)


def trace_json(trace: Iterable[tuple[str, bytes]]) -> list[dict[str, str]]:
    return [{"channel": channel, "raw_hex": raw.hex()} for channel, raw in trace]


class Findings:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(
        self,
        identifier: str,
        status: str,
        summary: str,
        **evidence: Any,
    ) -> None:
        if status not in ("PASS", "FAIL", "UNKNOWN"):
            raise ValueError("invalid finding status")
        item: dict[str, Any] = {
            "id": identifier,
            "status": status,
            "summary": summary,
        }
        if evidence:
            item["evidence"] = evidence
        self.items.append(item)

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


def exact_cardinalities() -> dict[str, Any]:
    universe = (256**256 - 1) // 255
    potentially_successful = 43
    invalid = universe - potentially_successful

    frame_prefix = 1 + 256
    frame_short = sum((65535 - actual) * 256**actual for actual in range(254))
    frame_excess = sum(actual * 256**actual for actual in range(254))
    opcode_missing = 1
    opcode_unknown = sum(246 * 256 ** (length - 1) for length in range(1, 254))
    arity = (
        sum(256 ** (length - 1) for length in range(1, 6))
        + sum(256 ** (length - 1) for length in range(7, 254))
        + 1
        + sum(256 ** (length - 1) for length in range(3, 254))
        + 7 * sum(256 ** (length - 1) for length in range(2, 254))
    )
    bit_value = 256**5 - 2**5
    nonce_value = 256 - 2
    update_header = 1 + 256
    update_length = sum(65535 * 256**text_length for text_length in range(251))
    contract_text = sum(256**text_length for text_length in range(251)) - 2
    validation_counts = {
        "ARITY": arity,
        "BIT_VALUE": bit_value,
        "CONTRACT_TEXT": contract_text,
        "FRAME_EXCESS": frame_excess,
        "FRAME_PREFIX": frame_prefix,
        "FRAME_SHORT": frame_short,
        "NONCE_VALUE": nonce_value,
        "OPCODE_MISSING": opcode_missing,
        "OPCODE_UNKNOWN": opcode_unknown,
        "UPDATE_HEADER": update_header,
        "UPDATE_LENGTH": update_length,
    }
    s252 = sum(256**power for power in range(253))
    assert arity == 9 * s252 - 256**5 - 263
    validation_expressions = {
        "ARITY": "9*S_252-256^5-263",
        "BIT_VALUE": "256^5-32",
        "CONTRACT_TEXT": "S_250-2",
        "FRAME_EXCESS": "sum(a=0..253,a*256^a)",
        "FRAME_PREFIX": "257",
        "FRAME_SHORT": "sum(a=0..253,(65535-a)*256^a)",
        "NONCE_VALUE": "254",
        "OPCODE_MISSING": "1",
        "OPCODE_UNKNOWN": "246*S_252",
        "UPDATE_HEADER": "257",
        "UPDATE_LENGTH": "65535*S_250",
        "notation": "S_j=sum(k=0..j,256^k)",
    }
    partition_total = potentially_successful + sum(validation_counts.values())

    pre_sequences = 1 + universe + universe**2
    post_sequences = 1 + universe + universe**2 + universe**3
    safe_runs = pre_sequences * post_sequences * 4**5 * 201
    residual = [1]
    for _ in range(3):
        residual.append(1 + universe * 804 * residual[-1])
    seconds_per_year = 31_556_952
    years_at_exaops = universe // (10**18 * seconds_per_year)

    return {
        "U": {
            "decimal": str(universe),
            "decimal_digits": len(str(universe)),
            "expression": "sum(k=0..255,256^k)=(256^256-1)/255",
        },
        "D": {
            "decimal": str(invalid),
            "decimal_digits": len(str(invalid)),
            "expression": "Ucount-43",
        },
        "P": {"decimal": "43", "expression": "32+2+7+1+1"},
        "validation_partition": {
            "counts_decimal": {name: str(count) for name, count in validation_counts.items()},
            "expressions": validation_expressions,
            "sum_equals_U": partition_total == universe,
        },
        "bounds": {
            "pre_sequence_expression": "1+Ucount+Ucount^2",
            "pre_sequence_decimal_digits": len(str(pre_sequences)),
            "post_sequence_expression": "1+Ucount+Ucount^2+Ucount^3",
            "post_sequence_decimal_digits": len(str(post_sequences)),
            "safe_run_expression": "(1+U+U^2)*(1+U+U^2+U^3)*4^5*201",
            "safe_run_decimal_digits": len(str(safe_runs)),
            "T3_expression": "1+804*U*(1+804*U*(1+804*U))",
            "T3_decimal_digits": len(str(residual[3])),
            "U_iteration_years_at_10^18_per_second_decimal_digits": len(
                str(years_at_exaops)
            ),
            "U_iteration_years_at_10^18_per_second_expression": (
                "floor(Ucount/(10^18*31556952))"
            ),
        },
        "candidate_semantic_base": {
            "decimal": "228",
            "expression": "2*(1 virgin + 1 retired + 16*(2*3+1) live)",
        },
        "coarse_unbounded_direct_tuple": {
            "decimal": "456",
            "expression": "228*2",
        },
        "detailed_non_none_provenance": {
            "decimal": str(universe),
            "expression": "Dcount+43=Ucount",
        },
        "detailed_naive_cartesian_tuple_space": {
            "decimal": str(228 * (universe + 1)),
            "expression": "228*(Ucount+1)",
            "note": "capacity, not bounded-horizon reachability",
        },
    }


def bfs_states(
    profile: str,
    alphabet: Sequence[bytes],
    depth: int,
) -> tuple[set[State], list[int]]:
    reached = {State()}
    frontier = {State()}
    counts = [1]
    for _ in range(depth):
        following: set[State] = set()
        for state in frontier:
            for raw in alphabet:
                following.add(transition_state(state, raw, profile))
        reached.update(following)
        frontier = following
        counts.append(len(reached))
    return reached, counts


def exact_depth_states(
    profile: str,
    alphabet: Sequence[bytes],
    depth: int,
) -> list[set[State]]:
    levels = [{State()}]
    for _ in range(depth):
        following: set[State] = set()
        for state in levels[-1]:
            for raw in alphabet:
                following.add(transition_state(state, raw, profile))
        levels.append(following)
    return levels


def normalized_congruence(
    profile: str,
    alphabet: Sequence[bytes],
    max_reachable_depth: int,
) -> tuple[bool, dict[str, Any]]:
    levels = exact_depth_states(profile, alphabet, max_reachable_depth)
    checked_pairs = 0
    checked_transitions = 0
    first_collision: Optional[dict[str, Any]] = None

    # Every state reachable before the final step is checked once.  One-step
    # congruence plus identical observable traces proves equality of complete
    # adaptive residuals by induction, without materializing the DAG.
    states = set().union(*levels[:-1])
    groups: dict[tuple[Any, ...], list[State]] = {}
    for state in states:
        groups.setdefault(canonical_state(state, profile), []).append(state)
    for key, members in groups.items():
        if len(members) < 2:
            continue
        members.sort()
        exemplar = members[0]
        for other in members[1:]:
            checked_pairs += 1
            for raw in alphabet:
                left = request_outcomes(exemplar, raw, profile)
                right = request_outcomes(other, raw, profile)
                checked_transitions += max(len(left), len(right))
                left_view = tuple(
                    (outcome.choice, outcome.trace, canonical_state(outcome.state, profile))
                    for outcome in left
                )
                right_view = tuple(
                    (outcome.choice, outcome.trace, canonical_state(outcome.state, profile))
                    for outcome in right
                )
                if left_view != right_view:
                    first_collision = {
                        "key": repr(key),
                        "raw_hex": raw.hex(),
                        "left": repr(exemplar),
                        "right": repr(other),
                    }
                    return False, {
                        "checked_pairs": checked_pairs,
                        "checked_transitions": checked_transitions,
                        "first_collision": first_collision,
                        "level_state_counts": [len(level) for level in levels],
                        "unique_states_checked": len(states),
                    }
    return True, {
        "checked_pairs": checked_pairs,
        "checked_transitions": checked_transitions,
        "first_collision": first_collision,
        "level_state_counts": [len(level) for level in levels],
        "unique_states_checked": len(states),
    }


def semantic_key(state: State) -> tuple[Any, ...]:
    # Strip provenance from the specified direct key.
    return canonical_state(replace(state, provenance=None), "detailed")[:-1]


def symbolic_direct_counts() -> dict[str, Any]:
    universe = (256**256 - 1) // 255
    invalid = universe - 43

    # P-only states account exactly for none and semantic-rejection provenance.
    p_levels_detailed = exact_depth_states("detailed", P_FRAMES, 5)
    p_upto_2 = set().union(*p_levels_detailed[:3])
    p_upto_5 = set().union(*p_levels_detailed[:6])
    k2 = len({canonical_state(state, "detailed") for state in p_upto_2})
    k5 = len({canonical_state(state, "detailed") for state in p_upto_5})

    # For a fixed invalid R, two total submissions can place its exact Detail
    # alongside precisely the semantic states reachable with <=1 successful P.
    success_one_semantics = {semantic_key(State())}
    for raw in P_FRAMES:
        outcome = run_request(State(), raw, "detailed")
        if outcome.state.provenance is None:
            success_one_semantics.add(semantic_key(outcome.state))
    assert len(success_one_semantics) == 34

    # Within five total submissions, put any invalid first and then reach every
    # one of the 228 normalized semantic states in at most four successes.
    success_levels = [{State()}]
    for _ in range(4):
        following: set[State] = set()
        for state in success_levels[-1]:
            for raw in P_FRAMES:
                outcome = run_request(state, raw, "detailed")
                if outcome.state.provenance is None:
                    following.add(outcome.state)
        success_levels.append(following)
    semantics_upto_4 = {
        semantic_key(state) for level in success_levels for state in level
    }
    assert len(semantics_upto_4) == 228

    coarse_levels = exact_depth_states("coarse", P_FRAMES + (b"",), 2)
    coarse_pre = len(
        {
            canonical_state(state, "coarse")
            for level in coarse_levels
            for state in level
        }
    )
    return {
        "coarse_pre_cut_at_most_2": {
            "decimal": str(coarse_pre),
            "method": "exact 43-P plus one symbolic coarse-invalid transition",
            "dense_id_width_bytes": 1,
        },
        "detailed_pre_cut_at_most_2": {
            "expression": "34*Ucount-67",
            "decimal": str(34 * invalid + k2),
            "P_only_term": k2,
            "equivalent_D_expression": f"34*Dcount+{k2}",
            "dense_id_width_bytes": 256,
        },
        "detailed_complete_run_at_most_5": {
            "expression": "228*Ucount-324",
            "decimal": str(228 * invalid + k5),
            "P_only_term": k5,
            "equivalent_D_expression": f"228*Dcount+{k5}",
        },
        "pre_cut_distribution": {
            "CT1_virgin": {"coarse": "2", "detailed": "Ucount-35"},
            "CT2_virgin": {"coarse": "2", "detailed": "Ucount-33"},
            "CT1_live_unused": {"coarse": "64", "detailed": "32*(Ucount-3)"},
            "CT2_live_unused": {"coarse": "32", "detailed": "32"},
            "CT1_live_one_nonce_used": {"coarse": "64", "detailed": "64"},
            "CT1_retired": {"coarse": "1", "detailed": "1"},
        },
        "invalid_symbolic_lemma": (
            "coarse maps every D member to some without semantic mutation; detailed "
            "maps each R injectively to (rule,offset,u16be(len(R)),R), and no request "
            "consults provenance except EXPLAIN"
        ),
    }


def response_tail(outcome: Outcome) -> bytes:
    return outcome.trace[-1][1]


def state_after(frames: Sequence[bytes], profile: str = "detailed") -> State:
    return run_sequence(frames, profile)[0]


def separating_witnesses() -> tuple[list[dict[str, Any]], bool]:
    c00000 = create_frame((0, 0, 0, 0, 0))
    c10000 = create_frame((1, 0, 0, 0, 0))
    c01000 = create_frame((0, 1, 0, 0, 0))
    c00100 = create_frame((0, 0, 1, 0, 0))
    c00010 = create_frame((0, 0, 0, 1, 0))
    c00001 = create_frame((0, 0, 0, 0, 1))

    specs: list[tuple[str, Sequence[bytes], Sequence[bytes], bytes, dict[str, Any]]] = [
        ("CREATE_authoring", (), (c00000,), c00000, {}),
        ("retirement", (c00000,), (c00000, RETIRE), OBSERVE, {}),
        ("observation", (c00000,), (c10000,), OBSERVE, {}),
        ("query", (c00000,), (c01000,), QUERY, {}),
        ("action_value", (c00000,), (c00100,), ACTION0, {"acknowledgment": "direct"}),
        ("QUERY2_value", (UPDATE2, c00000), (UPDATE2, c00010), QUERY2, {}),
        (
            "interpretation",
            (c00000,),
            (c00001,),
            INTERPRET,
            {"table": (0, 1)},
        ),
        ("nonce_use", (c00000,), (c00000, ACTION0), ACTION0, {}),
        ("explanation_existence", (), (b"",), EXPLAIN, {}),
        ("evolution_identity", (), (UPDATE2,), IDENTIFY, {}),
        ("CT2_closure", (), (UPDATE2,), UPDATE1, {}),
        ("CT1_QUERY2", (c00000,), (UPDATE2, c00000), QUERY2, {}),
    ]
    witnesses: list[dict[str, Any]] = []
    all_separate = True
    for name, left_history, right_history, future, options in specs:
        left_state = state_after(left_history)
        right_state = state_after(right_history)
        left = run_request(left_state, future, "detailed", **options)
        right = run_request(right_state, future, "detailed", **options)
        separates = left.trace != right.trace
        all_separate &= separates
        witnesses.append(
            {
                "capability": name,
                "future_hex": future.hex(),
                "left_pre_frames": [raw.hex() for raw in left_history],
                "left_trace": trace_json(left.trace),
                "right_pre_frames": [raw.hex() for raw in right_history],
                "right_trace": trace_json(right.trace),
                "separates": separates,
            }
        )
    return witnesses, all_separate


def power_core_traces() -> dict[str, tuple[tuple[str, bytes], ...]]:
    client = ("C->S", ACTION0)
    f0 = ("F->*", envelope(b"F0"))
    f1 = ("*->F", envelope(b"F1"))
    a0 = ("S->A", envelope(b"A0\x00\x00"))
    ae = ("A->W", envelope(b"AE\x00\x00"))
    a2 = ("S->A", envelope(b"A2\x00"))
    absent = ("A->S", envelope(b"A1\x00\x01"))
    applied = ("A->S", envelope(b"A1\x00\x00"))
    success = ("S->C", envelope(b"\x80"))
    return {
        "receiver_pre": (client, f0, f1, a2, absent, a0, ae, applied, success),
        "receiver_post": (client, a0, ae, f0, f1, a2, applied, success),
        # Section 12.2 permits the crash immediately after the observable A0.
        "after_A0_prefix": (client, a0, f0, f1),
        # Sections 10.2 and 12.2 also expose this point before the subsequent
        # durable receiver record (a one-byte write is still old here).
        "after_AE_before_receiver_write_prefix": (client, a0, ae, f0, f1),
    }


def atomic_quiescent_crash(state: State) -> Outcome:
    return Outcome(
        "atomic-gap-crash",
        (("F->*", envelope(b"F0")), ("*->F", envelope(b"F1"))),
        state,
    )


def is_prefix(prefix: Sequence[Any], whole: Sequence[Any]) -> bool:
    return tuple(whole[: len(prefix)]) == tuple(prefix)


def deliberate_negative_checks(findings: Findings) -> None:
    mutated = CT1[:-1] + b"\x00"
    findings.test(
        "NEGATIVE_MUTATED_CT_REJECTED",
        len(mutated) == len(CT1)
        and mutated != CT1
        and validate(envelope(b"\x60" + u16be(len(mutated)) + mutated))
        == Rejection(RULE["CONTRACT_TEXT"], 5 + len(CT1) - 1),
        "A same-length one-byte CT mutation is rejected at its first offense.",
        "The deliberate CT mutation escaped exact-text validation.",
    )

    try:
        envelope(b"\x00" * 65536)
        oversized_rejected = False
    except ValueError:
        oversized_rejected = True
    findings.test(
        "NEGATIVE_U16_OVERFLOW_REJECTED",
        oversized_rejected,
        "The encoder rejects payloads that do not fit u16be.",
        "The encoder accepted a 65536-byte payload.",
    )

    c0 = state_after((create_frame((0, 0, 0, 0, 0)),))
    c1 = state_after((create_frame((1, 0, 0, 0, 0)),))
    bad_key: Callable[[State], tuple[Any, ...]] = lambda state: (
        state.version,
        state.lifecycle,
        state.bits[1:] if state.bits else None,
        state.used_mask,
        state.provenance,
    )
    left = run_request(c0, OBSERVE, "detailed")
    right = run_request(c1, OBSERVE, "detailed")
    findings.test(
        "NEGATIVE_DROP_O_COLLIDES",
        bad_key(c0) == bad_key(c1) and left.trace != right.trace,
        "A deliberately bad representation dropping live o collides; OBSERVE is the separator.",
        "The deliberate drop-o representation was not falsified.",
        witness={"left": trace_json(left.trace), "right": trace_json(right.trace)},
    )

    v1 = State()
    v2 = state_after((UPDATE2,))
    bad_version_key = lambda state: canonical_state(state, "detailed")[1:]
    left_id = run_request(v1, IDENTIFY, "detailed")
    right_id = run_request(v2, IDENTIFY, "detailed")
    findings.test(
        "NEGATIVE_DROP_VERSION_COLLIDES",
        bad_version_key(v1) == bad_version_key(v2) and left_id.trace != right_id.trace,
        "A deliberately bad representation dropping version collides; IDENTIFY separates it.",
        "The deliberate drop-version representation was not falsified.",
    )


def run_checks(contract_sha256: str) -> dict[str, Any]:
    findings = Findings()
    findings.test(
        "FROZEN_SHA256",
        contract_sha256 == EXPECTED_CONTRACT_SHA256,
        "Frozen contract SHA-256 matches the required digest.",
        "Frozen contract SHA-256 mismatch; no semantic result is authorized.",
        actual=contract_sha256,
        expected=EXPECTED_CONTRACT_SHA256,
    )

    findings.test(
        "CT_BYTES_AND_LENGTHS",
        len(CT1) == 172
        and len(CT2) == 182
        and CT1[-1:] == b"\n"
        and CT2[-1:] == b"\n",
        "CT1/CT2 bytes, terminal LF, lengths, and u16be lengths satisfy static assertions.",
        "A contract-text byte or length assertion failed.",
        ct1_sha256=hashlib.sha256(CT1).hexdigest(),
        ct2_sha256=hashlib.sha256(CT2).hexdigest(),
    )

    displayed = {
        "CREATE_00000": hx(create_frame((0, 0, 0, 0, 0))),
        "RETIRE": hx(RETIRE),
        "ACTION_00": hx(ACTION0),
        "UPDATE_CT1_prefix": hx(UPDATE1[:5]),
        "UPDATE_CT2_prefix": hx(UPDATE2[:5]),
        "timeout": hx(envelope(b"\xff")),
        "fault": hx(envelope(b"F0")),
        "restart": hx(envelope(b"F1")),
    }
    findings.test(
        "DISPLAYED_ENCODINGS",
        displayed
        == {
            "CREATE_00000": "0006100000000000",
            "RETIRE": "000111",
            "ACTION_00": "00023000",
            "UPDATE_CT1_prefix": "00af6000ac",
            "UPDATE_CT2_prefix": "00b96000b6",
            "timeout": "0001ff",
            "fault": "00024630",
            "restart": "00024631",
        },
        "All displayed fixed/request prefix encodings match exact wire bytes.",
        "At least one displayed encoding differs.",
        encodings=displayed,
    )

    # Section 2's universal framing sentence and exact crossing terminator do
    # not admit the malformed raw crossings that Sections 4, 8, and 16 require.
    framing_witnesses = {
        "empty": "",
        "short_declares_one": "0001",
        "excess_after_E_empty": "000000",
    }
    malformed_are_E_messages = all(
        len(bytes.fromhex(raw_hex)) >= 2
        and len(bytes.fromhex(raw_hex))
        == 2 + int.from_bytes(bytes.fromhex(raw_hex)[:2], "big")
        for raw_hex in framing_witnesses.values()
    )
    findings.add(
        "CONTRADICTION_MALFORMED_CROSSING_BOUNDARY",
        "PASS" if malformed_are_E_messages else "FAIL",
        (
            "The required malformed crossings all satisfy the universal E(P) rule."
            if malformed_are_E_messages
            else "Section 2 says every crossing is E(P) and ends at 2+|P| with no alternate termination, but U and h0 require empty, short, and excess raw crossings. An unstated external record boundary is needed to make them crossings."
        ),
        minimal_witnesses=framing_witnesses,
    )

    invalid_ok = True
    invalid_actual: list[dict[str, Any]] = []
    for raw, expected_name, expected_offset in INVALID_REP_EXPECTED:
        actual = validate(raw)
        expected = Rejection(RULE[expected_name], expected_offset)
        invalid_ok &= actual == expected
        invalid_actual.append(
            {
                "raw_hex": raw.hex(),
                "expected": [expected_name, expected_offset],
                "actual": [RULE_NAME.get(actual.rule, "?") if isinstance(actual, Rejection) else "ACCEPT", actual.offset if isinstance(actual, Rejection) else None],
            }
        )
    findings.test(
        "VALIDATION_PRECEDENCE_REPRESENTATIVES",
        invalid_ok,
        "Shortest representatives cover every validation rule and each distinct offset branch.",
        "A validation representative produced the wrong first rule or offset.",
        cases=invalid_actual,
    )

    cardinalities = exact_cardinalities()
    findings.test(
        "SYMBOLIC_U_PARTITION",
        cardinalities["validation_partition"]["sum_equals_U"],
        "The disjoint validation-rule formulas plus 43 P frames sum exactly to U.",
        "The symbolic validation partition does not sum to U.",
    )

    coarse_h0 = run_request(State(), b"", "coarse")
    detailed_h0 = run_request(State(), b"", "detailed")
    detailed_h1 = run_request(State(), b"\x00", "detailed")
    coarse_explain = run_request(coarse_h0.state, EXPLAIN, "coarse")
    detailed_explain_h0 = run_request(detailed_h0.state, EXPLAIN, "detailed")
    detailed_explain_h1 = run_request(detailed_h1.state, EXPLAIN, "detailed")
    explain_ok = (
        response_tail(coarse_h0) == envelope(b"\x82")
        and response_tail(detailed_h0) == envelope(b"\x83\x01\x00")
        and response_tail(detailed_h1) == envelope(b"\x83\x01\x01")
        and response_tail(coarse_explain) == envelope(b"\x95\x01")
        and response_tail(detailed_explain_h0) == envelope(b"\x95\x01\x00\x00\x00")
        and response_tail(detailed_explain_h1)
        == envelope(b"\x95\x01\x01\x00\x01\x00")
    )
    findings.test(
        "REJECTION_AND_EXPLAIN_BYTES",
        explain_ok,
        "Coarse/detailed immediate rejection and h0/h1 EXPLAIN bytes are exact.",
        "A rejection or EXPLAIN byte sequence differs from Sections 8 or 16.",
        coarse_h0=trace_json(coarse_h0.trace),
        detailed_h0_explain=trace_json(detailed_explain_h0.trace),
        detailed_h1_explain=trace_json(detailed_explain_h1.trace),
    )

    malformed_by_opcode = (
        envelope(b"\x10\xff\x00\x00\x00\x00"),
        envelope(b"\x30\xff"),
        envelope(b"\x60\x00\x00"),
        envelope(b"\x40\x00"),
        envelope(b"\x70\x00"),
    )
    replacement_state = State()
    replacement_ok = True
    replacement_cases: list[dict[str, str]] = []
    for malformed in malformed_by_opcode:
        rejected = run_request(replacement_state, malformed, "detailed")
        replacement_state = rejected.state
        detail = replacement_state.provenance
        replacement_ok &= isinstance(detail, Detail) and detail.raw == malformed
        explained = run_request(replacement_state, EXPLAIN, "detailed")
        expected_payload = (
            bytes((0x95, detail.rule, detail.offset)) + detail.length + detail.raw
            if isinstance(detail, Detail)
            else b""
        )
        replacement_ok &= response_tail(explained) == envelope(expected_payload)
        replacement_cases.append(
            {
                "rejected_raw_hex": malformed.hex(),
                "explain_response_hex": response_tail(explained).hex(),
            }
        )
    findings.test(
        "DETAILED_REJECTION_REPLACEMENT_ALL_SHAPES",
        replacement_ok,
        "Malformed CREATE, ACTION, UPDATE, EXPLAIN, and IDENTIFY each replace the complete detailed tuple and are exposed byte-for-byte.",
        "A malformed opcode failed to replace or expose detailed provenance.",
        cases=replacement_cases,
    )

    reject_then_update = state_after((b"", UPDATE2))
    preserved_explain = run_request(reject_then_update, EXPLAIN, "detailed")
    cleared_after_update = replace(reject_then_update, provenance=None)
    cleared_explain = run_request(cleared_after_update, EXPLAIN, "detailed")
    findings.add(
        "SUCCESS_PROVENANCE_AFTER_PRIMARY_TRANSITION",
        "UNKNOWN",
        "Section 6 says success never changes provenance 'unless' its primary transition overlaps no provenance field. Every listed primary transition overlaps none, so the exception permits but does not specify clearing. The instrument's transition results are conditional on preservation.",
        minimal_history=["empty raw rejection", "UPDATE CT2", "EXPLAIN"],
        preserve_response_hex=response_tail(preserved_explain).hex(),
        clear_response_hex=response_tail(cleared_explain).hex(),
    )

    u1_state = run_request(State(), UPDATE1, "detailed")
    u2_state = run_request(State(), UPDATE2, "detailed")
    u2_self = run_request(u2_state.state, UPDATE2, "detailed")
    downgrade = run_request(u2_state.state, UPDATE1, "detailed")
    update_ok = (
        u1_state.state.version == 1
        and u2_state.state.version == 2
        and u2_self.state.version == 2
        and response_tail(u1_state) == envelope(b"\x80")
        and response_tail(u2_state) == envelope(b"\x80")
        and response_tail(u2_self) == envelope(b"\x80")
        and response_tail(downgrade) == envelope(b"\x83\x24\x05")
    )
    findings.test(
        "UPDATE_VERSION_BEHAVIOR",
        update_ok,
        "CT1 self-update, CT1->CT2, CT2 self-update, and detailed downgrade rejection are exact.",
        "UPDATE/version behavior differs from the closed table.",
        downgrade_trace=trace_json(downgrade.trace),
    )

    identify_v1 = run_request(State(), IDENTIFY, "detailed")
    stale_history_state = run_request(identify_v1.state, UPDATE2, "detailed").state
    same_manifest = MANIFESTS[2]
    stale_latest_response = response_tail(identify_v1)
    stale_future = run_request(stale_history_state, UPDATE1, "detailed")
    fresh_future = run_request(identify_v1.state, UPDATE1, "detailed")
    identity_collision = stale_latest_response == response_tail(identify_v1) and (
        stale_future.trace != fresh_future.trace
    )
    findings.add(
        "CONTRADICTION_STALE_LATEST_IDENTIFY",
        "FAIL" if identity_collision else "PASS",
        (
            "With one detailed/atomic manifest, [IDENTIFY] and [IDENTIFY,U2] retain the same latest IDENTIFY response but have CT1 versus CT2 active; future U1 succeeds versus downgrade-rejects. Section 19's stated pair is therefore not a current total identity."
            if identity_collision
            else "The latest IDENTIFY pair remained collision-free after UPDATE."
        ),
        manifest_ascii=same_manifest.decode("ascii"),
        latest_identify_hex=stale_latest_response.hex(),
        ct1_future=trace_json(fresh_future.trace),
        ct2_future=trace_json(stale_future.trace),
    )

    created_i1 = state_after((create_frame((0, 0, 0, 0, 1)),))
    interpret = run_request(created_i1, INTERPRET, "detailed", table=(0, 1))
    created_a0 = state_after((create_frame((0, 0, 0, 0, 0)),))
    action_direct = run_request(created_a0, ACTION0, "detailed", acknowledgment="direct")
    action_timeout = run_request(created_a0, ACTION0, "detailed", acknowledgment="timeout")
    direct_trace_ok = interpret.trace == (
        ("C->S", INTERPRET),
        ("S->I", envelope(b"I0\x01")),
        ("I->S", envelope(b"I1\x00\x01")),
        ("S->C", envelope(b"\x92\x01")),
    ) and action_direct.trace == (
        ("C->S", ACTION0),
        ("S->A", envelope(b"A0\x00\x00")),
        ("A->W", envelope(b"AE\x00\x00")),
        ("A->S", envelope(b"A1\x00\x00")),
        ("S->C", envelope(b"\x80")),
    ) and action_timeout.trace == (
        ("C->S", ACTION0),
        ("S->A", envelope(b"A0\x00\x00")),
        ("A->W", envelope(b"AE\x00\x00")),
        ("T->S", envelope(b"\xff")),
        ("S->A", envelope(b"A2\x00")),
        ("A->S", envelope(b"A1\x00\x00")),
        ("S->C", envelope(b"\x80")),
    )
    findings.test(
        "DIRECT_INTERPRETER_ACTION_TRACES",
        direct_trace_ok,
        "Interpreter plus direct/timeout action traces match every stated no-crash crossing.",
        "A direct interpreter or action trace is out of order or incorrectly encoded.",
        action_direct=trace_json(action_direct.trace),
        action_timeout=trace_json(action_timeout.trace),
        interpreter=trace_json(interpret.trace),
    )

    atomic_cut = state_after((UPDATE2, create_frame((1, 0, 1, 0, 1)), ACTION0))
    atomic_fault = atomic_quiescent_crash(atomic_cut)
    findings.test(
        "ATOMIC_QUIESCENT_CRASH",
        atomic_fault.state == atomic_cut
        and atomic_fault.trace
        == (("F->*", envelope(b"F0")), ("*->F", envelope(b"F1"))),
        "Atomic-scope crash emits exactly F0,F1 and preserves the complete stable cut state.",
        "Atomic-scope crash changed state or fault bytes.",
        trace=trace_json(atomic_fault.trace),
    )

    witnesses, witnesses_ok = separating_witnesses()
    findings.test(
        "STATED_NO_CRASH_WITNESSES",
        witnesses_ok,
        "All twelve unambiguous no-crash seed witnesses separate with the stated frame counts.",
        "At least one stated no-crash seed does not separate.",
    )

    coarse_congruent, coarse_stats = normalized_congruence(
        "coarse", REP_ALPHABET, 5
    )
    detailed_congruent, detailed_stats = normalized_congruence(
        "detailed", REP_ALPHABET, 5
    )
    findings.test(
        "DIRECT_TUPLE_ATOMIC_REPRESENTATIVE_CONGRUENCE",
        coarse_congruent and detailed_congruent,
        "One-step full-trace congruence proves depth-three adaptive equality for every representative-reachable normalization collision.",
        "The mandatory direct tuple has a representative-reachable collision.",
        coarse=coarse_stats,
        detailed=detailed_stats,
        invalid_representatives=len(INVALID_REPS),
        potentially_successful_frames=len(P_FRAMES),
        proof=(
            "All 43 P frames are explicit. For D, the symbolic invalid lemma is exact: "
            "coarse rejection has one effect; detailed provenance contains R injectively. "
            "Equal one-step observations and equal successor keys imply equal adaptive "
            "residuals by induction for the requested three-step future."
        ),
    )

    # Two explicit normalization claims that only become reachable after three
    # successes are checked from a fresh empty future observation.
    retired0 = state_after((create_frame((0, 0, 0, 0, 0)), RETIRE))
    retired1 = state_after((create_frame((1, 1, 1, 1, 1)), RETIRE))
    both0 = state_after((create_frame((0, 0, 0, 0, 0)), ACTION0, ACTION1))
    both1 = state_after((create_frame((0, 0, 1, 0, 0)), ACTION0, ACTION1))
    discarded_ok = (
        canonical_state(retired0, "detailed") == canonical_state(retired1, "detailed")
        and canonical_state(both0, "detailed") == canonical_state(both1, "detailed")
        and all(
            tuple(
                (out.choice, out.trace, canonical_state(out.state, "detailed"))
                for out in request_outcomes(retired0, raw, "detailed")
            )
            == tuple(
                (out.choice, out.trace, canonical_state(out.state, "detailed"))
                for out in request_outcomes(retired1, raw, "detailed")
            )
            and tuple(
                (out.choice, out.trace, canonical_state(out.state, "detailed"))
                for out in request_outcomes(both0, raw, "detailed")
            )
            == tuple(
                (out.choice, out.trace, canonical_state(out.state, "detailed"))
                for out in request_outcomes(both1, raw, "detailed")
            )
            for raw in REP_ALPHABET
        )
    )
    findings.test(
        "DISCARDED_RETIRED_BITS_AND_EXHAUSTED_ACTION",
        discarded_ok,
        "Retired creation/nonce data and live a after both nonces complete are one-step congruent under all representatives.",
        "A field claimed MAY FORGET changes a representative future trace.",
    )

    direct_counts = symbolic_direct_counts()
    universe = (256**256 - 1) // 255
    exact_direct_counts_ok = (
        direct_counts["coarse_pre_cut_at_most_2"]["decimal"] == "165"
        and direct_counts["detailed_pre_cut_at_most_2"]["decimal"]
        == str(34 * universe - 67)
        and direct_counts["detailed_complete_run_at_most_5"]["decimal"]
        == str(228 * universe - 324)
    )
    findings.test(
        "DIRECT_TUPLE_SYMBOLIC_CARDINALITIES",
        exact_direct_counts_ok,
        "Direct-tuple reachable cardinalities are exact symbolic polynomials in Dcount; D was not materialized.",
        "Symbolic direct-tuple cardinality derivation failed.",
        counts=direct_counts,
    )

    # The table in Section 18 says the detailed length and offset MUST SURVIVE,
    # while its own verdict definition makes exactly derivable fields MAY REBUILD.
    # Both are deterministic functions of surviving rule/raw bytes.
    derivation_cases = []
    derivable = True
    for raw, _, _ in INVALID_REP_EXPECTED:
        rejection = validate(raw)
        assert isinstance(rejection, Rejection)
        detail = Detail(rejection.rule, rejection.offset, u16be(len(raw)), raw)
        rebuilt_length = u16be(len(detail.raw))
        rebuilt_offset = derive_offset_from_rule_raw(detail.rule, detail.raw)
        derivable &= rebuilt_length == detail.length and rebuilt_offset == detail.offset
        derivation_cases.append(
            {
                "raw_hex": raw.hex(),
                "rebuilt_length_hex": rebuilt_length.hex(),
                "rebuilt_offset": rebuilt_offset,
            }
        )
    raw_semantic_states = [State(version=version) for version in (1, 2)]
    raw_semantic_states += [
        State(version=version, lifecycle="retired") for version in (1, 2)
    ]
    raw_semantic_states += [
        State(version=version, lifecycle="live", bits=tuple(bits), used_mask=mask)
        for version in (1, 2)
        for bits in itertools.product(BIT, repeat=5)
        for mask in range(4)
    ]
    semantic_details: set[Detail] = set()
    for state in raw_semantic_states:
        for raw in P_FRAMES:
            parsed = validate(raw)
            assert isinstance(parsed, Parsed)
            semantic = semantic_rejection(state, parsed)
            if semantic is not None:
                semantic_details.add(
                    Detail(semantic.rule, semantic.offset, u16be(len(raw)), raw)
                )
    semantic_derivable = len(semantic_details) == 43 and all(
        detail.length == u16be(len(detail.raw))
        and detail.offset == derive_offset_from_rule_raw(detail.rule, detail.raw)
        for detail in semantic_details
    )
    derivable &= semantic_derivable
    findings.add(
        "CONTRADICTION_DETAILED_LENGTH_OFFSET_MUST_SURVIVE",
        "FAIL" if derivable else "UNKNOWN",
        (
            "Section 18 requires detailed length and offset to MUST SURVIVE, but "
            "length=u16be(len(raw)) and offset is exactly recomputable from retained "
            "rule/raw under the closed validator; its own verdict definition therefore "
            "classifies those copies as MAY REBUILD."
            if derivable
            else "The claimed derivation did not cover all representative rules."
        ),
        shortest_length_witness={"raw_hex": "", "derived_length_hex": "0000"},
        semantic_tuple_count=len(semantic_details),
        offset_derivation_cases=derivation_cases,
    )

    # Rule itself is not redundant: the same Q2 raw and same final state can save
    # two different rules in two frames, depending on request order.
    q2_then_u2 = state_after((QUERY2, UPDATE2))
    u2_then_q2 = state_after((UPDATE2, QUERY2))
    rule_non_derivable = (
        q2_then_u2.version == u2_then_q2.version == 2
        and q2_then_u2.lifecycle == u2_then_q2.lifecycle == "virgin"
        and isinstance(q2_then_u2.provenance, Detail)
        and isinstance(u2_then_q2.provenance, Detail)
        and q2_then_u2.provenance.raw == u2_then_q2.provenance.raw == QUERY2
        and q2_then_u2.provenance.offset == u2_then_q2.provenance.offset == 2
        and q2_then_u2.provenance.rule != u2_then_q2.provenance.rule
    )
    findings.test(
        "DETAILED_RULE_GENUINELY_SURVIVES",
        rule_non_derivable,
        "QUERY2;U2 versus U2;QUERY2 gives the same current state/raw/offset but different saved rules.",
        "The rule-independence witness did not form.",
        left=repr(q2_then_u2.provenance),
        right=repr(u2_then_q2.provenance),
    )

    power = power_core_traces()
    section16_shape = (
        len(power["receiver_pre"]) == 9
        and len(power["receiver_post"]) == 8
        and power["receiver_pre"][1:3]
        == (("F->*", envelope(b"F0")), ("*->F", envelope(b"F1")))
        and power["receiver_post"][1:3]
        == (
            ("S->A", envelope(b"A0\x00\x00")),
            ("A->W", envelope(b"AE\x00\x00")),
        )
    )
    findings.test(
        "POWER_SECTION16_STATED_CORE_BYTES",
        section16_shape,
        "The two Section 16 core traces are encoded exactly as written.",
        "A Section 16 core trace was transcribed incorrectly.",
        receiver_pre=trace_json(power["receiver_pre"]),
        receiver_post=trace_json(power["receiver_post"]),
    )

    middle = power["after_A0_prefix"]
    compatible = is_prefix(middle, power["receiver_pre"]) or is_prefix(
        middle, power["receiver_post"]
    )
    findings.add(
        "CONTRADICTION_POWER_AFTER_A0_PREFIX",
        "PASS" if compatible else "FAIL",
        (
            "The after-A0 fault prefix is represented by a reference pre/post outcome."
            if compatible
            else "Section 12.2 permits a crash immediately after observable A0, yielding C,A0,F0,F1. Section 12.3 pre has F0 before A0 and post requires AE before F0; prefix preservation makes neither outcome legal."
        ),
        minimal_prefix=trace_json(middle),
        reference_pre=trace_json(power["receiver_pre"]),
        reference_post=trace_json(power["receiver_post"]),
    )

    after_ae = power["after_AE_before_receiver_write_prefix"]
    findings.add(
        "CONTRADICTION_POWER_AFTER_AE_OLD_BYTE",
        "FAIL",
        (
            "Section 10 orders the durable receiver record after A0 and AE, while "
            "Section 12.2 permits a crash after AE and before/during the first one-byte "
            "record write. Old-or-new atomicity includes the old (absent) byte, but the "
            "Section 12.3 post oracle requires applied and its pre oracle forbids the "
            "already-crossed A0/AE prefix."
        ),
        minimal_prefix=trace_json(after_ae),
        physical_old_state="receiver nonce 00 absent",
        reference_post_state="receiver nonce 00 applied",
    )

    client, a0, ae = power["receiver_post"][:3]
    f0 = ("F->*", envelope(b"F0"))
    f1 = ("*->F", envelope(b"F1"))
    a2 = ("S->A", envelope(b"A2\x00"))
    applied = ("A->S", envelope(b"A1\x00\x00"))
    success = ("S->C", envelope(b"\x80"))
    generic_pre_a1 = (client, a0, ae, f0, f1, applied, success)
    pending_pre_a1 = (client, a0, ae, f0, f1, a2, applied, success)
    generic_post_a1 = (client, a0, ae, applied, f0, f1, success)
    pending_post_a1 = (client, a0, ae, applied, f0, f1, a2, applied, success)
    findings.add(
        "CONTRADICTION_POWER_A1_RECOVERY_ORDER",
        "FAIL",
        "For a crash immediately before A1, the generic crossing-pre oracle resumes with A1, while Section 10.3 says every pending restart begins A2. Immediately after A1 but before local completion, generic crossing-post commits without replay while Section 10.3 again requires A2/A1. No precedence rule selects an exact set.",
        before_A1_generic=trace_json(generic_pre_a1),
        before_A1_pending_rule=trace_json(pending_pre_a1),
        after_A1_generic=trace_json(generic_post_a1),
        after_A1_pending_rule=trace_json(pending_post_a1),
    )

    universe_digits = cardinalities["U"]["decimal_digits"]
    findings.test(
        "ENUMERATION_FINITE_NOT_PHYSICALLY_RUNNABLE",
        universe_digits > 600,
        "The enumerator is mathematically finite/terminating, but U alone has over 600 decimal digits and its explicit residual root cannot fit ordinary finite memory.",
        "The feasibility magnitude calculation was unexpectedly small.",
        finite=True,
        abstract_termination=True,
        ordinary_physical_execution=False,
        minimum_root_entries_expression="Ucount",
        minimum_root_pointer_bytes_expression="8*Ucount",
        caveat="Streaming U needs little counter memory but cannot make the prescribed explicit sorted/hash-consed residual DAG physically runnable.",
    )

    findings.add(
        "FULL_POWER_RESIDUAL_QUOTIENT",
        "UNKNOWN",
        "No unique exhaustive power oracle remains after the receiver-acceptance contradictions; only the exact stated core traces were instantiated.",
        unimplemented=(
            "ambiguous mid-transition recovery sites, physical layouts/write schedules, "
            "and the contradictory A0/AE intermediate sites"
        ),
    )
    findings.add(
        "POWER_VS_ATOMIC_EQUIVALENCE_RELATION",
        "UNKNOWN",
        "Section 13 defines equivalence on boundary histories, but Section 16 argues strict refinement using one atomic-conforming/power-nonconforming realization and does not define the asserted realization-equivalence relation. The direct quiescent tuple itself gains no B field.",
        conditional_cut_counts={
            "atomic_coarse": "165",
            "atomic_detailed": "34*Ucount-67",
            "power_coarse": "165",
            "power_detailed": "34*Ucount-67",
        },
    )
    findings.add(
        "SHORTEST_WITNESS_TOTAL_ORDER",
        "UNKNOWN",
        "The stated minimization key does not define which bytes from two histories, outputs, and nondeterministic sets contribute to total_raw_bytes, nor a serialization/pair orientation for lexicographic_encoding; a unique globally first witness cannot be confirmed.",
        confirmed="the twelve unambiguous seed pairs separate and have the displayed completed-frame counts",
    )
    findings.add(
        "DENSE_ID_AND_RESIDUAL_DAG_PARTITION",
        "UNKNOWN",
        "The authoritative full-U residual DAG and therefore its dense class count/identifier width cannot be physically materialized by this practical falsifier.",
        proved="direct-tuple representative congruence plus an all-D symbolic reduction for atomic no-crash behavior",
        unproved="full power residual equality and global unequal-pair first-witness enumeration",
    )
    findings.add(
        "UNLIKE_PHYSICAL_REALIZATIONS",
        "UNKNOWN",
        "The frozen seed supplies requirements but no fixed-overwrite or append/fold realization to execute or compare.",
    )

    deliberate_negative_checks(findings)

    summary = {status: 0 for status in ("PASS", "FAIL", "UNKNOWN")}
    for item in findings.items:
        summary[item["status"]] += 1

    with open(__file__, "rb") as source_file:
        source_sha256 = hashlib.sha256(source_file.read()).hexdigest()

    strongest = [
        {
            "id": "malformed_crossing_boundary",
            "claim": "the required empty raw crossing cannot be any E(P), whose minimum length is two",
            "raw_hex": "",
        },
        {
            "id": "power_after_A0",
            "claim": "permitted observable prefix belongs to neither mandated pre/post outcome",
            "trace": trace_json(power["after_A0_prefix"]),
        },
        {
            "id": "power_after_AE_old_byte",
            "claim": "observable A0/AE survived while the next receiver byte may legally remain old/absent",
            "trace": trace_json(power["after_AE_before_receiver_write_prefix"]),
        },
        {
            "id": "detailed_length_rebuild",
            "claim": "u16be(length) is exactly u16be(len(raw)); a separate copy cannot satisfy MUST SURVIVE under Section 18's definition",
            "raw_hex": "",
            "rebuilt_hex": "0000",
        },
        {
            "id": "detailed_rule_survival",
            "claim": "Q2;U2 and U2;Q2 converge on CT2 virgin with the same saved raw/offset but different saved rule",
            "left_rule": RULE_NAME[q2_then_u2.provenance.rule],
            "right_rule": RULE_NAME[u2_then_q2.provenance.rule],
        },
        {
            "id": "stale_identify",
            "claim": "IDENTIFY;U2 preserves the CT1 latest IDENTIFY bytes while active state becomes CT2",
            "future": "U1 succeeds from CT1 and rejects from CT2",
        },
    ]

    return {
        "artifact": {
            "contract_path": CONTRACT_PATH,
            "contract_sha256": contract_sha256,
            "expected_contract_sha256": EXPECTED_CONTRACT_SHA256,
            "instrument_path": os.path.abspath(__file__),
            "instrument_sha256": source_sha256,
            "standard_library_only": True,
        },
        "cardinalities": cardinalities,
        "checks": findings.items,
        "direct_tuple_cardinalities": direct_counts,
        "measurement_note": (
            "Wall time and RSS are intentionally excluded from canonical stdout because "
            "they are nondeterministic; measure them externally with /usr/bin/time. The "
            "stdout SHA-256 is likewise reported externally to avoid a self-referential JSON hash."
        ),
        "model_scope": {
            "implemented": (
                "exact codec, validation, preserve-provenance no-crash quiescent "
                "transitions, direct/timeout action, four interpreter tables, atomic "
                "quiescent crash prefix, and uniquely stated Section 16 core traces"
            ),
            "conditional_assumption": (
                "successful requests preserve saved provenance; Section 6's unless-clause "
                "is separately reported UNKNOWN"
            ),
            "not_implemented": (
                "contradictory or non-unique power microstep oracles and absent physical realizations"
            ),
        },
        "representative_corpus": {
            "invalid_count": len(INVALID_REPS),
            "invalid_hex": [raw.hex() for raw in INVALID_REPS],
            "potentially_successful_count": len(P_FRAMES),
            "total_count": len(REP_ALPHABET),
        },
        "stated_witnesses": witnesses,
        "strongest_minimal_witnesses": strongest,
        "summary": summary,
    }


def emit_canonical(value: Any) -> None:
    sys.stdout.write(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    )


def main() -> int:
    try:
        with open(CONTRACT_PATH, "rb") as contract_file:
            contract_bytes = contract_file.read()
    except OSError as error:
        emit_canonical(
            {
                "fatal": "FROZEN_CONTRACT_UNREADABLE",
                "path": CONTRACT_PATH,
                "reason": str(error),
            }
        )
        return 2

    contract_sha256 = hashlib.sha256(contract_bytes).hexdigest()
    if contract_sha256 != EXPECTED_CONTRACT_SHA256:
        emit_canonical(
            {
                "actual_sha256": contract_sha256,
                "expected_sha256": EXPECTED_CONTRACT_SHA256,
                "fatal": "FROZEN_CONTRACT_SHA256_MISMATCH",
                "semantic_checks_executed": False,
            }
        )
        return 2

    report = run_checks(contract_sha256)
    emit_canonical(report)
    return 1 if report["summary"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
