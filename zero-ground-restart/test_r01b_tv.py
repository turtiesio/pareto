"""Independent literal-vector and rejection tests for the R0.1B TV codec."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

import r01b_tv as tv


# These bytes are transcribed directly from correction profile section 3.  No
# subject encoder, decoder, tag constant, framing helper, or struct helper is
# used to construct the expected side.
EXACT_VECTORS = (
    (tv.U64(0), "010000000000000000"),
    (tv.I64(-1), "02ffffffffffffffff"),
    (b"\x00\xff", "03000000000000000200ff"),
    ("é", "040000000000000002c3a9"),
    (False, "05"),
    (True, "06"),
    (
        [tv.U64(1), False],
        "07000000000000000201000000000000000105",
    ),
    (
        {"b": True, "a": False},
        "0800000000000000020001610500016206",
    ),
    (
        tv.Unknown("r", "e"),
        "090400000000000000017204000000000000000165",
    ),
    (
        tv.Unsupported("r"),
        "0a04000000000000000172",
    ),
    (
        tv.ClosedEnum(1, 2),
        "0b00010002",
    ),
)

NESTED_VALUE = {
    "z": {"b": True},
    "a": [tv.U64(1), tv.Unknown("r", "e")],
}
NESTED_HEX = (
    "080000000000000002"
    "000161"
    "070000000000000002"
    "010000000000000001"
    "090400000000000000017204000000000000000165"
    "00017a"
    "080000000000000001"
    "000162"
    "06"
)


class ExactVectorTests(unittest.TestCase):
    def test_every_tag_has_an_independent_exact_hex_vector(self) -> None:
        self.assertEqual(len(EXACT_VECTORS), 11)
        for expected_tag, (value, expected_hex) in enumerate(EXACT_VECTORS, 1):
            with self.subTest(tag=expected_tag):
                expected = bytes.fromhex(expected_hex)
                self.assertEqual(expected[0], expected_tag)
                self.assertEqual(tv.encode(value), expected)

    def test_every_exact_vector_decodes_and_reencodes_identically(self) -> None:
        for value, expected_hex in EXACT_VECTORS:
            with self.subTest(hex=expected_hex):
                encoded = bytes.fromhex(expected_hex)
                decoded = tv.decode(encoded)
                if isinstance(value, list):
                    self.assertEqual(decoded, tuple(value))
                else:
                    self.assertEqual(decoded, value)
                self.assertEqual(tv.encode(decoded), encoded)

    def test_nested_map_list_vector_is_exact(self) -> None:
        expected = bytes.fromhex(NESTED_HEX)
        self.assertEqual(tv.encode(NESTED_VALUE), expected)
        self.assertEqual(tv.encode(tv.decode(expected)), expected)
        self.assertEqual(
            tv.decode(expected),
            {
                "a": (tv.U64(1), tv.Unknown("r", "e")),
                "z": {"b": True},
            },
        )

    def test_map_encoder_sorts_by_unsigned_ascii_bytes(self) -> None:
        left = {"~": False, "A": True, "a": False, " ": True}
        right = {" ": True, "A": True, "a": False, "~": False}
        self.assertEqual(tv.encode(left), tv.encode(right))
        self.assertEqual(list(tv.decode(tv.encode(left))), [" ", "A", "a", "~"])

    def test_text_is_not_normalized(self) -> None:
        composed = "é"
        decomposed = "e\u0301"
        self.assertNotEqual(tv.encode(composed), tv.encode(decomposed))
        self.assertEqual(tv.decode(tv.encode(composed)), composed)
        self.assertEqual(tv.decode(tv.encode(decomposed)), decomposed)

    def test_empty_map_key_is_allowed_because_only_reasons_are_nonempty(self) -> None:
        exact = bytes.fromhex("080000000000000001000005")
        self.assertEqual(tv.encode({"": False}), exact)
        self.assertEqual(tv.decode(exact), {"": False})


class StrictDecoderTests(unittest.TestCase):
    def test_every_proper_prefix_of_every_vector_is_rejected(self) -> None:
        vectors = [bytes.fromhex(item[1]) for item in EXACT_VECTORS]
        vectors.append(bytes.fromhex(NESTED_HEX))
        for vector in vectors:
            for length in range(len(vector)):
                with self.subTest(vector=vector.hex(), length=length):
                    with self.assertRaises(tv.TVDecodeError):
                        tv.decode(vector[:length])

    def test_trailing_byte_is_rejected_for_every_vector(self) -> None:
        for _, expected_hex in EXACT_VECTORS:
            with self.subTest(hex=expected_hex):
                with self.assertRaisesRegex(tv.TVDecodeError, "trailing"):
                    tv.decode(bytes.fromhex(expected_hex) + b"\x00")

    def test_unknown_tags_are_rejected(self) -> None:
        for encoded in (b"\x00", b"\x0c", b"\xff"):
            with self.subTest(encoded=encoded.hex()):
                with self.assertRaisesRegex(tv.TVDecodeError, "unknown.*tag"):
                    tv.decode(encoded)

    def test_duplicate_map_key_is_rejected(self) -> None:
        duplicate = bytes.fromhex(
            "080000000000000002"
            "00016105"
            "00016106"
        )
        with self.assertRaisesRegex(tv.TVDecodeError, "duplicate"):
            tv.decode(duplicate)

    def test_unsorted_map_keys_are_rejected(self) -> None:
        unsorted = bytes.fromhex(
            "080000000000000002"
            "00016205"
            "00016106"
        )
        with self.assertRaisesRegex(tv.TVDecodeError, "not in unsigned byte order"):
            tv.decode(unsorted)

    def test_non_ascii_and_nonprintable_map_keys_are_rejected(self) -> None:
        prefix = "0800000000000000010001"
        for bad_key in ("00", "1f", "7f", "80", "ff"):
            encoded = bytes.fromhex(prefix + bad_key + "05")
            with self.subTest(key=bad_key):
                with self.assertRaisesRegex(tv.TVDecodeError, "map key"):
                    tv.decode(encoded)

    def test_invalid_utf8_text_is_rejected(self) -> None:
        invalid_payloads = (
            "ff",
            "c080",
            "eda080",
            "c3",
        )
        for payload_hex in invalid_payloads:
            length_hex = f"{len(bytes.fromhex(payload_hex)):016x}"
            with self.subTest(payload=payload_hex):
                with self.assertRaisesRegex(tv.TVDecodeError, "UTF-8"):
                    tv.decode(bytes.fromhex("04" + length_hex + payload_hex))

    def test_unknown_requires_two_nonempty_text_members(self) -> None:
        malformed = {
            "reason-not-text": "0903000000000000000004000000000000000165",
            "empty-reason": "0904000000000000000004000000000000000165",
            "evidence-not-text": "0904000000000000000172030000000000000000",
            "empty-evidence": "0904000000000000000172040000000000000000",
        }
        for name, encoded_hex in malformed.items():
            with self.subTest(name=name):
                with self.assertRaises(tv.TVDecodeError):
                    tv.decode(bytes.fromhex(encoded_hex))

    def test_unsupported_requires_one_nonempty_text_member(self) -> None:
        for encoded_hex in (
            "0a030000000000000000",
            "0a040000000000000000",
        ):
            with self.subTest(hex=encoded_hex):
                with self.assertRaises(tv.TVDecodeError):
                    tv.decode(bytes.fromhex(encoded_hex))

    def test_impossible_container_counts_fail_as_truncation(self) -> None:
        for encoded in (
            bytes.fromhex("07ffffffffffffffff"),
            bytes.fromhex("08ffffffffffffffff"),
        ):
            with self.subTest(encoded=encoded.hex()):
                with self.assertRaisesRegex(tv.TVDecodeError, "truncated"):
                    tv.decode(encoded)

    def test_non_bytes_input_is_rejected(self) -> None:
        for value in (None, "05", 5, [5]):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    tv.decode(value)  # type: ignore[arg-type]


class HostValueValidationTests(unittest.TestCase):
    def test_wrappers_are_immutable(self) -> None:
        values_and_fields = (
            (tv.U64(1), "value"),
            (tv.I64(-1), "value"),
            (tv.Unknown("r", "e"), "reason"),
            (tv.Unsupported("r"), "reason"),
            (tv.ClosedEnum(1, 2), "code"),
        )
        for value, field in values_and_fields:
            with self.subTest(value=value):
                with self.assertRaises(FrozenInstanceError):
                    setattr(value, field, 3)

    def test_integer_wrappers_cover_boundaries(self) -> None:
        unsigned = (tv.U64(0), tv.U64((1 << 64) - 1))
        signed = (tv.I64(-(1 << 63)), tv.I64((1 << 63) - 1), tv.I64(1))
        for value in unsigned + signed:
            self.assertEqual(tv.decode(tv.encode(value)), value)
        for constructor, value in (
            (tv.U64, -1),
            (tv.U64, 1 << 64),
            (tv.I64, -(1 << 63) - 1),
            (tv.I64, 1 << 63),
        ):
            with self.subTest(constructor=constructor.__name__, value=value):
                with self.assertRaises(ValueError):
                    constructor(value)
        for constructor in (tv.U64, tv.I64):
            with self.assertRaises(TypeError):
                constructor(True)

    def test_plain_int_null_float_set_and_bytearray_are_rejected(self) -> None:
        for value in (0, -1, None, 1.0, {"x"}, bytearray(b"x")):
            with self.subTest(value=value):
                with self.assertRaises(tv.TVEncodeError):
                    tv.encode(value)

    def test_bad_map_keys_are_rejected_by_encoder(self) -> None:
        bad_maps = (
            {1: False},
            {"é": False},
            {"\n": False},
            {"\x7f": False},
            {"x" * 65536: False},
        )
        for value in bad_maps:
            with self.subTest(key=next(iter(value))):
                with self.assertRaises(tv.TVEncodeError):
                    tv.encode(value)

    def test_surrogate_text_is_rejected_by_encoder(self) -> None:
        for value in ("\ud800", {"a": "\udfff"}):
            with self.subTest(value=repr(value)):
                with self.assertRaises(tv.TVEncodeError):
                    tv.encode(value)

    def test_cyclic_containers_are_rejected(self) -> None:
        sequence: list[object] = []
        sequence.append(sequence)
        mapping: dict[str, object] = {}
        mapping["a"] = mapping
        for value in (sequence, mapping):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaisesRegex(tv.TVEncodeError, "cyclic"):
                    tv.encode(value)

    def test_unknown_and_unsupported_constructors_require_nonempty_text(self) -> None:
        for constructor, arguments in (
            (tv.Unknown, ("", "e")),
            (tv.Unknown, ("r", "")),
            (tv.Unsupported, ("",)),
        ):
            with self.subTest(constructor=constructor.__name__, args=arguments):
                with self.assertRaises(ValueError):
                    constructor(*arguments)
        with self.assertRaises(TypeError):
            tv.Unknown(b"r", "e")  # type: ignore[arg-type]
        for constructor, arguments in (
            (tv.Unknown, ("\ud800", "e")),
            (tv.Unknown, ("r", "\udfff")),
            (tv.Unsupported, ("\ud800",)),
        ):
            with self.subTest(constructor=constructor.__name__, args=repr(arguments)):
                with self.assertRaises(ValueError):
                    constructor(*arguments)

    def test_closed_enum_constructor_requires_u16_coordinates(self) -> None:
        for namespace, code in ((-1, 0), (65536, 0), (0, -1), (0, 65536)):
            with self.subTest(namespace=namespace, code=code):
                with self.assertRaises(ValueError):
                    tv.ClosedEnum(namespace, code)
        with self.assertRaises(TypeError):
            tv.ClosedEnum(True, 0)


class EnumRegistryTests(unittest.TestCase):
    REGISTRY = {1: frozenset({2, 3}), 7: (9,)}
    VECTOR = bytes.fromhex("0b00010002")

    def test_registry_accepts_registered_enum_on_both_paths(self) -> None:
        value = tv.ClosedEnum(1, 2)
        self.assertEqual(tv.encode(value, enum_registry=self.REGISTRY), self.VECTOR)
        self.assertEqual(
            tv.decode(self.VECTOR, enum_registry=self.REGISTRY),
            value,
        )

    def test_no_registry_permits_structurally_valid_u16_pair(self) -> None:
        self.assertEqual(tv.decode(self.VECTOR), tv.ClosedEnum(1, 2))

    def test_registry_rejects_unknown_namespace_or_code_on_both_paths(self) -> None:
        for value in (tv.ClosedEnum(1, 4), tv.ClosedEnum(2, 2)):
            encoded = bytes([0x0B]) + value.namespace.to_bytes(2) + value.code.to_bytes(2)
            with self.subTest(value=value):
                with self.assertRaises(tv.TVEncodeError):
                    tv.encode(value, enum_registry=self.REGISTRY)
                with self.assertRaises(tv.TVDecodeError):
                    tv.decode(encoded, enum_registry=self.REGISTRY)

    def test_malformed_registry_is_rejected(self) -> None:
        bad_registries = (
            {(True): (2,)},
            {1: "2"},
            {1: (True,)},
            {-1: (2,)},
            {1: (65536,)},
        )
        for registry in bad_registries:
            with self.subTest(registry=registry):
                with self.assertRaises(tv.TVRegistryError):
                    tv.decode(self.VECTOR, enum_registry=registry)
        with self.assertRaises(tv.TVRegistryError):
            tv.decode(self.VECTOR, enum_registry={(1, 2)})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
