"""Canonical R0.1B typed-value codec from correction profile section 3.

The wire format distinguishes unsigned and signed positive integers, so this
host API uses explicit ``U64`` and ``I64`` wrappers and rejects bare ``int``.
No repository subject implementation is imported.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
import struct
from typing import Final, TypeAlias


TAG_U64: Final = 0x01
TAG_I64: Final = 0x02
TAG_BYTES: Final = 0x03
TAG_TEXT: Final = 0x04
TAG_FALSE: Final = 0x05
TAG_TRUE: Final = 0x06
TAG_LIST: Final = 0x07
TAG_MAP: Final = 0x08
TAG_UNKNOWN: Final = 0x09
TAG_UNSUPPORTED: Final = 0x0A
TAG_ENUM: Final = 0x0B

U64_MAX: Final = (1 << 64) - 1
I64_MIN: Final = -(1 << 63)
I64_MAX: Final = (1 << 63) - 1
U16_MAX: Final = (1 << 16) - 1


class TVError(ValueError):
    """Base error for typed-value construction or wire processing."""


class TVEncodeError(TVError):
    """A host value has no canonical R0.1B typed-value encoding."""


class TVDecodeError(TVError):
    """Input is malformed, truncated, or noncanonical R0.1B bytes."""


class TVRegistryError(TVError):
    """An optional closed-enum registry is malformed."""


def _exact_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact int, not {type(value).__name__}")
    return value


@dataclass(frozen=True, slots=True)
class U64:
    value: int

    def __post_init__(self) -> None:
        value = _exact_int(self.value, "U64.value")
        if not 0 <= value <= U64_MAX:
            raise ValueError("U64.value is outside 0..2^64-1")


@dataclass(frozen=True, slots=True)
class I64:
    value: int

    def __post_init__(self) -> None:
        value = _exact_int(self.value, "I64.value")
        if not I64_MIN <= value <= I64_MAX:
            raise ValueError("I64.value is outside -2^63..2^63-1")


def _nonempty_text(value: object, label: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{label} must be an exact str")
    if not value:
        raise ValueError(f"{label} must be nonempty")
    try:
        value.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{label} contains a non-UTF-8-encodable surrogate") from exc
    return value


@dataclass(frozen=True, slots=True)
class Unknown:
    reason: str
    needed_evidence: str

    def __post_init__(self) -> None:
        _nonempty_text(self.reason, "Unknown.reason")
        _nonempty_text(self.needed_evidence, "Unknown.needed_evidence")


@dataclass(frozen=True, slots=True)
class Unsupported:
    reason: str

    def __post_init__(self) -> None:
        _nonempty_text(self.reason, "Unsupported.reason")


@dataclass(frozen=True, slots=True)
class ClosedEnum:
    namespace: int
    code: int

    def __post_init__(self) -> None:
        namespace = _exact_int(self.namespace, "ClosedEnum.namespace")
        code = _exact_int(self.code, "ClosedEnum.code")
        if not 0 <= namespace <= U16_MAX:
            raise ValueError("ClosedEnum.namespace is outside 0..65535")
        if not 0 <= code <= U16_MAX:
            raise ValueError("ClosedEnum.code is outside 0..65535")


EnumRegistry: TypeAlias = Mapping[int, Collection[int]]
EnumPairs: TypeAlias = frozenset[tuple[int, int]] | None


def _normalize_registry(registry: EnumRegistry | None) -> EnumPairs:
    if registry is None:
        return None
    if not isinstance(registry, Mapping):
        raise TVRegistryError("enum registry must be a namespace-to-codes mapping")
    pairs: set[tuple[int, int]] = set()
    for namespace, codes in registry.items():
        try:
            namespace = _exact_int(namespace, "enum registry namespace")
        except TypeError as exc:
            raise TVRegistryError(str(exc)) from exc
        if not 0 <= namespace <= U16_MAX:
            raise TVRegistryError("enum registry namespace is outside 0..65535")
        if isinstance(codes, (str, bytes, bytearray)) or not isinstance(codes, Collection):
            raise TVRegistryError("enum registry codes must be a collection of integers")
        for code in codes:
            try:
                code = _exact_int(code, "enum registry code")
            except TypeError as exc:
                raise TVRegistryError(str(exc)) from exc
            if not 0 <= code <= U16_MAX:
                raise TVRegistryError("enum registry code is outside 0..65535")
            pairs.add((namespace, code))
    return frozenset(pairs)


def _validate_enum(value: ClosedEnum, pairs: EnumPairs,
                   error_type: type[TVError]) -> None:
    if pairs is not None and (value.namespace, value.code) not in pairs:
        raise error_type(
            f"unregistered closed enum ({value.namespace}, {value.code})"
        )


def _u64(value: int) -> bytes:
    return struct.pack(">Q", value)


def _text_bytes(value: str, error_type: type[TVError]) -> bytes:
    try:
        return value.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise error_type("text contains a non-UTF-8-encodable surrogate") from exc


def _map_key_bytes(value: object) -> bytes:
    if type(value) is not str:
        raise TVEncodeError("map keys must be exact str values")
    try:
        encoded = value.encode("ascii", "strict")
    except UnicodeEncodeError as exc:
        raise TVEncodeError("map key is not ASCII") from exc
    if len(encoded) > U16_MAX:
        raise TVEncodeError("map key exceeds 65535 encoded bytes")
    if any(byte < 0x20 or byte > 0x7E for byte in encoded):
        raise TVEncodeError("map key contains non-printable ASCII")
    return encoded


class _Encoder:
    def __init__(self, enum_pairs: EnumPairs):
        self.enum_pairs = enum_pairs
        self.active_container_ids: set[int] = set()

    def encode(self, value: object) -> bytes:
        if isinstance(value, U64):
            return bytes([TAG_U64]) + struct.pack(">Q", value.value)
        if isinstance(value, I64):
            return bytes([TAG_I64]) + struct.pack(">q", value.value)
        if type(value) is bytes:
            return bytes([TAG_BYTES]) + _u64(len(value)) + value
        if type(value) is str:
            encoded = _text_bytes(value, TVEncodeError)
            return bytes([TAG_TEXT]) + _u64(len(encoded)) + encoded
        if value is False:
            return bytes([TAG_FALSE])
        if value is True:
            return bytes([TAG_TRUE])
        if isinstance(value, Unknown):
            reason = _nonempty_text(value.reason, "Unknown.reason")
            evidence = _nonempty_text(
                value.needed_evidence, "Unknown.needed_evidence"
            )
            return (
                bytes([TAG_UNKNOWN])
                + self.encode(reason)
                + self.encode(evidence)
            )
        if isinstance(value, Unsupported):
            reason = _nonempty_text(value.reason, "Unsupported.reason")
            return bytes([TAG_UNSUPPORTED]) + self.encode(reason)
        if isinstance(value, ClosedEnum):
            _validate_enum(value, self.enum_pairs, TVEncodeError)
            return (
                bytes([TAG_ENUM])
                + struct.pack(">H", value.namespace)
                + struct.pack(">H", value.code)
            )
        if type(value) in (list, tuple):
            return self._encode_list(value)
        if isinstance(value, Mapping):
            return self._encode_map(value)
        if type(value) is int:
            raise TVEncodeError("bare int is ambiguous; use U64 or I64")
        raise TVEncodeError(
            f"unsupported typed-value host type: {type(value).__name__}"
        )

    def _enter(self, value: object) -> int:
        identity = id(value)
        if identity in self.active_container_ids:
            raise TVEncodeError("cyclic list or map has no finite encoding")
        self.active_container_ids.add(identity)
        return identity

    def _encode_list(self, value: list[object] | tuple[object, ...]) -> bytes:
        identity = self._enter(value)
        try:
            return (
                bytes([TAG_LIST])
                + _u64(len(value))
                + b"".join(self.encode(item) for item in value)
            )
        finally:
            self.active_container_ids.remove(identity)

    def _encode_map(self, value: Mapping[object, object]) -> bytes:
        identity = self._enter(value)
        try:
            entries: list[tuple[bytes, object]] = []
            seen: set[bytes] = set()
            for key, item in value.items():
                encoded_key = _map_key_bytes(key)
                if encoded_key in seen:
                    raise TVEncodeError("map exposes duplicate encoded key bytes")
                seen.add(encoded_key)
                entries.append((encoded_key, item))
            entries.sort(key=lambda pair: pair[0])
            body = bytearray(bytes([TAG_MAP]) + _u64(len(entries)))
            for key, item in entries:
                body.extend(struct.pack(">H", len(key)))
                body.extend(key)
                body.extend(self.encode(item))
            return bytes(body)
        finally:
            self.active_container_ids.remove(identity)


def encode(value: object, *, enum_registry: EnumRegistry | None = None) -> bytes:
    """Return the one canonical R0.1B encoding of ``value``.

    If ``enum_registry`` is provided, every ``ClosedEnum`` must occur in its
    ``{namespace: collection_of_codes}`` relation.
    """

    return _Encoder(_normalize_registry(enum_registry)).encode(value)


class _Decoder:
    def __init__(self, data: bytes, enum_pairs: EnumPairs):
        self.data = data
        self.offset = 0
        self.enum_pairs = enum_pairs

    def _take(self, count: int) -> bytes:
        if count < 0 or count > len(self.data) - self.offset:
            raise TVDecodeError("truncated typed value")
        start = self.offset
        self.offset += count
        return self.data[start:self.offset]

    def _byte(self) -> int:
        return self._take(1)[0]

    def _u16(self) -> int:
        return struct.unpack(">H", self._take(2))[0]

    def _u64(self) -> int:
        return struct.unpack(">Q", self._take(8))[0]

    def _text(self) -> str:
        length = self._u64()
        raw = self._take(length)
        try:
            return raw.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise TVDecodeError("invalid UTF-8 text") from exc

    def _required_text_member(self, label: str) -> str:
        if self._byte() != TAG_TEXT:
            raise TVDecodeError(f"{label} must use the text tag")
        value = self._text()
        if not value:
            raise TVDecodeError(f"{label} must be nonempty")
        return value

    def value(self) -> object:
        tag = self._byte()
        if tag == TAG_U64:
            return U64(self._u64())
        if tag == TAG_I64:
            return I64(struct.unpack(">q", self._take(8))[0])
        if tag == TAG_BYTES:
            return self._take(self._u64())
        if tag == TAG_TEXT:
            return self._text()
        if tag == TAG_FALSE:
            return False
        if tag == TAG_TRUE:
            return True
        if tag == TAG_LIST:
            count = self._u64()
            return tuple(self.value() for _ in range(count))
        if tag == TAG_MAP:
            return self._map()
        if tag == TAG_UNKNOWN:
            reason = self._required_text_member("unknown reason")
            evidence = self._required_text_member("unknown needed evidence")
            return Unknown(reason, evidence)
        if tag == TAG_UNSUPPORTED:
            return Unsupported(self._required_text_member("unsupported reason"))
        if tag == TAG_ENUM:
            value = ClosedEnum(self._u16(), self._u16())
            _validate_enum(value, self.enum_pairs, TVDecodeError)
            return value
        raise TVDecodeError(f"unknown typed-value tag 0x{tag:02x}")

    def _map(self) -> dict[str, object]:
        count = self._u64()
        result: dict[str, object] = {}
        previous: bytes | None = None
        for _ in range(count):
            key_length = self._u16()
            key_bytes = self._take(key_length)
            if any(byte < 0x20 or byte > 0x7E for byte in key_bytes):
                raise TVDecodeError("map key contains non-printable or non-ASCII byte")
            if previous is not None and key_bytes <= previous:
                if key_bytes == previous:
                    raise TVDecodeError("duplicate map key")
                raise TVDecodeError("map keys are not in unsigned byte order")
            previous = key_bytes
            key = key_bytes.decode("ascii")
            result[key] = self.value()
        return result


def decode(data: bytes | bytearray | memoryview, *,
           enum_registry: EnumRegistry | None = None) -> object:
    """Decode exactly one canonical R0.1B typed value.

    Truncation, unknown tags, malformed structured leaves, noncanonical maps,
    invalid UTF-8, and any trailing byte are rejected.
    """

    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("typed-value input must be bytes-like")
    decoder = _Decoder(bytes(data), _normalize_registry(enum_registry))
    value = decoder.value()
    if decoder.offset != len(decoder.data):
        raise TVDecodeError("trailing bytes after typed value")
    return value


__all__ = [
    "ClosedEnum",
    "EnumRegistry",
    "I64",
    "TVDecodeError",
    "TVEncodeError",
    "TVError",
    "TVRegistryError",
    "U64",
    "Unknown",
    "Unsupported",
    "decode",
    "encode",
]
