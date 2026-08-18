from __future__ import annotations

import hashlib

import pytest
from symbolica import E

from crossed_box_support import (
    CROSSED_BOX_SPECS,
    TARGET_INDICES,
    CrossedBoxSpec,
    build_project,
    expected_rhs,
    load_fire_rules,
    nontrivial_indices,
    symbolica_integral,
    zero_indices,
)
from ludy_kira.result import ReductionResult

SPEC_IDS = tuple(spec.family_name for spec in CROSSED_BOX_SPECS)

assert tuple(spec.topology_id for spec in CROSSED_BOX_SPECS) == tuple(range(22, 32))


@pytest.mark.parametrize("spec", CROSSED_BOX_SPECS, ids=SPEC_IDS)
def test_crossed_box_fire_oracle_is_a_total_complete_partition(
    spec: CrossedBoxSpec,
) -> None:
    requested = tuple(
        E(symbolica_integral(spec, indices)) for indices in TARGET_INDICES
    )
    masters = tuple(
        E(symbolica_integral(spec, indices)) for indices in spec.master_indices
    )
    oracle = ReductionResult(
        family_name=spec.family_name,
        arity=3,
        requested_targets=requested,
        rules=load_fire_rules(spec.topology_id),
        masters=masters,
        workdir=spec.fixture_root,
    )
    zeros = zero_indices(spec.topology_id)
    nontrivial = nontrivial_indices(spec.topology_id)

    assert len(TARGET_INDICES) == 27
    assert len(zeros) == spec.expected_zero_count
    assert len(nontrivial) == spec.expected_nontrivial_count
    assert set(expected_rhs(spec.topology_id)) == set(TARGET_INDICES)
    assert set(oracle.rules) == set(requested)
    assert oracle.complete
    assert oracle.missing_targets == ()
    assert oracle.unresolved_integrals == ()
    assert set(oracle.zero_integrals) == {
        E(symbolica_integral(spec, indices)) for indices in zeros
    }

    project = build_project(spec)
    assert project.targets == requested
    assert project.preferred_masters == masters
    assert project.bounds.sectors == (7,)
    assert project.bounds.r == 9
    assert project.bounds.s == 4
    assert project.bounds.d == 2
    assert project.check_masters is True
    assert project.reconstruct_mass is spec.has_internal_mass


@pytest.mark.parametrize("spec", CROSSED_BOX_SPECS, ids=SPEC_IDS)
def test_crossed_box_fire_oracle_provenance(spec: CrossedBoxSpec) -> None:
    for filename, expected in spec.source_sha256.items():
        source = spec.fixture_root / filename
        actual = hashlib.sha256(source.read_bytes()).hexdigest()
        assert actual == expected, f"unexpected SHA-256 for {source}"
