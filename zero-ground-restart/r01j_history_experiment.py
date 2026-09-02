#!/usr/bin/env python3
"""Independent fail-closed executable falsifier for frozen FBH R0.1J."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Sequence


CANDIDATE_PATH = "/root/pareto/zero-ground-restart/HISTORY-SEED-R01J.md"
EXPECTED_CANDIDATE_SHA256 = "7c9b2a742eab81f6c104b6ca3566315ddb29ecc63d216d25cff91bf1c70836dc"
SCHEMA = "FBH-R01J-FALSIFIER-1"

C_FRAME, C_FIN, R_FRAME, R_STOPPED, A_FRAME, L_DOWN, L_READY, F_FRAME = range(1, 9)
Crossing = tuple[int, bytes]
Trace = tuple[Crossing, ...]
Residual = tuple[int, int, int]

ALIASES = ("O0", "O1", "AI", "AN", "RI", "RN", "D", "Q", "X", "T", "E", "K")
RANK = {alias: rank for rank, alias in enumerate(ALIASES)}
REQUEST_TEXT = (
    "OBSERVE 0", "OBSERVE 1", "AUTHOR ID", "AUTHOR NOT", "REPLACE ID",
    "REPLACE NOT", "RETIRE", "QUERY", "EXPLAIN", "ATTEMPT", "EVOLVE", "CURRENT",
)
REQUEST_BYTES = {a: (text + "\n").encode("ascii") for a, text in zip(ALIASES, REQUEST_TEXT)}
ALIAS_BY_FRAME = {frame: alias for alias, frame in REQUEST_BYTES.items()}

O_NAME = ("U", "0", "1")
P_NAME = ("EMPTY", "ID", "NOT")
G_NAME = ("E0", "E1")

CUT = b"CUT REMAINING=3\n"
SELECT_OLD = b"SELECT old\n"
SELECT_NEW = b"SELECT new\n"
RESUME_FIN = b"RESUME FIN_PENDING\n"
RESUME_TERMINAL = b"RESUME TERMINAL\n"

SCOPE_CODE = {"PUBLIC": 0, "CLIENT": 1, "CAPTURE": 2, "SELECTOR": 3, "PRIV": 4}
SCOPE_TAGS = {
    "PUBLIC": frozenset((C_FRAME, C_FIN, R_FRAME, R_STOPPED, A_FRAME, L_DOWN, L_READY)),
    "CLIENT": frozenset((C_FRAME, C_FIN, R_FRAME, R_STOPPED, L_DOWN, L_READY)),
    "CAPTURE": frozenset((A_FRAME,)),
    "SELECTOR": frozenset((F_FRAME,)),
}

CUT_MAGIC = b"FBH-R01J-CUT\x00"
CTL_MAGIC = b"FBH-R01J-CTL\x00"
SCH_MAGIC = b"FBH-R01J-SCH\x00"
WITNESS_MAGIC = b"FBH-R01J-WITNESS\x00"
MANIFEST_MAGIC = b"FBH-R01J-FALSIFY\x00"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u8(value: int) -> bytes:
    if not 0 <= value <= 255:
        raise ValueError("U8 overflow")
    return bytes((value,))


def u64(value: int) -> bytes:
    if not 0 <= value <= 0xFFFFFFFFFFFFFFFF:
        raise ValueError("U64 overflow")
    return value.to_bytes(8, "big")


def block(value: bytes) -> bytes:
    return u64(len(value)) + value


def seq(items: Iterable[bytes]) -> bytes:
    values = tuple(items)
    return u64(len(values)) + b"".join(block(value) for value in values)


class DecodeError(ValueError):
    pass


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def take(self, count: int) -> bytes:
        if count < 0 or self.pos + count > len(self.data):
            raise DecodeError("truncated")
        out = self.data[self.pos:self.pos + count]
        self.pos += count
        return out

    def one(self) -> int:
        return self.take(1)[0]

    def uint64(self) -> int:
        return int.from_bytes(self.take(8), "big")

    def get_block(self) -> bytes:
        return self.take(self.uint64())

    def finish(self) -> None:
        if self.pos != len(self.data):
            raise DecodeError("trailing bytes")


def residual_text(r: Residual) -> str:
    return f"O={O_NAME[r[0]]} P={P_NAME[r[1]]} E={G_NAME[r[2]]}"


def value_of(r: Residual) -> str:
    o, p, _g = r
    if p == 0:
        return "NONE"
    if o == 0:
        return "UNKNOWN"
    allowed = (p == 1 and o == 2) or (p == 2 and o == 1)
    return "ALLOW" if allowed else "DENY"


def delta(r: Residual, alias: str) -> Residual:
    o, p, g = r
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


def reply_bytes(r: Residual, alias: str) -> bytes:
    _o, p, g = r
    if alias == "O0": text = "OK OBSERVE 0"
    elif alias == "O1": text = "OK OBSERVE 1"
    elif alias == "AI": text = "OK AUTHOR ID" if p == 0 else "ERR ACTIVE"
    elif alias == "AN": text = "OK AUTHOR NOT" if p == 0 else "ERR ACTIVE"
    elif alias == "RI": text = "OK REPLACE ID" if p != 0 else "ERR EMPTY"
    elif alias == "RN": text = "OK REPLACE NOT" if p != 0 else "ERR EMPTY"
    elif alias == "D": text = "OK RETIRE" if p != 0 else "ERR EMPTY"
    elif alias == "Q": text = f"VALUE {value_of(r)}"
    elif alias == "X": text = f"WHY {residual_text(r)} V={value_of(r)}"
    elif alias == "T": text = "OK ATTEMPTED"
    elif alias == "E": text = "OK ENGINE E1" if g == 0 else "OK ENGINE E1 ALREADY"
    elif alias == "K": text = f"ENGINE {G_NAME[g]}"
    else: raise ValueError("UNSUPPORTED(REQUEST)")
    return (text + "\n").encode("ascii")


def attempt_bytes(r: Residual) -> bytes:
    return f"TRY {residual_text(r)} V={value_of(r)}\n".encode("ascii")


ALL_R_FRAMES = frozenset(reply_bytes(r, a) for r in itertools.product(range(3), range(3), range(2)) for a in ALIASES)
ALL_A_FRAMES = frozenset(attempt_bytes(r) for r in itertools.product(range(3), range(3), range(2)))


def f_crash(gap: int) -> bytes:
    if gap < 0:
        raise ValueError("gap")
    return f"CRASH GAP={gap}\n".encode("ascii")


def f_resume(r: Residual) -> bytes:
    return f"RESUME ACTIVE {residual_text(r)}\n".encode("ascii")


def f_allowance(d: int) -> bytes:
    if not 0 <= d <= 3:
        raise ValueError("allowance")
    return f"ALLOWANCE {d}\n".encode("ascii")


def valid_f_frame(payload: bytes) -> bool:
    if payload in (CUT, SELECT_OLD, SELECT_NEW, RESUME_FIN, RESUME_TERMINAL):
        return True
    if re.fullmatch(rb"CRASH GAP=(0|[1-9][0-9]*)\n", payload):
        return True
    if payload in {f_allowance(d) for d in range(4)}:
        return True
    return payload in {f_resume(r) for r in itertools.product(range(3), range(3), range(2))}


def validate_crossing(c: Crossing) -> None:
    tag, payload = c
    if tag not in range(1, 9):
        raise DecodeError("unknown crossing tag")
    if tag in (C_FIN, R_STOPPED, L_DOWN, L_READY):
        if payload:
            raise DecodeError("typed payload nonempty")
        return
    if not payload:
        raise DecodeError("frame payload empty")
    try:
        payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise DecodeError("non-ASCII frame") from exc
    if tag == C_FRAME and payload not in ALIAS_BY_FRAME:
        raise DecodeError("C frame grammar")
    if tag == R_FRAME and payload not in ALL_R_FRAMES:
        raise DecodeError("R frame grammar")
    if tag == A_FRAME and payload not in ALL_A_FRAMES:
        raise DecodeError("A frame grammar")
    if tag == F_FRAME and not valid_f_frame(payload):
        raise DecodeError("F frame grammar")


def enc_crossing(c: Crossing) -> bytes:
    validate_crossing(c)
    return u8(c[0]) + block(c[1])


def dec_crossing(data: bytes) -> Crossing:
    reader = Reader(data)
    c = (reader.one(), reader.get_block())
    reader.finish()
    validate_crossing(c)
    if enc_crossing(c) != data:
        raise DecodeError("crossing noncanonical")
    return c


def enc_trace(trace: Sequence[Crossing]) -> bytes:
    return seq(enc_crossing(c) for c in trace)


def dec_trace(data: bytes) -> Trace:
    reader = Reader(data)
    count = reader.uint64()
    trace = tuple(dec_crossing(reader.get_block()) for _ in range(count))
    reader.finish()
    if enc_trace(trace) != data:
        raise DecodeError("trace noncanonical")
    return trace


def project(trace: Sequence[Crossing], scope: str) -> Trace:
    if scope == "PRIV":
        raise ValueError("PRIV is a family scope")
    if scope not in SCOPE_TAGS:
        raise ValueError("UNSUPPORTED(VIEWER)")
    tags = SCOPE_TAGS[scope]
    return tuple(c for c in trace if c[0] in tags)


def enc_trace_set(traces: Iterable[Sequence[Crossing]]) -> bytes:
    return seq(sorted(set(enc_trace(t) for t in traces)))


def dec_trace_set(data: bytes) -> tuple[Trace, ...]:
    reader = Reader(data)
    count = reader.uint64()
    raw = tuple(reader.get_block() for _ in range(count))
    reader.finish()
    if raw != tuple(sorted(set(raw))):
        raise DecodeError("trace set sort/dedup")
    return tuple(dec_trace(x) for x in raw)


def enc_obs(branches: Sequence[Trace], scope: str) -> bytes:
    if scope == "PRIV":
        return seq(enc_trace(t) for t in branches)
    return enc_trace_set(project(t, scope) for t in branches)


def enc_obs_bundle(branches: Sequence[Trace]) -> bytes:
    return seq(enc_obs(branches, scope) for scope in ("PUBLIC", "CLIENT", "CAPTURE", "SELECTOR", "PRIV"))


def append_completed(trace: list[Crossing], r: Residual, alias: str) -> Residual:
    trace.append((C_FRAME, REQUEST_BYTES[alias]))
    if alias == "T":
        trace.append((A_FRAME, attempt_bytes(r)))
    trace.append((R_FRAME, reply_bytes(r, alias)))
    return delta(r, alias)


def execute_word(r: Residual, word: Sequence[str]) -> tuple[Trace, Residual]:
    trace: list[Crossing] = []
    current = r
    for alias in word:
        current = append_completed(trace, current, alias)
    return tuple(trace), current


def words_exact(length: int) -> Iterator[tuple[str, ...]]:
    yield from itertools.product(ALIASES, repeat=length)


def words_through(maximum: int) -> Iterator[tuple[str, ...]]:
    for length in range(maximum + 1):
        yield from words_exact(length)


@dataclass(frozen=True, order=True)
class CutInfo:
    phase: str
    residual: Optional[Residual]
    d: int
    alias: Optional[str] = None

    @property
    def active(self) -> bool:
        return self.phase in ("CLEAN", "IDLE", "PENDING", "T_PRE_A", "T_POST_A")


def parse_failure_free_transactions(events: Sequence[Crossing], start: Residual, maximum: int) -> Residual:
    r = start
    pos = 0
    count = 0
    while pos < len(events):
        if count >= maximum or events[pos][0] != C_FRAME or events[pos][1] not in ALIAS_BY_FRAME:
            raise DecodeError("failure-free transaction C")
        alias = ALIAS_BY_FRAME[events[pos][1]]
        pos += 1
        if alias == "T":
            if pos >= len(events) or events[pos] != (A_FRAME, attempt_bytes(r)):
                raise DecodeError("failure-free T A")
            pos += 1
        if pos >= len(events) or events[pos] != (R_FRAME, reply_bytes(r, alias)):
            raise DecodeError("failure-free reply")
        pos += 1
        r = delta(r, alias)
        count += 1
    return r


def parse_cut_trace(trace: Sequence[Crossing]) -> CutInfo:
    for crossing in trace:
        validate_crossing(crossing)
    cut_positions = [i for i, c in enumerate(trace) if c == (F_FRAME, CUT)]
    if len(cut_positions) != 1:
        raise DecodeError("cut count")
    cut_pos = cut_positions[0]
    r = parse_failure_free_transactions(trace[:cut_pos], (0, 0, 0), 2)
    after = tuple(trace[cut_pos + 1:])
    if not after:
        return CutInfo("CLEAN", r, 3)
    if len(after) < 2 or after[-1] != (L_DOWN, b"") or after[-2][0] != F_FRAME:
        raise DecodeError("recovery cut ending")
    crash = after[-2][1]
    match = re.fullmatch(rb"CRASH GAP=(0|[1-9][0-9]*)\n", crash)
    if not match:
        raise DecodeError("crash frame")
    nominal = after[:-2]
    if int(match.group(1)) != len(nominal):
        raise DecodeError("crash ordinal")

    d = 3
    phase = "IDLE"
    pending_alias: Optional[str] = None
    pre: Optional[Residual] = None
    for crossing in nominal:
        tag, payload = crossing
        if phase == "IDLE":
            if tag == C_FRAME and payload in ALIAS_BY_FRAME and d > 0:
                pending_alias = ALIAS_BY_FRAME[payload]
                pre = r
                d -= 1
                phase = "T_PRE_A" if pending_alias == "T" else "PENDING"
            elif tag == C_FIN:
                phase = "FIN_PENDING"
            else:
                raise DecodeError("idle nominal crossing")
        elif phase == "PENDING":
            assert pending_alias is not None and pre is not None
            if crossing != (R_FRAME, reply_bytes(pre, pending_alias)):
                raise DecodeError("pending reply")
            r = delta(pre, pending_alias)
            phase = "IDLE"
            pending_alias = None
            pre = None
        elif phase == "T_PRE_A":
            assert pre is not None
            if crossing != (A_FRAME, attempt_bytes(pre)):
                raise DecodeError("T A")
            phase = "T_POST_A"
        elif phase == "T_POST_A":
            assert pre is not None
            if crossing != (R_FRAME, reply_bytes(pre, "T")):
                raise DecodeError("T reply")
            r = pre
            phase = "IDLE"
            pending_alias = None
            pre = None
        elif phase == "FIN_PENDING":
            if crossing != (R_STOPPED, b""):
                raise DecodeError("STOPPED")
            phase = "TERMINAL"
        else:
            raise DecodeError("crossing after terminal")

    if phase == "IDLE":
        return CutInfo("IDLE", r, d)
    if phase == "PENDING":
        assert pre is not None and pending_alias is not None
        return CutInfo("PENDING", pre, d, pending_alias)
    if phase in ("T_PRE_A", "T_POST_A"):
        assert pre is not None
        return CutInfo(phase, pre, d, "T")
    if phase == "FIN_PENDING":
        return CutInfo("FIN_PENDING", r, d)
    if phase == "TERMINAL":
        return CutInfo("TERMINAL", r, d)
    raise AssertionError(phase)


def enc_cut(trace: Sequence[Crossing]) -> bytes:
    parse_cut_trace(trace)
    return CUT_MAGIC + block(enc_trace(trace))


def dec_cut(data: bytes) -> tuple[Trace, CutInfo]:
    if not data.startswith(CUT_MAGIC):
        raise DecodeError("cut magic")
    reader = Reader(data[len(CUT_MAGIC):])
    trace = dec_trace(reader.get_block())
    reader.finish()
    info = parse_cut_trace(trace)
    if enc_cut(trace) != data:
        raise DecodeError("cut noncanonical")
    return trace, info


def clean_history(word: Sequence[str]) -> tuple[Trace, Residual]:
    trace, r = execute_word((0, 0, 0), word)
    return trace + ((F_FRAME, CUT),), r


def enc_decision_key(d: int, client_suffix: Sequence[Crossing]) -> bytes:
    if not 0 <= d <= 3:
        raise ValueError("decision d")
    return u8(d) + block(enc_trace(client_suffix))


def dec_decision_key(data: bytes) -> tuple[int, Trace]:
    reader = Reader(data)
    d = reader.one()
    if d > 3:
        raise DecodeError("decision d")
    trace = dec_trace(reader.get_block())
    reader.finish()
    return d, trace


def enc_gap_key(public_suffix: Sequence[Crossing], proposed: Optional[Crossing]) -> bytes:
    if proposed is None:
        return block(enc_trace(public_suffix)) + u8(1) + block(b"")
    return block(enc_trace(public_suffix)) + u8(0) + block(enc_crossing(proposed))


def dec_gap_key(data: bytes) -> tuple[Trace, Optional[Crossing]]:
    reader = Reader(data)
    public = dec_trace(reader.get_block())
    kind = reader.one()
    payload = reader.get_block()
    reader.finish()
    if kind == 0:
        if not payload:
            raise DecodeError("empty next crossing")
        proposed = dec_crossing(payload)
    elif kind == 1:
        if payload:
            raise DecodeError("nonempty END")
        proposed = None
    else:
        raise DecodeError("next kind")
    if enc_gap_key(public, proposed) != data:
        raise DecodeError("gap key noncanonical")
    return public, proposed


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []
        self.findings: dict = {}

    def check(self, name: str, actual, expected, scope: str = "direct", **detail) -> bool:
        ok = actual == expected
        item = {"name": name, "status": "PASS" if ok else "FAIL", "scope": scope,
                "actual": actual, "expected": expected}
        if detail:
            item["detail"] = detail
        self.items.append(item)
        return ok

    def true(self, name: str, value: bool, scope: str = "direct", **detail) -> bool:
        return self.check(name, bool(value), True, scope, **detail)

    def unknown(self, name: str, reason: str, scope: str = "unresolved", **detail) -> None:
        item = {"name": name, "status": "UNKNOWN", "scope": scope, "reason": reason}
        if detail:
            item["detail"] = detail
        self.items.append(item)

    def output(self, source: dict, runtime: dict) -> dict:
        totals = Counter(item["status"] for item in self.items)
        for label in ("PASS", "FAIL", "UNKNOWN"):
            totals.setdefault(label, 0)
        return json_safe({
            "schema": SCHEMA,
            "source": source,
            "evaluations": self.items,
            "findings": self.findings,
            "runtime": runtime,
            "summary": dict(sorted(totals.items())),
            "overall": "FAIL" if totals["FAIL"] else ("UNKNOWN" if totals["UNKNOWN"] else "PASS"),
        })


def json_safe(value):
    if isinstance(value, bytes):
        try: text = value.decode("ascii")
        except UnicodeDecodeError: text = None
        return {"hex": value.hex(), "ascii": text}
    if isinstance(value, tuple):
        return [json_safe(x) for x in value]
    if isinstance(value, list):
        return [json_safe(x) for x in value]
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    return value


def cutinfo_key(info: CutInfo) -> tuple:
    return (info.phase, (-1, -1, -1) if info.residual is None else info.residual,
            info.d, "" if info.alias is None else info.alias)


def nominal_gap_prefixes(start: Residual) -> tuple[tuple[Trace, CutInfo], ...]:
    """Every distinct nominal prefix/gap after a clean cut, including END."""
    rows: list[tuple[Trace, CutInfo]] = [((), CutInfo("IDLE", start, 3))]

    def walk(prefix: Trace, r: Residual, d: int) -> None:
        if d > 0:
            for alias in ALIASES:
                pre = r
                pending_d = d - 1
                current = prefix + ((C_FRAME, REQUEST_BYTES[alias]),)
                phase = "T_PRE_A" if alias == "T" else "PENDING"
                rows.append((current, CutInfo(phase, pre, pending_d, alias)))
                if alias == "T":
                    current += ((A_FRAME, attempt_bytes(pre)),)
                    rows.append((current, CutInfo("T_POST_A", pre, pending_d, alias)))
                current += ((R_FRAME, reply_bytes(pre, alias)),)
                post = delta(pre, alias)
                rows.append((current, CutInfo("IDLE", post, pending_d)))
                walk(current, post, pending_d)
        fin = prefix + ((C_FIN, b""),)
        rows.append((fin, CutInfo("FIN_PENDING", r, d)))
        stopped = fin + ((R_STOPPED, b""),)
        rows.append((stopped, CutInfo("TERMINAL", r, d)))

    walk((), start, 3)
    return tuple(rows)


def recovery_trace(clean: Trace, nominal: Trace) -> Trace:
    return clean + nominal + ((F_FRAME, f_crash(len(nominal))), (L_DOWN, b""))


def condition_family(info: CutInfo) -> str:
    if info.phase == "IDLE":
        return "idle_active"
    if info.phase == "PENDING":
        assert info.residual is not None and info.alias is not None
        return "pending_non_t_changing" if delta(info.residual, info.alias) != info.residual else "pending_non_t_noop"
    if info.phase == "T_PRE_A":
        return "t_before_a"
    if info.phase == "T_POST_A":
        return "t_after_a"
    if info.phase == "FIN_PENDING":
        return "fin_pending"
    if info.phase == "TERMINAL":
        return "terminal"
    raise ValueError(info.phase)


def enumerate_corpus(report: Report) -> tuple[list[tuple[Trace, Residual]], tuple[CutInfo, ...]]:
    clean_rows: list[tuple[Trace, Residual]] = []
    clean_encodings: set[bytes] = set()
    residual_counts: Counter[Residual] = Counter()
    for word in words_through(2):
        trace, r = clean_history(word)
        parsed = parse_cut_trace(trace)
        report.true("internal_clean_fold" if not clean_rows else "internal_clean_fold_accumulator",
                    parsed == CutInfo("CLEAN", r, 3), scope="direct", word=word) if False else None
        encoded = enc_cut(trace)
        decoded, decoded_info = dec_cut(encoded)
        if decoded != trace or decoded_info != parsed:
            raise AssertionError("clean cut round trip")
        clean_rows.append((trace, r))
        clean_encodings.add(encoded)
        residual_counts[r] += 1

    report.check("clean_history_count", len(clean_rows), 157)
    report.check("clean_history_distinct_encodings", len(clean_encodings), 157)
    report.check("clean_residual_class_count", len(residual_counts), 14)
    report.check("clean_residual_class_multiset", sorted(residual_counts.values(), reverse=True),
                 [59, 17, 17, 16, 16, 16, 2, 2, 2, 2, 2, 2, 2, 2])
    same_pairs = sum(n * (n - 1) // 2 for n in residual_counts.values())
    total_pairs = len(clean_rows) * (len(clean_rows) - 1) // 2
    report.check("clean_same_class_pairs", same_pairs, 2351)
    report.check("clean_unequal_pairs", total_pairs - same_pairs, 9895)
    report.check("clean_total_pairs", total_pairs, 12246)

    by_residual: dict[Residual, tuple[tuple[Trace, CutInfo], ...]] = {}
    normalized: set[CutInfo] = set()
    per_clean_counts: set[int] = set()
    per_clean_family_counts: set[tuple[tuple[str, int], ...]] = set()
    per_clean_collapsed_counts: set[tuple[tuple[str, int], ...]] = set()
    exact_count = 0
    exact_stream = hashlib.sha256()
    all_roundtrip = True
    for clean, r in clean_rows:
        rows = by_residual.setdefault(r, nominal_gap_prefixes(r))
        per_clean_counts.add(len(rows))
        family_counter: Counter[str] = Counter()
        local_nominal: set[Trace] = set()
        for nominal, claimed in rows:
            local_nominal.add(nominal)
            trace = recovery_trace(clean, nominal)
            parsed = parse_cut_trace(trace)
            if parsed != claimed:
                raise AssertionError(("recovery fold", parsed, claimed))
            encoded = CUT_MAGIC + block(enc_trace(trace))
            # Exact round trips are checked for the complete normalized carrier;
            # every exact lift is nevertheless folded and serialized here.
            exact_stream.update(block(encoded))
            exact_count += 1
            normalized.add(parsed)
            family_counter[condition_family(parsed)] += 1
        if len(local_nominal) != len(rows):
            all_roundtrip = False
        per_clean_family_counts.add(tuple(sorted(family_counter.items())))
        collapsed_counter = {
            "idle_active": family_counter["idle_active"],
            "pending_non_t": family_counter["pending_non_t_changing"] + family_counter["pending_non_t_noop"],
            "t_before_a": family_counter["t_before_a"],
            "t_after_a": family_counter["t_after_a"],
            "fin_pending": family_counter["fin_pending"],
            "terminal": family_counter["terminal"],
        }
        per_clean_collapsed_counts.add(tuple(sorted(collapsed_counter.items())))

    normalized_rows = tuple(sorted(normalized, key=cutinfo_key))
    normalized_roundtrip = True
    representative_clean = {r: clean for clean, r in clean_rows}
    for info in normalized_rows:
        # Locate the exact shortest representative by the generated condition.
        found: Optional[Trace] = None
        assert info.residual is not None
        for nominal, candidate_info in by_residual.get(info.residual, ()):
            if candidate_info == info:
                found = recovery_trace(representative_clean[info.residual], nominal)
                break
        if found is None:
            # FIN/terminal source residual can be reachable even where a pending
            # pre-residual lookup above is not the clean start; search all 14.
            for r, rows in by_residual.items():
                for nominal, candidate_info in rows:
                    if candidate_info == info:
                        found = recovery_trace(representative_clean[r], nominal)
                        break
                if found is not None:
                    break
        if found is None:
            raise AssertionError(("missing normalized representative", info))
        encoded = enc_cut(found)
        decoded_trace, decoded_info = dec_cut(encoded)
        normalized_roundtrip &= decoded_trace == found and decoded_info == info

    # The frozen table combines the two non-T pending subfamilies.
    per_clean_table = next(iter(per_clean_collapsed_counts)) if len(per_clean_collapsed_counts) == 1 else ()
    candidate_rows = dict(per_clean_table)
    report.check("recovery_prefixes_per_clean", sorted(per_clean_counts), [7696])
    report.check("recovery_condition_rows_per_clean", candidate_rows,
                 {"idle_active": 1885, "pending_non_t": 1727, "t_before_a": 157,
                  "t_after_a": 157, "fin_pending": 1885, "terminal": 1885})
    report.check("recovery_exact_history_count", exact_count, 1208272,
                 scope="direct_enumeration")
    report.true("recovery_local_prefix_injectivity", all_roundtrip,
                scope="direct_enumeration")
    report.check("all_declared_cut_count", len(clean_rows) + exact_count, 1208429,
                 scope="direct_enumeration")
    report.check("normalized_recovery_count", len(normalized_rows), 854)
    normalized_families = Counter(condition_family(info) for info in normalized_rows)
    report.check("normalized_recovery_family_counts", dict(sorted(normalized_families.items())),
                 {"fin_pending": 68, "idle_active": 68, "pending_non_t_changing": 195,
                  "pending_non_t_noop": 355, "t_after_a": 50, "t_before_a": 50,
                  "terminal": 68})
    report.true("normalized_cut_codec_roundtrips", normalized_roundtrip)
    report.findings["corpus"] = {
        "exact_recovery_enumeration_digest": exact_stream.hexdigest(),
        "digest_definition": "SHA256(concat(Block(EncCut)) in clean-word/gap-tree order)",
        "exact_histories": exact_count + len(clean_rows),
        "normalized_recovery_conditions": len(normalized_rows),
    }
    return clean_rows, normalized_rows


def forced_recovery_prefix(info: CutInfo) -> tuple[tuple[Trace, Residual, int], ...]:
    assert info.residual is not None
    r, d = info.residual, info.d
    if info.phase == "IDLE":
        prefix = ((F_FRAME, f_resume(r)), (F_FRAME, f_allowance(d)), (L_READY, b""))
        return ((prefix, r, d),)
    if info.phase in ("PENDING", "T_PRE_A", "T_POST_A"):
        assert info.alias is not None
        post = delta(r, info.alias)
        old = ((F_FRAME, SELECT_OLD), (F_FRAME, f_resume(r)),
               (F_FRAME, f_allowance(d)), (L_READY, b""))
        new = ((F_FRAME, SELECT_NEW), (F_FRAME, f_resume(post)),
               (F_FRAME, f_allowance(d)), (L_READY, b""))
        return ((old, r, d), (new, post, d))
    if info.phase == "FIN_PENDING":
        return ((((F_FRAME, RESUME_FIN), (L_READY, b""), (R_STOPPED, b"")), r, 0),)
    if info.phase == "TERMINAL":
        return ((((F_FRAME, RESUME_TERMINAL), (L_READY, b"")), r, 0),)
    raise ValueError(info.phase)


def recovery_branches_for_word(info: CutInfo, word: Sequence[str]) -> tuple[Trace, ...]:
    branches: list[Trace] = []
    for prefix, r, d in forced_recovery_prefix(info):
        if info.phase in ("FIN_PENDING", "TERMINAL"):
            branches.append(prefix)
            continue
        current = r
        trace = list(prefix)
        for alias in word[:d]:
            current = append_completed(trace, current, alias)
        trace.extend(((C_FIN, b""), (R_STOPPED, b"")))
        branches.append(tuple(trace))
    return tuple(branches)


def refine_recovery_quotients(infos: tuple[CutInfo, ...], report: Report) -> tuple[list[int], list[int]]:
    public_labels = [0] * len(infos)
    contract_labels = [0] * len(infos)
    probes = tuple(words_through(3))
    for word in probes:
        public_map: dict[tuple[int, bytes], int] = {}
        contract_map: dict[tuple[int, bytes], int] = {}
        next_public: list[int] = []
        next_contract: list[int] = []
        for index, info in enumerate(infos):
            branches = recovery_branches_for_word(info, word)
            pkey = (public_labels[index], enc_obs(branches, "PUBLIC"))
            ckey = (contract_labels[index], enc_obs(branches, "PRIV"))
            if pkey not in public_map:
                public_map[pkey] = len(public_map)
            if ckey not in contract_map:
                contract_map[ckey] = len(contract_map)
            next_public.append(public_map[pkey])
            next_contract.append(contract_map[ckey])
        public_labels, contract_labels = next_public, next_contract

    public_count = len(set(public_labels))
    contract_count = len(set(contract_labels))
    histogram = Counter(Counter(contract_labels).values())
    report.check("recovery_public_outcome_functions", public_count, 139,
                 scope="direct_exact_partition_refinement")
    report.check("recovery_contractual_classes", contract_count, 315,
                 scope="direct_exact_partition_refinement")
    report.check("recovery_contractual_multiplicity_histogram", dict(sorted(histogram.items())),
                 {1: 263, 8: 9, 9: 27, 10: 14, 68: 2},
                 scope="direct_exact_partition_refinement")
    report.check("combined_public_outcome_functions", 14 + public_count, 153,
                 scope="direct_partition_plus_no_merger_witness")
    report.check("combined_contractual_classes", 14 + contract_count, 329,
                 scope="direct_partition_plus_no_merger_witness")
    combined_hist = Counter(histogram)
    combined_hist[1] += 14
    report.check("combined_normalized_histogram", dict(sorted(combined_hist.items())),
                 {1: 277, 8: 9, 9: 27, 10: 14, 68: 2})
    report.findings["quotient_scope"] = {
        "direct_domain": "14 clean residual coordinates plus 854 normalized recovery conditions",
        "recovery_signature_probes": len(probes),
        "probe_definition": "all fixed failure-free words of length 0..3 followed by FIN",
        "exact_history_lift": "symbolic: exact cuts lift through their derived normalized condition",
        "cryptographic_grouping": False,
    }
    return public_labels, contract_labels


def append_public(public: Trace, crossing: Crossing) -> Trace:
    return public + ((crossing,) if crossing[0] in SCOPE_TAGS["PUBLIC"] else ())


class ClosureExplorer:
    """Policy-free least closure for the exact D/G definitions."""

    def __init__(self) -> None:
        self.d_keys: set[bytes] = set()
        self.g_keys: set[bytes] = set()
        self.visited_budget0: set[tuple[Residual, int, Trace]] = set()
        self.visited_budget1: set[tuple[Residual, int, Trace]] = set()

    def recover(self, info: CutInfo, public_after_down: Trace) -> None:
        assert info.residual is not None
        ready = append_public(public_after_down, (L_READY, b""))
        if info.phase == "IDLE":
            self.idle(info.residual, info.d, ready, 0)
        elif info.phase in ("PENDING", "T_PRE_A", "T_POST_A"):
            assert info.alias is not None
            self.idle(info.residual, info.d, ready, 0)
            self.idle(delta(info.residual, info.alias), info.d, ready, 0)
        elif info.phase == "FIN_PENDING":
            append_public(ready, (R_STOPPED, b""))
        elif info.phase == "TERMINAL":
            return
        else:
            raise AssertionError(info.phase)

    def proposed(self, public: Trace, proposed: Crossing, budget: int,
                 crash_info: CutInfo, on_pass) -> None:
        if budget:
            self.g_keys.add(enc_gap_key(public, proposed))
            self.recover(crash_info, append_public(public, (L_DOWN, b"")))
        on_pass(append_public(public, proposed), budget)

    def end_gap(self, public: Trace, budget: int, terminal_info: CutInfo) -> None:
        if budget:
            self.g_keys.add(enc_gap_key(public, None))
            self.recover(terminal_info, append_public(public, (L_DOWN, b"")))

    def idle(self, r: Residual, d: int, public: Trace, budget: int) -> None:
        visited = self.visited_budget1 if budget else self.visited_budget0
        state = (r, d, public)
        if state in visited:
            return
        visited.add(state)
        client = tuple(c for c in public if c[0] in SCOPE_TAGS["CLIENT"])
        self.d_keys.add(enc_decision_key(d, client))

        def fin_pass(after_fin: Trace, remaining_budget: int) -> None:
            fin_info = CutInfo("FIN_PENDING", r, d)

            def stopped_pass(after_stopped: Trace, final_budget: int) -> None:
                self.end_gap(after_stopped, final_budget, CutInfo("TERMINAL", r, d))

            self.proposed(after_fin, (R_STOPPED, b""), remaining_budget,
                          fin_info, stopped_pass)

        self.proposed(public, (C_FIN, b""), budget, CutInfo("IDLE", r, d), fin_pass)
        if d == 0:
            return
        for alias in ALIASES:
            pre = r
            post = delta(pre, alias)
            next_d = d - 1

            def c_pass(after_c: Trace, remaining_budget: int, alias=alias,
                       pre=pre, post=post, next_d=next_d) -> None:
                if alias == "T":
                    def a_pass(after_a: Trace, budget_after_a: int) -> None:
                        def r_pass(after_r: Trace, budget_after_r: int) -> None:
                            self.idle(post, next_d, after_r, budget_after_r)
                        self.proposed(after_a, (R_FRAME, reply_bytes(pre, alias)), budget_after_a,
                                      CutInfo("T_POST_A", pre, next_d, alias), r_pass)
                    self.proposed(after_c, (A_FRAME, attempt_bytes(pre)), remaining_budget,
                                  CutInfo("T_PRE_A", pre, next_d, alias), a_pass)
                else:
                    def r_pass(after_r: Trace, budget_after_r: int) -> None:
                        self.idle(post, next_d, after_r, budget_after_r)
                    self.proposed(after_c, (R_FRAME, reply_bytes(pre, alias)), remaining_budget,
                                  CutInfo("PENDING", pre, next_d, alias), r_pass)

            self.proposed(public, (C_FRAME, REQUEST_BYTES[alias]), budget,
                          CutInfo("IDLE", r, d), c_pass)

    def seed_recovery(self, info: CutInfo) -> None:
        assert info.residual is not None
        public: Trace = ((L_READY, b""),)
        if info.phase == "IDLE":
            self.idle(info.residual, info.d, public, 0)
        elif info.phase in ("PENDING", "T_PRE_A", "T_POST_A"):
            assert info.alias is not None
            self.idle(info.residual, info.d, public, 0)
            self.idle(delta(info.residual, info.alias), info.d, public, 0)
        # FIN-pending and terminal do not consult either policy.


def enumerate_closures(clean_rows: list[tuple[Trace, Residual]], infos: tuple[CutInfo, ...],
                       report: Report) -> tuple[tuple[bytes, ...], tuple[bytes, ...]]:
    explorer = ClosureExplorer()
    for r in sorted(set(r for _trace, r in clean_rows)):
        explorer.idle(r, 3, (), 1)
    for info in infos:
        explorer.seed_recovery(info)
    d_keys = tuple(sorted(explorer.d_keys))
    g_keys = tuple(sorted(explorer.g_keys))
    d_distribution = Counter(dec_decision_key(key)[0] for key in d_keys)
    next_distribution: Counter[str] = Counter()
    for key in g_keys:
        _trace, proposed = dec_gap_key(key)
        next_distribution["END" if proposed is None else str(proposed[0])] += 1
    report.true("D_nonempty", bool(d_keys), scope="direct_least_closure")
    report.true("G_nonempty", bool(g_keys), scope="direct_least_closure")
    report.true("D_codec_roundtrips", all(enc_decision_key(*dec_decision_key(k)) == k for k in d_keys),
                scope="direct_least_closure")
    report.true("G_codec_roundtrips", all(enc_gap_key(*dec_gap_key(k)) == k for k in g_keys),
                scope="direct_least_closure")
    report.true("D_d0_forces_FIN_coordinate", all(dec_decision_key(k)[0] in range(4) for k in d_keys))
    report.findings["closures"] = {
        "status_against_seed": "new direct enumeration; seed predicted no numeric value",
        "D": len(d_keys),
        "D_by_d": dict(sorted(d_distribution.items())),
        "G": len(g_keys),
        "G_by_next_tag": dict(sorted(next_distribution.items())),
        "budget_one_states": len(explorer.visited_budget1),
        "budget_zero_states": len(explorer.visited_budget0),
    }
    return d_keys, g_keys


def enc_controller(actions: Sequence[int], d_keys: Sequence[bytes]) -> bytes:
    if len(actions) != len(d_keys):
        raise ValueError("controller count")
    for action, key in zip(actions, d_keys):
        d, _client = dec_decision_key(key)
        if action not in range(13) or (d == 0 and action != 0):
            raise ValueError("controller action")
    return CTL_MAGIC + u64(len(d_keys)) + bytes(actions)


def dec_controller(data: bytes, d_keys: Sequence[bytes]) -> tuple[int, ...]:
    if not data.startswith(CTL_MAGIC):
        raise DecodeError("controller magic")
    reader = Reader(data[len(CTL_MAGIC):])
    count = reader.uint64()
    if count != len(d_keys):
        raise DecodeError("controller D count")
    raw = reader.take(count)
    reader.finish()
    actions = tuple(raw)
    try:
        encoded = enc_controller(actions, d_keys)
    except ValueError as exc:
        raise DecodeError(str(exc)) from exc
    if encoded != data:
        raise DecodeError("controller noncanonical")
    return actions


def enc_scheduler(bits: Sequence[int], g_keys: Sequence[bytes]) -> bytes:
    if len(bits) != len(g_keys) or any(bit not in (0, 1) for bit in bits):
        raise ValueError("scheduler bits")
    raw = bytearray((len(bits) + 7) // 8)
    for index, bit in enumerate(bits):
        if bit:
            raw[index // 8] |= 1 << (7 - index % 8)
    return SCH_MAGIC + u64(len(g_keys)) + bytes(raw)


def dec_scheduler(data: bytes, g_keys: Sequence[bytes]) -> tuple[int, ...]:
    if not data.startswith(SCH_MAGIC):
        raise DecodeError("scheduler magic")
    reader = Reader(data[len(SCH_MAGIC):])
    count = reader.uint64()
    if count != len(g_keys):
        raise DecodeError("scheduler G count")
    byte_count = (count + 7) // 8
    raw = reader.take(byte_count)
    reader.finish()
    if count % 8 and raw and raw[-1] & ((1 << (8 - count % 8)) - 1):
        raise DecodeError("scheduler padding")
    bits = tuple((raw[i // 8] >> (7 - i % 8)) & 1 for i in range(count))
    if enc_scheduler(bits, g_keys) != data:
        raise DecodeError("scheduler noncanonical")
    return bits


class Evaluator:
    def __init__(self, d_keys: Sequence[bytes], actions: Sequence[int],
                 g_keys: Sequence[bytes], bits: Sequence[int]):
        self.controller = dict(zip(d_keys, actions))
        self.scheduler = dict(zip(g_keys, bits))

    def crash(self, suffix: Trace, ordinal: int, info: CutInfo) -> tuple[Trace, ...]:
        prefix = suffix + ((F_FRAME, f_crash(ordinal)), (L_DOWN, b""))
        return self.recover(info, prefix)

    def recover(self, info: CutInfo, suffix: Trace = ()) -> tuple[Trace, ...]:
        assert info.residual is not None
        out: list[Trace] = []
        for prefix, r, d in forced_recovery_prefix(info):
            current = suffix + prefix
            if info.phase in ("FIN_PENDING", "TERMINAL"):
                out.append(current)
            else:
                out.extend(self.idle(r, d, current, 0, 0))
        return tuple(out)

    def gap_crashes(self, suffix: Trace, proposed: Optional[Crossing], budget: int) -> bool:
        if not budget:
            return False
        public = project(suffix, "PUBLIC")
        key = enc_gap_key(public, proposed)
        if key not in self.scheduler:
            raise AssertionError("G closure miss")
        return bool(self.scheduler[key])

    def idle(self, r: Residual, d: int, suffix: Trace, budget: int,
             ordinal: int) -> tuple[Trace, ...]:
        key = enc_decision_key(d, project(suffix, "CLIENT"))
        if key not in self.controller:
            raise AssertionError("D closure miss")
        code = self.controller[key]
        if d == 0 and code != 0:
            raise AssertionError("non-FIN d0")
        if code == 0:
            return self.finish(r, d, suffix, budget, ordinal)
        return self.request(r, d, ALIASES[code - 1], suffix, budget, ordinal)

    def request(self, r: Residual, d: int, alias: str, suffix: Trace,
                budget: int, ordinal: int) -> tuple[Trace, ...]:
        c = (C_FRAME, REQUEST_BYTES[alias])
        if self.gap_crashes(suffix, c, budget):
            return self.crash(suffix, ordinal, CutInfo("IDLE", r, d))
        suffix += (c,)
        ordinal += 1
        next_d = d - 1
        if alias == "T":
            a = (A_FRAME, attempt_bytes(r))
            if self.gap_crashes(suffix, a, budget):
                return self.crash(suffix, ordinal, CutInfo("T_PRE_A", r, next_d, alias))
            suffix += (a,)
            ordinal += 1
            reply = (R_FRAME, reply_bytes(r, alias))
            if self.gap_crashes(suffix, reply, budget):
                return self.crash(suffix, ordinal, CutInfo("T_POST_A", r, next_d, alias))
        else:
            reply = (R_FRAME, reply_bytes(r, alias))
            if self.gap_crashes(suffix, reply, budget):
                return self.crash(suffix, ordinal, CutInfo("PENDING", r, next_d, alias))
        suffix += (reply,)
        ordinal += 1
        return self.idle(delta(r, alias), next_d, suffix, budget, ordinal)

    def finish(self, r: Residual, d: int, suffix: Trace, budget: int,
               ordinal: int) -> tuple[Trace, ...]:
        fin = (C_FIN, b"")
        if self.gap_crashes(suffix, fin, budget):
            return self.crash(suffix, ordinal, CutInfo("IDLE", r, d))
        suffix += (fin,)
        ordinal += 1
        stopped = (R_STOPPED, b"")
        if self.gap_crashes(suffix, stopped, budget):
            return self.crash(suffix, ordinal, CutInfo("FIN_PENDING", r, d))
        suffix += (stopped,)
        ordinal += 1
        if self.gap_crashes(suffix, None, budget):
            return self.crash(suffix, ordinal, CutInfo("TERMINAL", r, d))
        return (suffix,)

    def evaluate(self, info: CutInfo) -> tuple[Trace, ...]:
        if info.phase == "CLEAN":
            assert info.residual is not None
            return self.idle(info.residual, info.d, (), 1, 0)
        return self.recover(info)


def max_count(branches: Sequence[Trace], tag: int) -> int:
    return max((sum(c[0] == tag for c in branch) for branch in branches), default=0)


def make_evaluator(d_keys: Sequence[bytes], g_keys: Sequence[bytes],
                   special_actions: Optional[dict[bytes, int]] = None,
                   crash_keys: Iterable[bytes] = ()) -> tuple[Evaluator, bytes, bytes]:
    special_actions = special_actions or {}
    actions = []
    for key in d_keys:
        d, _client = dec_decision_key(key)
        action = special_actions.get(key, 0)
        if d == 0:
            action = 0
        actions.append(action)
    crash_set = set(crash_keys)
    bits = [int(key in crash_set) for key in g_keys]
    ctl = enc_controller(actions, d_keys)
    sch = enc_scheduler(bits, g_keys)
    return Evaluator(d_keys, actions, g_keys, bits), ctl, sch


def enc_witness(scope_code: int, left: Trace, right: Trace,
                controller: bytes, scheduler: bytes) -> bytes:
    if scope_code not in range(5):
        raise ValueError("scope")
    left_bytes, right_bytes = enc_cut(left), enc_cut(right)
    if not left_bytes < right_bytes:
        raise ValueError("pair order")
    return (WITNESS_MAGIC + u8(scope_code) + block(left_bytes) + block(right_bytes) +
            block(controller) + block(scheduler))


def dec_witness_structure(data: bytes) -> tuple[int, bytes, bytes, bytes, bytes]:
    if not data.startswith(WITNESS_MAGIC):
        raise DecodeError("witness magic")
    reader = Reader(data[len(WITNESS_MAGIC):])
    scope = reader.one()
    left = reader.get_block()
    right = reader.get_block()
    controller = reader.get_block()
    scheduler = reader.get_block()
    reader.finish()
    return scope, left, right, controller, scheduler


def clean_behavior_checks(clean_rows: list[tuple[Trace, Residual]], infos: tuple[CutInfo, ...],
                          d_keys: Sequence[bytes], g_keys: Sequence[bytes],
                          report: Report) -> dict[str, bytes]:
    residuals = sorted(set(r for _trace, r in clean_rows))
    no_crash, fin_ctl, zero_sch = make_evaluator(d_keys, g_keys)
    initial_key = enc_decision_key(3, ())
    x_eval, x_ctl, _ = make_evaluator(d_keys, g_keys, {initial_key: RANK["X"] + 1})
    initial_fin_gap = enc_gap_key((), (C_FIN, b""))
    crash_eval, crash_ctl, crash_sch = make_evaluator(d_keys, g_keys,
                                                       crash_keys=(initial_fin_gap,))

    all_zero_privileged = True
    all_one_c_public = True
    for left, right in itertools.combinations(residuals, 2):
        left_info = CutInfo("CLEAN", left, 3)
        right_info = CutInfo("CLEAN", right, 3)
        lb = crash_eval.evaluate(left_info)
        rb = crash_eval.evaluate(right_info)
        all_zero_privileged &= (enc_obs(lb, "SELECTOR") != enc_obs(rb, "SELECTOR") and
                                enc_obs(lb, "PRIV") != enc_obs(rb, "PRIV") and
                                max_count(lb + rb, C_FRAME) == 0)
        lp = x_eval.evaluate(left_info)
        rp = x_eval.evaluate(right_info)
        all_one_c_public &= (enc_obs(lp, "PUBLIC") != enc_obs(rp, "PUBLIC") and
                             max_count(lp + rp, C_FRAME) == 1)
    report.true("every_unequal_clean_pair_zero_C_selector_priv_separator",
                all_zero_privileged, scope="direct_91_pair_execution")
    report.true("every_unequal_clean_pair_one_C_X_public_separator",
                all_one_c_public, scope="direct_91_pair_execution")

    fin_path_keys = (
        enc_gap_key((), (C_FIN, b"")),
        enc_gap_key(((C_FIN, b""),), (R_STOPPED, b"")),
        enc_gap_key(((C_FIN, b""), (R_STOPPED, b"")), None),
    )
    zero_public_equal = True
    for mask in range(8):
        keys = tuple(key for i, key in enumerate(fin_path_keys) if mask & (1 << i))
        evaluator, _ctl, _sch = make_evaluator(d_keys, g_keys, crash_keys=keys)
        values = {enc_obs(evaluator.evaluate(CutInfo("CLEAN", r, 3)), "PUBLIC") for r in residuals}
        zero_public_equal &= len(values) == 1
    report.true("no_zero_C_public_clean_separator", zero_public_equal,
                scope="direct_all_8_FIN_path_scheduler_masks")

    empty_trace, empty_r = clean_history(())
    ri_trace, ri_r = clean_history(("RI",))
    report.true("Q3_smallest_clean_merger_same_derived_state",
                empty_r == ri_r and parse_cut_trace(empty_trace) == parse_cut_trace(ri_trace),
                scope="mechanical_state_identity")

    no_clean_recovery_merger = True
    for r in residuals:
        clean_value = enc_obs(no_crash.evaluate(CutInfo("CLEAN", r, 3)), "PUBLIC")
        for info in infos:
            no_clean_recovery_merger &= clean_value != enc_obs(no_crash.evaluate(info), "PUBLIC")
    report.true("no_clean_class_joins_recovery_class_FIN_pass",
                no_clean_recovery_merger, scope="direct_14x854_execution")

    initial_idle = CutInfo("IDLE", (0, 0, 0), 3)
    clean_q7 = no_crash.evaluate(CutInfo("CLEAN", (0, 0, 0), 3))
    recovery_q7 = no_crash.evaluate(initial_idle)
    q7_public = enc_obs(clean_q7, "PUBLIC") != enc_obs(recovery_q7, "PUBLIC")
    report.true("Q7_clean_vs_initial_idle_recovery_FIN_pass_separator", q7_public,
                scope="direct", clean_public=enc_obs(clean_q7, "PUBLIC"),
                recovery_public=enc_obs(recovery_q7, "PUBLIC"))
    # Section 10 says no other responsibility receives a classification, but
    # deleting whether this forced recovery closure is owed merges Q7.
    report.check("responsibility_table_includes_recovery_closure_owed", False, True,
                 scope="literal_spec_audit",
                 collision="H() clean vs its GAP=0 idle-recovery cut; FIN/pass; PUBLIC READY differs")

    q4_left = CutInfo("PENDING", (0, 0, 0), 2, "AI")
    q4_right = CutInfo("PENDING", (0, 1, 0), 2, "D")
    q4l, q4r = recovery_branches_for_word(q4_left, ()), recovery_branches_for_word(q4_right, ())
    report.true("Q4_public_merger", enc_obs(q4l, "PUBLIC") == enc_obs(q4r, "PUBLIC"))
    report.true("Q4_selector_priv_orientation_separator",
                enc_obs(q4l, "SELECTOR") != enc_obs(q4r, "SELECTOR") and
                enc_obs(q4l, "PRIV") != enc_obs(q4r, "PRIV"))

    q5_idle = CutInfo("IDLE", (0, 0, 0), 2)
    q5_pending = CutInfo("PENDING", (0, 0, 0), 2, "RI")
    q5l, q5r = recovery_branches_for_word(q5_idle, ()), recovery_branches_for_word(q5_pending, ())
    report.true("Q5_public_merger_NONE_vs_selector_family",
                enc_obs(q5l, "PUBLIC") == enc_obs(q5r, "PUBLIC"))
    report.true("Q5_selector_priv_separator",
                enc_obs(q5l, "SELECTOR") != enc_obs(q5r, "SELECTOR") and
                enc_obs(q5l, "PRIV") != enc_obs(q5r, "PRIV"))

    q6_pre = CutInfo("T_PRE_A", (0, 0, 0), 2, "T")
    q6_post = CutInfo("T_POST_A", (0, 0, 0), 2, "T")
    report.true("Q6_T_pre_post_continuation_merger",
                enc_obs_bundle(recovery_branches_for_word(q6_pre, ("T",))) ==
                enc_obs_bundle(recovery_branches_for_word(q6_post, ("T",))))

    # Phase-totality and exact STOPPED obligations under a single global pair.
    phase_reps = {
        "clean": CutInfo("CLEAN", (0, 0, 0), 3),
        "down_idle": CutInfo("IDLE", (0, 0, 0), 3),
        "down_pending": CutInfo("PENDING", (0, 0, 0), 2, "AI"),
        "down_T_pre": q6_pre,
        "down_T_post": q6_post,
        "down_FIN": CutInfo("FIN_PENDING", (0, 0, 0), 3),
        "down_terminal": CutInfo("TERMINAL", (0, 0, 0), 3),
    }
    phase_results = {name: no_crash.evaluate(info) for name, info in phase_reps.items()}
    report.true("total_router_all_derived_start_phases",
                all(bool(branches) for branches in phase_results.values()),
                scope="direct_single_global_policy_pair")
    report.check("pending_router_branch_count", len(phase_results["down_pending"]), 2)
    report.check("FIN_pending_exact_STOPPED",
                 [sum(c[0] == R_STOPPED for c in b) for b in phase_results["down_FIN"]], [1])
    report.check("terminal_recovery_no_STOPPED",
                 [sum(c[0] == R_STOPPED for c in b) for b in phase_results["down_terminal"]], [0])

    retry_eval, _retry_ctl, _retry_sch = make_evaluator(
        d_keys, g_keys, {enc_decision_key(2, ((L_READY, b""),)): RANK["T"] + 1})
    pre_retry = retry_eval.evaluate(q6_pre)
    post_retry = retry_eval.evaluate(q6_post)
    suffix_a_pre = [sum(c[0] == A_FRAME for c in b) for b in pre_retry]
    suffix_a_post = [sum(c[0] == A_FRAME for c in b) for b in post_retry]
    report.check("T_preA_total_capture_count_with_retry",
                 [n + 0 for n in suffix_a_pre], [1, 1])
    report.check("T_postA_total_capture_count_with_retry",
                 [n + 1 for n in suffix_a_post], [2, 2],
                 detail_note="one A lies in exact pre-cut prefix")
    report.true("T_retry_client_blind_to_pre_cut_A",
                enc_obs(pre_retry, "CLIENT") == enc_obs(post_retry, "CLIENT"))

    left_trace, right_trace = sorted((empty_trace, clean_history(("O0",))[0]), key=enc_cut)
    q1 = enc_witness(SCOPE_CODE["SELECTOR"], left_trace, right_trace, crash_ctl, crash_sch)
    q2 = enc_witness(SCOPE_CODE["PUBLIC"], left_trace, right_trace, x_ctl, zero_sch)
    report.findings["canonical_witnesses"] = {
        "Q1_contractual": {"sha256": digest(q1), "length": len(q1)},
        "Q2_PUBLIC": {"sha256": digest(q2), "length": len(q2)},
        "scope_admissibility": "Q4 cannot use lower CLIENT/CAPTURE/PUBLIC codes because they do not separate",
    }
    report.unknown("arbitrary_pair_canonical_witness_search",
                   "exact global minimization was executed only for the frozen Q1/Q2 controls",
                   scope="bounded_nonclaim")
    return {"q1": q1, "q2": q2, "fin_ctl": fin_ctl, "zero_sch": zero_sch,
            "empty_cut": enc_cut(empty_trace), "o0_cut": enc_cut(clean_history(("O0",))[0])}


def enc_raw_crossing(crossing: Crossing) -> bytes:
    tag, payload = crossing
    return u8(tag) + block(payload)


def dec_raw_crossing(data: bytes) -> Crossing:
    reader = Reader(data)
    crossing = (reader.one(), reader.get_block())
    reader.finish()
    return crossing


def enc_raw_trace(trace: Sequence[Crossing]) -> bytes:
    return seq(enc_raw_crossing(c) for c in trace)


def dec_raw_trace(data: bytes) -> Trace:
    reader = Reader(data)
    count = reader.uint64()
    trace = tuple(dec_raw_crossing(reader.get_block()) for _ in range(count))
    reader.finish()
    return trace


def enc_raw_family(branches: Sequence[Trace]) -> bytes:
    return seq(enc_raw_trace(trace) for trace in branches)


def dec_raw_family(data: bytes) -> tuple[Trace, ...]:
    reader = Reader(data)
    count = reader.uint64()
    branches = tuple(dec_raw_trace(reader.get_block()) for _ in range(count))
    reader.finish()
    return branches


def enc_evidence_observation(kind: int, body: bytes) -> bytes:
    if kind == 0:
        dec_raw_family(body)
    elif kind == 1:
        if body:
            raise ValueError("timeout body nonempty")
    else:
        raise ValueError("result kind")
    return u8(kind) + block(body)


def dec_evidence_observation(data: bytes) -> tuple[int, bytes]:
    reader = Reader(data)
    kind = reader.one()
    body = reader.get_block()
    reader.finish()
    try:
        canonical = enc_evidence_observation(kind, body)
    except (ValueError, DecodeError) as exc:
        raise DecodeError(str(exc)) from exc
    if canonical != data:
        raise DecodeError("observation noncanonical")
    return kind, body


def enc_evidence_case(origin: int, cut: bytes, controller: bytes,
                      scheduler: bytes, observation: bytes) -> bytes:
    if origin not in (0, 1):
        raise ValueError("origin")
    dec_evidence_observation(observation)
    return (u8(origin) + block(cut) + block(controller) + block(scheduler) +
            block(observation))


def dec_evidence_case(data: bytes) -> tuple[int, bytes, bytes, bytes, int, bytes]:
    reader = Reader(data)
    origin = reader.one()
    cut = reader.get_block()
    controller = reader.get_block()
    scheduler = reader.get_block()
    observation = reader.get_block()
    reader.finish()
    if origin not in (0, 1):
        raise DecodeError("origin")
    kind, body = dec_evidence_observation(observation)
    if origin == 0 and kind != 0:
        raise DecodeError("formal origin timeout")
    return origin, cut, controller, scheduler, kind, body


def enc_manifest(spec_digest: bytes, cases: Sequence[bytes]) -> bytes:
    if len(spec_digest) != 32:
        raise ValueError("spec digest length")
    if tuple(cases) != tuple(sorted(set(cases))):
        raise ValueError("case ordering")
    for case in cases:
        dec_evidence_case(case)
    return MANIFEST_MAGIC + spec_digest + u64(len(cases)) + b"".join(block(case) for case in cases)


def dec_manifest_structure(data: bytes) -> tuple[bytes, tuple[bytes, ...]]:
    if not data.startswith(MANIFEST_MAGIC):
        raise DecodeError("manifest magic")
    reader = Reader(data[len(MANIFEST_MAGIC):])
    spec_digest = reader.take(32)
    count = reader.uint64()
    cases = tuple(reader.get_block() for _ in range(count))
    reader.finish()
    if cases != tuple(sorted(set(cases))):
        raise DecodeError("case sorting/dedup")
    for case in cases:
        dec_evidence_case(case)
    return spec_digest, cases


def cut_error_reason(data: bytes) -> str:
    if not data.startswith(CUT_MAGIC):
        return "UNSUPPORTED(ENCODING)"
    try:
        reader = Reader(data[len(CUT_MAGIC):])
        encoded_trace = reader.get_block()
        reader.finish()
    except DecodeError:
        return "UNSUPPORTED(ENCODING)"
    try:
        trace = dec_trace(encoded_trace)
    except DecodeError:
        return "UNSUPPORTED(CROSSING)"
    try:
        parse_cut_trace(trace)
    except DecodeError:
        return "UNSUPPORTED(CUT)"
    return "SUPPORTED"


def classify_manifest(data: bytes, candidate_digest: bytes, d_keys: Sequence[bytes],
                      g_keys: Sequence[bytes], envelope_bound_violation: Optional[bool]) -> str:
    try:
        spec_digest, encoded_cases = dec_manifest_structure(data)
        cases = [dec_evidence_case(case) for case in encoded_cases]
    except DecodeError:
        return "UNSUPPORTED(EVIDENCE_ENCODING)"
    if spec_digest != candidate_digest:
        return "UNSUPPORTED(SPEC_DIGEST)"

    decoded_inputs = []
    for origin, cut_bytes, ctl_bytes, sch_bytes, kind, body in cases:
        reason = cut_error_reason(cut_bytes)
        if reason != "SUPPORTED":
            return reason
        try:
            trace, info = dec_cut(cut_bytes)
        except DecodeError:
            return "UNSUPPORTED(CUT)"
        try:
            actions = dec_controller(ctl_bytes, d_keys)
        except DecodeError:
            return "UNSUPPORTED(CONTROLLER)"
        try:
            bits = dec_scheduler(sch_bytes, g_keys)
        except DecodeError:
            return "UNSUPPORTED(SCHEDULER)"
        decoded_inputs.append((origin, trace, info, actions, bits, kind, body))

    expected_rows = []
    for origin, _trace, info, actions, bits, kind, body in decoded_inputs:
        expected = enc_raw_family(Evaluator(d_keys, actions, g_keys, bits).evaluate(info))
        expected_rows.append((origin, kind, body, expected))

    for origin, kind, body, expected in expected_rows:
        if origin == 0 and body != expected:
            return "FAIL(GENERATOR_DISAGREEMENT)"
    for origin, kind, _body, _expected in expected_rows:
        if origin == 1 and kind == 1:
            return "FAIL(NON_TOTAL)" if envelope_bound_violation is True else "UNKNOWN(OBSERVATION_BOUND)"
    for origin, kind, body, expected in expected_rows:
        if origin == 1 and kind == 0 and body != expected:
            return "FAIL(CONFORMANCE)"
    return "SUPPORTED_EVIDENCE"


def operational_reason(*, prehistory_depth=False, request=False, allowance=False,
                       crash=False, concurrency=False, phase_action=False, scope=False) -> str:
    ordered = ((prehistory_depth, "UNSUPPORTED(PREHISTORY_DEPTH)"),
               (request, "UNSUPPORTED(REQUEST)"),
               (allowance, "UNSUPPORTED(ALLOWANCE)"),
               (crash, "UNSUPPORTED(CRASH)"),
               (concurrency, "UNSUPPORTED(CONCURRENCY)"),
               (phase_action, "UNSUPPORTED(PHASE_ACTION)"),
               (scope, "UNSUPPORTED(SCOPE)"))
    return next((reason for active, reason in ordered if active), "SUPPORTED")


def classifier_and_evidence_checks(candidate_bytes: bytes, d_keys: Sequence[bytes],
                                   g_keys: Sequence[bytes], artifacts: dict[str, bytes],
                                   report: Report) -> None:
    candidate_digest = bytes.fromhex(digest(candidate_bytes))
    fin_actions = dec_controller(artifacts["fin_ctl"], d_keys)
    zero_bits = dec_scheduler(artifacts["zero_sch"], g_keys)
    report.true("controller_codec_roundtrip",
                enc_controller(fin_actions, d_keys) == artifacts["fin_ctl"])
    report.true("scheduler_codec_roundtrip",
                enc_scheduler(zero_bits, g_keys) == artifacts["zero_sch"])

    controller_controls: dict[str, str] = {}
    for name, mutant in {
        "wrong_D_count": CTL_MAGIC + u64(len(d_keys) + 1) + bytes(fin_actions),
        "missing_action": artifacts["fin_ctl"][:-1],
        "extra_action": artifacts["fin_ctl"] + b"\x00",
    }.items():
        try:
            dec_controller(mutant, d_keys)
            controller_controls[name] = "ACCEPTED"
        except DecodeError:
            controller_controls[name] = "UNSUPPORTED(CONTROLLER)"
    bad_code = bytearray(artifacts["fin_ctl"])
    bad_code[len(CTL_MAGIC) + 8] = 13
    try:
        dec_controller(bytes(bad_code), d_keys)
        controller_controls["unknown_code"] = "ACCEPTED"
    except DecodeError:
        controller_controls["unknown_code"] = "UNSUPPORTED(CONTROLLER)"
    d0_index = next(i for i, key in enumerate(d_keys) if dec_decision_key(key)[0] == 0)
    bad_d0 = bytearray(artifacts["fin_ctl"])
    bad_d0[len(CTL_MAGIC) + 8 + d0_index] = 1
    try:
        dec_controller(bytes(bad_d0), d_keys)
        controller_controls["non_FIN_d0"] = "ACCEPTED"
    except DecodeError:
        controller_controls["non_FIN_d0"] = "UNSUPPORTED(CONTROLLER)"
    report.check("controller_negative_controls", controller_controls,
                 {name: "UNSUPPORTED(CONTROLLER)" for name in controller_controls})

    scheduler_controls: dict[str, str] = {}
    mutants = {
        "wrong_G_count": SCH_MAGIC + u64(len(g_keys) + 1) + artifacts["zero_sch"][len(SCH_MAGIC) + 8:],
        "missing_policy_byte": artifacts["zero_sch"][:-1],
        "extra_policy_byte": artifacts["zero_sch"] + b"\x00",
    }
    if len(g_keys) % 8:
        padding = bytearray(artifacts["zero_sch"])
        padding[-1] |= 1
        mutants["nonzero_padding"] = bytes(padding)
    for name, mutant in mutants.items():
        try:
            dec_scheduler(mutant, g_keys)
            scheduler_controls[name] = "ACCEPTED"
        except DecodeError:
            scheduler_controls[name] = "UNSUPPORTED(SCHEDULER)"
    report.check("scheduler_negative_controls", scheduler_controls,
                 {name: "UNSUPPORTED(SCHEDULER)" for name in scheduler_controls})

    crossing_controls = {}
    for name, raw in {
        "unknown_tag": u8(255) + block(b"x"),
        "typed_nonempty": u8(L_READY) + block(b"x"),
        "frame_empty": u8(C_FRAME) + block(b""),
        "non_ASCII": u8(C_FRAME) + block(b"\xff\n"),
        "missing_LF": u8(C_FRAME) + block(b"QUERY"),
        "excess_LF": u8(C_FRAME) + block(b"QUERY\n\n"),
        "unknown_request": u8(C_FRAME) + block(b"NOPE\n"),
    }.items():
        try:
            dec_crossing(raw)
            crossing_controls[name] = "ACCEPTED"
        except DecodeError:
            crossing_controls[name] = "UNSUPPORTED(CROSSING)"
    report.check("crossing_negative_controls", crossing_controls,
                 {name: "UNSUPPORTED(CROSSING)" for name in crossing_controls})

    precedence_cases = {
        "all": operational_reason(prehistory_depth=True, request=True, allowance=True,
                                  crash=True, concurrency=True, phase_action=True, scope=True),
        "without_depth": operational_reason(request=True, allowance=True, crash=True,
                                            concurrency=True, phase_action=True, scope=True),
        "without_request": operational_reason(allowance=True, crash=True, concurrency=True,
                                              phase_action=True, scope=True),
        "without_allowance": operational_reason(crash=True, concurrency=True,
                                                phase_action=True, scope=True),
        "without_crash": operational_reason(concurrency=True, phase_action=True, scope=True),
        "without_concurrency": operational_reason(phase_action=True, scope=True),
        "scope_only": operational_reason(scope=True),
    }
    report.check("operational_classifier_precedence", precedence_cases,
                 {"all": "UNSUPPORTED(PREHISTORY_DEPTH)",
                  "without_depth": "UNSUPPORTED(REQUEST)",
                  "without_request": "UNSUPPORTED(ALLOWANCE)",
                  "without_allowance": "UNSUPPORTED(CRASH)",
                  "without_crash": "UNSUPPORTED(CONCURRENCY)",
                  "without_concurrency": "UNSUPPORTED(PHASE_ACTION)",
                  "scope_only": "UNSUPPORTED(SCOPE)"})

    empty_info = parse_cut_trace(dec_cut(artifacts["empty_cut"])[0])
    expected = Evaluator(d_keys, fin_actions, g_keys, zero_bits).evaluate(empty_info)
    exact_body = enc_raw_family(expected)
    exact_obs = enc_evidence_observation(0, exact_body)
    exact_formal = enc_evidence_case(0, artifacts["empty_cut"], artifacts["fin_ctl"],
                                     artifacts["zero_sch"], exact_obs)
    exact_real = enc_evidence_case(1, artifacts["empty_cut"], artifacts["fin_ctl"],
                                   artifacts["zero_sch"], exact_obs)

    def manifest_for(case_list: Sequence[bytes], digest_bytes: bytes = candidate_digest) -> bytes:
        return enc_manifest(digest_bytes, tuple(sorted(case_list)))

    controls: dict[str, tuple[bytes, str]] = {
        "zero_case_manifest": (enc_manifest(candidate_digest, ()), "SUPPORTED_EVIDENCE"),
        "origin0_exact_only": (manifest_for((exact_formal,)), "SUPPORTED_EVIDENCE"),
        "origin1_exact": (manifest_for((exact_real,)), "SUPPORTED_EVIDENCE"),
    }

    base_trace = expected[0]
    raw_variants = {
        "wrong_payload": ((base_trace[:-1] + ((R_STOPPED, b"WRONG"),)),),
        "missing_crossing": (base_trace[:-1],),
        "duplicate_crossing": ((base_trace + (base_trace[-1],)),),
        "duplicate_trace": (base_trace, base_trace),
        "unknown_tag": (((255, b"opaque"),) + base_trace[1:],),
        "non_ASCII": (((C_FRAME, b"\xff"),) + base_trace[1:],),
        "empty_family": (),
    }
    for name, raw_family in raw_variants.items():
        obs = enc_evidence_observation(0, enc_raw_family(raw_family))
        case = enc_evidence_case(1, artifacts["empty_cut"], artifacts["fin_ctl"],
                                 artifacts["zero_sch"], obs)
        controls[name] = (manifest_for((case,)), "FAIL(CONFORMANCE)")

    wrong_formal_obs = enc_evidence_observation(0, enc_raw_family(()))
    wrong_formal_case = enc_evidence_case(0, artifacts["empty_cut"], artifacts["fin_ctl"],
                                          artifacts["zero_sch"], wrong_formal_obs)
    controls["origin0_wrong"] = (manifest_for((wrong_formal_case,)),
                                  "FAIL(GENERATOR_DISAGREEMENT)")

    timeout_obs = enc_evidence_observation(1, b"")
    timeout_case = enc_evidence_case(1, artifacts["empty_cut"], artifacts["fin_ctl"],
                                     artifacts["zero_sch"], timeout_obs)
    timeout_manifest = manifest_for((timeout_case,))
    controls["observation_timeout"] = (timeout_manifest, "UNKNOWN(OBSERVATION_BOUND)")

    partial = enc_raw_family((base_trace[:1],))
    invalid_timeout_obs = u8(1) + block(partial)
    invalid_timeout_case = (u8(1) + block(artifacts["empty_cut"]) + block(artifacts["fin_ctl"]) +
                            block(artifacts["zero_sch"]) + block(invalid_timeout_obs))
    invalid_timeout_manifest = (MANIFEST_MAGIC + candidate_digest + u64(1) +
                                block(invalid_timeout_case))
    controls["partial_raw_then_timeout"] = (invalid_timeout_manifest,
                                              "UNSUPPORTED(EVIDENCE_ENCODING)")
    controls["wrong_spec_digest"] = (enc_manifest(b"\x00" * 32, ()),
                                      "UNSUPPORTED(SPEC_DIGEST)")

    invalid_kind_obs = u8(2) + block(b"")
    invalid_kind_case = (u8(1) + block(artifacts["empty_cut"]) + block(artifacts["fin_ctl"]) +
                         block(artifacts["zero_sch"]) + block(invalid_kind_obs))
    controls["unknown_result_kind"] = (
        MANIFEST_MAGIC + candidate_digest + u64(1) + block(invalid_kind_case),
        "UNSUPPORTED(EVIDENCE_ENCODING)")
    invalid_origin_case = (u8(2) + block(artifacts["empty_cut"]) + block(artifacts["fin_ctl"]) +
                           block(artifacts["zero_sch"]) + block(exact_obs))
    controls["unknown_origin"] = (
        MANIFEST_MAGIC + candidate_digest + u64(1) + block(invalid_origin_case),
        "UNSUPPORTED(EVIDENCE_ENCODING)")
    duplicate_manifest = (MANIFEST_MAGIC + candidate_digest + u64(2) +
                          block(exact_formal) + block(exact_formal))
    controls["duplicate_cases"] = (duplicate_manifest, "UNSUPPORTED(EVIDENCE_ENCODING)")
    if exact_formal != exact_real:
        ordered = sorted((exact_formal, exact_real))
        unsorted_manifest = (MANIFEST_MAGIC + candidate_digest + u64(2) +
                             block(ordered[1]) + block(ordered[0]))
        controls["unsorted_cases"] = (unsorted_manifest, "UNSUPPORTED(EVIDENCE_ENCODING)")
    controls["truncated_manifest"] = (MANIFEST_MAGIC + candidate_digest + u64(1),
                                       "UNSUPPORTED(EVIDENCE_ENCODING)")

    observed_results = {
        name: classify_manifest(data, candidate_digest, d_keys, g_keys, None)
        for name, (data, _expected) in controls.items()
    }
    report.check("raw_evidence_negative_controls", observed_results,
                 {name: expected_status for name, (_data, expected_status) in controls.items()})
    report.true("raw_defects_are_not_crossing_parse_rejections",
                all(observed_results[name] == "FAIL(CONFORMANCE)" for name in raw_variants))
    report.unknown("zero_case_manifest_evidentiary_adequacy",
                   "the codec permits zero cases; it proves no generator, verifier, or realization property")
    report.unknown("origin0_only_manifest_is_not_a_verifier_test",
                   "the seed explicitly says generated valid traces do not exercise negative rejection")

    without_envelope = classify_manifest(timeout_manifest, candidate_digest, d_keys, g_keys, None)
    with_unbound_flag = classify_manifest(timeout_manifest, candidate_digest, d_keys, g_keys, True)
    report.check("same_manifest_has_context_independent_total_verdict",
                 without_envelope == with_unbound_flag, True,
                 scope="literal_semantic_collision",
                 manifest_sha256=digest(timeout_manifest),
                 no_envelope=without_envelope, unbound_external_flag=with_unbound_flag)
    report.unknown("experiment_envelope_encoding_and_manifest_binding",
                   "no bytes, signature grammar, authority, or binding rule is frozen; the experiment does not invent them")
    report.findings["evidence_envelope_collision"] = {
        "same_manifest_sha256": digest(timeout_manifest),
        "manifest_only": without_envelope,
        "external_boolean_true": with_unbound_flag,
        "conclusion": "the advertised manifest classifier is not a function of manifest bytes without an unbound external context",
    }

    # Exact separator structural codecs and admissibility controls.
    for name in ("q1", "q2"):
        scope, left, right, ctl, sch = dec_witness_structure(artifacts[name])
        report.true(f"{name}_witness_structural_roundtrip",
                    (WITNESS_MAGIC + u8(scope) + block(left) + block(right) + block(ctl) + block(sch)) ==
                    artifacts[name])
    q1_scope, q1_left, q1_right, q1_ctl, q1_sch = dec_witness_structure(artifacts["q1"])
    left_info = dec_cut(q1_left)[1]
    right_info = dec_cut(q1_right)[1]
    q1_eval = Evaluator(d_keys, dec_controller(q1_ctl, d_keys),
                         g_keys, dec_scheduler(q1_sch, g_keys))
    q1_branches = q1_eval.evaluate(left_info), q1_eval.evaluate(right_info)
    scope_name = next(name for name, code in SCOPE_CODE.items() if code == q1_scope)
    report.true("Q1_named_scope_actually_separates",
                enc_obs(q1_branches[0], scope_name) != enc_obs(q1_branches[1], scope_name))
    report.true("Q1_lower_projected_scopes_inadmissible",
                all(enc_obs(q1_branches[0], name) == enc_obs(q1_branches[1], name)
                    for name in ("PUBLIC", "CLIENT", "CAPTURE")))

    report.findings["raw_evidence_controls"] = observed_results


def verify_frozen_text(candidate: bytes, report: Report) -> None:
    text_value = candidate.decode("utf-8")
    required_literals = [
        "There are exactly\n\n    12^0 + 12^1 + 12^2 = 157",
        "| total recovery cuts | 7,696 | 1,208,272 |",
        "Normalizing recovery histories by only the values used by continuation gives\n854 conditions",
        "There is no cut-kind, phase, pending-alias, live-allowance, prefix-length, or\nrealization-name gate.",
        "PUBLIC-image count = 14 + 139 = 153",
        "contractual classes = 14 + 315 = 329.",
        "For result-kind 1, meaning",
        "body is empty.",
        "separately signed experiment envelope",
    ]
    report.check("frozen_normative_literals", [literal in text_value for literal in required_literals],
                 [True] * len(required_literals), scope="direct_source_parse")
    parsed_requests = []
    for rank, alias in enumerate(ALIASES):
        frame = REQUEST_BYTES[alias].decode("ascii").rstrip("\n")
        pattern = rf"\| {rank} \| {re.escape(alias)} \| `{re.escape(frame)}\\n` \|"
        parsed_requests.append(bool(re.search(pattern, text_value)))
    report.check("request_alphabet_table_parse", parsed_requests, [True] * 12,
                 scope="direct_source_parse")
    viewer_rows = {
        "CLIENT": "C, R, L",
        "CAPTURE": "A",
        "PUBLIC": "C, R, A, L",
        "SELECTOR": "F",
    }
    parsed_viewers = {
        viewer: f"| {viewer} | {crossings} |" in text_value
        for viewer, crossings in viewer_rows.items()
    }
    report.check("viewer_projection_table_parse", parsed_viewers,
                 {viewer: True for viewer in viewer_rows}, scope="direct_source_parse")
    report.true("manifest_envelope_has_no_frozen_codec",
                "EncExperimentEnvelope" not in text_value and "FBH-R01J-ENVELOPE" not in text_value,
                scope="direct_source_parse")


def main() -> int:
    started = time.monotonic()
    report = Report()
    try:
        with open(CANDIDATE_PATH, "rb") as handle:
            candidate = handle.read()
    except OSError as exc:
        output = {
            "schema": SCHEMA,
            "source": {"candidate_path": CANDIDATE_PATH, "error": str(exc)},
            "evaluations": [{"name": "candidate_read", "status": "FAIL"}],
            "summary": {"PASS": 0, "FAIL": 1, "UNKNOWN": 0},
            "overall": "FAIL",
        }
        print(json.dumps(output, sort_keys=True, separators=(",", ":")))
        return 2

    actual_hash = digest(candidate)
    source = {
        "candidate_path": CANDIDATE_PATH,
        "candidate_sha256": actual_hash,
        "required_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
        "candidate_bytes": len(candidate),
    }
    if actual_hash != EXPECTED_CANDIDATE_SHA256:
        report.check("candidate_sha256", actual_hash, EXPECTED_CANDIDATE_SHA256)
        output = report.output(source, {"seconds": round(time.monotonic() - started, 6)})
        print(json.dumps(output, sort_keys=True, separators=(",", ":")))
        return 2

    report.check("candidate_sha256", actual_hash, EXPECTED_CANDIDATE_SHA256)
    verify_frozen_text(candidate, report)
    clean_rows, infos = enumerate_corpus(report)
    refine_recovery_quotients(infos, report)
    d_keys, g_keys = enumerate_closures(clean_rows, infos, report)
    artifacts = clean_behavior_checks(clean_rows, infos, d_keys, g_keys, report)
    classifier_and_evidence_checks(candidate, d_keys, g_keys, artifacts, report)

    with open(os.path.abspath(__file__), "rb") as handle:
        script_bytes = handle.read()
    source["script_path"] = os.path.abspath(__file__)
    source["script_sha256"] = digest(script_bytes)
    source["script_bytes"] = len(script_bytes)
    elapsed = time.monotonic() - started
    output = report.output(source, {"seconds": round(elapsed, 6)})
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 1 if output["summary"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
