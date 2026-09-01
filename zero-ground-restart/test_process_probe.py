"""Focused framing and committed-evidence tests for c0_process_probe."""

from __future__ import annotations

from io import BytesIO
import hashlib
import json
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from c0_candidates import OrdinalEncoding, RepresentativeEncoding
from c0_process_probe import (
    CANDIDATE_TAGS,
    ENVELOPE_HEADER,
    FORMAT_VERSION,
    ORDINAL,
    REPRESENTATIVE,
    STREAM_HEADER,
    STREAM_MAGIC,
    _pack_envelope,
    _read_envelope,
    _read_stream_header,
    decode_envelope,
    deserialize_encoding,
    serialize_encoding,
)


DIGEST_HEX = "01" * 32
DIGEST_BYTES = bytes.fromhex(DIGEST_HEX)


class EnvelopeTests(unittest.TestCase):
    def test_ordinal_envelope_is_exact_and_non_pickle(self) -> None:
        raw = serialize_encoding(ORDINAL, OrdinalEncoding(DIGEST_HEX, 0x12345))
        name, digest, payload = decode_envelope(raw, expected_candidate=ORDINAL)
        self.assertEqual(name, ORDINAL)
        self.assertEqual(digest, DIGEST_BYTES)
        self.assertEqual(payload, b"\x01\x23\x45")
        self.assertNotIn(b"pickle", raw.lower())
        self.assertEqual(
            deserialize_encoding(ORDINAL, raw),
            OrdinalEncoding(DIGEST_HEX, 0x12345),
        )

    def test_empty_representative_payload_is_canonical_framing(self) -> None:
        raw = serialize_encoding(
            REPRESENTATIVE, RepresentativeEncoding(DIGEST_HEX, b"")
        )
        name, digest, payload = decode_envelope(
            raw, expected_candidate=REPRESENTATIVE
        )
        self.assertEqual((name, digest, payload), (REPRESENTATIVE, DIGEST_BYTES, b""))

    def test_wrong_tag_truncation_and_trailing_bytes_are_rejected(self) -> None:
        raw = serialize_encoding(ORDINAL, OrdinalEncoding(DIGEST_HEX, 0))
        with self.assertRaisesRegex(ValueError, "candidate tag"):
            decode_envelope(raw, expected_candidate=REPRESENTATIVE)
        for length in range(len(raw)):
            with self.subTest(length=length):
                with self.assertRaises(ValueError):
                    decode_envelope(raw[:length])
        with self.assertRaisesRegex(ValueError, "trailing"):
            decode_envelope(raw + b"x")

    def test_ordinal_payload_width_is_fixed(self) -> None:
        for length in (0, 1, 2, 4):
            with self.subTest(length=length):
                raw = _pack_envelope(ORDINAL, DIGEST_BYTES, b"\0" * length)
                with self.assertRaisesRegex(ValueError, "three bytes"):
                    decode_envelope(raw, expected_candidate=ORDINAL)

    def test_internal_digest_spelling_is_lowercase_exact(self) -> None:
        with self.assertRaisesRegex(ValueError, "lowercase hexadecimal"):
            serialize_encoding(ORDINAL, OrdinalEncoding(("ab" * 32).upper(), 0))
        with self.assertRaisesRegex(ValueError, "lowercase hexadecimal"):
            serialize_encoding(ORDINAL, OrdinalEncoding("0" * 63, 0))

    def test_stream_header_and_exact_envelope_boundaries(self) -> None:
        envelope = serialize_encoding(ORDINAL, OrdinalEncoding(DIGEST_HEX, 7))
        raw = (
            STREAM_HEADER.pack(
                STREAM_MAGIC,
                FORMAT_VERSION,
                CANDIDATE_TAGS[ORDINAL],
                1,
            )
            + envelope
        )
        stream = BytesIO(raw)
        self.assertEqual(_read_stream_header(stream, ORDINAL), 1)
        self.assertEqual(_read_envelope(stream, ORDINAL), envelope)
        self.assertEqual(stream.read(1), b"")


class CommittedEvidenceTests(unittest.TestCase):
    def test_process_restore_b3_evidence_is_self_consistent(self) -> None:
        path = HERE / "PROCESS-RESTORE-B3.json"
        if not path.exists():
            self.skipTest("B3 process evidence has not been frozen yet")
        evidence = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["schema"], "zero-ground-process-restore-b3-v1")
        probe_hash = hashlib.sha256((HERE / "c0_process_probe.py").read_bytes()).hexdigest()
        self.assertEqual(evidence["process_probe_sha256"], probe_hash)
        b2_hash = hashlib.sha256((HERE / "EVIDENCE-B2.json").read_bytes()).hexdigest()
        self.assertEqual(evidence["b2_evidence_sha256_before_probe"], b2_hash)
        limitations = "\n".join(evidence["isolation_ledger"]["not_enforced"])
        self.assertIn("not state-payload integrity", limitations)
        self.assertIn("no mount namespace", limitations)
        self.assertIn("no unlike runtime", limitations)
        for candidate_name in (ORDINAL, REPRESENTATIVE):
            result = evidence["candidates"][candidate_name]
            checks = result["checks"]
            self.assertTrue(checks["producer_matches_expected_stream"])
            self.assertEqual(checks["consumer_runs_match_expected"], [True, True])
            self.assertTrue(checks["consumer_runs_identical"])
            self.assertTrue(checks["transition_chunk_counts_identical"])
            self.assertEqual(checks["transition_chunk_counts"], [323, 323, 323])
            self.assertEqual(checks["transition_chunk_mismatch_count"], 0)
            self.assertEqual(result["consumer_run_1"]["state_records"], 82584)
            self.assertEqual(result["consumer_run_1"]["transition_records"], 1403928)
            expected = result["expected_raw_oracle"]
            for consumer_name in ("consumer_run_1", "consumer_run_2"):
                consumer = result[consumer_name]
                self.assertEqual(consumer["state_stream_sha256"], expected["state_stream_sha256"])
                self.assertEqual(consumer["transition_sha256"], expected["transition_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
