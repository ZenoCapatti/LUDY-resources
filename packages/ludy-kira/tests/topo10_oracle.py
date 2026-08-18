"""Exact regenerated FIRE oracle for DY topology 10."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from types import MappingProxyType

from symbolica import E, Expression

from ludy_kira.parser import parse_kira2math_file

Index = tuple[int, int, int]

FAMILY_NAME = "topo10"
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "fire_topo10"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "37f890f88aadd91e19378514e2f3e4ff4fa94ead4ab0356ab548d93a51fd209a",
    "ToReduce.m": "0767735cff6f21119f2ea25142f9807d7d6e505c2e504f42a8850ee71a491ab6",
    "topo10.tables": "6d57d07b1ba42285815d61bcd96059f856df1c9160d1e8a7765eb0acde4f0799",
    "decoded-rules.m": "c1676fa44aea303105b4e86744af6fe133fa77135f8b63086ef8d9880d2e1e5a",
    "topo10.rules.m": "7809c30d2f0942cfbd0e31290f34a52d4a2d2e49482892abc8ca9ae17acfb669",
}

# This is the exact Cartesian-product ordering in the notebook's ToReduce.m.
TARGET_INDICES: tuple[Index, ...] = tuple(
    (first, second, third)
    for first in (2, 1, 0, -1, -2)
    for second in (2, 1, 0, -1, -2)
    for third in (2, 1, 0, -1, -2)
)

MASTER_INDICES = frozenset({(0, 0, 1), (1, 0, 1)})


def symbolica_integral(indices: Index) -> str:
    """Return the canonical Symbolica spelling used by the oracle."""

    return f"{FAMILY_NAME}({','.join(map(str, indices))})"


def wolfram_integral(indices: Index) -> str:
    """Return the line format accepted by Kira target/master files."""

    return f"{FAMILY_NAME}[{','.join(map(str, indices))}]"


@cache
def load_fire_rules() -> MappingProxyType[Expression, Expression]:
    """Load the exact decoded FIRE rules and synthesize master identities."""

    rules = parse_kira2math_file(
        FIXTURE_ROOT / "topo10.rules.m",
        family_name=FAMILY_NAME,
        arity=3,
    )
    for indices in MASTER_INDICES:
        master = E(symbolica_integral(indices))
        rules.setdefault(master, master)
    return MappingProxyType(rules)


EXPECTED_RHS = MappingProxyType(
    {
        indices: load_fire_rules()[E(symbolica_integral(indices))]
        for indices in TARGET_INDICES
    }
)
ZERO_INDICES = frozenset(
    indices for indices, right in EXPECTED_RHS.items() if right == E("0")
)
NONZERO_REDUCED_INDICES = frozenset(
    set(TARGET_INDICES) - MASTER_INDICES - ZERO_INDICES
)

PREFERRED_MASTERS = tuple(
    wolfram_integral(indices) for indices in ((0, 0, 1), (1, 0, 1))
)

assert len(TARGET_INDICES) == 125
assert len(MASTER_INDICES) == 2
assert len(ZERO_INDICES) == 75
assert len(NONZERO_REDUCED_INDICES) == 48
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
