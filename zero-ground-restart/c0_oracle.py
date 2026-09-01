"""Independent raw-boundary oracle for the frozen C0 experiment.

The dataclasses in this module are implementation conveniences for exhaustive
falsification.  They are not proposed system primitives.  In particular,
``replay`` derives its snapshot from the complete boundary trace; candidate
encoders live in a different module and consume only quotient class names.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Optional, Sequence


CLIENT = "client"
ACTION = "action"
IN = "in"
OUT = "out"


@dataclass(frozen=True, order=True)
class Frame:
    direction: str
    port: str
    kind: str
    args: tuple[str, ...] = ()

    def token(self) -> str:
        body = ",".join(self.args)
        return f"{self.direction}:{self.port}:{self.kind}" + (
            f"({body})" if body else ""
        )


@dataclass(frozen=True, order=True)
class Descriptor:
    source: str
    bit: str
    rule_label: str
    result: str

    def flat(self) -> tuple[str, ...]:
        return (self.source, self.bit, self.rule_label, self.result)


@dataclass(frozen=True, order=True)
class ActionRecord:
    status: str  # pending | done
    descriptor: Descriptor


@dataclass(frozen=True)
class Snapshot:
    content: Optional[tuple[str, str]]
    rule: tuple[str, str, str]
    action_k: Optional[ActionRecord]
    action_l: Optional[ActionRecord]
    owed: Optional[Frame]

    def action(self, key: str) -> Optional[ActionRecord]:
        return self.action_k if key == "k" else self.action_l

    def with_action(self, key: str, value: Optional[ActionRecord]) -> "Snapshot":
        if key == "k":
            return Snapshot(self.content, self.rule, value, self.action_l, self.owed)
        return Snapshot(self.content, self.rule, self.action_k, value, self.owed)


@dataclass(frozen=True)
class Step:
    legal: bool
    snapshot: Snapshot
    crossed: tuple[Frame, ...] = ()
    reason: str = ""


INITIAL = Snapshot(None, ("d", "0", "1"), None, None, None)


def inbound(kind: str, *args: str, port: str = CLIENT) -> Frame:
    return Frame(IN, port, kind, tuple(args))


def outbound(kind: str, *args: str, port: str = CLIENT) -> Frame:
    return Frame(OUT, port, kind, tuple(args))


INPUTS: tuple[Frame, ...] = tuple(
    sorted(
        [
            *(inbound("P", source, bit) for source in ("a", "b") for bit in ("0", "1")),
            inbound("R", "u", "0", "1"),
            inbound("R", "u", "0", "0"),
            inbound("R", "v", "0", "1"),
            inbound("O"),
            inbound("Q"),
            inbound("X"),
            *(inbound("A", key) for key in ("k", "l")),
            *(inbound("ACK", key, port=ACTION) for key in ("k", "l")),
            *(inbound("S", key) for key in ("k", "l")),
        ],
        key=Frame.token,
    )
)
INPUT_SET = frozenset(INPUTS)


def _mapped(snapshot: Snapshot) -> Optional[str]:
    if snapshot.content is None:
        return None
    bit = snapshot.content[1]
    return snapshot.rule[1] if bit == "0" else snapshot.rule[2]


def _descriptor(snapshot: Snapshot) -> Descriptor:
    assert snapshot.content is not None
    result = _mapped(snapshot)
    assert result is not None
    return Descriptor(snapshot.content[0], snapshot.content[1], snapshot.rule[0], result)


def _replace(
    snapshot: Snapshot,
    *,
    content: object = ...,
    rule: object = ...,
    owed: object = ...,
) -> Snapshot:
    return Snapshot(
        snapshot.content if content is ... else content,  # type: ignore[arg-type]
        snapshot.rule if rule is ... else rule,  # type: ignore[arg-type]
        snapshot.action_k,
        snapshot.action_l,
        snapshot.owed if owed is ... else owed,  # type: ignore[arg-type]
    )


def accept(snapshot: Snapshot, frame: Frame) -> Step:
    """Apply one inbound crossing without automatically emitting an output."""

    if snapshot.owed is not None:
        return Step(False, snapshot, reason="outbound frame is owed")
    if frame not in INPUT_SET:
        return Step(False, snapshot, reason="outside frozen input grammar")

    kind, args = frame.kind, frame.args
    if kind == "P":
        return Step(True, _replace(snapshot, content=(args[0], args[1])), (frame,))
    if kind == "R":
        return Step(True, _replace(snapshot, rule=(args[0], args[1], args[2])), (frame,))
    if kind == "O":
        owed = outbound("EMPTY") if snapshot.content is None else outbound("RAW", *snapshot.content)
        return Step(True, _replace(snapshot, owed=owed), (frame,))
    if kind == "Q":
        value = _mapped(snapshot)
        owed = outbound("EMPTY") if value is None else outbound("VAL", value)
        return Step(True, _replace(snapshot, owed=owed), (frame,))
    if kind == "X":
        if snapshot.content is None:
            owed = outbound("EMPTY")
        else:
            owed = outbound("WHY", *_descriptor(snapshot).flat())
        return Step(True, _replace(snapshot, owed=owed), (frame,))
    if kind == "A":
        key = args[0]
        record = snapshot.action(key)
        updated = snapshot
        if record is None:
            if snapshot.content is None:
                owed = outbound("NO_DATA", key)
            else:
                descriptor = _descriptor(snapshot)
                record = ActionRecord("pending", descriptor)
                updated = snapshot.with_action(key, record)
                owed = outbound("DO", key, *descriptor.flat(), port=ACTION)
        elif record.status == "pending":
            owed = outbound("DO", key, *record.descriptor.flat(), port=ACTION)
        else:
            owed = outbound("ALREADY", key, *record.descriptor.flat())
        return Step(True, _replace(updated, owed=owed), (frame,))
    if kind == "ACK":
        key = args[0]
        record = snapshot.action(key)
        if record is None or record.status != "pending":
            return Step(False, snapshot, reason="ACK requires a crossed pending action")
        updated = snapshot.with_action(key, ActionRecord("done", record.descriptor))
        return Step(True, updated, (frame,))
    if kind == "S":
        key = args[0]
        record = snapshot.action(key)
        if record is None:
            owed = outbound("ABSENT", key)
        else:
            status = "PENDING" if record.status == "pending" else "DONE"
            owed = outbound(status, key, *record.descriptor.flat())
        return Step(True, _replace(snapshot, owed=owed), (frame,))
    raise AssertionError(f"unhandled frozen input: {frame}")


def resume(snapshot: Snapshot) -> Step:
    """Emit the single owed frame, if one exists."""

    if snapshot.owed is None:
        return Step(True, snapshot)
    frame = snapshot.owed
    return Step(True, _replace(snapshot, owed=None), (frame,))


@lru_cache(maxsize=None)
def replay(history: tuple[Frame, ...]) -> Snapshot:
    """Validate and reduce a complete raw boundary prefix."""

    snapshot = INITIAL
    for index, frame in enumerate(history):
        if frame.direction == IN:
            step = accept(snapshot, frame)
            if not step.legal:
                raise ValueError(f"illegal inbound crossing at {index}: {step.reason}")
            snapshot = step.snapshot
            continue
        if frame.direction == OUT:
            if snapshot.owed != frame:
                expected = snapshot.owed.token() if snapshot.owed else "nothing"
                raise ValueError(
                    f"illegal outbound crossing at {index}: expected {expected}, got {frame.token()}"
                )
            snapshot = resume(snapshot).snapshot
            continue
        raise ValueError(f"unknown direction at {index}: {frame.direction}")
    return snapshot


def complete_turn(snapshot: Snapshot, frame: Frame) -> tuple[Step, tuple[Frame, ...]]:
    """Accept a frozen input and drain its one possible output."""

    first = accept(snapshot, frame)
    if not first.legal:
        return first, ()
    second = resume(first.snapshot)
    outputs = tuple(crossing for crossing in second.crossed if crossing.direction == OUT)
    return Step(True, second.snapshot, first.crossed + second.crossed), outputs


def append_legal(history: tuple[Frame, ...], frame: Frame) -> tuple[Frame, ...]:
    step = accept(replay(history), frame)
    if not step.legal:
        raise ValueError(step.reason)
    return history + (frame,)


def drain_history(history: tuple[Frame, ...]) -> tuple[Frame, ...]:
    step = resume(replay(history))
    return history + step.crossed


def frame_tokens(frames: Iterable[Frame]) -> tuple[str, ...]:
    return tuple(frame.token() for frame in frames)


def history_token(history: Sequence[Frame]) -> str:
    return ";".join(frame.token() for frame in history)

