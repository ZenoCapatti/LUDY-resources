"""Compact semantic oracle for the checked-in DY FIRE topology 8 run."""

from __future__ import annotations

Index = tuple[int, int, int]

FAMILY_NAME = "topo8"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "f72aa97acb708b6c38d29a4580f7b1e1c8dc1a067d9923e73f7d480f51308175",
    "ToReduce.m": "5c93dc7c825146d32bf565134c0d3cfe77e550d0fc1f581d8ab6014b4a17600e",
    "topo8.tables": "2d2adc1424af2a5e511873a34d60f7296e5af190ad9ad41d2209941e5501a805",
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

MASTER_INDICES = frozenset(
    {
        (1, 1, 1),
        (1, 1, 0),
        (1, 0, 1),
        (0, 1, 1),
    }
)
NONZERO_REDUCED_INDICES = frozenset(
    {
        (-2, 1, 1),
        (-1, 1, 1),
        (1, -2, 1),
        (1, -1, 1),
        (1, 1, -2),
        (1, 1, -1),
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
        (-2, 1, 1): (
            "(-ipp1p1*ipp2p2+d*ipp1p2^2)/(d-1)*topo8(0,1,1)"
        ),
        (-1, 1, 1): "ipp1p2*topo8(0,1,1)",
        (1, -2, 1): (
            "(-ipp1p1*ipp2p2+d*ipp1p2^2+(-2*d+2)*ipp1p1*ipp1p2"
            "+(d-1)*ipp1p1^2)/(d-1)*topo8(1,0,1)"
        ),
        (1, -1, 1): "(-ipp1p2+ipp1p1)*topo8(1,0,1)",
        (1, 1, -2): (
            "((d-1)*ipp2p2^2+((-2*d+2)*ipp1p2-ipp1p1)*ipp2p2"
            "+d*ipp1p2^2)/(d-1)*topo8(1,1,0)"
        ),
        (1, 1, -1): "(ipp2p2-ipp1p2)*topo8(1,1,0)",
    }
)

PREFERRED_MASTERS = tuple(
    wolfram_integral(indices)
    for indices in (
        (1, 1, 1),
        (1, 1, 0),
        (1, 0, 1),
        (0, 1, 1),
    )
)

assert len(TARGET_INDICES) == 64
assert len(MASTER_INDICES) == 4
assert len(ZERO_INDICES) == 54
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
