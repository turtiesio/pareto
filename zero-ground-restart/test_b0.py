"""Golden and exhaustive-within-scope tests for the C0/B1 falsification harness."""

from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from c0_candidates import (
    BoundaryResult,
    OrdinalCandidate,
    OrdinalEncoding,
    QuotientBoundaryMachine,
    RepresentativeCandidate,
    RepresentativeEncoding,
    decode_history,
    encode_history,
)
from c0_experiment import (
    COMPONENT_NAMES,
    DISABLED,
    ENABLED,
    RESUME,
    BoundedResiduals,
    Context,
    StableRightCongruence,
    UnknownCell,
    direct_deletion_witnesses,
    evaluate_context,
    exhaustive_component_deletions,
    future_contexts,
    generate_histories,
    mask_names,
    minimized_pair_witness_certificate,
    pair_merge_certificate,
)
from c0_evolution import (
    authored_crossing_count_observer,
    current_b1_observer,
    factor_probe,
)
from c0_oracle import (
    ACTION,
    CLIENT,
    INITIAL,
    INPUTS,
    Frame,
    accept,
    append_legal,
    drain_history,
    inbound,
    replay,
    resume,
)
from run_b0 import (
    candidate_observation,
    verify_boundary_step,
    verify_candidates,
    verify_deterministic_rebuild,
    verify_full_universe_encodings,
    verify_may_rebuild_recipes,
)


def history(*commands: Frame, drain: bool = True) -> tuple[Frame, ...]:
    result: tuple[Frame, ...] = ()
    for command in commands:
        result = append_legal(result, command)
        if drain and replay(result).owed is not None:
            result = drain_history(result)
    return result


class OracleGoldenTests(unittest.TestCase):
    def test_exact_descriptor_and_action_port(self) -> None:
        prefix = history(inbound("R", "u", "0", "0"), inbound("P", "a", "1"))
        cut = append_legal(prefix, inbound("A", "k"))
        owed = replay(cut).owed
        self.assertIsNotNone(owed)
        self.assertEqual(owed.port, ACTION)
        self.assertEqual(owed.token(), "out:action:DO(k,a,1,u,0)")

    def test_ack_is_silent_and_same_key_only_after_crossed_do(self) -> None:
        prefix = history(inbound("P", "a", "0"))
        cut = append_legal(prefix, inbound("A", "k"))
        self.assertFalse(accept(replay(cut), inbound("ACK", "k", port=ACTION)).legal)

        pending = drain_history(cut)
        wrong = accept(replay(pending), inbound("ACK", "l", port=ACTION))
        self.assertFalse(wrong.legal)
        correct = accept(replay(pending), inbound("ACK", "k", port=ACTION))
        self.assertTrue(correct.legal)
        self.assertIsNone(correct.snapshot.owed)
        self.assertEqual(correct.crossed, (inbound("ACK", "k", port=ACTION),))
        self.assertFalse(accept(correct.snapshot, inbound("ACK", "k", port=ACTION)).legal)

    def test_direct_attempt_at_owed_cut_is_disabled_until_resume(self) -> None:
        prefix = history(inbound("P", "a", "0"))
        cut = append_legal(prefix, inbound("Q"))
        snapshot = replay(cut)
        direct = Context((inbound("O"),))
        scheduled = Context((RESUME, inbound("O"), RESUME))
        direct_result = evaluate_context(snapshot, direct)
        self.assertEqual(direct_result.admission, (DISABLED,))
        self.assertEqual(direct_result.client, ())
        scheduled_result = evaluate_context(snapshot, scheduled)
        self.assertEqual(scheduled_result.admission, (ENABLED,))
        self.assertEqual(
            scheduled_result.client,
            ("out:client:VAL(0)", "out:client:RAW(a,0)"),
        )

    def test_union_admission_distinguishes_wrong_key(self) -> None:
        pending_k = replay(history(inbound("P", "a", "0"), inbound("A", "k")))
        pending_l = replay(history(inbound("P", "a", "0"), inbound("A", "l")))
        context = Context((inbound("ACK", "k", port=ACTION),))
        self.assertEqual(evaluate_context(pending_k, context).admission, (ENABLED,))
        self.assertEqual(evaluate_context(pending_l, context).admission, (DISABLED,))

    def test_admission_is_observed_before_boundary_crossing(self) -> None:
        disabled = accept(INITIAL, inbound("ACK", "k", port=ACTION))
        self.assertFalse(disabled.legal)
        self.assertEqual(disabled.crossed, ())
        self.assertEqual(disabled.snapshot, INITIAL)
        enabled_frame = inbound("P", "a", "0")
        enabled = accept(INITIAL, enabled_frame)
        self.assertTrue(enabled.legal)
        self.assertEqual(enabled.crossed, (enabled_frame,))

    def test_latent_rule_bit_requires_two_inputs_and_resume(self) -> None:
        left = replay(history(inbound("P", "a", "0"), inbound("R", "u", "0", "1")))
        right = replay(history(inbound("P", "a", "0"), inbound("R", "u", "0", "0")))
        context = Context((inbound("P", "a", "1"), inbound("Q"), RESUME))
        self.assertEqual(evaluate_context(left, Context((inbound("Q"), RESUME))),
                         evaluate_context(right, Context((inbound("Q"), RESUME))))
        self.assertNotEqual(evaluate_context(left, context), evaluate_context(right, context))

    def test_may_forget_examples_have_identical_raw_snapshots(self) -> None:
        overwritten = replay(history(inbound("P", "a", "0"), inbound("P", "b", "1")))
        direct = replay(history(inbound("P", "b", "1")))
        self.assertEqual(overwritten, direct)

        before_query = history(inbound("P", "a", "0"))
        after_query = history(inbound("P", "a", "0"), inbound("Q"))
        self.assertEqual(replay(before_query), replay(after_query))

        once = history(inbound("P", "a", "0"), inbound("A", "k"))
        twice = history(inbound("P", "a", "0"), inbound("A", "k"), inbound("A", "k"))
        self.assertEqual(replay(once), replay(twice))

    def test_owed_and_crossed_are_distinct(self) -> None:
        prefix = history(inbound("P", "a", "0"))
        owed = replay(append_legal(prefix, inbound("Q")))
        crossed = resume(owed).snapshot
        context = Context((RESUME,))
        self.assertNotEqual(evaluate_context(owed, context), evaluate_context(crossed, context))


class FreshGoldenTests(unittest.TestCase):
    """Literal G01--G09 and E01--E09 from FRESH-ATTACKS-B0.md."""

    @staticmethod
    def observe(raw_history: tuple[Frame, ...], *operations: Frame | str):
        return evaluate_context(replay(raw_history), Context(tuple(operations)))

    def test_g01_owed_once_vs_crossed(self) -> None:
        owed = append_legal((), inbound("O"))
        crossed = drain_history(owed)
        self.assertEqual(self.observe(owed, RESUME).client, ("out:client:EMPTY",))
        self.assertEqual(self.observe(crossed, RESUME).client, ())

    def test_g02_latent_rule_behavior(self) -> None:
        left = history(inbound("R", "u", "0", "1"))
        right = history(inbound("R", "u", "0", "0"))
        operations = (inbound("P", "a", "1"), inbound("Q"), RESUME)
        self.assertEqual(self.observe(left, *operations).client, ("out:client:VAL(1)",))
        self.assertEqual(self.observe(right, *operations).client, ("out:client:VAL(0)",))

    def test_g03_explanatory_rule_identity(self) -> None:
        left = history(inbound("R", "u", "0", "1"))
        right = history(inbound("R", "v", "0", "1"))
        operations = (inbound("P", "a", "0"), inbound("X"), RESUME)
        self.assertEqual(
            self.observe(left, *operations).client,
            ("out:client:WHY(a,0,u,0)",),
        )
        self.assertEqual(
            self.observe(right, *operations).client,
            ("out:client:WHY(a,0,v,0)",),
        )

    def test_g04_frozen_descriptor(self) -> None:
        left = history(
            inbound("P", "a", "0"), inbound("A", "k"), inbound("P", "a", "1")
        )
        right = history(inbound("P", "a", "1"), inbound("A", "k"))
        operations = (inbound("S", "k"), RESUME)
        self.assertIn("PENDING(k,a,0,d,0)", self.observe(left, *operations).client[0])
        self.assertIn("PENDING(k,a,1,d,1)", self.observe(right, *operations).client[0])

    def test_g05_retry_uses_original_descriptor(self) -> None:
        pending = history(
            inbound("P", "a", "0"), inbound("A", "k"), inbound("P", "a", "1")
        )
        result = self.observe(pending, inbound("A", "k"), RESUME)
        self.assertEqual(result.action, ("out:action:DO(k,a,0,d,0)",))

    def test_g06_pending_done(self) -> None:
        pending = history(inbound("P", "a", "0"), inbound("A", "k"))
        done = history(
            inbound("P", "a", "0"),
            inbound("A", "k"),
            inbound("ACK", "k", port=ACTION),
        )
        operations = (inbound("S", "k"), RESUME)
        self.assertIn("PENDING", self.observe(pending, *operations).client[0])
        self.assertIn("DONE", self.observe(done, *operations).client[0])

    def test_g07_action_key_association(self) -> None:
        pending_k = history(inbound("P", "a", "0"), inbound("A", "k"))
        pending_l = history(inbound("P", "a", "0"), inbound("A", "l"))
        operations = (inbound("S", "k"), RESUME)
        self.assertIn("PENDING", self.observe(pending_k, *operations).client[0])
        self.assertEqual(self.observe(pending_l, *operations).client, ("out:client:ABSENT(k)",))

    def test_g08_no_data_vs_absent(self) -> None:
        no_data = append_legal((), inbound("A", "k"))
        absent = append_legal((), inbound("S", "k"))
        self.assertEqual(self.observe(no_data, RESUME).client, ("out:client:NO_DATA(k)",))
        self.assertEqual(self.observe(absent, RESUME).client, ("out:client:ABSENT(k)",))

    def test_g09_exact_why_after_restart(self) -> None:
        cut = append_legal(history(inbound("P", "a", "1")), inbound("X"))
        self.assertEqual(
            self.observe(cut, RESUME).client,
            ("out:client:WHY(a,1,d,1)",),
        )

    def test_e01_empty_o_q_x_cuts_are_equivalent(self) -> None:
        snapshots = [replay(append_legal((), inbound(kind))) for kind in ("O", "Q", "X")]
        self.assertEqual(snapshots[0], snapshots[1])
        self.assertEqual(snapshots[1], snapshots[2])

    def test_e02_completed_observations_are_forgotten(self) -> None:
        base = replay(history(inbound("P", "a", "0")))
        for commands in (
            (inbound("P", "a", "0"), inbound("O")),
            (inbound("P", "a", "0"), inbound("Q")),
            (inbound("P", "a", "0"), inbound("O"), inbound("Q")),
        ):
            self.assertEqual(replay(history(*commands)), base)

    def test_e03_overwritten_content(self) -> None:
        self.assertEqual(
            replay(history(inbound("P", "a", "0"), inbound("P", "b", "1"))),
            replay(history(inbound("P", "b", "1"))),
        )

    def test_e04_overwritten_rule(self) -> None:
        self.assertEqual(
            replay(history(inbound("R", "u", "0", "0"), inbound("R", "v", "0", "1"))),
            replay(history(inbound("R", "v", "0", "1"))),
        )

    def test_e05_independent_p_r_order(self) -> None:
        self.assertEqual(
            replay(history(inbound("P", "a", "0"), inbound("R", "v", "0", "1"))),
            replay(history(inbound("R", "v", "0", "1"), inbound("P", "a", "0"))),
        )

    def test_e06_completed_no_data_action(self) -> None:
        self.assertEqual(replay(()), replay(history(inbound("A", "k"))))

    def test_e07_no_data_before_real_action(self) -> None:
        left = history(inbound("A", "k"), inbound("P", "a", "0"), inbound("A", "k"))
        right = history(inbound("P", "a", "0"), inbound("A", "k"))
        self.assertEqual(replay(left), replay(right))

    def test_e08_retry_count_forgotten(self) -> None:
        once = history(inbound("P", "a", "0"), inbound("A", "k"))
        twice = history(inbound("P", "a", "0"), inbound("A", "k"), inbound("A", "k"))
        self.assertEqual(replay(once), replay(twice))

    def test_e09_completed_status_forgotten(self) -> None:
        pending = history(inbound("P", "a", "0"), inbound("A", "k"))
        with_status = history(
            inbound("P", "a", "0"), inbound("A", "k"), inbound("S", "k")
        )
        self.assertEqual(replay(pending), replay(with_status))


class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = generate_histories(4)
        cls.contexts = future_contexts(2)
        cls.residuals = BoundedResiduals(cls.contexts)
        cls.congruence = StableRightCongruence()
        cls.machine = QuotientBoundaryMachine(cls.congruence)

    def test_golden_enumeration_counts(self) -> None:
        snapshots = {replay(item) for item in self.corpus.histories}
        bounded = {self.residuals.class_id(snapshot) for snapshot in snapshots}
        stable = {self.congruence.class_key(snapshot) for snapshot in snapshots}
        self.assertEqual(len(INPUTS), 16)
        self.assertEqual(len(self.contexts), 2114)
        self.assertEqual(len(self.corpus.histories), 62528)
        self.assertEqual(len(snapshots), 1192)
        self.assertEqual(len(bounded), 1192)
        self.assertEqual(len(stable), 1192)
        self.assertEqual(len(self.congruence.states), 10420)
        self.assertEqual(self.congruence.class_count, 10420)
        self.assertEqual(self.congruence.refinement_rounds, 2)
        self.assertEqual(len(self.machine.all_keys), 82584)

    def test_residual_budgets_are_derived_from_supplied_contexts(self) -> None:
        zero = BoundedResiduals(future_contexts(0))
        one = BoundedResiduals(future_contexts(1))
        self.assertEqual(
            (zero.max_inbound_attempts, zero.max_resume_steps, zero.max_total_steps),
            (0, 1, 1),
        )
        self.assertEqual(
            (one.max_inbound_attempts, one.max_resume_steps, one.max_total_steps),
            (1, 2, 3),
        )
        left = replay(history(inbound("R", "u", "0", "1")))
        right = replay(history(inbound("R", "u", "0", "0")))
        self.assertEqual(one.class_id(left), one.class_id(right))
        self.assertNotEqual(self.residuals.class_id(left), self.residuals.class_id(right))

    def test_stable_partition_is_a_right_congruence(self) -> None:
        fingerprints: dict[int, tuple[object, ...]] = {}
        for index, part in enumerate(self.congruence.partitions):
            value = tuple(
                (edge.observation, self.congruence.partitions[edge.target])
                for edge in self.congruence.edges[index]
            )
            self.assertEqual(fingerprints.setdefault(part, value), value)

    def test_candidates_round_trip_every_generated_cut(self) -> None:
        checks = verify_candidates(
            self.corpus.histories,
            self.contexts,
            self.machine,
            check_all_contexts=False,
        )
        self.assertEqual(checks["in_process_encode_recover_round_trips"], 125056)
        self.assertEqual(checks["ordinal_encoding_collisions"], 0)
        self.assertEqual(checks["representative_encoding_collisions"], 0)
        self.assertGreater(checks["decoded_context_checks"], 0)

    def test_ten_kind_cut_encode_recover_matrix(self) -> None:
        pending = history(inbound("P", "a", "0"), inbound("A", "k"))
        done = history(
            inbound("P", "a", "0"),
            inbound("A", "k"),
            inbound("ACK", "k", port=ACTION),
        )
        scenarios = (
            ("EMPTY", (), inbound("O"), True),
            ("RAW", history(inbound("P", "a", "0")), inbound("O"), True),
            ("VAL", history(inbound("P", "a", "0")), inbound("Q"), True),
            ("WHY", history(inbound("P", "a", "1")), inbound("X"), True),
            ("NO_DATA", (), inbound("A", "k"), True),
            ("DO", history(inbound("P", "a", "0")), inbound("A", "k"), False),
            ("ALREADY", done, inbound("A", "k"), True),
            ("ABSENT", (), inbound("S", "k"), True),
            ("PENDING", pending, inbound("S", "k"), True),
            ("DONE", done, inbound("S", "k"), True),
        )
        ordinal = OrdinalCandidate(self.machine)
        representative = RepresentativeCandidate(self.machine)
        seen: set[str] = set()
        for kind, base, request, read_only in scenarios:
            before = replay(base)
            cut_history = append_legal(base, request)
            cut = replay(cut_history)
            self.assertIsNotNone(cut.owed)
            self.assertEqual(cut.owed.kind, kind)
            seen.add(kind)

            # Repeated in-process decode leaves both encodings at the same cut.
            expected_key = self.machine.class_key(cut)
            ordinal_encoding = ordinal.persist(cut)
            representative_encoding = representative.persist(cut)
            for _decode in range(3):
                self.assertEqual(ordinal.recover(ordinal_encoding), expected_key)
                self.assertEqual(representative.recover(representative_encoding), expected_key)

            # A fresh inbound is disabled until the owed output crosses.
            probe = inbound("P", "b", "1")
            self.assertFalse(accept(cut, probe).legal)
            self.assertEqual(self.machine.input_step(expected_key, probe).admission, DISABLED)

            # It crosses once; subsequent resumes do not duplicate it.
            first = resume(cut)
            self.assertEqual(len(first.crossed), 1)
            self.assertEqual(first.crossed[0].kind, kind)
            self.assertEqual(resume(first.snapshot).crossed, ())
            candidate_first = self.machine.resume_step(expected_key)
            candidate_second = self.machine.resume_step(candidate_first.next_key)
            self.assertEqual(len(candidate_first.client) + len(candidate_first.action), 1)
            self.assertEqual(candidate_second.client + candidate_second.action, ())
            if read_only:
                self.assertEqual(first.snapshot, before)
        self.assertEqual(
            seen,
            {"EMPTY", "RAW", "VAL", "WHY", "NO_DATA", "DO", "ALREADY", "ABSENT", "PENDING", "DONE"},
        )

    def test_all_canonical_representatives_are_unique_and_rank_ordered(self) -> None:
        representatives = self.machine.representatives
        self.assertEqual(len(representatives), len(set(representatives.values())))
        expected = tuple(
            sorted(representatives, key=lambda key: (len(representatives[key]), tuple(f.token() for f in representatives[key])))
        )
        self.assertEqual(self.machine.ordered_keys, expected)

    def test_both_encoders_round_trip_the_full_generated_class_universe(self) -> None:
        checks = verify_full_universe_encodings(self.machine)
        self.assertEqual(checks["full_universe_classes"], 82584)
        self.assertEqual(checks["ordinal_full_universe_in_process_encode_recover"], 82584)
        self.assertEqual(
            checks["representative_full_universe_in_process_encode_recover"], 82584
        )
        self.assertEqual(checks["ordinal_full_universe_distinct_encodings"], 82584)
        self.assertEqual(checks["representative_full_universe_distinct_encodings"], 82584)
        self.assertEqual(
            checks["full_universe_resume_and_16_input_differential_checks"],
            82584 * 17,
        )

    def test_clean_rebuild_regenerates_identical_bound_artifacts(self) -> None:
        checks = verify_deterministic_rebuild(self.machine)
        self.assertEqual(checks["clean_rebuilds"], 1)
        self.assertTrue(checks["artifact_digest_equal_after_clean_rebuild"])
        self.assertTrue(checks["rank_order_equal_after_clean_rebuild"])
        self.assertTrue(checks["canonical_representatives_equal_after_clean_rebuild"])

    def test_may_rebuild_recipes_cover_full_boundary_universe(self) -> None:
        checks = verify_may_rebuild_recipes(self.machine)
        self.assertEqual(checks["rule_on_0"]["full_universe_checks"], 82584)
        self.assertEqual(checks["owed_port"]["full_universe_checks"], 82584)
        self.assertEqual(
            set(checks["owed_port"]["observed_owed_kinds_including_quiescent_sentinel"]),
            {"-", "ABSENT", "ALREADY", "DO", "DONE", "EMPTY", "NO_DATA", "PENDING", "RAW", "VAL", "WHY"},
        )

    def test_noncanonical_or_wrong_spec_encodings_are_rejected(self) -> None:
        ordinal = OrdinalCandidate(self.machine)
        representative = RepresentativeCandidate(self.machine)
        with self.assertRaisesRegex(ValueError, "digest"):
            ordinal.recover(OrdinalEncoding("0" * 64, 0))
        with self.assertRaisesRegex(ValueError, "digest"):
            representative.recover(RepresentativeEncoding("0" * 64, b""))

        repeated = history(inbound("P", "a", "0"), inbound("P", "a", "0"))
        encoding = RepresentativeEncoding(self.machine.specification_digest, encode_history(repeated))
        with self.assertRaisesRegex(ValueError, "noncanonical"):
            representative.recover(encoding)

    def test_exhaustive_component_projection_search(self) -> None:
        search = exhaustive_component_deletions(
            self.corpus.histories, self.congruence.class_key
        )
        self.assertEqual(search.rows, 1192)
        self.assertEqual(len(search.sound_masks), 4)
        self.assertEqual(len(search.inclusion_minimal_masks), 1)
        self.assertEqual(
            mask_names(search.inclusion_minimal_masks[0]),
            (
                "current_source",
                "current_bit",
                "rule_label",
                "rule_on_1",
                "action_k",
                "action_l",
                "owed_kind",
                "owed_arguments",
            ),
        )

    def test_direct_deletion_witnesses_are_globally_minimized(self) -> None:
        search = exhaustive_component_deletions(
            self.corpus.histories, self.congruence.class_key
        )
        witnesses = direct_deletion_witnesses(
            self.corpus.histories, search, self.residuals
        )
        expected_total_crossings = {
            "current_source": 2,
            "current_bit": 2,
            "rule_label": 1,
            "rule_on_0": None,
            "rule_on_1": 2,
            "action_k": 4,
            "action_l": 4,
            "owed_port": None,
            "owed_kind": 2,
            "owed_arguments": 2,
        }
        for name, total in expected_total_crossings.items():
            value = witnesses[name]
            if total is None:
                self.assertIsInstance(value, str)
            else:
                self.assertNotIsInstance(value, str)
                self.assertEqual(value.score[0], total)  # type: ignore[union-attr]

    def test_pair_merge_branch_certificate_is_exhaustive(self) -> None:
        keys = {self.congruence.class_key(replay(item)) for item in self.corpus.histories}
        count, digest = pair_merge_certificate(keys)
        self.assertEqual(count, 1192 * 1191 // 2)
        self.assertEqual(len(digest), 64)
        self.assertEqual((count, digest), pair_merge_certificate(reversed(sorted(keys))))

    def test_all_pair_minimized_witness_certificate(self) -> None:
        certificate = minimized_pair_witness_certificate(
            self.corpus.histories,
            self.congruence.class_key,
            self.contexts,
        )
        simple_count, _simple_digest = pair_merge_certificate(
            self.congruence.class_key(replay(item)) for item in self.corpus.histories
        )
        self.assertEqual(certificate.pair_count, simple_count)
        self.assertEqual(certificate.pair_count, 709836)
        self.assertEqual(certificate.depth_counts, {0: 596382, 1: 113306, 2: 148})
        self.assertEqual(certificate.active_vertices_by_depth, {0: 1192, 1: 1160, 2: 248})
        self.assertEqual(certificate.winning_contexts, 25)
        self.assertEqual(certificate.pair_context_comparisons, 8983832)
        self.assertEqual(certificate.winning_context_map_raw_bytes, 1419672)
        self.assertEqual(
            certificate.sha256,
            "643a4cc860a4de957d47be9aa144df1d8da482509157bc00fe60cf6597ba770d",
        )
        self.assertEqual(
            certificate.winning_context_map_sha256,
            "4e4a93c868c7ccdd59f30acf921ac009605b3c4e234477f686d33cc17db5e3d4",
        )
        self.assertIn("not temporal", certificate.tie_break)

    def test_evolution_factor_through_and_split_criterion_for_both_encodings(self) -> None:
        ordinal = OrdinalCandidate(self.machine)
        representative = RepresentativeCandidate(self.machine)
        encoders = (
            lambda item: ordinal.persist(replay(item)),
            lambda item: representative.persist(replay(item)),
        )
        for encode in encoders:
            compatible = factor_probe(
                self.corpus.histories, encode, current_b1_observer
            )
            self.assertTrue(compatible.factors_through_old_encoding)
            self.assertIsNone(compatible.witness)

            split = factor_probe(
                self.corpus.histories, encode, authored_crossing_count_observer
            )
            self.assertFalse(split.factors_through_old_encoding)
            self.assertIsNotNone(split.witness)

        e03_left = history(inbound("P", "a", "0"), inbound("P", "b", "1"))
        e03_right = history(inbound("P", "b", "1"))
        self.assertEqual(ordinal.persist(replay(e03_left)), ordinal.persist(replay(e03_right)))
        self.assertEqual(
            representative.persist(replay(e03_left)), representative.persist(replay(e03_right))
        )
        self.assertNotEqual(
            authored_crossing_count_observer(e03_left),
            authored_crossing_count_observer(e03_right),
        )

    def test_unknown_is_never_used_as_equivalence(self) -> None:
        self.assertNotEqual(UnknownCell("left"), UnknownCell("right"))
        unknown = Frame("in", CLIENT, "FRESH", ())
        with self.assertRaisesRegex(KeyError, "UNKNOWN"):
            self.machine.input_step(self.machine.class_key(INITIAL), unknown)
        with self.assertRaisesRegex(ValueError, "UNKNOWN"):
            decode_history(b"not-a-frame")

    def test_deliberate_transition_table_mutation_is_detected(self) -> None:
        initial_key = self.machine.class_key(INITIAL)
        part = int(initial_key[1])
        q_index = INPUTS.index(inbound("Q"))
        table_key = (part, q_index)
        original = self.machine._q_edges[table_key]
        self.machine._q_edges[table_key] = BoundaryResult(ENABLED, (), (), initial_key)
        try:
            with self.assertRaisesRegex(AssertionError, "transition"):
                verify_boundary_step(self.machine, INITIAL, inbound("Q"))
        finally:
            self.machine._q_edges[table_key] = original

    def test_oracle_has_no_candidate_or_quotient_import(self) -> None:
        path = Path(__file__).resolve().parent / "c0_oracle.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertFalse(any(name.startswith("c0_candidates") for name in imported))
        self.assertFalse(any(name.startswith("c0_experiment") for name in imported))


if __name__ == "__main__":
    unittest.main(verbosity=2)
