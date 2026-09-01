import json
import unittest

from model.round0001 import (
    AcquisitionTranscript,
    ArchiveError,
    ArtifactOnlyArchive,
    normalized_json,
)


class Round0001Tests(unittest.TestCase):
    def test_exact_arbitrary_bytes_survive(self) -> None:
        transcript = AcquisitionTranscript()
        values = [b"", b"\x00\xff\x80", "é".encode(), b"future\x00format"]
        records = [
            transcript.capture(f"c{i}".encode(), value, None)
            for i, value in enumerate(values)
        ]
        self.assertEqual(values, [transcript.read(record.payload) for record in records])

    def test_content_only_collapses_occurrences(self) -> None:
        archive = ArtifactOnlyArchive()
        archive.retain(b"same webhook")
        archive.retain(b"same webhook")
        self.assertEqual(1, len(archive.artifacts))

        transcript = AcquisitionTranscript()
        transcript.capture(b"delivery-1", b"same webhook", b"provider channel")
        transcript.capture(b"delivery-2", b"same webhook", b"local replay")
        self.assertEqual(2, len(transcript.captures))
        self.assertEqual(transcript.captures[0].payload, transcript.captures[1].payload)
        self.assertNotEqual(
            transcript.captures[0].acquisition,
            transcript.captures[1].acquisition,
        )

    def test_absent_and_empty_acquisition_do_not_collapse(self) -> None:
        transcript = AcquisitionTranscript()
        missing = transcript.capture(b"missing", b"p", None)
        empty = transcript.capture(b"empty", b"p", b"")
        self.assertIsNone(missing.acquisition)
        self.assertIsNotNone(empty.acquisition)
        self.assertEqual(b"", transcript.read(empty.acquisition))

    def test_normalized_json_loses_future_relevant_syntax(self) -> None:
        compact = b'{"amount":1}'
        spaced = b'{ "amount" : 1 }'
        self.assertEqual(normalized_json(compact), normalized_json(spaced))

        transcript = AcquisitionTranscript()
        a = transcript.capture(b"a", compact, None)
        b = transcript.capture(b"b", spaced, None)
        self.assertNotEqual(a.payload, b.payload)

    def test_normalized_json_loses_duplicate_key_occurrence(self) -> None:
        duplicate = b'{"status":"pending","status":"paid"}'
        single = b'{"status":"paid"}'
        self.assertEqual(normalized_json(duplicate), normalized_json(single))

        transcript = AcquisitionTranscript()
        a = transcript.capture(b"duplicate", duplicate, None)
        b = transcript.capture(b"single", single, None)
        self.assertNotEqual(a.payload, b.payload)

    def test_unknown_structure_is_preserved_without_validation(self) -> None:
        payload = b'{"future-field":{"unpublished-format":"?"},"x":1,"x":2}'
        acquisition = b"\x99unknown-capture-context\x00"
        transcript = AcquisitionTranscript()
        record = transcript.capture(b"unknown-1", payload, acquisition)
        self.assertEqual(payload, transcript.read(record.payload))
        self.assertEqual(acquisition, transcript.read(record.acquisition))

    def test_duplicate_occurrence_address_is_rejected(self) -> None:
        transcript = AcquisitionTranscript()
        transcript.capture(b"same-id", b"first", None)
        with self.assertRaises(ArchiveError):
            transcript.capture(b"same-id", b"second", None)

    def test_deterministic_export_round_trip(self) -> None:
        transcript = AcquisitionTranscript()
        transcript.capture(b"one", b"\xffpayload", b"source-a")
        transcript.capture(b"two", b"\xffpayload", b"")
        encoded = transcript.export()
        restored = AcquisitionTranscript.load(encoded)
        self.assertEqual(encoded, restored.export())
        self.assertEqual(transcript.captures, restored.captures)
        self.assertEqual(transcript.artifacts, restored.artifacts)

    def test_export_tampering_is_detected(self) -> None:
        transcript = AcquisitionTranscript()
        transcript.capture(b"one", b"payload", None)
        document = json.loads(transcript.export())
        document["artifacts"][0]["data"] = "dGFtcGVyZWQ="
        tampered = json.dumps(document, separators=(",", ":")).encode()
        with self.assertRaises(ArchiveError):
            AcquisitionTranscript.load(tampered)

    def test_transcript_schema_does_not_silently_accept_unknown_field(self) -> None:
        transcript = AcquisitionTranscript()
        transcript.capture(b"one", b"payload", None)
        document = json.loads(transcript.export())
        document["future"] = {"meaning": "not fabricated"}
        extended = json.dumps(document, separators=(",", ":")).encode()
        with self.assertRaises(ArchiveError):
            AcquisitionTranscript.load(extended)


if __name__ == "__main__":
    unittest.main()

