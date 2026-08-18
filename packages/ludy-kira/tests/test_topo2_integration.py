from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml
from symbolica import E, Replacement, S

from ludy_kira import Kira
from ludy_kira.models import KiraProject
from ludy_kira.parser import parse_masters_file
from topo2_oracle import EXPECTED_RHS, MASTER_INDICES, TARGET_INDICES, ZERO_INDICES


def _assert_exact_equal(actual, expected, *, indices) -> None:
    delta = (actual - expected).together().cancel()
    assert delta == E("0"), (
        f"topo2{indices} differs after exact normalization:\n"
        f"actual   = {actual}\nexpected = {expected}\ndelta    = {delta}"
    )


def test_real_kira_matches_checked_fire_topo2(
    tmp_path: Path,
    topo2_project: KiraProject,
) -> None:
    """Run the full 27-target DY topology-2 fixture through Kira 3.1."""

    if os.environ.get("LUDY_KIRA_RUN_INTEGRATION") != "1":
        pytest.skip("set LUDY_KIRA_RUN_INTEGRATION=1 to run the native Kira parity test")

    kira = Kira(executable=os.environ.get("KIRA_BIN", "kira"))
    kira.doctor().raise_for_errors()
    workdir = tmp_path / "topo2"

    result = kira.reduce(
        family=topo2_project.family,
        kinematics=topo2_project.kinematics,
        targets=topo2_project.targets,
        bounds=topo2_project.bounds,
        preferred_masters=topo2_project.preferred_masters,
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
    assert jobs["jobs"][1]["kira2math"]["reconstruct_mass"] is True

    requested = {topo2_project.family(*indices) for indices in TARGET_INDICES}
    fire_masters = {topo2_project.family(*indices) for indices in MASTER_INDICES}
    assert set(result.requested_targets) == requested
    assert set(result.rules) == requested
    assert result.complete
    assert result.missing_targets == ()
    assert result.unresolved_integrals == ()
    assert dict(result.invariant_aliases) == {"m2": S("m") ** 2}
    assert all("m2" not in right.format_plain() for right in result.rules.values())
    assert set(result.zero_integrals) == {
        topo2_project.family(*indices) for indices in ZERO_INDICES
    }

    # Reduce FIRE's masters through Kira before comparing. This remains valid
    # if Kira selects a different basis despite the preferred-master request.
    bridge = [
        Replacement(master, result.rules[master])
        for master in fire_masters
    ]
    for indices in TARGET_INDICES:
        target = topo2_project.family(*indices)
        actual = result.rules[target]
        expected = E(EXPECTED_RHS[indices]).replace_multiple(bridge, repeat=False)
        _assert_exact_equal(actual, expected, indices=indices)

    assert set(result.masters) == fire_masters
    final_masters = parse_masters_file(
        workdir / "results" / "topo2" / "masters.final",
        family_name="topo2",
        arity=3,
    )
    assert set(final_masters) == fire_masters
