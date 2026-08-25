import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


with app.setup(hide_code=True):
    import marimo as _marimo
    from masters import typst_md as _typst_md

    # Typst source cells retain Marimo's prose styling while remaining fully
    # editable as source, just like native Markdown cells.
    _marimo.md = _typst_md


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    from symbolica import S, Expression
    from masters import render_typst_html, typst_md, typst_shared_css

    # Keep the patch in an ordinary dependency cell as well as app.setup.
    # Marimo's static exporter evaluates this cell before the prose cells.
    mo.md = typst_md

    from kirapy import (
        IntegralFamily,
        KinematicInvariant,
        Kinematics,
        Kira,
        Propagator,
        ReductionBounds,
        ScalarProductRule,
    )
    from physical import (
        PHYSICAL_TOPOLOGY_NAMES,
        EndpointCoefficient,
        assemble_closed_form_dy,
        assemble_full_dy,
    )

    def expression_table(data, **kwargs):
        """Render exact Symbolica entries as Typst/MathML table cells."""

        columns = tuple(
            dict.fromkeys(column for row in data for column in row)
        )

        def _format_value(value):
            if isinstance(value, Expression):
                return mo.Html(
                    render_typst_html(
                        f"$ {value.to_typst()} $",
                        font_size=12.5,
                        include_styles=False,
                    )
                )
            return value

        kwargs.setdefault("selection", None)
        kwargs.setdefault("show_download", False)
        kwargs.setdefault("show_search", False)
        kwargs.setdefault("show_data_types", False)
        return mo.vstack(
            [
                mo.Html(typst_shared_css()),
                mo.ui.table(
                    data,
                    format_mapping={column: _format_value for column in columns},
                    **kwargs,
                ),
            ],
            gap=0,
        )

    return (
        IntegralFamily,
        KinematicInvariant,
        Kinematics,
        Kira,
        PHYSICAL_TOPOLOGY_NAMES,
        Path,
        Propagator,
        ReductionBounds,
        S,
        ScalarProductRule,
        EndpointCoefficient,
        assemble_closed_form_dy,
        assemble_full_dy,
        expression_table,
        mo,
        typst_md,
    )


@app.cell(hide_code=True)
def _(typst_md):
    typst_md(r"""
    = Native Symbolica--Kira assembly of the NLO DY coefficient

    This is the portable Python counterpart of the validated IBP-reduction jobs in
    #link("../mathematica/DY_calculation.nb")[`DY_calculation.nb`].
    It recreates the selected topology and its complete requested target set from the
    retained FIRE fixture, asks Kira for a complete reduction, and parses the
    result into exact Symbolica expressions. The second half runs the 18 physical
    sector jobs, reduces all eight routed numerators, constructs the explicit
    Kira-to-analytic-master handoff, integrates the leading external virtualities,
    and assembles the quark--antiquark and $q g$ coefficient functions.

    Kira is never launched merely by opening the notebook. Inspect the complete
    project below, then use either run button when ready. The consistently transverse
    native result, cached-notebook result, and manuscript physical target are separate
    objects because their final projector and endpoint treatments are not mutually
    consistent.
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
            KinematicInvariant(m**2, 2),
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
    kira_workdir = application_root / "runs" / "kirapy" / f"dy-{family.name}"

    def _kinematics_for_name(name):
        if name == "topo11":
            return topo11_kinematics
        if name in {"topo28", "topo30", "topo31"}:
            return p1_massive_internal_kinematics
        if name in {"topo24", "topo26", "topo27"}:
            return p2_massive_internal_kinematics
        if name in {"topo10", "topo20", "topo22", "topo23"}:
            return topo10_kinematics
        if name == "topo8":
            return fully_off_shell_kinematics
        if name in {"topo6", "topo25"}:
            return p2_massive_kinematics
        if name in {"topo7", "topo29"}:
            return p1_massive_kinematics
        if name in {"topo4", "topo5", "topo21"}:
            return massless_kinematics
        return massive_kinematics

    def _target_indices_for_name(name):
        if name in {"topo10", "topo11"}:
            return topology_10_target_indices
        if name in {"topo5", "topo6", "topo7", "topo8"}:
            return topology_5_to_8_target_indices
        return topology_1_to_4_target_indices

    def _bounds_for_name(name):
        return (
            ReductionBounds(sectors=(7,), r=9, s=6, d=3)
            if name in {"topo10", "topo11"}
            else ReductionBounds(sectors=(7,), r=9, s=4, d=2)
        )

    topology_specs = {
        name: {
            "family": candidate,
            "kinematics": _kinematics_for_name(name),
            "targets": tuple(
                candidate(*indices) for indices in _target_indices_for_name(name)
            ),
            "bounds": _bounds_for_name(name),
            "preferred_masters": tuple(
                candidate(*indices) for indices in master_indices[name]
            ),
            "workdir": application_root
            / "runs"
            / "kirapy"
            / f"dy-{name}",
        }
        for name, candidate in families.items()
    }
    return (
        bounds,
        family,
        ipp1p2,
        kinematics,
        kira_workdir,
        preferred_masters,
        targets,
        topology_specs,
    )


@app.cell(hide_code=True)
def _(bounds, family, kira_workdir, preferred_masters, targets, typst_md):
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
            "The composite invariant `m**2` crosses Kira through a deterministic "
            "private alias and is restored exactly on every parsed right-hand side."
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
        _invariant_note = (
            "This family is massless; its kinematic symbols still cross Kira "
            "through `kirapy`'s private aliases."
        )
    typst_md(f"""
    #table(
      columns: (auto, 1fr),
      table.header([*project item*], [*value*]),
      [family], [`{family.name}` with `{family.arity}` propagators],
      [targets], [`{len(targets)}` (`{_target_domain}`)],
      [reduction seed], [sector `{bounds.sectors[0]}`, `r={bounds.r}`, `s={bounds.s}`, `d={bounds.d}`],
      [preferred masters], [`{len(preferred_masters)}` with `check_masters=True`],
      [persistent workdir], [`{kira_workdir}`],
    )

    {_invariant_note} The historical notebook later identifies `ipp1p2 = s/2`.
    """)
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
def _(expression_table, reduction, typst_md):
    if reduction is None:
        _rules = typst_md("Reduction rules will appear here after the run.")
    else:
        _rules = expression_table(
            [
                {
                    "target": target,
                    "reduction": reduction.rules[target],
                }
                for target in reduction.requested_targets
            ],
            pagination=True,
            page_size=27,
        )
    _rules
    return


@app.cell(hide_code=True)
def _(family, ipp1p2, reduction, typst_md):
    if reduction is None:
        _physical_rules = typst_md(
            "The downstream substitution `ipp1p2 -> s/2` will be shown here."
        )
    else:
        _physical_rules = typst_md(
            "The result remains exact and can now enter the downstream DY "
            f"calculation. For example, the rule for `{family.name}(1, -1, 1)` is "
            f"`{reduction.rules[next(target for target in reduction.requested_targets if target.format_plain() == f'{family.name}(1,-1,1)')].format_plain()}` "
            f"before applying `{ipp1p2.format_plain()} -> s/2`."
        )
    _physical_rules
    return


@app.cell(hide_code=True)
def _(typst_md):
    typst_md(r"""
    == Assemble the complete leading-power NLO DY coefficient

    The topology selector above remains useful for inspecting one FIRE/Kira job.
    The physical button below instead runs or resumes every sector used by the
    eight routed transverse numerators:

    - `topo5`--`topo8`: the virtual triangle and bubble, including all cuts;
    - `topo10`--`topo11`: the direct quark--antiquark box and the three $q g$ graphs;
    - `topo20`--`topo31`: the three reducible crossed-box cuts;
    - the fourth crossed-box cut: the analytic maximal-cut master $M_(00)$.

    The numerator reducer starts from the actual graph powers.  In particular,
    the direct and $q g$ boxes start at $I(1,2,1)$, while a numerator monomial
    shifts those base indices.  Each Kira expression is then filtered only onto
    the cut-compatible analytic master listed in `masters.py`. External
    $upright(d) p_i^2/(2 pi)$ measures and graph/process weights remain explicit.

    We write

    $D_0(z)=[1/(1-z)]_+$,
    $D_1(z)=[log(1-z)/(1-z)]_+$,
    $P_(q q)(z)=3/2 delta(1-z)+2z D_0(z)+(1-z)$, and
    $P_(q g)(z)/T_F=1-2z+2z^2$.
    """)
    return


@app.cell
def _(mo):
    run_full_dy = mo.ui.run_button(
        label="Run/resume all physical reductions and assemble DY",
        kind="warn",
        full_width=True,
    )
    run_full_dy
    return (run_full_dy,)


@app.cell
def _(
    Kira,
    PHYSICAL_TOPOLOGY_NAMES,
    assemble_full_dy,
    run_full_dy,
    topology_specs,
):
    if run_full_dy.value:
        full_kira = Kira()
        full_doctor_report = full_kira.doctor()
        full_doctor_report.raise_for_errors()
        full_reductions = {}
        for physical_name in PHYSICAL_TOPOLOGY_NAMES:
            spec = topology_specs[physical_name]
            full_reductions[physical_name] = full_kira.reduce(
                family=spec["family"],
                kinematics=spec["kinematics"],
                targets=spec["targets"],
                bounds=spec["bounds"],
                preferred_masters=spec["preferred_masters"],
                check_masters=True,
                workdir=spec["workdir"],
                parallel="physical",
                resume=True,
            )
        full_audit, full_dy = assemble_full_dy(full_reductions)
    else:
        full_audit = None
        full_doctor_report = None
        full_dy = None
        full_reductions = {}
    return full_audit, full_doctor_report, full_dy, full_reductions


@app.cell
def _(assemble_closed_form_dy):
    full_dy_preview = assemble_closed_form_dy()

    def endpoint_row(label, coefficient):
        return {
            "contribution": label,
            "delta(1-z)": coefficient.delta,
            "D0 prefactor": coefficient.d0_prefactor,
            "D1 prefactor": coefficient.d1_prefactor,
            "ordinary part": coefficient.regular,
        }

    return endpoint_row, full_dy_preview


@app.cell(hide_code=True)
def _(
    PHYSICAL_TOPOLOGY_NAMES,
    endpoint_row,
    expression_table,
    full_audit,
    full_doctor_report,
    full_dy,
    full_dy_preview,
    full_reductions,
    mo,
    typst_md,
):
    displayed_dy = full_dy if full_dy is not None else full_dy_preview
    if full_audit is None:
        _run_status = mo.callout(
            "Closed-form graph ledgers are visible below, but the native "
            "numerator-to-Kira audit has not been run in this session.",
            kind="neutral",
        )
        _reduction_table = typst_md(
            "Press the physical run button to load or compute all 18 sector jobs."
        )
        _audit_table = typst_md("Exact Kira residuals will appear after that run.")
        _master_table = typst_md(
            "The explicit Kira-to-analytic-master ledger will appear after that run."
        )
        _crossed_endpoint_table = typst_md(
            "The cut-by-cut crossed-box endpoint expansion will appear after that run."
        )
        _normalization_table = typst_md(
            "Channel normalization factors will appear with the master ledger."
        )
    else:
        _handoff = full_dy.master_handoff
        _run_status = mo.callout(
            f"Kira `{full_doctor_report.version}` completed the native provenance "
            f"assembly: "
            f"{len(full_audit.complete_topologies)}/{len(PHYSICAL_TOPOLOGY_NAMES)} "
            f"sector jobs complete; all algebra, Ward, selected-master, and "
            f"finite master-handoff residuals are zero.",
            kind="success",
        )
        _reduction_table = mo.ui.table(
            [
                {
                    "family": name,
                    "targets": len(full_reductions[name].requested_targets),
                    "masters": len(full_reductions[name].masters),
                    "complete": full_reductions[name].complete,
                    "workdir": str(full_reductions[name].workdir),
                }
                for name in PHYSICAL_TOPOLOGY_NAMES
            ],
            pagination=True,
            page_size=18,
        )
        _audit_rows = [
            {
                "check": f"numerator reconstruction: {name}",
                "residual": residual,
            }
            for name, residual in full_audit.numerator_reconstruction_residuals.items()
        ]
        _audit_rows.extend(
            {
                "check": f"virtual master coefficient: {name}",
                "residual": residual,
            }
            for name, residual in full_audit.virtual_expected_residuals.items()
        )
        _audit_rows.extend(
            {
                "check": f"direct-box master coefficient: {name}",
                "residual": residual,
            }
            for name, residual in full_audit.direct_box_expected_residuals.items()
        )
        _audit_rows.extend(
            {
                "check": f"qg master coefficient: {name}",
                "residual": residual,
            }
            for name, residual in full_audit.qg_expected_residuals.items()
        )
        _audit_rows.extend(
            {
                "check": f"qg Ward master equality: {name}",
                "residual": residual,
            }
            for name, residual in full_audit.qg_ward_expected_residuals.items()
        )
        _audit_rows.append(
            {
                "check": "qg Ward combination 2 triangle - box - bubble",
                "residual": full_audit.qg_ward_cancellation_residual,
            }
        )
        _audit_rows.extend(
            {
                "check": f"crossed-box cut {name} master coefficient",
                "residual": residual,
            }
            for name, residual in full_audit.crossed_box_expected_residuals.items()
        )
        _audit_rows.extend(
            [
                {
                    "check": "crossed-box apart reconstruction",
                    "residual": full_audit.crossed_box_reconstruction_residual,
                },
                {
                    "check": "direct qqbar analytic-master finite term",
                    "residual": _handoff.direct_finite_residual,
                },
                {
                    "check": "qg analytic-master finite term",
                    "residual": _handoff.qg_finite_residual,
                },
            ]
        )
        _endpoint_components = ("delta", "D0", "D1", "ordinary")
        for _power, _residual in _handoff.crossed_pole_residuals.items():
            _audit_rows.extend(
                {
                    "check": (
                        f"crossed all-cut epsilon^{_power}: {_component}"
                    ),
                    "residual": _value,
                }
                for _component, _value in zip(
                    _endpoint_components,
                    _residual.canonical().residuals(),
                    strict=True,
                )
            )
        _audit_rows.extend(
            {
                "check": f"crossed all-cut finite term: {_component}",
                "residual": _value,
            }
            for _component, _value in zip(
                _endpoint_components,
                _handoff.crossed_finite_residual.canonical().residuals(),
                strict=True,
            )
        )
        _audit_table = expression_table(
            _audit_rows,
            pagination=True,
            page_size=40,
        )
        _master_table = expression_table(
            [
                {
                    "channel": item.channel,
                    "sector": item.sector,
                    "topologies": ", ".join(item.topologies) or "analytic 00",
                    "IBP coefficient": item.ibp_coefficient,
                    "analytic master": item.analytic_master,
                    "virtuality factor": item.virtuality_factor,
                    "relative weight": item.relative_weight,
                }
                for item in _handoff.insertions.values()
            ],
            pagination=True,
            page_size=20,
        )
        _crossed_endpoint_rows = [
            endpoint_row(
                f"crossed cut {name}: unexpanded endpoint distribution",
                endpoint,
            )
            for name, endpoint in _handoff.crossed_cut_endpoint.items()
        ]
        _crossed_endpoint_rows.extend(
            [
                endpoint_row(
                    "crossed 11+10+01+00: finite coefficient",
                    _handoff.crossed_finite,
                ),
                endpoint_row(
                    "finite coefficient - crossed graph ledger",
                    _handoff.crossed_finite_residual.canonical(),
                ),
            ]
        )
        _crossed_endpoint_table = expression_table(
            _crossed_endpoint_rows,
            pagination=False,
        )
        _normalization_table = expression_table(
            [
                {"factor": name, "expression": value}
                for name, value in _handoff.normalization_factors.items()
            ],
            pagination=False,
        )

    _virtual_rows = [
        endpoint_row("ordinary virtual form-factor benchmark", displayed_dy.ordinary_virtual),
        endpoint_row("local all-cut virtual (complex)", displayed_dy.local_all_cut_virtual),
    ]
    _qq_graph_rows = [
        endpoint_row(name, coefficient)
        for name, coefficient in displayed_dy.qq_transverse.pieces.items()
    ]
    _qq_graph_rows.append(
        endpoint_row(
            "native transverse qqbar candidate",
            displayed_dy.qq_transverse.total,
        )
    )
    _qg_graph_rows = [
        endpoint_row(name, coefficient)
        for name, coefficient in displayed_dy.qg_transverse.pieces.items()
    ]
    _qg_graph_rows.append(
        endpoint_row("native transverse qg candidate", displayed_dy.qg_transverse.total)
    )
    _comparison_rows = [
        endpoint_row("qqbar: physical target, manuscript Eq. 317", displayed_dy.qq_manuscript),
        endpoint_row("qqbar: native transverse", displayed_dy.qq_transverse.total),
        endpoint_row("qqbar: cached notebook", displayed_dy.qq_cached_notebook),
        endpoint_row(
            "qqbar: transverse - notebook",
            displayed_dy.qq_transverse_minus_notebook,
        ),
        endpoint_row(
            "qqbar: transverse - manuscript",
            displayed_dy.qq_transverse_minus_manuscript,
        ),
        endpoint_row(
            "qqbar: notebook - manuscript",
            displayed_dy.qq_notebook_minus_manuscript,
        ),
        endpoint_row("qg: physical target, manuscript Eq. 318", displayed_dy.qg_manuscript),
        endpoint_row("qg: native transverse", displayed_dy.qg_transverse.total),
        endpoint_row("qg: cached notebook", displayed_dy.qg_cached_notebook),
        endpoint_row(
            "qg: transverse - manuscript",
            displayed_dy.qg_transverse_minus_manuscript,
        ),
    ]
    mo.vstack(
        [
            _run_status,
            typst_md("=== Physical Kira sectors"),
            _reduction_table,
            typst_md("=== Exact native audits"),
            _audit_table,
            typst_md("=== Kira-to-analytic-master handoff"),
            _master_table,
            _normalization_table,
            typst_md("=== Crossed-box endpoint sum over all four cuts"),
            _crossed_endpoint_table,
            typst_md("=== Ordinary and local all-cut virtual objects"),
            expression_table(_virtual_rows, pagination=False),
            typst_md("=== qqbar graph and all-cut ledger"),
            expression_table(_qq_graph_rows, pagination=False),
            typst_md("=== qg graph ledger"),
            expression_table(_qg_graph_rows, pagination=False),
            typst_md("=== Final partonic channels and independent oracles"),
            expression_table(_comparison_rows, pagination=False),
            mo.callout(
                "The source comparison residuals are intentionally nonzero. "
                "The manuscript equations are the physical targets: in particular, "
                "their positive qqbar soft D1 sign agrees with the standard soft "
                "check. The native transverse reconstruction is retained as exact "
                "provenance rather than silently tuned, and the cached notebook's qg "
                "formula contains the displayed Ward remainder even though the exact "
                "native Ward combination vanishes.",
                kind="warn",
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
