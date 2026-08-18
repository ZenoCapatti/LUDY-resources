import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    from symbolica import S

    from ludy_kira import (
        IntegralFamily,
        KinematicInvariant,
        Kinematics,
        Kira,
        Propagator,
        ReductionBounds,
        ScalarProductRule,
    )

    return (
        IntegralFamily,
        KinematicInvariant,
        Kinematics,
        Kira,
        Path,
        Propagator,
        ReductionBounds,
        S,
        ScalarProductRule,
        mo,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DY topologies 1–8, 10–11, and 20–31: FIRE to Kira

    This is the portable Python counterpart of the validated IBP-reduction jobs in
    [`DY_calculation.nb`](../mathematica/DY_calculation.nb).
    It recreates the selected topology and its complete requested target set from the
    retained FIRE fixture, asks Kira for a complete reduction, and parses the
    result into exact Symbolica expressions.

    Kira is never launched merely by opening the notebook. Inspect the complete
    project below, then use the run button when ready.
    """)
    return


@app.cell
def _(mo):
    topology_choice = mo.ui.radio(
        options=[
            "topo1",
            "topo2",
            "topo3",
            "topo4",
            "topo5",
            "topo6",
            "topo7",
            "topo8",
            "topo10",
            "topo11",
            "topo20",
            "topo21",
            "topo22",
            "topo23",
            "topo24",
            "topo25",
            "topo26",
            "topo27",
            "topo28",
            "topo29",
            "topo30",
            "topo31",
        ],
        value="topo1",
        label="Topology",
        inline=True,
    )
    topology_choice
    return (topology_choice,)


@app.cell
def _(
    IntegralFamily,
    KinematicInvariant,
    Kinematics,
    Path,
    Propagator,
    ReductionBounds,
    S,
    ScalarProductRule,
    topology_choice,
):
    q1, k1, p1, p2, m, msq, ipp1p1, ipp1p2, ipp2p2 = S(
        "q1", "k1", "p1", "p2", "m", "msq", "ipp1p1", "ipp1p2", "ipp2p2"
    )

    families = {
        "topo1": IntegralFamily(
            name="topo1",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1, m**2),
                Propagator(q1 - p1),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo2": IntegralFamily(
            name="topo2",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1, m**2),
                Propagator(q1 - p1),
                Propagator(q1 - p1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo3": IntegralFamily(
            name="topo3",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1, m**2),
                Propagator(q1 - p2),
                Propagator(q1 - p1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo4": IntegralFamily(
            name="topo4",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1 - p1),
                Propagator(q1 - p2),
                Propagator(q1 - p1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo5": IntegralFamily(
            name="topo5",
            loop_momenta=(k1,),
            propagators=(
                Propagator(k1),
                Propagator(k1 - p1),
                Propagator(k1 + p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo6": IntegralFamily(
            name="topo6",
            loop_momenta=(k1,),
            propagators=(
                Propagator(k1),
                Propagator(k1 - p1),
                Propagator(k1 + p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo7": IntegralFamily(
            name="topo7",
            loop_momenta=(k1,),
            propagators=(
                Propagator(k1),
                Propagator(k1 - p1),
                Propagator(k1 + p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo8": IntegralFamily(
            name="topo8",
            loop_momenta=(k1,),
            propagators=(
                Propagator(k1),
                Propagator(k1 - p1),
                Propagator(k1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo10": IntegralFamily(
            name="topo10",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1),
                Propagator(q1 - p1 - p2, msq),
            ),
            top_level_sectors=(7,),
        ),
        "topo11": IntegralFamily(
            name="topo11",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1),
                Propagator(q1 - p1 - p2, msq),
            ),
            top_level_sectors=(7,),
        ),
        "topo20": IntegralFamily(
            name="topo20",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1),
                Propagator(q1 - p1 - p2, msq),
            ),
            top_level_sectors=(7,),
        ),
        "topo21": IntegralFamily(
            name="topo21",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo22": IntegralFamily(
            name="topo22",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1 - p2, msq),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo23": IntegralFamily(
            name="topo23",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1 - p1),
                Propagator(q1 - p1 - p2, msq),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo24": IntegralFamily(
            name="topo24",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1),
                Propagator(q1 - p1 - p2, msq),
            ),
            top_level_sectors=(7,),
        ),
        "topo25": IntegralFamily(
            name="topo25",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo26": IntegralFamily(
            name="topo26",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1 - p2, msq),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo27": IntegralFamily(
            name="topo27",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1 - p1),
                Propagator(q1 - p1 - p2, msq),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo28": IntegralFamily(
            name="topo28",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1),
                Propagator(q1 - p1 - p2, msq),
            ),
            top_level_sectors=(7,),
        ),
        "topo29": IntegralFamily(
            name="topo29",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo30": IntegralFamily(
            name="topo30",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1),
                Propagator(q1 - p1 - p2, msq),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
        "topo31": IntegralFamily(
            name="topo31",
            loop_momenta=(q1,),
            propagators=(
                Propagator(q1 - p1),
                Propagator(q1 - p1 - p2, msq),
                Propagator(q1 - p2),
            ),
            top_level_sectors=(7,),
        ),
    }
    family = families[topology_choice.value]
    massive_kinematics = Kinematics(
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
    massless_kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(KinematicInvariant(ipp1p2, 2),),
        scalar_products=(
            ScalarProductRule(p1, p1, 0),
            ScalarProductRule(p2, p2, 0),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
    )
    p2_massive_kinematics = Kinematics(
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
    p1_massive_kinematics = Kinematics(
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
    p2_massive_internal_kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=(
            KinematicInvariant(msq, 2),
            KinematicInvariant(ipp1p2, 2),
            KinematicInvariant(ipp2p2, 2),
        ),
        scalar_products=(
            ScalarProductRule(p1, p1, 0),
            ScalarProductRule(p2, p2, ipp2p2),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
        symbol_to_replace_by_one=msq,
    )
    p1_massive_internal_kinematics = Kinematics(
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
    fully_off_shell_kinematics = Kinematics(
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
    topo10_kinematics = Kinematics(
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
    topo11_kinematics = Kinematics(
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
    if family.name == "topo11":
        kinematics = topo11_kinematics
    elif family.name in {"topo28", "topo30", "topo31"}:
        kinematics = p1_massive_internal_kinematics
    elif family.name in {"topo24", "topo26", "topo27"}:
        kinematics = p2_massive_internal_kinematics
    elif family.name in {"topo10", "topo20", "topo22", "topo23"}:
        kinematics = topo10_kinematics
    elif family.name == "topo8":
        kinematics = fully_off_shell_kinematics
    elif family.name in {"topo6", "topo25"}:
        kinematics = p2_massive_kinematics
    elif family.name in {"topo7", "topo29"}:
        kinematics = p1_massive_kinematics
    elif family.name in {"topo4", "topo5", "topo21"}:
        kinematics = massless_kinematics
    else:
        kinematics = massive_kinematics
    topology_1_to_4_target_indices = (
        (1, 1, 1),
        (1, 1, 0),
        (1, 1, -1),
        (1, 0, 1),
        (1, 0, 0),
        (1, 0, -1),
        (1, -1, 1),
        (1, -1, 0),
        (1, -1, -1),
        (0, 1, 1),
        (0, 1, 0),
        (0, 1, -1),
        (0, 0, 1),
        (0, 0, 0),
        (0, 0, -1),
        (0, -1, 1),
        (0, -1, 0),
        (0, -1, -1),
        (-1, 1, 1),
        (-1, 1, 0),
        (-1, 1, -1),
        (-1, 0, 1),
        (-1, 0, 0),
        (-1, 0, -1),
        (-1, -1, 1),
        (-1, -1, 0),
        (-1, -1, -1),
    )
    topology_5_to_8_target_indices = (
        (1, 1, 1),
        (1, 1, 0),
        (1, 1, -1),
        (1, 1, -2),
        (1, 0, 1),
        (1, 0, 0),
        (1, 0, -1),
        (1, 0, -2),
        (1, -1, 1),
        (1, -1, 0),
        (1, -1, -1),
        (1, -1, -2),
        (1, -2, 1),
        (1, -2, 0),
        (1, -2, -1),
        (1, -2, -2),
        (0, 1, 1),
        (0, 1, 0),
        (0, 1, -1),
        (0, 1, -2),
        (0, 0, 1),
        (0, 0, 0),
        (0, 0, -1),
        (0, 0, -2),
        (0, -1, 1),
        (0, -1, 0),
        (0, -1, -1),
        (0, -1, -2),
        (0, -2, 1),
        (0, -2, 0),
        (0, -2, -1),
        (0, -2, -2),
        (-1, 1, 1),
        (-1, 1, 0),
        (-1, 1, -1),
        (-1, 1, -2),
        (-1, 0, 1),
        (-1, 0, 0),
        (-1, 0, -1),
        (-1, 0, -2),
        (-1, -1, 1),
        (-1, -1, 0),
        (-1, -1, -1),
        (-1, -1, -2),
        (-1, -2, 1),
        (-1, -2, 0),
        (-1, -2, -1),
        (-1, -2, -2),
        (-2, 1, 1),
        (-2, 1, 0),
        (-2, 1, -1),
        (-2, 1, -2),
        (-2, 0, 1),
        (-2, 0, 0),
        (-2, 0, -1),
        (-2, 0, -2),
        (-2, -1, 1),
        (-2, -1, 0),
        (-2, -1, -1),
        (-2, -1, -2),
        (-2, -2, 1),
        (-2, -2, 0),
        (-2, -2, -1),
        (-2, -2, -2),
    )
    topology_10_target_indices = tuple(
        (first, second, third)
        for first in (2, 1, 0, -1, -2)
        for second in (2, 1, 0, -1, -2)
        for third in (2, 1, 0, -1, -2)
    )
    if family.name in {"topo10", "topo11"}:
        target_indices = topology_10_target_indices
    elif family.name in {"topo5", "topo6", "topo7", "topo8"}:
        target_indices = topology_5_to_8_target_indices
    else:
        target_indices = topology_1_to_4_target_indices
    targets = tuple(family(*indices) for indices in target_indices)
    bounds = (
        ReductionBounds(sectors=(7,), r=9, s=6, d=3)
        if family.name in {"topo10", "topo11"}
        else ReductionBounds(sectors=(7,), r=9, s=4, d=2)
    )
    master_indices = {
        "topo1": ((1, 1, 1), (0, 1, 1), (1, 0, 0)),
        "topo2": ((1, 0, 1), (1, 0, 0)),
        "topo3": ((1, 0, 1), (1, 0, 0)),
        "topo4": ((1, 1, 0),),
        "topo5": ((0, 1, 1),),
        "topo6": ((0, 1, 1), (1, 0, 1)),
        "topo7": ((0, 1, 1), (1, 1, 0)),
        "topo8": ((1, 1, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)),
        "topo10": ((0, 0, 1), (1, 0, 1)),
        "topo11": ((0, 0, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
        "topo20": ((0, 0, 1), (1, 0, 1)),
        "topo21": ((0, 1, 1),),
        "topo22": ((0, 1, 0), (1, 1, 0)),
        "topo23": ((0, 1, 0), (1, 0, 1), (1, 1, 1)),
        "topo24": ((0, 0, 1), (0, 1, 1), (1, 0, 1)),
        "topo25": ((0, 1, 1), (1, 0, 1)),
        "topo26": ((0, 1, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
        "topo27": ((0, 1, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
        "topo28": ((0, 0, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
        "topo29": ((0, 1, 1), (1, 1, 0)),
        "topo30": ((0, 1, 0), (0, 1, 1), (1, 1, 0)),
        "topo31": ((0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)),
    }
    preferred_masters = tuple(
        family(*indices) for indices in master_indices[family.name]
    )
    application_root = Path(__file__).resolve().parent
    kira_workdir = application_root / "runs" / f"dy-{family.name}"
    return (
        bounds,
        family,
        ipp1p2,
        kinematics,
        kira_workdir,
        preferred_masters,
        targets,
    )


@app.cell(hide_code=True)
def _(bounds, family, kira_workdir, mo, preferred_masters, targets):
    _target_domain = (
        "{2, 1, 0, -1, -2}^3"
        if family.name in {"topo10", "topo11"}
        else (
            "{1, 0, -1, -2}^3"
            if family.name in {"topo5", "topo6", "topo7", "topo8"}
            else "{1, 0, -1}^3"
        )
    )
    if family.name in {"topo1", "topo2", "topo3"}:
        _invariant_note = (
            "The composite invariant `m**2` is serialized as Kira's safe symbol "
            "`m2` and restored exactly on every parsed right-hand side."
        )
    elif family.name in {"topo6", "topo25"}:
        _invariant_note = "The external invariant `p2**2 = ipp2p2` remains exact."
    elif family.name in {"topo7", "topo29"}:
        _invariant_note = "The external invariant `p1**2 = ipp1p1` remains exact."
    elif family.name == "topo8":
        _invariant_note = (
            "The external invariants `p1**2 = ipp1p1`, `p1*p2 = ipp1p2`, "
            "and `p2**2 = ipp2p2` remain exact."
        )
    elif family.name in {"topo10", "topo20", "topo22", "topo23"}:
        _invariant_note = (
            "The internal mass-squared invariant `msq` and external invariant "
            "`p1*p2 = ipp1p2` remain exact."
        )
    elif family.name in {"topo24", "topo26", "topo27"}:
        _invariant_note = (
            "The internal mass-squared invariant `msq`, external invariant "
            "`p2**2 = ipp2p2`, and `p1*p2 = ipp1p2` remain exact."
        )
    elif family.name in {"topo28", "topo30", "topo31"}:
        _invariant_note = (
            "The internal mass-squared invariant `msq`, external invariant "
            "`p1**2 = ipp1p1`, and `p1*p2 = ipp1p2` remain exact."
        )
    elif family.name == "topo11":
        _invariant_note = (
            "The internal mass-squared invariant `msq`, external invariant "
            "`p1**2 = ipp1p1`, and `p1*p2 = ipp1p2` remain exact."
        )
    else:
        _invariant_note = "This family is massless and needs no composite invariant alias."
    mo.md(
        f"""
    | project item | value |
    | --- | --- |
    | family | `{family.name}` with `{family.arity}` propagators |
    | targets | `{len(targets)}` (`{_target_domain}`) |
    | reduction seed | sector `{bounds.sectors[0]}`, `r={bounds.r}`, `s={bounds.s}`, `d={bounds.d}` |
    | preferred masters | `{len(preferred_masters)}` with `check_masters=True` |
    | persistent workdir | `{kira_workdir}` |

    {_invariant_note} The historical notebook later identifies `ipp1p2 = s/2`.
    """
    )
    return


@app.cell
def _(family, mo):
    run_kira = mo.ui.run_button(
        label=f"Run the complete Kira reduction for {family.name}"
    )
    run_kira
    return (run_kira,)


@app.cell
def _(
    Kira,
    bounds,
    family,
    kinematics,
    kira_workdir,
    preferred_masters,
    run_kira,
    targets,
):
    if run_kira.value:
        kira = Kira()
        doctor_report = kira.doctor()
        doctor_report.raise_for_errors()
        reduction = kira.reduce(
            family=family,
            kinematics=kinematics,
            targets=targets,
            bounds=bounds,
            preferred_masters=preferred_masters,
            check_masters=True,
            workdir=kira_workdir,
            parallel="physical",
            resume=True,
        )
    else:
        doctor_report = None
        reduction = None
    return doctor_report, reduction


@app.cell(hide_code=True)
def _(doctor_report, mo, reduction):
    if reduction is None:
        _summary = mo.callout(
            "Ready. No subprocess has been started.",
            kind="neutral",
        )
    else:
        _summary = mo.callout(
            f"Kira `{doctor_report.version}` completed: "
            f"{len(reduction.requested_targets)} targets, "
            f"{len(reduction.masters)} masters, "
            f"{len(reduction.zero_integrals)} zero integrals, "
            f"complete={reduction.complete}.",
            kind="success",
        )
    _summary
    return


@app.cell(hide_code=True)
def _(mo, reduction):
    if reduction is None:
        _rules = mo.md("Reduction rules will appear here after the run.")
    else:
        _rules = mo.ui.table(
            [
                {
                    "target": target.format_plain(),
                    "reduction": reduction.rules[target].format_plain(),
                }
                for target in reduction.requested_targets
            ],
            pagination=True,
            page_size=27,
        )
    _rules
    return


@app.cell(hide_code=True)
def _(family, ipp1p2, mo, reduction):
    if reduction is None:
        _physical_rules = mo.md(
            "The downstream substitution `ipp1p2 -> s/2` will be shown here."
        )
    else:
        _physical_rules = mo.md(
            "The result remains exact and can now enter the downstream DY "
            f"calculation. For example, the rule for `{family.name}(1, -1, 1)` is "
            f"`{reduction.rules[next(target for target in reduction.requested_targets if target.format_plain() == f'{family.name}(1,-1,1)')].format_plain()}` "
            f"before applying `{ipp1p2.format_plain()} -> s/2`."
        )
    _physical_rules
    return


if __name__ == "__main__":
    app.run()
