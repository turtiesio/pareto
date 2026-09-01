#!/usr/bin/env python3
"""Fresh-process persistence probe for the finite B1 laboratory contract.

This file is deliberately absent from ``c0_candidates.SPECIFICATION_FILES``.
It tests the existing artifact without changing the artifact it tests.

The probe has three roles:

* ``produce`` rebuilds the artifact, calls a candidate's public ``persist``
  method for every canonical boundary-phase snapshot, writes canonical binary
  envelopes, and exits.
* ``consume`` starts separately with only the declared source bundle, this
  probe, and one candidate's state stream.  It rebuilds the artifact, calls the
  public ``recover`` method, evaluates ``resume`` and every frozen proposal,
  and hashes exact outputs plus the next canonical persisted envelope.
* ``orchestrate`` runs one producer followed by two consumers in distinct clean
  directories for each candidate, and independently computes the same digest
  through the raw oracle.

Domain membership is a proof projection: ``enabled`` means that a proposed
input belongs to the state's legal-next domain and ``disabled`` means it does
not.  ``resume`` has no domain-membership value.  None of these proof markers
is treated as a physical boundary output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from typing import BinaryIO, Iterable, Iterator, Mapping, Sequence


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    # ``-I -S`` intentionally removes the script directory.  The probe adds
    # back exactly the copied bundle containing this file.
    sys.path.insert(0, str(HERE))


SPECIFICATION_NAMES = (
    "CONTRACT-B1.md",
    "c0_oracle.py",
    "c0_experiment.py",
    "c0_candidates.py",
)
PROBE_NAME = "c0_process_probe.py"
BUNDLE_NAMES = (*SPECIFICATION_NAMES, PROBE_NAME)

ENVELOPE_MAGIC = b"ZGPE"
STREAM_MAGIC = b"ZGPS"
TRANSITION_MAGIC = b"ZGTR"
FORMAT_VERSION = 1
ORDINAL_PAYLOAD_BYTES = 3
MAX_REPRESENTATIVE_PAYLOAD = 1 << 20
CHUNK_STATES = 256

ORDINAL = "ordinal"
REPRESENTATIVE = "representative"
CANDIDATE_TAGS = {ORDINAL: 1, REPRESENTATIVE: 2}
TAG_CANDIDATES = {value: key for key, value in CANDIDATE_TAGS.items()}

ENVELOPE_HEADER = struct.Struct(">4sBB32sI")
STREAM_HEADER = struct.Struct(">4sBBI")
U32 = struct.Struct(">I")
HEX_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1 << 20)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _print_json(value: object) -> None:
    sys.stdout.write(_canonical_json(value) + "\n")


def _candidate_name(value: str) -> str:
    if value not in CANDIDATE_TAGS:
        raise ValueError(f"unknown candidate: {value}")
    return value


def _digest_bytes(digest: str) -> bytes:
    if HEX_DIGEST.fullmatch(digest) is None:
        raise ValueError("specification digest must be 64 lowercase hexadecimal characters")
    return bytes.fromhex(digest)


def _pack_envelope(candidate_name: str, digest: bytes, payload: bytes) -> bytes:
    candidate_name = _candidate_name(candidate_name)
    if len(digest) != 32:
        raise ValueError("raw specification digest must contain exactly 32 bytes")
    if len(payload) > MAX_REPRESENTATIVE_PAYLOAD:
        raise ValueError("envelope payload exceeds the probe bound")
    return ENVELOPE_HEADER.pack(
        ENVELOPE_MAGIC,
        FORMAT_VERSION,
        CANDIDATE_TAGS[candidate_name],
        digest,
        len(payload),
    ) + payload


def serialize_encoding(candidate_name: str, encoding: object) -> bytes:
    """Serialize one public candidate encoding without pickle."""

    from c0_candidates import OrdinalEncoding, RepresentativeEncoding

    candidate_name = _candidate_name(candidate_name)
    if candidate_name == ORDINAL:
        if not isinstance(encoding, OrdinalEncoding):
            raise TypeError("ordinal envelope requires OrdinalEncoding")
        if encoding.rank < 0 or encoding.rank >= 1 << (8 * ORDINAL_PAYLOAD_BYTES):
            raise ValueError("ordinal cannot be represented in three bytes")
        payload = encoding.rank.to_bytes(ORDINAL_PAYLOAD_BYTES, "big")
        digest = _digest_bytes(encoding.specification_digest)
    else:
        if not isinstance(encoding, RepresentativeEncoding):
            raise TypeError("representative envelope requires RepresentativeEncoding")
        payload = encoding.marks
        digest = _digest_bytes(encoding.specification_digest)
    return _pack_envelope(candidate_name, digest, payload)


def decode_envelope(
    data: bytes, *, expected_candidate: str | None = None
) -> tuple[str, bytes, bytes]:
    """Decode structural framing and require exact EOF/canonical lengths."""

    if len(data) < ENVELOPE_HEADER.size:
        raise ValueError("truncated envelope header")
    magic, version, tag, digest, payload_length = ENVELOPE_HEADER.unpack(
        data[: ENVELOPE_HEADER.size]
    )
    if magic != ENVELOPE_MAGIC:
        raise ValueError("wrong envelope magic")
    if version != FORMAT_VERSION:
        raise ValueError("unsupported envelope version")
    candidate_name = TAG_CANDIDATES.get(tag)
    if candidate_name is None:
        raise ValueError("unknown candidate tag")
    if expected_candidate is not None and candidate_name != _candidate_name(expected_candidate):
        raise ValueError("candidate tag does not match the selected decoder")
    if payload_length > MAX_REPRESENTATIVE_PAYLOAD:
        raise ValueError("envelope payload exceeds the probe bound")
    expected_length = ENVELOPE_HEADER.size + payload_length
    if len(data) != expected_length:
        raise ValueError("envelope payload length or trailing bytes are invalid")
    payload = data[ENVELOPE_HEADER.size :]
    if candidate_name == ORDINAL and len(payload) != ORDINAL_PAYLOAD_BYTES:
        raise ValueError("ordinal payload must contain exactly three bytes")
    return candidate_name, digest, payload


def deserialize_encoding(candidate_name: str, data: bytes) -> object:
    """Construct the public dataclass consumed by the candidate's recover API."""

    from c0_candidates import OrdinalEncoding, RepresentativeEncoding

    actual, digest, payload = decode_envelope(data, expected_candidate=candidate_name)
    digest_hex = digest.hex()
    if actual == ORDINAL:
        return OrdinalEncoding(digest_hex, int.from_bytes(payload, "big"))
    return RepresentativeEncoding(digest_hex, payload)


def _read_exact(stream: BinaryIO, length: int, label: str) -> bytes:
    value = stream.read(length)
    if len(value) != length:
        raise ValueError(f"truncated {label}")
    return value


def _read_envelope(stream: BinaryIO, expected_candidate: str) -> bytes:
    header = _read_exact(stream, ENVELOPE_HEADER.size, "state envelope header")
    magic, version, tag, digest, payload_length = ENVELOPE_HEADER.unpack(header)
    if payload_length > MAX_REPRESENTATIVE_PAYLOAD:
        raise ValueError("state envelope payload exceeds the probe bound")
    payload = _read_exact(stream, payload_length, "state envelope payload")
    envelope = header + payload
    decode_envelope(envelope, expected_candidate=expected_candidate)
    return envelope


def _write_stream_header(stream: BinaryIO, candidate_name: str, count: int) -> None:
    stream.write(
        STREAM_HEADER.pack(
            STREAM_MAGIC,
            FORMAT_VERSION,
            CANDIDATE_TAGS[_candidate_name(candidate_name)],
            count,
        )
    )


def _read_stream_header(stream: BinaryIO, expected_candidate: str) -> int:
    raw = _read_exact(stream, STREAM_HEADER.size, "state-stream header")
    magic, version, tag, count = STREAM_HEADER.unpack(raw)
    if magic != STREAM_MAGIC:
        raise ValueError("wrong state-stream magic")
    if version != FORMAT_VERSION:
        raise ValueError("unsupported state-stream version")
    if tag != CANDIDATE_TAGS[_candidate_name(expected_candidate)]:
        raise ValueError("state-stream candidate tag mismatch")
    return count


def _bundle_manifest(directory: Path = HERE) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for name in BUNDLE_NAMES:
        path = directory / name
        data = path.read_bytes()
        result.append({"name": name, "bytes": len(data), "sha256": _sha256_bytes(data)})
    return result


def _runtime_identity() -> dict[str, object]:
    return {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "cache_tag": sys.implementation.cache_tag,
        "byteorder": sys.byteorder,
    }


def _verify_bundle_imports() -> None:
    import c0_candidates
    import c0_experiment
    import c0_oracle

    for module in (c0_candidates, c0_experiment, c0_oracle):
        path = Path(module.__file__).resolve()
        if path.parent != HERE or path.name not in SPECIFICATION_NAMES:
            raise RuntimeError(f"module escaped copied bundle: {path}")
    for path in c0_candidates.SPECIFICATION_FILES:
        resolved = Path(path).resolve()
        if resolved.parent != HERE or resolved.name not in SPECIFICATION_NAMES:
            raise RuntimeError(f"specification path escaped copied bundle: {resolved}")


def _build_machine():
    from c0_candidates import QuotientBoundaryMachine
    from c0_experiment import StableRightCongruence

    _verify_bundle_imports()
    return QuotientBoundaryMachine(StableRightCongruence())


def _candidate(machine: object, candidate_name: str):
    from c0_candidates import OrdinalCandidate, RepresentativeCandidate

    if _candidate_name(candidate_name) == ORDINAL:
        return OrdinalCandidate(machine)
    return RepresentativeCandidate(machine)


def _canonical_envelopes(machine: object, candidate_name: str):
    """Call public persist for every canonical snapshot and return keyed bytes."""

    from c0_oracle import replay

    candidate = _candidate(machine, candidate_name)
    by_key: dict[tuple[str, ...], bytes] = {}
    ordered: list[bytes] = []
    payload_lengths: list[int] = []
    for key in machine.ordered_keys:
        snapshot = replay(machine.representatives[key])
        encoding = candidate.persist(snapshot)
        if candidate.recover(encoding) != key:
            raise AssertionError("public persist/recover failed for a canonical snapshot")
        envelope = serialize_encoding(candidate_name, encoding)
        parsed_name, _digest, payload = decode_envelope(
            envelope, expected_candidate=candidate_name
        )
        if parsed_name != candidate_name:
            raise AssertionError("serialized candidate tag changed")
        by_key[key] = envelope
        ordered.append(envelope)
        payload_lengths.append(len(payload))
    if len(set(ordered)) != len(ordered):
        raise AssertionError("public candidate persistence collided in the full universe")
    return candidate, by_key, tuple(ordered), tuple(payload_lengths)


def _operation_sequence() -> tuple[object, ...]:
    from c0_oracle import INPUTS

    return ("resume", *INPUTS)


def _update_blob(digest: object, tag: bytes, value: bytes) -> None:
    digest.update(tag)  # type: ignore[attr-defined]
    digest.update(U32.pack(len(value)))  # type: ignore[attr-defined]
    digest.update(value)  # type: ignore[attr-defined]


def _update_tokens(digest: object, tag: bytes, values: Sequence[str]) -> None:
    digest.update(tag)  # type: ignore[attr-defined]
    digest.update(U32.pack(len(values)))  # type: ignore[attr-defined]
    for value in values:
        _update_blob(digest, b"V", value.encode("utf-8"))


def _transition_header(
    candidate_name: str, artifact_digest: str, state_count: int
) -> bytes:
    operations = _operation_sequence()
    result = bytearray(TRANSITION_MAGIC)
    result.extend(bytes((FORMAT_VERSION, CANDIDATE_TAGS[candidate_name])))
    result.extend(_digest_bytes(artifact_digest))
    result.extend(U32.pack(state_count))
    result.extend(U32.pack(len(operations)))
    result.extend(b"proof-domain-membership-v1\0")
    for operation in operations:
        token = "resume" if operation == "resume" else operation.token()
        encoded = token.encode("utf-8")
        result.extend(U32.pack(len(encoded)))
        result.extend(encoded)
    return bytes(result)


class TransitionAccumulator:
    """Canonical length-prefixed transition digest with per-chunk localization."""

    def __init__(self, candidate_name: str, artifact_digest: str, state_count: int):
        self.header = _transition_header(candidate_name, artifact_digest, state_count)
        self.global_digest = hashlib.sha256(self.header)
        self.chunk_digest: object | None = None
        self.chunk_digests: list[str] = []
        self.state_count = state_count
        self.transition_count = 0

    @staticmethod
    def _add_record(
        digest: object,
        envelope: bytes,
        operation_token: str,
        domain_membership: str | None,
        client: Sequence[str],
        action: Sequence[str],
        next_envelope: bytes,
    ) -> None:
        _update_blob(digest, b"S", envelope)
        _update_blob(digest, b"O", operation_token.encode("utf-8"))
        membership = b"N" if domain_membership is None else domain_membership.encode("ascii")
        if membership not in (b"N", b"enabled", b"disabled"):
            raise ValueError("unexpected proof-domain membership marker")
        _update_blob(digest, b"M", membership)
        _update_tokens(digest, b"C", client)
        _update_tokens(digest, b"A", action)
        _update_blob(digest, b"N", next_envelope)

    def begin_state(self, index: int) -> None:
        if index % CHUNK_STATES == 0:
            if self.chunk_digest is not None:
                self.chunk_digests.append(self.chunk_digest.hexdigest())  # type: ignore[attr-defined]
            self.chunk_digest = hashlib.sha256(
                self.header + b"CHUNK" + U32.pack(index // CHUNK_STATES)
            )

    def add(
        self,
        envelope: bytes,
        operation_token: str,
        domain_membership: str | None,
        client: Sequence[str],
        action: Sequence[str],
        next_envelope: bytes,
    ) -> None:
        if self.chunk_digest is None:
            raise AssertionError("begin_state must precede transition records")
        for digest in (self.global_digest, self.chunk_digest):
            self._add_record(
                digest,
                envelope,
                operation_token,
                domain_membership,
                client,
                action,
                next_envelope,
            )
        self.transition_count += 1

    def finish(self) -> tuple[str, tuple[str, ...]]:
        if self.chunk_digest is not None:
            self.chunk_digests.append(self.chunk_digest.hexdigest())  # type: ignore[attr-defined]
            self.chunk_digest = None
        return self.global_digest.hexdigest(), tuple(self.chunk_digests)


def _stream_digest_from_envelopes(
    candidate_name: str, envelopes: Sequence[bytes]
) -> tuple[str, int]:
    digest = hashlib.sha256()
    header = STREAM_HEADER.pack(
        STREAM_MAGIC,
        FORMAT_VERSION,
        CANDIDATE_TAGS[candidate_name],
        len(envelopes),
    )
    digest.update(header)
    size = len(header)
    for envelope in envelopes:
        digest.update(envelope)
        size += len(envelope)
    return digest.hexdigest(), size


def produce(candidate_name: str, state_stream: Path) -> dict[str, object]:
    """Producer role: public-persist all canonical states and exit."""

    candidate_name = _candidate_name(candidate_name)
    machine = _build_machine()
    _candidate_object, _by_key, envelopes, payload_lengths = _canonical_envelopes(
        machine, candidate_name
    )
    with state_stream.open("xb") as stream:
        _write_stream_header(stream, candidate_name, len(envelopes))
        for envelope in envelopes:
            stream.write(envelope)
    expected_sha, expected_size = _stream_digest_from_envelopes(candidate_name, envelopes)
    if _sha256_file(state_stream) != expected_sha or state_stream.stat().st_size != expected_size:
        raise AssertionError("written state stream differs from canonical bytes")
    return {
        "schema": "zero-ground-process-probe-v1",
        "role": "producer",
        "candidate": candidate_name,
        "artifact_digest": machine.specification_digest,
        "state_records": len(envelopes),
        "state_stream_bytes": expected_size,
        "state_stream_sha256": expected_sha,
        "payload_bytes": {
            "minimum": min(payload_lengths),
            "maximum": max(payload_lengths),
            "total": sum(payload_lengths),
        },
        "public_persist_calls": len(envelopes),
        "public_recover_checks": len(envelopes),
        "bundle_manifest": _bundle_manifest(),
        "bundle_import_paths_verified": True,
        "runtime_tcb": _runtime_identity(),
    }


def consume(candidate_name: str, state_stream: Path) -> dict[str, object]:
    """Consumer role: restore only supplied envelopes plus rebuilt specification."""

    from c0_experiment import DISABLED, ENABLED
    from c0_oracle import INPUTS

    candidate_name = _candidate_name(candidate_name)
    machine = _build_machine()
    candidate, envelope_by_key, _ordered, _lengths = _canonical_envelopes(
        machine, candidate_name
    )
    operations = _operation_sequence()
    accumulator = TransitionAccumulator(
        candidate_name, machine.specification_digest, len(machine.ordered_keys)
    )
    seen_keys: set[tuple[str, ...]] = set()
    state_records = 0
    with state_stream.open("rb") as stream:
        declared_count = _read_stream_header(stream, candidate_name)
        if declared_count != len(machine.ordered_keys):
            raise ValueError("state stream does not contain the complete class universe")
        for index in range(declared_count):
            envelope = _read_envelope(stream, candidate_name)
            encoding = deserialize_encoding(candidate_name, envelope)
            key = candidate.recover(encoding)
            if key in seen_keys:
                raise ValueError("state stream repeats a recovered class")
            seen_keys.add(key)
            accumulator.begin_state(index)
            for operation in operations:
                if operation == "resume":
                    result = machine.resume_step(key)
                    token = "resume"
                    if result.domain_membership is not None:
                        raise AssertionError("resume must have no proof-domain membership")
                else:
                    result = machine.input_step(key, operation)
                    token = operation.token()
                    if result.domain_membership not in (ENABLED, DISABLED):
                        raise AssertionError(
                            "input proposal must have enabled/disabled proof-domain membership"
                        )
                accumulator.add(
                    envelope,
                    token,
                    result.domain_membership,
                    result.client,
                    result.action,
                    envelope_by_key[result.next_key],
                )
            state_records += 1
        if stream.read(1) != b"":
            raise ValueError("trailing bytes after declared state-stream records")
    if seen_keys != set(machine.all_keys):
        raise AssertionError("restored state stream omitted generated classes")
    transition_sha, chunks = accumulator.finish()
    expected_transitions = state_records * (1 + len(INPUTS))
    if accumulator.transition_count != expected_transitions:
        raise AssertionError("transition coverage count mismatch")
    return {
        "schema": "zero-ground-process-probe-v1",
        "role": "consumer",
        "candidate": candidate_name,
        "artifact_digest": machine.specification_digest,
        "state_records": state_records,
        "unique_recovered_classes": len(seen_keys),
        "public_recover_calls": state_records,
        "operations_per_state": 1 + len(INPUTS),
        "transition_records": accumulator.transition_count,
        "state_stream_bytes": state_stream.stat().st_size,
        "state_stream_sha256": _sha256_file(state_stream),
        "transition_sha256": transition_sha,
        "transition_chunk_size_states": CHUNK_STATES,
        "transition_chunk_sha256": chunks,
        "bundle_manifest": _bundle_manifest(),
        "bundle_import_paths_verified": True,
        "runtime_tcb": _runtime_identity(),
    }


def expected_raw(candidate_name: str, machine: object | None = None) -> dict[str, object]:
    """Parent-side raw-oracle path, independent of candidate transition lookup."""

    from c0_experiment import DISABLED, ENABLED
    from c0_oracle import ACTION, CLIENT, INPUTS, OUT, accept, replay, resume

    candidate_name = _candidate_name(candidate_name)
    machine = _build_machine() if machine is None else machine
    _candidate_object, envelope_by_key, envelopes, _lengths = _canonical_envelopes(
        machine, candidate_name
    )
    accumulator = TransitionAccumulator(candidate_name, machine.specification_digest, len(envelopes))
    for index, (key, envelope) in enumerate(zip(machine.ordered_keys, envelopes)):
        snapshot = replay(machine.representatives[key])
        accumulator.begin_state(index)
        raw_resume = resume(snapshot)
        client = tuple(
            frame.token()
            for frame in raw_resume.crossed
            if frame.direction == OUT and frame.port == CLIENT
        )
        action = tuple(
            frame.token()
            for frame in raw_resume.crossed
            if frame.direction == OUT and frame.port == ACTION
        )
        accumulator.add(
            envelope,
            "resume",
            None,
            client,
            action,
            envelope_by_key[machine.class_key(raw_resume.snapshot)],
        )
        for frame in INPUTS:
            raw = accept(snapshot, frame)
            client = tuple(
                crossed.token()
                for crossed in raw.crossed
                if crossed.direction == OUT and crossed.port == CLIENT
            )
            action = tuple(
                crossed.token()
                for crossed in raw.crossed
                if crossed.direction == OUT and crossed.port == ACTION
            )
            accumulator.add(
                envelope,
                frame.token(),
                ENABLED if raw.legal else DISABLED,
                client,
                action,
                envelope_by_key[machine.class_key(raw.snapshot)],
            )
    transition_sha, chunks = accumulator.finish()
    stream_sha, stream_size = _stream_digest_from_envelopes(candidate_name, envelopes)
    return {
        "candidate": candidate_name,
        "artifact_digest": machine.specification_digest,
        "state_records": len(envelopes),
        "operations_per_state": 1 + len(INPUTS),
        "transition_records": accumulator.transition_count,
        "state_stream_bytes": stream_size,
        "state_stream_sha256": stream_sha,
        "transition_sha256": transition_sha,
        "transition_chunk_sha256": chunks,
    }


def _expect_failure(case_id: str, operation: object) -> str:
    try:
        operation()  # type: ignore[operator]
    except (TypeError, ValueError):
        return case_id
    raise AssertionError(f"malformed case unexpectedly passed: {case_id}")


def _require_all_prefixes_truncated(data: bytes) -> None:
    checked = 0
    for length in range(len(data)):
        try:
            decode_envelope(data[:length])
        except ValueError:
            checked += 1
            continue
        raise AssertionError(f"proper envelope prefix unexpectedly passed: {length}")
    if checked != len(data):
        raise AssertionError("not every proper envelope prefix was checked")


def envelope_validation_cases(machine: object) -> tuple[str, ...]:
    """Exercise structural and public-recovery rejection paths."""

    from c0_candidates import OrdinalEncoding, RepresentativeEncoding

    digest_hex = machine.specification_digest
    digest = _digest_bytes(digest_hex)
    ordinal_candidate = _candidate(machine, ORDINAL)
    representative_candidate = _candidate(machine, REPRESENTATIVE)
    valid_ordinal = serialize_encoding(ORDINAL, OrdinalEncoding(digest_hex, 0))
    passed: list[str] = []

    passed.append(_expect_failure("empty-envelope", lambda: decode_envelope(b"")))
    _require_all_prefixes_truncated(valid_ordinal)
    passed.append("all-proper-prefix-truncations")
    bad_magic = bytearray(valid_ordinal)
    bad_magic[0] ^= 1
    passed.append(_expect_failure("wrong-magic", lambda: decode_envelope(bytes(bad_magic))))
    bad_version = bytearray(valid_ordinal)
    bad_version[4] = FORMAT_VERSION + 1
    passed.append(_expect_failure("wrong-version", lambda: decode_envelope(bytes(bad_version))))
    passed.append(
        _expect_failure(
            "candidate-tag-confusion",
            lambda: decode_envelope(valid_ordinal, expected_candidate=REPRESENTATIVE),
        )
    )
    passed.append(
        _expect_failure("trailing-byte", lambda: decode_envelope(valid_ordinal + b"x"))
    )
    passed.append(
        _expect_failure(
            "uppercase-internal-digest",
            lambda: serialize_encoding(ORDINAL, OrdinalEncoding(digest_hex.upper(), 0)),
        )
    )
    for length in (0, 2, 4):
        malformed = _pack_envelope(ORDINAL, digest, b"\0" * length)
        passed.append(
            _expect_failure(
                f"ordinal-payload-length-{length}",
                lambda value=malformed: decode_envelope(value, expected_candidate=ORDINAL),
            )
        )
    for rank, case_id in (
        (len(machine.ordered_keys), "ordinal-rank-class-count"),
        ((1 << 24) - 1, "ordinal-rank-ffffff"),
    ):
        envelope = _pack_envelope(ORDINAL, digest, rank.to_bytes(3, "big"))
        encoding = deserialize_encoding(ORDINAL, envelope)
        passed.append(_expect_failure(case_id, lambda value=encoding: ordinal_candidate.recover(value)))

    wrong_digest = bytearray(digest)
    wrong_digest[0] ^= 1
    mismatch = deserialize_encoding(
        ORDINAL, _pack_envelope(ORDINAL, bytes(wrong_digest), b"\0\0\0")
    )
    passed.append(
        _expect_failure("artifact-digest-mismatch", lambda: ordinal_candidate.recover(mismatch))
    )

    initial = RepresentativeEncoding(digest_hex, b"")
    initial_envelope = serialize_encoding(REPRESENTATIVE, initial)
    if representative_candidate.recover(deserialize_encoding(REPRESENTATIVE, initial_envelope)) != machine.ordered_keys[0]:
        raise AssertionError("zero-length representative did not recover canonical initial state")
    passed.append("zero-length-representative-accepted")

    representative_bad = {
        "representative-invalid-utf8": b"\xff",
        "representative-nul": b"\0",
        "representative-trailing-separator": b"in:client:P(a,0);",
        "representative-outside-grammar": b"not-a-frame",
        "representative-illegal-prefix": b"in:client:O;in:client:P(a,0)",
        "representative-legal-noncanonical": b"in:client:P(a,0);in:client:P(a,0)",
    }
    for case_id, payload in representative_bad.items():
        encoding = deserialize_encoding(
            REPRESENTATIVE, _pack_envelope(REPRESENTATIVE, digest, payload)
        )
        passed.append(
            _expect_failure(
                case_id, lambda value=encoding: representative_candidate.recover(value)
            )
        )
    return tuple(passed)


def _copy_bundle(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=False)
    for name in BUNDLE_NAMES:
        destination = target / name
        shutil.copyfile(HERE / name, destination)
        destination.chmod(0o444)


def _sanitized_environment() -> dict[str, str]:
    return {"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC"}


def _run_child(directory: Path, arguments: Sequence[str]) -> tuple[dict[str, object], dict[str, object]]:
    command = (
        str(Path(sys.executable).resolve()),
        "-I",
        "-S",
        "-B",
        str(directory / PROBE_NAME),
        *arguments,
    )
    completed = subprocess.run(
        command,
        cwd=directory,
        env=_sanitized_environment(),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "isolated child failed\n"
            + completed.stderr.decode("utf-8", errors="replace")
        )
    if completed.stderr:
        raise RuntimeError("isolated child produced unexpected stderr")
    try:
        result = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("isolated child did not emit canonical JSON") from exc
    if completed.stdout.decode("utf-8") != _canonical_json(result) + "\n":
        raise RuntimeError("isolated child JSON is not canonical")
    process = {
        "exit_code": completed.returncode,
        "stderr_empty": completed.stderr == b"",
        "python_flags": ["-I", "-S", "-B"],
        "environment_keys": sorted(_sanitized_environment()),
        "close_fds": True,
    }
    return result, process


def _directory_clean(directory: Path, extra_names: Iterable[str] = ()) -> bool:
    expected = set(BUNDLE_NAMES) | set(extra_names)
    actual = {entry.name for entry in directory.iterdir()}
    return actual == expected and all(entry.is_file() for entry in directory.iterdir())


def _without_chunks(value: Mapping[str, object]) -> dict[str, object]:
    return {key: item for key, item in value.items() if key != "transition_chunk_sha256"}


def orchestrate() -> dict[str, object]:
    """Run producer -> exit -> two independent consumers for each candidate."""

    machine = _build_machine()
    malformed_cases = envelope_validation_cases(machine)
    candidates: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="zero-ground-process-probe-") as temporary:
        temporary_root = Path(temporary)
        for candidate_name in (ORDINAL, REPRESENTATIVE):
            expected = expected_raw(candidate_name, machine)

            producer_dir = temporary_root / f"{candidate_name}-producer"
            _copy_bundle(producer_dir)
            producer, producer_process = _run_child(
                producer_dir,
                ("produce", "--candidate", candidate_name, "--state-stream", "states.bin"),
            )
            producer_stream = producer_dir / "states.bin"
            producer_stream.chmod(0o444)
            producer_clean = _directory_clean(producer_dir, ("states.bin",))

            consumers: list[dict[str, object]] = []
            consumer_processes: list[dict[str, object]] = []
            consumer_clean: list[bool] = []
            for run_index in (1, 2):
                consumer_dir = temporary_root / f"{candidate_name}-consumer-{run_index}"
                _copy_bundle(consumer_dir)
                shutil.copyfile(producer_stream, consumer_dir / "states.bin")
                (consumer_dir / "states.bin").chmod(0o444)
                consumer, process = _run_child(
                    consumer_dir,
                    ("consume", "--candidate", candidate_name, "--state-stream", "states.bin"),
                )
                consumers.append(consumer)
                consumer_processes.append(process)
                consumer_clean.append(_directory_clean(consumer_dir, ("states.bin",)))

            expected_chunks = tuple(expected["transition_chunk_sha256"])  # type: ignore[arg-type]
            first_chunks = tuple(consumers[0]["transition_chunk_sha256"])  # type: ignore[arg-type]
            second_chunks = tuple(consumers[1]["transition_chunk_sha256"])  # type: ignore[arg-type]
            chunk_lengths = tuple(
                len(chunks) for chunks in (expected_chunks, first_chunks, second_chunks)
            )
            mismatches = [
                index
                for index in range(max(chunk_lengths))
                for values in (
                    tuple(
                        chunks[index] if index < len(chunks) else None
                        for chunks in (expected_chunks, first_chunks, second_chunks)
                    ),
                )
                if len(set(values)) != 1
            ]
            expected_common = {
                key: expected[key]
                for key in (
                    "artifact_digest",
                    "state_records",
                    "state_stream_bytes",
                    "state_stream_sha256",
                    "transition_records",
                    "transition_sha256",
                )
            }
            producer_common = {
                key: producer[key]
                for key in (
                    "artifact_digest",
                    "state_records",
                    "state_stream_bytes",
                    "state_stream_sha256",
                )
            }
            consumer_matches = [
                all(consumer[key] == expected_common[key] for key in expected_common)
                for consumer in consumers
            ]
            checks = {
                "producer_matches_expected_stream": all(
                    producer_common[key] == expected_common[key] for key in producer_common
                ),
                "consumer_runs_match_expected": consumer_matches,
                "consumer_runs_identical": consumers[0] == consumers[1],
                "transition_chunk_count": len(expected_chunks),
                "transition_chunk_counts": list(chunk_lengths),
                "transition_chunk_counts_identical": len(set(chunk_lengths)) == 1,
                "transition_chunk_mismatch_count": len(mismatches),
                "first_transition_chunk_mismatch": mismatches[0] if mismatches else None,
                "producer_directory_contains_only_declared_files": producer_clean,
                "consumer_directories_contain_only_declared_files": consumer_clean,
            }
            booleans = [
                checks["producer_matches_expected_stream"],
                *checks["consumer_runs_match_expected"],
                checks["consumer_runs_identical"],
                checks["transition_chunk_counts_identical"],
                checks["transition_chunk_mismatch_count"] == 0,
                checks["producer_directory_contains_only_declared_files"],
                *checks["consumer_directories_contain_only_declared_files"],
            ]
            if not all(booleans):
                raise AssertionError(f"fresh-process comparison failed: {candidate_name}: {checks}")
            candidates[candidate_name] = {
                "producer": producer,
                "producer_process": producer_process,
                "expected_raw_oracle": _without_chunks(expected),
                "consumer_run_1": _without_chunks(consumers[0]),
                "consumer_run_2": _without_chunks(consumers[1]),
                "consumer_processes": consumer_processes,
                "checks": checks,
            }

    b2_path = HERE / "EVIDENCE-B2.json"
    return {
        "schema": "zero-ground-process-restore-b3-v1",
        "contract": "finite B1/B2 laboratory artifact; process probe does not alter its digest",
        "artifact_digest": machine.specification_digest,
        "b2_evidence_sha256_before_probe": _sha256_file(b2_path),
        "process_probe_sha256": _sha256_file(HERE / PROBE_NAME),
        "envelope": {
            "magic_ascii": ENVELOPE_MAGIC.decode("ascii"),
            "version": FORMAT_VERSION,
            "candidate_tags": CANDIDATE_TAGS,
            "header": "magic[4],version[u8],candidate[u8],artifact_sha256[32],payload_length[u32be]",
            "ordinal_payload": "exactly three-byte big-endian rank",
            "representative_payload": "exact canonical B1 representative bytes; empty is valid",
            "pickle_used": False,
        },
        "state_stream": {
            "magic_ascii": STREAM_MAGIC.decode("ascii"),
            "version": FORMAT_VERSION,
            "header": "magic[4],version[u8],candidate[u8],record_count[u32be]",
            "exact_eof_required": True,
        },
        "transition_digest": {
            "sha256_assumption": True,
            "canonical_record": (
                "length-prefixed state envelope, operation, optional proof-domain membership, "
                "ordered client outputs, ordered action outputs, next state envelope"
            ),
            "operation_order": ["resume", *(frame.token() for frame in _operation_sequence()[1:])],
            "chunk_size_states": CHUNK_STATES,
        },
        "bundle_manifest": _bundle_manifest(),
        "runtime_tcb": _runtime_identity(),
        "malformed_envelope_cases_passed": malformed_cases,
        "candidates": candidates,
        "isolation_ledger": {
            "enforced": [
                "producer exits before either consumer starts",
                "producer and consumers use distinct newly-created directories",
                "consumer receives only its candidate state stream and copied declared bundle",
                "no originating snapshots or class keys are supplied",
                "representative payload itself is necessarily history-shaped; no separate history is supplied",
                "absolute interpreter invoked with -I -S -B",
                "environment reduced to LANG, LC_ALL, and TZ",
                "stdin closed, inherited file descriptors closed, bundle files read-only",
                "imports verified to resolve inside copied bundle",
                "no extra files or bytecode appear in clean directories",
            ],
            "not_enforced": [
                "no mount namespace or filesystem syscall sandbox; host files are technically reachable",
                "no network namespace or syscall filter",
                "same interpreter, standard library, OS kernel, host, oracle, and probe code",
                "artifact digest binds the specification artifact, not state-payload integrity; absent the parent stream-hash comparison or external integrity, a valid corrupted payload can select another class",
                "no physical medium, power loss, torn write, or boundary-capture failure",
                "no unlike runtime or physical realization",
            ],
            "tcb": [
                "copied B1 specification/source bundle",
                "c0_process_probe envelope, stream, and comparison code",
                "CPython interpreter and standard library",
                "host process/filesystem implementation",
                "SHA-256 for artifact, stream, and transition digest comparison",
            ],
        },
        "verdict": (
            "fresh-process reconstruction passed only if both candidates' two clean consumer "
            "runs match the independent raw-oracle digest for every generated class and one-step operation"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="role", required=True)
    for role in ("produce", "consume"):
        child = subparsers.add_parser(role)
        child.add_argument("--candidate", choices=tuple(CANDIDATE_TAGS), required=True)
        child.add_argument("--state-stream", type=Path, required=True)
    subparsers.add_parser("orchestrate")
    args = parser.parse_args()
    if args.role == "produce":
        _print_json(produce(args.candidate, args.state_stream))
    elif args.role == "consume":
        _print_json(consume(args.candidate, args.state_stream))
    else:
        _print_json(orchestrate())


if __name__ == "__main__":
    main()
