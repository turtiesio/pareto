#!/usr/bin/env python3
"""Fail-closed R0.1B registry and literal-result runner core.

Gate S is closed, so this module can mechanically consume all 3,028 subject
descriptor templates and their literal B oracles.  It does not execute a
subject trial: the correction profile never freezes the byte format/digest
rule for gate R or the per-descriptor neutral-frame mechanism byte.  Inventing
either here would make a private R0.1B profile.

The useful executable subset is therefore deliberately split in two:

* this file validates/scales the frozen registry and independently checks raw
  publisher/recovery result bytes; and
* :mod:`r01b_subject` implements the byte-declared record, recovery,
  publication, fixture, and frame primitives.

``execute`` remains a hard error until a later frozen authority closes the two
missing byte rules.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Final

import r01b_subject as subject
import r01b_tv as tv


BASE: Final = Path(__file__).resolve().parent
S1_NAME: Final = "R01B-S1.json"
SEMANTIC_FREEZE_NAME: Final = "R01B-SEMANTIC-FREEZE.json"
S1_SHA256: Final = "fb72f6b36ca3eae284003ee1983e995afb13d3e8ec9d518f0c1afeaca67a9043"
SEMANTIC_FREEZE_ID: Final = (
    "r01b-semantic-954e2b16b258ceb8869795dbb823a0284a8369ca1cb20481168d7f652d89fcfd"
)
SUBJECT_ROW_COUNT: Final = 3028
TOTAL_ROW_COUNT: Final = 6318
TRIAL_TAG: Final = b"ZGR01B-TRIAL\x00"

PUBLICATION_KEYS: Final = frozenset(
    {
        "backend",
        "case_id",
        "continuation",
        "cut",
        "history_production",
        "injected_fault",
        "mechanism_manifest",
        "observer_profile",
        "repetition",
        "requested_payload",
        "setup",
    }
)
RECOVERY_KEYS: Final = frozenset(
    {
        "backend",
        "case_id",
        "continuation",
        "history_production",
        "mechanism_manifest",
        "observer_profile",
        "recovery_fixture",
        "repetition",
    }
)

MISSING_AUTHORITIES: Final = (
    {
        "status": "UNKNOWN",
        "reason": "gate R has no frozen canonical manifest bytes or digest/ID derivation",
        "needed_evidence": "a frozen canonical A_real manifest encoding and realization_id rule",
    },
    {
        "status": "UNKNOWN",
        "reason": "neutral-frame mm meanings are frozen but descriptor/slot assignments are not",
        "needed_evidence": "a frozen descriptor-slot-to-mm byte table, including SELF_CUT",
    },
    {
        "status": "UNKNOWN",
        "reason": "typed BH/B_input_key/B_response container shapes are not frozen",
        "needed_evidence": "closed TV container schemas for the three typed behavioral values",
    },
)


class RegistryValidationError(ValueError):
    """Gate-S material is internally inconsistent for this runner."""


class ExecutionAuthorityError(RuntimeError):
    """A real subject launch lacks a required frozen byte authority."""


@dataclass(frozen=True, slots=True)
class DescriptorRow:
    case_id: str
    trial_id: str
    ordinal: int
    history_production: str
    descriptor_tv: bytes
    descriptor: dict[str, object]
    expected_reachability: str
    comparison_edge_ids: tuple[str, ...]
    comparison_partner_case_ids: tuple[str, ...]

    @property
    def trial_digest(self) -> bytes:
        return bytes.fromhex(self.trial_id.removeprefix("r01b-"))


@dataclass(frozen=True, slots=True)
class LiteralBExpectation:
    history_production: str
    kind: str
    publish_results: tuple[bytes, ...]
    recovery_observation: bytes | None


@dataclass(frozen=True, slots=True)
class ObservedBResponse:
    """Raw B result values, not a claimed canonical ``B_response`` TV."""

    history_production: str
    publish_results: tuple[bytes, ...]
    recovery_observation: bytes | None
    has_b_history: bool = True


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require_exact_dict(value: object, label: str) -> dict[str, object]:
    if type(value) is not dict:
        raise RegistryValidationError(f"{label} must be an exact JSON object")
    return value


def _require_ascii_text(value: object, label: str) -> str:
    if type(value) is not str or not value:
        raise RegistryValidationError(f"{label} must be nonempty text")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise RegistryValidationError(f"{label} is not ASCII") from exc
    return value


class SemanticRegistry:
    """Validated access to the sole frozen S1 member."""

    def __init__(self, base: Path = BASE):
        self.base = Path(base)
        s1_bytes = (self.base / S1_NAME).read_bytes()
        if _sha256(s1_bytes) != S1_SHA256:
            raise RegistryValidationError("R01B-S1.json does not match gate S")
        try:
            root = json.loads(s1_bytes)
            freeze = json.loads((self.base / SEMANTIC_FREEZE_NAME).read_bytes())
        except (OSError, json.JSONDecodeError) as exc:
            raise RegistryValidationError("semantic closure cannot be loaded") from exc
        self.root = _require_exact_dict(root, "S1")
        self.freeze = _require_exact_dict(freeze, "semantic freeze")
        self._validate_closure()
        self.literal_rows = self._load_literal_rows()
        self.rows = self._load_descriptor_rows()
        self.subject_rows = tuple(
            row for row in self.rows if row.history_production != "LAB_ONLY"
        )
        self.subject_by_case_id = {row.case_id: row for row in self.subject_rows}
        self.subject_by_trial_id = {row.trial_id: row for row in self.subject_rows}
        self._validate_subject_rows()

    def _validate_closure(self) -> None:
        if set(self.root) != {
            "descriptor_registry",
            "fixture_and_mutation_registry",
            "literal_oracle_registry",
            "measurement_base_fixture",
            "schema_id",
            "semantic_suite_digest",
        }:
            raise RegistryValidationError("S1 top-level shape is not closed")
        if self.root["schema_id"] != "R01B-S1-1":
            raise RegistryValidationError("unexpected S1 schema ID")
        if self.root["semantic_suite_digest"] != subject.SEMANTIC_SUITE_DIGEST_HEX:
            raise RegistryValidationError("subject suite digest differs from S1")
        if self.freeze.get("semantic_freeze_id") != SEMANTIC_FREEZE_ID:
            raise RegistryValidationError("semantic freeze ID differs from gate S")
        freeze_s1 = self.freeze.get("s1")
        if type(freeze_s1) is not dict or freeze_s1.get("file_sha256") != S1_SHA256:
            raise RegistryValidationError("closure record does not bind the loaded S1")
        descriptor_registry = self.root["descriptor_registry"]
        if type(descriptor_registry) is not dict:
            raise RegistryValidationError("descriptor_registry is not a map")
        if descriptor_registry.get("row_count") != TOTAL_ROW_COUNT:
            raise RegistryValidationError("descriptor row count is not 6318")
        rows = descriptor_registry.get("rows")
        if type(rows) is not list or len(rows) != TOTAL_ROW_COUNT:
            raise RegistryValidationError("descriptor row list is not complete")

    def _load_literal_rows(self) -> dict[str, dict[str, object]]:
        registry = self.root["literal_oracle_registry"]
        if type(registry) is not dict or type(registry.get("rows")) is not list:
            raise RegistryValidationError("literal oracle rows are missing")
        result: dict[str, dict[str, object]] = {}
        for raw in registry["rows"]:
            raw = _require_exact_dict(raw, "literal row")
            if set(raw) != {"case_id", "expected"}:
                raise RegistryValidationError("literal row shape is not closed")
            case_id = _require_ascii_text(raw["case_id"], "literal case_id")
            if case_id in result:
                raise RegistryValidationError("literal oracle repeats a case ID")
            result[case_id] = _require_exact_dict(raw["expected"], "expected")
        if len(result) != TOTAL_ROW_COUNT:
            raise RegistryValidationError("literal oracle linkage is not bijective")
        return result

    def _load_descriptor_rows(self) -> tuple[DescriptorRow, ...]:
        result: list[DescriptorRow] = []
        prior_trial_id: bytes | None = None
        for expected_ordinal, raw in enumerate(self.root["descriptor_registry"]["rows"]):
            raw = _require_exact_dict(raw, "descriptor row")
            production = raw.get("history_production")
            required = {
                "case_id",
                "comparison_edge_ids",
                "comparison_partner_case_ids",
                "descriptor_template_tv_hex",
                "history_production",
                "ordinal",
                "trial_id",
            }
            if production != "LAB_ONLY":
                required.add("expected_reachability")
            if set(raw) != required:
                raise RegistryValidationError("descriptor row shape is not closed")
            if raw["ordinal"] != expected_ordinal:
                raise RegistryValidationError("descriptor ordinal is not sorted position")
            case_id = _require_ascii_text(raw["case_id"], "case_id")
            trial_id = _require_ascii_text(raw["trial_id"], "trial_id")
            try:
                descriptor_tv = bytes.fromhex(raw["descriptor_template_tv_hex"])
            except (TypeError, ValueError) as exc:
                raise RegistryValidationError("descriptor TV hex is malformed") from exc
            expected_trial_id = "r01b-" + _sha256(TRIAL_TAG + descriptor_tv)
            if trial_id != expected_trial_id:
                raise RegistryValidationError("trial ID does not derive from descriptor TV")
            if prior_trial_id is not None and trial_id.encode() <= prior_trial_id:
                raise RegistryValidationError("trial IDs are not unique unsigned-byte order")
            prior_trial_id = trial_id.encode()
            try:
                descriptor = tv.decode(descriptor_tv)
            except tv.TVError as exc:
                raise RegistryValidationError("descriptor TV does not decode") from exc
            if type(descriptor) is not dict or tv.encode(descriptor) != descriptor_tv:
                raise RegistryValidationError("descriptor TV is not a canonical map")
            if descriptor.get("case_id") != case_id:
                raise RegistryValidationError("descriptor case ID linkage differs")
            edge_ids = raw["comparison_edge_ids"]
            partner_ids = raw["comparison_partner_case_ids"]
            if type(edge_ids) is not list or type(partner_ids) is not list:
                raise RegistryValidationError("comparison linkage must use lists")
            result.append(
                DescriptorRow(
                    case_id=case_id,
                    trial_id=trial_id,
                    ordinal=expected_ordinal,
                    history_production=production,
                    descriptor_tv=descriptor_tv,
                    descriptor=descriptor,
                    expected_reachability=raw.get(
                        "expected_reachability", "NOT_APPLICABLE"
                    ),
                    comparison_edge_ids=tuple(edge_ids),
                    comparison_partner_case_ids=tuple(partner_ids),
                )
            )
        return tuple(result)

    def _validate_subject_rows(self) -> None:
        if len(self.subject_rows) != SUBJECT_ROW_COUNT:
            raise RegistryValidationError("subject row count is not 3028")
        if len(self.subject_by_case_id) != SUBJECT_ROW_COUNT:
            raise RegistryValidationError("subject case IDs are not unique")
        if len(self.subject_by_trial_id) != SUBJECT_ROW_COUNT:
            raise RegistryValidationError("subject trial IDs are not unique")
        counts = {"PUBLICATION": 0, "RECOVERY_ONLY": 0}
        for row in self.subject_rows:
            descriptor = row.descriptor
            production = row.history_production
            if descriptor.get("history_production") != production:
                raise RegistryValidationError("row/descriptor production differs")
            expected_keys = (
                PUBLICATION_KEYS if production == "PUBLICATION" else RECOVERY_KEYS
            )
            if set(descriptor) != expected_keys:
                raise RegistryValidationError("subject descriptor shape is not closed")
            counts[production] += 1
            if descriptor["backend"] not in ("E", "T"):
                raise RegistryValidationError("subject backend is not E/T")
            if descriptor["mechanism_manifest"] not in subject.MECHANISM_MANIFESTS:
                raise RegistryValidationError("subject mechanism is not implemented")
            if descriptor["observer_profile"] != "ACTIVE_PTRACE_V1":
                raise RegistryValidationError("unexpected observer profile")
            if descriptor["continuation"] != subject.C:
                raise RegistryValidationError("subject continuation is outside suite")
            if not isinstance(descriptor["repetition"], tv.U64):
                raise RegistryValidationError("repetition is not TV U64")
            if production == "PUBLICATION":
                if descriptor["setup"] not in {
                    "ABSENT_CLEAN",
                    "VALID_P0_CLEAN",
                    "ABSENT_TMP",
                    "VALID_P0_TMP",
                }:
                    raise RegistryValidationError("publication setup is not registered")
                if descriptor["cut"] not in (*subject.SLOT_NAMES, "NORMAL"):
                    raise RegistryValidationError("publication cut is not registered")
                if descriptor["requested_payload"] not in (subject.P0, subject.P1):
                    raise RegistryValidationError("publication payload is outside suite")
                if descriptor["injected_fault"] not in subject.INJECTED_FAULTS:
                    raise RegistryValidationError("publication fault is not registered")
            self.literal_b_expectation(row.case_id)
        if counts != {"PUBLICATION": 684, "RECOVERY_ONLY": 2344}:
            raise RegistryValidationError("subject production counts differ from S1")

    def literal_b_expectation(self, case_id: str) -> LiteralBExpectation:
        try:
            expected = self.literal_rows[case_id]
        except KeyError as exc:
            raise RegistryValidationError("case has no literal oracle row") from exc
        raw = expected.get("b_expectation")
        if type(raw) is not dict:
            raise RegistryValidationError("subject literal has no B expectation")
        try:
            descriptor_production = self.subject_by_case_id[case_id].history_production
        except KeyError as exc:
            raise RegistryValidationError("B expectation is not linked to a subject row") from exc
        production = raw.get("history_production")
        kind = raw.get("kind")
        if kind == "NO_B_HISTORY":
            if raw != {"kind": "NO_B_HISTORY", "reason": "CONTROL_UNAVAILABLE"}:
                raise RegistryValidationError("NO_B_HISTORY shape is not closed")
            return LiteralBExpectation(descriptor_production, kind, (), None)
        if production != descriptor_production:
            raise RegistryValidationError("literal/descriptor B production differs")
        if kind != "EXACT" or set(raw) != {
            "history_production",
            "kind",
            "publish_result_hex_list",
            "recovery_observation_hex",
        }:
            raise RegistryValidationError("EXACT B expectation shape is not closed")
        try:
            publish_results = tuple(
                bytes.fromhex(value) for value in raw["publish_result_hex_list"]
            )
            recovery = bytes.fromhex(raw["recovery_observation_hex"])
        except (TypeError, ValueError) as exc:
            raise RegistryValidationError("literal B bytes are malformed hex") from exc
        if production == "RECOVERY_ONLY" and publish_results:
            raise RegistryValidationError("recovery-only literal has a publish result")
        if len(publish_results) > 1:
            raise RegistryValidationError("literal has more than one publish result")
        for result in publish_results:
            try:
                subject.parse_publish_result(result)
            except subject.R01BSubjectError as exc:
                raise RegistryValidationError("literal publish result is malformed") from exc
        try:
            subject.parse_recovery_observation(recovery)
        except subject.R01BSubjectError as exc:
            raise RegistryValidationError("literal recovery observation is malformed") from exc
        return LiteralBExpectation(production, kind, publish_results, recovery)

    def row_by_ordinal(self, ordinal: int) -> DescriptorRow:
        if type(ordinal) is not int or not 0 <= ordinal < len(self.rows):
            raise KeyError("ordinal is outside the full registry")
        row = self.rows[ordinal]
        if row.history_production == "LAB_ONLY":
            raise KeyError("ordinal selects a LAB_ONLY row")
        return row

    def row_by_case_id(self, case_id: str) -> DescriptorRow:
        return self.subject_by_case_id[case_id]


def compare_literal_b(
    expected: LiteralBExpectation, observed: ObservedBResponse
) -> bool:
    """Compare raw result crossings without inventing a ``B_response`` TV."""

    if observed.history_production != expected.history_production:
        return False
    if expected.kind == "NO_B_HISTORY":
        return (
            not observed.has_b_history
            and not observed.publish_results
            and observed.recovery_observation is None
        )
    return (
        observed.has_b_history
        and observed.publish_results == expected.publish_results
        and observed.recovery_observation == expected.recovery_observation
    )


def recover_fixture_value(fixture: dict[str, object]) -> bytes:
    """Evaluate only the declared recovery relation on a crossed fixture value.

    This is a pure registry/oracle consistency check, not a fresh-process or
    filesystem conformance trial.  A symlink is nonregular and therefore
    rejects without reading its auxiliary target.
    """

    entry = fixture.get("authoritative_entry")
    if type(entry) is not dict or type(entry.get("kind")) is not str:
        raise RegistryValidationError("recovery fixture entry is malformed")
    kind = entry["kind"]
    if kind == "ABSENT":
        return subject.ABSENT
    if kind == "REGULAR":
        value = entry.get("regular_bytes")
        if type(value) is not bytes:
            raise RegistryValidationError("regular fixture lacks exact bytes")
        return subject.recover_record_bytes(value)
    if kind == "SYMLINK":
        return subject.REJECT
    raise RegistryValidationError("recovery fixture kind is not closed")


def validate_recovery_literals(registry: SemanticRegistry) -> int:
    """Check all 2,344 recovery fixture values against independent raw wires."""

    count = 0
    for row in registry.subject_rows:
        if row.history_production != "RECOVERY_ONLY":
            continue
        expected = registry.literal_b_expectation(row.case_id)
        actual = recover_fixture_value(row.descriptor["recovery_fixture"])
        observed = ObservedBResponse("RECOVERY_ONLY", (), actual)
        if not compare_literal_b(expected, observed):
            raise RegistryValidationError(
                f"recovery fixture/literal mismatch at {row.case_id}"
            )
        count += 1
    if count != 2344:
        raise RegistryValidationError("recovery literal check did not cover 2344 rows")
    return count


def require_execution_authority() -> None:
    """Fail before any setup, publisher, recovery process, or B crossing."""

    raise ExecutionAuthorityError(
        "R0.1B execution is NOT_RUN: gate-R bytes/ID and checkpoint mm assignments "
        "are not frozen by REALIZATION-CORRECTION-R01B.md"
    )


def preflight_report(registry: SemanticRegistry) -> dict[str, object]:
    return {
        "claim_scope": "STATIC_GATE_S_AND_LITERAL_PREFLIGHT_ONLY",
        "execution": "NOT_RUN",
        "full_conformance": "UNKNOWN",
        "limitations": list(MISSING_AUTHORITIES),
        "semantic_freeze_id": SEMANTIC_FREEZE_ID,
        "semantic_suite_digest": subject.SEMANTIC_SUITE_DIGEST_HEX,
        "subject_row_count": len(registry.subject_rows),
        "subject_rows_by_production": {
            "PUBLICATION": sum(
                row.history_production == "PUBLICATION"
                for row in registry.subject_rows
            ),
            "RECOVERY_ONLY": sum(
                row.history_production == "RECOVERY_ONLY"
                for row in registry.subject_rows
            ),
        },
    }


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("preflight", "validate-recovery-literals", "execute")
    )
    parser.add_argument("--base", type=Path, default=BASE)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    registry = SemanticRegistry(args.base)
    if args.command == "preflight":
        print(_canonical_json(preflight_report(registry)))
        return 0
    if args.command == "validate-recovery-literals":
        print(
            _canonical_json(
                {
                    "checked_recovery_rows": validate_recovery_literals(registry),
                    "claim_scope": "PURE_FIXTURE_VALUE_RELATION",
                    "execution": "NOT_RUN",
                }
            )
        )
        return 0
    try:
        require_execution_authority()
    except ExecutionAuthorityError as exc:
        print(_canonical_json({"execution": "NOT_RUN", "error": str(exc)}))
        return 2
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
