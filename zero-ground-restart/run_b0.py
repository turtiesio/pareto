#!/usr/bin/env python3
"""Run the frozen B0 / executable B1 falsification experiment.

The program writes no evidence files implicitly. Its deterministic JSON output
can be captured by a caller that chooses where generated evidence belongs.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path
import statistics
import time
from typing import Iterable

from c0_candidates import (
    OrdinalCandidate,
    OrdinalEncoding,
    QuotientBoundaryMachine,
    RepresentativeCandidate,
    RepresentativeEncoding,
    SPECIFICATION_FILES,
    encode_history,
)
from c0_experiment import (
    COMPONENT_NAMES,
    DISABLED,
    ENABLED,
    BoundedResiduals,
    Context,
    Observation,
    StableRightCongruence,
    direct_deletion_witnesses,
    exhaustive_component_deletions,
    future_contexts,
    generate_histories,
    mask_names,
    minimized_pair_witness_certificate,
    pair_merge_certificate,
    rebuild_owed_port_from_kind,
    rebuild_rule_on_0_from_b1_specification,
)
from c0_evolution import (
    authored_crossing_count_observer,
    current_b1_observer,
    factor_probe,
)
from c0_core import build_witness_core
from c0_oracle import ACTION, CLIENT, INPUTS, Frame, Snapshot, accept, inbound, replay, resume


def candidate_observation(
    machine: QuotientBoundaryMachine,
    key: tuple[str, ...],
    context: Context,
) -> Observation:
    admission: list[str] = []
    client: list[str] = []
    action: list[str] = []
    current = key
    for operation in context.operations:
        if operation == "resume":
            step = machine.resume_step(current)
        else:
            assert isinstance(operation, Frame)
            step = machine.input_step(current, operation)
            admission.append(step.admission)
        client.extend(step.client)
        action.extend(step.action)
        current = step.next_key
    return Observation(tuple(admission), tuple(client), tuple(action))


def verify_boundary_step(
    machine: QuotientBoundaryMachine,
    snapshot: Snapshot,
    operation: Frame | str,
) -> None:
    """Compare one decoded candidate step with the independent raw oracle."""

    key = machine.class_key(snapshot)
    if operation == "resume":
        raw = resume(snapshot)
        candidate = machine.resume_step(key)
        raw_client = tuple(frame.token() for frame in raw.crossed if frame.port == CLIENT)
        raw_action = tuple(frame.token() for frame in raw.crossed if frame.port == ACTION)
        if (
            candidate.client != raw_client
            or candidate.action != raw_action
            or candidate.next_key != machine.class_key(raw.snapshot)
        ):
            raise AssertionError("candidate resume decoder disagrees with raw oracle")
        return

    assert isinstance(operation, Frame)
    raw = accept(snapshot, operation)
    candidate = machine.input_step(key, operation)
    expected_admission = ENABLED if raw.legal else DISABLED
    if candidate.admission != expected_admission:
        raise AssertionError("candidate admission disagrees with raw oracle")
    if candidate.next_key != machine.class_key(raw.snapshot):
        raise AssertionError("candidate transition disagrees with raw oracle")


def verify_candidates(
    histories: Iterable[tuple[Frame, ...]],
    contexts: tuple[Context, ...],
    machine: QuotientBoundaryMachine,
    *,
    check_all_contexts: bool,
) -> dict[str, int]:
    ordinal = OrdinalCandidate(machine)
    representative = RepresentativeCandidate(machine)
    encode_recover_checks = 0
    unique_snapshots: dict[Snapshot, tuple[Frame, ...]] = {}
    ordinal_seen: dict[object, tuple[str, ...]] = {}
    representative_seen: dict[object, tuple[str, ...]] = {}
    ordinal_collisions = 0
    representative_collisions = 0

    for history in histories:
        snapshot = replay(history)
        expected = machine.class_key(snapshot)
        ordinal_encoding = ordinal.persist(snapshot)
        representative_encoding = representative.persist(snapshot)
        if ordinal.recover(ordinal_encoding) != expected:
            raise AssertionError("ordinal in-process encode/recover changed quotient class")
        if representative.recover(representative_encoding) != expected:
            raise AssertionError("representative in-process encode/recover changed quotient class")
        prior = ordinal_seen.setdefault(ordinal_encoding, expected)
        if prior != expected:
            ordinal_collisions += 1
        prior = representative_seen.setdefault(representative_encoding, expected)
        if prior != expected:
            representative_collisions += 1
        unique_snapshots.setdefault(snapshot, history)
        encode_recover_checks += 2

    transition_checks = 0
    for snapshot in unique_snapshots:
        verify_boundary_step(machine, snapshot, "resume")
        transition_checks += 1

        for frame in INPUTS:
            verify_boundary_step(machine, snapshot, frame)
            transition_checks += 1

    decoded_context_checks = 0
    contexts_to_check = contexts if check_all_contexts else contexts[:: max(1, len(contexts) // 64)]
    for snapshot in unique_snapshots:
        key = machine.class_key(snapshot)
        from c0_experiment import evaluate_context

        for context in contexts_to_check:
            expected = evaluate_context(snapshot, context)
            actual = candidate_observation(machine, key, context)
            if actual != expected:
                raise AssertionError(
                    f"decoded context differs: {context.token()}\n{actual}\n{expected}"
                )
            decoded_context_checks += 1

    return {
        "in_process_encode_recover_round_trips": encode_recover_checks,
        "one_step_decoder_checks": transition_checks,
        "decoded_context_checks": decoded_context_checks,
        "unique_cut_snapshots": len(unique_snapshots),
        "ordinal_encoding_collisions": ordinal_collisions,
        "representative_encoding_collisions": representative_collisions,
    }


def verify_full_universe_encodings(
    machine: QuotientBoundaryMachine,
) -> dict[str, int]:
    """Exhaust both encoders and every boundary operation over all table classes."""

    ordinal = OrdinalCandidate(machine)
    representative = RepresentativeCandidate(machine)
    ordinal_values: set[OrdinalEncoding] = set()
    representative_values: set[RepresentativeEncoding] = set()
    boundary_differential_checks = 0
    for rank, key in enumerate(machine.ordered_keys):
        canonical_history = machine.representatives[key]
        canonical_snapshot = replay(canonical_history)
        if machine.class_key(canonical_snapshot) != key:
            raise AssertionError("canonical representative replays to the wrong class")
        # Exercise the actual public persist methods, not hand-built encodings.
        ordinal_encoding = ordinal.persist(canonical_snapshot)
        representative_encoding = representative.persist(canonical_snapshot)
        if ordinal.recover(ordinal_encoding) != key:
            raise AssertionError("full-universe ordinal decoder mismatch")
        if representative.recover(representative_encoding) != key:
            raise AssertionError("full-universe representative decoder mismatch")
        ordinal_values.add(ordinal_encoding)
        representative_values.add(representative_encoding)
        verify_boundary_step(machine, canonical_snapshot, "resume")
        boundary_differential_checks += 1
        for frame in INPUTS:
            verify_boundary_step(machine, canonical_snapshot, frame)
            boundary_differential_checks += 1
    expected = len(machine.ordered_keys)
    if len(ordinal_values) != expected or len(representative_values) != expected:
        raise AssertionError("full-universe candidate encoding collision")
    return {
        "full_universe_classes": expected,
        "ordinal_full_universe_in_process_encode_recover": expected,
        "representative_full_universe_in_process_encode_recover": expected,
        "ordinal_full_universe_distinct_encodings": len(ordinal_values),
        "representative_full_universe_distinct_encodings": len(representative_values),
        "full_universe_resume_and_16_input_differential_checks": boundary_differential_checks,
    }


def verify_deterministic_rebuild(
    original: QuotientBoundaryMachine,
) -> dict[str, object]:
    """Cleanly regenerate the quotient/table and compare exact bound artifacts."""

    rebuilt = QuotientBoundaryMachine(StableRightCongruence())
    digest_equal = rebuilt.specification_digest == original.specification_digest
    ranks_equal = rebuilt.ordered_keys == original.ordered_keys
    representatives_equal = rebuilt.representatives == original.representatives
    if not (digest_equal and ranks_equal and representatives_equal):
        raise AssertionError("clean quotient/table regeneration was not deterministic")
    return {
        "clean_rebuilds": 1,
        "artifact_digest_equal_after_clean_rebuild": digest_equal,
        "rank_order_equal_after_clean_rebuild": ranks_equal,
        "canonical_representatives_equal_after_clean_rebuild": representatives_equal,
    }


def verify_may_rebuild_recipes(
    machine: QuotientBoundaryMachine,
) -> dict[str, object]:
    """Exhaust exact B1 derivation recipes over every boundary class."""

    rule_checks = 0
    port_checks = 0
    observed_kinds: set[str] = set()
    for key in machine.ordered_keys:
        snapshot = replay(machine.representatives[key])
        rebuilt_on_0 = rebuild_rule_on_0_from_b1_specification()
        if rebuilt_on_0 != snapshot.rule[1]:
            raise AssertionError("rule_on_0 constant recipe failed")
        rule_checks += 1

        actual_kind = "-" if snapshot.owed is None else snapshot.owed.kind
        actual_port = "-" if snapshot.owed is None else snapshot.owed.port
        rebuilt_port = rebuild_owed_port_from_kind(actual_kind)
        if rebuilt_port != actual_port:
            raise AssertionError("owed-port-from-kind recipe failed")
        observed_kinds.add(actual_kind)
        port_checks += 1
    return {
        "rule_on_0": {
            "recipe": "return UTF-8 atom '0'; B1 admits only rule tables whose on_0 value is 0",
            "full_universe_checks": rule_checks,
        },
        "owed_port": {
            "recipe": "'-' for no owed output; 'action' iff owed_kind == 'DO'; otherwise 'client'",
            "full_universe_checks": port_checks,
            "observed_owed_kinds_including_quiescent_sentinel": sorted(observed_kinds),
        },
    }


def witness_json(value: object) -> object:
    if isinstance(value, str):
        return value
    data = asdict(value)  # type: ignore[arg-type]
    data["left_observation"] = asdict(value.left_observation)  # type: ignore[attr-defined]
    data["right_observation"] = asdict(value.right_observation)  # type: ignore[attr-defined]
    return data


def _distribution(values: Iterable[int]) -> dict[str, float | int]:
    materialized = sorted(values)
    return {
        "min": materialized[0],
        "median": statistics.median(materialized),
        "max": materialized[-1],
    }


def _artifact_inventory() -> list[dict[str, int | str]]:
    result = []
    verifier_paths = (
        *SPECIFICATION_FILES,
        Path(__file__).resolve().parent / "c0_core.py",
        Path(__file__).resolve().parent / "c0_evolution.py",
        Path(__file__).resolve().parent / "run_b0.py",
        Path(__file__).resolve().parent / "test_b0.py",
    )
    for path in dict.fromkeys(verifier_paths):
        data = path.read_bytes()
        result.append(
            {
                "file": path.name,
                "bytes": len(data),
                "physical_lines": len(data.splitlines()),
                "inventory_role": (
                    "artifact-bound specification/generator"
                    if path in SPECIFICATION_FILES
                    else "verification/evidence code not included in candidate artifact digest"
                ),
            }
        )
    return result


def _benchmarks(
    machine: QuotientBoundaryMachine,
    snapshots: tuple[Snapshot, ...],
    *,
    include_timing: bool,
) -> dict[str, object]:
    ordinal = OrdinalCandidate(machine)
    representative = RepresentativeCandidate(machine)
    ordinal_encodings = tuple(ordinal.persist(snapshot) for snapshot in snapshots)
    representative_encodings = tuple(representative.persist(snapshot) for snapshot in snapshots)

    operations = 0
    result: dict[str, object] = {
        "environment": "single CPython process; wall clock; not a physical realization test",
        "cut_classes": len(snapshots),
        "asymptotics": {
            "ordinal_recover": "O(1) table lookup after the table is available",
            "representative_recover": "O(serialized representative crossings + parse bytes)",
            "boundary_update": "O(1) generated table lookup in this finite realization",
        },
    }
    if not include_timing:
        result["timing"] = "excluded from deterministic evidence; run without --deterministic to measure"
        return result

    start = time.perf_counter()
    for encoding in ordinal_encodings:
        ordinal.recover(encoding)
    ordinal_seconds = time.perf_counter() - start

    # Clear only the raw replay memo so each distinct representative is parsed
    # and replayed once in this batch. This is a software cold-cache proxy, not
    # a physical cold-boot measurement.
    replay.cache_clear()
    start = time.perf_counter()
    for encoding in representative_encodings:
        representative.recover(encoding)
    representative_seconds = time.perf_counter() - start

    start = time.perf_counter()
    for snapshot in snapshots:
        key = machine.class_key(snapshot)
        machine.resume_step(key)
        operations += 1
        for frame in INPUTS:
            machine.input_step(key, frame)
            operations += 1
    update_seconds = time.perf_counter() - start
    result.update(
        {
            "timing": "measurement-only; excluded from deterministic certificates",
            "ordinal_recover_total_seconds": ordinal_seconds,
            "representative_parse_replay_total_seconds": representative_seconds,
            "boundary_table_operations": operations,
            "boundary_table_operations_total_seconds": update_seconds,
        }
    )
    return result


def run(
    *,
    max_inbound: int = 4,
    max_future_inputs: int = 2,
    full_context_check: bool = True,
    include_timing: bool = True,
) -> dict[str, object]:
    started = time.perf_counter()
    corpus = generate_histories(max_inbound)
    contexts = future_contexts(max_future_inputs)
    residuals = BoundedResiduals(contexts)
    bounded_ids = {residuals.class_id(replay(history)) for history in corpus.histories}

    congruence = StableRightCongruence()
    stable_keys = {congruence.class_key(replay(history)) for history in corpus.histories}
    machine = QuotientBoundaryMachine(congruence)

    candidate_checks = verify_candidates(
        corpus.histories, contexts, machine, check_all_contexts=full_context_check
    )
    full_universe_checks = verify_full_universe_encodings(machine)
    rebuild_checks = verify_deterministic_rebuild(machine)
    may_rebuild_checks = verify_may_rebuild_recipes(machine)
    deletions = exhaustive_component_deletions(corpus.histories, congruence.class_key)
    witnesses = direct_deletion_witnesses(corpus.histories, deletions, residuals)
    witness_core = build_witness_core(deletions, witnesses, residuals)
    pair_witnesses = minimized_pair_witness_certificate(
        corpus.histories, congruence.class_key, contexts
    )

    unique_snapshots = tuple(sorted({replay(history) for history in corpus.histories}, key=repr))
    corpus_rep_bytes = [
        len(encode_history(machine.representatives[machine.class_key(snapshot)]))
        for snapshot in unique_snapshots
    ]
    full_rep_bytes = [
        len(encode_history(history)) for history in machine.representatives.values()
    ]
    ordered_keys_text_proxy_bytes = sum(
        len(repr(key).encode("utf-8")) + 1 for key in machine.ordered_keys
    )
    rank_map_text_proxy_bytes = sum(
        len(repr((key, rank)).encode("utf-8")) + 1
        for key, rank in machine.rank_by_key.items()
    )
    representative_map_text_proxy_bytes = sum(
        len(repr((key, tuple(frame.token() for frame in machine.representatives[key]))).encode("utf-8")) + 1
        for key in machine.ordered_keys
    )
    qparts = congruence.class_count
    owed_classes = len(machine.all_keys) - qparts
    table_cells = qparts * len(INPUTS) + owed_classes
    rank_bits = max(1, math.ceil(math.log2(len(machine.all_keys))))
    candidate_measurements = {
        "logical_information": {
            "full_boundary_class_count": len(machine.all_keys),
            "ordinal_rank_bits": rank_bits,
            "ordinal_packed_rank_bytes": math.ceil(rank_bits / 8),
            "digest_current_utf8_hex_characters_and_bytes": 64,
            "digest_theoretical_binary_packing_bytes": 32,
        },
        "representative_serialized_bytes_excluding_digest": {
            "corpus_classes": _distribution(corpus_rep_bytes),
            "full_class_universe": _distribution(full_rep_bytes),
            "corpus_class_payload_total_bytes": sum(corpus_rep_bytes),
            "full_class_payload_total_bytes": sum(full_rep_bytes),
        },
        "generated_mapping_storage_proxies": {
            "ordered_keys_repr_utf8_bytes_plus_newlines": ordered_keys_text_proxy_bytes,
            "rank_map_repr_utf8_bytes_plus_newlines": rank_map_text_proxy_bytes,
            "representative_map_repr_utf8_bytes_plus_newlines": representative_map_text_proxy_bytes,
            "label": "deterministic textual proxies, not allocator/disk-format measurements",
        },
        "generated_table": {
            "explicit_transition_output_cells": table_cells,
            "approximate_textual_bytes": machine.approximate_table_bytes(),
            "note": "textual proxy only; Python objects, allocator, indexes, interpreter, and storage framing are additional",
        },
        "artifact_inventory": _artifact_inventory(),
        "inventory_completeness": (
            "INCOMPLETE total-system storage: excludes CPython/stdlib/OS, filesystem metadata, "
            "boundary capture/durability machinery, packaging, logs, and physical redundancy"
        ),
        "tcb_and_dependencies": [
            "boundary capture and durable cut mechanism (not implemented here)",
            "CPython interpreter and Python standard library",
            "CONTRACT-B1 framing, admission selector, and admission observation choices",
            "raw-trace parser/replay oracle",
            "finite-state enumerator and partition refinement",
            "canonical representative search and rank/table generator",
            "candidate decoder and conformance tests",
            "filesystem/medium retaining encoding and exact specification bundle",
            "same-runtime artifact selection/mismatch guard",
            "SHA-256 collision resistance for mismatch detection (assumption, not proved)",
        ],
        "human_and_physical": {
            "cognition_and_human_error": "UNKNOWN: no declared user protocol or study",
            "cross_physical_media_realization": "UNKNOWN: only software differential tests ran",
        },
        "benchmarks": _benchmarks(machine, unique_snapshots, include_timing=include_timing),
    }
    ordinal = OrdinalCandidate(machine)
    representative = RepresentativeCandidate(machine)
    evolution_probes = {}
    e03_left = (
        inbound("P", "a", "0"),
        inbound("P", "b", "1"),
    )
    e03_right = (inbound("P", "b", "1"),)
    for name, encoder in (
        ("ordinal", lambda item: ordinal.persist(replay(item))),
        ("canonical_representative", lambda item: representative.persist(replay(item))),
    ):
        compatible = factor_probe(corpus.histories, encoder, current_b1_observer)
        split = factor_probe(corpus.histories, encoder, authored_crossing_count_observer)
        evolution_probes[name] = {
            "corpus_current_b1_observer_factors": compatible.factors_through_old_encoding,
            "split_authored_count_observer_factors": split.factors_through_old_encoding,
            "split_witness": (
                None
                if split.witness is None
                else {
                    "left": tuple(frame.token() for frame in split.witness[0]),
                    "right": tuple(frame.token() for frame in split.witness[1]),
                    "left_value": split.witness[2],
                    "right_value": split.witness[3],
                }
            ),
            "explicit_e03_split_witness": {
                "left": tuple(frame.token() for frame in e03_left),
                "right": tuple(frame.token() for frame in e03_right),
                "same_old_encoding": encoder(e03_left) == encoder(e03_right),
                "left_authored_count": authored_crossing_count_observer(e03_left),
                "right_authored_count": authored_crossing_count_observer(e03_right),
            },
        }

    full_mask = (1 << len(COMPONENT_NAMES)) - 1
    direct = {}
    for index, name in enumerate(COMPONENT_NAMES):
        mask = full_mask & ~(1 << index)
        direct[name] = {
            "verdict": "sound" if mask in deletions.sound_masks else "collision",
            "witness": witness_json(witnesses[name]),
        }

    return {
        "contract": "FROZEN-B0 + executable contract B1",
        "evidence_protocol": "B2",
        "specification_and_generated_artifact_sha256": machine.specification_digest,
        "digest_verdict": (
            "same-runtime artifact-mismatch guard only, not a general portability mechanism and "
            "not MUST SURVIVE within singleton fixed B1; deletion externalizes artifact selection. "
            "SHA-256 collision behavior is UNKNOWN"
        ),
        "bounds": {
            "max_history_inbound_frames": max_inbound,
            "max_future_inbound_attempts": max_future_inputs,
            "normalized_future_contexts": len(contexts),
            "boundary_prefix_cuts": len(corpus.histories),
        },
        "enumeration": {
            "legal_boundary_prefix_histories": len(corpus.histories),
            "unique_raw_oracle_snapshots": candidate_checks["unique_cut_snapshots"],
            "bounded_residual_classes_in_corpus": len(bounded_ids),
            "stable_classes_in_corpus": len(stable_keys),
            "finite_domain_quiescent_states": len(congruence.states),
            "finite_domain_right_congruence_classes": congruence.class_count,
            "right_congruence_refinement_rounds": congruence.refinement_rounds,
            "candidate_boundary_classes": len(machine.all_keys),
        },
        "candidate_checks": {
            **candidate_checks,
            **full_universe_checks,
            **rebuild_checks,
            "actual_process_restart_restore_checks": 0,
        },
        "may_rebuild_recipe_checks": may_rebuild_checks,
        "merge_search": {
            "corpus_class_pair_branches_enumerated": pair_witnesses.pair_count,
            "executed_and_hashed_minimized_witnesses": pair_witnesses.pair_count,
            "witness_certificate_sha256": pair_witnesses.sha256,
            "winning_context_uint16_map_sha256": pair_witnesses.winning_context_map_sha256,
            "winning_context_uint16_map_raw_bytes": pair_witnesses.winning_context_map_raw_bytes,
            "earliest_depth_counts": pair_witnesses.depth_counts,
            "active_vertices_by_earliest_depth": pair_witnesses.active_vertices_by_depth,
            "winning_context_count": pair_witnesses.winning_contexts,
            "pair_context_comparisons": pair_witnesses.pair_context_comparisons,
            "history_candidates_per_class": pair_witnesses.history_candidates_per_class,
            "history_selection": pair_witnesses.history_selection,
            "context_tie_break": pair_witnesses.tie_break,
            "basis": (
                "each pair has a selected bounded context with unequal exact observations; "
                "all shallower contexts and all same-depth tie-break candidates were checked; "
                "canonical length-prefixed records hash pair/class/history/context/observations"
            ),
        },
        "component_deletion_search": {
            "declared_components": COMPONENT_NAMES,
            "unique_component_rows": deletions.rows,
            "masks_exhausted": 1 << len(COMPONENT_NAMES),
            "sound_masks": len(deletions.sound_masks),
            "inclusion_minimal_sound_kept_sets": [
                mask_names(mask) for mask in deletions.inclusion_minimal_masks
            ],
            "direct_deletions": direct,
        },
        "deduplicated_witness_core": {
            "minimality_claim": (
                "fixed-point 1-deletion-minimal relative to retaining the exact named G01-G09, "
                "E01-E09, ten output-kind cut endpoints, and at least one bounded collision for "
                "every unsound direct component deletion; not globally smallest"
            ),
            "history_count": len(witness_core.histories),
            "context_count": len(witness_core.contexts),
            "histories": [
                tuple(frame.token() for frame in history)
                for history in witness_core.histories
            ],
            "contexts": [context.token() for context in witness_core.contexts],
            "named_cases": witness_core.named_case_ids,
            "direct_collision_components": witness_core.direct_collision_components,
            "delta_certificate": witness_core.deletion_certificate,
        },
        "unknown_cells_used_for_equivalence": 0,
        "candidate_measurements": candidate_measurements,
        "evolution_probe": {
            "criterion": "new observer must be a total function of every old encoding cell",
            "positive_scope": (
                "only current_b1_observer over the enumerated 62,528-history corpus; "
                "no general positive evolution claim"
            ),
            "encodings": evolution_probes,
            "verdict": (
                "the one corpus observer factors through both old encodings; the explicit E03 "
                "same-encoding pair conclusively refutes deterministic migration for the split "
                "authored-count observer; general evolution unsupported"
            ),
        },
        **(
            {"experiment_wall_seconds": time.perf_counter() - started}
            if include_timing
            else {"experiment_timing": "excluded from deterministic evidence"}
        ),
        "common_mode_risk": {
            "mitigations_run": [
                "raw oracle imports no quotient or candidate module",
                "literal black-box G01-G09 and E01-E09 goldens",
                "ten-output-kind logical-cut encode/recover matrix",
                "right-congruence invariant and candidate/oracle differential checks",
                "deliberate generated-table mutation caught by the checker",
            ],
            "remaining": (
                "oracle, quotient, candidates, and tests still share Frame values, CPython, the B1 "
                "interpretation, and one host; correlated specification/runtime errors remain possible"
            ),
        },
        "unsupported": [
            "actual process restart/restore and cross-process decoder initialization",
            "fresh labels, payloads, keys, rules, or operations",
            "malformed byte framing beyond reporting UNKNOWN",
            "concurrency, input reordering, and non-serial delivery",
            "time, expiry, billing, audit, authorization, and confidentiality",
            "physical effects beyond crossing DO",
            "capture failures and physical output-delivery ambiguity",
            "resource deadlines and unbounded-domain storage growth",
            "contract evolution that splits a prior quotient class",
            "cryptographic proof of SHA-256 collision resistance",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sample-context-check",
        action="store_true",
        help="sample decoded contexts; all enumeration and quotient work remains exact",
    )
    parser.add_argument(
        "--deterministic",
        action="store_true",
        help="exclude variable wall-clock measurements for a stable evidence artifact",
    )
    args = parser.parse_args()
    result = run(
        full_context_check=not args.sample_context_check,
        include_timing=not args.deterministic,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
