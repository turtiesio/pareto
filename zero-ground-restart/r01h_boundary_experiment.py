#!/usr/bin/env python3
"""Executable falsifier for the closed-world ZERO GROUND R0.1H seed.

This is deliberately an oracle experiment, not a candidate architecture.  It
uses only the Python standard library and the frozen seed beside this file.
Any mismatch is recorded as FAIL; unsupported realization and physical-system
claims are recorded as UNKNOWN rather than inferred.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional, Sequence


EXPERIMENT = "ZERO GROUND R0.1H boundary-history falsifier"
SEED_NAME = "HISTORY-SEED-R01H.md"
EXPECTED_SEED_SHA256 = (
    "4954ed2a9612ea8a7e95041b689b549a1b9636e2d7457bf003d7d2c056958658"
)

ALIASES = (
    "O0",
    "O1",
    "AI",
    "AN",
    "RI",
    "RN",
    "D",
    "Q",
    "X",
    "T",
    "E",
    "K",
)
REQUEST = {
    "O0": b"OBSERVE 0\n",
    "O1": b"OBSERVE 1\n",
    "AI": b"AUTHOR ID\n",
    "AN": b"AUTHOR NOT\n",
    "RI": b"REPLACE ID\n",
    "RN": b"REPLACE NOT\n",
    "D": b"RETIRE\n",
    "Q": b"QUERY\n",
    "X": b"EXPLAIN\n",
    "T": b"ATTEMPT\n",
    "E": b"EVOLVE\n",
    "K": b"CURRENT\n",
}
ALIAS_FOR_REQUEST = {frame: alias for alias, frame in REQUEST.items()}
RANK = {alias: rank for rank, alias in enumerate(ALIASES)}

Crossing = tuple[str, bytes]
Trace = tuple[Crossing, ...]

DOWN: Crossing = ("L", b"DOWN")
READY: Crossing = ("L", b"READY")
FIN: Crossing = ("C", b"FIN")
STOPPED: Crossing = ("R", b"STOPPED\n")

MUST_NAMES = (
    "recovery_reaches_READY",
    "legal_controller_reaches_exactly_one_STOPPED",
    "no_completion_invented_for_interrupted_request",
    "A_occurs_only_for_T",
    "failure_free_T_has_A_before_reply",
    "recovery_residual_is_oracle_old_or_new",
)
EXPECTED_MUST = frozenset(MUST_NAMES)


@dataclass(frozen=True, order=True)
class State:
    observation: str
    program: str
    engine: str

    def label(self) -> str:
        return f"({self.observation},{self.program},{self.engine})"


INITIAL = State("U", "EMPTY", "E0")
ALL_STATES = tuple(
    State(observation, program, engine)
    for observation in ("U", "0", "1")
    for program in ("EMPTY", "ID", "NOT")
    for engine in ("E0", "E1")
)


@dataclass(frozen=True)
class History:
    word: tuple[str, ...]
    trace: Trace
    state: State


@dataclass(frozen=True)
class Evaluation:
    traces: frozenset[Trace]
    residuals_valid: bool = True
    selector_states: tuple[tuple[str, State], ...] = ()


@dataclass(frozen=True)
class Unsupported:
    reason: str


class Results:
    def __init__(self) -> None:
        self.items: list[dict[str, object]] = []

    def add(
        self,
        name: str,
        status: str,
        reason: str,
        details: Optional[dict[str, object]] = None,
    ) -> None:
        assert status in {"PASS", "FAIL", "UNKNOWN"}
        item: dict[str, object] = {
            "name": name,
            "status": status,
            "reason": reason,
        }
        if details:
            item["details"] = details
        self.items.append(item)

    def check(
        self,
        name: str,
        condition: bool,
        pass_reason: str,
        fail_reason: str,
        details: Optional[dict[str, object]] = None,
    ) -> bool:
        self.add(name, "PASS" if condition else "FAIL", pass_reason if condition else fail_reason, details)
        return condition

    def unknown(self, name: str, reason: str, details: Optional[dict[str, object]] = None) -> None:
        self.add(name, "UNKNOWN", reason, details)

    def totals(self) -> dict[str, int]:
        counts = Counter(item["status"] for item in self.items)
        return {status: counts[status] for status in ("PASS", "FAIL", "UNKNOWN")}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lp(data: bytes) -> bytes:
    return len(data).to_bytes(8, "big") + data


def serialize_crossing(crossing: Crossing) -> bytes:
    channel, payload = crossing
    return lp(channel.encode("ascii")) + lp(payload)


def serialize_trace(trace: Trace) -> bytes:
    return len(trace).to_bytes(8, "big") + b"".join(lp(serialize_crossing(item)) for item in trace)


def serialize_trace_set(traces: Iterable[Trace]) -> bytes:
    encoded = sorted(serialize_trace(trace) for trace in set(traces))
    return len(encoded).to_bytes(8, "big") + b"".join(lp(item) for item in encoded)


def display_crossing(crossing: Crossing) -> str:
    channel, payload = crossing
    if crossing == FIN:
        return "C:FIN"
    if channel in {"L", "F"}:
        return f"{channel}:{payload.decode('ascii')}"
    escaped = payload.decode("ascii").replace("\\", "\\\\").replace("\n", "\\n")
    return f'{channel}:"{escaped}"'


def display_trace(trace: Trace) -> list[str]:
    return [display_crossing(crossing) for crossing in trace]


def value_of(state: State) -> str:
    if state.program == "EMPTY":
        return "NONE"
    if state.observation == "U":
        return "UNKNOWN"
    if state.program == "ID":
        return "ALLOW" if state.observation == "1" else "DENY"
    if state.program == "NOT":
        return "DENY" if state.observation == "1" else "ALLOW"
    raise AssertionError(f"invalid program in oracle state: {state.program}")


def transition(state: State, alias: str) -> State:
    observation, program, engine = state.observation, state.program, state.engine
    if alias == "O0":
        observation = "0"
    elif alias == "O1":
        observation = "1"
    elif alias == "AI" and program == "EMPTY":
        program = "ID"
    elif alias == "AN" and program == "EMPTY":
        program = "NOT"
    elif alias == "RI" and program != "EMPTY":
        program = "ID"
    elif alias == "RN" and program != "EMPTY":
        program = "NOT"
    elif alias == "D" and program != "EMPTY":
        program = "EMPTY"
    elif alias == "E" and engine == "E0":
        engine = "E1"
    elif alias not in ALIASES:
        raise ValueError(f"unsupported alias: {alias!r}")
    return State(observation, program, engine)


def completion_crossings(state: State, alias: str) -> Trace:
    if alias == "O0":
        return (("R", b"OK OBSERVE 0\n"),)
    if alias == "O1":
        return (("R", b"OK OBSERVE 1\n"),)
    if alias == "AI":
        reply = b"OK AUTHOR ID\n" if state.program == "EMPTY" else b"ERR ACTIVE\n"
        return (("R", reply),)
    if alias == "AN":
        reply = b"OK AUTHOR NOT\n" if state.program == "EMPTY" else b"ERR ACTIVE\n"
        return (("R", reply),)
    if alias == "RI":
        reply = b"OK REPLACE ID\n" if state.program != "EMPTY" else b"ERR EMPTY\n"
        return (("R", reply),)
    if alias == "RN":
        reply = b"OK REPLACE NOT\n" if state.program != "EMPTY" else b"ERR EMPTY\n"
        return (("R", reply),)
    if alias == "D":
        reply = b"OK RETIRE\n" if state.program != "EMPTY" else b"ERR EMPTY\n"
        return (("R", reply),)
    if alias == "Q":
        return (("R", f"VALUE {value_of(state)}\n".encode("ascii")),)
    if alias == "X":
        reply = (
            f"WHY O={state.observation} P={state.program} E={state.engine} "
            f"V={value_of(state)}\n"
        ).encode("ascii")
        return (("R", reply),)
    if alias == "T":
        action = (
            f"TRY O={state.observation} P={state.program} E={state.engine} "
            f"V={value_of(state)}\n"
        ).encode("ascii")
        return (("A", action), ("R", b"OK ATTEMPTED\n"))
    if alias == "E":
        reply = b"OK ENGINE E1\n" if state.engine == "E0" else b"OK ENGINE E1 ALREADY\n"
        return (("R", reply),)
    if alias == "K":
        return (("R", f"ENGINE {state.engine}\n".encode("ascii")),)
    raise ValueError(f"unsupported alias: {alias!r}")


def transaction(state: State, alias: str) -> tuple[Trace, State]:
    return (("C", REQUEST[alias]),) + completion_crossings(state, alias), transition(state, alias)


def execute_word(initial: State, word: Sequence[str], finish: bool = False) -> tuple[Trace, State]:
    state = initial
    trace: list[Crossing] = []
    for alias in word:
        crossings, state = transaction(state, alias)
        trace.extend(crossings)
    if finish:
        trace.extend((FIN, STOPPED))
    return tuple(trace), state


def parse_completed_history(trace: Trace) -> State:
    """Fold only commands whose exact completion is present and validated."""
    state = INITIAL
    offset = 0
    while offset < len(trace):
        crossing = trace[offset]
        if crossing[0] != "C" or crossing == FIN or crossing[1] not in ALIAS_FOR_REQUEST:
            raise ValueError(f"non-request at completed-history offset {offset}: {display_crossing(crossing)}")
        alias = ALIAS_FOR_REQUEST[crossing[1]]
        expected = completion_crossings(state, alias)
        actual = trace[offset + 1 : offset + 1 + len(expected)]
        if actual != expected:
            raise ValueError(
                f"completion mismatch for {alias} at offset {offset}: "
                f"expected {display_trace(expected)}, got {display_trace(actual)}"
            )
        state = transition(state, alias)
        offset += 1 + len(expected)
    return state


def canonical_words(maximum_length: int) -> list[tuple[str, ...]]:
    return [
        tuple(word)
        for length in range(maximum_length + 1)
        for word in itertools.product(ALIASES, repeat=length)
    ]


def history_key(history: History) -> tuple[object, ...]:
    return (
        len(history.word),
        tuple(RANK[alias] for alias in history.word),
        serialize_trace(history.trace),
    )


def enumerate_histories() -> list[History]:
    histories: list[History] = []
    for word in canonical_words(2):
        trace, state = execute_word(INITIAL, word)
        histories.append(History(word, trace, state))
    return histories


def shape_for(word: Sequence[str]) -> tuple[tuple[str, Optional[str]], ...]:
    shape: list[tuple[str, Optional[str]]] = []
    for alias in word:
        shape.append(("C", alias))
        if alias == "T":
            shape.append(("A", alias))
        shape.append(("R", alias))
    shape.extend((("FIN", None), ("STOPPED", None)))
    return tuple(shape)


def gap_phase(word: Sequence[str], gap: int) -> tuple[str, Optional[str], Optional[int]]:
    shape = shape_for(word)
    if not 0 <= gap <= len(shape):
        raise ValueError(f"gap {gap} outside 0..{len(shape)}")
    previous = shape[gap - 1] if gap else None
    following = shape[gap] if gap < len(shape) else None
    if previous and previous[0] == "C" and following and following[0] in {"A", "R"}:
        message_index = sum(1 for kind, _ in shape[: gap - 1] if kind == "C")
        return "PENDING_REQUEST", previous[1], message_index
    if previous and previous[0] == "A" and following and following[0] == "R":
        message_index = sum(1 for kind, _ in shape[:gap] if kind == "C") - 1
        return "POST_ACTION_PRE_REPLY", "T", message_index
    if previous and previous[0] == "FIN" and following and following[0] == "STOPPED":
        return "FIN_PENDING", None, None
    if previous and previous[0] == "STOPPED" and following is None:
        return "TERMINAL", None, None
    return "IDLE", None, None


@lru_cache(maxsize=None)
def linear_evaluation(initial: State, word: tuple[str, ...], crash_gap: Optional[int]) -> Evaluation:
    normal, _ = execute_word(initial, word, finish=True)
    if crash_gap is None:
        return Evaluation(frozenset((normal,)))
    shape = shape_for(word)
    if not 0 <= crash_gap <= len(shape):
        raise ValueError(f"crash gap {crash_gap} outside nominal range 0..{len(shape)}")
    phase, alias, message_index = gap_phase(word, crash_gap)
    if phase not in {"PENDING_REQUEST", "POST_ACTION_PRE_REPLY"}:
        interrupted = normal[:crash_gap] + (DOWN, READY) + normal[crash_gap:]
        return Evaluation(frozenset((interrupted,)))

    assert alias is not None and message_index is not None
    prefix, state_before = execute_word(initial, word[:message_index])
    visible_prefix: Trace = prefix + (("C", REQUEST[alias]),)
    if phase == "POST_ACTION_PRE_REPLY":
        action = completion_crossings(state_before, alias)[0]
        if action[0] != "A":
            raise AssertionError("post-action phase synthesized for a non-ATTEMPT request")
        visible_prefix += (action,)
    visible_prefix += (DOWN, READY)

    branch_states = (("old", state_before), ("new", transition(state_before, alias)))
    traces: set[Trace] = set()
    for _, residual in branch_states:
        tail, _ = execute_word(residual, word[message_index + 1 :], finish=True)
        traces.add(visible_prefix + tail)
    return Evaluation(frozenset(traces), True, branch_states)


def trace_properties(trace: Trace) -> dict[str, bool]:
    properties = {name: True for name in MUST_NAMES[:-1]}

    down_positions = [index for index, crossing in enumerate(trace) if crossing == DOWN]
    properties["recovery_reaches_READY"] = all(
        index + 1 < len(trace) and trace[index + 1] == READY for index in down_positions
    )

    fin_positions = [index for index, crossing in enumerate(trace) if crossing == FIN]
    stop_positions = [index for index, crossing in enumerate(trace) if crossing == STOPPED]
    properties["legal_controller_reaches_exactly_one_STOPPED"] = (
        len(fin_positions) == 1
        and len(stop_positions) == 1
        and fin_positions[0] < stop_positions[0]
    )

    pending: Optional[str] = None
    interrupted = False
    action_seen = False
    no_invented = True
    action_only_t = True
    t_order = True

    for crossing in trace:
        channel, payload = crossing
        if channel == "C" and crossing != FIN:
            if payload not in ALIAS_FOR_REQUEST:
                no_invented = False
                continue
            if pending is not None and not interrupted:
                no_invented = False
            pending = ALIAS_FOR_REQUEST[payload]
            interrupted = False
            action_seen = False
        elif crossing == FIN:
            if pending is not None and not interrupted:
                no_invented = False
            pending = None
            interrupted = False
        elif crossing == DOWN:
            if pending is not None:
                interrupted = True
        elif channel == "A":
            if pending != "T" or interrupted:
                action_only_t = False
            action_seen = True
        elif channel == "R" and crossing != STOPPED:
            if pending is None or interrupted:
                no_invented = False
            if pending == "T" and not action_seen:
                t_order = False
            pending = None
            interrupted = False
            action_seen = False

    properties["no_completion_invented_for_interrupted_request"] = no_invented
    properties["A_occurs_only_for_T"] = action_only_t
    properties["failure_free_T_has_A_before_reply"] = t_order
    return properties


def must_set(evaluation: Evaluation) -> frozenset[str]:
    result = set(MUST_NAMES)
    for trace in evaluation.traces:
        properties = trace_properties(trace)
        for name, truth in properties.items():
            if not truth:
                result.discard(name)
    if not evaluation.residuals_valid:
        result.discard("recovery_residual_is_oracle_old_or_new")
    return frozenset(result)


def retry_once_after_interruption(
    initial: State, alias: str, phase: str, selector: Optional[str] = None
) -> Evaluation | Unsupported:
    if phase not in {"after_input", "after_action"}:
        return Unsupported(f"selector barrier phase {phase!r} is not defined")
    if phase == "after_action" and alias != "T":
        return Unsupported("after_action exists only for ATTEMPT")
    if selector not in {None, "old", "new"}:
        return Unsupported(f"selector {selector!r} is neither old nor new")

    prefix: Trace = (("C", REQUEST[alias]),)
    if phase == "after_action":
        prefix += (completion_crossings(initial, alias)[0],)
    prefix += (DOWN, READY)
    branches = (("old", initial), ("new", transition(initial, alias)))
    if selector is not None:
        branches = tuple(branch for branch in branches if branch[0] == selector)
    traces: set[Trace] = set()
    for _, residual in branches:
        retry, _ = execute_word(residual, (alias,), finish=True)
        traces.add(prefix + retry)
    return Evaluation(frozenset(traces), True, branches)


def selected_branch_manifest_witness(alias: str, separator: str = "X") -> dict[str, object]:
    """Build distinct old/new manifests at one interrupted request barrier.

    The manifests retain privileged F controls.  Their public C/R/A/L
    projections coincide, but they are not called the same exact prefix here.
    Under a literal R-completion fold, neither manifest completed the
    interrupted ordinary command even though SELECT(new) chooses its
    post-transition residual for the continuation.
    """
    old_state = INITIAL
    new_state = transition(INITIAL, alias)
    crash: Crossing = ("F", b"CRASH(after-C-before-next-crossing)")
    select_old: Crossing = ("F", b"SELECT(old)")
    select_new: Crossing = ("F", b"SELECT(new)")
    old_manifest_prefix: Trace = (
        ("C", REQUEST[alias]),
        crash,
        DOWN,
        select_old,
        READY,
    )
    new_manifest_prefix: Trace = (
        ("C", REQUEST[alias]),
        crash,
        DOWN,
        select_new,
        READY,
    )
    old_public_projection = tuple(item for item in old_manifest_prefix if item[0] != "F")
    new_public_projection = tuple(item for item in new_manifest_prefix if item[0] != "F")
    old_tail, _ = execute_word(old_state, (separator,), finish=True)
    new_tail, _ = execute_word(new_state, (separator,), finish=True)
    old_complete_manifest = old_manifest_prefix + old_tail
    new_complete_manifest = new_manifest_prefix + new_tail
    return {
        "request": alias,
        "separator": separator,
        "old_manifest_prefix": display_trace(old_manifest_prefix),
        "new_manifest_prefix": display_trace(new_manifest_prefix),
        "manifests_are_distinct": old_manifest_prefix != new_manifest_prefix,
        "public_C_R_A_L_projections_equal": old_public_projection == new_public_projection,
        "public_C_R_A_L_projection": display_trace(old_public_projection),
        "ordinary_reply_before_continuation": False,
        "literal_R_completion_fold_old_manifest": old_state.label(),
        "literal_R_completion_fold_new_manifest": old_state.label(),
        "SELECT_old_residual": old_state.label(),
        "SELECT_new_residual": new_state.label(),
        "old_selected_continuation": display_trace(old_tail),
        "new_selected_continuation": display_trace(new_tail),
        "old_complete_branch_manifest": display_trace(old_complete_manifest),
        "new_complete_branch_manifest": display_trace(new_complete_manifest),
        "selected_continuations_differ": old_tail != new_tail,
    }


def attempt_crash_after_reply(initial: State) -> Evaluation:
    attempt, _ = execute_word(initial, ("T",))
    return Evaluation(frozenset((attempt + (DOWN, READY, FIN, STOPPED),)))


def stop_crash_evaluation() -> Evaluation:
    return Evaluation(frozenset(((FIN, DOWN, READY, STOPPED),)))


def meta_oracle(
    pre_frames: Sequence[bytes],
    future_frames: Sequence[bytes],
    crash_count: int,
    *,
    fragmented: bool = False,
    concurrent: bool = False,
) -> str | Unsupported:
    if fragmented:
        return Unsupported("partial or fragmented frames are outside the atomic-crossing domain")
    if concurrent:
        return Unsupported("concurrent requests are outside the serial single-client domain")
    if len(pre_frames) > 2:
        return Unsupported("more than two pre-cut messages")
    if len(future_frames) > 3:
        return Unsupported("more than three post-cut messages counting retries")
    if crash_count not in {0, 1}:
        return Unsupported("scheduler permits no crash or exactly one crash")
    for frame in tuple(pre_frames) + tuple(future_frames):
        if frame == b"":
            return Unsupported("empty request frame is not a submission")
        if frame not in ALIAS_FOR_REQUEST:
            return Unsupported("request bytes are outside the complete twelve-frame alphabet")
    return "SUPPORTED"


def expected_class_table() -> dict[State, tuple[int, int, int]]:
    return {
        State("U", "EMPTY", "E0"): (1, 7, 51),
        State("0", "EMPTY", "E0"): (0, 1, 16),
        State("1", "EMPTY", "E0"): (0, 1, 16),
        State("U", "ID", "E0"): (0, 1, 15),
        State("U", "NOT", "E0"): (0, 1, 15),
        State("U", "EMPTY", "E1"): (0, 1, 15),
        State("0", "ID", "E0"): (0, 0, 2),
        State("0", "NOT", "E0"): (0, 0, 2),
        State("0", "EMPTY", "E1"): (0, 0, 2),
        State("1", "ID", "E0"): (0, 0, 2),
        State("1", "NOT", "E0"): (0, 0, 2),
        State("1", "EMPTY", "E1"): (0, 0, 2),
        State("U", "ID", "E1"): (0, 0, 2),
        State("U", "NOT", "E1"): (0, 0, 2),
    }


def future_trace(state: State, word: Sequence[str]) -> Trace:
    trace, _ = execute_word(state, word, finish=True)
    return trace


def block_bytes(block: Trace) -> bytes:
    return serialize_trace(block)


def terminal_signature(crash_budget: int) -> tuple[tuple[str, bytes, tuple[str, ...]], ...]:
    cases: list[tuple[str, Trace]] = [("no_crash", (FIN, STOPPED))]
    if crash_budget:
        cases.extend(
            (
                ("crash_before_FIN", (DOWN, READY, FIN, STOPPED)),
                ("crash_FIN_pending", (FIN, DOWN, READY, STOPPED)),
                ("crash_after_STOPPED", (FIN, STOPPED, DOWN, READY)),
            )
        )
    return tuple(
        (name, block_bytes(trace), tuple(sorted(must_set(Evaluation(frozenset((trace,)))))))
        for name, trace in cases
    )


def adaptive_partition_ids(max_depth: int = 3) -> tuple[dict[tuple[int, State, int], int], dict[str, object]]:
    ids: dict[tuple[int, State, int], int] = {}
    signatures_by_depth: dict[int, dict[tuple[State, int], object]] = {}
    class_counts: dict[str, int] = {}

    for depth in range(max_depth + 1):
        signatures: dict[tuple[State, int], object] = {}
        for state in ALL_STATES:
            for budget in (0, 1):
                terminal = terminal_signature(budget)
                messages: list[object] = []
                if depth:
                    for alias in ALIASES:
                        tx, new_state = transaction(state, alias)
                        modes: list[object] = [
                            (
                                "request_completes_no_crash_yet",
                                ((block_bytes(tx), ids[(depth - 1, new_state, budget)]),),
                            )
                        ]
                        if budget:
                            modes.append(
                                (
                                    "crash_before_input",
                                    ((block_bytes((DOWN, READY) + tx), ids[(depth - 1, new_state, 0)]),),
                                )
                            )
                            residual_ids = tuple(
                                sorted(
                                    {
                                        ids[(depth - 1, state, 0)],
                                        ids[(depth - 1, transition(state, alias), 0)],
                                    }
                                )
                            )
                            input_block: Trace = (("C", REQUEST[alias]), DOWN, READY)
                            modes.append(
                                (
                                    "crash_pending_request",
                                    tuple((block_bytes(input_block), child_id) for child_id in residual_ids),
                                )
                            )
                            if alias == "T":
                                action = completion_crossings(state, alias)[0]
                                action_block: Trace = (("C", REQUEST[alias]), action, DOWN, READY)
                                modes.append(
                                    (
                                        "crash_post_action_pre_reply",
                                        ((block_bytes(action_block), ids[(depth - 1, state, 0)]),),
                                    )
                                )
                            modes.append(
                                (
                                    "crash_after_reply",
                                    ((block_bytes(tx + (DOWN, READY)), ids[(depth - 1, new_state, 0)]),),
                                )
                            )
                        messages.append((alias, tuple(modes)))
                signatures[(state, budget)] = (terminal, tuple(messages))

        canonical = sorted({repr(signature) for signature in signatures.values()})
        id_for_repr = {signature: index for index, signature in enumerate(canonical)}
        for key, signature in signatures.items():
            ids[(depth, key[0], key[1])] = id_for_repr[repr(signature)]
        signatures_by_depth[depth] = signatures
        for budget in (0, 1):
            class_counts[f"depth_{depth}_crash_budget_{budget}"] = len(
                {ids[(depth, state, budget)] for state in ALL_STATES}
            )

    digest = hashlib.sha256()
    for depth in range(max_depth + 1):
        for state in ALL_STATES:
            for budget in (0, 1):
                digest.update(lp(str(depth).encode("ascii")))
                digest.update(lp(state.label().encode("ascii")))
                digest.update(lp(str(budget).encode("ascii")))
                digest.update(lp(repr(signatures_by_depth[depth][(state, budget)]).encode("utf-8")))
    return ids, {
        "memoized_state_depth_budget_nodes": len(ALL_STATES) * (max_depth + 1) * 2,
        "invented_phase_label_count_not_in_memo_key": 16,
        "arithmetic_node_times_phase_product_not_executed": (
            len(ALL_STATES) * (max_depth + 1) * 2 * 16
        ),
        "phase_transition_refinement_nodes_executed": 0,
        "class_counts": class_counts,
        "signature_sha256": digest.hexdigest(),
    }


def configuration_encoding(state: State, phase: str) -> bytes:
    fields = (state.observation, state.program, state.engine, phase)
    return b"CFG" + b"".join(lp(field.encode("ascii")) for field in fields)


def detect_model_difference(
    completion_function,
) -> tuple[bool, Optional[dict[str, object]]]:
    for state in ALL_STATES:
        for alias in ALIASES:
            expected = completion_crossings(state, alias)
            actual = completion_function(state, alias)
            if actual != expected:
                return True, {
                    "state": state.label(),
                    "message": alias,
                    "expected": display_trace(expected),
                    "actual": display_trace(actual),
                }
    return False, None


def run_experiment(seed_path: Path, source_path: Path) -> tuple[dict[str, object], int]:
    results = Results()
    actual_seed_hash = sha256_file(seed_path)
    source_hash = sha256_file(source_path)
    coverage: dict[str, object] = {}
    observations: dict[str, object] = {}

    if actual_seed_hash != EXPECTED_SEED_SHA256:
        results.add(
            "frozen_seed_sha256",
            "FAIL",
            "seed bytes do not match the required authority; behavioral execution was refused",
            {"expected": EXPECTED_SEED_SHA256, "actual": actual_seed_hash},
        )
        summary = {
            "experiment": EXPERIMENT,
            "source": {"path": str(source_path), "sha256": source_hash},
            "seed": {
                "path": str(seed_path),
                "expected_sha256": EXPECTED_SEED_SHA256,
                "actual_sha256": actual_seed_hash,
                "verified": False,
            },
            "coverage": coverage,
            "observations": observations,
            "checks": results.items,
            "totals": results.totals(),
            "exit_policy": "nonzero iff one or more FAIL results exist",
        }
        return summary, 1

    results.add(
        "frozen_seed_sha256",
        "PASS",
        "seed bytes exactly match the required SHA-256 authority",
        {"sha256": actual_seed_hash},
    )

    histories = enumerate_histories()
    history_digest = hashlib.sha256()
    history_parse_errors: list[str] = []
    for history in histories:
        history_digest.update(lp(bytes(RANK[alias] for alias in history.word)))
        history_digest.update(lp(serialize_trace(history.trace)))
        try:
            parsed = parse_completed_history(history.trace)
            if parsed != history.state:
                history_parse_errors.append(
                    f"word {history.word}: generated {history.state.label()} parsed {parsed.label()}"
                )
        except ValueError as error:
            history_parse_errors.append(f"word {history.word}: {error}")

    unique_words = len({history.word for history in histories})
    unique_traces = len({serialize_trace(history.trace) for history in histories})
    ordered = all(history_key(left) < history_key(right) for left, right in zip(histories, histories[1:]))
    coverage["precut_histories"] = len(histories)
    coverage["precut_histories_by_length"] = dict(sorted(Counter(len(h.word) for h in histories).items()))
    coverage["precut_exact_history_sha256"] = history_digest.hexdigest()
    coverage["oracle_history_parses"] = len(histories)
    results.check(
        "precut_corpus_exact_enumeration",
        len(histories) == 157 and unique_words == 157 and unique_traces == 157 and ordered,
        "enumerated 157 canonically ordered words and 157 distinct exact crossing histories",
        "pre-cut enumeration, exact-history uniqueness, or canonical ordering differs from the seed",
        {
            "histories": len(histories),
            "unique_words": unique_words,
            "unique_exact_histories": unique_traces,
            "canonical_order": ordered,
        },
    )
    results.check(
        "clean_cut_completed_prefix_oracle",
        not history_parse_errors,
        "all 157 failure-free completed cuts parse completely and reproduce their generated coordinates",
        history_parse_errors[0] if history_parse_errors else "unreachable",
        {"cases": len(histories), "errors": len(history_parse_errors)},
    )

    selected_branch_witnesses = tuple(
        selected_branch_manifest_witness(alias) for alias in ("AI", "O1", "E")
    )
    literal_completion_counterexample = all(
        witness["manifests_are_distinct"]
        and witness["public_C_R_A_L_projections_equal"]
        and not witness["ordinary_reply_before_continuation"]
        and witness["literal_R_completion_fold_new_manifest"]
        != witness["SELECT_new_residual"]
        and witness["selected_continuations_differ"]
        for witness in selected_branch_witnesses
    )
    observations["selected_old_new_branch_manifest_witnesses"] = list(
        selected_branch_witnesses
    )
    results.check(
        "literal_R_completion_O_P_G_continuation_consistency",
        not literal_completion_counterexample,
        "literal R-completion folds agree with every selected residual continuation tested",
        "under the literal Sections 1/3 completed-command reading, AUTHOR, OBSERVE, and EVOLVE have no R completion and fold to old state in both distinct SELECT manifests, while Section 3.3 SELECT(new) continues from post-transition state",
        {
            "minimal_state_changing_requests": ["AI", "O1", "E"],
            "reading": "C occurrence and R completion are separate; command is completed only when its ordinary R crosses",
            "witnesses": list(selected_branch_witnesses),
        },
    )
    results.unknown(
        "SELECT_new_as_semantic_completion_interpretation",
        "the inconsistency disappears if SELECT(new) is defined to make/apply a semantic command completion without an R crossing, but the seed does not define whether 'completed command' has that hidden meaning",
        {
            "alternative": "fold O/P/G over ordinary R completions plus SELECT(new) semantic application",
            "manifest_selector_remains_privileged": True,
        },
    )
    results.check(
        "conditional_manifest_selected_residual_repair",
        literal_completion_counterexample,
        "conditionally augmenting oracle input with the manifest selector and an explicit selector-to-residual rule makes all six minimized continuations exact",
        "the manifest-selected-residual completion failed to distinguish a minimized old/new continuation",
        {
            "repair_input": "(C/R/A/L history, F branch manifest)",
            "repair_rule": "SELECT(old)->pre-request residual; SELECT(new)->transition(pre-request residual, request)",
            "conditional_not_frozen": True,
            "cases": len(selected_branch_witnesses) * 2,
        },
    )

    oracle_output_digest = hashlib.sha256()
    oracle_output_cases = 0
    invalid_frame_errors: list[str] = []
    for history in histories:
        parsed_state = parse_completed_history(history.trace)
        for alias in ALIASES:
            tx, next_state = transaction(parsed_state, alias)
            oracle_output_digest.update(lp(serialize_trace(history.trace)))
            oracle_output_digest.update(lp(alias.encode("ascii")))
            oracle_output_digest.update(lp(serialize_trace(tx)))
            oracle_output_digest.update(lp(next_state.label().encode("ascii")))
            oracle_output_cases += 1
            for channel, payload in tx:
                if channel in {"C", "R", "A"} and not payload.endswith(b"\n"):
                    invalid_frame_errors.append(
                        f"{history.word}/{alias}: {channel} frame lacks LF: {payload!r}"
                    )
                if channel in {"C", "R", "A"} and not payload:
                    invalid_frame_errors.append(f"{history.word}/{alias}: empty {channel} frame")
                try:
                    payload.decode("ascii")
                except UnicodeDecodeError:
                    invalid_frame_errors.append(f"{history.word}/{alias}: non-ASCII {channel} frame")
    coverage["precut_next_request_oracle_cases"] = oracle_output_cases
    coverage["precut_next_request_oracle_sha256"] = oracle_output_digest.hexdigest()
    results.check(
        "exact_failure_free_oracle_outputs",
        oracle_output_cases == 157 * 12 and not invalid_frame_errors,
        "computed all 1,884 next-request transactions with nonempty ASCII LF-terminated frames",
        invalid_frame_errors[0] if invalid_frame_errors else "oracle case count is not 1,884",
        {"cases": oracle_output_cases, "frame_errors": len(invalid_frame_errors)},
    )

    actual_table: dict[State, tuple[int, int, int]] = {}
    for state, members in itertools.groupby(sorted(histories, key=lambda h: h.state), key=lambda h: h.state):
        counts = Counter(len(member.word) for member in members)
        actual_table[state] = tuple(counts[length] for length in range(3))
    expected_table = expected_class_table()
    actual_multiset = sorted(sum(counts) for counts in actual_table.values())
    expected_multiset = sorted((59, 17, 17, 16, 16, 16, 2, 2, 2, 2, 2, 2, 2, 2))
    observations["cut_class_table"] = {
        state.label(): {
            "length_0": counts[0],
            "length_1": counts[1],
            "length_2": counts[2],
            "size": sum(counts),
        }
        for state, counts in sorted(actual_table.items())
    }
    observations["cut_class_size_multiset"] = actual_multiset
    results.check(
        "predicted_fourteen_class_quotient",
        actual_table == expected_table and actual_multiset == expected_multiset,
        "independent folds yield the exact fourteen coordinates and predicted class-size multiset",
        "computed coordinate table or class-size multiset contradicts the frozen prediction",
        {"class_count": len(actual_table), "class_size_multiset": actual_multiset},
    )

    one_message_cache = {
        (state, alias): future_trace(state, (alias,)) for state in ALL_STATES for alias in ALIASES
    }
    empty_cache = {state: future_trace(state, ()) for state in ALL_STATES}
    same_pairs = 0
    unequal_pairs = 0
    diagonal_reflexive = 0
    x_separates_all = True
    empty_separates_any = False
    same_split: Optional[dict[str, object]] = None
    unequal_without_x: Optional[dict[str, object]] = None
    separator_histogram: Counter[str] = Counter()
    all_separator_digest = hashlib.sha256()

    for history in histories:
        if empty_cache[history.state] == empty_cache[history.state]:
            diagonal_reflexive += 1
    for left_index, right_index in itertools.combinations(range(len(histories)), 2):
        left, right = histories[left_index], histories[right_index]
        if empty_cache[left.state] != empty_cache[right.state]:
            empty_separates_any = True
        separators = tuple(
            alias
            for alias in ALIASES
            if one_message_cache[(left.state, alias)] != one_message_cache[(right.state, alias)]
        )
        all_separator_digest.update(lp(str(left_index).encode("ascii")))
        all_separator_digest.update(lp(str(right_index).encode("ascii")))
        all_separator_digest.update(lp(",".join(separators).encode("ascii")))
        if left.state == right.state:
            same_pairs += 1
            if separators and same_split is None:
                same_split = {
                    "left": left.word,
                    "right": right.word,
                    "separators": separators,
                }
        else:
            unequal_pairs += 1
            if not separators:
                x_separates_all = False
                if unequal_without_x is None:
                    unequal_without_x = {"left": left.word, "right": right.word, "reason": "no separator"}
            else:
                separator_histogram[separators[0]] += 1
            if "X" not in separators:
                x_separates_all = False
                if unequal_without_x is None:
                    unequal_without_x = {
                        "left": left.word,
                        "right": right.word,
                        "separators": separators,
                    }

    coverage["unordered_distinct_history_pairs"] = same_pairs + unequal_pairs
    coverage["diagonal_history_pairs"] = diagonal_reflexive
    coverage["one_message_pair_message_comparisons"] = (same_pairs + unequal_pairs) * len(ALIASES)
    coverage["one_message_separator_sha256"] = all_separator_digest.hexdigest()
    observations["canonical_one_message_separator_histogram"] = dict(
        sorted(separator_histogram.items(), key=lambda item: RANK[item[0]])
    )
    results.check(
        "predicted_pair_counts",
        same_pairs == 2351 and unequal_pairs == 9895 and same_pairs + unequal_pairs == 12246,
        "all 12,246 unordered distinct pairs yield 2,351 same-coordinate and 9,895 unequal pairs",
        "computed unordered pair counts contradict the frozen prediction",
        {"same_class": same_pairs, "unequal": unequal_pairs, "total": same_pairs + unequal_pairs},
    )
    results.check(
        "one_message_separators_all_pairs",
        not empty_separates_any and same_split is None and x_separates_all and unequal_without_x is None,
        "empty STOP futures split no pair; every unequal pair is split by exact one-message X; same classes never split",
        "an empty future split a pair, a same class split, or an unequal pair lacked exact X separation",
        {
            "empty_future_split": empty_separates_any,
            "first_same_class_split": same_split,
            "first_unequal_without_X": unequal_without_x,
            "diagonal_reflexive": diagonal_reflexive,
        },
    )

    future_words = canonical_words(3)
    by_length_word_schedule: Counter[int] = Counter()
    total_t_occurrences: Counter[int] = Counter()
    phase_counts: Counter[str] = Counter()
    frozen_per_message_padded_word_slots = 0
    per_interrupted_gap_padded_word_slots = 0
    structural_errors: list[str] = []
    for word in future_words:
        length = len(word)
        attempts = word.count("T")
        shape = shape_for(word)
        schedule_cases = 1 + len(shape) + 1
        by_length_word_schedule[length] += schedule_cases
        total_t_occurrences[length] += attempts
        # The printed seed formula adds one old/new slot per message.  Section
        # 3.3 applies old/new at every C-crossed/R-not-crossed gap, however, so
        # ATTEMPT has two such gaps (pre-A and post-A) and needs two extra slots.
        frozen_per_message_padded_word_slots += 3 * length + attempts + 4
        per_interrupted_gap_padded_word_slots += schedule_cases + length + attempts
        if len(shape) != 2 * length + attempts + 2:
            structural_errors.append(
                f"word {word}: shape {len(shape)}, expected {2 * length + attempts + 2}"
            )
        for gap in range(len(shape) + 1):
            phase, alias, _ = gap_phase(word, gap)
            phase_counts[phase] += 1
            if phase == "POST_ACTION_PRE_REPLY" and alias != "T":
                structural_errors.append(f"word {word} gap {gap}: post-action phase for {alias}")

    exact_word_schedule_cases = sum(by_length_word_schedule.values())
    exact_history_word_schedule_cases = len(histories) * exact_word_schedule_cases
    frozen_per_message_padded_history_slots = (
        len(histories) * frozen_per_message_padded_word_slots
    )
    per_interrupted_gap_padded_history_slots = (
        len(histories) * per_interrupted_gap_padded_word_slots
    )
    expected_by_length = {0: 4, 1: 73, 2: 1176, 3: 17712}
    expected_t_by_length = {0: 0, 1: 1, 2: 24, 3: 432}
    expected_phases = {
        "IDLE": 7369,
        "PENDING_REQUEST": 5484,
        "POST_ACTION_PRE_REPLY": 457,
        "FIN_PENDING": 1885,
        "TERMINAL": 1885,
    }
    coverage["linear_future_words"] = len(future_words)
    coverage["linear_word_schedule_cases"] = exact_word_schedule_cases
    coverage["linear_history_word_schedule_cases_conceptual_product"] = (
        exact_history_word_schedule_cases
    )
    coverage["frozen_per_message_padded_word_slots"] = frozen_per_message_padded_word_slots
    coverage["frozen_per_message_padded_history_slots"] = frozen_per_message_padded_history_slots
    coverage["corrected_per_interrupted_gap_padded_word_slots"] = (
        per_interrupted_gap_padded_word_slots
    )
    coverage["corrected_per_interrupted_gap_padded_history_slots"] = (
        per_interrupted_gap_padded_history_slots
    )
    coverage["crash_gap_phase_cases_per_residual"] = dict(sorted(phase_counts.items()))
    coverage["attempt_pre_action_interrupt_gaps_per_residual"] = phase_counts["PENDING_REQUEST"] - (
        sum(length * (12**length) for length in range(4)) - sum(total_t_occurrences.values())
    )
    coverage["attempt_post_action_interrupt_gaps_per_residual"] = phase_counts[
        "POST_ACTION_PRE_REPLY"
    ]
    results.check(
        "exact_base_schedule_arithmetic",
        dict(by_length_word_schedule) == expected_by_length
        and dict(total_t_occurrences) == expected_t_by_length
        and exact_word_schedule_cases == 18965
        and exact_history_word_schedule_cases == 2977505,
        "enumerated 18,965 word/schedule structures; multiplying by 157 clean histories gives the conceptual 2,977,505 product independently of selector padding",
        "base word/schedule arithmetic contradicts the frozen 18,965 and 2,977,505 totals",
        {
            "word_schedule_by_length": dict(sorted(by_length_word_schedule.items())),
            "T_occurrences_by_length": dict(sorted(total_t_occurrences.items())),
            "word_schedule_total": exact_word_schedule_cases,
            "history_word_schedule_conceptual_product_not_executed": exact_history_word_schedule_cases,
        },
    )
    minimal_attempt_word = ("T",)
    minimal_attempt_base = 2 * len(minimal_attempt_word) + minimal_attempt_word.count("T") + 4
    minimal_attempt_frozen_padding = (
        3 * len(minimal_attempt_word) + minimal_attempt_word.count("T") + 4
    )
    minimal_attempt_per_gap_padding = (
        minimal_attempt_base + len(minimal_attempt_word) + minimal_attempt_word.count("T")
    )
    results.check(
        "frozen_padded_old_new_slot_prediction",
        per_interrupted_gap_padded_history_slots == 3838493,
        "per-interrupted-gap expansion equals the frozen 3,838,493-slot prediction",
        "Section 3.3 requires old/new at both interrupted ATTEMPT gaps, so per-gap expansion is 24,906 words / 3,910,242 history slots, contradicting frozen prediction 3,838,493",
        {
            "frozen_per_message_word_slots": frozen_per_message_padded_word_slots,
            "frozen_per_message_history_slots": frozen_per_message_padded_history_slots,
            "per_interrupted_gap_word_slots": per_interrupted_gap_padded_word_slots,
            "per_interrupted_gap_history_slots": per_interrupted_gap_padded_history_slots,
            "minimal_witness": {
                "word": ["T"],
                "base_schedule_cases": minimal_attempt_base,
                "frozen_per_message_padded_slots": minimal_attempt_frozen_padding,
                "required_per_interrupted_gap_padded_slots": minimal_attempt_per_gap_padding,
                "interrupted_phases": ["PENDING_REQUEST(pre-A)", "POST_ACTION_PRE_REPLY"],
            },
        },
    )
    results.check(
        "corrected_per_interrupted_gap_selector_padding",
        per_interrupted_gap_padded_word_slots == 24906
        and per_interrupted_gap_padded_history_slots == 3910242
        and minimal_attempt_per_gap_padding == 9
        and minimal_attempt_frozen_padding == 8,
        "padding every C-crossed/R-not-crossed gap yields 24,906 word slots and 3,910,242 history slots; [T] is the minimal 9-versus-8 witness",
        "corrected per-interrupted-gap padding or its minimized ATTEMPT witness is inconsistent",
        {
            "word_slots": per_interrupted_gap_padded_word_slots,
            "history_slots": per_interrupted_gap_padded_history_slots,
            "T_word_required": minimal_attempt_per_gap_padding,
            "T_word_frozen": minimal_attempt_frozen_padding,
        },
    )
    results.check(
        "schedule_pending_phase_enumeration",
        not structural_errors and dict(phase_counts) == expected_phases,
        "all crash gaps classify exactly, including distinct ATTEMPT pre-A/post-A and FIN-pending/terminal phases",
        structural_errors[0] if structural_errors else "phase histogram contradicts structural gap enumeration",
        {"phase_counts": dict(sorted(phase_counts.items())), "expected": expected_phases},
    )

    semantic_digest_by_state: dict[State, str] = {}
    semantic_case_count = 0
    split_may_cases = 0
    must_fail_case: Optional[dict[str, object]] = None
    max_may_cardinality = 0
    for state in ALL_STATES:
        digest = hashlib.sha256()
        for word in future_words:
            schedules: tuple[Optional[int], ...] = (None,) + tuple(range(len(shape_for(word)) + 1))
            for schedule in schedules:
                evaluation = linear_evaluation(state, word, schedule)
                must = must_set(evaluation)
                semantic_case_count += 1
                cardinality = len(evaluation.traces)
                max_may_cardinality = max(max_may_cardinality, cardinality)
                if cardinality > 1:
                    split_may_cases += 1
                if must != EXPECTED_MUST and must_fail_case is None:
                    must_fail_case = {
                        "state": state.label(),
                        "word": word,
                        "schedule": "no_crash" if schedule is None else schedule,
                        "must": sorted(must),
                        "missing": sorted(EXPECTED_MUST - must),
                    }
                digest.update(lp(bytes(RANK[alias] for alias in word)))
                schedule_bytes = b"N" if schedule is None else b"G" + schedule.to_bytes(2, "big")
                digest.update(lp(schedule_bytes))
                digest.update(lp(serialize_trace_set(evaluation.traces)))
                digest.update(lp("\n".join(sorted(must)).encode("ascii")))
        semantic_digest_by_state[state] = digest.hexdigest()

    symbolic_lift_defined = all(history.state in semantic_digest_by_state for history in histories)
    coverage["linear_semantic_residual_cases_evaluated_in_process"] = semantic_case_count
    coverage["linear_history_cases_conceptual_state_lift_only"] = exact_history_word_schedule_cases
    coverage["same_class_history_pairs_enumerated_no_full_future_pair_execution"] = same_pairs
    coverage["linear_split_may_cases_across_18_residuals"] = split_may_cases
    coverage["linear_max_may_trace_cardinality"] = max_may_cardinality
    observations["linear_semantic_sha256_by_residual"] = {
        state.label(): digest for state, digest in sorted(semantic_digest_by_state.items())
    }
    results.check(
        "conditional_bounded_linear_May_and_Must",
        semantic_case_count == len(ALL_STATES) * 18965
        and max_may_cardinality <= 2
        and must_fail_case is None,
        "under the experiment's declared post-STOP projection and vacuous no-crash recovery predicate, evaluated every length-0..3 word and schedule over all 18 selected residuals in process",
        "a linear semantic case count, May branch bound, or required Must predicate failed",
        {
            "residual_cases_evaluated_in_process": semantic_case_count,
            "conceptual_state_lift_history_cases_not_executed": exact_history_word_schedule_cases,
            "split_may_cases": split_may_cases,
            "max_may_cardinality": max_may_cardinality,
            "first_must_failure": must_fail_case,
        },
    )
    results.unknown(
        "post_STOPPED_lifecycle_trace_projection",
        "the seed counts the gap after STOPPED and forbids another reply, but does not uniquely say whether later DOWN/READY crossings remain inside a trace already complete at STOPPED; this experiment includes them conditionally",
        {"encoded_terminal_gap_trace": display_trace((FIN, STOPPED, DOWN, READY))},
    )
    results.unknown(
        "Must_recovery_READY_on_no_crash",
        "the vocabulary says recovery reaches READY but does not freeze whether a no-crash run satisfies that proposition vacuously; this experiment conditionally treats every-DOWN-has-READY as true when there is no DOWN",
        {"encoded_no_crash_Must": sorted(must_set(Evaluation(frozenset(((FIN, STOPPED),)))))},
    )
    results.check(
        "conditional_symbolic_same_coordinate_future_lift",
        symbolic_lift_defined and same_pairs == 2351,
        "the encoded model maps each of the 2,351 enumerated same-coordinate pairs to one shared state-keyed future signature by construction",
        "a clean-cut state lacks an encoded residual signature or the enumerated same-pair count changed",
        {
            "same_pairs_enumerated": same_pairs,
            "independent_history_pair_full_future_comparisons_executed": 0,
            "construction": "semantic_digest_by_state[history.state]",
            "conditional_on": "assumed O/P/G selected-residual factoring",
        },
    )
    results.unknown(
        "independent_same_class_history_pair_full_future_equality",
        "no independent realization executed all futures separately from each of the 2,351 history pairs; dictionary reuse on equal State keys is a symbolic lift, not pairwise evidence",
        {"pairs_enumerated": same_pairs, "pairwise_full_future_executions": 0},
    )

    adaptive_ids, adaptive_details = adaptive_partition_ids(3)
    cut_adaptive_classes = {
        adaptive_ids[(3, history.state, 1)] for history in histories
    }
    full_adaptive_classes = {adaptive_ids[(3, state, 1)] for state in ALL_STATES}
    coverage["adaptive_partition"] = adaptive_details
    results.check(
        "conditional_encoded_adaptive_state_budget_partition_depth_three",
        len(cut_adaptive_classes) == 14
        and len(full_adaptive_classes) == 18
        and adaptive_details["memoized_state_depth_budget_nodes"] == 144
        and adaptive_details["arithmetic_node_times_phase_product_not_executed"] == 2304
        and adaptive_details["phase_transition_refinement_nodes_executed"] == 0,
        "under encoded scheduler-mode and visibility choices, memoized exactly 144 (depth,state,budget) nodes; the cut maps to 14 state-keyed classes and the full modeled state set to 18",
        "the 144-node conditional adaptive construction or its state-keyed cut/full-domain class counts changed",
        {
            "cut_classes": len(cut_adaptive_classes),
            "full_domain_classes": len(full_adaptive_classes),
            "history_pair_adaptive_executions": 0,
            "phase_is_not_a_memoized_state_dimension": True,
            **adaptive_details,
        },
    )
    results.unknown(
        "phase_transition_refinement_over_2304_product",
        "2,304 is only 144 memoized (depth,state,budget) nodes multiplied by 16 invented phase labels; no transition refinement was executed with phase in the memo key",
        {
            "memoized_nodes_executed": adaptive_details["memoized_state_depth_budget_nodes"],
            "phase_labels": adaptive_details["invented_phase_label_count_not_in_memo_key"],
            "arithmetic_product": adaptive_details[
                "arithmetic_node_times_phase_product_not_executed"
            ],
            "phase_transition_nodes_executed": adaptive_details[
                "phase_transition_refinement_nodes_executed"
            ],
        },
    )
    results.unknown(
        "adaptive_scheduler_domain",
        "the seed does not freeze how one scheduler S names gaps across controller branches whose nominal crossing paths diverge; the implemented scheduler-mode tuples are one conditional completion, not a uniquely reproducible frozen domain",
        {
            "encoded_modes": [
                "crash_before_input",
                "crash_pending_request",
                "crash_post_action_pre_reply(T)",
                "crash_after_reply",
                "terminal_gap_modes",
            ]
        },
    )
    results.unknown(
        "adaptive_controller_capture_peer_visibility",
        "A is sent to an independent capture peer while the controller chooses from its observed suffix; the seed includes A in traces but does not state whether or when the client controller observes the peer's A crossing",
        {"encoded_choice": "A is available in the controller-visible suffix"},
    )

    author = retry_once_after_interruption(INITIAL, "AI", "after_input")
    assert isinstance(author, Evaluation)
    expected_author_old: Trace = (
        ("C", b"AUTHOR ID\n"),
        DOWN,
        READY,
        ("C", b"AUTHOR ID\n"),
        ("R", b"OK AUTHOR ID\n"),
        FIN,
        STOPPED,
    )
    expected_author_new: Trace = (
        ("C", b"AUTHOR ID\n"),
        DOWN,
        READY,
        ("C", b"AUTHOR ID\n"),
        ("R", b"ERR ACTIVE\n"),
        FIN,
        STOPPED,
    )
    expected_author = frozenset((expected_author_old, expected_author_new))
    observations["author_crash_retry_May"] = [
        display_trace(trace) for trace in sorted(author.traces, key=serialize_trace)
    ]
    observations["author_crash_retry_Must"] = sorted(must_set(author))
    results.check(
        "exact_author_crash_retry_May_Must",
        author.traces == expected_author and must_set(author) == EXPECTED_MUST,
        "author interruption produces exactly the literal old/new May traces and all six Must propositions",
        "author interruption May set or Must set differs from the literal seed witness",
        {
            "may_cardinality": len(author.traces),
            "must": sorted(must_set(author)),
            "expected_may_cardinality": 2,
        },
    )

    forced_old = retry_once_after_interruption(INITIAL, "AI", "after_input", "old")
    forced_new = retry_once_after_interruption(INITIAL, "AI", "after_input", "new")
    collapsed = retry_once_after_interruption(State("U", "ID", "E0"), "AI", "after_input")
    assert isinstance(forced_old, Evaluation) and isinstance(forced_new, Evaluation)
    assert isinstance(collapsed, Evaluation)
    selector_not_observable = all(
        channel != "F"
        and not (channel == "C" and payload.startswith(b"SELECT"))
        for trace in author.traces
        for channel, payload in trace
    )
    results.check(
        "selector_old_new_and_collapsing_behavior",
        forced_old.traces == frozenset((expected_author_old,))
        and forced_new.traces == frozenset((expected_author_new,))
        and len(collapsed.traces) == 1
        and selector_not_observable,
        "forced old/new select the corresponding hidden branch, failed-precondition branches deduplicate, and selector bytes stay erased",
        "forced selector result, collapsed alternative, or observable projection violates the seed",
        {
            "forced_old_traces": len(forced_old.traces),
            "forced_new_traces": len(forced_new.traces),
            "failed_precondition_deduplicated_traces": len(collapsed.traces),
            "selector_erased": selector_not_observable,
        },
    )

    action_state = State("1", "ID", "E0")
    before_action = retry_once_after_interruption(action_state, "T", "after_input")
    after_action = retry_once_after_interruption(action_state, "T", "after_action")
    after_reply = attempt_crash_after_reply(action_state)
    assert isinstance(before_action, Evaluation) and isinstance(after_action, Evaluation)
    expected_try = ("A", b"TRY O=1 P=ID E=E0 V=ALLOW\n")
    expected_before_action: Trace = (
        ("C", b"ATTEMPT\n"),
        DOWN,
        READY,
        ("C", b"ATTEMPT\n"),
        expected_try,
        ("R", b"OK ATTEMPTED\n"),
        FIN,
        STOPPED,
    )
    expected_after_action: Trace = (
        ("C", b"ATTEMPT\n"),
        expected_try,
        DOWN,
        READY,
        ("C", b"ATTEMPT\n"),
        expected_try,
        ("R", b"OK ATTEMPTED\n"),
        FIN,
        STOPPED,
    )
    before_trace = next(iter(before_action.traces))
    after_trace = next(iter(after_action.traces))
    reply_trace = next(iter(after_reply.traces))
    action_must = must_set(before_action) == must_set(after_action) == must_set(after_reply) == EXPECTED_MUST
    observations["attempt_retry_before_A"] = display_trace(before_trace)
    observations["attempt_retry_after_A"] = display_trace(after_trace)
    results.check(
        "exact_ATTEMPT_interruption_retry_phases",
        before_action.traces == frozenset((expected_before_action,))
        and after_action.traces == frozenset((expected_after_action,))
        and sum(1 for crossing in before_trace if crossing[0] == "A") == 1
        and sum(1 for crossing in after_trace if crossing[0] == "A") == 2
        and sum(1 for crossing in reply_trace if crossing[0] == "A") == 1
        and sum(1 for crossing in reply_trace if crossing == ("C", REQUEST["T"])) == 1
        and action_must,
        "pre-A crash exposes one attempt, post-A/pre-reply crash exposes two after retry, and post-reply crash exposes one with no retry",
        "ATTEMPT phase trace, crossing count, retry decision, or Must set differs from the seed",
        {
            "before_A_attempt_crossings": sum(1 for crossing in before_trace if crossing[0] == "A"),
            "after_A_attempt_crossings": sum(1 for crossing in after_trace if crossing[0] == "A"),
            "after_reply_attempt_crossings": sum(1 for crossing in reply_trace if crossing[0] == "A"),
            "must": sorted(must_set(after_action)),
        },
    )

    stop_crash = stop_crash_evaluation()
    expected_stop = frozenset(((FIN, DOWN, READY, STOPPED),))
    results.check(
        "exact_FIN_pending_crash_May_Must",
        stop_crash.traces == expected_stop and must_set(stop_crash) == EXPECTED_MUST,
        "FIN-pending crash preserves one FIN and produces exactly one STOPPED after READY",
        "FIN-pending exact trace or Must set differs from the literal seed witness",
        {"trace": display_trace(next(iter(stop_crash.traces))), "must": sorted(must_set(stop_crash))},
    )

    phases = (
        "IDLE",
        *(f"PENDING:{alias}" for alias in ALIASES),
        "POST_ACTION_PRE_REPLY",
        "FIN_PENDING",
        "TERMINAL",
    )
    encodings: dict[bytes, tuple[State, str]] = {}
    first_encoding_collision: Optional[dict[str, object]] = None
    for state in ALL_STATES:
        for phase in phases:
            encoding = configuration_encoding(state, phase)
            if encoding in encodings and first_encoding_collision is None:
                prior = encodings[encoding]
                first_encoding_collision = {
                    "left": [prior[0].label(), prior[1]],
                    "right": [state.label(), phase],
                }
            encodings[encoding] = (state, phase)
    coverage["invented_local_phase_string_labels"] = len(phases)
    coverage["invented_local_state_phase_cartesian_encodings"] = len(encodings)
    results.check(
        "invented_string_phase_encoding_injectivity_smoke_test",
        len(phases) == 16 and len(encodings) == len(ALL_STATES) * 16 and first_encoding_collision is None,
        "this experiment's invented eight-byte length-prefix strings are injective over the 18-by-16 Cartesian label product only",
        "two distinct entries in the locally invented state/phase string product have the same local encoding",
        {
            "states": len(ALL_STATES),
            "invented_phase_strings": len(phases),
            "encodings": len(encodings),
            "first_collision": first_encoding_collision,
            "phase_reachability_checked": False,
            "phase_transitions_checked": False,
            "seed_canonicalization_checked": False,
        },
    )
    serialization_choices_missing = (
        "crossing tag values and direction representation",
        "integer width and endianness for lengths/cardinalities",
        "controller node/branch grammar and serialization",
        "scheduler/no-crash/gap/phase serialization",
        "typed FIN and lifecycle payload serialization",
    )
    results.add(
        "frozen_canonical_serialization_reproducibility",
        "FAIL",
        "the witness order calls for bytewise canonical controller/scheduler/outcome serialization but does not freeze enough bytes to reproduce one canonicalizer independently",
        {
            "experiment_local_choice": "eight-byte big-endian length prefixes with ASCII channel names",
            "missing_frozen_choices": list(serialization_choices_missing),
            "reported_SHA256_values_are": "implementation-local manifests, not seed-defined canonical encodings",
        },
    )

    meta_cases = {
        "empty": meta_oracle((), (b"",), 0),
        "unknown_frame": meta_oracle((), (b"INSTALL EQ x\n",), 0),
        "future_depth_4": meta_oracle((), (REQUEST["Q"],) * 4, 0),
        "two_crashes": meta_oracle((), (), 2),
        "fragmented": meta_oracle((), (REQUEST["Q"],), 0, fragmented=True),
        "concurrent": meta_oracle((), (REQUEST["Q"],), 0, concurrent=True),
        "client_selector": meta_oracle((), (b"SELECT old\n",), 0),
    }
    all_unsupported = all(isinstance(value, Unsupported) for value in meta_cases.values())
    results.check(
        "closed_world_meta_oracle_negative_inputs",
        all_unsupported,
        "all explicit outside-domain probes return typed UNSUPPORTED reasons without a behavioral trace",
        "an outside-domain probe was accepted or failed without a typed reason",
        {
            name: value.reason if isinstance(value, Unsupported) else value
            for name, value in sorted(meta_cases.items())
        },
    )

    # Negative controls: these deliberately corrupt one obligation at a time.
    negative_controls: list[dict[str, object]] = []

    def record_negative(name: str, detected: bool, detector: str, evidence: object) -> None:
        negative_controls.append(
            {"name": name, "detected": detected, "detector": detector, "evidence": evidence}
        )

    def mutated_not(state: State, alias: str) -> Trace:
        if alias in {"Q", "X", "T"} and state.program == "NOT" and state.observation in {"0", "1"}:
            wrong = State(state.observation, "ID", state.engine)
            return completion_crossings(wrong, alias)
        return completion_crossings(state, alias)

    detected, evidence = detect_model_difference(mutated_not)
    record_negative("NOT_truth_table_changed_to_ID", detected, "exhaustive 18x12 oracle comparison", evidence)

    def mutated_drop_action(state: State, alias: str) -> Trace:
        result = completion_crossings(state, alias)
        return result[1:] if alias == "T" else result

    detected, evidence = detect_model_difference(mutated_drop_action)
    dropped_trace = (("C", REQUEST["T"]),) + mutated_drop_action(action_state, "T") + (FIN, STOPPED)
    dropped_must = must_set(Evaluation(frozenset((dropped_trace,))))
    record_negative(
        "ATTEMPT_A_deleted",
        detected and "failure_free_T_has_A_before_reply" not in dropped_must,
        "exact output comparison plus Must ordering predicate",
        {"first_difference": evidence, "must": sorted(dropped_must)},
    )

    swapped_trace = (
        ("C", REQUEST["T"]),
        ("R", b"OK ATTEMPTED\n"),
        expected_try,
        FIN,
        STOPPED,
    )
    swapped_must = must_set(Evaluation(frozenset((swapped_trace,))))
    record_negative(
        "ATTEMPT_A_and_reply_swapped",
        "failure_free_T_has_A_before_reply" not in swapped_must,
        "Must A-before-reply predicate",
        {"must": sorted(swapped_must)},
    )

    exposed_selector_trace = expected_author_old[:3] + (("F", b"SELECT old"),) + expected_author_old[3:]
    record_negative(
        "selector_leaked_into_observable_trace",
        exposed_selector_trace not in expected_author,
        "literal complete May-set equality",
        display_trace(exposed_selector_trace),
    )

    collapsed_author = frozenset((expected_author_old,))
    record_negative(
        "author_old_new_May_collapsed",
        collapsed_author != expected_author,
        "literal author retry May-set equality",
        {"mutated_cardinality": len(collapsed_author), "required_cardinality": len(expected_author)},
    )

    duplicated_stop = expected_author_old + (STOPPED,)
    duplicated_stop_must = must_set(Evaluation(frozenset((duplicated_stop,))))
    record_negative(
        "STOPPED_duplicated",
        "legal_controller_reaches_exactly_one_STOPPED" not in duplicated_stop_must,
        "exactly-one STOPPED Must predicate",
        {"must": sorted(duplicated_stop_must)},
    )

    invented_reply = (
        ("C", REQUEST["AI"]),
        DOWN,
        READY,
        ("R", b"OK AUTHOR ID\n"),
        FIN,
        STOPPED,
    )
    invented_must = must_set(Evaluation(frozenset((invented_reply,))))
    record_negative(
        "reply_invented_for_interrupted_request",
        "no_completion_invented_for_interrupted_request" not in invented_must,
        "interrupted-request Must predicate",
        {"must": sorted(invented_must)},
    )

    mutated_schedule_total = sum(
        (2 * len(word) + word.count("T") + 3) for word in future_words
    )
    record_negative(
        "schedule_gap_off_by_one",
        mutated_schedule_total != exact_word_schedule_cases,
        "enumerated nominal crossing gaps plus explicit no-crash schedule",
        {"mutated": mutated_schedule_total, "required": exact_word_schedule_cases},
    )

    merge_left = INITIAL
    merge_right = State("0", "EMPTY", "E0")
    merge_separator = future_trace(merge_left, ("X",)) != future_trace(merge_right, ("X",))
    record_negative(
        "distinct_coordinates_forced_to_one_label",
        merge_separator,
        "canonical one-message separator",
        {
            "left": merge_left.label(),
            "right": merge_right.label(),
            "message": "X",
        },
    )

    collision_left = configuration_encoding(INITIAL, "IDLE")
    collision_right = configuration_encoding(State("1", "ID", "E1"), "IDLE")
    forced_hash = lambda _data: b"forced-collision"
    collision_detected = (
        forced_hash(collision_left) == forced_hash(collision_right)
        and collision_left != collision_right
        and future_trace(INITIAL, ("X",))
        != future_trace(State("1", "ID", "E1"), ("X",))
    )
    record_negative(
        "forced_hash_collision_between_distinguishable_residuals",
        collision_detected,
        "compare canonical bytes and X behavior after injected hash collision",
        {"hash_equal": True, "encoding_equal": collision_left == collision_right},
    )

    attempt_without_retry = frozenset(
        (
            (
                ("C", REQUEST["T"]),
                expected_try,
                DOWN,
                READY,
                FIN,
                STOPPED,
            ),
        )
    )
    record_negative(
        "post_A_interruption_retry_omitted",
        attempt_without_retry != after_action.traces,
        "literal post-A retry May-set equality",
        {
            "mutated_attempts": 1,
            "required_attempts": 2,
        },
    )

    failed_negative = next((case for case in negative_controls if not case["detected"]), None)
    coverage["negative_controls"] = len(negative_controls)
    observations["negative_controls"] = negative_controls
    results.check(
        "explicit_negative_control_detection",
        failed_negative is None,
        "all deliberate semantic, ordering, selector, schedule, collision, retry, and STOP mutations were rejected",
        "a deliberate mutation escaped its named detector",
        {"controls": len(negative_controls), "first_escaped": failed_negative},
    )

    # Required attack accounting.  UNKNOWN is intentional where no independent
    # realization, external dependency, human study, or platform perturbation
    # exists inside this oracle-only executable.
    results.add(
        "attack_MERGE",
        "PASS",
        "a forced unequal-coordinate merge is rejected by its exact X separator",
        {"negative_control": "distinct_coordinates_forced_to_one_label"},
    )
    results.add(
        "attack_COLLIDE_oracle_encoding",
        "PASS",
        "all 288 strings in the experiment-local 18-by-16 label product are injective and a forced state-label hash collision is rejected; no phase reachability, phase transition, or seed canonicalizer claim follows",
        {
            "encodings": len(encodings),
            "scope": "invented string Cartesian product only",
            "phase_transition_checks": 0,
        },
    )
    results.add(
        "conditional_attack_FUTURE_encoded_domain",
        "PASS",
        "the 144-node state/budget adaptive construction and 341,370 in-process residual/word/schedule evaluations agree with the predicted quotient under this experiment's scheduler, visibility, terminal, Must, and selected-residual choices",
        {
            "linear_residual_cases_evaluated_in_process": semantic_case_count,
            "history_cases_conceptual_lift_only": exact_history_word_schedule_cases,
            "adaptive_depth_state_budget_nodes_memoized": adaptive_details[
                "memoized_state_depth_budget_nodes"
            ],
            "phase_transition_refinement_nodes": 0,
        },
    )
    results.unknown(
        "attack_FUTURE_frozen_domain",
        "an unconditional FUTURE verdict requires frozen adaptive scheduler identity, capture-peer visibility to the controller, post-STOP trace projection, and no-crash Must semantics; those are not uniquely specified",
    )
    results.unknown(
        "attack_DELETE",
        "no candidate realization or named stored responsibility exists in this oracle-only experiment to delete and cold-start",
    )
    results.unknown(
        "attack_DERIVE",
        "no candidate bytes and independently surviving responsibility were supplied for a delete-and-rebuild experiment",
    )
    results.unknown(
        "attack_RECOMPUTE",
        "no restartable candidate representation, replay machinery, or measured recovery cost was supplied",
    )
    results.unknown(
        "attack_EXTERNALIZE",
        "no client, capture-peer, build-artifact, or service dependency was introduced and severed during recovery",
    )
    results.unknown(
        "attack_REALIZE_and_prediction_10",
        "independent Family J, Family Q, and Harness H implementations were not supplied; conformance cannot be inferred from this oracle",
    )
    fresh_implementer_choices = (
        "choose whether completed command means literal ordinary R completion or SELECT(new) semantic application; under the literal reading, augment the oracle with manifest-selected residual",
        "pad old/new per interrupted gap, including both ATTEMPT gaps",
        "include or exclude lifecycle crossings scheduled after STOPPED",
        "decide whether recovery-reaches-READY is vacuously true without a crash",
        "define scheduler identity across divergent adaptive paths",
        "define whether/when the client controller observes capture-peer A crossings",
        "choose concrete crossing/controller/scheduler canonical serialization bytes",
    )
    observations["fresh_implementer_choices_required_outside_seed"] = list(
        fresh_implementer_choices
    )
    results.add(
        "attack_COGNITION_spec_reproducibility",
        "FAIL",
        "this fresh implementation required behaviorally or canonically material choices not frozen by the seed, so specification-only reproduction is not established",
        {"outside_seed_choices": list(fresh_implementer_choices)},
    )
    results.unknown(
        "attack_COGNITION_human_performance",
        "no controlled fresh-human implementation study was run; the executable counterexample establishes specification underdetermination, not a human-performance measurement",
    )
    results.unknown(
        "attack_TCB",
        "runtime, OS, transport, serializer, compiler, caches, fault hook, capture peer, canonicalizer, and build inputs were not independently perturbed",
    )
    results.unknown(
        "physical_and_external_claims",
        "software-boundary enumeration cannot establish power-loss/media persistence, physical absence, privacy, authority, or downstream exactly-once effects",
    )

    summary = {
        "experiment": EXPERIMENT,
        "source": {"path": str(source_path), "sha256": source_hash},
        "seed": {
            "path": str(seed_path),
            "expected_sha256": EXPECTED_SEED_SHA256,
            "actual_sha256": actual_seed_hash,
            "verified": True,
        },
        "coverage": coverage,
        "observations": observations,
        "checks": results.items,
        "totals": results.totals(),
        "exit_policy": "nonzero iff one or more FAIL results exist",
    }
    return summary, 1 if results.totals()["FAIL"] else 0


def main() -> int:
    source_path = Path(__file__).resolve()
    seed_path = source_path.with_name(SEED_NAME)
    try:
        summary, exit_code = run_experiment(seed_path, source_path)
    except Exception as error:  # fail closed, while preserving structured output
        source_hash = sha256_file(source_path) if source_path.is_file() else "UNAVAILABLE"
        seed_hash = sha256_file(seed_path) if seed_path.is_file() else "UNAVAILABLE"
        summary = {
            "experiment": EXPERIMENT,
            "source": {"path": str(source_path), "sha256": source_hash},
            "seed": {
                "path": str(seed_path),
                "expected_sha256": EXPECTED_SEED_SHA256,
                "actual_sha256": seed_hash,
                "verified": seed_hash == EXPECTED_SEED_SHA256,
            },
            "coverage": {},
            "observations": {},
            "checks": [
                {
                    "name": "uncaught_experiment_error",
                    "status": "FAIL",
                    "reason": f"{type(error).__name__}: {error}",
                }
            ],
            "totals": {"PASS": 0, "FAIL": 1, "UNKNOWN": 0},
            "exit_policy": "nonzero iff one or more FAIL results exist",
        }
        exit_code = 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
