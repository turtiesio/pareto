#!/usr/bin/env python3
"""Independent tests for the R0.1B black-box breaker.

The tests use frozen semantic artifacts and synthetic raw envelopes only.  No
subject, runner, realization codec, or Rust implementation is imported.
"""

from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import r01b_blackbox_breaker as breaker


class BlackBoxBreakerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = breaker.FrozenCorpus()
        cls.report = breaker.static_report(cls.corpus)

    def _enum(self, coordinate: str, label: str) -> breaker.ClosedEnum:
        table = self.corpus.status_registry["status_coordinate_registry"][coordinate]
        code = next(item["code"] for item in table["codes"] if item["label"] == label)
        return breaker.ClosedEnum(table["namespace"], code)

    def _status_tv(self, expected: dict) -> dict:
        labels = breaker._expected_coordinate_labels(expected)
        self.assertFalse(labels.get("failure_reasons"))
        return {
            "applicability": self._enum("applicability", labels["applicability"]),
            "behavioral_comparison": self._enum(
                "behavioral_comparison", labels["behavioral_comparison"]
            ),
            "execution": self._enum("execution", labels["execution"]),
            "failure_reasons": [],
            "full_conformance": self._enum("full_conformance", labels["full_conformance"]),
            "needed_evidence": list(labels.get("needed_evidence", [])),
            "oracle": self._enum("oracle", labels["oracle"]),
            "scope": [self._enum("scope", label) for label in labels["scope"]],
        }

    def _envelope_for(self, case_id: str, marker: bytes = b"record") -> bytes:
        body = {
            "canonical_records": marker,
            "inventory_pack": b"inventory",
            "raw_measurement_pack": b"measurement",
            "raw_trace_pack": b"trace",
            "status_coordinates": self._status_tv(self.corpus.literal[case_id]),
        }
        return breaker.ENVELOPE_PREFIX + breaker.encode_tv(body)

    def test_independently_reconstructs_every_identity_and_check(self) -> None:
        self.assertEqual(len(self.corpus.descriptors), 6318)
        self.assertEqual(len(self.corpus.symbolic), 6318)
        self.assertEqual(len(self.corpus.edges), 2010)
        self.assertEqual(self.corpus.subject_check_count, 64680)
        self.assertEqual(self.corpus.lab_check_count, 9870)
        self.assertEqual(
            self.corpus.semantic_freeze_id,
            "r01b-semantic-954e2b16b258ceb8869795dbb823a0284a8369ca1cb20481168d7f652d89fcfd",
        )

    def test_tv_codec_preserves_integer_and_status_types(self) -> None:
        value = {
            "bool": False,
            "bytes": b"\x00",
            "enum": breaker.ClosedEnum(4, 2),
            "i64": breaker.I64(-1),
            "list": [breaker.U64(0), "x"],
            "u64": breaker.U64(0),
            "unknown": breaker.StructuredUnknown("why", "trace"),
            "unsupported": breaker.StructuredUnsupported("outside scope"),
        }
        encoded = breaker.encode_tv(value)
        self.assertEqual(breaker.decode_tv(encoded), value)
        with self.assertRaises(breaker.BreakerError):
            breaker.encode_tv(0)
        with self.assertRaises(breaker.BreakerError):
            breaker.tv_from_json(None)
        with self.assertRaises(breaker.BreakerError):
            breaker.decode_tv(encoded + b"\x00")

    def test_aggregate_precedence_does_not_turn_unknown_into_pass(self) -> None:
        self.assertEqual(breaker.aggregate_full_conformance(["PASS", "UNKNOWN"]), "UNKNOWN")
        self.assertEqual(
            breaker.aggregate_full_conformance(["NOT_APPLICABLE", "PASS"]), "PASS"
        )
        self.assertEqual(breaker.aggregate_behavior(["MATCH", "UNKNOWN"]), "UNKNOWN")
        self.assertEqual(breaker.aggregate_behavior(["MATCH", "DIFFER"]), "DIFFER")

    def test_every_mandatory_attack_is_exercised(self) -> None:
        matrix = self.report["mandatory_attack_coverage"]
        self.assertEqual(set(matrix), set(breaker.MANDATORY_ATTACKS))
        self.assertTrue(all(matrix[name] for name in breaker.MANDATORY_ATTACKS))

    def test_contract_defects_are_separate_from_implementation_failure(self) -> None:
        self.assertEqual(self.report["verdict"], "CONTRACT_DEFECT_UNDECIDABLE")
        self.assertFalse(self.report["pass_awarded"])
        self.assertEqual(self.report["implementation_failures"], [])
        ids = {item["finding_id"] for item in self.report["contract_defects"]}
        self.assertEqual(
            ids,
            {
                "R01B-CONTRACT-CANONICAL-RECORD-GRAMMAR",
                "R01B-CONTRACT-FAILURE-REASON-NAMESPACE",
                "R01B-CONTRACT-REALIZATION-ID-CONSTRUCTION",
                "R01B-CONTRACT-NEEDED-EVIDENCE-SORT",
                "R01B-CONTRACT-POSITIVE-REPLAY-STATUS-SHAPE",
            },
        )

    def test_retained_static_report_is_exactly_regenerable(self) -> None:
        self.assertEqual(
            (breaker.HERE / breaker.REPORT_NAME).read_bytes(),
            breaker.canonical_report_bytes(self.report),
        )

    def test_persistence_classifies_information_not_normalized_copies(self) -> None:
        verdicts = self.report["persistence"]
        must_text = " ".join(item["responsibility"] for item in verdicts["MUST_SURVIVE"])
        rebuild_text = " ".join(item["responsibility"] for item in verdicts["MAY_REBUILD"])
        self.assertIn("raw trace/measurement/inventory byte", must_text)
        self.assertIn("scratch spellings", must_text)
        self.assertNotIn("per-edge results and constituent", must_text)
        self.assertIn("normalized per-edge comparison results", rebuild_text)
        self.assertIn("normalized constituent check statuses", rebuild_text)
        self.assertEqual(verdicts["MAY_FORGET"], [])

    def test_positive_replay_exact_envelope_deletes_two_required_lists(self) -> None:
        case_id, raw = self.corpus.positive_replay_fixture()
        self.assertEqual(
            case_id,
            "r01b-case-42ae315f4fd5286123fde985e90ee1b755470b06855f00b8cfafb174012689ef",
        )
        self.assertEqual(len(raw), 365)
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "23ef24df0532a76909d23ce60bb77660db2a15cd60091bf6a948f07780c3c271",
        )
        inspection = breaker.inspect_envelope(raw, self.corpus.status_registry)
        self.assertEqual(
            set(inspection.value["status_coordinates"]),
            {
                "applicability",
                "behavioral_comparison",
                "execution",
                "full_conformance",
                "oracle",
                "scope",
            },
        )
        self.assertIn(
            "missing status members: failure_reasons,needed_evidence", inspection.defects
        )

    def test_needed_evidence_future_has_two_different_canonical_orders(self) -> None:
        finding = next(
            item
            for item in self.report["contract_defects"]
            if item["finding_id"] == "R01B-CONTRACT-NEEDED-EVIDENCE-SORT"
        )
        witness = finding["smallest_witness"]
        self.assertEqual(witness["unsigned_utf8_order"], ["aa", "z"])
        self.assertEqual(witness["raw_tv_order"], ["z", "aa"])
        self.assertNotEqual(
            witness["unsigned_utf8_list_tv_hex"], witness["raw_tv_list_tv_hex"]
        )
        max_current = max(
            len(expected.get("needed_evidence", expected["status_coordinates"].get("needed_evidence", [])))
            for expected in self.corpus.literal.values()
        )
        self.assertEqual(max_current, 1)

    def test_gate_r_same_inventory_has_two_unruled_digests(self) -> None:
        finding = next(
            item
            for item in self.report["contract_defects"]
            if item["finding_id"] == "R01B-CONTRACT-REALIZATION-ID-CONSTRUCTION"
        )
        witness = finding["smallest_witness"]
        self.assertNotEqual(
            witness["candidate_preimage_1_sha256"], witness["candidate_preimage_2_sha256"]
        )
        self.assertEqual(len(witness["same_inventory"]), 1)

    def test_failure_reason_registry_cannot_derive_tag_0b_namespace(self) -> None:
        first = self.corpus.status_registry["failure_reason_registry"][0]
        self.assertEqual(set(first), {"code", "label", "origins"})
        self.assertNotIn("namespace", first)
        self.assertNotEqual(
            breaker.encode_tv(breaker.ClosedEnum(7, first["code"])),
            breaker.encode_tv(breaker.ClosedEnum(8, first["code"])),
        )

    def test_matching_outer_envelope_stays_undecidable_never_pass(self) -> None:
        case_id = next(
            case_id
            for case_id, row in self.corpus.descriptors.items()
            if row["history_production"] == "RECOVERY_ONLY"
            and not self.corpus.literal[case_id]["status_coordinates"]["failure_reasons"]
        )
        result = breaker.audit_envelopes(
            [(case_id, self._envelope_for(case_id))], self.corpus
        )
        self.assertEqual(result["verdict"], "CONTRACT_DEFECT_UNDECIDABLE")
        self.assertFalse(result["pass_awarded"])
        self.assertEqual(result["implementation_failures"], [])
        self.assertEqual(result["unknowns"][0]["status"], "UNKNOWN")

    def test_status_mutation_is_an_implementation_failure(self) -> None:
        case_id = next(
            case_id
            for case_id, row in self.corpus.descriptors.items()
            if row["history_production"] == "RECOVERY_ONLY"
            and self.corpus.literal[case_id]["status_coordinates"]["execution"] == "COMPLETE"
            and not self.corpus.literal[case_id]["status_coordinates"]["failure_reasons"]
        )
        raw = self._envelope_for(case_id)
        body = breaker.decode_tv(raw[len(breaker.ENVELOPE_PREFIX) :])
        body["status_coordinates"]["execution"] = self._enum("execution", "NOT_RUN")
        mutated = breaker.ENVELOPE_PREFIX + breaker.encode_tv(body)
        result = breaker.audit_envelopes([(case_id, mutated)], self.corpus)
        self.assertEqual(result["verdict"], "IMPLEMENTATION_FAILURE")
        failure = next(
            item for item in result["implementation_failures"]
            if item["failure_id"] == "STATUS_ORACLE_MISMATCH"
        )
        self.assertEqual(failure["smallest_witness"]["coordinate"], "execution")

    def test_same_envelope_for_distinguishable_cases_is_minimized_collision(self) -> None:
        groups: dict[bytes, list[str]] = {}
        for case_id, expected in self.corpus.literal.items():
            labels = breaker._expected_coordinate_labels(expected)
            if labels.get("failure_reasons"):
                continue
            key = breaker.canonical_json_bytes(
                {
                    name: labels[name]
                    for name in (
                        "applicability",
                        "behavioral_comparison",
                        "execution",
                        "full_conformance",
                        "needed_evidence",
                        "oracle",
                        "scope",
                    )
                }
            )
            groups.setdefault(key, []).append(case_id)
        pair = next(
            (values[0], candidate)
            for values in groups.values()
            for candidate in values[1:]
            if self.corpus.expected_fingerprint(values[0])
            != self.corpus.expected_fingerprint(candidate)
        )
        envelope = self._envelope_for(pair[0], marker=b"shared")
        result = breaker.audit_envelopes(
            [(pair[0], envelope), (pair[1], envelope)], self.corpus
        )
        collision = next(
            item for item in result["implementation_failures"]
            if item["failure_id"] == "DISTINGUISHABLE_HISTORY_COLLISION"
        )
        self.assertEqual(
            {collision["smallest_witness"]["left_case_id"], collision["smallest_witness"]["right_case_id"]},
            set(pair),
        )

    def test_malformed_and_unregistered_envelopes_are_failures(self) -> None:
        result = breaker.audit_envelopes(
            [
                ("r01b-case-" + "0" * 64, b"wrong"),
                (next(iter(self.corpus.literal)), b"wrong"),
            ],
            self.corpus,
        )
        ids = {item["failure_id"] for item in result["implementation_failures"]}
        self.assertEqual(ids, {"UNREGISTERED_CASE", "MALFORMED_ENVELOPE"})

    def test_carrier_is_strict_and_does_not_create_a_pass_protocol(self) -> None:
        case_id = next(
            case_id
            for case_id, row in self.corpus.descriptors.items()
            if row["history_production"] == "RECOVERY_ONLY"
            and not self.corpus.literal[case_id]["status_coordinates"]["failure_reasons"]
        )
        carrier = {
            "schema_id": "R01B-BLACKBOX-CARRIER-1",
            "semantic_freeze_id": self.corpus.semantic_freeze_id,
            "envelopes": [
                {"case_id": case_id, "envelope_hex": self._envelope_for(case_id).hex()}
            ],
        }
        result = breaker.audit_carrier(carrier, self.corpus)
        self.assertEqual(result["verdict"], "CONTRACT_DEFECT_UNDECIDABLE")
        self.assertFalse(result["pass_awarded"])
        invalid = dict(carrier, realization_id="invented")
        with self.assertRaises(breaker.BreakerError):
            breaker.audit_carrier(invalid, self.corpus)

    def test_cli_has_no_zero_exit_for_frozen_or_matching_synthetic_evidence(self) -> None:
        with redirect_stdout(io.StringIO()):
            self.assertEqual(breaker.main(["static"]), 2)
        case_id = next(
            case_id
            for case_id, row in self.corpus.descriptors.items()
            if row["history_production"] == "RECOVERY_ONLY"
            and not self.corpus.literal[case_id]["status_coordinates"]["failure_reasons"]
        )
        carrier = {
            "envelopes": [
                {"case_id": case_id, "envelope_hex": self._envelope_for(case_id).hex()}
            ],
            "schema_id": "R01B-BLACKBOX-CARRIER-1",
            "semantic_freeze_id": self.corpus.semantic_freeze_id,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "carrier.json"
            path.write_bytes(breaker.canonical_json_bytes(carrier))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(breaker.main(["carrier", str(path)]), 2)


if __name__ == "__main__":
    unittest.main()
