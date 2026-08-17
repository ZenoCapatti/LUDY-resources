import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    from itertools import product
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
        product,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DY topology 1: FIRE to Kira

    This is the portable Python counterpart of the first IBP-reduction job in
    [`DY_calculation.nb`](../mathematica/DY_calculation.nb).
    It recreates the topology and all 27 requested integrals from the retained
    FIRE fixture, asks Kira for a complete reduction, and parses the result into
    exact Symbolica expressions.

    Kira is never launched merely by opening the notebook. Inspect the complete
    project below, then use the run button when ready.
    """)
    return


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
    product,
):
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
    targets = tuple(
        family(*indices) for indices in product((1, 0, -1), repeat=3)
    )
    bounds = ReductionBounds(sectors=(7,), r=9, s=4, d=2)
    preferred_masters = tuple(
        family(*indices)
        for indices in ((1, 1, 1), (0, 1, 1), (1, 0, 0))
    )
    application_root = Path(__file__).resolve().parent
    kira_workdir = application_root / "runs" / "dy-topo1"
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
    mo.md(
        f"""
    | project item | value |
    | --- | --- |
    | family | `{family.name}` with `{family.arity}` propagators |
    | targets | `{len(targets)}` (`{{1, 0, -1}}^3`) |
    | reduction seed | sector `{bounds.sectors[0]}`, `r={bounds.r}`, `s={bounds.s}`, `d={bounds.d}` |
    | preferred masters | `{len(preferred_masters)}` with `check_masters=True` |
    | persistent workdir | `{kira_workdir}` |

    The composite invariant `m**2` is serialized as Kira's safe symbol `m2`
    and restored exactly on every parsed right-hand side. The historical
    notebook later identifies `ipp1p2 = s/2`.
    """
    )
    return


@app.cell
def _(mo):
    run_kira = mo.ui.run_button(label="Run the complete Kira reduction")
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
def _(ipp1p2, mo, reduction):
    if reduction is None:
        _physical_rules = mo.md(
            "The downstream substitution `ipp1p2 -> s/2` will be shown here."
        )
    else:
        _physical_rules = mo.md(
            "The result remains exact and can now enter the downstream DY "
            f"calculation. For example, the rule for `topo1(1, -1, 1)` is "
            f"`{reduction.rules[next(target for target in reduction.requested_targets if target.format_plain() == 'topo1(1,-1,1)')].format_plain()}` "
            f"before applying `{ipp1p2.format_plain()} -> s/2`."
        )
    _physical_rules
    return


if __name__ == "__main__":
    app.run()
