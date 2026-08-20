"""Exact regenerated FIRE oracle for DY topology 20."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from types import MappingProxyType

from symbolica import E, Expression

from kirapy.parser import parse_kira2math_file

Index = tuple[int, int, int]

FAMILY_NAME = "topo20"
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "fire_topo20"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "04141e0305c543ca60fe678f6cea38407b4e843d569d88f06315e4ff643f12d0",
    "ToReduce.m": "4c562b7e3c9b4d59423f6da423f0da7bf0414af1819cd49f0481e2629192ec8d",
    "topo20.tables": "192851e2e202a0039bbf67f27b8004d5798ac7a3275ed9e9fc1b45acdd842066",
    "decoded-rules.m": "d7df7edfc60381ced5e68a72b0419ac1896dff458df9c06356249df592fc3f16",
    "topo20.rules.m": "dad55f2557fe222d06e1a1d8cb91b5c22e6fa0ecb66f2965035bd78f2d330cc6",
}

TARGET_INDICES: tuple[Index, ...] = tuple(
    (first, second, third)
    for first in (1, 0, -1)
    for second in (1, 0, -1)
    for third in (1, 0, -1)
)
MASTER_INDICES = frozenset({(0, 0, 1), (1, 0, 1)})


def symbolica_integral(indices: Index) -> str:
    return f"{FAMILY_NAME}({','.join(map(str, indices))})"


def wolfram_integral(indices: Index) -> str:
    return f"{FAMILY_NAME}[{','.join(map(str, indices))}]"


@cache
def load_fire_rules() -> MappingProxyType[Expression, Expression]:
    rules = parse_kira2math_file(
        FIXTURE_ROOT / "topo20.rules.m",
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

assert len(TARGET_INDICES) == 27
assert len(MASTER_INDICES) == 2
assert len(ZERO_INDICES) == 18
assert len(NONZERO_REDUCED_INDICES) == 7
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
