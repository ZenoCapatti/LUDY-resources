"""Exact regenerated FIRE oracle for DY topology 20."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from types import MappingProxyType

from symbolica import E, Expression

from ludy_kira.parser import parse_kira2math_file

Index = tuple[int, int, int]

FAMILY_NAME = "topo21"
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "fire_topo21"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "45a6e57c099f461181e5a5b1cde7eddde0cef45b9002ed2a327aed21f3a87d61",
    "ToReduce.m": "cd3a19a8f046e83d9cc2db1d5a60b00ef2452b0a3d139c040f2ed9b93a98155b",
    "topo21.tables": "c14ae5ef81e515f4c94f2dd92ff90113aed9215cc22c29983117556812c0f4c3",
    "decoded-rules.m": "f03f62825ace32360586032eaeb60126e6ae0b8ffd3c5e8318f77bd38b4a0b0b",
    "topo21.rules.m": "f18d395123cb7fd2eb9ae6fe70db78c991aca6d569134d49e91b731b2e13ee79",
}

TARGET_INDICES: tuple[Index, ...] = tuple(
    (first, second, third)
    for first in (1, 0, -1)
    for second in (1, 0, -1)
    for third in (1, 0, -1)
)
MASTER_INDICES = frozenset({(0, 1, 1)})


def symbolica_integral(indices: Index) -> str:
    return f"{FAMILY_NAME}({','.join(map(str, indices))})"


def wolfram_integral(indices: Index) -> str:
    return f"{FAMILY_NAME}[{','.join(map(str, indices))}]"


@cache
def load_fire_rules() -> MappingProxyType[Expression, Expression]:
    rules = parse_kira2math_file(
        FIXTURE_ROOT / "topo21.rules.m",
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
    wolfram_integral(indices) for indices in ((0, 1, 1),)
)

assert len(TARGET_INDICES) == 27
assert len(MASTER_INDICES) == 1
assert len(ZERO_INDICES) == 24
assert len(NONZERO_REDUCED_INDICES) == 2
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
