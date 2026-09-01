"""Focused executable checks for the frozen R0 laboratory contract."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import struct
import unittest

import r0_adapter
import r0_realization as runner
import r0_record


BASE = Path(__file__).resolve().parent


class R0ByteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.q, cls.a, cls.d = r0_record.derive_digests(BASE)

    def test_frozen_contract_digest(self) -> None:
        self.assertEqual(self.q.hex(), runner.CONTRACT_SHA256)

    def test_smallest_suite_relations(self) -> None:
        self.assertEqual(
            sum(map(len, (
                r0_adapter.P0, r0_adapter.P1, r0_adapter.C,
                r0_adapter.Y0, r0_adapter.Y1,
            ))),
            2,
        )
        self.assertNotEqual(r0_adapter.P0, r0_adapter.P1)
        self.assertNotEqual(r0_adapter.Y0, r0_adapter.Y1)
        self.assertEqual(r0_adapter.apply(r0_adapter.P0, r0_adapter.C), r0_adapter.Y0)
        self.assertEqual(r0_adapter.apply(r0_adapter.P1, r0_adapter.C), r0_adapter.Y1)

    def test_literal_observation_bytes(self) -> None:
        self.assertEqual(runner.literal_expected("ABSENT"), b"\x00")
        self.assertEqual(runner.literal_expected("REJECT"), b"\x01")
        self.assertEqual(runner.literal_expected("P0"), b"\x02\x00\x00\x00\x00")
        self.assertEqual(
            runner.literal_expected("P1"), b"\x02\x00\x00\x00\x01\x00"
        )

    def test_bundle_manifest_independent_construction(self) -> None:
        entries = []
        for name in sorted(r0_record.BUNDLE_NAMES, key=lambda item: item.encode("utf-8")):
            name_bytes = name.encode("utf-8")
            contents = (BASE / name).read_bytes()
            entries.append(
                struct.pack(">I", len(name_bytes)) + name_bytes
                + struct.pack(">Q", len(contents)) + contents
            )
        manual = b"".join(entries)
        self.assertEqual(manual, r0_record.canonical_bundle_manifest(BASE))
        self.assertEqual(hashlib.sha256(manual).digest(), self.a)

    def test_suite_digest_independent_construction(self) -> None:
        def lp(value: bytes) -> bytes:
            return struct.pack(">I", len(value)) + value

        manual = hashlib.sha256(
            b"ZERO-GROUND-R0-SUITE\x00"
            + self.q
            + self.a
            + lp(b"")
            + lp(b"\x00")
            + lp(b"")
            + lp(b"")
            + lp(b"\x00")
        ).digest()
        self.assertEqual(manual, self.d)

    def test_exact_records_and_round_trip(self) -> None:
        for payload, size in ((r0_adapter.P0, 64), (r0_adapter.P1, 65)):
            record = r0_record.encode_record(self.d, payload)
            self.assertEqual(len(record), size)
            manual_hash = hashlib.sha256(
                b"ZERO-GROUND-R0-RECORD\x00"
                + self.d
                + struct.pack(">Q", len(payload))
                + payload
            ).digest()
            self.assertEqual(record, self.d + payload + manual_hash)
            self.assertEqual(r0_record.parse_record(record, self.d), payload)

    def test_all_prefixes_and_single_bits_reject_in_parser(self) -> None:
        for payload in (r0_adapter.P0, r0_adapter.P1):
            record = r0_record.encode_record(self.d, payload)
            for length in range(len(record)):
                with self.assertRaises(r0_record.RecordReject):
                    r0_record.parse_record(record[:length], self.d)
            for index in range(len(record)):
                for bit in range(8):
                    changed = bytearray(record)
                    changed[index] ^= 1 << bit
                    with self.assertRaises(r0_record.RecordReject):
                        r0_record.parse_record(bytes(changed), self.d)

    def test_wrong_suite_coherent_hash_rejects(self) -> None:
        wrong = bytes([self.d[0] ^ 0x80]) + self.d[1:]
        record = r0_record.encode_record(wrong, r0_adapter.P1)
        with self.assertRaises(r0_record.RecordReject):
            r0_record.parse_record(record, self.d)

    def test_component_deletion_finds_smaller_candidate_and_collision(self) -> None:
        experiment = runner.Experiment(self.q, self.a, self.d, {})
        findings = runner.evaluate_component_deletions(experiment)
        no_digest = findings["in_band_suite_digest"]
        self.assertEqual(no_digest["failures"], [])
        self.assertEqual(no_digest["candidate_record_sizes"], {"P0": 32, "P1": 33})
        witness = findings["integrity_comparison_value"]["minimal_witness"]
        self.assertNotEqual(witness["required_hex"], witness["observed_hex"])

    def test_common_mode_mutations_are_caught(self) -> None:
        experiment = runner.Experiment(self.q, self.a, self.d, {})
        runner.run_common_mode_controls(experiment)
        self.assertTrue(experiment.common_mode["table_mutation"]["checker_caught"])
        self.assertTrue(
            experiment.common_mode["ignore_hash_parser_mutation"]["checker_caught"]
        )


class R0ProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.q, cls.a, cls.d = r0_record.derive_digests(BASE)
        cls.backend_info = {
            symbol: runner.validate_backend(symbol) for symbol in ("E", "T")
        }
        cls.publication = runner.Experiment(
            cls.q, cls.a, cls.d, cls.backend_info
        )
        runner.run_publication_matrix(
            cls.publication, ("E", "T"), 1,
            category="conformance", variant="candidate",
        )

    def test_declared_backends_are_distinct_guest_filesystems(self) -> None:
        self.assertEqual(self.backend_info["E"]["filesystem"], "ext4")
        self.assertEqual(self.backend_info["T"]["filesystem"], "tmpfs")
        self.assertNotEqual(
            self.backend_info["E"]["statfs_magic_hex"],
            self.backend_info["T"]["statfs_magic_hex"],
        )
        self.assertEqual(
            self.backend_info["E"]["physical_substrate"]["status"], "UNKNOWN"
        )

    def test_every_cut_case_backend_row_passes_in_fresh_processes(self) -> None:
        self.assertEqual(len(self.publication.results), 28)
        self.assertTrue(all(result.passed for result in self.publication.results))
        terminals = {result.fields["publisher_terminal"] for result in self.publication.results}
        self.assertEqual(terminals, {b"SIGKILL", b"EXIT0"})

    def test_cross_backend_semantic_projection_matches(self) -> None:
        comparison = runner._semantic_cross_backend(self.publication)
        self.assertEqual(comparison["status"], "PASS")
        self.assertEqual(comparison["comparable_trials"], 14)

    def test_fresh_recovery_rejects_symlink(self) -> None:
        base = runner.BACKENDS["E"]["base"]
        self.assertIsInstance(base, Path)
        record = r0_record.encode_record(self.d, r0_adapter.P0)
        with runner.fresh_directory(base) as directory:
            runner.install_state(directory, record, "target.bin")
            os.symlink("target.bin", directory / r0_record.STATE_NAME)
            outcome = runner.run_recovery(directory, self.d, r0_adapter.C)
        self.assertEqual(outcome.returncode, 0)
        self.assertEqual(outcome.stderr, b"")
        self.assertEqual(outcome.observation, runner.literal_expected("REJECT"))

    def test_fresh_worker_rejects_bundle_digest_mismatch(self) -> None:
        base = runner.BACKENDS["T"]["base"]
        self.assertIsInstance(base, Path)
        wrong = bytes([self.d[0] ^ 0x80]) + self.d[1:]
        with runner.fresh_directory(base) as directory:
            outcome = runner.run_recovery(directory, wrong, r0_adapter.C)
        self.assertEqual(outcome.returncode, 0)
        self.assertEqual(outcome.stderr, b"")
        self.assertEqual(outcome.observation, runner.literal_expected("REJECT"))

    def test_simulated_short_write_and_errors(self) -> None:
        experiment = runner.Experiment(
            self.q, self.a, self.d, {"E": self.backend_info["E"]}
        )
        runner.run_io_fault_matrix(experiment, ("E",))
        self.assertEqual(len(experiment.results), 18)
        self.assertTrue(all(result.passed for result in experiment.results))
        self.assertTrue(any("directory_fsync" in item.trial_id for item in experiment.results))

    def test_mechanism_deletion_witnesses_replace_only(self) -> None:
        experiment = runner.Experiment(
            self.q, self.a, self.d, {"E": self.backend_info["E"]}
        )
        runner.run_mechanism_deletions(experiment, ("E",))
        self.assertEqual(
            experiment.deletion_findings["delete-file-fsync"]["verdict"],
            "NO_WITNESS_IN_R0",
        )
        self.assertEqual(
            experiment.deletion_findings["delete-directory-fsync"]["verdict"],
            "NO_WITNESS_IN_R0",
        )
        self.assertEqual(
            experiment.deletion_findings["delete-exclusive-creation"]["verdict"],
            "NO_WITNESS_IN_R0",
        )
        self.assertEqual(
            experiment.deletion_findings["delete-replace"]["verdict"],
            "WITNESSED_REQUIRED_WITHIN_R0",
        )

    def test_all_dimension_names_are_present(self) -> None:
        experiment = self.publication
        experiment.deletion_findings.update(runner.evaluate_component_deletions(experiment))
        runner.run_common_mode_controls(experiment)
        inventory = runner._source_inventory()
        dimensions = runner._dimension_ledger(experiment, inventory)
        self.assertEqual(set(dimensions), {
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
        })


if __name__ == "__main__":
    unittest.main()
