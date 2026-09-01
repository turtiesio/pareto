"""Repeatable microbenchmark for the Round 0001 experimental apparatus."""

from __future__ import annotations

import argparse
import json
import resource
import time

from model.round0001 import AcquisitionTranscript, ArtifactOnlyArchive


def fixed_bytes(prefix: bytes, value: int, length: int) -> bytes:
    seed = prefix + value.to_bytes(8, "big")
    return (seed * ((length + len(seed) - 1) // len(seed)))[:length]


def run(count: int, payload_size: int, context_size: int, unique_ratio: float) -> dict:
    unique_payloads = max(1, int(count * unique_ratio))

    artifact_only = ArtifactOnlyArchive()
    start = time.perf_counter()
    for index in range(count):
        artifact_only.retain(
            fixed_bytes(b"p", index % unique_payloads, payload_size)
        )
    artifact_only_ingest = time.perf_counter() - start

    transcript = AcquisitionTranscript()
    start = time.perf_counter()
    for index in range(count):
        transcript.capture(
            occurrence=index.to_bytes(8, "big"),
            payload=fixed_bytes(b"p", index % unique_payloads, payload_size),
            acquisition=fixed_bytes(b"c", index, context_size),
        )
    transcript_ingest = time.perf_counter() - start

    start = time.perf_counter()
    transcript.verify()
    verify = time.perf_counter() - start

    start = time.perf_counter()
    encoded = transcript.export()
    export = time.perf_counter() - start

    start = time.perf_counter()
    restored = AcquisitionTranscript.load(encoded)
    load = time.perf_counter() - start
    restored.verify()

    artifact_bytes = sum(len(data) for data in transcript.artifacts.values())
    artifact_only_bytes = sum(len(data) for data in artifact_only.artifacts.values())
    return {
        "measurement": "single-process Python 3 wall clock; experimental JSON encoding",
        "captures": count,
        "payload_bytes_each": payload_size,
        "acquisition_bytes_each": context_size,
        "unique_payload_ratio": unique_ratio,
        "artifact_only": {
            "retained_occurrences": 0,
            "unique_artifacts": len(artifact_only.artifacts),
            "artifact_bytes": artifact_only_bytes,
            "ingest_seconds": artifact_only_ingest,
        },
        "transcript": {
            "retained_occurrences": len(transcript.captures),
            "unique_artifacts": len(transcript.artifacts),
            "artifact_bytes": artifact_bytes,
            "encoded_bytes": len(encoded),
            "ingest_seconds": transcript_ingest,
            "verify_seconds": verify,
            "export_seconds": export,
            "load_seconds": load,
            "max_rss_kib_process": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int)
    parser.add_argument("--payload-size", type=int, default=256)
    parser.add_argument("--context-size", type=int, default=64)
    parser.add_argument("--unique-ratio", type=float, default=0.1)
    arguments = parser.parse_args()
    print(
        json.dumps(
            run(
                arguments.count,
                arguments.payload_size,
                arguments.context_size,
                arguments.unique_ratio,
            ),
            sort_keys=True,
        )
    )

