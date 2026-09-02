#!/usr/bin/env python3
"""Deterministic, fail-closed falsifier for the frozen R0.1K text.

This is a static boundary-history experiment.  It does not implement R0.1K,
prove an architecture, or promote absent execution/physical evidence to PASS.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent
INPUTS = (
    (
        "HISTORY-SEED-R01K.md",
        "2ae3ac8fda2a78a0b1cd4eef45a8a9d412dc6617b3fff098f4f348855c8eb678",
    ),
    (
        "POSTFREEZE-BREAK-R01K.md",
        "9c78c4830db263e5e200923fc51a36edbd1f7f37b70f90d420aae1e0e3ac983b",
    ),
)
VERDICTS = ("FAIL", "PASS", "UNKNOWN")


def emit(document: dict[str, Any]) -> None:
    """Emit one canonical JSON line."""
    sys.stdout.write(
        json.dumps(document, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n"
    )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def result(
    check_id: str,
    name: str,
    verdict: str,
    scope: str,
    claim: str,
    details: dict[str, Any],
    witness: dict[str, Any],
) -> dict[str, Any]:
    if verdict not in VERDICTS:
        raise ValueError("invalid verdict")
    if scope not in ("direct", "static"):
        raise ValueError("invalid scope")
    return {
        "claim": claim,
        "details": details,
        "id": check_id,
        "name": name,
        "scope": scope,
        "verdict": verdict,
        "witness": witness,
    }


def section(text: str, start: str, end: str | None = None) -> str:
    start_at = text.index(start)
    if end is None:
        return text[start_at:]
    end_at = text.index(end, start_at + len(start))
    return text[start_at:end_at]


def code_spans(value: str) -> list[str]:
    return re.findall(r"`([^`]+)`", value, flags=re.DOTALL)


def abbreviation_tokens(value: str) -> list[str]:
    tokens: list[str] = []
    for span in code_spans(value):
        tokens.extend(part.strip() for part in span.split(",") if part.strip())
    return tokens


def table_at(text: str, first_header: str) -> tuple[list[str], list[list[str]]]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == first_header:
            headers = cells
            rows: list[list[str]] = []
            for row_line in lines[index + 2 :]:
                if not row_line.startswith("|"):
                    break
                row = [cell.strip() for cell in row_line.strip().strip("|").split("|")]
                rows.append(row)
            return headers, rows
    raise ValueError("table not found: " + first_header)


def clean_code(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value


def encoded_item(value: bytes) -> bytes:
    return struct.pack(">I", len(value)) + value


def quantifier(values: list[str], universal: bool) -> str:
    if not values:
        return "VACUOUS" if universal else "FALSE"
    if universal:
        if "-" in values:
            return "FALSE"
        if all(value == "+" for value in values):
            return "TRUE"
        return "UNKNOWN"
    if "+" in values:
        return "TRUE"
    if all(value == "-" for value in values):
        return "FALSE"
    return "UNKNOWN"


def first_match_phase(history: list[str]) -> str:
    def word(item: str) -> str:
        return item.split(":", 1)[0]

    has_term_done = any(item == "TERM-DONE" for item in history)
    if has_term_done:
        return "terminal"
    has_term_applied = any(item == "TERM-APPLIED" for item in history)
    if has_term_applied:
        return "term-applied"
    has_term_request = any(word(item) == "TERMINATE" for item in history)
    if has_term_request:
        return "term-requested"
    crash_indexes = [index for index, item in enumerate(history) if word(item) == "CRASH"]
    recovered_indexes = [
        index for index, item in enumerate(history) if word(item) == "RECOVERED"
    ]
    if crash_indexes and (not recovered_indexes or recovered_indexes[-1] < crash_indexes[-1]):
        recover_requests = [
            index for index, item in enumerate(history) if word(item) == "RECOVER"
        ]
        if recover_requests and recover_requests[-1] > crash_indexes[-1]:
            return "recovery-pending"
        return "crashed"
    evolve_requests = [
        index for index, item in enumerate(history) if word(item) == "EVOLVE"
    ]
    evolved = [index for index, item in enumerate(history) if word(item) == "EVOLVED"]
    if evolve_requests and (not evolved or evolved[-1] < evolve_requests[-1]):
        return "evolution-pending"
    attempt_indexes = [
        index for index, item in enumerate(history) if word(item) == "ATTEMPT"
    ]
    if attempt_indexes:
        last_attempt = attempt_indexes[-1]
        suffix = history[last_attempt + 1 :]
        if any(item.startswith("APPLIED") for item in suffix) and not any(
            item.startswith(("EXPIRE:completion", "COMPLETE:completion"))
            for item in suffix
        ):
            return "action-applied"
        if any(item.startswith("OCCURRED") for item in suffix) and not any(
            item.startswith(("APPLIED", "DENIED-BEFORE-OCCURRENCE", "APPLICATION-UNRESOLVED"))
            for item in suffix
        ):
            return "action-occurred"
        if not any(
            item.startswith(("OCCURRED", "DENIED-BEFORE-OCCURRENCE"))
            for item in suffix
        ):
            return "action-requested"
    observe_indexes = [index for index, item in enumerate(history) if item == "OBSERVE"]
    if observe_indexes:
        suffix = history[observe_indexes[-1] + 1 :]
        if not any(item.startswith(("COMPLETE", "EXPIRE", "UNAVAILABLE")) for item in suffix):
            return "observation-open"
    synchronous = ("INTERPRET", "AUTHOR", "QUERY", "CAPTURE", "EXPLAIN")
    if history and history[-1].split(":", 1)[0] in synchronous:
        return "synchronous-pending"
    return "open"


def parse_frozen(candidate: str) -> dict[str, Any]:
    observation_section = section(
        candidate,
        "### 6.2 Common observation/interpretation/authoring prefix",
        "### 6.3 Query over all five carrier histories",
    )
    _, observation_rows = table_at(observation_section, "leaf")
    prefixes: dict[str, list[str]] = {}
    for row in observation_rows:
        leaf = clean_code(row[0])
        prefixes[leaf] = (
            abbreviation_tokens(row[1])
            + abbreviation_tokens(row[2])
            + abbreviation_tokens(row[3])
        )

    suffix_section = section(
        candidate,
        "### 6.4 Action, capture, evolution, and recovery suffixes",
        "### 6.5 Termination and retained post-terminal evidence",
    )
    _, suffix_rows = table_at(suffix_section, "leaf")
    suffixes = {
        clean_code(row[0]): abbreviation_tokens(row[1]) for row in suffix_rows
    }

    terminal_section = section(
        candidate,
        "### 6.5 Termination and retained post-terminal evidence",
        "### 6.6 The exact finite leaf set and dimension coverage",
    )
    tail_match = re.search(
        r"Every branch ends with the exact tail:\s*`([^`]+)`",
        terminal_section,
        flags=re.DOTALL,
    )
    if tail_match is None:
        raise ValueError("terminal tail not found")
    terminal_tail = [part.strip() for part in tail_match.group(1).split(",")]

    count_match = re.search(
        r"the exact occurrence\s+counts are (.*?)\.", candidate, flags=re.DOTALL
    )
    if count_match is None:
        raise ValueError("declared counts not found")
    declared_counts = {
        leaf: int(count)
        for leaf, count in re.findall(r"`(a|b|ab|n|u)=(\d+)`", count_match.group(1))
    }

    outcomes_match = re.search(
        r"declared carrier outcomes are `a:([+\-?])`, `b:([+\-?])`, "
        r"`ab:([+\-?])`, `n:([+\-?])`, and `u:([+\-?])`",
        candidate,
    )
    if outcomes_match is None:
        raise ValueError("carrier outcomes not found")
    outcomes = dict(zip(("a", "b", "ab", "n", "u"), outcomes_match.groups()))

    ledger_section = section(
        candidate, "### 8.2 Exhaustive families in K/1", "### 8.3 Completeness check"
    )
    _, family_rows = table_at(ledger_section, "family")
    action_row = next(row for row in family_rows if clean_code(row[0]) == "action")
    action_set = code_spans(action_row[1])[0].strip("{}")
    action_labels = [item.strip() for item in action_set.split(",")]

    matrix_section = section(
        candidate,
        "### 7.2 Coverage matrix",
        "### 7.3 Finite decoder and depth breakers",
    )
    matrix_headers, matrix_rows = table_at(matrix_section, "history predicate")
    matrix = {
        clean_code(row[0]): {
            matrix_headers[index]: clean_code(row[index])
            for index in range(1, len(matrix_headers))
        }
        for row in matrix_rows
    }

    vocabulary_match = re.search(
        r"The request vocabulary is:\s*`([^`]+)`", candidate, flags=re.DOTALL
    )
    if vocabulary_match is None:
        raise ValueError("request vocabulary not found")
    request_vocabulary = [
        item.strip()
        for item in vocabulary_match.group(1).replace("\n", " ").split(",")
    ]

    notation = section(candidate, "### 6.1 Occurrence notation", "### 6.2 Common")
    ans_match = re.search(
        r"words\s+(`INTERPRETED`.*?`TERMINAL-REFUSAL`) expand to `ANS`",
        notation,
        flags=re.DOTALL,
    )
    cut_match = re.search(
        r"(`OCCURRED`.*?`TERM-DONE`) expand to `CUT`", notation, flags=re.DOTALL
    )
    if ans_match is None or cut_match is None:
        raise ValueError("direction assignments not found")
    ans_words = code_spans(ans_match.group(1))
    ans_words.extend(("CHUNK", "COMPLETE", "EXPIRE", "UNAVAILABLE"))
    cut_words = code_spans(cut_match.group(1))

    depth_match = re.search(r'depth\.full="(\d+)"', candidate)
    positive_match = re.search(
        r"first\s+positive depths are: `a=(\d+)`, `b=(\d+)`, and `ab=(\d+)`",
        candidate,
    )
    if depth_match is None or positive_match is None:
        raise ValueError("depth declarations not found")

    return {
        "action_labels": action_labels,
        "ans_words": sorted(set(ans_words)),
        "cut_words": sorted(set(cut_words)),
        "declared_counts": declared_counts,
        "depth_full": int(depth_match.group(1)),
        "matrix": matrix,
        "matrix_headers": matrix_headers[1:],
        "outcomes": outcomes,
        "positive_depths": dict(
            zip(("a", "b", "ab"), map(int, positive_match.groups()))
        ),
        "prefixes": prefixes,
        "request_vocabulary": request_vocabulary,
        "suffixes": suffixes,
        "terminal_tail": terminal_tail,
    }


def run_checks(candidate: str, _report: str) -> list[dict[str, Any]]:
    parsed = parse_frozen(candidate)
    checks: list[dict[str, Any]] = []

    common_occurrences = 1 + 4  # DECL plus two QUERY request/answer pairs.
    explanation_occurrences = 4
    terminal_occurrences = len(parsed["terminal_tail"])
    actual_counts = {
        leaf: common_occurrences
        + len(parsed["prefixes"][leaf])
        + len(parsed["suffixes"][leaf])
        + explanation_occurrences
        + terminal_occurrences
        for leaf in sorted(parsed["declared_counts"])
    }
    count_pass = actual_counts == parsed["declared_counts"]
    checks.append(
        result(
            "P01",
            "written_leaf_abbreviation_counts",
            "PASS" if count_pass else "FAIL",
            "direct",
            "The five written token scripts count 38/38/39/36/38.",
            {
                "actual": actual_counts,
                "declared": parsed["declared_counts"],
                "promoted_to_exact_byte_histories": False,
            },
            {
                "components": {
                    "common_decl_and_queries": common_occurrences,
                    "explanations": explanation_occurrences,
                    "terminal_tail": terminal_occurrences,
                }
            },
        )
    )

    carrier_order = ("a", "b", "ab", "n", "u")
    values = [parsed["outcomes"][leaf] for leaf in carrier_order]
    without_n = [
        parsed["outcomes"][leaf] for leaf in carrier_order if leaf != "n"
    ]
    quantifier_answers = {
        "full": {"MAY": quantifier(values, False), "MUST": quantifier(values, True)},
        "without_n": {
            "MAY": quantifier(without_n, False),
            "MUST": quantifier(without_n, True),
        },
    }
    quantifier_pass = quantifier_answers == {
        "full": {"MAY": "TRUE", "MUST": "FALSE"},
        "without_n": {"MAY": "TRUE", "MUST": "UNKNOWN"},
    }
    checks.append(
        result(
            "P02",
            "five_carrier_quantifiers",
            "PASS" if quantifier_pass else "FAIL",
            "direct",
            "MAY/MUST arithmetic is correct for {+,+,+,-,?} and after deleting n.",
            {"answers": quantifier_answers, "carrier_values": dict(zip(carrier_order, values))},
            {"deleted_carrier": "n", "remaining_values": without_n},
        )
    )

    action_count = len(parsed["action_labels"])
    pair_count = action_count * (action_count - 1) // 2
    added_pairs = action_count
    pair_pass = pair_count == 28 and added_pairs == 8
    checks.append(
        result(
            "P03",
            "action_pair_arithmetic",
            "PASS" if pair_pass else "FAIL",
            "direct",
            "Eight action labels yield 28 unordered pairs; completed adds eight.",
            {
                "action_label_count": action_count,
                "added_pairs_for_completed": added_pairs,
                "unordered_pairs": pair_count,
            },
            {"labels": parsed["action_labels"]},
        )
    )

    empty_cells = sorted(
        f"{row}/{column}"
        for row, cells in parsed["matrix"].items()
        for column, value in cells.items()
        if not value
    )
    matrix_dimensions = [len(parsed["matrix"]), len(parsed["matrix_headers"])]
    matrix_pass = (
        matrix_dimensions == [12, 10]
        and not empty_cells
        and parsed["matrix_headers"] == parsed["request_vocabulary"]
    )
    checks.append(
        result(
            "P04",
            "router_matrix_occupancy",
            "PASS" if matrix_pass else "FAIL",
            "direct",
            "The displayed router matrix has 12 populated rows and 10 vocabulary columns.",
            {
                "dimensions": matrix_dimensions,
                "empty_cells": empty_cells,
                "headers_match_vocabulary": parsed["matrix_headers"]
                == parsed["request_vocabulary"],
                "reachable_prefix_totality_proved": False,
            },
            {"operations": parsed["matrix_headers"], "predicates": sorted(parsed["matrix"])},
        )
    )

    marker = encoded_item(b"UNBOUND")
    bound_raw = encoded_item(b"UNBOUND")
    collision = marker == bound_raw and "literal marker `UNBOUND`" in candidate
    checks.append(
        result(
            "F01",
            "unbound_sentinel_collision",
            "FAIL" if collision else "UNKNOWN",
            "direct",
            "The UNBOUND marker must be disjoint from bound opaque content.",
            {
                "bound_raw_hex": bound_raw.hex(),
                "encoded_bytes_equal": collision,
                "marker_hex": marker.hex(),
            },
            {
                "dependency_key": "k",
                "left_semantics": "unbound marker",
                "right_semantics": "bound opaque ASCII UNBOUND",
            },
        )
    )

    q_may = "REQ|audit|s0|QUERY|MAY:q:depth=6"
    a_may = "ANS|audit|s0|QUERY|TRUE|witness=a"
    q_must = "REQ|audit|s0|QUERY|MUST:q:depth=6"
    a_must = "ANS|audit|s0|QUERY|FALSE|counterexample=n"
    may_root = ["DECL:K/1"]
    must_root = may_root + [q_may, a_may]
    shifted_depths = {
        leaf: depth + 1 for leaf, depth in parsed["positive_depths"].items()
    }
    common_root_claim = "from that one exact\nroot history" in candidate
    root_collision = may_root != must_root and common_root_claim
    checks.append(
        result(
            "F02",
            "sequential_query_common_root",
            "FAIL" if root_collision else "UNKNOWN",
            "direct",
            "Sequential MAY and MUST occurrences cannot both be rooted at DECL alone.",
            {
                "asserted_positive_depths": parsed["positive_depths"],
                "may_first_written_depths": shifted_depths,
                "roots_equal": may_root == must_root,
            },
            {
                "may_root": may_root,
                "must_root": must_root,
                "pd": {
                    "common_prefix": may_root,
                    "may_suffix": [],
                    "must_suffix": [q_may, a_may],
                },
                "written_following_query": [q_must, a_must],
            },
        )
    )

    depth_seven_claimed_true = "true at depths six and seven" in candidate
    depth_conflict = parsed["depth_full"] == 6 and depth_seven_claimed_true
    checks.append(
        result(
            "F03",
            "depth_six_envelope_vs_depth_seven",
            "FAIL" if depth_conflict else "UNKNOWN",
            "static",
            "A depth-seven query cannot be both outside depth.full=6 and TRUE.",
            {
                "declared_depth_full": parsed["depth_full"],
                "depth_seven_claimed_true": depth_seven_claimed_true,
                "required_results": ["OUT-OF-ENVELOPE", "TRUE"],
            },
            {"request": "REQ|audit|s0|QUERY|MAY:q:depth=7"},
        )
    )

    observe_request = "REQ|audit|s0|OBSERVE|-"
    answer_a = "ANS|audit|s0|OBSERVE|CHUNK|a"
    answer_b = "ANS|audit|s0|OBSERVE|CHUNK|b"
    unique_n = "`N(h,r)` is the unique result" in candidate
    observation_collision = unique_n and answer_a != answer_b
    checks.append(
        result(
            "F04",
            "unique_n_observation_collision",
            "FAIL" if observation_collision else "UNKNOWN",
            "direct",
            "The same pre-OBSERVE history/request has two admitted first answer bytes despite unique N.",
            {"answers_equal": answer_a == answer_b, "unique_n_claimed": unique_n},
            {
                "answers": [answer_a, answer_b],
                "history": ["DECL:K/1", q_may, a_may, q_must, a_must],
                "request": observe_request,
            },
        )
    )

    nonrequest_match = re.search(
        r"Non-request answer, cut, and evidence words are:\s*`([^`]+)`",
        candidate,
        flags=re.DOTALL,
    )
    nonrequest_words = []
    if nonrequest_match:
        nonrequest_words = [
            item.strip()
            for item in nonrequest_match.group(1).replace("\n", " ").split(",")
        ]
    assigned = set(parsed["ans_words"]) | set(parsed["cut_words"])
    directionless = sorted(word for word in nonrequest_words if word not in assigned)
    explicitly_authorized_cuts = {"DECL", "EXPIRE:completion-observer"}
    missing_cut_authorities = sorted(
        word for word in parsed["cut_words"] if word not in explicitly_authorized_cuts
    )
    direction_failure = (
        "APPLICATION-UNRESOLVED" in directionless and bool(missing_cut_authorities)
    )
    checks.append(
        result(
            "F05",
            "direction_expansion_and_cut_authority",
            "FAIL" if direction_failure else "UNKNOWN",
            "static",
            "Every abbreviation must select one direction and every CUT must bind its authority.",
            {
                "assigned_ans_words": parsed["ans_words"],
                "assigned_cut_words": parsed["cut_words"],
                "directionless_words": directionless,
                "missing_cut_authorities": missing_cut_authorities,
            },
            {
                "ambiguous_cut_payloads": [
                    "CUT|corpus-driver|OCCURRED|R",
                    "CUT|subject|OCCURRED|R",
                ],
                "minimal_directionless_abbreviation": "APPLICATION-UNRESOLVED:capture-missing",
            },
        )
    )

    closure_fragments = {
        "ATTEMPT": ["ATTEMPT:R@s0", "OCCURRED:R", "CAPTURE"],
        "EVOLVE": ["EVOLVE:s1", "EVOLVED:s1", "QUERY:q"],
        "TERMINATE": ["TERMINATE", "TERM-APPLIED", "TERM-DONE", "CAPTURE"],
    }
    terminal_answer_words = set(parsed["ans_words"])
    closure_status: dict[str, bool] = {}
    for operation, fragment in closure_fragments.items():
        intervening = fragment[1:-1]
        closure_status[operation] = any(
            token.split(":", 1)[0] in terminal_answer_words
            or token.startswith("EXPIRE:operation")
            for token in intervening
        )
    closure_failure = not all(closure_status.values()) and "A terminal\nanswer" in candidate
    checks.append(
        result(
            "F06",
            "successful_request_answer_or_expiry_closure",
            "FAIL" if closure_failure else "UNKNOWN",
            "static",
            "Successful ATTEMPT, EVOLVE, and TERMINATE must close with ANS or operation expiry.",
            {
                "closed_by_written_ans_or_expiry": closure_status,
                "cuts_treated_as_answers": False,
            },
            {"fragments": closure_fragments},
        )
    )

    poisoned_history = [
        "OBSERVE",
        "EVOLVE:s1",
        "BUSY:observation",
    ]
    selected_phase = first_match_phase(poisoned_history)
    observation_author = parsed["matrix"]["observation-open"]["AUTHOR"]
    poisoned_author = parsed["matrix"]["evolution-pending"]["AUTHOR"]
    phase_failure = (
        selected_phase == "evolution-pending"
        and observation_author == "BUSY:observation"
        and poisoned_author == "BUSY:evolution"
    )
    checks.append(
        result(
            "F07",
            "refused_evolve_phase_poisoning",
            "FAIL" if phase_failure else "UNKNOWN",
            "direct",
            "A retained refused EVOLVE request must not manufacture evolution-pending.",
            {
                "first_matching_phase": selected_phase,
                "pre_refusal_author_result": observation_author,
                "post_refusal_author_result": poisoned_author,
            },
            {
                "suffix": [
                    "REQ|audit|s0|EVOLVE|s1",
                    "ANS|audit|s0|EVOLVE|BUSY|observation",
                    "REQ|audit|s0|AUTHOR|R",
                ]
            },
        )
    )

    capture_literal = next(
        token for token in parsed["terminal_tail"] if token.startswith("CAPTURED:")
    )
    capture_has_promised_bytes = "CHUNK" in capture_literal and "EXPIRE" in capture_literal
    capture_failure = (
        capture_literal == "CAPTURED:retained"
        and not capture_has_promised_bytes
        and "includes the original observation\nchunks" in candidate
    )
    checks.append(
        result(
            "F08",
            "literal_retained_capture_payload",
            "FAIL" if capture_failure else "UNKNOWN",
            "static",
            "The exact CAPTURED payload must contain the promised retained chunk and expiry bytes.",
            {
                "literal": capture_literal,
                "literal_contains_chunk_and_expire": capture_has_promised_bytes,
            },
            {
                "expanded_answer": "ANS|audit|s1|CAPTURE|CAPTURED|retained",
                "distinct_promised_inputs": [
                    ["CHUNK:a", "EXPIRE"],
                    ["CHUNK:b", "EXPIRE"],
                ],
            },
        )
    )

    terminal_matrix = parsed["matrix"]["terminal"]["ATTEMPT"]
    terminal_tail_answer = parsed["terminal_tail"][-1]
    terminal_collision = terminal_matrix != terminal_tail_answer
    checks.append(
        result(
            "F09",
            "terminal_matrix_vs_terminal_refusal",
            "FAIL" if terminal_collision else "PASS",
            "direct",
            "The terminal ATTEMPT constructor must equal the literal terminal-tail answer.",
            {
                "literal_tail_answer": terminal_tail_answer,
                "matrix_constructor": terminal_matrix,
                "results_equal": not terminal_collision,
            },
            {
                "history_suffix": ["TERM-DONE"],
                "request": "REQ|audit|s1|ATTEMPT|R@s0",
                "required_results": [terminal_matrix, terminal_tail_answer],
            },
        )
    )

    limited_request = "REQ|limited|s0|OBSERVE|-"
    limited_forbids_identity = (
        'viewer.limited="generic-result,no-token-identity,no-evidence-identity"'
        in candidate
    )
    open_observe_route = parsed["matrix"]["open"]["OBSERVE"]
    observation_section = section(
        candidate,
        "### 6.2 Common observation/interpretation/authoring prefix",
        "### 6.3 Query over all five carrier histories",
    )
    explicit_limited_observation = "limited" in observation_section
    limited_failure = (
        limited_forbids_identity
        and open_observe_route == "N"
        and not explicit_limited_observation
    )
    checks.append(
        result(
            "F10",
            "limited_viewer_observation_constructor",
            "FAIL" if limited_failure else "UNKNOWN",
            "static",
            "An authorized limited OBSERVE needs an exact non-token-leaking constructor.",
            {
                "explicit_limited_observation_constructor": explicit_limited_observation,
                "limited_forbids_token_identity": limited_forbids_identity,
                "open_route": open_observe_route,
            },
            {
                "declared_chunk_payloads": ["a", "a+b", "b", "n"],
                "request": limited_request,
            },
        )
    )

    mutant_categories = (
        "length zero",
        "one malformed encoding",
        "one well-formed unknown operation",
        "one unknown version",
        "one unauthorized viewer",
    )
    normalized_candidate = " ".join(candidate.split())
    mutant_categories_present = all(
        item in normalized_candidate for item in mutant_categories
    )
    materialized_e_ledger_present = bool(
        re.search(r"(?:`E_K`|E_K)\s*=", candidate)
    )
    ledger_blockers = sorted(
        [
            "directionless APPLICATION-UNRESOLVED",
            "missing ordinary CUT authorities",
            "section 7.3 category-only mutants",
            "no materialized E ledger",
        ]
    )
    ledger_failure = (
        direction_failure and mutant_categories_present and not materialized_e_ledger_present
    )
    checks.append(
        result(
            "F11",
            "p_k_and_ledger_materializability",
            "FAIL" if ledger_failure else "UNKNOWN",
            "static",
            "The frozen bytes must determine reproducible P_K, Pairs(P_K), C entries, and E entries.",
            {
                "blockers": ledger_blockers,
                "category_mutants_present": mutant_categories_present,
                "exact_p_k_materializable": False,
                "materialized_e_ledger_present": materialized_e_ledger_present,
            },
            {
                "smallest_blocking_member": "APPLICATION-UNRESOLVED:capture-missing"
            },
        )
    )

    checks.extend(
        [
            result(
                "U01",
                "implementation_conformance",
                "UNKNOWN",
                "static",
                "No subject implementation or execution evidence may receive PASS.",
                {"executable_subject_supplied": False},
                {"missing": ["implementation", "runner output", "subject traces"]},
            ),
            result(
                "U02",
                "physical_and_unlike_realization_claims",
                "UNKNOWN",
                "static",
                "Physical completion, physical negatives, and cross-realization behavior need independent evidence.",
                {
                    "base_completion_evidence": "MISSING",
                    "materially_unlike_realizations_instantiated": 0,
                },
                {
                    "missing": [
                        "independent physical observer",
                        "physical interval and clock evidence",
                        "two realization-specific evidence sets",
                    ]
                },
            ),
            result(
                "U03",
                "global_support_minimality",
                "UNKNOWN",
                "static",
                "No global C/D/E minimization run or complete candidate universe is materialized.",
                {"deletion_only_promoted_to_global_minimum": False, "enumeration_supplied": False},
                {"missing": ["all smaller admissible tries", "range-addressed support archive"]},
            ),
            result(
                "U04",
                "tcb_and_external_context_closure",
                "UNKNOWN",
                "static",
                "K-CLOSE can falsify tested context binding but cannot prove global TCB closure.",
                {"finite_perturbation_surface_supplied": False, "independent_oracle_supplied": False},
                {"missing": ["dependency inventory", "perturbation evidence", "independent adjudicator"]},
            ),
        ]
    )

    return sorted(checks, key=lambda item: item["id"])


def main() -> int:
    loaded: dict[str, bytes] = {}
    input_records: list[dict[str, str]] = []
    gate_pass = True
    for name, required in INPUTS:
        path = BASE / name
        try:
            data = path.read_bytes()
            observed = sha256(data)
        except OSError:
            data = b""
            observed = "MISSING"
        verdict = "PASS" if observed == required else "FAIL"
        gate_pass = gate_pass and verdict == "PASS"
        loaded[name] = data
        input_records.append(
            {
                "name": name,
                "observed_sha256": observed,
                "required_sha256": required,
                "verdict": verdict,
            }
        )

    if not gate_pass:
        checks = [
            result(
                "F00",
                "frozen_input_gate",
                "FAIL",
                "direct",
                "All frozen inputs must match their pinned hashes before checks run.",
                {"checks_executed": False},
                {"failed_inputs": sorted(item["name"] for item in input_records if item["verdict"] == "FAIL")},
            )
        ]
    else:
        try:
            checks = run_checks(
                loaded["HISTORY-SEED-R01K.md"].decode("utf-8"),
                loaded["POSTFREEZE-BREAK-R01K.md"].decode("utf-8"),
            )
        except (UnicodeDecodeError, ValueError) as error:
            checks = [
                result(
                    "F00",
                    "frozen_input_parse",
                    "FAIL",
                    "static",
                    "Pinned input parsing must complete before substantive checks.",
                    {"checks_executed": False, "error_type": type(error).__name__},
                    {"parser_state": "fail-closed"},
                )
            ]

    counts = {verdict: 0 for verdict in VERDICTS}
    for check in checks:
        counts[check["verdict"]] += 1
    overall = "FAIL" if counts["FAIL"] else "UNKNOWN" if counts["UNKNOWN"] else "PASS"
    document = {
        "artifact": "r01k-history-experiment",
        "input_gate": "PASS" if gate_pass else "FAIL",
        "inputs": input_records,
        "overall": overall,
        "results": checks,
        "scope_semantics": {
            "direct": "constructed bytes, sequences, or finite arithmetic",
            "static": "contradiction or coverage check over pinned frozen text",
        },
        "summary": counts,
        "version": 1,
    }
    emit(document)
    return 1 if overall == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
