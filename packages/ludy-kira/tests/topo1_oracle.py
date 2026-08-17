"""Compact semantic oracle for the checked-in DY FIRE topology 1 run.

The source files are mirrored in ``tests/fixtures/fire_topo1`` and retained in
the full Mathematica context under
``calculations/dy/mathematica/temp/FIRE/topo1``. This module
intentionally records their already-decoded semantics instead of adding a FIRE
table parser to :mod:`ludy_kira`.

The oracle deliberately retains FIRE's mass symbol ``m``.  A Kira comparison
must reconstruct its mass-squared invariant and apply the exact alias
``m2 -> m^2``; keeping that translation visible prevents a run with ``m2=1``
from looking like a valid parity result.
"""

from __future__ import annotations

Index = tuple[int, int, int]

FAMILY_NAME = "topo1"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "3a43db121f0bff78abaa9695448682f16c8de5b2b0a06c8ef28833b18d4beb45",
    "ToReduce.m": "dc97adc460b36532bff4bfb9768c346bb603e5a26a3151e67a3081a65fb8aa33",
    "topo1.tables": "e4260a9b01955538e0a351675fc4a9671b76381e3548382ef7a46dcc5ef9a637",
}

# This is the exact Cartesian-product ordering in FIRE's ToReduce.m. Spell out
# the three axes so static type checkers retain the fixed tuple width.
TARGET_INDICES: tuple[Index, ...] = tuple(
    (first, second, third)
    for first in (1, 0, -1)
    for second in (1, 0, -1)
    for third in (1, 0, -1)
)

MASTER_INDICES = frozenset(
    {
        (1, 1, 1),
        (0, 1, 1),
        (1, 0, 0),
    }
)

ZERO_INDICES = frozenset(
    {
        (0, 1, 0),
        (0, 1, -1),
        (0, 0, 1),
        (0, 0, 0),
        (0, 0, -1),
        (0, -1, 1),
        (0, -1, 0),
        (0, -1, -1),
        (-1, 1, 0),
        (-1, 1, -1),
        (-1, 0, 1),
        (-1, 0, 0),
        (-1, 0, -1),
        (-1, -1, 1),
        (-1, -1, 0),
        (-1, -1, -1),
    }
)


def symbolica_integral(indices: Index) -> str:
    """Return the canonical Symbolica spelling used by the oracle."""

    return f"{FAMILY_NAME}({','.join(map(str, indices))})"


def wolfram_integral(indices: Index) -> str:
    """Return the line format accepted by Kira target/master files."""

    return f"{FAMILY_NAME}[{','.join(map(str, indices))}]"


EXPECTED_RHS = {
    indices: symbolica_integral(indices) for indices in MASTER_INDICES
}
EXPECTED_RHS.update({indices: "0" for indices in ZERO_INDICES})
EXPECTED_RHS.update(
    {
        (-1, 1, 1): "(ipp1p2-m^2)*topo1(0,1,1)",
        (1, -1, 1): "(d*m^2-4*ipp1p2)/(d*m^2)*topo1(1,0,0)",
        (1, 1, -1): "(d*m^2-4*ipp1p2)/(d*m^2)*topo1(1,0,0)",
        (1, 0, 1): "topo1(1,0,0)/m^2",
        (1, 1, 0): "topo1(1,0,0)/m^2",
        (1, -1, -1): "(d*m^4+4*ipp1p2*m^2)/d*topo1(1,0,0)",
        (1, 0, -1): "m^2*topo1(1,0,0)",
        (1, -1, 0): "m^2*topo1(1,0,0)",
    }
)

PREFERRED_MASTERS = tuple(
    wolfram_integral(indices)
    for indices in (
        (1, 1, 1),
        (0, 1, 1),
        (1, 0, 0),
    )
)

assert len(TARGET_INDICES) == 27
assert len(MASTER_INDICES) == 3
assert len(ZERO_INDICES) == 16
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
