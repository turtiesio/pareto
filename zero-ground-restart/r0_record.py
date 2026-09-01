"""Exact bytes, digest derivation, and recovery parser for R0."""

from __future__ import annotations

import errno
import hashlib
import hmac
import os
from pathlib import Path
import stat
import struct
from typing import Iterable

import r0_adapter


CONTRACT_NAME = "REALIZATION-CONTRACT-R0.md"
BUNDLE_NAMES = ("r0_adapter.py", "r0_record.py", "r0_worker.py")
SUITE_TAG = b"ZERO-GROUND-R0-SUITE\x00"
RECORD_TAG = b"ZERO-GROUND-R0-RECORD\x00"
STATE_NAME = "state.bin"
TEMP_NAME = ".state.tmp"
MAX_OPAQUE = 4096

ABSENT = b"\x00"
REJECT = b"\x01"


class RecordReject(ValueError):
    """The candidate record is not acceptable under R0."""


def lp4(value: bytes) -> bytes:
    if len(value) > 0xFFFFFFFF:
        raise ValueError("LP value too large")
    return struct.pack(">I", len(value)) + value


def ok_observation(value: bytes) -> bytes:
    if len(value) > MAX_OPAQUE:
        raise ValueError("opaque result too large")
    return b"\x02" + lp4(value)


def sha256(value: bytes) -> bytes:
    return hashlib.sha256(value).digest()


def contract_digest(base: Path) -> bytes:
    return sha256((base / CONTRACT_NAME).read_bytes())


def canonical_bundle_manifest(base: Path,
                              names: Iterable[str] = BUNDLE_NAMES) -> bytes:
    entries: list[tuple[bytes, bytes]] = []
    for name in names:
        encoded = name.encode("utf-8")
        if name.startswith("/") or ".." in Path(name).parts or "\\" in name:
            raise ValueError(f"non-canonical bundle path: {name!r}")
        entries.append((encoded, (base / name).read_bytes()))
    entries.sort(key=lambda pair: pair[0])
    return b"".join(
        lp4(name) + struct.pack(">Q", len(contents)) + contents
        for name, contents in entries
    )


def bundle_digest(base: Path) -> bytes:
    return sha256(canonical_bundle_manifest(base))


def suite_digest(contract_sha: bytes, adapter_sha: bytes) -> bytes:
    if len(contract_sha) != 32 or len(adapter_sha) != 32:
        raise ValueError("suite digest inputs must be 32 bytes")
    return sha256(
        SUITE_TAG
        + contract_sha
        + adapter_sha
        + lp4(r0_adapter.P0)
        + lp4(r0_adapter.P1)
        + lp4(r0_adapter.C)
        + lp4(r0_adapter.Y0)
        + lp4(r0_adapter.Y1)
    )


def derive_digests(base: Path) -> tuple[bytes, bytes, bytes]:
    q = contract_digest(base)
    a = bundle_digest(base)
    return q, a, suite_digest(q, a)


def record_hash(digest: bytes, payload: bytes) -> bytes:
    if len(digest) != 32:
        raise ValueError("suite digest must be 32 bytes")
    if len(payload) > MAX_OPAQUE:
        raise ValueError("payload too large")
    return sha256(
        RECORD_TAG + digest + struct.pack(">Q", len(payload)) + payload
    )


def encode_record(digest: bytes, payload: bytes) -> bytes:
    return digest + payload + record_hash(digest, payload)


def parse_record(data: bytes, expected_digest: bytes) -> bytes:
    if len(expected_digest) != 32:
        raise RecordReject("invalid expected digest")
    if len(data) < 64 or len(data) > 64 + MAX_OPAQUE:
        raise RecordReject("invalid record length")
    observed_digest = data[:32]
    payload = data[32:-32]
    observed_hash = data[-32:]
    if not hmac.compare_digest(observed_digest, expected_digest):
        raise RecordReject("wrong suite")
    expected_hash = record_hash(observed_digest, payload)
    if not hmac.compare_digest(observed_hash, expected_hash):
        raise RecordReject("record hash mismatch")
    return payload


def _read_authoritative(directory: Path) -> bytes | None:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(directory / STATE_NAME, flags)
    except FileNotFoundError:
        return None
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            return None
        raise RecordReject("authoritative path cannot be opened") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise RecordReject("authoritative path is not regular")
        if info.st_size < 64 or info.st_size > 64 + MAX_OPAQUE:
            raise RecordReject("invalid record length")
        chunks: list[bytes] = []
        remaining = info.st_size
        while remaining:
            chunk = os.read(fd, remaining)
            if not chunk:
                raise RecordReject("short record read")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(fd, 1):
            raise RecordReject("record grew during read")
        return b"".join(chunks)
    finally:
        os.close(fd)


def recover(directory: Path, expected_digest: bytes,
            continuation: bytes) -> bytes:
    try:
        data = _read_authoritative(directory)
        if data is None:
            return ABSENT
        payload = parse_record(data, expected_digest)
        first = r0_adapter.apply(payload, continuation)
        second = r0_adapter.apply(payload, continuation)
        if first != second or len(first) > MAX_OPAQUE:
            return REJECT
        return ok_observation(first)
    except Exception:
        return REJECT

