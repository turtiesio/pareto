"""Bounded history enumeration and independent quotient construction for C0/B1."""

from __future__ import annotations

from array import array
import base64
from collections import defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
import hashlib
from itertools import product
from typing import Callable, Iterable, Iterator, Mapping, Optional
import zlib

from c0_oracle import (
    ACTION,
    CLIENT,
    INPUTS,
    Frame,
    Snapshot,
    accept,
    complete_turn,
    frame_tokens,
    history_token,
    replay,
    resume,
)


DISABLED = "disabled"
ENABLED = "enabled"


@dataclass(frozen=True, order=True)
class UnknownCell:
    """An out-of-grammar result that is deliberately unusable as equivalence."""

    cell: str


@dataclass(frozen=True, order=True)
class Observation:
    """Proof comparison value.

    ``domain_membership`` contains proof markers, not boundary output frames.
    """

    domain_membership: tuple[str, ...]
    client: tuple[str, ...]
    action: tuple[str, ...]

    def flattened(self) -> tuple[str, ...]:
        return (
            *(f"domain:{value}" for value in self.domain_membership),
            *(f"client:{value}" for value in self.client),
            *(f"action:{value}" for value in self.action),
        )


RESUME = "resume"


@dataclass(frozen=True, order=True)
class Context:
    operations: tuple[Frame | str, ...]

    @property
    def depth(self) -> int:
        return sum(isinstance(operation, Frame) for operation in self.operations)

    def token(self) -> str:
        return ";".join(
            operation.token() if isinstance(operation, Frame) else operation
            for operation in self.operations
        ) or "<stop>"


@dataclass(frozen=True)
class HistoryCorpus:
    histories: tuple[tuple[Frame, ...], ...]
    inbound_depth: Mapping[tuple[Frame, ...], int]
    max_inbound: int


def history_order(history: tuple[Frame, ...]) -> tuple[object, ...]:
    return (len(history), frame_tokens(history))


def generate_histories(max_inbound: int = 4) -> HistoryCorpus:
    """Generate every legal raw boundary prefix under the inbound bound."""

    root: tuple[Frame, ...] = ()
    queue = deque([(root, 0)])
    seen: dict[tuple[Frame, ...], int] = {root: 0}
    while queue:
        history, depth = queue.popleft()
        snapshot = replay(history)
        if snapshot.owed is not None:
            child = history + (snapshot.owed,)
            if child not in seen:
                seen[child] = depth
                queue.append((child, depth))
            continue
        if depth >= max_inbound:
            continue
        for frame in INPUTS:
            step = accept(snapshot, frame)
            if not step.legal:
                continue
            child = history + (frame,)
            if child not in seen:
                seen[child] = depth + 1
                queue.append((child, depth + 1))
    histories = tuple(sorted(seen, key=history_order))
    return HistoryCorpus(histories, seen, max_inbound)


def future_contexts(max_inputs: int = 2) -> tuple[Context, ...]:
    """All normalized scheduler choices around domain proposals.

    There may be a resume before the first proposal, between proposals, and
    after the final proposal. A rejected proposal is a proof-level non-event;
    the marker records domain membership, not a boundary response. Consecutive
    resumes are observationally idempotent in B1 and therefore have a single
    normalized representative.
    """

    contexts: list[Context] = []
    for depth in range(max_inputs + 1):
        for word in product(INPUTS, repeat=depth):
            for resume_slots in product((False, True), repeat=depth + 1):
                operations: list[Frame | str] = []
                for index, frame in enumerate(word):
                    if resume_slots[index]:
                        operations.append(RESUME)
                    operations.append(frame)
                if resume_slots[-1]:
                    operations.append(RESUME)
                contexts.append(Context(tuple(operations)))
    return tuple(sorted(set(contexts), key=lambda c: (c.depth, len(c.operations), c.token())))


def _append_output(
    frame: Frame,
    client: list[str],
    action: list[str],
) -> None:
    if frame.port == CLIENT:
        client.append(frame.token())
    elif frame.port == ACTION:
        action.append(frame.token())
    else:
        raise AssertionError(f"undeclared output port: {frame.port}")


def evaluate_context(snapshot: Snapshot, context: Context) -> Observation:
    """Evaluate one union-domain proof context without a candidate encoder."""

    domain_membership: list[str] = []
    client: list[str] = []
    action: list[str] = []

    current = snapshot
    for operation in context.operations:
        if operation == RESUME:
            emitted = resume(current)
            for crossed in emitted.crossed:
                _append_output(crossed, client, action)
            current = emitted.snapshot
            continue
        assert isinstance(operation, Frame)
        step = accept(current, operation)
        if not step.legal:
            domain_membership.append(DISABLED)
            continue
        domain_membership.append(ENABLED)
        current = step.snapshot
    return Observation(tuple(domain_membership), tuple(client), tuple(action))


class BoundedResiduals:
    """Intern exact bounded strategy trees; hashes are never equality.

    Inbound-proposal, scheduler-resume, and total-step budgets are derived from the
    supplied contexts. For the default C0 contexts they are 2, 3, and 5. Keeping
    the derived step bound explicit prevents a quiescent ``resume`` self-loop
    from making the recursion infinite and keeps non-default runs consistent
    with their context generator.
    """

    def __init__(self, contexts: tuple[Context, ...]):
        self.contexts = contexts
        self.max_inbound_proposals = max((context.depth for context in contexts), default=0)
        self.max_resume_steps = max(
            (
                sum(operation == RESUME for operation in context.operations)
                for context in contexts
            ),
            default=0,
        )
        self.max_total_steps = max(
            (len(context.operations) for context in contexts), default=0
        )
        self._ids: dict[tuple[object, ...], int] = {}
        self._nodes: list[tuple[object, ...]] = []

    @lru_cache(maxsize=None)
    def _node(
        self,
        snapshot: Snapshot,
        proposals_left: int,
        resumes_left: int,
        steps_left: int,
    ) -> int:
        if steps_left == 0 or (proposals_left == 0 and resumes_left == 0):
            key: tuple[object, ...] = ("stop",)
        else:
            branches: list[object] = []
            if resumes_left:
                emitted = resume(snapshot)
                client = tuple(
                    frame.token() for frame in emitted.crossed if frame.port == CLIENT
                )
                action = tuple(
                    frame.token() for frame in emitted.crossed if frame.port == ACTION
                )
                observation = Observation((), client, action)
                child = self._node(
                    emitted.snapshot, proposals_left, resumes_left - 1, steps_left - 1
                )
                branches.append((RESUME, observation, child))
            if proposals_left:
                for frame in INPUTS:
                    step = accept(snapshot, frame)
                    observation = Observation(
                        ((ENABLED if step.legal else DISABLED),), (), ()
                    )
                    child = self._node(
                        step.snapshot,
                        proposals_left - 1,
                        resumes_left,
                        steps_left - 1,
                    )
                    branches.append((frame.token(), observation, child))
            key = tuple(branches)
        found = self._ids.get(key)
        if found is not None:
            return found
        value = len(self._nodes)
        self._ids[key] = value
        self._nodes.append(key)
        return value

    def class_id(self, snapshot: Snapshot) -> int:
        return self._node(
            snapshot,
            self.max_inbound_proposals,
            self.max_resume_steps,
            self.max_total_steps,
        )

    def first_difference(
        self, left: Snapshot, right: Snapshot
    ) -> Optional[tuple[Context, Observation, Observation, int]]:
        if self.class_id(left) == self.class_id(right):
            return None
        best: Optional[
            tuple[tuple[object, ...], Context, Observation, Observation, int]
        ] = None
        for context in self.contexts:
            lvalue = evaluate_context(left, context)
            rvalue = evaluate_context(right, context)
            if lvalue != rvalue:
                divergence = first_divergence(lvalue, rvalue)
                score = (context.depth, divergence, context.token())
                candidate = (score, context, lvalue, rvalue, divergence)
                if best is None or score < best[0]:
                    best = candidate
        if best is None:
            return None
        return best[1], best[2], best[3], best[4]


def first_divergence(left: Observation, right: Observation) -> int:
    """Return the first differing flattened coordinate, not temporal order."""
    lflat, rflat = left.flattened(), right.flattened()
    common = min(len(lflat), len(rflat))
    for index in range(common):
        if lflat[index] != rflat[index]:
            return index
    return common


@dataclass(frozen=True)
class TurnEdge:
    """One proof edge; ``in_domain`` is membership, not emitted output."""

    in_domain: bool
    client: tuple[str, ...]
    action: tuple[str, ...]
    target: int

    @property
    def proof_signature(self) -> tuple[object, ...]:
        return (self.in_domain, self.client, self.action)


class StableRightCongruence:
    """Stable Mealy quotient of the complete finite-domain quiescent machine.

    Bounded signatures remain separately available. This refinement closes only
    the frozen value grammar; it says nothing about fresh values or operations.
    """

    def __init__(self) -> None:
        self.states: list[Snapshot] = []
        self.state_ids: dict[Snapshot, int] = {}
        self.edges: list[tuple[TurnEdge, ...]] = []
        self.partitions: tuple[int, ...] = ()
        self.refinement_rounds = 0
        self._build_reachable_turn_machine()
        self._refine()
        self._representative_state_by_part: dict[int, int] = {}
        for index, part in enumerate(self.partitions):
            self._representative_state_by_part.setdefault(part, index)

    def _add(self, snapshot: Snapshot) -> tuple[int, bool]:
        assert snapshot.owed is None
        found = self.state_ids.get(snapshot)
        if found is not None:
            return found, False
        index = len(self.states)
        self.state_ids[snapshot] = index
        self.states.append(snapshot)
        self.edges.append(())
        return index, True

    def _build_reachable_turn_machine(self) -> None:
        from c0_oracle import INITIAL

        _, _ = self._add(INITIAL)
        cursor = 0
        while cursor < len(self.states):
            snapshot = self.states[cursor]
            state_edges: list[TurnEdge] = []
            for frame in INPUTS:
                step, outputs = complete_turn(snapshot, frame)
                if not step.legal:
                    state_edges.append(TurnEdge(False, (), (), cursor))
                    continue
                assert step.snapshot.owed is None
                target, _new = self._add(step.snapshot)
                client = tuple(output.token() for output in outputs if output.port == CLIENT)
                action = tuple(output.token() for output in outputs if output.port == ACTION)
                state_edges.append(TurnEdge(True, client, action, target))
            self.edges[cursor] = tuple(state_edges)
            cursor += 1

    @staticmethod
    def _intern(keys: Iterable[object]) -> tuple[int, ...]:
        ids: dict[object, int] = {}
        result: list[int] = []
        for key in keys:
            if key not in ids:
                ids[key] = len(ids)
            result.append(ids[key])
        return tuple(result)

    def _refine(self) -> None:
        proof_signatures = tuple(
            tuple(edge.proof_signature for edge in state_edges)
            for state_edges in self.edges
        )
        parts = self._intern(proof_signatures)
        while True:
            keys = (
                (
                    proof_signatures[index],
                    tuple(parts[edge.target] for edge in self.edges[index]),
                )
                for index in range(len(self.states))
            )
            refined = self._intern(keys)
            self.refinement_rounds += 1
            if len(set(refined)) == len(set(parts)):
                parts = refined
                break
            parts = refined
        self.partitions = parts
        self._verify_right_congruence()

    def _verify_right_congruence(self) -> None:
        fingerprints: dict[int, tuple[object, ...]] = {}
        for index, part in enumerate(self.partitions):
            fingerprint = tuple(
                (edge.proof_signature, self.partitions[edge.target])
                for edge in self.edges[index]
            )
            prior = fingerprints.setdefault(part, fingerprint)
            if prior != fingerprint:
                raise AssertionError("partition is not a right congruence")

    @property
    def class_count(self) -> int:
        return len(set(self.partitions))

    def quiescent_part(self, snapshot: Snapshot) -> int:
        if snapshot.owed is not None:
            raise ValueError("snapshot is not quiescent")
        return self.partitions[self.state_ids[snapshot]]

    def class_key(self, snapshot: Snapshot) -> tuple[str, ...]:
        if snapshot.owed is None:
            return ("q", str(self.quiescent_part(snapshot)))
        owed = snapshot.owed
        settled = resume(snapshot).snapshot
        return ("o", owed.token(), str(self.quiescent_part(settled)))

    def representative_index(self, part: int) -> int:
        return self._representative_state_by_part[part]

    def edge_for_part(self, part: int, input_index: int) -> TurnEdge:
        return self.edges[self.representative_index(part)][input_index]


COMPONENT_NAMES: tuple[str, ...] = (
    "current_source",
    "current_bit",
    "rule_label",
    "rule_on_0",
    "rule_on_1",
    "action_k",
    "action_l",
    "owed_port",
    "owed_kind",
    "owed_arguments",
)


def _action_component(record: object) -> str:
    if record is None:
        return "-"
    status = record.status  # type: ignore[attr-defined]
    descriptor = record.descriptor  # type: ignore[attr-defined]
    return ":".join((status, *descriptor.flat()))


def component_vector(snapshot: Snapshot) -> tuple[str, ...]:
    source, bit = snapshot.content if snapshot.content is not None else ("-", "-")
    if snapshot.owed is None:
        owed_port, owed_kind, owed_args = "-", "-", "-"
    else:
        owed_port = snapshot.owed.port
        owed_kind = snapshot.owed.kind
        owed_args = ",".join(snapshot.owed.args)
    return (
        source,
        bit,
        snapshot.rule[0],
        snapshot.rule[1],
        snapshot.rule[2],
        _action_component(snapshot.action_k),
        _action_component(snapshot.action_l),
        owed_port,
        owed_kind,
        owed_args,
    )


def rebuild_rule_on_0_from_b1_specification() -> str:
    """B1 recipe: every admitted/default interpretation maps input 0 to 0."""

    return "0"


def rebuild_owed_port_from_kind(owed_kind: str) -> str:
    """B1 recipe: DO uses action; every other owed output uses client."""

    if owed_kind == "-":
        return "-"
    return ACTION if owed_kind == "DO" else CLIENT


@dataclass(frozen=True)
class DeletionSearch:
    sound_masks: tuple[int, ...]
    inclusion_minimal_masks: tuple[int, ...]
    first_conflict: Mapping[int, tuple[tuple[Frame, ...], tuple[Frame, ...]]]
    rows: int


def exhaustive_component_deletions(
    histories: Iterable[tuple[Frame, ...]],
    class_of: Callable[[Snapshot], object],
) -> DeletionSearch:
    """Try all 2^10 projections in the explicitly declared component grammar."""

    ordered = tuple(sorted(histories, key=history_order))
    rows_by_vector: dict[tuple[str, ...], tuple[object, tuple[Frame, ...]]] = {}
    for history in ordered:
        snapshot = replay(history)
        vector = component_vector(snapshot)
        value = class_of(snapshot)
        prior = rows_by_vector.get(vector)
        if prior is not None and prior[0] != value:
            raise AssertionError("full declared component vector is not sound")
        rows_by_vector.setdefault(vector, (value, history))

    width = len(COMPONENT_NAMES)
    sound: list[int] = []
    conflicts: dict[int, tuple[tuple[Frame, ...], tuple[Frame, ...]]] = {}
    for mask in range(1 << width):
        groups: dict[tuple[str, ...], tuple[object, tuple[Frame, ...]]] = {}
        conflict: Optional[tuple[tuple[Frame, ...], tuple[Frame, ...]]] = None
        for vector, (value, history) in rows_by_vector.items():
            projected = tuple(vector[i] for i in range(width) if mask & (1 << i))
            prior = groups.get(projected)
            if prior is None:
                groups[projected] = (value, history)
            elif prior[0] != value:
                conflict = (prior[1], history)
                break
        if conflict is None:
            sound.append(mask)
        else:
            conflicts[mask] = conflict

    sound_set = set(sound)
    minimal = []
    for mask in sound:
        proper = (mask - 1) & mask
        has_sound_subset = False
        while proper:
            if proper in sound_set:
                has_sound_subset = True
                break
            proper = (proper - 1) & mask
        if not has_sound_subset and (0 not in sound_set or mask == 0):
            minimal.append(mask)
    return DeletionSearch(tuple(sound), tuple(minimal), conflicts, len(rows_by_vector))


def mask_names(mask: int) -> tuple[str, ...]:
    return tuple(name for i, name in enumerate(COMPONENT_NAMES) if mask & (1 << i))


def levenshtein(left: tuple[Frame, ...], right: tuple[Frame, ...]) -> int:
    previous = list(range(len(right) + 1))
    for i, lframe in enumerate(left, 1):
        current = [i]
        for j, rframe in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (lframe != rframe),
                )
            )
        previous = current
    return previous[-1]


@dataclass(frozen=True)
class Witness:
    left: tuple[str, ...]
    right: tuple[str, ...]
    future: str
    left_proof_result: Observation
    right_proof_result: Observation
    score: tuple[object, ...]


def minimize_given_collision(
    left: tuple[Frame, ...],
    right: tuple[Frame, ...],
    residuals: BoundedResiduals,
) -> Optional[Witness]:
    """Deterministically orient a collision and minimize its bounded future."""

    if history_order(right) < history_order(left):
        left, right = right, left
    difference = residuals.first_difference(replay(left), replay(right))
    if difference is None:
        return None
    context, lobs, robs, divergence = difference
    score = (
        len(left) + len(right),
        levenshtein(left, right),
        context.depth,
        divergence,
        frame_tokens(left),
        frame_tokens(right),
        context.token(),
    )
    return Witness(
        frame_tokens(left),
        frame_tokens(right),
        context.token(),
        lobs,
        robs,
        score,
    )


def _projection(snapshot: Snapshot, mask: int) -> tuple[str, ...]:
    vector = component_vector(snapshot)
    return tuple(value for i, value in enumerate(vector) if mask & (1 << i))


def globally_minimize_deletion_collision(
    histories: Iterable[tuple[Frame, ...]],
    mask: int,
    residuals: BoundedResiduals,
) -> Optional[Witness]:
    """Exhaust the frozen witness order for one projection collision.

    Search stops only after every pair at the first possible total crossing
    count has been evaluated. This is tractable because direct component
    deletions in C0 acquire witnesses at very short histories.
    """

    by_length: dict[
        int,
        dict[tuple[str, ...], dict[int, list[tuple[Frame, ...]]]],
    ] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    max_length = 0
    for history in sorted(histories, key=history_order):
        length = len(history)
        max_length = max(max_length, length)
        snapshot = replay(history)
        projected = _projection(snapshot, mask)
        signature = residuals.class_id(snapshot)
        by_length[length][projected][signature].append(history)

    for total in range(2 * max_length + 1):
        best: Optional[Witness] = None
        for left_length in range(max_length + 1):
            right_length = total - left_length
            if right_length < left_length or right_length > max_length:
                continue
            left_groups = by_length.get(left_length, {})
            right_groups = by_length.get(right_length, {})
            for projected in sorted(set(left_groups) & set(right_groups)):
                lvalues = left_groups[projected]
                rvalues = right_groups[projected]
                for left_signature in sorted(lvalues):
                    for right_signature in sorted(rvalues):
                        if left_signature == right_signature:
                            continue
                        # Avoid considering both orientations when lengths match.
                        if left_length == right_length and right_signature < left_signature:
                            continue
                        for left in lvalues[left_signature]:
                            for right in rvalues[right_signature]:
                                witness = minimize_given_collision(left, right, residuals)
                                if witness is None:
                                    continue
                                if best is None or witness.score < best.score:
                                    best = witness
        if best is not None:
            return best
    return None


def direct_deletion_witnesses(
    histories: Iterable[tuple[Frame, ...]],
    search: DeletionSearch,
    residuals: BoundedResiduals,
) -> dict[str, Witness | str]:
    full = (1 << len(COMPONENT_NAMES)) - 1
    result: dict[str, Witness | str] = {}
    for index, name in enumerate(COMPONENT_NAMES):
        mask = full & ~(1 << index)
        collision = search.first_conflict.get(mask)
        if collision is None:
            if name in {"rule_on_0", "owed_port"}:
                result[name] = "MAY_REBUILD_BY_EXHAUSTIVELY_CHECKED_B1_RECIPE"
            else:
                result[name] = "NO_BOUNDED_COLLISION; CLASSIFICATION_UNRESOLVED"
            continue
        witness = globally_minimize_deletion_collision(histories, mask, residuals)
        result[name] = witness if witness is not None else "NO_BOUNDED_FUTURE_WITNESS"
    return result


def count_pair_merges(class_keys: Iterable[object]) -> int:
    """Every pair of distinct quotient classes is an unsound merge by construction."""

    count = len(set(class_keys))
    return count * (count - 1) // 2


def pair_merge_certificate(class_keys: Iterable[object]) -> tuple[int, str]:
    """Legacy branch-only digest used to cross-check all-pair coverage.

    This small digest is not the minimized-witness certificate. The latter is
    produced by :func:`minimized_pair_witness_certificate` and executes a
    separating context for every pair.
    """

    keys = tuple(sorted(set(class_keys)))
    digest = hashlib.sha256()
    count = 0
    for left_index, left in enumerate(keys):
        for right in keys[left_index + 1 :]:
            if left == right:
                raise AssertionError("pair enumerator received duplicate class")
            digest.update(repr((left, right)).encode("utf-8"))
            digest.update(b"\n")
            count += 1
    expected = len(keys) * (len(keys) - 1) // 2
    if count != expected:
        raise AssertionError("pair merge enumeration is incomplete")
    return count, digest.hexdigest()


@dataclass(frozen=True)
class PairWitnessCertificate:
    pair_count: int
    sha256: str
    winning_context_map_sha256: str
    winning_context_map_raw_bytes: int
    winning_context_map_zlib_bytes: int
    winning_context_map_zlib_base64: str
    depth_counts: Mapping[int, int]
    active_vertices_by_depth: Mapping[int, int]
    winning_contexts: int
    pair_context_comparisons: int
    maximum_minimum_length_histories_per_class: int
    total_minimum_length_histories_retained: int
    history_selection: str
    tie_break: str


def _length_prefixed(data: bytes) -> bytes:
    return len(data).to_bytes(8, "big") + data


def _proof_result_record(proof_result: Observation) -> bytes:
    fields = (
        proof_result.domain_membership,
        proof_result.client,
        proof_result.action,
    )
    result = len(fields).to_bytes(4, "big")
    for field in fields:
        result += len(field).to_bytes(4, "big")
        for value in field:
            result += _length_prefixed(value.encode("utf-8"))
    return result


def _history_pair(
    left: tuple[tuple[Frame, ...], ...],
    right: tuple[tuple[Frame, ...], ...],
) -> tuple[tuple[Frame, ...], tuple[Frame, ...]]:
    best: Optional[
        tuple[tuple[object, ...], tuple[Frame, ...], tuple[Frame, ...]]
    ] = None
    left_minimum = len(left[0])
    right_minimum = len(right[0])
    # A longer member cannot win the primary total-crossing criterion.
    for left_history in left:
        if len(left_history) != left_minimum:
            continue
        for right_history in right:
            if len(right_history) != right_minimum:
                continue
            score = (
                len(left_history) + len(right_history),
                levenshtein(left_history, right_history),
                frame_tokens(left_history),
                frame_tokens(right_history),
            )
            candidate = (score, left_history, right_history)
            if best is None or score < best[0]:
                best = candidate
    assert best is not None
    return best[1], best[2]


def minimized_pair_witness_certificate(
    histories: Iterable[tuple[Frame, ...]],
    class_of: Callable[[Snapshot], object],
    contexts: tuple[Context, ...],
) -> PairWitnessCertificate:
    """Execute and hash a minimized bounded witness for every quotient pair.

    Context minimization is exact over the supplied contexts: earliest inbound
    depth, then ``Observation.flattened`` divergence index, then context token.
    Histories are selected separately and exactly over the corpus: retain every
    history at each class's minimum crossing length, then minimize Levenshtein
    distance and the two lexical frame-token tuples. Total crossings is included
    in the certificate score even though it is constant over those retained
    candidates.
    """

    grouped: dict[object, list[tuple[Frame, ...]]] = defaultdict(list)
    for history in sorted(histories, key=history_order):
        grouped[class_of(replay(history))].append(history)
    class_keys = tuple(sorted(grouped))
    class_histories = tuple(
        tuple(
            history
            for history in grouped[key]
            if len(history) == len(grouped[key][0])
        )
        for key in class_keys
    )
    if any(not values for values in class_histories):
        raise AssertionError("each corpus class must retain a minimum-length history")
    maximum_minimum_length_histories = max(map(len, class_histories), default=0)
    total_minimum_length_histories = sum(map(len, class_histories))
    snapshots = tuple(replay(values[0]) for values in class_histories)

    observation_ids: dict[Observation, int] = {}
    observations: list[Observation] = []
    rows: list[array] = []
    for context in contexts:
        row = array("H")
        for snapshot in snapshots:
            observation = evaluate_context(snapshot, context)
            identifier = observation_ids.get(observation)
            if identifier is None:
                identifier = len(observations)
                if identifier >= 1 << 16:
                    raise AssertionError("Observation-id row exceeds uint16")
                observation_ids[observation] = identifier
                observations.append(observation)
            row.append(identifier)
        rows.append(row)

    contexts_by_depth: dict[int, tuple[int, ...]] = {}
    for depth in sorted({context.depth for context in contexts}):
        contexts_by_depth[depth] = tuple(
            index for index, context in enumerate(contexts) if context.depth == depth
        )

    digest = hashlib.sha256()
    winning_map = array("H")
    depth_counts: dict[int, int] = defaultdict(int)
    active_vertices: dict[int, set[int]] = defaultdict(set)
    used_contexts: set[int] = set()
    comparisons = 0
    pair_count = 0

    for left_index in range(len(class_keys)):
        for right_index in range(left_index + 1, len(class_keys)):
            winner: Optional[
                tuple[tuple[int, str], int, Observation, Observation, int]
            ] = None
            winning_depth: Optional[int] = None
            for depth, context_indices in contexts_by_depth.items():
                # "Active" means this pair reached this depth after every
                # shallower context failed, whether it wins here or later.
                active_vertices[depth].update((left_index, right_index))
                same_depth: Optional[
                    tuple[tuple[int, str], int, Observation, Observation, int]
                ] = None
                for context_index in context_indices:
                    comparisons += 1
                    left_id = rows[context_index][left_index]
                    right_id = rows[context_index][right_index]
                    if left_id == right_id:
                        continue
                    left_observation = observations[left_id]
                    right_observation = observations[right_id]
                    divergence = first_divergence(left_observation, right_observation)
                    context = contexts[context_index]
                    score = (divergence, context.token())
                    candidate = (
                        score,
                        context_index,
                        left_observation,
                        right_observation,
                        divergence,
                    )
                    if same_depth is None or score < same_depth[0]:
                        same_depth = candidate
                if same_depth is not None:
                    winner = same_depth
                    winning_depth = depth
                    break
            if winner is None or winning_depth is None:
                raise AssertionError("distinct quotient pair lacks a bounded separator")

            _score, context_index, left_observation, right_observation, divergence = winner
            if left_observation == right_observation:
                raise AssertionError("winning context does not separate its pair")
            winning_map.append(context_index)
            depth_counts[winning_depth] += 1
            used_contexts.add(context_index)

            left_history, right_history = _history_pair(
                class_histories[left_index], class_histories[right_index]
            )
            context = contexts[context_index]
            record = b"".join(
                (
                    left_index.to_bytes(4, "big"),
                    right_index.to_bytes(4, "big"),
                    _length_prefixed(repr(class_keys[left_index]).encode("utf-8")),
                    _length_prefixed(repr(class_keys[right_index]).encode("utf-8")),
                    _length_prefixed(repr(frame_tokens(left_history)).encode("utf-8")),
                    _length_prefixed(repr(frame_tokens(right_history)).encode("utf-8")),
                    winning_depth.to_bytes(4, "big"),
                    divergence.to_bytes(4, "big"),
                    _length_prefixed(context.token().encode("utf-8")),
                    _length_prefixed(_proof_result_record(left_observation)),
                    _length_prefixed(_proof_result_record(right_observation)),
                )
            )
            digest.update(_length_prefixed(record))
            pair_count += 1

    expected_pairs = len(class_keys) * (len(class_keys) - 1) // 2
    if pair_count != expected_pairs or len(winning_map) != expected_pairs:
        raise AssertionError("not every quotient pair received one witness")

    # Canonicalize the uint16 map as network byte order before hashing.
    canonical_map = array("H", winning_map)
    import sys

    if sys.byteorder == "little":
        canonical_map.byteswap()
    map_bytes = canonical_map.tobytes()
    compressed_map = zlib.compress(map_bytes, level=9)
    return PairWitnessCertificate(
        pair_count=pair_count,
        sha256=digest.hexdigest(),
        winning_context_map_sha256=hashlib.sha256(map_bytes).hexdigest(),
        winning_context_map_raw_bytes=len(map_bytes),
        winning_context_map_zlib_bytes=len(compressed_map),
        winning_context_map_zlib_base64=base64.b64encode(compressed_map).decode("ascii"),
        depth_counts=dict(sorted(depth_counts.items())),
        active_vertices_by_depth={
            depth: len(vertices) for depth, vertices in sorted(active_vertices.items())
        },
        winning_contexts=len(used_contexts),
        pair_context_comparisons=comparisons,
        maximum_minimum_length_histories_per_class=(
            maximum_minimum_length_histories
        ),
        total_minimum_length_histories_retained=total_minimum_length_histories,
        history_selection=(
            "per class retain every corpus history at that class's minimum crossing length; "
            "per pair exhaustively minimize total crossings, Levenshtein distance, left "
            "tokens, right tokens"
        ),
        tie_break=(
            "earliest inbound depth; then first differing Observation.flattened coordinate "
            "(proof-domain tuple, client tuple, action tuple; not temporal); then context token"
        ),
    )


def corpus_class_representatives(
    histories: Iterable[tuple[Frame, ...]],
    class_of: Callable[[Snapshot], object],
) -> dict[object, tuple[Frame, ...]]:
    result: dict[object, tuple[Frame, ...]] = {}
    for history in sorted(histories, key=history_order):
        result.setdefault(class_of(replay(history)), history)
    return result


def summarize_history(history: tuple[Frame, ...]) -> str:
    return history_token(history) or "<empty>"
