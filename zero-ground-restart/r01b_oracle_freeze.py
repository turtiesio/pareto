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
EDGE_TAG = b"ZGR01B-EDGE\x00"
ABSENT = "00"
REJECT = "01"
OK_Y0 = "0200000000"
OK_Y1 = "020000000100"
NO_CROSSING = "NO_CROSSING"
NO_OBSERVATION = "NO_OBSERVATION"
HERE = Path(__file__).resolve().parent
STATUS_REGISTRY_PATH = HERE / "R01B-STATUS-REGISTRY.json"
STATUS_REGISTRY_SHA256 = "54857699919b5c95de79bb25006a6fd4f9f448870c7d97c4364be75c6191c61a"
STATUS_REGISTRY_BYTES = STATUS_REGISTRY_PATH.read_bytes()
if hashlib.sha256(STATUS_REGISTRY_BYTES).hexdigest() != STATUS_REGISTRY_SHA256:
    raise RuntimeError("pinned common status registry changed")
STATUS_REGISTRY = json.loads(STATUS_REGISTRY_BYTES)
STATUS_ENUMS = {
    name: [item["label"] for item in table["codes"]]
    for name, table in STATUS_REGISTRY["status_coordinate_registry"].items()
}
OPERATION_ORDER = tuple(STATUS_REGISTRY["operation_registry"])
OPERATION_EXPECTATIONS = tuple(
    item["label"] for item in STATUS_REGISTRY["operation_fact_registry"]
)
ERRNO_COORDINATES = tuple(STATUS_REGISTRY["errno_coordinate_registry"])
CONFIGURED_SOURCES = tuple(STATUS_REGISTRY["configured_source_registry"])
EVIDENCE_SOURCES = tuple(STATUS_REGISTRY["evidence_source_registry"])
FULL_CONFORMANCE_PRECEDENCE = tuple(
    STATUS_REGISTRY["aggregation_precedence"]["full_conformance"][
        "highest_to_lowest"
    ]
)

BASE_CONFORMANCE_CHECKS = (
    (
        "DESCRIPTOR_INPUT",
        "SUBMITTED_DESCRIPTOR_TEMPLATE_BYTES_AND_FREEZE_OVERLAY_IDS",
        "descriptor_registry/case_id",
    ),
    (
        "EXECUTION",
        "ACTUAL_EXECUTION_COORDINATE",
        "status_coordinates/execution",
    ),
    (
        "CUT_REACHABILITY",
        "OBSERVED_CUT_REACHABILITY_AND_TERMINATION_POSITION",
        "cut_reachability",
    ),
    (
        "CONTROL_PROTOCOL",
        "OBSERVED_NEUTRAL_FRAME_SEQUENCE_FLAGS_TRIAL_DIGEST_AND_ACK_RELATION",
        "control_protocol_and_descriptor_manifest",
    ),
    (
        "CHECKPOINT_STREAM",
        "OBSERVED_ORDERED_CHECKPOINT_SLOT_STREAM",
        "expected_checkpoint_slots",
    ),
    (
        "B_RESPONSE",
        "ACTUAL_COMPLETE_B_HISTORY_OR_VERIFIED_NO_B_HISTORY",
        "b_expectation",
    ),
    (
        "TERMINAL",
        "OBSERVED_PUBLISHER_OR_RECOVERY_TERMINAL",
        "expected_terminal",
    ),
    (
        "WAIT_ORDER",
        "OBSERVED_EXACT_PUBLISHER_WAIT_REAP_ORDER",
        "expected_wait_order",
    ),
    (
        "EVIDENCE_ENVELOPE",
        "RETAINED_SINGLE_ENVELOPE_SCHEMA_HASH_BOUNDS_AND_REPLAY_INDEX",
        "evidence_envelope_schema",
    ),
    (
        "EXPECTED_RISK_LABEL",
        "RISK_LABEL_DERIVED_FROM_THE_ACTUAL_COMPLETE_HISTORY",
        "expected_risk_label",
    ),
)

CONDITIONAL_CONFORMANCE_CHECKS = (
    "PASSIVE_REAP_OBSERVER",
    "STAGE_CONTINUATION",
)
def conformance_check_registry() -> dict[str, Any]:
    return {
        "base_checks": {
            key: {
                "oracle_reference": oracle_reference,
                "verification_target": verification_target,
            }
            for key, verification_target, oracle_reference in BASE_CONFORMANCE_CHECKS
        },
        "conditional_checks": {
            "PASSIVE_REAP_OBSERVER": {
                "expected_full_conformance": "UNKNOWN",
                "oracle_reference": "status_coordinates/needed_evidence/PASSIVE_REAP_OBSERVER_WITH_FROZEN_SEMANTICS",
                "verification_target": "PASSIVE_NONPARTICIPATING_OBSERVATION_OF_PRE_RECOVERY_REAP_DELETION",
            },
            "STAGE_CONTINUATION": {
                "expected_full_conformance": "UNKNOWN",
                "oracle_reference": "status_coordinates/needed_evidence/CUT_CONTINUATION_WITHOUT_STAGE_CONTROLLER",
                "verification_target": "CUT_CONTINUATION_CAPABILITY_WITHOUT_THE_NAMED_STAGE_CONTROLLER",
            },
        },
        "dynamic_checks": {
            "COMPARISON_EDGE/<edge_id>": {
                "expected_full_conformance": "UNKNOWN iff the registered edge result is UNKNOWN; otherwise PASS",
                "oracle_reference": "comparison_edges/<edge_id>/expected_result",
                "verification_target": "ACTUAL_B_RESPONSE_EQUALITY_RESULT_FOR_<edge_id>",
            },
            "OPERATION_FACT/<operation>": {
                "expected_full_conformance": "PASS",
                "oracle_reference": "operation_expectations/<operation>",
                "verification_target": "ACTUAL_<operation>_EXPECTATION_ERRNO_CONFIGURED_SOURCE_AND_REQUIRED_EVIDENCE",
            },
        },
        "expected_full_conformance_domain": ["PASS", "UNKNOWN"],
        "identity_rule": "the pair (enclosing case_id, check_key); the concatenated display ID is MAY_REBUILD",
        "persisted_row_form": "ordered unique check_key strings only; target, reference, and status are rebuilt from this registry and registered edges",
        "sort_rule": "unsigned UTF-8 check_key bytes",
    }


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


def reached(body: dict[str, Any], slot: int) -> bool:
    """Whether work ending immediately before J<slot> is reached."""
    if body["history_production"] != "PUBLICATION":
        return False
    if body["manifest"] == "DROP_STAGE_CONTROLLER" and body["cut"] != "NORMAL":
        return False
    if body["family"] == "OCCUPIED_STAGING" and body["manifest"] == "REFERENCE":
        return slot == 1 and body["cut"] != "J0"
    if body["family"] == "WRAPPER_ERROR":
        terminal_slot = {
            "FILE_FSYNC_EIO": 3,
            "REPLACE_EIO": 4,
            "DIRECTORY_FSYNC_EIO": 5,
        }[body["injection"]]
        return slot <= terminal_slot
    if body["cut"] == "NORMAL":
        return True
    return int(body["cut"][1:]) >= slot


def fact(
    operation: str,
    expectation: str,
    *,
    configured_source: str,
    errno: str = "NONE",
    sources: tuple[str, ...] = ("INDEPENDENT_TRACE", "MECHANISM_MANIFEST", "SELF_REPORT"),
) -> dict[str, Any]:
    if operation not in OPERATION_ORDER or expectation not in OPERATION_EXPECTATIONS \
            or errno not in ERRNO_COORDINATES or configured_source not in CONFIGURED_SOURCES:
        raise ValueError((operation, expectation, configured_source, errno))
    if not sources or not set(sources) <= set(EVIDENCE_SOURCES):
        raise ValueError((operation, sources))
    return {
        "configured_source": configured_source,
        "errno": errno,
        "expectation": expectation,
        "operation": operation,
        "required_sources": sorted(sources),
    }


def filesystem_fact(
    body: dict[str, Any],
    operation: str,
    *,
    slot: int,
    omitted_manifest: str,
    simulated_injection: str,
) -> dict[str, Any]:
    configured_source = (
        "MANIFEST_BRANCH"
        if body["manifest"] == omitted_manifest
        else "PUBLISHER_WRAPPER"
        if body["injection"] == simulated_injection
        else "PUBLISHER_KERNEL"
    )
    if not reached(body, slot):
        return fact(operation, "NOT_REACHED", configured_source=configured_source)
    if body["manifest"] == omitted_manifest:
        return fact(operation, "OBSERVED_ABSENT", configured_source=configured_source)
    if body["injection"] == simulated_injection:
        return fact(
            operation,
            "SIMULATED_ERROR_WITHOUT_KERNEL_ENTRY",
            configured_source=configured_source,
            errno="EIO_5",
        )
    return fact(operation, "OBSERVED_SUCCESS", configured_source=configured_source)


def default_source(operation: str) -> str:
    return {
        "ACQUIRE_EXCLUSIVE": "PUBLISHER_KERNEL",
        "ACQUIRE_NONEXCLUSIVE": "PUBLISHER_KERNEL",
        "FILE_FSYNC": "PUBLISHER_KERNEL",
        "REPLACE": "PUBLISHER_KERNEL",
        "DIRECTORY_FSYNC": "PUBLISHER_KERNEL",
        "SELF_STOP_SIGNAL": "PUBLISHER_SELF_CUT",
        "CAUSAL_KILL_SIGNAL": "STAGE_CONTROLLER",
        "PUBLISHER_TERMINATION_OBSERVATION": "LIFECYCLE_SUPERVISOR",
        "EXACT_PUBLISHER_REAP": "PARENT_WAIT",
        "RECOVERY_EXEC": "RECOVERY_LAUNCHER",
    }[operation]


def operation_expectations(body: dict[str, Any]) -> list[dict[str, Any]]:
    if body["history_production"] == "RECOVERY_ONLY":
        values = [
            fact(
                name,
                "NOT_APPLICABLE",
                configured_source=default_source(name),
                sources=("SEMANTIC_DESCRIPTOR",),
            )
            for name in OPERATION_ORDER[:-1]
        ]
        values.append(
            fact(
                "RECOVERY_EXEC",
                "OBSERVED_SUCCESS",
                configured_source="RECOVERY_LAUNCHER",
                sources=("EXACT_PROCESS_IDENTITY", "EXEC_RECORD", "INDEPENDENT_TRACE"),
            )
        )
        return values

    control_unavailable = (
        body["manifest"] == "DROP_STAGE_CONTROLLER" and body["cut"] != "NORMAL"
    )
    if control_unavailable:
        return [
            fact(
                name,
                "CONTROL_UNAVAILABLE",
                configured_source=default_source(name),
                sources=("CONTROL_RECORD", "SEMANTIC_DESCRIPTOR"),
            )
            for name in OPERATION_ORDER
        ]

    acquisition_reached = reached(body, 1)
    nonexclusive = body["manifest"] == "NO_EXCLUSIVE_CREATE"
    occupied_reference = (
        body["family"] == "OCCUPIED_STAGING"
        and body["manifest"] == "REFERENCE"
        and acquisition_reached
    )
    acquisition_selected = "ACQUIRE_NONEXCLUSIVE" if nonexclusive else "ACQUIRE_EXCLUSIVE"
    acquisition_other = "ACQUIRE_EXCLUSIVE" if nonexclusive else "ACQUIRE_NONEXCLUSIVE"
    if not acquisition_reached:
        acquisition_value = fact(
            acquisition_selected,
            "NOT_REACHED",
            configured_source="PUBLISHER_KERNEL",
        )
    elif occupied_reference:
        acquisition_value = fact(
            acquisition_selected,
            "OBSERVED_KERNEL_ERROR",
            configured_source="PUBLISHER_KERNEL",
            errno="EEXIST_17",
        )
    else:
        acquisition_value = fact(
            acquisition_selected,
            "OBSERVED_SUCCESS",
            configured_source="PUBLISHER_KERNEL",
        )
    values = [
        acquisition_value,
        fact(
            acquisition_other,
            "NOT_SELECTED",
            configured_source="MANIFEST_BRANCH",
            sources=("MECHANISM_MANIFEST",),
        ),
        filesystem_fact(
            body,
            "FILE_FSYNC",
            slot=3,
            omitted_manifest="NO_FILE_FSYNC",
            simulated_injection="FILE_FSYNC_EIO",
        ),
        filesystem_fact(
            body,
            "REPLACE",
            slot=4,
            omitted_manifest="NO_REPLACE",
            simulated_injection="REPLACE_EIO",
        ),
        filesystem_fact(
            body,
            "DIRECTORY_FSYNC",
            slot=5,
            omitted_manifest="NO_DIRECTORY_FSYNC",
            simulated_injection="DIRECTORY_FSYNC_EIO",
        ),
    ]
    cut_reached = body["cut"].startswith("J") and body["cut_reachability"] == "REACHABLE"
    self_cut = body["manifest"] == "SELF_CUT"
    values.append(
        fact(
            "SELF_STOP_SIGNAL",
            "OBSERVED_SUCCESS" if self_cut and cut_reached else "NOT_REACHED" if self_cut else "NOT_SELECTED",
            configured_source="PUBLISHER_SELF_CUT" if self_cut else "MANIFEST_BRANCH",
            sources=("CONTROL_RECORD", "EXACT_PROCESS_IDENTITY", "INDEPENDENT_TRACE"),
        )
    )
    values.append(
        fact(
            "CAUSAL_KILL_SIGNAL",
            "OBSERVED_SUCCESS" if cut_reached else "NOT_REACHED",
            configured_source="LIFECYCLE_SUPERVISOR" if self_cut else "STAGE_CONTROLLER",
            sources=("CONTROL_RECORD", "EXACT_PROCESS_IDENTITY", "INDEPENDENT_TRACE"),
        )
    )
    values.append(
        fact(
            "PUBLISHER_TERMINATION_OBSERVATION",
            "OBSERVED_SUCCESS",
            configured_source=(
                "PIDFD_PROC_OBSERVER"
                if body["manifest"] == "NO_PRE_RECOVERY_REAP_BEHAVIORAL" and cut_reached
                else "LIFECYCLE_SUPERVISOR"
            ),
            sources=("EXACT_PROCESS_IDENTITY", "INDEPENDENT_TRACE", "TERMINATION_RECORD"),
        )
    )
    values.append(
        fact(
            "EXACT_PUBLISHER_REAP",
            "OBSERVED_SUCCESS",
            configured_source="PARENT_WAIT",
            sources=("EXACT_PROCESS_IDENTITY", "INDEPENDENT_TRACE", "WAIT_RECORD"),
        )
    )
    values.append(
        fact(
            "RECOVERY_EXEC",
            "OBSERVED_SUCCESS",
            configured_source="RECOVERY_LAUNCHER",
            sources=("EXACT_PROCESS_IDENTITY", "EXEC_RECORD", "INDEPENDENT_TRACE"),
        )
    )
    return sorted(values, key=lambda item: OPERATION_ORDER.index(item["operation"]))


def checkpoint_slots(body: dict[str, Any]) -> list[str]:
    if body["history_production"] != "PUBLICATION":
        return []
    if body["manifest"] == "DROP_STAGE_CONTROLLER" and body["cut"] != "NORMAL":
        return []
    if body["family"] == "OCCUPIED_STAGING" and body["manifest"] == "REFERENCE" \
            and body["cut"] != "J0":
        return ["J0"]
    if body["family"] == "WRAPPER_ERROR":
        last = {"FILE_FSYNC_EIO": 2, "REPLACE_EIO": 3, "DIRECTORY_FSYNC_EIO": 4}[body["injection"]]
    elif body["cut"] == "NORMAL":
        last = 5
    else:
        last = int(body["cut"][1:])
    return [f"J{slot}" for slot in range(last + 1)]


def status_coordinates(body: dict[str, Any]) -> dict[str, Any]:
    control_unavailable = (
        body["manifest"] == "DROP_STAGE_CONTROLLER" and body["cut"] != "NORMAL"
    )
    reaping_unknown = body["manifest"] == "NO_PRE_RECOVERY_REAP_BEHAVIORAL"
    scopes = ["L_EVIDENCE", "GUEST_REALIZATION"]
    if body["cut"].startswith("J"):
        scopes.append("B_PROCESS_KILL")
    scopes.sort(key=STATUS_ENUMS["scope"].index)
    needed: list[str] = []
    if control_unavailable:
        needed.append("CUT_CONTINUATION_WITHOUT_STAGE_CONTROLLER")
    if reaping_unknown:
        needed.append("PASSIVE_REAP_OBSERVER_WITH_FROZEN_SEMANTICS")
    return {
        "applicability": "APPLICABLE",
        "behavioral_comparison": "NOT_COMPARED",
        "execution": "CONTROL_UNAVAILABLE" if control_unavailable else "COMPLETE",
        "failure_reasons": [],
        "full_conformance": "UNKNOWN" if control_unavailable or reaping_unknown else "PASS",
        "needed_evidence": sorted(needed),
        "oracle": "ASSERTED",
        "scope": scopes,
    }


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
        expected = record_fault_oracle(body)
    else:
        expected = publication_oracle(body)
    expected.pop("execution_applicability")
    publish_result = expected.pop("expected_publish_result_hex")
    recovery_observation = expected.pop("expected_recovery_hex")
    control_unavailable = (
        body["manifest"] == "DROP_STAGE_CONTROLLER" and body["cut"] != "NORMAL"
    )
    if control_unavailable:
        if publish_result != NO_CROSSING or recovery_observation != NO_OBSERVATION:
            raise ValueError("control-unavailable oracle fabricated a B observation")
        b_expectation = {
            "kind": "NO_B_HISTORY",
            "reason": "CONTROL_UNAVAILABLE",
        }
    else:
        if recovery_observation == NO_OBSERVATION:
            raise ValueError("executed subject row lacks a recovery observation")
        b_expectation = {
            "history_production": body["history_production"],
            "kind": "EXACT",
            "publish_result_hex_list": (
                [] if publish_result == NO_CROSSING else [publish_result]
            ),
            "recovery_observation_hex": recovery_observation,
        }
    expected.update(
        {
            "b_expectation": b_expectation,
            "cut_reachability": body["cut_reachability"],
            "expected_checkpoint_slots": checkpoint_slots(body),
            "operation_expectations": operation_expectations(body),
            "status_coordinates": status_coordinates(body),
        }
    )
    return expected


def comparison_key(body: dict[str, Any], ignored: set[str]) -> bytes:
    return canonical_json({key: value for key, value in body.items() if key not in ignored})


def expected_edge_result(
    left_expected: dict[str, Any], right_expected: dict[str, Any]
) -> str:
    if "NO_B_HISTORY" in {
        left_expected["b_expectation"]["kind"],
        right_expected["b_expectation"]["kind"],
    }:
        return "UNKNOWN"
    left_response = left_expected["b_expectation"]
    right_response = right_expected["b_expectation"]
    return "MATCH" if left_response == right_response else "DIFFER"


def build_comparison_edges(
    row_work: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, list[str]], dict[str, list[str]]]:
    by_case = {row["case_id"]: row for row in row_work}
    cross_backend: dict[bytes, list[dict[str, Any]]] = {}
    reference_index: dict[bytes, list[dict[str, Any]]] = {}
    for row in row_work:
        body = row["body"]
        cross_backend.setdefault(comparison_key(body, {"backend"}), []).append(row)
        if body["manifest"] == "REFERENCE":
            normalized = dict(body)
            normalized["comparison_rules"] = []
            normalized.pop("cut_reachability")
            reference_index.setdefault(canonical_json(normalized), []).append(row)

    edge_work: dict[str, dict[str, Any]] = {}
    incident: dict[str, list[str]] = {case_id: [] for case_id in by_case}
    incident_results: dict[str, list[str]] = {case_id: [] for case_id in by_case}

    def add(left: dict[str, Any], right: dict[str, Any], relation: str) -> None:
        left_id, right_id = sorted((left["case_id"], right["case_id"]))
        identity = {
            "left_case_id": left_id,
            "relation": relation,
            "right_case_id": right_id,
            "scope": "B_RESPONSE_EQUALITY",
        }
        edge_id = "r01b-edge-" + hashlib.sha256(EDGE_TAG + tv(identity)).hexdigest()
        result = expected_edge_result(by_case[left_id]["expected"], by_case[right_id]["expected"])
        edge = {
            "edge_id": edge_id,
            "expected_result": result,
            "identity": identity,
            "smallest_witness_order": [
                "crossing_count",
                "input_bytes",
                "cut_ordinal",
                "fault_ordinal",
                "canonical_record_unsigned_lex",
            ],
        }
        previous = edge_work.setdefault(edge_id, edge)
        if previous != edge:
            raise ValueError("comparison edge-id collision")
        for case_id in (left_id, right_id):
            if edge_id not in incident[case_id]:
                incident[case_id].append(edge_id)
                incident_results[case_id].append(result)

    for group in cross_backend.values():
        if len(group) != 2 or {row["body"]["backend"] for row in group} != {"E", "T"}:
            raise ValueError("cross-backend comparison group is not an exact pair")
        add(group[0], group[1], "CROSS_BACKEND_SAME_SYMBOLIC_ROW")

    for row in row_work:
        body = row["body"]
        if "PAIR_REFERENCE_SAME_BACKEND" not in body["comparison_rules"]:
            continue
        normalized = dict(body)
        normalized["manifest"] = "REFERENCE"
        normalized["comparison_rules"] = []
        normalized.pop("cut_reachability")
        if normalized["family"] == "STAGE_CONTROL":
            normalized["family"] = "CLEAN_MECHANISM"
        candidates = reference_index.get(canonical_json(normalized), [])
        if len(candidates) != 1:
            raise ValueError(f"reference comparison is not unique: {row['case_id']}")
        add(row, candidates[0], "PAIR_REFERENCE_SAME_BACKEND")

    for case_id in incident:
        incident[case_id].sort()
    edges = sorted(edge_work.values(), key=lambda edge: edge["edge_id"])
    return edges, incident, incident_results


def aggregate_behavior(results: list[str]) -> str:
    if "DIFFER" in results:
        return "DIFFER"
    if "UNKNOWN" in results:
        return "UNKNOWN"
    if results:
        return "MATCH"
    return "NOT_COMPARED"


def expected_check_status(
    check_key: str,
    incident_edge_results: dict[str, str],
) -> str:
    if check_key in CONDITIONAL_CONFORMANCE_CHECKS:
        return "UNKNOWN"
    if check_key.startswith("COMPARISON_EDGE/"):
        edge_id = check_key.removeprefix("COMPARISON_EDGE/")
        if edge_id not in incident_edge_results:
            raise ValueError(f"unregistered incident comparison check: {check_key}")
        return "UNKNOWN" if incident_edge_results[edge_id] == "UNKNOWN" else "PASS"
    return "PASS"


def aggregate_full_conformance(
    check_keys: list[str],
    incident_edge_results: dict[str, str],
) -> str:
    if not check_keys:
        raise ValueError("a row cannot aggregate an empty conformance-check set")
    statuses = [expected_check_status(key, incident_edge_results) for key in check_keys]
    if not set(statuses) <= {"PASS", "UNKNOWN"}:
        raise ValueError(
            "the frozen subject check domain permits only PASS or UNKNOWN: "
            f"{statuses}"
        )
    for status in FULL_CONFORMANCE_PRECEDENCE:
        if status in statuses:
            return status
    raise ValueError("full-conformance precedence does not cover check statuses")


def conformance_check_keys(
    body: dict[str, Any],
    expected: dict[str, Any],
    incident_edge_results: dict[str, str],
) -> list[str]:
    keys: list[str] = []

    def add(check_key: str) -> None:
        try:
            encoded_key = check_key.encode("utf-8", "strict")
        except UnicodeEncodeError as error:
            raise ValueError(f"non-UTF-8 conformance-check key: {check_key!r}") from error
        if not encoded_key:
            raise ValueError("conformance check key must be nonempty")
        keys.append(check_key)

    for check_key, _, _ in BASE_CONFORMANCE_CHECKS:
        add(check_key)

    operation_facts = expected["operation_expectations"]
    if [item["operation"] for item in operation_facts] != list(OPERATION_ORDER):
        raise ValueError("operation expectations are not the exact registered domain")
    for operation in OPERATION_ORDER:
        add(f"OPERATION_FACT/{operation}")

    if not incident_edge_results:
        raise ValueError("every subject row requires a registered comparison edge")
    for edge_id, literal_result in incident_edge_results.items():
        if literal_result not in STATUS_ENUMS["behavioral_comparison"][:-1]:
            raise ValueError(f"invalid literal comparison-edge result: {literal_result}")
        add(f"COMPARISON_EDGE/{edge_id}")

    if expected["status_coordinates"]["execution"] == "CONTROL_UNAVAILABLE":
        add("STAGE_CONTINUATION")
    if body["manifest"] == "NO_PRE_RECOVERY_REAP_BEHAVIORAL":
        add("PASSIVE_REAP_OBSERVER")

    keys.sort(key=lambda key: key.encode("utf-8"))
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate row-local conformance-check key")
    for key in keys:
        if expected_check_status(key, incident_edge_results) not in {"PASS", "UNKNOWN"}:
            raise ValueError("invalid rebuilt conformance-check status")
    return keys


def descriptor_view(item: dict[str, Any]) -> dict[str, Any]:
    """Independent V2 symbolic-row projection used only by the oracle."""
    identity = item["identity"]
    metadata = item["metadata"]
    view: dict[str, Any] = {
        "backend": identity["backend"],
        "comparison_rules": metadata["comparison_rules"],
        "continuation_hex": identity["continuation_hex"],
        "cut_reachability": metadata["cut_reachability"],
        "family": metadata["family"],
        "history_production": identity["history_production"],
        "manifest": identity["mechanism_manifest"],
        "observer_profile": identity["observer_profile"],
        "origin": metadata["origin"],
        "repetition": identity["repetition"],
    }
    if identity["history_production"] == "PUBLICATION":
        setup = identity["setup"]
        view.update(
            {
                "base_record_payload_hex": "",
                "case": "CREATE" if setup.startswith("ABSENT") else "UPDATE",
                "cut": identity["cut"],
                "injection": identity["injected_fault"],
                "mutation": "NONE",
                "mutation_arg0": -1,
                "mutation_arg1": -1,
                "mutation_target_payload_hex": "",
                "publish_payload_hex": identity["requested_payload_hex"],
                "setup": setup,
            }
        )
    elif identity["history_production"] == "RECOVERY_ONLY":
        recipe = identity["recovery_fixture_recipe"]
        view.update(
            {
                "base_record_payload_hex": recipe["base_record_payload_hex"],
                "case": "RECOVERY_ONLY",
                "cut": "RECOVERY_ONLY",
                "injection": "NONE",
                "mutation": recipe["mutation"],
                "mutation_arg0": recipe["arg0"],
                "mutation_arg1": recipe["arg1"],
                "mutation_target_payload_hex": recipe["target_payload_hex"],
                "publish_payload_hex": "",
                "setup": "INSTALLED_MUTATED_RECORD",
            }
        )
    else:
        raise ValueError(identity["history_production"])
    return view


def build_oracle(descriptor_package: dict[str, Any]) -> dict[str, Any]:
    if descriptor_package.get("schema_id") != "R01B-SYMBOLIC-DESCRIPTORS-2":
        raise ValueError("wrong descriptor schema")
    row_work: list[dict[str, Any]] = []
    previous = ""
    for case_ordinal, item in enumerate(descriptor_package["rows"]):
        body = descriptor_view(item)
        case_id = "r01b-case-" + hashlib.sha256(
            CASE_TAG + tv(item["identity"])
        ).hexdigest()
        if case_id != item["case_id"] or case_ordinal != item["case_ordinal"]:
            raise ValueError("descriptor identity mismatch")
        if previous and case_id <= previous:
            raise ValueError("descriptor order mismatch")
        previous = case_id
        row_work.append(
            {
                "body": body,
                "case_id": case_id,
                "case_ordinal": case_ordinal,
                "expected": expected_for(body),
            }
        )
    if len(row_work) != 3028:
        raise AssertionError(len(row_work))
    edges, incident, incident_results = build_comparison_edges(row_work)
    edges_by_id = {edge["edge_id"]: edge for edge in edges}
    if len(edges_by_id) != len(edges):
        raise ValueError("duplicate comparison edge ID")
    rows: list[dict[str, Any]] = []
    total_check_count = 0
    for row in row_work:
        case_id = row["case_id"]
        expected = row["expected"]
        expected["comparison_edge_ids"] = incident[case_id]
        expected["status_coordinates"]["behavioral_comparison"] = aggregate_behavior(
            incident_results[case_id]
        )
        edge_results = {
            edge_id: edges_by_id[edge_id]["expected_result"]
            for edge_id in incident[case_id]
        }
        expected["conformance_check_keys"] = conformance_check_keys(
            row["body"],
            expected,
            edge_results,
        )
        total_check_count += len(expected["conformance_check_keys"])
        aggregate = aggregate_full_conformance(
            expected["conformance_check_keys"], edge_results
        )
        if aggregate != expected["status_coordinates"]["full_conformance"]:
            raise ValueError(
                f"full-conformance aggregate mismatch for {case_id}: "
                f"{aggregate} != "
                f"{expected['status_coordinates']['full_conformance']}"
            )
        rows.append(
            {
                "case_id": case_id,
                "expected": expected,
            }
        )
    return {
        "comparison_edge_count": len(edges),
        "comparison_edges": edges,
        "conformance_check_count": total_check_count,
        "conformance_check_registry": conformance_check_registry(),
        "descriptor_stream_sha256": hashlib.sha256(
            canonical_json(descriptor_package)
        ).hexdigest(),
        "oracle_independence_boundary": (
            "literal labels only; no subject record encoder, parser, adapter, "
            "publisher, recovery, or normalizer import"
        ),
        "row_count": len(rows),
        "rows": rows,
        "schema_id": "R01B-LITERAL-ORACLE-2",
        "status_registry_source": {
            "schema_id": STATUS_REGISTRY["schema_id"],
            "sha256": STATUS_REGISTRY_SHA256,
        },
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
