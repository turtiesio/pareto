#!/usr/bin/env python3
"""Finite Realization S falsifier for HISTORY-SEED-R01G.

This program implements only the frozen, bounded one-byte packed-quotient
experiment.  It deliberately provides no behavior for arbitrary messages,
concurrency, additional crashes, receiver effects, or storage faults other
than the specified one-byte old/new outcome.

With no command-line mode, stdin and stdout form a stateful, line-oriented
JSON protocol.  Every input line receives exactly one canonical JSON line.
Use ``--protocol-help`` for its machine-readable description and
``--self-test`` for the deterministic exhaustive report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


EXPECTED_SEED_SHA256 = "9fcf79f7544e3fe7d11f0830e224635758921f199e4478bb4180ada991629008"
SEED_FILENAME = "HISTORY-SEED-R01G.md"
PROTOCOL_VERSION = "r01g-realization-s-jsonl-v1"


class SeedIntegrityError(RuntimeError):
    """The sole specification input is absent or has the wrong digest."""


class ProtocolError(ValueError):
    """A request is outside the deliberately finite test protocol."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class InvalidImage(ValueError):
    """A persistent image is not exactly one valid packed quotient byte."""


class SelfTestFailure(AssertionError):
    """An exhaustive check disagreed with an independently stated expectation."""


def _verify_seed() -> str:
    path = Path(__file__).resolve().with_name(SEED_FILENAME)
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise SeedIntegrityError(f"cannot read frozen seed {path}: {exc}") from exc
    actual = hashlib.sha256(content).hexdigest()
    if actual != EXPECTED_SEED_SHA256:
        raise SeedIntegrityError(
            f"frozen seed hash mismatch: expected {EXPECTED_SEED_SHA256}, got {actual}"
        )
    return actual


# Verification occurs before the implementation or protocol can be used.
ACTIVE_SEED_SHA256 = _verify_seed()


MESSAGE_ORDER: Tuple[bytes, ...] = (
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

MESSAGE_NAMES: Mapping[bytes, str] = {
    b"\x00": "observe_zero",
    b"\x01": "observe_one",
    b"\x10": "author_I",
    b"\x11": "author_N",
    b"\x20": "retire",
    b"\x30": "query",
    b"\x40": "action",
    b"\x50": "evolve",
    b"\x60": "identity",
    b"\xfe": "unknown_sample",
    b"\x30\x00": "malformed_query_sample",
}

STATE_CHANGE_FAULTS = ("none", "write_old", "write_new", "after_reply")
NO_WRITE_FAULTS = ("none", "before_reply", "after_reply")
ACTION_FAULTS = ("none", "before_delivery", "after_delivery", "after_reply")
HALF_CLOSE_FAULTS = ("none",)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def byte_text(data: bytes) -> str:
    return " ".join(f"{value:02x}" for value in data)


def byte_cell(value: int) -> str:
    return f"{value:02x}"


def _hex_nibble(character: str) -> int:
    if "0" <= character <= "9":
        return ord(character) - ord("0")
    lowered = character.lower()
    if "a" <= lowered <= "f":
        return ord(lowered) - ord("a") + 10
    raise ProtocolError("bad_hex", f"non-hexadecimal character {character!r}")


def _parse_hex_tokens(text: Any, field: str) -> bytes:
    if not isinstance(text, str):
        raise ProtocolError("bad_field_type", f"{field} must be a string")
    if not text or text.startswith(" ") or text.endswith(" ") or "  " in text:
        raise ProtocolError("bad_hex", f"{field} must use two-digit bytes separated by one space")
    tokens = text.split(" ")
    output = bytearray()
    for token in tokens:
        if len(token) != 2:
            raise ProtocolError("bad_hex", f"{field} contains a token that is not two digits")
        output.append((_hex_nibble(token[0]) << 4) | _hex_nibble(token[1]))
    return bytes(output)


def parse_message(text: Any) -> bytes:
    message = _parse_hex_tokens(text, "message")
    if message not in MESSAGE_NAMES:
        raise ProtocolError("unsupported_message", "message is outside the frozen eleven-message alphabet")
    return message


def parse_image(text: Any) -> int:
    encoded = _parse_hex_tokens(text, "image")
    if len(encoded) != 1:
        raise ProtocolError("bad_image_width", "persistent image must contain exactly one byte")
    return encoded[0]


@dataclass(frozen=True)
class QuotientState:
    revision: int
    interpreter: int
    observation: int

    def __post_init__(self) -> None:
        if type(self.revision) is not int or self.revision not in (0, 1):
            raise ValueError("revision must be 0 or 1")
        if type(self.interpreter) is not int or self.interpreter not in (0, 1, 2):
            raise ValueError("interpreter must encode absent, I, or N as 0, 1, or 2")
        if type(self.observation) is not int or self.observation not in (0, 1, 2):
            raise ValueError("observation must encode absent, zero, or one as 0, 1, or 2")


def encode_persistent(state: QuotientState) -> int:
    """Encode the complete quotient into its one-byte persistent image."""
    value = 9 * state.revision + 3 * state.interpreter + state.observation
    if not 0 <= value <= 0x11:
        raise InvalidImage("encoder produced a value outside 00..11")
    return value


def recover_image(raw: Any) -> QuotientState:
    """Read and range-check exactly one persistent byte, then decode it."""
    if type(raw) is not int or not 0 <= raw <= 0xFF:
        raise InvalidImage("persistent image is not one byte")
    if raw > 0x11:
        raise InvalidImage(f"persistent image {raw:02x} is outside 00..11")
    revision, remainder = divmod(raw, 9)
    interpreter, observation = divmod(remainder, 3)
    state = QuotientState(revision, interpreter, observation)
    if encode_persistent(state) != raw:
        raise InvalidImage("persistent image failed canonical round trip")
    return state


def derived_state(state: QuotientState) -> Dict[str, Any]:
    interpreter = ("-", "I", "N")[state.interpreter]
    observation: Optional[int] = None if state.observation == 0 else state.observation - 1
    return {
        "class": encode_persistent(state),
        "interpreter": interpreter,
        "observation": observation,
        "revision": state.revision,
    }


@dataclass(frozen=True)
class Transition:
    classification: str
    state: QuotientState
    reply: bytes
    delivery: Optional[bytes] = None


def _interpreted_bit(state: QuotientState) -> int:
    observed = state.observation - 1
    return observed if state.interpreter == 1 else 1 - observed


def transition(state: QuotientState, message: bytes) -> Transition:
    """Apply one exact message to a recovered quotient state."""
    r = state.revision
    t = state.interpreter
    o = state.observation

    if message == b"\xfe":
        return Transition("rejected", state, b"\xe0\x01")
    if message == b"\x30\x00":
        return Transition("rejected", state, b"\xe0\x02")
    if message == b"\x00":
        target = QuotientState(r, t, 1)
        kind = "no_op" if target == state else "state_change"
        return Transition(kind, target, b"\x80\x00")
    if message == b"\x01":
        target = QuotientState(r, t, 2)
        kind = "no_op" if target == state else "state_change"
        return Transition(kind, target, b"\x80\x01")
    if message == b"\x10":
        target = QuotientState(r, 1, o)
        kind = "no_op" if target == state else "state_change"
        return Transition(kind, target, b"\x81\x10")
    if message == b"\x11":
        target = QuotientState(r, 2, o)
        kind = "no_op" if target == state else "state_change"
        return Transition(kind, target, b"\x81\x11")
    if message == b"\x20":
        if t == 0:
            return Transition("rejected", state, b"\xe0\x05")
        return Transition("state_change", QuotientState(r, 0, o), b"\x82")
    if message == b"\x30":
        if t == 0:
            return Transition("rejected", state, b"\xe0\x03")
        if o == 0:
            return Transition("rejected", state, b"\xe0\x04")
        return Transition("readonly", state, bytes((0x83, _interpreted_bit(state))))
    if message == b"\x40":
        if t == 0:
            return Transition("rejected", state, b"\xe0\x03")
        if o == 0:
            return Transition("rejected", state, b"\xe0\x04")
        delivery = bytes((0xA0 + r, _interpreted_bit(state)))
        return Transition("readonly", state, b"\x84", delivery)
    if message == b"\x50":
        if r == 1:
            return Transition("rejected", state, b"\xe0\x06")
        return Transition("state_change", QuotientState(1, t, o), b"\x85\x01")
    if message == b"\x60":
        descriptor = bytes((r, 0x40, 0xA0 + r))
        return Transition("readonly", state, b"\x86\x03" + descriptor)
    raise ProtocolError("unsupported_message", "message is outside the frozen eleven-message alphabet")


def _client_event(message: bytes) -> str:
    return "C!" + byte_text(message)


def _reply_event(reply: bytes) -> str:
    return "R!" + byte_text(reply)


def _delivery_event(delivery: bytes) -> str:
    return "D!" + byte_text(delivery)


class Simulator:
    """One-byte physical realization plus explicit crash/crossing instrumentation."""

    def __init__(self) -> None:
        self.image = 0
        self.status = "running"
        self.crash_used = False

    def _base(self, op: str, events: Sequence[str], writes: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        state = recover_image(self.image)
        return {
            "crash_used": self.crash_used,
            "derived_state": derived_state(state),
            "events": list(events),
            "image": byte_cell(self.image),
            "ok": True,
            "op": op,
            "status": self.status,
            "writes": list(writes),
        }

    def reset(self) -> Dict[str, Any]:
        self.image = 0
        self.status = "running"
        self.crash_used = False
        return self._base("reset", (), ())

    def boot_image(self, image_text: Any) -> Dict[str, Any]:
        candidate = parse_image(image_text)
        state = recover_image(candidate)
        self.image = encode_persistent(state)
        self.status = "running"
        self.crash_used = False
        result = self._base("boot", (), ())
        result["reads"] = 1
        return result

    def inspect(self) -> Dict[str, Any]:
        recover_image(self.image)
        result = self._base("state", (), ())
        result["reads"] = 1
        return result

    def _require_running(self) -> None:
        if self.status != "running":
            raise ProtocolError("not_running", f"service status is {self.status}")

    def _require_crash_available(self) -> None:
        if self.crash_used:
            raise ProtocolError("second_crash_unsupported", "the sole supported crash has already occurred")

    def request(self, message_text: Any, fault: Any = "none") -> Dict[str, Any]:
        self._require_running()
        message = parse_message(message_text)
        if not isinstance(fault, str):
            raise ProtocolError("bad_field_type", "fault must be a string")

        old_state = recover_image(self.image)
        planned = transition(old_state, message)
        new_image = encode_persistent(planned.state)
        changes_image = planned.classification == "state_change"

        if changes_image:
            allowed = STATE_CHANGE_FAULTS
        elif planned.delivery is not None:
            allowed = ACTION_FAULTS
        else:
            allowed = NO_WRITE_FAULTS
        if fault not in allowed:
            raise ProtocolError(
                "inapplicable_fault",
                f"fault {fault!r} is not applicable; choose one of {','.join(allowed)}",
            )
        if fault != "none":
            self._require_crash_available()

        events: List[str] = [_client_event(message)]
        writes: List[Dict[str, Any]] = []

        if changes_image:
            if fault in ("none", "write_old", "write_new", "after_reply"):
                outcome = "old" if fault == "write_old" else "new"
                writes.append(
                    {
                        "address": 0,
                        "new": byte_cell(new_image),
                        "old": byte_cell(self.image),
                        "outcome": outcome,
                    }
                )
                if outcome == "new":
                    self.image = new_image
            if fault in ("write_old", "write_new"):
                events.append("K!CRASH")
                self.status = "crashed"
                self.crash_used = True
            else:
                events.append(_reply_event(planned.reply))
                if fault == "after_reply":
                    events.append("K!CRASH")
                    self.status = "crashed"
                    self.crash_used = True
        elif planned.delivery is not None:
            if fault == "before_delivery":
                events.append("K!CRASH")
                self.status = "crashed"
                self.crash_used = True
            else:
                events.append(_delivery_event(planned.delivery))
                if fault == "after_delivery":
                    events.append("K!CRASH")
                    self.status = "crashed"
                    self.crash_used = True
                else:
                    events.append(_reply_event(planned.reply))
                    if fault == "after_reply":
                        events.append("K!CRASH")
                        self.status = "crashed"
                        self.crash_used = True
        else:
            if fault == "before_reply":
                events.append("K!CRASH")
                self.status = "crashed"
                self.crash_used = True
            else:
                events.append(_reply_event(planned.reply))
                if fault == "after_reply":
                    events.append("K!CRASH")
                    self.status = "crashed"
                    self.crash_used = True

        result = self._base("request", events, writes)
        result["classification"] = planned.classification
        result["fault"] = fault
        result["message"] = byte_text(message)
        result["message_name"] = MESSAGE_NAMES[message]
        return result

    def crash(self) -> Dict[str, Any]:
        self._require_running()
        self._require_crash_available()
        self.status = "crashed"
        self.crash_used = True
        return self._base("crash", ("K!CRASH",), ())

    def restart(self) -> Dict[str, Any]:
        if self.status != "crashed":
            raise ProtocolError("not_crashed", f"cannot restart while status is {self.status}")
        # Validate before reporting completed recovery or changing lifecycle state.
        recover_image(self.image)
        self.status = "running"
        result = self._base("restart", ("K!RESTART", "R!88"), ())
        result["reads"] = 1
        return result

    def half_close(self, fault: Any = "none") -> Dict[str, Any]:
        self._require_running()
        if not isinstance(fault, str):
            raise ProtocolError("bad_field_type", "fault must be a string")
        if fault not in HALF_CLOSE_FAULTS:
            raise ProtocolError(
                "inapplicable_fault",
                f"fault {fault!r} is not applicable; choose one of {','.join(HALF_CLOSE_FAULTS)}",
            )
        events = ["C\u2193", "R!87"]
        self.status = "halted"
        result = self._base("half_close", events, ())
        result["fault"] = fault
        return result


def protocol_description() -> Dict[str, Any]:
    return {
        "faults": {
            "action_success": list(ACTION_FAULTS),
            "half_close": list(HALF_CLOSE_FAULTS),
            "no_write": list(NO_WRITE_FAULTS),
            "state_change": list(STATE_CHANGE_FAULTS),
        },
        "image": "one lowercase hexadecimal byte; recovery accepts 00..11",
        "messages": [byte_text(message) for message in MESSAGE_ORDER],
        "operations": {
            "boot": {"required": ["image"]},
            "capabilities": {"required": []},
            "crash": {"required": []},
            "half_close": {"optional": ["fault"], "required": []},
            "request": {"optional": ["fault"], "required": ["message"]},
            "reset": {"required": []},
            "restart": {"required": []},
            "state": {"required": []},
        },
        "protocol": PROTOCOL_VERSION,
        "scope": "finite falsifier only",
        "seed_sha256": ACTIVE_SEED_SHA256,
    }


def _check_fields(command: Mapping[str, Any], required: Iterable[str], optional: Iterable[str] = ()) -> None:
    required_set = set(required)
    allowed = required_set | set(optional) | {"op"}
    missing = sorted(required_set - set(command))
    unknown = sorted(set(command) - allowed)
    if missing:
        raise ProtocolError("missing_field", "missing field(s): " + ",".join(missing))
    if unknown:
        raise ProtocolError("unknown_field", "unknown field(s): " + ",".join(unknown))


class ProtocolSession:
    def __init__(self) -> None:
        self.simulator = Simulator()

    def dispatch(self, command: Any) -> Dict[str, Any]:
        if not isinstance(command, dict):
            raise ProtocolError("bad_command", "each JSON line must be an object")
        op = command.get("op")
        if not isinstance(op, str):
            raise ProtocolError("bad_operation", "op must be a string")
        if op == "reset":
            _check_fields(command, ())
            return self.simulator.reset()
        if op == "boot":
            _check_fields(command, ("image",))
            return self.simulator.boot_image(command["image"])
        if op == "state":
            _check_fields(command, ())
            return self.simulator.inspect()
        if op == "request":
            _check_fields(command, ("message",), ("fault",))
            return self.simulator.request(command["message"], command.get("fault", "none"))
        if op == "crash":
            _check_fields(command, ())
            return self.simulator.crash()
        if op == "restart":
            _check_fields(command, ())
            return self.simulator.restart()
        if op == "half_close":
            _check_fields(command, (), ("fault",))
            return self.simulator.half_close(command.get("fault", "none"))
        if op == "capabilities":
            _check_fields(command, ())
            result = self.simulator._base("capabilities", (), ())
            result["capabilities"] = protocol_description()
            return result
        raise ProtocolError("unknown_operation", f"unknown operation {op!r}")

    def error_response(self, error: Exception) -> Dict[str, Any]:
        if isinstance(error, ProtocolError):
            code = error.code
        elif isinstance(error, InvalidImage):
            code = "invalid_image"
        else:
            code = "bad_json"
        response: Dict[str, Any] = {
            "crash_used": self.simulator.crash_used,
            "error": {"code": code, "message": str(error)},
            "events": [],
            "image": byte_cell(self.simulator.image),
            "ok": False,
            "status": self.simulator.status,
            "writes": [],
        }
        return response


def _pairs_without_duplicates(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError("duplicate_field", f"duplicate JSON field {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> Any:
    raise ProtocolError("bad_json", f"non-finite JSON constant {value!r}")


def decode_json_line(line: str) -> Any:
    if line == "":
        raise ProtocolError("empty_line", "empty input line")
    try:
        return json.loads(
            line,
            object_pairs_hook=_pairs_without_duplicates,
            parse_constant=_reject_json_constant,
        )
    except ProtocolError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ProtocolError("bad_json", str(exc)) from exc


def serve_json_lines(instream: Any, outstream: Any) -> int:
    session = ProtocolSession()
    for physical_line in instream:
        line = physical_line.rstrip("\r\n")
        try:
            command = decode_json_line(line)
            response = session.dispatch(command)
        except (ProtocolError, InvalidImage) as exc:
            response = session.error_response(exc)
        outstream.write(canonical_json(response) + "\n")
        outstream.flush()
    return 0


class Ledger:
    def __init__(self) -> None:
        self.checks = 0

    def equal(self, actual: Any, expected: Any, label: str) -> None:
        self.checks += 1
        if actual != expected:
            raise SelfTestFailure(
                f"{label}: expected {expected!r}, received {actual!r}"
            )

    def truth(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise SelfTestFailure(label)

    def raises(self, exception_type: type, function: Callable[[], Any], label: str) -> Exception:
        self.checks += 1
        try:
            function()
        except exception_type as exc:
            return exc
        except Exception as exc:
            raise SelfTestFailure(
                f"{label}: expected {exception_type.__name__}, got {type(exc).__name__}: {exc}"
            ) from exc
        raise SelfTestFailure(f"{label}: expected {exception_type.__name__}")


@dataclass(frozen=True)
class ExpectedTransition:
    classification: str
    new_code: int
    reply: bytes
    delivery: Optional[bytes]


def _independent_expected(code: int, message: bytes) -> ExpectedTransition:
    """A compact test oracle stated independently of transition()."""
    revision = code // 9
    tail = code % 9
    interpreter = tail // 3
    observation = tail % 3

    if message == b"\xfe":
        return ExpectedTransition("rejected", code, b"\xe0\x01", None)
    if message == b"\x30\x00":
        return ExpectedTransition("rejected", code, b"\xe0\x02", None)
    if message in (b"\x00", b"\x01"):
        wanted = 1 if message == b"\x00" else 2
        new_code = code - observation + wanted
        kind = "no_op" if new_code == code else "state_change"
        return ExpectedTransition(kind, new_code, b"\x80" + message, None)
    if message in (b"\x10", b"\x11"):
        wanted = 1 if message == b"\x10" else 2
        new_code = code - 3 * interpreter + 3 * wanted
        kind = "no_op" if new_code == code else "state_change"
        return ExpectedTransition(kind, new_code, b"\x81" + message, None)
    if message == b"\x20":
        if interpreter == 0:
            return ExpectedTransition("rejected", code, b"\xe0\x05", None)
        return ExpectedTransition("state_change", code - 3 * interpreter, b"\x82", None)
    if message in (b"\x30", b"\x40"):
        if interpreter == 0:
            return ExpectedTransition("rejected", code, b"\xe0\x03", None)
        if observation == 0:
            return ExpectedTransition("rejected", code, b"\xe0\x04", None)
        observed_bit = observation - 1
        result_bit = observed_bit if interpreter == 1 else 1 - observed_bit
        if message == b"\x30":
            return ExpectedTransition("readonly", code, bytes((0x83, result_bit)), None)
        return ExpectedTransition(
            "readonly", code, b"\x84", bytes((0xA0 + revision, result_bit))
        )
    if message == b"\x50":
        if revision == 1:
            return ExpectedTransition("rejected", code, b"\xe0\x06", None)
        return ExpectedTransition("state_change", code + 9, b"\x85\x01", None)
    if message == b"\x60":
        reply = bytes((0x86, 0x03, revision, 0x40, 0xA0 + revision))
        return ExpectedTransition("readonly", code, reply, None)
    raise SelfTestFailure("test oracle received a message outside its finite alphabet")


def _normal_events(message: bytes, expected: ExpectedTransition) -> List[str]:
    events = [_client_event(message)]
    if expected.delivery is not None:
        events.append(_delivery_event(expected.delivery))
    events.append(_reply_event(expected.reply))
    return events


def _boot(code: int) -> Simulator:
    simulator = Simulator()
    simulator.boot_image(byte_cell(code))
    return simulator


def _count_events(responses: Iterable[Mapping[str, Any]], prefix: str) -> int:
    return sum(
        1
        for response in responses
        for event in response["events"]
        if isinstance(event, str) and event.startswith(prefix)
    )


def run_self_test() -> Dict[str, Any]:
    ledger = Ledger()
    counts: Dict[str, int] = {
        "action_retry_cases": 0,
        "action_schedule_cases": 0,
        "invalid_images": 0,
        "messages": len(MESSAGE_ORDER),
        "no_write_crash_cases": 0,
        "no_write_fault_rejections": 0,
        "readonly_success": 0,
        "rejected": 0,
        "restart_stability_cases": 0,
        "semantic_noops": 0,
        "second_crash_rejections": 0,
        "state_changing": 0,
        "transition_cases": 0,
        "valid_images": 0,
        "write_after_reply_cases": 0,
        "write_fault_outcomes": 0,
        "write_new_outcomes": 0,
        "write_old_outcomes": 0,
    }

    ledger.equal(ACTIVE_SEED_SHA256, EXPECTED_SEED_SHA256, "active seed digest")
    ledger.equal(len(MESSAGE_ORDER), 11, "message alphabet size")
    ledger.equal(len(set(MESSAGE_ORDER)), 11, "message alphabet uniqueness")

    encodings = set()
    for raw in range(256):
        if raw <= 0x11:
            state = recover_image(raw)
            ledger.equal(encode_persistent(state), raw, f"image {raw:02x} round trip")
            encodings.add(encode_persistent(state))
            counts["valid_images"] += 1
        else:
            ledger.raises(InvalidImage, lambda raw=raw: recover_image(raw), f"image {raw:02x} rejection")
            counts["invalid_images"] += 1
    ledger.equal(encodings, set(range(18)), "all packed encodings are injective and complete")
    ledger.raises(InvalidImage, lambda: recover_image(-1), "negative image rejection")
    ledger.raises(InvalidImage, lambda: recover_image(256), "wide image rejection")
    ledger.raises(InvalidImage, lambda: recover_image(True), "boolean image rejection")

    state_change_cases: List[Tuple[int, bytes, ExpectedTransition]] = []
    no_write_cases: List[Tuple[int, bytes, ExpectedTransition]] = []
    action_codes: List[int] = []

    for code in range(18):
        for message in MESSAGE_ORDER:
            expected = _independent_expected(code, message)
            simulator = _boot(code)
            response = simulator.request(byte_text(message), "none")
            counts["transition_cases"] += 1
            counts_key = {
                "state_change": "state_changing",
                "no_op": "semantic_noops",
                "readonly": "readonly_success",
                "rejected": "rejected",
            }[expected.classification]
            counts[counts_key] += 1

            ledger.equal(response["classification"], expected.classification, f"classification {code}/{byte_text(message)}")
            ledger.equal(response["events"], _normal_events(message, expected), f"events {code}/{byte_text(message)}")
            ledger.equal(response["image"], byte_cell(expected.new_code), f"image {code}/{byte_text(message)}")
            ledger.equal(response["status"], "running", f"running {code}/{byte_text(message)}")
            expected_write_count = 1 if expected.classification == "state_change" else 0
            ledger.equal(len(response["writes"]), expected_write_count, f"write count {code}/{byte_text(message)}")
            if expected_write_count:
                write = response["writes"][0]
                ledger.equal(write["old"], byte_cell(code), f"write old {code}/{byte_text(message)}")
                ledger.equal(write["new"], byte_cell(expected.new_code), f"write new {code}/{byte_text(message)}")
                ledger.equal(write["outcome"], "new", f"normal write outcome {code}/{byte_text(message)}")
                state_change_cases.append((code, message, expected))
            else:
                no_write_cases.append((code, message, expected))
            if message == b"\x40" and expected.delivery is not None:
                action_codes.append(code)

    ledger.equal(counts["transition_cases"], 198, "complete transition matrix")
    ledger.equal(counts["state_changing"], 69, "state-changing transition count")
    ledger.equal(counts["semantic_noops"], 24, "semantic no-op count")
    ledger.equal(counts["rejected"], 71, "rejected transition count")
    ledger.equal(counts["readonly_success"], 34, "read-only success count")
    ledger.equal(len(no_write_cases), 129, "no-write case count")
    ledger.equal(sorted(set(action_codes)), action_codes, "successful action class order")
    ledger.equal(len(action_codes), 8, "successful action class count")

    # Every issued state-changing write is crashed once to old and once to new.
    for code, message, expected in state_change_cases:
        for outcome in ("old", "new"):
            simulator = _boot(code)
            response = simulator.request(byte_text(message), "write_" + outcome)
            counts["write_fault_outcomes"] += 1
            counts["write_" + outcome + "_outcomes"] += 1
            durable = code if outcome == "old" else expected.new_code
            ledger.equal(response["events"], [_client_event(message), "K!CRASH"], f"write-{outcome} crossings {code}/{byte_text(message)}")
            ledger.equal(response["image"], byte_cell(durable), f"write-{outcome} image {code}/{byte_text(message)}")
            ledger.equal(response["status"], "crashed", f"write-{outcome} crash state {code}/{byte_text(message)}")
            ledger.equal(len(response["writes"]), 1, f"write-{outcome} physical count {code}/{byte_text(message)}")
            ledger.equal(response["writes"][0]["outcome"], outcome, f"write-{outcome} declaration {code}/{byte_text(message)}")
            ledger.truth(not any(event.startswith(("R!", "D!")) for event in response["events"]), f"interrupted write emits no response {code}/{byte_text(message)}")
            restarted = simulator.restart()
            ledger.equal(restarted["events"], ["K!RESTART", "R!88"], f"write-{outcome} restart events {code}/{byte_text(message)}")
            ledger.equal(restarted["image"], byte_cell(durable), f"write-{outcome} restart image {code}/{byte_text(message)}")
            ledger.equal(restarted["derived_state"]["class"], durable, f"write-{outcome} recovered class {code}/{byte_text(message)}")

        simulator = _boot(code)
        acknowledged = simulator.request(byte_text(message), "after_reply")
        counts["write_after_reply_cases"] += 1
        ledger.equal(acknowledged["events"], _normal_events(message, expected) + ["K!CRASH"], f"acknowledged write crossings {code}/{byte_text(message)}")
        ledger.equal(acknowledged["image"], byte_cell(expected.new_code), f"acknowledged write durable image {code}/{byte_text(message)}")
        ledger.equal(len(acknowledged["writes"]), 1, f"acknowledged write count {code}/{byte_text(message)}")
        after_restart = simulator.restart()
        ledger.equal(after_restart["derived_state"]["class"], expected.new_code, f"acknowledged write recovery {code}/{byte_text(message)}")

    ledger.equal(counts["write_fault_outcomes"], 138, "old/new write outcome total")
    ledger.equal(counts["write_old_outcomes"], 69, "old write outcome total")
    ledger.equal(counts["write_new_outcomes"], 69, "new write outcome total")
    ledger.equal(counts["write_after_reply_cases"], 69, "acknowledged mutation crash total")

    # All successful no-ops, reads, actions, and rejections must remain write-free.
    for code, message, expected in no_write_cases:
        simulator = _boot(code)
        before_image = simulator.image
        ledger.raises(
            ProtocolError,
            lambda simulator=simulator, message=message: simulator.request(byte_text(message), "write_old"),
            f"no-write old/new injection refusal {code}/{byte_text(message)}",
        )
        counts["no_write_fault_rejections"] += 1
        ledger.equal(simulator.image, before_image, f"inapplicable fault preserves image {code}/{byte_text(message)}")
        ledger.equal(simulator.status, "running", f"inapplicable fault preserves lifecycle {code}/{byte_text(message)}")

        simulator = _boot(code)
        early_fault = "before_delivery" if expected.delivery is not None else "before_reply"
        interrupted = simulator.request(byte_text(message), early_fault)
        counts["no_write_crash_cases"] += 1
        ledger.equal(interrupted["events"], [_client_event(message), "K!CRASH"], f"no-write early crash {code}/{byte_text(message)}")
        ledger.equal(interrupted["writes"], [], f"no-write early crash physical writes {code}/{byte_text(message)}")
        ledger.equal(interrupted["image"], byte_cell(code), f"no-write early crash image {code}/{byte_text(message)}")
        restarted = simulator.restart()
        ledger.equal(restarted["image"], byte_cell(code), f"no-write restart image {code}/{byte_text(message)}")

    ledger.equal(counts["no_write_fault_rejections"], 129, "all no-write cases reject byte fault injection")
    ledger.equal(counts["no_write_crash_cases"], 129, "all no-write cases survive early crash unchanged")

    # Exact action projections for every class in which an action can succeed.
    for code in action_codes:
        expected = _independent_expected(code, b"\x40")
        delivery_event = _delivery_event(expected.delivery or b"")
        schedules = {
            "none": ["C!40", delivery_event, "R!84"],
            "before_delivery": ["C!40", "K!CRASH"],
            "after_delivery": ["C!40", delivery_event, "K!CRASH"],
            "after_reply": ["C!40", delivery_event, "R!84", "K!CRASH"],
        }
        for fault, wanted_events in schedules.items():
            simulator = _boot(code)
            response = simulator.request("40", fault)
            counts["action_schedule_cases"] += 1
            ledger.equal(response["events"], wanted_events, f"action schedule {code}/{fault}")
            ledger.equal(response["writes"], [], f"action never writes {code}/{fault}")
            ledger.equal(response["image"], byte_cell(code), f"action preserves image {code}/{fault}")
            if fault != "none":
                recovery = simulator.restart()
                ledger.equal(recovery["events"], ["K!RESTART", "R!88"], f"action recovery events {code}/{fault}")
                ledger.equal(_count_events((recovery,), "D!"), 0, f"action recovery does not retry {code}/{fault}")

        for first_fault, expected_attempts in (("before_delivery", 1), ("after_delivery", 2)):
            simulator = _boot(code)
            first = simulator.request("40", first_fault)
            recovery = simulator.restart()
            retry = simulator.request("40", "none")
            counts["action_retry_cases"] += 1
            ledger.equal(
                _count_events((first, recovery, retry), "D!"),
                expected_attempts,
                f"action retry attempt exposure {code}/{first_fault}",
            )
            ledger.equal(_count_events((first, recovery, retry), "R!84"), 1, f"only retry acknowledged {code}/{first_fault}")

    ledger.equal(counts["action_schedule_cases"], 32, "all action crossing schedules")
    ledger.equal(counts["action_retry_cases"], 16, "action retry uncertainty cases")

    # Quiescent crash/restart preserves every valid image and reports only R!88.
    for code in range(18):
        simulator = _boot(code)
        crashed = simulator.crash()
        restarted = simulator.restart()
        counts["restart_stability_cases"] += 1
        ledger.equal(crashed["events"], ["K!CRASH"], f"quiescent crash {code}")
        ledger.equal(restarted["events"], ["K!RESTART", "R!88"], f"quiescent restart {code}")
        ledger.equal(restarted["image"], byte_cell(code), f"quiescent restart image {code}")
        ledger.equal(restarted["reads"], 1, f"quiescent recovery read count {code}")
    ledger.equal(counts["restart_stability_cases"], 18, "all valid images restart")

    # A completed recovery does not silently open a second fault budget.
    simulator = _boot(0)
    simulator.crash()
    simulator.restart()
    ledger.raises(ProtocolError, simulator.crash, "second quiescent crash is unsupported")
    counts["second_crash_rejections"] += 1
    ledger.raises(
        ProtocolError,
        lambda: simulator.request("60", "before_reply"),
        "second in-request crash is unsupported",
    )
    counts["second_crash_rejections"] += 1
    ledger.equal(simulator.image, 0, "second crash rejection preserves image")
    ledger.equal(simulator.status, "running", "second crash rejection preserves lifecycle")
    ledger.equal(counts["second_crash_rejections"], 2, "second crash guards")

    # Boot rejects every invalid byte and does not partially install it.
    for raw in range(0x12, 0x100):
        simulator = _boot(5)
        ledger.raises(InvalidImage, lambda raw=raw, simulator=simulator: simulator.boot_image(byte_cell(raw)), f"invalid boot image {raw:02x}")
        ledger.equal(simulator.image, 5, f"invalid boot preserves old image {raw:02x}")
        ledger.equal(simulator.status, "running", f"invalid boot preserves lifecycle {raw:02x}")

    # STOP/framing anchors remain distinct at the public boundary.
    simulator = Simulator()
    stop = simulator.half_close()
    ledger.equal(stop["events"], ["C\u2193", "R!87"], "clean half-close")
    ledger.equal(stop["status"], "halted", "half-close halts")

    unknown = Simulator().request("fe")
    malformed = Simulator().request("30 00")
    sequence_simulator = Simulator()
    query = sequence_simulator.request("30")
    observe = sequence_simulator.request("00")
    ledger.equal(unknown["events"], ["C!fe", "R!e0 01"], "unknown sample framing")
    ledger.equal(malformed["events"], ["C!30 00", "R!e0 02"], "malformed sample framing")
    ledger.equal(query["events"] + observe["events"], ["C!30", "R!e0 03", "C!00", "R!80 00"], "two one-byte messages remain distinct")
    ledger.raises(ProtocolError, lambda: parse_message("ff"), "unsupported byte is outside experiment")
    ledger.raises(ProtocolError, lambda: parse_message("3000"), "message text requires atomic byte token framing")

    # JSON parsing rejects ambiguity and protocol errors do not create crossings.
    ledger.raises(
        ProtocolError,
        lambda: decode_json_line('{"op":"state","op":"reset"}'),
        "duplicate JSON key rejection",
    )
    session = ProtocolSession()
    before = session.simulator.inspect()
    error = session.error_response(
        ledger.raises(
            ProtocolError,
            lambda: session.dispatch({"op": "request", "message": "00", "fault": "write_old", "extra": 1}),
            "unknown protocol field rejection",
        )
    )
    after = session.simulator.inspect()
    ledger.equal(error["events"], [], "protocol error emits no boundary crossing")
    ledger.equal(error["writes"], [], "protocol error emits no write")
    ledger.equal(after["image"], before["image"], "protocol error preserves image")

    # Canonical serialization is stable for identical fresh sessions.
    command = {"op": "request", "message": "10", "fault": "none"}
    first = canonical_json(ProtocolSession().dispatch(command))
    second = canonical_json(ProtocolSession().dispatch(command))
    ledger.equal(first, second, "deterministic canonical protocol response")
    ledger.equal(canonical_json(json.loads(first)), first, "canonical response round trip")

    return {
        "counts": counts,
        "implementation": "S-packed-quotient-overwrite",
        "protocol": PROTOCOL_VERSION,
        "seed_sha256": ACTIVE_SEED_SHA256,
        "status": "ok",
        "test_checks": ledger.checks,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--self-test", action="store_true", help="run exhaustive deterministic checks")
    mode.add_argument("--protocol-help", action="store_true", help="emit canonical JSON protocol description")
    arguments = parser.parse_args(argv)

    if arguments.protocol_help:
        print(canonical_json(protocol_description()))
        return 0
    if arguments.self_test:
        try:
            report = run_self_test()
        except Exception as exc:
            failure = {
                "error": {"message": str(exc), "type": type(exc).__name__},
                "implementation": "S-packed-quotient-overwrite",
                "protocol": PROTOCOL_VERSION,
                "seed_sha256": ACTIVE_SEED_SHA256,
                "status": "failed",
            }
            print(canonical_json(failure))
            return 1
        print(canonical_json(report))
        return 0
    return serve_json_lines(sys.stdin, sys.stdout)


if __name__ == "__main__":
    raise SystemExit(main())
