"""Compact semantic oracle for the checked-in DY FIRE topology 6 run."""

from __future__ import annotations

Index = tuple[int, int, int]

FAMILY_NAME = "topo6"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "99fa7a9cb7de5347098ae27f454a68107269d75e717dd3ac1cd7b57b36bd4e75",
    "ToReduce.m": "62682d5b1c23615718888156a9a8270c00749064c20489ab00af15fb90a95845",
    "topo6.tables": "aaa8ad926a95ab6f0c13d67d803d29d4af20e1bbecb7bc44786c7b22f2a8498a",
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
        (1, 0, 1),
    }
)
NONZERO_REDUCED_INDICES = frozenset(
    {
        (1, 1, 1),
        (-1, 1, 1),
        (-2, 1, 1),
        (1, -1, 1),
        (1, -2, 1),
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
            "(-d+3)/((d-4)*ipp1p2)*topo6(0,1,1)"
            "+(d-3)/((d-4)*ipp1p2)*topo6(1,0,1)"
        ),
        (-1, 1, 1): "-ipp1p2*topo6(0,1,1)",
        (-2, 1, 1): "d*ipp1p2^2/(d-1)*topo6(0,1,1)",
        (1, -1, 1): "ipp1p2*topo6(1,0,1)",
        (1, -2, 1): "d*ipp1p2^2/(d-1)*topo6(1,0,1)",
    }
)

PREFERRED_MASTERS = tuple(
    wolfram_integral(indices)
    for indices in (
        (0, 1, 1),
        (1, 0, 1),
    )
)

assert len(TARGET_INDICES) == 64
assert len(MASTER_INDICES) == 2
assert len(ZERO_INDICES) == 57
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
