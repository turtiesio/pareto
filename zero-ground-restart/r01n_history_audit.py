#!/usr/bin/env python3
"""Pinned post-freeze falsifier for ZERO GROUND candidate R0.1N.

The candidate's embedded experiment is reproduced, then checked for boundary
correspondence, representation-boundary externalization, codec edges, a
smaller witness corpus, and one alternative injective coding.  This program is
an audit instrument, not a subject, architecture, or physical realization.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import unicodedata
from pathlib import Path


CANDIDATE = "HISTORY-SEED-R01N.md"
CANDIDATE_SHA256 = (
    "10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_code(text: str) -> str:
    marker = "```python\n# BEGIN E-R01N-1"
    start = text.index(marker) + len("```python\n")
    end = text.index("\n```", start)
    return text[start:end] + "\n"


def packed_encode(history, uleb):
    """Pack direction into the low bit of the payload-length header."""

    return b"".join(uleb((len(payload) << 1) | direction) + payload
                    for direction, payload in history)


def packed_decode(data, read_uleb):
    offset = 0
    result = []
    while offset < len(data):
        header, offset = read_uleb(data, offset)
        direction = header & 1
        length = header >> 1
        end = offset + length
        if end > len(data):
            raise ValueError("truncated packed payload")
        result.append((direction, data[offset:end]))
        offset = end
    return tuple(result)


def result(result_id: str, status: str, claim: str, evidence):
    return {
        "id": result_id,
        "status": status,
        "claim": claim,
        "evidence": evidence,
    }


candidate_path = Path(__file__).resolve().parent / CANDIDATE
candidate_bytes = candidate_path.read_bytes()
candidate_hash = sha256(candidate_bytes)
if candidate_hash != CANDIDATE_SHA256:
    raise SystemExit(
        f"candidate hash mismatch: {candidate_hash} != {CANDIDATE_SHA256}"
    )

candidate_text = candidate_bytes.decode("utf-8")
code = extract_code(candidate_text)
code_hash = sha256(code.encode("utf-8"))

namespace = {}
captured_stdout = io.StringIO()
embedded_exception = None
try:
    with contextlib.redirect_stdout(captured_stdout):
        exec(compile(code, f"{CANDIDATE}:E-R01N-1", "exec"), namespace)
except Exception as error:  # pragma: no cover - emitted as evidence
    embedded_exception = f"{type(error).__name__}: {error}"

embedded_stdout = captured_stdout.getvalue().encode("utf-8")
results = [
    result(
        "R01",
        "PASS",
        "The frozen candidate bytes match the declared artifact.",
        {"candidate_sha256": candidate_hash},
    ),
    result(
        "R02",
        "PASS" if embedded_exception is None else "FAIL",
        "The embedded bounded experiment executes without an assertion or exception.",
        {
            "code_sha256": code_hash,
            "stdout_sha256": sha256(embedded_stdout),
            "stdout_bytes": len(embedded_stdout),
            "stdout_lines": len(embedded_stdout.splitlines()),
            "exception": embedded_exception,
        },
    ),
]

if embedded_exception is not None:
    print(json.dumps({"results": results}, sort_keys=True, separators=(",", ":")))
    raise SystemExit(1)

histories = namespace["HISTORIES"]
fresh_histories = namespace["FRESH_HISTORIES"]
futures = namespace["FUTURES"]
encode_full = namespace["encode_full"]
decode_full = namespace["decode_full"]
uleb = namespace["uleb"]
read_uleb = namespace["read_uleb"]

public_encodings = {encode_full(history) for history in histories}
fresh_encodings = {encode_full(history) for history in fresh_histories}
roundtrip_ok = all(decode_full(encode_full(h)) == h for h in histories)
roundtrip_ok &= all(decode_full(encode_full(h)) == h for h in fresh_histories)
results.append(
    result(
        "R03",
        "PASS"
        if roundtrip_ok
        and len(public_encodings) == len(histories)
        and len(fresh_encodings) == len(fresh_histories)
        else "FAIL",
        "P01 is injective and round-trips over the two frozen bounded corpora.",
        {
            "public_histories": len(histories),
            "public_encodings": len(public_encodings),
            "fresh_histories": len(fresh_histories),
            "fresh_encodings": len(fresh_encodings),
            "roundtrip": roundtrip_ok,
        },
    )
)

boundary_lengths = (0, 1, 2, 127, 128, 129, 16383, 16384, 16385)
boundary_cases = []
boundary_ok = True
for length in boundary_lengths:
    payload = b"x" * length
    for direction in (0, 1):
        history = ((direction, payload),)
        encoded = encode_full(history)
        ok = decode_full(encoded) == history
        boundary_ok &= ok
        boundary_cases.append(
            {
                "direction": direction,
                "payload_length": length,
                "uleb_hex": uleb(length).hex(),
                "encoded_length": len(encoded),
                "roundtrip": ok,
            }
        )
results.append(
    result(
        "R04",
        "PASS" if boundary_ok else "FAIL",
        "P01 round-trips selected ULEB tier boundaries.",
        {"cases": boundary_cases},
    )
)

all_bounded_histories = tuple(histories) + tuple(fresh_histories)
packed_roundtrip = all(
    packed_decode(packed_encode(history, uleb), read_uleb) == history
    for history in all_bounded_histories
)
packed_encodings = {packed_encode(history, uleb) for history in histories}
packed_fresh_encodings = {
    packed_encode(history, uleb) for history in fresh_histories
}
p01_total_bytes = sum(len(encode_full(history)) for history in all_bounded_histories)
packed_total_bytes = sum(
    len(packed_encode(history, uleb)) for history in all_bounded_histories
)
never_larger = all(
    len(packed_encode(history, uleb)) <= len(encode_full(history))
    for history in all_bounded_histories
)
strictly_smaller_count = sum(
    len(packed_encode(history, uleb)) < len(encode_full(history))
    for history in all_bounded_histories
)
packed_ok = (
    packed_roundtrip
    and len(packed_encodings) == len(histories)
    and len(packed_fresh_encodings) == len(fresh_histories)
    and never_larger
    and strictly_smaller_count > 0
)
results.append(
    result(
        "R05",
        "PASS" if packed_ok else "FAIL",
        "A direction-in-length coding is another bounded injective candidate and uses no more bytes on every tested history.",
        {
            "public_encodings": len(packed_encodings),
            "fresh_encodings": len(packed_fresh_encodings),
            "roundtrip": packed_roundtrip,
            "never_larger": never_larger,
            "strictly_smaller_histories": strictly_smaller_count,
            "p01_total_bytes": p01_total_bytes,
            "packed_total_bytes": packed_total_bytes,
            "interpretation": "storage counterexample only; corruption detection, cognition, runtime, and TCB prevent a total-system dominance claim",
        },
    )
)

attacks = list(namespace["MUTANTS"])
for position in range(namespace["MAX_HISTORY"]):
    attacks.extend(
        (
            (f"DELETE_EVENT_AT_{position}", namespace["erase_event_at"](position)),
            (
                f"DELETE_DIRECTION_AT_{position}",
                namespace["erase_direction_at"](position),
            ),
            (
                f"DELETE_PAYLOAD_AT_{position}",
                namespace["erase_payload_at"](position),
            ),
        )
    )

witness_union = set()
for _, encoder in attacks:
    collision = namespace["minimized_collisions"](encoder)[0]
    witness_union.update((collision[2], collision[3]))
witness_corpus = tuple(sorted(witness_union, key=namespace["history_rank"]))
witness_coverage = {}
for name, encoder in attacks:
    witness_coverage[name] = bool(
        namespace["minimized_collisions"](
            encoder, histories=witness_corpus, futures=futures
        )
    )

active = ["transcript", "count", "last", "direction_0_count"]
deletion_order = ("count", "last", "direction_0_count", "transcript")
while True:
    deleted = False
    for component in deletion_order:
        if component not in active:
            continue
        trial = [item for item in active if item != component]
        if not namespace["minimized_collisions"](
            namespace["redundant_bundle"](trial),
            histories=witness_corpus,
            futures=futures,
        ):
            active = trial
            deleted = True
            break
    if not deleted:
        break

coverage_ok = all(witness_coverage.values()) and active == ["transcript"]
results.append(
    result(
        "R06",
        "PASS" if coverage_ok else "FAIL",
        "A deterministic union of the frozen minimum pairs reproduces every listed public mutant witness and bundle deletion with 13 histories.",
        {
            "full_public_corpus": len(histories),
            "witness_union_corpus": len(witness_corpus),
            "histories": [namespace["show"](history) for history in witness_corpus],
            "attacks_covered": sum(witness_coverage.values()),
            "attacks_total": len(witness_coverage),
            "bundle_fixed_point": active,
            "minimality": "not proved; 13 is an upper bound and already shows 585 was not necessary for the listed witnesses",
        },
    )
)

h0 = ()
h1 = ((0, b""),)
length_future = next(fn for _, name, fn in futures if name == "LENGTH")
harness_outputs = (length_future(h0), length_future(h1))


def fixed_snapshot_length(history, snapshot):
    return snapshot if snapshot <= len(history) else "REJECTED"


fixed_snapshot_outputs = {
    str(snapshot): (
        fixed_snapshot_length(h0, snapshot),
        fixed_snapshot_length(h1, snapshot),
    )
    for snapshot in (0, 1, 2)
}
same_request_matches = harness_outputs in fixed_snapshot_outputs.values()
results.append(
    result(
        "F01",
        "FAIL" if not same_request_matches else "PASS",
        "The executable LENGTH witness is one common snapshot-bearing C01 continuation.",
        {
            "histories": [namespace["show"](h0), namespace["show"](h1)],
            "harness_outputs": harness_outputs,
            "fixed_snapshot_outputs_before_request_capture": fixed_snapshot_outputs,
            "same_fixed_request_matches": same_request_matches,
            "boundary_capture_timing": "undefined by C01",
            "type": "contract/harness correspondence failure, not a P01 collision",
        },
    )
)

one = ((0, b""),)
two = one + one
concat_equals_one_history = (
    encode_full(one) + encode_full(one) == encode_full(two)
)
results.append(
    result(
        "F02",
        "FAIL" if concat_equals_one_history else "PASS",
        "P01 is a self-delimiting history word without an external container extent.",
        {
            "one_occurrence_hex": encode_full(one).hex(),
            "two_occurrence_hex": encode_full(two).hex(),
            "concatenation_equals_two_occurrences": concat_equals_one_history,
            "type": "externalized representation-boundary responsibility, not an injectivity collision when byte-string extent is supplied",
        },
    )
)

original = encode_full(((0, b""),))
coherently_corrupted = bytes((1,)) + original[1:]
corruption_observation = {
    "original_hex": original.hex(),
    "corrupted_hex": coherently_corrupted.hex(),
    "original_decodes_to": namespace["show"](decode_full(original)),
    "corrupted_decodes_to": namespace["show"](decode_full(coherently_corrupted)),
    "both_valid": True,
}
results.append(
    result(
        "U01",
        "UNKNOWN",
        "Physical corruption is detectable and recoverable.",
        {
            **corruption_observation,
            "reason": "P01 has no retained integrity reference; candidate correctly leaves corruption detection/recovery unspecified",
        },
    )
)

e01_markers = {
    "opcode_table_in_executable": "OPCODE" in code or "opcode" in code,
    "run_request_in_executable": "RUN(" in code,
    "snapshot_parameter_in_make_futures": "snapshot" in code[
        code.index("def make_futures") : code.index("def signature")
    ],
}
results.append(
    result(
        "F03",
        "FAIL",
        "The frozen total contract and bounded experiment execute the declared RUN/view/interpretation/action/explanation behavior.",
        {
            **e01_markers,
            "reason": "E01's normative opcode table and binary grammar are explicitly incomplete; test futures are direct Python projections rather than encoded E01 programs",
            "type": "unsupported required capability, not a P01 collision",
        },
    )
)

unknowns = (
    "complete_history_equivalence_under_exact_captured_request_response_semantics",
    "global_minimum_total_system",
    "independently_committed_hidden_suite",
    "subject_conformance",
    "physical_durability_and_recovery",
    "human_cognition_and_authoring",
    "query_navigation_service_levels",
    "TCB_closure",
    "contract_evolution_and_migration",
    "materially_unlike_realizations",
)
for number, claim in enumerate(unknowns, start=2):
    results.append(
        result(
            f"U{number:02d}",
            "UNKNOWN",
            claim,
            {"reason": "not established by the frozen candidate or this logical falsifier"},
        )
    )

summary = {
    status: sum(item["status"] == status for item in results)
    for status in ("PASS", "FAIL", "UNKNOWN")
}
record = {
    "candidate": CANDIDATE,
    "candidate_sha256": candidate_hash,
    "code_sha256": code_hash,
    "python": sys.version.split()[0],
    "unicode_database": unicodedata.unidata_version,
    "summary": summary,
    "results": results,
    "verdict": "FIRST MILESTONE FAIL / NOT ACHIEVED",
}
print(json.dumps(record, sort_keys=True, separators=(",", ":")))
raise SystemExit(1 if summary["FAIL"] else 0)
