#!/usr/bin/env python3
"""Materialize the pre-subject R0.1B symbolic history corpus."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
from typing import Any


BACKENDS = ("E", "T")
CUTS = ("J0", "J1", "J2", "J3", "J4", "J5", "NORMAL")
CLEAN_MANIFESTS = (
    "REFERENCE",
    "NO_FILE_FSYNC",
    "NO_DIRECTORY_FSYNC",
    "NO_EXCLUSIVE_CREATE",
    "NO_REPLACE",
    "NO_PRE_RECOVERY_REAP_BEHAVIORAL",
)
CASE_TAG = b"ZGR01B-CASE\x00"
SCHEMA_ID = "R01B-SYMBOLIC-DESCRIPTORS-1"


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def tv(value: Any) -> bytes:
    """R0.1B section-3 typed encoding for symbolic descriptor values."""
    if isinstance(value, bool):
        return b"\x06" if value else b"\x05"
    if isinstance(value, int):
        if value >= 0:
            if value > 0xFFFFFFFFFFFFFFFF:
                raise ValueError("unsigned integer out of range")
            return b"\x01" + struct.pack(">Q", value)
        if value < -(1 << 63):
            raise ValueError("signed integer out of range")
        return b"\x02" + struct.pack(">q", value)
    if isinstance(value, bytes):
        return b"\x03" + struct.pack(">Q", len(value)) + value
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        return b"\x04" + struct.pack(">Q", len(encoded)) + encoded
    if isinstance(value, list):
        return b"\x07" + struct.pack(">Q", len(value)) + b"".join(
            tv(item) for item in value
        )
    if isinstance(value, dict):
        parts = [b"\x08", struct.pack(">Q", len(value))]
        keys = sorted(value, key=lambda item: item.encode("ascii"))
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate map key")
        for key in keys:
            encoded = key.encode("ascii")
            if not encoded or len(encoded) > 0xFFFF or not all(32 <= b <= 126 for b in encoded):
                raise ValueError(f"invalid map key: {key!r}")
            parts.extend((struct.pack(">H", len(encoded)), encoded, tv(value[key])))
        return b"".join(parts)
    raise TypeError(type(value).__name__)


def clean_case(case: str) -> tuple[str, str]:
    if case == "CREATE":
        return "ABSENT_CLEAN", ""
    if case == "UPDATE":
        return "VALID_P0_CLEAN", "00"
    raise ValueError(case)


def blank_descriptor(**updates: Any) -> dict[str, Any]:
    descriptor: dict[str, Any] = {
        "backend": "",
        "base_record_payload_hex": "",
        "base_record_present": False,
        "case": "",
        "comparison_rules": [],
        "continuation_hex": "",
        "cut": "",
        "family": "",
        "history_production": "",
        "injection": "NONE",
        "manifest": "REFERENCE",
        "mutation": "NONE",
        "mutation_arg0": -1,
        "mutation_arg1": -1,
        "mutation_target_payload_hex": "",
        "origin": "R01B",
        "publish_payload_hex": "",
        "publish_present": False,
        "repetition": 0,
        "semantic_profile": "R01B",
        "setup": "",
    }
    descriptor.update(updates)
    if set(descriptor) != {
        "backend",
        "base_record_payload_hex",
        "base_record_present",
        "case",
        "comparison_rules",
        "continuation_hex",
        "cut",
        "family",
        "history_production",
        "injection",
        "manifest",
        "mutation",
        "mutation_arg0",
        "mutation_arg1",
        "mutation_target_payload_hex",
        "origin",
        "publish_payload_hex",
        "publish_present",
        "repetition",
        "semantic_profile",
        "setup",
    }:
        raise AssertionError("descriptor key drift")
    return descriptor


def publication_descriptor(
    *,
    family: str,
    backend: str,
    manifest: str,
    case: str,
    setup: str,
    payload_hex: str,
    cut: str,
    repetition: int,
    comparison_rules: list[str] | None = None,
    injection: str = "NONE",
    origin: str = "R01B",
) -> dict[str, Any]:
    return blank_descriptor(
        backend=backend,
        case=case,
        comparison_rules=(comparison_rules or ["CROSS_BACKEND_SAME_SYMBOLIC_ROW"]),
        cut=cut,
        family=family,
        history_production="PUBLICATION",
        injection=injection,
        manifest=manifest,
        origin=origin,
        publish_payload_hex=payload_hex,
        publish_present=True,
        repetition=repetition,
        setup=setup,
    )


def enumerate_clean(rows: list[dict[str, Any]]) -> None:
    for backend in BACKENDS:
        for manifest in CLEAN_MANIFESTS:
            for case in ("CREATE", "UPDATE"):
                setup, payload = clean_case(case)
                for cut in CUTS[:-1]:
                    for repetition in range(3):
                        rows.append(
                            publication_descriptor(
                                family="CLEAN_MECHANISM",
                                backend=backend,
                                manifest=manifest,
                                case=case,
                                setup=setup,
                                payload_hex=payload,
                                cut=cut,
                                comparison_rules=(
                                    ["ANCHOR_FOR_REGISTERED_VARIANTS", "CROSS_BACKEND_SAME_SYMBOLIC_ROW"]
                                    if manifest == "REFERENCE"
                                    else ["CROSS_BACKEND_SAME_SYMBOLIC_ROW", "PAIR_REFERENCE_SAME_BACKEND"]
                                ),
                                repetition=repetition,
                            )
                        )
                rows.append(
                    publication_descriptor(
                        family="CLEAN_MECHANISM",
                        backend=backend,
                        manifest=manifest,
                        case=case,
                        setup=setup,
                        payload_hex=payload,
                        cut="NORMAL",
                        comparison_rules=(
                            ["ANCHOR_FOR_REGISTERED_VARIANTS", "CROSS_BACKEND_SAME_SYMBOLIC_ROW"]
                            if manifest == "REFERENCE"
                            else ["CROSS_BACKEND_SAME_SYMBOLIC_ROW", "PAIR_REFERENCE_SAME_BACKEND"]
                        ),
                        repetition=0,
                    )
                )


def enumerate_occupied(rows: list[dict[str, Any]]) -> None:
    occupied_cases = (
        ("CREATE", "ABSENT_TMP", ""),
        ("UPDATE", "VALID_P0_TMP", "00"),
    )
    for backend in BACKENDS:
        for case, setup, payload in occupied_cases:
            for repetition in range(3):
                rows.append(
                    publication_descriptor(
                        family="OCCUPIED_STAGING",
                        backend=backend,
                        manifest="REFERENCE",
                        case=case,
                        setup=setup,
                        payload_hex=payload,
                        cut="J0",
                        comparison_rules=["ANCHOR_FOR_REGISTERED_VARIANTS", "CROSS_BACKEND_SAME_SYMBOLIC_ROW"],
                        repetition=repetition,
                    )
                )
            rows.append(
                publication_descriptor(
                    family="OCCUPIED_STAGING",
                    backend=backend,
                    manifest="REFERENCE",
                    case=case,
                    setup=setup,
                    payload_hex=payload,
                    cut="NORMAL",
                    comparison_rules=["ANCHOR_FOR_REGISTERED_VARIANTS", "CROSS_BACKEND_SAME_SYMBOLIC_ROW"],
                    repetition=0,
                )
            )
            for cut in CUTS[1:-1]:
                rows.append(
                    publication_descriptor(
                        family="OCCUPIED_STAGING",
                        backend=backend,
                        manifest="REFERENCE",
                        case=case,
                        setup=setup,
                        payload_hex=payload,
                        cut=cut,
                        comparison_rules=["ANCHOR_FOR_REGISTERED_VARIANTS", "CROSS_BACKEND_SAME_SYMBOLIC_ROW"],
                        repetition=0,
                    )
                )
            for cut in CUTS[:-1]:
                for repetition in range(3):
                    rows.append(
                        publication_descriptor(
                            family="OCCUPIED_STAGING",
                            backend=backend,
                            manifest="NO_EXCLUSIVE_CREATE",
                            case=case,
                            setup=setup,
                            payload_hex=payload,
                            cut=cut,
                            comparison_rules=(
                                ["CROSS_BACKEND_SAME_SYMBOLIC_ROW", "PAIR_REFERENCE_SAME_BACKEND"]
                                if cut == "J0" or repetition == 0
                                else ["CROSS_BACKEND_SAME_SYMBOLIC_ROW"]
                            ),
                            repetition=repetition,
                        )
                    )
            rows.append(
                publication_descriptor(
                    family="OCCUPIED_STAGING",
                    backend=backend,
                    manifest="NO_EXCLUSIVE_CREATE",
                    case=case,
                    setup=setup,
                    payload_hex=payload,
                    cut="NORMAL",
                    comparison_rules=["CROSS_BACKEND_SAME_SYMBOLIC_ROW", "PAIR_REFERENCE_SAME_BACKEND"],
                    repetition=0,
                )
            )


def enumerate_control(rows: list[dict[str, Any]]) -> None:
    for backend in BACKENDS:
        for case in ("CREATE", "UPDATE"):
            setup, payload = clean_case(case)
            for cut in CUTS[:-1]:
                for repetition in range(3):
                    rows.append(
                        publication_descriptor(
                            family="STAGE_CONTROL",
                            backend=backend,
                            manifest="SELF_CUT",
                            case=case,
                            setup=setup,
                            payload_hex=payload,
                            cut=cut,
                            comparison_rules=["CROSS_BACKEND_SAME_SYMBOLIC_ROW", "PAIR_REFERENCE_SAME_BACKEND"],
                            repetition=repetition,
                        )
                    )
                rows.append(
                    publication_descriptor(
                        family="STAGE_CONTROL",
                        backend=backend,
                        manifest="DROP_STAGE_CONTROLLER",
                        case=case,
                        setup=setup,
                        payload_hex=payload,
                        cut=cut,
                        comparison_rules=["CROSS_BACKEND_SAME_SYMBOLIC_ROW"],
                        repetition=0,
                    )
                )
            for manifest in ("SELF_CUT", "DROP_STAGE_CONTROLLER"):
                rows.append(
                    publication_descriptor(
                        family="STAGE_CONTROL",
                        backend=backend,
                        manifest=manifest,
                        case=case,
                        setup=setup,
                        payload_hex=payload,
                        cut="NORMAL",
                        comparison_rules=(
                            ["CROSS_BACKEND_SAME_SYMBOLIC_ROW", "PAIR_REFERENCE_SAME_BACKEND"]
                            if manifest in ("SELF_CUT", "DROP_STAGE_CONTROLLER")
                            else ["CROSS_BACKEND_SAME_SYMBOLIC_ROW"]
                        ),
                        repetition=0,
                    )
                )


def enumerate_io_errors(rows: list[dict[str, Any]]) -> None:
    for backend in BACKENDS:
        for case in ("CREATE", "UPDATE"):
            setup, payload = clean_case(case)
            for injection in (
                "FILE_FSYNC_EIO",
                "REPLACE_EIO",
                "DIRECTORY_FSYNC_EIO",
            ):
                rows.append(
                    publication_descriptor(
                        family="WRAPPER_ERROR",
                        backend=backend,
                        manifest="REFERENCE",
                        case=case,
                        setup=setup,
                        payload_hex=payload,
                        cut="NORMAL",
                        comparison_rules=["CROSS_BACKEND_SAME_SYMBOLIC_ROW"],
                        repetition=0,
                        injection=injection,
                    )
                )


def record_fault_descriptor(
    *,
    backend: str,
    base_payload_hex: str,
    mutation: str,
    arg0: int = -1,
    arg1: int = -1,
    target_payload_hex: str = "",
) -> dict[str, Any]:
    return blank_descriptor(
        backend=backend,
        base_record_payload_hex=base_payload_hex,
        base_record_present=True,
        case="RECOVERY_ONLY",
        comparison_rules=["CROSS_BACKEND_SAME_SYMBOLIC_ROW"],
        cut="RECOVERY_ONLY",
        family="RECORD_FAULT",
        history_production="RECOVERY_ONLY",
        mutation=mutation,
        mutation_arg0=arg0,
        mutation_arg1=arg1,
        mutation_target_payload_hex=target_payload_hex,
        origin="R0_SECTION_7_1_ADAPTED_R01B",
        setup="INSTALLED_MUTATED_RECORD",
    )


def enumerate_record_faults(rows: list[dict[str, Any]]) -> None:
    for backend in BACKENDS:
        for payload_hex, record_length in (("", 64), ("00", 65)):
            rows.append(
                record_fault_descriptor(
                    backend=backend,
                    base_payload_hex=payload_hex,
                    mutation="MISSING",
                )
            )
            for length in range(record_length):
                rows.append(
                    record_fault_descriptor(
                        backend=backend,
                        base_payload_hex=payload_hex,
                        mutation="TRUNCATE",
                        arg0=length,
                    )
                )
            for byte_index in range(record_length):
                for bit_index in range(8):
                    rows.append(
                        record_fault_descriptor(
                            backend=backend,
                            base_payload_hex=payload_hex,
                            mutation="FLIP",
                            arg0=byte_index,
                            arg1=bit_index,
                        )
                    )
            for mutation in ("APPEND_ZERO", "WRONG_SUITE", "NONREGULAR"):
                rows.append(
                    record_fault_descriptor(
                        backend=backend,
                        base_payload_hex=payload_hex,
                        mutation=mutation,
                    )
                )

        rows.append(
            record_fault_descriptor(
                backend=backend,
                base_payload_hex="00",
                mutation="STALE_VALID",
                target_payload_hex="",
            )
        )
        rows.append(
            record_fault_descriptor(
                backend=backend,
                base_payload_hex="",
                mutation="OTHER_VALID",
                target_payload_hex="00",
            )
        )
        rows.append(
            record_fault_descriptor(
                backend=backend,
                base_payload_hex="00",
                mutation="OTHER_VALID",
                target_payload_hex="",
            )
        )


def build_package() -> dict[str, Any]:
    bodies: list[dict[str, Any]] = []
    enumerate_clean(bodies)
    enumerate_occupied(bodies)
    enumerate_control(bodies)
    enumerate_io_errors(bodies)
    enumerate_record_faults(bodies)
    if len(bodies) != 3028:
        raise AssertionError(f"unexpected descriptor total: {len(bodies)}")

    identified: list[tuple[str, dict[str, Any]]] = []
    for body in bodies:
        case_id = "r01b-case-" + hashlib.sha256(CASE_TAG + tv(body)).hexdigest()
        identified.append((case_id, body))
    identified.sort(key=lambda item: item[0].encode("ascii"))
    if len({item[0] for item in identified}) != len(identified):
        raise AssertionError("case-id collision")

    rows = [
        {"body": body, "case_id": case_id, "case_ordinal": ordinal}
        for ordinal, (case_id, body) in enumerate(identified)
    ]
    counts = dict(sorted(Counter(row["body"]["family"] for row in rows).items()))
    expected_counts = {
        "CLEAN_MECHANISM": 456,
        "OCCUPIED_STAGING": 112,
        "RECORD_FAULT": 2344,
        "STAGE_CONTROL": 104,
        "WRAPPER_ERROR": 12,
    }
    if counts != expected_counts:
        raise AssertionError((counts, expected_counts))
    return {
        "counts_by_family": counts,
        "row_count": len(rows),
        "rows": rows,
        "schema_id": SCHEMA_ID,
        "case_id_rule": "ASCII(r01b-case-)||lowerhex(sha256(ASCII(ZGR01B-CASE)||00||TV(body)))",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = canonical_json(build_package())
    args.output.write_bytes(value)
    print(f"bytes={len(value)} sha256={hashlib.sha256(value).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
