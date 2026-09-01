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
        cls.descriptor_package = json.loads(cls.descriptor_bytes)
        cls.oracle_package = json.loads(cls.oracle_bytes)

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
                descriptors.CASE_TAG + descriptors.tv(row["body"])
            ).hexdigest()
            self.assertEqual(row["case_id"], expected_id)
            self.assertEqual(row["case_ordinal"], ordinal)
            self.assertGreater(expected_id, previous)
            previous = expected_id

    def test_record_fault_domain(self) -> None:
        faults = Counter(
            row["body"]["mutation"]
            for row in self.descriptor_package["rows"]
            if row["body"]["family"] == "RECORD_FAULT"
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

    def test_all_declared_comparison_rules_resolve(self) -> None:
        bodies = [row["body"] for row in self.descriptor_package["rows"]]

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
            if target["family"] == "STAGE_CONTROL":
                target["family"] = "CLEAN_MECHANISM"
            matches = []
            for candidate in bodies:
                normalized = dict(candidate)
                normalized["comparison_rules"] = []
                if normalized == target:
                    matches.append(candidate)
            self.assertEqual(len(matches), 1, body)

    def test_literal_oracle_alignment_and_outcomes(self) -> None:
        oracle_package = self.oracle_package
        self.assertEqual(oracle_package["row_count"], 3028)
        self.assertEqual(
            oracle_package["descriptor_stream_sha256"],
            hashlib.sha256(self.descriptor_bytes).hexdigest(),
        )
        self.assertEqual(
            [row["case_id"] for row in self.descriptor_package["rows"]],
            [row["case_id"] for row in oracle_package["rows"]],
        )
        applicability = Counter(
            row["expected"]["execution_applicability"]
            for row in oracle_package["rows"]
        )
        self.assertEqual(
            applicability,
            {"EXECUTED": 3004, "UNKNOWN_CONTROL_UNAVAILABLE": 24},
        )
        observations = Counter(
            row["expected"]["expected_recovery_hex"]
            for row in oracle_package["rows"]
        )
        self.assertEqual(
            observations,
            {
                "01": 2334,
                "0200000000": 334,
                "00": 232,
                "020000000100": 104,
                "NO_OBSERVATION": 24,
            },
        )


if __name__ == "__main__":
    unittest.main()
