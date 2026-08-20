"""Compact semantic oracle for the checked-in DY FIRE topology 5 run."""

from __future__ import annotations

Index = tuple[int, int, int]

FAMILY_NAME = "topo5"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "227811a96d58ce15e430526580609f45ad1d0dfe47d07f715d35952d6c8e80ce",
    "ToReduce.m": "0476f41565653bd1a81425131ef039be70cf31a425a22313c48b82cfea3d4a35",
    "topo5.tables": "de0fbea186adb8b0e845fc8a029be0af16692b5597db0b8833010170279dff88",
}

TARGET_INDICES: tuple[Index, ...] = (
    (1, 1, 1),
    (1, 1, 0),
    (1, 1, -1),
    (1, 1, -2),
    (1, 0, 1),
    (1, 0, 0),
    (1, 0, -1),
    (1, 0, -2),
    (1, -1, 1),
    (1, -1, 0),
    (1, -1, -1),
    (1, -1, -2),
    (1, -2, 1),
    (1, -2, 0),
    (1, -2, -1),
    (1, -2, -2),
    (0, 1, 1),
    (0, 1, 0),
    (0, 1, -1),
    (0, 1, -2),
    (0, 0, 1),
    (0, 0, 0),
    (0, 0, -1),
    (0, 0, -2),
    (0, -1, 1),
    (0, -1, 0),
    (0, -1, -1),
    (0, -1, -2),
    (0, -2, 1),
    (0, -2, 0),
    (0, -2, -1),
    (0, -2, -2),
    (-1, 1, 1),
    (-1, 1, 0),
    (-1, 1, -1),
    (-1, 1, -2),
    (-1, 0, 1),
    (-1, 0, 0),
    (-1, 0, -1),
    (-1, 0, -2),
    (-1, -1, 1),
    (-1, -1, 0),
    (-1, -1, -1),
    (-1, -1, -2),
    (-1, -2, 1),
    (-1, -2, 0),
    (-1, -2, -1),
    (-1, -2, -2),
    (-2, 1, 1),
    (-2, 1, 0),
    (-2, 1, -1),
    (-2, 1, -2),
    (-2, 0, 1),
    (-2, 0, 0),
    (-2, 0, -1),
    (-2, 0, -2),
    (-2, -1, 1),
    (-2, -1, 0),
    (-2, -1, -1),
    (-2, -1, -2),
    (-2, -2, 1),
    (-2, -2, 0),
    (-2, -2, -1),
    (-2, -2, -2),
)

MASTER_INDICES = frozenset({(0, 1, 1)})
NONZERO_REDUCED_INDICES = frozenset(
    {
        (1, 1, 1),
        (-1, 1, 1),
        (-2, 1, 1),
    }
)
ZERO_INDICES = frozenset(
    set(TARGET_INDICES) - MASTER_INDICES - NONZERO_REDUCED_INDICES
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
        (1, 1, 1): "(-d+3)/((d-4)*ipp1p2)*topo5(0,1,1)",
        (-1, 1, 1): "-ipp1p2*topo5(0,1,1)",
        (-2, 1, 1): "d*ipp1p2^2/(d-1)*topo5(0,1,1)",
    }
)

PREFERRED_MASTERS = (wolfram_integral((0, 1, 1)),)

assert len(TARGET_INDICES) == 64
assert len(MASTER_INDICES) == 1
assert len(ZERO_INDICES) == 60
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
