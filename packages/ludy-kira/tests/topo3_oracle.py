"""Compact semantic oracle for the checked-in DY FIRE topology 2 run.

The source files are mirrored in ``tests/fixtures/fire_topo3`` and retained in
the full Mathematica context under
``calculations/dy/mathematica/temp/FIRE/topo3``. This module records their
already-decoded semantics without adding a FIRE table parser to
:mod:`ludy_kira`.

The oracle retains FIRE's mass symbol ``m``. A Kira comparison must reconstruct
its mass-squared invariant and apply the exact alias ``m2 -> m^2``.
"""

from __future__ import annotations

Index = tuple[int, int, int]

FAMILY_NAME = "topo3"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "fd8a50c3e4b635d0f0f11c78fccacc3ad945ffba690c73b94f45e38c460229cb",
    "ToReduce.m": "997232b1a9e961f4970d27c45644174aa4cd593d79bca78689aad4a73654dbb1",
    "topo3.tables": "c07a0b0e95dbbccea2f51c2ee370d4fa57b414b51dbbeeedf55565afa5677766",
}

TARGET_INDICES: tuple[Index, ...] = (
    (1, 1, 1),
    (1, 1, 0),
    (1, 1, -1),
    (1, 0, 1),
    (1, 0, 0),
    (1, 0, -1),
    (1, -1, 1),
    (1, -1, 0),
    (1, -1, -1),
    (0, 1, 1),
    (0, 1, 0),
    (0, 1, -1),
    (0, 0, 1),
    (0, 0, 0),
    (0, 0, -1),
    (0, -1, 1),
    (0, -1, 0),
    (0, -1, -1),
    (-1, 1, 1),
    (-1, 1, 0),
    (-1, 1, -1),
    (-1, 0, 1),
    (-1, 0, 0),
    (-1, 0, -1),
    (-1, -1, 1),
    (-1, -1, 0),
    (-1, -1, -1),
)

MASTER_INDICES = frozenset(
    {
        (1, 0, 1),
        (1, 0, 0),
    }
)

ZERO_INDICES = frozenset(
    {
        (0, 1, 1),
        (0, 1, 0),
        (0, 1, -1),
        (0, 0, 1),
        (0, 0, 0),
        (0, 0, -1),
        (0, -1, 1),
        (0, -1, 0),
        (0, -1, -1),
        (-1, 1, 1),
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
        (1, 1, 1): (
            "(-d+2)/((d-4)*m^4+(-2*d+8)*ipp1p2*m^2)*topo3(1,0,0)"
            "+(2*d-6)/((d-4)*m^2+(-2*d+8)*ipp1p2)*topo3(1,0,1)"
        ),
        (1, 1, 0): "topo3(1,0,0)/m^2",
        (1, 1, -1): (
            "(d*m^2+(2*d-4)*ipp1p2)/(d*m^2)*topo3(1,0,0)"
        ),
        (1, 0, -1): "(m^2+2*ipp1p2)*topo3(1,0,0)",
        (1, -1, 1): (
            "topo3(1,0,0)/2+(m^2-2*ipp1p2)/2*topo3(1,0,1)"
        ),
        (1, -1, 0): "m^2*topo3(1,0,0)",
        (1, -1, -1): (
            "(d*m^4+(2*d+4)*ipp1p2*m^2)/d*topo3(1,0,0)"
        ),
    }
)

PREFERRED_MASTERS = tuple(
    wolfram_integral(indices)
    for indices in (
        (1, 0, 1),
        (1, 0, 0),
    )
)

assert len(TARGET_INDICES) == 27
assert len(MASTER_INDICES) == 2
assert len(ZERO_INDICES) == 18
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
