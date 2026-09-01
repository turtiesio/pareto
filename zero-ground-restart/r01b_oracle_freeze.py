#!/usr/bin/env python3
"""Materialize literal expected outputs for frozen R0.1B descriptors."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
from typing import Any


CASE_TAG = b"ZGR01B-CASE\x00"
ABSENT = "00"
REJECT = "01"
OK_Y0 = "0200000000"
OK_Y1 = "020000000100"
NO_CROSSING = "NO_CROSSING"
NO_OBSERVATION = "NO_OBSERVATION"


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def tv(value: Any) -> bytes:
    if isinstance(value, bool):
        return b"\x06" if value else b"\x05"
    if isinstance(value, int):
        return (b"\x01" + struct.pack(">Q", value)) if value >= 0 else (
            b"\x02" + struct.pack(">q", value)
        )
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
        keys = sorted(value, key=lambda item: item.encode("ascii"))
        parts = [b"\x08", struct.pack(">Q", len(keys))]
        for key in keys:
            encoded = key.encode("ascii")
            parts.extend((struct.pack(">H", len(encoded)), encoded, tv(value[key])))
        return b"".join(parts)
    raise TypeError(type(value).__name__)


def old_observation(case: str) -> str:
    if case == "CREATE":
        return ABSENT
    if case == "UPDATE":
        return OK_Y0
    raise ValueError(case)


def new_observation(case: str) -> str:
    if case == "CREATE":
        return OK_Y0
    if case == "UPDATE":
        return OK_Y1
    raise ValueError(case)


def error_result(slot: int, source: int, number: int) -> str:
    return (b"\x11" + bytes((slot, source)) + struct.pack(">i", number)).hex()


def publication_oracle(body: dict[str, Any]) -> dict[str, Any]:
    case = body["case"]
    cut = body["cut"]
    manifest = body["manifest"]
    family = body["family"]
    injection = body["injection"]
    old = old_observation(case)
    new = new_observation(case)

    if family == "STAGE_CONTROL" and manifest == "DROP_STAGE_CONTROLLER" \
            and cut != "NORMAL":
        return {
            "execution_applicability": "UNKNOWN_CONTROL_UNAVAILABLE",
            "expected_checkpoint_last": "NO_EXECUTION",
            "expected_publish_result_hex": NO_CROSSING,
            "expected_recovery_hex": NO_OBSERVATION,
            "expected_risk_label": "CUT_FUTURE_UNEXECUTABLE",
            "expected_terminal": "NO_EXECUTION",
            "expected_wait_order": "NO_EXECUTION",
        }

    if family == "OCCUPIED_STAGING" and manifest == "REFERENCE" \
            and cut != "J0":
        return {
            "execution_applicability": "EXECUTED",
            "expected_checkpoint_last": "J0",
            "expected_publish_result_hex": error_result(1, 0, 17),
            "expected_recovery_hex": old,
            "expected_risk_label": "STALE_COLLISION_REFUSED",
            "expected_terminal": "EXIT_NONZERO",
            "expected_wait_order": "WAIT_BEFORE_RECOVERY",
        }

    if family == "WRAPPER_ERROR":
        mapping = {
            "FILE_FSYNC_EIO": (3, old),
            "REPLACE_EIO": (4, old),
            "DIRECTORY_FSYNC_EIO": (5, new),
        }
        slot, recovery = mapping[injection]
        checkpoint_last = {3: "J2", 4: "J3", 5: "J4"}[slot]
        return {
            "execution_applicability": "EXECUTED",
            "expected_checkpoint_last": checkpoint_last,
            "expected_publish_result_hex": error_result(slot, 1, 5),
            "expected_recovery_hex": recovery,
            "expected_risk_label": "SIMULATED_WRAPPER_ERROR",
            "expected_terminal": "EXIT_NONZERO",
            "expected_wait_order": "WAIT_BEFORE_RECOVERY",
        }

    if cut == "NORMAL":
        recovery = old if manifest == "NO_REPLACE" else new
        return {
            "execution_applicability": "EXECUTED",
            "expected_checkpoint_last": "J5",
            "expected_publish_result_hex": "10",
            "expected_recovery_hex": recovery,
            "expected_risk_label": "NONE",
            "expected_terminal": "EXIT_0",
            "expected_wait_order": (
                "WAIT_AFTER_RECOVERY"
                if manifest == "NO_PRE_RECOVERY_REAP_BEHAVIORAL"
                else "WAIT_BEFORE_RECOVERY"
            ),
        }

    cut_number = int(cut[1:])
    recovery = old
    if manifest != "NO_REPLACE" and cut_number >= 4:
        recovery = new
    return {
        "execution_applicability": "EXECUTED",
        "expected_checkpoint_last": cut,
        "expected_publish_result_hex": NO_CROSSING,
        "expected_recovery_hex": recovery,
        "expected_risk_label": "NONE",
        "expected_terminal": "SIGNAL_9",
        "expected_wait_order": (
            "WAIT_AFTER_RECOVERY"
            if manifest == "NO_PRE_RECOVERY_REAP_BEHAVIORAL"
            else "WAIT_BEFORE_RECOVERY"
        ),
    }


def record_fault_oracle(body: dict[str, Any]) -> dict[str, Any]:
    mutation = body["mutation"]
    recovery = REJECT
    risk = "ACCIDENTAL_CORRUPTION_REJECTED"
    if mutation == "MISSING":
        recovery = ABSENT
        risk = "MISSING_REPORTED_ABSENT"
    elif mutation in ("STALE_VALID", "OTHER_VALID"):
        recovery = OK_Y0 if body["mutation_target_payload_hex"] == "" else OK_Y1
        risk = (
            "UNDETECTED_STALE"
            if mutation == "STALE_VALID"
            else "UNDETECTED_COHERENT_REPLACEMENT"
        )
    return {
        "execution_applicability": "EXECUTED",
        "expected_checkpoint_last": "NOT_APPLICABLE",
        "expected_publish_result_hex": NO_CROSSING,
        "expected_recovery_hex": recovery,
        "expected_risk_label": risk,
        "expected_terminal": "RECOVERY_ONLY",
        "expected_wait_order": "RECOVERY_ONLY",
    }


def expected_for(body: dict[str, Any]) -> dict[str, Any]:
    if body["family"] == "RECORD_FAULT":
        return record_fault_oracle(body)
    return publication_oracle(body)


def build_oracle(descriptor_package: dict[str, Any]) -> dict[str, Any]:
    if descriptor_package.get("schema_id") != "R01B-SYMBOLIC-DESCRIPTORS-1":
        raise ValueError("wrong descriptor schema")
    rows: list[dict[str, Any]] = []
    previous = ""
    for case_ordinal, item in enumerate(descriptor_package["rows"]):
        body = item["body"]
        case_id = "r01b-case-" + hashlib.sha256(CASE_TAG + tv(body)).hexdigest()
        if case_id != item["case_id"] or case_ordinal != item["case_ordinal"]:
            raise ValueError("descriptor identity mismatch")
        if previous and case_id <= previous:
            raise ValueError("descriptor order mismatch")
        previous = case_id
        rows.append(
            {
                "case_id": case_id,
                "case_ordinal": case_ordinal,
                "expected": expected_for(body),
            }
        )
    if len(rows) != 3028:
        raise AssertionError(len(rows))
    return {
        "descriptor_stream_sha256": hashlib.sha256(
            canonical_json(descriptor_package)
        ).hexdigest(),
        "oracle_independence_boundary": (
            "literal labels only; no subject record encoder, parser, adapter, "
            "publisher, recovery, or normalizer import"
        ),
        "row_count": len(rows),
        "rows": rows,
        "schema_id": "R01B-LITERAL-ORACLE-1",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--descriptors", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    descriptors = json.loads(args.descriptors.read_bytes())
    value = canonical_json(build_oracle(descriptors))
    args.output.write_bytes(value)
    print(f"bytes={len(value)} sha256={hashlib.sha256(value).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
