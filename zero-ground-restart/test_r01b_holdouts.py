from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
import unittest


BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

import r01b_holdout_freeze as holdouts


class R01BHoldoutFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = (BASE / "R01B-HOLDOUTS.json").read_bytes()
        cls.package = json.loads(cls.raw)
        cls.measurements = json.loads((BASE / "R01B-MEASUREMENT-REGISTRY.json").read_bytes())
        cls.breaker = json.loads((BASE / "R01-BREAKER-OBJECT.json").read_bytes())
        cls.descriptors = json.loads((BASE / "R01B-DESCRIPTORS.json").read_bytes())
        cls.status_registry_raw = (BASE / "R01B-STATUS-REGISTRY.json").read_bytes()
        cls.status_registry = json.loads(cls.status_registry_raw)
        cls.rows = cls.package["rows"]
        cls.by_logical_id = {row["body"]["logical_id"]: row for row in cls.rows}

    def test_exact_regeneration_and_canonical_bytes(self) -> None:
        self.assertEqual(holdouts.encoded_package(), self.raw)
        self.assertEqual(holdouts.canonical_json(self.package), self.raw)
        self.assertEqual(self.package["schema_id"], "R01B-LAB-HOLDOUTS-1")
        self.assertEqual(self.package["row_count"], 3290)
        self.assertEqual(
            self.package["case_id_rule"],
            "ASCII(r01b-case-)||lowerhex(sha256(ASCII(ZGR01B-CASE)||00||TV(body)))",
        )
        self.assertEqual(
            hashlib.sha256(self.status_registry_raw).hexdigest(),
            holdouts.STATUS_REGISTRY_SHA256,
        )
        self.assertEqual(
            self.package["status_registry_source"],
            {
                "artifact": "R01B-STATUS-REGISTRY.json",
                "byte_length": len(self.status_registry_raw),
                "schema_id": self.status_registry["schema_id"],
                "sha256": holdouts.STATUS_REGISTRY_SHA256,
            },
        )
        self.assertEqual(
            self.package["status_coordinate_registry"],
            self.status_registry["status_coordinate_registry"],
        )
        self.assertEqual(
            self.package["failure_reason_registry"],
            self.status_registry["failure_reason_registry"],
        )

    def test_case_identity_order_and_expected_answer_exclusion(self) -> None:
        previous = ""
        logical_ids = set()
        for ordinal, row in enumerate(self.rows):
            body = row["body"]
            case_id = "r01b-case-" + hashlib.sha256(
                holdouts.CASE_TAG + holdouts.tv(body)
            ).hexdigest()
            self.assertEqual(row["case_id"], case_id)
            self.assertEqual(row["case_ordinal"], ordinal)
            self.assertGreater(case_id, previous)
            previous = case_id
            self.assertNotIn(body["logical_id"], logical_ids)
            logical_ids.add(body["logical_id"])

            # The complete oracle can change without changing history identity.
            mutated_expected = json.loads(json.dumps(row["expected"]))
            mutated_expected["needed_evidence"] = ["deliberate test mutation"]
            self.assertEqual(
                case_id,
                "r01b-case-" + hashlib.sha256(
                    holdouts.CASE_TAG + holdouts.tv(body)
                ).hexdigest(),
            )

            def keys(value: object) -> set[str]:
                if isinstance(value, dict):
                    return set(value) | set().union(*(keys(child) for child in value.values()), set())
                if isinstance(value, list):
                    return set().union(*(keys(child) for child in value), set())
                return set()

            body_keys = keys(body)
            self.assertNotIn("expected", body_keys)
            self.assertNotIn("expected_full_verdict", body_keys)
            self.assertNotIn("expected_recovery_hex", body_keys)
            self.assertNotIn("only_permitted_claim", body_keys)
            self.assertNotIn("status_coordinates", body_keys)
            self.assertNotIn("failure_reasons", body_keys)

    def test_subject_and_lab_case_id_union_is_unique(self) -> None:
        subject_ids = [row["case_id"] for row in self.descriptors["rows"]]
        lab_ids = [row["case_id"] for row in self.rows]
        self.assertEqual(len(subject_ids), len(set(subject_ids)))
        self.assertEqual(len(lab_ids), len(set(lab_ids)))
        self.assertTrue(set(subject_ids).isdisjoint(lab_ids))
        self.assertEqual(len(subject_ids + lab_ids), len(set(subject_ids + lab_ids)))
        self.assertTrue(all(case_id.startswith("r01b-case-") for case_id in subject_ids + lab_ids))
        neutral_fixture = self.by_logical_id["NEUTRAL_FRAME_DUPLICATE_NEGATIVE"]["body"]["fixture"]
        replay_fixture = self.by_logical_id["EVIDENCE_REPLAY_POSITIVE"]["body"]["fixture"]
        nested_fixture_ids = [
            neutral_fixture["controller_trial_registry"]["descriptor_identity"]["case_id"],
            replay_fixture["replay_index"]["descriptor_identity"]["case_id"],
        ]
        self.assertEqual(len(nested_fixture_ids), len(set(nested_fixture_ids)))
        self.assertTrue(set(nested_fixture_ids).isdisjoint(subject_ids + lab_ids))

    def test_every_row_is_laboratory_only(self) -> None:
        for row in self.rows:
            body = row["body"]
            expected = row["expected"]
            self.assertEqual(body["history_production"], "LAB_ONLY")
            self.assertEqual(body["b_crossing_count"], 0)
            self.assertEqual(body["b_comparison_eligibility"], "FORBIDDEN")
            self.assertEqual(body["b_state_verdict_eligibility"], "FORBIDDEN")
            self.assertEqual(body["repetition"], 0)
            self.assertNotIn("b_state_verdict", expected)
            self.assertEqual(
                expected["status_coordinates"]["behavioral_comparison"]["label"],
                "NOT_COMPARED",
            )
            scopes = expected["status_coordinates"]["scope"]
            self.assertNotIn("B_PROCESS_KILL", {scope["label"] for scope in scopes})

    def test_status_coordinates_and_reason_invariants(self) -> None:
        coordinate_names = {
            "applicability",
            "behavioral_comparison",
            "execution",
            "full_conformance",
            "oracle",
            "scope",
        }
        for row in self.rows:
            expected = row["expected"]
            coordinates = expected["status_coordinates"]
            self.assertEqual(set(coordinates), coordinate_names)
            for name in coordinate_names - {"scope"}:
                namespace, labels = holdouts.STATUS_TABLES[name]
                value = coordinates[name]
                self.assertEqual(value["namespace"], namespace)
                self.assertEqual(value["code"], labels.index(value["label"]))
            scope_codes = [value["code"] for value in coordinates["scope"]]
            self.assertEqual(scope_codes, sorted(set(scope_codes)))
            self.assertEqual(expected["needed_evidence"], sorted(set(expected["needed_evidence"])))
            reason_codes = [reason["code"] for reason in expected["failure_reasons"]]
            self.assertEqual(reason_codes, sorted(set(reason_codes)))
            common_reasons = {
                item["label"]: item for item in self.status_registry["failure_reason_registry"]
            }
            for reason in expected["failure_reasons"]:
                self.assertEqual(reason, {
                    "code": common_reasons[reason["label"]]["code"],
                    "label": reason["label"],
                })
                self.assertIn("LAB_HOLDOUT", common_reasons[reason["label"]]["origins"])
            self.assertEqual(
                coordinates["full_conformance"]["label"] == "FAIL",
                bool(expected["failure_reasons"]),
            )

    def test_all_22_historical_cases_have_exact_mapping(self) -> None:
        mappings = self.package["historical_case_mappings"]
        self.assertEqual(len(mappings), 22)
        self.assertEqual(
            [(item["source_case_index"], item["source_case_id"]) for item in mappings],
            [(index, case["id"]) for index, case in enumerate(self.breaker["cases"])],
        )
        expected_counts = {index: 1 for index in range(22)}
        expected_counts.update({4: 2, 19: 1040, 20: 2081, 21: 2})
        self.assertEqual(
            {item["source_case_index"]: item["mapped_case_id_count"] for item in mappings},
            expected_counts,
        )
        mapped = defaultdict(list)
        for row in self.rows:
            for provenance in row["provenance"]:
                if provenance.get("artifact") == "R01-BREAKER-OBJECT.json":
                    mapped[provenance["source_case_index"]].append(row["case_id"])
        for item in mappings:
            ids = sorted(mapped[item["source_case_index"]])
            self.assertEqual(item["mapped_case_ids_sha256"], hashlib.sha256(holdouts.canonical_json(ids)).hexdigest())

    def test_every_v2_path_has_one_delete_and_both_structured_status_cases(self) -> None:
        delete_paths = []
        unknown_paths = []
        unsupported_paths = []
        for row in self.rows:
            body = row["body"]
            if body["attack_kind"] == "DELETE_EXACT_MEASUREMENT_LEAF":
                delete_paths.append(body["fixture"]["path"])
            if body["attack_kind"] == "REPLACE_EXACT_MEASUREMENT_LEAF_WITH_STRUCTURED_UNKNOWN":
                unknown_paths.append(body["fixture"]["path"])
                replacement = body["fixture"]["replacement"]
                self.assertEqual(set(replacement), {"needed_evidence", "reason", "status"})
                self.assertEqual(replacement["status"], "UNKNOWN")
                self.assertEqual(
                    body["fixture"]["replacement_tv_hex"],
                    holdouts.structured_unknown_bytes(
                        replacement["reason"], replacement["needed_evidence"]
                    ).hex(),
                )
            if body["attack_kind"] == "REPLACE_EXACT_MEASUREMENT_LEAF_WITH_STRUCTURED_UNSUPPORTED":
                unsupported_paths.append(body["fixture"]["path"])
                replacement = body["fixture"]["replacement"]
                self.assertEqual(set(replacement), {"reason", "status"})
                self.assertEqual(replacement["status"], "UNSUPPORTED")
                self.assertEqual(
                    body["fixture"]["replacement_tv_hex"],
                    holdouts.structured_unsupported_bytes(replacement["reason"]).hex(),
                )
        self.assertEqual(sorted(delete_paths), sorted(self.measurements["paths"]))
        self.assertEqual(sorted(unknown_paths), sorted(self.measurements["paths"]))
        self.assertEqual(sorted(unsupported_paths), sorted(self.measurements["paths"]))
        self.assertEqual(Counter(delete_paths), Counter({path: 1 for path in self.measurements["paths"]}))
        self.assertEqual(Counter(unknown_paths), Counter({path: 1 for path in self.measurements["paths"]}))
        self.assertEqual(Counter(unsupported_paths), Counter({path: 1 for path in self.measurements["paths"]}))
        self.assertEqual(
            self.package["named_case_family_registry"]["MEASURE_STRUCTURED_UNKNOWN_VALID"],
            {
                "attack_kind": "REPLACE_EXACT_MEASUREMENT_LEAF_WITH_STRUCTURED_UNKNOWN",
                "expansion": "exactly one MEASURE_STRUCTURED_UNKNOWN(path) per final V2 path",
                "path_count": 1040,
            },
        )

        for path in self.measurements["paths"]:
            row = self.by_logical_id[f"MEASURE_STRUCTURED_UNKNOWN({path})"]
            policy = self.measurements["path_policies"][path]["status_policy"]
            full = row["expected"]["status_coordinates"]["full_conformance"]["label"]
            if policy == "NATIVE_ONLY":
                self.assertEqual(full, "FAIL")
                self.assertEqual(
                    [reason["label"] for reason in row["expected"]["failure_reasons"]],
                    ["STRUCTURED_STATUS_FORBIDDEN"],
                )
            else:
                self.assertEqual(full, "UNKNOWN")
                self.assertTrue(row["expected"]["needed_evidence"])

            unsupported = self.by_logical_id[f"MEASURE_STRUCTURED_UNSUPPORTED({path})"]
            unsupported_full = unsupported["expected"]["status_coordinates"]["full_conformance"]["label"]
            if policy == "NATIVE_OR_UNKNOWN_OR_UNSUPPORTED":
                self.assertEqual(unsupported_full, "UNSUPPORTED")
                self.assertFalse(unsupported["expected"]["failure_reasons"])
            else:
                self.assertEqual(unsupported_full, "FAIL")
                self.assertEqual(
                    [reason["label"] for reason in unsupported["expected"]["failure_reasons"]],
                    ["STRUCTURED_STATUS_FORBIDDEN"],
                )

    def test_measurement_attacks_bind_an_explicit_open_s1_fixture_recipe(self) -> None:
        registry_entry = self.package["pre_execution_fixture_registry"][
            holdouts.MEASUREMENT_FIXTURE_RECIPE_ID
        ]
        recipe = registry_entry["recipe"]
        recipe_sha256 = hashlib.sha256(holdouts.canonical_json(recipe)).hexdigest()
        self.assertEqual(registry_entry["recipe_sha256"], recipe_sha256)
        self.assertEqual(recipe["materialization_status"], "OPEN")
        self.assertFalse(recipe["exact_materialized_bytes_present"])
        self.assertIn("S1 MUST retain", recipe["retention_requirement"])
        for row in self.rows:
            if row["body"]["family"] != "MEASUREMENT_SCHEMA":
                continue
            binding = row["body"]["fixture"]["source_fixture"]
            self.assertEqual(binding["recipe_id"], holdouts.MEASUREMENT_FIXTURE_RECIPE_ID)
            self.assertEqual(binding["recipe_sha256"], recipe_sha256)

    def test_every_required_closed_member_has_one_deletion_case(self) -> None:
        expected_members = set()
        schema_domains = {
            "closed_container_schemas": self.measurements["closed_container_schemas"],
            "native_value_kinds.definitions": self.measurements["native_value_kinds"]["definitions"],
            "structured_statuses": self.measurements["structured_statuses"],
        }
        for domain, schemas in schema_domains.items():
            for schema_name, schema in schemas.items():
                for location, member in holdouts.required_members(schema):
                    expected_members.add((domain, schema_name, location, member))

        actual_members = []
        for row in self.rows:
            body = row["body"]
            if body["attack_kind"] not in {
                "DELETE_REQUIRED_CLOSED_CONTAINER_MEMBER",
                "DELETE_REQUIRED_STRUCTURED_UNKNOWN_MEMBER",
            }:
                continue
            fixture = body["fixture"]
            actual_members.append(
                (
                    fixture["schema_domain"],
                    fixture["schema_name"],
                    fixture["schema_location"],
                    fixture["member_deleted"],
                )
            )
        self.assertEqual(len(actual_members), 147)
        self.assertEqual(set(actual_members), expected_members)
        self.assertEqual(len(actual_members), len(set(actual_members)))

    def test_corrected_split_identities_are_distinct(self) -> None:
        required = {
            "POWER_GUARD",
            "SELECT_ALT_PRE",
            "SELECT_ALT_POST",
            "LEGACY_A000_DUPLICATE_NEGATIVE",
            "NEUTRAL_FRAME_DUPLICATE_NEGATIVE",
            "EVIDENCE_HASH_ONLY_NEGATIVE",
            "EVIDENCE_REPLAY_POSITIVE",
            "MEASURE_UNKNOWN_MISSING_EVIDENCE_NEGATIVE",
            "REAP_ORDER_REFERENCE_FORGERY_NEGATIVE",
            "ADAPTER_TIMEOUT",
            "ADAPTER_SIGNAL_15",
            "RECOVERY_SIGNAL_9",
            "ENV_PARENT_X_PAIR",
            "COMPARATOR_EXPECTED_BYTE_MUTATION_NEGATIVE",
        }
        self.assertLessEqual(required, set(self.by_logical_id))

        legacy = self.by_logical_id["LEGACY_A000_DUPLICATE_NEGATIVE"]
        neutral = self.by_logical_id["NEUTRAL_FRAME_DUPLICATE_NEGATIVE"]
        self.assertNotEqual(legacy["case_id"], neutral["case_id"])
        self.assertEqual(legacy["body"]["fixture"]["submitted_l_record"]["legacy_frames_hex"], ["a000", "a000"])
        frames = neutral["body"]["fixture"]["submitted_frames_hex"]
        self.assertEqual(len(frames), 2)
        self.assertEqual(frames[0], frames[1])
        self.assertEqual(len(bytes.fromhex(frames[0])), 40)
        self.assertTrue(frames[0].startswith("5a474e4601000100"))
        trial_registry = neutral["body"]["fixture"]["controller_trial_registry"]
        symbolic_case_id = "r01b-case-" + hashlib.sha256(
            holdouts.CASE_TAG + holdouts.tv(trial_registry["symbolic_case_body"])
        ).hexdigest()
        self.assertEqual(trial_registry["descriptor_identity"]["case_id"], symbolic_case_id)
        digest = hashlib.sha256(
            b"ZGR01B-TRIAL\x00" + holdouts.tv(trial_registry["descriptor_identity"])
        ).hexdigest()
        self.assertEqual(trial_registry["trial_id"], "r01b-" + digest)
        self.assertEqual(neutral["body"]["fixture"]["registered_trial_digest_hex"], digest)
        self.assertTrue(frames[0].endswith(digest))
        self.assertEqual(trial_registry["symbolic_case_body"]["history_production"], "LAB_ONLY")
        self.assertEqual(trial_registry["descriptor_identity"]["history_production"], "LAB_ONLY")
        self.assertIn("exact_lab_input", trial_registry["descriptor_identity"])
        self.assertNotIn("exact_b_inputs", trial_registry["descriptor_identity"])

        negative = self.by_logical_id["EVIDENCE_HASH_ONLY_NEGATIVE"]
        positive = self.by_logical_id["EVIDENCE_REPLAY_POSITIVE"]
        self.assertEqual(negative["body"]["fixture"]["envelope_bytes"], "ABSENT")
        self.assertNotIn("envelope_hex", negative["body"]["fixture"])
        self.assertTrue(positive["body"]["fixture"]["envelope_hex"])
        self.assertEqual(
            negative["body"]["fixture"]["envelope_sha256"],
            positive["body"]["fixture"]["envelope_sha256"],
        )
        selector = positive["body"]["fixture"]["selector"]
        raw_selectors = positive["body"]["fixture"]["raw_selectors"]
        self.assertEqual(selector["ordinal"], 0)
        self.assertRegex(selector["trial_id"], r"^r01b-[0-9a-f]{64}$")
        self.assertEqual(selector, negative["body"]["fixture"]["selector"])
        self.assertEqual(raw_selectors, negative["body"]["fixture"]["raw_selectors"])
        replay_index = positive["body"]["fixture"]["replay_index"]
        self.assertEqual(replay_index, negative["body"]["fixture"]["replay_index"])
        selectors = [selector, *raw_selectors]
        self.assertEqual(replay_index["entries"], selectors)
        self.assertEqual(replay_index["ordered_trial_ids"], [selector["trial_id"]])
        replay_case_id = "r01b-case-" + hashlib.sha256(
            holdouts.CASE_TAG + holdouts.tv(replay_index["symbolic_case_body"])
        ).hexdigest()
        self.assertEqual(replay_index["descriptor_identity"]["case_id"], replay_case_id)
        replay_trial_digest = hashlib.sha256(
            b"ZGR01B-TRIAL\x00" + holdouts.tv(replay_index["descriptor_identity"])
        ).hexdigest()
        self.assertEqual(selector["trial_id"], "r01b-" + replay_trial_digest)
        expected_ranges = {
            item["stream"]: bytes.fromhex(item["selected_hex"])
            for item in positive["expected"]["details"]["selected_ranges"]
        }
        self.assertEqual(
            set(expected_ranges),
            {"canonical_records", "inventory_pack", "raw_measurement_pack", "raw_trace_pack"},
        )
        self.assertEqual({item["stream"] for item in raw_selectors}, set(expected_ranges) - {"canonical_records"})
        envelope = bytes.fromhex(positive["body"]["fixture"]["envelope_hex"])
        expected_wire_coordinates = {
            ("applicability", "APPLICABLE"),
            ("behavioral_comparison", "NOT_COMPARED"),
            ("execution", "COMPLETE"),
            ("full_conformance", "UNKNOWN"),
            ("oracle", "NOT_DECLARED"),
            ("scope", "L_EVIDENCE"),
        }
        for name, label in expected_wire_coordinates:
            self.assertIn(holdouts.tv(holdouts.wire_enum(name, label)), envelope)
            self.assertNotIn(holdouts.tv(label), envelope)
        negative_body_bytes = holdouts.canonical_json(negative["body"])
        stream_inventory = replay_index["descriptor_identity"]["exact_lab_input"]["stream_inventory"]
        self.assertEqual(
            {item["stream"] for item in stream_inventory},
            set(expected_ranges),
        )
        for range_selector in selectors:
            stream_name = range_selector["stream"]
            selected = expected_ranges[stream_name]
            self.assertEqual(range_selector["ordinal"], 0)
            self.assertEqual(range_selector["trial_id"], selector["trial_id"])
            self.assertEqual(range_selector["offset"], 0)
            self.assertEqual(range_selector["length"], len(selected))
            self.assertEqual(range_selector["record_sha256"], hashlib.sha256(selected).hexdigest())
            self.assertEqual(
                replay_index["stream_sha256_by_name"][stream_name],
                hashlib.sha256(selected).hexdigest(),
            )
            self.assertIn(selected, envelope)
            self.assertNotIn(selected.hex().encode("ascii"), negative_body_bytes)
        self.assertNotEqual(negative["case_id"], positive["case_id"])

        reaping = self.by_logical_id["REAP_ORDER_REFERENCE_FORGERY_NEGATIVE"]
        self.assertEqual(
            reaping["body"]["fixture"]["submitted_l_record"]["mechanism_manifest"],
            "REFERENCE",
        )

    def test_unknown_or_unsupported_rows_do_not_claim_pass(self) -> None:
        for row in self.rows:
            coordinates = row["expected"]["status_coordinates"]
            full = coordinates["full_conformance"]["label"]
            applicability = coordinates["applicability"]["label"]
            if full in {"UNKNOWN", "UNSUPPORTED", "NOT_APPLICABLE"}:
                self.assertNotEqual(full, "PASS")
            if applicability in {"CONDITIONAL_ONLY", "UNSUPPORTED_HERE"}:
                self.assertEqual(coordinates["execution"]["label"], "NOT_RUN")
                self.assertTrue(row["expected"]["needed_evidence"])


if __name__ == "__main__":
    unittest.main()
