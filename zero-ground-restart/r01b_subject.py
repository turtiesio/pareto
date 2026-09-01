#!/usr/bin/env python3
"""Byte-exact R0.1B subject primitives whose formats are frozen.

This module deliberately does *not* choose a gate-R manifest format, a
``realization_id`` derivation, a ``BH`` container encoding, or the neutral
frame mechanism byte for a descriptor.  The correction profile requires all
four but does not assign their exact bytes.  Callers may use the record,
recovery, publication-result, fixture, and neutral-frame primitives below,
but an R0.1B runner must remain ``NOT_RUN`` until those missing authorities are
frozen.

No historical R0 record helper is imported: R0.1B has a different hash tag
and obtains its semantic suite digest from the closed S1 registry.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import errno
import hashlib
import hmac
import os
from pathlib import Path
import signal
import stat
import struct
from typing import Final


SEMANTIC_SUITE_DIGEST_HEX: Final = (
    "996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a6"
)
SEMANTIC_SUITE_DIGEST: Final = bytes.fromhex(SEMANTIC_SUITE_DIGEST_HEX)
RECORD_TAG: Final = b"ZERO-GROUND-R01B-RECORD\x00"
STATE_NAME: Final = "state.bin"
STAGING_NAME: Final = ".state.tmp"
MAX_OPAQUE: Final = 4096

P0: Final = b""
P1: Final = b"\x00"
C: Final = b""
Y0: Final = b""
Y1: Final = b"\x00"

ABSENT: Final = b"\x00"
REJECT: Final = b"\x01"
PUBLISH_COMPLETE: Final = b"\x10"

SLOT_NAMES: Final = ("J0", "J1", "J2", "J3", "J4", "J5")
SLOT_CODES: Final = {name: code for code, name in enumerate(SLOT_NAMES)}
SLOT_ACQUISITION: Final = 1
SLOT_WRITE: Final = 2
SLOT_FILE_FSYNC: Final = 3
SLOT_REPLACE: Final = 4
SLOT_DIRECTORY_FSYNC: Final = 5
SLOT_CONTROL: Final = 6

SOURCE_KERNEL: Final = 0
SOURCE_SIMULATED_WRAPPER: Final = 1

MECHANISM_INVARIANT: Final = 0
MECHANISM_REFERENCE: Final = 1
MECHANISM_OMITTED: Final = 2
MECHANISM_ALTERNATE: Final = 3
MECHANISM_SELF_CUT: Final = 4

NO_ACK_REQUIRED: Final = 0x01
SELF_CUT_TARGET: Final = 0x02
ACK_CONTINUE: Final = b"\xc1"
FRAME_PREFIX: Final = b"ZGNF\x01"
FRAME_LENGTH: Final = 40

MECHANISM_MANIFESTS: Final = frozenset(
    {
        "REFERENCE",
        "NO_FILE_FSYNC",
        "NO_DIRECTORY_FSYNC",
        "NO_EXCLUSIVE_CREATE",
        "NO_REPLACE",
        "NO_PRE_RECOVERY_REAP_BEHAVIORAL",
        "DROP_STAGE_CONTROLLER",
        "SELF_CUT",
    }
)
INJECTED_FAULTS: Final = frozenset(
    {"NONE", "FILE_FSYNC_EIO", "REPLACE_EIO", "DIRECTORY_FSYNC_EIO"}
)


class R01BSubjectError(ValueError):
    """Base error for malformed R0.1B subject inputs."""


class RecordReject(R01BSubjectError):
    """The authoritative record cannot be accepted."""


class FixtureError(R01BSubjectError):
    """A crossed fixture is not one of the closed section-1.3 shapes."""


class ControlProtocolError(R01BSubjectError):
    """A neutral-frame or acknowledgement value is malformed."""


class PublicationConfigurationError(R01BSubjectError):
    """A publication mechanism/fault combination is outside frozen S1."""


def _exact_bytes(value: object, label: str) -> bytes:
    if type(value) is not bytes:
        raise TypeError(f"{label} must be exact bytes")
    return value


def _sha256(value: bytes) -> bytes:
    return hashlib.sha256(value).digest()


def record_hash(suite_digest: bytes, payload: bytes) -> bytes:
    """Return the exact R0.1B record hash from correction section 10.1."""

    suite_digest = _exact_bytes(suite_digest, "suite_digest")
    payload = _exact_bytes(payload, "payload")
    if len(suite_digest) != 32:
        raise ValueError("suite_digest must contain exactly 32 bytes")
    if len(payload) > MAX_OPAQUE:
        raise ValueError("payload exceeds 4096 bytes")
    return _sha256(
        RECORD_TAG + suite_digest + struct.pack(">Q", len(payload)) + payload
    )


def encode_record(suite_digest: bytes, payload: bytes) -> bytes:
    """Encode ``D_sem || P || H`` without using any R0 helper."""

    suite_digest = _exact_bytes(suite_digest, "suite_digest")
    payload = _exact_bytes(payload, "payload")
    return suite_digest + payload + record_hash(suite_digest, payload)


def parse_record(data: bytes, expected_suite_digest: bytes) -> bytes:
    """Return the opaque payload or raise ``RecordReject``."""

    data = _exact_bytes(data, "data")
    expected_suite_digest = _exact_bytes(
        expected_suite_digest, "expected_suite_digest"
    )
    if len(expected_suite_digest) != 32:
        raise RecordReject("expected suite digest is not 32 bytes")
    if not 64 <= len(data) <= 64 + MAX_OPAQUE:
        raise RecordReject("record length is outside 64..4160")
    observed_suite_digest = data[:32]
    payload = data[32:-32]
    observed_hash = data[-32:]
    if not hmac.compare_digest(observed_suite_digest, expected_suite_digest):
        raise RecordReject("record belongs to a different semantic suite")
    expected_hash = record_hash(observed_suite_digest, payload)
    if not hmac.compare_digest(observed_hash, expected_hash):
        raise RecordReject("record hash does not match")
    return payload


def adapter_apply(payload: bytes, continuation: bytes) -> bytes:
    """Apply the two frozen opaque adapter rows; all other inputs reject."""

    payload = _exact_bytes(payload, "payload")
    continuation = _exact_bytes(continuation, "continuation")
    if continuation != C:
        raise RecordReject("continuation is outside the frozen suite")
    if payload == P0:
        return Y0
    if payload == P1:
        return Y1
    raise RecordReject("payload is outside the frozen suite")


def ok_observation(output: bytes) -> bytes:
    output = _exact_bytes(output, "output")
    if len(output) > MAX_OPAQUE:
        raise ValueError("adapter output exceeds 4096 bytes")
    return b"\x02" + struct.pack(">I", len(output)) + output


def recover_record_bytes(
    data: bytes | None,
    expected_suite_digest: bytes = SEMANTIC_SUITE_DIGEST,
    continuation: bytes = C,
) -> bytes:
    """Apply the exact recovery relation to an absent or regular byte value."""

    if data is None:
        return ABSENT
    try:
        payload = parse_record(data, expected_suite_digest)
        first = adapter_apply(payload, continuation)
        second = adapter_apply(payload, continuation)
        if first != second or len(first) > MAX_OPAQUE:
            return REJECT
        return ok_observation(first)
    except Exception:
        return REJECT


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
        raise RecordReject("authoritative entry cannot be opened") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise RecordReject("authoritative entry is not regular")
        if not 64 <= info.st_size <= 64 + MAX_OPAQUE:
            raise RecordReject("authoritative entry has an invalid length")
        chunks: list[bytes] = []
        remaining = info.st_size
        while remaining:
            chunk = os.read(fd, remaining)
            if not chunk:
                raise RecordReject("authoritative entry shortened while read")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(fd, 1):
            raise RecordReject("authoritative entry grew while read")
        return b"".join(chunks)
    finally:
        os.close(fd)


def recover_directory(
    directory: str | os.PathLike[str],
    expected_suite_digest: bytes = SEMANTIC_SUITE_DIGEST,
    continuation: bytes = C,
) -> bytes:
    """Recover from ``state.bin`` without following a symlink."""

    try:
        data = _read_authoritative(Path(directory))
    except Exception:
        return REJECT
    return recover_record_bytes(data, expected_suite_digest, continuation)


def parse_recovery_observation(value: bytes) -> tuple[str, bytes | None]:
    """Strictly parse one declared recovery stdout value."""

    value = _exact_bytes(value, "value")
    if value == ABSENT:
        return "ABSENT", None
    if value == REJECT:
        return "REJECT", None
    if len(value) < 5 or value[0] != 0x02:
        raise R01BSubjectError("malformed recovery observation")
    length = struct.unpack(">I", value[1:5])[0]
    if length > MAX_OPAQUE or len(value) != 5 + length:
        raise R01BSubjectError("malformed OK recovery observation")
    return "OK", value[5:]


def publish_error(slot: int, source: int, number: int) -> bytes:
    """Encode exact ``ERROR(slot, source, errno)`` publisher bytes."""

    if type(slot) is not int or not 1 <= slot <= 6:
        raise ValueError("publisher result slot must be 1..6")
    if type(source) is not int or source not in (0, 1):
        raise ValueError("publisher result source must be 0 or 1")
    if type(number) is not int or not 1 <= number <= 0x7FFFFFFF:
        raise ValueError("publisher errno must be a positive i32")
    return b"\x11" + bytes((slot, source)) + struct.pack(">i", number)


def parse_publish_result(value: bytes) -> tuple[str, int | None, int | None, int | None]:
    """Strictly parse one declared publisher-result crossing."""

    value = _exact_bytes(value, "value")
    if value == PUBLISH_COMPLETE:
        return "COMPLETE", None, None, None
    if len(value) != 7 or value[0] != 0x11:
        raise R01BSubjectError("malformed publisher result")
    slot = value[1]
    source = value[2]
    number = struct.unpack(">i", value[3:])[0]
    if not 1 <= slot <= 6 or source not in (0, 1) or number <= 0:
        raise R01BSubjectError("publisher result contains an invalid coordinate")
    return "ERROR", slot, source, number


@dataclass(frozen=True, slots=True)
class NeutralFrame:
    slot: int
    mechanism: int
    flags: int
    trial_digest: bytes

    @property
    def slot_name(self) -> str:
        return SLOT_NAMES[self.slot]


def encode_neutral_frame(
    trial_digest: bytes,
    slot: int | str,
    mechanism: int,
    flags: int,
) -> bytes:
    """Encode the exact forty-byte section-4.2 neutral frame.

    ``mechanism`` is intentionally explicit.  The frozen profile defines the
    five code meanings but does not assign a code to each descriptor/slot.
    """

    trial_digest = _exact_bytes(trial_digest, "trial_digest")
    if len(trial_digest) != 32:
        raise ValueError("trial_digest must contain exactly 32 bytes")
    if type(slot) is str:
        try:
            slot_code = SLOT_CODES[slot]
        except KeyError as exc:
            raise ValueError("slot must be J0..J5") from exc
    elif type(slot) is int and 0 <= slot <= 5:
        slot_code = slot
    else:
        raise ValueError("slot must be J0..J5 or integer 0..5")
    if type(mechanism) is not int or not 0 <= mechanism <= 4:
        raise ValueError("mechanism code must be 0..4")
    if type(flags) is not int or flags & ~(NO_ACK_REQUIRED | SELF_CUT_TARGET):
        raise ValueError("frame flags contain an undeclared bit")
    return FRAME_PREFIX + bytes((slot_code, mechanism, flags)) + trial_digest


def decode_neutral_frame(value: bytes) -> NeutralFrame:
    value = _exact_bytes(value, "value")
    if len(value) != FRAME_LENGTH:
        raise ControlProtocolError("neutral frame is not forty bytes")
    if value[:5] != FRAME_PREFIX:
        raise ControlProtocolError("neutral frame has a bad magic or version")
    slot, mechanism, flags = value[5:8]
    if slot > 5:
        raise ControlProtocolError("neutral frame slot is outside J0..J5")
    if mechanism > 4:
        raise ControlProtocolError("neutral frame mechanism is not registered")
    if flags & ~(NO_ACK_REQUIRED | SELF_CUT_TARGET):
        raise ControlProtocolError("neutral frame has an undeclared flag bit")
    return NeutralFrame(slot, mechanism, flags, value[8:])


def write_all_fd(fd: int, value: bytes) -> None:
    """Write exact bytes with short-write retry."""

    value = _exact_bytes(value, "value")
    view = memoryview(value)
    while view:
        count = os.write(fd, view)
        if count <= 0:
            raise OSError(errno.EIO, "zero-progress write")
        view = view[count:]


def read_exact_fd(fd: int, length: int) -> bytes:
    if type(length) is not int or length < 0:
        raise ValueError("length must be a nonnegative integer")
    chunks: list[bytes] = []
    remaining = length
    while remaining:
        chunk = os.read(fd, remaining)
        if not chunk:
            raise ControlProtocolError("unexpected EOF")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def emit_neutral_frame(fd: int, frame: bytes) -> None:
    if len(frame) != FRAME_LENGTH:
        raise ControlProtocolError("neutral frame is not forty bytes")
    decode_neutral_frame(frame)
    write_all_fd(fd, frame)


def await_continue_ack(fd: int) -> None:
    if read_exact_fd(fd, 1) != ACK_CONTINUE:
        raise ControlProtocolError("continuation acknowledgement is not c1")


def self_stop() -> None:
    """Perform the exact SELF_CUT stop action after its target frame."""

    os.kill(os.getpid(), signal.SIGSTOP)
    raise ControlProtocolError("SELF_CUT publisher resumed instead of being killed")


def _entry_kind(entry: object) -> str:
    if not isinstance(entry, Mapping) or type(entry.get("kind")) is not str:
        raise FixtureError("entry must be a map with a text kind")
    kind = entry["kind"]
    expected_keys = {
        "ABSENT": {"kind"},
        "REGULAR": {"kind", "regular_bytes"},
        "SYMLINK": {"kind", "symlink_target_bytes"},
    }
    if kind not in expected_keys or set(entry) != expected_keys[kind]:
        raise FixtureError("entry does not have an exact closed shape")
    if kind == "REGULAR":
        _exact_bytes(entry["regular_bytes"], "regular_bytes")
    if kind == "SYMLINK":
        _exact_bytes(entry["symlink_target_bytes"], "symlink_target_bytes")
    return kind


def _require_empty_directory(directory: Path) -> None:
    if not directory.is_dir():
        raise FixtureError("fixture destination is not a directory")
    if any(directory.iterdir()):
        raise FixtureError("fixture destination is not empty")


def _write_regular(path: Path, value: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    fd = os.open(path, flags, 0o600)
    try:
        write_all_fd(fd, value)
    finally:
        os.close(fd)


def install_publication_setup(
    directory: str | os.PathLike[str],
    setup: str,
    suite_digest: bytes = SEMANTIC_SUITE_DIGEST,
) -> None:
    """Install one exact section-1.3 publication fixture."""

    destination = Path(directory)
    _require_empty_directory(destination)
    if setup not in {
        "ABSENT_CLEAN",
        "VALID_P0_CLEAN",
        "ABSENT_TMP",
        "VALID_P0_TMP",
    }:
        raise FixtureError("unknown publication setup")
    if setup.startswith("VALID_P0"):
        _write_regular(destination / STATE_NAME, encode_record(suite_digest, P0))
    if setup.endswith("TMP"):
        _write_regular(destination / STAGING_NAME, b"")


def _validate_auxiliary_name(name: bytes) -> None:
    if not name or b"\x00" in name or b"/" in name:
        raise FixtureError("auxiliary name is not one nonempty relative component")
    if name in (STATE_NAME.encode(), STAGING_NAME.encode()):
        raise FixtureError("auxiliary name collides with a reserved entry")


def install_recovery_fixture(
    directory: str | os.PathLike[str], fixture: Mapping[str, object]
) -> None:
    """Install the complete typed recovery fixture that crossed ``B``."""

    destination = Path(directory)
    _require_empty_directory(destination)
    if not isinstance(fixture, Mapping) or set(fixture) != {
        "authoritative_entry",
        "auxiliary_regular_entries",
    }:
        raise FixtureError("recovery fixture does not have its closed map shape")
    authoritative = fixture["authoritative_entry"]
    kind = _entry_kind(authoritative)
    auxiliary = fixture["auxiliary_regular_entries"]
    if not isinstance(auxiliary, Sequence) or isinstance(
        auxiliary, (str, bytes, bytearray)
    ):
        raise FixtureError("auxiliary_regular_entries must be a list")
    parsed_auxiliary: list[tuple[bytes, bytes]] = []
    for item in auxiliary:
        if not isinstance(item, Mapping) or set(item) != {
            "name_bytes",
            "regular_bytes",
        }:
            raise FixtureError("auxiliary entry does not have its closed shape")
        name = _exact_bytes(item["name_bytes"], "name_bytes")
        value = _exact_bytes(item["regular_bytes"], "regular_bytes")
        _validate_auxiliary_name(name)
        parsed_auxiliary.append((name, value))
    names = [item[0] for item in parsed_auxiliary]
    if names != sorted(names) or len(names) != len(set(names)):
        raise FixtureError("auxiliary names are not sorted and unique")
    if kind in ("ABSENT", "REGULAR") and parsed_auxiliary:
        raise FixtureError("ABSENT/REGULAR authoritative entries require no auxiliary")

    for name, value in parsed_auxiliary:
        _write_regular(Path(os.fsdecode(os.fsencode(destination) + b"/" + name)), value)
    state_path = destination / STATE_NAME
    if kind == "REGULAR":
        _write_regular(state_path, authoritative["regular_bytes"])
    elif kind == "SYMLINK":
        target = authoritative["symlink_target_bytes"]
        os.symlink(target, os.fsencode(state_path))


Checkpoint = Callable[[int], None]


def _configured_publication(mechanism: str, injected_fault: str) -> None:
    if mechanism not in MECHANISM_MANIFESTS:
        raise PublicationConfigurationError("mechanism manifest is not registered")
    if injected_fault not in INJECTED_FAULTS:
        raise PublicationConfigurationError("injected fault is not registered")
    if injected_fault != "NONE" and mechanism != "REFERENCE":
        raise PublicationConfigurationError(
            "S1 admits injected publication faults only for REFERENCE"
        )


def _kernel_error(slot: int, exc: OSError) -> bytes:
    number = exc.errno if type(exc.errno) is int and exc.errno > 0 else errno.EIO
    return publish_error(slot, SOURCE_KERNEL, number)


def publish_directory(
    directory: str | os.PathLike[str],
    payload: bytes,
    mechanism: str,
    injected_fault: str,
    checkpoint: Checkpoint,
    suite_digest: bytes = SEMANTIC_SUITE_DIGEST,
) -> bytes:
    """Execute the declared slot program and return one publisher result.

    ``checkpoint(slot)`` is called after each slot's work.  It is deliberately
    responsible for framing/blocking/stopping: R0.1B does not freeze the
    descriptor-to-``mm`` assignment needed to construct those bytes here.
    A process killed while blocked in the callback naturally produces no
    publisher-result crossing.
    """

    payload = _exact_bytes(payload, "payload")
    _configured_publication(mechanism, injected_fault)
    if payload not in (P0, P1):
        raise PublicationConfigurationError("requested payload is outside S1")
    if not callable(checkpoint):
        raise TypeError("checkpoint must be callable")
    destination = Path(directory)
    record = encode_record(suite_digest, payload)
    staging = destination / STAGING_NAME
    authoritative = destination / STATE_NAME
    half = len(record) // 2
    fd: int | None = None
    directory_fd: int | None = None

    checkpoint(0)
    flags = os.O_WRONLY | os.O_CREAT
    if mechanism == "NO_EXCLUSIVE_CREATE":
        flags |= os.O_TRUNC
    else:
        flags |= os.O_EXCL
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    try:
        fd = os.open(staging, flags, 0o600)
    except OSError as exc:
        return _kernel_error(SLOT_ACQUISITION, exc)

    try:
        try:
            write_all_fd(fd, record[:half])
        except OSError as exc:
            return _kernel_error(SLOT_WRITE, exc)
        checkpoint(1)
        try:
            write_all_fd(fd, record[half:])
        except OSError as exc:
            return _kernel_error(SLOT_WRITE, exc)
        checkpoint(2)

        if injected_fault == "FILE_FSYNC_EIO":
            return publish_error(
                SLOT_FILE_FSYNC, SOURCE_SIMULATED_WRAPPER, errno.EIO
            )
        if mechanism != "NO_FILE_FSYNC":
            try:
                os.fsync(fd)
            except OSError as exc:
                return _kernel_error(SLOT_FILE_FSYNC, exc)
        try:
            os.close(fd)
        except OSError as exc:
            return _kernel_error(SLOT_FILE_FSYNC, exc)
        fd = None
        checkpoint(3)

        if injected_fault == "REPLACE_EIO":
            return publish_error(SLOT_REPLACE, SOURCE_SIMULATED_WRAPPER, errno.EIO)
        if mechanism != "NO_REPLACE":
            try:
                os.replace(staging, authoritative)
            except OSError as exc:
                return _kernel_error(SLOT_REPLACE, exc)
        checkpoint(4)

        if injected_fault == "DIRECTORY_FSYNC_EIO":
            return publish_error(
                SLOT_DIRECTORY_FSYNC, SOURCE_SIMULATED_WRAPPER, errno.EIO
            )
        if mechanism != "NO_DIRECTORY_FSYNC":
            try:
                directory_fd = os.open(
                    destination,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_CLOEXEC", 0),
                )
                os.fsync(directory_fd)
            except OSError as exc:
                return _kernel_error(SLOT_DIRECTORY_FSYNC, exc)
            finally:
                if directory_fd is not None:
                    os.close(directory_fd)
                    directory_fd = None
        checkpoint(5)
        return PUBLISH_COMPLETE
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if directory_fd is not None:
            try:
                os.close(directory_fd)
            except OSError:
                pass


__all__ = [
    "ABSENT",
    "ACK_CONTINUE",
    "C",
    "ControlProtocolError",
    "FixtureError",
    "FRAME_LENGTH",
    "MECHANISM_ALTERNATE",
    "MECHANISM_INVARIANT",
    "MECHANISM_OMITTED",
    "MECHANISM_REFERENCE",
    "MECHANISM_SELF_CUT",
    "NO_ACK_REQUIRED",
    "P0",
    "P1",
    "PUBLISH_COMPLETE",
    "PublicationConfigurationError",
    "R01BSubjectError",
    "REJECT",
    "RecordReject",
    "SELF_CUT_TARGET",
    "SEMANTIC_SUITE_DIGEST",
    "SEMANTIC_SUITE_DIGEST_HEX",
    "SLOT_NAMES",
    "SOURCE_KERNEL",
    "SOURCE_SIMULATED_WRAPPER",
    "NeutralFrame",
    "adapter_apply",
    "await_continue_ack",
    "decode_neutral_frame",
    "emit_neutral_frame",
    "encode_neutral_frame",
    "encode_record",
    "install_publication_setup",
    "install_recovery_fixture",
    "ok_observation",
    "parse_publish_result",
    "parse_record",
    "parse_recovery_observation",
    "publish_directory",
    "publish_error",
    "read_exact_fd",
    "record_hash",
    "recover_directory",
    "recover_record_bytes",
    "self_stop",
    "write_all_fd",
]
