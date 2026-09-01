"""Pure/static tests for the byte-authorized R0.1B Python subset.

These tests intentionally launch no publisher, recovery process, controller,
or filesystem trial.  Gate R cannot be closed from the frozen profile because
its manifest/ID encoding is unspecified, so process-level conformance tests
would be premature.
"""

from __future__ import annotations

import hashlib
import unittest
from unittest import mock

import r01b_runner as runner
import r01b_subject as subject


# Independently copied from the frozen S1 record_by_payload table.
P0_RECORD_HEX = (
    "996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a6"
    "4853649d24acf49ef566702f884ed0d4c8e6d74c9cfeb64e1ba76dfe3a3c0196"
)
P1_RECORD_HEX = (
    "996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a6"
    "00"
    "fa75a2cd3940cbf598707da3d715930c7c71121fc2858fdef84aef0dd5ff318b"
)


class RecordVectorTests(unittest.TestCase):
    def test_exact_s1_record_vectors(self) -> None:
        self.assertEqual(
            subject.encode_record(subject.SEMANTIC_SUITE_DIGEST, b"").hex(),
            P0_RECORD_HEX,
        )
        self.assertEqual(
            subject.encode_record(subject.SEMANTIC_SUITE_DIGEST, b"\x00").hex(),
            P1_RECORD_HEX,
        )

    def test_r01b_tag_is_not_the_historical_r0_tag(self) -> None:
        digest = subject.SEMANTIC_SUITE_DIGEST
        payload = b""
        r01b = hashlib.sha256(
            b"ZERO-GROUND-R01B-RECORD\x00"
            + digest
            + len(payload).to_bytes(8, "big")
            + payload
        ).digest()
        r0 = hashlib.sha256(
            b"ZERO-GROUND-R0-RECORD\x00"
            + digest
            + len(payload).to_bytes(8, "big")
            + payload
        ).digest()
        self.assertEqual(subject.record_hash(digest, payload), r01b)
        self.assertNotEqual(r01b, r0)

    def test_valid_records_recover_to_the_two_exact_ok_wires(self) -> None:
        self.assertEqual(
            subject.recover_record_bytes(bytes.fromhex(P0_RECORD_HEX)),
            bytes.fromhex("0200000000"),
        )
        self.assertEqual(
            subject.recover_record_bytes(bytes.fromhex(P1_RECORD_HEX)),
            bytes.fromhex("020000000100"),
        )

    def test_absent_and_every_proper_prefix_have_exact_results(self) -> None:
        self.assertEqual(subject.recover_record_bytes(None), b"\x00")
        for record_hex in (P0_RECORD_HEX, P1_RECORD_HEX):
            record = bytes.fromhex(record_hex)
            for length in range(len(record)):
                with self.subTest(record_length=len(record), prefix=length):
                    self.assertEqual(
                        subject.recover_record_bytes(record[:length]), b"\x01"
                    )

    def test_every_single_bit_flip_and_append_zero_reject(self) -> None:
        for record_hex in (P0_RECORD_HEX, P1_RECORD_HEX):
            record = bytes.fromhex(record_hex)
            for index in range(len(record)):
                for bit in range(8):
                    mutated = bytearray(record)
                    mutated[index] ^= 1 << bit
                    with self.subTest(
                        record_length=len(record), index=index, bit=bit
                    ):
                        self.assertEqual(
                            subject.recover_record_bytes(bytes(mutated)), b"\x01"
                        )
            self.assertEqual(subject.recover_record_bytes(record + b"\x00"), b"\x01")

    def test_wrong_suite_rehash_rejects_but_coherent_other_valid_accepts(self) -> None:
        p0 = bytes.fromhex(P0_RECORD_HEX)
        wrong_digest = bytes((p0[0] ^ 0x80,)) + p0[1:32]
        wrong = subject.encode_record(wrong_digest, b"")
        self.assertEqual(subject.recover_record_bytes(wrong), b"\x01")
        self.assertEqual(
            subject.recover_record_bytes(bytes.fromhex(P1_RECORD_HEX)),
            bytes.fromhex("020000000100"),
        )

    def test_unknown_payload_or_continuation_rejects(self) -> None:
        unknown_payload_record = subject.encode_record(
            subject.SEMANTIC_SUITE_DIGEST, b"x"
        )
        self.assertEqual(subject.recover_record_bytes(unknown_payload_record), b"\x01")
        self.assertEqual(
            subject.recover_record_bytes(
                bytes.fromhex(P0_RECORD_HEX), continuation=b"x"
            ),
            b"\x01",
        )


class ResultWireTests(unittest.TestCase):
    def test_exact_publisher_result_vectors(self) -> None:
        vectors = (
            (subject.PUBLISH_COMPLETE, ("COMPLETE", None, None, None)),
            (
                bytes.fromhex("11010000000011"),
                ("ERROR", 1, 0, 17),
            ),
            (
                bytes.fromhex("11030100000005"),
                ("ERROR", 3, 1, 5),
            ),
            (
                bytes.fromhex("11040100000005"),
                ("ERROR", 4, 1, 5),
            ),
            (
                bytes.fromhex("11050100000005"),
                ("ERROR", 5, 1, 5),
            ),
        )
        for encoded, expected in vectors:
            with self.subTest(encoded=encoded.hex()):
                self.assertEqual(subject.parse_publish_result(encoded), expected)
        self.assertEqual(
            subject.publish_error(1, subject.SOURCE_KERNEL, 17),
            bytes.fromhex("11010000000011"),
        )
        self.assertEqual(
            subject.publish_error(5, subject.SOURCE_SIMULATED_WRAPPER, 5),
            bytes.fromhex("11050100000005"),
        )

    def test_exact_recovery_wires_parse_strictly(self) -> None:
        vectors = (
            ("00", ("ABSENT", None)),
            ("01", ("REJECT", None)),
            ("0200000000", ("OK", b"")),
            ("020000000100", ("OK", b"\x00")),
        )
        for encoded_hex, expected in vectors:
            self.assertEqual(
                subject.parse_recovery_observation(bytes.fromhex(encoded_hex)),
                expected,
            )
        for malformed in (b"", b"\x02", b"\x02\x00\x00\x00\x01"):
            with self.assertRaises(subject.R01BSubjectError):
                subject.parse_recovery_observation(malformed)


class MockedPublicationProgramTests(unittest.TestCase):
    """Exercise slot/deletion logic without a process or filesystem trial."""

    def _run(
        self,
        mechanism: str,
        fault: str = "NONE",
        *,
        open_effect: object = None,
    ) -> tuple[bytes, list[int], dict[str, mock.Mock]]:
        checkpoints: list[int] = []
        if open_effect is None:
            open_effect = [10, 11]
        calls: dict[str, mock.Mock] = {}
        with (
            mock.patch.object(subject.os, "open", side_effect=open_effect) as opened,
            mock.patch.object(
                subject.os, "write", side_effect=lambda _fd, value: len(value)
            ) as written,
            mock.patch.object(subject.os, "fsync") as fsynced,
            mock.patch.object(subject.os, "close") as closed,
            mock.patch.object(subject.os, "replace") as replaced,
        ):
            result = subject.publish_directory(
                "/not-accessed",
                subject.P0,
                mechanism,
                fault,
                checkpoints.append,
            )
            calls.update(
                open=opened,
                write=written,
                fsync=fsynced,
                close=closed,
                replace=replaced,
            )
        return result, checkpoints, calls

    def test_reference_performs_both_stabilizations_and_selection(self) -> None:
        result, checkpoints, calls = self._run("REFERENCE")
        self.assertEqual(result, subject.PUBLISH_COMPLETE)
        self.assertEqual(checkpoints, [0, 1, 2, 3, 4, 5])
        self.assertEqual(calls["fsync"].call_args_list, [mock.call(10), mock.call(11)])
        calls["replace"].assert_called_once()

    def test_each_mechanism_deletion_omits_only_its_selected_operation(self) -> None:
        result, checkpoints, calls = self._run("NO_FILE_FSYNC")
        self.assertEqual((result, checkpoints), (subject.PUBLISH_COMPLETE, [0, 1, 2, 3, 4, 5]))
        self.assertEqual(calls["fsync"].call_args_list, [mock.call(11)])

        result, checkpoints, calls = self._run("NO_DIRECTORY_FSYNC")
        self.assertEqual((result, checkpoints), (subject.PUBLISH_COMPLETE, [0, 1, 2, 3, 4, 5]))
        self.assertEqual(calls["fsync"].call_args_list, [mock.call(10)])
        self.assertEqual(calls["open"].call_count, 1)

        result, checkpoints, calls = self._run("NO_REPLACE")
        self.assertEqual((result, checkpoints), (subject.PUBLISH_COMPLETE, [0, 1, 2, 3, 4, 5]))
        calls["replace"].assert_not_called()

        result, checkpoints, calls = self._run("NO_EXCLUSIVE_CREATE")
        self.assertEqual((result, checkpoints), (subject.PUBLISH_COMPLETE, [0, 1, 2, 3, 4, 5]))
        staging_flags = calls["open"].call_args_list[0].args[1]
        self.assertTrue(staging_flags & subject.os.O_TRUNC)
        self.assertFalse(staging_flags & subject.os.O_EXCL)

    def test_simulated_errors_stop_at_the_declared_slot_without_kernel_entry(self) -> None:
        cases = (
            ("FILE_FSYNC_EIO", "11030100000005", [0, 1, 2]),
            ("REPLACE_EIO", "11040100000005", [0, 1, 2, 3]),
            ("DIRECTORY_FSYNC_EIO", "11050100000005", [0, 1, 2, 3, 4]),
        )
        for fault, result_hex, expected_checkpoints in cases:
            with self.subTest(fault=fault):
                result, checkpoints, _ = self._run("REFERENCE", fault)
                self.assertEqual(result, bytes.fromhex(result_hex))
                self.assertEqual(checkpoints, expected_checkpoints)

    def test_occupied_staging_kernel_eexist_is_the_exact_B_result(self) -> None:
        result, checkpoints, calls = self._run(
            "REFERENCE", open_effect=FileExistsError(17, "exists")
        )
        self.assertEqual(result, bytes.fromhex("11010000000011"))
        self.assertEqual(checkpoints, [0])
        calls["write"].assert_not_called()


class NeutralFrameTests(unittest.TestCase):
    def test_exact_forty_byte_vector(self) -> None:
        digest = bytes(range(32))
        expected = bytes.fromhex(
            "5a474e4601"  # ZGNF, version 1
            "02"          # J2
            "02"          # omitted mechanism
            "03"          # NO_ACK_REQUIRED | SELF_CUT_TARGET
            "000102030405060708090a0b0c0d0e0f"
            "101112131415161718191a1b1c1d1e1f"
        )
        encoded = subject.encode_neutral_frame(
            digest,
            "J2",
            subject.MECHANISM_OMITTED,
            subject.NO_ACK_REQUIRED | subject.SELF_CUT_TARGET,
        )
        self.assertEqual(encoded, expected)
        self.assertEqual(
            subject.decode_neutral_frame(encoded),
            subject.NeutralFrame(2, 2, 3, digest),
        )

    def test_frame_rejects_bad_length_header_coordinates_and_flags(self) -> None:
        valid = subject.encode_neutral_frame(bytes(32), "J0", 0, 0)
        malformed = (
            valid[:-1],
            b"X" + valid[1:],
            valid[:5] + b"\x06" + valid[6:],
            valid[:6] + b"\x05" + valid[7:],
            valid[:7] + b"\x04" + valid[8:],
        )
        for value in malformed:
            with self.subTest(value=value.hex()):
                with self.assertRaises(subject.ControlProtocolError):
                    subject.decode_neutral_frame(value)

    def test_encoder_requires_explicit_mm_and_does_not_derive_a_plan(self) -> None:
        with self.assertRaises(ValueError):
            subject.encode_neutral_frame(bytes(32), "J0", None, 0)  # type: ignore[arg-type]
        self.assertFalse(hasattr(subject, "descriptor_frame_plan"))


class FrozenRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = runner.SemanticRegistry()

    def test_all_3028_subject_rows_load_and_rederive_trial_ids(self) -> None:
        self.assertEqual(len(self.registry.rows), 6318)
        self.assertEqual(len(self.registry.subject_rows), 3028)
        self.assertEqual(
            sum(r.history_production == "PUBLICATION" for r in self.registry.subject_rows),
            684,
        )
        self.assertEqual(
            sum(r.history_production == "RECOVERY_ONLY" for r in self.registry.subject_rows),
            2344,
        )

    def test_every_literal_subject_result_is_a_strict_wire_value(self) -> None:
        no_history = 0
        for row in self.registry.subject_rows:
            literal = self.registry.literal_b_expectation(row.case_id)
            if literal.kind == "NO_B_HISTORY":
                no_history += 1
            else:
                for result in literal.publish_results:
                    subject.parse_publish_result(result)
                subject.parse_recovery_observation(literal.recovery_observation)
        self.assertEqual(no_history, 24)

    def test_all_2344_recovery_fixture_values_match_literal_oracle(self) -> None:
        self.assertEqual(runner.validate_recovery_literals(self.registry), 2344)

    def test_no_b_history_and_exact_comparisons_are_distinct(self) -> None:
        no_history_row = next(
            row
            for row in self.registry.subject_rows
            if self.registry.literal_b_expectation(row.case_id).kind == "NO_B_HISTORY"
        )
        expected = self.registry.literal_b_expectation(no_history_row.case_id)
        self.assertTrue(
            runner.compare_literal_b(
                expected,
                runner.ObservedBResponse("PUBLICATION", (), None, False),
            )
        )
        self.assertFalse(
            runner.compare_literal_b(
                expected,
                runner.ObservedBResponse("PUBLICATION", (), b"\x00", True),
            )
        )

    def test_preflight_preserves_unknown_and_execute_fails_closed(self) -> None:
        report = runner.preflight_report(self.registry)
        self.assertEqual(report["execution"], "NOT_RUN")
        self.assertEqual(report["full_conformance"], "UNKNOWN")
        self.assertEqual(len(report["limitations"]), 3)
        with self.assertRaises(runner.ExecutionAuthorityError):
            runner.require_execution_authority()


if __name__ == "__main__":
    unittest.main()
