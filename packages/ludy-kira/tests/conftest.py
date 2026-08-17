from __future__ import annotations

from collections.abc import Callable

import pytest
from symbolica import S

from ludy_kira.models import (
    IntegralFamily,
    KinematicInvariant,
    Kinematics,
    KiraProject,
    Propagator,
    ReductionBounds,
    ScalarProductRule,
)
from topo1_oracle import MASTER_INDICES, TARGET_INDICES


@pytest.fixture
def topo1_project() -> KiraProject:
    q1, p1, p2, m, ipp1p2 = S("q1", "p1", "p2", "m", "ipp1p2")
    family = IntegralFamily(
        name="topo1",
        loop_momenta=(q1,),
        propagators=(
            Propagator(q1, m**2),
            Propagator(q1 - p1),
            Propagator(q1 - p2),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(
            KinematicInvariant(m**2, 2, kira_name="m2"),
            KinematicInvariant(ipp1p2, 2),
        ),
        scalar_products=(
            ScalarProductRule(p1, p1, 0),
            ScalarProductRule(p2, p2, 0),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
        symbol_to_replace_by_one=m**2,
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=tuple(
            family(*indices)
            for indices in (
                (1, 1, 1),
                (0, 1, 1),
                (1, 0, 0),
            )
        ),
        check_masters=True,
        reconstruct_mass=True,
    )


@pytest.fixture
def topo1_integral(topo1_project: KiraProject) -> Callable[[tuple[int, int, int]], object]:
    return lambda indices: topo1_project.family(*indices)


@pytest.fixture
def topo1_masters(topo1_project: KiraProject) -> frozenset[object]:
    return frozenset(topo1_project.family(*indices) for indices in MASTER_INDICES)
