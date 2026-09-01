#!/usr/bin/env python3
"""Freeze and validate the common closed R0.1B status vocabulary.

This module is deliberately stdlib-only.  Its constants are the authoritative
source; the current correction, LAB holdout, and base oracle are read only as
independent validation targets.  The emitted registry therefore has no
dependency on downstream oracle or holdout hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "R01B-STATUS-REGISTRY.json"
CORRECTION = HERE / "REALIZATION-CORRECTION-R01B.md"
HOLDOUT_SOURCE = HERE / "r01b_holdout_freeze.py"
BASE_ORACLE = HERE / "R01B-LITERAL-ORACLE.json"

SCHEMA_ID = "R01B-STATUS-REGISTRY-1"

STATUS_NAMESPACES: tuple[tuple[str, int, tuple[str, ...]], ...] = (
    (
        "applicability",
        1,
        ("APPLICABLE", "CONDITIONAL_ONLY", "NOT_APPLICABLE", "UNSUPPORTED_HERE", "UNKNOWN"),
    ),
    (
        "execution",
        2,
        (
            "NOT_RUN",
            "COMPLETE",
            "CONTROL_UNAVAILABLE",
            "APPARATUS_FAILURE",
            "TIME_BOUND_EXCEEDED",
            "STORAGE_BOUND_EXCEEDED",
        ),
    ),
    ("oracle", 3, ("ASSERTED", "CONDITIONAL_RETAINED", "NOT_DECLARED", "UNKNOWN")),
    ("full_conformance", 4, ("PASS", "FAIL", "UNKNOWN", "UNSUPPORTED", "NOT_APPLICABLE")),
    ("behavioral_comparison", 5, ("MATCH", "DIFFER", "UNKNOWN", "NOT_COMPARED")),
    (
        "scope",
        6,
        ("B_PROCESS_KILL", "L_EVIDENCE", "GUEST_REALIZATION", "CONDITIONAL_FUTURE", "PHYSICAL_OR_POWER"),
    ),
)

FULL_CONFORMANCE_PRECEDENCE = ("FAIL", "UNKNOWN", "UNSUPPORTED", "NOT_APPLICABLE", "PASS")
BEHAVIORAL_COMPARISON_PRECEDENCE = ("DIFFER", "UNKNOWN", "MATCH", "NOT_COMPARED")

LAB_HOLDOUT_FAILURE_LABELS = (
    "COMPARATOR_FALSE_MATCH",
    "CUT_OVERRUN",
    "DUPLICATE_LEGACY_STAGE",
    "DUPLICATE_NEUTRAL_FRAME",
    "EVIDENCE_UNAVAILABLE",
    "FALSE_SUCCESS_ATTESTATION_DIRECTORY_FSYNC",
    "FALSE_SUCCESS_ATTESTATION_EXCLUSIVE_CREATE",
    "FALSE_SUCCESS_ATTESTATION_FILE_FSYNC",
    "FALSE_SUCCESS_ATTESTATION_REPLACE",
    "KILL_NOT_CAUSAL",
    "MALFORMED_STRUCTURED_UNKNOWN",
    "MISSING_MEASUREMENT",
    "MISSING_RECOVERY_OBSERVATION",
    "MISSING_REQUIRED_CONTAINER_MEMBER",
    "RECOVERY_BEFORE_REAP",
    "SELECTION_MISSING",
    "SEMANTIC_MISMATCH",
    "STRUCTURED_STATUS_FORBIDDEN",
)

CORE_RUNTIME_FAILURE_LABELS = (
    "DESCRIPTOR_OR_OVERLAY_MISMATCH",
    "CUT_REACHABILITY_MISMATCH",
    "TERMINAL_MISMATCH",
    "WAIT_ORDER_MISMATCH",
    "B_RESPONSE_MISMATCH",
    "OPERATION_FACT_MISMATCH",
    "OPERATION_SOURCE_MISMATCH",
    "OPERATION_ERRNO_MISMATCH",
    "CONTROL_PROTOCOL_MISMATCH",
    "MANIFEST_SELF_REPORT_TRACE_DISAGREEMENT",
    "COMPARISON_EDGE_EXPECTATION_MISMATCH",
    "UNREGISTERED_B_OR_L_CROSSING",
    "EVIDENCE_ENVELOPE_SCHEMA_MISMATCH",
    "REPLAY_EXACT_BYTES_MISMATCH",
    "COMMON_MODE_NEGATIVE_NOT_REJECTED",
)

SPECIAL_FAILURE_LABELS = ("UNREGISTERED_ERRNO",)

# Preserve every already-issued LAB failure code, then assign new labels in
# ascending unsigned-UTF-8 order.  This is deterministic without renumbering
# retained holdout evidence.
FAILURE_REASON_LABELS = LAB_HOLDOUT_FAILURE_LABELS + tuple(
    sorted(
        (set(CORE_RUNTIME_FAILURE_LABELS) | set(SPECIAL_FAILURE_LABELS))
        - set(LAB_HOLDOUT_FAILURE_LABELS),
        key=lambda value: value.encode("utf-8"),
    )
)

OPERATION_IDS = (
    "ACQUIRE_EXCLUSIVE",
    "ACQUIRE_NONEXCLUSIVE",
    "FILE_FSYNC",
    "REPLACE",
    "DIRECTORY_FSYNC",
    "SELF_STOP_SIGNAL",
    "CAUSAL_KILL_SIGNAL",
    "PUBLISHER_TERMINATION_OBSERVATION",
    "EXACT_PUBLISHER_REAP",
    "RECOVERY_EXEC",
)

CURRENT_BASE_OPERATION_FACTS = (
    "NOT_APPLICABLE",
    "NOT_REACHED",
    "NOT_SELECTED",
    "CONTROL_UNAVAILABLE",
    "OBSERVED_ABSENT",
    "OBSERVED_SUCCESS",
    "OBSERVED_KERNEL_ERROR",
    "SIMULATED_ERROR_WITHOUT_KERNEL_ENTRY",
    "UNKNOWN",
)

OPERATION_FACTS = CURRENT_BASE_OPERATION_FACTS

OPERATION_FACT_ROLES = {
    "CONTROL_UNAVAILABLE": "EXPECTATION_OR_OBSERVATION",
    "NOT_APPLICABLE": "EXPECTATION_OR_OBSERVATION",
    "NOT_REACHED": "EXPECTATION_OR_OBSERVATION",
    "NOT_SELECTED": "EXPECTATION_ONLY",
    "OBSERVED_ABSENT": "EXPECTATION_OR_OBSERVATION",
    "OBSERVED_KERNEL_ERROR": "EXPECTATION_OR_OBSERVATION",
    "OBSERVED_SUCCESS": "EXPECTATION_OR_OBSERVATION",
    "SIMULATED_ERROR_WITHOUT_KERNEL_ENTRY": "EXPECTATION_OR_OBSERVATION",
    "UNKNOWN": "OBSERVATION_ONLY",
}

CONFIGURED_SOURCES = (
    "PUBLISHER_KERNEL",
    "PUBLISHER_WRAPPER",
    "MANIFEST_BRANCH",
    "STAGE_CONTROLLER",
    "PUBLISHER_SELF_CUT",
    "LIFECYCLE_SUPERVISOR",
    "PARENT_WAIT",
    "PIDFD_PROC_OBSERVER",
    "RECOVERY_LAUNCHER",
)

ERRNO_COORDINATES = ("NONE", "EEXIST_17", "EIO_5")

EVIDENCE_SOURCE_IDS = (
    "CONTROL_RECORD",
    "EXACT_PROCESS_IDENTITY",
    "EXEC_RECORD",
    "INDEPENDENT_TRACE",
    "MECHANISM_MANIFEST",
    "PIDFD_PROC_RECORD",
    "SELF_REPORT",
    "SEMANTIC_DESCRIPTOR",
    "TERMINATION_RECORD",
    "WAIT_RECORD",
)

REACHABILITY_LABELS = (
    "CONTROL_UNAVAILABLE",
    "EXPECTED_ERROR_TERMINAL",
    "EXPECTED_TERMINAL",
    "NOT_APPLICABLE",
    "REACHABLE",
    "TERMINATES_BEFORE_REQUESTED_POSITION",
)
B_EXPECTATION_KINDS = ("EXACT", "NO_B_HISTORY")
TERMINAL_LABELS = ("EXIT_0", "EXIT_NONZERO", "NO_EXECUTION", "RECOVERY_ONLY", "SIGNAL_9")
WAIT_ORDER_LABELS = ("NO_EXECUTION", "RECOVERY_ONLY", "WAIT_AFTER_RECOVERY", "WAIT_BEFORE_RECOVERY")
RISK_CLASS_LABELS = (
    "ACCIDENTAL_CORRUPTION_REJECTED",
    "CUT_FUTURE_UNEXECUTABLE",
    "MISSING_REPORTED_ABSENT",
    "NONE",
    "SIMULATED_WRAPPER_ERROR",
    "STALE_COLLISION_REFUSED",
    "UNDETECTED_COHERENT_REPLACEMENT",
    "UNDETECTED_STALE",
)

CORRECTION_REQUIRED_OPERATION_FACTS = (
    "NOT_REACHED",
    "OBSERVED_ABSENT",
    "OBSERVED_SUCCESS",
    "OBSERVED_KERNEL_ERROR",
    "SIMULATED_ERROR_WITHOUT_KERNEL_ENTRY",
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _assert_unique(values: Sequence[Any], name: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"{name} contains a duplicate")


def _assert_unsigned_utf8_order(values: Sequence[str], name: str) -> None:
    expected = sorted(values, key=lambda value: value.encode("utf-8"))
    if list(values) != expected:
        raise ValueError(f"{name} is not in ascending unsigned-UTF-8 order")


def status_registry() -> dict[str, Any]:
    return {
        name: {
            "codes": [{"code": code, "label": label} for code, label in enumerate(labels)],
            "namespace": namespace,
        }
        for name, namespace, labels in STATUS_NAMESPACES
    }


def _parse_correction_status_tables(text: str) -> dict[int, tuple[str, ...]]:
    section = text.split("## 5. Closed status coordinates", 1)[1].split("## 6.", 1)[0]
    parsed: dict[int, tuple[str, ...]] = {}
    for raw_namespace, cell in re.findall(r"^\| `([0-9a-f]{2})` [^|]+\| (.+) \|$", section, re.MULTILINE):
        entries = re.findall(r"`([0-9a-f]{2}) ([A-Z0-9_]+)`", cell)
        codes = tuple(int(code, 16) for code, _ in entries)
        if codes != tuple(range(len(entries))):
            raise ValueError(f"correction namespace {raw_namespace} has nonsequential codes")
        parsed[int(raw_namespace, 16)] = tuple(label for _, label in entries)
    return parsed


def validate_correction() -> dict[str, Any]:
    raw = CORRECTION.read_bytes()
    text = raw.decode("utf-8")
    parsed = _parse_correction_status_tables(text)
    expected = {namespace: labels for _, namespace, labels in STATUS_NAMESPACES}
    if parsed != expected:
        raise ValueError(f"correction section-5 tables differ: {parsed!r}")

    normalized = " ".join(text.split())
    behavioral_rule = (
        "`DIFFER` if any edge differs; otherwise `UNKNOWN` if any edge is unknown; "
        "otherwise `MATCH` if at least one edge was compared; otherwise `NOT_COMPARED`"
    )
    full_rule = (
        "`FAIL` if any check fails; otherwise `UNKNOWN` if any check is unknown; "
        "otherwise `UNSUPPORTED` if any applicable check is explicitly unsupported; "
        "otherwise `NOT_APPLICABLE` if there are no applicable checks; otherwise `PASS`"
    )
    if behavioral_rule not in normalized:
        raise ValueError("correction behavioral aggregation rule differs")
    if full_rule not in normalized:
        raise ValueError("correction full-conformance aggregation rule differs")

    oracle_section = text.split("### 11.4 Literal oracle registry", 1)[1].split("## 12.", 1)[0]
    for label in CORRECTION_REQUIRED_OPERATION_FACTS:
        if f"`{label}" not in oracle_section:
            raise ValueError(f"correction no longer requires operation fact {label}")
    for label in ERRNO_COORDINATES:
        if f"`{label}`" not in oracle_section:
            raise ValueError(f"correction no longer freezes errno coordinate {label}")
    return {"byte_length": len(raw), "sha256": sha256(raw)}


def _expected_authority_source() -> dict[str, str]:
    return {"schema_id": SCHEMA_ID, "sha256": sha256(encoded_registry())}


def validate_holdout_source() -> None:
    declared = runpy.run_path(str(HOLDOUT_SOURCE))
    if declared["STATUS_REGISTRY_SHA256"] != _expected_authority_source()["sha256"]:
        raise ValueError("LAB holdout generator pins a different status authority")
    authority = declared["STATUS_AUTHORITY"]
    if authority != build_registry():
        raise ValueError("LAB holdout generator loaded different status-authority bytes")
    source_tables = declared["STATUS_TABLES"]
    expected_tables = {
        name: (namespace, labels)
        for name, namespace, labels in STATUS_NAMESPACES
    }
    if source_tables != expected_tables:
        raise ValueError("LAB holdout generator declares different status tables")
    if tuple(declared["FAILURE_REASON_REGISTRY"]) != tuple(_failure_registry()):
        raise ValueError("LAB holdout generator declares different failure reasons")


def validate_base_oracle() -> tuple[str, ...]:
    package = json.loads(BASE_ORACLE.read_bytes())
    if package["row_count"] != 3028 or len(package["rows"]) != 3028:
        raise ValueError("base oracle is not the 3,028-row corpus")
    if package["status_registry_source"] != _expected_authority_source():
        raise ValueError("base oracle pins a different status authority")

    rows = package["rows"]
    domains = {
        "reachability": {row["expected"]["cut_reachability"] for row in rows},
        "b_expectation_kind": {row["expected"]["b_expectation"]["kind"] for row in rows},
        "terminal": {row["expected"]["expected_terminal"] for row in rows},
        "wait_order": {row["expected"]["expected_wait_order"] for row in rows},
        "risk_class": {row["expected"]["expected_risk_label"] for row in rows},
    }
    expected_domains = {
        "reachability": set(REACHABILITY_LABELS),
        "b_expectation_kind": set(B_EXPECTATION_KINDS),
        "terminal": set(TERMINAL_LABELS),
        "wait_order": set(WAIT_ORDER_LABELS),
        "risk_class": set(RISK_CLASS_LABELS),
    }
    if domains != expected_domains:
        raise ValueError(f"base oracle label domains differ: {domains!r}")

    status_domains = {
        name: set(labels) for name, _, labels in STATUS_NAMESPACES
    }
    registered_failures = set(FAILURE_REASON_LABELS)
    for row in rows:
        coordinates = row["expected"]["status_coordinates"]
        for name in ("applicability", "execution", "oracle", "full_conformance", "behavioral_comparison"):
            if coordinates[name] not in status_domains[name]:
                raise ValueError(f"base oracle uses unregistered {name} status")
        if not set(coordinates["scope"]) <= status_domains["scope"]:
            raise ValueError("base oracle uses an unregistered scope status")
        if not set(coordinates["failure_reasons"]) <= registered_failures:
            raise ValueError("base oracle uses an unregistered failure reason")
        operations = row["expected"]["operation_expectations"]
        if tuple(item["operation"] for item in operations) != OPERATION_IDS:
            raise ValueError(f"base oracle operation expansion differs at {row['case_id']}")
        for item in operations:
            if item["expectation"] not in CURRENT_BASE_OPERATION_FACTS:
                raise ValueError("base oracle uses an unregistered operation fact")
            if item["configured_source"] not in CONFIGURED_SOURCES:
                raise ValueError("base oracle uses an unregistered configured source")
            if item["errno"] not in ERRNO_COORDINATES:
                raise ValueError("base oracle uses an unregistered errno coordinate")
            if item["required_sources"] != sorted(set(item["required_sources"])):
                raise ValueError("base oracle evidence sources are not sorted and unique")
            if not set(item["required_sources"]) <= set(EVIDENCE_SOURCE_IDS):
                raise ValueError("base oracle uses an unregistered evidence source")

    behavioral = status_domains["behavioral_comparison"]
    if not all(edge["expected_result"] in behavioral for edge in package["comparison_edges"]):
        raise ValueError("base oracle comparison edge uses an unregistered result")
    return ()


def aggregate_full_conformance(values: Iterable[str]) -> str:
    observed = tuple(values)
    allowed = set(
        next(labels for name, _, labels in STATUS_NAMESPACES if name == "full_conformance")
    )
    if not set(observed) <= allowed:
        raise ValueError("invalid full-conformance value")
    if not observed:
        return "NOT_APPLICABLE"
    for label in FULL_CONFORMANCE_PRECEDENCE:
        if label in observed:
            return label
    raise AssertionError("unreachable full-conformance aggregation")


def aggregate_behavioral_comparison(values: Iterable[str]) -> str:
    observed = tuple(values)
    allowed = set(
        next(labels for name, _, labels in STATUS_NAMESPACES if name == "behavioral_comparison")
    )
    if not set(observed) <= allowed:
        raise ValueError("invalid behavioral-comparison value")
    if not observed:
        return "NOT_COMPARED"
    for label in BEHAVIORAL_COMPARISON_PRECEDENCE:
        if label in observed:
            return label
    raise AssertionError("unreachable behavioral aggregation")


def validate_constants() -> None:
    names = tuple(name for name, _, _ in STATUS_NAMESPACES)
    namespaces = tuple(namespace for _, namespace, _ in STATUS_NAMESPACES)
    _assert_unique(names, "status namespace names")
    _assert_unique(namespaces, "status namespace codes")
    if namespaces != tuple(range(1, 7)):
        raise ValueError("status namespaces are not exactly 1..6")
    for name, _, labels in STATUS_NAMESPACES:
        _assert_unique(labels, f"status labels for {name}")

    for name, values in (
        ("LAB holdout failures", LAB_HOLDOUT_FAILURE_LABELS),
        ("core runtime failures", CORE_RUNTIME_FAILURE_LABELS),
        ("common failure reasons", FAILURE_REASON_LABELS),
        ("operation IDs", OPERATION_IDS),
        ("operation facts", OPERATION_FACTS),
        ("configured sources", CONFIGURED_SOURCES),
        ("errno coordinates", ERRNO_COORDINATES),
        ("evidence source IDs", EVIDENCE_SOURCE_IDS),
        ("reachability labels", REACHABILITY_LABELS),
        ("B-expectation kinds", B_EXPECTATION_KINDS),
        ("terminal labels", TERMINAL_LABELS),
        ("wait-order labels", WAIT_ORDER_LABELS),
        ("risk-class labels", RISK_CLASS_LABELS),
    ):
        _assert_unique(values, name)

    _assert_unsigned_utf8_order(LAB_HOLDOUT_FAILURE_LABELS, "LAB holdout failures")
    new_failures = FAILURE_REASON_LABELS[len(LAB_HOLDOUT_FAILURE_LABELS):]
    _assert_unsigned_utf8_order(new_failures, "new common failure reasons")
    for name, values in (
        ("evidence source IDs", EVIDENCE_SOURCE_IDS),
        ("reachability labels", REACHABILITY_LABELS),
        ("B-expectation kinds", B_EXPECTATION_KINDS),
        ("terminal labels", TERMINAL_LABELS),
        ("wait-order labels", WAIT_ORDER_LABELS),
        ("risk-class labels", RISK_CLASS_LABELS),
    ):
        _assert_unsigned_utf8_order(values, name)

    if set(OPERATION_FACT_ROLES) != set(OPERATION_FACTS):
        raise ValueError("operation fact roles are not total")
    if not set(CORRECTION_REQUIRED_OPERATION_FACTS) <= set(OPERATION_FACTS):
        raise ValueError("common operation facts do not cover correction section 11.4")
    if not set(CURRENT_BASE_OPERATION_FACTS) <= set(OPERATION_FACTS):
        raise ValueError("common operation facts do not cover the current base oracle")

    full_labels = next(labels for name, _, labels in STATUS_NAMESPACES if name == "full_conformance")
    behavioral_labels = next(labels for name, _, labels in STATUS_NAMESPACES if name == "behavioral_comparison")
    if set(FULL_CONFORMANCE_PRECEDENCE) != set(full_labels):
        raise ValueError("full-conformance precedence is not total")
    if set(BEHAVIORAL_COMPARISON_PRECEDENCE) != set(behavioral_labels):
        raise ValueError("behavioral precedence is not total")


def _failure_registry() -> list[dict[str, Any]]:
    result = []
    lab = set(LAB_HOLDOUT_FAILURE_LABELS)
    core = set(CORE_RUNTIME_FAILURE_LABELS)
    special = set(SPECIAL_FAILURE_LABELS)
    for code, label in enumerate(FAILURE_REASON_LABELS):
        origins = []
        if label in lab:
            origins.append("LAB_HOLDOUT")
        if label in core:
            origins.append("CORE_RUNTIME")
        if label in special:
            origins.append("ERRNO_CLOSURE")
        result.append({"code": code, "label": label, "origins": origins})
    return result


def build_registry() -> dict[str, Any]:
    validate_constants()
    correction_source = validate_correction()
    return {
        "aggregation_precedence": {
            "behavioral_comparison": {
                "empty_input": "NOT_COMPARED",
                "highest_to_lowest": list(BEHAVIORAL_COMPARISON_PRECEDENCE),
                "rule": "DIFFER>UNKNOWN>MATCH>NOT_COMPARED",
            },
            "full_conformance": {
                "empty_input": "NOT_APPLICABLE",
                "highest_to_lowest": list(FULL_CONFORMANCE_PRECEDENCE),
                "rule": "FAIL>UNKNOWN>UNSUPPORTED>NOT_APPLICABLE>PASS",
            },
        },
        "base_oracle_label_registries": {
            "b_expectation_kind": list(B_EXPECTATION_KINDS),
            "reachability": list(REACHABILITY_LABELS),
            "risk_class": list(RISK_CLASS_LABELS),
            "terminal": list(TERMINAL_LABELS),
            "wait_order": list(WAIT_ORDER_LABELS),
        },
        "configured_source_registry": list(CONFIGURED_SOURCES),
        "correction_source": {
            "byte_length": correction_source["byte_length"],
            "path": CORRECTION.name,
            "sha256": correction_source["sha256"],
        },
        "errno_coordinate_registry": list(ERRNO_COORDINATES),
        "evidence_source_registry": list(EVIDENCE_SOURCE_IDS),
        "failure_reason_order": "retained_LAB_codes_then_new_labels_ascending_unsigned_utf8",
        "failure_reason_registry": _failure_registry(),
        "naming_policy": {
            "implicit_aliases": False,
            "rule": "labels_are_exact_and_cross_registry_synonyms_require_a_new_explicit_freeze",
        },
        "operation_fact_registry": [
            {"label": label, "role": OPERATION_FACT_ROLES[label]}
            for label in OPERATION_FACTS
        ],
        "operation_registry": list(OPERATION_IDS),
        "schema_id": SCHEMA_ID,
        "status_coordinate_registry": status_registry(),
        "validation_boundaries": {
            "base_oracle": BASE_ORACLE.name,
            "correction": CORRECTION.name,
            "lab_holdout_source": HOLDOUT_SOURCE.name,
            "rule": "downstream artifacts are validation targets, not registry hash inputs",
        },
    }


def validate_external_sources() -> tuple[str, ...]:
    """Validate downstream drafts without making them registry hash inputs."""
    validate_holdout_source()
    return validate_base_oracle()


def encoded_registry() -> bytes:
    return canonical_json(build_registry())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify exact generated bytes")
    args = parser.parse_args()
    validate_external_sources()
    raw = encoded_registry()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != raw:
            raise SystemExit(f"{OUTPUT.name} is not the deterministic generated registry")
    else:
        OUTPUT.write_bytes(raw)
    package = json.loads(raw)
    print(f"schema_id={package['schema_id']}")
    print(f"failure_reasons={len(package['failure_reason_registry'])}")
    print(f"bytes={len(raw)}")
    print(f"sha256={sha256(raw)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
