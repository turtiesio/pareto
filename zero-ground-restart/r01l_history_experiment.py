#!/usr/bin/env python3
"""Independent finite falsifier for frozen ZERO GROUND candidate R0.1L.

This executes the candidate's embedded reference block, audits its declared
pair-minimization implementation, and runs the post-freeze D1 domain.  It is a
falsification instrument, not a subject implementation or architecture.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path


CANDIDATE = "HISTORY-SEED-R01L.md"
CANDIDATE_SHA256 = (
    "0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb"
)
CODE_SHA256 = "a7fe34a112919b319739fc79dc37f8c9c0ed036a4e73ae2a33081df55a3e4d84"
EXPECTED_STDOUT_SHA256 = (
    "f6b53a0777363a7173c703fd34397bc3f770905705d3f35f08b4279e30009587"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fenced_after(text: str, marker: str, language: str) -> str:
    marker_at = text.index(marker)
    opening = f"```{language}\n"
    start = text.index(opening, marker_at) + len(opening)
    end = text.index("\n```", start)
    return text[start:end] + "\n"


def encode_projection(history, kept=(0, 2, 3), mode="ordered"):
    events = [bytes(command[k] for k in kept) for command in history[3]]
    if mode == "bag":
        events = sorted(events)
    elif mode == "set":
        events = sorted(set(events))
    return NS["seq"](events)


def local_hkey(histories, i: int, j: int):
    a, b = histories[i], histories[j]
    la, lb = len(a[0]) - 1, len(b[0]) - 1
    return (
        la + lb,
        max(la, lb),
        min(a[4], b[4]),
        max(a[4], b[4]),
    )


def exact_collision(
    histories,
    encoder,
    state_to_id,
    equivalence_id,
    signatures,
    futures,
):
    """Return the exact declared minimum without first-representative bias."""

    # For a fixed encoding, tail length, and equivalence class, only the
    # lexically least transcript can improve the declared pair key.
    groups = {}
    for i, history in enumerate(histories):
        encoded = encoder(history)
        q = equivalence_id[state_to_id[history[2]]]
        bucket = groups.setdefault(encoded, {})
        slot = (len(history[0]) - 1, q)
        prior = bucket.get(slot)
        if prior is None or history[4] < histories[prior][4]:
            bucket[slot] = i

    best = None
    for bucket in groups.values():
        representatives = sorted(bucket.items())
        for left_pos in range(len(representatives)):
            (left_length, left_q), left = representatives[left_pos]
            for right_pos in range(left_pos + 1, len(representatives)):
                (right_length, right_q), right = representatives[right_pos]
                if left_q == right_q:
                    continue
                key = local_hkey(histories, left, right)
                if best is not None and key >= best[0]:
                    continue
                left_signature = signatures[state_to_id[histories[left][2]]]
                right_signature = signatures[state_to_id[histories[right][2]]]
                witness = next(
                    z
                    for z, (a, b) in enumerate(
                        zip(left_signature, right_signature, strict=True)
                    )
                    if a != b
                )
                best = key, left, right, witness
    return best


def history_names(history):
    return [command.decode("ascii") for command in history[0]]


def normalized_pair(histories, collision):
    if collision is None:
        return None
    key, left, right, witness = collision
    names = sorted((history_names(histories[left]), history_names(histories[right])))
    return {
        "key": [key[0], key[1], key[2].hex(), key[3].hex()],
        "histories": names,
        "witness_index": witness,
    }


def reference_pair(reference_collision):
    if reference_collision is None:
        return None
    key, left, right, witness = reference_collision
    names = sorted((history_names(NS["hist"][left]), history_names(NS["hist"][right])))
    return {
        "key": [key[0], key[1], key[2].hex(), key[3].hex()],
        "histories": names,
        "witness_index": witness,
    }


def build_d1_histories():
    alphabet = NS["H"]
    level = [()]
    for _ in range(4):
        level = [prefix + (command,) for prefix in level for command in alphabet]

    histories = list(NS["hist"])
    for tail in level:
        commands = (b"B",) + tail
        state, outputs = NS["run"](NS["init"](), commands)
        histories.append(
            (
                commands,
                outputs,
                state,
                NS["accepted"](commands),
                NS["transcript"](commands, outputs),
            )
        )
    return histories


def build_d1_futures():
    futures = list(NS["futs"])
    first = (b"B", b"DA0B", b"IA01", b"FA01", b"AA00")
    next_commands = (b"WA0x", b"Q0r", b"Q0t", b"E0c", b"AA00")
    futures.extend(
        ("N3", (a, b, c))
        for a in first
        for b in next_commands
        for c in next_commands
    )

    thirds = (b"E0c", b"Q0r", b"Q0t", b"AA00", b"Q0o")
    futures.extend(
        ("A3", adaptive + (third,))
        for adaptive, third in zip(NS["ads"], thirds, strict=True)
    )
    futures.extend(
        (
            (
                "A3",
                (b"FA01", b"K", b"WA1x", b"Q1p", b"Q1r"),
            ),
            (
                "A3",
                (b"DA0B", b"K", b"AB00", b"AA00", b"E00"),
            ),
        )
    )
    return futures


def evaluate_extended(state, future):
    kind, payload = future
    if kind in ("N", "A"):
        return NS["feval"](state, future)
    if kind == "N3":
        return NS["run"](state, payload)[1]
    first, prefix, yes, no, third = payload
    next_state, first_output = NS["step"](state, first)
    second = yes if first_output.startswith(prefix) else no
    next_state, second_output = NS["step"](next_state, second)
    _, third_output = NS["step"](next_state, third)
    return (
        NS["frm"](b"O", first_output),
        NS["frm"](b"O", second_output),
        NS["frm"](b"O", third_output),
    )


def state_partition(histories, futures):
    states = []
    state_to_id = {}
    for history in histories:
        state = history[2]
        if state not in state_to_id:
            state_to_id[state] = len(states)
            states.append(state)

    signatures = [
        tuple(evaluate_extended(state, future) for future in futures)
        for state in states
    ]
    signature_to_equivalence = {}
    equivalence_id = []
    for signature in signatures:
        if signature not in signature_to_equivalence:
            signature_to_equivalence[signature] = len(signature_to_equivalence)
        equivalence_id.append(signature_to_equivalence[signature])
    return states, state_to_id, signatures, equivalence_id


def first_bounded_collision(histories, encoder, state_to_id, equivalence_id):
    seen = {}
    for index, history in enumerate(histories):
        encoded = encoder(history)
        q = equivalence_id[state_to_id[history[2]]]
        prior = seen.get(encoded)
        if prior is None:
            seen[encoded] = q, index
        elif prior[0] != q:
            return prior[1], index
    return None


def replay_projection(history):
    state = NS["init"]()
    for command in history[3]:
        operation, target, argument = command[0], command[2], command[3]
        branches, _ = NS["maps"](state)
        if target not in branches:
            return None
        actor = branches[target][1]
        reconstructed = bytes((operation, actor, target, argument))
        next_state, _ = NS["step"](state, reconstructed)
        if next_state == state:
            return None
        state = next_state
    return state


ROOT = Path(__file__).resolve().parent
candidate_bytes = (ROOT / CANDIDATE).read_bytes()
candidate_digest = sha256(candidate_bytes)
if candidate_digest != CANDIDATE_SHA256:
    raise SystemExit(
        json.dumps(
            {
                "artifact": "r01l-history-experiment",
                "input_gate": "FAIL",
                "observed_sha256": candidate_digest,
                "required_sha256": CANDIDATE_SHA256,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )

candidate_text = candidate_bytes.decode("utf-8")
code = fenced_after(candidate_text, "### 4.3 Executable reference", "python")
expected_stdout = fenced_after(
    candidate_text, "### 4.4 Exact expected output", "text"
)

code_digest = sha256(code.encode("utf-8"))
captured = io.StringIO()
NS = {"__builtins__": __builtins__}
with contextlib.redirect_stdout(captured):
    exec(compile(code, f"{CANDIDATE}:embedded", "exec"), NS)
reference_stdout = captured.getvalue()

results = []


def record(identifier, verdict, claim, details):
    results.append(
        {
            "id": identifier,
            "verdict": verdict,
            "claim": claim,
            "details": details,
        }
    )


reference_ok = (
    code_digest == CODE_SHA256
    and sha256(reference_stdout.encode("utf-8")) == EXPECTED_STDOUT_SHA256
    and reference_stdout == expected_stdout
)
record(
    "R01",
    "PASS" if reference_ok else "FAIL",
    "The embedded reference block and exact expected stdout reproduce.",
    {
        "code_sha256": code_digest,
        "stdout_sha256": sha256(reference_stdout.encode("utf-8")),
        "stdout_matches_frozen_text": reference_stdout == expected_stdout,
    },
)

minimization_mismatches = []
for name, encoder in NS["cands"]:
    reference = reference_pair(NS["collision"](encoder))
    exact = normalized_pair(
        NS["hist"],
        exact_collision(
            NS["hist"],
            encoder,
            NS["sid"],
            NS["eq"],
            NS["sigs"],
            NS["futs"],
        ),
    )
    if reference != exact:
        minimization_mismatches.append(
            {"candidate": name, "reference": reference, "exact": exact}
        )

record(
    "R02",
    "PASS" if not minimization_mismatches else "FAIL",
    "The reference collision routine returns the declared exact pair minimum.",
    {"mismatches": minimization_mismatches},
)

d1_histories = build_d1_histories()
d1_futures = build_d1_futures()
d1_states, d1_sid, d1_signatures, d1_eq = state_partition(
    d1_histories, d1_futures
)

projected_collision = first_bounded_collision(
    d1_histories,
    lambda history: encode_projection(history),
    d1_sid,
    d1_eq,
)
accepted_collision = first_bounded_collision(
    d1_histories,
    NS["eaccept"],
    d1_sid,
    d1_eq,
)

record(
    "R03",
    "PASS" if projected_collision is None else "FAIL",
    "PROJECTED3 has no collision in the frozen D1 history/future domain.",
    {
        "collision": None
        if projected_collision is None
        else [
            history_names(d1_histories[projected_collision[0]]),
            history_names(d1_histories[projected_collision[1]]),
        ],
        "histories": len(d1_histories),
        "states": len(d1_states),
        "futures": len(d1_futures),
        "equivalence_classes": len(set(d1_eq)),
    },
)

record(
    "R04",
    "PASS" if accepted_collision is None else "FAIL",
    "ACCEPTED4 has no collision in the frozen D1 history/future domain.",
    {
        "collision": None
        if accepted_collision is None
        else [
            history_names(d1_histories[accepted_collision[0]]),
            history_names(d1_histories[accepted_collision[1]]),
        ]
    },
)

projection_failures = []
for index, history in enumerate(d1_histories):
    reconstructed = replay_projection(history)
    if reconstructed != history[2]:
        projection_failures.append(
            {
                "history": history_names(history),
                "reconstructed": None if reconstructed is None else repr(reconstructed),
            }
        )
        if len(projection_failures) == 5:
            break

record(
    "R05",
    "PASS" if not projection_failures else "FAIL",
    "Actor reconstruction reaches the oracle state for every D1 history.",
    {"first_failures": projection_failures},
)

long_state = NS["init"]()
state_at_9361 = None
long_outputs_accepted = True
for write_number in range(1, 9363):
    next_state, output = NS["step"](long_state, b"WA0x")
    if next_state == long_state or output != b"K":
        long_outputs_accepted = False
        break
    long_state = next_state
    if write_number == 9361:
        state_at_9361 = long_state

oracle_at_9361 = None
oracle_at_9362 = None
try:
    oracle_at_9361 = NS["oracle"](state_at_9361)
except Exception as error:  # pragma: no cover - evidence is reported below
    oracle_at_9361 = f"{type(error).__name__}: {error}"
try:
    NS["oracle"](long_state)
except Exception as error:
    oracle_at_9362 = f"{type(error).__name__}: {error}"

branch_item_length_9361 = 8 + 7 * 9361
branch_item_length_9362 = 8 + 7 * 9362
oracle_total = (
    long_outputs_accepted
    and isinstance(oracle_at_9361, bytes)
    and oracle_at_9362 is None
)
record(
    "F01",
    "PASS" if oracle_total else "FAIL",
    "ORACLE is a total canonical serialization for every valid ZG-1 history.",
    {
        "all_9362_writes_accepted": long_outputs_accepted,
        "branch_item_length_at_9361": branch_item_length_9361,
        "branch_item_length_at_9362": branch_item_length_9362,
        "u16_maximum": 65535,
        "oracle_at_9361": "encoded"
        if isinstance(oracle_at_9361, bytes)
        else oracle_at_9361,
        "oracle_at_9362": oracle_at_9362,
        "witness": {
            "history": "B followed by 9,362 WA0x requests",
            "future_needed": [],
        },
    },
)

unknown_obligations = (
    (
        "U01",
        "complete_future_observable_quotient",
        "Only the frozen D and D1 future domains were enumerated.",
    ),
    (
        "U02",
        "global_minimality",
        "No complete candidate-representation universe or all-smaller search exists.",
    ),
    (
        "U03",
        "subject_conformance",
        "The reference replay is an oracle/falsifier, not a subject execution.",
    ),
    (
        "U04",
        "physical_durability",
        "No fault set, persistent substrate, or independent physical evidence was run.",
    ),
    (
        "U05",
        "human_cognition",
        "No authoring, comprehension, navigation, or verification study was run.",
    ),
    (
        "U06",
        "tcb_closure",
        "No complete influence inventory, perturbation surface, or independent oracle exists.",
    ),
    (
        "U07",
        "materially_unlike_realizations",
        "No pair of physical realizations or independently rooted evidence sets exists.",
    ),
)
for identifier, name, reason in unknown_obligations:
    record(
        identifier,
        "UNKNOWN",
        f"{name} is not established by this executable.",
        {"reason": reason},
    )

summary = {"PASS": 0, "FAIL": 0, "UNKNOWN": 0}
for result in results:
    summary[result["verdict"]] += 1

report = {
    "artifact": "r01l-history-experiment",
    "version": 1,
    "input_gate": "PASS",
    "candidate_sha256": candidate_digest,
    "scope": {
        "reference_domain": "7,240 histories and 655 futures",
        "fresh_domain": "137,561 histories and 787 futures",
        "not_established": [
            "complete future-observable quotient",
            "global minimality",
            "subject conformance",
            "physical durability",
            "human cognition",
            "TCB closure",
            "materially unlike realizations",
        ],
    },
    "results": results,
    "summary": summary,
    "overall": "FAIL" if summary["FAIL"] else "PASS_WITH_UNKNOWNS",
}

print(json.dumps(report, sort_keys=True, separators=(",", ":")))
raise SystemExit(1 if summary["FAIL"] else 0)
