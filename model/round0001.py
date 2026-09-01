"""Executable falsification model for ZERO GROUND Round 0001.

This is experimental apparatus, not a proposed semantic kernel.  It compares a
content-only archive with a lossless acquisition transcript that separates
content identity from capture occurrence identity.
"""

from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib
import json
from typing import Iterable


FORMAT = "zero-ground-acquisition-transcript-0.1"
HASH_ALGORITHM = "sha256-v1"


class ArchiveError(ValueError):
    """The transcript is malformed or fails an integrity condition."""


@dataclass(frozen=True, order=True)
class ContentRef:
    algorithm: str
    digest: bytes
    size: int


@dataclass(frozen=True)
class CaptureRecord:
    """One occurrence, without claiming what the payload means.

    `acquisition` is an optional reference to exact evidence emitted by the
    capture mechanism.  None means no acquisition artifact was retained; a
    reference to an empty artifact means an empty artifact was retained.
    """

    occurrence: bytes
    payload: ContentRef
    acquisition: ContentRef | None


def content_ref(data: bytes) -> ContentRef:
    return ContentRef(HASH_ALGORITHM, hashlib.sha256(data).digest(), len(data))


class ArtifactOnlyArchive:
    """Deliberately weak competing candidate: a set of unique byte strings."""

    def __init__(self) -> None:
        self.artifacts: dict[ContentRef, bytes] = {}

    def retain(self, data: bytes) -> ContentRef:
        ref = content_ref(data)
        previous = self.artifacts.get(ref)
        if previous is not None and previous != data:
            raise ArchiveError("content-address collision")
        self.artifacts[ref] = bytes(data)
        return ref


class AcquisitionTranscript:
    """Exact artifacts plus an append-ordered sequence of capture records."""

    def __init__(self) -> None:
        self.artifacts: dict[ContentRef, bytes] = {}
        self.captures: list[CaptureRecord] = []
        self._occurrences: set[bytes] = set()

    def retain_artifact(self, data: bytes) -> ContentRef:
        ref = content_ref(data)
        previous = self.artifacts.get(ref)
        if previous is not None and previous != data:
            raise ArchiveError("content-address collision")
        self.artifacts[ref] = bytes(data)
        return ref

    def capture(
        self,
        occurrence: bytes,
        payload: bytes,
        acquisition: bytes | None,
    ) -> CaptureRecord:
        occurrence = bytes(occurrence)
        if not occurrence:
            raise ArchiveError("occurrence address must not be empty")
        if occurrence in self._occurrences:
            raise ArchiveError("occurrence address already exists")
        payload_ref = self.retain_artifact(payload)
        acquisition_ref = (
            None if acquisition is None else self.retain_artifact(acquisition)
        )
        record = CaptureRecord(occurrence, payload_ref, acquisition_ref)
        self.captures.append(record)
        self._occurrences.add(occurrence)
        return record

    def read(self, ref: ContentRef) -> bytes:
        data = self.artifacts[ref]
        if content_ref(data) != ref:
            raise ArchiveError("artifact failed integrity verification")
        return data

    def verify(self) -> None:
        if len(self._occurrences) != len(self.captures):
            raise ArchiveError("duplicate occurrence address")
        for ref, data in self.artifacts.items():
            if content_ref(data) != ref:
                raise ArchiveError("artifact failed integrity verification")
        for record in self.captures:
            if record.payload not in self.artifacts:
                raise ArchiveError("missing payload artifact")
            if record.acquisition is not None and record.acquisition not in self.artifacts:
                raise ArchiveError("missing acquisition artifact")

    def export(self) -> bytes:
        """Return a deterministic experimental interchange document."""

        self.verify()
        artifacts = [
            {
                "algorithm": ref.algorithm,
                "digest": ref.digest.hex(),
                "size": ref.size,
                "data": _b64(data),
            }
            for ref, data in sorted(self.artifacts.items())
        ]
        captures = [
            {
                "occurrence": _b64(record.occurrence),
                "payload": _ref_to_data(record.payload),
                "acquisition": (
                    None
                    if record.acquisition is None
                    else _ref_to_data(record.acquisition)
                ),
            }
            for record in self.captures
        ]
        document = {"format": FORMAT, "artifacts": artifacts, "captures": captures}
        return json.dumps(
            document,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")

    @classmethod
    def load(cls, encoded: bytes) -> "AcquisitionTranscript":
        try:
            document = json.loads(encoded, object_pairs_hook=_unique_object)
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as error:
            raise ArchiveError("invalid transcript encoding") from error
        if not isinstance(document, dict) or document.get("format") != FORMAT:
            raise ArchiveError("unsupported transcript format")
        if set(document) != {"format", "artifacts", "captures"}:
            raise ArchiveError("unknown or missing transcript field")

        transcript = cls()
        try:
            for item in document["artifacts"]:
                if set(item) != {"algorithm", "digest", "size", "data"}:
                    raise ArchiveError("unknown or missing artifact field")
                ref = ContentRef(
                    str(item["algorithm"]),
                    bytes.fromhex(item["digest"]),
                    int(item["size"]),
                )
                data = _unb64(item["data"])
                if ref.algorithm != HASH_ALGORITHM or content_ref(data) != ref:
                    raise ArchiveError("artifact address does not match bytes")
                previous = transcript.artifacts.get(ref)
                if previous is not None and previous != data:
                    raise ArchiveError("content-address collision")
                transcript.artifacts[ref] = data

            for item in document["captures"]:
                if set(item) != {"occurrence", "payload", "acquisition"}:
                    raise ArchiveError("unknown or missing capture field")
                occurrence = _unb64(item["occurrence"])
                if not occurrence or occurrence in transcript._occurrences:
                    raise ArchiveError("invalid or duplicate occurrence address")
                payload = _ref_from_data(item["payload"])
                acquisition = (
                    None
                    if item["acquisition"] is None
                    else _ref_from_data(item["acquisition"])
                )
                transcript.captures.append(
                    CaptureRecord(occurrence, payload, acquisition)
                )
                transcript._occurrences.add(occurrence)
        except (KeyError, ValueError, TypeError, base64.binascii.Error) as error:
            if isinstance(error, ArchiveError):
                raise
            raise ArchiveError("invalid transcript value") from error
        transcript.verify()
        return transcript


def normalized_json(data: bytes) -> object:
    """A deliberately lossy competing projection using a conventional parser."""

    return json.loads(data)


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _unb64(text: str) -> bytes:
    if not isinstance(text, str):
        raise ArchiveError("base64 value must be text")
    return base64.b64decode(text, validate=True)


def _ref_to_data(ref: ContentRef) -> dict[str, object]:
    return {"algorithm": ref.algorithm, "digest": ref.digest.hex(), "size": ref.size}


def _ref_from_data(data: object) -> ContentRef:
    if not isinstance(data, dict) or set(data) != {"algorithm", "digest", "size"}:
        raise ArchiveError("invalid content reference")
    return ContentRef(str(data["algorithm"]), bytes.fromhex(data["digest"]), int(data["size"]))


def _unique_object(pairs: Iterable[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ArchiveError(f"duplicate transcript field: {key}")
        result[key] = value
    return result

