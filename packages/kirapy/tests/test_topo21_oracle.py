from __future__ import annotations

import hashlib

import pytest
from symbolica import E

from kirapy.result import ReductionResult
from topo21_oracle import (
    EXPECTED_RHS,
    FIRE_SOURCE_SHA256,
    FIXTURE_ROOT,
    MASTER_INDICES,
    NONZERO_REDUCED_INDICES,
    PREFERRED_MASTERS,
    TARGET_INDICES,
    ZERO_INDICES,
    load_fire_rules,
    symbolica_integral,
)


def test_fire_topo21_oracle_is_a_total_complete_partition() -> None:
    requested = tuple(E(symbolica_integral(indices)) for indices in TARGET_INDICES)
    masters = tuple(E(symbolica_integral(indices)) for indices in MASTER_INDICES)
    oracle = ReductionResult(
        family_name="topo21",
        arity=3,
        requested_targets=requested,
        rules=load_fire_rules(),
        masters=masters,
        workdir=FIXTURE_ROOT,
    )

    assert len(TARGET_INDICES) == 27
    assert len(MASTER_INDICES) == 1
    assert len(ZERO_INDICES) == 24
    assert len(NONZERO_REDUCED_INDICES) == 2
    assert set(EXPECTED_RHS) == set(TARGET_INDICES)
    assert set(oracle.rules) == set(requested)
    assert oracle.complete
    assert oracle.missing_targets == ()
    assert oracle.unresolved_integrals == ()
    assert set(oracle.zero_integrals) == {
        E(symbolica_integral(indices)) for indices in ZERO_INDICES
    }
    assert PREFERRED_MASTERS == ("topo21[0,1,1]",)


@pytest.mark.parametrize(("filename", "expected"), FIRE_SOURCE_SHA256.items())
def test_fire_topo21_oracle_provenance(filename: str, expected: str) -> None:
    source = FIXTURE_ROOT / filename
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    assert actual == expected
