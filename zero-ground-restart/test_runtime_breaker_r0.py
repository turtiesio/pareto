#!/usr/bin/env python3
"""Held-out cross-runtime breaker for the frozen B1/B3 byte contract.

The Rust CLI has no command that accepts one envelope.  This test therefore
uses the CLI for ``inspect`` and compiles a throwaway executable, from stdin,
against the frozen crate's public ``Machine`` API for isolated-envelope
recovery.  It does not add or modify Rust source.

Portable breaker categories are deliberately kept separate from native error
strings.  The frozen observable contract requires the final accept/reject and
accepted semantics; it does not require either runtime to expose a staged
transport/recovery error taxonomy.

This remains one-host, process-level evidence.  It does not test power loss,
torn writes, durable publication, physical media, network isolation, or an
independent implementation of the frozen specification/oracle.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
SUITE_PATH = HERE / "RUNTIME-BREAKER-R0.json"
RUST_ROOT = HERE / "rust-realizer"
EXPECTED_CANONICAL_BYTES = 13_666
EXPECTED_COMMITMENT = "85741dda1ed537ef5225a1514d0947d277f4ee552b5234ea038fb6c8551e2e97"
EXPECTED_ARTIFACT = "b38fc5d3e57fd0117b9ee1fd4c0d0686833115db9ce22dd5950fe6fb41a09339"
EXPECTED_INSPECT = (
    "states=83352 quiescent=10420 classes=82584 refinement_rounds=3 "
    "representative_min=0 representative_max=236 representative_total=14584671\n"
)

ENVELOPE_HEADER = struct.Struct(">4sBB32sI")
U32 = struct.Struct(">I")
TRANSCRIPT_PREAMBLE = b"proof-domain-membership-v1\0"
ORDINAL = "ordinal"
REPRESENTATIVE = "representative"
TAG_TO_CANDIDATE = {1: ORDINAL, 2: REPRESENTATIVE}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _reject_duplicate_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member {key!r}")
        result[key] = value
    return result


def _load_suite() -> dict[str, Any]:
    value = json.loads(
        SUITE_PATH.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_members,
    )
    if not isinstance(value, dict):
        raise TypeError("breaker suite must be a JSON object")
    return value


def _expand_cases(suite: dict[str, Any]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for source in suite["cases"]:
        if "wire_hex" in source:
            item = dict(source)
            item["source_id"] = source["id"]
            expanded.append(item)
            continue
        generator = source["wire_generator"]
        base = bytes.fromhex(suite["fixtures"][generator["base_fixture"]])
        first = generator["lengths"]["first"]
        last = generator["lengths"]["last_inclusive"]
        if not (first == 0 and last == len(base) - 1):
            raise AssertionError("proper-prefix generator does not cover every prefix")
        for length in range(first, last + 1):
            item = {key: value for key, value in source.items() if key != "wire_generator"}
            item.update(
                {
                    "id": f"{source['id']}/prefix-{length:02d}",
                    "source_id": source["id"],
                    "prefix_length": length,
                    "wire_hex": base[:length].hex(),
                }
            )
            expanded.append(item)
    return expanded


def _selected_candidate(case: dict[str, Any]) -> str:
    selected = case.get("selected_candidate")
    if selected is not None:
        return selected
    wire = bytes.fromhex(case["wire_hex"])
    if len(wire) > 5:
        return TAG_TO_CANDIDATE.get(wire[5], ORDINAL)
    return ORDINAL


def _expected_accept(case: dict[str, Any]) -> bool:
    return case["expect"].get("recover") == "accept"


def _normalized_ordinal_rank(envelope_hex: str, artifact: str) -> int:
    data = bytes.fromhex(envelope_hex)
    if len(data) != 45:
        raise AssertionError(f"normalized ordinal envelope has {len(data)} bytes")
    magic, version, tag, digest, length = ENVELOPE_HEADER.unpack(data[:42])
    if (magic, version, tag, digest.hex(), length) != (
        b"ZGPE",
        1,
        1,
        artifact,
        3,
    ):
        raise AssertionError("invalid normalized ordinal envelope")
    return int.from_bytes(data[42:], "big")


def _read_u32(data: bytes, cursor: int) -> tuple[int, int]:
    end = cursor + 4
    if end > len(data):
        raise AssertionError("truncated u32 in Rust transcript")
    return U32.unpack(data[cursor:end])[0], end


def _read_blob(data: bytes, cursor: int) -> tuple[bytes, int]:
    length, cursor = _read_u32(data, cursor)
    end = cursor + length
    if end > len(data):
        raise AssertionError("truncated blob in Rust transcript")
    return data[cursor:end], end


def _read_tag(data: bytes, cursor: int, expected: bytes) -> int:
    end = cursor + len(expected)
    if data[cursor:end] != expected:
        raise AssertionError(
            f"Rust transcript tag mismatch at {cursor}: expected {expected!r}"
        )
    return end


def _read_frame_list(data: bytes, cursor: int, tag: bytes) -> tuple[list[str], int]:
    cursor = _read_tag(data, cursor, tag)
    count, cursor = _read_u32(data, cursor)
    values: list[str] = []
    for _ in range(count):
        cursor = _read_tag(data, cursor, b"V")
        raw, cursor = _read_blob(data, cursor)
        values.append(raw.decode("utf-8"))
    return values, cursor


def _parse_rust_transcript(
    transcript_hex: str, ranks: list[int], artifact: str
) -> dict[int, list[dict[str, Any]]]:
    data = bytes.fromhex(transcript_hex)
    cursor = 0
    cursor = _read_tag(data, cursor, b"ZGTR")
    cursor = _read_tag(data, cursor, bytes((1, 1)))
    digest = data[cursor : cursor + 32]
    cursor += 32
    if digest.hex() != artifact:
        raise AssertionError("Rust transition artifact digest mismatch")
    state_count, cursor = _read_u32(data, cursor)
    operation_count, cursor = _read_u32(data, cursor)
    if state_count != len(ranks) or operation_count != 17:
        raise AssertionError(
            f"Rust transcript counts {(state_count, operation_count)} are invalid"
        )
    cursor = _read_tag(data, cursor, TRANSCRIPT_PREAMBLE)
    operation_order: list[str] = []
    for _ in range(operation_count):
        raw, cursor = _read_blob(data, cursor)
        operation_order.append(raw.decode("utf-8"))

    by_rank: dict[int, list[dict[str, Any]]] = {}
    for expected_rank in ranks:
        transitions: list[dict[str, Any]] = []
        for expected_operation in operation_order:
            cursor = _read_tag(data, cursor, b"S")
            state, cursor = _read_blob(data, cursor)
            if _normalized_ordinal_rank(state.hex(), artifact) != expected_rank:
                raise AssertionError("Rust transcript current-state rank mismatch")
            cursor = _read_tag(data, cursor, b"O")
            operation, cursor = _read_blob(data, cursor)
            operation_text = operation.decode("utf-8")
            if operation_text != expected_operation:
                raise AssertionError("Rust transcript operation-order mismatch")
            cursor = _read_tag(data, cursor, b"M")
            membership, cursor = _read_blob(data, cursor)
            domain_membership = None if membership == b"N" else membership.decode("ascii")
            client, cursor = _read_frame_list(data, cursor, b"C")
            action, cursor = _read_frame_list(data, cursor, b"A")
            cursor = _read_tag(data, cursor, b"N")
            next_envelope, cursor = _read_blob(data, cursor)
            next_hex = next_envelope.hex()
            next_rank = _normalized_ordinal_rank(next_hex, artifact)
            transitions.append(
                {
                    "operation": operation_text,
                    "proof_domain_membership": domain_membership,
                    "client_outputs": client,
                    "action_outputs": action,
                    "next_rank": next_rank,
                    "next_envelope_hex": next_hex,
                }
            )
        by_rank[expected_rank] = transitions
    if cursor != len(data):
        raise AssertionError(f"trailing bytes in Rust transcript: {len(data) - cursor}")
    return by_rank


def _python_transitions(machine: Any, key: Any) -> list[dict[str, Any]]:
    from c0_candidates import OrdinalEncoding
    from c0_oracle import INPUTS
    from c0_process_probe import ORDINAL as PROBE_ORDINAL, serialize_encoding

    operations: list[tuple[str, Any]] = [("resume", machine.resume_step(key))]
    operations.extend((frame.token(), machine.input_step(key, frame)) for frame in INPUTS)
    result: list[dict[str, Any]] = []
    for operation, step in operations:
        next_rank = machine.rank_by_key[step.next_key]
        next_envelope = serialize_encoding(
            PROBE_ORDINAL,
            OrdinalEncoding(machine.specification_digest, next_rank),
        )
        result.append(
            {
                "operation": operation,
                "proof_domain_membership": step.domain_membership,
                "client_outputs": list(step.client),
                "action_outputs": list(step.action),
                "next_rank": next_rank,
                "next_envelope_hex": next_envelope.hex(),
            }
        )
    return result


def _python_worker(payload: dict[str, Any]) -> dict[str, Any]:
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    from c0_candidates import OrdinalCandidate, RepresentativeCandidate
    from c0_process_probe import (
        ORDINAL as PROBE_ORDINAL,
        REPRESENTATIVE as PROBE_REPRESENTATIVE,
        _build_machine,
        decode_envelope,
        deserialize_encoding,
        serialize_encoding,
    )

    machine = _build_machine()
    candidates = {
        PROBE_ORDINAL: OrdinalCandidate(machine),
        PROBE_REPRESENTATIVE: RepresentativeCandidate(machine),
    }
    results: list[dict[str, Any]] = []
    for request in payload["cases"]:
        wire = bytes.fromhex(request["wire_hex"])
        selected = request.get("selected_candidate")
        try:
            actual, _digest, _payload = decode_envelope(
                wire, expected_candidate=selected
            )
        except Exception as error:  # the public decoder defines the rejection boundary
            results.append(
                {
                    "accepted": False,
                    "stage": "transport",
                    "transport": "reject",
                    "error": str(error),
                }
            )
            continue
        try:
            encoding = deserialize_encoding(actual, wire)
            key = candidates[actual].recover(encoding)
        except Exception as error:  # the public candidate defines semantic recovery
            results.append(
                {
                    "accepted": False,
                    "stage": "recover",
                    "transport": "accept",
                    "recover": "reject",
                    "error": str(error),
                }
            )
            continue
        rank = machine.rank_by_key[key]
        canonical = serialize_encoding(actual, encoding)
        results.append(
            {
                "accepted": True,
                "stage": "recover",
                "transport": "accept",
                "recover": "accept",
                "candidate": actual,
                "rank": rank,
                "canonical_hex": canonical.hex(),
                "transitions": _python_transitions(machine, key),
            }
        )
    return {
        "artifact_digest": machine.specification_digest,
        "results": results,
    }


RUST_HELPER = r'''
use std::io::{self, BufRead};
use b1_realizer::{Candidate, Machine};

fn nibble(byte: u8) -> Result<u8, String> {
    match byte {
        b'0'..=b'9' => Ok(byte - b'0'),
        b'a'..=b'f' => Ok(byte - b'a' + 10),
        b'A'..=b'F' => Ok(byte - b'A' + 10),
        _ => Err("invalid hex".to_owned()),
    }
}

fn decode_hex(text: &str) -> Result<Vec<u8>, String> {
    let bytes = text.as_bytes();
    if bytes.len() % 2 != 0 { return Err("odd hex".to_owned()); }
    let mut result = Vec::with_capacity(bytes.len() / 2);
    for pair in bytes.chunks_exact(2) {
        result.push((nibble(pair[0])? << 4) | nibble(pair[1])?);
    }
    Ok(result)
}

fn encode_hex(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut result = String::with_capacity(bytes.len() * 2);
    for &byte in bytes {
        result.push(HEX[(byte >> 4) as usize] as char);
        result.push(HEX[(byte & 15) as usize] as char);
    }
    result
}

fn main() {
    let machine = Machine::build().expect("frozen Rust machine must build");
    let stdin = io::stdin();
    for line in stdin.lock().lines() {
        let line = line.expect("line read");
        let fields: Vec<&str> = line.split('\t').collect();
        match fields.as_slice() {
            ["R", candidate, wire] => {
                let candidate = Candidate::parse(candidate).expect("selected candidate");
                match decode_hex(wire).and_then(|bytes| {
                    machine.recover_envelope(candidate, &bytes)
                        .map(|rank| (rank, machine.envelope(candidate, rank)))
                        .map_err(|error| error.to_string())
                }) {
                    Ok((rank, canonical)) => println!("R\tOK\t{}\t{}", rank, encode_hex(&canonical)),
                    Err(error) => println!("R\tERR\t{}", encode_hex(error.as_bytes())),
                }
            }
            ["T", ranks] => {
                let parsed: Result<Vec<usize>, _> = if ranks.is_empty() {
                    Ok(Vec::new())
                } else {
                    ranks.split(',').map(str::parse::<usize>).collect()
                };
                match parsed {
                    Ok(parsed) => {
                        let mut transcript = Vec::new();
                        match machine.write_transition_transcript(
                            Candidate::Ordinal, &parsed, &mut transcript
                        ) {
                            Ok(_) => println!("T\tOK\t{}", encode_hex(&transcript)),
                            Err(error) => println!("T\tERR\t{}", encode_hex(error.to_string().as_bytes())),
                        }
                    }
                    Err(error) => println!("T\tERR\t{}", encode_hex(error.to_string().as_bytes())),
                }
            }
            _ => println!("P\tERR\t{}", encode_hex(b"invalid helper request")),
        }
    }
}
'''


def _sanitized_environment(specification: dict[str, str]) -> dict[str, str]:
    return {
        "LANG": specification["LANG"],
        "LC_ALL": specification["LC_ALL"],
        "TZ": specification["TZ"],
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _run_python_process(
    cases: list[dict[str, Any]], environment: dict[str, str]
) -> dict[str, Any]:
    requests = [
        {
            "wire_hex": case["wire_hex"],
            **(
                {"selected_candidate": case["selected_candidate"]}
                if "selected_candidate" in case
                else {}
            ),
        }
        for case in cases
    ]
    completed = subprocess.run(
        [sys.executable, "-I", "-S", "-B", str(Path(__file__).resolve()), "--python-worker"],
        input=_canonical_json({"cases": requests}) + b"\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_sanitized_environment(environment),
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "Python worker failed: " + completed.stderr.decode("utf-8", "replace")
        )
    return json.loads(completed.stdout)


def _run_rust_process(
    helper: Path,
    cases: list[dict[str, Any]],
    accepted_ranks: list[int],
    environment: dict[str, str],
    artifact: str,
) -> tuple[list[dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    lines = [
        f"R\t{_selected_candidate(case)}\t{case['wire_hex']}" for case in cases
    ]
    lines.append("T\t" + ",".join(str(rank) for rank in accepted_ranks))
    completed = subprocess.run(
        [str(helper)],
        input=("\n".join(lines) + "\n").encode("ascii"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_sanitized_environment(environment),
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "Rust helper failed: " + completed.stderr.decode("utf-8", "replace")
        )
    output_lines = completed.stdout.decode("ascii").splitlines()
    if len(output_lines) != len(cases) + 1:
        raise AssertionError(
            f"Rust helper returned {len(output_lines)} lines for {len(cases)} cases"
        )
    results: list[dict[str, Any]] = []
    for line in output_lines[:-1]:
        fields = line.split("\t")
        if fields[:2] == ["R", "OK"] and len(fields) == 4:
            results.append(
                {
                    "accepted": True,
                    "rank": int(fields[2]),
                    "canonical_hex": fields[3],
                }
            )
        elif fields[:2] == ["R", "ERR"] and len(fields) == 3:
            results.append(
                {
                    "accepted": False,
                    "error": bytes.fromhex(fields[2]).decode("utf-8"),
                }
            )
        else:
            raise AssertionError(f"invalid Rust helper result: {line!r}")
    transcript_fields = output_lines[-1].split("\t")
    if transcript_fields[:2] != ["T", "OK"] or len(transcript_fields) != 3:
        raise AssertionError(f"invalid Rust transcript result: {output_lines[-1]!r}")
    transitions = _parse_rust_transcript(
        transcript_fields[2], accepted_ranks, artifact
    )
    return results, transitions


def _python_native_category(message: str) -> str:
    mappings = (
        ("truncated envelope header", "truncated_envelope"),
        ("wrong envelope magic", "wrong_magic"),
        ("unsupported envelope version", "unsupported_version"),
        ("unknown candidate tag", "unknown_candidate_tag"),
        ("candidate tag does not match", "candidate_tag_mismatch"),
        ("envelope payload exceeds", "payload_too_large"),
        ("envelope payload length or trailing bytes", "payload_length_or_trailing_invalid"),
        ("ordinal payload must contain", "ordinal_payload_width"),
        ("specification digest mismatch", "specification_digest_mismatch"),
        ("ordinal outside generated quotient", "ordinal_outside_generated_quotient"),
        ("representative is not UTF-8", "representative_not_utf8"),
        ("representative lies outside B1 frame grammar", "representative_outside_b1_grammar"),
        ("representative is not a legal C0 boundary prefix", "representative_not_legal_b1_prefix"),
        ("representative is legal but noncanonical", "representative_legal_but_noncanonical"),
    )
    for fragment, category in mappings:
        if fragment in message:
            return category
    return "unclassified_native_error"


def _rust_native_category(message: str) -> str:
    mappings = (
        ("truncated envelope header", "truncated_envelope"),
        ("wrong envelope magic", "wrong_magic"),
        ("wrong envelope version", "unsupported_version"),
        ("envelope candidate tag", "candidate_tag_mismatch"),
        ("artifact digest mismatch", "specification_digest_mismatch"),
        ("envelope length says", "envelope_length_mismatch"),
        ("ordinal payload length", "ordinal_payload_width"),
        ("ordinal rank", "ordinal_outside_generated_quotient"),
        ("representative is malformed, illegal, or noncanonical", "representative_rejected"),
    )
    for fragment, category in mappings:
        if fragment in message:
            return category
    return "unclassified_native_error"


def _category_projection(result: dict[str, Any], runtime: str) -> dict[str, Any]:
    if result["accepted"]:
        return {
            "accepted": True,
            "rank": result["rank"],
            "canonical_hex": result["canonical_hex"],
            **({"transitions": result["transitions"]} if "transitions" in result else {}),
        }
    categorizer = _python_native_category if runtime == "python" else _rust_native_category
    return {"accepted": False, "category": categorizer(result["error"])}


class RuntimeBreakerR0(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.suite = _load_suite()
        cls.expanded = _expand_cases(cls.suite)
        cls.summary: dict[str, Any] = {
            "schema": "zero-ground-runtime-breaker-first-run-v1",
            "suite_canonical_bytes": EXPECTED_CANONICAL_BYTES,
            "suite_sha256": EXPECTED_COMMITMENT,
            "category_only_mismatches": [],
            "limitations": [
                "Rust exposes combined envelope recovery, not separate transport/recover stages",
                "native free-text errors are not portable breaker categories",
                "temporary harness links the public Rust library because the CLI has no single-envelope recover command",
                "environment probes share one host kernel, CPU, filesystem, Rust stdlib, and Python stdlib",
                "locale availability is not required because byte parsing must not depend on locale",
                "publication, power-loss, torn-write, physical-media, and network-isolation profiles are not tested or credited",
            ],
        }
        cls.temporary = tempfile.TemporaryDirectory(prefix="runtime-breaker-r0-")
        cls.helper = Path(cls.temporary.name) / "rust-runtime-breaker"

        build = subprocess.run(
            ["cargo", "build", "--release", "--locked", "--offline"],
            cwd=RUST_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if build.returncode != 0:
            raise AssertionError(build.stderr.decode("utf-8", "replace"))
        library = RUST_ROOT / "target" / "release" / "libb1_realizer.rlib"
        compile_helper = subprocess.run(
            [
                "rustc",
                "-",
                "--crate-name",
                "runtime_breaker_helper",
                "--edition=2021",
                "-O",
                "--extern",
                f"b1_realizer={library}",
                "-L",
                f"dependency={RUST_ROOT / 'target' / 'release' / 'deps'}",
                "-o",
                str(cls.helper),
            ],
            input=RUST_HELPER.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if compile_helper.returncode != 0:
            raise AssertionError(compile_helper.stderr.decode("utf-8", "replace"))

    @classmethod
    def tearDownClass(cls) -> None:
        print(
            "RUNTIME_BREAKER_R0_FIRST_RUN="
            + _canonical_json(cls.summary).decode("utf-8")
        )
        cls.temporary.cleanup()

    def test_01_committed_object_is_exact(self) -> None:
        raw = SUITE_PATH.read_bytes()
        canonical = _canonical_json(self.suite)
        self.assertEqual(raw, canonical + b"\n")
        self.assertEqual(len(canonical), EXPECTED_CANONICAL_BYTES)
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), EXPECTED_COMMITMENT)
        self.assertEqual(self.suite["artifact_digest_hex"], EXPECTED_ARTIFACT)
        self.assertEqual(self.suite["schema"], "zero-ground-cross-runtime-transport-breaker-v1")
        self.assertEqual(len(self.suite["cases"]), 26)
        self.assertEqual(len(self.expanded), 70)
        prefixes = [
            case["prefix_length"]
            for case in self.expanded
            if case["source_id"] == "truncation-every-proper-prefix"
        ]
        self.assertEqual(prefixes, list(range(45)))

    def _record_category(
        self, runtime: str, case: dict[str, Any], result: dict[str, Any]
    ) -> None:
        if result["accepted"]:
            return
        expected = case["expect"]["code"]
        native = (
            _python_native_category(result["error"])
            if runtime == "python"
            else _rust_native_category(result["error"])
        )
        if native != expected:
            self.summary["category_only_mismatches"].append(
                {
                    "case": case["id"],
                    "expected_suite_category": expected,
                    "native_category": native,
                    "runtime": runtime,
                }
            )

    def _check_case(
        self,
        case: dict[str, Any],
        python_result: dict[str, Any],
        rust_result: dict[str, Any],
        rust_transitions: dict[int, list[dict[str, Any]]],
    ) -> None:
        expected_accept = _expected_accept(case)
        self.assertEqual(python_result["accepted"], expected_accept, case["id"] + "/python")
        self.assertEqual(rust_result["accepted"], expected_accept, case["id"] + "/rust")

        if case["expect"]["transport"] == "reject":
            self.assertEqual(python_result.get("stage"), "transport", case["id"])
        elif case["expect"].get("recover") == "reject":
            self.assertEqual(python_result.get("transport"), "accept", case["id"])
            self.assertEqual(python_result.get("stage"), "recover", case["id"])

        if not expected_accept:
            self._record_category("python", case, python_result)
            self._record_category("rust", case, rust_result)
            return

        value = case["expect"]["value"]
        for runtime, result in (("python", python_result), ("rust", rust_result)):
            self.assertEqual(result["rank"], value["rank"], case["id"] + "/" + runtime)
            self.assertEqual(
                result["canonical_hex"], case["wire_hex"], case["id"] + "/" + runtime
            )
        self.assertEqual(value["candidate"], _selected_candidate(case))
        if "canonical_history_utf8" in value:
            payload = bytes.fromhex(case["wire_hex"])[42:]
            self.assertEqual(payload.decode("utf-8"), value["canonical_history_utf8"])

        self.assertEqual(
            python_result["transitions"], rust_transitions[value["rank"]], case["id"]
        )

    def _assert_committed_continuation(
        self, continuation: dict[str, Any], transitions: list[dict[str, Any]]
    ) -> None:
        resume = transitions[0]
        self.assertEqual(resume["operation"], continuation["operation"])
        self.assertEqual(
            resume["proof_domain_membership"],
            continuation["proof_domain_membership"],
        )
        self.assertEqual(resume["client_outputs"], continuation["client_outputs"])
        self.assertEqual(resume["action_outputs"], continuation["action_outputs"])
        expected_next = self.suite["fixtures"][continuation["next_envelope_fixture"]]
        self.assertEqual(resume["next_envelope_hex"], expected_next)

    def test_02_all_vectors_both_runtimes_all_environments(self) -> None:
        environments = self.suite["environment_matrix"]["environments"]
        baseline_environment = environments[0]

        inspect = subprocess.run(
            [str(RUST_ROOT / "target" / "release" / "b1-realizer"), "inspect"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_sanitized_environment(baseline_environment),
            check=False,
        )
        self.assertEqual(inspect.returncode, 0)
        self.assertEqual(inspect.stderr, b"")
        self.assertEqual(inspect.stdout.decode("ascii"), EXPECTED_INSPECT)
        self.summary["rust_cli_inspect"] = inspect.stdout.decode("ascii").strip()

        accepted_ranks = sorted(
            {case["expect"]["value"]["rank"] for case in self.expanded if _expected_accept(case)}
        )
        self.assertEqual(accepted_ranks, [0, 1, 4, 66051, 82583])

        python_batch = _run_python_process(self.expanded, baseline_environment)
        self.assertEqual(python_batch["artifact_digest"], EXPECTED_ARTIFACT)
        rust_results, rust_transitions = _run_rust_process(
            self.helper,
            self.expanded,
            accepted_ranks,
            baseline_environment,
            EXPECTED_ARTIFACT,
        )
        python_results = python_batch["results"]
        self.assertEqual(len(python_results), 70)
        self.assertEqual(len(rust_results), 70)

        for case, python_result, rust_result in zip(
            self.expanded, python_results, rust_results, strict=True
        ):
            self._check_case(case, python_result, rust_result, rust_transitions)

        accepted_per_runtime = sum(result["accepted"] for result in python_results)
        rejected_per_runtime = len(python_results) - accepted_per_runtime
        self.assertEqual((accepted_per_runtime, rejected_per_runtime), (5, 65))

        accepted_by_rank = {
            result["rank"]: result
            for result in python_results
            if result["accepted"]
        }
        for source in self.suite["cases"]:
            continuation = source.get("expect", {}).get("continuation")
            if continuation is not None:
                rank = source["expect"]["value"]["rank"]
                self._assert_committed_continuation(
                    continuation, accepted_by_rank[rank]["transitions"]
                )
            true_continuation = source.get("expect", {}).get(
                "true_history_expected_continuation"
            )
            if true_continuation is not None:
                self._assert_committed_continuation(
                    true_continuation, accepted_by_rank[0]["transitions"]
                )
                substituted = accepted_by_rank[source["expect"]["value"]["rank"]][
                    "transitions"
                ][0]
                true_resume = accepted_by_rank[0]["transitions"][0]
                self.assertNotEqual(substituted, true_resume)

        matrix_ids = self.suite["environment_matrix"]["case_ids"]
        index_by_source_id = {
            case["source_id"]: index
            for index, case in enumerate(self.expanded)
            if case["source_id"] in matrix_ids
        }
        self.assertEqual(set(index_by_source_id), set(matrix_ids))
        matrix_cases = [self.expanded[index_by_source_id[case_id]] for case_id in matrix_ids]
        baseline_python = [
            python_results[index_by_source_id[case_id]] for case_id in matrix_ids
        ]
        baseline_rust = [rust_results[index_by_source_id[case_id]] for case_id in matrix_ids]
        matrix_ranks = sorted(
            {case["expect"]["value"]["rank"] for case in matrix_cases if _expected_accept(case)}
        )
        self.assertEqual(matrix_ranks, [0, 4, 66051])

        # The C/UTC observations above are the first of the three matrix rows.
        # Start fresh processes for both remaining environments.
        for environment in environments[1:]:
            other_python_batch = _run_python_process(matrix_cases, environment)
            self.assertEqual(other_python_batch["artifact_digest"], EXPECTED_ARTIFACT)
            other_rust, other_transitions = _run_rust_process(
                self.helper,
                matrix_cases,
                matrix_ranks,
                environment,
                EXPECTED_ARTIFACT,
            )
            self.assertEqual(other_python_batch["results"], baseline_python)
            self.assertEqual(other_rust, baseline_rust)
            for rank in matrix_ranks:
                self.assertEqual(other_transitions[rank], rust_transitions[rank])

        category_mismatches = self.summary["category_only_mismatches"]
        category_mismatches.sort(
            key=lambda item: (item["runtime"], item["case"])
        )
        self.summary["mandatory"] = {
            "expanded_cases": 70,
            "runtime_case_checks": 140,
            "accepted": 10,
            "rejected": 130,
            "failed": 0,
            "proper_prefixes_per_runtime": 45,
        }
        self.summary["semantics"] = {
            "accepted_unique_ranks": accepted_ranks,
            "operations_per_rank": 17,
            "cross_runtime_transition_comparisons": len(accepted_ranks) * 17,
            "committed_resume_examples": 2,
            "coherent_substitution_divergence_witnesses": 1,
        }
        self.summary["environment_matrix"] = {
            "environments": 3,
            "cases_per_environment": 5,
            "runtime_case_checks": 30,
            "accepted": 18,
            "rejected": 12,
            "failed": 0,
            "baseline_checks_reused_from_mandatory": 10,
            "fresh_additional_process_case_probes": 20,
        }
        self.summary["physical_case_probes"] = {
            "mandatory_plus_additional_environment_probes": 160,
            "logical_checks_including_reused_environment_baseline": 170,
        }

    def test_03_publication_profiles_are_not_credited(self) -> None:
        profiles = self.suite["publication_profiles"]
        self.assertEqual(profiles["frozen_contract_verdict"], "UNSUPPORTED_BY_B1_B3")
        for name, profile in profiles.items():
            if name == "frozen_contract_verdict":
                continue
            self.assertTrue(profile["claim_is_optional"], name)
        for case in self.suite["publication_cases"]:
            self.assertEqual(
                case["expect_under_frozen_contract"], "UNSUPPORTED_BY_B1_B3"
            )
        self.summary["publication"] = {
            "conditional_cases": len(self.suite["publication_cases"]),
            "profiles_claimed_by_this_runtime_breaker": 0,
            "profiles_credited": 0,
            "verdict": "UNSUPPORTED_BY_B1_B3",
        }


if __name__ == "__main__" and len(sys.argv) == 2 and sys.argv[1] == "--python-worker":
    request = json.loads(sys.stdin.buffer.read())
    sys.stdout.buffer.write(_canonical_json(_python_worker(request)) + b"\n")
elif __name__ == "__main__":
    unittest.main(verbosity=2)
