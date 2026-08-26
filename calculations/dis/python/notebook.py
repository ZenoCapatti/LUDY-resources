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
    from calculations.dis.python.physical import (
        DIS_GRAPH_SPECS,
        DIS_KINEMATICS,
        KNOWN_DIS_CUTS,
        NORMALIZATION_LEDGER,
        PAPER_TARGETS,
        audit_projected_numerator_reductions,
        build_kira_smoke_projects,
        build_validation_ledger,
        crossed_box_apart,
        d,
        derive_all_projected_numerators,
        epsilon,
        p_squared,
    )
    from calculations.dy.python.masters import typst_md
    from kirapy import Kira
    from ludy import spenso_table

    _marimo.md = typst_md
    globals()["mo"] = _marimo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    = Native DIS paper-validation notebook

    This notebook reconstructs the NLO DIS input layer used by the active LU
    manuscript. It keeps three kinds of evidence separate:

    - *source transcription*: six graph families, their eight-gamma traces,
      normalizations, and the printed coefficient-function targets;
    - *native algebra*: Spenso gamma simplification, the metric and transverse
      projector contractions, Symbolica multivariate partial fractioning, and
      exact numerator reconstruction;
    - *physical validation*: oriented all-cut weights, Kira reductions, master
      insertion, the $p^2$ integral, pole cancellation, and the final channel
      residual.

    The first two layers are executable below. The third is deliberately not
    called complete while graph signs, multiplicities, and the active-to-historical
    $F_2$ projector normalization remain unresolved. Opening or exporting this
    notebook never launches Kira; the only subprocess is behind the explicit run
    button.
    """)
    return


@app.cell
def _():
    projected_numerators = derive_all_projected_numerators()
    apart_expression, apart_terms = crossed_box_apart()
    numerator_audits = audit_projected_numerator_reductions(
        projected_numerators
    )

    smoke_projects = build_kira_smoke_projects()
    return (
        apart_expression,
        apart_terms,
        numerator_audits,
        projected_numerators,
        smoke_projects,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 1. Exact finite-virtuality kinematics

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
    denominator_rows = [
        {
            "line": f"D{index}",
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
    == 2. Six physical graphs and their source traces

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
                "photon slots": _graph.trace.photon_slots,
                "source trace": source_chain,
            }
        )
    spenso_table(graph_rows, pagination=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 3. Spenso projectors and physical numerators

    The active manuscript prints an uppercase $P$ without defining it. Its cited
    DIS source does define the transverse vector

    $ P^mu=p^mu-frac(p dot q,q^2)q^mu, quad P dot q=0. $

    We use that definition explicitly. For every graph, Spenso evaluates five
    traces: the metric contraction and the $p p$, $p q$, $q p$, and $q q$
    contractions of the two photon slots. Linearity then constructs
    $P_mu P_nu N^(mu nu)/P^2$ without wrapping $P$ in an opaque atom.

    The table shows the printed-manuscript projector result after the transparent
    leading-power display replacement $p^2=0$ and $d=4-2 epsilon$. The full
    finite-$p^2$ expressions, not these shortened displays, are what the exact
    numerator-reconstruction checks use.
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
            {
                "graph": graph_choice.value,
                "contraction": "Ward q_mu q_nu",
                "leading-power numerator": display_limit(
                    selected_numerator.ward
                ),
            },
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 4. Native partial fractioning and numerator reduction

    Symbolica's multivariate `apart(kk,kp,kq)` rewrites
    $1/(D_1D_2D_3D_4)$ into four three-denominator children. Their alternating
    coefficients are retained as exact expressions, and the sum reconstructs
    the four-line kernel with zero residual.

    Each projected numerator is then rewritten in independent denominator
    coordinates. The graph's actual base powers are used: in particular, both
    boxes start at $(1,2,1)$, the bubble at $(1,0,1)$, and the LSZ graph at
    $(1,1,0)$. A zero residual means the shifted family integrals reconstruct
    the original rational integrand exactly; it is not an IBP result yet.
    """)
    return


@app.cell(hide_code=True)
def _(apart_expression, apart_terms, spenso_table):
    apart_rows = [
        {
            "retained graph lines": tuple(
                index + 1 for index in term.retained_indices
            ),
            "coefficient": term.coefficient,
        }
        for term in apart_terms
    ]
    apart_rows.append(
        {
            "retained graph lines": "all four children",
            "coefficient": (
                apart_expression
                - 1
                / prod(DIS_KINEMATICS.scalar_denominators[:4])
            )
            .expand()
            .together()
            .cancel(),
        }
    )
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
                "shifted terms": audit.term_count,
                "reconstruction residual": audit.residual,
            }
            for audit in numerator_audits
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 5. The full structural all-cut contribution

    The iterated discontinuity has four logical pieces: both external channel
    poles, an internal initial cut with the external final pole, the external
    initial pole with an internal final cut, and a pair of internal cuts sharing
    one edge. Expanding those possibilities in the common $D$ basis gives six
    channel patterns. Intersecting them with each graph's nonzero propagator
    support leaves the 15 rows below.

    `order 0` denotes an ordinary cut delta. `order 1` exposes the derivative
    generated by a raised propagator: $D_2^2$ in the two boxes, $D_6^2$ in the
    bubble, or $D_5^2$ in the LSZ graph. This is the complete *structural*
    coverage. Cut orientations, relative signs, and multiplicities are still
    missing source data, so the weighted all-cut sum is not fabricated.
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
                "sign": "missing" if cut.relative_sign is None else cut.relative_sign,
                "multiplicity": (
                    "missing" if cut.multiplicity is None else cut.multiplicity
                ),
            }
            for cut in KNOWN_DIS_CUTS
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 6. Cut-specialized Kira projects and master handoff

    External $D_5,D_6$ cuts specialize the invariant rules but never become Kira
    propagators. Internal cut lines are written to `cut_propagators` using local
    one-based family positions. The complete smoke target cube
    $a_i in {1,0,-1}$ is filtered so every cut index stays positive; the physical
    raised target $(1,2,1)$ is added where needed.

    The expected scalar basis is $B(q^2)$, $slash(B)(p^2)$,
    $slash(B)((p+q)^2)$, and the fully three-mass $slash(T)$. These identities
    are supplied to Kira as checked preferred masters. The button below asks
    Kira 3.1 to verify all 16 cut-specialized scalar-basis jobs; they are smoke
    reductions, not the still-missing graph-level numerator reductions.
    """)
    return


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
    if run_kira.value:
        kira = Kira()
        kira_doctor = kira.doctor()
        kira_doctor.raise_for_errors()
        kira_reductions = {}
        kira_work_root = repository_root / "runs" / "dis-paper-kirapy"
        for _project_key, _project_input in sorted(smoke_projects.items()):
            _project = _project_input.project
            kira_reductions[_project_key] = kira.reduce(
                family=_project.family,
                kinematics=_project.kinematics,
                targets=_project.targets,
                bounds=_project.bounds,
                dimension=_project.dimension,
                preferred_masters=_project.preferred_masters,
                check_masters=_project.check_masters,
                reconstruct_mass=_project.reconstruct_mass,
                workdir=kira_work_root / _project.family.name,
                parallel="physical",
                resume=True,
            )
    else:
        kira_doctor = None
        kira_reductions = {}
        kira_work_root = repository_root / "runs" / "dis-paper-kirapy"
    return kira_doctor, kira_reductions, kira_work_root


@app.cell(hide_code=True)
def _(kira_doctor, kira_reductions, kira_work_root, mo, spenso_table):
    if not kira_reductions:
        kira_summary = mo.callout(
            f"Ready; no Kira subprocess was started. Work root: {kira_work_root}",
            kind="neutral",
        )
    else:
        complete = sum(result.complete for result in kira_reductions.values())
        kira_summary = mo.vstack(
            [
                mo.callout(
                    f"Kira {kira_doctor.version}: {complete}/{len(kira_reductions)} "
                    "cut-specialized reductions complete.",
                    kind=(
                        "success"
                        if complete == len(kira_reductions)
                        else "warn"
                    ),
                ),
                spenso_table(
                    [
                        {
                            "project": key,
                            "complete": result.complete,
                            "rules": len(result.rules),
                            "masters": result.masters,
                        }
                        for key, result in sorted(kira_reductions.items())
                    ],
                    pagination=False,
                ),
            ]
        )
    kira_summary
    return


@app.cell
def _(
    apart_terms,
    kira_reductions,
    numerator_audits,
    projected_numerators,
    smoke_projects,
):
    validation_ledger = build_validation_ledger(
        smoke_projects,
        projected_numerators=projected_numerators,
        numerator_audits=numerator_audits,
        apart_child_count=len(apart_terms),
        kira_reductions=kira_reductions,
    )
    return (validation_ledger,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 7. Analytic one-loop masters and normalization ownership

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
def _(spenso_table):
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
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 8. Paper targets are targets, not derived answers

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
    == 9. Validation ledger

    A `pass` below means an exact check was actually executed. `not-run` means
    the necessary stage exists but its subprocess or analytic handoff has not
    run. `blocked` means required source information or a convention choice is
    missing. Only the conjunction of every required row may set
    `physical_result_validated` to true.
    """)
    return


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
