#!/usr/bin/env python3
"""Finite Realization L falsifier for HISTORY-SEED-R01G.

The JSON-lines protocol is deliberately stateless: each operation accepts the
five-byte durable image and returns the resulting image.  This makes every
old/new write outcome visible to, and selectable by, an independent comparison
harness.  Hex values in output are lowercase and contain no separators.

This program implements only the bounded model in the frozen seed.  In
particular, a sixth successful mutator is an unsupported capacity overflow,
not a newly invented public reply.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence


EXPECTED_SEED_SHA256 = (
    "9fcf79f7544e3fe7d11f0830e224635758921f199e4478bb4180ada991629008"
)
SEED_NAME = "HISTORY-SEED-R01G.md"
IMPLEMENTATION = "r01g-realization-l"
PROTOCOL = "r01g-jsonl-v1"
IMAGE_BYTES = 5
ERASED = 0xFF

OP_OBSERVE_ZERO = 0x00
OP_OBSERVE_ONE = 0x01
OP_AUTHOR_I = 0x10
OP_AUTHOR_N = 0x11
OP_RETIRE = 0x20
OP_QUERY = 0x30
OP_ACTION = 0x40
OP_EVOLVE = 0x50
OP_IDENTITY = 0x60
OP_UNKNOWN_SAMPLE = 0xFE

PERSISTED_OPCODES = (
    OP_OBSERVE_ZERO,
    OP_OBSERVE_ONE,
    OP_AUTHOR_I,
    OP_AUTHOR_N,
    OP_RETIRE,
    OP_EVOLVE,
)

MESSAGE_ORDER = (
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


class RealizationError(Exception):
    """Base class for controlled, fail-closed errors."""

    code = "realization_error"


class SeedVerificationError(RealizationError):
    code = "seed_verification_failed"


class ProtocolInputError(RealizationError):
    code = "protocol_input"


class UnsupportedMessage(RealizationError):
    code = "unsupported_message"


class InvalidImage(RealizationError):
    code = "invalid_image"


class CapacityExceeded(RealizationError):
    code = "capacity_exceeded"


class InvalidSchedule(RealizationError):
    code = "invalid_schedule"


class SelfTestFailure(RealizationError):
    code = "self_test_failure"


def _seed_digest() -> str:
    seed_path = Path(__file__).resolve().with_name(SEED_NAME)
    try:
        content = seed_path.read_bytes()
    except OSError as exc:
        raise SeedVerificationError(f"cannot read frozen seed: {exc}") from exc
    actual = hashlib.sha256(content).hexdigest()
    if actual != EXPECTED_SEED_SHA256:
        raise SeedVerificationError(
            f"frozen seed hash is {actual}, expected {EXPECTED_SEED_SHA256}"
        )
    return actual


try:
    VERIFIED_SEED_SHA256: Optional[str] = _seed_digest()
    SEED_BOOT_ERROR: Optional[SeedVerificationError] = None
except SeedVerificationError as _seed_error:
    VERIFIED_SEED_SHA256 = None
    SEED_BOOT_ERROR = _seed_error


def _require_verified_seed() -> None:
    if SEED_BOOT_ERROR is not None or VERIFIED_SEED_SHA256 != EXPECTED_SEED_SHA256:
        if SEED_BOOT_ERROR is not None:
            raise SEED_BOOT_ERROR
        raise SeedVerificationError("frozen seed was not verified")


@dataclass(frozen=True, order=True)
class LogicalState:
    revision: int = 0
    table: Optional[str] = None
    observation: Optional[int] = None

    def __post_init__(self) -> None:
        if self.revision not in (0, 1):
            raise ValueError("revision must be zero or one")
        if self.table not in (None, "I", "N"):
            raise ValueError("table must be absent, I, or N")
        if self.observation not in (None, 0, 1):
            raise ValueError("observation must be absent, zero, or one")

    def as_json(self) -> dict[str, Any]:
        return {
            "observation": self.observation,
            "revision": self.revision,
            "table": self.table,
        }


@dataclass(frozen=True)
class Crossing:
    channel: str
    payload: bytes

    def __post_init__(self) -> None:
        if self.channel not in ("R", "D"):
            raise ValueError("only R and D product crossings are represented")
        if not self.payload:
            raise ValueError("crossing payloads are nonempty")

    def as_json(self) -> dict[str, str]:
        return {"bytes": self.payload.hex(), "channel": self.channel}


def _reply(payload: bytes) -> Crossing:
    return Crossing("R", payload)


def _delivery(payload: bytes) -> Crossing:
    return Crossing("D", payload)


@dataclass(frozen=True)
class RequestPlan:
    name: str
    category: str
    outputs: tuple[Crossing, ...]
    opcode: Optional[int] = None
    new_state: Optional[LogicalState] = None

    @property
    def is_mutation(self) -> bool:
        return self.category == "mutation"

    @property
    def is_successful_action(self) -> bool:
        return self.category == "action"


@dataclass(frozen=True)
class Recovery:
    state: LogicalState
    entries: int


@dataclass(frozen=True)
class PersistentImage:
    cells: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.cells, bytes) or len(self.cells) != IMAGE_BYTES:
            raise InvalidImage("persistent image must contain exactly five bytes")

    @classmethod
    def erased(cls) -> "PersistentImage":
        return cls(bytes([ERASED]) * IMAGE_BYTES)

    @classmethod
    def from_hex(cls, text: Any) -> "PersistentImage":
        if not isinstance(text, str):
            raise ProtocolInputError("image must be a hexadecimal string")
        if len(text) != IMAGE_BYTES * 2:
            raise ProtocolInputError("image hex must contain exactly ten digits")
        if any(character not in "0123456789abcdefABCDEF" for character in text):
            raise ProtocolInputError("image contains a non-hexadecimal digit")
        return cls(bytes(int(text[index : index + 2], 16) for index in range(0, 10, 2)))

    def to_hex(self) -> str:
        return self.cells.hex()

    def append(self, opcode: int, outcome: str) -> tuple["PersistentImage", int]:
        if opcode not in PERSISTED_OPCODES:
            raise InvalidImage(f"cannot persist opcode {opcode:02x}")
        try:
            index = self.cells.index(ERASED)
        except ValueError as exc:
            raise CapacityExceeded("five successful mutators already occupy the image") from exc
        if any(cell != ERASED for cell in self.cells[index:]):
            raise InvalidImage("append target is not a contiguous erased suffix")
        if outcome == "old":
            return self, index
        if outcome != "new":
            raise InvalidSchedule("write outcome must be old or new")
        changed = bytearray(self.cells)
        changed[index] = opcode
        return PersistentImage(bytes(changed)), index


def _table_result(state: LogicalState) -> int:
    if state.table is None or state.observation is None:
        raise ValueError("table result requested without table and observation")
    if state.table == "I":
        return state.observation
    return 1 - state.observation


def _fold_persisted_opcode(state: LogicalState, opcode: int) -> LogicalState:
    """Replay one already-durable successful mutator."""
    if opcode == OP_OBSERVE_ZERO:
        return LogicalState(state.revision, state.table, 0)
    if opcode == OP_OBSERVE_ONE:
        return LogicalState(state.revision, state.table, 1)
    if opcode == OP_AUTHOR_I:
        return LogicalState(state.revision, "I", state.observation)
    if opcode == OP_AUTHOR_N:
        return LogicalState(state.revision, "N", state.observation)
    if opcode == OP_RETIRE:
        if state.table is None:
            raise InvalidImage("persisted retirement has no active interpreter")
        return LogicalState(state.revision, None, state.observation)
    if opcode == OP_EVOLVE:
        if state.revision != 0:
            raise InvalidImage("persisted contract evolution is repeated")
        return LogicalState(1, state.table, state.observation)
    raise InvalidImage(f"persisted opcode {opcode:02x} is not valid")


def recover_image(image: PersistentImage) -> Recovery:
    _require_verified_seed()
    state = LogicalState()
    entries = 0
    erased_suffix = False
    for index, opcode in enumerate(image.cells):
        if opcode == ERASED:
            erased_suffix = True
            continue
        if erased_suffix:
            raise InvalidImage(f"non-erased byte follows erased cell at index {index}")
        if opcode not in PERSISTED_OPCODES:
            raise InvalidImage(f"invalid persisted opcode {opcode:02x} at index {index}")
        state = _fold_persisted_opcode(state, opcode)
        entries += 1
    return Recovery(state, entries)


def parse_client_message(message: bytes) -> str:
    """Parse exactly the eleven bounded byte messages; STOP is not a message."""
    _require_verified_seed()
    if message == b"\x00":
        return "observe_zero"
    if message == b"\x01":
        return "observe_one"
    if message == b"\x10":
        return "author_i"
    if message == b"\x11":
        return "author_n"
    if message == b"\x20":
        return "retire"
    if message == b"\x30":
        return "query"
    if message == b"\x40":
        return "action"
    if message == b"\x50":
        return "evolve"
    if message == b"\x60":
        return "identity"
    if message == b"\xfe":
        return "unknown_sample"
    if message == b"\x30\x00":
        return "malformed_query_sample"
    raise UnsupportedMessage(f"byte message {message.hex()} is outside the bounded alphabet")


def plan_request(state: LogicalState, message: bytes) -> RequestPlan:
    name = parse_client_message(message)
    if name == "observe_zero":
        new_state = LogicalState(state.revision, state.table, 0)
        return RequestPlan(name, "mutation", (_reply(b"\x80\x00"),), OP_OBSERVE_ZERO, new_state)
    if name == "observe_one":
        new_state = LogicalState(state.revision, state.table, 1)
        return RequestPlan(name, "mutation", (_reply(b"\x80\x01"),), OP_OBSERVE_ONE, new_state)
    if name == "author_i":
        new_state = LogicalState(state.revision, "I", state.observation)
        return RequestPlan(name, "mutation", (_reply(b"\x81\x10"),), OP_AUTHOR_I, new_state)
    if name == "author_n":
        new_state = LogicalState(state.revision, "N", state.observation)
        return RequestPlan(name, "mutation", (_reply(b"\x81\x11"),), OP_AUTHOR_N, new_state)
    if name == "retire":
        if state.table is None:
            return RequestPlan(name, "rejection", (_reply(b"\xe0\x05"),))
        new_state = LogicalState(state.revision, None, state.observation)
        return RequestPlan(name, "mutation", (_reply(b"\x82"),), OP_RETIRE, new_state)
    if name == "query":
        if state.table is None:
            return RequestPlan(name, "rejection", (_reply(b"\xe0\x03"),))
        if state.observation is None:
            return RequestPlan(name, "rejection", (_reply(b"\xe0\x04"),))
        return RequestPlan(name, "read", (_reply(bytes((0x83, _table_result(state)))),))
    if name == "action":
        if state.table is None:
            return RequestPlan(name, "rejection", (_reply(b"\xe0\x03"),))
        if state.observation is None:
            return RequestPlan(name, "rejection", (_reply(b"\xe0\x04"),))
        prefix = 0xA0 if state.revision == 0 else 0xA1
        bit = _table_result(state)
        return RequestPlan(
            name,
            "action",
            (_delivery(bytes((prefix, bit))), _reply(b"\x84")),
        )
    if name == "evolve":
        if state.revision == 1:
            return RequestPlan(name, "rejection", (_reply(b"\xe0\x06"),))
        new_state = LogicalState(1, state.table, state.observation)
        return RequestPlan(name, "mutation", (_reply(b"\x85\x01"),), OP_EVOLVE, new_state)
    if name == "identity":
        descriptor = b"\x00\x40\xa0" if state.revision == 0 else b"\x01\x40\xa1"
        return RequestPlan(name, "read", (_reply(b"\x86\x03" + descriptor),))
    if name == "unknown_sample":
        return RequestPlan(name, "rejection", (_reply(b"\xe0\x01"),))
    if name == "malformed_query_sample":
        return RequestPlan(name, "rejection", (_reply(b"\xe0\x02"),))
    raise AssertionError("complete parser produced an unhandled name")


@dataclass(frozen=True)
class StepResult:
    schedule: str
    image: PersistentImage
    state: LogicalState
    outputs: tuple[Crossing, ...]
    crashed: bool
    transition: str
    write: Optional[dict[str, Any]] = None

    def as_json(self) -> dict[str, Any]:
        return {
            "crashed": self.crashed,
            "image": self.image.to_hex(),
            "outputs": [crossing.as_json() for crossing in self.outputs],
            "schedule": self.schedule,
            "state": self.state.as_json(),
            "transition": self.transition,
            "write": self.write,
        }


def schedules_for(image: PersistentImage, message: bytes) -> tuple[str, ...]:
    recovery = recover_image(image)
    plan = plan_request(recovery.state, message)
    if plan.is_mutation:
        if recovery.entries == IMAGE_BYTES:
            raise CapacityExceeded("successful mutation lies beyond the five-write horizon")
        return ("none", "write_old", "write_new", "after_r")
    if plan.is_successful_action:
        return ("none", "before_d", "after_d", "after_r")
    return ("none", "before_r", "after_r")


def execute_step(image: PersistentImage, message: bytes, schedule: str = "none") -> StepResult:
    recovery = recover_image(image)
    plan = plan_request(recovery.state, message)

    if plan.is_mutation:
        allowed = ("none", "write_old", "write_new", "after_r")
        if schedule not in allowed:
            raise InvalidSchedule(f"mutation schedule must be one of {','.join(allowed)}")
        if recovery.entries == IMAGE_BYTES:
            raise CapacityExceeded("successful mutation lies beyond the five-write horizon")
        assert plan.opcode is not None and plan.new_state is not None
        outcome = "old" if schedule == "write_old" else "new"
        durable_image, index = image.append(plan.opcode, outcome)
        durable_state = recover_image(durable_image).state
        expected_state = recovery.state if outcome == "old" else plan.new_state
        if durable_state != expected_state:
            raise InvalidImage("durable write did not recover to its declared old/new state")
        outputs = plan.outputs if schedule in ("none", "after_r") else ()
        return StepResult(
            schedule=schedule,
            image=durable_image,
            state=durable_state,
            outputs=outputs,
            crashed=schedule != "none",
            transition="mutation_noop" if plan.new_state == recovery.state else "mutation",
            write={
                "index": index,
                "new": f"{plan.opcode:02x}",
                "old": "ff",
                "outcome": outcome,
            },
        )

    if plan.is_successful_action:
        allowed = ("none", "before_d", "after_d", "after_r")
        if schedule not in allowed:
            raise InvalidSchedule(f"action schedule must be one of {','.join(allowed)}")
        output_count = {"none": 2, "before_d": 0, "after_d": 1, "after_r": 2}[schedule]
        return StepResult(
            schedule,
            image,
            recovery.state,
            plan.outputs[:output_count],
            schedule != "none",
            "action",
        )

    allowed = ("none", "before_r", "after_r")
    if schedule not in allowed:
        raise InvalidSchedule(f"reply schedule must be one of {','.join(allowed)}")
    outputs = () if schedule == "before_r" else plan.outputs
    return StepResult(
        schedule,
        image,
        recovery.state,
        outputs,
        schedule != "none",
        plan.category,
    )


def perform_restart(image: PersistentImage) -> dict[str, Any]:
    recovery = recover_image(image)
    return {
        "image": image.to_hex(),
        "outputs": [_reply(b"\x88").as_json()],
        "state": recovery.state.as_json(),
    }


def perform_stop(image: PersistentImage, schedule: str = "none") -> dict[str, Any]:
    recovery = recover_image(image)
    if schedule not in ("none", "before_r", "after_r"):
        raise InvalidSchedule("STOP schedule must be none, before_r, or after_r")
    outputs = [] if schedule == "before_r" else [_reply(b"\x87").as_json()]
    return {
        "crashed": schedule != "none",
        "halted": schedule in ("none", "after_r"),
        "image": image.to_hex(),
        "outputs": outputs,
        "schedule": schedule,
        "state": recovery.state.as_json(),
        "write": None,
    }


def _decode_message_hex(value: Any) -> bytes:
    if not isinstance(value, str):
        raise ProtocolInputError("message must be a hexadecimal string")
    if " " in value:
        pieces = value.split(" ")
        if any(len(piece) != 2 for piece in pieces):
            raise ProtocolInputError("spaced message hex requires two digits per byte")
        compact = "".join(pieces)
    else:
        compact = value
    if len(compact) % 2:
        raise ProtocolInputError("message hex must contain complete bytes")
    if any(character not in "0123456789abcdefABCDEF" for character in compact):
        raise ProtocolInputError("message contains a non-hexadecimal digit")
    return bytes(int(compact[index : index + 2], 16) for index in range(0, len(compact), 2))


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _check(condition: bool, label: str) -> None:
    if not condition:
        raise SelfTestFailure(label)


# The self-test oracle below is intentionally a second spelling of the finite
# transition table.  It does not call plan_request or the persistence fold when
# constructing expected states and crossings.
def _reference_mutator(state: LogicalState, opcode: int) -> Optional[LogicalState]:
    if opcode == 0x00:
        return LogicalState(state.revision, state.table, 0)
    if opcode == 0x01:
        return LogicalState(state.revision, state.table, 1)
    if opcode == 0x10:
        return LogicalState(state.revision, "I", state.observation)
    if opcode == 0x11:
        return LogicalState(state.revision, "N", state.observation)
    if opcode == 0x20:
        if state.table is None:
            return None
        return LogicalState(state.revision, None, state.observation)
    if opcode == 0x50:
        if state.revision == 1:
            return None
        return LogicalState(1, state.table, state.observation)
    raise SelfTestFailure(f"reference received non-mutator {opcode:02x}")


@dataclass(frozen=True)
class ReferenceResult:
    name: str
    category: str
    state: LogicalState
    outputs: tuple[tuple[str, bytes], ...]
    opcode: Optional[int] = None


def _reference_evaluate(state: LogicalState, message: bytes) -> ReferenceResult:
    def result_bit() -> int:
        assert state.table is not None and state.observation is not None
        return state.observation if state.table == "I" else 1 - state.observation

    if message == b"\x00":
        return ReferenceResult("observe_zero", "mutation", LogicalState(state.revision, state.table, 0), (("R", b"\x80\x00"),), 0x00)
    if message == b"\x01":
        return ReferenceResult("observe_one", "mutation", LogicalState(state.revision, state.table, 1), (("R", b"\x80\x01"),), 0x01)
    if message == b"\x10":
        return ReferenceResult("author_i", "mutation", LogicalState(state.revision, "I", state.observation), (("R", b"\x81\x10"),), 0x10)
    if message == b"\x11":
        return ReferenceResult("author_n", "mutation", LogicalState(state.revision, "N", state.observation), (("R", b"\x81\x11"),), 0x11)
    if message == b"\x20":
        if state.table is None:
            return ReferenceResult("retire", "rejection", state, (("R", b"\xe0\x05"),))
        return ReferenceResult("retire", "mutation", LogicalState(state.revision, None, state.observation), (("R", b"\x82"),), 0x20)
    if message == b"\x30":
        if state.table is None:
            return ReferenceResult("query", "rejection", state, (("R", b"\xe0\x03"),))
        if state.observation is None:
            return ReferenceResult("query", "rejection", state, (("R", b"\xe0\x04"),))
        return ReferenceResult("query", "read", state, (("R", bytes((0x83, result_bit()))),))
    if message == b"\x40":
        if state.table is None:
            return ReferenceResult("action", "rejection", state, (("R", b"\xe0\x03"),))
        if state.observation is None:
            return ReferenceResult("action", "rejection", state, (("R", b"\xe0\x04"),))
        prefix = 0xA0 if state.revision == 0 else 0xA1
        return ReferenceResult("action", "action", state, (("D", bytes((prefix, result_bit()))), ("R", b"\x84")))
    if message == b"\x50":
        if state.revision == 1:
            return ReferenceResult("evolve", "rejection", state, (("R", b"\xe0\x06"),))
        return ReferenceResult("evolve", "mutation", LogicalState(1, state.table, state.observation), (("R", b"\x85\x01"),), 0x50)
    if message == b"\x60":
        descriptor = b"\x00\x40\xa0" if state.revision == 0 else b"\x01\x40\xa1"
        return ReferenceResult("identity", "read", state, (("R", b"\x86\x03" + descriptor),))
    if message == b"\xfe":
        return ReferenceResult("unknown_sample", "rejection", state, (("R", b"\xe0\x01"),))
    if message == b"\x30\x00":
        return ReferenceResult("malformed_query_sample", "rejection", state, (("R", b"\xe0\x02"),))
    raise UnsupportedMessage("reference input is outside the bounded alphabet")


def _event_pairs(events: Iterable[Crossing]) -> tuple[tuple[str, bytes], ...]:
    return tuple((event.channel, event.payload) for event in events)


def _reference_recover_cells(cells: bytes) -> Optional[LogicalState]:
    if len(cells) != 5:
        return None
    state = LogicalState()
    saw_erased = False
    for opcode in cells:
        if opcode == 0xFF:
            saw_erased = True
            continue
        if saw_erased or opcode not in PERSISTED_OPCODES:
            return None
        next_state = _reference_mutator(state, opcode)
        if next_state is None:
            return None
        state = next_state
    return state


def _class_code(state: LogicalState) -> int:
    table_number = {None: 0, "I": 1, "N": 2}[state.table]
    observation_number = {None: 0, 0: 1, 1: 2}[state.observation]
    return 9 * state.revision + 3 * table_number + observation_number


def _reference_word(state: LogicalState, word: Sequence[bytes]) -> tuple[LogicalState, tuple[tuple[str, bytes], ...]]:
    outputs: list[tuple[str, bytes]] = []
    for message in word:
        result = _reference_evaluate(state, message)
        outputs.extend(result.outputs)
        if result.category == "mutation":
            state = result.state
    return state, tuple(outputs)


def _reachable_images() -> dict[bytes, LogicalState]:
    initial = bytes([0xFF]) * 5
    reachable: dict[bytes, LogicalState] = {initial: LogicalState()}
    frontier: list[tuple[bytes, LogicalState, int]] = [(initial, LogicalState(), 0)]
    while frontier:
        cells, state, depth = frontier.pop()
        if depth == 5:
            continue
        for opcode in PERSISTED_OPCODES:
            next_state = _reference_mutator(state, opcode)
            if next_state is None:
                continue
            changed = bytearray(cells)
            changed[depth] = opcode
            next_cells = bytes(changed)
            _check(next_cells not in reachable, "two mutation words encoded to one L image")
            reachable[next_cells] = next_state
            frontier.append((next_cells, next_state, depth + 1))
    return reachable


def _assert_restart(image: PersistentImage, expected_state: LogicalState) -> None:
    restarted = perform_restart(image)
    _check(restarted["state"] == expected_state.as_json(), "restart recovered the wrong state")
    _check(restarted["outputs"] == [{"bytes": "88", "channel": "R"}], "restart did not emit only R!88")


def run_self_test() -> dict[str, Any]:
    _require_verified_seed()
    counts: Counter[str] = Counter()

    expected_names = (
        "observe_zero",
        "observe_one",
        "author_i",
        "author_n",
        "retire",
        "query",
        "action",
        "evolve",
        "identity",
        "unknown_sample",
        "malformed_query_sample",
    )
    for message, expected_name in zip(MESSAGE_ORDER, expected_names):
        _check(parse_client_message(message) == expected_name, "bounded parser mapping differs")
        counts["parser_accepted_messages"] += 1
    for unsupported in (b"", b"\x02", b"\xff", b"\x30\x01", b"\x00\x01", b"\x30\x00\x00"):
        try:
            parse_client_message(unsupported)
        except UnsupportedMessage:
            counts["parser_rejected_samples"] += 1
        else:
            raise SelfTestFailure("parser accepted an unsupported sample")

    reachable = _reachable_images()
    by_length: Counter[int] = Counter()
    reachable_states: set[LogicalState] = set()
    for cells, expected_state in sorted(reachable.items()):
        image = PersistentImage(cells)
        recovered = recover_image(image)
        _check(recovered.state == expected_state, "recovery disagrees with independent replay")
        _check(image.to_hex() == cells.hex(), "persistent serializer is not canonical")
        _check(PersistentImage.from_hex(image.to_hex()) == image, "persistent serializer does not round trip")
        by_length[recovered.entries] += 1
        reachable_states.add(recovered.state)
        counts["reachable_images"] += 1
        _assert_restart(image, expected_state)
        counts["restart_checks"] += 1

        for message in MESSAGE_ORDER:
            reference = _reference_evaluate(expected_state, message)
            plan = plan_request(expected_state, message)
            _check(plan.name == reference.name, "request name disagrees with reference")
            _check(plan.category == reference.category, "request category disagrees with reference")
            _check(_event_pairs(plan.outputs) == reference.outputs, "fault-free outputs disagree with reference")
            if reference.category == "mutation":
                _check(plan.opcode == reference.opcode, "mutator opcode disagrees with reference")
                _check(plan.new_state == reference.state, "mutator state disagrees with reference")
            counts["message_image_pairs"] += 1

            if reference.category == "mutation":
                counts["successful_mutation_transitions"] += 1
                if reference.state == expected_state:
                    counts["semantic_noop_transitions"] += 1
                if recovered.entries == 5:
                    for schedule in ("none", "write_old", "write_new", "after_r"):
                        try:
                            execute_step(image, message, schedule)
                        except CapacityExceeded:
                            counts["capacity_schedule_refusals"] += 1
                        else:
                            raise SelfTestFailure("a sixth successful mutator exceeded L capacity")
                    counts["capacity_transition_refusals"] += 1
                    continue

                new_cells = bytearray(cells)
                assert reference.opcode is not None
                new_cells[recovered.entries] = reference.opcode
                expected_new_image = PersistentImage(bytes(new_cells))
                for schedule in ("none", "write_old", "write_new", "after_r"):
                    stepped = execute_step(image, message, schedule)
                    _check(stepped.write is not None, "successful L mutator omitted its byte write")
                    _check(stepped.write["index"] == recovered.entries, "L write used the wrong append cell")
                    if schedule == "write_old":
                        _check(stepped.image == image and stepped.state == expected_state, "old write outcome changed durable state")
                        _check(stepped.outputs == () and stepped.crashed, "old write outcome leaked a reply")
                        counts["write_old_outcomes"] += 1
                    elif schedule == "write_new":
                        _check(stepped.image == expected_new_image and stepped.state == reference.state, "new write outcome did not survive")
                        _check(stepped.outputs == () and stepped.crashed, "new write outcome leaked a reply")
                        counts["write_new_outcomes"] += 1
                    else:
                        _check(stepped.image == expected_new_image and stepped.state == reference.state, "completed write recovered incorrectly")
                        _check(_event_pairs(stepped.outputs) == reference.outputs, "completed mutator reply differs")
                        _check(stepped.crashed == (schedule == "after_r"), "mutator crash flag differs")
                        counts["completed_write_schedules"] += 1
                    if reference.state == expected_state and schedule != "write_old":
                        _check(stepped.image != image, "semantic no-op failed to append its opcode")
                    if schedule != "none":
                        _assert_restart(stepped.image, stepped.state)
                        counts["restart_checks"] += 1
                continue

            if reference.category == "action":
                prefixes = {"none": 2, "before_d": 0, "after_d": 1, "after_r": 2}
                action_results: dict[str, StepResult] = {}
                for schedule, length in prefixes.items():
                    stepped = execute_step(image, message, schedule)
                    action_results[schedule] = stepped
                    _check(_event_pairs(stepped.outputs) == reference.outputs[:length], "action crash projection is not an exact prefix")
                    _check(stepped.image == image and stepped.state == expected_state, "action changed persistence")
                    _check(stepped.write is None, "action issued a persistent write")
                    _check(stepped.crashed == (schedule != "none"), "action crash flag differs")
                    counts["action_schedule_cases"] += 1
                    if schedule != "none":
                        _assert_restart(stepped.image, expected_state)
                        counts["restart_checks"] += 1
                _check([event.channel for event in action_results["none"].outputs] == ["D", "R"], "action did not cross D before R")
                for uncertain in ("before_d", "after_d"):
                    _assert_restart(action_results[uncertain].image, expected_state)
                    retry = execute_step(action_results[uncertain].image, message, "none")
                    delivered_before = sum(event.channel == "D" for event in action_results[uncertain].outputs)
                    delivered_retry = sum(event.channel == "D" for event in retry.outputs)
                    _check(delivered_retry == 1, "client retry did not create exactly one new attempt")
                    _check(delivered_before in (0, 1), "interrupted occurrence emitted too many attempts")
                    counts["action_retry_cases"] += 1
                counts["successful_action_transitions"] += 1
                continue

            for schedule, expected_length in (("none", 1), ("before_r", 0), ("after_r", 1)):
                stepped = execute_step(image, message, schedule)
                _check(_event_pairs(stepped.outputs) == reference.outputs[:expected_length], "reply-only crash projection differs")
                _check(stepped.image == image and stepped.state == expected_state, "read or rejection changed persistence")
                _check(stepped.write is None, "read or rejection issued a write")
                _check(stepped.crashed == (schedule != "none"), "reply-only crash flag differs")
                counts["reply_schedule_cases"] += 1
                if schedule != "none":
                    _assert_restart(stepped.image, expected_state)
                    counts["restart_checks"] += 1
            if reference.category == "rejection":
                counts["rejected_transitions"] += 1
            else:
                counts["read_only_successes"] += 1

    _check(len(reachable_states) == 18, "full five-message horizon did not reach all eighteen states")
    _check(set(_class_code(state) for state in reachable_states) == set(range(18)), "reachable class codes are not 00..11 hex")

    alphabet_valid_images: set[bytes] = set()
    alphabet_invalid = 0
    image_alphabet = PERSISTED_OPCODES + (ERASED,)
    for cells_tuple in itertools.product(image_alphabet, repeat=5):
        cells = bytes(cells_tuple)
        expected = _reference_recover_cells(cells)
        try:
            actual = recover_image(PersistentImage(cells)).state
        except InvalidImage:
            actual = None
        _check(actual == expected, "scanner classification differs on valid/ff alphabet")
        if expected is None:
            alphabet_invalid += 1
        else:
            alphabet_valid_images.add(cells)
        counts["alphabet_image_checks"] += 1
    _check(alphabet_valid_images == set(reachable), "scanner-valid images differ from reachable append histories")
    counts["alphabet_invalid_images"] = alphabet_invalid

    invalid_bytes = tuple(value for value in range(256) if value not in image_alphabet)
    for position in range(5):
        for invalid_byte in invalid_bytes:
            cells = bytes([OP_OBSERVE_ZERO]) * position + bytes([invalid_byte]) + bytes([ERASED]) * (4 - position)
            try:
                recover_image(PersistentImage(cells))
            except InvalidImage:
                counts["invalid_opcode_position_checks"] += 1
            else:
                raise SelfTestFailure("scanner accepted a byte outside the persisted alphabet")

    for length in range(11):
        if length == 5:
            continue
        try:
            PersistentImage(bytes([ERASED]) * length)
        except InvalidImage:
            counts["invalid_binary_length_checks"] += 1
        else:
            raise SelfTestFailure("persistent image accepted the wrong binary length")
    for invalid_hex in ("", "ff", "fffffffff", "ffffffffffff", "gggggggggg", "ff ff ff ff ff"):
        try:
            PersistentImage.from_hex(invalid_hex)
        except ProtocolInputError:
            counts["invalid_hex_image_checks"] += 1
        else:
            raise SelfTestFailure("persistent serializer accepted malformed image hex")

    stop_image = PersistentImage.erased()
    for schedule, expected_outputs in (("none", 1), ("before_r", 0), ("after_r", 1)):
        stopped = perform_stop(stop_image, schedule)
        _check(len(stopped["outputs"]) == expected_outputs, "STOP crash projection differs")
        if expected_outputs:
            _check(stopped["outputs"] == [{"bytes": "87", "channel": "R"}], "STOP reply differs")
        counts["stop_schedule_cases"] += 1

    class_histogram: Counter[int] = Counter()
    revision_histogram: Counter[int] = Counter()
    cut_histories = [()] + [(message,) for message in MESSAGE_ORDER]
    cut_histories.extend((first, second) for first in MESSAGE_ORDER for second in MESSAGE_ORDER)
    for history in cut_histories:
        state, _ = _reference_word(LogicalState(), history)
        class_histogram[_class_code(state)] += 1
        revision_histogram[state.revision] += 1
    expected_histogram = {
        0: 45, 1: 15, 2: 15, 3: 14, 4: 2, 5: 2, 6: 14,
        7: 2, 8: 2, 9: 14, 10: 2, 11: 2, 12: 2, 15: 2,
    }
    _check(dict(class_histogram) == expected_histogram, "133-history cut partition differs")
    _check(revision_histogram == Counter({0: 111, 1: 22}), "cut revision counts differ")
    counts["cut_histories"] = len(cut_histories)
    counts["cut_classes"] = len(class_histogram)

    future_words: list[tuple[bytes, ...]] = [()]
    future_words.extend((message,) for message in MESSAGE_ORDER)
    future_words.extend((first, second) for first in MESSAGE_ORDER for second in MESSAGE_ORDER)
    max_witness_depth = 0
    ordered_states = sorted(reachable_states, key=_class_code)
    for left_index, left in enumerate(ordered_states):
        for right in ordered_states[left_index + 1 :]:
            witness_depth: Optional[int] = None
            for word in future_words:
                _, left_outputs = _reference_word(left, word)
                _, right_outputs = _reference_word(right, word)
                if left_outputs != right_outputs:
                    witness_depth = len(word)
                    break
            _check(witness_depth is not None and witness_depth <= 2, "unequal states lacked a two-message witness")
            max_witness_depth = max(max_witness_depth, witness_depth)
            counts["distinguished_state_pairs"] += 1
    _check(counts["distinguished_state_pairs"] == 153, "did not check all eighteen-class merges")
    _check(max_witness_depth == 2, "maximum shortest state witness is not two")

    _check(sum(by_length.values()) == len(reachable), "reachable image length accounting differs")
    _check(counts["write_old_outcomes"] == counts["write_new_outcomes"], "old/new write schedules are unbalanced")
    _check(counts["semantic_noop_transitions"] > 0, "no semantic no-op was exercised")
    _check(counts["rejected_transitions"] > 0, "no rejected transition was exercised")
    _check(counts["capacity_transition_refusals"] > 0, "capacity bound was not reached")

    return {
        "counts": dict(sorted(counts.items())),
        "implementation": IMPLEMENTATION,
        "max_distinguishing_future_messages": max_witness_depth,
        "ok": True,
        "protocol": PROTOCOL,
        "reachable_images_by_log_length": {str(key): by_length[key] for key in range(6)},
        "seed_sha256": EXPECTED_SEED_SHA256,
    }


def _require_keys(request: dict[str, Any], required: set[str], optional: set[str] = set()) -> None:
    missing = required - set(request)
    extra = set(request) - required - optional
    if missing:
        raise ProtocolInputError(f"missing keys: {','.join(sorted(missing))}")
    if extra:
        raise ProtocolInputError(f"unexpected keys: {','.join(sorted(extra))}")


def _description() -> dict[str, Any]:
    return {
        "commands": ["describe", "recover", "restart", "step", "enumerate", "stop", "self_test"],
        "image_bytes": IMAGE_BYTES,
        "initial_image": PersistentImage.erased().to_hex(),
        "implementation": IMPLEMENTATION,
        "message_order": [message.hex() for message in MESSAGE_ORDER],
        "protocol": PROTOCOL,
        "schedules": {
            "action_success": ["none", "before_d", "after_d", "after_r"],
            "mutation_success": ["none", "write_old", "write_new", "after_r"],
            "reply_only": ["none", "before_r", "after_r"],
        },
        "seed_sha256": EXPECTED_SEED_SHA256,
    }


def dispatch_protocol(request: Any) -> dict[str, Any]:
    _require_verified_seed()
    if not isinstance(request, dict):
        raise ProtocolInputError("each JSON line must be an object")
    operation = request.get("op")
    if not isinstance(operation, str):
        raise ProtocolInputError("op must be a string")

    if operation == "describe":
        _require_keys(request, {"op"})
        return {"ok": True, "result": _description()}
    if operation == "recover":
        _require_keys(request, {"op", "image"})
        image = PersistentImage.from_hex(request["image"])
        recovery = recover_image(image)
        return {
            "ok": True,
            "result": {"entries": recovery.entries, "image": image.to_hex(), "state": recovery.state.as_json()},
        }
    if operation == "restart":
        _require_keys(request, {"op", "image"})
        image = PersistentImage.from_hex(request["image"])
        return {"ok": True, "result": perform_restart(image)}
    if operation in ("step", "enumerate"):
        optional = {"schedule"} if operation == "step" else set()
        _require_keys(request, {"op", "image", "message"}, optional)
        image = PersistentImage.from_hex(request["image"])
        message = _decode_message_hex(request["message"])
        parse_client_message(message)
        if operation == "step":
            schedule = request.get("schedule", "none")
            if not isinstance(schedule, str):
                raise ProtocolInputError("schedule must be a string")
            return {"ok": True, "result": execute_step(image, message, schedule).as_json()}
        results = [execute_step(image, message, schedule).as_json() for schedule in schedules_for(image, message)]
        return {"ok": True, "result": {"outcomes": results}}
    if operation == "stop":
        _require_keys(request, {"op", "image"}, {"schedule"})
        image = PersistentImage.from_hex(request["image"])
        schedule = request.get("schedule", "none")
        if not isinstance(schedule, str):
            raise ProtocolInputError("schedule must be a string")
        return {"ok": True, "result": perform_stop(image, schedule)}
    if operation == "self_test":
        _require_keys(request, {"op"})
        return run_self_test()
    raise ProtocolInputError(f"unknown op {operation!r}")


def _error_object(exc: BaseException) -> dict[str, Any]:
    code = exc.code if isinstance(exc, RealizationError) else "internal_error"
    return {"error": {"code": code, "message": str(exc)}, "ok": False}


def _run_protocol() -> int:
    for line_number, line in enumerate(sys.stdin, 1):
        try:
            request = json.loads(line)
            response = dispatch_protocol(request)
        except json.JSONDecodeError as exc:
            response = _error_object(ProtocolInputError(f"line {line_number}: invalid JSON: {exc.msg}"))
        except Exception as exc:
            response = _error_object(exc)
        sys.stdout.write(_canonical_json(response) + "\n")
        sys.stdout.flush()
    return 0


def main(argv: Sequence[str]) -> int:
    if SEED_BOOT_ERROR is not None:
        sys.stderr.write(_canonical_json(_error_object(SEED_BOOT_ERROR)) + "\n")
        return 3
    if list(argv) == ["--self-test"]:
        try:
            report = run_self_test()
        except Exception as exc:
            report = _error_object(exc)
            report["implementation"] = IMPLEMENTATION
            report["seed_sha256"] = EXPECTED_SEED_SHA256
            sys.stdout.write(_canonical_json(report) + "\n")
            return 1
        sys.stdout.write(_canonical_json(report) + "\n")
        return 0
    if list(argv) == ["--describe"]:
        sys.stdout.write(_canonical_json({"ok": True, "result": _description()}) + "\n")
        return 0
    if argv:
        error = ProtocolInputError("usage: r01g_realization_l.py [--self-test|--describe]")
        sys.stderr.write(_canonical_json(_error_object(error)) + "\n")
        return 2
    return _run_protocol()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
