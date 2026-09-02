#!/usr/bin/env python3
"""Executable, fail-closed falsifier for HISTORY-SEED-R01I.md.

The seed is the only input authority.  This program deliberately reports a
literal Section 7.3 quotient separately from the relaxed suffix-only quotient
used by the numerical predictions in Section 9.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from typing import Iterable, Iterator, Optional, Sequence


SEED_PATH = "/root/pareto/zero-ground-restart/HISTORY-SEED-R01I.md"
EXPECTED_SEED_SHA256 = "d52c083c34aa37144fa47ee8a02d9279adb75029613125f38dad5a98b0df8d9c"
SCHEMA = "FBH-R01I-FALSIFIER-1"


# Crossing tags from Section 10.1.
C_FRAME = 1
C_FIN = 2
R_FRAME = 3
R_STOPPED = 4
A_FRAME = 5
L_DOWN = 6
L_READY = 7
F_FRAME = 8

Crossing = tuple[int, bytes]
Trace = tuple[Crossing, ...]
Residual = tuple[int, int, int]

O_NAMES = ("U", "0", "1")
P_NAMES = ("EMPTY", "ID", "NOT")
G_NAMES = ("E0", "E1")

ALIASES = ("O0", "O1", "AI", "AN", "RI", "RN", "D", "Q", "X", "T", "E", "K")
RANK = {name: i for i, name in enumerate(ALIASES)}
REQUEST_TEXT = (
    "OBSERVE 0",
    "OBSERVE 1",
    "AUTHOR ID",
    "AUTHOR NOT",
    "REPLACE ID",
    "REPLACE NOT",
    "RETIRE",
    "QUERY",
    "EXPLAIN",
    "ATTEMPT",
    "EVOLVE",
    "CURRENT",
)
REQUEST_BYTES = {a: (s + "\n").encode("ascii") for a, s in zip(ALIASES, REQUEST_TEXT)}

VIEWER_CODES = {"CLIENT": 0, "CAPTURE": 1, "PUBLIC": 2, "SELECTOR": 3}
VIEWER_TAGS = {
    "CLIENT": frozenset((C_FRAME, C_FIN, R_FRAME, R_STOPPED, L_DOWN, L_READY)),
    "CAPTURE": frozenset((A_FRAME,)),
    "PUBLIC": frozenset((C_FRAME, C_FIN, R_FRAME, R_STOPPED, A_FRAME, L_DOWN, L_READY)),
    "SELECTOR": frozenset((F_FRAME,)),
}

CUT = b"CUT REMAINING=3\n"
SELECT_OLD = b"SELECT old\n"
SELECT_NEW = b"SELECT new\n"
RESUME_FIN = b"RESUME FIN_PENDING\n"
RESUME_TERMINAL = b"RESUME TERMINAL\n"

BRANCH_CODE = {"NONE": 0, "OLD": 1, "NEW": 2}
ALL_MUST = (1 << 10) - 1
RECOVERY_MUST_AUDITS = 0
RECOVERY_MUST_FAILURES: list[dict] = []

KIND_CODE = {
    "CLEAN": 0,
    "IDLE_RECOVERY": 1,
    "PENDING_NON_T": 2,
    "T_PRE_A": 3,
    "T_POST_A": 4,
    "FIN_PENDING": 5,
    "TERMINAL": 6,
}
ACTIVE_KINDS = frozenset(("IDLE_RECOVERY", "PENDING_NON_T", "T_PRE_A", "T_POST_A"))
DEAD_KINDS = frozenset(("FIN_PENDING", "TERMINAL"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u8(n: int) -> bytes:
    if not 0 <= n <= 0xFF:
        raise ValueError("U8 range")
    return bytes((n,))


def u16(n: int) -> bytes:
    if not 0 <= n <= 0xFFFF:
        raise ValueError("U16 range")
    return n.to_bytes(2, "big")


def u64(n: int) -> bytes:
    if not 0 <= n <= 0xFFFFFFFFFFFFFFFF:
        raise ValueError("U64 range")
    return n.to_bytes(8, "big")


def enc_bytes(value: bytes) -> bytes:
    return u64(len(value)) + value


def enc_list(encoded_items: Iterable[bytes]) -> bytes:
    items = tuple(encoded_items)
    return u64(len(items)) + b"".join(enc_bytes(item) for item in items)


class DecodeError(ValueError):
    pass


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def take(self, n: int) -> bytes:
        if n < 0 or self.offset + n > len(self.data):
            raise DecodeError("truncated")
        out = self.data[self.offset : self.offset + n]
        self.offset += n
        return out

    def one(self) -> int:
        return self.take(1)[0]

    def uint16(self) -> int:
        return int.from_bytes(self.take(2), "big")

    def uint64(self) -> int:
        return int.from_bytes(self.take(8), "big")

    def byte_string(self) -> bytes:
        return self.take(self.uint64())

    def finish(self) -> None:
        if self.offset != len(self.data):
            raise DecodeError("trailing bytes")


def enc_crossing(crossing: Crossing) -> bytes:
    tag, payload = crossing
    if tag not in range(1, 9):
        raise ValueError("crossing tag")
    if tag in (C_FIN, R_STOPPED, L_DOWN, L_READY) and payload:
        raise ValueError("typed crossing payload")
    if tag in (C_FRAME, R_FRAME, A_FRAME, F_FRAME) and not payload:
        raise ValueError("empty framed crossing")
    return u8(tag) + enc_bytes(payload)


def dec_crossing(data: bytes) -> Crossing:
    reader = Reader(data)
    tag = reader.one()
    payload = reader.byte_string()
    reader.finish()
    crossing = (tag, payload)
    if enc_crossing(crossing) != data:
        raise DecodeError("noncanonical crossing")
    return crossing


def enc_trace(trace: Sequence[Crossing]) -> bytes:
    return enc_list(enc_crossing(c) for c in trace)


def dec_trace(data: bytes) -> Trace:
    reader = Reader(data)
    count = reader.uint64()
    items = tuple(dec_crossing(reader.byte_string()) for _ in range(count))
    reader.finish()
    if enc_trace(items) != data:
        raise DecodeError("noncanonical trace")
    return items


def enc_residual(residual: Residual) -> bytes:
    o, p, g = residual
    if not (0 <= o <= 2 and 0 <= p <= 2 and 0 <= g <= 1):
        raise ValueError("residual code")
    return bytes((o, p, g))


def dec_residual(data: bytes) -> Residual:
    if len(data) != 3:
        raise DecodeError("residual length")
    residual = (data[0], data[1], data[2])
    if enc_residual(residual) != data:
        raise DecodeError("residual code")
    return residual


def enc_trace_set(traces: Iterable[Sequence[Crossing]]) -> bytes:
    encoded = sorted(set(enc_trace(t) for t in traces))
    return enc_list(encoded)


def dec_trace_set(data: bytes) -> tuple[Trace, ...]:
    reader = Reader(data)
    count = reader.uint64()
    raw = tuple(reader.byte_string() for _ in range(count))
    reader.finish()
    if tuple(sorted(set(raw))) != raw:
        raise DecodeError("trace set is not sorted and unique")
    traces = tuple(dec_trace(item) for item in raw)
    if enc_trace_set(traces) != data:
        raise DecodeError("noncanonical trace set")
    return traces


def project(trace: Sequence[Crossing], viewer: str) -> Trace:
    if viewer not in VIEWER_TAGS:
        raise ValueError("UNSUPPORTED(VIEWER)")
    tags = VIEWER_TAGS[viewer]
    return tuple(c for c in trace if c[0] in tags)


def residual_text(residual: Residual) -> str:
    return f"O={O_NAMES[residual[0]]} P={P_NAMES[residual[1]]} E={G_NAMES[residual[2]]}"


def value_of(residual: Residual) -> str:
    o, p, _g = residual
    if p == 0:
        return "NONE"
    if o == 0:
        return "UNKNOWN"
    allow = (p == 1 and o == 2) or (p == 2 and o == 1)
    return "ALLOW" if allow else "DENY"


def delta(residual: Residual, alias: str) -> Residual:
    o, p, g = residual
    if alias == "O0":
        o = 1
    elif alias == "O1":
        o = 2
    elif alias == "AI" and p == 0:
        p = 1
    elif alias == "AN" and p == 0:
        p = 2
    elif alias == "RI" and p != 0:
        p = 1
    elif alias == "RN" and p != 0:
        p = 2
    elif alias == "D" and p != 0:
        p = 0
    elif alias == "E" and g == 0:
        g = 1
    elif alias not in ALIASES:
        raise ValueError("UNSUPPORTED(REQUEST)")
    return (o, p, g)


def reply_bytes(residual: Residual, alias: str) -> bytes:
    _o, p, g = residual
    if alias == "O0":
        text = "OK OBSERVE 0"
    elif alias == "O1":
        text = "OK OBSERVE 1"
    elif alias == "AI":
        text = "OK AUTHOR ID" if p == 0 else "ERR ACTIVE"
    elif alias == "AN":
        text = "OK AUTHOR NOT" if p == 0 else "ERR ACTIVE"
    elif alias == "RI":
        text = "OK REPLACE ID" if p != 0 else "ERR EMPTY"
    elif alias == "RN":
        text = "OK REPLACE NOT" if p != 0 else "ERR EMPTY"
    elif alias == "D":
        text = "OK RETIRE" if p != 0 else "ERR EMPTY"
    elif alias == "Q":
        text = f"VALUE {value_of(residual)}"
    elif alias == "X":
        text = f"WHY {residual_text(residual)} V={value_of(residual)}"
    elif alias == "T":
        text = "OK ATTEMPTED"
    elif alias == "E":
        text = "OK ENGINE E1" if g == 0 else "OK ENGINE E1 ALREADY"
    elif alias == "K":
        text = f"ENGINE {G_NAMES[g]}"
    else:
        raise ValueError("UNSUPPORTED(REQUEST)")
    return (text + "\n").encode("ascii")


def attempt_bytes(residual: Residual) -> bytes:
    return f"TRY {residual_text(residual)} V={value_of(residual)}\n".encode("ascii")


def f_crash(gap: int) -> bytes:
    if gap < 0:
        raise ValueError("negative gap")
    return f"CRASH GAP={gap}\n".encode("ascii")


def f_resume(residual: Residual) -> bytes:
    return f"RESUME ACTIVE {residual_text(residual)}\n".encode("ascii")


def f_allowance(d: int) -> bytes:
    if not 0 <= d <= 3:
        raise ValueError("allowance")
    return f"ALLOWANCE {d}\n".encode("ascii")


def append_completed(trace: list[Crossing], residual: Residual, alias: str) -> Residual:
    trace.append((C_FRAME, REQUEST_BYTES[alias]))
    if alias == "T":
        trace.append((A_FRAME, attempt_bytes(residual)))
    trace.append((R_FRAME, reply_bytes(residual, alias)))
    return delta(residual, alias)


def execute_word(residual: Residual, word: Sequence[str]) -> tuple[Trace, Residual]:
    trace: list[Crossing] = []
    current = residual
    for alias in word:
        current = append_completed(trace, current, alias)
    return tuple(trace), current


def words_exact(n: int) -> Iterator[tuple[str, ...]]:
    yield from itertools.product(ALIASES, repeat=n)


def words_through(n: int) -> Iterator[tuple[str, ...]]:
    for length in range(n + 1):
        yield from words_exact(length)


def clean_history(word: Sequence[str]) -> tuple[Trace, Residual]:
    trace, residual = execute_word((0, 0, 0), word)
    return trace + ((F_FRAME, CUT),), residual


def complete_after_active(prefix: Sequence[Crossing], residual: Residual, word: Sequence[str]) -> tuple[Trace, Residual]:
    trace = list(prefix)
    current = residual
    for alias in word:
        current = append_completed(trace, current, alias)
    trace.extend(((C_FIN, b""), (R_STOPPED, b"")))
    return tuple(trace), current


@dataclass(frozen=True, order=True)
class Condition:
    kind: str
    d: int
    residual: Optional[Residual]
    alias: Optional[str] = None

    @property
    def live_d(self) -> Optional[int]:
        return self.d if self.kind in ACTIVE_KINDS else None

    def semantic_key(self) -> tuple:
        return (self.kind, self.d, self.residual, self.alias)


@dataclass(frozen=True)
class Branch:
    label: str
    suffix: Trace
    selected: Optional[Residual]
    start_d: int
    end_d: int
    truth_mask: int = ALL_MUST


def branch_record_experimental(branch: Branch) -> bytes:
    """Structural codec test only; semantic population is reported UNKNOWN.

    The experiment uses the selected recovery residual when present.  It never
    claims this is the uniquely specified population rule for Section 10.3.
    """
    present = branch.selected is not None
    return (
        u8(BRANCH_CODE[branch.label])
        + u8(branch.start_d)
        + u8(branch.end_d)
        + u8(1 if present else 0)
        + (enc_residual(branch.selected) if present else b"")
        + u16(branch.truth_mask)
        + enc_bytes(enc_trace(branch.suffix))
    )


def dec_branch_record_experimental(data: bytes) -> Branch:
    reader = Reader(data)
    branch_code = reader.one()
    reverse = {v: k for k, v in BRANCH_CODE.items()}
    if branch_code not in reverse:
        raise DecodeError("branch code")
    start_d = reader.one()
    end_d = reader.one()
    present = reader.one()
    if present not in (0, 1):
        raise DecodeError("residual presence")
    selected = dec_residual(reader.take(3)) if present else None
    mask = reader.uint16()
    if mask & ~ALL_MUST:
        raise DecodeError("Must padding bits")
    suffix = dec_trace(reader.byte_string())
    reader.finish()
    result = Branch(reverse[branch_code], suffix, selected, start_d, end_d, mask)
    if branch_record_experimental(result) != data:
        raise DecodeError("noncanonical branch record")
    return result


def enc_outcome_experimental(branches: Sequence[Branch]) -> bytes:
    records = enc_list(branch_record_experimental(b) for b in branches)
    projections = b"".join(
        enc_trace_set(project(b.suffix, viewer) for b in branches)
        for viewer in ("CLIENT", "CAPTURE", "PUBLIC", "SELECTOR")
    )
    family_mask = ALL_MUST
    for branch in branches:
        family_mask &= branch.truth_mask
    return records + projections + u16(family_mask)


def dec_outcome_experimental(data: bytes) -> tuple[Branch, ...]:
    reader = Reader(data)
    count = reader.uint64()
    branches = tuple(dec_branch_record_experimental(reader.byte_string()) for _ in range(count))
    for _viewer in range(4):
        # Parse one length-delimited List directly from the shared reader.
        trace_count = reader.uint64()
        raw = tuple(reader.byte_string() for _ in range(trace_count))
        if tuple(sorted(set(raw))) != raw:
            raise DecodeError("outcome trace set")
        for item in raw:
            dec_trace(item)
    mask = reader.uint16()
    if mask & ~ALL_MUST:
        raise DecodeError("outcome Must padding")
    reader.finish()
    if enc_outcome_experimental(branches) != data:
        raise DecodeError("outcome projection mismatch")
    return branches


def recovery_branches(condition: Condition, word: Sequence[str]) -> tuple[Branch, ...]:
    if condition.kind in ACTIVE_KINDS and len(word) > condition.d:
        raise ValueError("UNSUPPORTED(ALLOWANCE)")
    branches: list[Branch] = []
    if condition.kind == "IDLE_RECOVERY":
        assert condition.residual is not None
        initials = (("NONE", condition.residual, ((F_FRAME, f_resume(condition.residual)),
                                                    (F_FRAME, f_allowance(condition.d)),
                                                    (L_READY, b""))),)
    elif condition.kind in ("PENDING_NON_T", "T_PRE_A", "T_POST_A"):
        assert condition.residual is not None
        alias = condition.alias if condition.kind == "PENDING_NON_T" else "T"
        assert alias is not None
        old = condition.residual
        new = delta(old, alias)
        initials = (
            ("OLD", old, ((F_FRAME, SELECT_OLD), (F_FRAME, f_resume(old)),
                          (F_FRAME, f_allowance(condition.d)), (L_READY, b""))),
            ("NEW", new, ((F_FRAME, SELECT_NEW), (F_FRAME, f_resume(new)),
                          (F_FRAME, f_allowance(condition.d)), (L_READY, b""))),
        )
    elif condition.kind == "FIN_PENDING":
        initials = (("NONE", None, ((F_FRAME, RESUME_FIN), (L_READY, b""), (R_STOPPED, b""))),)
    elif condition.kind == "TERMINAL":
        initials = (("NONE", None, ((F_FRAME, RESUME_TERMINAL), (L_READY, b""))),)
    else:
        raise ValueError("condition kind")

    for label, selected, prefix in initials:
        if selected is None:
            suffix = tuple(prefix)
        else:
            suffix, _final_residual = complete_after_active(prefix, selected, word)
        branches.append(Branch(label, suffix, selected, condition.d if selected is not None else 255, 255))
    provisional = tuple(branches)
    mask = evaluate_recovery_must(condition, provisional)
    global RECOVERY_MUST_AUDITS
    RECOVERY_MUST_AUDITS += 1
    if mask != ALL_MUST and len(RECOVERY_MUST_FAILURES) < 16:
        RECOVERY_MUST_FAILURES.append({"condition": condition.semantic_key(), "word": tuple(word), "mask": mask})
    return tuple(replace(branch, truth_mask=mask) for branch in provisional)


def evaluate_recovery_must(condition: Condition, branches: Sequence[Branch]) -> int:
    """Evaluate the ten Section 7.2 propositions for a recovery-cut family.

    The recovery prefix is fixed by the condition: it already contains exactly
    one F:CRASH followed by DOWN.  FIN_PENDING additionally has a pre-cut FIN;
    TERMINAL has pre-cut FIN and STOPPED; T_POST_A has one pre-cut A while its
    interrupted T is pending.
    """
    truths = [True] * 10
    interrupted = condition.kind in ("PENDING_NON_T", "T_PRE_A", "T_POST_A")
    expected_labels = ("OLD", "NEW") if interrupted else ("NONE",)

    # 1: the fixed pre-cut CRASH/DOWN has exactly one valid recovery closure.
    for branch in branches:
        trace = branch.suffix
        ready_positions = [i for i, c in enumerate(trace) if c[0] == L_READY]
        selects = [c for c in trace if c == (F_FRAME, SELECT_OLD) or c == (F_FRAME, SELECT_NEW)]
        truths[0] &= len(ready_positions) == 1 and not any(c[0] in (L_DOWN,) or (c[0] == F_FRAME and c[1].startswith(b"CRASH GAP=")) for c in trace)
        truths[0] &= len(selects) == (1 if interrupted else 0)

    # 2: include the pre-cut FIN/STOPPED facts for special recovery kinds.
    for branch in branches:
        pre = []
        if condition.kind in DEAD_KINDS:
            pre.append((C_FIN, b""))
        if condition.kind == "TERMINAL":
            pre.append((R_STOPPED, b""))
        full = tuple(pre) + branch.suffix
        fin_positions = [i for i, c in enumerate(full) if c[0] == C_FIN]
        stop_positions = [i for i, c in enumerate(full) if c[0] == R_STOPPED]
        ok = len(fin_positions) == 1 and len(stop_positions) == 1 and fin_positions[0] < stop_positions[0]
        if ok:
            ok &= not any(c[0] in (C_FRAME, C_FIN, R_FRAME, R_STOPPED) for c in full[stop_positions[0] + 1 :])
        truths[1] &= ok

    # 3, 4, 5, and 10: parse post-recovery serial transactions.  Recovery
    # selection cancels the interrupted request; a later R must have a new C.
    request_by_bytes = {value: alias for alias, value in REQUEST_BYTES.items()}
    for branch in branches:
        try:
            ready = next(i for i, c in enumerate(branch.suffix) if c[0] == L_READY)
        except StopIteration:
            truths[2] = truths[3] = truths[4] = truths[9] = False
            continue
        before_ready = branch.suffix[:ready]
        if interrupted:
            truths[2] &= not any(c[0] == R_FRAME for c in before_ready)
        post = branch.suffix[ready + 1 :]
        pending_alias: Optional[str] = None
        pending_a = 0
        seen_new_c = False
        for crossing in post:
            tag, payload = crossing
            if tag == C_FRAME:
                if pending_alias is not None or payload not in request_by_bytes:
                    truths[3] = truths[4] = False
                    continue
                pending_alias = request_by_bytes[payload]
                pending_a = 0
                seen_new_c = True
            elif tag == A_FRAME:
                truths[3] &= pending_alias == "T"
                if interrupted and not seen_new_c:
                    truths[9] = False
                pending_a += 1
            elif tag == R_FRAME:
                truths[2] &= pending_alias is not None
                if pending_alias == "T":
                    truths[4] &= pending_a == 1
                pending_alias = None
                pending_a = 0
            elif tag == C_FIN:
                truths[4] &= pending_alias is None
        truths[4] &= pending_alias is None

    # 6: exact ordered family and old/new semantic endpoints.
    if interrupted:
        alias = condition.alias if condition.kind == "PENDING_NON_T" else "T"
        assert condition.residual is not None and alias is not None
        truths[5] &= tuple(branch.label for branch in branches) == expected_labels
        truths[5] &= len(branches) == 2
        if len(branches) == 2:
            truths[5] &= branches[0].selected == condition.residual
            truths[5] &= branches[1].selected == delta(condition.residual, alias)

    # 7: every non-interrupted/special recovery has no SELECT.
    if not interrupted:
        truths[6] &= tuple(branch.label for branch in branches) == ("NONE",)
        truths[6] &= all(not any(c in ((F_FRAME, SELECT_OLD), (F_FRAME, SELECT_NEW)) for c in branch.suffix) for branch in branches)

    # 8: allowance is exact and ordinary C occurrences cannot exceed it.
    for branch in branches:
        ordinary = sum(c[0] == C_FRAME for c in branch.suffix)
        allowances = [c[1] for c in branch.suffix if c[0] == F_FRAME and c[1].startswith(b"ALLOWANCE ")]
        if condition.kind in ACTIVE_KINDS:
            truths[7] &= branch.start_d == condition.d and branch.end_d == 255
            truths[7] &= allowances == [f_allowance(condition.d)] and ordinary <= condition.d
        else:
            truths[7] &= branch.start_d == 255 and not allowances

    # 9: exact RESUME token equals the selected residual or special phase.
    for branch in branches:
        resumes = [c[1] for c in branch.suffix if c[0] == F_FRAME and c[1].startswith(b"RESUME ")]
        if condition.kind in ACTIVE_KINDS:
            truths[8] &= branch.selected is not None and resumes == [f_resume(branch.selected)]
        elif condition.kind == "FIN_PENDING":
            truths[8] &= resumes == [RESUME_FIN]
        else:
            truths[8] &= resumes == [RESUME_TERMINAL]

    return sum((1 << index) for index, truth in enumerate(truths) if truth)


def recovery_projection_probe(condition: Condition, word: Sequence[str], viewer: str) -> bytes:
    branches = recovery_branches(condition, word)
    return enc_trace_set(project(branch.suffix, viewer) for branch in branches)


def recovery_contract_probe(condition: Condition, word: Sequence[str]) -> bytes:
    return enc_outcome_experimental(recovery_branches(condition, word))


def probe_chunks(condition: Condition, contract: bool) -> tuple[bytes, ...]:
    max_depth = condition.d if condition.kind in ACTIVE_KINDS else 0
    chunks: list[bytes] = []
    for length in range(max_depth + 1):
        entries: list[bytes] = []
        for word in words_exact(length):
            key = u8(length) + bytes(RANK[a] for a in word)
            result = recovery_contract_probe(condition, word) if contract else recovery_projection_probe(condition, word, "PUBLIC")
            entries.append(enc_bytes(key) + enc_bytes(result))
        chunks.append(enc_list(entries))
    return tuple(chunks)


def signature_at(chunks: Sequence[bytes], depth: int) -> bytes:
    return enc_list(chunks[: depth + 1])


def canonical_decimal(data: bytes) -> bool:
    return data == b"0" or (bool(re.fullmatch(rb"[1-9][0-9]*", data)))


def enc_decision_key(d: int, client_suffix: Sequence[Crossing]) -> bytes:
    if not 0 <= d <= 3:
        raise ValueError("decision allowance")
    return u8(d) + enc_bytes(enc_trace(client_suffix))


def dec_decision_key(data: bytes) -> tuple[int, Trace]:
    reader = Reader(data)
    d = reader.one()
    if d > 3:
        raise DecodeError("decision allowance")
    trace = dec_trace(reader.byte_string())
    reader.finish()
    if enc_decision_key(d, trace) != data:
        raise DecodeError("decision key")
    return d, trace


def enc_gap_key(public_suffix: Sequence[Crossing], proposed: Optional[Crossing]) -> bytes:
    left = enc_bytes(enc_trace(public_suffix))
    return left + (b"\xff" if proposed is None else enc_bytes(enc_crossing(proposed)))


def dec_gap_key(data: bytes) -> tuple[Trace, Optional[Crossing]]:
    reader = Reader(data)
    trace = dec_trace(reader.byte_string())
    if reader.offset >= len(data):
        raise DecodeError("missing proposed crossing")
    if data[reader.offset :] == b"\xff":
        reader.offset = len(data)
        proposed = None
    else:
        proposed = dec_crossing(reader.byte_string())
    reader.finish()
    if enc_gap_key(trace, proposed) != data:
        raise DecodeError("gap key")
    return trace, proposed


def enc_controller(actions: Sequence[int], d0_indexes: frozenset[int]) -> bytes:
    for i, action in enumerate(actions):
        if not 0 <= action <= 12:
            raise ValueError("controller action")
        if i in d0_indexes and action != 0:
            raise ValueError("UNSUPPORTED(CONTROLLER_D0)")
    return u8(1) + u64(len(actions)) + bytes(actions)


def dec_controller(data: bytes, expected_count: int, d0_indexes: frozenset[int]) -> tuple[int, ...]:
    reader = Reader(data)
    if reader.one() != 1:
        raise DecodeError("controller version")
    count = reader.uint64()
    if count != expected_count:
        raise DecodeError("controller count")
    actions = tuple(reader.take(count))
    reader.finish()
    try:
        canonical = enc_controller(actions, d0_indexes)
    except ValueError as exc:
        raise DecodeError(str(exc)) from exc
    if canonical != data:
        raise DecodeError("controller canonical")
    return actions


def enc_scheduler(bits: Sequence[int]) -> bytes:
    packed = bytearray((len(bits) + 7) // 8)
    for i, bit in enumerate(bits):
        if bit not in (0, 1):
            raise ValueError("scheduler bit")
        packed[i // 8] |= bit << (7 - i % 8)
    return u8(1) + u64(len(bits)) + bytes(packed)


def dec_scheduler(data: bytes, expected_count: int) -> tuple[int, ...]:
    reader = Reader(data)
    if reader.one() != 1:
        raise DecodeError("scheduler version")
    count = reader.uint64()
    if count != expected_count:
        raise DecodeError("scheduler count")
    packed = reader.take((count + 7) // 8)
    reader.finish()
    if count % 8 and packed and packed[-1] & ((1 << (8 - count % 8)) - 1):
        raise DecodeError("scheduler padding")
    bits = tuple((packed[i // 8] >> (7 - i % 8)) & 1 for i in range(count))
    if enc_scheduler(bits) != data:
        raise DecodeError("scheduler canonical")
    return bits


def expect_decode_failure(fn, data: bytes) -> bool:
    try:
        fn(data)
    except (DecodeError, ValueError, IndexError):
        return True
    return False


class Report:
    def __init__(self) -> None:
        self.evaluations: list[dict] = []
        self.findings: dict = {}

    def check(self, name: str, actual, expected, **detail) -> bool:
        ok = actual == expected
        item = {"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected}
        if detail:
            item["detail"] = detail
        self.evaluations.append(item)
        return ok

    def assert_true(self, name: str, actual: bool, **detail) -> bool:
        return self.check(name, bool(actual), True, **detail)

    def unknown(self, name: str, reason: str, **detail) -> None:
        item = {"name": name, "status": "UNKNOWN", "reason": reason}
        if detail:
            item["detail"] = detail
        self.evaluations.append(item)

    def output(self, source: dict) -> dict:
        totals = Counter(item["status"] for item in self.evaluations)
        for status in ("PASS", "FAIL", "UNKNOWN"):
            totals.setdefault(status, 0)
        return json_safe({
            "schema": SCHEMA,
            "source": source,
            "evaluations": self.evaluations,
            "findings": self.findings,
            "summary": dict(sorted(totals.items())),
            "overall": "FAIL" if totals["FAIL"] else ("UNKNOWN" if totals["UNKNOWN"] else "PASS"),
        })


def json_safe(value):
    if isinstance(value, bytes):
        try:
            ascii_value = value.decode("ascii")
        except UnicodeDecodeError:
            ascii_value = None
        return {"hex": value.hex(), "ascii": ascii_value}
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    return value


def parse_seed_tables(text: str) -> dict:
    alphabet_rows = re.findall(r"^\| (\d+) \| ([A-Z0-9]+) \| (.+) \|$", text, re.MULTILINE)
    parsed_alphabet = []
    for rank, alias, phrase in alphabet_rows[:12]:
        if not phrase.endswith(" newline"):
            raise ValueError("alphabet newline spelling")
        parsed_alphabet.append((int(rank), alias, (phrase[:-8] + "\n").encode("ascii")))

    viewer_rows = re.findall(r"^\| (CLIENT|CAPTURE|PUBLIC|SELECTOR) \| ([A-Z, ]+) \|$", text, re.MULTILINE)
    viewers = {name: tuple(part.strip() for part in channels.split(",")) for name, channels in viewer_rows}
    crossing_rows = re.findall(r"^\| (\d+) \| (C frame|typed C:FIN|R frame|R:STOPPED newline|A frame|L:DOWN|L:READY|F frame) \|", text, re.MULTILINE)
    must_block = text.split("The fixed proposition order is:", 1)[1].split("Each is a universal implication", 1)[0]
    must_numbers = tuple(int(n) for n in re.findall(r"(?m)^(\d+)\. ", must_block))
    required_fragments = (
        "F:SELECT old does not semantically apply the interrupted request and resumes r.",
        "F:SELECT new semantically applies delta(r,m) without inventing an R completion",
        "SELECT is forbidden at idle, after an ordinary R, during FIN recovery, and",
        "FIN does not.",
        "No ordinary C is legal at d=0.",
        "The scheduler observes PUBLIC, including A, so it can target",
        "Branch records are ordered NONE alone or OLD then NEW.",
        "Only cuts with the same cut kind and live allowance contract are compared.",
        "The scheduler must nevertheless evaluate the one terminal gap after STOPPED.",
    )
    normalized_text = " ".join(text.split())
    return {
        "alphabet": parsed_alphabet,
        "viewers": viewers,
        "crossing_tags": tuple((int(tag), name) for tag, name in crossing_rows),
        "must_numbers": must_numbers,
        "required_fragments_present": tuple(fragment in normalized_text for fragment in required_fragments),
    }


def clean_corpus(report: Report) -> tuple[list[tuple[tuple[str, ...], Trace, Residual]], dict[Residual, list[int]]]:
    corpus = []
    classes: dict[Residual, list[int]] = defaultdict(list)
    encoded_seen: dict[bytes, int] = {}
    roundtrips_ok = True
    collision_pairs = []
    for word in words_through(2):
        trace, residual = clean_history(word)
        encoded = enc_trace(trace)
        roundtrips_ok &= dec_trace(encoded) == trace
        if encoded in encoded_seen:
            collision_pairs.append((encoded_seen[encoded], len(corpus)))
        encoded_seen[encoded] = len(corpus)
        classes[residual].append(len(corpus))
        corpus.append((word, trace, residual))
    report.check("claim.clean_history_count", len(corpus), 157)
    report.assert_true("canonical.clean_trace_roundtrips", roundtrips_ok)
    report.check("canonical.clean_trace_collision_pairs", collision_pairs, [])
    report.check("claim.clean_distinct_canonical_histories", len(encoded_seen), 157)
    sizes = sorted((len(v) for v in classes.values()), reverse=True)
    report.check("claim.clean_class_count", len(classes), 14)
    report.check("claim.clean_class_size_multiset", sizes, [59, 17, 17, 16, 16, 16, 2, 2, 2, 2, 2, 2, 2, 2])
    same_pairs = sum(n * (n - 1) // 2 for n in sizes)
    total_pairs = len(corpus) * (len(corpus) - 1) // 2
    report.check("claim.clean_same_class_pairs", same_pairs, 2351)
    report.check("claim.clean_unequal_pairs", total_pairs - same_pairs, 9895)
    report.check("claim.clean_total_pairs", total_pairs, 12246)
    return corpus, classes


def clean_separator_and_signatures(report: Report, corpus, classes) -> None:
    empty = {}
    x_probe = {}
    for residual in classes:
        empty[residual] = enc_trace_set((complete_after_active((), residual, ())[0],))
        x_probe[residual] = enc_trace_set((complete_after_active((), residual, ("X",))[0],))
    report.check("clean.no_crash_empty_PUBLIC_signature_classes", len(set(empty.values())), 1)
    report.check("claim.clean_one_X_signature_classes", len(set(x_probe.values())), 14)
    unequal_all_x = all(x_probe[a] != x_probe[b] for a, b in itertools.combinations(classes, 2))
    report.assert_true("claim.every_unequal_clean_pair_X_separated", unequal_all_x)

    # Literal contractual equality also includes SELECTOR and Priv for the same
    # scheduler vector.  With the controller choosing FIN immediately, a bit on
    # the initial pre-FIN gap performs an idle crash and exposes F:RESUME r.
    empty_initial_crash_selector = {}
    for residual in classes:
        branches = simulate_clean_linear(residual, (), ("IDLE", 0))
        empty_initial_crash_selector[residual] = enc_trace_set(project(branch.suffix, "SELECTOR") for branch in branches)
    report.check("prediction.3.no_zero_ordinary_contractual_separator",
                 len(set(empty_initial_crash_selector.values())) == 1, True,
                 actual_selector_signature_classes=len(set(empty_initial_crash_selector.values())),
                 witness="controller FIN; scheduler crashes at initial gap; SELECTOR sees RESUME ACTIVE")
    report.assert_true("clean.every_unequal_pair_zero_ordinary_SELECTOR_separated",
                       all(empty_initial_crash_selector[a] != empty_initial_crash_selector[b]
                           for a, b in itertools.combinations(classes, 2)))
    same_lift = defaultdict(list)
    for index, (_word, _trace, residual) in enumerate(corpus):
        same_lift[x_probe[residual]].append(index)
    report.check("clean.future_signature_lift_class_sizes", sorted((len(v) for v in same_lift.values()), reverse=True),
                 [59, 17, 17, 16, 16, 16, 2, 2, 2, 2, 2, 2, 2, 2],
                 method="exact no-crash X future bytes; exhaustive crash congruence checked separately")


def gap_descriptors(word: Sequence[str]) -> list[tuple[str, int]]:
    gaps: list[tuple[str, int]] = [("IDLE", 0)]
    for i, alias in enumerate(word):
        gaps.append(("T_PRE_A" if alias == "T" else "PENDING", i))
        if alias == "T":
            gaps.append(("T_POST_A", i))
        gaps.append(("IDLE", i + 1))
    gaps.extend((("FIN_PENDING", len(word)), ("TERMINAL", len(word))))
    return gaps


def simulate_clean_linear(start: Residual, word: Sequence[str], gap: Optional[tuple[str, int]]) -> tuple[Branch, ...]:
    # Prefix through the selected nominal gap.
    completed = 0
    prefix: list[Crossing] = []
    residual = start
    if gap is None:
        full, final_residual = complete_after_active((), start, word)
        return (Branch("NONE", full, final_residual, 3, 255),)

    phase, index = gap
    for alias in word[:index]:
        residual = append_completed(prefix, residual, alias)
        completed += 1
    crossing_count = len(prefix)
    d = 3 - completed

    if phase == "IDLE":
        prefix.extend(((F_FRAME, f_crash(crossing_count)), (L_DOWN, b""),
                       (F_FRAME, f_resume(residual)), (F_FRAME, f_allowance(d)), (L_READY, b"")))
        suffix, final = complete_after_active(prefix, residual, word[index:])
        return (Branch("NONE", suffix, residual, 3, 255),)

    if phase in ("PENDING", "T_PRE_A", "T_POST_A"):
        alias = word[index]
        prefix.append((C_FRAME, REQUEST_BYTES[alias]))
        d -= 1
        if phase == "T_POST_A":
            prefix.append((A_FRAME, attempt_bytes(residual)))
        crossing_count = len(prefix)
        prefix.extend(((F_FRAME, f_crash(crossing_count)), (L_DOWN, b"")))
        out = []
        for label, selected in (("OLD", residual), ("NEW", delta(residual, alias))):
            local = list(prefix)
            local.extend(((F_FRAME, SELECT_OLD if label == "OLD" else SELECT_NEW),
                          (F_FRAME, f_resume(selected)), (F_FRAME, f_allowance(d)), (L_READY, b"")))
            suffix, _final = complete_after_active(local, selected, word[index + 1 :])
            out.append(Branch(label, suffix, selected, 3, 255))
        return tuple(out)

    # Finish every ordinary request before the special FIN gaps.
    for alias in word[index:]:
        residual = append_completed(prefix, residual, alias)
    if phase == "FIN_PENDING":
        prefix.append((C_FIN, b""))
        crossing_count = len(prefix)
        prefix.extend(((F_FRAME, f_crash(crossing_count)), (L_DOWN, b""),
                       (F_FRAME, RESUME_FIN), (L_READY, b""), (R_STOPPED, b"")))
        return (Branch("NONE", tuple(prefix), None, 3, 255),)
    if phase == "TERMINAL":
        prefix.extend(((C_FIN, b""), (R_STOPPED, b"")))
        crossing_count = len(prefix)
        prefix.extend(((F_FRAME, f_crash(crossing_count)), (L_DOWN, b""),
                       (F_FRAME, RESUME_TERMINAL), (L_READY, b"")))
        return (Branch("NONE", tuple(prefix), None, 3, 255),)
    raise AssertionError(phase)


def linear_schedule_checks(report: Report, reachable_clean: Sequence[Residual]) -> None:
    rows = []
    total_words = total_t = total_base = total_padded = 0
    plan_digest = hashlib.sha256()
    congruence: dict[Residual, str] = {}
    for n in range(4):
        words = list(words_exact(n))
        t_count = sum(word.count("T") for word in words)
        base = 0
        padded = 0
        for word in words:
            gaps = gap_descriptors(word)
            base += 1 + len(gaps)
            padded += 1
            for descriptor in gaps:
                padded += 2 if descriptor[0] in ("PENDING", "T_PRE_A", "T_POST_A") else 1
        rows.append({"n": n, "words": len(words), "T_occurrences": t_count, "base": base, "padded": padded})
        total_words += len(words)
        total_t += t_count
        total_base += base
        total_padded += padded
    report.check("claim.schedule.rows", rows, [
        {"n": 0, "words": 1, "T_occurrences": 0, "base": 4, "padded": 4},
        {"n": 1, "words": 12, "T_occurrences": 1, "base": 73, "padded": 86},
        {"n": 2, "words": 144, "T_occurrences": 24, "base": 1176, "padded": 1488},
        {"n": 3, "words": 1728, "T_occurrences": 432, "base": 17712, "padded": 23328},
    ])
    report.check("claim.schedule.total_words", total_words, 1885)
    report.check("claim.schedule.total_T_occurrences", total_t, 457)
    report.check("claim.schedule.base_per_clean", total_base, 18965)
    report.check("claim.schedule.padded_per_clean", total_padded, 24906)
    report.check("claim.schedule.base_across_clean_histories", total_base * 157, 2977505)
    report.check("claim.schedule.padded_across_clean_histories", total_padded * 157, 3910242)

    # Exhaust every linear word/gap oracle outcome for each reachable clean
    # coordinate.  The digest is evidence only; grouping never relies on hash
    # equality.  Exact X bytes above establish all unequal classes.
    for residual in sorted(set(reachable_clean)):
        digest = hashlib.sha256()
        structures = 0
        slots = 0
        for word in words_through(3):
            schedules = [None] + gap_descriptors(word)
            for schedule in schedules:
                branches = simulate_clean_linear(residual, word, schedule)
                assert tuple(branch.label for branch in branches) in (("NONE",), ("OLD", "NEW"))
                encoded = enc_outcome_experimental(branches)
                dec_outcome_experimental(encoded)
                digest.update(enc_bytes(u8(len(word)) + bytes(RANK[a] for a in word)))
                schedule_bytes = b"NO" if schedule is None else (schedule[0] + ":" + str(schedule[1])).encode("ascii")
                digest.update(enc_bytes(schedule_bytes))
                digest.update(enc_bytes(encoded))
                structures += 1
                slots += len(branches)
        assert structures == 18965 and slots == 24906
        congruence[residual] = digest.hexdigest()
        plan_digest.update(enc_residual(residual) + bytes.fromhex(congruence[residual]))
    report.check("clean.exhaustive_linear_future_signature_count", len(set(congruence.values())), 14)
    report.findings["clean_linear_future_manifest"] = {
        "method": "all words length 0..3; no-crash and every nominal gap; OLD/NEW retained before projection",
        "reachable_coordinate_digests": len(congruence),
        "aggregate_sha256": plan_digest.hexdigest(),
    }


def trace_token_key(trace: Sequence[Crossing], token_ids: dict[Crossing, int]) -> int:
    # Exact injective radix encoding over the finite crossing-token alphabet.
    key = 1
    for crossing in trace:
        if crossing not in token_ids:
            token_ids[crossing] = len(token_ids) + 1
        token = token_ids[crossing]
        if token >= 256:
            raise RuntimeError("prefix token alphabet exceeded exact radix")
        key = (key << 8) | token
    return key


def enumerate_recovery_prefixes(report: Report, clean) -> tuple[set[Condition], Counter[Condition]]:
    conditions: set[Condition] = set()
    lifts: Counter[Condition] = Counter()
    distinct_prefixes: set[int] = set()
    token_ids: dict[Crossing, int] = {}
    phase_counts = Counter()
    corpus_digest = hashlib.sha256()
    roundtrip_samples = 0
    per_clean_totals = []

    future_cache: dict[tuple[Residual, tuple[str, ...]], tuple[Trace, Residual]] = {}
    for clean_index, (_clean_word, clean_trace, start) in enumerate(clean):
        per_clean = Counter()
        for length in range(4):
            for word in words_exact(length):
                cache_key = (start, word)
                if cache_key not in future_cache:
                    future_cache[cache_key] = execute_word(start, word)
                future_trace, source = future_cache[cache_key]
                g = len(future_trace)
                d_idle = 3 - length

                entries: list[tuple[str, Trace, Condition]] = []
                entries.append(("Idle", clean_trace + future_trace + ((F_FRAME, f_crash(g)), (L_DOWN, b"")),
                                Condition("IDLE_RECOVERY", d_idle, source)))
                entries.append(("FIN-pending", clean_trace + future_trace + ((C_FIN, b""),
                                (F_FRAME, f_crash(g + 1)), (L_DOWN, b"")),
                                Condition("FIN_PENDING", d_idle, source)))
                entries.append(("Terminal", clean_trace + future_trace + ((C_FIN, b""), (R_STOPPED, b""),
                                (F_FRAME, f_crash(g + 2)), (L_DOWN, b"")),
                                Condition("TERMINAL", d_idle, source)))

                if length <= 2:
                    d_pending = 2 - length
                    for alias in ALIASES:
                        if alias == "T":
                            continue
                        entries.append(("Non-T pending", clean_trace + future_trace
                                        + ((C_FRAME, REQUEST_BYTES[alias]), (F_FRAME, f_crash(g + 1)), (L_DOWN, b"")),
                                        Condition("PENDING_NON_T", d_pending, source, alias)))
                    entries.append(("T pre-A", clean_trace + future_trace
                                    + ((C_FRAME, REQUEST_BYTES["T"]), (F_FRAME, f_crash(g + 1)), (L_DOWN, b"")),
                                    Condition("T_PRE_A", d_pending, source)))
                    entries.append(("T post-A", clean_trace + future_trace
                                    + ((C_FRAME, REQUEST_BYTES["T"]), (A_FRAME, attempt_bytes(source)),
                                       (F_FRAME, f_crash(g + 2)), (L_DOWN, b"")),
                                    Condition("T_POST_A", d_pending, source)))

                for family, prefix, condition in entries:
                    key = trace_token_key(prefix, token_ids)
                    distinct_prefixes.add(key)
                    phase_counts[family] += 1
                    per_clean[family] += 1
                    conditions.add(condition)
                    lifts[condition] += 1
                    encoded = enc_trace(prefix)
                    corpus_digest.update(enc_bytes(encoded))
                    if roundtrip_samples < 64 or (len(distinct_prefixes) % 4096 == 0):
                        if dec_trace(encoded) != prefix:
                            report.assert_true("canonical.recovery_prefix_roundtrip", False)
                        roundtrip_samples += 1
        per_clean_totals.append(sum(per_clean.values()))

    expected_phases = {
        "Idle": 295945,
        "Non-T pending": 271139,
        "T pre-A": 24649,
        "T post-A": 24649,
        "FIN-pending": 295945,
        "Terminal": 295945,
    }
    report.check("claim.recovery_prefix_phase_counts", dict(sorted(phase_counts.items())), dict(sorted(expected_phases.items())))
    report.check("claim.recovery_prefixes_per_clean_history", Counter(per_clean_totals), {7696: 157})
    report.check("claim.recovery_prefix_total", sum(phase_counts.values()), 1208272)
    report.check("claim.recovery_prefix_exact_distinct", len(distinct_prefixes), 1208272,
                 method="injective base-256 sequence of exact crossing tokens; canonical trace codec sampled round trips")
    report.check("claim.total_cut_histories", len(clean) + len(distinct_prefixes), 1208429)
    report.findings["recovery_prefix_manifest"] = {
        "canonical_enumeration_sha256": corpus_digest.hexdigest(),
        "exact_crossing_token_count": len(token_ids),
        "roundtrip_samples": roundtrip_samples,
    }
    return conditions, lifts


def condition_counts(report: Report, conditions: set[Condition]) -> None:
    family = Counter()
    changing = Counter()
    reachable_by_d = defaultdict(set)
    for condition in conditions:
        if condition.kind == "IDLE_RECOVERY":
            family["Idle active (r,d)"] += 1
            reachable_by_d[condition.d].add(condition.residual)
        elif condition.kind == "PENDING_NON_T":
            assert condition.residual is not None and condition.alias is not None
            if delta(condition.residual, condition.alias) == condition.residual:
                family["Interrupted no-op non-T"] += 1
                changing[(condition.d, "noop")] += 1
            else:
                family["Interrupted changing non-T"] += 1
                changing[(condition.d, "changing")] += 1
        elif condition.kind == "T_PRE_A":
            family["T pre-A"] += 1
        elif condition.kind == "T_POST_A":
            family["T post-A"] += 1
        elif condition.kind == "FIN_PENDING":
            family["FIN-pending source conditions"] += 1
        elif condition.kind == "TERMINAL":
            family["Terminal source conditions"] += 1
    expected = {
        "Idle active (r,d)": 68,
        "Interrupted changing non-T": 195,
        "Interrupted no-op non-T": 355,
        "T pre-A": 50,
        "T post-A": 50,
        "FIN-pending source conditions": 68,
        "Terminal source conditions": 68,
    }
    report.check("claim.normalized_condition_families", dict(sorted(family.items())), dict(sorted(expected.items())))
    report.check("claim.normalized_condition_total", len(conditions), 854)
    reach_counts = {3 - d: len(values) for d, values in reachable_by_d.items()}
    report.check("claim.reachable_residuals_after_completed_depth", [reach_counts[i] for i in range(4)], [14, 18, 18, 18])
    detail = {
        str(d): {"changing": changing[(d, "changing")], "noop": changing[(d, "noop")]}
        for d in (2, 1, 0)
    }
    report.check("claim.interrupted_non_T_by_remaining_allowance", detail, {
        "2": {"changing": 57, "noop": 97},
        "1": {"changing": 69, "noop": 129},
        "0": {"changing": 69, "noop": 129},
    })


def quotient_checks(report: Report, conditions: set[Condition], lifts: Counter[Condition]) -> None:
    chunks_public: dict[Condition, tuple[bytes, ...]] = {}
    chunks_contract: dict[Condition, tuple[bytes, ...]] = {}
    for condition in sorted(conditions):
        chunks_public[condition] = probe_chunks(condition, contract=False)
        chunks_contract[condition] = probe_chunks(condition, contract=True)
    report.assert_true("Must.recovery_complete_branch_families_audited", RECOVERY_MUST_AUDITS > 0,
                       family_evaluations=RECOVERY_MUST_AUDITS)
    report.check("prediction.14.recovery_branch_Must_failures", RECOVERY_MUST_FAILURES, [])

    def final_sig(table: dict[Condition, tuple[bytes, ...]], condition: Condition) -> bytes:
        depth = condition.d if condition.kind in ACTIVE_KINDS else 0
        return signature_at(table[condition], depth)

    def relaxed_classes(table):
        groups = defaultdict(list)
        for condition in conditions:
            groups[(condition.live_d, final_sig(table, condition))].append(condition)
        return groups

    def literal_classes(table):
        groups = defaultdict(list)
        for condition in conditions:
            groups[(condition.kind, condition.live_d, final_sig(table, condition))].append(condition)
        return groups

    public_relaxed = relaxed_classes(chunks_public)
    contract_relaxed = relaxed_classes(chunks_contract)
    public_literal = literal_classes(chunks_public)
    contract_literal = literal_classes(chunks_contract)

    def by_d(groups):
        counts = Counter()
        for key in groups:
            # relaxed key=(d,sig), literal=(kind,d,sig)
            d = key[-2]
            counts["dead" if d is None else str(d)] += 1
        return dict(sorted(counts.items()))

    report.check("prediction.7.PUBLIC_contractual_literal_quotient", len(public_literal), 139,
                 actual_by_allowance=by_d(public_literal),
                 cause="Section 7.3 forbids comparison across distinct cut kinds")
    report.check("prediction.7.PRIV_SELECTOR_contractual_literal_quotient", len(contract_literal), 315,
                 actual_by_allowance=by_d(contract_literal),
                 cause="Section 7.3 forbids comparison across distinct cut kinds")
    report.check("section9.relaxed_PUBLIC_suffix_behavior_quotient", len(public_relaxed), 139,
                 scope="ignores F/Priv and also relaxes Section 7.3 cut-kind comparability")
    report.check("section9.relaxed_PRIV_suffix_behavior_quotient", len(contract_relaxed), 315,
                 scope="relaxes Section 7.3 cut-kind comparability")
    report.check("section9.relaxed_PUBLIC_by_allowance", by_d(public_relaxed),
                 {"0": 1, "1": 63, "2": 59, "3": 14, "dead": 2})
    report.check("literal.PUBLIC_by_allowance", by_d(public_literal),
                 {"0": 4, "1": 117, "2": 101, "3": 14, "dead": 2})
    report.check("section9.relaxed_PRIV_by_allowance", by_d(contract_relaxed),
                 {"0": 105, "1": 105, "2": 89, "3": 14, "dead": 2})
    report.check("literal.PRIV_by_allowance", by_d(contract_literal),
                 {"0": 141, "1": 141, "2": 117, "3": 14, "dead": 2})

    relaxed_hist = Counter(len(group) for group in contract_relaxed.values())
    literal_hist = Counter(len(group) for group in contract_literal.values())
    report.check("prediction.8.relaxed_normalized_multiplicity_histogram",
                 dict(sorted(relaxed_hist.items())), {1: 263, 8: 9, 9: 27, 10: 14, 68: 2},
                 scope="matches only after cross-kind merging")
    report.check("prediction.8.contractual_literal_multiplicity_histogram",
                 dict(sorted(literal_hist.items())), {1: 263, 8: 9, 9: 27, 10: 14, 68: 2},
                 actual_expected_from_literal_rules={1: 363, 6: 9, 7: 27, 8: 14, 68: 2})

    # Symbolic exact-prefix lifts.  Future signatures were evaluated once per
    # normalized condition; exact histories are mapped through their enumerated
    # condition frequencies.  This is not a direct 1.2m-history future run.
    def lift_hist(groups):
        return Counter(sum(lifts[c] for c in group) for group in groups.values())

    report.findings["symbolic_exact_prefix_lifts"] = {
        "method": "enumerated exact-prefix -> normalized-condition frequency, then exact normalized future signature",
        "not_direct_exact_history_future_evaluation": True,
        "public_relaxed_classes": len(public_relaxed),
        "public_literal_classes": len(public_literal),
        "contract_relaxed_classes": len(contract_relaxed),
        "contract_literal_classes": len(contract_literal),
        "public_relaxed_class_size_histogram": {str(k): v for k, v in sorted(lift_hist(public_relaxed).items())},
        "contract_relaxed_class_size_histogram": {str(k): v for k, v in sorted(lift_hist(contract_relaxed).items())},
        "contract_literal_class_size_histogram": {str(k): v for k, v in sorted(lift_hist(contract_literal).items())},
    }

    # Remaining-depth refinements are computed from exact probe bytes, not from
    # residual/predicted labels.
    depth_rows = []
    for d in (3, 2, 1, 0):
        subset = [c for c in conditions if c.kind in ACTIVE_KINDS and c.d == d]
        for depth in range(d + 1):
            pub_rel = len({signature_at(chunks_public[c], depth) for c in subset})
            priv_rel = len({signature_at(chunks_contract[c], depth) for c in subset})
            pub_lit = len({(c.kind, signature_at(chunks_public[c], depth)) for c in subset})
            priv_lit = len({(c.kind, signature_at(chunks_contract[c], depth)) for c in subset})
            depth_rows.append({"remaining_d": d, "probe_depth": depth,
                               "public_relaxed": pub_rel, "public_literal": pub_lit,
                               "priv_relaxed": priv_rel, "priv_literal": priv_lit})
    report.findings["remaining_depth_future_refinement"] = depth_rows

    # Explicitly exercise the Section 11.4 pair.
    pre = next(c for c in conditions if c.kind == "T_PRE_A" and c.d == 2 and c.residual == (0, 0, 0))
    post = next(c for c in conditions if c.kind == "T_POST_A" and c.d == 2 and c.residual == (0, 0, 0))
    same_public = final_sig(chunks_public, pre) == final_sig(chunks_public, post)
    same_priv = final_sig(chunks_contract, pre) == final_sig(chunks_contract, post)
    report.assert_true("section11.4.T_pre_post_relaxed_suffix_merger", same_public and same_priv)
    report.check("section11.4.T_pre_post_literal_future_equivalence", pre.kind == post.kind and same_priv, True,
                 actual_cut_kinds=[pre.kind, post.kind], section7_3="same cut kind required")

    # Exact signature collision audit: equal signature groups must agree on all
    # stored exact probe chunks.  This detects implementation hash shortcuts;
    # grouping itself used the bytes, never hashes or predicted labels.
    collision_ok = True
    for groups, table in ((public_relaxed, chunks_public), (contract_relaxed, chunks_contract),
                          (public_literal, chunks_public), (contract_literal, chunks_contract)):
        for group in groups.values():
            reference = table[group[0]]
            collision_ok &= all(table[c] == reference for c in group)
    report.assert_true("future_signature.exact_bytes_no_false_hash_collisions", collision_ok)


def negative_controls(report: Report, conditions: set[Condition]) -> None:
    controls = {}

    # Alphabet and request boundary.
    controls["alphabet_empty_is_not_FIN"] = b"" not in REQUEST_BYTES.values() and (C_FIN, b"") != (C_FRAME, b"")
    controls["alphabet_rank_and_bytes_unique"] = len(set(REQUEST_BYTES.values())) == 12 and tuple(RANK[a] for a in ALIASES) == tuple(range(12))
    controls["nonalphabet_rejected"] = False
    try:
        delta((0, 0, 0), "PLUGIN")
    except ValueError:
        controls["nonalphabet_rejected"] = True

    # Projection isolation, including A-visible scheduler/public distinction.
    probe = ((C_FRAME, REQUEST_BYTES["T"]), (A_FRAME, attempt_bytes((0, 0, 0))),
             (F_FRAME, SELECT_OLD), (L_READY, b""), (R_FRAME, reply_bytes((0, 0, 0), "T")))
    controls["viewer_CLIENT_excludes_A_F"] = tuple(c[0] for c in project(probe, "CLIENT")) == (C_FRAME, L_READY, R_FRAME)
    controls["viewer_CAPTURE_only_A"] = tuple(c[0] for c in project(probe, "CAPTURE")) == (A_FRAME,)
    controls["viewer_PUBLIC_includes_A_excludes_F"] = tuple(c[0] for c in project(probe, "PUBLIC")) == (C_FRAME, A_FRAME, L_READY, R_FRAME)
    controls["viewer_SELECTOR_only_F"] = tuple(c[0] for c in project(probe, "SELECTOR")) == (F_FRAME,)

    # Occurrence/application/SELECT and exact completion distinctions.
    r0 = (0, 0, 0)
    controls["C_occurrence_does_not_apply"] = r0 != delta(r0, "AI")
    controls["SELECT_old_no_apply"] = r0 == r0 and r0 != delta(r0, "AI")
    controls["SELECT_new_applies_without_R"] = delta(r0, "AI") == (0, 1, 0)
    pending = Condition("PENDING_NON_T", 2, r0, "AI")
    branches = recovery_branches(pending, ())
    controls["OLD_NEW_order_retained"] = tuple(b.label for b in branches) == ("OLD", "NEW")
    controls["interrupted_has_no_ordinary_R"] = all(not any(c[0] == R_FRAME for c in b.suffix[:4]) for b in branches)
    controls["Priv_keeps_noop_labels_May_dedups"] = (
        len(recovery_branches(Condition("PENDING_NON_T", 2, r0, "Q"), ())) == 2
        and len({project(b.suffix, "PUBLIC") for b in recovery_branches(Condition("PENDING_NON_T", 2, r0, "Q"), ())}) == 1
    )
    controls["completion_precondition_changes_bytes"] = reply_bytes(r0, "AI") != reply_bytes((0, 1, 0), "AI")
    ttrace, _ = execute_word(r0, ("T",))
    controls["completed_T_A_before_R"] = tuple(c[0] for c in ttrace) == (C_FRAME, A_FRAME, R_FRAME)

    # Allowance/terminal distinctions.
    controls["ordinary_decrements_FIN_does_not"] = pending.d == 2 and C_FIN != C_FRAME
    controls["d0_controller_forces_FIN"] = expect_decode_failure(
        lambda data: dec_controller(data, 1, frozenset((0,))),
        u8(1) + u64(1) + b"\x01",
    )
    fin = next(c for c in conditions if c.kind == "FIN_PENDING")
    term = next(c for c in conditions if c.kind == "TERMINAL")
    fin_public = recovery_projection_probe(fin, (), "PUBLIC")
    term_public = recovery_projection_probe(term, (), "PUBLIC")
    controls["FIN_pending_vs_terminal_zero_ordinary_separator"] = fin_public != term_public
    controls["FIN_pending_exactly_one_STOPPED"] = sum(c[0] == R_STOPPED for c in recovery_branches(fin, ())[0].suffix) == 1
    controls["terminal_recovery_no_C_or_R"] = not any(c[0] in (C_FRAME, C_FIN, R_FRAME, R_STOPPED) for c in recovery_branches(term, ())[0].suffix)

    # T pre/post capture fact and blind retry.
    source = (0, 0, 0)
    pre_prefix = ((C_FRAME, REQUEST_BYTES["T"]),)
    post_prefix = pre_prefix + ((A_FRAME, attempt_bytes(source)),)
    retry_trace, _ = execute_word(source, ("T",))
    controls["T_pre_retry_one_A"] = sum(c[0] == A_FRAME for c in pre_prefix + retry_trace) == 1
    controls["T_post_retry_two_A"] = sum(c[0] == A_FRAME for c in post_prefix + retry_trace) == 2

    # Scheduler key includes proposed crossing and PUBLIC A.
    empty_key_c = enc_gap_key((), (C_FRAME, REQUEST_BYTES["T"]))
    empty_key_fin = enc_gap_key((), (C_FIN, b""))
    pre_a_key = enc_gap_key(((C_FRAME, REQUEST_BYTES["T"]),), (A_FRAME, attempt_bytes(source)))
    post_a_key = enc_gap_key(((C_FRAME, REQUEST_BYTES["T"]), (A_FRAME, attempt_bytes(source))),
                             (R_FRAME, reply_bytes(source, "T")))
    controls["scheduler_proposed_crossing_distinguishes_C_FIN"] = empty_key_c != empty_key_fin
    controls["scheduler_PUBLIC_A_distinguishes_T_gaps"] = pre_a_key != post_a_key
    controls["scheduler_END_distinct"] = enc_gap_key((), None) != enc_gap_key((), (R_STOPPED, b""))
    controls["smallest_padding_T_is_nine"] = 1 + sum(2 if d[0] in ("PENDING", "T_PRE_A", "T_POST_A") else 1 for d in gap_descriptors(("T",))) == 9

    # Primitive/canonical round trips and malformed negative controls.
    all_residuals = tuple(itertools.product(range(3), range(3), range(2)))
    controls["residual_codec_roundtrip_collision_free"] = (
        len({enc_residual(r) for r in all_residuals}) == 18
        and all(dec_residual(enc_residual(r)) == r for r in all_residuals)
    )
    supported_crossings = [(C_FRAME, b) for b in REQUEST_BYTES.values()] + [
        (C_FIN, b""), (R_STOPPED, b""), (L_DOWN, b""), (L_READY, b""),
        (F_FRAME, CUT), (F_FRAME, SELECT_OLD), (F_FRAME, SELECT_NEW),
    ]
    controls["crossing_codec_roundtrip_collision_free"] = (
        len({enc_crossing(c) for c in supported_crossings}) == len(supported_crossings)
        and all(dec_crossing(enc_crossing(c)) == c for c in supported_crossings)
    )
    controls["typed_crossing_payload_rejected"] = expect_decode_failure(dec_crossing, u8(C_FIN) + enc_bytes(b"x"))
    controls["trailing_bytes_rejected"] = expect_decode_failure(dec_crossing, enc_crossing((C_FIN, b"")) + b"x")
    controls["trace_set_duplicate_rejected"] = expect_decode_failure(dec_trace_set, enc_list((enc_trace(()), enc_trace(()))))
    controls["canonical_decimal_rejects_leading_zero"] = canonical_decimal(b"0") and canonical_decimal(b"17") and not canonical_decimal(b"00") and not canonical_decimal(b"01")
    decision = enc_decision_key(2, ((L_READY, b""),))
    controls["decision_key_roundtrip"] = dec_decision_key(decision) == (2, ((L_READY, b""),))
    gap = enc_gap_key(((A_FRAME, attempt_bytes(source)),), (R_FRAME, reply_bytes(source, "T")))
    controls["gap_key_roundtrip"] = dec_gap_key(gap) == (((A_FRAME, attempt_bytes(source)),), (R_FRAME, reply_bytes(source, "T")))
    controller = enc_controller((1, 0), frozenset((1,)))
    controls["controller_roundtrip"] = dec_controller(controller, 2, frozenset((1,))) == (1, 0)
    scheduler = enc_scheduler((1, 0, 1, 0, 1, 0, 1, 0, 1))
    controls["scheduler_roundtrip_nine_bits"] = dec_scheduler(scheduler, 9) == (1, 0, 1, 0, 1, 0, 1, 0, 1)
    malformed_scheduler = scheduler[:-1] + bytes((scheduler[-1] | 1,))
    controls["scheduler_nonzero_padding_rejected"] = expect_decode_failure(lambda b: dec_scheduler(b, 9), malformed_scheduler)
    experimental_outcome = enc_outcome_experimental(branches)
    controls["branch_outcome_structural_roundtrip"] = dec_outcome_experimental(experimental_outcome) == branches

    # Independently falsify each Must bit with a targeted malformed family.
    def map_suffix(family: Sequence[Branch], transform) -> tuple[Branch, ...]:
        return tuple(replace(branch, suffix=transform(branch.suffix)) for branch in family)

    def remove_first(trace: Trace, predicate) -> Trace:
        out = list(trace)
        for i, crossing in enumerate(out):
            if predicate(crossing):
                del out[i]
                return tuple(out)
        return tuple(out)

    def insert_after_ready(trace: Trace, crossing: Crossing) -> Trace:
        out = list(trace)
        index = next(i for i, item in enumerate(out) if item[0] == L_READY)
        out.insert(index + 1, crossing)
        return tuple(out)

    valid_pending = recovery_branches(pending, ())
    controls["Must_all_ten_valid_family"] = evaluate_recovery_must(pending, valid_pending) == ALL_MUST
    m1 = map_suffix(valid_pending, lambda t: remove_first(t, lambda c: c[0] == L_READY))
    controls["Must_1_missing_READY_detected"] = not (evaluate_recovery_must(pending, m1) & (1 << 0))
    m2 = map_suffix(valid_pending, lambda t: t + ((C_FIN, b""),))
    controls["Must_2_C_after_STOPPED_detected"] = not (evaluate_recovery_must(pending, m2) & (1 << 1))
    m3 = map_suffix(valid_pending, lambda t: ((R_FRAME, b"INVENTED\n"),) + t)
    controls["Must_3_interrupted_R_detected"] = not (evaluate_recovery_must(pending, m3) & (1 << 2))
    idle = Condition("IDLE_RECOVERY", 2, r0)
    valid_idle = recovery_branches(idle, ())
    m4 = map_suffix(valid_idle, lambda t: insert_after_ready(t, (A_FRAME, attempt_bytes(r0))))
    controls["Must_4_A_without_pending_T_detected"] = not (evaluate_recovery_must(idle, m4) & (1 << 3))
    completed_t = recovery_branches(idle, ("T",))
    m5 = map_suffix(completed_t, lambda t: tuple(c for c in t if c[0] != A_FRAME))
    controls["Must_5_completed_T_missing_A_detected"] = not (evaluate_recovery_must(idle, m5) & (1 << 4))
    controls["Must_6_missing_NEW_branch_detected"] = not (evaluate_recovery_must(pending, valid_pending[:1]) & (1 << 5))
    m7 = map_suffix(valid_idle, lambda t: ((F_FRAME, SELECT_OLD),) + t)
    controls["Must_7_idle_SELECT_detected"] = not (evaluate_recovery_must(idle, m7) & (1 << 6))
    m8 = map_suffix(valid_idle, lambda t: tuple((F_FRAME, b"ALLOWANCE 1\n") if c == (F_FRAME, f_allowance(2)) else c for c in t))
    controls["Must_8_wrong_ALLOWANCE_detected"] = not (evaluate_recovery_must(idle, m8) & (1 << 7))
    m9 = map_suffix(valid_idle, lambda t: tuple((F_FRAME, f_resume((1, 0, 0))) if c == (F_FRAME, f_resume(r0)) else c for c in t))
    controls["Must_9_wrong_RESUME_detected"] = not (evaluate_recovery_must(idle, m9) & (1 << 8))
    post_condition = Condition("T_POST_A", 2, r0)
    valid_post = recovery_branches(post_condition, ())
    m10 = map_suffix(valid_post, lambda t: insert_after_ready(t, (A_FRAME, attempt_bytes(r0))))
    controls["Must_10_replayed_A_detected"] = not (evaluate_recovery_must(post_condition, m10) & (1 << 9))

    for name, actual in sorted(controls.items()):
        report.assert_true("negative_control." + name, actual)


def codec_ambiguities(report: Report) -> None:
    # Two distinct presence maps both satisfy every explicit byte-production
    # sentence because the promised kind->presence table is absent.
    residual = (0, 0, 0)
    terminal_prefix = ((F_FRAME, CUT), (C_FIN, b""), (R_STOPPED, b""),
                       (F_FRAME, f_crash(2)), (L_DOWN, b""))
    absent = u8(KIND_CODE["TERMINAL"]) + u8(255) + enc_trace(terminal_prefix)
    present = u8(KIND_CODE["TERMINAL"]) + u8(255) + enc_residual(residual) + enc_trace(terminal_prefix)
    report.unknown(
        "canonical.EncCut_optional_presence_and_roundtrip",
        "Section 10.1 says residual/alias presence is determined by kind but supplies no kind-to-presence table.",
        two_distinct_plausible_terminal_encodings={"absent_sha256": sha256(absent), "present_sha256": sha256(present)},
    )
    report.unknown(
        "canonical.EncBranchRecord_residual_population",
        "The residual-present field is encoded, but the record prose does not uniquely say whether it carries the recovery-selected residual, final residual, or is absent in a complete terminal suffix.",
    )
    report.unknown(
        "canonical.EncWitness_exact_bytes",
        "EncWitness embeds EncCut and EncOutcome/branch records, so the two unresolved population rules prevent a unique canonical witness byte string.",
    )
    report.unknown(
        "canonical.EncWitness_viewer_admissibility",
        "EncWitness encodes a viewer code, but the witness-order rules do not require that viewer to name a differing projection and define no Priv/Must reason code. Allowing every stated viewer code makes CLIENT=0 bytewise preferred even for a SELECTOR-only distinction; adding a relevance rule would be unwritten semantics.",
    )
    report.unknown(
        "closure.D_size_and_controller_table_count",
        "The seed explicitly declares the numeric D size UNKNOWN; this experiment does not invent it.",
    )
    report.unknown(
        "closure.G_size_and_scheduler_table_count",
        "The seed explicitly declares the numeric G size UNKNOWN; this experiment checks the key/vector codec and linear schedules only.",
    )
    report.unknown(
        "attack_gate.unexecuted_external_attacks",
        "DELETE/DERIVE/RECOMPUTE/EXTERNALIZE/REALIZE/COGNITION/TCB require realizations or external systems not supplied by the seed.",
    )


def main() -> int:
    report = Report()
    try:
        with open(SEED_PATH, "rb") as handle:
            seed_bytes = handle.read()
    except OSError as exc:
        source = {"seed_path": SEED_PATH, "expected_seed_sha256": EXPECTED_SEED_SHA256,
                  "seed_read_error": str(exc), "experiment_sha256": None}
        report.check("source.seed_readable", False, True)
        output = report.output(source)
        print(json.dumps(output, sort_keys=True, indent=2))
        return 1

    actual_seed_hash = sha256(seed_bytes)
    try:
        with open(os.path.abspath(__file__), "rb") as handle:
            experiment_hash = sha256(handle.read())
    except OSError:
        experiment_hash = None
    source = {
        "seed_path": SEED_PATH,
        "expected_seed_sha256": EXPECTED_SEED_SHA256,
        "actual_seed_sha256": actual_seed_hash,
        "experiment_path": os.path.abspath(__file__),
        "experiment_sha256": experiment_hash,
    }
    if not report.check("source.seed_sha256", actual_seed_hash, EXPECTED_SEED_SHA256):
        output = report.output(source)
        print(json.dumps(output, sort_keys=True, indent=2))
        return 1

    try:
        seed_text = seed_bytes.decode("utf-8")
    except UnicodeDecodeError:
        report.check("source.seed_utf8", False, True)
        output = report.output(source)
        print(json.dumps(output, sort_keys=True, indent=2))
        return 1

    parsed = parse_seed_tables(seed_text)
    report.check("parse.alphabet", parsed["alphabet"],
                 [(i, alias, REQUEST_BYTES[alias]) for i, alias in enumerate(ALIASES)])
    report.check("parse.viewer_channels", parsed["viewers"], {
        "CLIENT": ("C", "R", "L"), "CAPTURE": ("A",),
        "PUBLIC": ("C", "R", "A", "L"), "SELECTOR": ("F",),
    })
    report.check("parse.crossing_tags", parsed["crossing_tags"], (
        (1, "C frame"), (2, "typed C:FIN"), (3, "R frame"), (4, "R:STOPPED newline"),
        (5, "A frame"), (6, "L:DOWN"), (7, "L:READY"), (8, "F frame"),
    ))
    report.check("parse.Must_vocabulary_order", parsed["must_numbers"], tuple(range(1, 11)))
    report.assert_true("parse.normative_application_scheduler_branch_terminal_fragments", all(parsed["required_fragments_present"]),
                       presence=list(parsed["required_fragments_present"]))

    clean, classes = clean_corpus(report)
    clean_separator_and_signatures(report, clean, classes)
    linear_schedule_checks(report, [item[2] for item in clean])
    conditions, lifts = enumerate_recovery_prefixes(report, clean)
    condition_counts(report, conditions)
    quotient_checks(report, conditions, lifts)
    negative_controls(report, conditions)
    codec_ambiguities(report)

    report.findings["semantic_conclusion"] = {
        "literal_section_7_3": "Distinct recovery cut kinds are not comparable.",
        "predictions_7_8": "The advertised 139/315 quotients and 315-class histogram require an unstated relaxation of cut-kind comparability.",
        "section_11_4": "T_PRE_A and T_POST_A have equal suffix behavior at fixed r,d but cannot merge under literal Section 7.3.",
    }
    output = report.output(source)
    print(json.dumps(output, sort_keys=True, indent=2))
    return 1 if output["summary"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
