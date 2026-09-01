#!/usr/bin/env python3
"""Fresh-process publisher and recovery roles for R0."""

from __future__ import annotations

import argparse
import errno
import os
from pathlib import Path
import signal
import sys

# `-I` prevents ambient import paths from selecting a different bundle. Add
# only this worker's frozen bundle directory before loading its local modules.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import r0_record


ERROR_CODES = {
    "write_before_half": 1,
    "write_after_half": 1,
    "file_fsync": 2,
    "replace": 3,
    "directory_fsync": 4,
}


class SimulatedIOError(OSError):
    def __init__(self, kind: str, number: int):
        super().__init__(number, kind)
        self.kind = kind


def _bundle_matches(digest: bytes) -> bool:
    try:
        _, _, local_digest = r0_record.derive_digests(Path(__file__).resolve().parent)
    except Exception:
        return False
    return local_digest == digest


def _emit(value: bytes) -> None:
    view = memoryview(value)
    while view:
        count = os.write(sys.stdout.fileno(), view)
        if count <= 0:
            os._exit(72)
        view = view[count:]


def _stage(number: int) -> None:
    _emit(b"\xa0" + bytes([number]))
    os.kill(os.getpid(), signal.SIGSTOP)


def _write_all(fd: int, value: bytes, maximum: int) -> None:
    view = memoryview(value)
    while view:
        offered = view if maximum <= 0 else view[:maximum]
        count = os.write(fd, offered)
        if count <= 0:
            raise OSError(errno.EIO, "zero-progress write")
        view = view[count:]


def _publish(args: argparse.Namespace) -> int:
    directory = Path(args.directory)
    digest = bytes.fromhex(args.digest)
    payload = bytes.fromhex(args.payload)
    if not _bundle_matches(digest):
        return 71
    record = r0_record.encode_record(digest, payload)
    half = len(record) // 2
    temporary = directory / r0_record.TEMP_NAME
    authoritative = directory / r0_record.STATE_NAME
    fd: int | None = None
    directory_fd: int | None = None

    try:
        _stage(0)
        flags = os.O_WRONLY | os.O_CREAT
        if args.skip_exclusive_creation:
            flags |= os.O_TRUNC
        else:
            flags |= os.O_EXCL
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        fd = os.open(temporary, flags, 0o600)
        if args.inject == "write_before_half":
            raise SimulatedIOError(args.inject, errno.ENOSPC)
        _write_all(fd, record[:half], args.max_write)
        _stage(1)
        if args.inject == "write_after_half":
            raise SimulatedIOError(args.inject, errno.ENOSPC)
        _write_all(fd, record[half:], args.max_write)
        _stage(2)
        if args.inject == "file_fsync":
            raise SimulatedIOError(args.inject, errno.EIO)
        if not args.skip_file_fsync:
            os.fsync(fd)
        os.close(fd)
        fd = None
        _stage(3)
        if args.inject == "replace":
            raise SimulatedIOError(args.inject, errno.EIO)
        if not args.skip_replace:
            os.replace(temporary, authoritative)
        _stage(4)
        directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        if args.inject == "directory_fsync":
            raise SimulatedIOError(args.inject, errno.EIO)
        if not args.skip_directory_fsync:
            os.fsync(directory_fd)
        _stage(5)
        os.close(directory_fd)
        directory_fd = None
        return 0
    except SimulatedIOError as exc:
        if fd is not None:
            os.close(fd)
        if directory_fd is not None:
            os.close(directory_fd)
        _emit(b"\xaf" + bytes([ERROR_CODES[exc.kind]]))
        return 70
    except BaseException:
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
        return 71


def _recover(args: argparse.Namespace) -> int:
    digest = bytes.fromhex(args.digest)
    if not _bundle_matches(digest):
        _emit(r0_record.REJECT)
        return 0
    observation = r0_record.recover(
        Path(args.directory),
        digest,
        bytes.fromhex(args.continuation),
    )
    _emit(observation)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest="role", required=True)

    publish = subparsers.add_parser("publish", add_help=False)
    publish.add_argument("--directory", required=True)
    publish.add_argument("--digest", required=True)
    publish.add_argument("--payload", required=True)
    publish.add_argument("--inject", choices=tuple(ERROR_CODES), default=None)
    publish.add_argument("--max-write", type=int, default=0)
    publish.add_argument("--skip-file-fsync", action="store_true")
    publish.add_argument("--skip-directory-fsync", action="store_true")
    publish.add_argument("--skip-replace", action="store_true")
    publish.add_argument("--skip-exclusive-creation", action="store_true")

    recover = subparsers.add_parser("recover", add_help=False)
    recover.add_argument("--directory", required=True)
    recover.add_argument("--digest", required=True)
    recover.add_argument("--continuation", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.role == "publish":
        return _publish(args)
    return _recover(args)


if __name__ == "__main__":
    raise SystemExit(main())
