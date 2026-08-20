from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml
from symbolica import E, Expression, Replacement

from crossed_box_support import (
    CROSSED_BOX_SPECS,
    TARGET_INDICES,
    CrossedBoxSpec,
    build_project,
    expected_rhs,
    zero_indices,
)
from kirapy import Kira
from integration_support import load_native_final_masters

SPEC_IDS = tuple(spec.family_name for spec in CROSSED_BOX_SPECS)


def _assert_exact_equal(
    actual: Expression,
    expected: Expression,
    *,
    spec: CrossedBoxSpec,
    indices: tuple[int, int, int],
) -> None:
    delta = (actual - expected).together().cancel()
    assert delta == E("0"), (
        f"{spec.family_name}{indices} differs after exact normalization:\n"
        f"actual   = {actual}\nexpected = {expected}\ndelta    = {delta}"
    )


@pytest.mark.parametrize("spec", CROSSED_BOX_SPECS, ids=SPEC_IDS)
def test_real_kira_matches_regenerated_fire_crossed_box(
    tmp_path: Path,
    spec: CrossedBoxSpec,
) -> None:
    if os.environ.get("KIRAPY_RUN_INTEGRATION") != "1":
        pytest.skip("set KIRAPY_RUN_INTEGRATION=1 to run the native Kira parity test")

    project = build_project(spec)
    kira = Kira(executable=os.environ.get("KIRA_BIN", "kira"))
    kira.doctor().raise_for_errors()
    workdir = tmp_path / spec.family_name
    result = kira.reduce(
        family=project.family,
        kinematics=project.kinematics,
        targets=project.targets,
        bounds=project.bounds,
        preferred_masters=project.preferred_masters,
        check_masters=project.check_masters,
        reconstruct_mass=project.reconstruct_mass,
        require_complete=True,
        workdir=workdir,
        timeout=120,
    )

    jobs = yaml.safe_load((workdir / "jobs.yaml").read_text(encoding="utf-8"))
    assert jobs["jobs"][0]["reduce_sectors"]["reduce"] == [
        {"sectors": ["b111"], "r": 9, "s": 4, "d": 2}
    ]
    assert jobs["jobs"][0]["reduce_sectors"]["preferred_masters"] == (
        "preferred_masters"
    )
    assert jobs["jobs"][0]["reduce_sectors"]["check_masters"] is True
    kira2math = jobs["jobs"][1]["kira2math"]
    if spec.has_internal_mass:
        assert kira2math["reconstruct_mass"] is True
    else:
        assert "reconstruct_mass" not in kira2math

    requested = set(project.targets)
    fire_masters = tuple(
        project.family(*indices) for indices in spec.master_indices
    )
    assert set(result.requested_targets) == requested
    assert set(result.rules) == requested
    assert result.complete
    assert result.missing_targets == ()
    assert result.unresolved_integrals == ()
    assert result.symbol_aliases
    assert set(result.zero_integrals) == {
        project.family(*indices) for indices in zero_indices(spec.topology_id)
    }

    bridge = [Replacement(master, result.rules[master]) for master in fire_masters]
    fire_expected = expected_rhs(spec.topology_id)
    for indices in TARGET_INDICES:
        target = project.family(*indices)
        expected = fire_expected[indices].replace_multiple(bridge, repeat=False)
        _assert_exact_equal(
            result.rules[target],
            expected,
            spec=spec,
            indices=indices,
        )

    final_masters = load_native_final_masters(workdir, project.family)
    assert set(final_masters) == set(result.masters)
