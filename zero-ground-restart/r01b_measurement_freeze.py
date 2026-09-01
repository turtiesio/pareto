#!/usr/bin/env python3
"""Generate and validate the frozen R0.1B measurement registry V2.

The generator is intentionally stdlib-only.  It treats paths as a closed set,
expands every finite component/variant/phase domain, and validates the retained
R0 breaker crosswalk before emitting deterministic JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "R01B-MEASUREMENT-REGISTRY.json"
BREAKER = HERE / "R01-BREAKER-OBJECT.json"

V1_SCHEMA_ID = "R01B-MEASUREMENT-PATHS-1"
V1_SHA256 = "74be5e922e2788657e6e9f080ddd421d556a3afa300d99ce0f060b9c84386363"
V1_PATH_COUNT = 502
V1_BYTE_LENGTH = 67822
BREAKER_SHA256 = "99f81a9a4d4f4bf55109a9f43b7cd361c887c9b0b7255a22d009767238e79dfa"
BREAKER_PATH_COUNT = 144

DIMENSIONS = (
    "information_distinction_preservation",
    "persistent_state",
    "semantic_machinery",
    "human_cognition",
    "authoring_burden",
    "query_navigation_burden",
    "runtime",
    "storage",
    "operations",
    "trusted_computing_base",
    "evolution",
    "portability",
    "explainability",
    "information_loss_risk",
)

FAMILIES = (
    "adapter_fault",
    "apparatus",
    "comparator_held_out",
    "controller_externalization",
    "deletion_comparison",
    "environment",
    "evidence_replay",
    "io_fault",
    "measurement_schema",
    "publication_cut",
    "record_fault",
)

EVIDENCE_STREAMS = (
    "apparatus_failures",
    "canonical_records",
    "inventory_pack",
    "raw_measurement_pack",
    "raw_trace_pack",
    "replay_index",
)

MECHANISM_MANIFESTS = (
    "DROP_STAGE_CONTROLLER",
    "NO_DIRECTORY_FSYNC",
    "NO_EXCLUSIVE_CREATE",
    "NO_FILE_FSYNC",
    "NO_PRE_RECOVERY_REAP_BEHAVIORAL",
    "NO_REPLACE",
    "REFERENCE",
    "SELF_CUT",
)

UNSUPPORTED_ALLOWED_PATHS = frozenset(
    {
        "evolution.format_support",
        "evolution.freshness_support",
        "evolution.generation_support",
        "evolution.migration_support",
        "evolution.rollback_support",
        "evolution.version_support",
        "information_loss_risk.physical_faults",
        "information_loss_risk.power_loss_faults",
        "portability.physical_portability_status",
    }
)

NORMATIVE_ASSERTION_PATHS = frozenset(
    {
        "human_cognition.no_inference_from_loc_alone",
        "runtime.timing_is_measurement_only",
    }
)

RUNTIME_PHASES = (
    "launch",
    "write",
    "acquisition",
    "file_fsync",
    "replace",
    "directory_fsync",
    "J0",
    "J1",
    "J2",
    "J3",
    "J4",
    "J5",
    "checkpoint_control",
    "kill",
    "wait",
    "recovery",
    "adapter",
    "trace",
    "verify",
    "total",
)

RUNTIME_METRICS = ("wall", "process_cpu")

SEMANTIC_COMPONENTS = (
    "adapter",
    "backend_selector",
    "collector",
    "comparator",
    "contract",
    "controller",
    "descriptor_generator",
    "environment_selector",
    "evidence_packager",
    "injector",
    "mechanism_selector",
    "measurement_collector",
    "normalizer",
    "oracle",
    "oracle_generator",
    "process_launcher",
    "publisher",
    "reaper",
    "recovery",
    "replay_index",
    "replay_reader",
    "schema",
    "serializer",
    "tests",
    "tracer",
    "verifier",
)

TCB_COMPONENTS = (
    "adapter",
    "backend_selector",
    "block_layer",
    "collector",
    "comparator",
    "contract_and_suite",
    "controller",
    "descriptor_generator",
    "environment_selector",
    "evidence_packager",
    "evidence_store",
    "ext4",
    "hash_implementation",
    "host",
    "hypervisor",
    "injector",
    "kernel",
    "libc",
    "mechanism_selector",
    "measurement_collector",
    "normalizer",
    "oracle",
    "oracle_generator",
    "physical_media",
    "process_launcher",
    "publisher",
    "python_runtime",
    "reaper",
    "recovery",
    "replay_index",
    "replay_reader",
    "schema_validator",
    "serializer",
    "swap_subsystem",
    "test_runner",
    "tmpfs",
    "tracer",
    "verifier",
    "vfs",
)

DELETION_VARIANTS = (
    "DROP_COMPARATOR",
    "DROP_REAPER",
    "DROP_SELECTOR",
    "DROP_STAGE_CONTROLLER",
    "DROP_TRACER",
    "DROP_VERIFIER",
    "NO_DIRECTORY_FSYNC",
    "NO_EXCLUSIVE_CREATE",
    "NO_FILE_FSYNC",
    "NO_PRE_RECOVERY_REAP",
    "NO_REPLACE",
)

EXTERNALIZATION_VARIANTS = ("SELF_CUT_EXTERNALIZE",)

SEMANTIC_FIELDS = (
    "dependencies",
    "files",
    "generated_cells",
    "logical_lines",
    "physical_lines",
    "sha256_per_file",
    "source_bytes",
)

SEMANTIC_EXPANDED_FIELDS = tuple(sorted(SEMANTIC_FIELDS + ("generated_bytes",)))

TCB_FIELDS = (
    "code_config_bytes",
    "common_mode_dependencies",
    "dependency_status",
    "provenance",
    "role",
    "source",
    "version",
)

COMPLEXITY_FIELDS = (
    "changed_code_config",
    "changed_operations",
    "changed_operator_concepts",
    "changed_persisted_bytes",
    "changed_runtime",
    "changed_tcb",
    "changed_verification_work",
    "unsupported_futures",
)


def ref(name: str) -> dict[str, str]:
    return {"$ref": f"#/native_value_kinds/definitions/{name}"}


def closed_object(properties: dict[str, Any], required: tuple[str, ...] | None = None) -> dict[str, Any]:
    keys = tuple(sorted(properties)) if required is None else tuple(sorted(required))
    return {
        "additionalProperties": False,
        "properties": properties,
        "required": list(keys),
        "type": "object",
    }


def closed_record_array(properties: dict[str, Any], order: str, unique_by: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "items": closed_object(properties),
        "order": order,
        "type": "array",
    }
    if unique_by is not None:
        result["uniqueBy"] = unique_by
    return result


def build_schema_definitions() -> tuple[dict[str, Any], dict[str, Any]]:
    native = {
        "backend_id": {"enum": ["E", "T"], "type": "string"},
        "boolean": {"type": "boolean"},
        "constant_true": {"const": True, "type": "boolean"},
        "contract_profile_id": {"const": "R01B", "type": "string"},
        "hex_bytes": {"pattern": "^(?:[0-9a-f]{2})*$", "type": "string"},
        "mechanism_manifest_id": {"enum": list(MECHANISM_MANIFESTS), "type": "string"},
        "nonempty_utf8": {"minLength": 1, "type": "string"},
        "registry_schema_id": {"const": "R01B-MEASUREMENT-PATHS-2", "type": "string"},
        "run_id": {"pattern": "^r01b-run-[0-9a-f]{64}$", "type": "string"},
        "sha256_hex": {"pattern": "^[0-9a-f]{64}$", "type": "string"},
        "trial_id": {"pattern": "^r01b-[0-9a-f]{64}$", "type": "string"},
        "measured_nonnegative_integer": closed_object(
            {
                "method": ref("nonempty_utf8"),
                "scope": ref("nonempty_utf8"),
                "unit": ref("nonempty_utf8"),
                "value": {"minimum": 0, "type": "integer"},
            }
        ),
    }

    text_set = {
        "items": ref("nonempty_utf8"),
        "order": "ascending_unsigned_utf8",
        "type": "array",
        "uniqueItems": True,
    }
    text_sequence = {"items": ref("nonempty_utf8"), "order": "declared", "type": "array"}
    family_counts = closed_object(
        {
            "counts": closed_object({family: {"minimum": 0, "type": "integer"} for family in FAMILIES}),
            "method": ref("nonempty_utf8"),
            "scope": ref("nonempty_utf8"),
        }
    )
    fault_summary = closed_object(
        {
            "failed": {"minimum": 0, "type": "integer"},
            "method": ref("nonempty_utf8"),
            "passed": {"minimum": 0, "type": "integer"},
            "scope": ref("nonempty_utf8"),
            "total": {"minimum": 0, "type": "integer"},
            "unknown": {"minimum": 0, "type": "integer"},
            "unsupported": {"minimum": 0, "type": "integer"},
        }
    )
    containers = {
        "action_inventory": closed_record_array(
            {
                "detail": ref("nonempty_utf8"),
                "name": ref("nonempty_utf8"),
                "ordinal": {"minimum": 0, "type": "integer"},
                "scope": ref("nonempty_utf8"),
            },
            "ordinal_ascending",
            "ordinal",
        ),
        "branch_line_inventory": closed_record_array(
            {
                "branches": {"minimum": 0, "type": "integer"},
                "lines": {"minimum": 0, "type": "integer"},
                "name": ref("nonempty_utf8"),
            },
            "name_unsigned_utf8",
            "name",
        ),
        "authored_item_inventory": closed_record_array(
            {
                "description": ref("nonempty_utf8"),
                "id": ref("nonempty_utf8"),
                "source": ref("nonempty_utf8"),
                "value_sha256": ref("sha256_hex"),
            },
            "id_unsigned_utf8",
            "id",
        ),
        "byte_change": closed_object(
            {
                "after_bytes": {"minimum": 0, "type": "integer"},
                "before_bytes": {"minimum": 0, "type": "integer"},
                "delta_bytes": {"type": "integer"},
                "method": ref("nonempty_utf8"),
                "scope": ref("nonempty_utf8"),
            }
        ),
        "collision_inventory": closed_record_array(
            {
                "continuation_hex": ref("hex_bytes"),
                "expected_left_hex": ref("hex_bytes"),
                "expected_right_hex": ref("hex_bytes"),
                "id": ref("nonempty_utf8"),
                "left_history_sha256": ref("sha256_hex"),
                "right_history_sha256": ref("sha256_hex"),
                "scope": ref("nonempty_utf8"),
            },
            "id_unsigned_utf8",
            "id",
        ),
        "complexity_delta_inventory": closed_record_array(
            {
                "after": {"type": ["integer", "string"]},
                "before": {"type": ["integer", "string"]},
                "item": ref("nonempty_utf8"),
                "method": ref("nonempty_utf8"),
                "scope": ref("nonempty_utf8"),
                "unit": ref("nonempty_utf8"),
            },
            "item_unsigned_utf8",
            "item",
        ),
        "dependency_inventory": closed_record_array(
            {
                "classification": {"enum": ["COMMON", "EXTERNAL", "VARIANT"], "type": "string"},
                "name": ref("nonempty_utf8"),
                "status": {"enum": ["IDENTIFIED", "PARTIAL", "UNAVAILABLE"], "type": "string"},
            },
            "name_unsigned_utf8",
            "name",
        ),
        "environment_inventory": closed_record_array(
            {"name": ref("nonempty_utf8"), "value_hex": ref("hex_bytes")},
            "name_unsigned_utf8",
            "name",
        ),
        "continuation_inventory": closed_record_array(
            {
                "byte_length": {"minimum": 0, "type": "integer"},
                "continuation_hex": ref("hex_bytes"),
                "id": ref("nonempty_utf8"),
                "source": ref("nonempty_utf8"),
            },
            "id_unsigned_utf8",
            "id",
        ),
        "evidence_stream_inventory": closed_object(
            {
                name: closed_object(
                    {
                        "byte_length": {"minimum": 0, "type": "integer"},
                        "replay_available": {"type": "boolean"},
                        "retained": {"type": "boolean"},
                        "sha256": ref("sha256_hex"),
                    }
                )
                for name in EVIDENCE_STREAMS
            }
        ),
        "family_count_vector": family_counts,
        "fault_summary": fault_summary,
        "file_hash_inventory": closed_record_array(
            {"path": ref("nonempty_utf8"), "sha256": ref("sha256_hex")},
            "path_unsigned_utf8",
            "path",
        ),
        "file_path_inventory": text_set,
        "named_fault_summary_inventory": closed_record_array(
            {"name": ref("nonempty_utf8"), "summary": fault_summary},
            "name_unsigned_utf8",
            "name",
        ),
        "old_new_matrix": closed_record_array(
            {
                "actual_hex": ref("hex_bytes"),
                "cut": {"enum": ["J0", "J1", "J2", "J3", "J4", "J5", "NORMAL"], "type": "string"},
                "expected_hex": ref("hex_bytes"),
                "setup": {"enum": ["ABSENT_CLEAN", "VALID_P0_CLEAN"], "type": "string"},
                "verdict": {"enum": ["DIFFER", "MATCH", "NOT_COMPARED", "UNKNOWN"], "type": "string"},
            },
            "setup_then_cut",
            None,
        ),
        "platform_inventory": closed_record_array(
            {
                "name": ref("nonempty_utf8"),
                "reason": ref("nonempty_utf8"),
                "status": {"enum": ["FAILED", "PASSED", "UNTESTED"], "type": "string"},
            },
            "name_unsigned_utf8",
            "name",
        ),
        "probe_result": closed_object(
            {
                "actual_hex": ref("hex_bytes"),
                "expected_hex": ref("hex_bytes"),
                "reason": ref("nonempty_utf8"),
                "scope": ref("nonempty_utf8"),
                "status": {"enum": ["FAIL", "NO_WITNESS", "PASS"], "type": "string"},
            }
        ),
        "replay_selector_record": closed_object(
            {
                "length": {"minimum": 0, "type": "integer"},
                "offset": {"minimum": 0, "type": "integer"},
                "ordinal": {"minimum": 0, "type": "integer"},
                "record_sha256": ref("sha256_hex"),
                "trial_id": ref("trial_id"),
            }
        ),
        "runtime_series": closed_object(
            {
                "method": ref("nonempty_utf8"),
                "scope": ref("nonempty_utf8"),
                "unit": {"const": "ns", "type": "string"},
                "values": {"items": {"minimum": 0, "type": "integer"}, "minItems": 1, "order": "trial_descriptor_order", "type": "array"},
            }
        ),
        "syscall_count_inventory": closed_object(
            {
                "entries": closed_record_array(
                    {"count": {"minimum": 0, "type": "integer"}, "name": ref("nonempty_utf8")},
                    "name_unsigned_utf8",
                    "name",
                ),
                "method": ref("nonempty_utf8"),
                "scope": ref("nonempty_utf8"),
            }
        ),
        "study_protocol": closed_object(
            {
                "outcome_measure": ref("nonempty_utf8"),
                "population": ref("nonempty_utf8"),
                "preregistered_sha256": ref("sha256_hex"),
                "protocol_id": ref("nonempty_utf8"),
                "sampling_method": ref("nonempty_utf8"),
                "task_definition": ref("nonempty_utf8"),
            }
        ),
        "text_sequence": text_sequence,
        "text_set": text_set,
        "witness_inventory": closed_record_array(
            {
                "continuation_hex": ref("hex_bytes"),
                "id": ref("nonempty_utf8"),
                "left_hex": ref("hex_bytes"),
                "right_hex": ref("hex_bytes"),
                "scope": ref("nonempty_utf8"),
            },
            "id_unsigned_utf8",
            "id",
        ),
    }
    return native, containers


class RegistryBuilder:
    def __init__(self) -> None:
        self.paths: dict[str, str] = {}
        self.policies: dict[str, dict[str, Any]] = {}

    def add(
        self,
        path: str,
        native_kind: str,
        *,
        status_policy: str | None = None,
        unit: str | None = None,
        zero_policy: str = "NOT_APPLICABLE",
    ) -> None:
        if path in self.paths:
            raise ValueError(f"duplicate path: {path}")
        if status_policy is None:
            status_policy = (
                "NATIVE_OR_UNKNOWN_OR_UNSUPPORTED"
                if path in UNSUPPORTED_ALLOWED_PATHS
                else "NATIVE_OR_UNKNOWN"
            )
        self.paths[path] = native_kind
        policy: dict[str, Any] = {
            "native_kind": native_kind,
            "status_policy": status_policy,
            "zero_policy": zero_policy,
        }
        if unit is not None:
            policy["unit"] = unit
        self.policies[path] = policy

    def number(self, path: str, unit: str) -> None:
        self.add(
            path,
            "measured_nonnegative_integer",
            unit=unit,
            zero_policy="ZERO_REQUIRES_NONEMPTY_SCOPE_AND_METHOD",
        )


def build_paths() -> RegistryBuilder:
    b = RegistryBuilder()

    for path, kind in (
        ("identity.backend", "backend_id"),
        ("identity.breaker_object_sha256", "sha256_hex"),
        ("identity.contract_profile", "contract_profile_id"),
        ("identity.descriptor_stream_sha256", "sha256_hex"),
        ("identity.implementation_bundle_sha256", "sha256_hex"),
        ("identity.literal_oracle_sha256", "sha256_hex"),
        ("identity.manifest", "mechanism_manifest_id"),
        ("identity.measurement_registry_sha256", "sha256_hex"),
        ("identity.run_id", "run_id"),
        ("identity.schema_id", "registry_schema_id"),
        ("identity.suite_digest", "sha256_hex"),
    ):
        b.add(path, kind, status_policy="NATIVE_ONLY")

    info_kinds = {
        "common_mode_controls": "named_fault_summary_inventory",
        "corruption_controls": "named_fault_summary_inventory",
        "exact_collision_list": "collision_inventory",
        "fail_counts_by_family": "family_count_vector",
        "minimized_witnesses": "witness_inventory",
        "mutation_coverage": "named_fault_summary_inventory",
        "old_new_matrix": "old_new_matrix",
        "pass_counts_by_family": "family_count_vector",
        "trial_totals_by_family": "family_count_vector",
        "unknown_counts_by_family": "family_count_vector",
        "unsupported_counts_by_family": "family_count_vector",
    }
    for leaf, kind in info_kinds.items():
        b.add(f"information_distinction_preservation.{leaf}", kind)
    for leaf in ("C", "Y0", "Y1"):
        b.add(f"information_distinction_preservation.separating_witness.{leaf}", "hex_bytes")

    for leaf in (
        "authoritative_allocated_bytes",
        "authoritative_logical_bytes",
        "directory_entry_count",
        "external_digest_bytes",
        "in_band_digest_bytes",
        "inode_count",
        "manifest_state_bytes",
        "peak_simultaneous_allocated_bytes",
        "peak_simultaneous_logical_bytes",
        "selector_state_bytes",
        "staging_allocated_bytes",
        "staging_logical_bytes",
    ):
        b.number(f"persistent_state.{leaf}", "bytes" if "bytes" in leaf else "count")
    b.add("persistent_state.filesystem_allocation_caveat", "nonempty_utf8")
    b.add("persistent_state.lower_bound_status", "probe_result")

    semantic_kind = {
        "dependencies": "dependency_inventory",
        "files": "file_path_inventory",
        "generated_cells": "measured_nonnegative_integer",
        "logical_lines": "measured_nonnegative_integer",
        "physical_lines": "measured_nonnegative_integer",
        "sha256_per_file": "file_hash_inventory",
        "source_bytes": "measured_nonnegative_integer",
    }
    for component in SEMANTIC_COMPONENTS:
        for field in SEMANTIC_FIELDS:
            path = f"semantic_machinery.components.{component}.{field}"
            if field in ("generated_cells", "logical_lines", "physical_lines", "source_bytes"):
                b.number(path, "bytes" if field == "source_bytes" else "count")
            else:
                b.add(path, semantic_kind[field])
        b.number(f"semantic_machinery.components.{component}.generated_bytes", "bytes")

    for path, kind in (
        ("human_cognition.failure_labels", "text_set"),
        ("human_cognition.required_concepts", "text_set"),
        ("human_cognition.roles", "text_set"),
        ("human_cognition.study_protocol", "study_protocol"),
    ):
        b.add(path, kind)
    for leaf in (
        "failure_label_count",
        "instruction_words",
        "observed_error_count",
        "operator_choice_count",
        "operator_command_count",
        "participant_count",
        "required_concept_count",
        "role_count",
    ):
        b.number(f"human_cognition.{leaf}", "count")
    b.number("human_cognition.task_time_ns", "ns")
    b.add("human_cognition.no_inference_from_loc_alone", "constant_true", status_policy="NATIVE_ONLY")

    for leaf in (
        "correction_count",
        "distinct_manual_decision_count",
        "fixture_count",
        "generated_bytes",
        "generated_file_count",
        "generated_logical_lines",
        "hand_authored_bytes",
        "hand_authored_file_count",
        "hand_authored_logical_lines",
        "manifest_entry_count",
        "parameter_count",
        "review_count",
    ):
        b.number(f"authoring_burden.{leaf}", "bytes" if leaf.endswith("_bytes") else "count")
    for leaf in ("fixtures", "manifest_entries", "parameters"):
        b.add(f"authoring_burden.{leaf}", "authored_item_inventory")

    for leaf in (
        "adapter_call_count",
        "continuation_bytes",
        "continuation_count",
        "index_machinery_count",
        "lookup_step_count",
        "open_count",
        "read_count",
        "search_machinery_count",
        "table_step_count",
        "transcript_bytes",
    ):
        b.number(f"query_navigation_burden.{leaf}", "bytes" if leaf.endswith("_bytes") else "count")
    b.add("query_navigation_burden.continuations", "continuation_inventory")

    for phase in RUNTIME_PHASES:
        b.number(f"runtime.phases.{phase}.sample_count", "count")
        for metric in RUNTIME_METRICS:
            prefix = f"runtime.phases.{phase}.{metric}"
            b.add(f"{prefix}.series_ns", "runtime_series")
            for statistic in ("aggregate_ns", "minimum_ns", "median_ns", "p95_ns", "maximum_ns"):
                b.number(f"{prefix}.{statistic}", "ns")
    b.add("runtime.perturbation_caveat", "nonempty_utf8")
    b.add("runtime.timing_is_measurement_only", "constant_true", status_policy="NATIVE_ONLY")

    for area in (
        "authoritative",
        "directory",
        "filesystem_delta",
        "hypervisor",
        "normalized_evidence",
        "os",
        "physical_backing",
        "raw_evidence",
        "replay_index",
        "runtime_interpreter",
        "source_spec",
        "staging",
    ):
        b.number(f"storage.{area}.allocated_bytes", "bytes")
        b.number(f"storage.{area}.logical_bytes", "bytes")
    b.number("storage.shared_bytes", "bytes")
    b.number("storage.unattributable_bytes", "bytes")
    b.add("storage.incomplete_totals_statement", "nonempty_utf8")
    b.add("storage.retained_stream_inventory", "evidence_stream_inventory")

    for leaf in (
        "cleanup_steps",
        "configured_output_descriptors",
        "namespace_steps",
        "privilege_requirements",
        "recovery_actions",
        "setup_steps",
        "signals",
        "trace_actions",
        "waits",
    ):
        b.add(f"operations.{leaf}", "action_inventory" if leaf not in ("privilege_requirements", "configured_output_descriptors") else "text_set")
    for leaf in (
        "cleanup_step_count",
        "failure_count",
        "namespace_step_count",
        "process_count",
        "recovery_action_count",
        "retry_count",
        "setup_step_count",
        "signal_count",
        "trace_action_count",
        "wait_count",
    ):
        b.number(f"operations.{leaf}", "count")
    b.add("operations.complete_syscall_counts_by_name", "syscall_count_inventory")
    for syscall in ("close", "fsync", "open", "read", "replace", "write"):
        b.number(f"operations.syscall_counts.{syscall}", "count")
    b.add("operations.inherited_environment_allowlist", "environment_inventory")
    b.add("operations.effective_environment", "environment_inventory")
    b.add("operations.launcher_environment_construction", "action_inventory")
    b.add("operations.trace_window", "probe_result")
    b.add("operations.trace_completeness", "probe_result")
    b.add("operations.reaping_observation_method", "probe_result")
    b.number("operations.apparatus_deadline_ns", "ns")
    b.number("operations.apparatus_storage_bound_bytes", "bytes")
    b.add("operations.apparatus_overrun_status", "probe_result")
    b.add("operations.replay_selector", "replay_selector_record")
    b.add("operations.replay_consistency", "probe_result")

    for component in TCB_COMPONENTS:
        for field in TCB_FIELDS:
            path = f"trusted_computing_base.components.{component}.{field}"
            if field == "code_config_bytes":
                b.number(path, "bytes")
            elif field == "common_mode_dependencies":
                b.add(path, "dependency_inventory")
            elif field == "dependency_status":
                b.add(path, "probe_result")
            else:
                b.add(path, "nonempty_utf8")

    for leaf in (
        "class_splitting_probe",
        "compatible_factor_through_observer",
        "format_support",
        "freshness_support",
        "generation_support",
        "migration_support",
        "rollback_support",
        "split_extension_collision_result",
        "version_support",
    ):
        b.add(f"evolution.{leaf}", "probe_result")
    b.add("evolution.external_information_required", "text_set")
    b.add("evolution.migration_inputs", "text_set")
    b.number("evolution.migration_bytes", "bytes")

    b.add("portability.backend_variant_branches", "branch_line_inventory")
    b.add("portability.backend_variant_lines", "branch_line_inventory")
    b.add("portability.exact_E_T_behavioral_comparison", "probe_result")
    for leaf in ("filesystem_prerequisites", "kernel_prerequisites", "os_prerequisites"):
        b.add(f"portability.{leaf}", "text_set")
    for leaf in ("failed_platforms", "tested_platforms", "untested_platforms"):
        b.add(f"portability.{leaf}", "platform_inventory")
    for leaf in ("host_portability_status", "physical_portability_status", "runtime_portability_status"):
        b.add(f"portability.{leaf}", "probe_result")

    for leaf in ("exact_actual_bytes", "exact_expected_bytes"):
        b.add(f"explainability.{leaf}", "hex_bytes")
    b.number("explainability.explanation_bytes", "bytes")
    for leaf in ("causal_steps",):
        b.add(f"explainability.{leaf}", "action_inventory")
    for leaf in (
        "human_comprehension_study",
        "manifest",
        "operation_result",
        "operation_source",
        "slot",
        "smallest_trial",
        "trace_locator",
    ):
        b.add(f"explainability.{leaf}", "probe_result")
    b.add("explainability.recovery_tag", "nonempty_utf8")
    b.add("explainability.causal_stage_or_fault_label", "nonempty_utf8")

    for leaf in (
        "append_faults",
        "attestation_disagreements",
        "bit_faults",
        "coherent_replacement_faults",
        "controller_faults",
        "error_faults",
        "io_faults",
        "overlap_faults",
        "physical_faults",
        "power_loss_faults",
        "process_kill_faults",
        "stale_replacement_faults",
        "truncation_faults",
    ):
        b.add(f"information_loss_risk.{leaf}", "fault_summary")
    for leaf in (
        "false_accept_count",
        "false_reject_count",
        "undetected_coherent_replacement_count",
    ):
        b.number(f"information_loss_risk.{leaf}", "count")
    for leaf in ("hash_collision_status", "malicious_fault_status"):
        b.add(f"information_loss_risk.{leaf}", "probe_result")
    b.add("information_loss_risk.hash_assumption", "nonempty_utf8")
    b.add("information_loss_risk.unsupported_fault_classes", "text_set")

    for variant in DELETION_VARIANTS + EXTERNALIZATION_VARIANTS:
        prefix = f"where_is_complexity_now.{variant}"
        for field in COMPLEXITY_FIELDS:
            if field == "changed_persisted_bytes":
                b.add(f"{prefix}.{field}", "byte_change")
            elif field == "unsupported_futures":
                b.add(f"{prefix}.{field}", "text_set")
            else:
                b.add(f"{prefix}.{field}", "complexity_delta_inventory")

    return b


def measurement_semantics(builder: RegistryBuilder) -> dict[str, dict[str, str]]:
    scope_by_root = {
        "authoring_burden": "implementation_bundle",
        "evolution": "conditional_future_registry",
        "explainability": "smallest_trial_and_evidence",
        "human_cognition": "human_study",
        "identity": "backend_manifest_run_report",
        "information_distinction_preservation": "frozen_suite",
        "information_loss_risk": "registered_attack_suite",
        "operations": "backend_manifest_run",
        "persistent_state": "backend_manifest_persistent_namespace",
        "portability": "platform_matrix",
        "query_navigation_burden": "registered_recovery_queries",
        "runtime": "trial_descriptor_series",
        "semantic_machinery": "implementation_bundle",
        "storage": "backend_manifest_run_artifacts",
        "trusted_computing_base": "implementation_and_run_dependencies",
        "where_is_complexity_now": "exact_deletion_or_externalization_variant",
    }
    inventory_kinds = {
        "action_inventory",
        "authored_item_inventory",
        "branch_line_inventory",
        "collision_inventory",
        "complexity_delta_inventory",
        "continuation_inventory",
        "dependency_inventory",
        "environment_inventory",
        "evidence_stream_inventory",
        "file_hash_inventory",
        "file_path_inventory",
        "named_fault_summary_inventory",
        "platform_inventory",
        "syscall_count_inventory",
        "text_sequence",
        "text_set",
        "witness_inventory",
    }
    result: dict[str, dict[str, str]] = {}
    for path in sorted(builder.paths):
        kind = builder.paths[path]
        policy = builder.policies[path]
        if path in NORMATIVE_ASSERTION_PATHS or path.startswith("identity."):
            applicability = "ALWAYS_REQUIRED"
        elif path in {
            "information_loss_risk.physical_faults",
            "information_loss_risk.power_loss_faults",
        }:
            applicability = "PHYSICAL_OR_POWER_IF_REALIZED_HERE"
        elif path == "portability.physical_portability_status":
            applicability = "PHYSICAL_PLATFORM_IF_TESTED_HERE"
        elif path in UNSUPPORTED_ALLOWED_PATHS:
            applicability = "CONDITIONAL_FUTURE_IF_REALIZED_HERE"
        else:
            applicability = "REQUIRED_OR_EXACT_UNKNOWN"

        if path.endswith(".series_ns"):
            aggregation = "ORDER_BY_TRIAL_DESCRIPTOR"
        elif path.endswith(".aggregate_ns"):
            aggregation = "SUM_SERIES_VALUES"
        elif path.endswith(".minimum_ns"):
            aggregation = "MIN_SERIES_VALUES"
        elif path.endswith(".median_ns"):
            aggregation = "SORTED_SERIES_VALUE_AT_ZERO_BASED_INDEX_(n-1)//2"
        elif path.endswith(".p95_ns"):
            aggregation = "NEAREST_RANK_CEILING_0.95_OF_SORTED_SERIES"
        elif path.endswith(".maximum_ns"):
            aggregation = "MAX_SERIES_VALUES"
        elif kind in inventory_kinds:
            aggregation = "EXACT_CLOSED_CANONICAL_INVENTORY"
        elif kind == "measured_nonnegative_integer":
            aggregation = "DIRECT_MEASUREMENT_UNLESS_NAMED_INVARIANT_APPLIES"
        else:
            aggregation = "EXACT_SINGLE_NATIVE_VALUE"

        result[path] = {
            "aggregation_rule": aggregation,
            "applicability_rule": applicability,
            "deletion_mutation": f"DELETE_MEASUREMENT_LEAF::{path}",
            "scope": scope_by_root[path.split(".", 1)[0]],
            "unit": policy.get("unit", f"native::{kind}"),
        }
    return result


def load_breaker_paths() -> list[str]:
    raw = BREAKER.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != BREAKER_SHA256:
        raise ValueError(f"breaker hash changed: {actual}")
    obj = json.loads(raw)
    paths = obj["measurement_path_registry"]
    if len(paths) != BREAKER_PATH_COUNT or len(paths) != len(set(paths)):
        raise ValueError("breaker path registry is not the frozen 144-entry set")
    return paths


def make_crosswalk(old_paths: list[str], new_paths: set[str]) -> dict[str, Any]:
    direct: dict[str, list[str]] = {
        "information.total_legal_trials": ["information_distinction_preservation.trial_totals_by_family"],
        "information.pass_counts_by_kind": ["information_distinction_preservation.pass_counts_by_family"],
        "information.fail_counts_by_kind": ["information_distinction_preservation.fail_counts_by_family"],
        "information.exact_semantic_collision_list": ["information_distinction_preservation.exact_collision_list"],
        "information.separating_witness.C": ["information_distinction_preservation.separating_witness.C"],
        "information.separating_witness.Y0": ["information_distinction_preservation.separating_witness.Y0"],
        "information.separating_witness.Y1": ["information_distinction_preservation.separating_witness.Y1"],
        "information.old_new_cut_matrix": ["information_distinction_preservation.old_new_matrix"],
        "information.mutation_coverage": ["information_distinction_preservation.mutation_coverage"],
        "information.common_mode_mutation_result": ["information_distinction_preservation.common_mode_controls"],
        "persistent.state_bin_logical_bytes": ["persistent_state.authoritative_logical_bytes"],
        "persistent.state_tmp_logical_bytes": ["persistent_state.staging_logical_bytes"],
        "persistent.peak_simultaneous_logical_bytes": ["persistent_state.peak_simultaneous_logical_bytes"],
        "persistent.st_blocks_times_512": ["persistent_state.authoritative_allocated_bytes", "persistent_state.staging_allocated_bytes"],
        "persistent.inode_count": ["persistent_state.inode_count"],
        "persistent.directory_entry_count": ["persistent_state.directory_entry_count"],
        "persistent.suite_digest_bytes": ["persistent_state.in_band_digest_bytes"],
        "persistent.external_expected_digest_bytes": ["persistent_state.external_digest_bytes"],
        "persistent.filesystem_allocation_caveat": ["persistent_state.filesystem_allocation_caveat"],
        "human_cognition.human_error_study": ["human_cognition.study_protocol", "human_cognition.observed_error_count", "human_cognition.participant_count", "human_cognition.task_time_ns"],
        "authoring.manifest_entries": ["authoring_burden.manifest_entries", "authoring_burden.manifest_entry_count"],
        "authoring.parameters": ["authoring_burden.parameters", "authoring_burden.parameter_count"],
        "authoring.fixtures": ["authoring_burden.fixtures", "authoring_burden.fixture_count"],
        "authoring.distinct_manual_decisions": ["authoring_burden.distinct_manual_decision_count"],
        "query.recovery_open_count": ["query_navigation_burden.open_count"],
        "query.recovery_read_count": ["query_navigation_burden.read_count"],
        "query.continuation_count": [
            "query_navigation_burden.continuation_count",
            "query_navigation_burden.continuations",
        ],
        "query.continuation_bytes": [
            "query_navigation_burden.continuation_bytes",
            "query_navigation_burden.continuations",
        ],
        "query.adapter_invocation_count": ["query_navigation_burden.adapter_call_count"],
        "query.lookup_steps": ["query_navigation_burden.lookup_step_count"],
        "query.table_steps": ["query_navigation_burden.table_step_count"],
        "query.search_infrastructure_status": ["query_navigation_burden.search_machinery_count"],
        "query.index_infrastructure_status": ["query_navigation_burden.index_machinery_count"],
        "runtime.per_trial_monotonic_wall_ns": [f"runtime.phases.{p}.wall.series_ns" for p in RUNTIME_PHASES],
        "runtime.per_trial_process_cpu_ns": [f"runtime.phases.{p}.process_cpu.series_ns" for p in RUNTIME_PHASES],
        "runtime.aggregate_monotonic_wall_ns": [f"runtime.phases.{p}.wall.aggregate_ns" for p in RUNTIME_PHASES],
        "runtime.aggregate_process_cpu_ns": [f"runtime.phases.{p}.process_cpu.aggregate_ns" for p in RUNTIME_PHASES],
        "runtime.phase_process_launch_ns": ["runtime.phases.launch.wall.aggregate_ns"],
        "runtime.phase_publication_ns": [
            "runtime.phases.write.wall.aggregate_ns",
            "runtime.phases.acquisition.wall.aggregate_ns",
            "runtime.phases.file_fsync.wall.aggregate_ns",
            "runtime.phases.replace.wall.aggregate_ns",
            "runtime.phases.directory_fsync.wall.aggregate_ns",
            *[f"runtime.phases.J{i}.wall.aggregate_ns" for i in range(6)],
        ],
        "runtime.phase_fsync_ns": [
            "runtime.phases.file_fsync.wall.aggregate_ns",
            "runtime.phases.directory_fsync.wall.aggregate_ns",
        ],
        "runtime.phase_replace_ns": ["runtime.phases.replace.wall.aggregate_ns"],
        "runtime.phase_recovery_ns": ["runtime.phases.recovery.wall.aggregate_ns"],
        "runtime.phase_adapter_ns": ["runtime.phases.adapter.wall.aggregate_ns"],
        "runtime.phase_verification_ns": ["runtime.phases.verify.wall.aggregate_ns"],
        "runtime.sample_count": [f"runtime.phases.{p}.sample_count" for p in RUNTIME_PHASES],
        "runtime.minimum": [f"runtime.phases.{p}.{m}.minimum_ns" for p in RUNTIME_PHASES for m in RUNTIME_METRICS],
        "runtime.median": [f"runtime.phases.{p}.{m}.median_ns" for p in RUNTIME_PHASES for m in RUNTIME_METRICS],
        "runtime.p95": [f"runtime.phases.{p}.{m}.p95_ns" for p in RUNTIME_PHASES for m in RUNTIME_METRICS],
        "runtime.maximum": [f"runtime.phases.{p}.{m}.maximum_ns" for p in RUNTIME_PHASES for m in RUNTIME_METRICS],
        "runtime.timing_is_measurement_only": ["runtime.timing_is_measurement_only"],
        "storage.authoritative_logical_bytes": ["storage.authoritative.logical_bytes"],
        "storage.authoritative_allocated_bytes": ["storage.authoritative.allocated_bytes"],
        "storage.staging_peak_logical_bytes": ["storage.staging.logical_bytes"],
        "storage.staging_peak_allocated_bytes": ["storage.staging.allocated_bytes"],
        "storage.directory_logical_bytes": ["storage.directory.logical_bytes"],
        "storage.directory_allocated_bytes": ["storage.directory.allocated_bytes"],
        "storage.evidence_logical_bytes": ["storage.raw_evidence.logical_bytes", "storage.normalized_evidence.logical_bytes"],
        "storage.evidence_allocated_bytes": ["storage.raw_evidence.allocated_bytes", "storage.normalized_evidence.allocated_bytes"],
        "storage.code_spec_bundle_logical_bytes": ["storage.source_spec.logical_bytes"],
        "storage.code_spec_bundle_allocated_bytes": ["storage.source_spec.allocated_bytes"],
        "storage.interpreter_runtime_proxy_logical_bytes": ["storage.runtime_interpreter.logical_bytes"],
        "storage.interpreter_runtime_proxy_allocated_bytes": ["storage.runtime_interpreter.allocated_bytes"],
        "storage.filesystem_delta_logical_bytes": ["storage.filesystem_delta.logical_bytes"],
        "storage.filesystem_delta_allocated_bytes": ["storage.filesystem_delta.allocated_bytes"],
        "storage.incomplete_or_shared_totals_statement": ["storage.incomplete_totals_statement", "storage.shared_bytes", "storage.unattributable_bytes"],
        "operations.namespace_requirements": ["operations.namespace_steps"],
        "operations.syscall_counts_by_name": ["operations.complete_syscall_counts_by_name"],
        "operations.fsync_count": ["operations.syscall_counts.fsync"],
        "operations.replace_count": ["operations.syscall_counts.replace"],
        "operations.open_count": ["operations.syscall_counts.open"],
        "operations.read_count": ["operations.syscall_counts.read"],
        "operations.write_count": ["operations.syscall_counts.write"],
        "operations.close_count": ["operations.syscall_counts.close"],
        "operations.setup_steps": ["operations.setup_steps"],
        "operations.cleanup_steps": ["operations.cleanup_steps"],
        "operations.retries": ["operations.retry_count"],
        "operations.failed_operations": ["operations.failure_count"],
        "operations.recovery_actions": ["operations.recovery_actions"],
        "evolution.compatible_derived_observer_probe": ["evolution.compatible_factor_through_observer"],
        "evolution.split_extension_collision_result": ["evolution.split_extension_collision_result"],
        "evolution.format_support_status": ["evolution.format_support"],
        "evolution.version_support_status": ["evolution.version_support"],
        "evolution.generation_support_status": ["evolution.generation_support"],
        "evolution.rollback_result": ["evolution.rollback_support"],
        "evolution.freshness_result": ["evolution.freshness_support"],
        "portability.exact_E_T_observation_equality": ["portability.exact_E_T_behavioral_comparison"],
        "portability.backend_specific_branches": ["portability.backend_variant_branches"],
        "portability.backend_specific_lines": ["portability.backend_variant_lines"],
        "portability.untested_platforms": ["portability.untested_platforms"],
        "explainability.recovery_tag": ["explainability.recovery_tag"],
        "explainability.smallest_failing_trial_record": ["explainability.smallest_trial"],
        "explainability.causal_stage_or_fault_label": ["explainability.causal_stage_or_fault_label"],
        "explainability.explanation_steps": ["explainability.causal_steps"],
        "explainability.human_comprehension_status": ["explainability.human_comprehension_study"],
        "information_loss.truncation_case_count_and_outcomes": ["information_loss_risk.truncation_faults"],
        "information_loss.bit_case_count_and_outcomes": ["information_loss_risk.bit_faults"],
        "information_loss.error_case_count_and_outcomes": ["information_loss_risk.error_faults", "information_loss_risk.io_faults"],
        "information_loss.undetected_coherent_replacements": ["information_loss_risk.undetected_coherent_replacement_count", "information_loss_risk.coherent_replacement_faults"],
        "information_loss.unsupported_fault_classes": ["information_loss_risk.unsupported_fault_classes"],
        "information_loss.hash_assumption": ["information_loss_risk.hash_assumption"],
        "information_loss.recovery_false_accept_count": ["information_loss_risk.false_accept_count"],
        "information_loss.recovery_false_reject_count": ["information_loss_risk.false_reject_count"],
    }

    simple_prefixes = {
        "authoring.": "authoring_burden.",
        "human_cognition.": "human_cognition.",
        "query.": "query_navigation_burden.",
        "storage.": "storage.",
        "operations.": "operations.",
        "evolution.": "evolution.",
        "portability.": "portability.",
        "explainability.": "explainability.",
    }

    component_alias = {
        "adapter": "adapter",
        "contract": "contract",
        "injector": "injector",
        "manifest": "contract",
        "publisher": "publisher",
        "recovery": "recovery",
        "supervisor": "controller",
        "verifier": "verifier",
    }

    result: dict[str, Any] = {}
    unmapped: list[str] = []
    for old in old_paths:
        targets = direct.get(old)
        relation = "RENAMED_OR_EXPLICITLY_EXPANDED"
        if targets is None and old.startswith("semantic_machinery.file_list."):
            component = component_alias[old.rsplit(".", 1)[1]]
            targets = [f"semantic_machinery.components.{component}.files"]
        if targets is None and old.startswith("semantic_machinery."):
            leaf = old.rsplit(".", 1)[1]
            field_map = {
                "generated_table_bytes": "generated_bytes",
                "generated_table_cells": "generated_cells",
                "logical_lines": "logical_lines",
                "physical_lines": "physical_lines",
                "sha256_per_file": "sha256_per_file",
                "source_bytes": "source_bytes",
            }
            if leaf in field_map:
                targets = [f"semantic_machinery.components.{c}.{field_map[leaf]}" for c in SEMANTIC_COMPONENTS]
        if targets is None and old.startswith("tcb.every_registered_component."):
            leaf = old.rsplit(".", 1)[1]
            field = {"version": "version", "source": "source", "bytes_or_explicit_unknown": "code_config_bytes"}[leaf]
            targets = [f"trusted_computing_base.components.{c}.{field}" for c in TCB_COMPONENTS]
        if targets is None:
            for old_prefix, new_prefix in simple_prefixes.items():
                if old.startswith(old_prefix):
                    candidate = new_prefix + old[len(old_prefix):]
                    if candidate in new_paths:
                        targets = [candidate]
                    break
        if targets is None:
            unmapped.append(old)
            continue
        missing = sorted(set(targets) - new_paths)
        if missing:
            raise ValueError(f"crosswalk target missing for {old}: {missing}")
        result[old] = {"relation": relation, "targets": sorted(set(targets))}
    if unmapped:
        raise ValueError("unmapped historical breaker paths:\n" + "\n".join(unmapped))
    return result


def runtime_invariants() -> list[dict[str, Any]]:
    rules = []
    for phase in RUNTIME_PHASES:
        count = f"runtime.phases.{phase}.sample_count"
        for metric in RUNTIME_METRICS:
            prefix = f"runtime.phases.{phase}.{metric}"
            rules.append(
                {
                    "aggregate": f"{prefix}.aggregate_ns",
                    "maximum": f"{prefix}.maximum_ns",
                    "median": f"{prefix}.median_ns",
                    "median_rule": "sorted_values[(n-1)//2]",
                    "metric": metric,
                    "minimum": f"{prefix}.minimum_ns",
                    "p95": f"{prefix}.p95_ns",
                    "p95_rule": "nearest_rank_ceiling_0.95",
                    "phase": phase,
                    "sample_count": count,
                    "series": f"{prefix}.series_ns",
                    "status_propagation": "all_seven_paths_native_or_all_seven_paths_same_structured_status",
                }
            )
    return rules


def build_invariants() -> dict[str, Any]:
    count_list = []
    for stem in ("failure_label", "required_concept", "role"):
        plural = {"failure_label": "failure_labels", "required_concept": "required_concepts", "role": "roles"}[stem]
        count_list.append({"count": f"human_cognition.{stem}_count", "list": f"human_cognition.{plural}"})
    for stem in ("cleanup_step", "namespace_step", "recovery_action", "setup_step", "signal", "trace_action", "wait"):
        plural = {
            "cleanup_step": "cleanup_steps",
            "namespace_step": "namespace_steps",
            "recovery_action": "recovery_actions",
            "setup_step": "setup_steps",
            "signal": "signals",
            "trace_action": "trace_actions",
            "wait": "waits",
        }[stem]
        count_list.append({"count": f"operations.{stem}_count", "list": f"operations.{plural}"})
    for stem, plural in (
        ("fixture", "fixtures"),
        ("manifest_entry", "manifest_entries"),
        ("parameter", "parameters"),
    ):
        count_list.append(
            {
                "count": f"authoring_burden.{stem}_count",
                "list": f"authoring_burden.{plural}",
            }
        )
    count_list.append(
        {
            "count": "query_navigation_burden.continuation_count",
            "list": "query_navigation_burden.continuations",
        }
    )

    file_hash = [
        {
            "files": f"semantic_machinery.components.{component}.files",
            "hashes": f"semantic_machinery.components.{component}.sha256_per_file",
            "rule": "file_paths_equal_hash_inventory_paths",
        }
        for component in SEMANTIC_COMPONENTS
    ]
    persistent_storage = []
    for area in ("authoritative", "staging"):
        for metric in ("allocated_bytes", "logical_bytes"):
            persistent_storage.append(
                {
                    "left": f"persistent_state.{area}_{metric}",
                    "right": f"storage.{area}.{metric}",
                    "rule": "value_unit_scope_equal_when_both_native",
                }
            )
    return {
        "complexity_byte_changes": [
            {
                "path": f"where_is_complexity_now.{variant}.changed_persisted_bytes",
                "rule": "delta_bytes=after_bytes-before_bytes;zero_still_requires_nonempty_scope_and_method",
            }
            for variant in DELETION_VARIANTS + EXTERNALIZATION_VARIANTS
        ],
        "count_list_equalities": count_list,
        "continuation_inventory": {
            "bytes": "query_navigation_burden.continuation_bytes",
            "inventory": "query_navigation_burden.continuations",
            "rules": [
                "each_byte_length_equals_len(continuation_hex)/2",
                "continuation_count_equals_inventory_length",
                "continuation_bytes_equals_sum(byte_length)",
            ],
        },
        "evidence_stream_inventory": {
            "exact_members": list(EVIDENCE_STREAMS),
            "inventory": "storage.retained_stream_inventory",
            "rules": [
                "members_equal_evidence_stream_registry",
                "every_member_has_byte_length_sha256_retained_replay_available",
                "retained_false_requires_replay_available_false",
            ],
        },
        "family_count_equation": {
            "for_each": list(FAMILIES),
            "rule": "trial_totals=pass+fail+unknown+unsupported",
            "paths": {
                "fail": "information_distinction_preservation.fail_counts_by_family",
                "pass": "information_distinction_preservation.pass_counts_by_family",
                "total": "information_distinction_preservation.trial_totals_by_family",
                "unknown": "information_distinction_preservation.unknown_counts_by_family",
                "unsupported": "information_distinction_preservation.unsupported_counts_by_family",
            },
        },
        "file_hash_key_equalities": file_hash,
        "persistent_storage_equalities": persistent_storage,
        "replay_consistency": {
            "rules": [
                "trial_id_is_unique",
                "ordinal_equals_position_in_unsigned_utf8_trial_id_order",
                "offset_and_length_select_exactly_one_framed_record",
                "record_sha256_matches_selected_bytes",
            ],
            "selector_path": "operations.replay_selector",
            "verdict_path": "operations.replay_consistency",
        },
        "runtime_statistics": runtime_invariants(),
        "syscall_specific_counts": {
            "inventory": "operations.complete_syscall_counts_by_name",
            "members": {name: f"operations.syscall_counts.{name}" for name in ("close", "fsync", "open", "read", "replace", "write")},
            "rule": "specific_value_equals_inventory_entry_when_both_native",
        },
        "zero_rule": "Every measured_nonnegative_integer contains nonempty scope, method, and unit; zero has no special shortcut and is accepted only in that measured wrapper.",
    }


def requirement_coverage() -> dict[str, list[str]]:
    return {
        "apparatus": [
            "operations.apparatus_deadline_ns",
            "operations.apparatus_overrun_status",
            "operations.apparatus_storage_bound_bytes",
        ],
        "authored_items": [
            "authoring_burden.fixture_count",
            "authoring_burden.fixtures",
            "authoring_burden.manifest_entries",
            "authoring_burden.manifest_entry_count",
            "authoring_burden.parameter_count",
            "authoring_burden.parameters",
        ],
        "breaker_witness": [
            "information_distinction_preservation.separating_witness.C",
            "information_distinction_preservation.separating_witness.Y0",
            "information_distinction_preservation.separating_witness.Y1",
        ],
        "environment": [
            "operations.effective_environment",
            "operations.inherited_environment_allowlist",
            "operations.launcher_environment_construction",
        ],
        "evidence_stream": [
            "storage.normalized_evidence.allocated_bytes",
            "storage.normalized_evidence.logical_bytes",
            "storage.raw_evidence.allocated_bytes",
            "storage.raw_evidence.logical_bytes",
            "storage.retained_stream_inventory",
        ],
        "evolution": [
            "evolution.class_splitting_probe",
            "evolution.compatible_factor_through_observer",
            "evolution.external_information_required",
            "evolution.format_support",
            "evolution.freshness_support",
            "evolution.generation_support",
            "evolution.migration_bytes",
            "evolution.migration_inputs",
            "evolution.migration_support",
            "evolution.rollback_support",
            "evolution.split_extension_collision_result",
            "evolution.version_support",
        ],
        "manifest_and_selector": [
            "persistent_state.manifest_state_bytes",
            "persistent_state.selector_state_bytes",
        ],
        "operations": [
            "operations.complete_syscall_counts_by_name",
            *[f"operations.syscall_counts.{name}" for name in ("close", "fsync", "open", "read", "replace", "write")],
            "operations.reaping_observation_method",
        ],
        "query_continuations": [
            "query_navigation_burden.continuation_bytes",
            "query_navigation_burden.continuation_count",
            "query_navigation_burden.continuations",
        ],
        "replay": [
            "operations.replay_consistency",
            "operations.replay_selector",
            "storage.replay_index.allocated_bytes",
            "storage.replay_index.logical_bytes",
        ],
        "risk": [
            "information_loss_risk.false_accept_count",
            "information_loss_risk.false_reject_count",
            "information_loss_risk.hash_assumption",
            "information_loss_risk.hash_collision_status",
            "information_loss_risk.undetected_coherent_replacement_count",
            "information_loss_risk.unsupported_fault_classes",
        ],
        "runtime_slots": [
            f"runtime.phases.J{slot}.{metric}.{leaf}"
            for slot in range(6)
            for metric in RUNTIME_METRICS
            for leaf in ("series_ns", "aggregate_ns", "minimum_ns", "median_ns", "p95_ns", "maximum_ns")
        ],
        "runtime_operation_phases": [
            f"runtime.phases.{phase}.{metric}.{leaf}"
            for phase in ("acquisition", "file_fsync", "replace", "directory_fsync")
            for metric in RUNTIME_METRICS
            for leaf in ("series_ns", "aggregate_ns", "minimum_ns", "median_ns", "p95_ns", "maximum_ns")
        ],
        "trace": [
            "operations.configured_output_descriptors",
            "operations.trace_actions",
            "operations.trace_completeness",
            "operations.trace_window",
        ],
    }


def status_schemas() -> dict[str, Any]:
    unknown = closed_object(
        {
            "needed_evidence": ref("nonempty_utf8"),
            "reason": ref("nonempty_utf8"),
            "status": {"const": "UNKNOWN", "type": "string"},
        }
    )
    unsupported = closed_object(
        {
            "reason": ref("nonempty_utf8"),
            "status": {"const": "UNSUPPORTED", "type": "string"},
        }
    )
    return {"UNKNOWN": unknown, "UNSUPPORTED": unsupported}


def validate_closed_objects(value: Any, location: str = "root") -> None:
    if isinstance(value, dict):
        if value.get("type") == "object" and value.get("additionalProperties") is not False:
            raise ValueError(f"open object schema at {location}")
        for key, child in value.items():
            validate_closed_objects(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_closed_objects(child, f"{location}[{index}]")


def validate_schema_refs(value: Any, known_native: set[str], location: str = "root") -> None:
    if isinstance(value, dict):
        if "$ref" in value:
            prefix = "#/native_value_kinds/definitions/"
            target = value["$ref"]
            if not isinstance(target, str) or not target.startswith(prefix) or target[len(prefix):] not in known_native:
                raise ValueError(f"invalid schema reference at {location}: {target!r}")
        for key, child in value.items():
            validate_schema_refs(child, known_native, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_schema_refs(child, known_native, f"{location}[{index}]")


def validate_registry(registry: dict[str, Any]) -> None:
    paths = registry["paths"]
    path_set = set(paths)
    if paths != sorted(paths) or len(paths) != len(path_set):
        raise ValueError("paths must be sorted and unique")
    if any(any(token in path for token in ("*", "[", "]")) for path in paths):
        raise ValueError("wildcard-like path found")
    policies = registry["path_policies"]
    kinds = registry["native_value_kinds"]["paths"]
    if set(policies) != path_set or set(kinds) != path_set:
        raise ValueError("path policies/native kinds do not cover the closed path set")
    known_kinds = set(registry["native_value_kinds"]["definitions"]) | set(registry["closed_container_schemas"])
    unknown_kinds = set(kinds.values()) - known_kinds
    if unknown_kinds:
        raise ValueError(f"undefined native kinds: {sorted(unknown_kinds)}")
    expected_native_only = {path for path in path_set if path.startswith("identity.")} | set(
        NORMATIVE_ASSERTION_PATHS
    )
    actual_native_only = {
        path for path, policy in policies.items() if policy["status_policy"] == "NATIVE_ONLY"
    }
    if actual_native_only != expected_native_only:
        raise ValueError("identity and normative assertion NATIVE_ONLY set changed")
    actual_unsupported = {
        path
        for path, policy in policies.items()
        if policy["status_policy"] == "NATIVE_OR_UNKNOWN_OR_UNSUPPORTED"
    }
    if actual_unsupported != set(UNSUPPORTED_ALLOWED_PATHS):
        raise ValueError("UNSUPPORTED policy is not exactly the frozen allowlist")
    for path in path_set - expected_native_only - set(UNSUPPORTED_ALLOWED_PATHS):
        if policies[path]["status_policy"] != "NATIVE_OR_UNKNOWN":
            raise ValueError(f"non-allowlisted path permits wrong status set: {path}")
    exact_identity_kinds = {
        "identity.backend": "backend_id",
        "identity.contract_profile": "contract_profile_id",
        "identity.manifest": "mechanism_manifest_id",
        "identity.run_id": "run_id",
        "identity.schema_id": "registry_schema_id",
    }
    if any(kinds[path] != kind for path, kind in exact_identity_kinds.items()):
        raise ValueError("identity native kinds are not exact")
    if set(registry["historical_breaker_crosswalk"]) != set(load_breaker_paths()):
        raise ValueError("historical breaker crosswalk is not exactly 144 entries")
    for old, mapping in registry["historical_breaker_crosswalk"].items():
        if not mapping["targets"] or not set(mapping["targets"]) <= path_set:
            raise ValueError(f"invalid crosswalk targets for {old}")
    actual_dimensions = {path.split(".", 1)[0] for path in paths} & set(DIMENSIONS)
    if actual_dimensions != set(DIMENSIONS):
        raise ValueError("not all fourteen dimensions are instantiated")
    for component in registry["semantic_component_registry"]:
        actual = {
            path.rsplit(".", 1)[1]
            for path in paths
            if path.startswith(f"semantic_machinery.components.{component}.")
        }
        if actual != set(registry["semantic_component_field_registry"]):
            raise ValueError(f"incomplete semantic expansion: {component}")
    for component in registry["tcb_component_registry"]:
        actual = {
            path.rsplit(".", 1)[1]
            for path in paths
            if path.startswith(f"trusted_computing_base.components.{component}.")
        }
        if actual != set(registry["tcb_component_field_registry"]):
            raise ValueError(f"incomplete TCB expansion: {component}")
    for variant in registry["deletion_variant_registry"] + registry["externalization_variant_registry"]:
        actual = {
            path.rsplit(".", 1)[1]
            for path in paths
            if path.startswith(f"where_is_complexity_now.{variant}.")
        }
        if actual != set(registry["complexity_field_registry"]):
            raise ValueError(f"incomplete complexity expansion: {variant}")
    semantics = registry["measurement_semantics_by_path"]
    if set(semantics) != path_set:
        raise ValueError("measurement semantics map is not total over paths")
    deletion_mutations = [item["deletion_mutation"] for item in semantics.values()]
    if len(deletion_mutations) != len(set(deletion_mutations)):
        raise ValueError("leaf-deletion mutations are not unique")
    required_semantics = {
        "aggregation_rule",
        "applicability_rule",
        "deletion_mutation",
        "scope",
        "unit",
    }
    if any(set(item) != required_semantics or any(not value for value in item.values()) for item in semantics.values()):
        raise ValueError("per-path measurement semantics are incomplete")
    evidence_schema = registry["closed_container_schemas"]["evidence_stream_inventory"]
    if set(evidence_schema["properties"]) != set(EVIDENCE_STREAMS):
        raise ValueError("evidence-stream container is not the exact frozen registry")
    old_new_item = registry["closed_container_schemas"]["old_new_matrix"]["items"]
    if set(old_new_item["properties"]) != {"actual_hex", "cut", "expected_hex", "setup", "verdict"}:
        raise ValueError("old/new matrix does not retain actual, expected, and verdict")
    validate_closed_objects(registry["native_value_kinds"]["definitions"], "native_value_kinds.definitions")
    validate_closed_objects(registry["closed_container_schemas"], "closed_container_schemas")
    validate_closed_objects(registry["structured_statuses"], "structured_statuses")
    validate_schema_refs(registry["native_value_kinds"]["definitions"], set(registry["native_value_kinds"]["definitions"]), "native_value_kinds.definitions")
    validate_schema_refs(registry["closed_container_schemas"], set(registry["native_value_kinds"]["definitions"]), "closed_container_schemas")
    validate_schema_refs(registry["structured_statuses"], set(registry["native_value_kinds"]["definitions"]), "structured_statuses")
    for name, status in registry["structured_statuses"].items():
        if status["additionalProperties"] is not False or set(status["required"]) != set(status["properties"]):
            raise ValueError(f"status schema is not exact: {name}")
    for invariant_group in ("count_list_equalities", "file_hash_key_equalities", "persistent_storage_equalities"):
        for item in registry["invariants"][invariant_group]:
            for key, value in item.items():
                if key in {"count", "list", "files", "hashes", "left", "right"} and value not in path_set:
                    raise ValueError(f"invariant references missing path: {value}")
    for key in ("bytes", "inventory"):
        if registry["invariants"]["continuation_inventory"][key] not in path_set:
            raise ValueError("continuation invariant references a missing path")
    if registry["invariants"]["evidence_stream_inventory"]["inventory"] not in path_set:
        raise ValueError("evidence-stream invariant references a missing path")
    for item in registry["invariants"]["complexity_byte_changes"]:
        if item["path"] not in path_set:
            raise ValueError(f"complexity invariant references missing path: {item['path']}")
    for item in registry["invariants"]["runtime_statistics"]:
        for key in ("aggregate", "maximum", "median", "minimum", "p95", "sample_count", "series"):
            if item[key] not in path_set:
                raise ValueError(f"runtime invariant references missing path: {item[key]}")
    for responsibility, targets in registry["requirement_coverage"].items():
        if not targets or not set(targets) <= path_set:
            raise ValueError(f"requirement coverage is incomplete: {responsibility}")


def build_registry() -> dict[str, Any]:
    native, containers = build_schema_definitions()
    builder = build_paths()
    path_set = set(builder.paths)
    breaker_paths = load_breaker_paths()
    crosswalk = make_crosswalk(breaker_paths, path_set)
    registry = {
        "closed_container_schemas": containers,
        "complexity_field_registry": list(COMPLEXITY_FIELDS),
        "deletion_variant_registry": list(DELETION_VARIANTS),
        "dimension_registry": list(DIMENSIONS),
        "externalization_variant_registry": list(EXTERNALIZATION_VARIANTS),
        "evidence_stream_registry": list(EVIDENCE_STREAMS),
        "family_registry": list(FAMILIES),
        "historical_breaker_crosswalk": crosswalk,
        "historical_breaker_registry": {
            "crosswalk_entry_count": len(crosswalk),
            "path_count": BREAKER_PATH_COUNT,
            "role": "retained_attack_input_with_complete_v2_crosswalk",
            "sha256": BREAKER_SHA256,
        },
        "invariants": build_invariants(),
        "native_value_kinds": {
            "definitions": native,
            "paths": dict(sorted(builder.paths.items())),
            "rule": "Each path accepts its exact native kind subject to its per-path policy, or exactly one permitted structured status object.",
        },
        "measurement_semantics_by_path": measurement_semantics(builder),
        "mechanism_manifest_registry": list(MECHANISM_MANIFESTS),
        "path_policies": dict(sorted(builder.policies.items())),
        "path_semantics": {
            "closed_report": True,
            "deletion_domain": "each_exact_path_once_and_each_required_closed_container_member_once",
            "explicit_unknown_is_schema_complete_but_not_a_measurement_pass": True,
            "explicit_unsupported_is_schema_complete_but_not_a_measurement_pass": True,
            "missing_leaf_verdict": "FAIL(MISSING_MEASUREMENT:path)",
            "no_null_empty_or_bare_placeholder": True,
            "separator": ".",
            "status_policies": {
                "NATIVE_ONLY": "Only the declared native kind is legal.",
                "NATIVE_OR_UNKNOWN": "The native kind or the exact structured UNKNOWN status is legal; UNKNOWN prevents a measurement pass.",
                "NATIVE_OR_UNKNOWN_OR_UNSUPPORTED": "The native kind or one exact structured status is legal; either structured status prevents a measurement pass.",
            },
            "unregistered_path_verdict": "FAIL(UNREGISTERED_MEASUREMENT:path)",
            "wildcard_paths": False,
        },
        "paths": sorted(path_set),
        "previous_registry": {
            "byte_length": V1_BYTE_LENGTH,
            "path_count": V1_PATH_COUNT,
            "schema_id": V1_SCHEMA_ID,
            "sha256": V1_SHA256,
        },
        "runtime_metric_registry": list(RUNTIME_METRICS),
        "runtime_phase_registry": list(RUNTIME_PHASES),
        "requirement_coverage": requirement_coverage(),
        "schema_id": "R01B-MEASUREMENT-PATHS-2",
        "semantic_component_registry": list(SEMANTIC_COMPONENTS),
        "semantic_component_field_registry": list(SEMANTIC_EXPANDED_FIELDS),
        "structured_statuses": status_schemas(),
        "tcb_component_registry": list(TCB_COMPONENTS),
        "tcb_component_field_registry": list(TCB_FIELDS),
        "unsupported_path_registry": sorted(UNSUPPORTED_ALLOWED_PATHS),
    }
    validate_registry(registry)
    return registry


def encoded_registry() -> bytes:
    registry = build_registry()
    return (json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify that the retained artifact is exactly regenerated")
    args = parser.parse_args()
    data = encoded_registry()
    if args.check:
        retained = OUTPUT.read_bytes()
        if retained != data:
            raise SystemExit("R01B-MEASUREMENT-REGISTRY.json is not the deterministic V2 output")
    else:
        OUTPUT.write_bytes(data)
    obj = json.loads(data)
    print(f"schema_id={obj['schema_id']}")
    print(f"paths={len(obj['paths'])}")
    print(f"crosswalk={len(obj['historical_breaker_crosswalk'])}")
    print(f"bytes={len(data)}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
