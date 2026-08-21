import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path
    import sys

    import marimo as mo

    _repository_root = str(Path(__file__).resolve().parents[1])
    if _repository_root not in sys.path:
        sys.path.insert(0, _repository_root)

    from calculations.dy.python.masters import (
        apply_endpoint_expansion,
        endpoint_distribution_expansion,
        massive_cut_bubble,
        massive_cut_triangle,
        maximal_cross_box_cut_master,
        virtuality_integral_factor,
    )
    from kirapy import Kira
    from ludy import (
        apply_ibp_reductions,
        apply_kinematic_rules,
        assemble_ibp_expression,
        build_kira_projects,
        cut_filter_masters,
        find_loop_propagator_indices,
        gamma_trace_to_dots,
        identify_masters,
        momentum_printer,
        normalize_rational,
        partition_cuts,
        prepare_pre_ibp,
        project_cutset,
        propagator_denominators,
        run_kira_projects,
        spenso_table,
        square,
        validate_pre_ibp,
    )
    from symbolica import E, Expression, N, S
    from symbolica.community.spenso import Representation, TensorName, dot

    return (
        E,
        Expression,
        Kira,
        N,
        Path,
        Representation,
        S,
        TensorName,
        apply_endpoint_expansion,
        apply_ibp_reductions,
        apply_kinematic_rules,
        assemble_ibp_expression,
        build_kira_projects,
        cut_filter_masters,
        dot,
        endpoint_distribution_expansion,
        find_loop_propagator_indices,
        gamma_trace_to_dots,
        identify_masters,
        massive_cut_bubble,
        massive_cut_triangle,
        maximal_cross_box_cut_master,
        mo,
        momentum_printer,
        normalize_rational,
        partition_cuts,
        prepare_pre_ibp,
        project_cutset,
        propagator_denominators,
        run_kira_projects,
        spenso_table,
        square,
        validate_pre_ibp,
        virtuality_integral_factor,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Physical DY diagram runner

    This companion notebook applies the reusable helpers defined and tested in
    [`ludy.py`](ludy.py) to the first physical diagram: the crossed box.  It
    derives the metric-contracted Dirac trace, prepares the numerator for IBP,
    reduces the three affine cut blocks, attaches the analytic maximal-cut
    master, performs the leading virtuality integrations, and records the
    endpoint result in the standard delta/plus basis.

    The output here is a **physical crossed-box contribution**, not yet the
    complete physical DY coefficient function.  Gauge independence, graph
    multiplicities, UV renormalization, mass factorization, and cancellation
    against the box and remaining real/virtual diagrams will be added one
    diagram at a time and validated before their sum is called physical.

    Project construction and all analytic work before Kira are side-effect
    free.  Kira starts only when the explicit run control is pressed.  The
    physical trace uses one native integration dimension \(d\) throughout and
    therefore has a fresh work root; the older `mink(D)` manifests are left
    untouched.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Kinematics and the physical crossed-box numerator

    We use \(z=m^2/s\), with \(0<z<1\) for ordinary functions and
    \(z\in[0,1]\) after endpoint distributions are introduced.  Here \(s\) is
    the leading-power light-cone scale.  The exact finite-virtuality relation is

    \[
      2p_1\!\cdot p_2=s+\frac{p_1^2p_2^2}{s},
    \]

    and only the explicitly marked leading-power step below replaces it by
    \(2p_1\!\cdot p_2=s\).

    The numerator is the paper's metric-contracted trace

    \[
    \operatorname{Tr}\!\left[
      \slashed p_1\gamma^\sigma(\slashed k-\slashed p_1)\gamma^\mu
      \slashed p_2\gamma_\sigma(\slashed k-\slashed p_2)\gamma_\mu
    \right].
    \]

    Couplings, colour, spin/colour averages, the crossed-box graph sign, and
    observable normalizations are deliberately not part of this trace.
    """)
    return


@app.cell
def _(
    Expression,
    N,
    Representation,
    S,
    TensorName,
    dot,
    find_loop_propagator_indices,
    gamma_trace_to_dots,
    momentum_printer,
    project_cutset,
    propagator_denominators,
    square,
):
    dimension = S("d")
    epsilon = S("ε")
    mu_squared = S("μ") ** 2
    cutoff_squared = S("Λ") ** 2
    s = S("s")
    z = S("z")
    euler_gamma = Expression.EULER_GAMMA

    minkowski = Representation.mink(dimension=dimension)
    momentum = TensorName.vector("p", print=momentum_printer("p"))
    loop_momentum = TensorName.vector(
        "k",
        tags=["ludy::loop_momentum"],
        print=momentum_printer("k"),
    )
    p1 = momentum(1, minkowski)
    p2 = momentum(2, minkowski)
    k1 = loop_momentum(1, minkowski)
    q = S("q")

    propagators = [
        (p1, N(0)),
        (p2, N(0)),
        (k1, N(0)),
        (k1 - p1, N(0)),
        (p2 - k1, N(0)),
        (p1 + p2 - k1, q**2),
    ]
    cutsets = {
        "11": (1, 1, 1, 0, 0, 1),
        "10": (1, 0, 1, 0, 1, 1),
        "01": (0, 1, 1, 1, 0, 1),
        "00": (0, 0, 1, 1, 1, 1),
    }
    denominators = propagator_denominators(propagators)
    loop_propagator_indices = find_loop_propagator_indices(propagators)
    loop_denominators = [
        denominators[_index] for _index in loop_propagator_indices
    ]
    projected_cutsets = {
        _name: project_cutset(_mask, loop_propagator_indices)
        for _name, _mask in cutsets.items()
    }
    loop_scalar_products = [
        square(k1),
        dot(k1, p1),
        dot(k1, p2),
    ]
    delta = q**2 - 2 * dot(p1, p2)

    physical_numerator = gamma_trace_to_dots(
        [p1, None, k1 - p1, None, p2, None, k1 - p2, None],
        ["rho1", "sigma", "rho2", "mu", "rho3", "sigma", "rho4", "mu"],
        lorentz_dimension=dimension,
    )
    return (
        cutoff_squared,
        cutsets,
        delta,
        denominators,
        dimension,
        epsilon,
        euler_gamma,
        k1,
        loop_denominators,
        loop_propagator_indices,
        loop_scalar_products,
        mu_squared,
        p1,
        p2,
        physical_numerator,
        projected_cutsets,
        propagators,
        q,
        s,
        z,
    )


@app.cell(hide_code=True)
def _(
    cutoff_squared,
    dimension,
    epsilon,
    mo,
    mu_squared,
    physical_numerator,
    s,
    spenso_table,
    z,
):
    mo.vstack(
        [
            spenso_table(
                [
                    {"quantity": "z", "value": z, "meaning": "m²/s"},
                    {"quantity": "s", "value": s, "meaning": "LP light-cone scale"},
                    {"quantity": "d", "value": dimension, "meaning": "integration dimension"},
                    {"quantity": "ε", "value": epsilon, "meaning": "d = 4 - 2ε"},
                    {"quantity": "μ_R²", "value": mu_squared, "meaning": "renormalization scale squared"},
                    {"quantity": "Λ²", "value": cutoff_squared, "meaning": "common final beam-virtuality cutoff"},
                ],
                pagination=False,
                selection=None,
            ),
            mo.md("### Native metric-contracted trace"),
            spenso_table(
                [{"diagram": "crossed box", "numerator": physical_numerator}],
                pagination=False,
                selection=None,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Normalization ownership

    The reduction acts only on the kinematic trace.  The following factors are
    named separately so that a convention change cannot be hidden inside a
    numerator:

    - \(e_q^2g_s^2\), the coupling factor;
    - \(T_F(N_c^2-1)\), the crossed-box colour sum;
    - \(1/(2N_c)^2\), the incoming quark/antiquark spin-colour average;
    - the graph/discontinuity sign;
    - \(s\), converting a result differential in \(m^2\) to \(d/dz\);
    - an observable factor.

    The analytic master functions already contain \(d^dk/(2\pi)^d\), their
    internal \(2\pi\) cut factors, and the retained MS-bar normalization.  We
    add only the remaining external \(dp_i^2/(2\pi)\) factors.  The DIS
    \(1/(4\pi)\) is algebraically allowed to multiply a numerator because it is
    loop-independent, but semantically it is an observable/measure factor and
    stays in this ledger.  It is not applied to the DY crossed box below.
    """)
    return


@app.cell
def _(Expression, S, s, spenso_table):
    electric_charge = S("eq")
    strong_coupling = S("gs")
    color_count = S("Nc")
    trace_normalization = S("TF")
    coupling_factor = electric_charge**2 * strong_coupling**2
    color_factor = trace_normalization * (color_count**2 - 1)
    incoming_average = 1 / (2 * color_count) ** 2
    graph_sign = -1
    density_jacobian = s
    dy_observable_factor = 1
    dis_observable_factor = 1 / (4 * Expression.PI)
    dy_weight = (
        graph_sign
        * coupling_factor
        * color_factor
        * incoming_average
        * density_jacobian
        * dy_observable_factor
    )
    spenso_table(
        [
            {"layer": "couplings", "factor": coupling_factor},
            {"layer": "colour sum", "factor": color_factor},
            {"layer": "incoming average", "factor": incoming_average},
            {"layer": "crossed-box sign", "factor": graph_sign},
            {"layer": "d/dm² → d/dz", "factor": density_jacobian},
            {"layer": "DY observable", "factor": dy_observable_factor},
            {"layer": "DIS-only observable", "factor": dis_observable_factor},
            {"layer": "DY weight used below", "factor": dy_weight},
        ],
        pagination=False,
        selection=None,
    )
    return dis_observable_factor, dy_weight


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Prepare every affine child and retain the maximal cut

    `prepare_pre_ibp` applies the same exact partial-fraction and numerator
    reduction chain walked through in `ludy.py`.  The physical trace is
    quadratic in loop scalar products, so every resulting three-line target
    remains inside the existing \(\{1,0,-1\}^3\) cube.

    Cuts `11`, `10`, and `01` omit at least one loop propagator and can use
    those affine children.  Cut `00` requires all four loop lines at once and
    branches directly from the unpartial-fractioned graph.  It is not an IBP
    family and is never silently dropped.
    """)
    return


@app.cell
def _(
    E,
    apply_kinematic_rules,
    delta,
    dot,
    k1,
    loop_denominators,
    loop_propagator_indices,
    loop_scalar_products,
    p1,
    p2,
    partition_cuts,
    physical_numerator,
    prepare_pre_ibp,
    projected_cutsets,
    s,
    square,
):
    physical_pre_ibp = prepare_pre_ibp(
        numerator=physical_numerator,
        loop_denominators=loop_denominators,
        loop_scalar_products=loop_scalar_products,
        loop_propagator_indices=loop_propagator_indices,
        delta=delta,
    )
    reducible_cut_names, direct_cut_names = partition_cuts(
        physical_pre_ibp,
        projected_cutsets,
    )
    contributions_by_cut = {
        _cut_name: list(physical_pre_ibp.contributions)
        for _cut_name in reducible_cut_names
    }
    on_shell_rules_by_cut = {
        "11": ((square(p1), E("0")), (square(p2), E("0"))),
        "10": ((square(p1), E("0")),),
        "01": ((square(p2), E("0")),),
        "00": (),
    }
    maximal_cut_numerator = apply_kinematic_rules(
        physical_numerator,
        (
            (square(k1), E("0")),
            (dot(k1, p1), square(p1) / 2),
            (dot(k1, p2), square(p2) / 2),
            (square(p1), E("0")),
            (square(p2), E("0")),
            (dot(p1, p2), s / 2),
        ),
    )
    return (
        contributions_by_cut,
        direct_cut_names,
        maximal_cut_numerator,
        on_shell_rules_by_cut,
        physical_pre_ibp,
        reducible_cut_names,
    )


@app.cell(hide_code=True)
def _(
    direct_cut_names,
    maximal_cut_numerator,
    mo,
    physical_pre_ibp,
    reducible_cut_names,
    spenso_table,
):
    mo.vstack(
        [
            spenso_table(
                [
                    {
                        "partial-fraction children": len(
                            physical_pre_ibp.partial_fractions
                        ),
                        "numerator reductions": len(
                            physical_pre_ibp.numerator_reductions
                        ),
                        "IBP contributions": len(
                            physical_pre_ibp.contributions
                        ),
                    }
                ],
                pagination=False,
                selection=None,
            ),
            spenso_table(
                [
                    {
                        "cut": _name,
                        "route": (
                            "three-line affine children"
                            if _name in reducible_cut_names
                            else "analytic maximal-cut master"
                        ),
                    }
                    for _name in [*reducible_cut_names, *direct_cut_names]
                ],
                pagination=False,
                selection=None,
            ),
            mo.md("### Maximal-cut master coefficient at leading power"),
            spenso_table(
                [{"cut": "00", "numerator on support": maximal_cut_numerator}],
                pagination=False,
                selection=None,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Build the native Kira projects and exact IBP inputs

    The projects are still numerator-independent: every three-propagator
    family requests the complete \(\{1,0,-1\}^3\) target cube.  Their invariants
    are the native Spenso expressions \(p_1^2\), \(p_1\!\cdot p_2\),
    \(p_2^2\), and \(q^2\).  `kirapy` lowers them to short Fermat-safe wire
    names only at the text boundary and restores the exact native objects on
    load.

    The fresh `runs/dy-cross-box-physical-kirapy/` root is intentional.  These
    projects use `mink(d)`; the older walkthrough cache uses `mink(D)` and is
    neither overwritten nor migrated.
    """)
    return


@app.cell
def _(
    Path,
    assemble_ibp_expression,
    build_kira_projects,
    contributions_by_cut,
    cutsets,
    k1,
    on_shell_rules_by_cut,
    p1,
    p2,
    propagators,
    q,
):
    topology_projects = build_kira_projects(
        k1=k1,
        p1=p1,
        p2=p2,
        q=q,
        propagators=propagators,
        cutsets=cutsets,
    )
    project_keys_by_name = {
        _project.family.name: _project_key
        for _project_key, _project in topology_projects.items()
    }
    project_names = sorted(project_keys_by_name)
    topology_workdir_root = (
        Path(__file__).resolve().parents[1]
        / "runs"
        / "dy-cross-box-physical-kirapy"
    )
    ibp_inputs_by_cut = {
        _cut_name: assemble_ibp_expression(
            _contributions,
            _cut_name,
            topology_projects,
            on_shell_rules_by_cut[_cut_name],
        )
        for _cut_name, _contributions in contributions_by_cut.items()
    }
    return (
        ibp_inputs_by_cut,
        project_keys_by_name,
        project_names,
        topology_projects,
        topology_workdir_root,
    )


@app.cell(hide_code=True)
def _(ibp_inputs_by_cut, mo, spenso_table):
    mo.vstack(
        [
            mo.md("### Physical numerator after affine preparation"),
            spenso_table(
                [
                    {"cut": _cut_name, "exact IBP input": _expression}
                    for _cut_name, _expression in ibp_inputs_by_cut.items()
                ],
                pagination=False,
                selection=None,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo, project_names):
    topology_selector = mo.ui.multiselect(
        options=project_names,
        value=project_names,
        label="Kira families to inspect and run",
        full_width=True,
    )
    topology_selector
    return (topology_selector,)


@app.cell
def _(
    mo,
    project_keys_by_name,
    spenso_table,
    topology_projects,
    topology_selector,
    topology_workdir_root,
):
    selected_project_names = sorted(topology_selector.value)
    selected_topology_projects = {
        project_keys_by_name[_name]: topology_projects[
            project_keys_by_name[_name]
        ]
        for _name in selected_project_names
    }
    _project_rows = [
        {
            "cut": _project_key[0],
            "family": _project.family.name,
            "graph sources": [
                f"D{_source + 1}" for _source in _project_key[1]
            ],
            "propagator momenta": [
                _propagator.momentum
                for _propagator in _project.family.propagators
            ],
            "invariants": [
                _invariant.expression
                for _invariant in _project.kinematics.kinematic_invariants
            ],
            "dimension": _project.dimension,
            "targets": len(_project.targets),
            "preferred masters": list(_project.preferred_masters),
            "workdir": str(topology_workdir_root / _project.family.name),
        }
        for _project_key, _project in selected_topology_projects.items()
    ]
    if _project_rows:
        _inspection = spenso_table(
            _project_rows,
            selection=None,
            pagination=True,
            page_size=12,
        )
    else:
        _inspection = mo.callout(
            "Select at least one topology to inspect it.",
            kind="neutral",
        )
    _inspection
    return selected_project_names, selected_topology_projects


@app.cell(hide_code=True)
def _(mo, selected_project_names):
    _selection = ", ".join(selected_project_names)
    run_selected_topologies = mo.ui.run_button(
        label=(
            f"Run/resume selected physical projects ({_selection})"
            if _selection
            else "Select a Kira project before running"
        ),
        disabled=not selected_project_names,
        kind="warn",
        full_width=True,
    )
    run_selected_topologies
    return (run_selected_topologies,)


@app.cell
def _(
    Kira,
    run_kira_projects,
    run_selected_topologies,
    selected_topology_projects,
    topology_workdir_root,
):
    if run_selected_topologies.value:
        topology_kira_doctor, topology_kira_reductions = run_kira_projects(
            Kira(),
            selected_topology_projects,
            topology_workdir_root,
        )
    else:
        topology_kira_doctor = None
        topology_kira_reductions = {}
    return topology_kira_doctor, topology_kira_reductions


@app.cell(hide_code=True)
def _(mo, spenso_table, topology_kira_doctor, topology_kira_reductions):
    if topology_kira_doctor is None:
        _run_status = mo.callout(
            "Ready. No Kira subprocess has been started by this notebook run.",
            kind="neutral",
        )
    else:
        _result_rows = [
            {
                "family": _reduction.family_name,
                "complete": _reduction.complete,
                "rules": len(_reduction.rules),
                "masters": list(_reduction.masters),
                "missing targets": len(_reduction.missing_targets),
                "unresolved integrals": len(_reduction.unresolved_integrals),
                "workdir": str(_reduction.workdir),
            }
            for _project_key, _reduction in sorted(
                topology_kira_reductions.items()
            )
        ]
        _run_status = mo.vstack(
            [
                mo.callout(
                    f"Kira {topology_kira_doctor.version} completed the "
                    f"{len(_result_rows)} selected project(s).",
                    kind="success",
                ),
                spenso_table(
                    _result_rows,
                    selection=None,
                    pagination=True,
                    page_size=12,
                ),
            ]
        )
    _run_status
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Restore native masters and insert their analytic values

    A cut is evaluated only when all four of its selected family reductions are
    available.  `apply_ibp_reductions` retains every source-family key,
    `cut_filter_masters` imposes the physical cut in graph space, and
    `identify_masters` substitutes only the explicitly surviving massive bubble
    or triangle imported from `masters.py`.

    The returned rules, targets, masters, coefficients, and combined
    expressions are native Symbolica/Spenso objects.  Hashed `kirapy` wire names
    are an implementation detail of the external text boundary and are rejected
    if they survive restoration.
    """)
    return


@app.cell
def _(
    E,
    apply_ibp_reductions,
    contributions_by_cut,
    cut_filter_masters,
    cutsets,
    loop_propagator_indices,
    normalize_rational,
    on_shell_rules_by_cut,
    reducible_cut_names,
    topology_kira_reductions,
    topology_projects,
):
    complete_reducible_cut_names = [
        _cut_name
        for _cut_name in reducible_cut_names
        if all(
            _project_key in topology_kira_reductions
            for _project_key in topology_projects
            if _project_key[0] == _cut_name
        )
    ]
    ibp_terms_by_cut = {}
    master_expressions_by_cut = {}
    cut_expressions_by_cut = {}
    cut_kept_masters_by_cut = {}
    cut_dropped_masters_by_cut = {}
    required_loop_sources_by_cut = {
        _cut_name: tuple(
            _source
            for _source in loop_propagator_indices
            if _mask[_source]
        )
        for _cut_name, _mask in cutsets.items()
    }
    _sources_by_project = {
        _project_key: _project_key[1]
        for _project_key in topology_kira_reductions
    }
    for _cut_name in complete_reducible_cut_names:
        _terms = apply_ibp_reductions(
            contributions_by_cut[_cut_name],
            _cut_name,
            topology_projects,
            topology_kira_reductions,
            on_shell_rules_by_cut[_cut_name],
        )
        ibp_terms_by_cut[_cut_name] = _terms
        _master_expression = normalize_rational(
            sum(
                (_term.reduced_expression() for _term in _terms),
                E("0"),
            )
        )
        master_expressions_by_cut[_cut_name] = _master_expression
        _masters_by_project = {
            _project_key: _result.masters
            for _project_key, _result in topology_kira_reductions.items()
            if _project_key[0] == _cut_name
        }
        (
            cut_expressions_by_cut[_cut_name],
            cut_kept_masters_by_cut[_cut_name],
            cut_dropped_masters_by_cut[_cut_name],
        ) = cut_filter_masters(
            _master_expression,
            masters_by_project=_masters_by_project,
            sources_by_project=_sources_by_project,
            required_source_indices=required_loop_sources_by_cut[_cut_name],
        )
    return (
        complete_reducible_cut_names,
        cut_dropped_masters_by_cut,
        cut_expressions_by_cut,
        cut_kept_masters_by_cut,
        ibp_terms_by_cut,
        master_expressions_by_cut,
        required_loop_sources_by_cut,
    )


@app.cell
def _(
    cut_expressions_by_cut,
    cut_kept_masters_by_cut,
    dimension,
    dot,
    epsilon,
    euler_gamma,
    identify_masters,
    massive_cut_bubble,
    massive_cut_triangle,
    maximal_cross_box_cut_master,
    maximal_cut_numerator,
    mu_squared,
    normalize_rational,
    p1,
    p2,
    q,
    required_loop_sources_by_cut,
    s,
):
    analytic_master_values_by_cut = {
        "11": massive_cut_bubble(
            2 * dot(p1, p2),
            q**2,
            dimension=dimension,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        ),
        "10": massive_cut_triangle(
            dot(p2, p2),
            2 * dot(p1, p2),
            q**2,
            dimension=dimension,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        ),
        "01": massive_cut_triangle(
            dot(p1, p1),
            2 * dot(p1, p2),
            q**2,
            dimension=dimension,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        ),
        "00": maximal_cross_box_cut_master(
            s,
            dimension=dimension,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        ),
    }
    analytic_identifications_by_cut = {"00": []}
    analytic_expressions_by_cut = {
        "00": normalize_rational(
            maximal_cut_numerator * analytic_master_values_by_cut["00"]
        )
    }
    for _cut_name, _kept in cut_kept_masters_by_cut.items():
        _identifications = []
        for _project_key, _master in _kept:
            _source_indices = _project_key[1]
            _expected_powers = tuple(
                int(_source in required_loop_sources_by_cut[_cut_name])
                for _source in _source_indices
            )
            _actual_powers = tuple(int(_argument) for _argument in _master)
            if _actual_powers != _expected_powers:
                raise ValueError(
                    "A surviving cut master does not match its cut incidence: "
                    f"{_master.format_plain()}"
                )
            _identifications.append(
                (_master, analytic_master_values_by_cut[_cut_name])
            )
        analytic_identifications_by_cut[_cut_name] = _identifications
        analytic_expressions_by_cut[_cut_name] = normalize_rational(
            identify_masters(
                cut_expressions_by_cut[_cut_name],
                _identifications,
            )
        )
    return (
        analytic_expressions_by_cut,
        analytic_identifications_by_cut,
        analytic_master_values_by_cut,
    )


@app.cell(hide_code=True)
def _(
    analytic_expressions_by_cut,
    analytic_master_values_by_cut,
    cut_kept_masters_by_cut,
    mo,
    normalize_rational,
    spenso_table,
):
    if analytic_expressions_by_cut:
        _analytic_status = spenso_table(
            [
                {
                    "cut": _cut_name,
                    "route": (
                        "analytic maximal-cut master"
                        if _cut_name == "00"
                        else "Kira IBP"
                    ),
                    "surviving Kira masters": [
                        _master
                        for _project_key, _master in cut_kept_masters_by_cut.get(
                            _cut_name,
                            (),
                        )
                    ],
                    "analytic master": analytic_master_values_by_cut[
                        _cut_name
                    ],
                    "master coefficient": normalize_rational(
                        _expression
                        / analytic_master_values_by_cut[_cut_name]
                    ),
                    "analytic cut expression": _expression,
                }
                for _cut_name, _expression in analytic_expressions_by_cut.items()
            ],
            pagination=False,
            selection=None,
        )
    else:
        _analytic_status = mo.callout(
            "The maximal-cut 00 master is available without Kira. Run all "
            "four projects of a reducible cut to add that cut.",
            kind="neutral",
        )
    _analytic_status
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Take leading virtuality power and integrate \(p_i^2\)

    The singular master is isolated before any external virtuality is set to
    zero.  Only its rational IBP coefficient is expanded at leading power.
    With the one-sided boundary delta normalized by

    \[
      \int_0^{\Lambda^2}\frac{dv}{2\pi}\,
      \widehat\delta_\partial(v)=1,
    \]

    the continuous factor is

    \[
      J(\Lambda^2)=
      \int_0^{\Lambda^2}\frac{dv}{2\pi}v^{-1-\epsilon}
      =-\frac{(\Lambda^2)^{-\epsilon}}{2\pi\epsilon}.
    \]

    This identity first converges for \({\rm Re}\,\epsilon<0\) and is then
    analytically continued.  The direct `00` cut receives \(J^2\); `10` and
    `01` receive one \(J\); `11` receives none.  All four are finally multiplied
    by the common \(s\) Jacobian because this notebook reports \(d/dz\), not
    \(d/dm^2\).

    The mass parameter enters the graph as \(q^2\).  Since normalized IBP
    coefficients can contain canonical \(q^4\), the transparent LP map first
    verifies evenness in \(q\) and then replaces \(q\to\sqrt{zs}\); an exact
    subexpression replacement of only \(q^2\) would miss those higher powers.
    """)
    return


@app.cell
def _(
    E,
    N,
    analytic_expressions_by_cut,
    analytic_master_values_by_cut,
    apply_endpoint_expansion,
    apply_kinematic_rules,
    cutoff_squared,
    dimension,
    dot,
    dy_weight,
    endpoint_distribution_expansion,
    epsilon,
    euler_gamma,
    massive_cut_bubble,
    massive_cut_triangle,
    maximal_cross_box_cut_master,
    maximal_cut_numerator,
    mu_squared,
    normalize_rational,
    p1,
    p2,
    q,
    s,
    virtuality_integral_factor,
    z,
):
    dimensionally_regularized = N(4) - 2 * epsilon
    virtuality_factor = virtuality_integral_factor(
        cutoff_squared,
        epsilon,
    )
    _lp_rules = (
        (q, (z * s).sqrt()),
        (dot(p1, p2), s / 2),
        (dot(p1, p1), E("0")),
        (dot(p2, p2), E("0")),
        (dimension, dimensionally_regularized),
    )

    leading_master_values_by_cut = {
        "11": massive_cut_bubble(
            s,
            z * s,
            dimension=dimensionally_regularized,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        ),
        "10": massive_cut_triangle(
            N(1),
            s,
            z * s,
            dimension=dimensionally_regularized,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        ),
        "01": massive_cut_triangle(
            N(1),
            s,
            z * s,
            dimension=dimensionally_regularized,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        ),
        "00": maximal_cross_box_cut_master(
            s,
            dimension=dimensionally_regularized,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        ),
    }
    ibp_coefficients_by_cut = {}
    q_even_residuals_by_cut = {}
    master_coefficients_by_cut = {}
    for _cut_name, _expression in analytic_expressions_by_cut.items():
        if _cut_name == "00":
            continue
        _ratio = normalize_rational(
            _expression / analytic_master_values_by_cut[_cut_name]
        )
        _q_even_residual = normalize_rational(
            _ratio.replace(q, -q) - _ratio
        )
        q_even_residuals_by_cut[_cut_name] = _q_even_residual
        if _q_even_residual != E("0"):
            raise ValueError(
                f"Cut {_cut_name} is not even in the mass parameter q; "
                "the q -> sqrt(z s) leading-power map is unsafe"
            )
        ibp_coefficients_by_cut[_cut_name] = apply_kinematic_rules(
            _ratio,
            _lp_rules,
        )
        master_coefficients_by_cut[_cut_name] = ibp_coefficients_by_cut[
            _cut_name
        ]

    master_coefficients_by_cut["00"] = apply_kinematic_rules(
        maximal_cut_numerator,
        ((dimension, dimensionally_regularized),),
    )
    leading_cut_values_by_cut = {
        _cut_name: normalize_rational(
            master_coefficients_by_cut[_cut_name]
            * leading_master_values_by_cut[_cut_name]
        )
        for _cut_name in master_coefficients_by_cut
    }
    _virtuality_power_count_by_cut = {
        "11": 0,
        "10": 1,
        "01": 1,
        "00": 2,
    }
    virtuality_integrated_by_cut = {
        _cut_name: normalize_rational(
            _expression
            * virtuality_factor ** _virtuality_power_count_by_cut[_cut_name]
        )
        for _cut_name, _expression in leading_cut_values_by_cut.items()
    }
    maximal_cut_delta_coefficient = virtuality_integrated_by_cut["00"]

    endpoint_multiple_by_cut = {"11": 2, "10": 1, "01": 1}
    endpoint_regular_prefactors_by_cut = {
        _cut_name: normalize_rational(
            _expression
            * (1 - z) ** (
                1 + endpoint_multiple_by_cut[_cut_name] * epsilon
            )
        )
        for _cut_name in endpoint_multiple_by_cut
        if _cut_name in virtuality_integrated_by_cut
        for _expression in [virtuality_integrated_by_cut[_cut_name]]
    }
    weighted_endpoint_prefactors_by_cut = {
        _cut_name: normalize_rational(dy_weight * _prefactor)
        for _cut_name, _prefactor in endpoint_regular_prefactors_by_cut.items()
    }
    endpoint_expansions_by_cut = {
        _cut_name: endpoint_distribution_expansion(
            endpoint_multiple_by_cut[_cut_name],
            epsilon,
            order=2,
        )
        for _cut_name in weighted_endpoint_prefactors_by_cut
    }
    endpoint_distributions_by_cut = {
        _cut_name: apply_endpoint_expansion(
            endpoint_expansions_by_cut[_cut_name],
            _prefactor,
            z,
        )
        for _cut_name, _prefactor in weighted_endpoint_prefactors_by_cut.items()
    }
    weighted_maximal_cut_delta_coefficient = normalize_rational(
        dy_weight * maximal_cut_delta_coefficient
    )

    _distribution_count = len(endpoint_distributions_by_cut)
    if _distribution_count:
        _plus_order = max(
            _distribution.order
            for _distribution in endpoint_distributions_by_cut.values()
        )
        summed_plus_coefficients = tuple(
            normalize_rational(
                sum(
                    (
                        _distribution.plus_coefficients[_order]
                        for _distribution in endpoint_distributions_by_cut.values()
                    ),
                    E("0"),
                )
            )
            for _order in range(_plus_order + 1)
        )
        summed_regular_part = normalize_rational(
            sum(
                (
                    _distribution.regular_part
                    for _distribution in endpoint_distributions_by_cut.values()
                ),
                E("0"),
            )
        )
        summed_delta_coefficient = normalize_rational(
            weighted_maximal_cut_delta_coefficient
            + sum(
                (
                    _distribution.delta_coefficient
                    for _distribution in endpoint_distributions_by_cut.values()
                ),
                E("0"),
            )
        )
    else:
        summed_plus_coefficients = ()
        summed_regular_part = E("0")
        summed_delta_coefficient = weighted_maximal_cut_delta_coefficient
    return (
        dimensionally_regularized,
        maximal_cut_delta_coefficient,
        endpoint_distributions_by_cut,
        endpoint_expansions_by_cut,
        endpoint_multiple_by_cut,
        endpoint_regular_prefactors_by_cut,
        ibp_coefficients_by_cut,
        leading_cut_values_by_cut,
        leading_master_values_by_cut,
        master_coefficients_by_cut,
        q_even_residuals_by_cut,
        summed_delta_coefficient,
        summed_plus_coefficients,
        summed_regular_part,
        virtuality_factor,
        virtuality_integrated_by_cut,
        weighted_maximal_cut_delta_coefficient,
        weighted_endpoint_prefactors_by_cut,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Expand the endpoint kernels without inventing distribution atoms

    For a cut with endpoint exponent \(a\),

    \[
      (1-z)^{-1-a\epsilon}
      =-\frac{\delta(1-z)}{a\epsilon}
       +\sum_{n\ge0}\frac{(-a\epsilon)^n}{n!}\,\mathcal D_n(z),
      \qquad
      \mathcal D_n(z)=
      \left[\frac{\log^n(1-z)}{1-z}\right]_+.
    \]

    Cut `11` uses \(a=2\), while `10` and `01` use \(a=1\).  Cut `00`
    is already proportional to \(\delta(1-z)\).

    `EndpointDistribution` stores only the coefficients of this basis and the
    ordinary locally-integrable remainder.  For a smooth prefactor \(g(z)\),
    the code uses

    \[
      g(z)\mathcal D_n(z)=g(1)\mathcal D_n(z)
      +\frac{g(z)-g(1)}{1-z}\log^n(1-z).
    \]

    No fake Symbolica `delta` or `plus` function is introduced.  The expansion
    is retained through \(\mathcal O(\epsilon^2)\), which is necessary because
    virtuality and endpoint integrations can jointly generate double poles.
    """)
    return


@app.cell(hide_code=True)
def _(
    endpoint_distributions_by_cut,
    endpoint_multiple_by_cut,
    endpoint_regular_prefactors_by_cut,
    leading_master_values_by_cut,
    master_coefficients_by_cut,
    maximal_cut_delta_coefficient,
    mo,
    reducible_cut_names,
    spenso_table,
    summed_delta_coefficient,
    summed_plus_coefficients,
    summed_regular_part,
    virtuality_factor,
    weighted_maximal_cut_delta_coefficient,
):
    _support_rows = [
        {
            "cut": "11",
            "virtuality support": "δ̂∂(p₁²) δ̂∂(p₂²)",
            "virtuality integral": 1,
            "endpoint": "(1-z)^(-1-2ε)",
        },
        {
            "cut": "10",
            "virtuality support": "δ̂∂(p₁²) (p₂²)^(-1-ε)",
            "virtuality integral": virtuality_factor,
            "endpoint": "(1-z)^(-1-ε)",
        },
        {
            "cut": "01",
            "virtuality support": "(p₁²)^(-1-ε) δ̂∂(p₂²)",
            "virtuality integral": virtuality_factor,
            "endpoint": "(1-z)^(-1-ε)",
        },
        {
            "cut": "00",
            "virtuality support": "(p₁² p₂²)^(-1-ε)",
            "virtuality integral": virtuality_factor**2,
            "endpoint": "δ(1-z)",
        },
    ]
    _distribution_rows = [
        {
            "cut": _cut_name,
            "master coefficient": master_coefficients_by_cut[_cut_name],
            "analytic master": leading_master_values_by_cut[_cut_name],
            "a": endpoint_multiple_by_cut[_cut_name],
            "smooth prefactor g(z,ε) before DY weight": (
                endpoint_regular_prefactors_by_cut[_cut_name]
            ),
            "weighted δ coefficient": _distribution.delta_coefficient,
            "weighted D₀,D₁,D₂ coefficients": list(
                _distribution.plus_coefficients
            ),
            "weighted ordinary remainder": _distribution.regular_part,
        }
        for _cut_name, _distribution in endpoint_distributions_by_cut.items()
    ]
    _distribution_rows.append(
        {
            "cut": "00",
            "master coefficient": master_coefficients_by_cut["00"],
            "analytic master": leading_master_values_by_cut["00"],
            "a": "maximal-cut master",
            "smooth prefactor g(z,ε) before DY weight": maximal_cut_delta_coefficient,
            "weighted δ coefficient": weighted_maximal_cut_delta_coefficient,
            "weighted D₀,D₁,D₂ coefficients": [],
            "weighted ordinary remainder": 0,
        }
    )
    _all_reducible_complete = set(endpoint_distributions_by_cut) == set(
        reducible_cut_names
    )
    _sum_status = (
        mo.vstack(
            [
                mo.callout(
                    "All four crossed-box cuts are present in the aligned "
                    "delta/plus basis. This is still one diagram, not the "
                    "complete DY coefficient function.",
                    kind="success",
                ),
                spenso_table(
                    [
                        {
                            "basis element": "δ(1-z)",
                            "summed crossed-box coefficient": summed_delta_coefficient,
                        },
                        *[
                            {
                                "basis element": f"D{_order}(z)",
                                "summed crossed-box coefficient": _coefficient,
                            }
                            for _order, _coefficient in enumerate(
                                summed_plus_coefficients
                            )
                        ],
                        {
                            "basis element": "ordinary remainder",
                            "summed crossed-box coefficient": summed_regular_part,
                        },
                    ],
                    pagination=False,
                    selection=None,
                ),
            ]
        )
        if _all_reducible_complete
        else mo.callout(
            "The analytic 00 maximal-cut master is available. Run all projects "
            "for cuts 11, 10, and 01 to assemble the complete crossed-box "
            "distribution.",
            kind="neutral",
        )
    )
    mo.vstack(
        [
            mo.md("### Leading virtuality support"),
            spenso_table(_support_rows, pagination=False, selection=None),
            mo.md("### Per-cut endpoint data"),
            spenso_table(
                _distribution_rows,
                pagination=False,
                selection=None,
            ),
            mo.md("### Crossed-box sum"),
            _sum_status,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Validation

    All checks are collected here.  The independent trace polynomial tests the
    Idenso contraction, `validate_pre_ibp` reconstructs every algebraic handoff,
    the maximal-cut support and unit-numerator master test the boundary branch,
    and—when Kira has run—the known leading-power IBP coefficients test all
    three reducible cuts.

    Historical FIRE/Mathematica family names are intentionally absent from the
    derivation.  Their adapters belong here when the remaining physical oracle
    formulas are ported.
    """)
    return


@app.cell
def _(
    E,
    N,
    dimension,
    direct_cut_names,
    dot,
    endpoint_regular_prefactors_by_cut,
    epsilon,
    ibp_coefficients_by_cut,
    k1,
    leading_master_values_by_cut,
    loop_propagator_indices,
    master_coefficients_by_cut,
    maximal_cut_numerator,
    normalize_rational,
    p1,
    p2,
    physical_numerator,
    physical_pre_ibp,
    projected_cutsets,
    propagators,
    q_even_residuals_by_cut,
    reducible_cut_names,
    s,
    square,
    topology_kira_reductions,
    topology_projects,
    validate_pre_ibp,
    virtuality_factor,
    virtuality_integrated_by_cut,
    z,
):
    _p1_squared = square(p1)
    _p2_squared = square(p2)
    _k_squared = square(k1)
    _k_dot_p1 = dot(k1, p1)
    _k_dot_p2 = dot(k1, p2)
    _p1_dot_p2 = dot(p1, p2)
    _expected_trace = 4 * (dimension - 2) * (
        (dimension - 8) * _k_squared * _p1_dot_p2
        + 4 * _p1_dot_p2 * (_k_dot_p1 + _k_dot_p2)
        + (8 - 2 * dimension) * _k_dot_p1 * _k_dot_p2
        + (dimension - 4)
        * (_k_dot_p1 * _p2_squared + _k_dot_p2 * _p1_squared)
        + (4 - dimension) * _p1_squared * _p2_squared
        - 4 * _p1_dot_p2**2
    )
    physical_validation = dict(validate_pre_ibp(physical_pre_ibp))
    physical_validation["metric-contracted trace"] = normalize_rational(
        physical_numerator - _expected_trace
    )
    physical_validation["maximal-cut numerator"] = normalize_rational(
        maximal_cut_numerator + 4 * (dimension - 2) * s**2
    )
    physical_validation["maximal-cut master factorization"] = normalize_rational(
        virtuality_integrated_by_cut["00"]
        - master_coefficients_by_cut["00"]
        * leading_master_values_by_cut["00"]
        * virtuality_factor**2
    )
    physical_validation["all loop lines inferred"] = N(
        int(loop_propagator_indices != [2, 3, 4, 5])
    )
    physical_validation["cut partition"] = N(
        int(
            reducible_cut_names != ["11", "10", "01"]
            or direct_cut_names != ["00"]
        )
    )
    physical_validation["project coverage"] = N(
        int(
            any(
                (_cut_name, _contribution.source_indices)
                not in topology_projects
                for _cut_name in reducible_cut_names
                for _contribution in physical_pre_ibp.contributions
            )
        )
    )
    physical_validation["target cube coverage"] = N(
        int(
            any(
                _index not in (-1, 0, 1)
                for _contribution in physical_pre_ibp.contributions
                for _index in _contribution.integral_indices
            )
        )
    )
    physical_validation["single native dimension"] = N(
        int(any(_project.dimension != dimension for _project in topology_projects.values()))
    )

    _expected_coefficients = {
        "11": (
            8
            * (1 - epsilon)
            * (
                epsilon**2 * (1 - z) ** 2
                + 2 * z * (1 - 2 * epsilon)
            )
            / (epsilon * (1 - z) ** 2)
        ),
        "10": 8 * s * z * (1 - epsilon) / (1 - z),
        "01": 8 * s * z * (1 - epsilon) / (1 - z),
    }
    for _cut_name, _coefficient in ibp_coefficients_by_cut.items():
        physical_validation[
            f"cut {_cut_name} even mass dependence"
        ] = q_even_residuals_by_cut[_cut_name]
        physical_validation[
            f"cut {_cut_name} leading IBP coefficient"
        ] = normalize_rational(
            _coefficient - _expected_coefficients[_cut_name]
        )
        _a = 2 if _cut_name == "11" else 1
        physical_validation[
            f"cut {_cut_name} endpoint factorization"
        ] = normalize_rational(
            virtuality_integrated_by_cut[_cut_name]
            - endpoint_regular_prefactors_by_cut[_cut_name]
            * (1 - z) ** (-1 - _a * epsilon)
        )

    if topology_kira_reductions:
        _native_fragments = []
        for _result in topology_kira_reductions.values():
            _native_fragments.append(_result.family_name)
            _native_fragments.extend(
                _target.to_canonical_string()
                for _target in _result.requested_targets
            )
            _native_fragments.extend(
                _master.to_canonical_string()
                for _master in _result.masters
            )
            _native_fragments.extend(
                _expression.to_canonical_string()
                for _rule in _result.rules.items()
                for _expression in _rule
            )
        _native_text = "\n".join(_native_fragments)
        physical_validation["native Kira restoration"] = N(
            int(
                any(
                    _wire_name in _native_text
                    for _wire_name in (
                        "kp_",
                        "ipp1p1",
                        "ipp1p2",
                        "ipp2p2",
                    )
                )
            )
        )

    _failures = {
        _name: _residual
        for _name, _residual in physical_validation.items()
        if _residual != E("0")
    }
    if _failures:
        raise ValueError(
            "Physical crossed-box validation failed: "
            + ", ".join(
                f"{_name}: {_residual}"
                for _name, _residual in _failures.items()
            )
        )
    return (physical_validation,)


@app.cell(hide_code=True)
def _(mo, physical_validation, spenso_table):
    mo.vstack(
        [
            mo.callout(
                "The physical trace, all pre-IBP handoffs, maximal-cut "
                "master, source routing, target cube, and every available "
                "Kira/LP result pass exact validation.",
                kind="success",
            ),
            spenso_table(
                [
                    {"check": _name, "residual": _residual}
                    for _name, _residual in physical_validation.items()
                ],
                pagination=True,
                page_size=20,
                selection=None,
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
