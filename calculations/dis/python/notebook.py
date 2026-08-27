import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


with app.setup(hide_code=True):
    from math import prod
    from pathlib import Path
    import sys

    import marimo as _marimo
    from symbolica import E, Expression

    repository_root = Path(__file__).resolve().parents[3]
    _notebook_root = repository_root / "notebooks"
    for _path in (str(repository_root), str(_notebook_root)):
        if _path not in sys.path:
            sys.path.insert(0, _path)

    from calculations.dis.python.ancillary import ANCILLARY_SPECS
    from calculations.dis.python.assembly import (
        audit_raised_external_reductions,
        build_master_insertion_audit,
        build_raised_external_kira_projects,
        build_raised_external_master_boundaries,
    )
    from calculations.dis.python.masters import (
        MASTER_SUPPORT,
        NORMALIZATION_SELF_CHECKS,
        massless_cut_bubble,
        massless_cut_triangle,
        normalization_ledger as master_normalization_ledger,
        paper_cut_bubble,
        paper_cut_triangle,
        paper_uncut_bubble,
        uncut_bubble,
    )
    from calculations.dis.python.mathematica_reference import (
        MATHEMATICA_REFERENCE,
        MATHEMATICA_REFERENCE_SELF_CHECKS,
        mathematica_dy_fermion_conversion,
        mathematica_dy_gluon_conversion,
    )
    from calculations.dis.python.physical import (
        DIS_GRAPH_SPECS,
        DIS_KINEMATICS,
        KNOWN_DIS_CUTS,
        NORMALIZATION_LEDGER,
        PAPER_TARGETS,
        audit_kira_master_coefficients,
        audit_projected_numerator_reductions,
        build_kira_numerator_handoffs,
        build_kira_smoke_projects,
        build_validation_ledger,
        crossed_box_apart,
        d,
        derive_all_projected_numerators,
        epsilon,
        k,
        p,
        p_squared,
        q,
    )
    from calculations.dy.python.masters import typst_md
    from kirapy import Kira, KiraWorkdirError
    from ludy import spenso_table

    _marimo.md = typst_md
    globals()["mo"] = _marimo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    = Native DIS calculation pipeline

    This notebook follows the NLO DIS calculation in dependency order. It first
    defines the six graphs, their common denominator basis and momentum routing,
    and the projected physical numerators. It then applies the generic
    apart/numerator-reduction pipeline, constructs the Kira projects, restores
    every currently available reduction, and inserts analytic masters wherever
    the required boundary is complete.

    Partial cached reductions remain visible rather than being promoted to a
    complete graph sum. Oriented multiplicities, graph weights, the raised-cut
    reverse-unitarity sign map, derivative-cut endpoint rules, and the
    active-to-historical $F_2$ projector normalization remain unresolved. All
    residual checks, paper targets, historical Mathematica regressions, and
    provenance tables are collected in the final validation appendix. Opening
    or exporting this notebook never launches Kira; subprocesses are only behind
    the explicit run buttons.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 1. DIS graphs, routing, and physical numerators

    === Exact finite-virtuality kinematics and denominator basis

    We use $Q^2=-q^2>0$ and Bjorken $x in (0,1)$. The finite-$p^2$
    parametrization is

    $ p dot q = frac(Q^2/x-x p^2,2), $

    hence

    $ (p+q)^2=(1-x)(Q^2/x+p^2). $

    This exposes the final-state discontinuity in $1-x$ without imposing the
    leading-power replacement $p^2=0$. That replacement is a named later step;
    it is not hidden inside the numerator or Kira source model.
    """)
    return


@app.cell(hide_code=True)
def _(spenso_table):
    _routing = (k, k + p, k + p + q, k + q, p, p + q)
    denominator_rows = [
        {
            "line": f"D{index}",
            "momentum routing": _routing[index - 1],
            "expression": denominator,
            "role": "loop" if index <= 4 else "external virtuality",
        }
        for index, denominator in enumerate(
            DIS_KINEMATICS.scalar_denominators,
            start=1,
        )
    ]
    spenso_table(denominator_rows, pagination=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Six physical graphs and their source traces

    All graphs share $D_1,...,D_6$. Five use the three-line loop family
    $(D_1,D_2,D_3)$ directly. Only the gluon crossed box contains all four loop
    denominators and needs multivariate partial fractioning. External powers of
    $D_5=p^2$ and $D_6=(p+q)^2$ remain explicit: Kira never mistakes them for
    loop propagators.
    """)
    return


@app.cell(hide_code=True)
def _(spenso_table):
    graph_rows = []
    for _graph in DIS_GRAPH_SPECS.values():
        source_chain = " ".join(
            (
                f"slash({vector.plain})"
                if vector is not None
                else f"gamma({label})"
            )
            for vector, label in zip(
                _graph.trace.vectors,
                _graph.trace.lorentz_labels,
                strict=True,
            )
        )
        graph_rows.append(
            {
                "graph": _graph.name,
                "channel": _graph.channel,
                "powers D1...D6": _graph.powers,
                "denominator product": prod(
                    denominator**power
                    for denominator, power in zip(
                        DIS_KINEMATICS.scalar_denominators,
                        _graph.powers,
                        strict=True,
                    )
                ),
                "photon slots": _graph.trace.photon_slots,
                "source trace": source_chain,
            }
        )
    spenso_table(graph_rows, pagination=False)
    return


@app.cell
def _():
    projected_numerators = derive_all_projected_numerators()
    return (projected_numerators,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Spenso projectors and physical numerators

    The active manuscript prints an uppercase $P$ without defining it. Its cited
    DIS source does define the transverse vector

    $ P^mu=p^mu-frac(p dot q,q^2)q^mu, quad P dot q=0. $

    We use that definition explicitly. For every graph, Spenso evaluates five
    traces: the metric contraction and the $p p$, $p q$, $q p$, and $q q$
    contractions of the two photon slots. Linearity then constructs
    $P_mu P_nu N^(mu nu)/P^2$ without wrapping $P$ in an opaque atom.

    The table shows the physical projected numerators after the transparent
    leading-power display replacement $p^2=0$ and $d=4-2 epsilon$. The full
    finite-$p^2$ expressions, not these shortened displays, continue into the
    reduction pipeline.
    """)
    return


@app.cell
def _(mo):
    graph_choice = mo.ui.dropdown(
        options=tuple(DIS_GRAPH_SPECS),
        value="q_triangle",
        label="Graph numerator to display",
    )
    graph_choice
    return (graph_choice,)


@app.cell(hide_code=True)
def _(graph_choice, projected_numerators, spenso_table):
    selected_numerator = projected_numerators[graph_choice.value]
    display_rules = ((p_squared, E("0")), (d, 4 - 2 * epsilon))

    def display_limit(expression):
        result = expression
        for source, target in display_rules:
            result = result.replace(source, target)
        return result.expand().together().cancel()

    spenso_table(
        [
            {
                "graph": graph_choice.value,
                "contraction": "metric",
                "leading-power numerator": display_limit(
                    selected_numerator.metric
                ),
            },
            {
                "graph": graph_choice.value,
                "contraction": "P_mu P_nu / P^2",
                "leading-power numerator": display_limit(
                    selected_numerator.longitudinal
                ),
            },
            {
                "graph": graph_choice.value,
                "contraction": "printed F2 projector",
                "leading-power numerator": display_limit(
                    selected_numerator.F2
                ),
            },
            {
                "graph": graph_choice.value,
                "contraction": "printed FL = F1 - 2x F2",
                "leading-power numerator": display_limit(
                    selected_numerator.FL
                ),
            },
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 2. Generic apart and numerator-reduction pipeline

    Symbolica's multivariate `apart(kk,kp,kq)` rewrites
    $1/(D_1D_2D_3D_4)$ into four three-denominator children. Their alternating
    coefficients are retained as exact expressions. The reconstruction check is
    reported in the final validation appendix.

    Each projected numerator is then rewritten in independent denominator
    coordinates. The graph's actual base powers are used: in particular, both
    boxes start at $(1,2,1)$, the bubble at $(1,0,1)$, and the LSZ graph at
    $(1,1,0)$. The complete set of shifted family integrals is handed to the cut
    families below; this is not an IBP result yet.
    """)
    return


@app.cell
def _(projected_numerators):
    apart_expression, apart_terms = crossed_box_apart()
    numerator_audits = audit_projected_numerator_reductions(
        projected_numerators
    )
    return apart_expression, apart_terms, numerator_audits


@app.cell(hide_code=True)
def _(apart_terms, spenso_table):
    apart_rows = [
        {
            "retained graph lines": tuple(
                index + 1 for index in term.retained_indices
            ),
            "coefficient": term.coefficient,
        }
        for term in apart_terms
    ]
    spenso_table(apart_rows, pagination=False)
    return


@app.cell(hide_code=True)
def _(numerator_audits, spenso_table):
    spenso_table(
        [
            {
                "graph": audit.graph_name,
                "observable": audit.observable,
                "retained lines": audit.retained_loop_lines,
                "apart coefficient": audit.apart_coefficient,
                "shifted terms": audit.term_count,
            }
            for audit in numerator_audits
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Candidate structural ledger for the all-cut contribution

    The historical definition fixes a *plus sign* between all four formal
    pieces: both external channel poles, an internal initial cut with the
    external final pole, the external initial pole with an internal final cut,
    and a pair of internal cuts sharing one edge. Expanding those possibilities
    in the common $D$ basis gives six channel patterns. Intersecting them with
    each graph's nonzero propagator support leaves the 15 candidate rows below.

    `order 0` denotes an ordinary cut delta. `order 1` exposes the derivative
    generated by a raised propagator: $D_2^2$ in the two boxes, $D_6^2$ in the
    bubble, or $D_5^2$ in the LSZ graph. Each displayed $+1$ is inherited from
    the formal four-class sum; it is not an independent sign determination for
    that row. This internal ledger does not prove that every physical Cut
    orientation is present. A formal Cut operator sums over energy orientations,
    and the source does not resolve those sums into one multiplicity for each
    active $D_1,...,D_6$ sector. The graph weights, oriented multiplicities, and
    raised-cut convention map therefore remain unknown, so the weighted all-cut
    contribution is not fabricated.
    """)
    return


@app.cell(hide_code=True)
def _(spenso_table):
    spenso_table(
        [
            {
                "graph": cut.graph_name,
                "sector": cut.name,
                "disc p^2 lines": cut.initial_cut_lines,
                "disc (1-x) lines": cut.final_cut_lines,
                "cut derivative orders": cut.cut_orders,
                "formal four-piece sign": (
                    "missing" if cut.relative_sign is None else cut.relative_sign
                ),
                "oriented multiplicity": (
                    "unresolved"
                    if cut.multiplicity is None
                    else cut.multiplicity
                ),
            }
            for cut in KNOWN_DIS_CUTS
        ],
        pagination=False,
    )
    return


@app.cell
def _(numerator_audits):
    smoke_projects = build_kira_smoke_projects()
    numerator_handoffs = build_kira_numerator_handoffs(
        projects=smoke_projects,
        numerator_audits=numerator_audits,
    )
    return numerator_handoffs, smoke_projects


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Physical numerator handoff to the cut families

    The 18 exact numerator reconstructions are now intersected with the protected
    cut lines of every Kira project. Terms that cancel a cut propagator are kept
    in the audit but are zero by reverse unitarity and are not submitted as Kira
    targets. This produces 32 graph/observable handoffs and 48 distinct
    cut-preserving targets.

    Twenty-eight handoffs can use the support-specialized cached reductions.
    Four of those, the two observables in each $D_2^2$ box sector, still require
    a sign map between the historical raised-cut normalization and Kira's
    algebraic reverse-unitarity convention. Four further records, the two
    observables of the quark bubble and LSZ graph, contain a raised external cut.
    Their regulated derivative distribution must act before the corresponding
    invariant is specialized, so none of these raised-cut boundaries is
    promoted to a physical coefficient.
    """)
    return


@app.cell(hide_code=True)
def _(mo, numerator_handoffs, spenso_table):
    unique_handoff_targets = {
        (handoff.project_key, target)
        for handoff in numerator_handoffs
        for target in handoff.required_targets
    }
    ordinary_handoffs = sum(
        not handoff.requires_external_derivative
        for handoff in numerator_handoffs
    )
    derivative_handoffs = sum(
        handoff.requires_external_derivative
        for handoff in numerator_handoffs
    )
    mo.vstack(
        [
            spenso_table(
                [
                    {
                        "handoff records": len(numerator_handoffs),
                        "unique Kira targets": len(unique_handoff_targets),
                        "cut-specialized records": ordinary_handoffs,
                        "external-derivative records": derivative_handoffs,
                    }
                ],
                pagination=False,
            ),
            spenso_table(
                [
                    {
                        "project": handoff.project_key,
                        "graph": handoff.graph_name,
                        "observable": handoff.observable,
                        "retained lines": handoff.retained_loop_lines,
                        "required targets": len(handoff.required_targets),
                        "cut-cancelled indices": handoff.cut_cancelled_indices,
                        "external derivative": (
                            "required"
                            if handoff.requires_external_derivative
                            else "not required"
                        ),
                    }
                    for handoff in numerator_handoffs
                ],
                pagination=False,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 3. Kira projects, run controls, and available reductions

    External $D_5,D_6$ cuts specialize the invariant rules but never become Kira
    propagators. Internal cut lines are written to `cut_propagators` using local
    one-based family positions. The complete smoke target cube
    $a_i in {1,0,-1}$ is filtered so every cut index stays positive; the physical
    raised target $(1,2,1)$ is added where needed.

    The expected scalar basis is $B(q^2)$, $slash(B)(p^2)$,
    $slash(B)((p+q)^2)$, and the fully three-mass $slash(T)$. These identities
    are supplied to Kira as checked preferred masters. Each compatible cache is
    loaded independently without starting a subprocess, so completed subsets
    remain visible. Their rules are applied only to the matching numerator
    handoffs. A manifest whose fingerprint differs from the in-memory project is
    rejected as stale; it cannot enter the coefficient rows below.

    The button asks Kira 3.1 to run or resume the current project definitions.
    These reductions establish the graph-level master coefficients. The four
    raised-external records require separate finite-virtuality projects, shown
    immediately below. Neither reduction supplies the unresolved oriented-cut
    multiplicities, graph weights, raised-cut sign map, or regulated
    derivative-distribution endpoint rules.
    """)
    return


@app.cell
def _(numerator_handoffs, smoke_projects):
    raised_external_projects = build_raised_external_kira_projects(
        source_projects=smoke_projects,
        numerator_handoffs=numerator_handoffs,
    )
    return (raised_external_projects,)


@app.cell(hide_code=True)
def _(smoke_projects, spenso_table):
    spenso_table(
        [
            {
                "project": key,
                "global lines": project.retained_loop_lines,
                "local cuts": project.project.family.cut_propagators,
                "targets": len(project.project.targets),
                "expected master indices": project.expected_master_indices,
                "analytic master": project.expected_master_name,
            }
            for key, project in smoke_projects.items()
        ],
        pagination=False,
    )
    return


@app.cell
def _(mo):
    run_kira = mo.ui.run_button(
        label="Run/resume all 16 DIS scalar-master smoke reductions",
        kind="warn",
        full_width=True,
    )
    run_kira
    return (run_kira,)


@app.cell
def _(run_kira, smoke_projects):
    kira = Kira()
    kira_work_root = repository_root / "runs" / "dis-paper-kirapy"
    kira_reductions = {}
    kira_cache_modes = {}
    if run_kira.value:
        kira_doctor = kira.doctor()
        kira_doctor.raise_for_errors()
    else:
        kira_doctor = None

    for _project_key, _project_input in sorted(smoke_projects.items()):
        _project = _project_input.project
        _workdir = kira_work_root / _project.family.name
        if run_kira.value:
            try:
                kira_reductions[_project_key] = kira.reduce(
                    family=_project.family,
                    kinematics=_project.kinematics,
                    targets=_project.targets,
                    bounds=_project.bounds,
                    dimension=_project.dimension,
                    preferred_masters=_project.preferred_masters,
                    check_masters=_project.check_masters,
                    reconstruct_mass=_project.reconstruct_mass,
                    workdir=_workdir,
                    parallel="physical",
                    resume=True,
                )
                kira_cache_modes[_project_key] = "current project run/resume"
            except KiraWorkdirError as _error:
                if "does not match" not in str(_error):
                    raise
                kira_cache_modes[_project_key] = (
                    "stale cache rejected: current fingerprint differs"
                )
            continue

        if not (_workdir / "kirapy.json").is_file():
            kira_cache_modes[_project_key] = "no cached manifest"
            continue
        try:
            kira_reductions[_project_key] = kira.load(
                _workdir,
                project=_project,
            )
            kira_cache_modes[_project_key] = "verified current-project cache"
        except KiraWorkdirError as _error:
            if "does not match" not in str(_error):
                raise
            kira_cache_modes[_project_key] = (
                "stale cache rejected: current fingerprint differs"
            )
    return kira_cache_modes, kira_doctor, kira_reductions, kira_work_root


@app.cell(hide_code=True)
def _(
    kira_cache_modes,
    kira_doctor,
    kira_reductions,
    kira_work_root,
    mo,
    smoke_projects,
    spenso_table,
):
    complete = sum(result.complete for result in kira_reductions.values())
    full_cache = complete == len(smoke_projects)
    runtime_label = (
        f"Kira {kira_doctor.version}"
        if kira_doctor is not None
        else "Cached Kira outputs"
    )
    _project_rows = []
    for _key in sorted(smoke_projects):
        _result = kira_reductions.get(_key)
        _project_rows.append(
            {
                "project": _key,
                "load mode": kira_cache_modes[_key],
                "complete": False if _result is None else _result.complete,
                "rules": 0 if _result is None else len(_result.rules),
                "masters": () if _result is None else _result.masters,
            }
        )
    kira_summary = mo.vstack(
        [
            mo.callout(
                f"{runtime_label}: {complete}/{len(smoke_projects)} "
                f"cut-specialized reductions complete. Work root: {kira_work_root}",
                kind="success" if full_cache else "neutral" if complete == 0 else "warn",
            ),
            spenso_table(_project_rows, pagination=False),
        ]
    )
    kira_summary
    return


@app.cell
def _(kira_reductions, numerator_handoffs, smoke_projects):
    _available_project_keys = {
        key
        for key, result in kira_reductions.items()
        if key in smoke_projects and result.complete
    }
    _available_projects = {
        key: smoke_projects[key] for key in _available_project_keys
    }
    _available_reductions = {
        key: kira_reductions[key] for key in _available_project_keys
    }
    _available_handoffs = tuple(
        handoff
        for handoff in numerator_handoffs
        if handoff.project_key in _available_project_keys
    )
    if _available_handoffs:
        physical_reduction_audit = audit_kira_master_coefficients(
            _available_reductions,
            projects=_available_projects,
            numerator_handoffs=_available_handoffs,
        )
    else:
        physical_reduction_audit = None
    return (physical_reduction_audit,)


@app.cell(hide_code=True)
def _(mo, physical_reduction_audit, spenso_table):
    if physical_reduction_audit is None:
        physical_reduction_summary = mo.callout(
            "No completed compatible cut-specialized reduction is currently "
            "available, so there are no master-coefficient rows yet.",
            kind="neutral",
        )
    else:
        physical_reduction_summary = mo.vstack(
            [
                spenso_table(
                    [
                        {
                            "coefficient records": len(
                                physical_reduction_audit.coefficients
                            ),
                            "unique Kira targets": (
                                physical_reduction_audit.unique_required_targets
                            ),
                            "cut-specialized records": len(
                                physical_reduction_audit.cut_specialized_coefficients
                            ),
                            "external-derivative records": len(
                                physical_reduction_audit.raised_external_coefficients
                            ),
                            "missing targets": (
                                physical_reduction_audit.missing_targets
                            ),
                        }
                    ],
                    pagination=False,
                ),
                spenso_table(
                    [
                        {
                            "project": record.handoff.project_key,
                            "graph": record.handoff.graph_name,
                            "observable": record.handoff.observable,
                            "master": record.expected_master,
                            "coefficient": record.coefficient,
                            "status": (
                                "external derivative required"
                                if record.handoff.requires_external_derivative
                                else "ordinary"
                            ),
                        }
                        for record in physical_reduction_audit.coefficients
                    ],
                    pagination=False,
                ),
            ]
        )
    physical_reduction_summary
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Finite-virtuality reductions for the four raised-external records

    The quark bubble has a raised $D_6=(p+q)^2$ cut and the LSZ graph has a
    raised $D_5=p^2$ cut. Their two observables are therefore reduced in two
    additional Kira projects while both external invariants remain generic.
    A compatible cache under `runs/dis-paper-raised-external-kirapy`, when
    present, is loaded without launching Kira; the button is only for an
    explicit run or resume.

    A successful two-job reduction gives four exact coefficients of an uncut
    bubble, and the analytic bubble can then be inserted. This is still a
    boundary, not a physical graph contribution: cancellation against the
    regulated bubble, the reverse-unitarity derivative sign, the one-sided
    action of $delta'(p^2)$ or $delta'((p+q)^2)$, and the full graph weight
    remain unresolved. The universal plus signs of the four formal all-cut
    pieces determine none of those inputs.
    """)
    return


@app.cell
def _(mo):
    run_raised_kira = mo.ui.run_button(
        label="Run/resume 2 finite-virtuality raised-external reductions",
        kind="warn",
        full_width=True,
    )
    run_raised_kira
    return (run_raised_kira,)


@app.cell
def _(raised_external_projects, run_raised_kira):
    raised_kira = Kira()
    raised_kira_work_root = (
        repository_root / "runs" / "dis-paper-raised-external-kirapy"
    )
    raised_kira_reductions = {}
    raised_kira_cache_modes = {}
    if run_raised_kira.value:
        raised_kira_doctor = raised_kira.doctor()
        raised_kira_doctor.raise_for_errors()
    else:
        raised_kira_doctor = None

    for _raised_key, _raised_record in sorted(raised_external_projects.items()):
        _raised_project = _raised_record.project
        _raised_workdir = raised_kira_work_root / _raised_project.family.name
        if run_raised_kira.value:
            try:
                raised_kira_reductions[_raised_key] = raised_kira.reduce(
                    family=_raised_project.family,
                    kinematics=_raised_project.kinematics,
                    targets=_raised_project.targets,
                    bounds=_raised_project.bounds,
                    dimension=_raised_project.dimension,
                    preferred_masters=_raised_project.preferred_masters,
                    check_masters=_raised_project.check_masters,
                    reconstruct_mass=_raised_project.reconstruct_mass,
                    workdir=_raised_workdir,
                    parallel="physical",
                    resume=True,
                )
                raised_kira_cache_modes[_raised_key] = (
                    "current project run/resume"
                )
            except KiraWorkdirError as _raised_error:
                if "does not match" not in str(_raised_error):
                    raise
                raised_kira_cache_modes[_raised_key] = (
                    "stale cache rejected: current fingerprint differs"
                )
            continue

        if not (_raised_workdir / "kirapy.json").is_file():
            raised_kira_cache_modes[_raised_key] = "no cached manifest"
            continue
        try:
            raised_kira_reductions[_raised_key] = raised_kira.load(
                _raised_workdir,
                project=_raised_project,
            )
            raised_kira_cache_modes[_raised_key] = (
                "verified current-project cache"
            )
        except KiraWorkdirError as _raised_error:
            if "does not match" not in str(_raised_error):
                raise
            raised_kira_cache_modes[_raised_key] = (
                "stale cache rejected: current fingerprint differs"
            )
    return (
        raised_kira_cache_modes,
        raised_kira_doctor,
        raised_kira_reductions,
        raised_kira_work_root,
    )


@app.cell
def _(
    physical_reduction_audit,
    raised_external_projects,
    raised_kira_reductions,
    smoke_projects,
):
    if (
        set(raised_kira_reductions) == set(raised_external_projects)
        and all(result.complete for result in raised_kira_reductions.values())
    ):
        raised_external_audits = audit_raised_external_reductions(
            raised_kira_reductions,
            projects=raised_external_projects,
        )
        raised_external_boundaries = build_raised_external_master_boundaries(
            raised_external_audits,
            projects=raised_external_projects,
        )
    else:
        raised_external_audits = ()
        raised_external_boundaries = ()
    if (
        physical_reduction_audit is not None
        and physical_reduction_audit.exact
        and len(raised_external_audits) == 4
    ):
        master_insertion_audit = build_master_insertion_audit(
            physical_reduction_audit,
            raised_external_audits,
            ordinary_projects=smoke_projects,
            raised_projects=raised_external_projects,
        )
    else:
        master_insertion_audit = None
    return (
        master_insertion_audit,
        raised_external_audits,
        raised_external_boundaries,
    )


@app.cell(hide_code=True)
def _(
    mo,
    raised_external_audits,
    raised_external_projects,
    raised_kira_cache_modes,
    raised_kira_doctor,
    raised_kira_reductions,
    raised_kira_work_root,
    spenso_table,
):
    raised_complete = sum(
        result.complete for result in raised_kira_reductions.values()
    )
    raised_full_cache = raised_complete == len(raised_external_projects)
    raised_runtime_label = (
        f"Kira {raised_kira_doctor.version}"
        if raised_kira_doctor is not None
        else "Cached Kira outputs"
    )
    _raised_project_rows = []
    for _key in sorted(raised_external_projects):
        _result = raised_kira_reductions.get(_key)
        _raised_project_rows.append(
            {
                "project": _key,
                "load mode": raised_kira_cache_modes[_key],
                "complete": False if _result is None else _result.complete,
                "rules": 0 if _result is None else len(_result.rules),
                "masters": () if _result is None else _result.masters,
            }
        )
    raised_kira_summary = mo.vstack(
        [
            mo.callout(
                f"{raised_runtime_label}: {raised_complete}/"
                f"{len(raised_external_projects)} finite-virtuality jobs "
                f"complete; {len(raised_external_audits)}/4 exact "
                "numerator/master audits assembled.",
                kind=(
                    "success"
                    if raised_full_cache
                    and len(raised_external_audits) == 4
                    and all(audit.exact for audit in raised_external_audits)
                    else "neutral" if raised_complete == 0 else "warn"
                ),
            ),
            spenso_table(_raised_project_rows, pagination=False),
        ]
    )
    raised_kira_summary
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 4. Analytic master insertion and current assembly boundary

    Every displayed master now uses the physical relation $d=4-2 epsilon$;
    $d$ and $epsilon$ are not treated as independent regulators.

    The raw paper formulas retain their Minkowski/Cutkosky phases
    $i$, $-1$, and $-i$. The reusable values strip those phases and include the
    retained MS-bar loop factor. Theta-function support is metadata, because it
    depends on energy orientations not determined by invariant arguments alone.

    The first ledger below labels raw-paper, phase-stripped, and shared master
    factors explicitly. The second ledger is only the phase-stripped physical
    handoff. In particular, its cut edges carry $2 pi$, not the raw Cutkosky
    $2 pi i$; the exact conversion is checked through the recorded master
    phases.

    The scalar masters own the loop measure and cut-edge factors. The external
    $upright(d)p^2/(2 pi)$ integration, the DIS-only $1/(4 pi)$, spin/color
    averages, couplings, and graph weights remain outside. In particular,
    $upright(d)p^2/(2 pi)$ times $1/(4 pi)$ gives the manuscript's
    $upright(d)p^2/(8 pi^2)$.
    """)
    return


@app.cell(hide_code=True)
def _(spenso_table):
    Q2 = DIS_KINEMATICS.photon_scale
    p2 = DIS_KINEMATICS.incoming_virtuality
    s2 = DIS_KINEMATICS.final_state_invariant
    mu2 = DIS_KINEMATICS.renormalization_scale
    gamma_e = Expression.EULER_GAMMA
    physical_dimension = 4 - 2 * epsilon
    master_arguments = {
        "dimension": physical_dimension,
        "epsilon": epsilon,
        "mu_squared": mu2,
        "euler_gamma": gamma_e,
    }
    spenso_table(
        [
            {
                "master": "paper B(-Q^2)",
                "expression": paper_uncut_bubble(
                    -Q2,
                    dimension=physical_dimension,
                ),
                "support": MASTER_SUPPORT["uncut_bubble"].branch,
            },
            {
                "master": "reusable B(-Q^2)",
                "expression": uncut_bubble(-Q2, **master_arguments),
                "support": MASTER_SUPPORT["uncut_bubble"].branch,
            },
            {
                "master": "paper Bcut(s)",
                "expression": paper_cut_bubble(
                    s2,
                    dimension=physical_dimension,
                ),
                "support": MASTER_SUPPORT["cut_bubble"].theta_factors,
            },
            {
                "master": "reusable Bcut(s)",
                "expression": massless_cut_bubble(s2, **master_arguments),
                "support": MASTER_SUPPORT["cut_bubble"].theta_factors,
            },
            {
                "master": "paper Tcut(p^2,-Q^2,s)",
                "expression": paper_cut_triangle(
                    p2,
                    -Q2,
                    s2,
                    dimension=physical_dimension,
                ),
                "support": MASTER_SUPPORT["cut_triangle"].theta_factors,
            },
            {
                "master": "reusable Tcut(p^2,-Q^2,s)",
                "expression": massless_cut_triangle(
                    p2,
                    -Q2,
                    s2,
                    **master_arguments,
                ),
                "support": MASTER_SUPPORT["cut_triangle"].theta_factors,
            },
        ],
        pagination=False,
    )
    return (master_arguments,)


@app.cell(hide_code=True)
def _(master_arguments, spenso_table):
    master_ledger = [
        {
            "convention": entry.convention,
            "factor": entry.name,
            "value": entry.factor,
            "owner/applied": entry.included_in or "external",
        }
        for entry in master_normalization_ledger(**master_arguments)
    ]
    spenso_table(master_ledger, pagination=False)
    return


@app.cell(hide_code=True)
def _(spenso_table):
    physical_handoff_ledger = [
        {
            "channel": channel,
            "factor": entry.name,
            "value": entry.value,
            "owner/applied": (
                entry.owner,
                entry.applied_in_physical_handoff,
            ),
        }
        for channel, normalization in NORMALIZATION_LEDGER.items()
        for entry in normalization.entries
    ]
    spenso_table(physical_handoff_ledger, pagination=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Available master insertions and unresolved assembly inputs

    A coefficient/master product is displayed as soon as the corresponding
    exact boundary can be formed. It remains unweighted: external cut states,
    graph weights, raised-cut signs, oriented support, and derivative endpoints
    are retained explicitly. A partial Kira cache is useful intermediate output,
    but the strict 32-record insertion audit is only constructed when its full
    ordinary and raised inputs are present.
    """)
    return


@app.cell(hide_code=True)
def _(
    master_insertion_audit,
    mo,
    physical_reduction_audit,
    raised_external_boundaries,
    spenso_table,
):
    _ordinary_boundaries = (
        () if master_insertion_audit is None else master_insertion_audit.ordinary
    )
    _raised_boundaries = (
        raised_external_boundaries
        if master_insertion_audit is None
        else master_insertion_audit.raised
    )
    _coefficient_count = (
        0
        if physical_reduction_audit is None
        else len(physical_reduction_audit.coefficients)
    )
    if master_insertion_audit is not None:
        _boundary_status = mo.callout(
            f"Analytic masters inserted for "
            f"{len(_ordinary_boundaries)} ordinary and "
            f"{len(_raised_boundaries)} raised records. Physical assembly "
            "remains blocked by the recorded convention inputs.",
            kind="success",
        )
    else:
        _boundary_status = mo.callout(
            f"Current partial state: {_coefficient_count}/32 cached coefficient "
            f"records and {len(_raised_boundaries)}/4 raised "
            "master boundaries are available. Complete master insertion and "
            "the physical graph sum remain pending.",
            kind="warn" if _coefficient_count or _raised_boundaries else "neutral",
        )
    _boundary_items = [_boundary_status]
    if _ordinary_boundaries:
        _boundary_items.append(
            spenso_table(
                [
                    {
                        "project": boundary.audit.handoff.project_key,
                        "graph": boundary.audit.handoff.graph_name,
                        "observable": boundary.audit.handoff.observable,
                        "analytic master": boundary.identity.kind,
                        "unweighted loop term": boundary.unweighted_loop_term,
                        "external lines": tuple(
                            (
                                state.line,
                                state.denominator_power,
                                state.cut_order,
                            )
                            for state in boundary.external_lines
                        ),
                        "physical blockers": "; ".join(
                            blocker.description for blocker in boundary.blockers
                        ),
                    }
                    for boundary in _ordinary_boundaries
                ],
                pagination=False,
            )
        )
    if _raised_boundaries:
        _boundary_items.append(
            spenso_table(
                [
                    {
                        "project": boundary.audit.project_key,
                        "graph": boundary.audit.graph_name,
                        "observable": boundary.audit.observable,
                        "derivative cut": (
                            boundary.derivative.line,
                            boundary.derivative.order,
                        ),
                        "analytic master": boundary.identity.kind,
                        "unweighted loop term": boundary.unweighted_term,
                        "physical blockers": "; ".join(
                            blocker.description for blocker in boundary.blockers
                        ),
                    }
                    for boundary in _raised_boundaries
                ],
                pagination=False,
            )
        )
    mo.vstack(_boundary_items)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    = Validation and comparisons

    Everything below checks, compares, or records provenance for the calculation
    above. These tables do not feed values back into the reduction pipeline.

    == Exact algebraic residuals
    """)
    return


@app.cell(hide_code=True)
def _(
    apart_expression,
    numerator_audits,
    physical_reduction_audit,
    projected_numerators,
    raised_external_audits,
    spenso_table,
):
    _apart_residual = (
        apart_expression
        - 1 / prod(DIS_KINEMATICS.scalar_denominators[:4])
    ).expand().together().cancel()
    _residual_items = [
        spenso_table(
            [
                {
                    "check": "crossed-box apart reconstruction",
                    "residual": _apart_residual,
                    "status": "pass" if _apart_residual == E("0") else "fail",
                }
            ],
            pagination=False,
        ),
        spenso_table(
            [
                {
                    "graph": audit.graph_name,
                    "observable": audit.observable,
                    "retained lines": audit.retained_loop_lines,
                    "numerator reconstruction residual": audit.residual,
                }
                for audit in numerator_audits
            ],
            pagination=False,
        ),
        spenso_table(
            [
                {
                    "graph": name,
                    "leading-power Ward q_mu q_nu contraction": (
                        numerator.ward
                        .replace(p_squared, E("0"))
                        .replace(d, 4 - 2 * epsilon)
                        .expand()
                        .together()
                        .cancel()
                    ),
                }
                for name, numerator in projected_numerators.items()
            ],
            pagination=False,
        ),
        spenso_table(
            [
                {
                    "master check": name,
                    "residual": residual,
                    "status": "pass" if residual == E("0") else "fail",
                }
                for name, residual in NORMALIZATION_SELF_CHECKS.items()
            ],
            pagination=False,
        ),
    ]
    if physical_reduction_audit is not None:
        _residual_items.append(
            spenso_table(
                [
                    {
                        "project": record.handoff.project_key,
                        "graph": record.handoff.graph_name,
                        "observable": record.handoff.observable,
                        "one-master residual": record.residual,
                    }
                    for record in physical_reduction_audit.coefficients
                ],
                pagination=False,
            )
        )
    if raised_external_audits:
        _residual_items.append(
            spenso_table(
                [
                    {
                        "project": audit.project_key,
                        "graph": audit.graph_name,
                        "observable": audit.observable,
                        "one-master residual": audit.residual,
                    }
                    for audit in raised_external_audits
                ],
                pagination=False,
            )
        )
    mo.vstack(_residual_items)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Historical Mathematica formulas are regression references

    The sibling `DY_calculation.nb` does not contain a DIS graph derivation.
    Its `MPDISgluonic` and final `MPDISfermionic` cells are closed expressions
    inserted into a Drell--Yan scheme-change check. We retain them because they
    give useful all-$epsilon$, pole, finite, and distribution-canonicalization
    regressions, not because their names make them a native DIS result.

    The fermion reference is represented by separate $delta(1-x)$, $D_0$,
    $D_1$, and ordinary coefficients. Smooth factors multiply those typed
    distributions before endpoint evaluation; the notebook's invalid formal
    substitution that produced `delta(0)` is not reproduced. Agreement in the
    rows below checks internal consistency of the manually transcribed reference
    only. It neither parses the source notebook nor establishes a native-to-
    historical convention map, and it cannot replace the graph sum,
    external-cut derivatives, oriented multiplicities, or the active-paper
    projector map.
    """)
    return


@app.cell(hide_code=True)
def _(mo, spenso_table):
    _reference = MATHEMATICA_REFERENCE
    _fermion_pole = _reference.fermion_pole_bracket
    _fermion_finite = _reference.fermion_finite_bracket
    _fermion_dy = mathematica_dy_fermion_conversion()

    def _plus(coefficient, order):
        return (
            coefficient.plus[order]
            if order < len(coefficient.plus)
            else E("0")
        )

    _fermion_check = MATHEMATICA_REFERENCE_SELF_CHECKS[
        "fermion pole residual"
    ]
    mo.vstack(
        [
            spenso_table(
                [
                    {
                        "reference": "gluon compact all-epsilon input",
                        "delta(1-x)": E("0"),
                        "D0": E("0"),
                        "D1": E("0"),
                        "ordinary expression": _reference.gluon_all_epsilon,
                        "provenance": _reference.source["gluon"],
                    },
                    {
                        "reference": "gluon pole plus finite input",
                        "delta(1-x)": E("0"),
                        "D0": E("0"),
                        "D1": E("0"),
                        "ordinary expression": _reference.gluon_through_finite,
                        "provenance": _reference.source["gluon"],
                    },
                    {
                        "reference": "fermion pole bracket",
                        "delta(1-x)": _fermion_pole.delta,
                        "D0": _plus(_fermion_pole, 0),
                        "D1": _plus(_fermion_pole, 1),
                        "ordinary expression": _fermion_pole.regular,
                        "provenance": _reference.source["fermion"],
                    },
                    {
                        "reference": "fermion finite bracket",
                        "delta(1-x)": _fermion_finite.delta,
                        "D0": _plus(_fermion_finite, 0),
                        "D1": _plus(_fermion_finite, 1),
                        "ordinary expression": _fermion_finite.regular,
                        "provenance": _reference.source["fermion"],
                    },
                ],
                pagination=False,
            ),
            spenso_table(
                [
                    {
                        "regression": "compact gluon expansion",
                        "delta coefficient": E("0"),
                        "D0 coefficient": E("0"),
                        "D1 coefficient": E("0"),
                        "ordinary coefficient": (
                            MATHEMATICA_REFERENCE_SELF_CHECKS[
                                "gluon expansion residual"
                            ]
                        ),
                    },
                    {
                        "regression": "fermion distribution canonicalization",
                        "delta coefficient": _fermion_check.delta,
                        "D0 coefficient": _plus(_fermion_check, 0),
                        "D1 coefficient": _plus(_fermion_check, 1),
                        "ordinary coefficient": _fermion_check.regular,
                    },
                    {
                        "regression": "two-beam DY gluon conversion",
                        "delta coefficient": E("0"),
                        "D0 coefficient": E("0"),
                        "D1 coefficient": E("0"),
                        "ordinary coefficient": mathematica_dy_gluon_conversion(),
                    },
                    {
                        "regression": "typed two-beam DY fermion conversion",
                        "delta coefficient": _fermion_dy.delta,
                        "D0 coefficient": _plus(_fermion_dy, 0),
                        "D1 coefficient": _plus(_fermion_dy, 1),
                        "ordinary coefficient": _fermion_dy.regular,
                    },
                ],
                pagination=False,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Paper targets are targets, not derived answers

    The two scale-dependent equations at active-manuscript lines 296--297 are
    both labelled $F_L$, while lines 302--303 give a second, different pair of
    $F_L$ equations. We retain those literal labels and interpret the first pair
    as $F_2$ only in the comparison model.

    A second convention is also explicit: the target expands the undefined
    $P_(g q)(x,0)$ and $P_(q q)(x,0)$ as color-stripped leading-order kernels,
    because the printed equations already put $T_F$ and $C_F$ outside. The
    active printed $P_2/F_2$ normalization still differs from the cited DIS
    source. Until that map is settled, copying these rows cannot turn a native
    calculation into a passing paper residual.
    """)
    return


@app.cell(hide_code=True)
def _(spenso_table):
    target_functions = PAPER_TARGETS.functions
    spenso_table(
        [
            {
                "observable": name,
                "literal source label": PAPER_TARGETS.source_labels[name],
                "delta(1-x)": coefficient.delta,
                "D0 coefficient": (
                    coefficient.plus[0] if coefficient.plus else E("0")
                ),
                "ordinary part": coefficient.regular,
            }
            for name, coefficient in (
                ("F2q", target_functions.F2q),
                ("F2g", target_functions.F2g),
                ("FLq", target_functions.FLq),
                ("FLg", target_functions.FLg),
            )
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(spenso_table):
    spenso_table(
        [
            {
                "source issue": issue.key,
                "severity": issue.severity,
                "description": issue.description,
                "provenance": issue.source,
            }
            for issue in PAPER_TARGETS.issues
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Consolidated validation ledger

    A `pass` below means an exact check was actually executed. `not-run` means
    the necessary stage exists but its subprocess or analytic handoff has not
    run. `blocked` means required source information or a convention choice is
    missing. An available subset is reported in `actual` but does not pass a
    complete-coverage row. Only the conjunction of every required row may set
    `physical_result_validated` to true.
    """)
    return


@app.cell
def _(
    apart_terms,
    kira_reductions,
    master_insertion_audit,
    numerator_audits,
    physical_reduction_audit,
    projected_numerators,
    raised_external_audits,
    smoke_projects,
):
    validation_ledger = build_validation_ledger(
        smoke_projects,
        projected_numerators=projected_numerators,
        numerator_audits=numerator_audits,
        apart_child_count=len(apart_terms),
        kira_reductions=kira_reductions,
        physical_reduction_audit=physical_reduction_audit,
        raised_external_audits=raised_external_audits,
        master_insertion_audit=master_insertion_audit,
    )
    return (validation_ledger,)


@app.cell(hide_code=True)
def _(spenso_table, validation_ledger):
    spenso_table(
        [
            {
                "stage": check.stage,
                "check": check.key,
                "status": check.status,
                "actual": check.actual,
                "reason": check.reason or "",
            }
            for check in validation_ledger.checks
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo, validation_ledger):
    if validation_ledger.physical_result_validated:
        final_status = mo.callout(
            "The native DIS result agrees with the complete physical target.",
            kind="success",
        )
    else:
        blocker_text = "\n".join(
            f"- {check.stage}: {check.key} — {check.reason}"
            for check in validation_ledger.blockers
        )
        final_status = mo.callout(
            "Physical result not yet validated. Remaining hard blockers:\n"
            + blocker_text,
            kind="warn",
        )
    final_status
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Ancillary provenance

    These are pinned source fixtures only. Fetching them remains an explicit
    operation outside notebook evaluation.
    """)
    return


@app.cell(hide_code=True)
def _(spenso_table):
    spenso_table(
        [
            {
                "source fixture": spec.filename,
                "arXiv v1 URL": spec.url,
                "SHA-256": spec.sha256,
                "embeddings": spec.embeddings,
                "rooted records": spec.rooted_records,
                "status": "pinned metadata; fetch is explicit",
            }
            for spec in ANCILLARY_SPECS.values()
        ],
        pagination=False,
    )
    return


if __name__ == "__main__":
    app.run()
