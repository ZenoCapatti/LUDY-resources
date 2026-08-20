"""Compact semantic oracle for the checked-in DY FIRE topology 4 run."""

from __future__ import annotations

Index = tuple[int, int, int]

FAMILY_NAME = "topo4"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "8ae93a3c72a47192e28207ed15d55e68ab8c6a8010eca944ed99ae097d54253a",
    "ToReduce.m": "063354b9132f11bc096c164f0c656f0e246a6afd7abeacedf53d5a3066aef21d",
    "topo4.tables": "1a6850d7e8b975bc584ad0e66fef193ac057ca2f338afcb834a400ba5ea43e9c",
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

MASTER_INDICES = frozenset({(1, 1, 0)})

ZERO_INDICES = frozenset(
    {
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
        (1, 1, 1): "(d-3)/((d-4)*ipp1p2)*topo4(1,1,0)",
        (1, 1, -1): "ipp1p2*topo4(1,1,0)",
    }
)

PREFERRED_MASTERS = (wolfram_integral((1, 1, 0)),)

assert len(TARGET_INDICES) == 27
assert len(MASTER_INDICES) == 1
assert len(ZERO_INDICES) == 24
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
