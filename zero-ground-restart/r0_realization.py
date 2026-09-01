#!/usr/bin/env python3
"""Executable finite R0 guest-storage falsification experiment.

This runner keeps deterministic semantic certificate material separate from
timing, allocation, inode, path, and environment measurements.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import ctypes
from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import shutil
import signal
import statistics
import struct
import subprocess
import sys
import tempfile
import time
from typing import Iterator, Mapping

import r0_adapter
import r0_record


BASE = Path(__file__).resolve().parent
WORKER = BASE / "r0_worker.py"
CONTRACT_SHA256 = "3bdaa119942ef994e4ef0cf1c570d4518a2531bc102505065d967fed08522f15"

BACKENDS = {
    "E": {"base": Path("/tmp"), "magic": 0xEF53, "filesystem": "ext4"},
    "T": {"base": Path("/dev/shm"), "magic": 0x01021994, "filesystem": "tmpfs"},
}
CUTS = ("K0", "K1", "K2", "K3", "K4", "K5", "NORMAL")
CASES = ("CREATE", "UPDATE")
SHORT_WRITE_SIZES = (1, 2, 7, 31)
IO_FAULTS = (
    "write_before_half",
    "write_after_half",
    "file_fsync",
    "replace",
    "directory_fsync",
)

# This literal verifier path intentionally does not call the adapter, record
# parser, or candidate encoder.
_LITERAL_OBSERVATIONS = {
    "ABSENT": bytes.fromhex("00"),
    "REJECT": bytes.fromhex("01"),
    "P0": bytes.fromhex("0200000000"),
    "P1": bytes.fromhex("020000000100"),
}


def literal_expected(label: str) -> bytes:
    try:
        return _LITERAL_OBSERVATIONS[label]
    except KeyError as exc:
        raise AssertionError(f"literal oracle has no {label!r}") from exc


def oracle_accepts(label: str, observed: bytes) -> bool:
    return observed == literal_expected(label)


def _lp4(value: bytes) -> bytes:
    return struct.pack(">I", len(value)) + value


def _lp8(value: bytes) -> bytes:
    return struct.pack(">Q", len(value)) + value


def _b(value: str | bytes | int | bool) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bool):
        return b"true" if value else b"false"
    return str(value).encode("utf-8")


def _canonical_fields(fields: Mapping[str, bytes]) -> bytes:
    ordered = sorted((key.encode("utf-8"), value) for key, value in fields.items())
    return struct.pack(">I", len(ordered)) + b"".join(
        _lp4(key) + _lp8(value) for key, value in ordered
    )


def _child_cpu_ns() -> int:
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return int((usage.ru_utime + usage.ru_stime) * 1_000_000_000)


@dataclass
class PublisherOutcome:
    transcript: bytes
    terminal: str
    returncode: int
    stderr: bytes
    wall_ns: int
    child_cpu_ns: int


@dataclass
class RecoveryOutcome:
    observation: bytes
    returncode: int
    stderr: bytes
    wall_ns: int
    child_cpu_ns: int


@dataclass
class TrialResult:
    trial_id: str
    category: str
    expected: bytes
    observed: bytes
    fields: dict[str, bytes]
    passed: bool
    wall_ns: int
    child_cpu_ns: int
    explanation: str = ""
    measurement: dict[str, object] = field(default_factory=dict)

    def certificate_record(self, suite_digest: bytes) -> bytes:
        fixed = {
            "trial_id": _b(self.trial_id),
            "category": _b(self.category),
            "suite_digest": suite_digest,
            "expected": self.expected,
            "observed": self.observed,
            "verdict": _b("PASS" if self.passed else "FAIL"),
            "explanation": _b(self.explanation),
            **self.fields,
        }
        return _canonical_fields(fixed)


@dataclass
class Experiment:
    q: bytes
    a: bytes
    d: bytes
    backend_info: dict[str, dict[str, object]]
    results: list[TrialResult] = field(default_factory=list)
    deletion_findings: dict[str, object] = field(default_factory=dict)
    common_mode: dict[str, object] = field(default_factory=dict)

    def add(self, result: TrialResult) -> None:
        if any(old.trial_id == result.trial_id for old in self.results):
            raise AssertionError(f"duplicate trial id {result.trial_id}")
        self.results.append(result)

    def certificate(self, category: str | None = None) -> tuple[str, int, int]:
        selected = [
            result for result in self.results
            if category is None or result.category == category
        ]
        encoded = [
            result.certificate_record(self.d)
            for result in sorted(selected, key=lambda item: item.trial_id)
        ]
        stream = b"".join(_lp8(record) for record in encoded)
        return hashlib.sha256(stream).hexdigest(), len(encoded), len(stream)


def _statfs_magic(path: Path) -> int:
    # A deliberately oversized output buffer avoids depending on a Python
    # transcription of the platform's full struct statfs; f_type is its first
    # native long on the declared Linux/glibc environment.
    output = ctypes.create_string_buffer(512)
    libc = ctypes.CDLL(None, use_errno=True)
    statfs = libc.statfs
    statfs.argtypes = (ctypes.c_char_p, ctypes.c_void_p)
    statfs.restype = ctypes.c_int
    if statfs(os.fsencode(path), ctypes.byref(output)) != 0:
        number = ctypes.get_errno()
        raise OSError(number, os.strerror(number), str(path))
    return int(ctypes.c_long.from_buffer(output).value) & 0xFFFFFFFFFFFFFFFF


def _unescape_mount(value: str) -> str:
    for escaped, plain in (("\\040", " "), ("\\011", "\t"),
                           ("\\012", "\n"), ("\\134", "\\")):
        value = value.replace(escaped, plain)
    return value


def _mount_line(path: Path) -> str:
    resolved = str(path.resolve())
    matches: list[tuple[int, str]] = []
    for line in Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) < 10:
            continue
        mountpoint = _unescape_mount(fields[4])
        if resolved == mountpoint or resolved.startswith(mountpoint.rstrip("/") + "/"):
            matches.append((len(mountpoint), line))
    if not matches:
        raise RuntimeError(f"no mountinfo entry for {path}")
    return max(matches)[1]


def validate_backend(symbol: str) -> dict[str, object]:
    declaration = BACKENDS[symbol]
    base = declaration["base"]
    assert isinstance(base, Path)
    if not base.is_dir():
        raise RuntimeError(f"R0 backend {symbol} base is unavailable: {base}")
    magic = _statfs_magic(base)
    if magic != declaration["magic"]:
        raise RuntimeError(
            f"R0 backend {symbol} expected {declaration['filesystem']} "
            f"magic {declaration['magic']:#x}, found {magic:#x}"
        )
    info = os.stat(base)
    vfs = os.statvfs(base)
    return {
        "symbol": symbol,
        "base": str(base),
        "resolved_base": str(base.resolve()),
        "filesystem": declaration["filesystem"],
        "statfs_magic_hex": f"{magic:08x}",
        "device_major": os.major(info.st_dev),
        "device_minor": os.minor(info.st_dev),
        "mountinfo": _mount_line(base),
        "statvfs_block_size": vfs.f_frsize,
        "statvfs_blocks": vfs.f_blocks,
        "statvfs_blocks_available_at_start": vfs.f_bavail,
        "physical_substrate": {
            "status": "UNKNOWN",
            "reason": "guest filesystem identity does not identify host physical media",
        },
    }


@contextmanager
def fresh_directory(base: Path) -> Iterator[Path]:
    resolved_base = base.resolve()
    name = tempfile.mkdtemp(prefix="zero-ground-r0-", dir=resolved_base)
    directory = Path(name).resolve()
    if directory.parent != resolved_base:
        raise RuntimeError("temporary directory escaped declared backend")
    try:
        yield directory
    finally:
        if directory.parent != resolved_base or not directory.name.startswith("zero-ground-r0-"):
            raise RuntimeError("refusing unsafe temporary-directory cleanup")
        shutil.rmtree(directory)


def _write_all(fd: int, value: bytes) -> None:
    view = memoryview(value)
    while view:
        count = os.write(fd, view)
        if count <= 0:
            raise OSError("zero-progress write")
        view = view[count:]


def install_state(directory: Path, value: bytes, name: str = r0_record.STATE_NAME) -> None:
    path = directory / name
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    fd = os.open(path, flags, 0o600)
    try:
        _write_all(fd, value)
        os.fsync(fd)
    finally:
        os.close(fd)
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _worker_environment() -> dict[str, str]:
    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = "0"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def _read_exact(fd: int, count: int) -> bytes:
    chunks: list[bytes] = []
    remaining = count
    while remaining:
        chunk = os.read(fd, remaining)
        if not chunk:
            raise RuntimeError("worker closed stage pipe early")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def drive_publisher(
    directory: Path,
    digest: bytes,
    payload: bytes,
    *,
    cut: str = "NORMAL",
    inject: str | None = None,
    max_write: int = 0,
    skip_file_fsync: bool = False,
    skip_directory_fsync: bool = False,
    skip_replace: bool = False,
    skip_exclusive_creation: bool = False,
) -> PublisherOutcome:
    command = [
        sys.executable,
        "-I",
        "-B",
        str(WORKER),
        "publish",
        "--directory",
        str(directory),
        "--digest",
        digest.hex(),
        "--payload",
        payload.hex(),
    ]
    if inject:
        command.extend(("--inject", inject))
    if max_write:
        command.extend(("--max-write", str(max_write)))
    if skip_file_fsync:
        command.append("--skip-file-fsync")
    if skip_directory_fsync:
        command.append("--skip-directory-fsync")
    if skip_replace:
        command.append("--skip-replace")
    if skip_exclusive_creation:
        command.append("--skip-exclusive-creation")

    start_wall = time.monotonic_ns()
    start_cpu = _child_cpu_ns()
    process = subprocess.Popen(
        command,
        cwd=BASE,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        env=_worker_environment(),
    )
    assert process.stdout is not None and process.stderr is not None
    transcript = bytearray()
    injection_last_stage = {
        "write_before_half": 0,
        "write_after_half": 1,
        "file_fsync": 2,
        "replace": 3,
        "directory_fsync": 4,
    }

    try:
        for number in range(6):
            waited_pid, status = os.waitpid(process.pid, os.WUNTRACED)
            if waited_pid != process.pid or not os.WIFSTOPPED(status):
                raise RuntimeError(f"publisher did not stop at stage {number}")
            if os.WSTOPSIG(status) != signal.SIGSTOP:
                raise RuntimeError("publisher stopped with unexpected signal")
            frame = _read_exact(process.stdout.fileno(), 2)
            expected_frame = b"\xa0" + bytes([number])
            if frame != expected_frame:
                raise RuntimeError(
                    f"stage {number} frame {frame.hex()} != {expected_frame.hex()}"
                )
            transcript.extend(frame)

            if cut == f"K{number}":
                os.kill(process.pid, signal.SIGKILL)
                returncode = process.wait(timeout=5)
                tail = process.stdout.read()
                error = process.stderr.read()
                transcript.extend(tail)
                terminal = "SIGKILL" if returncode == -signal.SIGKILL else f"RC{returncode}"
                return PublisherOutcome(
                    bytes(transcript), terminal, returncode, error,
                    time.monotonic_ns() - start_wall,
                    _child_cpu_ns() - start_cpu,
                )

            os.kill(process.pid, signal.SIGCONT)
            if inject and injection_last_stage[inject] == number:
                break

        returncode = process.wait(timeout=5)
        tail = process.stdout.read()
        error = process.stderr.read()
        transcript.extend(tail)
        terminal = f"EXIT{returncode}"
        return PublisherOutcome(
            bytes(transcript), terminal, returncode, error,
            time.monotonic_ns() - start_wall,
            _child_cpu_ns() - start_cpu,
        )
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        process.stdout.close()
        process.stderr.close()


def run_recovery(directory: Path, digest: bytes,
                 continuation: bytes) -> RecoveryOutcome:
    command = [
        sys.executable,
        "-I",
        "-B",
        str(WORKER),
        "recover",
        "--directory",
        str(directory),
        "--digest",
        digest.hex(),
        "--continuation",
        continuation.hex(),
    ]
    start_wall = time.monotonic_ns()
    start_cpu = _child_cpu_ns()
    completed = subprocess.run(
        command,
        cwd=BASE,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
        check=False,
        env=_worker_environment(),
    )
    return RecoveryOutcome(
        completed.stdout,
        completed.returncode,
        completed.stderr,
        time.monotonic_ns() - start_wall,
        _child_cpu_ns() - start_cpu,
    )


def _case_values(case: str) -> tuple[bytes | None, bytes, str, str]:
    if case == "CREATE":
        return None, r0_adapter.P0, "ABSENT", "P0"
    if case == "UPDATE":
        return r0_adapter.P0, r0_adapter.P1, "P0", "P1"
    raise AssertionError(case)


def _expected_at_cut(case: str, cut: str) -> str:
    _, _, old_label, new_label = _case_values(case)
    return old_label if cut in ("K0", "K1", "K2", "K3") else new_label


def _state_measurement(directory: Path) -> dict[str, int]:
    result: dict[str, int] = {
        "authoritative_exists": 0,
        "authoritative_logical_bytes": 0,
        "authoritative_allocated_bytes": 0,
        "temporary_exists": 0,
        "temporary_logical_bytes": 0,
        "temporary_allocated_bytes": 0,
        "directory_entries": 0,
    }
    for entry in directory.iterdir():
        result["directory_entries"] += 1
        info = entry.lstat()
        if entry.name == r0_record.STATE_NAME:
            result["authoritative_exists"] = 1
            result["authoritative_logical_bytes"] = info.st_size
            result["authoritative_allocated_bytes"] = info.st_blocks * 512
        elif entry.name == r0_record.TEMP_NAME:
            result["temporary_exists"] = 1
            result["temporary_logical_bytes"] = info.st_size
            result["temporary_allocated_bytes"] = info.st_blocks * 512
    return result


def _stage_prefix(last_stage: int) -> bytes:
    return b"".join(b"\xa0" + bytes([number]) for number in range(last_stage + 1))


def run_publication_matrix(
    experiment: Experiment,
    backend_symbols: tuple[str, ...],
    repetitions: int,
    *,
    category: str = "conformance",
    variant: str = "candidate",
    skip_file_fsync: bool = False,
    skip_directory_fsync: bool = False,
    skip_replace: bool = False,
    skip_exclusive_creation: bool = False,
) -> None:
    for backend in backend_symbols:
        base = BACKENDS[backend]["base"]
        assert isinstance(base, Path)
        for case in CASES:
            old_payload, new_payload, _, _ = _case_values(case)
            old_record = b"" if old_payload is None else r0_record.encode_record(
                experiment.d, old_payload
            )
            new_record = r0_record.encode_record(experiment.d, new_payload)
            for cut in CUTS:
                for repetition in range(repetitions):
                    with fresh_directory(base) as directory:
                        if old_payload is not None:
                            install_state(directory, old_record)
                        publisher = drive_publisher(
                            directory,
                            experiment.d,
                            new_payload,
                            cut=cut,
                            skip_file_fsync=skip_file_fsync,
                            skip_directory_fsync=skip_directory_fsync,
                            skip_replace=skip_replace,
                            skip_exclusive_creation=skip_exclusive_creation,
                        )
                        storage = _state_measurement(directory)
                        recovery = run_recovery(directory, experiment.d, r0_adapter.C)

                    expected_label = _expected_at_cut(case, cut)
                    expected = literal_expected(expected_label)
                    if cut == "NORMAL":
                        expected_publisher = _stage_prefix(5)
                        publisher_ok = (
                            publisher.returncode == 0
                            and publisher.terminal == "EXIT0"
                            and publisher.transcript == expected_publisher
                            and publisher.stderr == b""
                        )
                    else:
                        number = int(cut[1:])
                        expected_publisher = _stage_prefix(number)
                        publisher_ok = (
                            publisher.returncode == -signal.SIGKILL
                            and publisher.terminal == "SIGKILL"
                            and publisher.transcript == expected_publisher
                            and publisher.stderr == b""
                        )
                    recovery_ok = (
                        recovery.returncode == 0
                        and recovery.stderr == b""
                        and oracle_accepts(expected_label, recovery.observation)
                    )
                    trial_id = (
                        f"{category}/{variant}/{backend}/{case}/{cut}/"
                        f"repeat-{repetition}"
                    )
                    experiment.add(TrialResult(
                        trial_id=trial_id,
                        category=category,
                        expected=expected,
                        observed=recovery.observation,
                        fields={
                            "backend": _b(backend),
                            "case": _b(case),
                            "cut": _b(cut),
                            "repetition": _b(repetition),
                            "variant": _b(variant),
                            "old_record": old_record,
                            "new_record": new_record,
                            "publisher_transcript": publisher.transcript,
                            "publisher_terminal": _b(publisher.terminal),
                            "publisher_returncode": _b(publisher.returncode),
                            "publisher_stderr": publisher.stderr,
                            "recovery_returncode": _b(recovery.returncode),
                            "recovery_stderr": recovery.stderr,
                        },
                        passed=publisher_ok and recovery_ok,
                        wall_ns=publisher.wall_ns + recovery.wall_ns,
                        child_cpu_ns=publisher.child_cpu_ns + recovery.child_cpu_ns,
                        explanation=(
                            "exact old/new cut row"
                            if publisher_ok and recovery_ok
                            else "publisher protocol or recovery observation differs"
                        ),
                        measurement={
                            "publisher_wall_ns": publisher.wall_ns,
                            "recovery_wall_ns": recovery.wall_ns,
                            "publisher_child_cpu_ns": publisher.child_cpu_ns,
                            "recovery_child_cpu_ns": recovery.child_cpu_ns,
                            "storage_at_recovery": storage,
                        },
                    ))


def _run_fault_recovery(
    experiment: Experiment,
    backend: str,
    payload_label: str,
    fault_id: str,
    source_record: bytes,
    installed_record: bytes | None,
    expected_label: str,
    *,
    symlink: bool = False,
    explanation: str = "record fault",
) -> None:
    base = BACKENDS[backend]["base"]
    assert isinstance(base, Path)
    with fresh_directory(base) as directory:
        if symlink:
            install_state(directory, source_record, "target.bin")
            os.symlink("target.bin", directory / r0_record.STATE_NAME)
        elif installed_record is not None:
            install_state(directory, installed_record)
        storage = _state_measurement(directory)
        recovery = run_recovery(directory, experiment.d, r0_adapter.C)
    expected = literal_expected(expected_label)
    passed = (
        recovery.returncode == 0
        and recovery.stderr == b""
        and oracle_accepts(expected_label, recovery.observation)
    )
    experiment.add(TrialResult(
        trial_id=f"conformance/record-fault/{backend}/{payload_label}/{fault_id}",
        category="conformance",
        expected=expected,
        observed=recovery.observation,
        fields={
            "backend": _b(backend),
            "payload_label": _b(payload_label),
            "fault": _b(fault_id),
            "source_record": source_record,
            "installed_record": b"" if installed_record is None else installed_record,
            "installed_record_status": _b("MISSING" if installed_record is None else "PRESENT"),
            "symlink": _b(symlink),
            "recovery_returncode": _b(recovery.returncode),
            "recovery_stderr": recovery.stderr,
        },
        passed=passed,
        wall_ns=recovery.wall_ns,
        child_cpu_ns=recovery.child_cpu_ns,
        explanation=explanation if passed else f"{explanation}: unexpected recovery",
        measurement={
            "recovery_wall_ns": recovery.wall_ns,
            "recovery_child_cpu_ns": recovery.child_cpu_ns,
            "storage_at_recovery": storage,
        },
    ))


def run_record_fault_matrix(experiment: Experiment,
                            backend_symbols: tuple[str, ...]) -> None:
    payloads = (("P0", r0_adapter.P0), ("P1", r0_adapter.P1))
    for backend in backend_symbols:
        base = BACKENDS[backend]["base"]
        assert isinstance(base, Path)
        for payload_label, payload in payloads:
            case = "CREATE" if payload_label == "P0" else "UPDATE"
            old_payload, _, _, _ = _case_values(case)
            with fresh_directory(base) as source_directory:
                if old_payload is not None:
                    install_state(
                        source_directory,
                        r0_record.encode_record(experiment.d, old_payload),
                    )
                publisher = drive_publisher(
                    source_directory, experiment.d, payload, cut="NORMAL"
                )
                source = (source_directory / r0_record.STATE_NAME).read_bytes()
                source_storage = _state_measurement(source_directory)
                source_recovery = run_recovery(
                    source_directory, experiment.d, r0_adapter.C
                )
            expected_source = r0_record.encode_record(experiment.d, payload)
            expected_observation = literal_expected(payload_label)
            source_passed = (
                publisher.returncode == 0
                and publisher.stderr == b""
                and publisher.transcript == _stage_prefix(5)
                and source == expected_source
                and source_recovery.returncode == 0
                and source_recovery.stderr == b""
                and source_recovery.observation == expected_observation
            )
            experiment.add(TrialResult(
                trial_id=f"conformance/fault-source/{backend}/{payload_label}",
                category="conformance",
                expected=expected_observation,
                observed=source_recovery.observation,
                fields={
                    "backend": _b(backend),
                    "case": _b(case),
                    "payload_label": _b(payload_label),
                    "source_record": source,
                    "expected_record": expected_source,
                    "publisher_transcript": publisher.transcript,
                    "publisher_terminal": _b(publisher.terminal),
                    "publisher_returncode": _b(publisher.returncode),
                    "publisher_stderr": publisher.stderr,
                    "recovery_returncode": _b(source_recovery.returncode),
                    "recovery_stderr": source_recovery.stderr,
                },
                passed=source_passed,
                wall_ns=publisher.wall_ns + source_recovery.wall_ns,
                child_cpu_ns=publisher.child_cpu_ns + source_recovery.child_cpu_ns,
                explanation="normally published source copied into fresh fault trials",
                measurement={
                    "publisher_wall_ns": publisher.wall_ns,
                    "recovery_wall_ns": source_recovery.wall_ns,
                    "storage_at_recovery": source_storage,
                },
            ))
            _run_fault_recovery(
                experiment, backend, payload_label, "MISSING", source, None,
                "ABSENT",
            )
            for length in range(len(source)):
                _run_fault_recovery(
                    experiment, backend, payload_label, f"TRUNCATE-{length:04d}",
                    source, source[:length], "REJECT",
                )
            for index in range(len(source)):
                for bit in range(8):
                    changed = bytearray(source)
                    changed[index] ^= 1 << bit
                    _run_fault_recovery(
                        experiment, backend, payload_label,
                        f"FLIP-{index:04d}-{bit}", source, bytes(changed), "REJECT",
                    )
            _run_fault_recovery(
                experiment, backend, payload_label, "APPEND_ZERO", source,
                source + b"\x00", "REJECT",
            )
            wrong_digest = bytes([experiment.d[0] ^ 0x80]) + experiment.d[1:]
            wrong = r0_record.encode_record(wrong_digest, payload)
            _run_fault_recovery(
                experiment, backend, payload_label, "WRONG_SUITE", source,
                wrong, "REJECT",
            )
            _run_fault_recovery(
                experiment, backend, payload_label, "NONREGULAR", source,
                source, "REJECT", symlink=True,
            )

        record0 = r0_record.encode_record(experiment.d, r0_adapter.P0)
        record1 = r0_record.encode_record(experiment.d, r0_adapter.P1)
        _run_fault_recovery(
            experiment, backend, "P1", "STALE_VALID", record1, record0, "P0",
            explanation="UNDETECTED_STALE",
        )
        _run_fault_recovery(
            experiment, backend, "P0", "OTHER_VALID-P1", record0, record1, "P1",
            explanation="UNDETECTED_COHERENT_REPLACEMENT",
        )
        _run_fault_recovery(
            experiment, backend, "P1", "OTHER_VALID-P0", record1, record0, "P0",
            explanation="UNDETECTED_COHERENT_REPLACEMENT",
        )


def run_io_fault_matrix(experiment: Experiment,
                        backend_symbols: tuple[str, ...]) -> None:
    error_tail = {
        "write_before_half": b"\xaf\x01",
        "write_after_half": b"\xaf\x01",
        "file_fsync": b"\xaf\x02",
        "replace": b"\xaf\x03",
        "directory_fsync": b"\xaf\x04",
    }
    last_stage = {
        "write_before_half": 0,
        "write_after_half": 1,
        "file_fsync": 2,
        "replace": 3,
        "directory_fsync": 4,
    }
    for backend in backend_symbols:
        base = BACKENDS[backend]["base"]
        assert isinstance(base, Path)
        for case in CASES:
            old_payload, new_payload, old_label, new_label = _case_values(case)
            old_record = b"" if old_payload is None else r0_record.encode_record(
                experiment.d, old_payload
            )
            new_record = r0_record.encode_record(experiment.d, new_payload)

            for maximum in SHORT_WRITE_SIZES:
                with fresh_directory(base) as directory:
                    if old_payload is not None:
                        install_state(directory, old_record)
                    publisher = drive_publisher(
                        directory, experiment.d, new_payload,
                        cut="NORMAL", max_write=maximum,
                    )
                    storage = _state_measurement(directory)
                    recovery = run_recovery(directory, experiment.d, r0_adapter.C)
                publisher_ok = (
                    publisher.returncode == 0
                    and publisher.stderr == b""
                    and publisher.transcript == _stage_prefix(5)
                )
                recovery_ok = (
                    recovery.returncode == 0
                    and recovery.stderr == b""
                    and oracle_accepts(new_label, recovery.observation)
                )
                experiment.add(TrialResult(
                    trial_id=f"conformance/io/{backend}/{case}/SHORT_WRITE-{maximum}",
                    category="conformance",
                    expected=literal_expected(new_label),
                    observed=recovery.observation,
                    fields={
                        "backend": _b(backend),
                        "case": _b(case),
                        "fault": _b(f"SHORT_WRITE({maximum})"),
                        "old_record": old_record,
                        "new_record": new_record,
                        "publisher_transcript": publisher.transcript,
                        "publisher_terminal": _b(publisher.terminal),
                        "publisher_returncode": _b(publisher.returncode),
                        "publisher_stderr": publisher.stderr,
                        "recovery_returncode": _b(recovery.returncode),
                        "recovery_stderr": recovery.stderr,
                    },
                    passed=publisher_ok and recovery_ok,
                    wall_ns=publisher.wall_ns + recovery.wall_ns,
                    child_cpu_ns=publisher.child_cpu_ns + recovery.child_cpu_ns,
                    explanation="short-write retry",
                    measurement={
                        "publisher_wall_ns": publisher.wall_ns,
                        "recovery_wall_ns": recovery.wall_ns,
                        "storage_at_recovery": storage,
                    },
                ))

            for fault in IO_FAULTS:
                with fresh_directory(base) as directory:
                    if old_payload is not None:
                        install_state(directory, old_record)
                    publisher = drive_publisher(
                        directory, experiment.d, new_payload,
                        cut="NORMAL", inject=fault,
                    )
                    storage = _state_measurement(directory)
                    recovery = run_recovery(directory, experiment.d, r0_adapter.C)
                expected_label = new_label if fault == "directory_fsync" else old_label
                expected_transcript = _stage_prefix(last_stage[fault]) + error_tail[fault]
                publisher_ok = (
                    publisher.returncode == 70
                    and publisher.terminal == "EXIT70"
                    and publisher.stderr == b""
                    and publisher.transcript == expected_transcript
                )
                recovery_ok = (
                    recovery.returncode == 0
                    and recovery.stderr == b""
                    and oracle_accepts(expected_label, recovery.observation)
                )
                experiment.add(TrialResult(
                    trial_id=f"conformance/io/{backend}/{case}/{fault}",
                    category="conformance",
                    expected=literal_expected(expected_label),
                    observed=recovery.observation,
                    fields={
                        "backend": _b(backend),
                        "case": _b(case),
                        "fault": _b(fault),
                        "old_record": old_record,
                        "new_record": new_record,
                        "publisher_transcript": publisher.transcript,
                        "publisher_terminal": _b(publisher.terminal),
                        "publisher_returncode": _b(publisher.returncode),
                        "publisher_stderr": publisher.stderr,
                        "recovery_returncode": _b(recovery.returncode),
                        "recovery_stderr": recovery.stderr,
                    },
                    passed=publisher_ok and recovery_ok,
                    wall_ns=publisher.wall_ns + recovery.wall_ns,
                    child_cpu_ns=publisher.child_cpu_ns + recovery.child_cpu_ns,
                    explanation="deterministic wrapper-level simulation",
                    measurement={
                        "publisher_wall_ns": publisher.wall_ns,
                        "recovery_wall_ns": recovery.wall_ns,
                        "storage_at_recovery": storage,
                        "fault_is_simulated": True,
                    },
                ))


def _no_digest_encode(digest: bytes, payload: bytes) -> bytes:
    return payload + r0_record.record_hash(digest, payload)


def _no_digest_recover(data: bytes | None, digest: bytes) -> bytes:
    if data is None:
        return literal_expected("ABSENT")
    if len(data) < 32 or len(data) > 32 + r0_record.MAX_OPAQUE:
        return literal_expected("REJECT")
    payload = data[:-32]
    observed_hash = data[-32:]
    if observed_hash != r0_record.record_hash(digest, payload):
        return literal_expected("REJECT")
    try:
        first = r0_adapter.apply(payload, r0_adapter.C)
        second = r0_adapter.apply(payload, r0_adapter.C)
    except Exception:
        return literal_expected("REJECT")
    if first != second:
        return literal_expected("REJECT")
    return r0_record.ok_observation(first)


def _no_hash_recover(data: bytes | None, digest: bytes) -> bytes:
    if data is None:
        return literal_expected("ABSENT")
    if len(data) < 32 or len(data) > 32 + r0_record.MAX_OPAQUE:
        return literal_expected("REJECT")
    if data[:32] != digest:
        return literal_expected("REJECT")
    try:
        value = r0_adapter.apply(data[32:], r0_adapter.C)
    except Exception:
        return literal_expected("REJECT")
    return r0_record.ok_observation(value)


def evaluate_component_deletions(experiment: Experiment) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def check(identifier: str, expected: bytes, observed: bytes) -> None:
        checks.append({
            "id": identifier,
            "expected_hex": expected.hex(),
            "observed_hex": observed.hex(),
            "passed": expected == observed,
        })

    no_digest_records: dict[str, bytes] = {}
    wrong_digest = bytes([experiment.d[0] ^ 0x80]) + experiment.d[1:]
    for label, payload in (("P0", r0_adapter.P0), ("P1", r0_adapter.P1)):
        record = _no_digest_encode(experiment.d, payload)
        no_digest_records[label] = record
        check(f"no-digest/valid/{label}", literal_expected(label),
              _no_digest_recover(record, experiment.d))
        check(f"no-digest/missing/{label}", literal_expected("ABSENT"),
              _no_digest_recover(None, experiment.d))
        for length in range(len(record)):
            check(
                f"no-digest/truncate/{label}/{length}",
                literal_expected("REJECT"),
                _no_digest_recover(record[:length], experiment.d),
            )
        for index in range(len(record)):
            for bit in range(8):
                changed = bytearray(record)
                changed[index] ^= 1 << bit
                check(
                    f"no-digest/flip/{label}/{index}/{bit}",
                    literal_expected("REJECT"),
                    _no_digest_recover(bytes(changed), experiment.d),
                )
        check(
            f"no-digest/append/{label}",
            literal_expected("REJECT"),
            _no_digest_recover(record + b"\x00", experiment.d),
        )
        coherent_wrong = payload + r0_record.record_hash(wrong_digest, payload)
        check(
            f"no-digest/wrong-suite/{label}",
            literal_expected("REJECT"),
            _no_digest_recover(coherent_wrong, experiment.d),
        )

    check(
        "no-digest/coherent/P0-to-P1",
        literal_expected("P1"),
        _no_digest_recover(no_digest_records["P1"], experiment.d),
    )
    check(
        "no-digest/coherent/P1-to-P0",
        literal_expected("P0"),
        _no_digest_recover(no_digest_records["P0"], experiment.d),
    )

    encoded_checks = [
        _canonical_fields({
            "id": _b(item["id"]),
            "expected": bytes.fromhex(str(item["expected_hex"])),
            "observed": bytes.fromhex(str(item["observed_hex"])),
            "passed": _b(bool(item["passed"])),
        })
        for item in sorted(checks, key=lambda item: str(item["id"]))
    ]
    no_digest_stream = b"".join(_lp8(item) for item in encoded_checks)
    no_digest_failures = [str(item["id"]) for item in checks if not item["passed"]]

    no_hash_p0 = experiment.d + r0_adapter.P0
    no_hash_appended = no_hash_p0 + b"\x00"
    no_hash_observed = _no_hash_recover(no_hash_appended, experiment.d)
    no_hash_expected = literal_expected("REJECT")

    retained_hash0 = r0_record.record_hash(experiment.d, r0_adapter.P0)
    retained_hash1 = r0_record.record_hash(experiment.d, r0_adapter.P1)
    lookup = {
        retained_hash0: literal_expected("P0"),
        retained_hash1: literal_expected("P1"),
    }
    omitted_payload0 = experiment.d + retained_hash0
    omitted_payload1 = experiment.d + retained_hash1
    lookup_outputs = (
        lookup[omitted_payload0[-32:]],
        lookup[omitted_payload1[-32:]],
    )
    no_influence = experiment.d + hashlib.sha256(
        b"PAYLOAD-INFLUENCE-DELETED\x00" + experiment.d
    ).digest()

    return {
        "in_band_suite_digest": {
            "verdict": "MAY_REBUILD_WITHIN_R0",
            "recipe": (
                "omit the 32-byte in-band D; split the last 32 bytes as H; "
                "recompute H from the trusted expected D, uint64 payload length, "
                "payload, and the exact record tag"
            ),
            "external_state": "the recovery bundle's existing trusted 32-byte D",
            "exhaustive_adapted_checks": len(checks),
            "failures": no_digest_failures,
            "certificate_sha256": hashlib.sha256(no_digest_stream).hexdigest(),
            "certificate_bytes": len(no_digest_stream),
            "candidate_record_sizes": {
                "P0": len(no_digest_records["P0"]),
                "P1": len(no_digest_records["P1"]),
            },
            "scope": "adapted finite R0 record-fault suite; path checks unchanged",
            "execution_boundary": (
                "in-process alternate encoder/parser falsification; not a second "
                "fresh-process realization run"
            ),
        },
        "integrity_comparison_value": {
            "verdict": "MUST_SURVIVE_AS_RESPONSIBILITY_WITHIN_R0",
            "deleted_variant": "D || P with no H or equivalent comparison value",
            "minimal_witness": {
                "history": "valid no-H P0 followed by APPEND_ZERO",
                "candidate_bytes_before_hex": no_hash_p0.hex(),
                "candidate_bytes_after_hex": no_hash_appended.hex(),
                "required_hex": no_hash_expected.hex(),
                "observed_hex": no_hash_observed.hex(),
                "distinction": "required REJECT versus accepted OK(Y1)",
            },
        },
        "payload_bytes": {
            "verdict": "MAY_REBUILD_ONLY_IF_DISTINCTION_AND_LOOKUP_SURVIVE",
            "retained_hash_records_distinct": omitted_payload0 != omitted_payload1,
            "lookup_outputs_hex": [value.hex() for value in lookup_outputs],
            "externalized_lookup_entries": 2,
            "externalized_lookup_key_bytes": 64,
            "explanation": (
                "removing raw P does not remove its distinction when H still "
                "depends on P; recovery then requires a frozen H-to-result table"
            ),
            "delete_payload_influence_collision": {
                "left_hex": no_influence.hex(),
                "right_hex": no_influence.hex(),
                "continuation_hex": r0_adapter.C.hex(),
                "required_left_hex": literal_expected("P0").hex(),
                "required_right_hex": literal_expected("P1").hex(),
            },
        },
        "all_persisted_bytes": {
            "verdict": "MUST_SURVIVE_AS_DISTINCTION_WITHIN_R0",
            "left_encoding_hex": "",
            "right_encoding_hex": "",
            "continuation_hex": r0_adapter.C.hex(),
            "required_left_hex": literal_expected("P0").hex(),
            "required_right_hex": literal_expected("P1").hex(),
        },
    }


def run_mechanism_deletions(experiment: Experiment,
                            backend_symbols: tuple[str, ...]) -> None:
    variants = (
        ("delete-file-fsync", True, False, False, False),
        ("delete-directory-fsync", False, True, False, False),
        ("delete-replace", False, False, True, False),
        ("delete-exclusive-creation", False, False, False, True),
    )
    for name, skip_file, skip_directory, skip_replace, skip_exclusive in variants:
        run_publication_matrix(
            experiment,
            backend_symbols,
            1,
            category="attack",
            variant=name,
            skip_file_fsync=skip_file,
            skip_directory_fsync=skip_directory,
            skip_replace=skip_replace,
            skip_exclusive_creation=skip_exclusive,
        )

    for name, _, _, _, _ in variants:
        selected = [
            result for result in experiment.results
            if result.category == "attack" and f"/{name}/" in result.trial_id
        ]
        failures = sorted(
            (result for result in selected if not result.passed),
            key=lambda result: (
                result.fields["case"] != b"CREATE",
                CUTS.index(result.fields["cut"].decode()),
                result.fields["backend"],
                result.trial_id,
            ),
        )
        if failures:
            first = failures[0]
            finding: dict[str, object] = {
                "verdict": "WITNESSED_REQUIRED_WITHIN_R0",
                "executed_rows": len(selected),
                "differing_rows": len(failures),
                "smallest_observed_witness": {
                    "trial_id": first.trial_id,
                    "expected_hex": first.expected.hex(),
                    "observed_hex": first.observed.hex(),
                },
            }
        else:
            finding = {
                "verdict": "NO_WITNESS_IN_R0",
                "executed_rows": len(selected),
                "differing_rows": 0,
                "larger_power_loss_contract": "UNKNOWN",
            }
        experiment.deletion_findings[name] = finding

    experiment.deletion_findings["delete-process-reaping"] = {
        "verdict": "UNKNOWN_NOT_EXECUTED",
        "reason": (
            "the process helper deliberately cannot return a killed publisher "
            "before wait/reap; removing this isolation condition needs a distinct "
            "supervisor implementation"
        ),
        "credited_complexity": "not zero; wait/process-isolation remains in TCB",
    }
    experiment.deletion_findings["delete-adapter"] = {
        "verdict": "WITNESSED_REQUIRED_AS_RESPONSIBILITY_WITHIN_R0",
        "witness": "P0 and P1 under C require unequal Y0 and Y1",
        "component_constructor_required": False,
    }
    experiment.deletion_findings["delete-verifier"] = {
        "verdict": "EXTERNAL_OBSERVATION_CANNOT_BE_ESTABLISHED",
        "reason": "expected/actual comparison would move to a human or another service",
    }
    experiment.deletion_findings["delete-backend-validator"] = {
        "verdict": "UNKNOWN_NOT_EXECUTED",
        "reason": "all realization trials abort unless statfs and mount selection are proved",
        "credited_complexity": "selector and validator remain in TCB",
    }
    experiment.deletion_findings["delete-stage-supervisor"] = {
        "verdict": "UNKNOWN_NOT_EXECUTED",
        "reason": "no independent mechanism was supplied to place all exact live-process cuts",
        "credited_complexity": "stage scheduling and process control remain in TCB",
    }


def run_common_mode_controls(experiment: Experiment) -> None:
    correct = literal_expected("P1")
    mutated_table_value = literal_expected("P0")
    table_mutation_caught = not oracle_accepts("P1", mutated_table_value)

    record = bytearray(r0_record.encode_record(experiment.d, r0_adapter.P1))
    record[-1] ^= 1
    candidate_rejected = False
    try:
        r0_record.parse_record(bytes(record), experiment.d)
    except r0_record.RecordReject:
        candidate_rejected = True
    mutant_ignore_hash_output = literal_expected("P1")
    parser_mutation_caught = not oracle_accepts("REJECT", mutant_ignore_hash_output)

    experiment.common_mode = {
        "literal_oracle_calls_candidate_adapter": False,
        "literal_oracle_calls_candidate_parser": False,
        "table_mutation": {
            "expected_hex": correct.hex(),
            "mutated_hex": mutated_table_value.hex(),
            "checker_caught": table_mutation_caught,
        },
        "ignore_hash_parser_mutation": {
            "candidate_parser_rejected_corruption": candidate_rejected,
            "mutant_output_hex": mutant_ignore_hash_output.hex(),
            "required_hex": literal_expected("REJECT").hex(),
            "checker_caught": parser_mutation_caught,
        },
        "residual_common_mode_risk": (
            "supervisor, literal table, suite author, and trial generator share "
            "one Python repository and operating environment"
        ),
    }
    if not table_mutation_caught or not parser_mutation_caught or not candidate_rejected:
        raise AssertionError("common-mode negative control failed")


def _semantic_cross_backend(experiment: Experiment) -> dict[str, object]:
    maps: dict[str, dict[str, str]] = {symbol: {} for symbol in experiment.backend_info}
    for result in experiment.results:
        if result.category != "conformance":
            continue
        backend = result.fields.get("backend", b"").decode("ascii", "ignore")
        if backend not in maps:
            continue
        normalized = result.trial_id.replace(f"/{backend}/", "/{BACKEND}/", 1)
        maps[backend][normalized] = result.observed.hex()
    symbols = sorted(maps)
    if len(symbols) != 2:
        return {
            "status": "UNKNOWN",
            "reason": "cross-backend comparison requires both E and T",
        }
    left, right = symbols
    left_keys = set(maps[left])
    right_keys = set(maps[right])
    differing = sorted(
        key for key in left_keys & right_keys if maps[left][key] != maps[right][key]
    )
    return {
        "status": "PASS" if left_keys == right_keys and not differing else "FAIL",
        "left": left,
        "right": right,
        "comparable_trials": len(left_keys & right_keys),
        "left_only": sorted(left_keys - right_keys),
        "right_only": sorted(right_keys - left_keys),
        "differing_observations": differing,
        "claim": "guest-level semantic equality in the finite R0 suite only",
    }


ARTIFACT_NAMES = (
    "REALIZATION-CONTRACT-R0.md",
    "r0_adapter.py",
    "r0_record.py",
    "r0_worker.py",
    "r0_realization.py",
    "test_realization_r0.py",
)


def _source_inventory() -> dict[str, object]:
    files: list[dict[str, object]] = []
    for name in ARTIFACT_NAMES:
        path = BASE / name
        if not path.is_file():
            raise RuntimeError(f"required R0 artifact missing: {name}")
        contents = path.read_bytes()
        text = contents.decode("utf-8")
        lines = text.splitlines()
        files.append({
            "name": name,
            "bytes": len(contents),
            "physical_lines": len(lines),
            "nonblank_lines": sum(bool(line.strip()) for line in lines),
            "sha256": hashlib.sha256(contents).hexdigest(),
        })
    canonical = b"".join(
        _lp4(str(item["name"]).encode())
        + bytes.fromhex(str(item["sha256"]))
        + struct.pack(">Q", int(item["bytes"]))
        for item in files
    )
    return {
        "files": files,
        "file_count": len(files),
        "total_bytes": sum(int(item["bytes"]) for item in files),
        "total_physical_lines": sum(int(item["physical_lines"]) for item in files),
        "artifact_inventory_sha256": hashlib.sha256(canonical).hexdigest(),
        "adapter_manifest_bytes": len(r0_record.canonical_bundle_manifest(BASE)),
        "adapter_bundle_names": list(r0_record.BUNDLE_NAMES),
    }


def _summary_distribution(values: list[int]) -> dict[str, object]:
    if not values:
        return {"status": "UNKNOWN", "reason": "no samples"}
    ordered = sorted(values)
    p95_index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "samples": len(ordered),
        "min": ordered[0],
        "median": int(statistics.median(ordered)),
        "p95": ordered[p95_index],
        "max": ordered[-1],
        "sum": sum(ordered),
    }


def _timing_measurements(experiment: Experiment) -> dict[str, object]:
    publication_wall = [
        int(result.measurement["publisher_wall_ns"])
        for result in experiment.results
        if "publisher_wall_ns" in result.measurement
    ]
    recovery_wall = [
        int(result.measurement["recovery_wall_ns"])
        for result in experiment.results
        if "recovery_wall_ns" in result.measurement
    ]
    return {
        "unit": "nanoseconds",
        "all_trial_wall": _summary_distribution([result.wall_ns for result in experiment.results]),
        "all_trial_child_cpu": _summary_distribution([
            result.child_cpu_ns for result in experiment.results
        ]),
        "publisher_wall": _summary_distribution(publication_wall),
        "recovery_wall": _summary_distribution(recovery_wall),
        "internal_write_fsync_replace_phase_timing": {
            "status": "UNKNOWN",
            "reason": (
                "no metrics channel was added to the worker; adding one would "
                "change the exact isolation surface"
            ),
        },
        "certificate_inclusion": False,
    }


def _storage_measurements(experiment: Experiment,
                          inventory: dict[str, object]) -> dict[str, object]:
    samples = [
        result.measurement["storage_at_recovery"]
        for result in experiment.results
        if "storage_at_recovery" in result.measurement
    ]
    keys = (
        "authoritative_logical_bytes",
        "authoritative_allocated_bytes",
        "temporary_logical_bytes",
        "temporary_allocated_bytes",
        "directory_entries",
    )
    maxima = {
        key: max((int(sample[key]) for sample in samples), default=0)
        for key in keys
    }
    maxima["peak_simultaneous_logical_file_bytes"] = max(
        (
            int(sample["authoritative_logical_bytes"])
            + int(sample["temporary_logical_bytes"])
            for sample in samples
        ),
        default=0,
    )
    return {
        "candidate_record_logical_bytes": {"P0": 64, "P1": 65},
        "candidate_in_band_overhead_bytes": 64,
        "suite_digest_binary_bytes": 32,
        "suite_digest_hex_text_characters_in_reports": 64,
        "external_expected_digest_bytes": 32,
        "observed_maxima": maxima,
        "experiment_artifact_bytes": inventory["total_bytes"],
        "adapter_manifest_bytes": inventory["adapter_manifest_bytes"],
        "interpreter_runtime_bytes": {
            "status": "UNKNOWN",
            "reason": "shared libraries, mapped pages, and filesystem cache not attributed",
        },
        "filesystem_directory_inode_allocation": {
            "status": "UNKNOWN",
            "reason": "st_blocks is not a complete directory/inode allocation measure",
        },
        "total_system_storage": {
            "status": "UNKNOWN",
            "reason": "shared kernel, runtime, hypervisor, host, and physical-media bytes unavailable",
        },
    }


def _environment_measurements() -> dict[str, object]:
    product_path = Path("/sys/class/dmi/id/product_name")
    product = product_path.read_text(encoding="utf-8").strip() if product_path.is_file() else None
    swaps = Path("/proc/swaps").read_text(encoding="utf-8") if Path("/proc/swaps").is_file() else None
    return {
        "kernel": platform.release(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "libc": list(platform.libc_ver()),
        "virtualization_product": product,
        "proc_swaps": swaps,
        "strace_available": Path("/usr/bin/strace").is_file(),
        "strace_used": False,
        "physical_media_identity": {
            "status": "UNKNOWN",
            "reason": "not exposed by the guest",
        },
    }


def _tcb_ledger() -> dict[str, object]:
    return {
        "common": [
            "frozen suite and external literal verifier table",
            "r0_adapter.py",
            "r0_record.py",
            "r0_worker.py",
            "worker local contract/bundle-to-suite-digest guard",
            "r0_realization.py supervisor, generator, injector, and serializer",
            "CPython interpreter and imported standard-library modules",
            "glibc statfs interface",
            "Linux VFS, process, signal, scheduler, pipe, and wait machinery",
            "SHA-256 implementation and finite non-collision assumption",
            "configured paths plus statfs and mountinfo validation",
        ],
        "E": [
            "Linux ext4 implementation",
            "guest block and virtual controller stack",
            "hypervisor/QEMU implementation (version and bytes UNKNOWN)",
            "host storage, controller, cache, flush path, and physical medium UNKNOWN",
        ],
        "T": [
            "Linux tmpfs and VM implementations",
            "guest swap subsystem and possible swapfile path",
            "hypervisor/QEMU memory implementation (version and bytes UNKNOWN)",
            "host RAM, swap, storage, controller, and physical medium UNKNOWN",
        ],
        "externalized": {
            "expected_suite_digest": "32 trusted bytes in recovery bundle",
            "expected_answers": "five frozen strings and literal observations in verifier",
            "trial_progress": "supervisor stage protocol and process control",
            "cleanup": "supervisor removes validated fresh directories",
            "freshness_generation_authority": "UNSUPPORTED; stored nowhere",
            "power_loss_and_physical_independence": "UNKNOWN; not observed",
        },
        "whole_tcb_code_bytes": {
            "status": "UNKNOWN",
            "reason": "kernel, filesystem, libc, interpreter, hypervisor, and host sizes incomplete",
        },
    }


def _result_counts(experiment: Experiment) -> dict[str, object]:
    counts: dict[str, dict[str, int]] = {}
    for result in experiment.results:
        group = counts.setdefault(result.category, {"total": 0, "passed": 0, "failed": 0})
        group["total"] += 1
        group["passed" if result.passed else "failed"] += 1
    conformance = [result for result in experiment.results if result.category == "conformance"]
    return {
        "by_category": counts,
        "conformance_kinds": {
            "publication": sum("/candidate/" in result.trial_id for result in conformance),
            "fault_source_publications": sum(
                "/fault-source/" in result.trial_id for result in conformance
            ),
            "record_fault": sum("/record-fault/" in result.trial_id for result in conformance),
            "io": sum("/io/" in result.trial_id for result in conformance),
            "short_write_simulations": sum(
                "/SHORT_WRITE-" in result.trial_id for result in conformance
            ),
            "injected_error_simulations": sum(
                "/io/" in result.trial_id and "/SHORT_WRITE-" not in result.trial_id
                for result in conformance
            ),
            "truncations": sum("/TRUNCATE-" in result.trial_id for result in conformance),
            "single_bit_flips": sum("/FLIP-" in result.trial_id for result in conformance),
            "coherent_negative_controls": sum(
                "STALE_VALID" in result.trial_id or "OTHER_VALID" in result.trial_id
                for result in conformance
            ),
            "simulated_io": sum("/io/" in result.trial_id for result in conformance),
        },
    }


def _operation_measurements(experiment: Experiment) -> dict[str, object]:
    publisher_results = [
        result for result in experiment.results if "publisher_transcript" in result.fields
    ]
    stage_frames = 0
    sigkills = 0
    for result in publisher_results:
        transcript = result.fields["publisher_transcript"]
        stage_frames += sum(
            transcript[index:index + 1] == b"\xa0"
            for index in range(0, len(transcript) - 1, 2)
        )
        sigkills += result.fields["publisher_terminal"] == b"SIGKILL"
    return {
        "fresh_publisher_processes": len(publisher_results),
        "fresh_recovery_processes": len(experiment.results),
        "publisher_stage_acknowledgements": stage_frames,
        "publisher_sigkills_and_reaps": sigkills,
        "privilege_requirement": "ordinary write access to /tmp and /dev/shm; no elevated privilege",
        "application_protocol_operations": {
            "authoritative_filename": r0_record.STATE_NAME,
            "temporary_filename": r0_record.TEMP_NAME,
            "normal_publish": (
                "exclusive open temp; two logical write regions with retry; file fsync; "
                "close; same-directory replace; open directory; directory fsync; close"
            ),
            "recovery": "nofollow open; fstat; bounded read; close; two adapter calls",
        },
        "whole_process_syscall_counts_by_name": {
            "status": "UNKNOWN",
            "reason": (
                "Python runtime and loader calls were not traced; protocol-level calls "
                "are explicit in code, but are not mislabeled whole-process counts"
            ),
        },
        "strace_gap": (
            "strace is available but was not inserted into the semantic run because it "
            "changes process launch and timing; a separately labeled instrumented run remains possible"
        ),
    }


def _dimension_ledger(experiment: Experiment,
                      inventory: dict[str, object]) -> dict[str, object]:
    counts = _result_counts(experiment)
    conformance = [result for result in experiment.results if result.category == "conformance"]
    failures = [result for result in conformance if not result.passed]
    cross = _semantic_cross_backend(experiment)
    timing = _timing_measurements(experiment)
    storage = _storage_measurements(experiment, inventory)
    operations = _operation_measurements(experiment)
    derived = {
        "P0": hashlib.sha256(
            b"ZERO-GROUND-R0-DERIVED\x00" + _lp4(r0_adapter.Y0)
        ).hexdigest(),
        "P1": hashlib.sha256(
            b"ZERO-GROUND-R0-DERIVED\x00" + _lp4(r0_adapter.Y1)
        ).hexdigest(),
    }
    return {
        "information_distinction_preservation": {
            **counts,
            "conformance_failures": [result.trial_id for result in failures],
            "separating_witness": {
                "left_payload_hex": r0_adapter.P0.hex(),
                "right_payload_hex": r0_adapter.P1.hex(),
                "continuation_hex": r0_adapter.C.hex(),
                "left_observation_hex": literal_expected("P0").hex(),
                "right_observation_hex": literal_expected("P1").hex(),
            },
            "cross_backend": cross,
        },
        "persistent_state": {
            **storage,
            "component_deletion_findings": experiment.deletion_findings,
        },
        "semantic_machinery": {
            "artifact_inventory": inventory,
            "adapter_bundle_digest": experiment.a.hex(),
            "suite_digest": experiment.d.hex(),
            "runtime_and_kernel_bytes": "UNKNOWN",
        },
        "human_cognition": {
            "operator_choices": ["backend set", "full versus focused mode"],
            "declared_failure_labels": 9,
            "human_study": {
                "status": "UNKNOWN",
                "reason": "no participant, comprehension, or error-rate study was run",
            },
            "loc_is_not_cognitive_evidence": True,
        },
        "authoring_burden": {
            "artifact_files": inventory["file_count"],
            "artifact_bytes": inventory["total_bytes"],
            "artifact_physical_lines": inventory["total_physical_lines"],
            "opaque_suite_values": 5,
            "manual_decisions_not_reliably_measured": "UNKNOWN",
        },
        "query_navigation_burden": {
            "continuations": 1,
            "continuation_bytes": len(r0_adapter.C),
            "authoritative_file_opens_per_recovery": 1,
            "contract_and_bundle_files_hashed_per_worker_start": 4,
            "adapter_invocations_per_accepted_recovery": 2,
            "search_or_index_infrastructure": 0,
            "valid_transcript_bytes": {
                "P0": len(literal_expected("P0")),
                "P1": len(literal_expected("P1")),
            },
        },
        "runtime": timing,
        "storage": storage,
        "operations": operations,
        "trusted_computing_base": _tcb_ledger(),
        "evolution": {
            "compatible_observer": {
                "status": "PASS",
                "recipe": "SHA256(DERIVED tag || LP(old OK payload))",
                "outputs": derived,
                "persistent_migration_bytes": 0,
                "scope": "two corpus payload positions and one observer only",
            },
            "split_extension": {
                "status": "UNSUPPORTED_SPLIT_WITHOUT_EXTERNAL_INFORMATION",
                "collision": "one identical R0 record with two newly required outputs",
            },
            "format_version_generation_rollback_support": "UNSUPPORTED",
        },
        "portability": {
            "guest_cross_backend": cross,
            "required_os": "Linux with process signals, statfs, directory fsync, and atomic replace",
            "tested_filesystems": [
                experiment.backend_info[key]["filesystem"]
                for key in sorted(experiment.backend_info)
            ],
            "physical_portability": "UNKNOWN",
            "other_operating_systems": "UNSUPPORTED/UNTESTED",
        },
        "explainability": {
            "recovery_tags": {"ABSENT": "00", "REJECT": "01", "OK": "02"},
            "failing_trial_count": len(failures),
            "failing_trials": [
                {
                    "id": result.trial_id,
                    "expected_hex": result.expected.hex(),
                    "observed_hex": result.observed.hex(),
                    "explanation": result.explanation,
                }
                for result in failures[:20]
            ],
            "human_comprehension": "UNKNOWN",
        },
        "information_loss_risk": {
            "truncation_trials": counts["conformance_kinds"]["truncations"],
            "single_bit_trials": counts["conformance_kinds"]["single_bit_flips"],
            "finite_false_accepts_or_rejects": len(failures),
            "coherent_replacement": "UNDETECTED by design; negative controls report it",
            "sha256_assumption": "no collision in the finite mutation set",
            "power_kernel_host_controller_media_faults": "UNKNOWN/UNSUPPORTED",
            "tmpfs_swap_path": "possible and not controlled",
        },
    }


def deterministic_report(experiment: Experiment,
                         inventory: dict[str, object]) -> dict[str, object]:
    all_certificate = experiment.certificate()
    conformance_certificate = experiment.certificate("conformance")
    attack_certificate = experiment.certificate("attack")
    counts = _result_counts(experiment)
    conformance_failures = sorted(
        result.trial_id
        for result in experiment.results
        if result.category == "conformance" and not result.passed
    )
    return {
        "schema": "zero-ground-realization-r0-deterministic-v1",
        "contract_sha256": experiment.q.hex(),
        "adapter_bundle_sha256": experiment.a.hex(),
        "suite_digest_sha256": experiment.d.hex(),
        "suite": {
            "P0_hex": r0_adapter.P0.hex(),
            "P1_hex": r0_adapter.P1.hex(),
            "C_hex": r0_adapter.C.hex(),
            "Y0_hex": r0_adapter.Y0.hex(),
            "Y1_hex": r0_adapter.Y1.hex(),
            "total_opaque_bytes": sum(map(len, (
                r0_adapter.P0, r0_adapter.P1, r0_adapter.C,
                r0_adapter.Y0, r0_adapter.Y1,
            ))),
        },
        "certificate_encoding": (
            "trials sorted by UTF-8 trial_id; each record is uint32 field count; "
            "fields sorted by unsigned UTF-8 key; key=uint32 length+bytes; "
            "value=uint64 length+bytes; stream=uint64 record length+record"
        ),
        "certificates": {
            "all": {
                "sha256": all_certificate[0],
                "records": all_certificate[1],
                "bytes": all_certificate[2],
            },
            "conformance": {
                "sha256": conformance_certificate[0],
                "records": conformance_certificate[1],
                "bytes": conformance_certificate[2],
            },
            "attack": {
                "sha256": attack_certificate[0],
                "records": attack_certificate[1],
                "bytes": attack_certificate[2],
            },
        },
        "counts": counts,
        "conformance_passed": not conformance_failures,
        "conformance_failures": conformance_failures,
        "guest_cross_backend": _semantic_cross_backend(experiment),
        "component_and_mechanism_deletions": experiment.deletion_findings,
        "common_mode_controls": experiment.common_mode,
        "artifact_inventory": inventory,
        "claims": {
            "candidate_format_is_architecture": False,
            "implementation_is_falsification_instrument": True,
            "power_loss_durability": "UNKNOWN",
            "two_unlike_physical_realizations": "UNKNOWN/UNSUPPORTED_IN_CURRENT_GUEST",
            "human_cognition": "UNKNOWN",
            "malicious_coherent_replacement": "UNSUPPORTED",
        },
    }


def measurement_report(experiment: Experiment,
                       inventory: dict[str, object]) -> dict[str, object]:
    backend_environment: dict[str, dict[str, object]] = {}
    filesystem_deltas: dict[str, dict[str, int]] = {}
    for symbol, original in experiment.backend_info.items():
        copied = dict(original)
        base = BACKENDS[symbol]["base"]
        assert isinstance(base, Path)
        end = os.statvfs(base)
        start_available = int(copied["statvfs_blocks_available_at_start"])
        copied["statvfs_blocks_available_at_end"] = end.f_bavail
        copied["statvfs_available_block_delta"] = end.f_bavail - start_available
        backend_environment[symbol] = copied
        filesystem_deltas[symbol] = {
            "fragment_size_bytes": end.f_frsize,
            "available_blocks_start": start_available,
            "available_blocks_end": end.f_bavail,
            "available_block_delta": end.f_bavail - start_available,
        }
    dimensions = _dimension_ledger(experiment, inventory)
    dimensions["storage"]["statvfs_available_block_delta_proxy"] = filesystem_deltas
    dimensions["persistent_state"]["statvfs_available_block_delta_proxy"] = filesystem_deltas
    return {
        "schema": "zero-ground-realization-r0-measurements-v1",
        "excluded_from_deterministic_certificate": True,
        "backend_environment": backend_environment,
        "host_guest_environment": _environment_measurements(),
        "dimensions": dimensions,
        "no_scalar_score": True,
    }


def execute(*, full: bool, backend_symbols: tuple[str, ...],
            publication_repetitions: int) -> Experiment:
    q, a, d = r0_record.derive_digests(BASE)
    if q.hex() != CONTRACT_SHA256:
        raise RuntimeError(
            f"frozen R0 contract changed: {q.hex()} != {CONTRACT_SHA256}"
        )
    if r0_adapter.apply(r0_adapter.P0, r0_adapter.C) != r0_adapter.Y0:
        raise AssertionError("P0 suite relation failed")
    if r0_adapter.apply(r0_adapter.P1, r0_adapter.C) != r0_adapter.Y1:
        raise AssertionError("P1 suite relation failed")
    if r0_adapter.P0 == r0_adapter.P1 or r0_adapter.Y0 == r0_adapter.Y1:
        raise AssertionError("suite lacks its required distinction")

    backend_info = {symbol: validate_backend(symbol) for symbol in backend_symbols}
    experiment = Experiment(q=q, a=a, d=d, backend_info=backend_info)
    run_publication_matrix(
        experiment, backend_symbols, publication_repetitions,
        category="conformance", variant="candidate",
    )
    if full:
        run_record_fault_matrix(experiment, backend_symbols)
        run_io_fault_matrix(experiment, backend_symbols)
        run_mechanism_deletions(experiment, backend_symbols)
    experiment.deletion_findings.update(evaluate_component_deletions(experiment))
    run_common_mode_controls(experiment)
    return experiment


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full", action="store_true",
        help="execute exhaustive faults, I/O simulations, and mechanism deletions",
    )
    parser.add_argument(
        "--backend", action="append", choices=tuple(BACKENDS),
        help="backend symbol; repeat to select both (default: E and T)",
    )
    parser.add_argument(
        "--publication-repetitions", type=int,
        help="override 3 repetitions in full mode or 1 in focused mode",
    )
    parser.add_argument(
        "--deterministic", action="store_true",
        help="print only deterministic evidence; timing/environment stay excluded",
    )
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    symbols = tuple(args.backend or ("E", "T"))
    if len(set(symbols)) != len(symbols):
        raise SystemExit("duplicate --backend")
    repetitions = args.publication_repetitions
    if repetitions is None:
        repetitions = 3 if args.full else 1
    if repetitions < 1:
        raise SystemExit("publication repetitions must be positive")
    experiment = execute(
        full=args.full,
        backend_symbols=symbols,
        publication_repetitions=repetitions,
    )
    inventory = _source_inventory()
    deterministic = deterministic_report(experiment, inventory)
    if args.deterministic:
        output: dict[str, object] = deterministic
    else:
        output = {
            "deterministic": deterministic,
            "measurements": measurement_report(experiment, inventory),
        }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if deterministic["conformance_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
