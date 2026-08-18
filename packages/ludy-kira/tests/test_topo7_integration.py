from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml
from symbolica import E, Replacement

from ludy_kira import Kira
from ludy_kira.models import KiraProject
from ludy_kira.parser import parse_masters_file
from topo7_oracle import EXPECTED_RHS, MASTER_INDICES, TARGET_INDICES, ZERO_INDICES


def _assert_exact_equal(actual, expected, *, indices) -> None:
    delta = (actual - expected).together().cancel()
    assert delta == E("0"), (
        f"topo7{indices} differs after exact normalization:\n"
        f"actual   = {actual}\nexpected = {expected}\ndelta    = {delta}"
    )


def test_real_kira_matches_checked_fire_topo7(
    tmp_path: Path,
    topo7_project: KiraProject,
) -> None:
    """Run the full 64-target DY topology-6 fixture through Kira 3.1."""

    if os.environ.get("LUDY_KIRA_RUN_INTEGRATION") != "1":
        pytest.skip("set LUDY_KIRA_RUN_INTEGRATION=1 to run the native Kira parity test")

    kira = Kira(executable=os.environ.get("KIRA_BIN", "kira"))
    kira.doctor().raise_for_errors()
    workdir = tmp_path / "topo7"

    result = kira.reduce(
        family=topo7_project.family,
        kinematics=topo7_project.kinematics,
        targets=topo7_project.targets,
        bounds=topo7_project.bounds,
        preferred_masters=topo7_project.preferred_masters,
        check_masters=True,
        workdir=workdir,
        timeout=60,
    )

    jobs = yaml.safe_load((workdir / "jobs.yaml").read_text(encoding="utf-8"))
    assert jobs["jobs"][0]["reduce_sectors"]["reduce"] == [
        {"sectors": ["b111"], "r": 9, "s": 4, "d": 2}
    ]
    assert jobs["jobs"][0]["reduce_sectors"]["preferred_masters"] == "preferred_masters"
    assert jobs["jobs"][0]["reduce_sectors"]["check_masters"] is True
    assert "reconstruct_mass" not in jobs["jobs"][1]["kira2math"]

    requested = {topo7_project.family(*indices) for indices in TARGET_INDICES}
    fire_masters = {topo7_project.family(*indices) for indices in MASTER_INDICES}
    assert set(result.requested_targets) == requested
    assert set(result.rules) == requested
    assert result.complete
    assert result.missing_targets == ()
    assert result.unresolved_integrals == ()
    assert dict(result.invariant_aliases) == {}
    assert set(result.zero_integrals) == {
        topo7_project.family(*indices) for indices in ZERO_INDICES
    }

    bridge = [
        Replacement(master, result.rules[master])
        for master in fire_masters
    ]
    for indices in TARGET_INDICES:
        target = topo7_project.family(*indices)
        actual = result.rules[target]
        expected = E(EXPECTED_RHS[indices]).replace_multiple(bridge, repeat=False)
        _assert_exact_equal(actual, expected, indices=indices)

    assert set(result.masters) == fire_masters
    final_masters = parse_masters_file(
        workdir / "results" / "topo7" / "masters.final",
        family_name="topo7",
        arity=3,
    )
    assert set(final_masters) == fire_masters
