"""Frozen opaque R0 suite and its deliberately tiny adapter.

The byte strings are chosen to minimize their total length under the R0
constraints.  Their labels are test-vector positions only.
"""

from __future__ import annotations


P0 = b""
P1 = b"\x00"
C = b""
Y0 = b""
Y1 = b"\x00"


class AdapterReject(ValueError):
    """The opaque input is outside the frozen finite suite."""


def apply(payload: bytes, continuation: bytes) -> bytes:
    if continuation != C:
        raise AdapterReject("unknown continuation")
    if payload == P0:
        return Y0
    if payload == P1:
        return Y1
    raise AdapterReject("unknown payload")

