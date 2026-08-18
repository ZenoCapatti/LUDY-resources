"""Compact semantic oracle for the checked-in DY FIRE topology 7 run."""

from __future__ import annotations

Index = tuple[int, int, int]

FAMILY_NAME = "topo7"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "bc52b0ec267ca105d17a5f8bc24ab721a59bc06d1eb2657411e867826acec30d",
    "ToReduce.m": "96531d2b17e5bbfbe1ffcacef5ff8ea83fd99382b15dc62aec934a93771ff4cf",
    "topo7.tables": "76399a919564c711ab72cc6a67ef9618ff3d77fed629abe636dbd13473dd313c",
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
        (0, 1, 1),
        (1, 1, 0),
    }
)
NONZERO_REDUCED_INDICES = frozenset(
    {
        (1, 1, 1),
        (-1, 1, 1),
        (-2, 1, 1),
        (1, 1, -1),
        (1, 1, -2),
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
        (1, 1, 1): (
            "(-d+3)/((d-4)*ipp1p2)*topo7(0,1,1)"
            "+(d-3)/((d-4)*ipp1p2)*topo7(1,1,0)"
        ),
        (-1, 1, 1): "-ipp1p2*topo7(0,1,1)",
        (-2, 1, 1): "d*ipp1p2^2/(d-1)*topo7(0,1,1)",
        (1, 1, -1): "ipp1p2*topo7(1,1,0)",
        (1, 1, -2): "d*ipp1p2^2/(d-1)*topo7(1,1,0)",
    }
)

PREFERRED_MASTERS = tuple(
    wolfram_integral(indices)
    for indices in (
        (0, 1, 1),
        (1, 1, 0),
    )
)

assert len(TARGET_INDICES) == 64
assert len(MASTER_INDICES) == 2
assert len(ZERO_INDICES) == 57
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
