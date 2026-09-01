#!/usr/bin/env python3
"""Generate the deterministic R0.1B LAB_ONLY holdout registry.

The registry is pre-subject evidence.  Its case identity covers only the
submitted LAB_ONLY input body.  Expected answers, status coordinates, and
source-case digests are deliberately outside that identity.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
BREAKER = HERE / "R01-BREAKER-OBJECT.json"
MEASUREMENTS = HERE / "R01B-MEASUREMENT-REGISTRY.json"
SUITE = HERE / "R01B-SUITE.json"
CORRECTION = HERE / "REALIZATION-CORRECTION-R01B.md"
STATUS_REGISTRY = HERE / "R01B-STATUS-REGISTRY.json"
OUTPUT = HERE / "R01B-HOLDOUTS.json"

BREAKER_SHA256 = "99f81a9a4d4f4bf55109a9f43b7cd361c887c9b0b7255a22d009767238e79dfa"
MEASUREMENT_SHA256 = "854abc48e8e610f9487e07c7c81ed64a32772836d70fc08e40cb3d8b72f6223d"
MEASUREMENT_PATH_COUNT = 1040
SUITE_SHA256 = "6f4a1b4588ff4218fff0cd75744d1e8ca2b31c9a9e401334f5d1c746d84cb5cc"
STATUS_REGISTRY_SHA256 = "3cd692eeebaeb55497bd73bc5e21156e6a706eef7a2b75c4f2e9316c2e2892d9"
CASE_TAG = b"ZGR01B-CASE\x00"
SCHEMA_ID = "R01B-LAB-HOLDOUTS-1"
MEASUREMENT_FIXTURE_RECIPE_ID = "R01B-SCHEMA-COMPLETE-MEASUREMENT-S0-1"

_status_registry_raw = STATUS_REGISTRY.read_bytes()
if hashlib.sha256(_status_registry_raw).hexdigest() != STATUS_REGISTRY_SHA256:
    raise ValueError("pinned input changed: R01B-STATUS-REGISTRY.json")
STATUS_AUTHORITY = json.loads(_status_registry_raw)
STATUS_TABLES: dict[str, tuple[int, tuple[str, ...]]] = {}
for _name, _registry in STATUS_AUTHORITY["status_coordinate_registry"].items():
    _codes = _registry["codes"]
    if [item["code"] for item in _codes] != list(range(len(_codes))):
        raise ValueError(f"noncontiguous status codes in common registry: {_name}")
    STATUS_TABLES[_name] = (
        _registry["namespace"],
        tuple(item["label"] for item in _codes),
    )
FAILURE_REASON_REGISTRY = tuple(STATUS_AUTHORITY["failure_reason_registry"])
if [item["code"] for item in FAILURE_REASON_REGISTRY] != list(
    range(len(FAILURE_REASON_REGISTRY))
):
    raise ValueError("noncontiguous failure codes in common registry")
FAILURE_REASON_CODES = {
    item["label"]: item["code"] for item in FAILURE_REASON_REGISTRY
}


@dataclass(frozen=True)
class ClosedEnumValue:
    namespace: int
    code: int


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def tv(value: Any) -> bytes:
    if isinstance(value, ClosedEnumValue):
        if not 0 <= value.namespace <= 0xFFFF or not 0 <= value.code <= 0xFFFF:
            raise ValueError("closed enum namespace/code out of range")
        return b"\x0b" + struct.pack(">HH", value.namespace, value.code)
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
        return b"\x07" + struct.pack(">Q", len(value)) + b"".join(tv(item) for item in value)
    if isinstance(value, dict):
        keys = sorted(value, key=lambda item: item.encode("ascii"))
        parts = [b"\x08", struct.pack(">Q", len(keys))]
        for key in keys:
            encoded = key.encode("ascii")
            if not encoded or len(encoded) > 0xFFFF or not all(32 <= byte <= 126 for byte in encoded):
                raise ValueError(f"invalid map key: {key!r}")
            parts.extend((struct.pack(">H", len(encoded)), encoded, tv(value[key])))
        return b"".join(parts)
    raise TypeError(type(value).__name__)


def read_pinned(path: Path, expected_sha256: str) -> tuple[bytes, Any]:
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"pinned input changed: {path.name}: {actual}")
    return raw, json.loads(raw)


def enum_coordinate(name: str, label: str) -> dict[str, Any]:
    namespace, labels = STATUS_TABLES[name]
    try:
        code = labels.index(label)
    except ValueError as error:
        raise ValueError(f"unknown {name} status: {label}") from error
    return {"code": code, "label": label, "namespace": namespace}


def wire_enum(name: str, label: str) -> ClosedEnumValue:
    coordinate = enum_coordinate(name, label)
    return ClosedEnumValue(coordinate["namespace"], coordinate["code"])


def failure_reason(label: str) -> dict[str, Any]:
    return {"code": FAILURE_REASON_CODES[label], "label": label}


def structured_unknown_bytes(reason: str, needed_evidence: str) -> bytes:
    if not reason or not needed_evidence:
        raise ValueError("structured UNKNOWN members must be nonempty")
    return b"\x09" + tv(reason) + tv(needed_evidence)


def structured_unsupported_bytes(reason: str) -> bytes:
    if not reason:
        raise ValueError("structured UNSUPPORTED reason must be nonempty")
    return b"\x0a" + tv(reason)


def measurement_fixture_binding() -> dict[str, Any]:
    """Name the symbolic S0 recipe without pretending S1 bytes exist."""
    recipe = measurement_fixture_recipe()
    return {
        "recipe_id": MEASUREMENT_FIXTURE_RECIPE_ID,
        "recipe_sha256": hashlib.sha256(canonical_json(recipe)).hexdigest(),
    }


def measurement_fixture_recipe() -> dict[str, Any]:
    return {
        "exact_materialized_bytes_present": False,
        "execution_gate": "FORBIDDEN_UNTIL_S1_EXACT_FIXTURE_IS_RETAINED",
        "materialization_status": "OPEN",
        "measurement_registry_sha256": MEASUREMENT_SHA256,
        "role": "SYMBOLIC_SCHEMA_COMPLETE_BASE_FIXTURE",
        "retention_requirement": "S1 MUST retain the exact canonical base-fixture bytes and SHA-256 before any mutation row executes",
    }


def expected_record(
    *,
    full_conformance: str,
    applicability: str = "APPLICABLE",
    execution: str = "COMPLETE",
    oracle: str = "ASSERTED",
    scopes: Iterable[str] = ("L_EVIDENCE",),
    failures: Iterable[str] = (),
    needed_evidence: Iterable[str] = (),
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    failure_labels = sorted(set(failures))
    needed = sorted(set(needed_evidence), key=lambda item: item.encode("utf-8"))
    if (full_conformance == "FAIL") != bool(failure_labels):
        raise ValueError("failure_reasons must be nonempty iff full conformance is FAIL")
    scope_coordinates = sorted(
        (enum_coordinate("scope", label) for label in set(scopes)),
        key=lambda item: item["code"],
    )
    result: dict[str, Any] = {
        "failure_reasons": [failure_reason(label) for label in failure_labels],
        "needed_evidence": needed,
        "status_coordinates": {
            "applicability": enum_coordinate("applicability", applicability),
            "behavioral_comparison": enum_coordinate("behavioral_comparison", "NOT_COMPARED"),
            "execution": enum_coordinate("execution", execution),
            "full_conformance": enum_coordinate("full_conformance", full_conformance),
            "oracle": enum_coordinate("oracle", oracle),
            "scope": scope_coordinates,
        },
    }
    if details is not None:
        result["details"] = details
    return result


def lab_body(*, logical_id: str, family: str, attack_kind: str, fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "attack_kind": attack_kind,
        "b_comparison_eligibility": "FORBIDDEN",
        "b_crossing_count": 0,
        "b_state_verdict_eligibility": "FORBIDDEN",
        "family": family,
        "fixture": fixture,
        "history_production": "LAB_ONLY",
        "logical_id": logical_id,
        "origin": "R01B",
        "repetition": 0,
        "semantic_profile": "R01B",
    }


def source_input(case: dict[str, Any]) -> dict[str, Any]:
    """Retain the submitted L record, excluding its oracle and interpretation."""
    crossings = [
        crossing for crossing in case["ordered_boundary_crossings"]
        if not crossing.startswith("expected_recovery(")
    ]
    return {
        "declared_mutation": case["declared_mutation"],
        "initial_entries": case["initial_entries"],
        "operation_facts": case["operation_facts"],
        "ordered_boundary_crossings": crossings,
        "profile": case["profile"],
    }


def conditional_source_input(case: dict[str, Any]) -> dict[str, Any]:
    """Retain a not-yet-executed input template without oracle responses."""
    result = source_input(case)
    result.pop("operation_facts")
    result["ordered_boundary_crossings"] = [
        crossing for crossing in result["ordered_boundary_crossings"]
        if not crossing.startswith(("recovery(", "wait(", "publisher_terminal("))
    ]
    return result


def source_oracle(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_expected_full_verdict": case["expected_full_verdict"],
        "source_expected_recovery_hex": case["expected_recovery_hex"],
        "source_only_permitted_claim": case["only_permitted_claim"],
    }


def conditional_source_oracle(case: dict[str, Any]) -> dict[str, Any]:
    result = source_oracle(case)
    result["conditional_expected_operation_facts"] = case["operation_facts"]
    result["conditional_response_crossings"] = [
        crossing for crossing in case["ordered_boundary_crossings"]
        if crossing.startswith(("expected_recovery(", "recovery(", "wait(", "publisher_terminal("))
    ]
    return result


def historical_provenance(
    case: dict[str, Any], index: int, *, relation: str = "ONE_TO_ONE_CANONICALIZATION"
) -> dict[str, Any]:
    return {
        "artifact": "R01-BREAKER-OBJECT.json",
        "artifact_sha256": BREAKER_SHA256,
        "mapping_relation": relation,
        "source_case_id": case["id"],
        "source_case_index": index,
        "source_case_sha256": hashlib.sha256(canonical_json(case)).hexdigest(),
    }


def measurement_provenance(**extra: Any) -> dict[str, Any]:
    result = {
        "artifact": "R01B-MEASUREMENT-REGISTRY.json",
        "artifact_sha256": MEASUREMENT_SHA256,
        "mapping_relation": "MECHANICAL_CLOSED_DOMAIN_EXPANSION",
    }
    result.update(extra)
    return result


def correction_provenance(section: str) -> dict[str, Any]:
    raw = CORRECTION.read_bytes()
    return {
        "artifact": CORRECTION.name,
        "artifact_sha256": hashlib.sha256(raw).hexdigest(),
        "mapping_relation": "CORRECTION_PROFILE_REQUIRED_HOLDOUT",
        "section": section,
    }


def replay_material() -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, bytes], bytes]:
    indexed_s0 = {
        "case": "REPLAY_SOURCE_RECORD",
        "history_production": "LAB_ONLY",
        "origin": "R01B_HOLDOUT_REPLAY_FIXTURE",
        "repetition": 0,
        "semantic_profile": "R01B",
    }
    indexed_case_id = "r01b-case-" + hashlib.sha256(
        CASE_TAG + tv(indexed_s0)
    ).hexdigest()
    streams = {
        "canonical_records": b"R01B-HOLDOUT-REPLAY-RECORD\x00",
        "inventory_pack": b"holdout-inventory\x00",
        "raw_measurement_pack": b"holdout-measurement\x00",
        "raw_trace_pack": b"holdout-trace\x00",
    }
    indexed_d0 = {
        "backend": "LAB_REPLAY_FIXTURE",
        "case_id": indexed_case_id,
        "cut": "NOT_APPLICABLE",
        "exact_lab_input": {
            "stream_inventory": [
                {
                    "length": len(stream_bytes),
                    "sha256": hashlib.sha256(stream_bytes).hexdigest(),
                    "stream": stream_name,
                }
                for stream_name, stream_bytes in sorted(streams.items())
            ],
        },
        "history_production": "LAB_ONLY",
        "injected_fault": "NONE",
        "mechanism_manifest": "LAB_REPLAY_FIXTURE",
        "repetition": 0,
    }
    trial_digest = hashlib.sha256(b"ZGR01B-TRIAL\x00" + tv(indexed_d0)).digest()
    envelope_map = {
        **streams,
        "status_coordinates": {
            "applicability": wire_enum("applicability", "APPLICABLE"),
            "behavioral_comparison": wire_enum("behavioral_comparison", "NOT_COMPARED"),
            "execution": wire_enum("execution", "COMPLETE"),
            "full_conformance": wire_enum("full_conformance", "UNKNOWN"),
            "oracle": wire_enum("oracle", "NOT_DECLARED"),
            "scope": [wire_enum("scope", "L_EVIDENCE")],
        },
    }
    envelope = b"ZGR01B-ENVELOPE\x00" + struct.pack(">H", 1) + tv(envelope_map)
    selectors = [
        {
            "length": len(stream_bytes),
            "offset": 0,
            "ordinal": 0,
            "record_sha256": hashlib.sha256(stream_bytes).hexdigest(),
            "stream": stream_name,
            "trial_id": "r01b-" + trial_digest.hex(),
        }
        for stream_name, stream_bytes in sorted(streams.items())
    ]
    replay_index = {
        "descriptor_identity": indexed_d0,
        "entries": selectors,
        "ordered_trial_ids": [selectors[0]["trial_id"]],
        "stream_sha256_by_name": {
            stream_name: hashlib.sha256(stream_bytes).hexdigest()
            for stream_name, stream_bytes in sorted(streams.items())
        },
        "symbolic_case_body": indexed_s0,
    }
    return selectors, replay_index, streams, envelope


def required_members(schema: Any, location: str = "$") -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    if not isinstance(schema, dict):
        return result
    if schema.get("type") == "object":
        for member in schema.get("required", []):
            result.append((location, member))
        for name, child in sorted(schema.get("properties", {}).items()):
            result.extend(required_members(child, f"{location}.{name}"))
    elif schema.get("type") == "array":
        result.extend(required_members(schema.get("items", {}), f"{location}[]"))
    return result


def default_source_specs() -> dict[int, dict[str, Any]]:
    return {
        0: {"logical_id": "FALSE_ATTEST_FILE_FSYNC", "family": "COMPARATOR_HELD_OUT", "full": "FAIL", "failures": ["FALSE_SUCCESS_ATTESTATION_FILE_FSYNC"]},
        1: {"logical_id": "FALSE_ATTEST_DIRECTORY_FSYNC", "family": "COMPARATOR_HELD_OUT", "full": "FAIL", "failures": ["FALSE_SUCCESS_ATTESTATION_DIRECTORY_FSYNC"]},
        2: {"logical_id": "FALSE_ATTEST_REPLACE", "family": "COMPARATOR_HELD_OUT", "full": "FAIL", "failures": ["FALSE_SUCCESS_ATTESTATION_REPLACE", "SEMANTIC_MISMATCH"]},
        3: {"logical_id": "FALSE_ATTEST_EXCLUSIVE_CREATE", "family": "COMPARATOR_HELD_OUT", "full": "FAIL", "failures": ["FALSE_SUCCESS_ATTESTATION_EXCLUSIVE_CREATE"]},
        5: {"logical_id": "KILL_EXIT_NEGATIVE", "family": "COMPARATOR_HELD_OUT", "full": "FAIL", "failures": ["KILL_NOT_CAUSAL"]},
        6: {"logical_id": "KILL_OVERRUN_NEGATIVE", "family": "COMPARATOR_HELD_OUT", "full": "FAIL", "failures": ["CUT_OVERRUN"]},
        7: {"logical_id": "REAP_ORDER_REFERENCE_FORGERY_NEGATIVE", "family": "REAPING", "full": "FAIL", "failures": ["RECOVERY_BEFORE_REAP"]},
        8: {"logical_id": "STALE_EMPTY_COLLISION_REFERENCE", "family": "COMPARATOR_HELD_OUT", "full": "PASS"},
        12: {"logical_id": "SELECT_OMIT_NEGATIVE", "family": "SELECTION", "full": "FAIL", "failures": ["SELECTION_MISSING", "SEMANTIC_MISMATCH"]},
        15: {"logical_id": "ADAPTER_TIMEOUT", "family": "ADAPTER", "full": "PASS"},
        16: {"logical_id": "ADAPTER_SIGNAL_15", "family": "ADAPTER", "full": "PASS"},
        17: {"logical_id": "RECOVERY_SIGNAL_9", "family": "ADAPTER", "full": "FAIL", "failures": ["MISSING_RECOVERY_OBSERVATION"]},
        18: {"logical_id": "ENV_PARENT_X_PAIR", "family": "ENVIRONMENT", "full": "PASS"},
    }


def build_package() -> dict[str, Any]:
    _, breaker = read_pinned(BREAKER, BREAKER_SHA256)
    _, measurements = read_pinned(MEASUREMENTS, MEASUREMENT_SHA256)
    _, suite = read_pinned(SUITE, SUITE_SHA256)
    cases = breaker["cases"]
    paths = measurements["paths"]
    if len(cases) != 22 or len({case["id"] for case in cases}) != 22:
        raise ValueError("breaker case domain is not the pinned 22-case domain")
    if len(paths) != MEASUREMENT_PATH_COUNT or len(paths) != len(set(paths)) or paths != sorted(paths):
        raise ValueError("measurement path domain is not the sorted 1,040-path V2 domain")

    pending: list[dict[str, Any]] = []

    def add(body: dict[str, Any], expected: dict[str, Any], provenance: list[dict[str, Any]]) -> None:
        pending.append({"body": body, "expected": expected, "provenance": provenance})

    for index, spec in default_source_specs().items():
        case = cases[index]
        fixture = source_input(case)
        if index == 15:
            fixture["injection_configuration"] = {
                "timeout_deadline_ns": suite["adapter_fault_futures"]["timeout_deadline_ns"]
            }
        elif index == 16:
            fixture["injection_configuration"] = {"signal": 15}
        elif index == 18:
            fixture["selected_subject_environment"] = suite["selected_subject_environment"]
        elif index == 7:
            fixture["mechanism_manifest"] = "REFERENCE"
        add(
            lab_body(
                logical_id=spec["logical_id"],
                family=spec["family"],
                attack_kind=case["declared_mutation"],
                fixture={"submitted_l_record": fixture},
            ),
            expected_record(
                full_conformance=spec["full"],
                failures=spec.get("failures", []),
                details=source_oracle(case),
            ),
            [historical_provenance(case, index)],
        )

    # Historical deletion probes have a retained oracle but no supplied 28-row
    # execution evidence in this LAB_ONLY registry.  Keep that gap explicit.
    for index, logical_id in ((9, "NO_FILE_FSYNC_FULL_MATRIX_CONDITIONAL"), (10, "NO_DIRECTORY_FSYNC_FULL_MATRIX_CONDITIONAL")):
        case = cases[index]
        add(
            lab_body(
                logical_id=logical_id,
                family="DELETION_COMPARISON",
                attack_kind=case["declared_mutation"],
                fixture={"conditional_l_history_template": conditional_source_input(case)},
            ),
            expected_record(
                applicability="CONDITIONAL_ONLY",
                execution="NOT_RUN",
                oracle="CONDITIONAL_RETAINED",
                full_conformance="UNKNOWN",
                scopes=("L_EVIDENCE", "CONDITIONAL_FUTURE"),
                needed_evidence=("complete legal 28-row trace and recovery matrix",),
                details=conditional_source_oracle(case),
            ),
            [historical_provenance(case, index, relation="CONDITIONAL_ORACLE_WITHOUT_EXECUTION_EVIDENCE")],
        )

    power = cases[11]
    add(
        lab_body(
            logical_id="POWER_GUARD",
            family="PHYSICAL_GUARD",
            attack_kind=power["declared_mutation"],
            fixture={"conditional_l_history_template": conditional_source_input(power)},
        ),
        expected_record(
            applicability="UNSUPPORTED_HERE",
            execution="NOT_RUN",
            oracle="CONDITIONAL_RETAINED",
            full_conformance="UNSUPPORTED",
            scopes=("PHYSICAL_OR_POWER",),
            needed_evidence=("identified physical realization with controlled total power loss and independent cold readback",),
            details=conditional_source_oracle(power),
        ),
        [historical_provenance(power, 11, relation="EXPLICIT_UNSUPPORTED_PHYSICAL_GUARD")],
    )

    for index, logical_id in ((13, "SELECT_ALT_PRE"), (14, "SELECT_ALT_POST")):
        case = cases[index]
        add(
            lab_body(
                logical_id=logical_id,
                family="SELECTION",
                attack_kind=case["declared_mutation"],
                fixture={"conditional_l_history_template": conditional_source_input(case)},
            ),
            expected_record(
                applicability="UNSUPPORTED_HERE",
                execution="NOT_RUN",
                oracle="CONDITIONAL_RETAINED",
                full_conformance="NOT_APPLICABLE",
                scopes=("CONDITIONAL_FUTURE",),
                needed_evidence=("frozen applicable opaque alternative selection realization",),
                details=conditional_source_oracle(case),
            ),
            [historical_provenance(case, index, relation="EXPLICIT_UNBUILT_ALTERNATIVE")],
        )

    legacy = cases[4]
    legacy_fixture = source_input(legacy)
    legacy_fixture["legacy_frames_hex"] = ["a000", "a000"]
    add(
        lab_body(
            logical_id="LEGACY_A000_DUPLICATE_NEGATIVE",
            family="CONTROL_PROTOCOL",
            attack_kind="DUPLICATE_LEGACY_A000_FRAME",
            fixture={"submitted_l_record": legacy_fixture},
        ),
        expected_record(
            full_conformance="FAIL",
            failures=("DUPLICATE_LEGACY_STAGE",),
            details=source_oracle(legacy),
        ),
        [historical_provenance(legacy, 4, relation="SPLIT_LEGACY_IDENTITY")],
    )

    registered_s0 = {
        "case": "NEUTRAL_CONTROL_FRAME_PARSER_FIXTURE",
        "cut": "J0",
        "history_production": "LAB_ONLY",
        "mechanism_manifest": "REFERENCE",
        "origin": "R01B_NEUTRAL_DUPLICATE_PARSER_FIXTURE",
        "repetition": 0,
        "semantic_profile": "R01B",
    }
    registered_case_id = "r01b-case-" + hashlib.sha256(
        CASE_TAG + tv(registered_s0)
    ).hexdigest()
    registered_d0 = {
        "backend": "LAB_CONTROL_FIXTURE",
        "case_id": registered_case_id,
        "cut": "J0",
        "exact_lab_input": {
            "control_stage": "J0",
            "frame_mode": "REFERENCE",
        },
        "history_production": "LAB_ONLY",
        "injected_fault": "NONE",
        "mechanism_manifest": "REFERENCE",
        "repetition": 0,
    }
    registered_digest = hashlib.sha256(b"ZGR01B-TRIAL\x00" + tv(registered_d0)).digest()
    neutral_frame = b"ZGNF" + bytes((1, 0, 1, 0)) + registered_digest
    add(
        lab_body(
            logical_id="NEUTRAL_FRAME_DUPLICATE_NEGATIVE",
            family="CONTROL_PROTOCOL",
            attack_kind="DUPLICATE_COMPLETE_NEUTRAL_FRAME",
            fixture={
                "controller_trial_registry": {
                    "descriptor_identity": registered_d0,
                    "ordinal": 0,
                    "symbolic_case_body": registered_s0,
                    "trial_id": "r01b-" + registered_digest.hex(),
                },
                "registered_trial_digest_hex": registered_digest.hex(),
                "submitted_frames_hex": [neutral_frame.hex(), neutral_frame.hex()],
            },
        ),
        expected_record(
            full_conformance="FAIL",
            failures=("DUPLICATE_NEUTRAL_FRAME",),
            details={"required_terminal": "FAIL(DUPLICATE_NEUTRAL_FRAME)"},
        ),
        [historical_provenance(legacy, 4, relation="SPLIT_NEW_NEUTRAL_IDENTITY"), correction_provenance("4.2")],
    )

    # One exact leaf deletion plus exact structured-UNKNOWN and
    # structured-UNSUPPORTED substitutions for every V2 path.  The frozen
    # per-path policy decides whether each well-formed status is admitted.
    delete_template = cases[19]
    unknown_template = cases[20]
    for path in paths:
        add(
            lab_body(
                logical_id=f"MEASURE_DELETE({path})",
                family="MEASUREMENT_SCHEMA",
                attack_kind="DELETE_EXACT_MEASUREMENT_LEAF",
                fixture={
                    "measurement_registry_sha256": MEASUREMENT_SHA256,
                    "mutation": "DELETE_LEAF",
                    "path": path,
                    "source_fixture": measurement_fixture_binding(),
                },
            ),
            expected_record(
                full_conformance="FAIL",
                failures=("MISSING_MEASUREMENT",),
                details={"required_terminal": f"FAIL(MISSING_MEASUREMENT:{path})"},
            ),
            [historical_provenance(delete_template, 19, relation="EXPAND_ONE_PER_FINAL_V2_PATH"), measurement_provenance(path=path)],
        )

        policy = measurements["path_policies"][path]["status_policy"]
        unknown_reason = "measurement unavailable in this holdout"
        unknown_needed_evidence = f"native measurement for {path}"
        replacement = {
            "needed_evidence": unknown_needed_evidence,
            "reason": unknown_reason,
            "status": "UNKNOWN",
        }
        if policy == "NATIVE_ONLY":
            structured_expected = expected_record(
                full_conformance="FAIL",
                failures=("STRUCTURED_STATUS_FORBIDDEN",),
                details={"path": path, "status_policy": policy, "validation": "REJECT"},
            )
        else:
            structured_expected = expected_record(
                full_conformance="UNKNOWN",
                needed_evidence=(f"native measurement for {path}",),
                details={"path": path, "status_policy": policy, "validation": "SCHEMA_COMPLETE_NOT_A_MEASUREMENT_PASS"},
            )
        add(
            lab_body(
                logical_id=f"MEASURE_STRUCTURED_UNKNOWN({path})",
                family="MEASUREMENT_SCHEMA",
                attack_kind="REPLACE_EXACT_MEASUREMENT_LEAF_WITH_STRUCTURED_UNKNOWN",
                fixture={
                    "measurement_registry_sha256": MEASUREMENT_SHA256,
                    "mutation": "REPLACE_LEAF",
                    "path": path,
                    "replacement": replacement,
                    "replacement_tv_hex": structured_unknown_bytes(
                        unknown_reason, unknown_needed_evidence
                    ).hex(),
                    "source_fixture": measurement_fixture_binding(),
                },
            ),
            structured_expected,
            [historical_provenance(unknown_template, 20, relation="EXPAND_VALID_STATUS_ONE_PER_FINAL_V2_PATH"), measurement_provenance(path=path)],
        )

        unsupported_reason = "measurement unsupported in this holdout"
        unsupported_replacement = {
            "reason": unsupported_reason,
            "status": "UNSUPPORTED",
        }
        if policy == "NATIVE_OR_UNKNOWN_OR_UNSUPPORTED":
            unsupported_expected = expected_record(
                full_conformance="UNSUPPORTED",
                needed_evidence=(f"realization supporting a native measurement for {path}",),
                details={
                    "path": path,
                    "status_policy": policy,
                    "validation": "SCHEMA_COMPLETE_UNSUPPORTED_NOT_A_MEASUREMENT_PASS",
                },
            )
        else:
            unsupported_expected = expected_record(
                full_conformance="FAIL",
                failures=("STRUCTURED_STATUS_FORBIDDEN",),
                details={"path": path, "status_policy": policy, "validation": "REJECT"},
            )
        add(
            lab_body(
                logical_id=f"MEASURE_STRUCTURED_UNSUPPORTED({path})",
                family="MEASUREMENT_SCHEMA",
                attack_kind="REPLACE_EXACT_MEASUREMENT_LEAF_WITH_STRUCTURED_UNSUPPORTED",
                fixture={
                    "measurement_registry_sha256": MEASUREMENT_SHA256,
                    "mutation": "REPLACE_LEAF",
                    "path": path,
                    "replacement": unsupported_replacement,
                    "replacement_tv_hex": structured_unsupported_bytes(
                        unsupported_reason
                    ).hex(),
                    "source_fixture": measurement_fixture_binding(),
                },
            ),
            unsupported_expected,
            [
                historical_provenance(
                    unknown_template,
                    20,
                    relation="EXPAND_UNSUPPORTED_ONE_PER_FINAL_V2_PATH",
                ),
                measurement_provenance(path=path),
            ],
        )

    # Required members of every closed container, native measured object, and
    # structured status are each attacked once.  The historical malformed
    # UNKNOWN case is the needed_evidence deletion member, not an alias for the
    # valid structured-status expansion above.
    schema_domains = {
        "closed_container_schemas": measurements["closed_container_schemas"],
        "native_value_kinds.definitions": measurements["native_value_kinds"]["definitions"],
        "structured_statuses": measurements["structured_statuses"],
    }
    malformed_key = ("structured_statuses", "UNKNOWN", "$", "needed_evidence")
    for domain, schemas in schema_domains.items():
        for schema_name, schema in sorted(schemas.items()):
            for location, member in required_members(schema):
                key = (domain, schema_name, location, member)
                if key == malformed_key:
                    allowed_paths = [
                        path for path in paths
                        if measurements["path_policies"][path]["status_policy"] != "NATIVE_ONLY"
                    ]
                    selected_path = allowed_paths[0]
                    body = lab_body(
                        logical_id="MEASURE_UNKNOWN_MISSING_EVIDENCE_NEGATIVE",
                        family="MEASUREMENT_SCHEMA",
                        attack_kind="DELETE_REQUIRED_STRUCTURED_UNKNOWN_MEMBER",
                        fixture={
                            "measurement_registry_sha256": MEASUREMENT_SHA256,
                            "path": selected_path,
                            "replacement": {
                                "reason": "nonempty",
                                "status": "UNKNOWN",
                            },
                            "schema_domain": domain,
                            "schema_location": location,
                            "schema_name": schema_name,
                            "source_fixture": measurement_fixture_binding(),
                            "member_deleted": member,
                        },
                    )
                    expected = expected_record(
                        full_conformance="FAIL",
                        failures=("MALFORMED_STRUCTURED_UNKNOWN",),
                        details={"required_terminal": "FAIL(MALFORMED_STRUCTURED_UNKNOWN:needed_evidence)"},
                    )
                    provenance = [
                        historical_provenance(unknown_template, 20, relation="PRESERVE_MALFORMED_TWO_MEMBER_UNKNOWN"),
                        measurement_provenance(schema_domain=domain, schema_location=location, schema_name=schema_name, member=member),
                    ]
                else:
                    logical_id = f"MEASURE_DELETE_CONTAINER_MEMBER({domain}:{schema_name}:{location}:{member})"
                    body = lab_body(
                        logical_id=logical_id,
                        family="MEASUREMENT_SCHEMA",
                        attack_kind="DELETE_REQUIRED_CLOSED_CONTAINER_MEMBER",
                        fixture={
                            "measurement_registry_sha256": MEASUREMENT_SHA256,
                            "mutation": "DELETE_REQUIRED_MEMBER",
                            "schema_domain": domain,
                            "schema_location": location,
                            "schema_name": schema_name,
                            "source_fixture": measurement_fixture_binding(),
                            "member_deleted": member,
                        },
                    )
                    expected = expected_record(
                        full_conformance="FAIL",
                        failures=("MISSING_REQUIRED_CONTAINER_MEMBER",),
                        details={
                            "required_terminal": f"FAIL(MISSING_REQUIRED_MEMBER:{domain}:{schema_name}:{location}:{member})"
                        },
                    )
                    provenance = [measurement_provenance(schema_domain=domain, schema_location=location, schema_name=schema_name, member=member)]
                add(body, expected, provenance)

    replay_case = cases[21]
    selectors, replay_index, replay_streams, envelope = replay_material()
    canonical_selector = next(
        selector for selector in selectors if selector["stream"] == "canonical_records"
    )
    raw_selectors = [
        selector for selector in selectors if selector["stream"] != "canonical_records"
    ]
    negative_fixture = {
        "envelope_bytes": "ABSENT",
        "envelope_sha256": hashlib.sha256(envelope).hexdigest(),
        "producer": "REMOVED",
        "raw_selectors": raw_selectors,
        "replay_index": replay_index,
        "selector": canonical_selector,
    }
    add(
        lab_body(
            logical_id="EVIDENCE_HASH_ONLY_NEGATIVE",
            family="EVIDENCE_REPLAY",
            attack_kind="REQUEST_EXACT_BYTES_FROM_HASH_ONLY",
            fixture=negative_fixture,
        ),
        expected_record(
            full_conformance="FAIL",
            failures=("EVIDENCE_UNAVAILABLE",),
            details={"replay_result": "FAIL(EXACT_BYTES_ABSENT)"},
        ),
        [historical_provenance(replay_case, 21, relation="SPLIT_HASH_ONLY_NEGATIVE")],
    )
    add(
        lab_body(
            logical_id="EVIDENCE_REPLAY_POSITIVE",
            family="EVIDENCE_REPLAY",
            attack_kind="REQUEST_EXACT_BYTES_FROM_RETAINED_ENVELOPE",
            fixture={
                "envelope_hex": envelope.hex(),
                "envelope_sha256": hashlib.sha256(envelope).hexdigest(),
                "producer": "REMOVED",
                "raw_selectors": raw_selectors,
                "replay_index": replay_index,
                "selector": canonical_selector,
            },
        ),
        expected_record(
            full_conformance="PASS",
            details={
                "envelope_sha256": hashlib.sha256(envelope).hexdigest(),
                "selected_ranges": [
                    {
                        "selected_hex": stream_bytes.hex(),
                        "selected_sha256": hashlib.sha256(stream_bytes).hexdigest(),
                        "stream": stream_name,
                    }
                    for stream_name, stream_bytes in sorted(replay_streams.items())
                ],
            },
        ),
        [historical_provenance(replay_case, 21, relation="SPLIT_POSITIVE_WITH_ADDED_EXACT_BYTES"), correction_provenance("8")],
    )

    add(
        lab_body(
            logical_id="COMPARATOR_EXPECTED_BYTE_MUTATION_NEGATIVE",
            family="COMPARATOR_HELD_OUT",
            attack_kind="COMMON_MODE_EXPECTED_BYTE_MUTATION_FALSE_MATCH",
            fixture={
                "actual_hex": "00",
                "frozen_reference_hex": "00",
                "mutated_reference_hex": "01",
                "submitted_comparator_verdict": "MATCH",
            },
        ),
        expected_record(
            full_conformance="FAIL",
            failures=("COMPARATOR_FALSE_MATCH",),
            details={"required_terminal": "FAIL(COMPARATOR_FALSE_MATCH)"},
        ),
        [correction_provenance("11.4")],
    )

    identified: list[tuple[str, dict[str, Any]]] = []
    logical_ids: set[str] = set()
    for item in pending:
        body = item["body"]
        if body["logical_id"] in logical_ids:
            raise ValueError(f"duplicate logical holdout ID: {body['logical_id']}")
        logical_ids.add(body["logical_id"])
        case_id = "r01b-case-" + hashlib.sha256(CASE_TAG + tv(body)).hexdigest()
        identified.append((case_id, item))
    identified.sort(key=lambda item: item[0].encode("ascii"))
    if len({case_id for case_id, _ in identified}) != len(identified):
        raise ValueError("holdout case-ID collision")
    rows = [
        {
            "body": item["body"],
            "case_id": case_id,
            "case_ordinal": ordinal,
            "expected": item["expected"],
            "provenance": item["provenance"],
        }
        for ordinal, (case_id, item) in enumerate(identified)
    ]

    mapped: dict[int, list[str]] = defaultdict(list)
    for row in rows:
        for provenance in row["provenance"]:
            if provenance.get("artifact") == "R01-BREAKER-OBJECT.json":
                mapped[provenance["source_case_index"]].append(row["case_id"])
    if set(mapped) != set(range(22)):
        raise ValueError(f"historical mapping is incomplete: {sorted(set(range(22)) - set(mapped))}")
    expected_mapping_counts = {index: 1 for index in range(22)}
    expected_mapping_counts.update(
        {
            4: 2,
            19: MEASUREMENT_PATH_COUNT,
            20: (2 * MEASUREMENT_PATH_COUNT) + 1,
            21: 2,
        }
    )
    if {index: len(ids) for index, ids in mapped.items()} != expected_mapping_counts:
        raise ValueError("historical mapping expansion count drift")
    mappings = []
    for index, case in enumerate(cases):
        ids = sorted(mapped[index])
        mappings.append(
            {
                "mapped_case_id_count": len(ids),
                "mapped_case_ids_sha256": hashlib.sha256(canonical_json(ids)).hexdigest(),
                "source_case_id": case["id"],
                "source_case_index": index,
                "source_case_sha256": hashlib.sha256(canonical_json(case)).hexdigest(),
            }
        )

    family_counts = dict(sorted(Counter(row["body"]["family"] for row in rows).items()))
    return {
        "case_id_rule": "ASCII(r01b-case-)||lowerhex(sha256(ASCII(ZGR01B-CASE)||00||TV(body)))",
        "counts_by_family": family_counts,
        "failure_reason_registry": list(FAILURE_REASON_REGISTRY),
        "historical_case_mappings": mappings,
        "historical_source": {
            "case_count": len(cases),
            "object_id": breaker["object_id"],
            "sha256": BREAKER_SHA256,
        },
        "measurement_source": {
            "closed_container_member_case_count": sum(
                len(required_members(schema))
                for schemas in schema_domains.values()
                for schema in schemas.values()
            ),
            "path_count": len(paths),
            "schema_id": measurements["schema_id"],
            "sha256": MEASUREMENT_SHA256,
        },
        "named_case_family_registry": {
            "MEASURE_STRUCTURED_UNKNOWN_VALID": {
                "attack_kind": "REPLACE_EXACT_MEASUREMENT_LEAF_WITH_STRUCTURED_UNKNOWN",
                "expansion": "exactly one MEASURE_STRUCTURED_UNKNOWN(path) per final V2 path",
                "path_count": len(paths),
            }
        },
        "pre_execution_fixture_registry": {
            MEASUREMENT_FIXTURE_RECIPE_ID: {
                "recipe": measurement_fixture_recipe(),
                "recipe_sha256": hashlib.sha256(
                    canonical_json(measurement_fixture_recipe())
                ).hexdigest(),
            }
        },
        "registry_phase": "S0_SYMBOLIC_LAB_ONLY_PRE_EXECUTION",
        "row_count": len(rows),
        "rows": rows,
        "schema_id": SCHEMA_ID,
        "status_coordinate_registry": STATUS_AUTHORITY["status_coordinate_registry"],
        "status_registry_source": {
            "artifact": STATUS_REGISTRY.name,
            "byte_length": len(_status_registry_raw),
            "schema_id": STATUS_AUTHORITY["schema_id"],
            "sha256": STATUS_REGISTRY_SHA256,
        },
        "suite_source": {"schema_id": suite["schema_id"], "sha256": SUITE_SHA256},
    }


def encoded_package() -> bytes:
    return canonical_json(build_package())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    data = encoded_package()
    if args.check:
        retained = args.output.read_bytes()
        if retained != data:
            raise SystemExit(f"{args.output.name} is not the deterministic holdout output")
    else:
        args.output.write_bytes(data)
    package = json.loads(data)
    print(f"schema_id={package['schema_id']}")
    print(f"rows={package['row_count']}")
    print(f"bytes={len(data)}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
