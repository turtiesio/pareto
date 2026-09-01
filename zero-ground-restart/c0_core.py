"""Deduplicated witness core for the declared B1 coverage criterion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from c0_candidates import decode_history
from c0_experiment import (
    COMPONENT_NAMES,
    RESUME,
    BoundedResiduals,
    Context,
    DeletionSearch,
    Witness,
    component_vector,
    history_order,
)
from c0_oracle import ACTION, Frame, append_legal, drain_history, inbound, replay


History = tuple[Frame, ...]


def _turns(*commands: Frame) -> History:
    result: History = ()
    for command in commands:
        result = append_legal(result, command)
        if replay(result).owed is not None:
            result = drain_history(result)
    return result


def _cut(base: History, command: Frame) -> History:
    return append_legal(base, command)


@dataclass(frozen=True)
class NamedCase:
    histories: tuple[History, ...]
    contexts: tuple[Context, ...] = ()


def named_cases() -> dict[str, NamedCase]:
    p0 = _turns(inbound("P", "a", "0"))
    p1 = _turns(inbound("P", "a", "1"))
    pending_k0 = _turns(inbound("P", "a", "0"), inbound("A", "k"))
    pending_k1 = _turns(inbound("P", "a", "1"), inbound("A", "k"))
    pending_l0 = _turns(inbound("P", "a", "0"), inbound("A", "l"))
    done_k0 = _turns(
        inbound("P", "a", "0"),
        inbound("A", "k"),
        inbound("ACK", "k", port=ACTION),
    )
    changed_pending = _turns(
        inbound("P", "a", "0"), inbound("A", "k"), inbound("P", "a", "1")
    )

    cases = {
        "G01": NamedCase(
            (_cut((), inbound("O")), _turns(inbound("O"))),
            (Context((RESUME,)),),
        ),
        "G02": NamedCase(
            (_turns(inbound("R", "u", "0", "1")), _turns(inbound("R", "u", "0", "0"))),
            (Context((inbound("P", "a", "1"), inbound("Q"), RESUME)),),
        ),
        "G03": NamedCase(
            (_turns(inbound("R", "u", "0", "1")), _turns(inbound("R", "v", "0", "1"))),
            (Context((inbound("P", "a", "0"), inbound("X"), RESUME)),),
        ),
        "G04": NamedCase(
            (changed_pending, pending_k1),
            (Context((inbound("S", "k"), RESUME)),),
        ),
        "G05": NamedCase(
            (changed_pending,), (Context((inbound("A", "k"), RESUME)),)
        ),
        "G06": NamedCase(
            (pending_k0, done_k0), (Context((inbound("S", "k"), RESUME)),)
        ),
        "G07": NamedCase(
            (pending_k0, pending_l0), (Context((inbound("S", "k"), RESUME)),)
        ),
        "G08": NamedCase(
            (_cut((), inbound("A", "k")), _cut((), inbound("S", "k"))),
            (Context((RESUME,)),),
        ),
        "G09": NamedCase(
            (_cut(p1, inbound("X")),), (Context((RESUME,)),)
        ),
        "E01": NamedCase(
            tuple(_cut((), inbound(kind)) for kind in ("O", "Q", "X"))
        ),
        "E02": NamedCase((p0, _turns(inbound("P", "a", "0"), inbound("O")), _turns(inbound("P", "a", "0"), inbound("Q")))),
        "E03": NamedCase((_turns(inbound("P", "a", "0"), inbound("P", "b", "1")), _turns(inbound("P", "b", "1")))),
        "E04": NamedCase((_turns(inbound("R", "u", "0", "0"), inbound("R", "v", "0", "1")), _turns(inbound("R", "v", "0", "1")))),
        "E05": NamedCase((_turns(inbound("P", "a", "0"), inbound("R", "v", "0", "1")), _turns(inbound("R", "v", "0", "1"), inbound("P", "a", "0")))),
        "E06": NamedCase(((), _turns(inbound("A", "k")))),
        "E07": NamedCase((_turns(inbound("A", "k"), inbound("P", "a", "0"), inbound("A", "k")), pending_k0)),
        "E08": NamedCase((pending_k0, _turns(inbound("P", "a", "0"), inbound("A", "k"), inbound("A", "k")))),
        "E09": NamedCase((pending_k0, _turns(inbound("P", "a", "0"), inbound("A", "k"), inbound("S", "k")))),
    }

    cut_bases = {
        "EMPTY": ((), inbound("O")),
        "RAW": (p0, inbound("O")),
        "VAL": (p0, inbound("Q")),
        "WHY": (p1, inbound("X")),
        "NO_DATA": ((), inbound("A", "k")),
        "DO": (p0, inbound("A", "k")),
        "ALREADY": (done_k0, inbound("A", "k")),
        "ABSENT": ((), inbound("S", "k")),
        "PENDING": (pending_k0, inbound("S", "k")),
        "DONE": (done_k0, inbound("S", "k")),
    }
    for kind, (base, command) in cut_bases.items():
        cases[f"CUT_{kind}"] = NamedCase(
            (_cut(base, command),),
            (
                Context((RESUME,)),
                Context((inbound("P", "b", "1"),)),
                Context((RESUME, RESUME)),
            ),
        )
    return cases


def _decode_context(token: str) -> Context:
    if token == "<stop>":
        return Context(())
    operations: list[Frame | str] = []
    for part in token.split(";"):
        if part == RESUME:
            operations.append(RESUME)
        else:
            operations.append(decode_history(part.encode("utf-8"))[0])
    return Context(tuple(operations))


def _has_collision(
    histories: Iterable[History], mask: int, residuals: BoundedResiduals
) -> bool:
    groups: dict[tuple[str, ...], int] = {}
    for history in histories:
        snapshot = replay(history)
        vector = component_vector(snapshot)
        projected = tuple(value for i, value in enumerate(vector) if mask & (1 << i))
        signature = residuals.class_id(snapshot)
        prior = groups.setdefault(projected, signature)
        if prior != signature:
            return True
    return False


@dataclass(frozen=True)
class WitnessCore:
    histories: tuple[History, ...]
    contexts: tuple[Context, ...]
    named_case_ids: tuple[str, ...]
    direct_collision_components: tuple[str, ...]
    deletion_certificate: Mapping[str, str]


def build_witness_core(
    deletion_search: DeletionSearch,
    direct_witnesses: Mapping[str, Witness | str],
    residuals: BoundedResiduals,
) -> WitnessCore:
    cases = named_cases()
    required_histories = {
        history for case in cases.values() for history in case.histories
    }
    histories = set(required_histories)
    contexts = {context for case in cases.values() for context in case.contexts}
    direct_masks: dict[str, int] = {}
    full = (1 << len(COMPONENT_NAMES)) - 1
    for index, name in enumerate(COMPONENT_NAMES):
        value = direct_witnesses[name]
        if isinstance(value, str):
            continue
        histories.add(decode_history(";".join(value.left).encode("utf-8")))
        histories.add(decode_history(";".join(value.right).encode("utf-8")))
        contexts.add(_decode_context(value.future))
        direct_masks[name] = full & ~(1 << index)

    # Greedily delta-delete only histories not fixed by an exact hidden/golden
    # endpoint. Repeat to a fixed point; every retained extra history then has a
    # named direct-deletion branch that would lose its last collision witness.
    changed = True
    while changed:
        changed = False
        for candidate in sorted(histories - required_histories, key=history_order, reverse=True):
            trial = histories - {candidate}
            if all(_has_collision(trial, mask, residuals) for mask in direct_masks.values()):
                histories = trial
                changed = True

    certificate: dict[str, str] = {}
    for candidate in histories:
        if candidate in required_histories:
            certificate[";".join(frame.token() for frame in candidate)] = "fixed named-case endpoint"
            continue
        lost = [
            name
            for name, mask in direct_masks.items()
            if not _has_collision(histories - {candidate}, mask, residuals)
        ]
        certificate[";".join(frame.token() for frame in candidate)] = (
            "last witness for " + ",".join(lost)
        )

    return WitnessCore(
        tuple(sorted(histories, key=history_order)),
        tuple(sorted(contexts, key=lambda value: (value.depth, len(value.operations), value.token()))),
        tuple(sorted(cases)),
        tuple(sorted(direct_masks)),
        certificate,
    )
