from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest


BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

import r01b_status_freeze as status


class R01BStatusFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = (BASE / "R01B-STATUS-REGISTRY.json").read_bytes()
        cls.package = json.loads(cls.raw)

    def test_exact_regeneration_and_canonical_bytes(self) -> None:
        self.assertEqual(status.encoded_registry(), self.raw)
        self.assertEqual(status.canonical_json(self.package), self.raw)
        self.assertFalse(self.raw.endswith(b"\n"))
        self.assertEqual(self.package["schema_id"], "R01B-STATUS-REGISTRY-1")

    def test_six_correction_namespaces_and_codes(self) -> None:
        tables = self.package["status_coordinate_registry"]
        self.assertEqual(len(tables), 6)
        self.assertEqual(
            sorted(value["namespace"] for value in tables.values()),
            list(range(1, 7)),
        )
        for name, namespace, labels in status.STATUS_NAMESPACES:
            table = tables[name]
            self.assertEqual(table["namespace"], namespace)
            self.assertEqual(
                table["codes"],
                [{"code": code, "label": label} for code, label in enumerate(labels)],
            )

    def test_aggregation_precedence_and_empty_inputs(self) -> None:
        self.assertEqual(status.aggregate_full_conformance([]), "NOT_APPLICABLE")
        self.assertEqual(status.aggregate_full_conformance(["PASS"]), "PASS")
        self.assertEqual(
            status.aggregate_full_conformance(["PASS", "UNSUPPORTED", "UNKNOWN"]),
            "UNKNOWN",
        )
        self.assertEqual(
            status.aggregate_full_conformance(["UNKNOWN", "FAIL"]),
            "FAIL",
        )
        self.assertEqual(status.aggregate_behavioral_comparison([]), "NOT_COMPARED")
        self.assertEqual(
            status.aggregate_behavioral_comparison(["MATCH", "UNKNOWN"]),
            "UNKNOWN",
        )
        self.assertEqual(
            status.aggregate_behavioral_comparison(["MATCH", "UNKNOWN", "DIFFER"]),
            "DIFFER",
        )
        with self.assertRaises(ValueError):
            status.aggregate_full_conformance(["BOGUS"])
        with self.assertRaises(ValueError):
            status.aggregate_behavioral_comparison(["BOGUS"])

    def test_failure_union_preserves_existing_lab_codes(self) -> None:
        registry = self.package["failure_reason_registry"]
        labels = tuple(item["label"] for item in registry)
        self.assertEqual(len(labels), 34)
        self.assertEqual(labels, status.FAILURE_REASON_LABELS)
        self.assertEqual(
            labels[: len(status.LAB_HOLDOUT_FAILURE_LABELS)],
            status.LAB_HOLDOUT_FAILURE_LABELS,
        )
        self.assertEqual([item["code"] for item in registry], list(range(len(registry))))
        self.assertEqual(
            set(labels),
            set(status.LAB_HOLDOUT_FAILURE_LABELS)
            | set(status.CORE_RUNTIME_FAILURE_LABELS)
            | {"UNREGISTERED_ERRNO"},
        )
        self.assertEqual(len(labels), len(set(labels)))

    def test_operation_and_evidence_registries_are_exact(self) -> None:
        self.assertEqual(tuple(self.package["operation_registry"]), status.OPERATION_IDS)
        self.assertEqual(len(status.OPERATION_IDS), 10)
        self.assertEqual(
            tuple(item["label"] for item in self.package["operation_fact_registry"]),
            status.OPERATION_FACTS,
        )
        self.assertEqual(
            {item["label"]: item["role"] for item in self.package["operation_fact_registry"]},
            status.OPERATION_FACT_ROLES,
        )
        self.assertEqual(
            tuple(self.package["configured_source_registry"]),
            status.CONFIGURED_SOURCES,
        )
        self.assertEqual(
            tuple(self.package["errno_coordinate_registry"]),
            ("NONE", "EEXIST_17", "EIO_5"),
        )
        self.assertEqual(
            tuple(self.package["evidence_source_registry"]),
            status.EVIDENCE_SOURCE_IDS,
        )

    def test_base_oracle_domains_are_exact(self) -> None:
        registries = self.package["base_oracle_label_registries"]
        self.assertEqual(tuple(registries["reachability"]), status.REACHABILITY_LABELS)
        self.assertEqual(tuple(registries["b_expectation_kind"]), status.B_EXPECTATION_KINDS)
        self.assertEqual(tuple(registries["terminal"]), status.TERMINAL_LABELS)
        self.assertEqual(tuple(registries["wait_order"]), status.WAIT_ORDER_LABELS)
        self.assertEqual(tuple(registries["risk_class"]), status.RISK_CLASS_LABELS)
        self.assertEqual(
            status.validate_base_oracle(),
            (),
        )

    def test_downstream_holdout_and_correction_validation(self) -> None:
        status.validate_constants()
        self.assertEqual(status.validate_external_sources(), status.validate_base_oracle())
        correction = status.validate_correction()
        raw = (BASE / "REALIZATION-CORRECTION-R01B.md").read_bytes()
        self.assertEqual(correction["byte_length"], len(raw))
        self.assertEqual(correction["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.package["correction_source"]["sha256"], correction["sha256"])

    def test_downstream_labels_have_one_authority_and_no_implicit_alias(self) -> None:
        self.assertEqual(status.validate_base_oracle(), ())
        common = {item["label"] for item in self.package["failure_reason_registry"]}
        self.assertEqual(common, set(status.FAILURE_REASON_LABELS))
        self.assertFalse(self.package["naming_policy"]["implicit_aliases"])

    def test_downstream_artifacts_are_not_hash_inputs(self) -> None:
        boundaries = self.package["validation_boundaries"]
        self.assertEqual(boundaries["base_oracle"], "R01B-LITERAL-ORACLE.json")
        self.assertEqual(boundaries["lab_holdout_source"], "r01b_holdout_freeze.py")
        serialized = json.dumps(self.package, sort_keys=True)
        oracle_sha = hashlib.sha256((BASE / boundaries["base_oracle"]).read_bytes()).hexdigest()
        self.assertNotIn(oracle_sha, serialized)


if __name__ == "__main__":
    unittest.main()
