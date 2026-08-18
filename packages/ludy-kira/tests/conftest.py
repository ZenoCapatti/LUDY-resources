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
from topo2_oracle import (
    MASTER_INDICES as TOPO2_MASTER_INDICES,
    TARGET_INDICES as TOPO2_TARGET_INDICES,
)
from topo3_oracle import (
    MASTER_INDICES as TOPO3_MASTER_INDICES,
    TARGET_INDICES as TOPO3_TARGET_INDICES,
)
from topo4_oracle import (
    MASTER_INDICES as TOPO4_MASTER_INDICES,
    TARGET_INDICES as TOPO4_TARGET_INDICES,
)
from topo5_oracle import (
    MASTER_INDICES as TOPO5_MASTER_INDICES,
    TARGET_INDICES as TOPO5_TARGET_INDICES,
)
from topo6_oracle import (
    MASTER_INDICES as TOPO6_MASTER_INDICES,
    TARGET_INDICES as TOPO6_TARGET_INDICES,
)
from topo7_oracle import (
    MASTER_INDICES as TOPO7_MASTER_INDICES,
    TARGET_INDICES as TOPO7_TARGET_INDICES,
)
from topo8_oracle import (
    MASTER_INDICES as TOPO8_MASTER_INDICES,
    TARGET_INDICES as TOPO8_TARGET_INDICES,
)
from topo10_oracle import (
    MASTER_INDICES as TOPO10_MASTER_INDICES,
    TARGET_INDICES as TOPO10_TARGET_INDICES,
)
from topo11_oracle import (
    MASTER_INDICES as TOPO11_MASTER_INDICES,
    TARGET_INDICES as TOPO11_TARGET_INDICES,
)
from topo20_oracle import (
    MASTER_INDICES as TOPO20_MASTER_INDICES,
    TARGET_INDICES as TOPO20_TARGET_INDICES,
)
from topo21_oracle import (
    MASTER_INDICES as TOPO21_MASTER_INDICES,
    TARGET_INDICES as TOPO21_TARGET_INDICES,
)


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


@pytest.fixture
def topo2_project() -> KiraProject:
    q1, p1, p2, m, ipp1p2 = S("q1", "p1", "p2", "m", "ipp1p2")
    family = IntegralFamily(
        name="topo2",
        loop_momenta=(q1,),
        propagators=(
            Propagator(q1, m**2),
            Propagator(q1 - p1),
            Propagator(q1 - p1 - p2),
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
        targets=tuple(family(*indices) for indices in TOPO2_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=tuple(
            family(*indices)
            for indices in (
                (1, 0, 1),
                (1, 0, 0),
            )
        ),
        check_masters=True,
        reconstruct_mass=True,
    )


@pytest.fixture
def topo2_masters(topo2_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo2_project.family(*indices) for indices in TOPO2_MASTER_INDICES
    )


@pytest.fixture
def topo3_project() -> KiraProject:
    q1, p1, p2, m, ipp1p2 = S("q1", "p1", "p2", "m", "ipp1p2")
    family = IntegralFamily(
        name="topo3",
        loop_momenta=(q1,),
        propagators=(
            Propagator(q1, m**2),
            Propagator(q1 - p2),
            Propagator(q1 - p1 - p2),
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
        targets=tuple(family(*indices) for indices in TOPO3_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=tuple(
            family(*indices)
            for indices in (
                (1, 0, 1),
                (1, 0, 0),
            )
        ),
        check_masters=True,
        reconstruct_mass=True,
    )


@pytest.fixture
def topo3_masters(topo3_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo3_project.family(*indices) for indices in TOPO3_MASTER_INDICES
    )


@pytest.fixture
def topo4_project() -> KiraProject:
    q1, p1, p2, ipp1p2 = S("q1", "p1", "p2", "ipp1p2")
    family = IntegralFamily(
        name="topo4",
        loop_momenta=(q1,),
        propagators=(
            Propagator(q1 - p1),
            Propagator(q1 - p2),
            Propagator(q1 - p1 - p2),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(KinematicInvariant(ipp1p2, 2),),
        scalar_products=(
            ScalarProductRule(p1, p1, 0),
            ScalarProductRule(p2, p2, 0),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TOPO4_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=(family(1, 1, 0),),
        check_masters=True,
    )


@pytest.fixture
def topo4_masters(topo4_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo4_project.family(*indices) for indices in TOPO4_MASTER_INDICES
    )


@pytest.fixture
def topo5_project() -> KiraProject:
    k1, p1, p2, ipp1p2 = S("k1", "p1", "p2", "ipp1p2")
    family = IntegralFamily(
        name="topo5",
        loop_momenta=(k1,),
        propagators=(
            Propagator(k1),
            Propagator(k1 - p1),
            Propagator(k1 + p2),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(KinematicInvariant(ipp1p2, 2),),
        scalar_products=(
            ScalarProductRule(p1, p1, 0),
            ScalarProductRule(p2, p2, 0),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TOPO5_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=(family(0, 1, 1),),
        check_masters=True,
    )


@pytest.fixture
def topo5_masters(topo5_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo5_project.family(*indices) for indices in TOPO5_MASTER_INDICES
    )


@pytest.fixture
def topo6_project() -> KiraProject:
    k1, p1, p2, ipp1p2, ipp2p2 = S("k1", "p1", "p2", "ipp1p2", "ipp2p2")
    family = IntegralFamily(
        name="topo6",
        loop_momenta=(k1,),
        propagators=(
            Propagator(k1),
            Propagator(k1 - p1),
            Propagator(k1 + p2),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(
            KinematicInvariant(ipp1p2, 2),
            KinematicInvariant(ipp2p2, 2),
        ),
        scalar_products=(
            ScalarProductRule(p1, p1, 0),
            ScalarProductRule(p2, p2, ipp2p2),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TOPO6_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=(family(0, 1, 1), family(1, 0, 1)),
        check_masters=True,
    )


@pytest.fixture
def topo6_masters(topo6_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo6_project.family(*indices) for indices in TOPO6_MASTER_INDICES
    )


@pytest.fixture
def topo7_project() -> KiraProject:
    k1, p1, p2, ipp1p1, ipp1p2 = S("k1", "p1", "p2", "ipp1p1", "ipp1p2")
    family = IntegralFamily(
        name="topo7",
        loop_momenta=(k1,),
        propagators=(
            Propagator(k1),
            Propagator(k1 - p1),
            Propagator(k1 + p2),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(
            KinematicInvariant(ipp1p1, 2),
            KinematicInvariant(ipp1p2, 2),
        ),
        scalar_products=(
            ScalarProductRule(p1, p1, ipp1p1),
            ScalarProductRule(p2, p2, 0),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TOPO7_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=(family(0, 1, 1), family(1, 1, 0)),
        check_masters=True,
    )


@pytest.fixture
def topo7_masters(topo7_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo7_project.family(*indices) for indices in TOPO7_MASTER_INDICES
    )


@pytest.fixture
def topo8_project() -> KiraProject:
    k1, p1, p2, ipp1p1, ipp1p2, ipp2p2 = S(
        "k1", "p1", "p2", "ipp1p1", "ipp1p2", "ipp2p2"
    )
    family = IntegralFamily(
        name="topo8",
        loop_momenta=(k1,),
        propagators=(
            Propagator(k1),
            Propagator(k1 - p1),
            Propagator(k1 - p2),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(
            KinematicInvariant(ipp1p1, 2),
            KinematicInvariant(ipp1p2, 2),
            KinematicInvariant(ipp2p2, 2),
        ),
        scalar_products=(
            ScalarProductRule(p1, p1, ipp1p1),
            ScalarProductRule(p2, p2, ipp2p2),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TOPO8_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=tuple(
            family(*indices)
            for indices in (
                (1, 1, 1),
                (1, 1, 0),
                (1, 0, 1),
                (0, 1, 1),
            )
        ),
        check_masters=True,
    )


@pytest.fixture
def topo8_masters(topo8_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo8_project.family(*indices) for indices in TOPO8_MASTER_INDICES
    )


@pytest.fixture
def topo10_project() -> KiraProject:
    q1, p1, p2, msq, ipp1p2 = S("q1", "p1", "p2", "msq", "ipp1p2")
    family = IntegralFamily(
        name="topo10",
        loop_momenta=(q1,),
        propagators=(
            Propagator(q1),
            Propagator(q1 - p1),
            Propagator(q1 - p1 - p2, msq),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(
            KinematicInvariant(msq, 2),
            KinematicInvariant(ipp1p2, 2),
        ),
        scalar_products=(
            ScalarProductRule(p1, p1, 0),
            ScalarProductRule(p2, p2, 0),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
        symbol_to_replace_by_one=msq,
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TOPO10_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=6, d=3),
        preferred_masters=tuple(
            family(*indices) for indices in ((0, 0, 1), (1, 0, 1))
        ),
        check_masters=True,
        reconstruct_mass=True,
    )


@pytest.fixture
def topo10_masters(topo10_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo10_project.family(*indices) for indices in TOPO10_MASTER_INDICES
    )


@pytest.fixture
def topo11_project() -> KiraProject:
    q1, p1, p2, msq, ipp1p1, ipp1p2 = S(
        "q1", "p1", "p2", "msq", "ipp1p1", "ipp1p2"
    )
    family = IntegralFamily(
        name="topo11",
        loop_momenta=(q1,),
        propagators=(
            Propagator(q1),
            Propagator(q1 - p1),
            Propagator(q1 - p1 - p2, msq),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(
            KinematicInvariant(msq, 2),
            KinematicInvariant(ipp1p1, 2),
            KinematicInvariant(ipp1p2, 2),
        ),
        scalar_products=(
            ScalarProductRule(p1, p1, ipp1p1),
            ScalarProductRule(p2, p2, 0),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
        symbol_to_replace_by_one=msq,
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TOPO11_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=6, d=3),
        preferred_masters=tuple(
            family(*indices)
            for indices in ((0, 0, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1))
        ),
        check_masters=True,
        reconstruct_mass=True,
    )


@pytest.fixture
def topo11_masters(topo11_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo11_project.family(*indices) for indices in TOPO11_MASTER_INDICES
    )


@pytest.fixture
def topo20_project() -> KiraProject:
    q1, p1, p2, msq, ipp1p2 = S("q1", "p1", "p2", "msq", "ipp1p2")
    family = IntegralFamily(
        name="topo20",
        loop_momenta=(q1,),
        propagators=(
            Propagator(q1),
            Propagator(q1 - p1),
            Propagator(q1 - p1 - p2, msq),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(
            KinematicInvariant(msq, 2),
            KinematicInvariant(ipp1p2, 2),
        ),
        scalar_products=(
            ScalarProductRule(p1, p1, 0),
            ScalarProductRule(p2, p2, 0),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
        symbol_to_replace_by_one=msq,
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TOPO20_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=tuple(
            family(*indices) for indices in ((0, 0, 1), (1, 0, 1))
        ),
        check_masters=True,
        reconstruct_mass=True,
    )


@pytest.fixture
def topo20_masters(topo20_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo20_project.family(*indices) for indices in TOPO20_MASTER_INDICES
    )


@pytest.fixture
def topo21_project() -> KiraProject:
    q1, p1, p2, ipp1p2 = S("q1", "p1", "p2", "ipp1p2")
    family = IntegralFamily(
        name="topo21",
        loop_momenta=(q1,),
        propagators=(
            Propagator(q1),
            Propagator(q1 - p1),
            Propagator(q1 - p2),
        ),
        top_level_sectors=(7,),
    )
    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(KinematicInvariant(ipp1p2, 2),),
        scalar_products=(
            ScalarProductRule(p1, p1, 0),
            ScalarProductRule(p2, p2, 0),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TOPO21_TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=(family(0, 1, 1),),
        check_masters=True,
    )


@pytest.fixture
def topo21_masters(topo21_project: KiraProject) -> frozenset[object]:
    return frozenset(
        topo21_project.family(*indices) for indices in TOPO21_MASTER_INDICES
    )
