#!/usr/bin/env python3
"""Third, black-box comparison harness for the frozen R01G experiment.

Only the three frozen inputs named below are trusted as inputs.  The two
realizations are always exercised as subprocesses through their JSONL
protocols; neither is imported.  The history oracle and both persistence
decoders in this file are independent spellings of the frozen seed.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import select
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence


ROOT = Path(__file__).resolve().parent
INPUT_HASHES = {
    "HISTORY-SEED-R01G.md": "9fcf79f7544e3fe7d11f0830e224635758921f199e4478bb4180ada991629008",
    "r01g_realization_l.py": "291aa322642d2be07d983422c054137658437c913150785e846f4a958cdd3398",
    "r01g_realization_s.py": "e8aca5702abe926cfe9ec7e2a6c722c38d1707b0c4e95ecce8f4b695af73b761",
}

MESSAGES = (
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
MUTATOR_OPCODES = (0x00, 0x01, 0x10, 0x11, 0x20, 0x50)
L_ALPHABET = MUTATOR_OPCODES + (0xFF,)


class Failure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def strict_pairs(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise Failure(f"duplicate JSON key from subprocess: {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> Any:
    raise Failure(f"non-finite JSON constant from subprocess: {value}")


def strict_load(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=strict_pairs, parse_constant=reject_constant)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise Failure(f"invalid JSON from subprocess: {exc}") from exc


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1 << 20)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def verify_inputs() -> dict[str, str]:
    actual: dict[str, str] = {}
    for name, expected in INPUT_HASHES.items():
        path = ROOT / name
        require(path.is_file(), f"frozen input is absent: {name}")
        digest = hash_file(path)
        require(digest == expected, f"frozen input hash mismatch for {name}: {digest}")
        actual[name] = digest
    return actual


def spaced(data: bytes) -> str:
    return " ".join(f"{byte:02x}" for byte in data)


def client_event(message: bytes) -> str:
    return "C!" + spaced(message)


def crossing_event(channel: str, payload: bytes) -> str:
    require(channel in ("R", "D") and bool(payload), "invalid public crossing")
    return channel + "!" + spaced(payload)


def decode_code(code: int) -> tuple[int, int, int]:
    require(type(code) is int and 0 <= code < 18, f"invalid quotient code {code!r}")
    revision, tail = divmod(code, 9)
    table, observation = divmod(tail, 3)
    return revision, table, observation


def encode_code(revision: int, table: int, observation: int) -> int:
    require(type(revision) is int and revision in (0, 1), "oracle revision range/type")
    require(type(table) is int and table in (0, 1, 2), "oracle table range/type")
    require(type(observation) is int and observation in (0, 1, 2), "oracle observation range/type")
    return 9 * revision + 3 * table + observation


@dataclass(frozen=True)
class Plan:
    kind: str
    new_code: int
    outputs: tuple[str, ...]
    opcode: Optional[int] = None


def oracle_plan(code: int, message: bytes) -> Plan:
    """History oracle, independently encoded from the prose transition rules."""
    revision, table, observation = decode_code(code)
    if message == b"\x00":
        return Plan("mutation", encode_code(revision, table, 1), ("R!80 00",), 0x00)
    if message == b"\x01":
        return Plan("mutation", encode_code(revision, table, 2), ("R!80 01",), 0x01)
    if message == b"\x10":
        return Plan("mutation", encode_code(revision, 1, observation), ("R!81 10",), 0x10)
    if message == b"\x11":
        return Plan("mutation", encode_code(revision, 2, observation), ("R!81 11",), 0x11)
    if message == b"\x20":
        if table == 0:
            return Plan("rejection", code, ("R!e0 05",))
        return Plan("mutation", encode_code(revision, 0, observation), ("R!82",), 0x20)
    if message in (b"\x30", b"\x40"):
        if table == 0:
            return Plan("rejection", code, ("R!e0 03",))
        if observation == 0:
            return Plan("rejection", code, ("R!e0 04",))
        observed = observation - 1
        bit = observed if table == 1 else 1 - observed
        if message == b"\x30":
            return Plan("read", code, (f"R!83 {bit:02x}",))
        return Plan("action", code, (f"D!{0xA0 + revision:02x} {bit:02x}", "R!84"))
    if message == b"\x50":
        if revision == 1:
            return Plan("rejection", code, ("R!e0 06",))
        return Plan("mutation", encode_code(1, table, observation), ("R!85 01",), 0x50)
    if message == b"\x60":
        return Plan("read", code, (f"R!86 03 {revision:02x} 40 {0xA0 + revision:02x}",))
    if message == b"\xfe":
        return Plan("rejection", code, ("R!e0 01",))
    if message == b"\x30\x00":
        return Plan("rejection", code, ("R!e0 02",))
    raise Failure(f"oracle received message outside bounded alphabet: {message.hex()}")


@dataclass(frozen=True)
class Outcome:
    events: tuple[str, ...]
    recovered_class: Optional[int]
    final_class: int

    def object(self) -> dict[str, Any]:
        return {
            "events": list(self.events),
            "final_class": self.final_class,
            "recovered_class": self.recovered_class,
        }

    def key(self) -> str:
        return canonical(self.object())


def oracle_step(code: int, message: bytes, semantic: str) -> Outcome:
    plan = oracle_plan(code, message)
    events = [client_event(message)]
    recovered: Optional[int] = None
    final = code

    if semantic in ("none", "after"):
        events.extend(plan.outputs)
        final = plan.new_code
        if semantic == "after":
            recovered = final
    elif semantic in ("old", "new"):
        require(plan.kind == "mutation", "old/new schedule applied to nonmutation")
        final = code if semantic == "old" else plan.new_code
        recovered = final
    elif semantic == "before_reply":
        require(plan.kind not in ("mutation", "action"), "reply gap applied to wrong plan")
        recovered = code
    elif semantic == "noop_before_reply":
        require(plan.kind == "mutation" and plan.new_code == code, "no-op gap applied to state change")
        recovered = code
    elif semantic == "before_delivery":
        require(plan.kind == "action", "delivery gap applied to nonaction")
        recovered = code
    elif semantic == "after_delivery":
        require(plan.kind == "action", "delivery gap applied to nonaction")
        events.append(plan.outputs[0])
        recovered = code
    else:
        raise Failure(f"unknown oracle schedule semantic {semantic}")

    if semantic != "none":
        events.extend(("K!CRASH", "K!RESTART", "R!88"))
    return Outcome(tuple(events), recovered, final)


def oracle_boundary(code: int) -> Outcome:
    return Outcome(("K!CRASH", "K!RESTART", "R!88"), code, code)


def append_outcomes(parts: Iterable[Outcome]) -> Outcome:
    events: list[str] = []
    recovered: Optional[int] = None
    final: Optional[int] = None
    for part in parts:
        events.extend(part.events)
        if part.recovered_class is not None:
            require(recovered is None, "more than one crash in composed outcome")
            recovered = part.recovered_class
        final = part.final_class
    require(final is not None, "empty outcome composition")
    return Outcome(tuple(events), recovered, final)


@dataclass(frozen=True)
class Spec:
    label: str
    kind: str
    index: int = -1
    semantic: str = ""


def abstract_specs(start_code: int, word: tuple[bytes, ...]) -> tuple[Spec, ...]:
    specs = [Spec("no_crash", "none"), Spec("boundary:0", "boundary", 0)]
    code = start_code
    for index, message in enumerate(word):
        plan = oracle_plan(code, message)
        specs.append(Spec(f"boundary:{index + 1}", "step", index, "after"))
        if plan.kind == "mutation":
            specs.append(Spec(f"message:{index}:mutation_old", "step", index, "old"))
            specs.append(Spec(f"message:{index}:mutation_new", "step", index, "new"))
        elif plan.kind == "action":
            specs.append(Spec(f"message:{index}:before_delivery", "step", index, "before_delivery"))
            specs.append(Spec(f"message:{index}:after_delivery", "step", index, "after_delivery"))
        else:
            specs.append(Spec(f"message:{index}:before_reply", "step", index, "before_reply"))
        code = plan.new_code
    return tuple(specs)


def oracle_run(start: int, word: tuple[bytes, ...], spec: Spec) -> Outcome:
    parts: list[Outcome] = []
    code = start
    if spec.kind == "boundary":
        require(spec.index == 0, "only cut boundary is a direct boundary spec")
        parts.append(oracle_boundary(code))
    for index, message in enumerate(word):
        semantic = spec.semantic if spec.kind == "step" and spec.index == index else "none"
        part = oracle_step(code, message, semantic)
        parts.append(part)
        code = part.final_class
    if not parts:
        return Outcome((), None, start)
    return append_outcomes(parts)


def l_recover_independent(image: str) -> tuple[int, int]:
    if not isinstance(image, str) or len(image) != 10:
        raise ValueError("L image width")
    try:
        cells = bytes.fromhex(image)
    except ValueError as exc:
        raise ValueError("L image hex") from exc
    require(len(cells) == 5, "L decoder width")
    code = 0
    entries = 0
    erased = False
    for cell in cells:
        if cell == 0xFF:
            erased = True
            continue
        if erased or cell not in MUTATOR_OPCODES:
            raise ValueError("L invalid alphabet/contiguity")
        plan = oracle_plan(code, bytes((cell,)))
        if plan.kind != "mutation":
            raise ValueError("L replay-invalid mutation log")
        code = plan.new_code
        entries += 1
    return code, entries


class JsonlProcess:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.calls = 0
        self.process = subprocess.Popen(
            [sys.executable, str(path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="strict",
            bufsize=1,
        )

    def request(self, request: Mapping[str, Any]) -> dict[str, Any]:
        require(self.process.poll() is None, f"subprocess exited early: {self.path.name}")
        require(self.process.stdin is not None and self.process.stdout is not None, "subprocess pipes absent")
        line = canonical(request)
        try:
            self.process.stdin.write(line + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise Failure(f"cannot write to {self.path.name}: {exc}") from exc
        ready, _, _ = select.select([self.process.stdout], [], [], 20.0)
        require(bool(ready), f"timeout waiting for {self.path.name}")
        response_line = self.process.stdout.readline()
        require(response_line != "", f"unexpected EOF from {self.path.name}")
        self.calls += 1
        response = strict_load(response_line.rstrip("\n"))
        require(isinstance(response, dict), f"non-object response from {self.path.name}")
        return response

    def close(self) -> None:
        if self.process.poll() is None:
            if self.process.stdin is not None:
                self.process.stdin.close()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired as exc:
                self.process.kill()
                self.process.wait()
                raise Failure(f"subprocess did not exit: {self.path.name}") from exc
        stderr = ""
        if self.process.stderr is not None:
            stderr = self.process.stderr.read()
        require(self.process.returncode == 0, f"{self.path.name} exited {self.process.returncode}: {stderr.strip()}")
        require(stderr == "", f"unexpected stderr from {self.path.name}: {stderr.strip()}")


def ok_result(response: Mapping[str, Any], label: str) -> Any:
    require(response.get("ok") is True, f"{label} failed: {canonical(response)}")
    require("result" in response, f"{label} omitted result")
    return response["result"]


def require_error(response: Mapping[str, Any], codes: set[str], label: str) -> str:
    require(response.get("ok") is False, f"{label} unexpectedly succeeded")
    error = response.get("error")
    require(isinstance(error, dict) and isinstance(error.get("code"), str), f"{label} malformed error")
    code = error["code"]
    require(code in codes, f"{label} wrong error {code!r}, expected {sorted(codes)}")
    return code


@dataclass(frozen=True)
class ActualStep:
    handle: Any
    outcome: Outcome


class LAdapter:
    name = "L"

    def __init__(self, process: JsonlProcess) -> None:
        self.process = process
        self.initial = "ffffffffff"
        self.recover_cache: dict[str, tuple[int, int]] = {}
        self.restart_cache: dict[str, Outcome] = {}
        self.outcome_cache: dict[tuple[str, bytes], dict[str, ActualStep]] = {}
        description = ok_result(process.request({"op": "describe"}), "L describe")
        require(description.get("implementation") == "r01g-realization-l", "L implementation identity")
        require(description.get("protocol") == "r01g-jsonl-v1", "L protocol identity")
        require(description.get("seed_sha256") == INPUT_HASHES["HISTORY-SEED-R01G.md"], "L seed identity")
        require(description.get("initial_image") == self.initial and description.get("image_bytes") == 5, "L image description")
        require(description.get("message_order") == [message.hex() for message in MESSAGES], "L message order")
        schedules = description.get("schedules")
        require(
            schedules == {
                "action_success": ["none", "before_d", "after_d", "after_r"],
                "mutation_success": ["none", "write_old", "write_new", "after_r"],
                "reply_only": ["none", "before_r", "after_r"],
            },
            "L schedule description",
        )

    def class_of(self, image: str) -> int:
        if image in self.recover_cache:
            return self.recover_cache[image][0]
        expected_code, expected_entries = l_recover_independent(image)
        result = ok_result(self.process.request({"op": "recover", "image": image}), "L recover")
        require(result.get("image") == image, "L recovery changed image")
        code = self._state_code(result.get("state"))
        require(code == expected_code and result.get("entries") == expected_entries, "L recovery differs from oracle")
        self.recover_cache[image] = (code, expected_entries)
        return code

    @staticmethod
    def _state_code(state: Any) -> int:
        require(isinstance(state, dict), "L state is not an object")
        require(set(state) == {"revision", "table", "observation"}, "L state fields")
        table_map = {None: 0, "I": 1, "N": 2}
        observation_map = {None: 0, 0: 1, 1: 2}
        require(state.get("table") in table_map, "L table value")
        observation = state.get("observation")
        require(observation is None or type(observation) is int and observation in (0, 1), "L observation value/type")
        return encode_code(state.get("revision"), table_map[state["table"]], observation_map[state["observation"]])

    @staticmethod
    def _outputs(value: Any) -> tuple[str, ...]:
        require(isinstance(value, list), "L outputs are not a list")
        events: list[str] = []
        for crossing in value:
            require(isinstance(crossing, dict) and set(crossing) == {"bytes", "channel"}, "L crossing shape")
            channel = crossing["channel"]
            text = crossing["bytes"]
            require(channel in ("R", "D") and isinstance(text, str) and len(text) % 2 == 0, "L crossing fields")
            try:
                payload = bytes.fromhex(text)
            except ValueError as exc:
                raise Failure("L crossing contains invalid hex") from exc
            events.append(crossing_event(channel, payload))
        return tuple(events)

    def restart(self, image: str) -> Outcome:
        if image in self.restart_cache:
            return self.restart_cache[image]
        code = self.class_of(image)
        result = ok_result(self.process.request({"op": "restart", "image": image}), "L restart")
        require(result.get("image") == image, "L restart changed durable image")
        require(self._state_code(result.get("state")) == code, "L restart state")
        outputs = self._outputs(result.get("outputs"))
        require(outputs == ("R!88",), "L restart output")
        outcome = Outcome(("K!RESTART",) + outputs, code, code)
        self.restart_cache[image] = outcome
        return outcome

    def boundary(self, image: str) -> ActualStep:
        restart = self.restart(image)
        return ActualStep(image, Outcome(("K!CRASH",) + restart.events, restart.recovered_class, restart.final_class))

    def _expected_schedules(self, code: int, message: bytes) -> tuple[str, ...]:
        plan = oracle_plan(code, message)
        if plan.kind == "mutation":
            return ("none", "write_old", "write_new", "after_r")
        if plan.kind == "action":
            return ("none", "before_d", "after_d", "after_r")
        return ("none", "before_r", "after_r")

    @staticmethod
    def _semantic(plan: Plan, schedule: str) -> str:
        if schedule == "none":
            return "none"
        if schedule == "after_r":
            return "after"
        if schedule == "write_old":
            return "old"
        if schedule == "write_new":
            return "new"
        if schedule == "before_d":
            return "before_delivery"
        if schedule == "after_d":
            return "after_delivery"
        if schedule == "before_r":
            return "before_reply"
        raise Failure(f"unknown L schedule {schedule}")

    def outcomes(self, image: str, message: bytes) -> dict[str, ActualStep]:
        key = (image, message)
        if key in self.outcome_cache:
            return self.outcome_cache[key]
        code = self.class_of(image)
        plan = oracle_plan(code, message)
        expected_schedules = self._expected_schedules(code, message)
        response = self.process.request({"op": "enumerate", "image": image, "message": message.hex()})
        payload = ok_result(response, "L enumerate")
        raw_outcomes = payload.get("outcomes") if isinstance(payload, dict) else None
        require(isinstance(raw_outcomes, list), "L enumerate outcomes")
        require(len(raw_outcomes) == len(expected_schedules), "L exposed schedule count")
        require(all(isinstance(item, dict) for item in raw_outcomes), "L enumerate outcome object type")
        require([item.get("schedule") for item in raw_outcomes] == list(expected_schedules), "L exposed schedules")
        entries = self.recover_cache[image][1]
        results: dict[str, ActualStep] = {}
        for raw, schedule in zip(raw_outcomes, expected_schedules):
            require(isinstance(raw, dict), "L step result shape")
            semantic = self._semantic(plan, schedule)
            expected_oracle = oracle_step(code, message, semantic)
            expected_immediate = expected_oracle.events
            if semantic != "none":
                expected_immediate = expected_immediate[:-2]
            expected_outputs = expected_immediate[1:-1] if semantic != "none" else expected_immediate[1:]
            actual_outputs = self._outputs(raw.get("outputs"))
            require(actual_outputs == expected_outputs, f"L immediate outputs differ for {image}/{message.hex()}/{schedule}")
            crashed = raw.get("crashed")
            require(crashed is (schedule != "none"), "L crash flag")

            expected_image = image
            if plan.kind == "mutation":
                require(entries < 5 and plan.opcode is not None, "L mutation capacity/model")
                outcome_name = "old" if schedule == "write_old" else "new"
                if outcome_name == "new":
                    cells = bytearray.fromhex(image)
                    cells[entries] = plan.opcode
                    expected_image = cells.hex()
                write = raw.get("write")
                require(
                    write == {
                        "index": entries,
                        "new": f"{plan.opcode:02x}",
                        "old": "ff",
                        "outcome": outcome_name,
                    },
                    "L write declaration",
                )
                expected_transition = "mutation_noop" if plan.new_code == code else "mutation"
                require(raw.get("transition") == expected_transition, "L mutation transition label")
            else:
                require(raw.get("write") is None, "L nonmutation wrote")
                expected_transition = "action" if plan.kind == "action" else plan.kind
                require(raw.get("transition") == expected_transition, "L nonmutation transition label")
            require(raw.get("image") == expected_image, "L durable image differs")
            end_code = self.class_of(expected_image)
            require(end_code == expected_oracle.final_class, "L recovered quotient differs after step")
            require(self._state_code(raw.get("state")) == end_code, "L returned state differs from image")

            events = (client_event(message),) + actual_outputs
            recovered: Optional[int] = None
            if crashed:
                events += ("K!CRASH",)
                restart = self.restart(expected_image)
                events += restart.events
                recovered = restart.recovered_class
            actual = Outcome(events, recovered, end_code)
            require(actual == expected_oracle, f"L step differs from independent oracle: {image}/{message.hex()}/{schedule}")
            results[schedule] = ActualStep(expected_image, actual)
        self.outcome_cache[key] = results
        return results

    def transition(self, image: str, message: bytes, semantic: str) -> ActualStep:
        code = self.class_of(image)
        plan = oracle_plan(code, message)
        mapping = {
            "none": "none",
            "after": "after_r",
            "old": "write_old",
            "new": "write_new",
            "before_reply": "before_r",
            "before_delivery": "before_d",
            "after_delivery": "after_d",
        }
        require(semantic in mapping, f"L cannot map semantic {semantic}")
        schedule = mapping[semantic]
        require(schedule in self._expected_schedules(code, message), "L inapplicable normalized schedule")
        return self.outcomes(image, message)[schedule]


class SAdapter:
    name = "S"

    def __init__(self, process: JsonlProcess) -> None:
        self.process = process
        self.initial = 0
        self.outcome_cache: dict[tuple[int, bytes], dict[str, ActualStep]] = {}
        self.boundary_cache: dict[int, Outcome] = {}
        response = process.request({"op": "capabilities"})
        require(response.get("ok") is True, "S capabilities failed")
        capabilities = response.get("capabilities")
        require(isinstance(capabilities, dict), "S capabilities shape")
        require(capabilities.get("protocol") == "r01g-realization-s-jsonl-v1", "S protocol identity")
        require(capabilities.get("seed_sha256") == INPUT_HASHES["HISTORY-SEED-R01G.md"], "S seed identity")
        require(capabilities.get("messages") == [spaced(message) for message in MESSAGES], "S message order")
        require(
            capabilities.get("faults") == {
                "action_success": ["none", "before_delivery", "after_delivery", "after_reply"],
                "half_close": ["none"],
                "no_write": ["none", "before_reply", "after_reply"],
                "state_change": ["none", "write_old", "write_new", "after_reply"],
            },
            "S fault description",
        )

    @staticmethod
    def class_of(handle: int) -> int:
        decode_code(handle)
        return handle

    def _boot(self, code: int) -> None:
        decode_code(code)
        response = self.process.request({"op": "boot", "image": f"{code:02x}"})
        require(response.get("ok") is True, "S valid boot failed")
        require(response.get("events") == [] and response.get("writes") == [], "S boot crossed public boundary or wrote")
        require(response.get("image") == f"{code:02x}" and response.get("status") == "running", "S boot result")
        self._validate_derived(response.get("derived_state"), code)

    @staticmethod
    def _validate_derived(state: Any, code: int) -> None:
        require(isinstance(state, dict), "S derived state shape")
        require(type(state.get("class")) is int, "S derived class type")
        require(type(state.get("revision")) is int, "S derived revision type")
        observation_value = state.get("observation")
        require(observation_value is None or type(observation_value) is int, "S derived observation type")
        require(type(state.get("interpreter")) is str, "S derived interpreter type")
        revision, table, observation = decode_code(code)
        require(
            state == {
                "class": code,
                "interpreter": ("-", "I", "N")[table],
                "observation": None if observation == 0 else observation - 1,
                "revision": revision,
            },
            "S derived state differs from quotient decoder",
        )

    @staticmethod
    def _faults(code: int, message: bytes) -> tuple[str, ...]:
        plan = oracle_plan(code, message)
        if plan.kind == "mutation" and plan.new_code != code:
            return ("none", "write_old", "write_new", "after_reply")
        if plan.kind == "action":
            return ("none", "before_delivery", "after_delivery", "after_reply")
        return ("none", "before_reply", "after_reply")

    @staticmethod
    def _semantic(code: int, message: bytes, fault: str) -> str:
        plan = oracle_plan(code, message)
        if fault == "none":
            return "none"
        if fault == "after_reply":
            return "after"
        if fault == "write_old":
            return "old"
        if fault == "write_new":
            return "new"
        if fault == "before_delivery":
            return "before_delivery"
        if fault == "after_delivery":
            return "after_delivery"
        if fault == "before_reply":
            return "noop_before_reply" if plan.kind == "mutation" else "before_reply"
        raise Failure(f"unknown S fault {fault}")

    def outcomes(self, code: int, message: bytes) -> dict[str, ActualStep]:
        key = (code, message)
        if key in self.outcome_cache:
            return self.outcome_cache[key]
        plan = oracle_plan(code, message)
        results: dict[str, ActualStep] = {}
        for fault in self._faults(code, message):
            self._boot(code)
            response = self.process.request({"op": "request", "message": spaced(message), "fault": fault})
            require(response.get("ok") is True, f"S request failed for {code}/{message.hex()}/{fault}")
            semantic = self._semantic(code, message, fault)
            expected = oracle_step(code, message, semantic)
            expected_immediate = expected.events if semantic == "none" else expected.events[:-2]
            require(tuple(response.get("events", ())) == expected_immediate, "S immediate public events")
            require(response.get("fault") == fault and response.get("message") == spaced(message), "S normalized request echo")
            expected_classification = (
                "state_change"
                if plan.kind == "mutation" and plan.new_code != code
                else "no_op"
                if plan.kind == "mutation"
                else "readonly"
                if plan.kind in ("read", "action")
                else "rejected"
            )
            require(response.get("classification") == expected_classification, "S classification")

            end = expected.final_class
            require(response.get("image") == f"{end:02x}", "S durable image")
            self._validate_derived(response.get("derived_state"), end)
            writes = response.get("writes")
            require(isinstance(writes, list), "S writes shape")
            if expected_classification == "state_change":
                outcome_name = "old" if fault == "write_old" else "new"
                require(
                    writes == [{"address": 0, "new": f"{plan.new_code:02x}", "old": f"{code:02x}", "outcome": outcome_name}],
                    "S write declaration",
                )
            else:
                require(writes == [], "S no-write transition wrote")

            events = tuple(response["events"])
            recovered: Optional[int] = None
            if semantic != "none":
                require(response.get("status") == "crashed", "S fault did not crash")
                restart = self.process.request({"op": "restart"})
                require(restart.get("ok") is True, "S restart failed")
                require(tuple(restart.get("events", ())) == ("K!RESTART", "R!88"), "S restart events")
                require(restart.get("image") == f"{end:02x}" and restart.get("writes") == [], "S restart persistence")
                self._validate_derived(restart.get("derived_state"), end)
                events += tuple(restart["events"])
                recovered = end
            else:
                require(response.get("status") == "running", "S no-fault lifecycle")
            actual = Outcome(events, recovered, end)
            require(actual == expected, f"S step differs from independent oracle: {code}/{message.hex()}/{fault}")
            results[fault] = ActualStep(end, actual)
        self.outcome_cache[key] = results
        return results

    def transition(self, code: int, message: bytes, semantic: str) -> ActualStep:
        plan = oracle_plan(code, message)
        if semantic == "none":
            fault = "none"
        elif semantic == "after":
            fault = "after_reply"
        elif semantic in ("old", "new"):
            fault = "write_" + semantic
        elif semantic in ("before_delivery", "after_delivery"):
            fault = semantic
        elif semantic == "before_reply":
            fault = "before_reply"
        elif semantic == "noop_before_reply":
            fault = "before_reply"
        else:
            raise Failure(f"S cannot map semantic {semantic}")
        require(fault in self._faults(code, message), "S inapplicable normalized schedule")
        if plan.kind == "mutation" and plan.new_code == code and semantic == "before_reply":
            semantic = "noop_before_reply"
        return self.outcomes(code, message)[fault]

    def boundary(self, code: int) -> ActualStep:
        if code in self.boundary_cache:
            return ActualStep(code, self.boundary_cache[code])
        self._boot(code)
        crash = self.process.request({"op": "crash"})
        require(crash.get("ok") is True and crash.get("events") == ["K!CRASH"], "S quiescent crash")
        require(crash.get("image") == f"{code:02x}" and crash.get("writes") == [], "S quiescent crash persistence")
        restart = self.process.request({"op": "restart"})
        require(restart.get("ok") is True and restart.get("events") == ["K!RESTART", "R!88"], "S quiescent restart")
        require(restart.get("image") == f"{code:02x}" and restart.get("writes") == [], "S quiescent restart persistence")
        self._validate_derived(restart.get("derived_state"), code)
        outcome = Outcome(("K!CRASH", "K!RESTART", "R!88"), code, code)
        self.boundary_cache[code] = outcome
        return ActualStep(code, outcome)

    def live_reset(self) -> None:
        """Reset one live protocol session; used only by the congruence suite."""
        response = self.process.request({"op": "reset"})
        require(response.get("ok") is True, "S live reset failed")
        require(response.get("events") == [] and response.get("writes") == [], "S live reset activity")
        require(response.get("image") == "00" and response.get("status") == "running", "S live reset state")
        require(response.get("crash_used") is False, "S live reset crash budget")
        self._validate_derived(response.get("derived_state"), 0)

    def live_request(
        self,
        code: int,
        message: bytes,
        fault: str = "none",
        expected_crash_used: Optional[bool] = None,
    ) -> tuple[int, tuple[str, ...]]:
        """Issue a request without booting, validating it against the independent oracle."""
        require(fault in self._faults(code, message), "S live request fault applicability")
        plan = oracle_plan(code, message)
        semantic = self._semantic(code, message, fault)
        expected = oracle_step(code, message, semantic)
        expected_immediate = expected.events if semantic == "none" else expected.events[:-2]
        response = self.process.request({"op": "request", "message": spaced(message), "fault": fault})
        require(response.get("ok") is True, "S live request failed")
        require(tuple(response.get("events", ())) == expected_immediate, "S live request public events")
        require(response.get("image") == f"{expected.final_class:02x}", "S live request durable image")
        require(response.get("fault") == fault and response.get("message") == spaced(message), "S live request echo")
        self._validate_derived(response.get("derived_state"), expected.final_class)
        writes = response.get("writes")
        require(isinstance(writes, list), "S live request writes shape")
        changes = plan.kind == "mutation" and plan.new_code != code
        if changes:
            outcome_name = "old" if fault == "write_old" else "new"
            require(
                writes == [{"address": 0, "new": f"{plan.new_code:02x}", "old": f"{code:02x}", "outcome": outcome_name}],
                "S live request write declaration",
            )
        else:
            require(writes == [], "S live no-write request wrote")
        require(response.get("status") == ("running" if fault == "none" else "crashed"), "S live lifecycle after request")
        if expected_crash_used is not None:
            require(response.get("crash_used") is expected_crash_used, "S live crash-budget state")
        return expected.final_class, tuple(response["events"])

    def live_restart(self, code: int) -> tuple[str, ...]:
        response = self.process.request({"op": "restart"})
        require(response.get("ok") is True, "S live restart failed")
        require(tuple(response.get("events", ())) == ("K!RESTART", "R!88"), "S live restart events")
        require(response.get("image") == f"{code:02x}" and response.get("writes") == [], "S live restart persistence")
        require(response.get("status") == "running" and response.get("crash_used") is True, "S live restart lifecycle")
        self._validate_derived(response.get("derived_state"), code)
        return tuple(response["events"])


def actual_specs(adapter: Any, start: Any, word: tuple[bytes, ...]) -> tuple[Spec, ...]:
    specs = [Spec("no_crash", "none"), Spec("boundary:0", "boundary", 0)]
    handle = start
    for index, message in enumerate(word):
        code = adapter.class_of(handle)
        plan = oracle_plan(code, message)
        specs.append(Spec(f"boundary:{index + 1}", "step", index, "after"))
        if adapter.name == "L" and plan.kind == "mutation":
            variants = ("old", "new")
        elif adapter.name == "S" and plan.kind == "mutation" and plan.new_code != code:
            variants = ("old", "new")
        elif plan.kind == "mutation":
            variants = ("noop_before_reply",)
        elif plan.kind == "action":
            variants = ("before_delivery", "after_delivery")
        else:
            variants = ("before_reply",)
        for variant in variants:
            specs.append(Spec(f"message:{index}:{variant}", "step", index, variant))
        handle = adapter.transition(handle, message, "none").handle
    return tuple(specs)


def actual_run(adapter: Any, start: Any, word: tuple[bytes, ...], spec: Spec) -> tuple[Outcome, Any]:
    parts: list[Outcome] = []
    handle = start
    if spec.kind == "boundary":
        require(spec.index == 0, "direct actual boundary must be cut boundary")
        boundary = adapter.boundary(handle)
        parts.append(boundary.outcome)
        handle = boundary.handle
    for index, message in enumerate(word):
        semantic = spec.semantic if spec.kind == "step" and spec.index == index else "none"
        step = adapter.transition(handle, message, semantic)
        parts.append(step.outcome)
        handle = step.handle
    if not parts:
        return Outcome((), None, adapter.class_of(start)), start
    outcome = append_outcomes(parts)
    require(outcome.final_class == adapter.class_of(handle), "actual final handle/quotient disagreement")
    return outcome, handle


def future_words() -> tuple[tuple[bytes, ...], ...]:
    words: list[tuple[bytes, ...]] = [()]
    for length in range(1, 4):
        words.extend(itertools.product(MESSAGES, repeat=length))
    require(len(words) == 1464, "future word count")
    return tuple(words)


def cut_histories() -> tuple[tuple[bytes, ...], ...]:
    histories: list[tuple[bytes, ...]] = [()]
    histories.extend((message,) for message in MESSAGES)
    histories.extend(itertools.product(MESSAGES, repeat=2))
    require(len(histories) == 133, "cut history count")
    return tuple(histories)


def feed_commitment(digest: Any, *pieces: str) -> None:
    for piece in pieces:
        encoded = piece.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)


def faultfree_oracle(code: int, word: Sequence[bytes]) -> Outcome:
    return oracle_run(code, tuple(word), Spec("no_crash", "none"))


def build_cut_records(l_adapter: LAdapter, s_adapter: SAdapter) -> tuple[list[dict[str, Any]], dict[Any, list[int]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    groups: dict[Any, list[int]] = defaultdict(list)
    class_histogram: Counter[int] = Counter()
    revision_histogram: Counter[int] = Counter()
    digest = hashlib.sha256()
    for history_index, history in enumerate(cut_histories()):
        code = 0
        l_handle: Any = l_adapter.initial
        s_handle: Any = s_adapter.initial
        oracle_events: list[str] = []
        l_events: list[str] = []
        s_events: list[str] = []
        for message in history:
            oracle_part = oracle_step(code, message, "none")
            l_part = l_adapter.transition(l_handle, message, "none")
            s_part = s_adapter.transition(s_handle, message, "none")
            require(l_part.outcome == oracle_part, f"L cut history mismatch at {history_index}")
            require(s_part.outcome == oracle_part, f"S cut history mismatch at {history_index}")
            oracle_events.extend(oracle_part.events)
            l_events.extend(l_part.outcome.events)
            s_events.extend(s_part.outcome.events)
            code = oracle_part.final_class
            l_handle = l_part.handle
            s_handle = s_part.handle
        require(tuple(l_events) == tuple(oracle_events) == tuple(s_events), "cut public transcript mismatch")
        require(l_adapter.class_of(l_handle) == s_adapter.class_of(s_handle) == code, "cut quotient mismatch")
        record = {
            "events": tuple(oracle_events),
            "history": history,
            "l": l_handle,
            "s": s_handle,
            "code": code,
        }
        records.append(record)
        key = (l_handle, s_handle, code)
        groups[key].append(history_index)
        class_histogram[code] += 1
        revision_histogram[decode_code(code)[0]] += 1
        feed_commitment(digest, str(history_index), canonical([message.hex() for message in history]), canonical(oracle_events), str(code), str(l_handle))

    expected_histogram = {
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
    require(dict(class_histogram) == expected_histogram, "cut class histogram")
    require(revision_histogram == Counter({0: 111, 1: 22}), "cut revision histogram")
    for key, indices in groups.items():
        for index in indices:
            record = records[index]
            require((record["l"], record["s"], record["code"]) == key, "factoring key invariant")
    report = {
        "class_histogram": {str(key): class_histogram[key] for key in sorted(class_histogram)},
        "classes": len(class_histogram),
        "groups_by_l_image_and_quotient": len(groups),
        "precut_projection_commitment_sha256": digest.hexdigest(),
        "revision_0": revision_histogram[0],
        "revision_1": revision_histogram[1],
        "total": len(records),
    }
    return records, groups, report


def scenario_set(adapter: Any, start: Any, code: int, word: tuple[bytes, ...]) -> tuple[set[str], int]:
    keys: set[str] = set()
    specs = actual_specs(adapter, start, word)
    labels: set[str] = set()
    for spec in specs:
        require(spec.label not in labels, f"duplicate {adapter.name} schedule label")
        labels.add(spec.label)
        actual, _ = actual_run(adapter, start, word, spec)
        oracle_semantic = spec.semantic
        if oracle_semantic == "noop_before_reply":
            oracle_semantic = "old"
        oracle_spec = Spec(spec.label, spec.kind, spec.index, oracle_semantic)
        expected = oracle_run(code, word, oracle_spec)
        require(actual == expected, f"{adapter.name} composed schedule differs: code={code} word={[m.hex() for m in word]} schedule={spec.label}")
        keys.add(actual.key())
    return keys, len(specs)


def oracle_set(code: int, word: tuple[bytes, ...]) -> tuple[set[str], int]:
    specs = abstract_specs(code, word)
    return {oracle_run(code, word, spec).key() for spec in specs}, len(specs)


def compare_products(
    records: list[dict[str, Any]],
    groups: dict[Any, list[int]],
    l_adapter: LAdapter,
    s_adapter: SAdapter,
) -> dict[str, Any]:
    words = future_words()
    expanded_scripts = 0
    factored_scripts = 0
    l_physical = 0
    s_physical = 0
    oracle_physical = 0
    canonical_behaviors = 0
    by_length: dict[str, Counter[str]] = {str(length): Counter() for length in range(4)}
    projection_commitment = hashlib.sha256()

    for (l_start, s_start, code), history_indices in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
        multiplicity = len(history_indices)
        require(l_adapter.class_of(l_start) == s_adapter.class_of(s_start) == code, "scenario start quotient")
        for word_index, word in enumerate(words):
            expected_set, expected_count = oracle_set(code, word)
            l_set, l_count = scenario_set(l_adapter, l_start, code, word)
            s_set, s_count = scenario_set(s_adapter, s_start, code, word)
            require(l_set == expected_set, f"L canonical trace set mismatch for {l_start}/{word_index}")
            require(s_set == expected_set, f"S canonical trace set mismatch for {s_start}/{word_index}")
            require(l_set == s_set, f"unlike canonical trace sets differ for {l_start}/{s_start}/{word_index}")
            factored_scripts += 1
            expanded_scripts += multiplicity
            l_physical += multiplicity * l_count
            s_physical += multiplicity * s_count
            oracle_physical += multiplicity * expected_count
            canonical_behaviors += multiplicity * len(expected_set)
            bucket = by_length[str(len(word))]
            bucket["scripts"] += multiplicity
            bucket["l_expanded_schedule_obligations"] += multiplicity * l_count
            bucket["s_expanded_schedule_obligations"] += multiplicity * s_count
            bucket["oracle_expanded_schedule_specs"] += multiplicity * expected_count
            bucket["canonical_behaviors"] += multiplicity * len(expected_set)
            scenario_digest = hashlib.sha256()
            for item in sorted(expected_set):
                feed_commitment(scenario_digest, item)
            for history_index in history_indices:
                record = records[history_index]
                feed_commitment(
                    projection_commitment,
                    str(history_index),
                    canonical([message.hex() for message in word]),
                    canonical(list(record["events"])),
                    scenario_digest.hexdigest(),
                )

    require(expanded_scripts == 133 * 1464 == 194712, "expanded script coverage")
    expected_scripts_by_length = {"0": 133, "1": 1463, "2": 16093, "3": 177023}
    require({key: by_length[key]["scripts"] for key in by_length} == expected_scripts_by_length, "scripts by future length")
    return {
        "abstract_oracle_expanded_schedule_specs": oracle_physical,
        "canonical_public_and_recovery_behaviors": canonical_behaviors,
        "expanded_history_future_scripts": expanded_scripts,
        "factored_history_future_state_cases": factored_scripts,
        "future_words": len(words),
        "l_expanded_schedule_obligations_symbolically_checked": l_physical,
        "projection_set_commitment_sha256": projection_commitment.hexdigest(),
        "s_expanded_schedule_obligations_symbolically_checked": s_physical,
        "by_future_length": {
            key: {name: by_length[key][name] for name in sorted(by_length[key])}
            for key in sorted(by_length)
        },
    }


def canonical_representative(code: int) -> tuple[bytes, ...]:
    revision, table, observation = decode_code(code)
    word: list[bytes] = []
    if revision:
        word.append(b"\x50")
    if table:
        word.append(b"\x10" if table == 1 else b"\x11")
    if observation:
        word.append(b"\x00" if observation == 1 else b"\x01")
    return tuple(word)


def full_class_checks(l_adapter: LAdapter, s_adapter: SAdapter) -> tuple[dict[int, str], dict[str, Any]]:
    l_images: dict[int, str] = {}
    packed: set[int] = set()
    representatives: set[bytes] = set()
    probes: set[tuple[int, int, int]] = set()
    for code in range(18):
        word = canonical_representative(code)
        oracle = faultfree_oracle(0, word)
        l_actual, l_handle = actual_run(l_adapter, l_adapter.initial, word, Spec("no_crash", "none"))
        s_actual, s_handle = actual_run(s_adapter, s_adapter.initial, word, Spec("no_crash", "none"))
        require(oracle == l_actual == s_actual and oracle.final_class == code, f"class {code} reachability")
        require(l_adapter.class_of(l_handle) == s_adapter.class_of(s_handle) == code, f"class {code} recovered reachability")
        l_images[code] = l_handle
        revision, table, observation = decode_code(code)
        packed.add(code)
        slots = list(message[0] for message in word) + [0xFF] * (3 - len(word))
        representatives.add(bytes((len(word), *slots)))
        probes.add((revision, (2, 0, 1)[table], (2, 0, 1)[observation]))
    require(len(packed) == len(representatives) == len(probes) == 18, "quotient representation collision")
    return l_images, {
        "canonical_representative_encodings": len(representatives),
        "full_horizon_classes": 18,
        "packed_encodings": len(packed),
        "probe_signatures": len(probes),
    }


def action_retry_checks(l_adapter: LAdapter, s_adapter: SAdapter, l_images: Mapping[int, str]) -> dict[str, int]:
    counts = Counter()
    for code in range(18):
        if oracle_plan(code, b"\x40").kind != "action":
            continue
        for adapter, start in ((l_adapter, l_images[code]), (s_adapter, code)):
            for semantic, attempts in (("before_delivery", 1), ("after_delivery", 2)):
                first = adapter.transition(start, b"\x40", semantic)
                retry = adapter.transition(first.handle, b"\x40", "none")
                combined = append_outcomes((first.outcome, retry.outcome))
                expected = append_outcomes((oracle_step(code, b"\x40", semantic), oracle_step(code, b"\x40", "none")))
                require(combined == expected, f"{adapter.name} action retry behavior")
                require(sum(event.startswith("D!") for event in combined.events) == attempts, "action retry delivery count")
                require(sum(event == "R!84" for event in combined.events) == 1, "action retry acknowledgement count")
                counts[adapter.name] += 1
    require(counts == Counter({"L": 16, "S": 16}), "action retry coverage")
    return {"l": counts["L"], "s": counts["S"], "successful_action_classes": 8, "total": sum(counts.values())}


def s_stateful_congruence_checks(s_adapter: SAdapter) -> dict[str, int]:
    """Exercise declared S states through live, non-cached multi-command paths.

    This is a bounded congruence/recomputation check, not a substitute for
    executing every expanded complete schedule in its own live session.
    """
    counts = Counter()

    # Every exact cut history is replayed live, once for every possible next
    # message.  This checks path convergence at all 133 declared cut points.
    for history in cut_histories():
        for probe in MESSAGES:
            s_adapter.live_reset()
            code = 0
            actual_events: list[str] = []
            for message in history + (probe,):
                code, events = s_adapter.live_request(code, message, "none", expected_crash_used=False)
                actual_events.extend(events)
            expected = faultfree_oracle(0, history + (probe,))
            require(tuple(actual_events) == expected.events and code == expected.final_class, "S live cut-path congruence")
            counts["cut_path_probe_sessions"] += 1
            counts["cut_path_requests"] += len(history) + 1

    # Reach every exposed crashing transition from each valid packed byte,
    # restart in the same live session, and try every fault-free next message.
    # The post-restart request retains crash_used=true, unlike cached boot tests.
    for code in range(18):
        for message in MESSAGES:
            for fault in s_adapter._faults(code, message):
                if fault == "none":
                    continue
                semantic = s_adapter._semantic(code, message, fault)
                first_expected = oracle_step(code, message, semantic)
                for probe in MESSAGES:
                    s_adapter._boot(code)
                    recovered, first_events = s_adapter.live_request(
                        code, message, fault, expected_crash_used=True
                    )
                    restart_events = s_adapter.live_restart(recovered)
                    final, probe_events = s_adapter.live_request(
                        recovered, probe, "none", expected_crash_used=True
                    )
                    expected_probe = oracle_step(recovered, probe, "none")
                    actual_events = first_events + restart_events + probe_events
                    expected_events = first_expected.events + expected_probe.events
                    require(actual_events == expected_events, "S post-recovery live public congruence")
                    require(final == expected_probe.final_class, "S post-recovery live quotient congruence")
                    counts["post_recovery_probe_sessions"] += 1
                    counts["post_recovery_requests"] += 2

    # Also retain crash_used=true across every quiescent boundary crash and
    # every possible next request; request-fault loops above do not cover it.
    for code in range(18):
        for probe in MESSAGES:
            s_adapter._boot(code)
            crash = s_adapter.process.request({"op": "crash"})
            require(crash.get("ok") is True, "S live quiescent crash failed")
            require(crash.get("events") == ["K!CRASH"] and crash.get("writes") == [], "S live quiescent crash activity")
            require(crash.get("image") == f"{code:02x}" and crash.get("status") == "crashed", "S live quiescent crash state")
            require(crash.get("crash_used") is True, "S live quiescent crash budget")
            restart_events = s_adapter.live_restart(code)
            final, probe_events = s_adapter.live_request(code, probe, "none", expected_crash_used=True)
            expected_probe = oracle_step(code, probe, "none")
            require(("K!CRASH",) + restart_events + probe_events == oracle_boundary(code).events + expected_probe.events, "S live boundary continuation")
            require(final == expected_probe.final_class, "S live boundary continuation quotient")
            counts["quiescent_recovery_probe_sessions"] += 1
            counts["quiescent_recovery_requests"] += 1

    require(counts["cut_path_probe_sessions"] == 133 * 11, "S live cut-path session count")
    require(counts["post_recovery_probe_sessions"] == 473 * 11, "S live post-recovery session count")
    require(counts["quiescent_recovery_probe_sessions"] == 18 * 11, "S live quiescent recovery session count")
    counts["live_sessions"] = (
        counts["cut_path_probe_sessions"]
        + counts["post_recovery_probe_sessions"]
        + counts["quiescent_recovery_probe_sessions"]
    )
    return {key: counts[key] for key in sorted(counts)}


def quotient_checks() -> dict[str, Any]:
    words = [()]
    words.extend((message,) for message in MESSAGES)
    words.extend(itertools.product(MESSAGES, repeat=2))
    max_depth = 0
    distinguished = 0
    full_depths: Counter[int] = Counter()
    full_witness_digest = hashlib.sha256()
    for left in range(18):
        for right in range(left + 1, 18):
            witness: Optional[tuple[bytes, ...]] = None
            for word in words:
                left_output = faultfree_oracle(left, word).events
                right_output = faultfree_oracle(right, word).events
                if left_output != right_output:
                    witness = tuple(word)
                    break
            require(witness is not None and len(witness) <= 2, f"class merge survived: {left}/{right}")
            max_depth = max(max_depth, len(witness))
            full_depths[len(witness)] += 1
            feed_commitment(full_witness_digest, str(left), str(right), canonical([message.hex() for message in witness]))
            distinguished += 1
    require(distinguished == 153 and max_depth == 2, "quotient witness coverage")

    cut_codes = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15)
    cut_distinguished = 0
    cut_witness_digest = hashlib.sha256()
    for left, right in itertools.combinations(cut_codes, 2):
        witness = next(
            (
                tuple(word)
                for word in words
                if faultfree_oracle(left, word).events != faultfree_oracle(right, word).events
            ),
            None,
        )
        require(witness is not None and len(witness) <= 2, f"cut class merge survived: {left}/{right}")
        feed_commitment(cut_witness_digest, str(left), str(right), canonical([message.hex() for message in witness]))
        cut_distinguished += 1
    require(cut_distinguished == 91, "cut-class merge coverage")

    handler_signatures: dict[bytes, str] = {}
    for message in MESSAGES:
        signature = []
        for code in range(18):
            plan = oracle_plan(code, message)
            signature.append((plan.kind, plan.new_code, plan.outputs))
        handler_signatures[message] = canonical(signature)
    require(len(set(handler_signatures.values())) == 11, "input handler transition signatures collided")
    handler_pairs = 0
    for left, right in itertools.combinations(MESSAGES, 2):
        require(handler_signatures[left] != handler_signatures[right], "input handler merge escaped")
        handler_pairs += 1
    require(handler_pairs == 55, "input-handler merge coverage")

    rejection_replies = {
        plan.outputs[0]
        for code in range(18)
        for message in MESSAGES
        for plan in (oracle_plan(code, message),)
        if plan.kind == "rejection"
    }
    require(rejection_replies == {f"R!e0 {value:02x}" for value in range(1, 7)}, "six rejection explanations")
    rejection_pair_controls = len(list(itertools.combinations(sorted(rejection_replies), 2)))
    require(rejection_pair_controls == 15, "rejection merge controls")

    # Execute the seed's characteristic-interpreter countermodel: author one
    # virtual interpreter per exact prior history, then query it against every
    # candidate prior.  Its 133 result vectors must be the identity matrix.
    histories = cut_histories()
    unrestricted_signatures: set[tuple[int, ...]] = set()
    characteristic_evaluations = 0
    for prior_index, prior in enumerate(histories):
        signature = tuple(1 if prior == target else 0 for target in histories)
        characteristic_evaluations += len(signature)
        require(sum(signature) == 1 and signature[prior_index] == 1, "characteristic interpreter result")
        unrestricted_signatures.add(signature)
    require(len(unrestricted_signatures) == 133, "unrestricted-history interpreter quotient")
    return {
        "class_merge_negative_controls": distinguished,
        "cut_class_merge_negative_controls": cut_distinguished,
        "cut_witness_commitment_sha256": cut_witness_digest.hexdigest(),
        "full_class_witness_commitment_sha256": full_witness_digest.hexdigest(),
        "full_class_witness_depths": {str(depth): full_depths[depth] for depth in sorted(full_depths)},
        "input_handler_merge_negative_controls": handler_pairs,
        "maximum_shortest_distinguishing_future": max_depth,
        "rejection_code_merge_negative_controls": rejection_pair_controls,
        "rejection_explanations": len(rejection_replies),
        "unrestricted_characteristic_evaluations": characteristic_evaluations,
        "unrestricted_interpreter_control_classes": len(unrestricted_signatures),
    }


def reachable_l_images() -> tuple[dict[str, int], Counter[int]]:
    current: dict[str, int] = {"ffffffffff": 0}
    all_images = dict(current)
    by_depth: Counter[int] = Counter({0: 1})
    for depth in range(5):
        next_level: dict[str, int] = {}
        for image, code in current.items():
            for opcode in MUTATOR_OPCODES:
                plan = oracle_plan(code, bytes((opcode,)))
                if plan.kind != "mutation":
                    continue
                cells = bytearray.fromhex(image)
                cells[depth] = opcode
                new_image = cells.hex()
                require(new_image not in all_images and new_image not in next_level, "L log encoding collision")
                next_level[new_image] = plan.new_code
        by_depth[depth + 1] = len(next_level)
        all_images.update(next_level)
        current = next_level
    return all_images, by_depth


def persistence_negative_checks(l_adapter: LAdapter, s_adapter: SAdapter) -> dict[str, Any]:
    counts = Counter()
    expected_images, by_depth = reachable_l_images()
    valid_seen: set[str] = set()
    for cells in itertools.product(L_ALPHABET, repeat=5):
        image = bytes(cells).hex()
        try:
            expected_code, _ = l_recover_independent(image)
        except ValueError:
            response = l_adapter.process.request({"op": "recover", "image": image})
            require_error(response, {"invalid_image"}, "L alphabet invalid image")
            counts["l_alphabet_invalid_images"] += 1
        else:
            require(l_adapter.class_of(image) == expected_code, "L alphabet valid image")
            valid_seen.add(image)
            counts["l_alphabet_valid_images"] += 1
        counts["l_alphabet_images"] += 1
    require(valid_seen == set(expected_images), "L accepted images differ from reachable append logs")
    require(counts["l_alphabet_images"] == 7**5, "L alphabet image total")

    invalid_byte_values = [value for value in range(256) if value not in L_ALPHABET]
    for position in range(5):
        for value in invalid_byte_values:
            cells = bytes((0x00,) * position + (value,) + (0xFF,) * (4 - position))
            response = l_adapter.process.request({"op": "recover", "image": cells.hex()})
            require_error(response, {"invalid_image"}, "L invalid opcode position")
            counts["l_invalid_opcode_position_cases"] += 1
    require(counts["l_invalid_opcode_position_cases"] == 5 * (256 - len(L_ALPHABET)), "L invalid opcode coverage")

    malformed_l = ("", "ff", "fffffffff", "ffffffffffff", "gggggggggg", "ff ff ff ff ff")
    for image in malformed_l:
        response = l_adapter.process.request({"op": "recover", "image": image})
        require_error(response, {"protocol_input"}, "L malformed image encoding")
        counts["l_malformed_image_encodings"] += 1

    image = l_adapter.initial
    for _ in range(5):
        image = l_adapter.transition(image, b"\x00", "none").handle
    require(image == "0000000000", "L capacity setup")
    for request in (
        {"op": "enumerate", "image": image, "message": "01"},
        {"op": "step", "image": image, "message": "01", "schedule": "none"},
        {"op": "step", "image": image, "message": "01", "schedule": "write_old"},
        {"op": "step", "image": image, "message": "01", "schedule": "write_new"},
        {"op": "step", "image": image, "message": "01", "schedule": "after_r"},
    ):
        response = l_adapter.process.request(request)
        require_error(response, {"capacity_exceeded"}, "L sixth successful mutator")
        counts["l_capacity_refusals"] += 1

    for raw in range(256):
        response = s_adapter.process.request({"op": "boot", "image": f"{raw:02x}"})
        if raw < 18:
            require(response.get("ok") is True and response.get("image") == f"{raw:02x}", "S valid image range")
            s_adapter._validate_derived(response.get("derived_state"), raw)
            counts["s_valid_images"] += 1
        else:
            require_error(response, {"invalid_image"}, "S invalid image range")
            counts["s_invalid_images"] += 1
    malformed_s = ("", "0", "00 00", "gg", "0000")
    for image_text in malformed_s:
        response = s_adapter.process.request({"op": "boot", "image": image_text})
        require_error(response, {"bad_hex", "bad_image_width"}, "S malformed image encoding")
        counts["s_malformed_image_encodings"] += 1

    l_bad_messages = ("", "02", "ff", "3001", "0001", "300000")
    for message in l_bad_messages:
        response = l_adapter.process.request({"op": "enumerate", "image": l_adapter.initial, "message": message})
        require_error(response, {"unsupported_message"}, "L unsupported message")
        counts["l_unsupported_message_samples"] += 1
    s_adapter._boot(0)
    for message in ("02", "ff", "30 01", "00 01", "30 00 00", "3000"):
        response = s_adapter.process.request({"op": "request", "message": message})
        require_error(response, {"unsupported_message", "bad_hex"}, "S unsupported message")
        require(response.get("events") == [] and response.get("writes") == [], "S protocol error created a crossing/write")
        counts["s_unsupported_message_samples"] += 1

    return {
        **{key: counts[key] for key in sorted(counts)},
        "l_reachable_images": len(expected_images),
        "l_reachable_images_by_log_length": {str(depth): by_depth[depth] for depth in range(6)},
    }


def stop_and_framing_checks(l_adapter: LAdapter, s_adapter: SAdapter) -> tuple[dict[str, Any], list[dict[str, str]]]:
    l_clean = ok_result(l_adapter.process.request({"op": "stop", "image": l_adapter.initial, "schedule": "none"}), "L clean STOP")
    l_events = ("C\u2193",) + l_adapter._outputs(l_clean.get("outputs"))
    require(l_events == ("C\u2193", "R!87") and l_clean.get("halted") is True, "L clean STOP trace")
    require(l_clean.get("crashed") is False and l_clean.get("schedule") == "none", "L clean STOP lifecycle")
    require(l_clean.get("image") == l_adapter.initial and l_clean.get("write") is None, "L clean STOP persistence")
    require(l_adapter._state_code(l_clean.get("state")) == 0, "L clean STOP state")

    s_adapter._boot(0)
    s_clean = s_adapter.process.request({"op": "half_close", "fault": "none"})
    require(s_clean.get("ok") is True and tuple(s_clean.get("events", ())) == ("C\u2193", "R!87"), "S clean STOP trace")
    require(s_clean.get("status") == "halted", "S clean STOP lifecycle")

    conditional_stop_traces: dict[str, list[str]] = {}
    for schedule, expected_prefix in (("before_r", ("C\u2193", "K!CRASH")), ("after_r", ("C\u2193", "R!87", "K!CRASH"))):
        raw = ok_result(l_adapter.process.request({"op": "stop", "image": l_adapter.initial, "schedule": schedule}), f"L STOP {schedule}")
        require(raw.get("crashed") is True and raw.get("schedule") == schedule, "L conditional STOP crash metadata")
        require(raw.get("halted") is (schedule == "after_r"), "L conditional STOP halt metadata")
        require(raw.get("image") == l_adapter.initial and raw.get("write") is None, "L conditional STOP persistence")
        require(l_adapter._state_code(raw.get("state")) == 0, "L conditional STOP recovered state")
        outputs = l_adapter._outputs(raw.get("outputs"))
        events = ("C\u2193",) + outputs + ("K!CRASH",)
        restart = l_adapter.restart(l_adapter.initial)
        events += restart.events
        require(events[: len(expected_prefix)] == expected_prefix and events[-2:] == ("K!RESTART", "R!88"), "L conditional STOP crash trace")
        conditional_stop_traces[schedule] = list(events)
    for fault in ("before_reply", "after_reply"):
        s_adapter._boot(0)
        response = s_adapter.process.request({"op": "half_close", "fault": fault})
        require_error(response, {"inapplicable_fault"}, "S extra STOP crash schedule")
        require(response.get("events") == [] and response.get("writes") == [], "S rejected STOP fault created activity")

    anchors = {
        "malformed": ["C!30 00", "R!e0 02"],
        "sequence": ["C!30", "R!e0 03", "C!00", "R!80 00"],
        "stop": ["C\u2193", "R!87"],
        "unknown": ["C!fe", "R!e0 01"],
    }
    require(len({canonical(value) for value in anchors.values()}) == 4, "STOP/framing anchors collided")
    for adapter, start in ((l_adapter, l_adapter.initial), (s_adapter, 0)):
        unknown = adapter.transition(start, b"\xfe", "none")
        malformed = adapter.transition(start, b"\x30\x00", "none")
        query = adapter.transition(start, b"\x30", "none")
        observe = adapter.transition(query.handle, b"\x00", "none")
        require(list(unknown.outcome.events) == anchors["unknown"], f"{adapter.name} unknown anchor")
        require(list(malformed.outcome.events) == anchors["malformed"], f"{adapter.name} malformed anchor")
        require(list(query.outcome.events + observe.outcome.events) == anchors["sequence"], f"{adapter.name} sequence anchor")

    unknowns = [
        {
            "id": "crash_interrupted_stop_scope",
            "status": "UNKNOWN",
            "reason": "The seed contracts clean terminal C-down separately from the continuing C-message crash product; L additionally exposes before/after-R STOP crash schedules while S exposes only clean STOP.",
            "chosen_conditional_interpretation": "Clean C-down/R!87 is compared as contracted. L's two extra STOP fault schedules are exercised against ordinary crossing-gap prefix semantics but excluded from unlike-equivalence trace-set equality; S's rejection of those extra schedules is verified.",
        }
    ]
    return {
        "anchor_histories": len(anchors),
        "clean_stop_realizations": 2,
        "l_conditional_extra_stop_schedule_reconstructions": conditional_stop_traces,
        "s_rejected_extra_stop_schedules": 2,
    }, unknowns


def deliberate_negative_controls() -> dict[str, Any]:
    controls = 0

    def differs(left: Outcome, right: Outcome, label: str) -> None:
        nonlocal controls
        require(left.key() != right.key(), f"negative control escaped comparison: {label}")
        controls += 1

    base = oracle_step(0, b"\x00", "none")
    differs(base, Outcome(("C!00", "R!80 01"), None, 1), "wrong reply byte")
    action = oracle_step(4, b"\x40", "none")
    differs(action, Outcome(("C!40", "R!84", "D!a0 00"), None, 4), "D/R reordering")
    identity = oracle_step(0, b"\x60", "none")
    differs(identity, Outcome(("C!60", "R!86 03 01 40 a1"), None, 0), "stale/wrong identity")
    old = oracle_step(0, b"\x10", "old")
    differs(old, Outcome(old.events, 3, 3), "old/new recovery merge")
    after_delivery = oracle_step(4, b"\x40", "after_delivery")
    differs(after_delivery, Outcome(after_delivery.events + ("D!a0 00",), 4, 4), "automatic action retry")
    differs(Outcome(("C\u2193", "R!87"), None, 0), Outcome(("C!fe", "R!e0 01"), None, 0), "STOP/message merge")
    differs(oracle_step(0, b"\x30\x00", "none"), append_outcomes((oracle_step(0, b"\x30", "none"), oracle_step(0, b"\x00", "none"))), "framing merge")
    before = oracle_step(4, b"\x40", "before_delivery")
    differs(before, Outcome(("C!40", "D!a0 00", "K!CRASH", "K!RESTART", "R!88"), 4, 4), "invented pre-D attempt")
    evolved = oracle_step(0, b"\x50", "after")
    differs(evolved, Outcome(evolved.events, 0, 0), "lost acknowledged mutation")
    rejection = oracle_step(0, b"\xfe", "none")
    differs(rejection, Outcome(("C!fe", "R!e0 02"), None, 0), "rejection explanation merge")
    require(controls == 10, "deliberate negative control total")
    return {
        "detected": controls,
        "injected": controls,
        "scope": "Local Outcome equality/ordering sensitivity controls; implementation mutation coverage is not claimed. Substantive finite merge attacks are reported under quotient.",
    }


def run() -> dict[str, Any]:
    hashes = verify_inputs()
    l_process = JsonlProcess(ROOT / "r01g_realization_l.py")
    s_process = JsonlProcess(ROOT / "r01g_realization_s.py")
    try:
        l_adapter = LAdapter(l_process)
        s_adapter = SAdapter(s_process)
        records, groups, cut_report = build_cut_records(l_adapter, s_adapter)
        l_images, class_report = full_class_checks(l_adapter, s_adapter)
        quotient_report = quotient_checks()
        comparison_report = compare_products(records, groups, l_adapter, s_adapter)
        retry_report = action_retry_checks(l_adapter, s_adapter, l_images)
        stateful_s_report = s_stateful_congruence_checks(s_adapter)
        persistence_report = persistence_negative_checks(l_adapter, s_adapter)
        framing_report, unknowns = stop_and_framing_checks(l_adapter, s_adapter)
        negative_report = deliberate_negative_controls()

        unknowns.extend(
            [
                {
                    "id": "expanded_end_to_end_session_execution",
                    "status": "UNKNOWN",
                    "reason": "The exact 194,712-script schedule product is constructed and matched under durable-image/quotient state factoring, not rerun as one fresh live subprocess session per expanded schedule. S live congruence covers every cut path/next message, every exposed request-crash outcome/next message, and every quiescent boundary-crash/next message, but not every length-0..3 post-recovery suffix in one uninterrupted session.",
                    "chosen_conditional_interpretation": "Expanded counters are named symbolic obligations, actual JSONL request counts are reported separately, and no end-to-end empirical unlike-realization claim is made.",
                },
                {
                    "id": "complete_attack_program",
                    "status": "UNKNOWN",
                    "reason": "This comparator executes class, cut-class, handler, rejection, persistence, framing, action, range, and characteristic-interpreter attacks, but it does not inject every DELETE/DERIVE/RECOMPUTE/TCB implementation mutation listed in seed section 9.",
                    "chosen_conditional_interpretation": "The finite transition comparison is reported separately from the seed's stronger all-attack empirical evidence gate.",
                },
            ]
        )

        require(verify_inputs() == hashes, "frozen inputs changed during comparison")
        protocol_calls = {"l_jsonl_requests": l_process.calls, "s_jsonl_requests": s_process.calls}
    finally:
        l_process.close()
        s_process.close()

    return {
        "claims": {
            "abstract_one_byte_transition_relation": "PASS",
            "complete_end_to_end_unlike_software_equivalence": "UNKNOWN",
            "condition": "See the three explicit UNKNOWN items; symbolic state factoring and live congruence are not mislabeled as fresh full-session executions.",
            "physical_media_or_power_loss_evidence": "NOT_CLAIMED",
            "receiver_semantic_effect": "UNSUPPORTED",
            "unlike_software_realization_equivalence_established": False,
        },
        "comparison": comparison_report,
        "coverage": {
            "action_retry": retry_report,
            "cut": cut_report,
            "full_classes_and_encodings": class_report,
            "negative_controls": negative_report,
            "persistence_and_range": persistence_report,
            "protocol_calls": protocol_calls,
            "quotient": quotient_report,
            "s_live_stateful_congruence": stateful_s_report,
            "stop_and_framing": framing_report,
        },
        "factoring_justification": {
            "machine_checked_invariant": "Every one of 133 cut transcripts was compared exactly and grouped only by identical L durable image, S packed byte, and independent quotient. All later adapter transitions were cached by durable image/byte plus message; expanded counts and commitments multiply only groups satisfying that invariant.",
            "public_projection_composition": "An already-equal checked pre-cut C/R/D prefix can be concatenated with an equal exact future C/R/D/K projection without changing equality. L provenance/capacity remains in the L-image grouping key.",
            "evidence_limit": "This is a symbolic transition-system proof over black-box one-step results. The separate S live congruence suite attacks path/cache dependence but does not turn multiplied expanded obligations into fresh physical subprocess runs.",
        },
        "hashes": {
            **hashes,
            "r01g_unlike_compare.py": hash_file(Path(__file__).resolve()),
        },
        "overall_status": "UNKNOWN",
        "specified_model_comparison": "PASS_FACTORED_TRANSITION_RELATION_ONLY",
        "unknowns": unknowns,
    }


def main() -> int:
    try:
        report = run()
    except Exception as exc:
        failure = {
            "error": {"message": str(exc), "type": type(exc).__name__},
            "overall_status": "FAIL",
        }
        sys.stdout.write(canonical(failure) + "\n")
        return 1
    sys.stdout.write(canonical(report) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
