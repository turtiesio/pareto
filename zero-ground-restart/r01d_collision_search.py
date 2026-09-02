#!/usr/bin/env python3
"""Bounded, nonauthorizing history-quotient falsification for R0.1D.

This is deliberately not a subject, LAB role, semantic decoder, gate,
provider, store, parser, or replay implementation.  It treats the corpus's
future answers as the bounded external contract and asks only whether candidate
encodings collapse histories that those futures distinguish.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable


RESPONSIBILITY_CANDIDATE = "R01D_RESPONSIBILITIES"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def project_value(value: Any, fields: list[str] | None) -> Any:
    if fields is None:
        return value
    if not isinstance(value, dict):
        raise ValueError("value_fields requires a map event value")
    if any(field not in value for field in fields):
        raise ValueError(f"projection field absent: {fields!r} from {value!r}")
    return {field: value[field] for field in fields}


def extract(history: dict[str, Any], spec: dict[str, Any]) -> Any:
    mode = spec["mode"]
    extractor_id = spec["id"]
    if mode == "events":
        kinds = set(spec["kinds"])
        fields = spec.get("value_fields")
        return [
            {
                "kind": event["kind"],
                "value": project_value(event["value"], fields),
            }
            for event in history["events"]
            if event["kind"] in kinds
        ]
    if mode == "declared_derived":
        return history.get("derived", {}).get(extractor_id)
    if mode == "research_internal":
        return history.get("internal", {}).get(extractor_id)
    raise ValueError(f"unknown extractor mode {mode!r}")


def encode(
    history: dict[str, Any],
    extractor_ids: Iterable[str],
    extractor_by_id: dict[str, dict[str, Any]],
) -> str:
    return canonical(
        {
            extractor_id: extract(history, extractor_by_id[extractor_id])
            for extractor_id in extractor_ids
        }
    )


def families(histories: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for history in histories:
        result.setdefault(history["family"], []).append(history)
    return result


def event_distance(left: dict[str, Any], right: dict[str, Any]) -> tuple[int, int, str, str]:
    left_events = [canonical(event) for event in left["events"]]
    right_events = [canonical(event) for event in right["events"]]
    shared = list(left_events)
    for event in right_events:
        if event in shared:
            shared.remove(event)
    symmetric_count = len(left_events) + len(right_events) - 2 * (
        len(left_events) - len(shared)
    )
    byte_cost = len(canonical(left["events"])) + len(canonical(right["events"]))
    return symmetric_count, byte_cost, left["id"], right["id"]


def collisions(
    histories: list[dict[str, Any]],
    extractor_ids: list[str],
    extractor_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for family, group in sorted(families(histories).items()):
        for left, right in itertools.combinations(group, 2):
            if canonical(left["answer"]) == canonical(right["answer"]):
                continue
            left_encoding = encode(left, extractor_ids, extractor_by_id)
            right_encoding = encode(right, extractor_ids, extractor_by_id)
            if left_encoding != right_encoding:
                continue
            found.append(
                {
                    "family": family,
                    "history_left": left["id"],
                    "history_right": right["id"],
                    "future_left": left["answer"],
                    "future_right": right["answer"],
                    "event_distance": event_distance(left, right)[0],
                    "event_byte_cost": event_distance(left, right)[1],
                }
            )
    return sorted(
        found,
        key=lambda item: (
            item["event_distance"],
            item["event_byte_cost"],
            item["family"],
            item["history_left"],
            item["history_right"],
        ),
    )


def is_sound(
    histories: list[dict[str, Any]],
    extractor_ids: list[str],
    extractor_by_id: dict[str, dict[str, Any]],
) -> bool:
    return not collisions(histories, extractor_ids, extractor_by_id)


def deletion_fixed_point(
    histories: list[dict[str, Any]],
    initial: list[str],
    extractor_by_id: dict[str, dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]]]:
    retained = list(initial)
    mode_priority = {"research_internal": 0, "declared_derived": 1, "events": 2}
    order = sorted(
        initial,
        key=lambda item: (mode_priority[extractor_by_id[item]["mode"]], item),
    )
    trace: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        for extractor_id in order:
            if extractor_id not in retained:
                continue
            candidate = [item for item in retained if item != extractor_id]
            witness = collisions(histories, candidate, extractor_by_id)
            if witness:
                trace.append(
                    {
                        "extractor": extractor_id,
                        "verdict": "RETAIN",
                        "minimal_collision": witness[0],
                    }
                )
            else:
                retained = candidate
                trace.append({"extractor": extractor_id, "verdict": "DELETE"})
                changed = True
    return retained, trace


def functionally_determined(
    histories: list[dict[str, Any]],
    bases: list[str],
    extra: str,
    extractor_by_id: dict[str, dict[str, Any]],
) -> bool:
    for group in families(histories).values():
        seen: dict[str, str] = {}
        for history in group:
            base_encoding = encode(history, bases, extractor_by_id)
            extra_encoding = canonical(extract(history, extractor_by_id[extra]))
            previous = seen.setdefault(base_encoding, extra_encoding)
            if previous != extra_encoding:
                return False
    return True


def merge_collision(
    corpus: dict[str, Any],
    attack: dict[str, Any],
    responsibilities: list[str],
    extractor_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    group = [
        history
        for history in corpus["histories"]
        if history["family"] == attack["family"]
    ]
    unmerged = [
        item for item in responsibilities if item not in set(attack["extractors"])
    ]
    encodings: dict[str, str] = {}
    for history in group:
        token = history.get("merge_tokens", {}).get(attack["id"])
        if token is None:
            raise ValueError(f"missing merge token for {attack['id']} / {history['id']}")
        encodings[history["id"]] = canonical(
            {
                "unmerged": json.loads(encode(history, unmerged, extractor_by_id)),
                "untagged_merged_value": token,
            }
        )
    found: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for left, right in itertools.combinations(group, 2):
        if canonical(left["answer"]) == canonical(right["answer"]):
            continue
        if encodings[left["id"]] == encodings[right["id"]]:
            found.append((left, right))
    if not found:
        return None
    left, right = min(found, key=lambda pair: event_distance(*pair))
    return {
        "family": attack["family"],
        "history_left": left["id"],
        "history_right": right["id"],
        "future_left": left["answer"],
        "future_right": right["answer"],
        "event_distance": event_distance(left, right)[0],
        "event_byte_cost": event_distance(left, right)[1],
    }


def validate(corpus: dict[str, Any]) -> None:
    if corpus.get("schema_id") != "ZERO-GROUND-R01D-HISTORY-CORPUS-1":
        raise ValueError("wrong corpus schema")
    extractors = corpus["extractors"]
    extractor_ids = [item["id"] for item in extractors]
    if len(extractor_ids) != len(set(extractor_ids)):
        raise ValueError("duplicate extractor ID")
    extractor_set = set(extractor_ids)
    history_ids = [item["id"] for item in corpus["histories"]]
    if len(history_ids) != len(set(history_ids)):
        raise ValueError("duplicate history ID")
    candidates = corpus["candidate_representations"]
    candidate_ids = [item["id"] for item in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("duplicate candidate ID")
    for candidate in candidates:
        unknown = set(candidate["extractors"]) - extractor_set
        if unknown:
            raise ValueError(f"unknown candidate extractors: {sorted(unknown)}")
        if len(candidate["extractors"]) != len(set(candidate["extractors"])):
            raise ValueError(f"duplicate extractor in {candidate['id']}")
    if RESPONSIBILITY_CANDIDATE not in candidate_ids:
        raise ValueError("missing responsibility candidate")
    for history in corpus["histories"]:
        if "family" not in history or "answer" not in history or "events" not in history:
            raise ValueError(f"incomplete history {history.get('id')}")
        for event in history["events"]:
            if set(event) != {"kind", "value"}:
                raise ValueError(f"open event shape in {history['id']}")
    for family, group in families(corpus["histories"]).items():
        if len(group) < 2:
            raise ValueError(f"family lacks a pair: {family}")
    if set(corpus.get("future_contract", {})) != set(families(corpus["histories"])):
        raise ValueError("future_contract must name every and only history family")


def build_report(corpus: dict[str, Any], corpus_bytes: bytes, contract: Path) -> dict[str, Any]:
    validate(corpus)
    extractor_by_id = {item["id"]: item for item in corpus["extractors"]}
    candidate_by_id = {
        item["id"]: item for item in corpus["candidate_representations"]
    }
    responsibilities = candidate_by_id[RESPONSIBILITY_CANDIDATE]["extractors"]
    extras = [item for item in extractor_by_id if item not in set(responsibilities)]

    candidate_results = []
    for candidate in corpus["candidate_representations"]:
        found = collisions(corpus["histories"], candidate["extractors"], extractor_by_id)
        candidate_results.append(
            {
                "candidate": candidate["id"],
                "extractor_count": len(candidate["extractors"]),
                "sound_in_searched_domain": not found,
                "collision_count": len(found),
                "minimal_collision": found[0] if found else None,
            }
        )

    deletion_witnesses: dict[str, Any] = {}
    for extractor_id in responsibilities:
        candidate = [item for item in responsibilities if item != extractor_id]
        found = collisions(corpus["histories"], candidate, extractor_by_id)
        deletion_witnesses[extractor_id] = found[0] if found else None

    may_rebuild: list[str] = []
    may_forget: list[str] = []
    for extractor_id in extras:
        if functionally_determined(
            corpus["histories"], responsibilities, extractor_id, extractor_by_id
        ):
            may_rebuild.append(extractor_id)
        else:
            may_forget.append(extractor_id)

    overcomplete = candidate_by_id["OVERCOMPLETE"]["extractors"]
    fixed_point, deletion_trace = deletion_fixed_point(
        corpus["histories"], overcomplete, extractor_by_id
    )

    merge_results = []
    for attack in corpus["merge_attacks"]:
        witness = merge_collision(corpus, attack, responsibilities, extractor_by_id)
        merge_results.append(
            {
                "attack": attack["id"],
                "collapsed_distinction": witness is not None,
                "minimal_collision": witness,
            }
        )

    quotient = []
    for family, group in sorted(families(corpus["histories"]).items()):
        quotient.append(
            {
                "family": family,
                "history_count": len(group),
                "future_equivalence_class_count": len(
                    {canonical(history["answer"]) for history in group}
                ),
            }
        )

    report = {
        "schema_id": "ZERO-GROUND-R01D-COLLISION-REPORT-1",
        "claim": corpus["scope"]["claim"],
        "inputs": {
            "contract_path": str(contract),
            "contract_sha256": hashlib.sha256(contract.read_bytes()).hexdigest(),
            "corpus_sha256": hashlib.sha256(corpus_bytes).hexdigest(),
        },
        "search_bound": {
            "family_count": len(families(corpus["histories"])),
            "history_count": len(corpus["histories"]),
            "future_count": len(corpus["future_contract"]),
            "extractor_count": len(corpus["extractors"]),
            "candidate_count": len(corpus["candidate_representations"]),
            "merge_attack_count": len(corpus["merge_attacks"]),
        },
        "future_quotient": quotient,
        "candidate_results": candidate_results,
        "classification": {
            "must_survive_in_searched_domain": sorted(responsibilities),
            "may_rebuild_in_searched_domain": sorted(may_rebuild),
            "may_forget_in_searched_domain": sorted(may_forget),
        },
        "delete_attacks": deletion_witnesses,
        "merge_attacks": merge_results,
        "overcomplete_deletion_search": {
            "initial_count": len(overcomplete),
            "fixed_point_count": len(fixed_point),
            "fixed_point_extractors": fixed_point,
            "trace": deletion_trace,
        },
        "research_tcb": [
            "corpus family conditioning",
            "declared future answers",
            "extractor implementations",
            "canonical JSON equality",
            "pair enumeration",
            "greedy deletion order",
            "event-distance witness ordering",
        ],
        "unknown": [
            "unlisted histories and futures",
            "cross-family continuations",
            "semantic adequacy of declared futures",
            "physical persistence and fault independence",
            "human cognition and authoring performance",
            "global minimality and uniqueness of the fixed point",
        ],
    }

    responsibility_result = next(
        item for item in candidate_results if item["candidate"] == RESPONSIBILITY_CANDIDATE
    )
    if not responsibility_result["sound_in_searched_domain"]:
        raise AssertionError("R01D responsibility candidate collided")
    missing = [key for key, witness in deletion_witnesses.items() if witness is None]
    if missing:
        raise AssertionError(f"claimed responsibility lacks deletion witness: {missing}")
    if set(fixed_point) != set(responsibilities):
        raise AssertionError(
            "preferred overcomplete deletion path did not reach R01D responsibilities: "
            f"{fixed_point!r}"
        )
    if not all(item["collapsed_distinction"] for item in merge_results):
        raise AssertionError("an untagged merge attack lacked a collision")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path(__file__).with_name("R01D-HISTORY-CORPUS.json"),
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path(__file__).with_name("REALIZATION-CORRECTION-R01D.md"),
    )
    args = parser.parse_args()
    corpus_bytes = args.corpus.read_bytes()
    corpus = json.loads(corpus_bytes)
    report = build_report(corpus, corpus_bytes, args.contract)
    print(json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
