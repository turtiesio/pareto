#!/usr/bin/env python3
"""Close the acyclic R0.1B semantic gate from the twelve frozen S0 files.

This is gate machinery, not a subject implementation.  It never imports a
publisher, recovery reader, adapter, comparator, or trace normalizer.
"""

from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import struct
from typing import Any, Iterable, Mapping, Sequence

import r01b_tv


HERE = Path(__file__).resolve().parent

S0_NAMES = (
    "FEASIBILITY-AUDIT-R01.md",
    "R01-BREAKER-OBJECT.json",
    "R01B-DESCRIPTORS.json",
    "R01B-HOLDOUTS.json",
    "R01B-LITERAL-ORACLE.json",
    "R01B-MEASUREMENT-REGISTRY.json",
    "R01B-STATUS-REGISTRY.json",
    "R01B-SUITE.json",
    "REALIZATION-CONTRACT-R0.md",
    "REALIZATION-CONTRACT-R01.md",
    "REALIZATION-CORRECTION-R01B.md",
    "REALIZATION-SUPPLEMENT-R01A.md",
)

GATE_MACHINERY_NAMES = (
    "r01b_descriptor_freeze.py",
    "r01b_holdout_freeze.py",
    "r01b_measurement_freeze.py",
    "r01b_oracle_freeze.py",
    "r01b_semantic_freeze.py",
    "r01b_status_freeze.py",
    "r01b_tv.py",
    "test_r01b_freeze.py",
    "test_r01b_holdouts.py",
    "test_r01b_semantic_corpus.py",
    "test_r01b_semantic_freeze.py",
    "test_r01b_status.py",
    "test_r01b_tv.py",
)

S0_INDEX_NAME = "R01B-S0-MANIFEST.json"
S1_NAME = "R01B-S1.json"
FREEZE_NAME = "R01B-SEMANTIC-FREEZE.json"

CASE_TAG = b"ZGR01B-CASE\x00"
TRIAL_TAG = b"ZGR01B-TRIAL\x00"
SUITE_TAG = b"ZERO-GROUND-R01B-SUITE\x00"
RECORD_TAG = b"ZERO-GROUND-R01B-RECORD\x00"
FREEZE_TAG = b"ZERO-GROUND-R01B-SEMANTIC-FREEZE\x00"
SYMLINK_TARGET = b".r01b-valid-target"

SUBJECT_ROW_COUNT = 3028
LAB_ROW_COUNT = 3290
TOTAL_ROW_COUNT = 6318
RECIPE_COUNT = 1172
UNIQUE_FIXTURE_COUNT = 1137
MEASUREMENT_PATH_COUNT = 1040


class FreezeError(ValueError):
    """A frozen input or a mechanically derived invariant disagrees."""


@dataclass(frozen=True)
class ManifestMember:
    filename: str
    byte_length: int
    sha256: str

    def json_value(self) -> dict[str, Any]:
        return {
            "byte_length": self.byte_length,
            "filename": self.filename,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class FreezeBuild:
    s0_index_value: dict[str, Any]
    s0_index_bytes: bytes
    s0_manifest_bytes: bytes
    semantic_seed_digest: bytes
    semantic_suite_digest: bytes
    s1_value: dict[str, Any]
    s1_bytes: bytes
    s1_manifest_bytes: bytes
    semantic_freeze_id: str
    gate_manifest_bytes: bytes
    closure_value: dict[str, Any]
    closure_bytes: bytes
    diagnostics: dict[str, Any]

    def outputs(self) -> dict[str, bytes]:
        return {
            S0_INDEX_NAME: self.s0_index_bytes,
            S1_NAME: self.s1_bytes,
            FREEZE_NAME: self.closure_bytes,
        }


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def lp(value: bytes) -> bytes:
    if len(value) > 0xFFFFFFFF:
        raise FreezeError("LP value exceeds u32")
    return struct.pack(">I", len(value)) + value


def u64(value: int) -> bytes:
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFFFFFFFFFF:
        raise FreezeError("u64 value out of range")
    return struct.pack(">Q", value)


def _assert_printable_ascii_json(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if type(key) is not str:
                raise FreezeError(f"non-text JSON key at {path}")
            _assert_printable_ascii_string(key, f"{path}.<key>")
            _assert_printable_ascii_json(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_printable_ascii_json(child, f"{path}[{index}]")
        return
    if type(value) is str:
        _assert_printable_ascii_string(value, path)
        return
    if value is None:
        raise FreezeError(f"null is not legal at {path}")
    if type(value) is int and value < 0:
        raise FreezeError(f"negative JSON integer is not legal at {path}")
    if type(value) in (bool, int):
        return
    raise FreezeError(f"unsupported JSON type at {path}: {type(value).__name__}")


def _assert_printable_ascii_string(value: str, path: str) -> None:
    try:
        raw = value.encode("ascii", "strict")
    except UnicodeEncodeError as exc:
        raise FreezeError(f"non-ASCII string at {path}") from exc
    if any(byte < 0x20 or byte > 0x7E for byte in raw):
        raise FreezeError(f"non-printable ASCII string at {path}")


def canonical_json(value: Any, *, printable_ascii: bool = False) -> bytes:
    if printable_ascii:
        _assert_printable_ascii_json(value)
    try:
        raw = json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise FreezeError(f"value has no canonical JSON encoding: {exc}") from exc
    if b"\\/" in raw:
        raise FreezeError("canonical JSON escaped a solidus")
    return raw


def parse_json(raw: bytes, label: str, *, require_canonical: bool = False) -> Any:
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise FreezeError(f"invalid JSON: {label}") from exc
    if require_canonical and canonical_json(value) != raw:
        raise FreezeError(f"noncanonical retained JSON: {label}")
    return value


def _validate_manifest_name(name: str) -> bytes:
    try:
        encoded = name.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise FreezeError(f"invalid manifest filename: {name!r}") from exc
    parts = name.split("/")
    if not name or name.startswith("/") or "\\" in name or ".." in parts:
        raise FreezeError(f"noncanonical manifest filename: {name!r}")
    return encoded


def capture_manifest(
    base: Path, names: Iterable[str]
) -> tuple[bytes, list[ManifestMember], dict[str, bytes]]:
    encoded_names: list[tuple[bytes, str]] = []
    seen: set[bytes] = set()
    for name in names:
        encoded = _validate_manifest_name(name)
        if encoded in seen:
            raise FreezeError(f"duplicate manifest filename: {name}")
        seen.add(encoded)
        encoded_names.append((encoded, name))
    encoded_names.sort(key=lambda item: item[0])

    chunks: list[bytes] = []
    members: list[ManifestMember] = []
    captured: dict[str, bytes] = {}
    for encoded, name in encoded_names:
        path = base / name
        if not path.is_file():
            raise FreezeError(f"missing manifest member: {name}")
        contents = path.read_bytes()
        captured[name] = contents
        chunks.extend((lp(encoded), u64(len(contents)), contents))
        members.append(
            ManifestMember(name, len(contents), hashlib.sha256(contents).hexdigest())
        )
    return b"".join(chunks), members, captured


def canonical_manifest(
    base: Path, names: Iterable[str]
) -> tuple[bytes, list[ManifestMember]]:
    manifest, members, _ = capture_manifest(base, names)
    return manifest, members


def verify_captured_files(base: Path, captured: Mapping[str, bytes]) -> None:
    changed = [
        name
        for name, expected in captured.items()
        if not (base / name).is_file() or (base / name).read_bytes() != expected
    ]
    if changed:
        raise FreezeError("input changed during freeze: " + ", ".join(changed))


def _typed_json(value: Any, *, allow_negative: bool) -> Any:
    """Map a frozen JSON tree to its declared TV host types."""
    if value is True or value is False:
        return value
    if type(value) is int:
        if value < 0:
            if not allow_negative:
                raise FreezeError("negative integer is not legal in this TV tree")
            return r01b_tv.I64(value)
        return r01b_tv.U64(value)
    if type(value) is str:
        return value
    if isinstance(value, list):
        return [_typed_json(item, allow_negative=allow_negative) for item in value]
    if isinstance(value, dict):
        return {
            key: _typed_json(child, allow_negative=allow_negative)
            for key, child in value.items()
        }
    raise FreezeError(f"unsupported typed JSON value: {type(value).__name__}")


def tv_bytes(value: Any) -> bytes:
    try:
        return r01b_tv.encode(value)
    except (TypeError, ValueError, r01b_tv.TVError) as exc:
        raise FreezeError(f"TV encoding failed: {exc}") from exc


def tv_hex(value: Any) -> str:
    return tv_bytes(value).hex()


def _record_hash(digest: bytes, payload: bytes) -> bytes:
    if len(digest) != 32:
        raise FreezeError("record digest is not 32 bytes")
    return sha256(RECORD_TAG + digest + u64(len(payload)) + payload)


def record(digest: bytes, payload: bytes) -> bytes:
    return digest + payload + _record_hash(digest, payload)


def absent_entry() -> dict[str, Any]:
    return {"kind": "ABSENT"}


def regular_entry(contents: bytes) -> dict[str, Any]:
    return {"kind": "REGULAR", "regular_bytes": contents}


def symlink_entry(target: bytes) -> dict[str, Any]:
    return {"kind": "SYMLINK", "symlink_target_bytes": target}


def publication_fixtures(record_p0: bytes) -> dict[str, dict[str, Any]]:
    return {
        "ABSENT_CLEAN": {
            "authoritative_entry": absent_entry(),
            "staging_entry": absent_entry(),
        },
        "VALID_P0_CLEAN": {
            "authoritative_entry": regular_entry(record_p0),
            "staging_entry": absent_entry(),
        },
        "ABSENT_TMP": {
            "authoritative_entry": absent_entry(),
            "staging_entry": regular_entry(b""),
        },
        "VALID_P0_TMP": {
            "authoritative_entry": regular_entry(record_p0),
            "staging_entry": regular_entry(b""),
        },
    }


def recovery_fixture_for_recipe(
    recipe: Mapping[str, Any], semantic_suite_digest: bytes
) -> dict[str, Any]:
    expected_keys = {
        "arg0",
        "arg1",
        "base_record_payload_hex",
        "mutation",
        "target_payload_hex",
    }
    if set(recipe) != expected_keys:
        raise FreezeError(f"recovery recipe key drift: {sorted(recipe)}")
    try:
        base_payload = bytes.fromhex(recipe["base_record_payload_hex"])
        target_payload = bytes.fromhex(recipe["target_payload_hex"])
    except (TypeError, ValueError) as exc:
        raise FreezeError("noncanonical recipe hex") from exc
    if base_payload.hex() != recipe["base_record_payload_hex"]:
        raise FreezeError("recipe base payload hex is noncanonical")
    if target_payload.hex() != recipe["target_payload_hex"]:
        raise FreezeError("recipe target payload hex is noncanonical")
    arg0 = recipe["arg0"]
    arg1 = recipe["arg1"]
    if type(arg0) is not int or type(arg1) is not int:
        raise FreezeError("recipe indexes are not integers")

    source = record(semantic_suite_digest, base_payload)
    mutation = recipe["mutation"]
    auxiliary: list[dict[str, Any]] = []

    if mutation == "MISSING":
        authoritative = absent_entry()
    elif mutation == "TRUNCATE":
        if not 0 <= arg0 < len(source) or arg1 != -1:
            raise FreezeError("invalid TRUNCATE recipe")
        authoritative = regular_entry(source[:arg0])
    elif mutation == "FLIP":
        if not 0 <= arg0 < len(source) or not 0 <= arg1 < 8:
            raise FreezeError("invalid FLIP recipe")
        changed = bytearray(source)
        changed[arg0] ^= 1 << arg1
        authoritative = regular_entry(bytes(changed))
    elif mutation == "APPEND_ZERO":
        authoritative = regular_entry(source + b"\x00")
    elif mutation == "WRONG_SUITE":
        wrong = bytes([semantic_suite_digest[0] ^ 0x80]) + semantic_suite_digest[1:]
        authoritative = regular_entry(record(wrong, base_payload))
    elif mutation == "NONREGULAR":
        authoritative = symlink_entry(SYMLINK_TARGET)
        auxiliary = [
            {"name_bytes": SYMLINK_TARGET, "regular_bytes": source}
        ]
    elif mutation in ("STALE_VALID", "OTHER_VALID"):
        authoritative = regular_entry(record(semantic_suite_digest, target_payload))
    else:
        raise FreezeError(f"unregistered recovery mutation: {mutation!r}")

    if mutation not in ("TRUNCATE", "FLIP") and (arg0 != -1 or arg1 != -1):
        raise FreezeError(f"unexpected indexes for {mutation}")
    if mutation == "FLIP" and target_payload:
        raise FreezeError("FLIP unexpectedly has a target payload")
    if mutation not in ("STALE_VALID", "OTHER_VALID") and target_payload:
        raise FreezeError(f"unexpected target payload for {mutation}")

    return {
        "authoritative_entry": authoritative,
        "auxiliary_regular_entries": auxiliary,
    }


def _json_pointer(root: Any, pointer: str) -> tuple[Any, str | None]:
    if pointer == "":
        return root, None
    if not pointer.startswith("#/"):
        raise FreezeError(f"unsupported JSON pointer: {pointer!r}")
    current = root
    last: str | None = None
    for raw_token in pointer[2:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if "~" in token and re.search(r"~(?![01])", raw_token):
            raise FreezeError(f"invalid JSON pointer escape: {pointer!r}")
        last = token
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            raise FreezeError(f"unresolved JSON pointer: {pointer!r}")
    return current, last


def _native_scalar(value: Any) -> Any:
    if value is True or value is False:
        return value
    if type(value) is int:
        if value < 0:
            raise FreezeError("measurement base cannot contain I64")
        return r01b_tv.U64(value)
    if type(value) is str:
        return value
    raise FreezeError(f"unsupported schema scalar: {value!r}")


def synthesize_measurement_value(
    schema: Mapping[str, Any], root: Mapping[str, Any], *, hint: str | None = None,
    active_refs: tuple[str, ...] = (),
) -> Any:
    if "$ref" in schema:
        if set(schema) != {"$ref"}:
            raise FreezeError("measurement $ref has sibling constraints")
        pointer = schema["$ref"]
        if pointer in active_refs:
            raise FreezeError(f"cyclic measurement schema ref: {pointer}")
        resolved, resolved_hint = _json_pointer(root, pointer)
        if not isinstance(resolved, dict):
            raise FreezeError(f"measurement ref is not a schema: {pointer}")
        return synthesize_measurement_value(
            resolved,
            root,
            hint=resolved_hint,
            active_refs=active_refs + (pointer,),
        )
    if "const" in schema:
        return _native_scalar(schema["const"])
    if "enum" in schema:
        choices = schema["enum"]
        if not isinstance(choices, list) or not choices:
            raise FreezeError("empty/non-list measurement enum")
        return _native_scalar(choices[0])

    kind = schema.get("type")
    if kind == "integer":
        value = schema.get("minimum", 0)
        if type(value) is not int or value < 0:
            raise FreezeError("measurement integer minimum is not nonnegative")
        return r01b_tv.U64(value)
    if kind == "boolean":
        return False
    if kind == "array":
        count = schema.get("minItems", 0)
        if type(count) is not int or count < 0:
            raise FreezeError("measurement minItems is invalid")
        item_schema = schema.get("items")
        if not isinstance(item_schema, dict):
            raise FreezeError("measurement array lacks one item schema")
        return [
            synthesize_measurement_value(item_schema, root)
            for _ in range(count)
        ]
    if kind == "object":
        required = schema.get("required")
        properties = schema.get("properties")
        if not isinstance(required, list) or not isinstance(properties, dict):
            raise FreezeError("measurement object lacks closed required properties")
        if len(required) != len(set(required)):
            raise FreezeError("measurement object repeats a required property")
        value: dict[str, Any] = {}
        for name in required:
            child = properties.get(name)
            if not isinstance(name, str) or not isinstance(child, dict):
                raise FreezeError("measurement required property is undefined")
            value[name] = synthesize_measurement_value(child, root)
        return value
    if kind == "string":
        if hint == "sha256_hex":
            return "0" * 64
        if hint == "trial_id":
            return "r01b-" + "0" * 64
        if hint == "run_id":
            return "r01b-run-" + "0" * 64
        if hint == "hex_bytes":
            return ""
        pattern = schema.get("pattern")
        if pattern == "^[0-9a-f]{64}$":
            return "0" * 64
        if pattern == "^r01b-[0-9a-f]{64}$":
            return "r01b-" + "0" * 64
        if pattern == "^r01b-run-[0-9a-f]{64}$":
            return "r01b-run-" + "0" * 64
        if pattern == "^(?:[0-9a-f]{2})*$":
            return ""
        candidate = "" if schema.get("minLength", 0) == 0 else "x"
        if pattern is not None and re.fullmatch(pattern, candidate) is None:
            candidate = "x"
        if pattern is not None and re.fullmatch(pattern, candidate) is None:
            raise FreezeError(f"cannot synthesize string for pattern {pattern!r}")
        return candidate
    raise FreezeError(f"unsupported measurement schema kind: {kind!r}")


def build_measurement_fixture(measurements: Mapping[str, Any]) -> dict[str, Any]:
    paths = measurements.get("paths")
    native = measurements.get("native_value_kinds")
    closed = measurements.get("closed_container_schemas")
    if not isinstance(paths, list) or not isinstance(native, dict) or not isinstance(closed, dict):
        raise FreezeError("measurement registry shape drift")
    if len(paths) != MEASUREMENT_PATH_COUNT or len(set(paths)) != len(paths):
        raise FreezeError("measurement path domain is not exactly 1040 unique paths")
    if paths != sorted(paths, key=lambda value: value.encode("utf-8")):
        raise FreezeError("measurement paths are not in unsigned UTF-8 order")
    path_kinds = native.get("paths")
    definitions = native.get("definitions")
    if not isinstance(path_kinds, dict) or not isinstance(definitions, dict):
        raise FreezeError("measurement native-kind registry shape drift")
    if set(path_kinds) != set(paths):
        raise FreezeError("measurement native-kind paths do not close")

    fixture: dict[str, Any] = {}
    for path in paths:
        kind = path_kinds[path]
        if kind in definitions:
            schema = definitions[kind]
        elif kind in closed:
            schema = closed[kind]
        else:
            raise FreezeError(f"unregistered measurement native kind: {kind}")
        if not isinstance(schema, dict):
            raise FreezeError(f"measurement native schema is not a map: {kind}")
        fixture[path] = synthesize_measurement_value(schema, measurements, hint=kind)
    return fixture


def _case_id(identity: Any) -> str:
    return "r01b-case-" + hashlib.sha256(CASE_TAG + tv_bytes(identity)).hexdigest()


def _trial_id(d0: Any) -> str:
    return "r01b-" + hashlib.sha256(TRIAL_TAG + tv_bytes(d0)).hexdigest()


def _canonical_hex(value: Any, label: str) -> bytes:
    if type(value) is not str or len(value) % 2:
        raise FreezeError(f"invalid {label} hex")
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise FreezeError(f"invalid {label} hex") from exc
    if raw.hex() != value:
        raise FreezeError(f"noncanonical {label} hex")
    return raw


def _build_subject_d0(
    row: Mapping[str, Any], semantic_suite_digest: bytes
) -> tuple[dict[str, Any], str]:
    case_id = row["case_id"]
    identity = row["identity"]
    metadata = row["metadata"]
    typed_identity = _typed_json(identity, allow_negative=True)
    if _case_id(typed_identity) != case_id:
        raise FreezeError(f"subject case-ID derivation mismatch: {case_id}")

    production = identity["history_production"]
    common: dict[str, Any] = {
        "backend": identity["backend"],
        "case_id": case_id,
        "continuation": _canonical_hex(identity["continuation_hex"], "continuation"),
        "history_production": production,
        "mechanism_manifest": identity["mechanism_manifest"],
        "observer_profile": identity["observer_profile"],
        "repetition": r01b_tv.U64(identity["repetition"]),
    }
    if production == "PUBLICATION":
        common.update(
            {
                "cut": identity["cut"],
                "injected_fault": identity["injected_fault"],
                "requested_payload": _canonical_hex(
                    identity["requested_payload_hex"], "requested payload"
                ),
                "setup": identity["setup"],
            }
        )
    elif production == "RECOVERY_ONLY":
        common["recovery_fixture"] = recovery_fixture_for_recipe(
            identity["recovery_fixture_recipe"], semantic_suite_digest
        )
    else:
        raise FreezeError(f"unregistered subject history production: {production}")
    reachability = metadata.get("cut_reachability")
    if type(reachability) is not str:
        raise FreezeError("subject row lacks expected reachability")
    return common, reachability


def _edge_incidence(
    comparison_edges: Sequence[Mapping[str, Any]], subject_ids: set[str]
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    edge_ids: dict[str, list[str]] = {case_id: [] for case_id in subject_ids}
    partners: dict[str, list[str]] = {case_id: [] for case_id in subject_ids}
    seen: set[str] = set()
    for edge in comparison_edges:
        edge_id = edge.get("edge_id")
        identity = edge.get("identity")
        if type(edge_id) is not str or not isinstance(identity, dict):
            raise FreezeError("comparison edge shape drift")
        if edge_id in seen:
            raise FreezeError(f"duplicate comparison edge: {edge_id}")
        seen.add(edge_id)
        left = identity.get("left_case_id")
        right = identity.get("right_case_id")
        if left not in subject_ids or right not in subject_ids or left == right:
            raise FreezeError(f"comparison edge endpoint drift: {edge_id}")
        edge_ids[left].append(edge_id)
        edge_ids[right].append(edge_id)
        partners[left].append(right)
        partners[right].append(left)
    for case_id in subject_ids:
        edge_ids[case_id].sort(key=lambda value: value.encode("ascii"))
        partners[case_id].sort(key=lambda value: value.encode("ascii"))
        if len(edge_ids[case_id]) != len(set(edge_ids[case_id])):
            raise FreezeError(f"duplicate incident edge: {case_id}")
        if len(partners[case_id]) != len(set(partners[case_id])):
            raise FreezeError(f"duplicate comparison partner: {case_id}")
    return edge_ids, partners


def build_s1(
    *, descriptors: Mapping[str, Any], oracle: Mapping[str, Any],
    holdouts: Mapping[str, Any], measurements: Mapping[str, Any],
    suite: Mapping[str, Any], semantic_suite_digest: bytes,
) -> tuple[dict[str, Any], dict[str, Any]]:
    subject_rows = descriptors.get("rows")
    oracle_rows = oracle.get("rows")
    lab_rows = holdouts.get("rows")
    comparison_edges = oracle.get("comparison_edges")
    if not all(isinstance(value, list) for value in (
        subject_rows, oracle_rows, lab_rows, comparison_edges
    )):
        raise FreezeError("source registry row shape drift")
    if len(subject_rows) != SUBJECT_ROW_COUNT or len(lab_rows) != LAB_ROW_COUNT:
        raise FreezeError("subject/LAB row counts drifted")

    subject_ids = {row["case_id"] for row in subject_rows}
    lab_ids = {row["case_id"] for row in lab_rows}
    if len(subject_ids) != SUBJECT_ROW_COUNT or len(lab_ids) != LAB_ROW_COUNT:
        raise FreezeError("source case IDs are not unique")
    if subject_ids & lab_ids:
        raise FreezeError("subject and LAB case-ID domains collide")
    oracle_by_case = {row["case_id"]: row for row in oracle_rows}
    if len(oracle_by_case) != SUBJECT_ROW_COUNT or set(oracle_by_case) != subject_ids:
        raise FreezeError("subject literal oracle is not a bijection")

    incident_edges, partners = _edge_incidence(comparison_edges, subject_ids)
    descriptor_candidates: list[tuple[str, dict[str, Any]]] = []
    d0_by_case: dict[str, bytes] = {}
    subject_by_case = {row["case_id"]: row for row in subject_rows}

    for case_id, row in subject_by_case.items():
        d0, reachability = _build_subject_d0(row, semantic_suite_digest)
        d0_raw = tv_bytes(d0)
        d0_by_case[case_id] = d0_raw
        trial_id = _trial_id(d0)
        source_edge_ids = oracle_by_case[case_id]["expected"].get(
            "comparison_edge_ids", []
        )
        if source_edge_ids != incident_edges[case_id]:
            raise FreezeError(f"oracle incidence mismatch: {case_id}")
        descriptor_candidates.append(
            (
                trial_id,
                {
                    "case_id": case_id,
                    "comparison_edge_ids": incident_edges[case_id],
                    "comparison_partner_case_ids": partners[case_id],
                    "descriptor_template_tv_hex": d0_raw.hex(),
                    "expected_reachability": reachability,
                    "history_production": row["identity"]["history_production"],
                    "ordinal": -1,
                    "trial_id": trial_id,
                },
            )
        )

    for row in lab_rows:
        case_id = row["case_id"]
        body = row["body"]
        typed_body = _typed_json(body, allow_negative=False)
        if _case_id(typed_body) != case_id:
            raise FreezeError(f"LAB case-ID derivation mismatch: {case_id}")
        if body.get("history_production") != "LAB_ONLY":
            raise FreezeError(f"non-LAB row in holdout registry: {case_id}")
        d0 = {"case_id": case_id, "lab_input": typed_body}
        d0_raw = tv_bytes(d0)
        d0_by_case[case_id] = d0_raw
        trial_id = _trial_id(d0)
        descriptor_candidates.append(
            (
                trial_id,
                {
                    "case_id": case_id,
                    "comparison_edge_ids": [],
                    "comparison_partner_case_ids": [],
                    "descriptor_template_tv_hex": d0_raw.hex(),
                    "history_production": "LAB_ONLY",
                    "ordinal": -1,
                    "trial_id": trial_id,
                },
            )
        )

    descriptor_candidates.sort(key=lambda item: item[0].encode("ascii"))
    trial_ids = [item[0] for item in descriptor_candidates]
    if len(trial_ids) != TOTAL_ROW_COUNT or len(set(trial_ids)) != TOTAL_ROW_COUNT:
        raise FreezeError("final trial IDs are not exactly 6318 unique values")
    descriptor_rows: list[dict[str, Any]] = []
    for ordinal, (_, row) in enumerate(descriptor_candidates):
        row["ordinal"] = ordinal
        descriptor_rows.append(row)

    positions = suite.get("opaque_positions")
    if not isinstance(positions, dict):
        raise FreezeError("suite opaque positions missing")
    payloads = [
        _canonical_hex(positions["P0_hex"], "P0"),
        _canonical_hex(positions["P1_hex"], "P1"),
    ]
    payloads.sort()
    if len(set(payloads)) != 2:
        raise FreezeError("P0 and P1 are not distinct")
    records = {payload: record(semantic_suite_digest, payload) for payload in payloads}
    record_rows = [
        {"payload_hex": payload.hex(), "record_hex": records[payload].hex()}
        for payload in payloads
    ]
    if [len(records[payload]) for payload in payloads] != [64, 65]:
        raise FreezeError("base record lengths drifted")

    setups = publication_fixtures(records[b""])
    setup_rows = [
        {"fixture_tv_hex": tv_hex(fixture), "setup": setup}
        for setup, fixture in sorted(
            setups.items(), key=lambda item: item[0].encode("ascii")
        )
    ]

    recipes_by_tv: dict[bytes, Mapping[str, Any]] = {}
    for row in subject_rows:
        identity = row["identity"]
        if identity["history_production"] != "RECOVERY_ONLY":
            continue
        recipe = identity["recovery_fixture_recipe"]
        recipe_raw = tv_bytes(_typed_json(recipe, allow_negative=True))
        prior = recipes_by_tv.setdefault(recipe_raw, recipe)
        if prior != recipe:
            raise FreezeError("one recipe TV value has unequal source maps")
    if len(recipes_by_tv) != RECIPE_COUNT:
        raise FreezeError(f"expected 1172 recipes, got {len(recipes_by_tv)}")
    recovery_rows: list[dict[str, str]] = []
    unique_fixture_hex: set[str] = set()
    for recipe_raw in sorted(recipes_by_tv):
        fixture = recovery_fixture_for_recipe(
            recipes_by_tv[recipe_raw], semantic_suite_digest
        )
        fixture_hex = tv_hex(fixture)
        unique_fixture_hex.add(fixture_hex)
        recovery_rows.append(
            {"fixture_tv_hex": fixture_hex, "recipe_tv_hex": recipe_raw.hex()}
        )
    if len(unique_fixture_hex) != UNIQUE_FIXTURE_COUNT:
        raise FreezeError(
            f"expected 1137 exact recovery fixtures, got {len(unique_fixture_hex)}"
        )

    literal_rows: list[dict[str, Any]] = []
    for row in oracle_rows:
        literal_rows.append(copy.deepcopy(row))
    for row in lab_rows:
        literal_rows.append(
            {"case_id": row["case_id"], "expected": copy.deepcopy(row["expected"])}
        )
    literal_rows.sort(key=lambda row: row["case_id"].encode("ascii"))
    literal_ids = [row["case_id"] for row in literal_rows]
    if literal_ids != sorted(subject_ids | lab_ids, key=lambda value: value.encode("ascii")):
        raise FreezeError("final literal rows are not an exact sorted bijection")

    measurement_fixture = build_measurement_fixture(measurements)
    measurement_tv = tv_bytes(measurement_fixture)

    s1 = {
        "descriptor_registry": {
            "row_count": TOTAL_ROW_COUNT,
            "rows": descriptor_rows,
        },
        "fixture_and_mutation_registry": {
            "publication_setups": setup_rows,
            "record_by_payload": record_rows,
            "recovery_recipes": recovery_rows,
        },
        "literal_oracle_registry": {
            "comparison_edges": copy.deepcopy(comparison_edges),
            "rows": literal_rows,
        },
        "measurement_base_fixture": {
            "fixture_tv_hex": measurement_tv.hex(),
            "fixture_tv_sha256": hashlib.sha256(measurement_tv).hexdigest(),
            "path_count": MEASUREMENT_PATH_COUNT,
        },
        "schema_id": "R01B-S1-1",
        "semantic_suite_digest": semantic_suite_digest.hex(),
    }

    subject_check_count = sum(
        len(row["expected"]["conformance_check_keys"]) for row in oracle_rows
    )
    lab_check_count = sum(
        len(row["expected"]["conformance_checks"]) for row in lab_rows
    )
    if lab_check_count != LAB_ROW_COUNT * 3:
        raise FreezeError("LAB conformance-check inventory is not three per row")
    if subject_check_count != 64680:
        raise FreezeError("subject conformance-check count is not 64680")
    if oracle.get("conformance_check_count") != subject_check_count:
        raise FreezeError("subject conformance-check summary disagrees")

    diagnostics = {
        "comparison_edge_count": len(comparison_edges),
        "conformance_check_count": subject_check_count + lab_check_count,
        "descriptor_row_count": len(descriptor_rows),
        "lab_conformance_check_count": lab_check_count,
        "measurement_path_count": len(measurement_fixture),
        "recovery_recipe_count": len(recovery_rows),
        "subject_conformance_check_count": subject_check_count,
        "unique_recovery_fixture_count": len(unique_fixture_hex),
    }
    return s1, diagnostics


def build(base: Path = HERE) -> FreezeBuild:
    s0_manifest, s0_members, s0_captured = capture_manifest(base, S0_NAMES)
    if tuple(member.filename for member in s0_members) != S0_NAMES:
        raise FreezeError("S0 filename tuple is not canonical unsigned UTF-8 order")
    semantic_seed_digest = sha256(s0_manifest)

    descriptors = parse_json(
        s0_captured["R01B-DESCRIPTORS.json"], "R01B-DESCRIPTORS.json"
    )
    oracle = parse_json(
        s0_captured["R01B-LITERAL-ORACLE.json"], "R01B-LITERAL-ORACLE.json"
    )
    holdouts = parse_json(
        s0_captured["R01B-HOLDOUTS.json"], "R01B-HOLDOUTS.json"
    )
    measurements = parse_json(
        s0_captured["R01B-MEASUREMENT-REGISTRY.json"],
        "R01B-MEASUREMENT-REGISTRY.json",
    )
    suite = parse_json(s0_captured["R01B-SUITE.json"], "R01B-SUITE.json")
    positions = suite.get("opaque_positions")
    if not isinstance(positions, dict):
        raise FreezeError("suite positions missing")
    p0 = _canonical_hex(positions["P0_hex"], "P0")
    p1 = _canonical_hex(positions["P1_hex"], "P1")
    continuation = _canonical_hex(positions["C_hex"], "C")
    y0 = _canonical_hex(positions["Y0_hex"], "Y0")
    y1 = _canonical_hex(positions["Y1_hex"], "Y1")
    semantic_suite_digest = sha256(
        SUITE_TAG
        + semantic_seed_digest
        + lp(p0)
        + lp(p1)
        + lp(continuation)
        + lp(y0)
        + lp(y1)
    )

    s0_index_value = {
        "canonical_manifest_byte_length": len(s0_manifest),
        "manifest_rule": "concat(LP(filename_utf8)||u64be(file_length)||file_bytes)_in_unsigned_UTF8_filename_order",
        "member_count": len(s0_members),
        "members": [member.json_value() for member in s0_members],
        "schema_id": "R01B-S0-MANIFEST-1",
        "semantic_seed_digest": semantic_seed_digest.hex(),
        "semantic_suite_digest": semantic_suite_digest.hex(),
    }
    s0_index_bytes = canonical_json(s0_index_value, printable_ascii=True)

    s1_value, diagnostics = build_s1(
        descriptors=descriptors,
        oracle=oracle,
        holdouts=holdouts,
        measurements=measurements,
        suite=suite,
        semantic_suite_digest=semantic_suite_digest,
    )
    s1_bytes = canonical_json(s1_value, printable_ascii=True)
    s1_manifest = lp(S1_NAME.encode("utf-8")) + u64(len(s1_bytes)) + s1_bytes
    freeze_digest = sha256(
        FREEZE_TAG + lp(s0_manifest) + semantic_suite_digest + lp(s1_manifest)
    )
    semantic_freeze_id = "r01b-semantic-" + freeze_digest.hex()

    gate_manifest, gate_members, gate_captured = capture_manifest(
        base, GATE_MACHINERY_NAMES
    )
    closure_value = {
        "acyclic_dependency_order": [
            "S0_manifest_bytes",
            "semantic_seed_digest",
            "semantic_suite_digest",
            "R01B-S1.json",
            "S1_manifest_bytes",
            "semantic_freeze_id",
        ],
        "cycle_exclusions": {
            "final_freeze_artifact_is_manifest_member": False,
            "semantic_freeze_id_in_descriptor_templates": False,
            "semantic_freeze_id_in_s0_or_s1": False,
            "s0_index_is_s0_member": False,
            "s1_contains_realization_id": False,
        },
        "gate_machinery": {
            "canonical_manifest_byte_length": len(gate_manifest),
            "manifest_sha256": hashlib.sha256(gate_manifest).hexdigest(),
            "member_count": len(gate_members),
            "members": [member.json_value() for member in gate_members],
            "semantic_hash_input": False,
        },
        "s0": {
            "canonical_manifest_byte_length": len(s0_manifest),
            "manifest_sha256": semantic_seed_digest.hex(),
            "member_count": len(s0_members),
            "source_index": S0_INDEX_NAME,
            "source_index_sha256": hashlib.sha256(s0_index_bytes).hexdigest(),
        },
        "s1": {
            "file": S1_NAME,
            "file_byte_length": len(s1_bytes),
            "file_sha256": hashlib.sha256(s1_bytes).hexdigest(),
            "manifest_byte_length": len(s1_manifest),
            "manifest_sha256": hashlib.sha256(s1_manifest).hexdigest(),
            "member_count": 1,
        },
        "schema_id": "R01B-SEMANTIC-FREEZE-1",
        "semantic_freeze_id": semantic_freeze_id,
        "semantic_suite_digest": semantic_suite_digest.hex(),
    }
    closure_bytes = canonical_json(closure_value, printable_ascii=True)
    verify_captured_files(base, s0_captured)
    verify_captured_files(base, gate_captured)
    return FreezeBuild(
        s0_index_value=s0_index_value,
        s0_index_bytes=s0_index_bytes,
        s0_manifest_bytes=s0_manifest,
        semantic_seed_digest=semantic_seed_digest,
        semantic_suite_digest=semantic_suite_digest,
        s1_value=s1_value,
        s1_bytes=s1_bytes,
        s1_manifest_bytes=s1_manifest,
        semantic_freeze_id=semantic_freeze_id,
        gate_manifest_bytes=gate_manifest,
        closure_value=closure_value,
        closure_bytes=closure_bytes,
        diagnostics=diagnostics,
    )


def _check_outputs(base: Path, result: FreezeBuild) -> None:
    mismatches: list[str] = []
    for name, expected in result.outputs().items():
        path = base / name
        if not path.is_file():
            mismatches.append(f"missing {name}")
        elif path.read_bytes() != expected:
            mismatches.append(f"byte mismatch {name}")
    if mismatches:
        raise FreezeError("semantic freeze check failed: " + "; ".join(mismatches))


def _write_outputs(base: Path, result: FreezeBuild) -> None:
    for name, contents in result.outputs().items():
        (base / name).write_bytes(contents)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args(argv)
    output_dir = args.output_dir.resolve()
    result = build(output_dir)
    if args.check:
        _check_outputs(output_dir, result)
    else:
        _write_outputs(output_dir, result)
    for name, contents in result.outputs().items():
        print(f"{name} bytes={len(contents)} sha256={hashlib.sha256(contents).hexdigest()}")
    print(f"semantic_freeze_id={result.semantic_freeze_id}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FreezeError as exc:
        raise SystemExit(str(exc)) from exc
