"""Candidate encoders over the quotient produced independently from raw traces."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Iterable, Optional

from c0_experiment import DISABLED, ENABLED, StableRightCongruence, history_order
from c0_oracle import INPUTS, Frame, Snapshot, accept, frame_tokens, replay, resume


_HERE = Path(__file__).resolve().parent
SPECIFICATION_FILES = (
    _HERE / "CONTRACT-B1.md",
    _HERE / "c0_oracle.py",
    _HERE / "c0_experiment.py",
    _HERE / "c0_candidates.py",
)


def base_specification_digest() -> str:
    """Bind the exact executable contract, oracle, quotient, and codec sources."""

    digest = hashlib.sha256()
    for path in SPECIFICATION_FILES:
        data = path.read_bytes()
        digest.update(path.name.encode("utf-8"))
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    digest.update(b"\nINPUT_ORDER\n")
    for frame in INPUTS:
        digest.update(frame.token().encode("utf-8") + b"\n")
    return digest.hexdigest()


BASE_SPECIFICATION_DIGEST = base_specification_digest()

ClassKey = tuple[str, ...]


@dataclass(frozen=True)
class BoundaryResult:
    """Generated step plus proof-only inbound-domain membership, when applicable."""

    domain_membership: Optional[str]
    client: tuple[str, ...]
    action: tuple[str, ...]
    next_key: ClassKey


class QuotientBoundaryMachine:
    """Boundary-step machine induced by the stable finite-domain quotient."""

    def __init__(self, quotient: StableRightCongruence):
        self.quotient = quotient
        self._q_edges: dict[tuple[int, int], BoundaryResult] = {}
        self._owed_frames: dict[ClassKey, Frame] = {}
        self._build_edges()
        self.representatives = self._canonical_representatives()
        self.ordered_keys = tuple(sorted(self.representatives, key=lambda k: history_order(self.representatives[k])))
        self.rank_by_key = {key: rank for rank, key in enumerate(self.ordered_keys)}
        self.specification_digest = self._artifact_digest()

    @staticmethod
    def qkey(part: int) -> ClassKey:
        return ("q", str(part))

    @staticmethod
    def owed_key(frame: Frame, settled_part: int) -> ClassKey:
        return ("o", frame.token(), str(settled_part))

    def _build_edges(self) -> None:
        for part in sorted(set(self.quotient.partitions)):
            state_index = self.quotient.representative_index(part)
            snapshot = self.quotient.states[state_index]
            for input_index, frame in enumerate(INPUTS):
                step = accept(snapshot, frame)
                if not step.legal:
                    self._q_edges[(part, input_index)] = BoundaryResult(
                        DISABLED, (), (), self.qkey(part)
                    )
                    continue
                if step.snapshot.owed is None:
                    target_part = self.quotient.quiescent_part(step.snapshot)
                    next_key = self.qkey(target_part)
                else:
                    owed = step.snapshot.owed
                    settled = resume(step.snapshot).snapshot
                    target_part = self.quotient.quiescent_part(settled)
                    next_key = self.owed_key(owed, target_part)
                    prior = self._owed_frames.setdefault(next_key, owed)
                    if prior != owed:
                        raise AssertionError("owed class key aliases different frames")
                self._q_edges[(part, input_index)] = BoundaryResult(
                    ENABLED, (), (), next_key
                )

    @property
    def all_keys(self) -> tuple[ClassKey, ...]:
        qkeys = tuple(self.qkey(part) for part in sorted(set(self.quotient.partitions)))
        return qkeys + tuple(sorted(self._owed_frames))

    def class_key(self, snapshot: Snapshot) -> ClassKey:
        return self.quotient.class_key(snapshot)

    def input_step(self, key: ClassKey, frame: Frame) -> BoundaryResult:
        if frame not in INPUTS:
            raise KeyError("UNKNOWN: input lies outside B1 grammar")
        if key[0] == "o":
            return BoundaryResult(DISABLED, (), (), key)
        input_index = INPUTS.index(frame)
        return self._q_edges[(int(key[1]), input_index)]

    def resume_step(self, key: ClassKey) -> BoundaryResult:
        if key[0] == "q":
            return BoundaryResult(None, (), (), key)
        frame = self._owed_frames[key]
        target = self.qkey(int(key[2]))
        if frame.port == "client":
            return BoundaryResult(None, (frame.token(),), (), target)
        return BoundaryResult(None, (), (frame.token(),), target)

    def _canonical_representatives(self) -> dict[ClassKey, tuple[Frame, ...]]:
        from c0_oracle import INITIAL

        initial = self.class_key(INITIAL)
        representatives: dict[ClassKey, tuple[Frame, ...]] = {initial: ()}
        queue = deque([initial])
        while queue:
            key = queue.popleft()
            history = representatives[key]
            crossings: list[tuple[Frame, ClassKey]] = []
            if key[0] == "q":
                for frame in INPUTS:
                    edge = self.input_step(key, frame)
                    if edge.domain_membership == ENABLED:
                        crossings.append((frame, edge.next_key))
            else:
                frame = self._owed_frames[key]
                crossings.append((frame, self.resume_step(key).next_key))
            for crossing, target in sorted(crossings, key=lambda item: item[0].token()):
                if target in representatives:
                    continue
                representatives[target] = history + (crossing,)
                queue.append(target)
        missing = set(self.all_keys) - set(representatives)
        if missing:
            raise AssertionError(f"unreachable quotient keys: {len(missing)}")
        return representatives

    def _artifact_digest(self) -> str:
        """Bind ranks, representatives, transition cells, and outputs exactly."""

        digest = hashlib.sha256()
        digest.update(BASE_SPECIFICATION_DIGEST.encode("ascii"))
        for rank, key in enumerate(self.ordered_keys):
            digest.update(repr((rank, key, frame_tokens(self.representatives[key]))).encode("utf-8"))
            digest.update(b"\n")
        for part in sorted(set(self.quotient.partitions)):
            key = self.qkey(part)
            for frame in INPUTS:
                edge = self.input_step(key, frame)
                digest.update(
                    repr(
                        (
                            key,
                            frame.token(),
                            edge.domain_membership,
                            edge.client,
                            edge.action,
                            edge.next_key,
                        )
                    ).encode("utf-8")
                )
                digest.update(b"\n")
        for key in sorted(self._owed_frames):
            edge = self.resume_step(key)
            digest.update(
                repr((key, "resume", edge.client, edge.action, edge.next_key)).encode("utf-8")
            )
            digest.update(b"\n")
        return digest.hexdigest()

    def approximate_table_bytes(self) -> int:
        """Size of a deterministic textual table rendition, not allocator RSS."""

        total = 0
        for part in sorted(set(self.quotient.partitions)):
            key = self.qkey(part)
            for frame in INPUTS:
                edge = self.input_step(key, frame)
                total += len(
                    repr(
                        (key, frame.token(), edge.domain_membership, edge.next_key)
                    ).encode("utf-8")
                ) + 1
        for key in self._owed_frames:
            edge = self.resume_step(key)
            total += len(
                repr((key, "resume", edge.client, edge.action, edge.next_key)).encode("utf-8")
            ) + 1
        return total


@dataclass(frozen=True)
class OrdinalEncoding:
    specification_digest: str
    rank: int


class OrdinalCandidate:
    def __init__(self, machine: QuotientBoundaryMachine):
        self.machine = machine

    def persist(self, snapshot: Snapshot) -> OrdinalEncoding:
        return OrdinalEncoding(
            self.machine.specification_digest,
            self.machine.rank_by_key[self.machine.class_key(snapshot)],
        )

    def recover(self, encoding: OrdinalEncoding) -> ClassKey:
        if encoding.specification_digest != self.machine.specification_digest:
            raise ValueError("specification digest mismatch")
        if encoding.rank < 0 or encoding.rank >= len(self.machine.ordered_keys):
            raise ValueError("ordinal outside generated quotient")
        return self.machine.ordered_keys[encoding.rank]


_FRAME_RE = re.compile(
    r"^(in|out):(client|action):([A-Z_]+)(?:\(([A-Za-z0-9_,]*)\))?$"
)


def encode_history(history: Iterable[Frame]) -> bytes:
    return ";".join(frame.token() for frame in history).encode("utf-8")


def decode_history(data: bytes) -> tuple[Frame, ...]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("UNKNOWN: representative is not UTF-8") from exc
    if text == "":
        return ()
    frames: list[Frame] = []
    for token in text.split(";"):
        match = _FRAME_RE.fullmatch(token)
        if match is None:
            raise ValueError("UNKNOWN: representative lies outside B1 frame grammar")
        direction, port, kind, body = match.groups()
        args = () if body in (None, "") else tuple(body.split(","))
        frames.append(Frame(direction, port, kind, args))
    return tuple(frames)


@dataclass(frozen=True)
class RepresentativeEncoding:
    specification_digest: str
    marks: bytes


class RepresentativeCandidate:
    def __init__(self, machine: QuotientBoundaryMachine):
        self.machine = machine

    def persist(self, snapshot: Snapshot) -> RepresentativeEncoding:
        key = self.machine.class_key(snapshot)
        return RepresentativeEncoding(
            self.machine.specification_digest, encode_history(self.machine.representatives[key])
        )

    def recover(self, encoding: RepresentativeEncoding) -> ClassKey:
        if encoding.specification_digest != self.machine.specification_digest:
            raise ValueError("specification digest mismatch")
        history = decode_history(encoding.marks)
        try:
            snapshot = replay(history)
        except ValueError as exc:
            raise ValueError("representative is not a legal C0 boundary prefix") from exc
        key = self.machine.class_key(snapshot)
        if self.machine.representatives[key] != history:
            raise ValueError("representative is legal but noncanonical")
        return key
