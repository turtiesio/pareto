from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import sys
import unittest


BASE = Path(__file__).resolve().parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

import r01b_semantic_freeze as freeze
import r01b_tv


AUTHORITY_HASHES = {
    "REALIZATION-CORRECTION-R01B.md": "250a001aa01f935a13a936ed72c75daecc5d9e29819c871fbd0605ba42672089",
    "R01B-STATUS-REGISTRY.json": "54857699919b5c95de79bb25006a6fd4f9f448870c7d97c4364be75c6191c61a",
    "R01B-HOLDOUTS.json": "19460295c8d75ad74cd88f66098bb96692ed8d49686b9be829e2d2a86ea6996b",
    "R01B-LITERAL-ORACLE.json": "68139147030cfa67a381b45910b87f04b74f351b131aa8f9cef5e69ee6f63b32",
    "R01B-DESCRIPTORS.json": "e20460d1ba30f1e91e274ee7670aa009bb1d2c37def6e8a6f31d067995198f12",
    "R01B-MEASUREMENT-REGISTRY.json": "854abc48e8e610f9487e07c7c81ed64a32772836d70fc08e40cb3d8b72f6223d",
    "R01B-SUITE.json": "6f4a1b4588ff4218fff0cd75744d1e8ca2b31c9a9e401334f5d1c746d84cb5cc",
}

EXPECTED_SEMANTIC_SEED = "078acf7c35cf1840b70886dd854f4fffcc0be1a7c5f8b1627d3bd36e148c2ece"
EXPECTED_SEMANTIC_SUITE = "996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a6"
EXPECTED_S0_INDEX_SHA256 = "49b946f5cf78d61e8238b902789904587b3bb8a74ba2303fe25ab892859f5e90"
EXPECTED_S1_SHA256 = "fb72f6b36ca3eae284003ee1983e995afb13d3e8ec9d518f0c1afeaca67a9043"
EXPECTED_SEMANTIC_FREEZE_ID = (
    "r01b-semantic-954e2b16b258ceb8869795dbb823a0284a8369ca1cb20481168d7f652d89fcfd"
)


def unwrap(value):
    if isinstance(value, (r01b_tv.U64, r01b_tv.I64)):
        return value.value
    if isinstance(value, tuple):
        return [unwrap(item) for item in value]
    if isinstance(value, dict):
        return {key: unwrap(child) for key, child in value.items()}
    return value


class R01BSemanticFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = freeze.build(BASE)
        cls.s1 = cls.result.s1_value

    def test_authority_snapshot_and_generated_artifacts_are_exact(self) -> None:
        for name, expected in AUTHORITY_HASHES.items():
            actual = hashlib.sha256((BASE / name).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, name)
        for name, expected in self.result.outputs().items():
            self.assertEqual((BASE / name).read_bytes(), expected, name)
        self.assertEqual(self.result.semantic_seed_digest.hex(), EXPECTED_SEMANTIC_SEED)
        self.assertEqual(self.result.semantic_suite_digest.hex(), EXPECTED_SEMANTIC_SUITE)
        self.assertEqual(
            hashlib.sha256(self.result.s0_index_bytes).hexdigest(),
            EXPECTED_S0_INDEX_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.result.s1_bytes).hexdigest(), EXPECTED_S1_SHA256
        )
        self.assertEqual(self.result.semantic_freeze_id, EXPECTED_SEMANTIC_FREEZE_ID)

    def test_s0_is_exact_and_every_member_deletion_changes_the_seed(self) -> None:
        members = self.result.s0_index_value["members"]
        self.assertEqual([item["filename"] for item in members], list(freeze.S0_NAMES))
        self.assertEqual(len(members), 12)
        self.assertEqual(
            hashlib.sha256(self.result.s0_manifest_bytes).digest(),
            self.result.semantic_seed_digest,
        )
        for deleted in freeze.S0_NAMES:
            manifest, _ = freeze.canonical_manifest(
                BASE, (name for name in freeze.S0_NAMES if name != deleted)
            )
            self.assertNotEqual(
                hashlib.sha256(manifest).digest(),
                self.result.semantic_seed_digest,
                deleted,
            )

    def test_descriptor_union_trial_ids_ordinals_and_linkage_are_exact(self) -> None:
        registry = self.s1["descriptor_registry"]
        rows = registry["rows"]
        self.assertEqual(registry["row_count"], 6318)
        self.assertEqual(len(rows), 6318)
        trial_ids = [row["trial_id"] for row in rows]
        self.assertEqual(trial_ids, sorted(trial_ids, key=lambda item: item.encode("ascii")))
        self.assertEqual(len(set(trial_ids)), 6318)
        self.assertEqual([row["ordinal"] for row in rows], list(range(6318)))
        for row in rows:
            expected = "r01b-" + hashlib.sha256(
                freeze.TRIAL_TAG + bytes.fromhex(row["descriptor_template_tv_hex"])
            ).hexdigest()
            self.assertEqual(row["trial_id"], expected)
            self.assertEqual(
                row["comparison_edge_ids"], sorted(set(row["comparison_edge_ids"]))
            )
            self.assertEqual(
                row["comparison_partner_case_ids"],
                sorted(set(row["comparison_partner_case_ids"])),
            )

        literals = self.s1["literal_oracle_registry"]["rows"]
        self.assertEqual(len(literals), 6318)
        self.assertEqual(
            [row["case_id"] for row in literals],
            sorted((row["case_id"] for row in rows), key=lambda item: item.encode("ascii")),
        )

    def test_recovery_recipe_mapping_preserves_real_collisions_only(self) -> None:
        recipes = self.s1["fixture_and_mutation_registry"]["recovery_recipes"]
        self.assertEqual(len(recipes), 1172)
        self.assertEqual(len({row["recipe_tv_hex"] for row in recipes}), 1172)
        self.assertEqual(len({row["fixture_tv_hex"] for row in recipes}), 1137)
        self.assertEqual(
            [bytes.fromhex(row["recipe_tv_hex"]) for row in recipes],
            sorted(bytes.fromhex(row["recipe_tv_hex"]) for row in recipes),
        )

    def test_flip_is_lsb_numbered_and_wrong_suite_is_coherently_rehashed(self) -> None:
        recipes = self.s1["fixture_and_mutation_registry"]["recovery_recipes"]
        digest = self.result.semantic_suite_digest
        saw_flip_zero = False
        wrong_count = 0
        for row in recipes:
            recipe = unwrap(r01b_tv.decode(bytes.fromhex(row["recipe_tv_hex"])))
            fixture = r01b_tv.decode(bytes.fromhex(row["fixture_tv_hex"]))
            payload = bytes.fromhex(recipe["base_record_payload_hex"])
            if recipe["mutation"] == "FLIP" and recipe["arg0"] == 0 and recipe["arg1"] == 0:
                source = freeze.record(digest, payload)
                expected = bytearray(source)
                expected[0] ^= 0x01
                self.assertEqual(
                    fixture["authoritative_entry"]["regular_bytes"], bytes(expected)
                )
                saw_flip_zero = True
            if recipe["mutation"] == "WRONG_SUITE":
                wrong = bytes([digest[0] ^ 0x80]) + digest[1:]
                expected = freeze.record(wrong, payload)
                self.assertEqual(
                    fixture["authoritative_entry"]["regular_bytes"], expected
                )
                self.assertEqual(expected[:32], wrong)
                self.assertNotEqual(expected[-32:], freeze.record(digest, payload)[-32:])
                wrong_count += 1
        self.assertTrue(saw_flip_zero)
        self.assertEqual(wrong_count, 2)

    def test_measurement_base_is_schema_complete_and_uses_u64(self) -> None:
        item = self.s1["measurement_base_fixture"]
        raw = bytes.fromhex(item["fixture_tv_hex"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), item["fixture_tv_sha256"])
        fixture = r01b_tv.decode(raw)
        self.assertEqual(len(fixture), 1040)
        self.assertEqual(item["path_count"], 1040)
        correction_count = fixture["authoring_burden.correction_count"]
        self.assertEqual(correction_count["value"], r01b_tv.U64(0))
        self.assertEqual(set(correction_count), {"method", "scope", "unit", "value"})
        self.assertEqual(fixture["identity.breaker_object_sha256"], "0" * 64)
        self.assertEqual(fixture["identity.run_id"], "r01b-run-" + "0" * 64)
        self.assertEqual(fixture["identity.backend"], "E")
        self.assertIs(fixture["human_cognition.no_inference_from_loc_alone"], True)

    def test_oracle_edges_and_check_inventory_survive_exactly(self) -> None:
        literal = self.s1["literal_oracle_registry"]
        self.assertEqual(len(literal["comparison_edges"]), 2010)
        subject_checks = sum(
            len(row["expected"].get("conformance_check_keys", []))
            for row in literal["rows"]
        )
        lab_checks = sum(
            len(row["expected"].get("conformance_checks", []))
            for row in literal["rows"]
        )
        self.assertEqual(subject_checks, 64680)
        self.assertEqual(lab_checks, 3290 * 3)

    def test_mixed_pass_and_not_applicable_aggregates_to_pass(self) -> None:
        status = freeze.parse_json(
            (BASE / "R01B-STATUS-REGISTRY.json").read_bytes(),
            "R01B-STATUS-REGISTRY.json",
        )
        rule = status["aggregation_precedence"]["full_conformance"]
        self.assertEqual(
            rule["highest_to_lowest"],
            ["FAIL", "UNKNOWN", "UNSUPPORTED", "PASS", "NOT_APPLICABLE"],
        )
        rank = {label: index for index, label in enumerate(rule["highest_to_lowest"])}
        values = ["PASS", "NOT_APPLICABLE"]
        aggregate = min(values, key=rank.__getitem__)
        self.assertEqual(aggregate, "PASS")
        self.assertEqual(rule["empty_input"], "NOT_APPLICABLE")

    def test_s1_top_level_deletion_and_cycle_attacks_fail(self) -> None:
        expected_keys = {
            "descriptor_registry",
            "fixture_and_mutation_registry",
            "literal_oracle_registry",
            "measurement_base_fixture",
            "schema_id",
            "semantic_suite_digest",
        }
        self.assertEqual(set(self.s1), expected_keys)
        for key in expected_keys:
            changed = copy.deepcopy(self.s1)
            del changed[key]
            self.assertNotEqual(
                freeze.canonical_json(changed, printable_ascii=True), self.result.s1_bytes
            )
        self.assertNotIn(b'"semantic_freeze_id"', self.result.s1_bytes)
        self.assertNotIn(b'"realization_id"', self.result.s1_bytes)
        self.assertNotIn(self.result.semantic_freeze_id.encode("ascii"), self.result.s1_bytes)
        self.assertFalse(
            self.result.closure_value["cycle_exclusions"][
                "final_freeze_artifact_is_manifest_member"
            ]
        )
        with self.assertRaises(freeze.FreezeError):
            freeze.canonical_json({"illegal": None}, printable_ascii=True)
        with self.assertRaises(freeze.FreezeError):
            freeze.canonical_json({"illegal": -1}, printable_ascii=True)

    def test_final_hash_is_framed_and_gate_machinery_cannot_change_it(self) -> None:
        expected_digest = hashlib.sha256(
            freeze.FREEZE_TAG
            + freeze.lp(self.result.s0_manifest_bytes)
            + self.result.semantic_suite_digest
            + freeze.lp(self.result.s1_manifest_bytes)
        ).hexdigest()
        self.assertEqual(
            self.result.semantic_freeze_id, "r01b-semantic-" + expected_digest
        )
        changed_gate_manifest = self.result.gate_manifest_bytes + b"unlike-generator"
        self.assertNotEqual(changed_gate_manifest, self.result.gate_manifest_bytes)
        # Gate machinery is deliberately absent from the semantic hash preimage.
        self.assertEqual(
            "r01b-semantic-" + expected_digest, self.result.semantic_freeze_id
        )


if __name__ == "__main__":
    unittest.main()
