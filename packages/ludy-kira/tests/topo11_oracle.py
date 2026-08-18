"""Exact regenerated FIRE oracle for DY topology 11."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from types import MappingProxyType

from symbolica import E, Expression

from ludy_kira.parser import parse_kira2math_file

Index = tuple[int, int, int]

FAMILY_NAME = "topo11"
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "fire_topo11"

FIRE_SOURCE_SHA256 = {
    "FIREinput.m": "0ab60f59a9370f3f297d6222b204dadddb2551aed161e77c7da62d7c8fb718c9",
    "ToReduce.m": "7f237226fa03df3cc6cf9576883fb5632ddbc7101a9d3bab8262a13d8142a406",
    "topo11.tables": "10e51a88cd4580f13345a3e2fa09b815db51428bf17e7219f9528df98dcfd068",
    "decoded-rules.m": "5d2d324b3bc3d72ba326a80e45e82c27a83e706bc672c656a9208a63d08a35ee",
    "topo11.rules.m": "0314c908ac2a2d373b819564bc6a5b4651c3c82237b0f01b3d728902d5f0e8f8",
}

# This is the exact Cartesian-product ordering in the notebook's ToReduce.m.
TARGET_INDICES: tuple[Index, ...] = tuple(
    (first, second, third)
    for first in (2, 1, 0, -1, -2)
    for second in (2, 1, 0, -1, -2)
    for third in (2, 1, 0, -1, -2)
)

MASTER_INDICES = frozenset({(0, 0, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1)})


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
        FIXTURE_ROOT / "topo11.rules.m",
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
    wolfram_integral(indices)
    for indices in ((0, 0, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1))
)

assert len(TARGET_INDICES) == 125
assert len(MASTER_INDICES) == 4
assert len(ZERO_INDICES) == 63
assert len(NONZERO_REDUCED_INDICES) == 58
assert set(EXPECTED_RHS) == set(TARGET_INDICES)
