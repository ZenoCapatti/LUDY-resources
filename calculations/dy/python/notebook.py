import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup(hide_code=True):
    from pathlib import Path as _Path
    import sys as _sys

    import marimo as _marimo

    _repository_root = _Path(__file__).resolve().parents[3]
    for _path in (
        str(_repository_root),
        str(_repository_root / "notebooks"),
    ):
        if _path not in _sys.path:
            _sys.path.insert(0, _path)

    from notebooks.typst_marimo import typst_md as _typst_md

    # Typst source cells retain Marimo's prose styling while remaining fully
    # editable as source, just like native Markdown cells.
    _marimo.md = _typst_md


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    from symbolica import E, S, Expression
    from symbolica.community.spenso import Representation, TensorName, dot
    from calculations.dy.python.masters import (
        apply_endpoint_expansion,
        endpoint_distribution_expansion,
        scalar_printer,
        typst_md,
    )

    # Keep the patch in an ordinary dependency cell as well as app.setup.
    # Marimo's static exporter evaluates this cell before the prose cells.
    mo.md = typst_md

    from kirapy import Kira, KiraError
    from notebooks.ludy import (
        gamma_trace_to_dots,
        momentum_printer,
        normalize_rational,
        replace_all,
        run_kira_projects,
        spenso_table as expression_table,
    )
    from calculations.dy.python.physical import (
        CutMembership,
        DYContext,
        DYGraphSpec,
        EndpointCoefficient,
        assemble_closed_form_dy,
        assemble_native_dy_scheme,
        assemble_reference_dy_handoff,
        build_dy_kira_projects,
        build_paper_dy_physical_handoff,
        crossed_box_reductions,
        native_dy_one_leg_scheme_kernel,
        numerator_reductions,
    )
    from calculations.dy.python.factorization import (
        build_aem_dis_1979_factorization_records,
        build_msbar_factorization_records,
    )

    return (
        CutMembership,
        DYContext,
        DYGraphSpec,
        E,
        EndpointCoefficient,
        Expression,
        Kira,
        KiraError,
        Path,
        Representation,
        S,
        TensorName,
        apply_endpoint_expansion,
        assemble_closed_form_dy,
        assemble_native_dy_scheme,
        assemble_reference_dy_handoff,
        build_dy_kira_projects,
        build_paper_dy_physical_handoff,
        build_aem_dis_1979_factorization_records,
        build_msbar_factorization_records,
        crossed_box_reductions,
        dot,
        endpoint_distribution_expansion,
        expression_table,
        gamma_trace_to_dots,
        mo,
        momentum_printer,
        native_dy_one_leg_scheme_kernel,
        normalize_rational,
        numerator_reductions,
        replace_all,
        run_kira_projects,
        scalar_printer,
        typst_md,
    )


@app.cell(hide_code=True)
def _(typst_md):
    typst_md(r"""
    = NLO Drell--Yan coefficient from physical cuts

    The Drell--Yan calculation follows the same mathematical sequence as the
    cross-box and DIS examples. Each contribution begins with its momentum
    routing, masses, propagator powers, and cut support. Transverse and
    longitudinal Dirac projections give scalar numerators. Denominator
    decomposition and integration-by-parts identities reduce every cut
    integral to analytic masters. Their leading behavior in the incoming
    virtualities is integrated to the physical cutoffs, and the resulting
    Laurent series is organized in the endpoint basis. Summing the physical
    cut sectors yields the $q bar(q)$ and $q g$ coefficients.

    One native contribution ledger is selected twice.  The ordinary on-shell
    cuts form $C^(upright("PM"),upright("bare"))$; adding the complementary
    incoming-virtuality cuts forms $C^(upright("MP"))$.  Their componentwise
    difference is the regularised transition coefficient in a Born-normalized
    convolution convention.  The independently assembled AEM parton-model
    branch then fixes the positive phase-space normalization of the common
    cuts and combines with the native transition to give the finite physical
    coefficient.  The pre-correction LaTeX snapshot and Mathematica formulae
    enter later as downstream historical comparisons.

    The companion DIS calculation then tests the same one-leg collinear
    transition in a distinct process.
    """)
    return


@app.cell
def _(
    DYContext,
    Expression,
    Representation,
    S,
    TensorName,
    dot,
    momentum_printer,
    scalar_printer,
):
    # This is the complete editable symbol input for the DY calculation.
    # Symbol attributes and custom printers are registered once per Symbolica
    # process; restart the Marimo kernel before deliberately rerunning this cell.
    d = S("d")
    epsilon = S(
        "DY_epsilon",
        print=scalar_printer(latex=r"\epsilon", typst="epsilon"),
    )
    _minkowski = Representation.mink(dimension=d)
    _external_momentum = TensorName.vector(
        "p",
        print=momentum_printer("p"),
    )
    _loop_momentum = TensorName.vector(
        "k",
        tags=["ludy::loop_momentum"],
        print=momentum_printer("k"),
    )
    p1 = _external_momentum(1, _minkowski)
    p2 = _external_momentum(2, _minkowski)
    k = _loop_momentum(1, _minkowski)

    kk, kp1, kp2 = dot(k, k), dot(k, p1), dot(k, p2)
    p1_squared, p2_squared, p1_dot_p2 = (
        dot(p1, p1),
        dot(p2, p2),
        dot(p1, p2),
    )
    loop_scalar_products = (kk, kp1, kp2)

    s, z = S("s", "z")
    mass_squared = S(
        "msq",
        print=scalar_printer(latex=r"m^2", typst="m^2"),
    )
    alpha_s = S(
        "DY_alpha_s",
        print=scalar_printer(latex=r"\alpha_s", typst="alpha_s"),
    )
    color_f = S(
        "DY_C_F",
        print=scalar_printer(latex=r"C_F", typst="C_F"),
    )
    color_t = S(
        "DY_T_F",
        print=scalar_printer(latex=r"T_F", typst="T_F"),
    )
    electric_charge = S(
        "DY_e_q",
        print=scalar_printer(latex=r"e_q", typst="e_q"),
    )
    strong_coupling = S(
        "DY_g_s",
        print=scalar_printer(latex=r"g_s", typst="g_s"),
    )
    color_count = S(
        "DY_N_c",
        print=scalar_printer(latex=r"N_c", typst="N_c"),
    )
    lambda1_squared = S(
        "Lambda1sq",
        print=scalar_printer(
            latex=r"\Lambda_1^2",
            typst="Lambda_1^2",
        ),
    )
    lambda2_squared = S(
        "Lambda2sq",
        print=scalar_printer(
            latex=r"\Lambda_2^2",
            typst="Lambda_2^2",
        ),
    )
    mu_r_squared = S(
        "mu_R_sq",
        print=scalar_printer(latex=r"\mu_R^2", typst="mu_R^2"),
    )
    endpoint_delta = S(
        "DY_delta_one_minus_z",
        print=scalar_printer(
            latex=r"\delta(1-z)",
            typst="delta(1-z)",
        ),
    )
    endpoint_d0 = S(
        "DY_D0_z",
        print=scalar_printer(
            latex=r"\left[\frac{1}{1-z}\right]_{+}",
            typst="lr([frac(1, 1-z)])_+",
        ),
    )
    endpoint_d1 = S(
        "DY_D1_z",
        print=scalar_printer(
            latex=r"\left[\frac{\log(1-z)}{1-z}\right]_{+}",
            typst="lr([frac(log(1-z), 1-z)])_+",
        ),
    )
    pi = Expression.PI

    dy_context = DYContext(
        d=d,
        epsilon=epsilon,
        p1=p1,
        p2=p2,
        k=k,
        kk=kk,
        kp1=kp1,
        kp2=kp2,
        p1_squared=p1_squared,
        p2_squared=p2_squared,
        p1_dot_p2=p1_dot_p2,
        loop_scalar_products=loop_scalar_products,
        s=s,
        z=z,
        mass_squared=mass_squared,
        alpha_s=alpha_s,
        color_f=color_f,
        color_t=color_t,
        electric_charge=electric_charge,
        strong_coupling=strong_coupling,
        color_count=color_count,
        lambda1_squared=lambda1_squared,
        lambda2_squared=lambda2_squared,
        mu_r_squared=mu_r_squared,
        pi=pi,
    )
    return (
        d,
        dy_context,
        endpoint_d0,
        endpoint_d1,
        endpoint_delta,
        k,
        kk,
        kp1,
        kp2,
        mass_squared,
        p1,
        p1_dot_p2,
        p1_squared,
        p2,
        p2_squared,
    )


@app.cell
def _(
    CutMembership,
    DYGraphSpec,
    E,
    k,
    mass_squared,
    p1,
    p1_dot_p2,
    p1_squared,
    p2,
    p2_squared,
):
    # These ordered (momentum, mass-squared) lines, full cut masks, analytic-
    # master weights, observable phases, and unsigned MP/PM memberships are
    # the editable physical graph input. Cut weights are relative to masters.py;
    # the observable phase is independent of both that convention and scheme
    # membership. No Kira object or historical family label enters a graph.
    zero = E("0")
    external = ((p1, zero), (p2, zero))
    virtual_direct = external + (
        (k, zero),
        (k - p1, zero),
        (k + p2, zero),
    )
    virtual_crossed = external + (
        (k, zero),
        (k - p1, zero),
        (p2 - k, zero),
    )
    direct_box = external + (
        (k, zero),
        (k - p1, zero),
        (p1 + p2 - k, mass_squared),
    )
    qg = external + (
        (k, zero),
        (k + p1, zero),
        (k + p1 + p2, mass_squared),
    )
    crossed_box = external + (
        (k, zero),
        (k - p1, zero),
        (p2 - k, zero),
        (p1 + p2 - k, mass_squared),
    )

    virtual_direct_cuts = {
        "11": (1, 1, 0, 1, 1),
        "10": (1, 0, 1, 0, 1),
        "01": (0, 1, 1, 1, 0),
    }
    virtual_crossed_cuts = {"00": (0, 0, 1, 1, 1)}
    bubble_cuts = {"10": virtual_direct_cuts["10"]}
    direct_cuts = {
        "11": (1, 1, 1, 0, 1),
        "01": (0, 1, 1, 1, 1),
    }
    crossed_cuts = {
        "11": (1, 1, 1, 0, 0, 1),
        "10": (1, 0, 1, 0, 1, 1),
        "01": (0, 1, 1, 1, 0, 1),
        "00": (0, 0, 1, 1, 1, 1),
    }
    qg_external = p1_squared + 2 * p1_dot_p2 + p2_squared

    def memberships(cut_names, *, mp_only=()):
        return {
            cut_name: CutMembership(
                pm_bare=cut_name not in mp_only,
                mp=True,
            )
            for cut_name in cut_names
        }

    dy_graphs = {
        "virtual triangle 1": DYGraphSpec(
            name="virtual triangle 1",
            propagators=virtual_direct,
            cutsets=dict(virtual_direct_cuts),
            propagator_powers=(1, 1, 1),
            numerator_divisor=E("1"),
            cut_weights={"11": E("1"), "10": E("-1"), "01": E("-1")},
            scheme_observable_phase=E("1"),
            cut_memberships=memberships(
                virtual_direct_cuts,
                mp_only=("10", "01"),
            ),
        ),
        "virtual triangle 2": DYGraphSpec(
            name="virtual triangle 2",
            propagators=virtual_crossed,
            cutsets=dict(virtual_crossed_cuts),
            propagator_powers=(1, 1, 1),
            numerator_divisor=E("1"),
            cut_weights={"00": E("1")},
            scheme_observable_phase=E("1"),
            cut_memberships=memberships(
                virtual_crossed_cuts,
                mp_only=("00",),
            ),
        ),
        "virtual bubble": DYGraphSpec(
            name="virtual bubble",
            propagators=virtual_direct,
            cutsets=dict(bubble_cuts),
            propagator_powers=(1, 0, 1),
            numerator_divisor=E("1"),
            cut_weights={"10": E("-1")},
            scheme_observable_phase=E("1"),
            cut_memberships=memberships(bubble_cuts, mp_only=("10",)),
        ),
        "qq direct box": DYGraphSpec(
            name="qq direct box",
            propagators=direct_box,
            cutsets=dict(direct_cuts),
            propagator_powers=(1, 2, 1),
            numerator_divisor=E("1"),
            cut_weights={"11": E("1"), "01": E("-1")},
            scheme_observable_phase=E("-1"),
            cut_memberships=memberships(direct_cuts, mp_only=("01",)),
        ),
        "qq crossed box": DYGraphSpec(
            name="qq crossed box",
            propagators=crossed_box,
            cutsets=dict(crossed_cuts),
            propagator_powers=(1, 1, 1, 1),
            numerator_divisor=E("1"),
            cut_weights={
                "11": E("-1"),
                "10": E("1"),
                "01": E("1"),
                "00": E("1"),
            },
            scheme_observable_phase=E("-1"),
            cut_memberships=memberships(
                crossed_cuts,
                mp_only=("10", "01", "00"),
            ),
            analytic_cuts=("00",),
        ),
        "qg box": DYGraphSpec(
            name="qg box",
            propagators=qg,
            cutsets=dict(direct_cuts),
            propagator_powers=(1, 2, 1),
            numerator_divisor=E("1"),
            cut_weights={"11": E("-1"), "01": E("1")},
            scheme_observable_phase=E("-1"),
            cut_memberships=memberships(direct_cuts, mp_only=("01",)),
        ),
        "qg triangle": DYGraphSpec(
            name="qg triangle",
            propagators=qg,
            cutsets=dict(direct_cuts),
            propagator_powers=(1, 1, 1),
            numerator_divisor=qg_external,
            cut_weights={"11": E("2"), "01": E("-2")},
            scheme_observable_phase=E("-1"),
            cut_memberships=memberships(direct_cuts, mp_only=("01",)),
        ),
        "qg bubble": DYGraphSpec(
            name="qg bubble",
            propagators=qg,
            cutsets=dict(direct_cuts),
            propagator_powers=(1, 0, 1),
            numerator_divisor=qg_external**2,
            cut_weights={"11": E("-1"), "01": E("0")},
            scheme_observable_phase=E("-1"),
            cut_memberships=memberships(direct_cuts, mp_only=("01",)),
        ),
    }
    return (dy_graphs,)


@app.cell
def _(d, gamma_trace_to_dots, k, p1, p2):
    # These raw chains are the editable physical numerator input. ``None`` is
    # an unslashed gamma matrix; repeated labels contract its Lorentz index.
    # The direct/crossed qq box routings already include the source-to-graph
    # loop reversal k_source = -k. Couplings and color factors remain separate
    # process weights.
    dy_trace_specs = {
        "virtual triangle 1": {
            "vectors": (None, p1 - k, None, p1, None, p2, None, k + p2),
            "lorentz labels": (
                "photon",
                "slash1",
                "gluon",
                "slash2",
                "photon",
                "slash3",
                "gluon",
                "slash4",
            ),
            "source": "DY_calculation.nb:4562",
        },
        "virtual triangle 2": {
            "vectors": (None, p1 - k, None, p1, None, p2 - k, None, p2),
            "lorentz labels": (
                "photon",
                "slash1",
                "gluon",
                "slash2",
                "photon",
                "slash3",
                "gluon",
                "slash4",
            ),
            "source": "DY_calculation.nb:5997",
        },
        "virtual bubble": {
            "vectors": (None, p2, None, k, p2, None, None, p1),
            "lorentz labels": (
                "photon",
                "slash1",
                "gluon",
                "slash2",
                "slash3",
                "photon",
                "gluon",
                "slash4",
            ),
            "source": "DY_calculation.nb:13923",
        },
        "qq direct box": {
            "vectors": (None, p1 - k, None, p1, None, p1 - k, None, p2),
            "lorentz labels": (
                "photon",
                "slash1",
                "gluon",
                "slash2",
                "gluon",
                "slash3",
                "photon",
                "slash4",
            ),
            "source": "DY_calculation.nb:16127; k_source = -k",
        },
        "qq crossed box": {
            "vectors": (None, p1 - k, None, p1, None, p2 - k, None, p2),
            "lorentz labels": (
                "photon",
                "slash1",
                "gluon",
                "slash2",
                "photon",
                "slash3",
                "gluon",
                "slash4",
            ),
            "source": "DY_calculation.nb:20868; k_source = -k",
        },
        "qg box": {
            "vectors": (None, k + p1, None, k, None, k + p1, None, p2),
            "lorentz labels": (
                "photon",
                "slash1",
                "gluon",
                "slash2",
                "gluon",
                "slash3",
                "photon",
                "slash4",
            ),
            "source": "DY_calculation.nb:32483",
        },
        "qg triangle": {
            "vectors": (None, k + p1, None, k, None, p1 + p2, None, p2),
            "lorentz labels": (
                "photon",
                "slash1",
                "gluon",
                "slash2",
                "photon",
                "slash3",
                "gluon",
                "slash4",
            ),
            "source": "DY_calculation.nb:34172",
        },
        "qg bubble": {
            "vectors": (None, p1 + p2, None, p2, None, p1 + p2, None, k),
            "lorentz labels": (
                "photon",
                "slash1",
                "gluon",
                "slash2",
                "gluon",
                "slash3",
                "photon",
                "slash4",
            ),
            "source": "DY_calculation.nb:36026",
        },
    }
    dy_numerators = {
        _graph_name: gamma_trace_to_dots(
            _trace_spec["vectors"],
            _trace_spec["lorentz labels"],
            lorentz_dimension=d,
        )
        for _graph_name, _trace_spec in dy_trace_specs.items()
    }
    return dy_numerators, dy_trace_specs


@app.cell
def _(
    d,
    dy_graphs,
    gamma_trace_to_dots,
    k,
    mass_squared,
    normalize_rational,
    p1,
    p1_squared,
    p2,
    p2_squared,
    replace_all,
):
    # The Ward inputs are the longitudinal q_mu q_nu projections of the same
    # qg traces. The minus sign is the longitudinal term of
    # g_(mu nu) - q_mu q_nu / mass_squared.
    _ward_q = k + p1 + p2
    dy_qg_ward_trace_specs = {
        "box": {
            "vectors": (
                _ward_q,
                k + p1,
                None,
                k,
                None,
                k + p1,
                _ward_q,
                p2,
            ),
            "lorentz labels": (
                "q1",
                "slash1",
                "gluon",
                "slash2",
                "gluon",
                "slash3",
                "q2",
                "slash4",
            ),
            "source": "DY_calculation.nb:32483",
        },
        "triangle": {
            "vectors": (
                _ward_q,
                k + p1,
                None,
                k,
                _ward_q,
                p1 + p2,
                None,
                p2,
            ),
            "lorentz labels": (
                "q1",
                "slash1",
                "gluon",
                "slash2",
                "q2",
                "slash3",
                "gluon",
                "slash4",
            ),
            "source": "DY_calculation.nb:34172",
        },
        "bubble": {
            "vectors": (
                _ward_q,
                p1 + p2,
                None,
                p2,
                None,
                p1 + p2,
                _ward_q,
                k,
            ),
            "lorentz labels": (
                "q1",
                "slash1",
                "gluon",
                "slash2",
                "gluon",
                "slash3",
                "q2",
                "slash4",
            ),
            "source": "DY_calculation.nb:36026",
        },
    }
    _ward_raw_traces = {
        _piece_name: gamma_trace_to_dots(
            _trace_spec["vectors"],
            _trace_spec["lorentz labels"],
            lorentz_dimension=d,
        )
        for _piece_name, _trace_spec in dy_qg_ward_trace_specs.items()
    }
    _ward_on_shell_rules = (
        (p1_squared, 0),
        (p2_squared, 0),
    )
    _ward_q_squared = replace_all(
        dy_graphs["qg triangle"].numerator_divisor,
        _ward_on_shell_rules,
    )
    _ward_divisors = {
        "box": mass_squared,
        "triangle": mass_squared * _ward_q_squared,
        "bubble": mass_squared * _ward_q_squared**2,
    }
    dy_qg_ward_numerators = {
        _piece_name: normalize_rational(
            -replace_all(_raw_trace, _ward_on_shell_rules)
            / _ward_divisors[_piece_name]
        )
        for _piece_name, _raw_trace in _ward_raw_traces.items()
    }
    return dy_qg_ward_numerators, dy_qg_ward_trace_specs


@app.cell(hide_code=True)
def _(
    dy_graphs,
    dy_numerators,
    dy_qg_ward_numerators,
    dy_qg_ward_trace_specs,
    dy_trace_specs,
    expression_table,
    mo,
    typst_md,
):
    _trace_rows = [
        {
            "graph": _graph_name,
            "Dirac-chain factors": tuple(
                "free gamma" if _vector is None else _vector
                for _vector in _trace_spec["vectors"]
            ),
            "contracted Lorentz indices": _trace_spec["lorentz labels"],
            "momentum routing": _trace_spec["source"],
            "scalar numerator": dy_numerators[_graph_name],
        }
        for _graph_name, _trace_spec in dy_trace_specs.items()
    ]
    _graph_rows = [
        {
            "graph": graph_name,
            "(momentum, mass²) lines": graph.propagators,
            "denominator lines": graph.loop_propagator_indices,
            "D_i(k)": graph.denominators,
            "cut masks": graph.cutsets,
            "cut weights": graph.cut_weights,
            "observable phase": graph.scheme_observable_phase,
            "PM-bare cuts": tuple(
                cut_name
                for cut_name, membership in graph.resolved_cut_memberships.items()
                if membership.pm_bare
            ),
            "MP cuts": tuple(
                cut_name
                for cut_name, membership in graph.resolved_cut_memberships.items()
                if membership.mp
            ),
            "propagator powers": graph.propagator_powers,
            "dependent-denominator decomposition": graph.requires_apart,
            "closed analytic cuts": graph.analytic_cuts,
        }
        for graph_name, graph in dy_graphs.items()
    ]
    _ward_trace_rows = [
        {
            "piece": _piece_name,
            "Dirac-chain factors": tuple(
                "free gamma" if _vector is None else _vector
                for _vector in _trace_spec["vectors"]
            ),
            "contracted Lorentz indices": _trace_spec["lorentz labels"],
            "momentum routing": _trace_spec["source"],
            "longitudinal numerator": dy_qg_ward_numerators[_piece_name],
        }
        for _piece_name, _trace_spec in dy_qg_ward_trace_specs.items()
    ]
    mo.vstack(
        [
            typst_md(r"""
            == 1. Physical kinematics, topologies, masses, and cuts

            Let $p_1$ and $p_2$ denote the incoming momenta, $k$ the loop
            momentum, $s=2p_1 dot p_2$, and $m^2=z s$. At finite virtuality,
            $(p_1+p_2)^2=s+p_1^2+p_2^2$. For topology $g$, each propagator is

            $ D_(g,i)(k)=q_(g,i)(p_1,p_2,k)^2-m_(g,i)^2. $

            Its propagator powers define the scalar integral family, while each
            cut mask specifies the on-shell support of a physical sector. The
            table fixes these data for the virtual, direct, crossed, and
            Compton topologies.  Its final two cut columns make the nested
            selections explicit: every PM-bare cut belongs to MP, and the
            remaining MP cuts carry the incoming-virtuality expansion.
            """),
            expression_table(_graph_rows, pagination=False),
            typst_md(r"""
            == 2. Dirac traces and projectors

            The transverse projection of each graph gives

            $ N_g^T(k)=P_(mu nu)^T
              upright("tr")(Gamma_g^mu dots.c Gamma_g^nu dots.c). $

            Momentum conservation and the leading-power kinematics reduce the
            traces to polynomials in $k^2$, $k dot p_1$, $k dot p_2$, $s$, and
            $z$. The longitudinal $q g$ projection supplies the corresponding
            Ward components.

            === Transverse projections and scalar numerators
            """),
            expression_table(_trace_rows, pagination=False),
            typst_md(r"""
            === Longitudinal $q g$ projection

            After reduction, the longitudinal coefficients satisfy

            $ 2 C_("triangle")^L-C_("box")^L-C_("circle")^L=0. $
            """),
            expression_table(_ward_trace_rows, pagination=False),
        ]
    )
    return


@app.cell
def _(Path, build_dy_kira_projects, dy_context, dy_graphs):
    dy_project_plan = build_dy_kira_projects(dy_graphs, dy_context)
    dy_kira_projects = dy_project_plan.projects
    physical_project_keys = tuple(dy_kira_projects)
    kira_workdir_root = (
        Path(__file__).resolve().parent / "runs" / "kirapy" / "graph-v3"
    )
    return (
        dy_kira_projects,
        dy_project_plan,
        kira_workdir_root,
        physical_project_keys,
    )


@app.cell(hide_code=True)
def _(dy_project_plan, expression_table, mo, typst_md):
    _project_rows = []
    for _route_key, _project_key in sorted(
        dy_project_plan.route_projects.items()
    ):
        _graph_name, _cut_name, _source_indices = _route_key
        _project = dy_project_plan.projects[_project_key]
        _project_rows.append(
            {
                "graph": _graph_name,
                "cut": _cut_name,
                "denominator lines": tuple(index + 1 for index in _source_indices),
                "denominator family": _project.family.name,
                "common denominator basis": _route_key != _project_key,
            }
        )
    mo.vstack(
        [
            typst_md(r"""
            == 3. Denominator decomposition and numerator reduction

            A graph contributes

            $ cal(I)_g=integral frac(upright(d)^d k, (2 pi)^d)
              frac(N_g(k), product_i D_(g,i)^(a_(g,i))). $

            Rewriting the loop scalar products in terms of the denominators gives

            $ N_g(k)=sum_(bold(nu)) c_(g,bold(nu))
                product_i D_(g,i)^(nu_i), quad
              cal(I)_g=sum_(bold(nu)) c_(g,bold(nu))
                I_g(bold(a)_g-bold(nu)). $

            The linearly dependent crossed-box denominator set decomposes into
            independent three-denominator sectors. The direct $q bar(q)$ and
            $q g$ boxes begin with powers $I(1,2,1)$, and each numerator
            monomial shifts those powers.

            === Cut sectors and denominator bases
            """),
            expression_table(_project_rows, pagination=True, page_size=25),
        ]
    )
    return


@app.cell
def _(
    crossed_box_reductions,
    dy_context,
    dy_graphs,
    dy_numerators,
    numerator_reductions,
):
    dy_numerator_reductions = numerator_reductions(
        dy_graphs,
        dy_numerators,
        dy_context,
    )
    _, crossed_children = crossed_box_reductions(
        dy_graphs,
        dy_numerators,
        dy_context,
    )
    return crossed_children, dy_numerator_reductions


@app.cell(hide_code=True)
def _(
    crossed_children,
    dy_numerator_reductions,
    expression_table,
    mo,
    typst_md,
):
    _reduction_rows = [
        {
            "graph": graph_name,
            "denominator sector": "complete denominator set",
            "initial propagator powers": reduction.base_integral_indices,
            "reduced numerator terms": len(reduction.terms),
        }
        for graph_name, reduction in dy_numerator_reductions.items()
    ] + [
        {
            "graph": "qq crossed box",
            "denominator sector": apart_term.retained_indices,
            "initial propagator powers": reduction.base_integral_indices,
            "reduced numerator terms": len(reduction.terms),
        }
        for apart_term, reduction in crossed_children
    ]
    mo.vstack(
        [
            typst_md("=== Reduced numerator powers"),
            expression_table(_reduction_rows, pagination=False),
        ]
    )
    return


@app.cell
def _(
    E,
    EndpointCoefficient,
    aem_pm_qg_single_pole,
    aem_pm_qq_single_pole,
    dy_context,
    endpoint_d0,
    endpoint_d1,
    endpoint_delta,
    native_dy_one_leg_scheme_kernel,
    native_scheme,
    normalize_rational,
    replace_all,
):
    # Historical DIS/DY formulas are imported only at this downstream boundary.
    # The independent AEM PM poles likewise enter only this comparison cell;
    # none of these expressions can select a cut or a sign in the native build.
    from calculations.dis.python.mathematica_reference import (
        factorization_pole as _reference_factorization_pole,
        lambda1_squared as _reference_lambda1_squared,
        lambda2_squared as _reference_lambda2_squared,
        mathematica_dy_fermion_conversion as _mathematica_dy_fermion_conversion,
        mathematica_dy_fermion_external_leg_virtual as _mathematica_dy_fermion_external_leg_virtual,
        mathematica_dy_fermion_mp_minus_pm as _mathematica_dy_fermion_mp_minus_pm,
        mathematica_dy_gluon_conversion as _mathematica_dy_gluon_conversion,
        mathematica_dy_gluon_mp_minus_pm as _mathematica_dy_gluon_mp_minus_pm,
    )
    from calculations.dis.python.physical import (
        alpha_s as _reference_alpha_s,
        color_count as _reference_color_count,
        color_f as _reference_color_f,
        color_t as _reference_color_t,
        electric_charge as _reference_electric_charge,
        epsilon as _reference_epsilon,
        mu_r_squared as _reference_mu_r_squared,
        strong_coupling as _reference_strong_coupling,
        x as _reference_x,
    )

    _reference_rules = (
        (_reference_x, dy_context.z),
        (_reference_factorization_pole, dy_context.epsilon),
        (_reference_epsilon, dy_context.epsilon),
        (_reference_alpha_s, dy_context.alpha_s),
        (_reference_color_f, dy_context.color_f),
        (_reference_color_t, dy_context.color_t),
        (_reference_color_count, dy_context.color_count),
        (_reference_electric_charge, dy_context.electric_charge),
        (_reference_strong_coupling, dy_context.strong_coupling),
        (_reference_lambda1_squared, dy_context.lambda1_squared),
        (_reference_lambda2_squared, dy_context.lambda2_squared),
        (_reference_mu_r_squared, dy_context.mu_r_squared),
    )
    _positive_log_rules = tuple(
        _rule
        for _cutoff in (
            dy_context.lambda1_squared,
            dy_context.lambda2_squared,
        )
        for _rule in (
            (
                (_cutoff / dy_context.mu_r_squared).log(),
                _cutoff.log() - dy_context.mu_r_squared.log(),
            ),
            (
                (dy_context.mu_r_squared / _cutoff).log(),
                dy_context.mu_r_squared.log() - _cutoff.log(),
            ),
            (
                (dy_context.z * _cutoff / dy_context.mu_r_squared).log(),
                dy_context.z.log()
                + _cutoff.log()
                - dy_context.mu_r_squared.log(),
            ),
            (
                (
                    dy_context.z
                    * _cutoff
                    * (1 - dy_context.z)
                    / dy_context.mu_r_squared
                ).log(),
                dy_context.z.log()
                + _cutoff.log()
                + (1 - dy_context.z).log()
                - dy_context.mu_r_squared.log(),
            ),
        )
    )

    def _reference_scalar(_value):
        _result = replace_all(_value, _reference_rules)
        for _ in range(2):
            _result = replace_all(_result, _positive_log_rules)
            _result = normalize_rational(_result)
        return _result

    def _reference_endpoint(_coefficient):
        _plus = tuple(
            _reference_scalar(_value) for _value in _coefficient.plus
        )
        return EndpointCoefficient(
            delta=_reference_scalar(_coefficient.delta),
            d0_prefactor=_plus[0] if len(_plus) > 0 else E("0"),
            d1_prefactor=_plus[1] if len(_plus) > 1 else E("0"),
            regular=_reference_scalar(_coefficient.regular),
        ).canonical(dy_context.z)

    def _endpoint_expression(_coefficient):
        _canonical = _coefficient.canonical(dy_context.z)
        return (
            _canonical.delta.factor() * endpoint_delta
            + _canonical.d0_prefactor.factor() * endpoint_d0
            + _canonical.d1_prefactor.factor() * endpoint_d1
            + _canonical.regular.factor()
        )

    def _component_row(_label, _coefficient):
        _canonical = _coefficient.canonical(dy_context.z)
        return {
            "DY contribution": _label,
            "delta(1-z)": _canonical.delta.factor(),
            "D0": _canonical.d0_prefactor.factor(),
            "D1": _canonical.d1_prefactor.factor(),
            "ordinary": _canonical.regular.factor(),
        }

    _dis_qg = normalize_rational(
        -_reference_scalar(_mathematica_dy_gluon_conversion())
    )
    _dis_qq = _reference_endpoint(
        _mathematica_dy_fermion_conversion()
    ).scaled(-1)
    _typed_dy_qg = _reference_scalar(_mathematica_dy_gluon_mp_minus_pm())
    _typed_dy_qq = _reference_endpoint(
        _mathematica_dy_fermion_mp_minus_pm()
    )
    _typed_external_bubbles = _reference_endpoint(
        _mathematica_dy_fermion_external_leg_virtual()
    )

    native_scheme_ready = native_scheme is not None
    if native_scheme_ready:
        _native = native_scheme
        _one_leg_1 = native_dy_one_leg_scheme_kernel(
            dy_context.z,
            dy_context.epsilon,
            dy_context.mu_r_squared,
            dy_context.lambda1_squared,
        )
        _one_leg_2 = native_dy_one_leg_scheme_kernel(
            dy_context.z,
            dy_context.epsilon,
            dy_context.mu_r_squared,
            dy_context.lambda2_squared,
        )
        _one_leg_qg_residual = normalize_rational(
            _native.qg_mp_minus_pm
            - dy_context.alpha_s
            * dy_context.color_t
            / (4 * dy_context.pi)
            * (_one_leg_1.qg + _one_leg_2.qg)
        )
        _one_leg_qq_residual = (
            _native.qq_mp_minus_pm
            - (_one_leg_1.qq + _one_leg_2.qq).scaled(
                dy_context.alpha_s
                * dy_context.color_f
                / (2 * dy_context.pi)
            )
        ).canonical(dy_context.z)
        assert _one_leg_qg_residual == E("0"), _one_leg_qg_residual
        assert _one_leg_qq_residual.is_zero_for(
            dy_context.z
        ), _one_leg_qq_residual
        # The historical qg source fixes T_F=1/2; retain T_F in the native
        # object and impose that QCD convention only in these comparison rows.
        _native_qg_qcd = _native.qg_mp_minus_pm.replace(
            dy_context.color_t,
            E("1/2"),
        )
        _qg_dis_raw_residual = normalize_rational(
            _native_qg_qcd - _dis_qg
        )
        _qg_dis_opposite_residual = normalize_rational(
            _native_qg_qcd + _dis_qg
        )
        _qq_dis_residual = (
            _native.qq_historical_z_normalization - _dis_qq
        ).canonical(dy_context.z)
        _qg_dy_raw_residual = normalize_rational(
            _native_qg_qcd - _typed_dy_qg
        )
        _qg_dy_opposite_residual = normalize_rational(
            _native_qg_qcd + _typed_dy_qg
        )
        _qq_dy_reconstructed_residual = (
            _native.qq_historical_z_normalization - _typed_dy_qq
        ).canonical(dy_context.z)
        _bubble_reference_residual = (
            _native.qq_external_bubbles - _typed_external_bubbles
        ).canonical(dy_context.z)

        _qg_pm_pole_residual = normalize_rational(
            _native.qg_single_pole_coefficient
            + aem_pm_qg_single_pole
        )
        _qq_pm_pole_residual = (
            _native.qq_single_pole_coefficient
            + aem_pm_qq_single_pole
        ).canonical(dy_context.z)

        assert _native.qg_double_pole_coefficient == E("0")
        assert _native.qq_double_pole_coefficient.is_zero_for(dy_context.z)
        assert (
            _native.coefficients.mp_minus_pm.qq_total
            - _native.qq_mp_minus_pm
        ).is_zero_for(dy_context.z)
        assert normalize_rational(
            _native.coefficients.mp_minus_pm.qg_beam_exchange_average
            - _native.qg_mp_minus_pm
        ) == E("0")
        assert _qg_pm_pole_residual == E("0")
        assert _qq_pm_pole_residual.is_zero_for(
            dy_context.z
        ), _qq_pm_pole_residual

        native_kernel_rows = [
            {
                "channel": "qg",
                "physical C_MP-C_PM": _native.qg_mp_minus_pm.factor(),
                "epsilon^-2 coefficient": _native.qg_double_pole_coefficient,
                "epsilon^-1 coefficient": (
                    _native.qg_single_pole_coefficient.factor()
                ),
                "one-leg factorization residual": _one_leg_qg_residual,
            },
            {
                "channel": "qqbar",
                "physical C_MP-C_PM": _endpoint_expression(
                    _native.qq_mp_minus_pm
                ),
                "epsilon^-2 coefficient": _endpoint_expression(
                    _native.qq_double_pole_coefficient
                ),
                "epsilon^-1 coefficient": _endpoint_expression(
                    _native.qq_single_pole_coefficient
                ),
                "one-leg factorization residual": _endpoint_expression(
                    _one_leg_qq_residual
                ),
            },
        ]
        native_pole_rows = [
            {
                "channel": "qg",
                "DY MP-PM pole": (
                    _native.qg_single_pole_coefficient.factor()
                ),
                "independent AEM PM pole": aem_pm_qg_single_pole.factor(),
                "DY transition + PM": _qg_pm_pole_residual,
                "physical relation": "exact: DY transition = -PM",
            },
            {
                "channel": "qqbar",
                "DY MP-PM pole": _endpoint_expression(
                    _native.qq_single_pole_coefficient
                ),
                "independent AEM PM pole": _endpoint_expression(
                    aem_pm_qq_single_pole
                ),
                "DY transition + PM": _endpoint_expression(_qq_pm_pole_residual),
                "physical relation": (
                    "exact in delta/D0/D1/regular basis"
                ),
            },
        ]
        native_sector_rows = [
            _component_row(
                "virtual triangle cuts",
                _native.qq_virtual_triangle,
            ),
            _component_row(
                "two external-bubble cuts",
                _native.qq_external_bubbles,
            ),
            _component_row(
                "direct complementary cuts",
                _native.qq_direct,
            ),
            _component_row(
                "crossed complementary cuts",
                _native.qq_crossed,
            ),
            _component_row(
                "physical sum (AEM/convolution normalization)",
                _native.qq_mp_minus_pm,
            ),
            _component_row(
                "historical normalization transform: z times physical sum",
                _native.qq_historical_z_normalization,
            ),
        ]
        historical_reference_rows = [
            {
                "reference and convention": "historical DY qg cut sum",
                "historical expression": _typed_dy_qg.factor(),
                "graph/master result": _native_qg_qcd.factor(),
                "difference": _qg_dy_raw_residual.factor(),
                "relation": (
                    "opposite sign (graph/master + historical = 0)"
                    if _qg_dy_opposite_residual == E("0")
                    else "nonzero residual"
                ),
            },
            {
                "reference and convention": "historical DIS qg two-beam conversion",
                "historical expression": _dis_qg.factor(),
                "graph/master result": _native_qg_qcd.factor(),
                "difference": _qg_dis_raw_residual.factor(),
                "relation": (
                    "opposite sign (graph/master + historical = 0)"
                    if _qg_dis_opposite_residual == E("0")
                    else "nonzero residual"
                ),
            },
            {
                "reference and convention": (
                    "DY qq reconstruction with external bubbles and exact z product"
                ),
                "historical expression": _endpoint_expression(_typed_dy_qq),
                "graph/master result": _endpoint_expression(
                    _native.qq_historical_z_normalization
                ),
                "difference": _endpoint_expression(
                    _qq_dy_reconstructed_residual
                ),
                "relation": "exact reconstructed match",
            },
            {
                "reference and convention": "historical DIS qq two-beam conversion",
                "historical expression": _endpoint_expression(_dis_qq),
                "graph/master result": _endpoint_expression(
                    _native.qq_historical_z_normalization
                ),
                "difference": _endpoint_expression(_qq_dis_residual),
                "relation": "exact relation in the historical normalization",
            },
            {
                "reference and convention": "two qq external-leg bubbles",
                "historical expression": _endpoint_expression(
                    _typed_external_bubbles
                ),
                "graph/master result": _endpoint_expression(
                    _native.qq_external_bubbles
                ),
                "difference": _endpoint_expression(
                    _bubble_reference_residual
                ),
                "relation": "exact after restoring both bubble terms",
            },
        ]
    else:
        _not_loaded = "cut-sector master sum"
        native_kernel_rows = [
            {
                "channel": _channel,
                "physical C_MP-C_PM": _not_loaded,
                "epsilon^-2 coefficient": _not_loaded,
                "epsilon^-1 coefficient": _not_loaded,
                "one-leg factorization residual": _not_loaded,
            }
            for _channel in ("qg", "qqbar")
        ]
        native_pole_rows = [
            {
                "channel": _channel,
                "DY MP-PM pole": _not_loaded,
                "independent AEM PM pole": _not_loaded,
                "DY transition + PM": _not_loaded,
                "physical relation": "cut-sector master identity",
            }
            for _channel in ("qg", "qqbar")
        ]
        native_sector_rows = [
            {
                "DY contribution": _not_loaded,
                "delta(1-z)": _not_loaded,
                "D0": _not_loaded,
                "D1": _not_loaded,
                "ordinary": _not_loaded,
            }
        ]
        historical_reference_rows = [
            {
                "reference and convention": _not_loaded,
                "historical expression": _not_loaded,
                "graph/master result": _not_loaded,
                "difference": _not_loaded,
                "relation": "cut-sector master identity",
            }
        ]

    scheme_source_audit_rows = [
        {
            "convention": "qq observable ordering",
            "full coefficient": (
                "C_real^MP - C_virtual^MP (39620-39624)"
            ),
            "historical scheme expression": (
                "C_virtual^MP - C_real^MP (42164-42179)"
            ),
            "mathematical resolution": (
                "the observable phase fixes the physical orientation"
            ),
        },
        {
            "convention": "qg benchmark orientation",
            "full coefficient": (
                "the benchmark and PM pole sum to zero (around 40900)"
            ),
            "historical scheme expression": "the extra-cut sum uses the reverse orientation",
            "mathematical resolution": "the physical transition has the positive P_qg pole",
        },
        {
            "convention": "external-leg bubbles",
            "full coefficient": (
                "two half-weighted terms present (38317-38365, 39294-39343)"
            ),
            "historical scheme expression": (
                "zero coefficients assigned at 41820-41872"
            ),
            "mathematical resolution": "both cut-bubble insertions enter the virtual sum",
        },
        {
            "convention": "smooth DY Jacobian",
            "full coefficient": (
                "C(z) maps to z C(z) for the comparison normalization (43023-43031)"
            ),
            "historical scheme expression": (
                "the replacement z -> 1 removes the regular Jacobian terms (43032-43034)"
            ),
            "mathematical resolution": "multiply by z and expand in the canonical endpoint basis",
        },
    ]
    return (
        historical_reference_rows,
        native_kernel_rows,
        native_pole_rows,
        native_scheme_ready,
        native_sector_rows,
        scheme_source_audit_rows,
    )


@app.cell(hide_code=True)
def _(typst_md):
    typst_md(r"""
    == 4. Integration-by-parts reduction and cut projection

    In each cut sector $c$, integration-by-parts identities reduce the shifted
    integrals to a cut-compatible master basis,

    $ I_(g,c)(a)=sum_m R_(a m)^(g,c)(d,s,z,p_1^2,p_2^2)
        M_m^(g,c). $

    The virtual triangle and bubble sectors use their three loop denominators.
    The direct $q bar(q)$ and $q g$ sectors use their physical three-denominator
    families. Each reducible crossed-box cut is the sum of its independent
    three-denominator sectors, and its fully complementary cut is the maximal
    cross-box master $M_(00)$.

    == 5. Analytic master integrals

    Substituting the analytic masters gives the routed contribution

    $ cal(I)_(g,c)=w_(g,c) R_(g,c) M_(g,c) J_(g,c), $

    where $w_(g,c)$ is the cut weight and
    $J_(g,c) in {1,J_1,J_2,J_1 J_2}$ records the incoming-virtuality
    integration.  The nested cut selections then give

    $ C^(upright("PM,bare"))
        =sum_(g,c) chi_(g,c)^(upright("PM")) cal(I)_(g,c), $

    $ C^(upright("MP"))
        =sum_(g,c) [chi_(g,c)^(upright("PM"))
          +(chi_(g,c)^(upright("MP"))-chi_(g,c)^(upright("PM"))) phi_g]
          cal(I)_(g,c). $

    Thus the observable phase $phi_g$ orients precisely the complementary
    MP cuts. The one-cut real sectors involve the massive cut triangle, the
    virtual sectors involve the massless cut bubble and triangle, and the
    fully complementary crossed sector involves the maximal cross-box cut.
    Setting $d=4-2 epsilon$ leaves an exact meromorphic expression in
    $epsilon$, $z$, and the incoming virtualities.
    """)
    return


@app.cell
def _(mo):
    run_full_dy = mo.ui.run_button(
        label="Evaluate cut-sector IBP reductions and the DY coefficient",
        kind="warn",
        full_width=True,
    )
    run_full_dy
    return (run_full_dy,)


@app.cell
def _(
    Kira,
    KiraError,
    assemble_native_dy_scheme,
    dy_context,
    dy_graphs,
    dy_kira_projects,
    dy_numerators,
    dy_project_plan,
    dy_qg_ward_numerators,
    kira_workdir_root,
    run_full_dy,
    run_kira_projects,
):
    if run_full_dy.value:
        full_doctor_report, full_reductions = run_kira_projects(
            Kira(),
            dy_kira_projects,
            kira_workdir_root,
        )
        full_audit, native_scheme = assemble_native_dy_scheme(
            full_reductions,
            plan=dy_project_plan,
            context=dy_context,
            graphs=dy_graphs,
            numerators=dy_numerators,
            ward_numerators=dy_qg_ward_numerators,
        )
    else:
        # Loading a matching complete state is read-only and does not invoke
        # Kira.  This makes the native result reproducible on export while the
        # button remains the only operation allowed to launch/resume reductions.
        _loader = Kira()
        try:
            full_reductions = {
                _project_key: _loader.load(
                    kira_workdir_root / _project.family.name,
                    project=_project,
                    require_complete=True,
                )
                for _project_key, _project in dy_kira_projects.items()
            }
        except KiraError:
            full_reductions = {}
        full_doctor_report = None
        if len(full_reductions) == len(dy_kira_projects):
            full_audit, native_scheme = assemble_native_dy_scheme(
                full_reductions,
                plan=dy_project_plan,
                context=dy_context,
                graphs=dy_graphs,
                numerators=dy_numerators,
                ward_numerators=dy_qg_ward_numerators,
            )
        else:
            full_audit = None
            native_scheme = None
    return full_audit, full_reductions, native_scheme


@app.cell
def _(
    E,
    dy_context,
    endpoint_d0,
    endpoint_d1,
    endpoint_delta,
    native_dy_one_leg_scheme_kernel,
    native_scheme,
    normalize_rational,
):
    """Construct the primary result from the native graph/master assembly only."""

    def _endpoint_expression(_coefficient):
        _canonical = _coefficient.canonical(dy_context.z)
        return (
            _canonical.delta.factor() * endpoint_delta
            + _canonical.d0_prefactor.factor() * endpoint_d0
            + _canonical.d1_prefactor.factor() * endpoint_d1
            + _canonical.regular.factor()
        )

    def _component_row(_label, _coefficient):
        _canonical = _coefficient.canonical(dy_context.z)
        return {
            "native qqbar sector": _label,
            "delta(1-z)": _canonical.delta.factor(),
            "D0(z)": _canonical.d0_prefactor.factor(),
            "D1(z)": _canonical.d1_prefactor.factor(),
            "ordinary": _canonical.regular.factor(),
        }

    native_result_ready = native_scheme is not None
    if native_result_ready:
        _native = native_scheme
        _one_leg_1 = native_dy_one_leg_scheme_kernel(
            dy_context.z,
            dy_context.epsilon,
            dy_context.mu_r_squared,
            dy_context.lambda1_squared,
        )
        _one_leg_2 = native_dy_one_leg_scheme_kernel(
            dy_context.z,
            dy_context.epsilon,
            dy_context.mu_r_squared,
            dy_context.lambda2_squared,
        )
        _qg_reconstruction = normalize_rational(
            _native.qg_mp_minus_pm
            - dy_context.alpha_s
            * dy_context.color_t
            / (4 * dy_context.pi)
                * (_one_leg_1.qg + _one_leg_2.qg)
        )
        _q1g2_reconstruction = normalize_rational(
            _native.qg_ordered_q1g2
            - dy_context.alpha_s
            * dy_context.color_t
            / (2 * dy_context.pi)
            * _one_leg_2.qg
        )
        _g1q2_reconstruction = normalize_rational(
            _native.qg_ordered_g1q2
            - dy_context.alpha_s
            * dy_context.color_t
            / (2 * dy_context.pi)
            * _one_leg_1.qg
        )
        _qq_reconstruction = (
            _native.qq_mp_minus_pm
            - (_one_leg_1.qq + _one_leg_2.qq).scaled(
                dy_context.alpha_s
                * dy_context.color_f
                / (2 * dy_context.pi)
            )
        ).canonical(dy_context.z)
        assert _qg_reconstruction == E("0"), _qg_reconstruction
        assert _q1g2_reconstruction == E("0"), _q1g2_reconstruction
        assert _g1q2_reconstruction == E("0"), _g1q2_reconstruction
        assert _qq_reconstruction.is_zero_for(
            dy_context.z
        ), _qq_reconstruction
        assert _native.qg_double_pole_coefficient == E("0")
        assert _native.qq_double_pole_coefficient.is_zero_for(dy_context.z)
        _q1g2_single_pole = normalize_rational(
            _native.qg_ordered_q1g2.series(
                dy_context.epsilon,
                0,
                0,
            ).get_coefficient(-1)
        )
        _g1q2_single_pole = normalize_rational(
            _native.qg_ordered_g1q2.series(
                dy_context.epsilon,
                0,
                0,
            ).get_coefficient(-1)
        )
        assert normalize_rational(
            _q1g2_single_pole - _native.qg_single_pole_coefficient
        ) == E("0")
        assert normalize_rational(
            _g1q2_single_pole - _native.qg_single_pole_coefficient
        ) == E("0")

        native_result_rows = [
            {
                "channel": "qqbar",
                "native Born-normalized C_MP-C_PM,bare": _endpoint_expression(
                    _native.qq_mp_minus_pm
                ),
                "epsilon^-2": _endpoint_expression(
                    _native.qq_double_pole_coefficient
                ),
                "epsilon^-1": _endpoint_expression(
                    _native.qq_single_pole_coefficient
                ),
                "leg-record reconstruction": _endpoint_expression(
                    _qq_reconstruction
                ),
            },
            {
                "channel": "ordered q(p1) g(p2)",
                "native Born-normalized C_MP-C_PM,bare": (
                    _native.qg_ordered_q1g2.factor()
                ),
                "epsilon^-2": E("0"),
                "epsilon^-1": _q1g2_single_pole.factor(),
                "leg-record reconstruction": _q1g2_reconstruction,
            },
            {
                "channel": "ordered g(p1) q(p2)",
                "native Born-normalized C_MP-C_PM,bare": (
                    _native.qg_ordered_g1q2.factor()
                ),
                "epsilon^-2": E("0"),
                "epsilon^-1": _g1q2_single_pole.factor(),
                "leg-record reconstruction": _g1q2_reconstruction,
            },
            {
                "channel": "qg beam-exchange average",
                "native Born-normalized C_MP-C_PM,bare": (
                    _native.qg_beam_exchange_average.factor()
                ),
                "epsilon^-2": _native.qg_double_pole_coefficient,
                "epsilon^-1": _native.qg_single_pole_coefficient.factor(),
                "leg-record reconstruction": _qg_reconstruction,
            },
        ]
        native_one_leg_rows = [
            {
                "one-leg record": "K_q(z, Lambda_1^2)",
                "regularised endpoint expression": _endpoint_expression(
                    _one_leg_1.qq
                ),
            },
            {
                "one-leg record": "K_g(z, Lambda_1^2)",
                "regularised endpoint expression": _one_leg_1.qg.factor(),
            },
            {
                "one-leg record": "K_q(z, Lambda_2^2)",
                "regularised endpoint expression": _endpoint_expression(
                    _one_leg_2.qq
                ),
            },
            {
                "one-leg record": "K_g(z, Lambda_2^2)",
                "regularised endpoint expression": _one_leg_2.qg.factor(),
            },
        ]
        native_result_pole_rows = [
            {
                "channel": "qqbar",
                "epsilon^-2 coefficient": _endpoint_expression(
                    _native.qq_double_pole_coefficient
                ),
                "epsilon^-1 coefficient": _endpoint_expression(
                    _native.qq_single_pole_coefficient
                ),
                "pole content": "two positive P_qq leg records",
            },
            {
                "channel": "qg",
                "epsilon^-2 coefficient": _native.qg_double_pole_coefficient,
                "epsilon^-1 coefficient": _native.qg_single_pole_coefficient.factor(),
                "pole content": "positive P_qg",
            },
        ]
        native_result_sector_rows = [
            _component_row("virtual triangle cuts", _native.qq_virtual_triangle),
            _component_row("two external-bubble cuts", _native.qq_external_bubbles),
            _component_row("direct complementary cuts", _native.qq_direct),
            _component_row("crossed complementary cuts", _native.qq_crossed),
            _component_row(
                "physical sum (native Born-normalized convention)",
                _native.qq_mp_minus_pm,
            ),
        ]
        _selection_labels = (
            (
                "PM,bare",
                _native.assemblies.pm_bare,
            ),
            ("MP", _native.assemblies.mp),
            (
                "MP - PM,bare",
                _native.assemblies.mp_minus_pm,
            ),
        )
        native_selection_rows = [
            {
                "selection": _label,
                "selected routed records": sum(
                    _multiplier.format_plain() != "0"
                    for _multiplier in _selection.term_multipliers.values()
                ),
                "qqbar virtual records": sum(
                    _selection.term_multipliers[_key].format_plain() != "0"
                    for _key, _term in _native.assemblies.contributions.items()
                    if _term.normalizer == "qq_virtual"
                ),
                "qqbar real records": sum(
                    _selection.term_multipliers[_key].format_plain() != "0"
                    for _key, _term in _native.assemblies.contributions.items()
                    if _term.normalizer == "qq_real"
                ),
                "qg/gq real records": sum(
                    _selection.term_multipliers[_key].format_plain() != "0"
                    for _key, _term in _native.assemblies.contributions.items()
                    if _term.normalizer == "qg_real"
                ),
            }
            for _label, _selection in _selection_labels
        ]

        def _ordered_channel_support(_term):
            if _term.insertion.channel != "qg":
                return "qqbar"
            return {
                "none": "q1g2 and g1q2",
                "p1": "g1q2",
                "p2": "q1g2",
                "both": "q1g2 and g1q2",
            }[_term.incoming_leg]

        native_contribution_rows = [
            {
                "record": _key,
                "graph / cut": (
                    f"{_term.insertion.graph_name} / "
                    f"{_term.insertion.cut_name}"
                ),
                "channel": _term.insertion.channel,
                "incoming virtuality": _term.incoming_leg,
                "ordered-channel support": _ordered_channel_support(_term),
                "endpoint support": _term.endpoint_route.support,
                "master weight w_(g,c)": _term.insertion.relative_weight,
                "PM,bare multiplier": _term.pm_bare_multiplier,
                "MP multiplier": _term.mp_multiplier,
                "MP - PM multiplier": _term.multiplier("mp_minus_pm"),
            }
            for _key, _term in _native.assemblies.contributions.items()
        ]
    else:
        _not_loaded = "cut-sector master sum"
        native_result_rows = [
            {
                "channel": _channel,
                "native Born-normalized C_MP-C_PM,bare": _not_loaded,
                "epsilon^-2": _not_loaded,
                "epsilon^-1": _not_loaded,
                "leg-record reconstruction": _not_loaded,
            }
            for _channel in (
                "qqbar",
                "ordered q(p1) g(p2)",
                "ordered g(p1) q(p2)",
                "qg beam-exchange average",
            )
        ]
        native_one_leg_rows = [
            {
                "one-leg record": "native one-leg record",
                "regularised endpoint expression": _not_loaded,
            }
        ]
        native_result_pole_rows = [
            {
                "channel": _channel,
                "epsilon^-2 coefficient": _not_loaded,
                "epsilon^-1 coefficient": _not_loaded,
                "pole content": _not_loaded,
            }
            for _channel in ("qqbar", "qg")
        ]
        native_result_sector_rows = [
            {
                "native qqbar sector": _not_loaded,
                "delta(1-z)": _not_loaded,
                "D0(z)": _not_loaded,
                "D1(z)": _not_loaded,
                "ordinary": _not_loaded,
            }
        ]
        native_selection_rows = [
            {
                "selection": _not_loaded,
                "selected routed records": _not_loaded,
                "qqbar virtual records": _not_loaded,
                "qqbar real records": _not_loaded,
                "qg/gq real records": _not_loaded,
            }
        ]
        native_contribution_rows = [
            {
                "record": _not_loaded,
                "graph / cut": _not_loaded,
                "channel": _not_loaded,
                "incoming virtuality": _not_loaded,
                "ordered-channel support": _not_loaded,
                "endpoint support": _not_loaded,
                "master weight w_(g,c)": _not_loaded,
                "PM,bare multiplier": _not_loaded,
                "MP multiplier": _not_loaded,
                "MP - PM multiplier": _not_loaded,
            }
        ]
    return (
        native_contribution_rows,
        native_one_leg_rows,
        native_result_pole_rows,
        native_result_ready,
        native_result_rows,
        native_result_sector_rows,
        native_selection_rows,
    )


@app.cell
def _(
    assemble_reference_dy_handoff,
    dy_context,
    full_audit,
    native_scheme,
):
    # Raw closed-form, Mathematica, and pre-correction LaTeX ledgers are
    # constructed only after the native graph/master result exists.  This
    # downstream cell may fail independently without blocking the native
    # scheme kernel or its pole checks.
    full_dy = (
        assemble_reference_dy_handoff(
            full_audit,
            native_scheme,
            context=dy_context,
        )
        if full_audit is not None and native_scheme is not None
        else None
    )
    return (full_dy,)


@app.cell
def _(
    assemble_closed_form_dy,
    dy_context,
    endpoint_d0,
    endpoint_d1,
    endpoint_delta,
):
    full_dy_preview = assemble_closed_form_dy(dy_context)

    def endpoint_row(label, coefficient):
        return {
            "contribution": label,
            "δ(1-z) term": coefficient.delta * endpoint_delta,
            "𝒟₀(z) term": coefficient.d0_prefactor * endpoint_d0,
            "𝒟₁(z) term": coefficient.d1_prefactor * endpoint_d1,
            "ordinary part": coefficient.regular,
        }

    def endpoint_expression(coefficient):
        return (
            coefficient.delta * endpoint_delta
            + coefficient.d0_prefactor * endpoint_d0
            + coefficient.d1_prefactor * endpoint_d1
            + coefficient.regular
        )

    def factorized_endpoint_expression(
        coefficient,
        *collectors,
        canonicalize=False,
    ):
        """Compact one endpoint expression using only Symbolica built-ins."""

        displayed = (
            coefficient.canonical(dy_context.z)
            if canonicalize
            else coefficient
        )
        regular = displayed.regular.expand()
        regular = (
            regular.collect(
                *collectors,
                coeff_map=lambda value: value.factor(),
            )
            if collectors
            else regular.factor()
        )
        return (
            displayed.delta.factor() * endpoint_delta
            + displayed.d0_prefactor.factor() * endpoint_d0
            + displayed.d1_prefactor.factor() * endpoint_d1
            + regular
        )

    return (
        endpoint_expression,
        endpoint_row,
        factorized_endpoint_expression,
        full_dy_preview,
    )


@app.cell
def _(
    E,
    EndpointCoefficient,
    S,
    apply_endpoint_expansion,
    d,
    dy_context,
    dy_graphs,
    dy_numerators,
    endpoint_distribution_expansion,
    kk,
    kp1,
    kp2,
    normalize_rational,
    p1_dot_p2,
    p1_squared,
    p2_squared,
    replace_all,
):
    # Independent, Kira-free parton-model check.  The same simplified traces
    # used by the physical graph assembly are put directly on the two-body
    # cut and combined as squared diagrams and interferences.  Here
    # Q^2 = m^2 = s + t + u.
    _t, _u = S("t", "u")
    _s = dy_context.s
    _q_squared = dy_context.mass_squared
    _on_shell_common = (
        (p1_squared, 0),
        (p2_squared, 0),
        (kk, 0),
        (p1_dot_p2, _s / 2),
    )

    # q(p1) + qbar(p2) -> gamma*(Q) + g: k is the outgoing gluon,
    # so t=(p1-k)^2 and u=(p2-k)^2.
    _qq_rules = _on_shell_common + ((kp1, -_t / 2), (kp2, -_u / 2))
    _qq_direct_graph = dy_graphs["qq direct box"]
    _qq_crossed_graph = dy_graphs["qq crossed box"]
    _qq_direct = normalize_rational(
        replace_all(dy_numerators["qq direct box"], _qq_rules)
        / replace_all(_qq_direct_graph.denominators[1], _qq_rules) ** 2
    )
    _swap_t = S("DY_parton_t_swap")
    _qq_mirror = normalize_rational(
        _qq_direct.replace(_t, _swap_t).replace(_u, _t).replace(_swap_t, _u)
    )
    _qq_interference = normalize_rational(
        replace_all(dy_numerators["qq crossed box"], _qq_rules)
        / (
            replace_all(_qq_crossed_graph.denominators[1], _qq_rules)
            * replace_all(_qq_crossed_graph.denominators[2], _qq_rules)
        )
    )
    _qq_kernel = normalize_rational(
        _qq_direct + _qq_mirror - 2 * _qq_interference
    )
    _qq_kernel_target = (
        2 * (d - 2) ** 2 * (_u / _t + _t / _u)
        + 8 * (d - 2) * _s * _q_squared / (_t * _u)
        - 4 * (d - 2) * (4 - d)
    )
    _qq_kernel_paper_on_shell = _qq_kernel_target.replace(
        _q_squared,
        _s + _t + _u,
    )
    _qq_kernel_residual = normalize_rational(
        _qq_kernel - _qq_kernel_paper_on_shell
    )

    # q(p1) + g(p2) -> gamma*(Q) + q: the existing qg routing takes k as
    # the incoming version of the outgoing quark, hence t=(k+p1)^2 and
    # u=(k+p2)^2.  The box/triangle/bubble trace decomposition is precisely
    # the square/interference decomposition of the two Compton diagrams.
    _qg_rules = _on_shell_common + ((kp1, _t / 2), (kp2, _u / 2))
    _qg_graph = dy_graphs["qg box"]
    _qg_denominator = replace_all(_qg_graph.denominators[1], _qg_rules)
    _qg_external = replace_all(
        dy_graphs["qg triangle"].numerator_divisor,
        _qg_rules,
    )
    _qg_box = normalize_rational(
        replace_all(dy_numerators["qg box"], _qg_rules)
        / _qg_denominator**2
    )
    _qg_triangle = normalize_rational(
        replace_all(dy_numerators["qg triangle"], _qg_rules)
        / (_qg_external * _qg_denominator)
    )
    _qg_bubble = normalize_rational(
        replace_all(dy_numerators["qg bubble"], _qg_rules)
        / _qg_external**2
    )
    _qg_kernel = normalize_rational(-_qg_box + 2 * _qg_triangle - _qg_bubble)
    _qg_kernel_target = (
        -2 * (d - 2) ** 2 * (_s / _t + _t / _s)
        - 8 * (d - 2) * _u * _q_squared / (_s * _t)
        + 4 * (d - 2) * (4 - d)
    )
    _qg_kernel_paper_on_shell = _qg_kernel_target.replace(
        _q_squared,
        _s + _t + _u,
    )
    _qg_kernel_residual = normalize_rational(
        _qg_kernel - _qg_kernel_paper_on_shell
    )

    # Integrate those same diagram sums over the paper's d-dimensional
    # two-body phase space (Eqs. 79-80).  The angular beta functions are
    # divided by R = Gamma(1-epsilon)^2/Gamma(1-2 epsilon); the remaining
    # Gamma(1-epsilon)/Gamma(1-2 epsilon) belongs to the common dimensional-
    # regularization factor stripped from both sides of the comparison.
    _epsilon = dy_context.epsilon
    _z = dy_context.z
    _y = S("DY_parton_y")
    _phase_space_rules = (
        (d, 4 - 2 * _epsilon),
        (_q_squared, _z * _s),
        (_t, -_s * (1 - _z) * (1 - _y)),
        (_u, -_s * (1 - _z) * _y),
    )

    def _normalized_beta_moment(power):
        # B(power + 1 - epsilon, 1 - epsilon) / R.  ``power=-1``
        # is the collinear endpoint moment B(-epsilon, 1-epsilon) / R.
        if power == -1:
            return -1 / _epsilon
        _numerator = E("1")
        _denominator = E("1")
        for _index in range(1, power + 1):
            _numerator *= _index - _epsilon
        for _index in range(1, power + 2):
            _denominator *= _index - 2 * _epsilon
        return normalize_rational(_numerator / _denominator)

    def _integrate_two_body_angle(kernel):
        # Integrate [y(1-y)]^(-epsilon) K(y) exactly.  The DY kernels have
        # only simple endpoint poles; after removing them the remainder is a
        # polynomial whose monomials are normalized beta moments.
        _pole_at_zero = normalize_rational(kernel * _y).replace(_y, 0)
        _pole_at_one = normalize_rational(kernel * (1 - _y)).replace(_y, 1)
        _regular = normalize_rational(
            kernel - _pole_at_zero / _y - _pole_at_one / (1 - _y)
        )
        _integral = -(_pole_at_zero + _pole_at_one) / _epsilon
        for _powers, _coefficient in _regular.to_polynomial(
            vars=[_y]
        ).coefficient_list([_y]):
            _integral += (
                _coefficient.to_expression()
                * _normalized_beta_moment(int(_powers[0]))
            )
        return normalize_rational(_integral)

    _qq_angular_kernel = normalize_rational(
        replace_all(_qq_kernel, _phase_space_rules)
    )
    _qg_angular_kernel = normalize_rational(
        replace_all(_qg_kernel, _phase_space_rules)
    )
    _qq_angular_integral = _integrate_two_body_angle(_qq_angular_kernel)
    _qg_angular_integral = _integrate_two_body_angle(_qg_angular_kernel)
    _p_qg = _z**2 + (1 - _z) ** 2
    _qq_angular_closed = 8 * (1 - _epsilon) * (
        -2 * (1 + _z**2) / (_epsilon * (1 - _z) ** 2)
        - 4 * _epsilon / (1 - 2 * _epsilon)
    )
    _qg_angular_closed = 8 * (1 - _epsilon) / (1 - _z) * (
        -_p_qg / _epsilon
        + (
            3
            + 2 * _z
            - 3 * _z**2
            - _epsilon * (1 + _z) ** 2
        )
        / (2 * (1 - 2 * _epsilon))
    )
    _angular_integration_residuals = {
        "qqbar beta-function angular integral": normalize_rational(
            _qq_angular_integral - _qq_angular_closed
        ),
        "qg beta-function angular integral": normalize_rational(
            _qg_angular_integral - _qg_angular_closed
        ),
    }
    assert all(
        _residual == 0
        for _residual in _angular_integration_residuals.values()
    ), _angular_integration_residuals

    # 4(d-2) = 8(1-epsilon) converts the notebook trace normalization to the
    # paper's Born-normalized kernels.  Combining the exact angular results
    # above with z^epsilon (1-z)^(1-2 epsilon) gives these compact reduced
    # two-body phase-space shapes.
    _qq_integrated_shape_compact = (
        _z**_epsilon
        * (1 - _z) ** (-2 * _epsilon)
        * (
            -2 * (1 + _z**2) / (_epsilon * (1 - _z))
            - 4 * _epsilon * (1 - _z) / (1 - 2 * _epsilon)
        )
    )
    _qg_integrated_shape_compact = (
        _z**_epsilon
        * (1 - _z) ** (-2 * _epsilon)
        * (
            -_p_qg / _epsilon
            + (
                3
                + 2 * _z
                - 3 * _z**2
                - _epsilon * (1 + _z) ** 2
            )
            / (2 * (1 - 2 * _epsilon))
        )
    )

    # The qqbar shape contains (1-z)^(-1-2 epsilon).  Apply the shared
    # endpoint-distribution helper to its smooth prefactor and retain the
    # finite Laurent coefficient.  The second term is evanescent and regular.
    _qq_soft_prefactor = (
        -2 * _z**_epsilon * (1 + _z**2) / _epsilon
    )
    _qq_endpoint = apply_endpoint_expansion(
        endpoint_distribution_expansion(2, _epsilon, order=1),
        _qq_soft_prefactor,
        _z,
    )
    _qq_evanescent_regular = (
        -4
        * _epsilon
        * _z**_epsilon
        * (1 - _z) ** (1 - 2 * _epsilon)
        / (1 - 2 * _epsilon)
    )

    def _through_finite(expression):
        return normalize_rational(
            expression.series(_epsilon, 0, 0).to_expression().expand()
        )

    _qq_normalization = (
        dy_context.alpha_s * dy_context.color_f / (2 * dy_context.pi)
    )
    _qg_normalization = (
        dy_context.alpha_s * dy_context.color_t / (2 * dy_context.pi)
    )
    _qq_integrated_from_diagrams = EndpointCoefficient(
        delta=_qq_normalization
        * _through_finite(_qq_endpoint.delta_coefficient),
        d0_prefactor=_qq_normalization
        * _through_finite(_qq_endpoint.plus_coefficients[0]),
        d1_prefactor=_qq_normalization
        * _through_finite(_qq_endpoint.plus_coefficients[1]),
        regular=_qq_normalization
        * _through_finite(
            _qq_endpoint.regular_part + _qq_evanescent_regular
        ),
    )
    _qg_integrated_from_diagrams = EndpointCoefficient(
        regular=_qg_normalization
        * _through_finite(_qg_integrated_shape_compact)
    )
    aem_integrated_from_diagrams = {
        "qqbar real emission (Eq. 88)": _qq_integrated_from_diagrams,
        "qg Compton (integrated result before Eq. 93)": (
            _qg_integrated_from_diagrams
        ),
    }
    aem_phase_space_derivation_rows = [
        {
            "result": "qqbar real emission",
            "K(y) / [8(1-epsilon)]": (
                _qq_angular_kernel / (8 * (1 - _epsilon))
            ),
            "integrated phase-space shape": _qq_integrated_shape_compact,
        },
        {
            "result": "qg Compton",
            "K(y) / [8(1-epsilon)]": (
                _qg_angular_kernel / (8 * (1 - _epsilon))
            ),
            "integrated phase-space shape": _qg_integrated_shape_compact,
        },
    ]

    aem_parton_kernel_rows = [
        {
            "channel": "qqbar real",
            "diagram piece": "emission from p1, squared",
            "weight x kernel": _qq_direct,
        },
        {
            "channel": "qqbar real",
            "diagram piece": "emission from p2, squared",
            "weight x kernel": _qq_mirror,
        },
        {
            "channel": "qqbar real",
            "diagram piece": "interference",
            "weight x kernel": -2 * _qq_interference,
        },
        {
            "channel": "qqbar real",
            "diagram piece": "Fig. 3(c,d) sum",
            "weight x kernel": _qq_kernel,
        },
        {
            "channel": "qqbar real",
            "diagram piece": "paper Eq. 77 kernel in notebook trace normalization",
            "weight x kernel": _qq_kernel_target,
        },
        {
            "channel": "qg Compton",
            "diagram piece": "box square",
            "weight x kernel": -_qg_box,
        },
        {
            "channel": "qg Compton",
            "diagram piece": "two interferences",
            "weight x kernel": 2 * _qg_triangle,
        },
        {
            "channel": "qg Compton",
            "diagram piece": "bubble square",
            "weight x kernel": -_qg_bubble,
        },
        {
            "channel": "qg Compton",
            "diagram piece": "Fig. 4 sum",
            "weight x kernel": _qg_kernel,
        },
        {
            "channel": "qg Compton",
            "diagram piece": "paper Eq. 85 kernel in notebook trace normalization",
            "weight x kernel": _qg_kernel_target,
        },
    ]
    aem_parton_kernel_residuals = {
        "Fig. 3(c,d) trace sum - Eq. 77 normalized kernel": _qq_kernel_residual,
        "Fig. 4 trace sum - Eq. 85 normalized kernel": _qg_kernel_residual,
    }
    aem_parton_kernel_comparison_rows = [
        {
            "level": "unintegrated kernel",
            "result": "qqbar real emission (Eq. 77)",
            "paper": _qq_kernel_paper_on_shell,
            "ours": _qq_kernel,
            "ours - paper": _qq_kernel_residual,
            "match": (
                "exact (residual = 0)"
                if _qq_kernel_residual == 0
                else "mismatch"
            ),
        },
        {
            "level": "unintegrated kernel",
            "result": "qg Compton (Eq. 85)",
            "paper": _qg_kernel_paper_on_shell,
            "ours": _qg_kernel,
            "ours - paper": _qg_kernel_residual,
            "match": (
                "exact (residual = 0)"
                if _qg_kernel_residual == 0
                else "mismatch"
            ),
        },
    ]
    assert all(
        _residual == 0
        for _residual in aem_parton_kernel_residuals.values()
    ), aem_parton_kernel_residuals
    return (
        aem_integrated_from_diagrams,
        aem_parton_kernel_comparison_rows,
        aem_parton_kernel_residuals,
        aem_parton_kernel_rows,
        aem_phase_space_derivation_rows,
    )


@app.cell
def _(
    E,
    EndpointCoefficient,
    build_aem_dis_1979_factorization_records,
    build_msbar_factorization_records,
    dy_context,
):
    # Paper benchmark transcription after phase-space integration.  These are
    # the Laurent coefficients after stripping the common dimensional-
    # regularization factor.  The DY diagrams still contain initial-state
    # collinear poles; the final rows explicitly apply the paper's DIS
    # parton-density definition.
    _epsilon = dy_context.epsilon
    _z = dy_context.z
    _alpha_s = dy_context.alpha_s
    _color_f = dy_context.color_f
    _color_t = dy_context.color_t
    _pi = dy_context.pi
    _qq_normalization = _alpha_s * _color_f / (2 * _pi)
    _qg_normalization = _alpha_s * _color_t / (2 * _pi)
    _p_qg_polynomial = _z**2 + (1 - _z) ** 2
    _log_z = _z.log()
    _log_one_minus_z = (1 - _z).log()

    _aem_born = EndpointCoefficient(delta=E("1"))
    _aem_qq_virtual = EndpointCoefficient(
        delta=_qq_normalization
        * (-2 / _epsilon**2 - 3 / _epsilon - 8 + 2 * _pi**2 / 3)
    )
    _aem_qq_real = EndpointCoefficient(
        delta=_qq_normalization * 2 / _epsilon**2,
        d0_prefactor=(
            -2 * _qq_normalization * (1 + _z**2) / _epsilon
        ),
        d1_prefactor=4 * _qq_normalization * (1 + _z**2),
        regular=(
            -2
            * _qq_normalization
            * (1 + _z**2)
            * _log_z
            / (1 - _z)
        ),
    )
    _aem_qq_bare = _aem_qq_virtual + _aem_qq_real
    _aem_qq_eq89 = EndpointCoefficient(
        delta=_qq_normalization
        * (-3 / _epsilon - 8 + 2 * _pi**2 / 3),
        d0_prefactor=(
            -2 * _qq_normalization * (1 + _z**2) / _epsilon
        ),
        d1_prefactor=4 * _qq_normalization * (1 + _z**2),
        regular=(
            -2
            * _qq_normalization
            * (1 + _z**2)
            * _log_z
            / (1 - _z)
        ),
    )
    _aem_two_dis_quark_legs = EndpointCoefficient(
        delta=_qq_normalization
        * (3 / _epsilon + 9 + 2 * _pi**2 / 3),
        d0_prefactor=_qq_normalization
        * (2 * (1 + _z**2) / _epsilon + 3),
        d1_prefactor=-2 * _qq_normalization * (1 + _z**2),
        regular=_qq_normalization
        * (
            2 * (1 + _z**2) * _log_z / (1 - _z)
            - 6
            - 4 * _z
        ),
    )
    aem_qq_dis_coefficient = _aem_qq_bare + _aem_two_dis_quark_legs
    _aem_qq_eq91 = EndpointCoefficient(
        delta=_qq_normalization * (1 + 4 * _pi**2 / 3),
        d0_prefactor=3 * _qq_normalization,
        d1_prefactor=2 * _qq_normalization * (1 + _z**2),
        regular=-_qq_normalization * (6 + 4 * _z),
    )

    _aem_qg_compton = EndpointCoefficient(
        regular=_qg_normalization
        * (
            -_p_qg_polynomial / _epsilon
            + _p_qg_polynomial * (2 * _log_one_minus_z - _log_z)
            - E("3/2") * _z**2
            + _z
            + E("3/2")
        )
    )
    _aem_one_dis_gluon_leg = EndpointCoefficient(
        regular=_qg_normalization
        * (
            _p_qg_polynomial / _epsilon
            - _p_qg_polynomial * (_log_one_minus_z - _log_z)
            - 6 * _z * (1 - _z)
        )
    )
    aem_qg_dis_coefficient = _aem_qg_compton + _aem_one_dis_gluon_leg
    _aem_qg_eq95 = EndpointCoefficient(
        regular=_qg_normalization
        * (
            _p_qg_polynomial * _log_one_minus_z
            + E("9/2") * _z**2
            - 5 * _z
            + E("3/2")
        )
    )

    # Mass factorization is an explicit ledger of shifts added to the bare
    # hard coefficient.  The qqbar channel has one q<-q record per incoming
    # beam; each ordered qg/gq channel has one q<-g record on its gluon beam.
    _p_qq = EndpointCoefficient(
        delta=E("3/2"),
        d0_prefactor=1 + _z**2,
    )
    _p_qg = EndpointCoefficient(regular=_p_qg_polynomial)
    msbar_factorization_records = build_msbar_factorization_records(
        dy_context,
        qq_pole_residue=_p_qq,
        qg_pole_residue=_p_qg,
        provenance=("MSbar NLO mass factorization",),
    )
    aem_dis_factorization_records = (
        build_aem_dis_1979_factorization_records(
            dy_context,
            qq_pole_residue=_p_qq,
            qq_finite=EndpointCoefficient(
                delta=E("9/2") + _pi**2 / 3,
                d0_prefactor=E("3/2"),
                d1_prefactor=-(1 + _z**2),
                regular=(
                    (1 + _z**2) * _log_z / (1 - _z)
                    - 3
                    - 2 * _z
                ),
            ),
            qg_pole_residue=_p_qg,
            qg_finite=EndpointCoefficient(
                regular=(
                    -_p_qg.regular * (_log_one_minus_z - _log_z)
                    - 6 * _z * (1 - _z)
                )
            ),
            provenance=("AEM (1979), Eqs. 61 and 69",),
        )
    )
    _aem_qq_from_records = aem_dis_factorization_records.factorize_bare(
        "qqbar",
        _aem_qq_bare,
        _z,
    )
    _aem_qg_from_records = aem_dis_factorization_records.factorize_bare(
        "qg",
        _aem_qg_compton,
        _z,
    )
    assert (
        _aem_qq_from_records - aem_qq_dis_coefficient
    ).is_zero_for(_z)
    assert (
        _aem_qg_from_records - aem_qg_dis_coefficient
    ).is_zero_for(_z)
    assert (
        aem_dis_factorization_records.hard_shift_added_to_bare(
            "qqbar", _z
        )
        - _aem_two_dis_quark_legs
    ).is_zero_for(_z)
    assert (
        aem_dis_factorization_records.hard_shift_added_to_bare("qg", _z)
        - _aem_one_dis_gluon_leg
    ).is_zero_for(_z)
    assert (
        aem_dis_factorization_records.hard_shift_added_to_bare("gq", _z)
        - _aem_one_dis_gluon_leg
    ).is_zero_for(_z)

    def _single_pole(_coefficient):
        _canonical = _coefficient.canonical(_z)

        def _extract(_expression):
            return _expression.series(_epsilon, 0, 0).get_coefficient(-1)

        return EndpointCoefficient(
            delta=_extract(_canonical.delta),
            d0_prefactor=_extract(_canonical.d0_prefactor),
            d1_prefactor=_extract(_canonical.d1_prefactor),
            regular=_extract(_canonical.regular),
        ).canonical(_z)

    # These independent AEM parton-model poles are comparison data only. They
    # are never passed to the native DY builder or used to choose its signs.
    aem_pm_qq_single_pole = _single_pole(_aem_qq_bare)
    aem_pm_qg_single_pole = _single_pole(_aem_qg_compton).regular
    aem_pm_bare_coefficients = {
        "qqbar": _aem_qq_bare.canonical(_z),
        "qg": _aem_qg_compton.canonical(_z),
        "gq": _aem_qg_compton.canonical(_z),
    }
    msbar_pm_coefficients = {
        _channel: msbar_factorization_records.factorize_bare(
            _channel,
            aem_pm_bare_coefficients[_channel],
            _z,
        )
        for _channel in ("qqbar", "qg", "gq")
    }
    aem_dis_pm_coefficients = {
        _channel: aem_dis_factorization_records.factorize_bare(
            _channel,
            aem_pm_bare_coefficients[_channel],
            _z,
        )
        for _channel in ("qqbar", "qg", "gq")
    }
    assert all(
        _single_pole(_coefficient).is_zero_for(_z)
        for _coefficient in msbar_pm_coefficients.values()
    )

    _mu_log = (dy_context.mu_r_squared / dy_context.s).log()
    aem_virtual_laurent = EndpointCoefficient(
        delta=_qq_normalization
        * (
            -2 / _epsilon**2
            - (3 + 2 * _mu_log) / _epsilon
            - 8
            + 7 * _pi**2 / 6
            - 3 * _mu_log
            - _mu_log**2
        )
    )
    aem_integrated_parton_pieces = {
        "Born: Fig. 3(a), Eq. 75": _aem_born,
        "qqbar virtual: Fig. 3(a,b), Eqs. 82-83": _aem_qq_virtual,
        "qqbar real: Fig. 3(c,d), Eq. 88": _aem_qq_real,
        "qqbar diagrams before factorization, Eq. 89": _aem_qq_bare,
        "two AEM-DIS hard shifts, Eq. 61": _aem_two_dis_quark_legs,
        "qqbar AEM-DIS coefficient from records, Eq. 91": (
            aem_dis_pm_coefficients["qqbar"]
        ),
        "qg Compton diagrams: Fig. 4, result before Eq. 93": _aem_qg_compton,
        "one AEM-DIS hard shift, Eq. 69": _aem_one_dis_gluon_leg,
        "qg AEM-DIS coefficient from records, Eq. 95": (
            aem_dis_pm_coefficients["qg"]
        ),
    }
    aem_integrated_paper_targets = {
        "qqbar real emission (Eq. 88)": _aem_qq_real,
        "qg Compton (integrated result before Eq. 93)": _aem_qg_compton,
    }
    aem_paper_residuals = {
        "Fig. 3 real + virtual - Eq. 89": _aem_qq_bare - _aem_qq_eq89,
        "Eq. 89 + two AEM-DIS hard shifts - Eq. 91": (
            aem_dis_pm_coefficients["qqbar"] - _aem_qq_eq91
        ),
        "Fig. 4 + one AEM-DIS hard shift - Eq. 95": (
            aem_dis_pm_coefficients["qg"] - _aem_qg_eq95
        ),
    }
    assert all(
        _residual.is_zero_for(_z)
        for _residual in aem_paper_residuals.values()
    ), aem_paper_residuals
    return (
        aem_dis_factorization_records,
        aem_dis_pm_coefficients,
        aem_integrated_paper_targets,
        aem_integrated_parton_pieces,
        aem_paper_residuals,
        aem_pm_qg_single_pole,
        aem_pm_bare_coefficients,
        aem_pm_qq_single_pole,
        aem_qq_dis_coefficient,
        aem_virtual_laurent,
        msbar_factorization_records,
        msbar_pm_coefficients,
    )


@app.cell
def _(
    aem_dis_factorization_records,
    dy_context,
    endpoint_expression,
    msbar_factorization_records,
):
    factorization_record_rows = [
        {
            "scheme": _record.scheme,
            "ordered channel": _record.ordered_channel,
            "factorizing beam": _record.beam,
            "splitting": _record.factorization_kernel,
            "convolution side": _record.convolution_side,
            "pole shift added to bare": endpoint_expression(
                _record.pole.scaled(_record.coupling_color_prefactor)
            ),
            "finite shift added to bare": endpoint_expression(
                _record.finite.scaled(_record.coupling_color_prefactor)
            ),
        }
        for _ledger in (
            msbar_factorization_records,
            aem_dis_factorization_records,
        )
        for _record in _ledger.records
    ]
    factorization_channel_rows = [
        {
            "scheme": _ledger.scheme,
            "ordered channel": _channel,
            "number of incoming-leg records": len(
                _ledger.for_ordered_channel(_channel)
            ),
            "total hard shift added to bare": endpoint_expression(
                _ledger.hard_shift_added_to_bare(
                    _channel,
                    dy_context.z,
                )
            ),
        }
        for _ledger in (
            msbar_factorization_records,
            aem_dis_factorization_records,
        )
        for _channel in ("qqbar", "qg", "gq")
    ]
    return factorization_channel_rows, factorization_record_rows


@app.cell
def _(
    E,
    EndpointCoefficient,
    Expression,
    aem_integrated_from_diagrams,
    aem_virtual_laurent,
    apply_endpoint_expansion,
    dy_context,
    endpoint_distribution_expansion,
    native_scheme,
    normalize_rational,
    replace_all,
):
    # The cut masters use the historical signed phase-space convention.  The
    # exact common factor below converts their on-shell 11-cut selection to
    # the positive, dimensionally factored AEM two-body convention.  It is
    # derived from the massive cut-bubble normalization and is common to the
    # qqbar and qg real channels; at epsilon=0 it equals -1.
    native_pm_aem_reduced = None
    native_pm_aem_residuals = {}
    native_pm_master_to_aem_factor = None
    native_pm_aem_targets = {
        "qqbar virtual interference": aem_virtual_laurent,
        **aem_integrated_from_diagrams,
    }
    if native_scheme is not None:
        _epsilon = dy_context.epsilon
        _z = dy_context.z
        _s = dy_context.s
        _pi = dy_context.pi
        _positive_radius = _s.sqrt() / 2 - _s.sqrt() * _z / 2
        _native_over_aem = (
            _pi.sqrt()
            / 2
            * _z ** (-_epsilon)
            * (
                Expression.EULER_GAMMA.exp()
                * dy_context.mu_r_squared
            ) ** _epsilon
            * (-1 + 2 * _epsilon)
            * (1 - _z) ** (2 * _epsilon)
            * _positive_radius ** (-2 * _epsilon)
            / (E("3/2") - _epsilon).gamma()
        )
        native_pm_master_to_aem_factor = 1 / _native_over_aem
        _pm_master = native_scheme.assemblies.pm_bare

        def _through_finite(_expression):
            return normalize_rational(
                _expression.series(_epsilon, 0, 0).to_expression().expand()
            )

        def _compact_scale_logs(_coefficient):
            _scale_log = (dy_context.mu_r_squared / _s).log()

            def _compact(_expression):
                return normalize_rational(
                    replace_all(
                        _expression,
                        (
                            (
                                dy_context.mu_r_squared.log(),
                                _scale_log + _s.log(),
                            ),
                        ),
                    )
                )

            return EndpointCoefficient(
                delta=_compact(_coefficient.delta),
                d0_prefactor=_compact(_coefficient.d0_prefactor),
                d1_prefactor=_compact(_coefficient.d1_prefactor),
                regular=_compact(_coefficient.regular),
            ).canonical(_z)

        _qq_scalar = (
            dy_context.alpha_s
            * dy_context.color_f
            / (1 - _epsilon)
            * _pm_master.normalizer_sums["qq_real"]
            * native_pm_master_to_aem_factor
        )
        _qq_smooth = normalize_rational(
            _qq_scalar * (1 - _z) ** (1 + 2 * _epsilon)
        )
        _qq_distribution = apply_endpoint_expansion(
            endpoint_distribution_expansion(2, _epsilon, order=1),
            _qq_smooth,
            _z,
        )
        _native_qq_real = EndpointCoefficient(
            delta=_through_finite(_qq_distribution.delta_coefficient),
            d0_prefactor=_through_finite(
                _qq_distribution.plus_coefficients[0]
            ),
            d1_prefactor=_through_finite(
                _qq_distribution.plus_coefficients[1]
            ),
            regular=_through_finite(_qq_distribution.regular_part),
        ).canonical(_z)
        _native_qg_real = EndpointCoefficient(
            regular=_through_finite(
                dy_context.alpha_s
                * dy_context.color_t
                / (2 * (1 - _epsilon))
                * _pm_master.normalizer_sums["qg_real"]
                * native_pm_master_to_aem_factor
            )
        ).canonical(_z)
        native_pm_aem_reduced = {
            "qqbar virtual interference": (
                _compact_scale_logs(
                    native_scheme.coefficients.pm_bare.qq_virtual
                )
            ),
            "qqbar real emission (Eq. 88)": _native_qq_real,
            "qg Compton (integrated result before Eq. 93)": (
                _native_qg_real
            ),
        }
        native_pm_aem_residuals = {
            _name: (
                native_pm_aem_reduced[_name] - _diagram_coefficient
            ).canonical(_z)
            for _name, _diagram_coefficient in native_pm_aem_targets.items()
        }
        assert all(
            _residual.is_zero_for(_z)
            for _residual in native_pm_aem_residuals.values()
        ), native_pm_aem_residuals
    return (
        native_pm_aem_reduced,
        native_pm_aem_residuals,
        native_pm_aem_targets,
        native_pm_master_to_aem_factor,
    )


@app.cell
def _(
    aem_pm_bare_coefficients,
    build_paper_dy_physical_handoff,
    dy_context,
    native_scheme,
):
    # This paper-facing handoff is downstream of both independent branches:
    # the native cut selection fixes MP-PM, while the AEM comparison fixes the
    # physical normalization of PM-bare.  Neither source can feed back into
    # graph membership, master routing, or transition signs.
    paper_dy_physical = (
        build_paper_dy_physical_handoff(
            native_scheme,
            dy_context,
            aem_pm_bare=aem_pm_bare_coefficients,
            provenance=(
                "independent AEM (1979) virtual, real, and Compton PM diagrams",
                "AEM dimensional factor restored with the explicit scale map",
            ),
        )
        if native_scheme is not None
        else None
    )
    return (paper_dy_physical,)


@app.cell(hide_code=True)
def _(
    dy_context,
    endpoint_row,
    expression_table,
    full_audit,
    full_dy,
    full_dy_preview,
    full_reductions,
    mo,
    physical_project_keys,
    typst_md,
):
    displayed_dy = full_dy if full_dy is not None else full_dy_preview
    if full_audit is None:
        _run_status = mo.callout(
            "The native MP-PM transition is assembled from physical cut "
            "sectors, IBP coefficients, and analytic masters. The closed-form "
            "ledger below is a separate downstream diagnostic.",
            kind="neutral",
        )
        _reduction_table = typst_md(
            f"The complete reduction contains {len(physical_project_keys)} "
            "physical cut sectors."
        )
        _master_table = typst_md(
            "Each cut coefficient multiplies its corresponding analytic master."
        )
        _crossed_endpoint_table = typst_md(
            "The crossed-box contribution is the sum of its four cut sectors."
        )
        _normalization_table = typst_md(
            "The channel factors multiply the corresponding analytic-master terms."
        )
    else:
        _handoff = full_dy.master_handoff
        _downstream_status = (
            "the closed-form identities also vanish"
            if full_audit.reference_targets_exact
            and _handoff.finite_checks_exact(dy_context.z)
            else "the source-comparison residuals are tabulated in the appendix"
        )
        _run_status = mo.callout(
            f"All {len(full_audit.complete_projects)} physical cut sectors are "
            f"reduced; the algebraic, Ward, and master-pole "
            f"residuals of the native transition are zero; {_downstream_status}.",
            kind="success",
        )
        _reduction_table = mo.ui.table(
            [
                {
                    "graph": project_key[0],
                    "cut": project_key[1],
                    "denominator lines": tuple(
                        index + 1 for index in project_key[2]
                    ),
                    "integral family": full_reductions[project_key].family_name,
                    "shifted integrals": len(
                        full_reductions[project_key].requested_targets
                    ),
                    "surviving masters": len(full_reductions[project_key].masters),
                }
                for project_key in physical_project_keys
            ],
            pagination=True,
            page_size=18,
        )
        _master_table = expression_table(
            [
                {
                    "channel": item.channel,
                    "sector": item.sector,
                    "cut families": ", ".join(item.projects) or "analytic 00",
                    "IBP coefficient": item.ibp_coefficient,
                    "analytic master": item.analytic_master,
                    "virtuality factor": item.virtuality_factor,
                    "sector weight": item.relative_weight,
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

    auxiliary_virtual_rows = [
        endpoint_row("ordinary virtual form-factor reference benchmark", displayed_dy.ordinary_virtual),
        endpoint_row("local all-cut virtual diagnostic (complex)", displayed_dy.local_all_cut_virtual),
    ]
    auxiliary_qq_rows = [
        endpoint_row(name, coefficient)
        for name, coefficient in displayed_dy.qq_transverse.pieces.items()
    ]
    auxiliary_qq_rows.append(
        endpoint_row(
            "assembled transverse qqbar reference ledger",
            displayed_dy.qq_transverse.total,
        )
    )
    auxiliary_qg_rows = [
        endpoint_row(name, coefficient)
        for name, coefficient in displayed_dy.qg_transverse.pieces.items()
    ]
    auxiliary_qg_rows.append(
        endpoint_row("assembled transverse qg reference ledger", displayed_dy.qg_transverse.total)
    )
    mo.vstack(
        [
            _run_status,
            typst_md("=== IBP coefficients by cut sector"),
            _reduction_table,
            typst_md("=== Analytic master insertions"),
            _master_table,
            typst_md(r"""
            == 6. Leading virtuality expansion and integration

            Write $v_i=p_i^2$. After the loop integrations, each uncut incoming
            virtuality contributes the leading-power factor

            $ J_i(Lambda_i^2)
              =integral_0^(Lambda_i^2) frac(upright(d) v_i, 2 pi)
                 v_i^(-1-epsilon)
              =-frac((Lambda_i^2)^(-epsilon), 2 pi epsilon). $

            A cut-supported virtuality is normalized by

            $ integral_0^(Lambda_i^2) frac(upright(d) v_i, 2 pi)
                hat(delta)_partial(v_i)=1. $

            If the two incidence labels state whether the corresponding
            incoming virtuality is cut, the sector weights are

            $ w_(11)=1, quad w_(10)=J_2, quad
              w_(01)=J_1, quad w_(00)=J_1J_2. $

            The virtuality integrals converge for $upright("Re") epsilon<0$
            and define their meromorphic continuation from that domain.

            The two half-weighted external-bubble insertions carry $J_1$ and $J_2$.
            Expanding these factors together with the masters through
            $epsilon^0$ produces the collinear poles and the logarithms of
            $Lambda_i^2/mu_R^2$.

            == 7. Endpoint expansion and coefficient assembly

            Singular factors at $z=1$ are expanded with $eta=a epsilon$ as

            $ (1-z)^(-1-eta)
              =-frac(delta(1-z), eta)+cal(D)_0(z)
               -eta cal(D)_1(z)+cal(O)(eta^2), $

            with

            $ cal(D)_0(z)=lr([frac(1,1-z)])_+, quad
              cal(D)_1(z)=lr([frac(log(1-z),1-z)])_+. $

            For the crossed-box sectors, $eta=2 epsilon$ in `11`,
            $eta=epsilon$ in `10` and `01`, and `00` is supported directly on
            $delta(1-z)$.

            The splitting kernels are

            $ P_(q q)(z)=3/2 delta(1-z)+2z cal(D)_0(z)+(1-z), quad
              P_(q g)(z)/T_F=1-2z+2z^2. $

            If $chi_(g,c)^(upright("MP"))$ and
            $chi_(g,c)^(upright("PM"))$ denote the cut memberships,
            the transition coefficient is

            $ C^(upright("MP")-upright("PM"))=sum_(g,c)
              (chi_(g,c)^(upright("MP"))-chi_(g,c)^(upright("PM")))
              phi_g w_(g,c)
              [R_(g,c) M_(g,c) J_(g,c)]_(upright("LP"),epsilon). $

            The virtual triangles, external bubbles, direct cuts, and crossed
            cuts form the $q bar(q)$ coefficient. The Compton box, triangle,
            and bubble sectors form the $q g$ selection; the complementary
            bubble numerator vanishes in the MP--PM-bare difference.
            """),
            typst_md("=== Channel normalization factors"),
            _normalization_table,
            typst_md("=== Crossed-box endpoint sum over all four cuts"),
            _crossed_endpoint_table,
        ]
    )
    return (
        auxiliary_qg_rows,
        auxiliary_qq_rows,
        auxiliary_virtual_rows,
        displayed_dy,
    )


@app.cell(hide_code=True)
def _(
    expression_table,
    mo,
    native_contribution_rows,
    native_one_leg_rows,
    native_result_pole_rows,
    native_result_ready,
    native_result_rows,
    native_result_sector_rows,
    native_selection_rows,
    typst_md,
):
    _result_status = (
        mo.callout(
            "All selected physical cut-sector reductions reconstruct the "
            "two-leg native transition exactly; both epsilon^-2 coefficients "
            "vanish.",
            kind="success",
        )
        if native_result_ready
        else mo.callout(
            "Run or load the complete physical Kira reductions to evaluate "
            "the native MP-PM transition.",
            kind="neutral",
        )
    )
    mo.vstack(
        [
            typst_md(r"""
            == 8. Native regularised MP--PM transition

            One contribution ledger supplies the two physical selections.
            The PM-bare selection contains the ordinary on-shell cuts.  The
            MP selection contains those common cuts together with the
            complementary incoming-virtuality cuts.  Their componentwise
            difference defines

            $ C_(a b)^(upright("MP"))-C_(a b)^(upright("PM,bare")) $

            after dividing out the common leading $q bar(q)$ hard factor.  The
            off-diagonal $qg$ label is a convolution channel.  We use
            $a_s=alpha_s/(2 pi)$, equivalently $g_s^2=4 pi alpha_s$, and retain
            $C_F$ and $T_F$ symbolically.

            Let $L_i=log(mu_R^2/Lambda_i^2)$ and introduce the colour-stripped
            kernels

            $ P_(q q)(z)=3/2 delta(1-z)+2 cal(D)_0(z)-(1+z), quad
              P_(q g)(z)=z^2+(1-z)^2. $

            The graph/master calculation gives one record for each routed
            incoming leg,

            $ K_q(z,Lambda_i^2)=P_(q q)(z)(1/epsilon+L_i)
              +(7/2-pi^2/3)delta(1-z)-2 cal(D)_1(z)
              +z-2-frac((1+z^2)log z,1-z)+(1+z)log(1-z), $

            $ K_g(z,Lambda_i^2)=P_(q g)(z)(1/epsilon+L_i)-2
              -P_(q g)(z)(log z+log(1-z)), $

            and the physical NLO transition terms are

            $ [C_(q bar(q))^(upright("MP")-upright("PM,bare"))]_(upright("NLO"))
              =a_s C_F
                (K_q(z,Lambda_1^2)+K_q(z,Lambda_2^2)), $

            $ [C_(q_1 g_2)^(upright("MP")-upright("PM,bare"))]_(upright("NLO"))
              =a_s T_F K_g(z,Lambda_2^2), $

            $ [C_(g_1 q_2)^(upright("MP")-upright("PM,bare"))]_(upright("NLO"))
              =a_s T_F K_g(z,Lambda_1^2). $

            Their beam-exchange average is

            $ [C_([q g])^(upright("MP")-upright("PM,bare"))]_(upright("NLO"))
              =frac(a_s T_F,2)
                (K_g(z,Lambda_1^2)+K_g(z,Lambda_2^2)). $

            The ordered coefficients multiply the $qg$ and $gq$ luminosities
            separately.  The half-sum is a beam-symmetrized diagnostic; at
            $Lambda_1^2=Lambda_2^2$ it equals either ordered coefficient.

            Equivalently, the displayed parentheses define the corresponding
            coefficients in $C=C^(0)+a_s C^(1)+cal(O)(a_s^2)$.

            Here *regularised* means that $d=4-2 epsilon$ and the physical
            virtuality cutoffs $Lambda_i^2$ are retained.  The simple
            collinear $1/epsilon$ poles and the endpoint distributions are
            part of this pre-factorization result.

            A common absolute observable factor, including a single global
            cluster factor such as $1/(4 pi)$, cancels from this
            Born-normalized MP--PM-bare difference.  An absolute cross section
            combines that global convention with flux, measurement,
            luminosity, and the common PM/MP cut sectors.
            """),
            typst_md("=== Native two-leg transition coefficients"),
            expression_table(native_result_rows, pagination=False),
            _result_status,
            typst_md("=== Native one-leg endpoint records"),
            expression_table(native_one_leg_rows, pagination=False),
            typst_md("=== Native pole content"),
            expression_table(native_result_pole_rows, pagination=False),
            typst_md(r"""
            === $q bar(q)$ transition by native physical sector

            The sector sum includes the two external-bubble insertions as
            physical terms.  The table is displayed in the same
            Born-normalized convention as the result above.
            """),
            expression_table(native_result_sector_rows, pagination=False),
            typst_md("=== PM-bare and MP selections of one contribution ledger"),
            expression_table(native_selection_rows, pagination=False),
            typst_md("==== Routed contribution membership"),
            expression_table(
                native_contribution_rows,
                pagination=True,
                page_size=21,
            ),
            typst_md(r"""
            === Cross-process test

            The two $K_q$ records and the two $K_g$ records form the public
            one-leg contract tested in the DIS notebook.  With the same
            cutoff on both sides, the quark DIS transition is one half of the
            $q bar(q)$ result, while the gluon record agrees with the $qg$
            result after the finite polarization conversion.  This comparison
            uses the native constructions of the two processes, with the
            historical LaTeX and Mathematica expressions reserved for the
            supporting source comparisons.
            """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(
    endpoint_expression,
    expression_table,
    mo,
    paper_dy_physical,
    typst_md,
):
    if paper_dy_physical is None:
        _physical_rows = [
            {
                "ordered channel": "full physical DY",
                "current paper compact form": "native reductions required",
                "native physical coefficient": "native reductions required",
                "native - paper": "native reductions required",
                "comparison": "pending native reductions",
            }
        ]
        _pole_rows = [
            {
                "channel": "full physical DY",
                "Laurent power": "native reductions required",
                "AEM PM-bare residue": "native reductions required",
                "native MP-PM residue": "native reductions required",
                "sum": "native reductions required",
            }
        ]
        _physical_status = mo.callout(
            "Run or load the complete native reductions to assemble the "
            "paper-facing full-DY coefficient.",
            kind="neutral",
        )
        _normalization_rows = [
            {
                "record": "paper-facing physical handoff",
                "value": "native reductions required",
            }
        ]
    else:
        _physical = paper_dy_physical
        _physical_rows = [
            {
                "ordered channel": "qqbar",
                "current paper compact form": endpoint_expression(
                    _physical.compact_targets["qqbar"]
                ),
                "native physical coefficient": endpoint_expression(
                    _physical.qqbar_finite
                ),
                "native - paper": endpoint_expression(
                    _physical.compact_residuals["qqbar"]
                ),
                "comparison": "exact (native - paper = 0)",
            },
            {
                "ordered channel": "q(p1) g(p2)",
                "current paper compact form": (
                    _physical.compact_targets["q1g2"].regular.factor()
                ),
                "native physical coefficient": (
                    _physical.qg_ordered_q1g2_finite.factor()
                ),
                "native - paper": (
                    _physical.compact_residuals["q1g2"].regular
                ),
                "comparison": "exact (native - paper = 0)",
            },
            {
                "ordered channel": "g(p1) q(p2)",
                "current paper compact form": (
                    _physical.compact_targets["g1q2"].regular.factor()
                ),
                "native physical coefficient": (
                    _physical.qg_ordered_g1q2_finite.factor()
                ),
                "native - paper": (
                    _physical.compact_residuals["g1q2"].regular
                ),
                "comparison": "exact (native - paper = 0)",
            },
            {
                "ordered channel": "qg beam-exchange average",
                "current paper compact form": (
                    _physical.compact_targets["qg_average"].regular.factor()
                ),
                "native physical coefficient": (
                    _physical.qg_beam_exchange_average_finite.factor()
                ),
                "native - paper": (
                    _physical.compact_residuals["qg_average"].regular
                ),
                "comparison": "exact (native - paper = 0)",
            },
        ]
        _pole_rows = [
            {
                "channel": _record.channel,
                "Laurent power": f"epsilon^{_record.power}",
                "AEM PM-bare residue": endpoint_expression(
                    _record.pm_bare
                ),
                "native MP-PM residue": endpoint_expression(
                    _record.mp_minus_pm
                ),
                "sum": endpoint_expression(_record.physical_sum),
            }
            for _record in _physical.pole_records
        ]
        _normalization_rows = [
            {
                "record": "normalization",
                "value": _physical.normalization_convention,
            },
            {
                "record": "AEM/native scale map",
                "value": _physical.aem_scale_map,
            },
            {
                "record": "restored AEM dimensional factor",
                "value": _physical.aem_dimensional_factor,
            },
            {
                "record": "provenance",
                "value": "; ".join(_physical.provenance),
            },
        ]
        _physical_status = mo.callout(
            "The AEM PM-bare poles and native MP-PM poles cancel in every "
            "ordered channel.  Each native physical coefficient equals the "
            "current paper compact form exactly.",
            kind="success",
        )

    mo.vstack(
        [
            typst_md(r"""
            == 9. Full physical DY coefficient for the paper

            The physical coefficient joins the independently normalised AEM
            parton-model branch to the native transition,

            $ C_(a b)^(upright("phys"))
              =C_(a b)^(upright("PM,bare"))
               +Delta C_(a b)^(upright("native MP-PM")). $

            MP names the graph selection used to form the native transition.
            The assembled result is denoted *physical*.  The corrected paper
            defines LU as precisely this PM-plus-complement graph set, giving
            $C^(upright("LU")) equiv C^(upright("phys"))$ by definition.

            The common AEM dimensional factor is multiplied as a smooth
            function before the endpoint expansion.  The scale identification

            $ mu_R^2=4 pi e^(-gamma_E) mu_(upright("AEM"))^2, quad Q^2=z s $

            makes its linear expansion
            $1+epsilon log(mu_R^2/Q^2)+cal(O)(epsilon^2)$.  This term combines
            with the PM collinear poles before the finite coefficient is read.

            Write

            $ L_(12)(z)=log(frac(Lambda_1^2 Lambda_2^2 z^2,s^2)), quad
              G_i(z)=log(frac(s(1-z),Lambda_i^2 z)). $

            In $C=C^(0)+a_s C^(1)+cal(O)(a_s^2)$, the finite result is

            $ C_(q bar(q))^(upright("LU"),(1))(z)
              =C_(q bar(q))^(upright("phys"),(1))(z)
              =C_F[-P_(q q)(z)L_(12)(z)-delta(1-z)
                +2(1+z^2)cal(D)_1(z)+2z-4], $

            $ C_(q_1 g_2)^(upright("LU"),(1))(z)
              =C_(q_1 g_2)^(upright("phys"),(1))(z)
              =T_F[P_(q g)(z)G_2(z)-frac(1-2z+3z^2,2)], $

            $ C_(g_1 q_2)^(upright("LU"),(1))(z)
              =C_(g_1 q_2)^(upright("phys"),(1))(z)
              =T_F[P_(q g)(z)G_1(z)-frac(1-2z+3z^2,2)]. $

            The ordered coefficients multiply their respective luminosities.
            Their beam-exchange average is

            $ C_([q g])^(upright("LU"),(1))(z)
              =C_([q g])^(upright("phys"),(1))(z)
              =frac(T_F,2)[P_(q g)(z)(G_1(z)+G_2(z))
                -(1-2z+3z^2)]. $

            These are Born-normalised convolution coefficients.  In the
            reduced convention of the paper an overall $e_q^2$ multiplies
            each channel; an absolute partonic cross section restores the QED
            Born factor, flux, and measurement normalization.
            """),
            typst_md("=== Finite ordered coefficients"),
            expression_table(_physical_rows, pagination=False),
            _physical_status,
            typst_md("=== Cancellation of the regularised poles"),
            expression_table(_pole_rows, pagination=False),
            typst_md("=== Normalization and provenance"),
            expression_table(_normalization_rows, pagination=False),
        ]
    )
    return


@app.cell(hide_code=True)
def _(
    aem_integrated_from_diagrams,
    aem_integrated_paper_targets,
    aem_parton_kernel_comparison_rows,
    aem_phase_space_derivation_rows,
    dy_context,
    endpoint_expression,
    expression_table,
    factorized_endpoint_expression,
    mo,
    native_pm_aem_reduced,
    native_pm_aem_residuals,
    native_pm_aem_targets,
    native_pm_master_to_aem_factor,
    typst_md,
):
    if aem_integrated_paper_targets.keys() != aem_integrated_from_diagrams.keys():
        raise ValueError("Paper and derived integrated comparison rows differ")

    _comparison_rows = [
        {
            "level": _row["level"],
            "result": _row["result"],
            "AEM reference": _row["paper"].factor(),
            "independent PM diagrams": _row["ours"].factor(),
            "difference": _row["ours - paper"],
            "comparison": _row["match"],
        }
        for _row in aem_parton_kernel_comparison_rows
    ]
    for _name, _paper_coefficient in aem_integrated_paper_targets.items():
        _our_coefficient = aem_integrated_from_diagrams[_name]
        _residual = (_our_coefficient - _paper_coefficient).canonical(
            dy_context.z
        )
        _exact = _residual.is_zero_for(dy_context.z)
        _collectors = (
            dy_context.z.log(),
            (1 - dy_context.z).log(),
        )
        _comparison_rows.append(
            {
                "level": "integrated two-body phase space",
                "result": _name,
                "AEM reference": factorized_endpoint_expression(
                    _paper_coefficient,
                    *_collectors,
                    canonicalize=True,
                ),
                "independent PM diagrams": factorized_endpoint_expression(
                    _our_coefficient,
                    *_collectors,
                    canonicalize=True,
                ),
                "difference": endpoint_expression(_residual),
                "comparison": "exact (residual = 0)" if _exact else "mismatch",
            }
        )
        assert _exact, {_name: _residual}

    if native_pm_aem_reduced is None:
        _native_bridge_rows = [
            {
                "result": "native PM-bare selection",
                "AEM PM target": "available without Kira",
                "native PM cut selection": "load the complete reductions",
                "native - diagrams": "load the complete reductions",
                "comparison": "pending cached reductions",
            }
        ]
        _native_bridge_status = mo.callout(
            "Load the complete reductions to evaluate the native PM cut "
            "selection against the independent diagram sum.",
            kind="neutral",
        )
    else:
        _native_bridge_rows = []
        for _name, _diagram_coefficient in native_pm_aem_targets.items():
            _native_coefficient = native_pm_aem_reduced[_name]
            _residual = native_pm_aem_residuals[_name]
            _exact = _residual.is_zero_for(dy_context.z)
            _native_bridge_rows.append(
                {
                    "result": _name,
                    "AEM PM target": factorized_endpoint_expression(
                        _diagram_coefficient,
                        dy_context.z.log(),
                        (1 - dy_context.z).log(),
                        canonicalize=True,
                    ),
                    "native PM cut selection": factorized_endpoint_expression(
                        _native_coefficient,
                        dy_context.z.log(),
                        (1 - dy_context.z).log(),
                        canonicalize=True,
                    ),
                    "native - diagrams": endpoint_expression(_residual),
                    "comparison": (
                        "exact (residual = 0)" if _exact else "mismatch"
                    ),
                }
            )
            assert _exact, {_name: _residual}
        _native_bridge_status = mo.callout(
            "The native PM-bare virtual selection equals the AEM virtual "
            "record, while its real-emission and Compton selections equal the "
            "independent diagram sums.  All three residuals vanish after the "
            "explicit cut-master convention maps.",
            kind="success",
        )

    _phase_space_table = expression_table(
        aem_phase_space_derivation_rows,
        pagination=False,
    )
    _comparison_table = expression_table(
        _comparison_rows,
        pagination=False,
    )
    _native_bridge_table = expression_table(
        _native_bridge_rows,
        pagination=False,
    )
    mo.vstack(
        [
            typst_md(r"""
            == 10. Reduced AEM parton-model validation

            This is the diagram-level derivation supporting the direct,
            all-factor comparison in the following section.  It documents the
            independently assembled PM diagrams in the stated AEM convention,
            downstream of the native graph selection, master reduction, and
            MP--PM normalization.

            For $q bar(q) arrow gamma^* g$, the two emission diagrams combine
            as their two squares minus twice their interference. For
            $q g arrow gamma^* q$, the crossed Compton diagrams combine into
            box, triangle-interference, and bubble terms.

            With $Q^2=s+t+u$, the unintegrated rows reproduce AEM Eqs. 77 and
            85. The integrated rows start from the same diagram sums, apply the
            $d$-dimensional two-body phase space of paper Eqs. 79--80, and
            reproduce Eq. 88 and the integrated $q g$ result immediately before
            Eq. 93. For this reduced derivation only, both columns factor out
            the common dimensional term
            $(4 pi mu^2/Q^2)^epsilon Gamma(1-epsilon)/Gamma(1-2epsilon)$.
            Section 11 restores it, together with the QED, flux, and
            luminosity factors. Each reduced row retains a compact displayed
            form, while the canonical expansion of the difference supplies the
            equality criterion.
            """),
            _phase_space_table,
            _comparison_table,
            mo.callout(
                "All four residuals vanish in the stated AEM normalization. "
                "This independently checks the PM diagram branch; the native "
                "MP-PM result is fixed by the graph ledger above.",
                kind="success",
            ),
            typst_md(r"""
            === The PM selection of the native cut ledger

            The common `11` cuts of the native ledger are precisely the
            PM-bare real selection.  Its massive cut master carries the signed
            historical phase-space convention.  Relative to the positive,
            dimensionally factored AEM convention the common exact factor is

            $ R_epsilon
              =frac(sqrt(pi),2) z^(-epsilon)
                (e^gamma_E mu_R^2)^epsilon (2epsilon-1)
                (1-z)^(2epsilon)
                lr(frac(sqrt(s)(1-z),2))^(-2epsilon)
                / Gamma(3/2-epsilon). $

            Thus $I_(upright("AEM"))=I_(upright("native"))/R_epsilon$.
            In four dimensions, $R_epsilon arrow -1$, exposing the relative
            sign of the native cut-master convention.
            Applying this map, followed by the same endpoint expansion, joins
            the PM branch of the native graph ledger to the independent
            parton-diagram calculation.

            The common virtual record uses the physical timelike interference
            projection

            $ B_(upright("virt"))(s)
              =frac(B(s+i0)+B(s-i0),2)
              =B(-s) cos(pi epsilon). $

            Its Laurent expansion supplies the virtual row below.  Together,
            the three rows connect the PM subset of the native graph ledger to
            the AEM virtual record and the independently assembled real NLO
            partonic channels.
            """),
            expression_table(
                [
                    {
                        "conversion": "native signed cut master -> positive AEM reduced phase space",
                        "factor multiplying native": native_pm_master_to_aem_factor,
                    }
                ],
                pagination=False,
            )
            if native_pm_master_to_aem_factor is not None
            else typst_md("The conversion factor is evaluated with the native reductions."),
            _native_bridge_table,
            _native_bridge_status,
            mo.callout(
                "The reduced identities use a_s = alpha_s/(2 pi), the real-cut "
                "factor R_epsilon, and the timelike cos(pi epsilon) projection. "
                "The global 1/(4 pi) cluster factor enters with the absolute "
                "observable normalization.",
                kind="neutral",
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(
    E,
    EndpointCoefficient,
    S,
    aem_integrated_from_diagrams,
    aem_integrated_parton_pieces,
    aem_integrated_paper_targets,
    dy_context,
    replace_all,
    scalar_printer,
):
    """Restore the external AEM cross-section convention around PM kernels.

    The endpoint coefficients above are intentionally reduced kernels.  This
    cell keeps the AEM luminosity, QED, flux, and dimensional factors outside
    them, so that the conventional absolute PM presentation cannot feed back
    into the native LU construction.
    """

    aem_a_s = S(
        "DY_AEM_a_s",
        print=scalar_printer(latex=r"a_s", typst="a_s"),
    )
    aem_alpha_em = S(
        "DY_AEM_alpha_em",
        print=scalar_printer(latex=r"\alpha_{\mathrm{em}}", typst="alpha_(em)"),
    )
    aem_hadronic_s = S(
        "DY_AEM_S",
        print=scalar_printer(latex=r"S", typst="S"),
    )
    aem_q_squared = S(
        "DY_AEM_Q_sq",
        print=scalar_printer(latex=r"Q^2", typst="Q^2"),
    )
    _aem_mu_squared = S(
        "DY_AEM_mu_sq",
        print=scalar_printer(
            latex=r"\mu_{\mathrm{AEM}}^2",
            typst="mu_(AEM)^2",
        ),
    )

    _epsilon = dy_context.epsilon
    _z = dy_context.z
    _aem_rules = (
        # AEM uses a_s = alpha_s/(2 pi).  The virtual reference is at z=1,
        # where its partonic invariant is Q^2.
        (dy_context.alpha_s, 2 * dy_context.pi * aem_a_s),
        (dy_context.s, aem_q_squared),
    )

    def _in_aem_convention(_coefficient):
        def _replace(_expression):
            return replace_all(_expression, _aem_rules).expand().together().cancel()

        return EndpointCoefficient(
            delta=_replace(_coefficient.delta),
            d0_prefactor=_replace(_coefficient.d0_prefactor),
            d1_prefactor=_replace(_coefficient.d1_prefactor),
            regular=_replace(_coefficient.regular),
        )

    # AEM Eqs. 25 and 35: the hadronic luminosity convention is separated from
    # the per-flavour electric charge.  The NLO rows additionally carry the
    # common d-dimensional factor which was divided out in section 10.
    aem_absolute_prefactor = (
        4
        * dy_context.pi
        * aem_alpha_em**2
        / (3 * dy_context.color_count * aem_hadronic_s * aem_q_squared)
    )
    aem_dimensional_factor = (
        (4 * dy_context.pi * _aem_mu_squared / aem_q_squared) ** _epsilon
        * (1 - _epsilon).gamma()
        / (1 - 2 * _epsilon).gamma()
    )
    aem_absolute_born_factor = (
        aem_absolute_prefactor * dy_context.electric_charge**2
    )
    aem_absolute_nlo_factor = (
        aem_absolute_born_factor * aem_dimensional_factor
    )
    aem_absolute_born = EndpointCoefficient(delta=E("1"))
    aem_absolute_targets = {
        _name: _in_aem_convention(_coefficient)
        for _name, _coefficient in aem_integrated_paper_targets.items()
    }
    aem_absolute_from_diagrams = {
        _name: _in_aem_convention(_coefficient)
        for _name, _coefficient in aem_integrated_from_diagrams.items()
    }
    aem_absolute_residuals = {
        _name: (
            aem_absolute_from_diagrams[_name] - aem_absolute_targets[_name]
        ).canonical(_z)
        for _name in aem_absolute_targets
    }
    assert all(
        _residual.is_zero_for(_z)
        for _residual in aem_absolute_residuals.values()
    ), aem_absolute_residuals

    aem_absolute_virtual_reference = _in_aem_convention(
        aem_integrated_parton_pieces[
            "qqbar virtual: Fig. 3(a,b), Eqs. 82-83"
        ]
    )
    return (
        aem_a_s,
        aem_absolute_born,
        aem_absolute_born_factor,
        aem_absolute_from_diagrams,
        aem_absolute_nlo_factor,
        aem_absolute_prefactor,
        aem_absolute_residuals,
        aem_absolute_targets,
        aem_absolute_virtual_reference,
        aem_alpha_em,
        aem_dimensional_factor,
        aem_hadronic_s,
        aem_q_squared,
    )


@app.cell(hide_code=True)
def _(
    aem_absolute_born,
    aem_absolute_born_factor,
    aem_absolute_from_diagrams,
    aem_absolute_nlo_factor,
    aem_absolute_residuals,
    aem_absolute_targets,
    aem_absolute_virtual_reference,
    dy_context,
    expression_table,
    factorization_channel_rows,
    factorization_record_rows,
    factorized_endpoint_expression,
    mo,
    typst_md,
):
    def _born_expression(_coefficient):
        return aem_absolute_born_factor * factorized_endpoint_expression(
            _coefficient,
            canonicalize=True,
        )

    def _nlo_expression(_coefficient):
        return aem_absolute_nlo_factor * factorized_endpoint_expression(
            _coefficient,
            dy_context.z.log(),
            (1 - dy_context.z).log(),
            canonicalize=True,
        )

    _real_rows = [
        {
            "partonic contribution": "Born qqbar -> gamma*",
            "AEM conventional cross section": _born_expression(aem_absolute_born),
            "independent PM diagrams": "Born normalization anchor",
            "PM - AEM": "normalization anchor",
            "comparison": "external Born normalization",
        }
    ]
    for _name, _target in aem_absolute_targets.items():
        _residual = aem_absolute_residuals[_name]
        _display_name = {
            "qg Compton (integrated result before Eq. 93)": (
                "ordered qg Compton: q(p_1) g(p_2) -> gamma* q"
            )
        }.get(_name, _name)
        _real_rows.append(
            {
                "partonic contribution": _display_name,
                "AEM conventional cross section": _nlo_expression(_target),
                "independent PM diagrams": _nlo_expression(
                    aem_absolute_from_diagrams[_name]
                ),
                "PM - AEM": _nlo_expression(_residual),
                "comparison": "exact (factorized residual = 0)",
            }
        )

    _virtual_rows = [
        {
            "partonic contribution": "qqbar virtual: Fig. 3(a,b), Eqs. 82--83",
            "AEM conventional cross section": _nlo_expression(
                aem_absolute_virtual_reference
            ),
            "independent PM diagrams": "AEM source transcription only",
            "PM - AEM": "source transcription",
            "comparison": "reference record",
        }
    ]
    mo.vstack(
        [
            typst_md(r"""
            == 11. Direct unstripped AEM PM validation

            This is a direct, unstripped validation of the independently
            assembled real PM diagrams in the AEM cross-section convention. It
            restores the external cross-section convention around the reduced
            kernels and remains external to the native
            $C^(upright("MP"))-C^(upright("PM"))$ construction.

            Write $z=Q^2/(x_1 x_2 S)$ and $hat(s)=x_1 x_2 S$.  In the AEM
            luminosity convention,

            $
              cal(B)_(upright("AEM"))(S,Q^2)
              = frac(4 pi alpha_(em)^2, 3 N_c S Q^2),
              quad
              cal(N)_epsilon
              = (frac(4 pi mu_(upright("AEM"))^2,Q^2))^epsilon
                frac(Gamma(1-epsilon),Gamma(1-2 epsilon)).
            $

            The native master scale and the unbarred AEM scale obey

            $ mu_R^2=4 pi e^(-gamma_E) mu_(upright("AEM"))^2, $

            so $(e^gamma_E mu_R^2)^epsilon$ and
            $(4 pi mu_(upright("AEM"))^2)^epsilon$ are the same dimensional
            convention.

            The corresponding partonic flux normalization is

            $
              frac(d hat(sigma)_(a b), d Q^2)
              = frac(4 pi alpha_(em)^2 e_q^2,
                  3 N_c Q^2 hat(s)) C_(a b)(z),
            $

            and the hadronic result is

            $
              frac(d sigma^(upright("PM")),d Q^2)
              = cal(B)_(upright("AEM")) sum_f e_f^2
                integral frac(d x_1,x_1) integral frac(d x_2,x_2)
                { [q_f bar(q)_f+bar(q)_f q_f] C_(q bar(q))(z)
                + [(q_f+bar(q)_f)g+g(q_f+bar(q)_f)] C_(q g)(z) }.
            $

            Thus the displayed Born row carries
            $cal(B)_(upright("AEM")) e_q^2$, while each NLO row carries
            $cal(B)_(upright("AEM")) e_q^2 cal(N)_epsilon$.  Its coefficient
            retains $a_s=alpha_s/(2 pi)$, $C_F$, or $T_F$ explicitly.  The
            real-emission and Compton rows below are independent diagram
            calculations; their equality is tested by the exact endpoint
            residual after restoring the same outer factors on both sides. The
            Compton row is the ordered $q(p_1)g(p_2)$ contribution.  The two
            $qg$ luminosities in the formula supply both beam orientations, and
            $q_f+bar(q)_f$ supplies the charge-conjugate channels.
            """),
            expression_table(_real_rows, pagination=False),
            typst_md(r"""
            === Incoming-leg mass-factorization records

            The factorization ledger uses the hard-coefficient convention

            $ C_(a b)^(upright("PM"),S)
              =C_(a b)^(upright("PM"),upright("bare"))
               +sum_(ell in (a,b)) H_(ell)^S. $

            The $q bar(q)$ channel contains one $q arrow q$ record on each
            incoming beam.  An ordered $q g$ or $g q$ channel contains one
            $g arrow q$ record on its gluon beam.  The two ordered Compton
            channels remain separate throughout this ledger.

            The $overline("MS")$ records contain the positive
            $P^(0)/epsilon$ hard shifts in the common factored dimensional
            convention.  The AEM-DIS-1979 records contain the same pole shifts
            and the finite terms of AEM Eqs. 61 and 69.  These records act on
            the PM-bare selection; the MP--PM cut difference is a separate
            graph-selection identity.
            """),
            expression_table(factorization_record_rows, pagination=False),
            typst_md("==== Sum of incoming-leg records by ordered channel"),
            expression_table(factorization_channel_rows, pagination=False),
            typst_md(r"""
            === Virtual: AEM source transcription only

            The virtual coefficient is shown in the same factored AEM
            convention.  Its reduced coefficient is the record validated
            directly against the native timelike interference in Section 10.
            """),
            expression_table(_virtual_rows, pagination=False),
            mo.callout(
                "The AEM prefactor supplies the QED, partonic-flux, and "
                "hadronic-luminosity convention.  The LU cluster factor "
                "1/(4 pi) belongs to the separate LU normalization ledger. "
                "An absolute LU comparison combines it with the complete QED "
                "Born process, flux, and leptonic measurement normalization.",
                kind="neutral",
            ),
            mo.callout(
                "The endpoint coefficients are retained through epsilon^0, "
                "so N_epsilon is intentionally kept factorized. Re-expanding "
                "it through the finite term would require the O(epsilon) real "
                "coefficient functions; the exact residuals above are "
                "factorized identities at the retained order.",
                kind="warn",
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(
    displayed_dy,
    dy_context,
    expression_table,
    factorized_endpoint_expression,
    mo,
    typst_md,
):
    _qq_source_log = (
        dy_context.lambda1_squared
        * dy_context.lambda2_squared
        * dy_context.z**2
        / dy_context.s**2
    ).log()
    _qg_source_log = (
        dy_context.lambda1_squared
        * dy_context.lambda2_squared
        * dy_context.z**2
        / (dy_context.s**2 * (1 - dy_context.z) ** 2)
    ).log()
    _coefficient_comparison_table = expression_table(
        [
            {
                "result": "qqbar transverse ledger",
                "pre-correction LaTeX snapshot": factorized_endpoint_expression(
                    displayed_dy.qq_historical_manuscript,
                    _qq_source_log,
                ),
                "recorded Mathematica": factorized_endpoint_expression(
                    displayed_dy.qq_recorded_mathematica,
                    _qq_source_log,
                ),
                "raw-master closed ledger": factorized_endpoint_expression(
                    displayed_dy.qq_transverse.total,
                    _qq_source_log,
                ),
                "ledger - pre-correction LaTeX": factorized_endpoint_expression(
                    displayed_dy.qq_transverse_minus_historical_manuscript,
                    _qq_source_log,
                    canonicalize=True,
                ),
                "ledger - Mathematica": factorized_endpoint_expression(
                    displayed_dy.qq_transverse_minus_recorded_mathematica,
                    _qq_source_log,
                    canonicalize=True,
                ),
            },
            {
                "result": "qg transverse ledger",
                "pre-correction LaTeX snapshot": factorized_endpoint_expression(
                    displayed_dy.qg_historical_manuscript,
                    _qg_source_log,
                ),
                "recorded Mathematica": factorized_endpoint_expression(
                    displayed_dy.qg_recorded_mathematica,
                    _qg_source_log,
                ),
                "raw-master closed ledger": factorized_endpoint_expression(
                    displayed_dy.qg_transverse.total,
                    _qg_source_log,
                ),
                "ledger - pre-correction LaTeX": factorized_endpoint_expression(
                    displayed_dy.qg_transverse_minus_historical_manuscript,
                    _qg_source_log,
                    canonicalize=True,
                ),
                "ledger - Mathematica": factorized_endpoint_expression(
                    displayed_dy.qg_transverse.total
                    - displayed_dy.qg_recorded_mathematica,
                    _qg_source_log,
                    canonicalize=True,
                ),
            },
        ],
        pagination=False,
    )
    mo.vstack(
        [
            typst_md(r"""
            = Supporting validation and reference comparisons

            The main text culminates in the direct AEM validation.  The
            following tables record source comparisons, polynomial identities,
            historical convention maps, and reference ledgers for the fixed
            native result.

            == Historical LaTeX and Mathematica comparison

            This downstream table places three separately recorded transverse
            ledgers side by side. *Pre-correction LaTeX snapshot* and
            *recorded Mathematica* are historical source records; the
            *raw-master closed ledger* is the finite diagnostic assembled with
            the historical cut convention.  The current paper coefficient and
            its exact native comparison appear in Section 9.  The two
            difference columns record every historical disagreement explicitly.
            """),
            _coefficient_comparison_table,
        ]
    )
    return


@app.cell(hide_code=True)
def _(
    auxiliary_qg_rows,
    auxiliary_qq_rows,
    auxiliary_virtual_rows,
    expression_table,
    mo,
    typst_md,
):
    mo.vstack(
        [
            typst_md(r"""
            == Auxiliary raw-master transverse ledger

            These convention-specific finite records support the source and
            master-routing diagnostics.  The paper-facing coefficient is the
            physical handoff in Section 9.
            """),
            typst_md("=== Virtual reference records"),
            expression_table(auxiliary_virtual_rows, pagination=False),
            typst_md("=== $q bar(q)$ transverse reference ledger"),
            expression_table(auxiliary_qq_rows, pagination=False),
            typst_md("=== $q g$ transverse reference ledger"),
            expression_table(auxiliary_qg_rows, pagination=False),
            typst_md(r"""
            == Trace-to-scalar polynomial identities

            The expanded scalar polynomials provide exact identities for the
            trace-reduced transverse and longitudinal numerators.
            """),
        ]
    )
    return


@app.cell
def _(
    E,
    d,
    dy_graphs,
    dy_numerators,
    dy_qg_ward_numerators,
    kk,
    kp1,
    kp2,
    mass_squared,
    normalize_rational,
    p1_dot_p2,
    p1_squared,
    p2_squared,
    replace_all,
):
    # Validation only: these expanded polynomials are independent oracles for
    # the editable trace inputs above. Nothing in the assembly depends on them.
    _oracle_triangle_direct = 4 * (d - 2) * (
        4 * kp1 * kp2
        + 4 * kp2 * p1_squared
        - d * kp2 * p1_squared
        - 4 * kk * p1_dot_p2
        + d * kk * p1_dot_p2
        - 4 * kp1 * p1_dot_p2
        + 4 * kp2 * p1_dot_p2
        - 4 * p1_dot_p2**2
        - 4 * kp1 * p2_squared
        + d * kp1 * p2_squared
        + 4 * p1_squared * p2_squared
        - d * p1_squared * p2_squared
    )
    _oracle_triangle_crossed = -4 * (d - 2) * (
        -8 * kp1 * kp2
        + 2 * d * kp1 * kp2
        + 4 * kp2 * p1_squared
        - d * kp2 * p1_squared
        + 8 * kk * p1_dot_p2
        - d * kk * p1_dot_p2
        - 4 * kp1 * p1_dot_p2
        - 4 * kp2 * p1_dot_p2
        + 4 * p1_dot_p2**2
        + 4 * kp1 * p2_squared
        - d * kp1 * p2_squared
        - 4 * p1_squared * p2_squared
        + d * p1_squared * p2_squared
    )
    _oracle_virtual_bubble = 4 * (d - 2) * (
        -8 * kp2 * p1_dot_p2
        + 2 * d * kp2 * p1_dot_p2
        + 6 * kp1 * p2_squared
        - d * kp1 * p2_squared
    )
    _oracle_direct_box = 4 * (d - 2) ** 2 * (
        p1_squared * (p1_dot_p2 - 2 * kp2)
        - p1_dot_p2 * kk
        + 2 * kp1 * kp2
    )
    _oracle_crossed_box = 4 * (d - 2) * (
        (d - 8) * kk * p1_dot_p2
        + 4 * p1_dot_p2 * (kp1 + kp2)
        + (8 - 2 * d) * kp1 * kp2
        + (d - 4) * (kp1 * p2_squared + kp2 * p1_squared)
        + (4 - d) * p1_squared * p2_squared
        - 4 * p1_dot_p2**2
    )
    _oracle_qg_box = 4 * (d - 2) ** 2 * (
        kk * kp2
        - kp2 * p1_squared
        + 2 * kk * p1_dot_p2
        + 2 * kp1 * p1_dot_p2
    )
    _oracle_qg_triangle = -4 * (d - 2) * (
        4 * kp1 * kp2
        + 4 * kp2**2
        + 8 * kp2 * p1_squared
        - d * kp2 * p1_squared
        - 4 * kk * p1_dot_p2
        + d * kk * p1_dot_p2
        - 8 * kp1 * p1_dot_p2
        + 2 * d * kp1 * p1_dot_p2
        + 4 * kp2 * p1_dot_p2
        - 4 * kk * p2_squared
        + d * kk * p2_squared
        - 4 * kp1 * p2_squared
        + d * kp1 * p2_squared
    )
    _oracle_qg_bubble = -4 * (d - 2) ** 2 * (
        kp2 * p1_squared
        - 2 * kp1 * p1_dot_p2
        - 2 * kp1 * p2_squared
        - kp2 * p2_squared
    )
    _expanded_numerator_oracles = {
        "virtual triangle 1": _oracle_triangle_direct,
        "virtual triangle 2": _oracle_triangle_crossed,
        "virtual bubble": _oracle_virtual_bubble,
        "qq direct box": _oracle_direct_box,
        "qq crossed box": _oracle_crossed_box,
        "qg box": _oracle_qg_box,
        "qg triangle": _oracle_qg_triangle,
        "qg bubble": _oracle_qg_bubble,
    }
    dy_trace_residuals = {
        _graph_name: normalize_rational(
            dy_numerators[_graph_name] - _expanded_oracle
        )
        for _graph_name, _expanded_oracle in _expanded_numerator_oracles.items()
    }

    # The former denominator-expanded Ward inputs are likewise retained only
    # as a validation oracle for the three longitudinal traces.
    _oracle_q_squared = 2 * p1_dot_p2
    _oracle_d0, _oracle_d1, _oracle_dm = tuple(
        replace_all(
            _denominator,
            (
                (p1_squared, E("0")),
                (p2_squared, E("0")),
            ),
        )
        for _denominator in dy_graphs["qg box"].denominators
    )
    _oracle_longitudinal_box = (
        2
        * (d - 2)
        * _oracle_d1**2
        * (
            _oracle_q_squared
            + _oracle_d1
            - _oracle_dm
            - mass_squared
        )
    )
    _oracle_longitudinal_triangle = (
        2
        * _oracle_q_squared
        * (d - 2)
        * _oracle_d1
        * (
            _oracle_q_squared
            - _oracle_d0
            + _oracle_d1
            - _oracle_dm
            - mass_squared
        )
    )
    _oracle_longitudinal_bubble = (
        2
        * _oracle_q_squared
        * (d - 2)
        * (
            -2 * _oracle_q_squared * _oracle_d0
            + _oracle_q_squared * _oracle_d1
            - _oracle_q_squared * _oracle_dm
            - _oracle_q_squared * mass_squared
            - _oracle_d0 * _oracle_d1
            + _oracle_q_squared**2
            + _oracle_d0**2
        )
    )
    _expanded_ward_oracles = {
        "box": -_oracle_longitudinal_box / mass_squared,
        "triangle": -_oracle_longitudinal_triangle
        / (mass_squared * _oracle_q_squared),
        "bubble": -_oracle_longitudinal_bubble
        / (mass_squared * _oracle_q_squared**2),
    }
    dy_qg_ward_trace_residuals = {
        _piece_name: normalize_rational(
            dy_qg_ward_numerators[_piece_name] - _expanded_oracle
        )
        for _piece_name, _expanded_oracle in _expanded_ward_oracles.items()
    }

    _nonzero_trace_residuals = {
        **{
            _graph_name: _residual
            for _graph_name, _residual in dy_trace_residuals.items()
            if _residual != E("0")
        },
        **{
            f"qg Ward {_piece_name}": _residual
            for _piece_name, _residual in dy_qg_ward_trace_residuals.items()
            if _residual != E("0")
        },
    }
    assert not _nonzero_trace_residuals, _nonzero_trace_residuals
    return dy_qg_ward_trace_residuals, dy_trace_residuals


@app.cell(hide_code=True)
def _(
    aem_integrated_parton_pieces,
    aem_paper_residuals,
    aem_parton_kernel_residuals,
    aem_parton_kernel_rows,
    aem_qq_dis_coefficient,
    aem_virtual_laurent,
    displayed_dy,
    dy_context,
    dy_qg_ward_trace_residuals,
    dy_trace_residuals,
    endpoint_row,
    expression_table,
    full_audit,
    historical_reference_rows,
    mo,
    normalize_rational,
    scheme_source_audit_rows,
    typst_md,
):
    _aem_kernel_table = expression_table(
        aem_parton_kernel_rows,
        pagination=False,
    )
    _aem_kernel_residual_table = expression_table(
        [
            {"check": _name, "residual": _residual}
            for _name, _residual in aem_parton_kernel_residuals.items()
        ],
        pagination=False,
    )
    _aem_integrated_table = expression_table(
        [
            endpoint_row(_name, _coefficient)
            for _name, _coefficient in aem_integrated_parton_pieces.items()
        ],
        pagination=False,
    )
    _aem_paper_residual_table = expression_table(
        [
            endpoint_row(_name, _residual)
            for _name, _residual in aem_paper_residuals.items()
        ],
        pagination=False,
    )
    _aem_virtual_residual = (
        displayed_dy.ordinary_virtual - aem_virtual_laurent
    ).canonical(dy_context.z)
    _aem_soft_d1_residual = normalize_rational(
        displayed_dy.qq_historical_manuscript.d1_prefactor
        - aem_qq_dis_coefficient.d1_prefactor
    )
    assert _aem_virtual_residual.is_zero_for(dy_context.z)
    assert _aem_soft_d1_residual == 0
    _aem_shared_checks = expression_table(
        [
            {
                "shared check": (
                    "transcribed time-like virtual benchmark consistency"
                ),
                "residual": _aem_virtual_residual.delta,
            },
            {
                "shared check": (
                    "pre-correction LaTeX soft D1 after its PDF conversion"
                ),
                "residual": _aem_soft_d1_residual,
            },
        ],
        pagination=False,
    )
    _trace_oracle_rows = [
        {
            "check": f"transverse trace -> expanded oracle: {_graph_name}",
            "residual": _residual,
        }
        for _graph_name, _residual in dy_trace_residuals.items()
    ] + [
        {
            "check": f"longitudinal trace -> expanded oracle: {_piece_name}",
            "residual": _residual,
        }
        for _piece_name, _residual in dy_qg_ward_trace_residuals.items()
    ]
    _trace_oracle_table = expression_table(
        _trace_oracle_rows,
        pagination=False,
    )
    if full_audit is None:
        _audit_table = typst_md(
            "The exact master residuals are the cut-sector IBP identities."
        )
        _crossed_validation_table = typst_md(
            "The crossed-box residual is the sum of its cut-family identities."
        )
    else:
        _handoff = displayed_dy.master_handoff
        _audit_rows = [
            {
                "check": f"reduced numerator reconstruction: {name}",
                "residual": residual,
            }
            for name, residual in full_audit.numerator_reconstruction_residuals.items()
        ]
        for _label, _residuals in (
            ("virtual master coefficient", full_audit.virtual_expected_residuals),
            ("direct-box master coefficient", full_audit.direct_box_expected_residuals),
            ("qg master coefficient", full_audit.qg_expected_residuals),
            ("qg Ward master equality", full_audit.qg_ward_expected_residuals),
            ("crossed-box master coefficient", full_audit.crossed_box_expected_residuals),
        ):
            _audit_rows.extend(
                {"check": f"{_label}: {name}", "residual": residual}
                for name, residual in _residuals.items()
            )
        _audit_rows.extend(
            [
                {
                    "check": "qg Ward combination 2 triangle - box - bubble",
                    "residual": full_audit.qg_ward_cancellation_residual,
                },
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
                {
                    "check": (
                        "external-bubble analytic master through finite order"
                    ),
                    "residual": (
                        _handoff.external_bubble_expected_residual.delta
                    ),
                },
            ]
        )
        _endpoint_components = (
            "δ(1-z)",
            "𝒟₀(z)",
            "𝒟₁(z)",
            "ordinary",
        )
        for _power, _residual in _handoff.crossed_pole_residuals.items():
            _audit_rows.extend(
                {
                    "check": f"crossed all-cut epsilon^{_power}: {_component}",
                    "residual": _value,
                }
                for _component, _value in zip(
                    _endpoint_components,
                    _residual.canonical(dy_context.z).residuals(),
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
                _handoff.crossed_finite_residual
                .canonical(dy_context.z)
                .residuals(),
                strict=True,
            )
        )
        _audit_table = expression_table(
            _audit_rows,
            pagination=True,
            page_size=40,
        )
        _crossed_validation_table = expression_table(
            [
                endpoint_row(
                    "finite coefficient - crossed graph ledger",
                    _handoff.crossed_finite_residual.canonical(dy_context.z),
                )
            ],
            pagination=False,
        )

    mo.vstack(
        [
            typst_md("=== Exact trace simplification residuals"),
            _trace_oracle_table,
            typst_md("== Exact numerator, IBP, and master identities"),
            _audit_table,
            typst_md("== Crossed-box endpoint identity"),
            _crossed_validation_table,
            typst_md(r"""
            == Historical convention map

            This reference ledger records historical orientations and smooth
            convention maps.  The raw $q g$ cut sum can consequently appear
            with the reverse sign, while the $q bar(q)$ reconstruction includes
            two half-weighted external-bubble contributions and the smooth map
            $C(z) arrow z C(z)$.  These rows diagnose source conventions; they
            follow the already fixed native coefficient.
            """),
            expression_table(historical_reference_rows, pagination=False),
            expression_table(scheme_source_audit_rows, pagination=False),
            typst_md(r"""
            == Supporting AEM diagram and transcription tables

            These downstream rows transcribe reference coefficients and follow
            #link("https://inspirehep.net/literature/140456")[Altarelli, Ellis, and Martinelli, Nucl. Phys. B157 (1979) 461--497]
            (#link("https://doi.org/10.1016/0550-3213(79)90116-0")[DOI]).
            The two real $q bar(q)$ emission diagrams are assembled as two
            squares minus twice their interference, and the two crossed $q g$
            Compton diagrams as box, triangle interference, and bubble terms.
            With $m^2 = Q^2 = s+t+u$, their sums reproduce the kinematic
            content of paper Eqs. 77 and 85 before phase-space integration,
            in the common trace normalization and with couplings, color factors,
            and Born normalization divided out. This first
            identity retains generic $d$; the integration below then sets
            $d=4-2 epsilon$.
            """),
            _aem_kernel_table,
            _aem_kernel_residual_table,
            typst_md(r"""
            The next table transcribes the paper's phase-space-integrated
            Laurent coefficients and checks their algebraic combination.  The
            ledger itself is a transcription; the independent derivation of
            the real-emission and Compton entries from our kernels appears in
            the comparison below.  Its rows cover the Born, virtual,
            real-emission, and Compton contributions through paper Eqs. 75,
            88, 89, and the integrated result preceding Eq. 93.
            The DY diagrams alone retain initial-state collinear poles.  The
            explicitly displayed DIS rows subtract two quark densities or one
            gluon density, as defined by the paper's DIS diagrams, before
            reproducing its finite Eqs. 91 and 95.  The common
            dimensional-regularization factor is stripped in this ledger.

            The time-like virtual row supplies a source-transcription identity
            against the closed benchmark. The external-bubble row supplies the
            corresponding master-level identity in the main scheme-change
            diagnostic.
            """),
            _aem_integrated_table,
            typst_md("=== Exact paper-transcription and algebra residuals"),
            _aem_paper_residual_table,
            typst_md("=== Shared checks with the present notebook"),
            _aem_shared_checks,
        ]
    )
    return


if __name__ == "__main__":
    from calculations.dy.python.results import main as _results_main

    raise SystemExit(_results_main(app))
