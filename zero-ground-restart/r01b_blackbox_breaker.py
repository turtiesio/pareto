#!/usr/bin/env python3
"""Ontology-independent black-box breaker for the frozen R0.1B corpus.

This module deliberately imports no R0.1B implementation, runner, codec, or
Rust code.  It derives identities and expectations from the frozen S0/S1
artifacts and implements a second TV codec locally.  Its JSON input format is
only an invocation carrier for exact envelopes; it is not offered as a repair
for the missing R0.1B canonical-record grammar.

The breaker has no PASS result while a frozen contract defect makes a required
wire value or realization identity nonconstructible.  UNKNOWN is never treated
as equality or success.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPORT_NAME = "R01B-BLACKBOX-BREAKER.json"
ENVELOPE_PREFIX = b"ZGR01B-ENVELOPE\x00\x00\x01"
CASE_DOMAIN = b"ZGR01B-CASE\x00"
TRIAL_DOMAIN = b"ZGR01B-TRIAL\x00"
MANDATORY_ATTACKS = (
    "DELETE",
    "MERGE",
    "DERIVE",
    "RECOMPUTE",
    "COLLIDE",
    "FUTURE",
    "EXTERNALIZE",
    "REALIZE",
    "COGNITION",
    "TCB",
)


class BreakerError(ValueError):
    """An independently detected malformed value or frozen-artifact conflict."""


@dataclass(frozen=True)
class U64:
    value: int


@dataclass(frozen=True)
class I64:
    value: int


@dataclass(frozen=True)
class StructuredUnknown:
    reason: str
    needed_evidence: str


@dataclass(frozen=True)
class StructuredUnsupported:
    reason: str


@dataclass(frozen=True, order=True)
class ClosedEnum:
    namespace: int
    code: int


def _u16(value: int) -> bytes:
    if not 0 <= value <= 0xFFFF:
        raise BreakerError(f"u16 out of range: {value}")
    return struct.pack(">H", value)


def _u64(value: int) -> bytes:
    if not 0 <= value <= 0xFFFFFFFFFFFFFFFF:
        raise BreakerError(f"u64 out of range: {value}")
    return struct.pack(">Q", value)


def tv_from_json(value: Any) -> Any:
    """Apply section 4.1's JSON-to-TV rule, without implementation imports."""

    if value is None or isinstance(value, float):
        raise BreakerError("null and floating point have no R0.1B TV value")
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return U64(value) if value >= 0 else I64(value)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [tv_from_json(item) for item in value]
    if isinstance(value, dict):
        return {key: tv_from_json(item) for key, item in value.items()}
    raise BreakerError(f"unsupported JSON value: {type(value).__name__}")


def encode_tv(value: Any) -> bytes:
    """Independent implementation of REALIZATION-CORRECTION-R01B section 3."""

    if isinstance(value, U64):
        return b"\x01" + _u64(value.value)
    if isinstance(value, I64):
        if not -(1 << 63) <= value.value < (1 << 63):
            raise BreakerError(f"i64 out of range: {value.value}")
        return b"\x02" + struct.pack(">q", value.value)
    if isinstance(value, bytes):
        return b"\x03" + _u64(len(value)) + value
    if isinstance(value, str):
        raw = value.encode("utf-8")
        return b"\x04" + _u64(len(raw)) + raw
    if value is False:
        return b"\x05"
    if value is True:
        return b"\x06"
    if isinstance(value, list) or isinstance(value, tuple):
        return b"\x07" + _u64(len(value)) + b"".join(encode_tv(v) for v in value)
    if isinstance(value, dict):
        parts: list[bytes] = []
        prior: bytes | None = None
        for key in sorted(value, key=lambda item: item.encode("ascii")):
            if not isinstance(key, str):
                raise BreakerError("TV map key is not text")
            raw_key = key.encode("ascii")
            if any(byte < 0x20 or byte > 0x7E for byte in raw_key):
                raise BreakerError("TV map key is not printable ASCII")
            if prior is not None and raw_key <= prior:
                raise BreakerError("duplicate or unsorted TV map key")
            prior = raw_key
            parts.append(_u16(len(raw_key)) + raw_key + encode_tv(value[key]))
        return b"\x08" + _u64(len(parts)) + b"".join(parts)
    if isinstance(value, StructuredUnknown):
        if not value.reason or not value.needed_evidence:
            raise BreakerError("structured unknown members must be nonempty")
        return b"\x09" + encode_tv(value.reason) + encode_tv(value.needed_evidence)
    if isinstance(value, StructuredUnsupported):
        if not value.reason:
            raise BreakerError("structured unsupported reason must be nonempty")
        return b"\x0a" + encode_tv(value.reason)
    if isinstance(value, ClosedEnum):
        return b"\x0b" + _u16(value.namespace) + _u16(value.code)
    if isinstance(value, int):
        raise BreakerError("bare integers are not typed TV integers")
    raise BreakerError(f"unsupported TV value: {type(value).__name__}")


class _TVReader:
    def __init__(self, data: bytes):
        self.data = data
        self.at = 0

    def _take(self, count: int) -> bytes:
        if count < 0 or self.at + count > len(self.data):
            raise BreakerError("truncated TV value")
        result = self.data[self.at : self.at + count]
        self.at += count
        return result

    def _number(self, width: int, signed: bool = False) -> int:
        return int.from_bytes(self._take(width), "big", signed=signed)

    def read(self) -> Any:
        tag = self._number(1)
        if tag == 0x01:
            return U64(self._number(8))
        if tag == 0x02:
            return I64(self._number(8, signed=True))
        if tag == 0x03:
            return self._take(self._number(8))
        if tag == 0x04:
            raw = self._take(self._number(8))
            try:
                return raw.decode("utf-8", errors="strict")
            except UnicodeDecodeError as error:
                raise BreakerError("invalid TV UTF-8 text") from error
        if tag == 0x05:
            return False
        if tag == 0x06:
            return True
        if tag == 0x07:
            return [self.read() for _ in range(self._number(8))]
        if tag == 0x08:
            result: dict[str, Any] = {}
            prior: bytes | None = None
            for _ in range(self._number(8)):
                raw_key = self._take(self._number(2))
                if any(byte < 0x20 or byte > 0x7E for byte in raw_key):
                    raise BreakerError("TV map key is not printable ASCII")
                if prior is not None and raw_key <= prior:
                    raise BreakerError("TV map keys are duplicate or out of order")
                prior = raw_key
                key = raw_key.decode("ascii")
                result[key] = self.read()
            return result
        if tag == 0x09:
            reason, evidence = self.read(), self.read()
            if not isinstance(reason, str) or not isinstance(evidence, str):
                raise BreakerError("structured unknown members are not text")
            if not reason or not evidence:
                raise BreakerError("structured unknown members are empty")
            return StructuredUnknown(reason, evidence)
        if tag == 0x0A:
            reason = self.read()
            if not isinstance(reason, str) or not reason:
                raise BreakerError("structured unsupported reason is not nonempty text")
            return StructuredUnsupported(reason)
        if tag == 0x0B:
            return ClosedEnum(self._number(2), self._number(2))
        raise BreakerError(f"unregistered TV tag: 0x{tag:02x}")


def decode_tv(data: bytes) -> Any:
    reader = _TVReader(data)
    value = reader.read()
    if reader.at != len(data):
        raise BreakerError(f"trailing bytes after TV value: {len(data) - reader.at}")
    if encode_tv(value) != data:
        raise BreakerError("TV value is not canonical")
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_report_bytes(value: Mapping[str, Any]) -> bytes:
    """Encode a retained breaker report without host formatting or a newline."""

    return canonical_json_bytes(value)


def _read_canonical_json(path: Path, *, require_canonical: bool = False) -> Any:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BreakerError(f"invalid JSON in {path.name}: {error}") from error
    if require_canonical and canonical_json_bytes(value) != raw:
        raise BreakerError(f"noncanonical JSON bytes in {path.name}")
    return value


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive_case_id(symbolic_body: Mapping[str, Any]) -> str:
    digest = _sha256(CASE_DOMAIN + encode_tv(tv_from_json(dict(symbolic_body))))
    return "r01b-case-" + digest


def derive_trial_id(descriptor_tv: bytes) -> str:
    return "r01b-" + _sha256(TRIAL_DOMAIN + descriptor_tv)


def aggregate_full_conformance(statuses: Iterable[str]) -> str:
    values = list(statuses)
    for label in ("FAIL", "UNKNOWN", "UNSUPPORTED", "PASS"):
        if label in values:
            return label
    if all(label == "NOT_APPLICABLE" for label in values):
        return "NOT_APPLICABLE"
    raise BreakerError(f"unregistered constituent status: {values!r}")


def aggregate_behavior(statuses: Iterable[str]) -> str:
    values = list(statuses)
    for label in ("DIFFER", "UNKNOWN", "MATCH"):
        if label in values:
            return label
    if all(label == "NOT_COMPARED" for label in values):
        return "NOT_COMPARED"
    raise BreakerError(f"unregistered behavior status: {values!r}")


@dataclass(frozen=True)
class EnvelopeInspection:
    sha256: str
    byte_length: int
    value: Mapping[str, Any]
    coordinate_labels: Mapping[str, Any]
    defects: tuple[str, ...]
    undecidable: tuple[str, ...]


def _coordinate_tables(status_registry: Mapping[str, Any]) -> dict[str, dict[ClosedEnum, str]]:
    tables: dict[str, dict[ClosedEnum, str]] = {}
    for name, table in status_registry["status_coordinate_registry"].items():
        namespace = table["namespace"]
        tables[name] = {
            ClosedEnum(namespace, item["code"]): item["label"] for item in table["codes"]
        }
    return tables


def inspect_envelope(data: bytes, status_registry: Mapping[str, Any]) -> EnvelopeInspection:
    if not data.startswith(ENVELOPE_PREFIX):
        raise BreakerError("wrong R0.1B envelope magic or version")
    value = decode_tv(data[len(ENVELOPE_PREFIX) :])
    if not isinstance(value, dict):
        raise BreakerError("envelope TV body is not a map")
    expected_outer = {
        "canonical_records",
        "inventory_pack",
        "raw_measurement_pack",
        "raw_trace_pack",
        "status_coordinates",
    }
    if set(value) != expected_outer:
        raise BreakerError(
            f"envelope keys differ: missing={sorted(expected_outer-set(value))}, "
            f"extra={sorted(set(value)-expected_outer)}"
        )
    for name in ("raw_trace_pack", "raw_measurement_pack"):
        if not isinstance(value[name], bytes):
            raise BreakerError(f"{name} is not the contract's opaque exact byte pack")

    status = value["status_coordinates"]
    if not isinstance(status, dict):
        raise BreakerError("status_coordinates is not a map")
    required = {
        "applicability",
        "execution",
        "oracle",
        "full_conformance",
        "behavioral_comparison",
        "scope",
        "failure_reasons",
        "needed_evidence",
    }
    defects: list[str] = []
    missing = sorted(required - set(status))
    extra = sorted(set(status) - required)
    if missing:
        defects.append("missing status members: " + ",".join(missing))
    if extra:
        defects.append("extra status members: " + ",".join(extra))

    tables = _coordinate_tables(status_registry)
    labels: dict[str, Any] = {}
    for name in (
        "applicability",
        "execution",
        "oracle",
        "full_conformance",
        "behavioral_comparison",
    ):
        if name not in status:
            continue
        coordinate = status[name]
        if coordinate not in tables[name]:
            defects.append(f"unregistered {name} enum: {coordinate!r}")
        else:
            labels[name] = tables[name][coordinate]

    if "scope" in status:
        scopes = status["scope"]
        if not isinstance(scopes, list):
            defects.append("scope is not a list")
        else:
            scope_labels: list[str] = []
            for coordinate in scopes:
                if coordinate not in tables["scope"]:
                    defects.append(f"unregistered scope enum: {coordinate!r}")
                else:
                    scope_labels.append(tables["scope"][coordinate])
            if scopes != sorted(scopes):
                defects.append("scope is not sorted by closed-enum TV order")
            labels["scope"] = scope_labels

    if "needed_evidence" in status:
        evidence = status["needed_evidence"]
        if not isinstance(evidence, list) or any(not isinstance(x, str) or not x for x in evidence):
            defects.append("needed_evidence is not a list of nonempty text")
        else:
            labels["needed_evidence"] = evidence

    undecidable: list[str] = [
        "canonical_records has no frozen inner framing or record schema"
    ]
    if "needed_evidence" in status and isinstance(status["needed_evidence"], list):
        if len(status["needed_evidence"]) > 1:
            undecidable.append("needed_evidence sort key is not frozen")

    if "failure_reasons" in status:
        reasons = status["failure_reasons"]
        if not isinstance(reasons, list) or any(not isinstance(x, ClosedEnum) for x in reasons):
            defects.append("failure_reasons is not a list of closed enums")
        else:
            # The source registry has code/label but no namespace, so no exact
            # mapping can be independently checked here.
            labels["failure_reasons"] = [asdict(item) for item in reasons]
            if reasons:
                undecidable.append("failure-reason enum namespace is not frozen")
            if labels.get("full_conformance") == "FAIL" and not reasons:
                defects.append("FAIL has an empty failure_reasons list")
            if labels.get("full_conformance") not in (None, "FAIL") and reasons:
                defects.append("non-FAIL has a nonempty failure_reasons list")

    return EnvelopeInspection(
        sha256=_sha256(data),
        byte_length=len(data),
        value=value,
        coordinate_labels=labels,
        defects=tuple(defects),
        undecidable=tuple(undecidable),
    )


class FrozenCorpus:
    """Independent reconstruction of frozen identities and check oracles."""

    def __init__(self, directory: Path = HERE):
        self.directory = directory
        self.descriptors_s0 = _read_canonical_json(directory / "R01B-DESCRIPTORS.json")
        self.holdouts_s0 = _read_canonical_json(directory / "R01B-HOLDOUTS.json")
        self.status_registry = _read_canonical_json(directory / "R01B-STATUS-REGISTRY.json")
        self.s1 = _read_canonical_json(directory / "R01B-S1.json", require_canonical=True)
        self.closure = _read_canonical_json(directory / "R01B-SEMANTIC-FREEZE.json")
        self._validate_and_index()

    def _validate_and_index(self) -> None:
        symbolic: dict[str, Mapping[str, Any]] = {}
        for row in self.descriptors_s0["rows"]:
            computed = derive_case_id(row["identity"])
            if row["case_id"] != computed:
                raise BreakerError(f"subject S0 case ID mismatch: {row['case_id']}")
            symbolic[computed] = row["identity"]
        for row in self.holdouts_s0["rows"]:
            computed = derive_case_id(row["body"])
            if row["case_id"] != computed:
                raise BreakerError(f"LAB S0 case ID mismatch: {row['case_id']}")
            if computed in symbolic:
                raise BreakerError(f"subject/LAB case collision: {computed}")
            symbolic[computed] = row["body"]

        rows = self.s1["descriptor_registry"]["rows"]
        if len(rows) != 6318 or self.s1["descriptor_registry"]["row_count"] != len(rows):
            raise BreakerError("S1 descriptor count is not the frozen 6318")
        if [row["ordinal"] for row in rows] != list(range(len(rows))):
            raise BreakerError("S1 ordinals are not contiguous zero-based positions")
        if [row["trial_id"] for row in rows] != sorted(row["trial_id"] for row in rows):
            raise BreakerError("S1 descriptor rows are not sorted by trial ID")

        descriptors: dict[str, Mapping[str, Any]] = {}
        trial_ids: set[str] = set()
        for row in rows:
            case_id = row["case_id"]
            if case_id not in symbolic:
                raise BreakerError(f"S1 case has no independently derived S0 identity: {case_id}")
            raw_tv = bytes.fromhex(row["descriptor_template_tv_hex"])
            descriptor = decode_tv(raw_tv)
            if not isinstance(descriptor, dict) or descriptor.get("case_id") != case_id:
                raise BreakerError(f"descriptor TV/case linkage mismatch: {case_id}")
            trial_id = derive_trial_id(raw_tv)
            if row["trial_id"] != trial_id or trial_id in trial_ids:
                raise BreakerError(f"trial identity mismatch or collision: {trial_id}")
            trial_ids.add(trial_id)
            descriptors[case_id] = row

        literal_rows = self.s1["literal_oracle_registry"]["rows"]
        if [row["case_id"] for row in literal_rows] != sorted(row["case_id"] for row in literal_rows):
            raise BreakerError("literal rows are not sorted by case ID")
        literal = {row["case_id"]: row["expected"] for row in literal_rows}
        if set(literal) != set(descriptors):
            raise BreakerError("descriptor/literal case linkage is not bijective")

        edges = {
            edge["edge_id"]: edge
            for edge in self.s1["literal_oracle_registry"]["comparison_edges"]
        }
        if len(edges) != 2010:
            raise BreakerError("comparison edge count is not the frozen 2010")
        for edge_id, edge in edges.items():
            identity = edge["identity"]
            for side in ("left_case_id", "right_case_id"):
                if identity[side] not in descriptors:
                    raise BreakerError(f"edge {edge_id} names absent {side}")

        conditional = set(
            _read_canonical_json(self.directory / "R01B-LITERAL-ORACLE.json")
            ["conformance_check_registry"]["conditional_checks"]
        )
        check_status: dict[tuple[str, str], str] = {}
        for case_id, expected in literal.items():
            if "conformance_check_keys" in expected:
                for key in expected["conformance_check_keys"]:
                    if key in conditional:
                        status = "UNKNOWN"
                    elif key.startswith("COMPARISON_EDGE/"):
                        edge_id = key.split("/", 1)[1]
                        if edge_id not in edges:
                            raise BreakerError(f"check refers to absent edge: {key}")
                        status = "UNKNOWN" if edges[edge_id]["expected_result"] == "UNKNOWN" else "PASS"
                    else:
                        status = "PASS"
                    check_status[(case_id, key)] = status
                rebuilt = aggregate_full_conformance(
                    check_status[(case_id, key)] for key in expected["conformance_check_keys"]
                )
                if rebuilt != expected["status_coordinates"]["full_conformance"]:
                    raise BreakerError(f"subject full-conformance reconstruction mismatch: {case_id}")
            else:
                for check in expected["conformance_checks"]:
                    identity = (case_id, check["check_id"])
                    if identity in check_status:
                        raise BreakerError(f"duplicate LAB check identity: {identity}")
                    check_status[identity] = check["expected_status"]["label"]
                rebuilt = aggregate_full_conformance(
                    item["expected_status"]["label"] for item in expected["conformance_checks"]
                )
                if rebuilt != expected["status_coordinates"]["full_conformance"]["label"]:
                    raise BreakerError(f"LAB full-conformance reconstruction mismatch: {case_id}")

        self.symbolic = symbolic
        self.descriptors = descriptors
        self.literal = literal
        self.edges = edges
        self.check_status = check_status
        self.subject_check_count = sum(
            1 for (case_id, _key) in check_status
            if descriptors[case_id]["history_production"] != "LAB_ONLY"
        )
        self.lab_check_count = len(check_status) - self.subject_check_count
        if self.subject_check_count != 64680 or self.lab_check_count != 9870:
            raise BreakerError("independently reconstructed check counts differ from freeze")

    @property
    def semantic_freeze_id(self) -> str:
        return self.closure["semantic_freeze_id"]

    def expected_fingerprint(self, case_id: str) -> bytes:
        if case_id not in self.literal:
            raise BreakerError(f"unknown frozen case: {case_id}")
        return canonical_json_bytes(self.literal[case_id])

    def positive_replay_fixture(self) -> tuple[str, bytes]:
        for row in self.holdouts_s0["rows"]:
            if row["body"].get("logical_id") == "EVIDENCE_REPLAY_POSITIVE":
                return row["case_id"], bytes.fromhex(row["body"]["fixture"]["envelope_hex"])
        raise BreakerError("EVIDENCE_REPLAY_POSITIVE is absent")


@dataclass(frozen=True)
class Finding:
    finding_id: str
    classification: str
    attacks: tuple[str, ...]
    responsibility: str
    summary: str
    smallest_witness: Mapping[str, Any]
    where_complexity_is_now: str


def _realization_manifest_witness() -> Mapping[str, Any]:
    member_name = b"x"
    member_bytes = b"y"
    raw_concatenation = member_name + member_bytes
    r0_style = struct.pack(">I", len(member_name)) + member_name + _u64(len(member_bytes)) + member_bytes
    return {
        "same_inventory": [{"relative_name_hex": member_name.hex(), "bytes_hex": member_bytes.hex()}],
        "candidate_preimage_1_hex": raw_concatenation.hex(),
        "candidate_preimage_1_sha256": _sha256(raw_concatenation),
        "candidate_preimage_2_hex": r0_style.hex(),
        "candidate_preimage_2_sha256": _sha256(r0_style),
        "distinguishing_future": "compare submitted realization_id or A_real bytes",
    }


def _needed_evidence_sort_witness() -> Mapping[str, Any]:
    values = ["z", "aa"]
    utf8_order = sorted(values, key=lambda item: item.encode("utf-8"))
    tv_order = sorted(values, key=lambda item: encode_tv(item))
    return {
        "values": values,
        "unsigned_utf8_order": utf8_order,
        "raw_tv_order": tv_order,
        "unsigned_utf8_list_tv_hex": encode_tv(utf8_order).hex(),
        "raw_tv_list_tv_hex": encode_tv(tv_order).hex(),
        "distinguishing_future": "exact envelope replay or bytewise verifier comparison",
    }


def contract_findings(corpus: FrozenCorpus) -> list[Finding]:
    replay_case, replay_envelope = corpus.positive_replay_fixture()
    replay = inspect_envelope(replay_envelope, corpus.status_registry)
    missing_lists = sorted(
        {"failure_reasons", "needed_evidence"} - set(replay.value["status_coordinates"])
    )
    if missing_lists != ["failure_reasons", "needed_evidence"]:
        raise BreakerError("frozen replay witness no longer has the audited status deletion")
    reason_shapes = {tuple(sorted(item)) for item in corpus.status_registry["failure_reason_registry"]}
    if reason_shapes != {("code", "label", "origins")}:
        raise BreakerError("failure-reason registry shape changed; namespace witness needs re-audit")
    maximum_needed_evidence = max(
        len(
            expected.get(
                "needed_evidence", expected["status_coordinates"].get("needed_evidence", [])
            )
        )
        for expected in corpus.literal.values()
    )

    return [
        Finding(
            finding_id="R01B-CONTRACT-CANONICAL-RECORD-GRAMMAR",
            classification="CONTRACT_DEFECT",
            attacks=("DELETE", "MERGE", "COLLIDE", "EXTERNALIZE", "TCB"),
            responsibility="mapping between canonical_records bytes and case/check/B observations",
            summary=(
                "Section 2 freezes only the outer field name.  It freezes no inner record "
                "shape, stream framing, event mapping, or case/check linkage, so an independent "
                "black-box verifier cannot decode the evidence used by sections 1 and 5."
            ),
            smallest_witness={
                "left_history": "one recovery observation ABSENT (wire 00)",
                "right_history": "one recovery observation REJECT (wire 01)",
                "deleted_responsibility": "record framing and recovery-observation field mapping",
                "collision": "the same opaque canonical_records byte string can be assigned either meaning",
                "distinguishing_future": "query the recovery observation",
            },
            where_complexity_is_now="an implementation-supplied decoder, prompt, or human convention in the TCB",
        ),
        Finding(
            finding_id="R01B-CONTRACT-FAILURE-REASON-NAMESPACE",
            classification="CONTRACT_DEFECT",
            attacks=("DERIVE", "COLLIDE", "FUTURE", "EXTERNALIZE", "TCB"),
            responsibility="closed-enum wire namespace for failure reasons",
            summary=(
                "Section 5 requires closed failure-reason enums and tag 0b requires a namespace, "
                "but the frozen failure_reason_registry supplies only code, label, and origins."
            ),
            smallest_witness={
                "registry_entry": {"code": 0, "label": "COMPARATOR_FALSE_MATCH"},
                "registry_entry_keys": ["code", "label", "origins"],
                "candidate_tv_hex_namespace_7": encode_tv(ClosedEnum(7, 0)).hex(),
                "candidate_tv_hex_namespace_8": encode_tv(ClosedEnum(8, 0)).hex(),
                "distinguishing_future": "exact-byte replay of a FAIL result",
            },
            where_complexity_is_now="an unregistered serializer/verifier convention",
        ),
        Finding(
            finding_id="R01B-CONTRACT-REALIZATION-ID-CONSTRUCTION",
            classification="CONTRACT_DEFECT",
            attacks=("DERIVE", "RECOMPUTE", "FUTURE", "REALIZE", "EXTERNALIZE", "TCB"),
            responsibility="A_real manifest bytes, digest preimage/domain, and final_R_id",
            summary=(
                "Section 10.2 names a broader implementation manifest and digest A_real but "
                "freezes neither its serialization nor the construction of realization_id.  "
                "R0's narrower adapter manifest is not explicitly adopted for this inventory."
            ),
            smallest_witness=_realization_manifest_witness(),
            where_complexity_is_now="the gate-R builder and launch-overlay checker, outside the frozen contract",
        ),
        Finding(
            finding_id="R01B-CONTRACT-NEEDED-EVIDENCE-SORT",
            classification="CONTRACT_DEFECT",
            attacks=("MERGE", "FUTURE", "REALIZE", "TCB"),
            responsibility="canonical order of two or more needed_evidence text values",
            summary=(
                "Section 5 says the text list is sorted but supplies no registry key.  Current "
                "lists have length at most one, so the defect is latent until a permitted future list grows."
            ),
            smallest_witness={
                **_needed_evidence_sort_witness(),
                "current_frozen_maximum_list_length": maximum_needed_evidence,
            },
            where_complexity_is_now="a serializer-specific sorting convention",
        ),
        Finding(
            finding_id="R01B-CONTRACT-POSITIVE-REPLAY-STATUS-SHAPE",
            classification="CONTRACT_DEFECT",
            attacks=("DELETE", "COLLIDE", "FUTURE"),
            responsibility="complete status coordinates in every evidence envelope",
            summary=(
                "The exact EVIDENCE_REPLAY_POSITIVE envelope omits failure_reasons and "
                "needed_evidence, although section 5 requires both lists in every result and "
                "section 2 calls this envelope member the complete coordinates."
            ),
            smallest_witness={
                "case_id": replay_case,
                "envelope_sha256": replay.sha256,
                "envelope_byte_length": replay.byte_length,
                "actual_status_keys": sorted(replay.value["status_coordinates"]),
                "missing_one_member_is_already_a_witness": missing_lists[0],
                "also_missing": missing_lists[1],
                "distinguishing_future": "schema validation or exact replay requiring an explicit empty list",
            },
            where_complexity_is_now="a verifier choice between the frozen exact fixture and prose schema",
        ),
    ]


def persistence_verdicts() -> Mapping[str, Sequence[Mapping[str, Any]]]:
    """Verdicts are responsibilities discovered by attacks, not primitive types."""

    return {
        "MUST_SURVIVE": [
            {
                "responsibility": (
                    "minimum exact boundary observations not deterministically regenerated by a rerun, "
                    "including actual B responses"
                ),
                "witness": "ABSENT 00 versus REJECT 01; a recovery query distinguishes them",
            },
            {
                "responsibility": (
                    "every exact raw trace/measurement/inventory byte that crossed L and is used "
                    "by the evidence or exact-replay claim, including observed scratch spellings "
                    "and timestamps"
                ),
                "witness": "hash-only replay and exact retained-byte replay have different permitted futures",
            },
            {
                "responsibility": "implementation inventory bytes and the specification that fixes their identity",
                "witness": "unlike loaded verifier bytes can change later interpretation of identical raw evidence",
            },
        ],
        "MAY_REBUILD": [
            {
                "responsibility": "case IDs, trial IDs, ordinals, check display identities, aggregates, and hashes",
                "specification": "the complete frozen codec/identity/order/aggregation rules plus surviving source bytes",
            },
            {
                "responsibility": "normalized per-edge comparison results",
                "specification": (
                    "exact retained B inputs/responses plus the frozen comparability and exact-byte "
                    "equality rules; UNKNOWN remains UNKNOWN when completeness is unavailable"
                ),
            },
            {
                "responsibility": "normalized constituent check statuses",
                "specification": (
                    "exact retained raw/B observations plus the identified frozen oracle, check registry, "
                    "normalizer/verifier bytes, and their execution semantics"
                ),
            },
        ],
        # An observed value inside an exact L pack is replay-visible and must
        # survive.  A name or timestamp that never crossed the boundary is not
        # a persisted item to delete.  This audit therefore found no
        # unconditional MAY_FORGET witness.
        "MAY_FORGET": [],
    }


def _attack_matrix(findings: Sequence[Finding]) -> Mapping[str, Sequence[str]]:
    matrix = {
        attack: [item.finding_id for item in findings if attack in item.attacks]
        for attack in MANDATORY_ATTACKS
    }
    # COGNITION is primarily a measured displacement, not another wire defect.
    matrix["COGNITION"] = [
        "R01B-UNKNOWN-HUMAN-DECODER-BURDEN",
        "R01B-CONTRACT-CANONICAL-RECORD-GRAMMAR",
    ]
    return matrix


def static_report(corpus: FrozenCorpus | None = None) -> Mapping[str, Any]:
    corpus = corpus or FrozenCorpus()
    findings = contract_findings(corpus)
    breaker_source = Path(__file__).read_bytes()
    test_path = HERE / "test_r01b_blackbox_breaker.py"
    test_source = test_path.read_bytes() if test_path.exists() else b""
    return {
        "schema_id": "R01B-BLACKBOX-BREAKER-REPORT-1",
        "verdict": "CONTRACT_DEFECT_UNDECIDABLE",
        "pass_awarded": False,
        "semantic_freeze_id": corpus.semantic_freeze_id,
        "boundary": (
            "frozen S0/S1/contracts/oracles/holdouts only; no subject, runner, "
            "implementation codec, or Rust import"
        ),
        "breaker_apparatus_charge": {
            "credited_as_subject_evidence_decoder": False,
            "source_byte_length": len(breaker_source),
            "source_physical_line_count": len(breaker_source.splitlines()),
            "source_sha256": _sha256(breaker_source),
            "test_byte_length": len(test_source),
            "test_physical_line_count": len(test_source.splitlines()),
            "test_sha256": _sha256(test_source),
            "runtime_dependencies": ["Python standard library"],
        },
        "independent_reconstruction": {
            "case_count": len(corpus.descriptors),
            "subject_case_count": sum(
                row["history_production"] != "LAB_ONLY" for row in corpus.descriptors.values()
            ),
            "lab_case_count": sum(
                row["history_production"] == "LAB_ONLY" for row in corpus.descriptors.values()
            ),
            "comparison_edge_count": len(corpus.edges),
            "subject_check_identity_count": corpus.subject_check_count,
            "lab_check_identity_count": corpus.lab_check_count,
        },
        "contract_defects": [asdict(item) for item in findings],
        "implementation_failures": [],
        "unknowns": [
            {
                "finding_id": "R01B-UNKNOWN-PHYSICAL-REALIZATION",
                "reason": "distinct software manifests do not establish unlike physical realization",
                "needed_evidence": "a frozen physical identity and observation protocol",
            },
            {
                "finding_id": "R01B-UNKNOWN-HUMAN-DECODER-BURDEN",
                "reason": "no executed cognition study or complete independently usable decoder exists",
                "needed_evidence": "a frozen study and independently executable evidence grammar",
            },
        ],
        "persistence": persistence_verdicts(),
        "mandatory_attack_coverage": _attack_matrix(findings),
    }


def _expected_coordinate_labels(expected: Mapping[str, Any]) -> Mapping[str, Any]:
    source = expected["status_coordinates"]
    if isinstance(source["applicability"], str):
        return source
    result = {
        name: source[name]["label"]
        for name in (
            "applicability",
            "execution",
            "oracle",
            "full_conformance",
            "behavioral_comparison",
        )
    }
    result["scope"] = [item["label"] for item in source["scope"]]
    result["failure_reasons"] = expected["failure_reasons"]
    result["needed_evidence"] = expected["needed_evidence"]
    return result


def audit_envelopes(
    envelopes: Iterable[tuple[str, bytes]], corpus: FrozenCorpus | None = None
) -> Mapping[str, Any]:
    """Audit exact raw envelopes supplied through an out-of-contract carrier.

    Envelope syntax/status contradictions can be implementation failures.
    Matching outer coordinates can never become PASS because the inner record
    grammar and gate-R construction are absent from the frozen contract.
    """

    corpus = corpus or FrozenCorpus()
    failures: list[Mapping[str, Any]] = []
    unknowns: list[Mapping[str, Any]] = []
    seen: dict[bytes, tuple[str, bytes]] = {}
    inspected: list[Mapping[str, Any]] = []
    for case_id, envelope in envelopes:
        if case_id not in corpus.literal:
            failures.append(
                {
                    "kind": "IMPLEMENTATION_FAILURE",
                    "failure_id": "UNREGISTERED_CASE",
                    "smallest_witness": {"case_id": case_id},
                }
            )
            continue
        try:
            result = inspect_envelope(envelope, corpus.status_registry)
        except BreakerError as error:
            failures.append(
                {
                    "kind": "IMPLEMENTATION_FAILURE",
                    "failure_id": "MALFORMED_ENVELOPE",
                    "smallest_witness": {"case_id": case_id, "error": str(error)},
                }
            )
            continue
        for defect in result.defects:
            failures.append(
                {
                    "kind": "IMPLEMENTATION_FAILURE",
                    "failure_id": "ENVELOPE_SCHEMA",
                    "smallest_witness": {"case_id": case_id, "error": defect},
                }
            )
        expected = _expected_coordinate_labels(corpus.literal[case_id])
        for name in (
            "applicability",
            "execution",
            "oracle",
            "full_conformance",
            "behavioral_comparison",
            "scope",
        ):
            if name in result.coordinate_labels and result.coordinate_labels[name] != expected[name]:
                failures.append(
                    {
                        "kind": "IMPLEMENTATION_FAILURE",
                        "failure_id": "STATUS_ORACLE_MISMATCH",
                        "smallest_witness": {
                            "case_id": case_id,
                            "coordinate": name,
                            "expected": expected[name],
                            "actual": result.coordinate_labels[name],
                        },
                    }
                )
        prior = seen.get(envelope)
        fingerprint = corpus.expected_fingerprint(case_id)
        if prior is not None and prior[1] != fingerprint:
            failures.append(
                {
                    "kind": "IMPLEMENTATION_FAILURE",
                    "failure_id": "DISTINGUISHABLE_HISTORY_COLLISION",
                    "smallest_witness": {
                        "left_case_id": prior[0],
                        "right_case_id": case_id,
                        "shared_envelope_sha256": result.sha256,
                        "distinguishing_future": "query either frozen literal expected observation",
                    },
                }
            )
        else:
            seen[envelope] = (case_id, fingerprint)
        unknowns.append(
            {
                "case_id": case_id,
                "status": "UNKNOWN",
                "reason": "canonical_records cannot be mapped independently to constituent observations",
                "needed_evidence": "a frozen inner stream/record/check schema and decoder identity",
            }
        )
        inspected.append(
            {"case_id": case_id, "envelope_sha256": result.sha256, "byte_length": result.byte_length}
        )

    return {
        "schema_id": "R01B-BLACKBOX-ENVELOPE-AUDIT-1",
        "verdict": "IMPLEMENTATION_FAILURE" if failures else "CONTRACT_DEFECT_UNDECIDABLE",
        "pass_awarded": False,
        "semantic_freeze_id": corpus.semantic_freeze_id,
        "inspected": inspected,
        "contract_defects": [asdict(item) for item in contract_findings(corpus)],
        "implementation_failures": failures,
        "unknowns": unknowns,
    }


def audit_carrier(value: Mapping[str, Any], corpus: FrozenCorpus | None = None) -> Mapping[str, Any]:
    """Read the minimal invocation carrier; it is explicitly not R0.1B evidence."""

    if set(value) != {"schema_id", "semantic_freeze_id", "envelopes"}:
        raise BreakerError("carrier has missing or extra keys")
    if value["schema_id"] != "R01B-BLACKBOX-CARRIER-1":
        raise BreakerError("unknown carrier schema")
    corpus = corpus or FrozenCorpus()
    if value["semantic_freeze_id"] != corpus.semantic_freeze_id:
        raise BreakerError("carrier semantic_freeze_id mismatch")
    rows = value["envelopes"]
    if not isinstance(rows, list):
        raise BreakerError("carrier envelopes is not a list")
    parsed: list[tuple[str, bytes]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"case_id", "envelope_hex"}:
            raise BreakerError(f"carrier row {index} has missing or extra keys")
        try:
            envelope = bytes.fromhex(row["envelope_hex"])
        except (TypeError, ValueError) as error:
            raise BreakerError(f"carrier row {index} has invalid hex") from error
        if row["envelope_hex"] != envelope.hex():
            raise BreakerError(f"carrier row {index} hex is not canonical lowercase")
        parsed.append((row["case_id"], envelope))
    return audit_envelopes(parsed, corpus)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    static = sub.add_parser("static", help="audit frozen contracts and corpus")
    static.add_argument(
        "--output",
        type=Path,
        help="retain canonical JSON at this path; this never changes the verdict",
    )
    carrier = sub.add_parser("carrier", help="audit exact envelopes in an invocation carrier")
    carrier.add_argument("path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        corpus = FrozenCorpus()
        if args.command == "static":
            report = static_report(corpus)
        else:
            report = audit_carrier(_read_canonical_json(args.path), corpus)
    except (BreakerError, OSError) as error:
        print(json.dumps({"verdict": "BREAKER_ERROR", "error": str(error)}, sort_keys=True))
        return 3
    output = getattr(args, "output", None)
    if output is not None:
        output.write_bytes(canonical_report_bytes(report))
    print(json.dumps(report, sort_keys=True, indent=2))
    if report["verdict"] == "IMPLEMENTATION_FAILURE":
        return 1
    if report["verdict"] == "CONTRACT_DEFECT_UNDECIDABLE":
        return 2
    return 3  # There intentionally is no PASS path in the frozen profile.


if __name__ == "__main__":
    sys.exit(main())
