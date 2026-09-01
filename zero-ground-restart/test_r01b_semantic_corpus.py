from __future__ import annotations

import json
from pathlib import Path
import unittest


BASE = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((BASE / name).read_bytes())


class R01BSemanticCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.descriptors = load("R01B-DESCRIPTORS.json")
        cls.oracle = load("R01B-LITERAL-ORACLE.json")
        cls.holdouts = load("R01B-HOLDOUTS.json")
        cls.status = load("R01B-STATUS-REGISTRY.json")

    def test_union_is_exact_and_globally_unique(self) -> None:
        subject_ids = [row["case_id"] for row in self.descriptors["rows"]]
        oracle_ids = [row["case_id"] for row in self.oracle["rows"]]
        lab_ids = [row["case_id"] for row in self.holdouts["rows"]]
        self.assertEqual(len(subject_ids), 3028)
        self.assertEqual(len(lab_ids), 3290)
        self.assertEqual(set(subject_ids), set(oracle_ids))
        self.assertEqual(len(set(subject_ids)), len(subject_ids))
        self.assertEqual(len(set(lab_ids)), len(lab_ids))
        self.assertTrue(set(subject_ids).isdisjoint(lab_ids))
        all_ids = subject_ids + lab_ids
        self.assertEqual(len(all_ids), 6318)
        self.assertTrue(all(case_id.startswith("r01b-case-") for case_id in all_ids))

    def test_lab_rows_have_no_subject_history_or_behavior_oracle(self) -> None:
        forbidden_keys = {
            "b_comparison_eligibility",
            "b_crossing_count",
            "b_expectation",
            "b_history",
            "b_input",
            "b_input_key",
            "b_response",
            "b_state",
            "b_state_verdict_eligibility",
            "comparison_edge_ids",
            "comparison_partner",
            "expected_b_response",
            "publish_result_hex_list",
            "recovery_observation_hex",
        }

        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key.lower()
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)

        for row in self.holdouts["rows"]:
            self.assertEqual(row["body"]["history_production"], "LAB_ONLY")
            self.assertEqual(
                row["expected"]["status_coordinates"]["behavioral_comparison"]["label"],
                "NOT_COMPARED",
            )
            self.assertTrue(forbidden_keys.isdisjoint(keys(row)))

    def test_every_status_coordinate_and_failure_code_comes_from_one_authority(self) -> None:
        authority_source = self.holdouts["status_registry_source"]
        self.assertEqual(authority_source["schema_id"], self.status["schema_id"])
        self.assertEqual(
            self.oracle["status_registry_source"]["sha256"],
            authority_source["sha256"],
        )
        tables = self.status["status_coordinate_registry"]
        failures = {
            (item["code"], item["label"])
            for item in self.status["failure_reason_registry"]
        }
        for row in self.holdouts["rows"]:
            for name, value in row["expected"]["status_coordinates"].items():
                values = value if isinstance(value, list) else [value]
                table = tables[name]
                allowed = {
                    (table["namespace"], item["code"], item["label"])
                    for item in table["codes"]
                }
                for item in values:
                    self.assertIn(
                        (item["namespace"], item["code"], item["label"]),
                        allowed,
                    )
            for item in row["expected"]["failure_reasons"]:
                self.assertIn((item["code"], item["label"]), failures)
            full = tables["full_conformance"]
            allowed_full = {
                (full["namespace"], item["code"], item["label"])
                for item in full["codes"]
            }
            for check in row["expected"]["conformance_checks"]:
                item = check["expected_status"]
                self.assertIn(
                    (item["namespace"], item["code"], item["label"]),
                    allowed_full,
                )


if __name__ == "__main__":
    unittest.main()
