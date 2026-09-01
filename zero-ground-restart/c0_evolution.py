"""Executable migration criterion for observers proposed after quotienting.

An added observer is rebuildable from an old encoding exactly when its required
value is constant on every old encoding cell. This is a probe, not a general
contract-evolution mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, Optional

from c0_experiment import history_order
from c0_oracle import Frame


History = tuple[Frame, ...]


@dataclass(frozen=True)
class FactorProbe:
    factors_through_old_encoding: bool
    encoded_cells_checked: int
    witness: Optional[tuple[History, History, object, object]]


def factor_probe(
    histories: Iterable[History],
    encode: Callable[[History], Hashable],
    observer: Callable[[History], object],
) -> FactorProbe:
    cells: dict[Hashable, tuple[object, History]] = {}
    for history in sorted(histories, key=history_order):
        encoded = encode(history)
        value = observer(history)
        prior = cells.get(encoded)
        if prior is None:
            cells[encoded] = (value, history)
        elif prior[0] != value:
            return FactorProbe(False, len(cells), (prior[1], history, prior[0], value))
    return FactorProbe(True, len(cells), None)


def current_b1_observer(history: History) -> bool:
    """A compatible observer: whether current authored content is exactly b/1."""

    from c0_oracle import replay

    return replay(history).content == ("b", "1")


def authored_crossing_count_observer(history: History) -> int:
    """A split extension: count all prior P crossings, including overwritten ones."""

    return sum(frame.direction == "in" and frame.kind == "P" for frame in history)

