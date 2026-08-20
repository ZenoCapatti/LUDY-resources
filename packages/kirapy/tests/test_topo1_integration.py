from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml
from symbolica import E, Replacement, S

from kirapy import Kira
from kirapy.models import KiraProject
from integration_support import load_native_final_masters
from topo1_oracle import EXPECTED_RHS, MASTER_INDICES, TARGET_INDICES, ZERO_INDICES

def _assert_exact_equal(actual, expected, *, indices) -> None:
    delta = (actual - expected).together().cancel()
    assert delta == E("0"), (
        f"topo1{indices} differs after exact normalization:\n"
        f"actual   = {actual}\nexpected = {expected}\ndelta    = {delta}"
    )


def test_real_kira_matches_checked_fire_topo1(
    tmp_path: Path,
    topo1_project: KiraProject,
) -> None:
    """Run the full 27-target DY fixture through a real Kira 3.1 executable."""

    if os.environ.get("KIRAPY_RUN_INTEGRATION") != "1":
        pytest.skip("set KIRAPY_RUN_INTEGRATION=1 to run the native Kira parity test")

    kira = Kira(executable=os.environ.get("KIRA_BIN", "kira"))
    kira.doctor().raise_for_errors()
    workdir = tmp_path / "topo1"

    # reconstruct_mass is intentionally omitted.  The facade must infer it
    # from symbol_to_replace_by_one=m2; otherwise Kira silently exports m2=1.
    result = kira.reduce(
        family=topo1_project.family,
        kinematics=topo1_project.kinematics,
        targets=topo1_project.targets,
        bounds=topo1_project.bounds,
        preferred_masters=topo1_project.preferred_masters,
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

    requested = {topo1_project.family(*indices) for indices in TARGET_INDICES}
    fire_masters = {topo1_project.family(*indices) for indices in MASTER_INDICES}
    assert set(result.requested_targets) == requested
    assert set(result.rules) == requested
    assert result.complete
    assert result.missing_targets == ()
    assert result.unresolved_integrals == ()
    assert S("m") ** 2 in result.symbol_aliases.values()
    assert all("m2" not in right.format_plain() for right in result.rules.values())
    assert set(result.zero_integrals) == {
        topo1_project.family(*indices) for indices in ZERO_INDICES
    }

    # Always perform the basis-independent comparison.  Reducing each FIRE
    # master through Kira provides the bridge even if Kira changes basis.
    bridge = [
        Replacement(master, result.rules[master])
        for master in fire_masters
    ]
    for indices in TARGET_INDICES:
        target = topo1_project.family(*indices)
        actual = result.rules[target]
        expected = E(EXPECTED_RHS[indices]).replace_multiple(bridge, repeat=False)
        _assert_exact_equal(actual, expected, indices=indices)

    # The preferred-master contract is a separate, stronger golden assertion.
    assert set(result.masters) == fire_masters
    final_masters = load_native_final_masters(workdir, topo1_project.family)
    assert set(final_masters) == fire_masters
