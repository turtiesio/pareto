from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import unittest


BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

import r01b_descriptor_freeze as descriptors
import r01b_oracle_freeze as oracle


class R01BSemanticFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.descriptor_bytes = (BASE / "R01B-DESCRIPTORS.json").read_bytes()
        cls.oracle_bytes = (BASE / "R01B-LITERAL-ORACLE.json").read_bytes()
        cls.status_bytes = (BASE / "R01B-STATUS-REGISTRY.json").read_bytes()
        cls.descriptor_package = json.loads(cls.descriptor_bytes)
        cls.oracle_package = json.loads(cls.oracle_bytes)
        cls.status_package = json.loads(cls.status_bytes)

    def test_typed_value_fixed_vectors_and_independent_copy(self) -> None:
        vectors = (
            (False, "05"),
            (True, "06"),
            (0, "010000000000000000"),
            (-1, "02ffffffffffffffff"),
            (b"", "030000000000000000"),
            ("", "040000000000000000"),
            ([], "070000000000000000"),
            ({}, "080000000000000000"),
        )
        for value, expected in vectors:
            with self.subTest(value=value):
                self.assertEqual(descriptors.tv(value).hex(), expected)
                self.assertEqual(oracle.tv(value).hex(), expected)

    def test_exact_regeneration(self) -> None:
        regenerated_descriptors = descriptors.canonical_json(
            descriptors.build_package()
        )
        self.assertEqual(regenerated_descriptors, self.descriptor_bytes)
        regenerated_oracle = oracle.canonical_json(
            oracle.build_oracle(json.loads(regenerated_descriptors))
        )
        self.assertEqual(regenerated_oracle, self.oracle_bytes)

    def test_counts_and_identity_order(self) -> None:
        package = self.descriptor_package
        self.assertEqual(package["row_count"], 3028)
        self.assertEqual(
            package["counts_by_family"],
            {
                "CLEAN_MECHANISM": 456,
                "OCCUPIED_STAGING": 112,
                "RECORD_FAULT": 2344,
                "STAGE_CONTROL": 104,
                "WRAPPER_ERROR": 12,
            },
        )
        previous = ""
        for ordinal, row in enumerate(package["rows"]):
            expected_id = "r01b-case-" + hashlib.sha256(
                descriptors.CASE_TAG + descriptors.tv(row["identity"])
            ).hexdigest()
            self.assertEqual(row["case_id"], expected_id)
            self.assertEqual(row["case_ordinal"], ordinal)
            self.assertGreater(expected_id, previous)
            previous = expected_id

    def test_record_fault_domain(self) -> None:
        faults = Counter(
            row["identity"]["recovery_fixture_recipe"]["mutation"]
            for row in self.descriptor_package["rows"]
            if row["metadata"]["family"] == "RECORD_FAULT"
        )
        self.assertEqual(
            faults,
            {
                "FLIP": 2064,
                "TRUNCATE": 258,
                "MISSING": 4,
                "APPEND_ZERO": 4,
                "WRONG_SUITE": 4,
                "NONREGULAR": 4,
                "STALE_VALID": 2,
                "OTHER_VALID": 4,
            },
        )

    def test_case_identity_is_only_the_tagged_l_boundary_input(self) -> None:
        identities = [row["identity"] for row in self.descriptor_package["rows"]]
        self.assertEqual(
            len({descriptors.tv(identity) for identity in identities}),
            len(identities),
        )
        forbidden = {
            "backend_applicability",
            "case",
            "comparison_rules",
            "cut_reachability",
            "family",
            "manifest_applicability",
            "origin",
            "semantic_profile",
        }
        for identity in identities:
            self.assertFalse(forbidden & set(identity))
            if identity["history_production"] == "PUBLICATION":
                self.assertEqual(
                    set(identity),
                    {
                        "backend",
                        "continuation_hex",
                        "cut",
                        "history_production",
                        "injected_fault",
                        "mechanism_manifest",
                        "observer_profile",
                        "repetition",
                        "requested_payload_hex",
                        "setup",
                    },
                )
            else:
                self.assertEqual(
                    set(identity),
                    {
                        "backend",
                        "continuation_hex",
                        "history_production",
                        "mechanism_manifest",
                        "observer_profile",
                        "recovery_fixture_recipe",
                        "repetition",
                    },
                )
    def test_all_declared_comparison_rules_resolve(self) -> None:
        bodies = [descriptors.row_view(row) for row in self.descriptor_package["rows"]]

        def key(body: dict[str, object], ignored: set[str]) -> tuple[object, ...]:
            return tuple(
                (name, json.dumps(value, sort_keys=True))
                for name, value in sorted(body.items())
                if name not in ignored
            )

        backend_groups: dict[tuple[object, ...], list[dict[str, object]]] = {}
        for body in bodies:
            backend_groups.setdefault(key(body, {"backend"}), []).append(body)
        for body in bodies:
            if "CROSS_BACKEND_SAME_SYMBOLIC_ROW" in body["comparison_rules"]:
                peers = backend_groups[key(body, {"backend"})]
                self.assertEqual({peer["backend"] for peer in peers}, {"E", "T"})
                self.assertEqual(len(peers), 2)

            if "PAIR_REFERENCE_SAME_BACKEND" not in body["comparison_rules"]:
                continue
            target = dict(body)
            target["manifest"] = "REFERENCE"
            target["comparison_rules"] = []
            target.pop("cut_reachability")
            if target["family"] == "STAGE_CONTROL":
                target["family"] = "CLEAN_MECHANISM"
            matches = []
            for candidate in bodies:
                normalized = dict(candidate)
                normalized["comparison_rules"] = []
                normalized.pop("cut_reachability")
                if normalized == target:
                    matches.append(candidate)
            self.assertEqual(len(matches), 1, body)

    def test_literal_oracle_alignment_and_outcomes(self) -> None:
        oracle_package = self.oracle_package
        self.assertEqual(oracle_package["schema_id"], "R01B-LITERAL-ORACLE-2")
        self.assertEqual(
            oracle_package["status_registry_source"],
            {
                "schema_id": self.status_package["schema_id"],
                "sha256": hashlib.sha256(self.status_bytes).hexdigest(),
            },
        )
        self.assertEqual(oracle_package["row_count"], 3028)
        self.assertEqual(
            oracle_package["descriptor_stream_sha256"],
            hashlib.sha256(self.descriptor_bytes).hexdigest(),
        )
        self.assertEqual(
            [row["case_id"] for row in self.descriptor_package["rows"]],
            [row["case_id"] for row in oracle_package["rows"]],
        )
        self.assertTrue(
            all(set(row) == {"case_id", "expected"} for row in oracle_package["rows"])
        )
        self.assertNotIn(b"NO_CROSSING", self.oracle_bytes)
        self.assertNotIn(b"NO_OBSERVATION", self.oracle_bytes)
        coordinates = [
            row["expected"]["status_coordinates"]
            for row in oracle_package["rows"]
        ]
        self.assertEqual(
            Counter(item["execution"] for item in coordinates),
            {"COMPLETE": 3004, "CONTROL_UNAVAILABLE": 24},
        )
        self.assertEqual(
            Counter(item["full_conformance"] for item in coordinates),
            {"PASS": 2928, "UNKNOWN": 100},
        )
        self.assertEqual(
            Counter(item["behavioral_comparison"] for item in coordinates),
            {"MATCH": 2900, "DIFFER": 104, "UNKNOWN": 24},
        )
        observations = Counter()
        for row in oracle_package["rows"]:
            expectation = row["expected"]["b_expectation"]
            observations.update(
                [
                    expectation["recovery_observation_hex"]
                    if expectation["kind"] == "EXACT"
                    else "NO_B_HISTORY"
                ]
            )
        self.assertEqual(
            observations,
            {
                "01": 2334,
                "0200000000": 334,
                "00": 232,
                "020000000100": 104,
                "NO_B_HISTORY": 24,
            },
        )

    def test_exact_comparison_edges_and_aggregate(self) -> None:
        package = self.oracle_package
        edges = package["comparison_edges"]
        self.assertEqual(package["comparison_edge_count"], 2010)
        self.assertEqual(
            Counter(edge["expected_result"] for edge in edges),
            {"MATCH": 1946, "DIFFER": 52, "UNKNOWN": 12},
        )
        edge_by_id = {edge["edge_id"]: edge for edge in edges}
        self.assertEqual(len(edge_by_id), len(edges))
        self.assertEqual(list(edge_by_id), sorted(edge_by_id))
        incident_results: dict[str, list[str]] = {
            row["case_id"]: [] for row in package["rows"]
        }
        for edge in edges:
            identity = edge["identity"]
            expected_id = "r01b-edge-" + hashlib.sha256(
                oracle.EDGE_TAG + oracle.tv(identity)
            ).hexdigest()
            self.assertEqual(edge["edge_id"], expected_id)
            for endpoint in (identity["left_case_id"], identity["right_case_id"]):
                incident_results[endpoint].append(edge["expected_result"])
        for row in package["rows"]:
            case_id = row["case_id"]
            self.assertEqual(
                row["expected"]["comparison_edge_ids"],
                sorted(
                    edge["edge_id"]
                    for edge in edges
                    if case_id in (
                        edge["identity"]["left_case_id"],
                        edge["identity"]["right_case_id"],
                    )
                ),
            )
            results = incident_results[case_id]
            aggregate = (
                "DIFFER" if "DIFFER" in results else
                "UNKNOWN" if "UNKNOWN" in results else
                "MATCH" if results else
                "NOT_COMPARED"
            )
            self.assertEqual(
                row["expected"]["status_coordinates"]["behavioral_comparison"],
                aggregate,
            )

    def test_in_memory_constituent_checks_exactly_derive_full_conformance(self) -> None:
        generated = oracle.build_oracle(self.descriptor_package)
        edges_by_id = {
            edge["edge_id"]: edge for edge in generated["comparison_edges"]
        }
        base_checks = {
            "DESCRIPTOR_INPUT": (
                "SUBMITTED_DESCRIPTOR_TEMPLATE_BYTES_AND_FREEZE_OVERLAY_IDS",
                "descriptor_registry/case_id",
            ),
            "EXECUTION": (
                "ACTUAL_EXECUTION_COORDINATE",
                "status_coordinates/execution",
            ),
            "CUT_REACHABILITY": (
                "OBSERVED_CUT_REACHABILITY_AND_TERMINATION_POSITION",
                "cut_reachability",
            ),
            "CONTROL_PROTOCOL": (
                "OBSERVED_NEUTRAL_FRAME_SEQUENCE_FLAGS_TRIAL_DIGEST_AND_ACK_RELATION",
                "control_protocol_and_descriptor_manifest",
            ),
            "CHECKPOINT_STREAM": (
                "OBSERVED_ORDERED_CHECKPOINT_SLOT_STREAM",
                "expected_checkpoint_slots",
            ),
            "B_RESPONSE": (
                "ACTUAL_COMPLETE_B_HISTORY_OR_VERIFIED_NO_B_HISTORY",
                "b_expectation",
            ),
            "TERMINAL": (
                "OBSERVED_PUBLISHER_OR_RECOVERY_TERMINAL",
                "expected_terminal",
            ),
            "WAIT_ORDER": (
                "OBSERVED_EXACT_PUBLISHER_WAIT_REAP_ORDER",
                "expected_wait_order",
            ),
            "EVIDENCE_ENVELOPE": (
                "RETAINED_SINGLE_ENVELOPE_SCHEMA_HASH_BOUNDS_AND_REPLAY_INDEX",
                "evidence_envelope_schema",
            ),
            "EXPECTED_RISK_LABEL": (
                "RISK_LABEL_DERIVED_FROM_THE_ACTUAL_COMPLETE_HISTORY",
                "expected_risk_label",
            ),
        }
        operation_ids = {
            f"OPERATION_FACT/{operation}"
            for operation in self.status_package["operation_registry"]
        }
        unknown_kinds: Counter[str] = Counter()
        total_check_count = 0
        global_id_pairs: set[tuple[str, str]] = set()
        registry = generated["conformance_check_registry"]
        self.assertEqual(
            registry["base_checks"],
            {
                key: {"verification_target": target, "oracle_reference": reference}
                for key, (target, reference) in base_checks.items()
            },
        )
        self.assertEqual(set(registry["conditional_checks"]), {
            "PASSIVE_REAP_OBSERVER", "STAGE_CONTINUATION"
        })
        self.assertEqual(registry["expected_full_conformance_domain"], ["PASS", "UNKNOWN"])
        self.assertEqual(registry["sort_rule"], "unsigned UTF-8 check_key bytes")

        for descriptor_row, generated_row in zip(
            self.descriptor_package["rows"], generated["rows"]
        ):
            expected = generated_row["expected"]
            self.assertNotIn("conformance_checks", expected)
            keys = expected["conformance_check_keys"]
            total_check_count += len(keys)
            self.assertTrue(keys)
            self.assertEqual(keys, sorted(keys, key=lambda item: item.encode("utf-8")))
            self.assertEqual(len(keys), len(set(keys)))
            pairs = {(generated_row["case_id"], key) for key in keys}
            self.assertTrue(global_id_pairs.isdisjoint(pairs))
            global_id_pairs.update(pairs)
            self.assertTrue(set(base_checks) <= set(keys))

            self.assertEqual(
                {check_key for check_key in keys if check_key.startswith("OPERATION_FACT/")},
                operation_ids,
            )

            comparison_ids = {
                f"COMPARISON_EDGE/{edge_id}"
                for edge_id in expected["comparison_edge_ids"]
            }
            self.assertTrue(comparison_ids)
            self.assertEqual(
                {check_key for check_key in keys if check_key.startswith("COMPARISON_EDGE/")},
                comparison_ids,
            )

            identity = descriptor_row["identity"]
            control_unavailable = (
                identity["mechanism_manifest"] == "DROP_STAGE_CONTROLLER"
                and identity["cut"] != "NORMAL"
            )
            reaping_unknown = (
                identity["mechanism_manifest"]
                == "NO_PRE_RECOVERY_REAP_BEHAVIORAL"
            )
            conditional_ids = set()
            if control_unavailable:
                conditional_ids.add("STAGE_CONTINUATION")
            if reaping_unknown:
                conditional_ids.add("PASSIVE_REAP_OBSERVER")
            self.assertEqual(
                set(keys)
                - set(base_checks)
                - operation_ids
                - comparison_ids,
                conditional_ids,
            )

            expected_unknown_ids = {
                f"COMPARISON_EDGE/{edge_id}"
                for edge_id in expected["comparison_edge_ids"]
                if edges_by_id[edge_id]["expected_result"] == "UNKNOWN"
            } | conditional_ids
            edge_results = {
                edge_id: edges_by_id[edge_id]["expected_result"]
                for edge_id in expected["comparison_edge_ids"]
            }
            statuses = {
                key: oracle.expected_check_status(key, edge_results) for key in keys
            }
            self.assertEqual(
                {key for key, status in statuses.items() if status == "UNKNOWN"},
                expected_unknown_ids,
            )
            for key, status in statuses.items():
                self.assertIn(status, {"PASS", "UNKNOWN"})
                if status == "UNKNOWN":
                    if key.startswith("COMPARISON_EDGE/"):
                        unknown_kinds["COMPARISON_EDGE"] += 1
                    else:
                        unknown_kinds[key] += 1

            aggregate = oracle.aggregate_full_conformance(keys, edge_results)
            self.assertEqual(
                expected["status_coordinates"]["full_conformance"],
                aggregate,
            )

        self.assertEqual(total_check_count, 64680)
        self.assertEqual(generated["conformance_check_count"], total_check_count)
        self.assertEqual(len(global_id_pairs), total_check_count)
        self.assertEqual(
            unknown_kinds,
            {
                "COMPARISON_EDGE": 24,
                "PASSIVE_REAP_OBSERVER": 76,
                "STAGE_CONTINUATION": 24,
            },
        )

    def test_operation_facts_preserve_same_b_response_distinction(self) -> None:
        pairs: dict[str, dict[str, object]] = {}
        for descriptor_row, oracle_row in zip(
            self.descriptor_package["rows"], self.oracle_package["rows"]
        ):
            body = descriptors.row_view(descriptor_row)
            if (
                body["backend"] == "E"
                and body["family"] == "CLEAN_MECHANISM"
                and body["case"] == "CREATE"
                and body["cut"] == "J3"
                and body["repetition"] == 0
                and body["manifest"] in {"REFERENCE", "NO_FILE_FSYNC"}
            ):
                pairs[body["manifest"]] = oracle_row["expected"]
        self.assertEqual(set(pairs), {"REFERENCE", "NO_FILE_FSYNC"})
        reference = pairs["REFERENCE"]
        deletion = pairs["NO_FILE_FSYNC"]
        self.assertEqual(
            reference["b_expectation"],
            deletion["b_expectation"],
        )
        reference_facts = {
            item["operation"]: item for item in reference["operation_expectations"]
        }
        deletion_facts = {
            item["operation"]: item for item in deletion["operation_expectations"]
        }
        self.assertEqual(
            reference_facts["FILE_FSYNC"]["expectation"],
            "OBSERVED_SUCCESS",
        )
        self.assertEqual(
            deletion_facts["FILE_FSYNC"]["expectation"],
            "OBSERVED_ABSENT",
        )
        self.assertIn(
            "INDEPENDENT_TRACE",
            deletion_facts["FILE_FSYNC"]["required_sources"],
        )

    def test_operation_fact_domain_is_closed_and_total(self) -> None:
        registry = {
            item["label"] for item in self.status_package["operation_fact_registry"]
        }
        for row in self.oracle_package["rows"]:
            facts = row["expected"]["operation_expectations"]
            self.assertEqual(
                [fact["operation"] for fact in facts],
                self.status_package["operation_registry"],
            )
            self.assertTrue({fact["expectation"] for fact in facts} <= registry)
            self.assertTrue(all(fact["required_sources"] for fact in facts))
            self.assertTrue(
                {fact["configured_source"] for fact in facts}
                <= set(self.status_package["configured_source_registry"])
            )
            self.assertTrue(
                {
                    source
                    for fact in facts
                    for source in fact["required_sources"]
                }
                <= set(self.status_package["evidence_source_registry"])
            )
            self.assertTrue(
                {fact["errno"] for fact in facts}
                <= set(self.status_package["errno_coordinate_registry"])
            )


if __name__ == "__main__":
    unittest.main()
