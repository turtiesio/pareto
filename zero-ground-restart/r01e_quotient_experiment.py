#!/usr/bin/env python3
"""External, nonauthorizing exhaustive experiment for frozen R0.1E.

This program deliberately has no repository dependencies.  Its only input is
the frozen specification adjacent to this file, whose digest is checked before
any experiment is run.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import deque
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable, Iterable, Optional


SPEC_NAME = "REALIZATION-CORRECTION-R01E.md"
SPEC_SHA256 = "a4c081623ccf9419ff19f3f842fff47e8631504940ee0c44038809198a15d2bf"
U = (0, 1)
UNDEFINED = 2
POLICY = frozenset(((0, 0), (0, 1), (1, 1)))

OFF = 1 << 0
RUN_MISSING = 1 << 1
AUTH_DISAGREES = 1 << 2
CHANNEL_MISSING = 1 << 3
RUN_DISAGREES = 1 << 4
POLICY_DENIES = 1 << 5
FULL = 1 << 6
FINAL_EPOCH = 1 << 7
ALREADY_UP = 1 << 8

OK = b"\x20"


class ContractError(ValueError):
    """A byte string or state violates the frozen contract."""


class IllegalCrossing(ContractError):
    """A crossing is not legal from the supplied state."""


def fail_closed_digest() -> str:
    path = Path(__file__).resolve().with_name(SPEC_NAME)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise SystemExit(f"R01E contract unavailable: {exc}") from exc
    actual = hashlib.sha256(data).hexdigest()
    if actual != SPEC_SHA256:
        raise SystemExit(
            f"R01E contract SHA-256 mismatch: expected {SPEC_SHA256}, got {actual}"
        )
    return actual


def val_frame(word: tuple[int, ...]) -> bytes:
    if len(word) > 2 or any(bit not in U for bit in word):
        raise ContractError("invalid VAL word")
    return bytes((0x21, len(word), *word))


def rej_frame(mask: int) -> bytes:
    if not 0 < mask <= 0x1FF:
        raise ContractError("invalid rejection bit range")
    return bytes((0x22, mask >> 8, mask & 0xFF))


def encode_input(opcode: int, *args: int) -> bytes:
    expected = {0x10: 3, 0x11: 4, 0x12: 3, 0x13: 0, 0x14: 0, 0x15: 0}
    if opcode not in expected or len(args) != expected[opcode]:
        raise ContractError("unknown input opcode or wrong arity")
    if any(value not in U for value in args):
        raise ContractError("input metavariables are exact bits")
    return bytes((opcode, *args))


def decode_input(frame: bytes) -> tuple[int, tuple[int, ...]]:
    if not isinstance(frame, bytes) or not frame:
        raise ContractError("input frame must be nonempty bytes")
    expected = {0x10: 3, 0x11: 4, 0x12: 3, 0x13: 0, 0x14: 0, 0x15: 0}
    opcode = frame[0]
    if opcode not in expected or len(frame) != expected[opcode] + 1:
        raise ContractError("unknown input frame or noncanonical length")
    args = tuple(frame[1:])
    if any(value not in U for value in args):
        raise ContractError("input metavariables are exact bits")
    return opcode, args


def all_input_frames() -> tuple[bytes, ...]:
    frames: list[bytes] = []
    frames.extend(encode_input(0x10, *args) for args in itertools.product(U, repeat=3))
    frames.extend(encode_input(0x11, *args) for args in itertools.product(U, repeat=4))
    frames.extend(encode_input(0x12, *args) for args in itertools.product(U, repeat=3))
    frames.extend((encode_input(0x13), encode_input(0x14), encode_input(0x15)))
    return tuple(sorted(frames))


INPUT_FRAMES = all_input_frames()


@dataclass(frozen=True, order=True)
class State:
    u: int
    e: int
    rho: tuple[Optional[int], Optional[int]]
    kappa: tuple[Optional[int], Optional[int]]
    omega: tuple[Optional[tuple[int, ...]], Optional[tuple[int, ...]]]
    pending: Optional[bytes] = None


INITIAL_STATE = State(1, 0, (None, None), (None, None), (None, None), None)


def validate_state_shape(state: State) -> None:
    if state.u not in U or state.e not in U:
        raise ContractError("u and e must be bits")
    if len(state.rho) != 2 or any(value not in (None, 0, 1) for value in state.rho):
        raise ContractError("invalid rho")
    if len(state.kappa) != 2 or any(value not in (None, 0, 1) for value in state.kappa):
        raise ContractError("invalid kappa")
    if len(state.omega) != 2:
        raise ContractError("invalid omega arity")
    domain_rho = {index for index, value in enumerate(state.rho) if value is not None}
    image_kappa = {value for value in state.kappa if value is not None}
    if domain_rho != image_kappa:
        raise ContractError("domain(rho) must equal image(kappa)")
    for channel in U:
        run = state.kappa[channel]
        word = state.omega[channel]
        if (run is None) != (word is None):
            raise ContractError("omega must be defined exactly for bound channels")
        if word is None:
            continue
        if len(word) > 2 or any(bit not in U for bit in word):
            raise ContractError("invalid omega word")
        assert run is not None
        authority = state.rho[run]
        if authority == 1 and word not in ((), (1,), (1, 1)):
            raise ContractError("omega violates immutable policy")


class Codec:
    def __init__(self, legal_rejection_masks: Iterable[int]):
        self.legal_rejection_masks = frozenset(legal_rejection_masks)

    def decode_output(self, frame: bytes) -> tuple[str, object]:
        if not isinstance(frame, bytes) or not frame:
            raise ContractError("output frame must be nonempty bytes")
        if frame == OK:
            return "OK", None
        if frame[0] == 0x21:
            if len(frame) < 2 or frame[1] not in (0, 1, 2) or len(frame) != frame[1] + 2:
                raise ContractError("noncanonical VAL length")
            word = tuple(frame[2:])
            if any(bit not in U for bit in word):
                raise ContractError("VAL octets must be bits")
            return "VAL", word
        if frame[0] == 0x22:
            if len(frame) != 3:
                raise ContractError("noncanonical REJ length")
            mask = (frame[1] << 8) | frame[2]
            if mask not in self.legal_rejection_masks:
                raise ContractError("impossible rejection mask")
            return "REJ", mask
        raise ContractError("unknown output frame")

    def encode_state(self, state: State) -> bytes:
        validate_state_shape(state)
        result = bytearray(19)
        result[0] = 0x5A
        result[1] = state.u
        result[2] = state.e
        result[3:5] = bytes(UNDEFINED if value is None else value for value in state.rho)
        result[5:7] = bytes(UNDEFINED if value is None else value for value in state.kappa)
        for channel, length_offset, bits_offset in ((0, 7, 8), (1, 10, 11)):
            word = state.omega[channel]
            if word is None:
                result[length_offset] = 3
            else:
                result[length_offset] = len(word)
                result[bits_offset : bits_offset + len(word)] = bytes(word)
        if state.pending is not None:
            kind, payload = self.decode_output(state.pending)
            if kind == "OK":
                result[13] = 1
            elif kind == "VAL":
                word = payload
                assert isinstance(word, tuple)
                result[13] = 2
                result[14] = len(word)
                result[15 : 15 + len(word)] = bytes(word)
            else:
                mask = payload
                assert isinstance(mask, int)
                result[13] = 3
                result[17] = mask >> 8
                result[18] = mask & 0xFF
        encoded = bytes(result)
        if self.decode_state(encoded) != state:
            raise AssertionError("canonical state codec failed its own round trip")
        return encoded

    def decode_state(self, encoded: bytes) -> State:
        if not isinstance(encoded, bytes) or len(encoded) != 19 or encoded[0] != 0x5A:
            raise ContractError("wrong canonical export marker or length")
        if encoded[1] not in U or encoded[2] not in U:
            raise ContractError("non-bit u or e")
        if any(value not in (0, 1, UNDEFINED) for value in encoded[3:7]):
            raise ContractError("noncanonical association octet")
        rho = tuple(None if value == UNDEFINED else value for value in encoded[3:5])
        kappa = tuple(None if value == UNDEFINED else value for value in encoded[5:7])
        words: list[Optional[tuple[int, ...]]] = []
        for length_offset, bits_offset in ((7, 8), (10, 11)):
            length = encoded[length_offset]
            raw_bits = encoded[bits_offset : bits_offset + 2]
            if length not in (0, 1, 2, 3):
                raise ContractError("invalid omega length")
            if length == 3:
                if raw_bits != b"\x00\x00":
                    raise ContractError("undefined omega has nonzero padding")
                words.append(None)
            else:
                if any(bit not in U for bit in raw_bits[:length]):
                    raise ContractError("omega octets must be bits")
                if any(raw_bits[length:]):
                    raise ContractError("omega has nonzero padding")
                words.append(tuple(raw_bits[:length]))
        tag = encoded[13]
        if tag == 0:
            if any(encoded[14:19]):
                raise ContractError("none pending tag has payload")
            pending = None
        elif tag == 1:
            if any(encoded[14:19]):
                raise ContractError("OK pending tag has payload")
            pending = OK
        elif tag == 2:
            length = encoded[14]
            if length not in (0, 1, 2):
                raise ContractError("invalid pending VAL length")
            raw_bits = encoded[15:17]
            if any(bit not in U for bit in raw_bits[:length]) or any(raw_bits[length:]):
                raise ContractError("invalid pending VAL bits or padding")
            if any(encoded[17:19]):
                raise ContractError("pending VAL has REJ payload")
            pending = val_frame(tuple(raw_bits[:length]))
        elif tag == 3:
            if any(encoded[14:17]):
                raise ContractError("pending REJ has VAL payload")
            pending = bytes((0x22, encoded[17], encoded[18]))
            self.decode_output(pending)
        else:
            raise ContractError("unknown pending tag")
        state = State(encoded[1], encoded[2], rho, kappa, tuple(words), pending)  # type: ignore[arg-type]
        validate_state_shape(state)
        if pending is not None:
            self.decode_output(pending)
        return state


def association_mask(state: State, a: int, r: int, c: int) -> int:
    mask = 0
    if state.rho[r] is None:
        mask |= RUN_MISSING
    elif state.rho[r] != a:
        mask |= AUTH_DISAGREES
    if state.kappa[c] is None:
        mask |= CHANNEL_MISSING
    elif state.kappa[c] != r:
        mask |= RUN_DISAGREES
    return mask


def reference_input(state: State, frame: bytes) -> State:
    if state.pending is not None:
        raise IllegalCrossing("input while output is pending")
    opcode, args = decode_input(frame)
    if opcode == 0x14:
        return replace(state, u=0)
    if opcode == 0x15:
        if state.u == 0:
            return replace(state, u=1, pending=OK)
        return replace(state, pending=rej_frame(ALREADY_UP))
    if state.u == 0:
        return replace(state, pending=rej_frame(OFF))
    if opcode == 0x10:
        a, r, c = args
        mask = 0
        if state.rho[r] is not None and state.rho[r] != a:
            mask |= AUTH_DISAGREES
        if state.kappa[c] is not None and state.kappa[c] != r:
            mask |= RUN_DISAGREES
        if mask:
            return replace(state, pending=rej_frame(mask))
        rho = list(state.rho)
        kappa = list(state.kappa)
        omega = list(state.omega)
        if rho[r] is None:
            rho[r] = a
        if kappa[c] is None:
            kappa[c] = r
            omega[c] = ()
        result = State(state.u, state.e, tuple(rho), tuple(kappa), tuple(omega), OK)
    elif opcode == 0x11:
        a, r, c, x = args
        mask = association_mask(state, a, r, c)
        if (a, x) not in POLICY:
            mask |= POLICY_DENIES
        if association_mask(state, a, r, c) == 0:
            word = state.omega[c]
            assert word is not None
            if len(word) == 2:
                mask |= FULL
        if mask:
            return replace(state, pending=rej_frame(mask))
        omega = list(state.omega)
        word = omega[c]
        assert word is not None
        omega[c] = word + (x,)
        result = State(state.u, state.e, state.rho, state.kappa, tuple(omega), OK)
    elif opcode == 0x12:
        a, r, c = args
        mask = association_mask(state, a, r, c)
        if mask:
            return replace(state, pending=rej_frame(mask))
        word = state.omega[c]
        assert word is not None
        result = replace(state, pending=val_frame(word))
    elif opcode == 0x13:
        if state.e == 1:
            return replace(state, pending=rej_frame(FINAL_EPOCH))
        result = replace(state, e=1, pending=OK)
    else:  # decode_input makes this unreachable.
        raise AssertionError("unhandled input")
    validate_state_shape(result)
    return result


@dataclass(frozen=True, order=True)
class Crossing:
    direction: str
    frame: bytes

    def as_json(self) -> dict[str, str]:
        return {"direction": self.direction, "frame_hex": self.frame.hex()}


def reference_crossing(state: State, crossing: Crossing) -> State:
    if crossing.direction == "input":
        return reference_input(state, crossing.frame)
    if crossing.direction != "output":
        raise IllegalCrossing("unknown crossing direction")
    if state.pending is None or crossing.frame != state.pending:
        raise IllegalCrossing("wrong or unsolicited output")
    return replace(state, pending=None)


@dataclass
class Graph:
    states: list[State]
    parents: list[Optional[tuple[int, Crossing]]]
    successors: list[dict[Crossing, int]]
    labels: tuple[Crossing, ...]
    outputs: tuple[bytes, ...]


def enumerate_graph() -> Graph:
    states = [INITIAL_STATE]
    parents: list[Optional[tuple[int, Crossing]]] = [None]
    successors: list[dict[Crossing, int]] = []
    state_ids = {INITIAL_STATE: 0}
    queue = deque((0,))
    observed_outputs: set[bytes] = set()
    while queue:
        state_id = queue.popleft()
        state = states[state_id]
        edges: dict[Crossing, int] = {}
        crossings = (
            tuple(Crossing("input", frame) for frame in INPUT_FRAMES)
            if state.pending is None
            else (Crossing("output", state.pending),)
        )
        for crossing in crossings:
            target = reference_crossing(state, crossing)
            if target.pending is not None:
                observed_outputs.add(target.pending)
            target_id = state_ids.get(target)
            if target_id is None:
                target_id = len(states)
                state_ids[target] = target_id
                states.append(target)
                parents.append((state_id, crossing))
                queue.append(target_id)
            edges[crossing] = target_id
        successors.append(edges)
    outputs = tuple(sorted(observed_outputs))
    labels = tuple(
        sorted(
            tuple(Crossing("input", frame) for frame in INPUT_FRAMES)
            + tuple(Crossing("output", frame) for frame in outputs)
        )
    )
    return Graph(states, parents, successors, labels, outputs)


def refine_partition(graph: Graph) -> tuple[list[int], int]:
    label_index = {label: index for index, label in enumerate(graph.labels)}
    rows: list[dict[int, int]] = [
        {label_index[label]: target for label, target in edges.items()}
        for edges in graph.successors
    ]
    classes = [0] * len(graph.states)
    rounds = 0
    while True:
        signatures = [
            tuple(classes[row[index]] if index in row else -1 for index in range(len(graph.labels)))
            for row in rows
        ]
        ordered = {signature: index for index, signature in enumerate(sorted(set(signatures)))}
        updated = [ordered[signature] for signature in signatures]
        rounds += 1
        if updated == classes:
            return classes, rounds
        classes = updated


def history(graph: Graph, state_id: int) -> list[Crossing]:
    result: list[Crossing] = []
    while graph.parents[state_id] is not None:
        parent_id, crossing = graph.parents[state_id]  # type: ignore[misc]
        result.append(crossing)
        state_id = parent_id
    result.reverse()
    return result


def shortest_distinguishing_suffix(
    graph: Graph, classes: list[int], left: int, right: int
) -> list[Crossing]:
    if classes[left] == classes[right]:
        raise ValueError("equivalent states have no distinguishing suffix")
    start = (left, right)
    queue = deque((start,))
    previous: dict[tuple[int, int], Optional[tuple[tuple[int, int], Crossing]]] = {start: None}
    while queue:
        pair = queue.popleft()
        left_edges = graph.successors[pair[0]]
        right_edges = graph.successors[pair[1]]
        for label in graph.labels:
            left_target = left_edges.get(label)
            right_target = right_edges.get(label)
            if (left_target is None) != (right_target is None):
                prefix: list[Crossing] = [label]
                cursor = pair
                while previous[cursor] is not None:
                    prior, prior_label = previous[cursor]  # type: ignore[misc]
                    prefix.append(prior_label)
                    cursor = prior
                prefix.reverse()
                return prefix
            if left_target is None or right_target is None:
                continue
            if classes[left_target] == classes[right_target]:
                continue
            next_pair = (left_target, right_target)
            if next_pair not in previous:
                previous[next_pair] = (pair, label)
                queue.append(next_pair)
    raise AssertionError("refinement separated a pair without a distinguishing suffix")


COMPONENTS: tuple[tuple[str, slice], ...] = (
    ("lifecycle_u", slice(1, 2)),
    ("epoch_e", slice(2, 3)),
    ("rho_0", slice(3, 4)),
    ("rho_1", slice(4, 5)),
    ("kappa_0", slice(5, 6)),
    ("kappa_1", slice(6, 7)),
    ("omega_0", slice(7, 10)),
    ("omega_1", slice(10, 13)),
    ("pending_tag", slice(13, 14)),
    ("pending_val", slice(14, 17)),
    ("pending_rej", slice(17, 19)),
)


def projection_collision(
    vectors: list[tuple[bytes, ...]], classes: list[int], retained_mask: int
) -> Optional[tuple[int, int]]:
    retained = tuple(index for index in range(len(COMPONENTS)) if retained_mask & (1 << index))
    seen: dict[tuple[bytes, ...], tuple[int, int]] = {}
    for state_id, vector in enumerate(vectors):
        key = tuple(vector[index] for index in retained)
        prior = seen.get(key)
        if prior is None:
            seen[key] = (classes[state_id], state_id)
        elif prior[0] != classes[state_id]:
            return prior[1], state_id
    return None


def deletion_family(
    vectors: list[tuple[bytes, ...]], classes: list[int]
) -> tuple[list[int], dict[int, tuple[int, int]], int]:
    full = (1 << len(COMPONENTS)) - 1
    tested = {
        mask: projection_collision(vectors, classes, mask)
        for mask in range(full + 1)
    }
    sound = {mask for mask, collision in tested.items() if collision is None}
    minimal = {
        mask
        for mask in sound
        if all(
            (mask & ~(1 << index)) not in sound
            for index in range(len(COMPONENTS))
            if mask & (1 << index)
        )
    }
    boundary = {
        mask: collision
        for mask, collision in tested.items()
        if collision is not None
        and any(
            (mask | (1 << index)) in sound
            for index in range(len(COMPONENTS))
            if not (mask & (1 << index))
        )
    }
    return sorted(minimal), boundary, len(sound)


def state_components(codec: Codec, states: list[State]) -> tuple[list[bytes], list[tuple[bytes, ...]]]:
    exports = [codec.encode_state(state) for state in states]
    vectors = [tuple(encoded[part] for _, part in COMPONENTS) for encoded in exports]
    return exports, vectors


def reconstruct_one_kappa_coordinate(
    states: list[State], exports: list[bytes]
) -> dict[str, object]:
    """Execute the constructor licensed by either sound one-kappa deletion."""

    checks = 0
    per_coordinate: dict[str, int] = {}
    for omitted_channel in U:
        offset = 5 + omitted_channel
        coordinate_checks = 0
        other_channel = 1 - omitted_channel
        for state, original in zip(states, exports):
            retained = bytearray(original)
            retained[offset] = 0xFF
            if state.omega[omitted_channel] is None:
                rebuilt = UNDEFINED
            else:
                domain = [run for run in U if state.rho[run] is not None]
                if len(domain) == 1:
                    rebuilt = domain[0]
                elif len(domain) == 2:
                    other = state.kappa[other_channel]
                    if state.omega[other_channel] is None or other not in U:
                        raise AssertionError("two-run kappa reconstruction lost its other channel")
                    rebuilt = 1 - other
                else:
                    raise AssertionError("defined omega has no reconstructible kappa endpoint")
            retained[offset] = rebuilt
            if bytes(retained) != original:
                raise AssertionError("one-coordinate kappa reconstruction changed export bytes")
            coordinate_checks += 1
            checks += 1
        per_coordinate[f"kappa_{omitted_channel}"] = coordinate_checks
    return {
        "rules": [
            "undefined omega(c) reconstructs undefined kappa(c)",
            "with one rho-domain endpoint, a defined channel names that endpoint",
            "with two rho-domain endpoints, both channels are defined and bijective, so the omitted endpoint is the complement of the retained channel endpoint",
        ],
        "coordinates_checked": per_coordinate,
        "executed_checks": checks,
        "all_reconstructed_exports_byte_equal": True,
    }


def merge_key(name: str, vector: tuple[bytes, ...]) -> tuple[bytes, ...]:
    values = list(vector)
    if name == "rho_endpoint_bag":
        values[2:4] = sorted(values[2:4])
    elif name == "kappa_endpoint_bag":
        values[4:6] = sorted(values[4:6])
    elif name == "omega_channel_bag":
        values[6:8] = sorted(values[6:8])
    elif name == "omega_bit_bag":
        for index in (6, 7):
            raw = values[index]
            length = raw[0]
            if length in (0, 1, 2):
                values[index] = bytes((length, *sorted(raw[1 : 1 + length]), *([0] * (2 - length))))
    elif name == "pending_kind_only":
        values[9] = b""
        values[10] = b""
    elif name == "generic_rejection":
        if values[8] == b"\x03":
            values[10] = b""
    elif name == "value_length_only":
        if values[8] == b"\x02":
            values[9] = values[9][:1]
    elif name == "lifecycle_epoch_or":
        merged = bytes((values[0][0] | values[1][0],))
        values[0] = merged
        values[1] = b""
    else:
        raise ValueError(name)
    return tuple(values)


def arbitrary_key_collision(
    vectors: list[tuple[bytes, ...]], classes: list[int], key: Callable[[tuple[bytes, ...]], object]
) -> Optional[tuple[int, int]]:
    seen: dict[object, tuple[int, int]] = {}
    for state_id, vector in enumerate(vectors):
        projected = key(vector)
        prior = seen.get(projected)
        if prior is None:
            seen[projected] = (classes[state_id], state_id)
        elif prior[0] != classes[state_id]:
            return prior[1], state_id
    return None


def pending_cell_encode(pending: Optional[bytes]) -> bytes:
    if pending is None:
        return b"\x00\x00\x00\x00\x00"
    if len(pending) > 4:
        raise ContractError("pending frame does not fit fixed cell")
    return bytes((len(pending),)) + pending + bytes(4 - len(pending))


def pending_cell_decode(cell: bytes, codec: Codec) -> Optional[bytes]:
    if len(cell) != 5 or cell[0] > 4:
        raise ContractError("invalid fixed pending cell")
    length = cell[0]
    if any(cell[1 + length :]):
        raise ContractError("nonzero fixed-cell padding")
    if length == 0:
        return None
    pending = cell[1 : 1 + length]
    codec.decode_output(pending)
    return pending


def folded_log_encode(u: int, entries: tuple[bytes, ...], pending: Optional[bytes]) -> bytes:
    if u not in U or len(entries) > 7:
        raise ContractError("invalid folded-log header")
    for entry in entries:
        opcode, _ = decode_input(entry)
        if opcode not in (0x10, 0x11, 0x13):
            raise ContractError("nonmutation in folded log")
    return b"\x4c" + bytes((u, len(entries))) + b"".join(entries) + pending_cell_encode(pending)


def folded_log_decode(durable: bytes, codec: Codec) -> tuple[State, tuple[bytes, ...]]:
    if not isinstance(durable, bytes) or len(durable) < 8 or durable[0] != 0x4C:
        raise ContractError("invalid folded-log marker or length")
    u, count = durable[1], durable[2]
    if u not in U or count > 7:
        raise ContractError("invalid folded-log header")
    offset = 3
    entries: list[bytes] = []
    lengths = {0x10: 4, 0x11: 5, 0x13: 1}
    for _ in range(count):
        if offset >= len(durable) - 5 or durable[offset] not in lengths:
            raise ContractError("truncated or invalid mutation log")
        length = lengths[durable[offset]]
        if offset + length > len(durable) - 5:
            raise ContractError("truncated mutation entry")
        entry = durable[offset : offset + length]
        decode_input(entry)
        entries.append(entry)
        offset += length
    if offset != len(durable) - 5:
        raise ContractError("trailing folded-log bytes")
    if sum(entry[0] == 0x10 for entry in entries) > 2:
        raise ContractError("too many state-changing B entries")
    if sum(entry[0] == 0x11 for entry in entries) > 4:
        raise ContractError("too many successful A entries")
    if sum(entry[0] == 0x13 for entry in entries) > 1:
        raise ContractError("too many successful E entries")
    state = INITIAL_STATE
    for entry in entries:
        opcode, args = decode_input(entry)
        if opcode == 0x10:
            a, r, c = args
            mismatch = (
                (state.rho[r] is not None and state.rho[r] != a)
                or (state.kappa[c] is not None and state.kappa[c] != r)
            )
            if mismatch or state.kappa[c] is not None:
                raise ContractError("logged B was not an accepted mutation")
            rho = list(state.rho)
            kappa = list(state.kappa)
            omega = list(state.omega)
            if rho[r] is None:
                rho[r] = a
            kappa[c] = r
            omega[c] = ()
            state = State(1, state.e, tuple(rho), tuple(kappa), tuple(omega), None)
        elif opcode == 0x11:
            a, r, c, x = args
            if (
                state.rho[r] != a
                or state.kappa[c] != r
                or (a, x) not in POLICY
                or state.omega[c] is None
                or len(state.omega[c]) == 2
            ):
                raise ContractError("logged A was not an accepted mutation")
            omega = list(state.omega)
            assert omega[c] is not None
            omega[c] = omega[c] + (x,)
            state = State(1, state.e, state.rho, state.kappa, tuple(omega), None)
        else:
            if state.e:
                raise ContractError("duplicate successful E")
            state = replace(state, e=1)
    pending = pending_cell_decode(durable[-5:], codec)
    state = replace(state, u=u, pending=pending)
    validate_state_shape(state)
    return state, tuple(entries)


def folded_log_input(
    state: State, entries: tuple[bytes, ...], frame: bytes
) -> tuple[State, tuple[bytes, ...]]:
    """A second, log-oriented implementation of the input rules."""
    if state.pending is not None:
        raise IllegalCrossing("log adapter input while pending")
    opcode, args = decode_input(frame)
    updated_entries = entries
    if opcode == 0x14:
        return replace(state, u=0), updated_entries
    if opcode == 0x15:
        if state.u:
            return replace(state, pending=rej_frame(ALREADY_UP)), updated_entries
        return replace(state, u=1, pending=OK), updated_entries
    if not state.u:
        return replace(state, pending=rej_frame(OFF)), updated_entries
    if opcode == 0x10:
        a, r, c = args
        bits = 0
        if state.rho[r] is not None and state.rho[r] != a:
            bits |= AUTH_DISAGREES
        if state.kappa[c] is not None and state.kappa[c] != r:
            bits |= RUN_DISAGREES
        if bits:
            return replace(state, pending=rej_frame(bits)), updated_entries
        if state.kappa[c] is None:
            updated_entries += (frame,)
            rho = list(state.rho)
            kappa = list(state.kappa)
            omega = list(state.omega)
            if rho[r] is None:
                rho[r] = a
            kappa[c] = r
            omega[c] = ()
            state = State(1, state.e, tuple(rho), tuple(kappa), tuple(omega), None)
        return replace(state, pending=OK), updated_entries
    if opcode == 0x11:
        a, r, c, x = args
        bits = 0
        if state.rho[r] is None:
            bits |= RUN_MISSING
        elif state.rho[r] != a:
            bits |= AUTH_DISAGREES
        if state.kappa[c] is None:
            bits |= CHANNEL_MISSING
        elif state.kappa[c] != r:
            bits |= RUN_DISAGREES
        if (a, x) not in POLICY:
            bits |= POLICY_DENIES
        exact = state.rho[r] == a and state.kappa[c] == r
        if exact:
            assert state.omega[c] is not None
            if len(state.omega[c]) == 2:
                bits |= FULL
        if bits:
            return replace(state, pending=rej_frame(bits)), updated_entries
        updated_entries += (frame,)
        omega = list(state.omega)
        assert omega[c] is not None
        omega[c] = omega[c] + (x,)
        return State(1, state.e, state.rho, state.kappa, tuple(omega), OK), updated_entries
    if opcode == 0x12:
        a, r, c = args
        bits = 0
        if state.rho[r] is None:
            bits |= RUN_MISSING
        elif state.rho[r] != a:
            bits |= AUTH_DISAGREES
        if state.kappa[c] is None:
            bits |= CHANNEL_MISSING
        elif state.kappa[c] != r:
            bits |= RUN_DISAGREES
        if bits:
            return replace(state, pending=rej_frame(bits)), updated_entries
        assert state.omega[c] is not None
        return replace(state, pending=val_frame(state.omega[c])), updated_entries
    if state.e:
        return replace(state, pending=rej_frame(FINAL_EPOCH)), updated_entries
    updated_entries += (frame,)
    return replace(state, e=1, pending=OK), updated_entries


def folded_log_advance(durable: bytes, crossing: Crossing, codec: Codec) -> bytes:
    state, entries = folded_log_decode(durable, codec)
    if crossing.direction == "output":
        if state.pending is None or state.pending != crossing.frame:
            raise IllegalCrossing("log adapter wrong output")
        state = replace(state, pending=None)
    elif crossing.direction == "input":
        state, entries = folded_log_input(state, entries, crossing.frame)
    else:
        raise IllegalCrossing("log adapter unknown direction")
    return folded_log_encode(state.u, entries, state.pending)


def folded_log_from_state(state: State) -> bytes:
    entries: list[bytes] = []
    for channel in U:
        run = state.kappa[channel]
        if run is not None:
            authority = state.rho[run]
            assert authority is not None
            entries.append(encode_input(0x10, authority, run, channel))
    for channel in U:
        run = state.kappa[channel]
        word = state.omega[channel]
        if run is not None:
            authority = state.rho[run]
            assert authority is not None and word is not None
            entries.extend(encode_input(0x11, authority, run, channel, bit) for bit in word)
    if state.e:
        entries.append(encode_input(0x13))
    return folded_log_encode(state.u, tuple(entries), state.pending)


def snapshot_input(state: State, frame: bytes) -> State:
    """A third, snapshot-oriented implementation of the input rules."""
    if state.pending is not None:
        raise IllegalCrossing("snapshot input while pending")
    opcode, fields = decode_input(frame)
    if opcode == 0x14:
        return State(0, state.e, state.rho, state.kappa, state.omega, None)
    if opcode == 0x15:
        output = OK if state.u == 0 else rej_frame(ALREADY_UP)
        return State(1, state.e, state.rho, state.kappa, state.omega, output)
    if state.u == 0:
        return replace(state, pending=rej_frame(OFF))
    if opcode == 0x13:
        return (
            replace(state, pending=rej_frame(FINAL_EPOCH))
            if state.e
            else replace(state, e=1, pending=OK)
        )
    a, r, c = fields[:3]
    auth = state.rho[r]
    bound_run = state.kappa[c]
    if opcode == 0x10:
        rejected = (AUTH_DISAGREES if auth is not None and auth != a else 0) | (
            RUN_DISAGREES if bound_run is not None and bound_run != r else 0
        )
        if rejected:
            return replace(state, pending=rej_frame(rejected))
        new_rho = list(state.rho)
        new_kappa = list(state.kappa)
        new_omega = list(state.omega)
        if auth is None:
            new_rho[r] = a
        if bound_run is None:
            new_kappa[c] = r
            new_omega[c] = ()
        return State(1, state.e, tuple(new_rho), tuple(new_kappa), tuple(new_omega), OK)
    rejected = 0
    rejected |= RUN_MISSING if auth is None else (AUTH_DISAGREES if auth != a else 0)
    rejected |= CHANNEL_MISSING if bound_run is None else (RUN_DISAGREES if bound_run != r else 0)
    if opcode == 0x12:
        if rejected:
            return replace(state, pending=rej_frame(rejected))
        assert state.omega[c] is not None
        return replace(state, pending=val_frame(state.omega[c]))
    x = fields[3]
    if (a, x) not in POLICY:
        rejected |= POLICY_DENIES
    associations_exact = auth == a and bound_run == r
    if associations_exact:
        assert state.omega[c] is not None
        if len(state.omega[c]) == 2:
            rejected |= FULL
    if rejected:
        return replace(state, pending=rej_frame(rejected))
    words = list(state.omega)
    assert words[c] is not None
    words[c] = words[c] + (x,)
    return State(1, state.e, state.rho, state.kappa, tuple(words), OK)


def snapshot_advance(durable: bytes, crossing: Crossing, codec: Codec) -> bytes:
    state = codec.decode_state(durable)
    if crossing.direction == "input":
        state = snapshot_input(state, crossing.frame)
    elif crossing.direction == "output":
        if state.pending is None or state.pending != crossing.frame:
            raise IllegalCrossing("snapshot wrong output")
        state = replace(state, pending=None)
    else:
        raise IllegalCrossing("snapshot unknown direction")
    return codec.encode_state(state)


def conformance(
    graph: Graph, codec: Codec, exports: list[bytes], classes: list[int]
) -> dict[str, object]:
    state_ids = {state: state_id for state_id, state in enumerate(graph.states)}
    log_durable: list[Optional[bytes]] = [None] * len(graph.states)
    snapshot_durable: list[Optional[bytes]] = [None] * len(graph.states)
    log_durable[0] = folded_log_encode(1, (), None)
    snapshot_durable[0] = codec.encode_state(INITIAL_STATE)
    shortest_history_checks = 1
    shortest_history_x_recoveries = 0
    for state_id in range(1, len(graph.states)):
        parent_id, crossing = graph.parents[state_id]  # type: ignore[misc]
        parent_log = log_durable[parent_id]
        parent_snapshot = snapshot_durable[parent_id]
        assert parent_log is not None and parent_snapshot is not None
        new_log = folded_log_advance(parent_log, crossing, codec)
        new_snapshot = snapshot_advance(parent_snapshot, crossing, codec)
        log_state, _ = folded_log_decode(bytes(new_log), codec)
        snapshot_state = codec.decode_state(bytes(new_snapshot))
        expected = graph.states[state_id]
        if log_state != expected or snapshot_state != expected:
            raise AssertionError("realization diverged on a shortest reachable history")
        if crossing.direction == "input" and crossing.frame == b"\x14":
            # bytes() produces a fresh durable-only value; decode above is the recovery.
            shortest_history_x_recoveries += 1
        log_durable[state_id] = new_log
        snapshot_durable[state_id] = new_snapshot
        shortest_history_checks += 1

    edge_checks = 0
    future_x_recoveries = 0
    for source_id, edges in enumerate(graph.successors):
        source_log = log_durable[source_id]
        source_snapshot = snapshot_durable[source_id]
        assert source_log is not None and source_snapshot is not None
        for crossing, target_id in edges.items():
            next_log = folded_log_advance(bytes(source_log), crossing, codec)
            next_snapshot = snapshot_advance(bytes(source_snapshot), crossing, codec)
            log_state, _ = folded_log_decode(bytes(next_log), codec)
            snapshot_state = codec.decode_state(bytes(next_snapshot))
            if log_state != graph.states[target_id] or snapshot_state != graph.states[target_id]:
                raise AssertionError("realization diverged on a permitted future")
            if classes[target_id] != classes[state_ids[log_state]]:
                raise AssertionError("realization diverged from quotient successor")
            if crossing.direction == "input" and crossing.frame == b"\x14":
                future_x_recoveries += 1
            edge_checks += 1

    constructor_checks = 0
    for state_id, state in enumerate(graph.states):
        rebuilt = folded_log_from_state(state)
        rebuilt_state, _ = folded_log_decode(rebuilt, codec)
        if codec.encode_state(rebuilt_state) != exports[state_id]:
            raise AssertionError("canonical representative log constructor failed")
        constructor_checks += 1

    log_sizes = [len(value) for value in log_durable if value is not None]
    return {
        "bounded_folded_log": {
            "durable_bytes_min": min(log_sizes),
            "durable_bytes_max": max(log_sizes),
            "fixed_lifecycle_completion": {
                "durable_bytes": 1,
                "encoding": "header byte 1 stores exact u bit",
                "updated_by": ["X", "R-while-down"],
                "charged_role": (
                    "this fixed durable byte is the explicit completion that keeps repeated "
                    "X/R lifecycle changes out of the bounded mutation log; its writes and "
                    "atomic relation to the fixed pending cell are charged to the realization"
                ),
            },
            "fixed_pending_cell_bytes": 5,
            "max_state_changing_B_entries": max(
                sum(entry[0] == 0x10 for entry in folded_log_decode(value, codec)[1])
                for value in log_durable
                if value is not None
            ),
            "max_successful_A_entries": max(
                sum(entry[0] == 0x11 for entry in folded_log_decode(value, codec)[1])
                for value in log_durable
                if value is not None
            ),
            "max_successful_E_entries": max(
                sum(entry[0] == 0x13 for entry in folded_log_decode(value, codec)[1])
                for value in log_durable
                if value is not None
            ),
        },
        "canonical_snapshot": {"durable_bytes": 19},
        "shortest_history_states_compared": shortest_history_checks,
        "permitted_future_edges_compared": edge_checks,
        "shortest_history_X_durable_recoveries": shortest_history_x_recoveries,
        "all_quiescent_future_X_durable_recoveries": future_x_recoveries,
        "snapshot_to_canonical_log_constructor_checks": constructor_checks,
        "result": "byte-exact logical agreement",
    }


def expect_raises(function: Callable[[], object]) -> None:
    try:
        function()
    except ContractError:
        return
    raise AssertionError("invalid value was accepted")


def negative_tests(graph: Graph, codec: Codec, exports: list[bytes]) -> dict[str, int]:
    checks = 0
    for frame in (b"", b"\x16", b"\x13\x00", b"\x10\x00\x00", b"\x10\x00\x00\x02"):
        expect_raises(lambda frame=frame: decode_input(frame))
        checks += 1
    for frame in (
        b"",
        b"\x20\x00",
        b"\x21",
        b"\x21\x03\x00\x00\x00",
        b"\x21\x01\x02",
        b"\x22\x02\x00",
        b"\x23",
    ):
        expect_raises(lambda frame=frame: codec.decode_output(frame))
        checks += 1
    pending_id = next(index for index, state in enumerate(graph.states) if state.pending is not None)
    quiescent_id = next(index for index, state in enumerate(graph.states) if state.pending is None)
    expect_raises(
        lambda: reference_crossing(graph.states[pending_id], Crossing("input", b"\x14"))
    )
    checks += 1
    expect_raises(
        lambda: reference_crossing(graph.states[quiescent_id], Crossing("output", OK))
    )
    checks += 1
    wrong = OK if graph.states[pending_id].pending != OK else val_frame(())
    expect_raises(
        lambda: reference_crossing(graph.states[pending_id], Crossing("output", wrong))
    )
    checks += 1
    corruptions: list[bytes] = []
    initial = bytearray(exports[0])
    for offset, value in ((0, 0), (1, 2), (3, 3), (7, 4), (8, 1), (13, 4)):
        corrupted = bytearray(initial)
        corrupted[offset] = value
        corruptions.append(bytes(corrupted))
    invalid_relation = bytearray(initial)
    invalid_relation[3] = 0
    corruptions.append(bytes(invalid_relation))
    impossible_mask = bytearray(initial)
    impossible_mask[13] = 3
    impossible_mask[17:19] = b"\x00\x00"
    corruptions.append(bytes(impossible_mask))
    for encoded in corruptions:
        expect_raises(lambda encoded=encoded: codec.decode_state(encoded))
        checks += 1
    return {"negative_cases": checks, "accepted_invalid_cases": 0}


def crossing_list_json(items: list[Crossing]) -> list[dict[str, str]]:
    return [item.as_json() for item in items]


def collision_json(
    name: str,
    pair: tuple[int, int],
    graph: Graph,
    classes: list[int],
    exports: list[bytes],
) -> dict[str, object]:
    left, right = pair
    suffix = shortest_distinguishing_suffix(graph, classes, left, right)
    return {
        "projection": name,
        "left": {
            "class": classes[left],
            "export_hex": exports[left].hex(),
            "shortest_history": crossing_list_json(history(graph, left)),
        },
        "right": {
            "class": classes[right],
            "export_hex": exports[right].hex(),
            "shortest_history": crossing_list_json(history(graph, right)),
        },
        "shortest_distinguishing_suffix": crossing_list_json(suffix),
        "suffix_crossings": len(suffix),
    }


def export_quotient_checks(
    exports: list[bytes], classes: list[int]
) -> tuple[Optional[tuple[int, int]], Optional[tuple[int, int]]]:
    by_export: dict[bytes, tuple[int, int]] = {}
    bad_collision = None
    for state_id, encoded in enumerate(exports):
        prior = by_export.get(encoded)
        if prior is None:
            by_export[encoded] = (classes[state_id], state_id)
        elif prior[0] != classes[state_id]:
            bad_collision = (prior[1], state_id)
            break
    by_class: dict[int, tuple[bytes, int]] = {}
    overcomplete = None
    for state_id, class_id in enumerate(classes):
        prior = by_class.get(class_id)
        if prior is None:
            by_class[class_id] = (exports[state_id], state_id)
        elif prior[0] != exports[state_id]:
            overcomplete = (prior[1], state_id)
            break
    return bad_collision, overcomplete


def exercise_forgetting(codec: Codec) -> dict[str, bool]:
    def drive(sequence: Iterable[Crossing]) -> State:
        state = INITIAL_STATE
        for crossing in sequence:
            state = reference_crossing(state, crossing)
        return state

    bind = Crossing("input", encode_input(0x10, 0, 0, 0))
    out_ok = Crossing("output", OK)
    stable = drive((bind, out_ok))
    reject_a = Crossing("input", encode_input(0x12, 0, 0, 0))
    reject_q = Crossing("input", encode_input(0x12, 1, 1, 1))
    after_a_pending = reference_crossing(INITIAL_STATE, reject_a)
    after_q_pending = reference_crossing(INITIAL_STATE, reject_q)
    rejected_operands = (
        after_a_pending.pending == after_q_pending.pending
        and reference_crossing(after_a_pending, Crossing("output", after_a_pending.pending)) == INITIAL_STATE  # type: ignore[arg-type]
        and reference_crossing(after_q_pending, Crossing("output", after_q_pending.pending)) == INITIAL_STATE  # type: ignore[arg-type]
    )
    repeated_rejections = drive(
        (
            reject_a,
            Crossing("output", after_a_pending.pending),  # type: ignore[arg-type]
            reject_a,
            Crossing("output", after_a_pending.pending),  # type: ignore[arg-type]
        )
    ) == INITIAL_STATE
    repeated_b = drive((bind, out_ok, bind, out_ok)) == stable
    repeated_x = drive((Crossing("input", b"\x14"), Crossing("input", b"\x14"))) == drive(
        (Crossing("input", b"\x14"),)
    )
    bind_other = Crossing("input", encode_input(0x10, 1, 1, 1))
    independent_order = drive((bind, out_ok, bind_other, out_ok)) == drive(
        (bind_other, out_ok, bind, out_ok)
    )
    pending_reencoded = all(
        state.pending is None
        or codec.decode_output(state.pending) == codec.decode_output(bytes(state.pending))
        for state in (after_a_pending, after_q_pending)
    )
    return {
        "rejected_operands_after_output": rejected_operands,
        "count_and_timing_of_rejected_attempts": repeated_rejections,
        "repeated_exact_B": repeated_b,
        "repeated_X": repeated_x,
        "independent_binding_order": independent_order,
        "pending_frame_reconstruction": pending_reencoded,
    }


REJECTION_BITS: tuple[tuple[str, int], ...] = (
    ("off", OFF),
    ("run-missing", RUN_MISSING),
    ("auth-disagrees", AUTH_DISAGREES),
    ("channel-missing", CHANNEL_MISSING),
    ("run-disagrees", RUN_DISAGREES),
    ("policy-denies", POLICY_DENIES),
    ("full", FULL),
    ("final-epoch", FINAL_EPOCH),
    ("already-up", ALREADY_UP),
)


def pending_rejection_projection_collision(
    exports: list[bytes], classes: list[int], deleted_bits: int
) -> Optional[tuple[int, int]]:
    seen: dict[bytes, tuple[int, int]] = {}
    for state_id, encoded in enumerate(exports):
        projected = bytearray(encoded)
        if encoded[13] == 3:
            mask = ((encoded[17] << 8) | encoded[18]) & ~deleted_bits
            projected[17] = mask >> 8
            projected[18] = mask & 0xFF
        key = bytes(projected)
        prior = seen.get(key)
        if prior is None:
            seen[key] = (classes[state_id], state_id)
        elif prior[0] != classes[state_id]:
            return prior[1], state_id
    return None


def pending_rejection_bit_deletions(
    graph: Graph, codec: Codec, exports: list[bytes], classes: list[int]
) -> tuple[dict[str, object], tuple[int, int]]:
    tests = {
        deleted: pending_rejection_projection_collision(exports, classes, deleted)
        for deleted in range(1 << len(REJECTION_BITS))
    }
    sound = {deleted for deleted, collision in tests.items() if collision is None}
    maximal_sound = sorted(
        deleted
        for deleted in sound
        if all(
            (deleted | bit) not in sound
            for _, bit in REJECTION_BITS
            if not (deleted & bit)
        )
    )
    expected = sorted((OFF | FINAL_EPOCH, OFF | ALREADY_UP))
    both_epoch_up_deleted = FINAL_EPOCH | ALREADY_UP
    collision = tests[both_epoch_up_deleted]
    if collision is None:
        raise AssertionError("deleting final-epoch and already-up did not expose a collision")
    off_states = []
    for state in graph.states:
        if state.pending is None:
            continue
        kind, payload = codec.decode_output(state.pending)
        if kind == "REJ" and isinstance(payload, int) and payload & OFF:
            off_states.append(state)
    off_derivation = bool(off_states) and all(
        state.u == 0 and state.pending == rej_frame(OFF) for state in off_states
    )
    pending_rej_states: list[tuple[State, int]] = []
    for state in graph.states:
        if state.pending is None:
            continue
        kind, payload = codec.decode_output(state.pending)
        if kind == "REJ":
            assert isinstance(payload, int)
            pending_rej_states.append((state, payload))

    reconstruction_checks = 0
    for deleted in sorted(sound):
        for state, original in pending_rej_states:
            retained = original & ~deleted
            reconstructed = retained
            if deleted & OFF and state.u == 0:
                reconstructed |= OFF
            if deleted & FINAL_EPOCH and state.u == 1 and state.e == 1 and retained == 0:
                reconstructed |= FINAL_EPOCH
            if deleted & ALREADY_UP and state.u == 1 and retained == 0:
                reconstructed |= ALREADY_UP
            if reconstructed != original:
                raise AssertionError("sound pending-REJ deletion failed explicit reconstruction")
            reconstruction_checks += 1

    def names(mask: int) -> list[str]:
        return [name for name, bit in REJECTION_BITS if mask & bit]

    result = {
        "definition": (
            "retain every canonical byte except that, only for pending REJ states, "
            "each selected deletion bit is zeroed in bytes 17..18; a deletion set is "
            "sound exactly when equality of these projected bytes implies equality of "
            "the fixed-point quotient class, so reconstruction may use all retained state"
        ),
        "bit_names_in_position_order": [name for name, _ in REJECTION_BITS],
        "family_size": len(tests),
        "evaluated_exhaustively": True,
        "sound_deletion_set_count": len(sound),
        "unsound_deletion_set_count": len(tests) - len(sound),
        "maximal_sound_deleted_bit_sets": [names(mask) for mask in maximal_sound],
        "expected_maximal_sound_deleted_bit_sets": [names(mask) for mask in expected],
        "expected_maximal_sets_reproduced": maximal_sound == expected,
        "off_reconstruction": {
            "rule": "a pending REJ with u=0 is exactly REJ(off)",
            "reachable_pending_off_states": len(off_states),
            "verified": off_derivation,
        },
        "explicit_reconstruction": {
            "rules": [
                "restore off when pending tag is REJ and u=0",
                "restore final-epoch when it was deleted, u=1, e=1, and retained mask is zero",
                "restore already-up when it was deleted, u=1, and retained mask is zero",
            ],
            "all_sound_deletion_sets_byte_compared": True,
            "reachable_pending_REJ_states_per_set": len(pending_rej_states),
            "executed_checks": reconstruction_checks,
        },
        "final_epoch_and_already_up_joint_deletion": {
            "deleted_bits": names(both_epoch_up_deleted),
            "sound": False,
            "collision_witness": "PENDING_REJ_DELETE:final-epoch,already-up",
        },
    }
    return result, collision


def breaker_audit(codec: Codec, exports: list[bytes]) -> dict[str, object]:
    counterfeit = bytes.fromhex("5a010002020202030000030000020000000000")
    decoded = codec.decode_state(counterfeit)
    local_accepts = codec.encode_state(decoded) == counterfeit

    initial = INITIAL_STATE
    r_pending = reference_crossing(initial, Crossing("input", encode_input(0x15)))
    r_loop = reference_crossing(r_pending, Crossing("output", rej_frame(ALREADY_UP)))
    if r_loop != initial:
        raise AssertionError("R rejection loop did not return to the initial reference state")

    return {
        "canonical_import_recovery_language": {
            "counterfeit_export_hex": counterfeit.hex(),
            "local_decode_accepts": local_accepts,
            "local_decode_reencodes_exactly": local_accepts,
            "present_in_reachable_exports": counterfeit in set(exports),
            "decoded_pending_frame_hex": decoded.pending.hex() if decoded.pending else None,
            "finding": (
                "UNDERSPECIFIED: local invariant/canonical checks accept a state absent "
                "from the reachable reference export language; the frozen contract does "
                "not define whether import/recovery must reject it"
            ),
            "instrument_action": "reported only; decoder contract was not silently strengthened",
        },
        "path_sensitive_hidden_state_limit": {
            "left_reference_history": [],
            "right_reference_history": [
                Crossing("input", encode_input(0x15)).as_json(),
                Crossing("output", rej_frame(ALREADY_UP)).as_json(),
            ],
            "right_history_notation": "?R !REJ(0100)",
            "same_reference_successor": r_loop == initial,
            "same_canonical_export": codec.encode_state(r_loop) == codec.encode_state(initial),
            "finding": (
                "shortest-reference-history conformance cannot detect a realization's "
                "path-sensitive hidden state on this convergent non-shortest loop"
            ),
        },
    }


def main() -> None:
    actual_sha = fail_closed_digest()
    if len(INPUT_FRAMES) != 35 or len(set(INPUT_FRAMES)) != 35:
        raise AssertionError("input alphabet construction did not reproduce 35 frames")
    graph = enumerate_graph()
    rejection_masks = sorted(
        (frame[1] << 8) | frame[2]
        for frame in graph.outputs
        if frame[0] == 0x22
    )
    codec = Codec(rejection_masks)
    for output in graph.outputs:
        codec.decode_output(output)
    exports, vectors = state_components(codec, graph.states)
    classes, refinement_rounds = refine_partition(graph)
    class_count = len(set(classes))
    quiescent_count = sum(state.pending is None for state in graph.states)
    pending_count = len(graph.states) - quiescent_count
    if quiescent_count != 1428:
        raise AssertionError(f"predicted quiescent count failed: {quiescent_count}")
    if len(graph.states) > 44268:
        raise AssertionError("crossing-machine hard bound exceeded")
    output_count_claim = len(graph.outputs) == 30
    rejection_count_claim = len(rejection_masks) == 22

    candidate_collision, overcomplete_pair = export_quotient_checks(exports, classes)
    minimal_masks, boundary_collisions, sound_projection_count = deletion_family(vectors, classes)
    kappa_reconstruction = reconstruct_one_kappa_coordinate(graph.states, exports)
    pending_rej_projection, pending_rej_collision = pending_rejection_bit_deletions(
        graph, codec, exports, classes
    )
    breaker_findings = breaker_audit(codec, exports)
    full_mask = (1 << len(COMPONENTS)) - 1
    minimal_names = [
        [COMPONENTS[index][0] for index in range(len(COMPONENTS)) if mask & (1 << index)]
        for mask in minimal_masks
    ]

    collision_witnesses: list[dict[str, object]] = []
    if candidate_collision is not None:
        collision_witnesses.append(
            collision_json("canonical_export", candidate_collision, graph, classes, exports)
        )
    boundary_items = sorted(
        boundary_collisions.items(),
        key=lambda item: tuple(
            COMPONENTS[index][0]
            for index in range(len(COMPONENTS))
            if not (item[0] & (1 << index))
        ),
    )
    for mask, pair in boundary_items:
        deleted = [
            COMPONENTS[index][0]
            for index in range(len(COMPONENTS))
            if not (mask & (1 << index))
        ]
        collision_witnesses.append(
            collision_json("DELETE:" + ",".join(deleted), pair, graph, classes, exports)
        )
    collision_witnesses.append(
        collision_json(
            "PENDING_REJ_DELETE:final-epoch,already-up",
            pending_rej_collision,
            graph,
            classes,
            exports,
        )
    )

    merge_names = (
        "rho_endpoint_bag",
        "kappa_endpoint_bag",
        "omega_channel_bag",
        "omega_bit_bag",
        "pending_kind_only",
        "generic_rejection",
        "value_length_only",
        "lifecycle_epoch_or",
    )
    merge_results = []
    merge_witness_names: dict[str, str] = {}
    for name in merge_names:
        pair = arbitrary_key_collision(vectors, classes, lambda vector, name=name: merge_key(name, vector))
        sound = pair is None
        merge_results.append({"name": name, "sound": sound})
        if pair is not None:
            witness_name = "MERGE:" + name
            merge_witness_names[name] = witness_name
            collision_witnesses.append(collision_json(witness_name, pair, graph, classes, exports))

    conformance_result = conformance(graph, codec, exports, classes)
    negative_result = negative_tests(graph, codec, exports)
    forgetting = exercise_forgetting(codec)
    transition_count = sum(len(edges) for edges in graph.successors)
    val_count = sum(frame[0] == 0x21 for frame in graph.outputs)
    pending_cases = {
        "rejection_inputs": 0,
        "successful_query_inputs": 0,
        "idempotent_B_success_inputs": 0,
        "R_inputs_while_down": 0,
        "R_inputs_while_up": 0,
    }
    for source_id, edges in enumerate(graph.successors):
        source = graph.states[source_id]
        if source.pending is not None:
            continue
        for crossing, target_id in edges.items():
            if crossing.direction != "input" or crossing.frame == b"\x14":
                continue
            opcode, _ = decode_input(crossing.frame)
            target = graph.states[target_id]
            assert target.pending is not None
            kind, _ = codec.decode_output(target.pending)
            if kind == "REJ":
                pending_cases["rejection_inputs"] += 1
            if opcode == 0x12 and kind == "VAL":
                pending_cases["successful_query_inputs"] += 1
            if opcode == 0x10 and kind == "OK" and replace(target, pending=None) == source:
                pending_cases["idempotent_B_success_inputs"] += 1
            if opcode == 0x15:
                pending_cases["R_inputs_while_down" if source.u == 0 else "R_inputs_while_up"] += 1

    must_survive = [
        {
            "responsibility": "positional associations",
            "classification": "MUST SURVIVE",
            "forcing_witness": merge_witness_names.get("kappa_endpoint_bag"),
        },
        {
            "responsibility": "ordered words and selecting channel",
            "classification": "MUST SURVIVE",
            "forcing_witness": merge_witness_names.get("omega_channel_bag"),
        },
        {
            "responsibility": "up/down distinction",
            "classification": "MUST SURVIVE",
            "forcing_witness": "DELETE:lifecycle_u",
        },
        {
            "responsibility": "consumed evolution distinction",
            "classification": "MUST SURVIVE",
            "forcing_witness": "DELETE:epoch_e",
        },
        {
            "responsibility": "exact pending output",
            "classification": "MUST SURVIVE",
            "forcing_witness": merge_witness_names.get("pending_kind_only"),
        },
    ]
    report = {
        "experiment": "R01E external nonauthorizing exhaustive quotient and realization check",
        "authority": "falsification instrument only; no authoring, action, or production authorization",
        "contract": {
            "file": SPEC_NAME,
            "expected_sha256": SPEC_SHA256,
            "observed_sha256": actual_sha,
            "fail_closed": True,
        },
        "alphabet": {
            "input_frames": len(INPUT_FRAMES),
            "output_symbols": len(graph.outputs),
            "predicted_output_symbols": 30,
            "predicted_output_symbol_count_reproduced": output_count_claim,
            "OK_symbols": int(OK in graph.outputs),
            "VAL_symbols": val_count,
            "REJ_symbols": len(rejection_masks),
            "predicted_REJ_symbols": 22,
            "predicted_REJ_symbol_count_reproduced": rejection_count_claim,
            "reachable_rejection_masks_hex": [f"{mask:04x}" for mask in rejection_masks],
        },
        "reachability": {
            "states": len(graph.states),
            "quiescent_states": quiescent_count,
            "pending_states": pending_count,
            "legal_crossing_transitions": transition_count,
            "hard_state_bound": 44268,
            "one_shortest_history_retained_per_state": True,
        },
        "quotient": {
            "classes": class_count,
            "partition_refinement_rounds_including_stable_check": refinement_rounds,
            "deterministic_labeled_partial_transition_refinement": True,
            "candidate_same_export_collision": candidate_collision is not None,
            "candidate_unequal_exports_same_class": overcomplete_pair is not None,
            "candidate_result": (
                "unsound"
                if candidate_collision is not None
                else "overcomplete"
                if overcomplete_pair is not None
                else "exactly one reachable export per finite quotient class"
            ),
        },
        "canonical_codec": {
            "bytes": 19,
            "reachable_round_trips": len(exports),
            "unique_reachable_exports": len(set(exports)),
            "invariant_and_canonical_padding_validation": "passed",
        },
        "breaker_findings": breaker_findings,
        "projections": {
            "declared_DELETE_family": {
                "definition": "all subsets of the 11 named canonical component groups; marker is always deleted as constant framing",
                "component_groups": [name for name, _ in COMPONENTS],
                "family_size": 1 << len(COMPONENTS),
                "sound_projection_count": sound_projection_count,
                "unsound_projection_count": (1 << len(COMPONENTS)) - sound_projection_count,
                "inclusion_minimal_sound_projections": minimal_names,
                "canonical_without_marker_mask": full_mask,
                "one_kappa_coordinate_reconstruction": kappa_reconstruction,
                "evaluation": "all 2^11 projections evaluated exhaustively",
            },
            "declared_MERGE_projections": merge_results,
            "pending_REJ_mask_bit_DELETE_family": pending_rej_projection,
        },
        "collision_witnesses": collision_witnesses,
        "realizations": conformance_result,
        "pending_case_coverage": pending_cases,
        "codec_and_legality_tests": negative_result,
        "persistence_classifications": {
            "must_survive": must_survive,
            "external_specification_and_TCB_responsibility": [
                {
                    "responsibility": "immutable transition specification and policy fixture",
                    "classification": "EXTERNAL SPECIFICATION / TCB RESPONSIBILITY",
                    "dynamic_history_classification": False,
                },
                {
                    "responsibility": "frame codec and canonical format version",
                    "classification": "EXTERNAL SPECIFICATION / TCB RESPONSIBILITY",
                    "dynamic_history_classification": False,
                },
                {
                    "responsibility": "contract SHA-256 verifier, fold, serializer, constructors, adapters, comparator, and partition refiner",
                    "classification": "EXTERNAL SPECIFICATION / TCB RESPONSIBILITY",
                    "dynamic_history_classification": False,
                },
            ],
            "may_rebuild": [
                {
                    "responsibility": "canonical export from folded log and fixed pending/lifecycle cells",
                    "classification": "MAY REBUILD",
                    "executed_checks": len(graph.states),
                },
                {
                    "responsibility": "canonical representative folded log from snapshot",
                    "classification": "MAY REBUILD",
                    "executed_checks": conformance_result["snapshot_to_canonical_log_constructor_checks"],
                },
                {
                    "responsibility": "pending frame bytes from exact pending symbol and codec",
                    "classification": "MAY REBUILD",
                    "executed": forgetting["pending_frame_reconstruction"],
                },
                {
                    "responsibility": "canonical padding, lengths, state/class numbers, and shortest witnesses",
                    "classification": "MAY REBUILD",
                    "executed_checks": len(graph.states),
                },
            ],
            "may_forget": [
                {"responsibility": key, "classification": "MAY FORGET", "executed": value}
                for key, value in forgetting.items()
                if key != "pending_frame_reconstruction"
            ],
            "unexecuted_out_of_scope_claims": [
                {
                    "responsibility": "provisional computation that never crossed and is atomically aborted",
                    "classification": "NOT ESTABLISHED",
                    "executed": False,
                    "reason": "atomic abort is outside the declared crossing history",
                },
                {
                    "responsibility": "cache, cursor, process, location, and scheduling detail",
                    "classification": "NOT ESTABLISHED",
                    "executed": False,
                    "reason": "not present in the finite logical machine",
                },
            ],
        },
        "limitations": [
            "finite two-token domains and words of length at most two only",
            "canonical import/recovery acceptance is underspecified beyond reachable exports; the exact reported counterfeit is locally accepted",
            "one shortest reference history per state cannot detect path-sensitive hidden realization state, as epsilon versus ?R !REJ(0100) demonstrates",
            "no crash during an input transition, output transition, or pending-output interval",
            "no physical durability, torn-write, power-loss, corruption, or independent-failure-domain proof",
            "logical adapters are unlike encodings but share this Python process, codec contract, and host",
            "no concurrency, pipelining, deletion, cancellation, replication, migration, or semantic upgrade",
            "no dynamic authorization, revocation, aggregation, discovery, general query, or free-form explanation",
            "finite quotient result is not a global quotient or target-contract adequacy proof",
        ],
        "instrument_status": "PASS",
        "candidate_status": (
            "CONSTRUCTION CLAIMS REPRODUCED"
            if output_count_claim and rejection_count_claim
            else "FALSIFIED: predicted 30-symbol/22-mask output alphabet was not reproduced"
        ),
    }
    print(json.dumps(report, sort_keys=True, indent=2, separators=(",", ": ")))


if __name__ == "__main__":
    main()
