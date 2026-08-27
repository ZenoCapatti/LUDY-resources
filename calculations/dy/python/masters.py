import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")

with app.setup(hide_code=True):
    from html import escape as _escape_html
    from inspect import cleandoc as _cleandoc
    import math
    import re as _re
    from threading import Lock as _Lock

    import marimo as _marimo
    from symbolica import E, S, Expression
    import typst as _typst

    _TYPST_FRAGMENT_CSS = r"""
    <style>
    .ludy-typst-fragment {
      color: inherit;
      display: inline-block;
      max-width: 100%;
      overflow-x: auto;
      vertical-align: middle;
    }
    .ludy-typst-fragment > p { margin: 0; }
    .ludy-typst-error {
      color: var(--error, #b00020);
      font-family: var(--monospace-font, ui-monospace, monospace);
      font-size: 0.875rem;
      white-space: pre-wrap;
    }
    </style>
    """

    def _typst_renderer_state():
        state = getattr(_typst, "_ludy_html_renderer_v2", None)
        if state is None:
            state = {
                "compiler": _typst.Compiler(ignore_system_fonts=True),
                "lock": _Lock(),
                "cache": {},
                "body_pattern": _re.compile(
                    r"<body(?:\s[^>]*)?>(.*?)</body>",
                    _re.DOTALL | _re.IGNORECASE,
                ),
                "head_pattern": _re.compile(
                    r"<head(?:\s[^>]*)?>(.*?)</head>",
                    _re.DOTALL | _re.IGNORECASE,
                ),
                "style_pattern": _re.compile(
                    r"<style(?:\s[^>]*)?>.*?</style>",
                    _re.DOTALL | _re.IGNORECASE,
                ),
                "heading_pattern": _re.compile(
                    r"<(/?)h([2-6])(?=[\s>])",
                    _re.IGNORECASE,
                ),
                "mathml_css": "",
            }
            setattr(_typst, "_ludy_html_renderer_v2", state)
        return state

    def typst_shared_css():
        state = _typst_renderer_state()
        return f'{state["mathml_css"]}{_TYPST_FRAGMENT_CSS}'

    def render_typst_html(
        source,
        *,
        font_size=15.0,
        prose=False,
        include_styles=True,
    ):
        """Compile one Typst fragment to themed prose or compact HTML."""

        if not isinstance(source, str):
            raise TypeError("Typst source must be a string")

        state = _typst_renderer_state()

        cleaned_source = _cleandoc(source)
        try:
            with state["lock"]:
                body = state["cache"].get(cleaned_source)
                if body is None:
                    compiled = state["compiler"].compile(
                        input=f"{cleaned_source}\n".encode("utf-8"),
                        format="html",
                    )
                    if not isinstance(compiled, bytes):
                        raise TypeError(
                            "Typst HTML export returned multiple outputs"
                        )
                    document = compiled.decode("utf-8")
                    body = state["body_pattern"].search(document)
                    if body is None:
                        raise ValueError(
                            "Typst HTML output did not contain a body"
                        )
                    head = state["head_pattern"].search(document)
                    mathml_css = (
                        ""
                        if head is None
                        else "".join(
                            state["style_pattern"].findall(head.group(1))
                        )
                    )
                    if mathml_css:
                        state["mathml_css"] = mathml_css
                    body = body.group(1)
                    state["cache"][cleaned_source] = body
                    if len(state["cache"]) > 512:
                        state["cache"].pop(next(iter(state["cache"])))
            styles = typst_shared_css() if include_styles else ""
            if prose:
                body = state["heading_pattern"].sub(
                    lambda match: (
                        f"<{match.group(1)}h{int(match.group(2)) - 1}"
                    ),
                    body,
                )
                return (
                    f"{styles}"
                    '<div class="markdown prose dark:prose-invert contents">'
                    f"{body}</div>"
                )

            size_style = (
                ""
                if font_size is None
                else f"font-size:{float(font_size):g}pt"
            )
            return (
                f"{styles}"
                f'<div class="ludy-typst-fragment" style="{size_style}">'
                f"{body}</div>"
            )
        except Exception as error:
            diagnostic = str(getattr(error, "diagnostic", None) or error)
            return (
                f"{_TYPST_FRAGMENT_CSS if include_styles else ''}"
                '<div class="ludy-typst-error" role="alert">'
                "<strong>Typst compilation failed</strong>"
                f"<pre>{_escape_html(diagnostic)}</pre>"
                "</div>"
            )

    def typst_html(source, *, font_size=15.0, prose=False):
        """Return one responsive Typst fragment as a Marimo HTML object."""

        return _marimo.Html(
            render_typst_html(source, font_size=font_size, prose=prose)
        )

    def typst_md(source):
        """Render Typst prose with Marimo's Markdown typography classes."""

        return typst_html(source, font_size=None, prose=True)

    def scalar_printer(*, latex: str, typst: str):
        """Build a display-only printer for a stable scalar name."""

        from symbolica import PrintMode

        def _print_scalar(_expression, mode, **_format_options):
            if mode == PrintMode.Latex:
                return latex
            if mode == PrintMode.Typst:
                return typst
            return None

        return _print_scalar

    _marimo.md = typst_md
    globals()["mo"] = _marimo


@app.cell(hide_code=True)
def _(E, Expression, mo):
    from html import escape as _escape_html

    def _typst_math(expression):
        return expression.to_typst()

    def _spenso_math_cell(expression, *, include_styles=True):
        return mo.Html(
            render_typst_html(
                f"$ {_typst_math(expression)} $",
                font_size=13.0,
                include_styles=include_styles,
            )
        )

    def _contains_expression(value):
        return isinstance(value, Expression) or (
            isinstance(value, (list, tuple))
            and any(_contains_expression(item) for item in value)
        )

    def _sequence_cell(values, *, include_styles=True):
        opening, closing = ("(", ")") if isinstance(values, tuple) else ("[", "]")
        parts = []
        for index, value in enumerate(values):
            if index:
                parts.append('<span aria-hidden="true">,</span>')
            if isinstance(value, Expression):
                parts.append(
                    _spenso_math_cell(
                        value,
                        include_styles=include_styles,
                    ).text
                )
            elif isinstance(value, (list, tuple)) and _contains_expression(value):
                parts.append(
                    _sequence_cell(
                        value,
                        include_styles=include_styles,
                    ).text
                )
            else:
                parts.append(f"<span>{_escape_html(str(value))}</span>")
        return mo.Html(
            '<div style="display: inline-flex; align-items: baseline; '
            'gap: 0.25rem; white-space: nowrap">'
            f"<span>{opening}</span>{''.join(parts)}<span>{closing}</span>"
            "</div>"
        )

    def _table_value(value, *, include_styles=True):
        if isinstance(value, Expression):
            return _spenso_math_cell(value, include_styles=include_styles)
        if isinstance(value, (list, tuple)) and _contains_expression(value):
            return _sequence_cell(value, include_styles=include_styles)
        return value

    def spenso_table(data, **kwargs):
        """Render exact expressions in one virtualized Marimo table.

        Typst and MathML styles are emitted once beside the table rather than
        serialized into every formatted cell. Nonessential table controls are
        disabled by default; callers can override every option explicitly.
        """

        if isinstance(data, dict):
            columns = tuple(data)
        elif isinstance(data, (list, tuple)) and all(
            isinstance(row, dict) for row in data
        ):
            columns = tuple(
                dict.fromkeys(column for row in data for column in row)
            )
        elif isinstance(data, (list, tuple)):
            columns = ("value",)
        else:
            columns = ()

        explicit_formatting = kwargs.pop("format_mapping", None) or {}
        automatic_formatting = {
            column: (
                lambda value: _table_value(value, include_styles=False)
            )
            for column in columns
        }
        kwargs.setdefault("selection", None)
        kwargs.setdefault("show_download", False)
        kwargs.setdefault("show_search", False)
        kwargs.setdefault("show_data_types", False)
        return mo.vstack(
            [
                mo.Html(typst_shared_css()),
                mo.ui.table(
                    data,
                    format_mapping={
                        **automatic_formatting,
                        **explicit_formatting,
                    },
                    **kwargs,
                ),
            ],
            gap=0,
        )

    _scalar_power_probe = _typst_math(1 / Expression.PI**2)
    _gamma_argument_probe = E("3/2-ep")
    _gamma_reciprocal_probe = _typst_math(
        1 / _gamma_argument_probe.gamma()
    )
    _gamma_square_probe = _typst_math(_gamma_argument_probe.gamma() ** 2)
    assert _scalar_power_probe == "frac(1,pi^2)"
    assert _gamma_reciprocal_probe == 'frac(1,Gamma(3/2-"ep"))'
    assert _gamma_square_probe == 'Gamma(3/2-"ep")^2'
    _scalar_power_mathml = render_typst_html(f"$ {_scalar_power_probe} $")
    _gamma_reciprocal_mathml = render_typst_html(
        f"$ {_gamma_reciprocal_probe} $"
    )
    _gamma_square_mathml = render_typst_html(f"$ {_gamma_square_probe} $")
    assert "<math" in _scalar_power_mathml
    assert "<mfrac>" in _gamma_reciprocal_mathml
    assert '<mi mathvariant="normal">Γ</mi>' in _gamma_reciprocal_mathml
    assert "<msup>" in _gamma_square_mathml
    assert '<mi mathvariant="normal">Γ</mi>' in _gamma_square_mathml
    return (spenso_table,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    = Analytic master integrals for the DY calculation

    This notebook isolates the closed-form master integrals used after the
    Kira/FIRE reduction.  It reconstructs their radial, light-cone, angular,
    Feynman-parameter, and Gram-determinant factors; checks the resulting
    expressions exactly with Symbolica; audits the physical normalization;
    expands them around $d = 4 - 2 epsilon$; and handles the leading virtuality
    and soft-endpoint distributions before providing a numerical evaluator.
    Exact expressions remain native Symbolica objects and are displayed with
    the same Spenso-aware Typst-to-MathML renderer used in `notebooks/ludy.py`.

    The definitions are faithful to
    #link("../mathematica/DY_calculation.nb")[DY_calculation.nb].  Opening or
    exporting this notebook never launches Kira and does not require a
    persisted `runs/` directory.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        "Physical 2π delta measures and historical Cutkosky signs are tracked "
        "separately. The derivations below keep both conventions explicit. "
        "Fractional powers use the principal symbolic branch; the numerical "
        "panel stays in a positive physical region.",
        kind="info",
    )
    return


@app.cell
def _(Expression, S):
    # Symbolica printer registration is global and one-shot.  Restart the
    # notebook kernel before deliberately rerunning this initialization cell.
    d = S("d")
    epsilon = S("eps")
    mu_squared = S(
        "mu_squared",
        print=scalar_printer(latex=r"\mu_R^2", typst="mu_R^2"),
    )
    p_squared = S(
        "psq",
        print=scalar_printer(latex=r"p^2", typst="p^2"),
    )
    s = S("s")
    mass_squared = S(
        "msq",
        print=scalar_printer(latex=r"m^2", typst="m^2"),
    )
    p1_squared = S(
        "p1sq",
        print=scalar_printer(latex=r"p_1^2", typst="p_1^2"),
    )
    p2_squared = S(
        "p2sq",
        print=scalar_printer(latex=r"p_2^2", typst="p_2^2"),
    )
    x = S("x")
    beta = S(
        "beta",
        print=scalar_printer(latex=r"\beta", typst="beta"),
    )
    kappa_squared = S(
        "kappasq",
        print=scalar_printer(
            latex=r"\kappa_\perp^2",
            typst="kappa_perp^2",
        ),
    )
    z = S("z")
    lambda_squared = S(
        "Lambdasq",
        print=scalar_printer(latex=r"\Lambda^2", typst="Lambda^2"),
    )
    s_lightcone = S(
        "sLC",
        print=scalar_printer(latex=r"Q", typst="Q"),
    )
    pi = Expression.PI
    euler_gamma = Expression.EULER_GAMMA
    return (
        beta,
        d,
        epsilon,
        euler_gamma,
        kappa_squared,
        lambda_squared,
        mass_squared,
        mu_squared,
        p1_squared,
        p2_squared,
        p_squared,
        pi,
        s,
        s_lightcone,
        x,
        z,
    )


@app.cell
def _(Expression):
    def canonical_zero(expression: Expression) -> Expression:
        """Normalize a rational expression for an exact zero comparison."""

        return expression.expand().together().cancel()

    return (canonical_zero,)


@app.function
def kallen(
    x: "Expression",
    y: "Expression",
    z: "Expression",
) -> "Expression":
    """Return the Källén polynomial λ(x,y,z)."""

    return x**2 + y**2 + z**2 - 2 * x * y - 2 * x * z - 2 * y * z


@app.function
def loop_normalization(
    mu_squared: "Expression",
    epsilon: "Expression",
    euler_gamma: "Expression",
) -> "Expression":
    """Retained MS-bar loop factor with the standard +gamma_E sign."""

    from symbolica import Expression as _Expression

    return (
        mu_squared * euler_gamma.exp() / (4 * _Expression.PI)
    ) ** epsilon


@app.function
def cut_normalization(
    mu_squared: "Expression",
    epsilon: "Expression",
    euler_gamma: "Expression",
) -> "Expression":
    """Closed-form factor after the explicit 4pi powers cancel."""

    return (mu_squared * euler_gamma.exp()) ** epsilon


@app.function
def sphere_volume(dimension: "Expression") -> "Expression":
    """Return the area of the unit sphere S^dimension."""

    from symbolica import Expression as _Expression

    return (
        2
        * _Expression.PI ** ((dimension + 1) / 2)
        / ((dimension + 1) / 2).gamma()
    )


@app.function
def apply_replacement_rules(
    expression: "Expression",
    rules: "tuple[tuple[Expression, Expression], ...]",
) -> "Expression":
    """Apply one simultaneous, non-repeating set of exact rules."""

    from symbolica import Replacement as _Replacement

    return expression.replace_multiple(
        [_Replacement(source, target) for source, target in rules],
        repeat=False,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Audit of `master_and_dump.pdf`

    The reusable master calculations are concentrated on PDF pages 1--3.
    Equation (7) gives the massive cut bubble.  The first triangle route ends
    at equation (25), while the independent transverse derivation in equations
    (31)--(37) exposes
    $kappa_perp^2 = x(1-x) p_1^2$ and reproduces the retained Mathematica
    master after the scheme conversion displayed below.

    Two inconsistencies in the draft are kept visible rather than silently
    resolved:

    - equation (25) is smaller than equation (37) by a factor of four;
    - pages 1--3 use $e^(-gamma_E)$, while the FLU formulas on pages 9--10
      and the Mathematica snapshot use $e^(+gamma_E)$.

    The notebook therefore uses equation (37) and the retained
    $e^(+gamma_E)$ convention.  The printed leading-$p_1^2$ triangle
    retaining $p_2^2$ is not copied because its equations (42)--(46) omit a
    required $sqrt(s)$; a new exact two-virtuality light-cone extension is
    derived below.  The
    later maximal-box, LU, zero-bin, and FLU notes mostly remain context.  The
    completed four-line endpoint factor is isolated below as the boundary
    master `M00`.
    """)
    return


@app.cell
def _(epsilon, euler_gamma, mo, spenso_table):
    source_audit_rows = (
        {
            "PDF pages": "1",
            "equations": "(1)--(7)",
            "content": "massive cut bubble",
            "status": "complete; retained shape",
        },
        {
            "PDF pages": "1--2",
            "equations": "(8)--(25)",
            "content": "cut triangle, angular route",
            "status": "factor 1/4 relative to the retained result",
        },
        {
            "PDF pages": "2--3",
            "equations": "(28)--(37)",
            "content": "cut triangle, transverse route",
            "status": "complete; matches after the displayed scheme conversion",
        },
        {
            "PDF pages": "3",
            "equations": "(38)--(46)",
            "content": "leading-p₁² triangle retaining p₂²",
            "status": "missing √s; a new exact extension is derived below",
        },
        {
            "PDF pages": "3--11",
            "equations": "(47)--(147)",
            "content": "maximal box, LU, zero-bin, FLU",
            "status": "direct endpoint retained as M00; remaining notes are context",
        },
    )
    _scheme_conversion = (-2 * epsilon * euler_gamma).exp()
    mo.vstack(
        [
            mo.ui.table(source_audit_rows, pagination=False),
            spenso_table(
                [
                    {
                        "conversion": "early-PDF / retained scheme",
                        "factor": _scheme_conversion,
                    }
                ],
                pagination=False,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Normalization ledger

    The physical phase-space convention is

    $
      integral frac(upright(d)^d k, (2 pi)^d), quad
      hat(delta)_plus.minus(q^2-m^2)
      = 2 pi theta(plus.minus q^0) delta(q^2-m^2), quad
      integral frac(upright(d) p_i^2, 2 pi).
    $

    Consequently a one-loop object with $N_c$ real cut edges and $N_v$
    virtuality integrations carries
    $(2 pi)^(N_c-d-N_v)$ before angular and delta-function Jacobians.
    Spin and colour averages remain observable-dependent prefactors and are
    not folded into a scalar master.  DIS receives the additional $1/(4 pi)$
    factor recorded in PDF equations (125) and (132).

    The early PDF master pages instead write $(2 pi i)^(N_c)$.  Its $i^2$
    explains the negative double-cut bubble; that Cutkosky phase is not a
    negative phase-space Jacobian.  The notebook therefore derives a positive
    real phase space first and applies the retained historical master sign
    separately.
    """)
    return


@app.cell
def _(d, pi, spenso_table):
    normalization_ledger = (
        {
            "object": "one-loop cut bubble",
            "loops": 1,
            "cut edges": 2,
            "virtuality integrals": 0,
            "2π factor": (2 * pi) ** (2 - d),
        },
        {
            "object": "one-loop cut triangle",
            "loops": 1,
            "cut edges": 3,
            "virtuality integrals": 0,
            "2π factor": (2 * pi) ** (3 - d),
        },
        {
            "object": "triangle + one pᵢ² integral",
            "loops": 1,
            "cut edges": 3,
            "virtuality integrals": 1,
            "2π factor": (2 * pi) ** (2 - d),
        },
        {
            "object": "triangle + two pᵢ² integrals",
            "loops": 1,
            "cut edges": 3,
            "virtuality integrals": 2,
            "2π factor": (2 * pi) ** (1 - d),
        },
        {
            "object": "cross-box cut + two pᵢ² integrals",
            "loops": 1,
            "cut edges": 4,
            "virtuality integrals": 2,
            "2π factor": (2 * pi) ** (2 - d),
        },
        {
            "object": "DIS-only observable factor",
            "loops": 0,
            "cut edges": 0,
            "virtuality integrals": 0,
            "2π factor": 1 / (4 * pi),
        },
    )
    spenso_table(normalization_ledger, pagination=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Light-cone derivations interleaved with the master definitions

    Choose null reference vectors $n_+$ and $n_-$ with
    $n_+^2=n_-^2=0$ and $2 n_+ dot n_-=Q$.  Every loop momentum is written as

    $
      k = alpha n_+ + beta n_- + k_perp, quad
      kappa_perp^2 equiv -k_perp^2 >= 0,
    $

    so that

    $
      k^2 = Q alpha beta-kappa_perp^2, quad
      upright(d)^d k = frac(Q,2)
        upright(d) alpha upright(d) beta upright(d)^(d-2)k_perp.
    $

    Each master below starts from this decomposition.  The accompanying code
    uses exact Symbolica replacement rules—simultaneously for independent
    substitutions and in stages for dependent cut solutions—and asserts an
    exact zero residual against the implementation.  The theta-function support
    is stated in prose because it is not encoded by an algebraic replacement
    rule.  Every closed-form cut comparison first imposes
    $d=4-2epsilon$; the public functions retain both arguments so that this
    dimensional-regularization slice stays visible at each call site.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Master 1 — uncut massless bubble $B(p^2)$

    Start from

    $
      B(p^2) = frac(overline(S)_epsilon,i)
      integral frac(upright(d)^d k, (2 pi)^d)
      frac(1, k^2 (k-p)^2).
    $

    The factor $1/i$ strips the conventional overall Minkowski phase, matching
    the real historical master returned by the function below.

    First make the light-front contour explicit.  Choose $p_perp=0$, set
    $k^+=x p^+$ and $p^+p^-=p^2$.  The two denominators are

    $
      D_0=x p^+ k^- - kappa_perp^2 + i 0, quad
      D_1=(1-x)p^+(p^- - k^-)-kappa_perp^2+i 0.
    $

    The $D_0$ pole is $k^-_*=kappa_perp^2/(x p^+)$, and its replacement in
    the second denominator gives

    $
      k^-=k^-_* quad => quad D_1
      = frac(x(1-x)p^2-kappa_perp^2,x).
    $

    Only $0<x<1$ puts the two poles on opposite sides of the contour.  The
    $k^-$ residue leaves a transverse integral.  The following equivalent
    Feynman-parameter route evaluates the same contour result:

    $
      frac(1,k^2(k-p)^2)
      = integral_0^1 upright(d) x
        [x k^2+(1-x)(k-p)^2]^(-2).
    $

    The exact shift $k=ell+(1-x)p$ is applied below as a simultaneous pair of
    rules for $k^2$ and $k dot p$; it turns the denominator into
    $ell^2+x(1-x)p^2$.  Decomposing $ell$ in the null basis above and performing
    the longitudinal contour and transverse radial integral yields

    $
      integral upright(d)^d ell [ell^2+x(1-x)p^2]^(-2)
      = pi^(d/2) Gamma(2-d/2)
        [-x(1-x)p^2]^(d/2-2).
    $

    The remaining parameter integral is

    $
      integral_0^1 upright(d) x [x(1-x)]^(d/2-2)
      = frac(Gamma((d-2)/2)^2, Gamma(d-2)).
    $

    This is the uncut counterpart of the delta-supported derivations below;
    the light-cone energy integrations are contour integrals rather than
    on-shell replacements.
    """)
    return


@app.function
def uncut_bubble(
    momentum_squared: "Expression",
    *,
    dimension: "Expression",
    epsilon: "Expression",
    mu_squared: "Expression",
    euler_gamma: "Expression",
) -> "Expression":
    """Massless uncut bubble B(p²) in the Mathematica normalization."""

    from symbolica import Expression as _Expression

    pi = _Expression.PI
    return (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        / (2 * pi) ** dimension
        * pi ** (dimension / 2)
        * ((dimension - 2) / 2).gamma() ** 2
        * ((4 - dimension) / 2).gamma()
        / (dimension - 2).gamma()
        * (-momentum_squared) ** ((dimension - 4) / 2)
    )


@app.cell
def _(
    S,
    apply_replacement_rules,
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    kappa_squared,
    mu_squared,
    p_squared,
    pi,
    spenso_table,
    x,
):
    _lc_p_plus, _lc_k_minus = S("lc_p_plus", "lc_k_minus")
    _first_lightfront_denominator = (
        x * _lc_p_plus * _lc_k_minus - kappa_squared
    )
    _second_lightfront_denominator = (
        (1 - x)
        * _lc_p_plus
        * (p_squared / _lc_p_plus - _lc_k_minus)
        - kappa_squared
    )
    _k_minus_pole = kappa_squared / (x * _lc_p_plus)
    assert canonical_zero(
        apply_replacement_rules(
            _first_lightfront_denominator,
            ((_lc_k_minus, _k_minus_pole),),
        )
    ) == 0
    _second_on_pole = canonical_zero(
        apply_replacement_rules(
            _second_lightfront_denominator,
            ((_lc_k_minus, _k_minus_pole),),
        )
    )
    _pole_residual = canonical_zero(
        x * _second_on_pole
        - x * (1 - x) * p_squared
        + kappa_squared
    )
    assert _pole_residual == 0

    _lc_k_squared, _lc_k_dot_p, _lc_ell_squared, _lc_ell_dot_p = S(
        "lc_k_squared",
        "lc_k_dot_p",
        "lc_ell_squared",
        "lc_ell_dot_p",
    )
    _combined_denominator = (
        x * _lc_k_squared
        + (1 - x)
        * (_lc_k_squared - 2 * _lc_k_dot_p + p_squared)
    )
    _shift_rules = (
        (
            _lc_k_squared,
            _lc_ell_squared
            + 2 * (1 - x) * _lc_ell_dot_p
            + (1 - x) ** 2 * p_squared,
        ),
        (
            _lc_k_dot_p,
            _lc_ell_dot_p + (1 - x) * p_squared,
        ),
    )
    _shifted_denominator = canonical_zero(
        apply_replacement_rules(_combined_denominator, _shift_rules)
    )
    assert canonical_zero(
        _shifted_denominator
        - _lc_ell_squared
        - x * (1 - x) * p_squared
    ) == 0

    _parameter_integral = (
        ((d - 2) / 2).gamma() ** 2 / (d - 2).gamma()
    )
    _loop_integral = (
        pi ** (d / 2)
        * ((4 - d) / 2).gamma()
        * (-p_squared) ** ((d - 4) / 2)
    )
    _derived_bubble = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        / (2 * pi) ** d
        * _loop_integral
        * _parameter_integral
    )
    _bubble_residual = canonical_zero(
        _derived_bubble
        - uncut_bubble(
            p_squared,
            dimension=d,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        )
    )
    assert _bubble_residual == 0
    spenso_table(
        [
            {"step": "D₀ light-front pole", "value": _k_minus_pole},
            {"step": "D₁ on the D₀ pole", "value": _second_on_pole},
            {"step": "pole residual", "value": _pole_residual},
            {"step": "combined denominator", "value": _combined_denominator},
            {"step": "after k=ℓ+(1-x)p rules", "value": _shifted_denominator},
            {"step": "light-cone/radial loop factor", "value": _loop_integral},
            {"step": "x beta integral", "value": _parameter_integral},
            {"step": "definition residual", "value": _bubble_residual},
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Master 2 — massless cut bubble $B_(upright("cut"))(P^2)$

    Put $P=n_++n_-$, so $Q=P^2$, and decompose
    $k=x n_+ + beta n_- + k_perp$.  The two real-cut constraints are

    $
      C_0 = Q x beta-kappa_perp^2, quad
      C_1 = Q(1-x)(1-beta)-kappa_perp^2.
    $

    The first delta gives $beta=kappa_perp^2/(Q x)$.  Applying that rule to
    $C_1$ gives

    $
      C_0=0 quad => quad C_1
      = Q(1-x)-frac(kappa_perp^2,x), quad
      kappa_perp^2=Q x(1-x).
    $

    The positive-energy branch has $0<x<1$.  The two longitudinal delta
    Jacobians and the angular integral leave

    $
      frac(Omega_(d-3),4) (P^2)^((d-4)/2)
      integral_0^1 upright(d)x [x(1-x)]^((d-4)/2).
    $

    With $d=4-2epsilon$, the beta integral and the duplication identity for
    $Gamma(2-2epsilon)$ produce the closed form below.  No rest-frame energy
    variable is needed.
    """)
    return


@app.function
def massless_cut_bubble(
    momentum_squared: "Expression",
    *,
    dimension: "Expression",
    epsilon: "Expression",
    mu_squared: "Expression",
    euler_gamma: "Expression",
) -> "Expression":
    """Massless cut bubble Bcut(p²)."""

    from symbolica import E as _E
    from symbolica import Expression as _Expression

    two_power = (-dimension).expand()
    pi_power = (_E("7/2") - dimension - 2 * epsilon).expand()
    return (
        cut_normalization(mu_squared, epsilon, euler_gamma)
        * 2**two_power
        * momentum_squared ** (-epsilon)
        * _Expression.PI**pi_power
        / (_E("3/2") - epsilon).gamma()
    )


@app.cell
def _(
    E,
    apply_replacement_rules,
    beta,
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    kappa_squared,
    mu_squared,
    p_squared,
    pi,
    spenso_table,
    x,
):
    _first_cut = p_squared * x * beta - kappa_squared
    _second_cut = (
        p_squared * (1 - x) * (1 - beta) - kappa_squared
    )
    _beta_solution = kappa_squared / (p_squared * x)
    _second_cut_reduced = canonical_zero(
        apply_replacement_rules(
            _second_cut,
            ((beta, _beta_solution),),
        )
    )
    _kappa_solution = p_squared * x * (1 - x)
    assert canonical_zero(
        _second_cut_reduced
        - p_squared * (1 - x)
        + kappa_squared / x
    ) == 0
    assert canonical_zero(
        apply_replacement_rules(
            _second_cut_reduced,
            ((kappa_squared, _kappa_solution),),
        )
    ) == 0

    _dimensionally_regularized = 4 - 2 * epsilon
    _parameter_integral = (
        ((_dimensionally_regularized - 2) / 2).gamma() ** 2
        / (_dimensionally_regularized - 2).gamma()
    )
    _raw_lightcone_measure = (
        sphere_volume(_dimensionally_regularized - 3)
        / 4
        * p_squared ** ((_dimensionally_regularized - 4) / 2)
        * _parameter_integral
    )
    _positive_lightcone_cut = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * (2 * pi) ** (2 - _dimensionally_regularized)
        * _raw_lightcone_measure
    )
    _finite_geometry_residual = canonical_zero(
        _positive_lightcone_cut.replace(epsilon, 0) - 1 / (8 * pi)
    )
    assert _finite_geometry_residual == 0

    _beta_integral_dimreg = (
        (1 - epsilon).gamma() ** 2
        / (2 - 2 * epsilon).gamma()
    )
    _gamma_one_minus_epsilon = (
        (_dimensionally_regularized - 2) / 2
    ).gamma()
    _gamma_duplication_rhs = (
        2 ** (1 - 2 * epsilon)
        / pi.sqrt()
        * (1 - epsilon).gamma()
        * (E("3/2") - epsilon).gamma()
    )
    _beta_after_duplication = canonical_zero(
        apply_replacement_rules(
            _beta_integral_dimreg,
            (((2 - 2 * epsilon).gamma(), _gamma_duplication_rhs),),
        )
    )
    _duplication_residual = canonical_zero(
        _beta_after_duplication
        - 2 ** (2 * epsilon - 1)
        * pi.sqrt()
        * (1 - epsilon).gamma()
        / (E("3/2") - epsilon).gamma()
    )
    assert _duplication_residual == 0

    _raw_gamma_duplication_rhs = (
        2 ** (1 - 2 * epsilon)
        / pi.sqrt()
        * _gamma_one_minus_epsilon
        * (E("3/2") - epsilon).gamma()
    )

    _positive_branch_rules = (
        (
            loop_normalization(mu_squared, epsilon, euler_gamma),
            cut_normalization(mu_squared, epsilon, euler_gamma)
            * 2 ** (-2 * epsilon)
            * pi ** (-epsilon),
        ),
        (
            (2 * pi) ** (2 - _dimensionally_regularized),
            2 ** (2 - _dimensionally_regularized)
            * pi ** (2 - _dimensionally_regularized),
        ),
        (
            (_dimensionally_regularized - 2).gamma(),
            _raw_gamma_duplication_rhs,
        ),
    )
    _closed_from_raw_lightcone = canonical_zero(
        apply_replacement_rules(
            _positive_lightcone_cut,
            _positive_branch_rules,
        )
    )
    _definition_residual = canonical_zero(
        _closed_from_raw_lightcone
        - massless_cut_bubble(
            p_squared,
            dimension=_dimensionally_regularized,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        )
    )
    assert _definition_residual == 0
    spenso_table(
        [
            {"step": "C₀", "value": _first_cut},
            {"step": "β rule", "value": _beta_solution},
            {"step": "C₁ after β rule", "value": _second_cut_reduced},
            {"step": "κ⊥² rule", "value": _kappa_solution},
            {"step": "raw light-cone measure", "value": _raw_lightcone_measure},
            {"step": "normalized light-cone cut", "value": _positive_lightcone_cut},
            {"step": "beta integral after Γ duplication", "value": _beta_after_duplication},
            {"step": "Γ-duplication residual", "value": _duplication_residual},
            {"step": "four-dimensional normalization residual", "value": _finite_geometry_residual},
            {"step": "after dim-reg and Γ rules", "value": _closed_from_raw_lightcone},
            {"step": "definition residual", "value": _definition_residual},
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Master 3 — massless cut triangle

    Retain both external virtualities in the light-cone parametrization

    $
      p_1=n_+ + frac(p_1^2,Q)n_-, quad
      p_2=n_- + frac(p_2^2,Q)n_+.
    $

    With $P=p_1+p_2$, the first two cut equations again fix $beta$ and
    $kappa_perp^2$.  The third massless cut fixes

    $
      J_3 = Q-frac(p_1^2p_2^2,Q), quad
      x_* = frac(Q+p_2^2,J_3),
    $

    and the exact identities are

    $
      J_3^2=lambda(P^2,p_1^2,p_2^2), quad
      R_perp^2=p_1^2 x_*(1-x_*)
      =-frac(p_1^2p_2^2P^2,J_3^2).
    $

    Here $p_3^2$ is the signed crossed argument of the historical master.  In
    the DY use $T_(upright("cut"))(p_1^2,p_2^2,-s)$, the replacement
    $P^2 -> p_3^2$ analytically continues the future-directed branch
    $P^2 approx +s$ to $p_3^2=-s$; that sign change is crossing, not a
    leading-virtuality approximation.  The leading-power step is the subsequent
    Gram projection.  The explicit rules are

    $
      P^2 -> p_3^2, quad
      J_3^2 -> lambda(0,0,p_3^2), quad
      R_perp^2 ->
        -frac(p_1^2p_2^2p_3^2,lambda(0,0,p_3^2)).
    $

    Applying them to
    $Omega_(d-3) R_perp^(d-4)/(4 J_3)$ gives the definition below.  The
    displayed branch assumes $J_3>0$, $0<x_*<1$, and positive-energy cut
    support; elsewhere the Jacobian requires an absolute value or analytic
    continuation.
    """)
    return


@app.function
def massless_cut_triangle(
    p1_squared: "Expression",
    p2_squared: "Expression",
    p3_squared: "Expression",
    *,
    dimension: "Expression",
    epsilon: "Expression",
    mu_squared: "Expression",
    euler_gamma: "Expression",
) -> "Expression":
    """Massless cut triangle Tcut(p1²,p2²,p3²)."""

    from symbolica import E as _E
    from symbolica import Expression as _Expression

    two_power = (2 - dimension - 2 * epsilon).expand()
    pi_power = (4 - dimension - 2 * epsilon).expand()
    kallen_power = (_E("1/2") - epsilon).expand()
    return (
        cut_normalization(mu_squared, epsilon, euler_gamma)
        * 2**two_power
        * (-p1_squared * p2_squared * p3_squared) ** (-epsilon)
        / kallen(0, 0, p3_squared) ** kallen_power
        * _Expression.PI**pi_power
        / (1 - epsilon).gamma()
    )


@app.cell
def _(
    E,
    S,
    apply_replacement_rules,
    canonical_zero,
    epsilon,
    euler_gamma,
    mu_squared,
    p1_squared,
    p2_squared,
    p_squared,
    pi,
    s_lightcone,
    spenso_table,
):
    _pair_invariant = (
        s_lightcone
        + p1_squared
        + p2_squared
        + p1_squared * p2_squared / s_lightcone
    )
    _third_jacobian = (
        s_lightcone - p1_squared * p2_squared / s_lightcone
    )
    _x_solution = (s_lightcone + p2_squared) / _third_jacobian
    _exact_radius_squared = p1_squared * _x_solution * (1 - _x_solution)
    _jacobian_residual = canonical_zero(
        _third_jacobian**2
        - kallen(_pair_invariant, p1_squared, p2_squared)
    )
    _radius_residual = canonical_zero(
        _exact_radius_squared
        + p1_squared
        * p2_squared
        * _pair_invariant
        / _third_jacobian**2
    )
    assert _jacobian_residual == 0
    assert _radius_residual == 0

    _pair_slot, _jacobian_squared_slot = S(
        "lc_massless_pair_slot",
        "lc_massless_jacobian_squared_slot",
    )
    _radius_template = (
        -p1_squared
        * p2_squared
        * _pair_slot
        / _jacobian_squared_slot
    )
    _historical_kallen = kallen(0, 0, p_squared)
    _leading_radius_squared = canonical_zero(
        apply_replacement_rules(
            _radius_template,
            (
                (_pair_slot, p_squared),
                (_jacobian_squared_slot, _historical_kallen),
            ),
        )
    )
    assert canonical_zero(
        _leading_radius_squared
        + p1_squared * p2_squared * p_squared / _historical_kallen
    ) == 0

    _dimensionally_regularized = 4 - 2 * epsilon
    _raw_historical_triangle = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * (2 * pi) ** (3 - _dimensionally_regularized)
        * sphere_volume(_dimensionally_regularized - 3)
        / (4 * _historical_kallen.sqrt())
        * _leading_radius_squared ** (-epsilon)
    )
    _positive_branch_rules = (
        (
            loop_normalization(mu_squared, epsilon, euler_gamma),
            cut_normalization(mu_squared, epsilon, euler_gamma)
            * 2 ** (-2 * epsilon)
            * pi ** (-epsilon),
        ),
        (
            (2 * pi) ** (3 - _dimensionally_regularized),
            2 ** (3 - _dimensionally_regularized)
            * pi ** (3 - _dimensionally_regularized),
        ),
        (
            ((_dimensionally_regularized - 2) / 2).gamma(),
            (1 - epsilon).gamma(),
        ),
        (
            _leading_radius_squared ** (-epsilon),
            (-p1_squared * p2_squared * p_squared) ** (-epsilon)
            * _historical_kallen**epsilon,
        ),
    )
    _closed_from_raw_lightcone = canonical_zero(
        apply_replacement_rules(
            _raw_historical_triangle,
            _positive_branch_rules,
        )
    )
    _definition_residual = canonical_zero(
        _closed_from_raw_lightcone
        - massless_cut_triangle(
            p1_squared,
            p2_squared,
            p_squared,
            dimension=_dimensionally_regularized,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        )
    )
    assert _definition_residual == 0
    spenso_table(
        [
            {"step": "exact P²", "value": _pair_invariant},
            {"step": "exact J₃", "value": _third_jacobian},
            {"step": "J₃²-λ residual", "value": _jacobian_residual},
            {"step": "x*", "value": _x_solution},
            {"step": "radius residual", "value": _radius_residual},
            {"step": "LP replacement for R⊥²", "value": _leading_radius_squared},
            {"step": "raw crossed light-cone measure", "value": _raw_historical_triangle},
            {"step": "after dim-reg and branch rules", "value": _closed_from_raw_lightcone},
            {"step": "definition residual", "value": _definition_residual},
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Master 4 — massive cut bubble $B_(upright("cutm"))(s,m^2)$

    Use $P=n_++n_-$ with $P^2=s$ and the same loop decomposition.  The two
    cuts are

    $
      C_0=s x beta-kappa_perp^2, quad
      C_m=s(1-x)(1-beta)-kappa_perp^2-m^2.
    $

    Applying $beta=kappa_perp^2/(s x)$ reduces the massive cut to

    $
      C_0=0 quad => quad C_m
      =s(1-x)-frac(kappa_perp^2,x)-m^2,
    $

    and hence

    $
      kappa_perp^2=x[s(1-x)-m^2].
    $

    Its positive support is $0<x<x_*$ with $x_*=1-m^2/s$.  Rescaling
    $x=x_* y$ exposes the standard two-body radius:

    $
      kappa_perp^2=4 r_*^2 y(1-y), quad
      r_* = frac(s-m^2,2 sqrt(s)), quad 0<y<1.
    $

    The beta integral therefore reconstructs the angular orbit
    $Omega_(d-2)r_*^(d-3)$ and gives the positive real two-body phase space.
    The definition below adds the retained historical Cutkosky minus sign;
    that sign is not part of the light-cone Jacobian.
    """)
    return


@app.function
def massive_cut_bubble(
    momentum_squared: "Expression",
    mass_squared: "Expression",
    *,
    dimension: "Expression",
    epsilon: "Expression",
    mu_squared: "Expression",
    euler_gamma: "Expression",
) -> "Expression":
    """Massive cut bubble Bcutm(s,m²)."""

    from symbolica import Expression as _Expression

    cut_radius = (
        (momentum_squared - mass_squared)
        / (2 * momentum_squared.sqrt())
    )
    gamma_argument = ((dimension - 1) / 2).expand()
    radial_power = (dimension - 3).expand()
    return -(
        cut_normalization(mu_squared, epsilon, euler_gamma)
        / (
            8
            * _Expression.PI.sqrt()
            * gamma_argument.gamma()
            * momentum_squared.sqrt()
        )
        * cut_radius ** radial_power
    )


@app.cell
def _(
    E,
    S,
    apply_replacement_rules,
    beta,
    canonical_zero,
    epsilon,
    euler_gamma,
    kappa_squared,
    mass_squared,
    mu_squared,
    pi,
    s,
    spenso_table,
    x,
):
    _first_cut = s * x * beta - kappa_squared
    _massive_cut = s * (1 - x) * (1 - beta) - kappa_squared - mass_squared
    _beta_solution = kappa_squared / (s * x)
    _massive_cut_reduced = canonical_zero(
        apply_replacement_rules(
            _massive_cut,
            ((beta, _beta_solution),),
        )
    )
    _kappa_solution = x * (s * (1 - x) - mass_squared)
    assert canonical_zero(
        _massive_cut_reduced
        - s * (1 - x)
        + kappa_squared / x
        + mass_squared
    ) == 0
    assert canonical_zero(
        apply_replacement_rules(
            _massive_cut_reduced,
            ((kappa_squared, _kappa_solution),),
        )
    ) == 0

    _y = S("lc_massive_bubble_y")
    _x_endpoint = 1 - mass_squared / s
    _cut_radius = (s - mass_squared) / (2 * s.sqrt())
    _rescaled_radius = canonical_zero(
        apply_replacement_rules(
            _kappa_solution,
            ((x, _x_endpoint * _y),),
        )
    )
    _rescaling_residual = canonical_zero(
        _rescaled_radius - 4 * _cut_radius**2 * _y * (1 - _y)
    )
    assert _rescaling_residual == 0

    _dimensionally_regularized = 4 - 2 * epsilon
    _positive_phase_space = (
        sphere_volume(_dimensionally_regularized - 2)
        / 4
        * (2 * pi) ** (2 - _dimensionally_regularized)
        / s.sqrt()
        * _cut_radius ** (_dimensionally_regularized - 3)
    )
    _positive_normalized_phase_space = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * _positive_phase_space
    )
    _positive_branch_rules = (
        (
            loop_normalization(mu_squared, epsilon, euler_gamma),
            cut_normalization(mu_squared, epsilon, euler_gamma)
            * 2 ** (-2 * epsilon)
            * pi ** (-epsilon),
        ),
        (
            (2 * pi) ** (2 - _dimensionally_regularized),
            2 ** (2 - _dimensionally_regularized)
            * pi ** (2 - _dimensionally_regularized),
        ),
        (
            ((_dimensionally_regularized - 1) / 2).gamma(),
            (E("3/2") - epsilon).gamma(),
        ),
    )
    _closed_from_raw_lightcone = -canonical_zero(
        apply_replacement_rules(
            _positive_normalized_phase_space,
            _positive_branch_rules,
        )
    )
    _definition_residual = canonical_zero(
        _closed_from_raw_lightcone
        - massive_cut_bubble(
            s,
            mass_squared,
            dimension=_dimensionally_regularized,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        )
    )
    assert _definition_residual == 0
    spenso_table(
        [
            {"step": "C₀", "value": _first_cut},
            {"step": "Cₘ after β rule", "value": _massive_cut_reduced},
            {"step": "κ⊥² rule", "value": _kappa_solution},
            {"step": "x endpoint", "value": _x_endpoint},
            {"step": "rescaled κ⊥²", "value": _rescaled_radius},
            {"step": "rescaling residual", "value": _rescaling_residual},
            {"step": "positive two-body phase space", "value": _positive_phase_space},
            {"step": "normalized positive phase space", "value": _positive_normalized_phase_space},
            {"step": "after dim-reg rules and historical sign", "value": _closed_from_raw_lightcone},
            {"step": "historical-sign definition residual", "value": _definition_residual},
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Master 5 — massive cut triangle $T_(upright("cutm"))(p_1^2,Q,m^2)$

    Here the historical second argument is the light-cone scale
    $Q=2p_1 dot p_2$, with $p_2^2=0$ for this master.  Write

    $
      p_1=n_+ + frac(p_1^2,Q)n_-, quad p_2=n_-, quad
      k=x n_+ + beta n_- + k_perp.
    $

    For the routing used by the notebook, the three cut constraints are

    $
      C_0=Q x beta-kappa_perp^2, \
      C_1=(1-x)(p_1^2-Q beta)-kappa_perp^2, \
      C_m=Q(1-x)(1+p_1^2/Q-beta)-kappa_perp^2-m^2.
    $

    They are solved in stages:

    $
      beta -> frac(kappa_perp^2,Q x), quad
      kappa_perp^2 -> x(1-x)p_1^2, quad
      x -> 1-frac(m^2,Q).
    $

    Consequently

    $
      R_perp^2 = frac(p_1^2(Q-m^2)m^2,Q^2), quad
      J_(upright("long"))=frac(1,2Q).
    $

    The transverse orbit is
    $Omega_(d-3)(R_perp^2)^((d-4)/2)$ and yields the definition below after
    the three cut-edge factors are included.  The supported branch has
    $Q>m^2>0$, $0<x<1$, and $R_perp^2>=0$.  Notice that $Q$ is not the exact
    $(p_1+p_2)^2$ when $p_1^2$ is retained.
    """)
    return


@app.function
def massive_cut_triangle(
    external_virtuality: "Expression",
    momentum_squared: "Expression",
    mass_squared: "Expression",
    *,
    dimension: "Expression",
    epsilon: "Expression",
    mu_squared: "Expression",
    euler_gamma: "Expression",
) -> "Expression":
    """Massive cut triangle with historical s = 2 p1·p2."""

    gram_factor = (
        external_virtuality
        * (momentum_squared - mass_squared)
        * mass_squared
    )
    gamma_argument = ((dimension - 2) / 2).expand()
    momentum_power = (dimension - 3).expand()
    gram_power = ((dimension - 4) / 2).expand()
    return (
        cut_normalization(mu_squared, epsilon, euler_gamma)
        / (
            4
            * gamma_argument.gamma()
            * momentum_squared ** momentum_power
        )
        * gram_factor ** gram_power
    )


@app.cell
def _(
    apply_replacement_rules,
    beta,
    canonical_zero,
    epsilon,
    euler_gamma,
    kappa_squared,
    mass_squared,
    mu_squared,
    p1_squared,
    pi,
    s_lightcone,
    spenso_table,
    x,
):
    _first_cut = s_lightcone * x * beta - kappa_squared
    _second_cut = (
        (1 - x) * (p1_squared - s_lightcone * beta)
        - kappa_squared
    )
    _massive_cut = (
        s_lightcone
        * (1 - x)
        * (1 + p1_squared / s_lightcone - beta)
        - kappa_squared
        - mass_squared
    )
    _beta_solution = kappa_squared / (s_lightcone * x)
    _second_cut_reduced = canonical_zero(
        apply_replacement_rules(
            _second_cut,
            ((beta, _beta_solution),),
        )
    )
    _kappa_solution = x * (1 - x) * p1_squared
    _massive_after_beta = canonical_zero(
        apply_replacement_rules(
            _massive_cut,
            ((beta, _beta_solution),),
        )
    )
    _massive_after_kappa = canonical_zero(
        apply_replacement_rules(
            _massive_after_beta,
            ((kappa_squared, _kappa_solution),),
        )
    )
    _x_solution = 1 - mass_squared / s_lightcone
    assert canonical_zero(
        _second_cut_reduced
        - (1 - x) * p1_squared
        + kappa_squared / x
    ) == 0
    assert canonical_zero(
        _massive_after_kappa
        - (s_lightcone * (1 - x) - mass_squared)
    ) == 0
    assert canonical_zero(
        apply_replacement_rules(
            _massive_after_kappa,
            ((x, _x_solution),),
        )
    ) == 0

    _radius_squared = canonical_zero(
        apply_replacement_rules(
            _kappa_solution,
            ((x, _x_solution),),
        )
    )
    _gram_factor = p1_squared * (s_lightcone - mass_squared) * mass_squared
    _radius_residual = canonical_zero(
        _radius_squared - _gram_factor / s_lightcone**2
    )
    assert _radius_residual == 0

    _dimensionally_regularized = 4 - 2 * epsilon
    _raw_lightcone_triangle = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * (2 * pi) ** (3 - _dimensionally_regularized)
        * sphere_volume(_dimensionally_regularized - 3)
        / (4 * s_lightcone)
        * _radius_squared ** (-epsilon)
    )
    _positive_branch_rules = (
        (
            loop_normalization(mu_squared, epsilon, euler_gamma),
            cut_normalization(mu_squared, epsilon, euler_gamma)
            * 2 ** (-2 * epsilon)
            * pi ** (-epsilon),
        ),
        (
            (2 * pi) ** (3 - _dimensionally_regularized),
            2 ** (3 - _dimensionally_regularized)
            * pi ** (3 - _dimensionally_regularized),
        ),
        (
            ((_dimensionally_regularized - 2) / 2).gamma(),
            (1 - epsilon).gamma(),
        ),
        (
            _radius_squared ** (-epsilon),
            _gram_factor ** (-epsilon) * s_lightcone ** (2 * epsilon),
        ),
    )
    _closed_from_raw_lightcone = canonical_zero(
        apply_replacement_rules(
            _raw_lightcone_triangle,
            _positive_branch_rules,
        )
    )
    _definition_residual = canonical_zero(
        _closed_from_raw_lightcone
        - massive_cut_triangle(
            p1_squared,
            s_lightcone,
            mass_squared,
            dimension=_dimensionally_regularized,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        )
    )
    assert _definition_residual == 0
    spenso_table(
        [
            {"step": "C₀", "value": _first_cut},
            {"step": "C₁ after β rule", "value": _second_cut_reduced},
            {"step": "Cₘ after β and κ⊥² rules", "value": _massive_after_kappa},
            {"step": "x rule", "value": _x_solution},
            {"step": "on-shell R⊥²", "value": _radius_squared},
            {"step": "radius residual", "value": _radius_residual},
            {"step": "raw light-cone measure", "value": _raw_lightcone_triangle},
            {"step": "after dim-reg and branch rules", "value": _closed_from_raw_lightcone},
            {"step": "definition residual", "value": _definition_residual},
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Master 6 — maximal four-line cut $M_(00)(s)$

    Current cut `00` puts all four cross-box loop lines on shell.  With

    $
      D_0=k^2, quad D_1=(k-p_1)^2, quad D_2=(p_2-k)^2, quad
      D_3=(p_1+p_2-k)^2-m^2,
    $

    the first three cuts imply the exact scalar-product rules

    $
      k^2 -> 0, quad k dot p_1 -> frac(p_1^2,2), quad
      k dot p_2 -> frac(p_2^2,2).
    $

    These are precisely the invariant form of the three staged light-cone
    solutions for $beta$, $kappa_perp^2$, and $x$.  Applying the rules to the
    dependent fourth denominator gives

    $
      D_0=D_1=D_2=0 quad => quad D_3
      =2p_1 dot p_2-m^2=s-m^2.
    $

    Thus the fourth cut is an endpoint delta, not another independent radial
    localization.  Factoring the leading external-virtuality singularity from
    the first three cuts leaves

    $
      T_(upright("stripped")) =
      frac((mu_R^2 e^(gamma_E))^epsilon s^(-epsilon),
        4 Gamma(1-epsilon)
        [lambda(0,0,s)]^(1/2-epsilon)).
    $

    The final real cut supplies $2 pi delta(s-m^2)$.  With $m^2=z s$ and
    $s>0$,

    $
      delta(s-m^2)=frac(delta(1-z),s), quad
      M_(00)(s)=frac(2 pi,s) T_(upright("stripped")).
    $

    This boundary master contains the loop measure, all four internal cut-edge
    factors, and the delta Jacobian.  It excludes the diagram numerator, the
    two external $upright(d)p_i^2/(2 pi)$ integrations, couplings, colour,
    spin averages, and the graph sign.
    """)
    return


@app.function
def maximal_cross_box_cut_master(
    momentum_squared: "Expression",
    *,
    dimension: "Expression",
    epsilon: "Expression",
    mu_squared: "Expression",
    euler_gamma: "Expression",
) -> "Expression":
    """Unit-numerator master for the maximal four-line cross-box cut.

    ``momentum_squared`` is the positive leading-power light-cone scale ``s``.
    The returned coefficient of ``delta(1-z)`` contains the loop measure, four
    real cut-edge factors, and the Jacobian
    ``delta(s-m^2) = delta(1-z)/s``. It deliberately excludes the diagram
    numerator, the two external ``dp_i^2/(2*pi)`` integrations and their
    ``(p_i^2)^(-1-epsilon)`` singularities, and all graph/process weights.

    Fractional powers follow the same positive-branch convention as the
    historical Mathematica calculation.
    """

    from symbolica import E as _E, Expression as _Expression

    pi = _Expression.PI
    loop_cut_measure = (
        4
        / (2 * pi) ** 3
        / pi ** ((dimension - 4) / 2)
        * cut_normalization(mu_squared, epsilon, euler_gamma)
        * momentum_squared ** (-epsilon)
        * pi ** (4 - epsilon)
        / (
            kallen(0, 0, momentum_squared)
            ** (_E("1/2") - epsilon)
            * (1 - epsilon).gamma()
        )
    )
    return (loop_cut_measure / momentum_squared).cancel()


@app.cell
def _(
    E,
    S,
    apply_replacement_rules,
    canonical_zero,
    epsilon,
    euler_gamma,
    mass_squared,
    mu_squared,
    p1_squared,
    p2_squared,
    pi,
    s,
    spenso_table,
    z,
):
    _k_squared, _k_dot_p1, _k_dot_p2 = S(
        "lc_maximal_k_squared",
        "lc_maximal_k_dot_p1",
        "lc_maximal_k_dot_p2",
    )
    _fourth_denominator = (
        p1_squared
        + p2_squared
        + _k_squared
        + s
        - 2 * _k_dot_p1
        - 2 * _k_dot_p2
        - mass_squared
    )
    _three_cut_rules = (
        (_k_squared, E("0")),
        (_k_dot_p1, p1_squared / 2),
        (_k_dot_p2, p2_squared / 2),
    )
    _fourth_on_cut = canonical_zero(
        apply_replacement_rules(_fourth_denominator, _three_cut_rules)
    )
    assert canonical_zero(_fourth_on_cut - (s - mass_squared)) == 0
    _endpoint_polynomial = canonical_zero(
        apply_replacement_rules(
            _fourth_on_cut,
            ((mass_squared, z * s),),
        )
    )
    assert canonical_zero(_endpoint_polynomial - s * (1 - z)) == 0

    _dimensionally_regularized = 4 - 2 * epsilon
    _stripped_three_cut = (
        cut_normalization(mu_squared, epsilon, euler_gamma)
        * s ** (-epsilon)
        / (
            4
            * (1 - epsilon).gamma()
            * kallen(0, 0, s) ** (E("1/2") - epsilon)
        )
    )
    _derived_maximal_master = 2 * pi / s * _stripped_three_cut
    _definition_residual = canonical_zero(
        _derived_maximal_master
        - maximal_cross_box_cut_master(
            s,
            dimension=_dimensionally_regularized,
            epsilon=epsilon,
            mu_squared=mu_squared,
            euler_gamma=euler_gamma,
        )
    )
    assert _definition_residual == 0
    spenso_table(
        [
            {"step": "D₃ before cut rules", "value": _fourth_denominator},
            {"step": "D₃ after D₀=D₁=D₂=0", "value": _fourth_on_cut},
            {"step": "after m²→zs", "value": _endpoint_polynomial},
            {"step": "stripped three-cut factor", "value": _stripped_three_cut},
            {"step": "M₀₀ definition residual", "value": _definition_residual},
        ],
        pagination=False,
    )
    return


@app.cell
def _(
    d,
    epsilon,
    euler_gamma,
    mass_squared,
    mu_squared,
    p1_squared,
    p2_squared,
    p_squared,
    s,
):
    analytic_master_formulas = (
        {
            "master": "B(psq)",
            "kind": "uncut bubble",
            "expression": uncut_bubble(
                p_squared,
                dimension=d,
                epsilon=epsilon,
                mu_squared=mu_squared,
                euler_gamma=euler_gamma,
            ),
        },
        {
            "master": "Bcut(s)",
            "kind": "massless cut bubble",
            "expression": massless_cut_bubble(
                s,
                dimension=d,
                epsilon=epsilon,
                mu_squared=mu_squared,
                euler_gamma=euler_gamma,
            ),
        },
        {
            "master": "Tcut(p1sq,p2sq,-s)",
            "kind": "massless cut triangle",
            "expression": massless_cut_triangle(
                p1_squared,
                p2_squared,
                -s,
                dimension=d,
                epsilon=epsilon,
                mu_squared=mu_squared,
                euler_gamma=euler_gamma,
            ),
        },
        {
            "master": "Bcutm(s,msq)",
            "kind": "massive cut bubble",
            "expression": massive_cut_bubble(
                s,
                mass_squared,
                dimension=d,
                epsilon=epsilon,
                mu_squared=mu_squared,
                euler_gamma=euler_gamma,
            ),
        },
        {
            "master": "Tcutm(p1sq,s,msq)",
            "kind": "massive cut triangle",
            "expression": massive_cut_triangle(
                p1_squared,
                s,
                mass_squared,
                dimension=d,
                epsilon=epsilon,
                mu_squared=mu_squared,
                euler_gamma=euler_gamma,
            ),
        },
        {
            "master": "M00(s)",
            "kind": "maximal four-line cut master",
            "expression": maximal_cross_box_cut_master(
                s,
                dimension=d,
                epsilon=epsilon,
                mu_squared=mu_squared,
                euler_gamma=euler_gamma,
            ),
        },
    )
    return (analytic_master_formulas,)


@app.cell(hide_code=True)
def _(analytic_master_formulas, mo, spenso_table):
    mo.vstack(
        [
            mo.md("== Closed-form basis"),
            spenso_table(analytic_master_formulas, pagination=False),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Feynman-parameter cross-check for the uncut bubble

    For the massless two-point integral, Feynman parametrization gives

    $
    frac(1, a b) = integral_0^1 frac(upright(d) x, [x a + (1-x)b]^2).
    $

    Shifting the loop momentum leaves a radial loop integral and a beta
    integral,

    $
    integral upright(d)^d ell (ell^2+Delta)^(-2)
      = pi^(d/2) Gamma(2-d/2) Delta^(d/2-2), quad
    integral_0^1 [x(1-x)]^(d/2-2) upright(d) x
      = frac(Gamma((d-2)/2)^2, Gamma(d-2)).
    $

    Multiplying these factors by the historical loop normalization produces
    `B(psq)` exactly.
    """)
    return


@app.cell
def _(canonical_zero, d, epsilon, euler_gamma, mu_squared, p_squared, pi):
    bubble_parameter_integral = (
        ((d - 2) / 2).gamma() ** 2 / (d - 2).gamma()
    )
    bubble_loop_integral = (
        pi ** (d / 2)
        * ((4 - d) / 2).gamma()
        * (-p_squared) ** ((d - 4) / 2)
    )
    bubble_from_derivation = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        / (2 * pi) ** d
        * bubble_loop_integral
        * bubble_parameter_integral
    )
    bubble_formula = uncut_bubble(
        p_squared,
        dimension=d,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    bubble_derivation_residual = canonical_zero(
        bubble_from_derivation - bubble_formula
    )
    assert bubble_derivation_residual == 0
    return (
        bubble_derivation_residual,
        bubble_loop_integral,
        bubble_parameter_integral,
    )


@app.cell
def _(
    bubble_derivation_residual,
    bubble_loop_integral,
    bubble_parameter_integral,
    spenso_table,
):
    spenso_table(
        [
            {
                "piece": "Feynman-parameter beta integral",
                "value": bubble_parameter_integral,
            },
            {
                "piece": "shifted loop-momentum integral",
                "value": bubble_loop_integral,
            },
            {
                "piece": "closed-form residual",
                "value": bubble_derivation_residual,
            },
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Rest-frame and historical-sign cross-checks for the cut bubbles

    In the rest frame of a timelike momentum $P^2=s$, the two cut
    constraints $k^2=0$ and $(P-k)^2=m^2$ fix

    $
      k^0 = abs(bold(k)) = r_* = frac(s-m^2, 2 sqrt(s)).
    $

    With $Omega_n = 2 pi^((n+1)/2)/Gamma((n+1)/2)$, the exact two-body
    phase space is

    $
      Phi_2^(d)(s;0,m^2) =
      frac(Omega_(d-2), 4(2 pi)^(d-2) sqrt(s)) r_*^(d-3).
    $

    Multiplication by
    $overline(S)_epsilon = (mu_R^2 e^(gamma_E)/(4 pi))^epsilon$, followed by
    $d = 4 - 2 epsilon$, reduces the measure prefactor to
    $(mu_R^2 e^(gamma_E))^epsilon/
    [8 sqrt(pi) Gamma((d-1)/2)]$.  The retained historical sign convention gives
    $B_(upright("cutm")) = -overline(S)_epsilon Phi_2^(d)$.

    The retained formulas assign opposite overall signs to `Bcut` and
    `Bcutm`; with that historical sign convention,
    $B_(upright("cut"))(s) = -B_(upright("cutm"))(s,0)$.  The equality of the complete
    all-$epsilon$ expressions is asserted below.
    """)
    return


@app.cell
def _(
    E,
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    mass_squared,
    mu_squared,
    pi,
    s,
):
    massive_cut_radius = (s - mass_squared) / (2 * s.sqrt())
    massive_cut_phase_space = (
        sphere_volume(d - 2)
        / (4 * (2 * pi) ** (d - 2) * s.sqrt())
        * massive_cut_radius ** (d - 3)
    )
    physical_massive_cut_bubble_geometric = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * massive_cut_phase_space
    )
    massive_cut_bubble_geometric = -physical_massive_cut_bubble_geometric

    _dimensionally_regularized = 4 - 2 * epsilon
    bubble_two_power = canonical_zero(
        -2 * epsilon + 3 - _dimensionally_regularized
    )
    bubble_pi_power = canonical_zero(
        -epsilon + (3 - _dimensionally_regularized) / 2
    )
    bubble_gamma_argument = (
        (_dimensionally_regularized - 1) / 2
    ).expand()
    assert bubble_two_power == E("-1")
    assert bubble_pi_power == E("-1/2")

    massive_cut_bubble_from_geometry_dimreg = -(
        cut_normalization(mu_squared, epsilon, euler_gamma)
        * 2**bubble_two_power
        * pi**bubble_pi_power
        / (4 * bubble_gamma_argument.gamma() * s.sqrt())
        * massive_cut_radius
        ** ((_dimensionally_regularized - 3).expand())
    )
    massive_cut_bubble_formula_dimreg = massive_cut_bubble(
        s,
        mass_squared,
        dimension=_dimensionally_regularized,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    massive_cut_bubble_residual = canonical_zero(
        massive_cut_bubble_from_geometry_dimreg
        - massive_cut_bubble_formula_dimreg
    )
    assert massive_cut_bubble_residual == 0, (
        massive_cut_bubble_residual.format_plain()
    )

    massless_cut_bubble_formula_dimreg = massless_cut_bubble(
        s,
        dimension=_dimensionally_regularized,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    massive_cut_bubble_massless_limit = -(
        cut_normalization(mu_squared, epsilon, euler_gamma)
        * 2 ** (-4 + 2 * epsilon)
        * pi ** E("-1/2")
        * s ** (-epsilon)
        / (E("3/2") - epsilon).gamma()
    )
    massless_cut_sign_residual = canonical_zero(
        massless_cut_bubble_formula_dimreg
        + massive_cut_bubble_massless_limit
    )
    assert massless_cut_sign_residual == 0
    return (
        bubble_gamma_argument,
        bubble_pi_power,
        bubble_two_power,
        massive_cut_bubble_geometric,
        massive_cut_bubble_residual,
        massive_cut_phase_space,
        massive_cut_radius,
        massless_cut_sign_residual,
        physical_massive_cut_bubble_geometric,
    )


@app.cell
def _(
    bubble_gamma_argument,
    bubble_pi_power,
    bubble_two_power,
    massive_cut_bubble_geometric,
    massive_cut_bubble_residual,
    massive_cut_phase_space,
    massive_cut_radius,
    massless_cut_sign_residual,
    physical_massive_cut_bubble_geometric,
    spenso_table,
):
    spenso_table(
        [
            {"piece": "on-shell radius", "value": massive_cut_radius},
            {
                "piece": "two-body phase space",
                "value": massive_cut_phase_space,
            },
            {
                "piece": "positive real Sbar × phase space",
                "value": physical_massive_cut_bubble_geometric,
            },
            {
                "piece": "historical Bcutm = -phase space",
                "value": massive_cut_bubble_geometric,
            },
            {
                "piece": "dim-reg powers (2, pi, Gamma argument)",
                "value": (
                    bubble_two_power,
                    bubble_pi_power,
                    bubble_gamma_argument,
                ),
            },
            {
                "piece": "Bcutm residual",
                "value": massive_cut_bubble_residual,
            },
            {
                "piece": "Bcut + Bcutm(s,0) residual",
                "value": massless_cut_sign_residual,
            },
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Light-cone coordinates and preferred DY variables

    Let $Q = 2 p_+ dot p_-$, with $p_+^2 = p_-^2 = 0$, and write

    $
      p_1 = p_+ + frac(p_1^2, Q) p_-, quad
      p_2 = p_- + frac(p_2^2, Q) p_+.
    $

    This gives the exact relations

    $
      2 p_1 dot p_2 = Q + frac(p_1^2 p_2^2, Q), quad
      (p_1+p_2)^2 = Q + p_1^2 + p_2^2 + frac(p_1^2 p_2^2, Q).
    $

    Thus the basis scale $Q$ may be identified with the preferred DY
    variable $s$ only after the leading-virtuality expansion.  This is also
    distinct from silently treating the second historical `Tcutm` argument as
    the exact pair invariant.  The preferred variables used below are
    $z = m^2/s in (0,1)$, $s$, $p_1^2$, $p_2^2$, and, after virtuality
    integration, $Lambda^2$ and optionally $mu_R^2$.
    """)
    return


@app.cell
def _(canonical_zero, p1_squared, p2_squared, s_lightcone, spenso_table):
    _twice_beam_dot = (
        s_lightcone + p1_squared * p2_squared / s_lightcone
    )
    _pair_invariant = (
        s_lightcone
        + p1_squared
        + p2_squared
        + p1_squared * p2_squared / s_lightcone
    )
    assert canonical_zero(
        _pair_invariant
        - _twice_beam_dot
        - p1_squared
        - p2_squared
    ) == 0
    spenso_table(
        [
            {"invariant": "2 p₁·p₂", "exact value": _twice_beam_dot},
            {"invariant": "(p₁+p₂)²", "exact value": _pair_invariant},
            {"invariant": "leading-virtuality basis scale", "exact value": s_lightcone},
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Shared light-cone audit for the massive cut triangle

    Use the mostly-minus metric and decompose the cut momentum as

    $
      k = x p_+ + k_perp + beta p_-, quad
      kappa_perp^2 equiv -k_perp^2 >= 0,
    $
    so that

    $
      upright(d)^d k = frac(Q, 2) upright(d) x upright(d) beta
        upright(d)^(d-2) k_perp, quad
      k^2 = Q x beta - kappa_perp^2.
    $

    The early PDF pages route a negative-energy momentum $k_(upright("PDF"))$
    through $(k_(upright("PDF"))+p_1)^2$ and
    $(k_(upright("PDF"))+p_1+p_2)^2-m^2$.  Here we set
    $k = -k_(upright("PDF"))$, so the same constraints appear as
    $(p_1-k)^2$ and $(p_1+p_2-k)^2-m^2$.  This routing change is separate
    from the historical Cutkosky phases discussed above.

    The first cut fixes
    $beta = kappa_perp^2/(Q x) = -k_perp^2/(Q x)$.  On that support the
    second cut is

    $
      (p_1-k)^2 = (1-x)p_1^2 - frac(kappa_perp^2, x) = 0, quad
      kappa_perp^2 = x(1-x)p_1^2.
    $

    The positive relation is therefore for the Euclidean transverse norm;
    the Minkowski quantity obeys
    $k_perp^2 = -x(1-x)p_1^2$.  For $p_2^2=0$, the massive third cut
    $(p_1+p_2-k)^2=m^2$ then fixes $x=1-m^2/Q=1-z$.  This makes the
    collinear localization $kappa_perp^2 -> 0$ as $p_1^2 -> 0$
    manifest.  The delta reductions retain the physical support
    $Q>m^2>0$ and $0<x<1$; these theta-function restrictions must not be
    discarded when continuing the symbolic formula to another region.
    """)
    return


@app.cell
def _(
    beta,
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    kappa_squared,
    mass_squared,
    mu_squared,
    p1_squared,
    pi,
    s_lightcone,
    x,
):
    lightcone_q_virtuality = s_lightcone * x * beta - kappa_squared
    lightcone_beta_solution = kappa_squared / (s_lightcone * x)

    _second_cut = (
        (1 - x) * (p1_squared - s_lightcone * beta)
        - kappa_squared
    )
    lightcone_second_cut_after_beta = canonical_zero(
        _second_cut.replace(beta, lightcone_beta_solution)
    )
    assert canonical_zero(
        lightcone_second_cut_after_beta
        - (1 - x) * p1_squared
        + kappa_squared / x
    ) == 0
    lightcone_kappa_solution = x * (1 - x) * p1_squared

    _third_cut = (
        s_lightcone
        * (1 - x)
        * (1 + p1_squared / s_lightcone - beta)
        - kappa_squared
        - mass_squared
    )
    lightcone_third_cut_reduced = canonical_zero(
        _third_cut.replace(beta, lightcone_beta_solution)
        .replace(kappa_squared, lightcone_kappa_solution)
    )
    assert canonical_zero(
        lightcone_third_cut_reduced
        - (s_lightcone * (1 - x) - mass_squared)
    ) == 0
    lightcone_x_solution = 1 - mass_squared / s_lightcone

    lightcone_longitudinal_jacobian = canonical_zero(
        s_lightcone / 2
        * 1 / (s_lightcone * x)
        * x
        * 1 / s_lightcone
    )
    assert canonical_zero(
        lightcone_longitudinal_jacobian - 1 / (2 * s_lightcone)
    ) == 0

    lightcone_bubble_parameter_integral = (
        ((d - 2) / 2).gamma() ** 2 / (d - 2).gamma()
    )
    lightcone_cut_bubble_measure = (
        sphere_volume(d - 3)
        / 4
        * p1_squared ** ((d - 4) / 2)
        * lightcone_bubble_parameter_integral
    )
    lightcone_cut_bubble_geometric = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * (2 * pi) ** (2 - d)
        * lightcone_cut_bubble_measure
    )
    lightcone_cut_bubble_finite_residual = canonical_zero(
        lightcone_cut_bubble_geometric
        .replace(d, 4)
        .replace(epsilon, 0)
        - 1 / (8 * pi)
    )
    assert lightcone_cut_bubble_finite_residual == 0

    lightcone_transverse_radius_squared = canonical_zero(
        lightcone_kappa_solution.replace(x, lightcone_x_solution)
    )
    lightcone_triangle_measure = (
        lightcone_longitudinal_jacobian
        * sphere_volume(d - 3)
        / 2
        * lightcone_transverse_radius_squared ** ((d - 4) / 2)
    )
    lightcone_triangle_geometric = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * (2 * pi) ** (3 - d)
        * lightcone_triangle_measure
    )
    return (
        lightcone_beta_solution,
        lightcone_bubble_parameter_integral,
        lightcone_cut_bubble_finite_residual,
        lightcone_cut_bubble_geometric,
        lightcone_cut_bubble_measure,
        lightcone_kappa_solution,
        lightcone_longitudinal_jacobian,
        lightcone_q_virtuality,
        lightcone_second_cut_after_beta,
        lightcone_third_cut_reduced,
        lightcone_transverse_radius_squared,
        lightcone_triangle_geometric,
        lightcone_triangle_measure,
        lightcone_x_solution,
    )


@app.cell
def _(
    lightcone_beta_solution,
    lightcone_bubble_parameter_integral,
    lightcone_cut_bubble_finite_residual,
    lightcone_cut_bubble_geometric,
    lightcone_cut_bubble_measure,
    lightcone_kappa_solution,
    lightcone_longitudinal_jacobian,
    lightcone_q_virtuality,
    lightcone_second_cut_after_beta,
    lightcone_third_cut_reduced,
    lightcone_transverse_radius_squared,
    lightcone_triangle_geometric,
    lightcone_triangle_measure,
    lightcone_x_solution,
    spenso_table,
):
    spenso_table(
        [
            {"step": "k² before the cut", "value": lightcone_q_virtuality},
            {"step": "β from k²=0", "value": lightcone_beta_solution},
            {
                "step": "(p₁-k)² after β",
                "value": lightcone_second_cut_after_beta,
            },
            {"step": "κ⊥² from the second cut", "value": lightcone_kappa_solution},
            {
                "step": "massive cut after first two cuts",
                "value": lightcone_third_cut_reduced,
            },
            {"step": "x from the massive cut", "value": lightcone_x_solution},
            {
                "step": "combined longitudinal Jacobian",
                "value": lightcone_longitudinal_jacobian,
            },
            {
                "step": "bubble x-integral",
                "value": lightcone_bubble_parameter_integral,
            },
            {
                "step": "raw two-delta bubble measure",
                "value": lightcone_cut_bubble_measure,
            },
            {
                "step": "positive real light-cone Bcut",
                "value": lightcone_cut_bubble_geometric,
            },
            {
                "step": "Bcut(d=4)-1/(8π) residual",
                "value": lightcone_cut_bubble_finite_residual,
            },
            {
                "step": "on-shell κ⊥²",
                "value": lightcone_transverse_radius_squared,
            },
            {"step": "raw three-delta measure", "value": lightcone_triangle_measure},
            {
                "step": "with loop/cut normalization",
                "value": lightcone_triangle_geometric,
            },
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Keeping both beam virtualities

    As a new extension beyond the PDF's leading-$p_1^2$ calculation, the
    Sudakov construction can retain both $p_1^2$ and $p_2^2$ exactly.  If
    $S=(p_1+p_2)^2$, the remaining third-cut
    Jacobian is

    $
      J_3 = Q - frac(p_1^2 p_2^2, Q), quad
      J_3^2 = lambda(S,p_1^2,p_2^2),
    $

    and the cut fixes

    $
      x_* = frac(Q+p_2^2-m^2, J_3).
    $

    On the displayed physical branch,
    $Q = [S-p_1^2-p_2^2+sqrt(lambda(S,p_1^2,p_2^2))]/2$.
    The phase-space formula below assumes $J_3>0$, $0<x_*<1$, and the routed
    positive-energy theta-function support.  It vanishes when that support is
    absent; on a reversed algebraic branch its Jacobian is $|J_3|$ rather than
    $J_3$.  Thus the expression shown in the table is the exact integrand
    factor on the stated supported branch, not a global analytic continuation
    of the phase space.

    The exact expression below is kept as a transparent pre-expansion
    cross-check; the historical Tcutm substitution is its
    $p_2^2 -> 0$, leading-$p_1^2$ limit.
    """)
    return


@app.cell
def _(
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    lightcone_transverse_radius_squared,
    mass_squared,
    mu_squared,
    p1_squared,
    p2_squared,
    pi,
    s,
    s_lightcone,
):
    full_virtuality_pair_invariant = (
        s_lightcone
        + p1_squared
        + p2_squared
        + p1_squared * p2_squared / s_lightcone
    )
    full_virtuality_third_jacobian = (
        s_lightcone - p1_squared * p2_squared / s_lightcone
    )
    full_virtuality_kallen = kallen(
        full_virtuality_pair_invariant,
        p1_squared,
        p2_squared,
    )
    full_virtuality_kallen_residual = canonical_zero(
        full_virtuality_third_jacobian**2 - full_virtuality_kallen
    )
    assert full_virtuality_kallen_residual == 0

    full_virtuality_x_solution = (
        s_lightcone + p2_squared - mass_squared
    ) / full_virtuality_third_jacobian
    full_virtuality_radius_squared = (
        p1_squared
        * full_virtuality_x_solution
        * (1 - full_virtuality_x_solution)
    )
    full_virtuality_triangle_geometric = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * (2 * pi) ** (3 - d)
        * sphere_volume(d - 3)
        / (4 * full_virtuality_third_jacobian)
        * full_virtuality_radius_squared ** ((d - 4) / 2)
    )
    full_virtuality_basis_from_pair = (
        s
        - p1_squared
        - p2_squared
        + kallen(s, p1_squared, p2_squared).sqrt()
    ) / 2

    _radius_p2_zero = full_virtuality_radius_squared.replace(p2_squared, 0)
    full_virtuality_p2_zero_residual = canonical_zero(
        _radius_p2_zero - lightcone_transverse_radius_squared
    )
    assert full_virtuality_p2_zero_residual == 0
    return (
        full_virtuality_basis_from_pair,
        full_virtuality_kallen,
        full_virtuality_kallen_residual,
        full_virtuality_p2_zero_residual,
        full_virtuality_pair_invariant,
        full_virtuality_radius_squared,
        full_virtuality_third_jacobian,
        full_virtuality_triangle_geometric,
        full_virtuality_x_solution,
    )


@app.cell
def _(
    full_virtuality_basis_from_pair,
    full_virtuality_kallen,
    full_virtuality_kallen_residual,
    full_virtuality_p2_zero_residual,
    full_virtuality_pair_invariant,
    full_virtuality_radius_squared,
    full_virtuality_third_jacobian,
    full_virtuality_triangle_geometric,
    full_virtuality_x_solution,
    spenso_table,
):
    spenso_table(
        [
            {"piece": "S=(p₁+p₂)²", "value": full_virtuality_pair_invariant},
            {"piece": "third-cut Jacobian J₃", "value": full_virtuality_third_jacobian},
            {"piece": "λ(S,p₁²,p₂²)", "value": full_virtuality_kallen},
            {"piece": "J₃²-λ residual", "value": full_virtuality_kallen_residual},
            {"piece": "x*", "value": full_virtuality_x_solution},
            {"piece": "κ⊥² at x*", "value": full_virtuality_radius_squared},
            {
                "piece": "three-cut factor on the supported branch",
                "value": full_virtuality_triangle_geometric,
            },
            {
                "piece": "Q(S,p₁²,p₂²), physical branch",
                "value": full_virtuality_basis_from_pair,
            },
            {
                "piece": "p₂²→0 radius residual",
                "value": full_virtuality_p2_zero_residual,
            },
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Geometric cross-check and generic cut triangles

    The third on-shell constraint fixes one more longitudinal component.  The
    remaining transverse orbit is controlled by a Gram determinant.  For the
    massive triangle,

    $
      Delta_m = p_i^2(s-m^2)m^2, quad
      R_m^2 = frac(Delta_m, s^2),
    $

    and the geometric cut is

    $
      cal(C)_3 = overline(S)_epsilon (2 pi)^(3-d)
      frac(Omega_(d-3), 4s) R_m^(d-4).
    $

    Here the historical second argument is $s = 2 p_1 dot p_2$; it is not
    $(p_1+p_2)^2$ when the displayed external virtuality is nonzero.

    For a generic massless triple cut,
    $R^2 = -x y z/lambda(x,y,z)$, and the longitudinal Jacobian contains
    $1/sqrt(lambda(x,y,z))$:

    $
      cal(C)_3^(upright("generic")) = overline(S)_epsilon (2 pi)^(3-d)
      frac(Omega_(d-3), 4 sqrt(lambda(x,y,z)))
      (frac(-x y z, lambda(x,y,z)))^((d-4)/2).
    $

    The retained `Tcut` formula deliberately
    replaces this full Gram determinant by $lambda(0,0,z)$, as appropriate
    to its leading-regulator use.  Both forms are kept visible below.
    """)
    return


@app.cell
def _(
    E,
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    lightcone_transverse_radius_squared,
    mass_squared,
    mu_squared,
    p1_squared,
    p2_squared,
    pi,
    s,
    s_lightcone,
):
    massive_triangle_gram = p1_squared * (s - mass_squared) * mass_squared
    lightcone_radius_residual = canonical_zero(
        lightcone_transverse_radius_squared.replace(s_lightcone, s)
        - massive_triangle_gram / s**2
    )
    assert lightcone_radius_residual == 0
    massive_triangle_transverse_orbit = (
        massive_triangle_gram ** ((d - 4) / 2)
        / s ** (d - 4)
    )
    massive_cut_triangle_geometric = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * (2 * pi) ** (3 - d)
        * sphere_volume(d - 3)
        / (4 * s)
        * massive_triangle_transverse_orbit
    )

    generic_triangle_kallen = kallen(p1_squared, p2_squared, -s)
    historical_triangle_kallen = kallen(0, 0, -s)
    generic_triangle_radius_squared = (
        p1_squared * p2_squared * s / generic_triangle_kallen
    )
    generic_massless_triangle_geometric = (
        loop_normalization(mu_squared, epsilon, euler_gamma)
        * (2 * pi) ** (3 - d)
        * sphere_volume(d - 3)
        / (4 * generic_triangle_kallen.sqrt())
        * generic_triangle_radius_squared ** ((d - 4) / 2)
    )

    _dimensionally_regularized = 4 - 2 * epsilon
    triangle_two_power = canonical_zero(
        -2 * epsilon + 4 - _dimensionally_regularized
    )
    triangle_pi_power = canonical_zero(
        -epsilon + 2 - _dimensionally_regularized / 2
    )
    triangle_gamma_argument = (
        (_dimensionally_regularized - 2) / 2
    ).expand()
    assert triangle_two_power == 0
    assert triangle_pi_power == 0
    assert canonical_zero(triangle_gamma_argument - (1 - epsilon)) == 0

    massive_cut_triangle_from_geometry_dimreg = (
        cut_normalization(mu_squared, epsilon, euler_gamma)
        * 2**triangle_two_power
        * pi**triangle_pi_power
        / (4 * s * triangle_gamma_argument.gamma())
        * massive_triangle_gram
        ** (((_dimensionally_regularized - 4) / 2).expand())
        / s ** ((_dimensionally_regularized - 4).expand())
    )
    massive_cut_triangle_formula_dimreg = massive_cut_triangle(
        p1_squared,
        s,
        mass_squared,
        dimension=_dimensionally_regularized,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    massive_cut_triangle_residual = canonical_zero(
        massive_cut_triangle_from_geometry_dimreg
        - massive_cut_triangle_formula_dimreg
    )
    assert massive_cut_triangle_residual == 0, (
        massive_cut_triangle_residual.format_plain()
    )

    historical_triangle_numerator = p1_squared * p2_squared * s
    historical_triangle_kallen_power = (
        E("1/2") - epsilon
    ).expand()
    historical_triangle_from_geometry_dimreg = (
        cut_normalization(mu_squared, epsilon, euler_gamma)
        * 2**triangle_two_power
        * pi**triangle_pi_power
        / (4 * triangle_gamma_argument.gamma())
        * historical_triangle_numerator ** (-epsilon)
        / historical_triangle_kallen**historical_triangle_kallen_power
    )
    historical_triangle_formula_dimreg = massless_cut_triangle(
        p1_squared,
        p2_squared,
        -s,
        dimension=_dimensionally_regularized,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    historical_triangle_residual = canonical_zero(
        historical_triangle_from_geometry_dimreg
        - historical_triangle_formula_dimreg
    )
    assert historical_triangle_residual == 0
    return (
        generic_massless_triangle_geometric,
        generic_triangle_kallen,
        historical_triangle_kallen,
        historical_triangle_residual,
        lightcone_radius_residual,
        massive_cut_triangle_geometric,
        massive_cut_triangle_residual,
        massive_triangle_gram,
        massive_triangle_transverse_orbit,
        triangle_gamma_argument,
        triangle_pi_power,
        triangle_two_power,
    )


@app.cell
def _(
    generic_massless_triangle_geometric,
    generic_triangle_kallen,
    historical_triangle_kallen,
    historical_triangle_residual,
    lightcone_radius_residual,
    massive_cut_triangle_geometric,
    massive_cut_triangle_residual,
    massive_triangle_gram,
    massive_triangle_transverse_orbit,
    spenso_table,
    triangle_gamma_argument,
    triangle_pi_power,
    triangle_two_power,
):
    spenso_table(
        [
            {
                "piece": "light-cone / Gram radius residual",
                "value": lightcone_radius_residual,
            },
            {"piece": "massive Gram factor", "value": massive_triangle_gram},
            {
                "piece": "massive transverse orbit",
                "value": massive_triangle_transverse_orbit,
            },
            {
                "piece": "massive geometric cut",
                "value": massive_cut_triangle_geometric,
            },
            {
                "piece": "generic / historical Kallen",
                "value": (
                    generic_triangle_kallen,
                    historical_triangle_kallen,
                ),
            },
            {
                "piece": "generic massless geometric cut",
                "value": generic_massless_triangle_geometric,
            },
            {
                "piece": "historical Tcut residual",
                "value": historical_triangle_residual,
            },
            {
                "piece": "dim-reg powers (2, pi, Gamma argument)",
                "value": (
                    triangle_two_power,
                    triangle_pi_power,
                    triangle_gamma_argument,
                ),
            },
            {
                "piece": "Tcutm residual",
                "value": massive_cut_triangle_residual,
            },
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Explicit reduction-to-master identifications

    These are the canonical/effective analytic substitutions used by the
    retained Mathematica calculation.  They are a catalog of *known analytic
    identifications*, not a claim that every preferred Kira master in the
    reduction notebook has already been evaluated.

    The literal legacy line `Int[6,{1,1,0}] -> B[p1]` is deliberately omitted:
    the surrounding routing has already remapped that sector to topology 7,
    whose following evaluation is the `Bcut(p1²)` entry below.  For the
    cross-box labels, current cut `11` is Mathematica `resxbox00`, current `10`
    is `resxbox10`, and current `01` is `resxbox01`. Current cut `00`
    (Mathematica `resxbox11`) identifies the analytic maximal-cut master
    `M00(s)`. It is a boundary master outside the three-propagator Kira
    families, not a missing Kira reduction.
    """)
    return


@app.cell
def _(mo):
    master_identifications = (
        {
            "source": "topo2(1,0,1)",
            "analytic master": "Bcutm(s,m²)",
            "context": "massive triangle block",
        },
        {
            "source": "topo3(1,0,1)",
            "analytic master": "Bcutm(s,m²)",
            "context": "massive triangle block",
        },
        {
            "source": "topo5(0,1,1)",
            "analytic master": "B(s)",
            "context": "uncut massless block",
        },
        {
            "source": "topo6(1,0,1)",
            "analytic master": "Bcut(p₂²)",
            "context": "single-cut block",
        },
        {
            "source": "topo7(1,1,0)",
            "analytic master": "Bcut(p₁²)",
            "context": "single-cut block",
        },
        {
            "source": "topo8(1,1,1)",
            "analytic master": "Tcut(p₁²,p₂²,-s)",
            "context": "double-cut block",
        },
        {
            "source": "topo10(1,0,1)",
            "analytic master": "Bcutm(s,m²)",
            "context": "massive block",
        },
        {
            "source": "topo11(1,1,1)",
            "analytic master": "Tcutm(p₁²,s,m²)",
            "context": "massive block",
        },
        {
            "source": "topo20(1,0,1)",
            "analytic master": "Bcutm(s,q²)",
            "context": "current cut 11 / Mathematica resxbox00",
        },
        {
            "source": "topo22(1,1,0)",
            "analytic master": "Bcutm(s,q²)",
            "context": "current cut 11 / Mathematica resxbox00",
        },
        {
            "source": "topo26(1,1,1)",
            "analytic master": "Tcutm(p₂²,s,q²)",
            "context": "current cut 10 / Mathematica resxbox10",
        },
        {
            "source": "topo28(1,1,1)",
            "analytic master": "Tcutm(p₁²,s,q²)",
            "context": "current cut 01 / Mathematica resxbox01",
        },
        {
            "source": "all four cross-box loop lines cut",
            "analytic master": "M00(s)",
            "context": "current cut 00 / Mathematica resxbox11; no Kira",
        },
    )
    mo.ui.table(master_identifications, pagination=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Dimensional regularization and exact checks

    Set $d = 4 - 2 epsilon$.  The cut bubbles are dimensionless, while both cut
    triangles have mass dimension $-2$.  At $epsilon=0$, the massive
    masters reduce to particularly simple phase-space factors.
    """)
    return


@app.cell
def _(
    E,
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    mass_squared,
    mu_squared,
    p1_squared,
    p2_squared,
    pi,
    s,
):
    dimensionally_regularized = 4 - 2 * epsilon
    bubble_mass_dimension = canonical_zero(
        (2 * epsilon + d - 4).replace(d, dimensionally_regularized)
    )
    triangle_mass_dimension = canonical_zero(
        (2 * epsilon + d - 6).replace(d, dimensionally_regularized)
    )
    assert bubble_mass_dimension == 0
    assert triangle_mass_dimension == E("-2")

    cut_bubble_dimreg = massless_cut_bubble(
        s,
        dimension=dimensionally_regularized,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    cut_triangle_dimreg = massless_cut_triangle(
        p1_squared,
        p2_squared,
        -s,
        dimension=dimensionally_regularized,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    massive_bubble_dimreg = massive_cut_bubble(
        s,
        mass_squared,
        dimension=dimensionally_regularized,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    massive_triangle_dimreg = massive_cut_triangle(
        p1_squared,
        s,
        mass_squared,
        dimension=dimensionally_regularized,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )

    leading_checks = (
        (
            "Bcut finite term",
            cut_bubble_dimreg.series(epsilon, 0, 0).to_expression(),
            1 / (8 * pi),
        ),
        (
            "Tcut finite term",
            cut_triangle_dimreg.series(epsilon, 0, 0).to_expression(),
            1 / (4 * (s**2).sqrt()),
        ),
        (
            "Bcutm finite term",
            massive_bubble_dimreg.series(epsilon, 0, 0).to_expression(),
            -(s - mass_squared) / (8 * pi * s),
        ),
        (
            "Tcutm finite term",
            massive_triangle_dimreg.series(epsilon, 0, 0).to_expression(),
            1 / (4 * s),
        ),
    )
    leading_validation_rows = []
    for _name, _actual, _expected in leading_checks:
        _residual = canonical_zero(_actual - _expected)
        assert _residual == 0, (
            f"{_name} failed: {_residual.format_plain()}"
        )
        leading_validation_rows.append(
            {
                "check": _name,
                "expected": _expected,
                "residual": _residual,
            }
        )
    return (
        cut_bubble_dimreg,
        cut_triangle_dimreg,
        dimensionally_regularized,
        leading_validation_rows,
        massive_bubble_dimreg,
        massive_triangle_dimreg,
    )


@app.cell
def _(leading_validation_rows, spenso_table):
    spenso_table(leading_validation_rows, pagination=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Reparametrize the massive masters by $z=m^2/s$

    In the positive DY region $0 < z < 1$, the light-cone radius becomes
    $R_perp^2 = p_1^2 z(1-z)$.  The dimensionally regulated triangle is
    therefore

    $
      T_(upright("cutm"))(p_1^2,s,z) =
      frac(1, 4s Gamma(1-epsilon))
      [frac(mu_R^2 e^(gamma_E), p_1^2 z(1-z))]^epsilon .
    $

    Keeping this compact form separate from the exact finite-virtuality
    expression makes the point at which the leading-$p_i^2$ expansion was
    taken explicit.
    """)
    return


@app.cell
def _(
    canonical_zero,
    epsilon,
    euler_gamma,
    mass_squared,
    massive_bubble_dimreg,
    massive_triangle_dimreg,
    mu_squared,
    p1_squared,
    s,
    spenso_table,
    z,
):
    _mass_substitution = z * s
    _bubble_in_dy_variables = massive_bubble_dimreg.replace(
        mass_squared,
        _mass_substitution,
    )
    _triangle_in_dy_variables = massive_triangle_dimreg.replace(
        mass_squared,
        _mass_substitution,
    )
    _dy_transverse_radius_squared = canonical_zero(
        p1_squared
        * (s - _mass_substitution)
        * _mass_substitution
        / s**2
    )
    _dy_radius_residual = canonical_zero(
        _dy_transverse_radius_squared - p1_squared * z * (1 - z)
    )
    assert _dy_radius_residual == 0
    _triangle_compact = (
        cut_normalization(mu_squared, epsilon, euler_gamma)
        / (4 * s * (1 - epsilon).gamma())
        * (p1_squared * z * (1 - z)) ** (-epsilon)
    )
    spenso_table(
        [
            {"master": "Bcutm(s,zs)", "expression": _bubble_in_dy_variables},
            {"master": "Tcutm(p₁²,s,zs)", "expression": _triangle_in_dy_variables},
            {"master": "light-cone radius R⊥²", "expression": _dy_transverse_radius_squared},
            {"master": "radius residual", "expression": _dy_radius_residual},
            {"master": "compact positive-branch Tcutm", "expression": _triangle_compact},
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    On the positive real branches, the compact expansions begin as

    $
    B(p^2) &= frac(1, 16 pi^2)
      [frac(1,epsilon) + 2 + log(frac(mu_R^2,-p^2))
      + cal(O)(epsilon)], \
    B_(upright("cut"))(s) &= frac(1, 8 pi)
      [1 + epsilon(2 + log(frac(mu_R^2,s)))
      + cal(O)(epsilon^2)], \
    B_(upright("cutm"))(s,m^2) &= -frac(s-m^2, 8 pi s)
      [1 + epsilon(2 +
      log(frac(mu_R^2 s, (s-m^2)^2)))
      + cal(O)(epsilon^2)].
    $

    In particular, the retained historical sign convention obeys
    $B_(upright("cut"))(s) = -B_(upright("cutm"))(s,0)$.  Both triangle families take
    the common form

    $
      T = frac(1,4s)[1 + epsilon L +
      frac(epsilon^2,2)(L^2-frac(pi^2,6))
      + cal(O)(epsilon^3)],
    $

    with
    $L = log[mu_R^2 s/(p_1^2 p_2^2)]$ for
    $T_(upright("cut"))(p_1^2,p_2^2,-s)$, and
    $L = log[mu_R^2 s^2/(p_i^2(s-m^2)m^2)]$ for
    $T_(upright("cutm"))(p_i^2,s,m^2)$.
    """)
    return


@app.cell
def _(mo):
    series_order = mo.ui.slider(
        start=0,
        stop=2,
        step=1,
        value=1,
        label="Highest displayed epsilon power",
        show_value=True,
    )
    series_order
    return (series_order,)


@app.cell
def _(
    cut_bubble_dimreg,
    cut_triangle_dimreg,
    dimensionally_regularized,
    epsilon,
    euler_gamma,
    massive_bubble_dimreg,
    massive_triangle_dimreg,
    mu_squared,
    p_squared,
    series_order,
):
    uncut_bubble_dimreg = uncut_bubble(
        p_squared,
        dimension=dimensionally_regularized,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    dimreg_masters = (
        ("B(psq)", uncut_bubble_dimreg),
        ("Bcut(s)", cut_bubble_dimreg),
        ("Tcut(p1sq,p2sq,-s)", cut_triangle_dimreg),
        ("Bcutm(s,msq)", massive_bubble_dimreg),
        ("Tcutm(p1sq,s,msq)", massive_triangle_dimreg),
    )
    epsilon_expansions = tuple(
        {
            "master": _name,
            "series": _expression.series(
                epsilon,
                0,
                series_order.value,
            ).to_expression().expand(),
        }
        for _name, _expression in dimreg_masters
    )
    return (epsilon_expansions,)


@app.cell
def _(epsilon_expansions, spenso_table):
    spenso_table(epsilon_expansions, pagination=False)
    return


@app.function
def virtuality_integral_factor(
    cutoff_squared: "Expression",
    epsilon: "Expression",
) -> "Expression":
    """Integrate v^(-1-epsilon) with the physical dv/(2*pi) measure."""

    from symbolica import Expression as _Expression

    return -(
        cutoff_squared ** (-epsilon)
        / (2 * _Expression.PI * epsilon)
    )


@app.cell
def _(
    E,
    S,
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    mu_squared,
    pi,
    s,
    spenso_table,
):
    _numerator_on_cut, _lambda1_squared, _lambda2_squared = S(
        "Nmax",
        "Lambda1sq",
        "Lambda2sq",
    )
    _native_maximal_cut_master = maximal_cross_box_cut_master(
        s,
        dimension=d,
        epsilon=epsilon,
        mu_squared=mu_squared,
        euler_gamma=euler_gamma,
    )
    _native_delta_coefficient = (
        _numerator_on_cut
        * _native_maximal_cut_master
        * virtuality_integral_factor(_lambda1_squared, epsilon)
        * virtuality_integral_factor(_lambda2_squared, epsilon)
    ).cancel()

    # DY_calculation.nb, resxbox11: the two explicit 1/(2*pi) factors are
    # applied later in xboxfull4, and delta(s-m^2)=delta(1-z)/s.  The notebook
    # made positivity assumptions before splitting the product power, so the
    # same positive-branch factorization is written explicitly here.
    _historical_delta_coefficient = (
        _numerator_on_cut
        * 4
        / (2 * pi) ** 3
        / pi ** ((d - 4) / 2)
        * (mu_squared * euler_gamma.exp()) ** epsilon
        * _lambda1_squared ** (-epsilon)
        * _lambda2_squared ** (-epsilon)
        * s ** (-epsilon)
        * pi ** (4 - epsilon)
        / (
            (s**2) ** (E("1/2") - epsilon)
            * (1 - epsilon).gamma()
        )
        / epsilon**2
        / (2 * pi) ** 2
        / s
    ).cancel()
    _historical_direct_cut_residual = canonical_zero(
        _native_delta_coefficient - _historical_delta_coefficient
    )
    assert _historical_direct_cut_residual == 0

    _physical_trace_on_cut = -4 * (d - 2) * s**2
    _dimensionally_regularized_direct_cut = _native_delta_coefficient.replace(
        _numerator_on_cut,
        _physical_trace_on_cut,
    ).replace(d, 4 - 2 * epsilon)
    _leading_pole_at_positive_s = (
        _dimensionally_regularized_direct_cut * epsilon**2
    ).replace(epsilon, 0).replace(s, E("5"))
    _leading_pole_residual = canonical_zero(
        _leading_pole_at_positive_s + 1 / pi
    )
    assert _leading_pole_residual == 0

    spenso_table(
        [
            {
                "check": "maximal-cut master / Mathematica resxbox11",
                "residual": _historical_direct_cut_residual,
            },
            {
                "check": "epsilon^2 direct-cut coefficient at positive s",
                "expected": -1 / pi,
                "residual": _leading_pole_residual,
            },
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Leading virtuality expansion and endpoint integration

    Write $v_i = p_i^2$.  After the analytic loop integrations, retain the
    leading-power operator explicitly:

    $
      upright("LP") I_4 &=
        a_4(s,z,epsilon,mu_R^2)
        v_1^(-1-epsilon) v_2^(-1-epsilon), \
      upright("LP") I_2 &=
        a_2(s,z,epsilon,mu_R^2)
        v_1^(-1-epsilon) hat(delta)_partial(v_2), \
      upright("LP") I_3 &=
        a_3(s,z,epsilon,mu_R^2)
        v_2^(-1-epsilon) hat(delta)_partial(v_1), \
      upright("LP") I_1 &=
        a_1(s,z,epsilon,mu_R^2)
        hat(delta)_partial(v_1) hat(delta)_partial(v_2).
    $

    In the manuscript's naming, (I_2) is current cut `01` and (I_3) is
    current cut `10`. The cut names and their explicit virtuality support are
    used in code so that the historical label reversal cannot silently swap
    the two beams.

    Here the one-sided cut delta is defined by
    $integral_0^(Lambda^2) upright(d) v hat(delta)_partial(v)/(2 pi) = 1$.
    This avoids the convention-dependent factor $1/2$ of an ordinary delta
    placed exactly at the boundary.  Equivalently, retain the PDF's original
    domain $(-infinity,Lambda^2]$ for delta-supported channels.

    For the continuous singularity,

    $
      J(Lambda^2) =
      integral_0^(Lambda^2) frac(upright(d) v, 2 pi) v^(-1-epsilon)
      = -frac((Lambda^2)^(-epsilon), 2 pi epsilon).
    $

    The integral first converges for $upright("Re") epsilon < 0$, followed by
    analytic continuation.  Relative remainders should be written as
    $1 + cal(O)(v_1/s) + cal(O)(v_2/s)$, rather than with the same
    scaling as the displayed leading term.  Differentiated cut deltas can
    generate cutoff-boundary contributions, as the PDF notes around
    equations (64)--(68), so those terms must be expanded separately.
    """)
    return


@app.cell
def _(S, canonical_zero, epsilon, lambda_squared, spenso_table):
    _virtuality = S("v")
    _a1 = S("a1", print=scalar_printer(latex=r"a_1", typst="a_1"))
    _a2 = S("a2", print=scalar_printer(latex=r"a_2", typst="a_2"))
    _a3 = S("a3", print=scalar_printer(latex=r"a_3", typst="a_3"))
    _a4 = S("a4", print=scalar_printer(latex=r"a_4", typst="a_4"))
    _antiderivative = -_virtuality ** (-epsilon) / epsilon
    _antiderivative_residual = canonical_zero(
        _antiderivative.derivative(_virtuality)
        - _virtuality ** (-1 - epsilon)
    )
    assert _antiderivative_residual == 0

    _virtuality_factor = virtuality_integral_factor(
        lambda_squared,
        epsilon,
    )
    spenso_table(
        [
            {
                "check": "d/dv[-v^(-ε)/ε] - v^(-1-ε)",
                "value": _antiderivative_residual,
            },
            {
                "check": "J(Λ²), including dp²/(2π)",
                "value": _virtuality_factor,
            },
            {"check": "integrated LP I₄", "value": _a4 * _virtuality_factor**2},
            {"check": "integrated LP I₃", "value": _a3 * _virtuality_factor},
            {"check": "integrated LP I₂", "value": _a2 * _virtuality_factor},
            {"check": "integrated LP I₁", "value": _a1},
        ],
        pagination=False,
    )
    return


@app.class_definition
@__import__("dataclasses").dataclass(frozen=True, slots=True)
class EndpointExpansion:
    """Coefficients in the delta/plus basis for one endpoint power.

    This is metadata about a distributional expansion, not a Symbolica
    expression.  In particular, it does not define test-function action and
    its coefficients must not be multiplied termwise by an arbitrary
    z-dependent prefactor.
    """

    exponent_multiple: int
    delta_coefficient: "Expression"
    plus_coefficients: tuple["Expression", ...]

    @property
    def order(self) -> int:
        """Highest represented D_n coefficient."""

        return len(self.plus_coefficients) - 1


@app.class_definition
@__import__("dataclasses").dataclass(frozen=True, slots=True)
class EndpointDistribution:
    """A delta/plus basis with an ordinary locally integrable remainder.

    The delta and plus coefficients are metadata, not Symbolica distribution
    atoms. The regular_part field is the only ordinary Symbolica expression
    in the represented distribution.
    """

    delta_coefficient: "Expression"
    plus_coefficients: tuple["Expression", ...]
    regular_part: "Expression"

    @property
    def order(self) -> int:
        """Highest represented D_n coefficient."""

        return len(self.plus_coefficients) - 1


@app.function
def endpoint_distribution_expansion(
    exponent_multiple: int,
    epsilon: "Expression",
    *,
    order: int,
) -> "EndpointExpansion":
    r"""Describe ``(1-z)^(-1-a*epsilon)`` through ``D_order``.

    The returned record stores the coefficient of ``delta(1-z)`` and then
    the coefficients of ``D_0(z), ..., D_order(z)``.  It intentionally does
    not manufacture symbolic delta or plus-distribution function heads.
    """

    from math import factorial

    if (
        isinstance(exponent_multiple, bool)
        or not isinstance(exponent_multiple, int)
        or exponent_multiple <= 0
    ):
        raise ValueError("exponent_multiple must be a positive integer")
    if isinstance(order, bool) or not isinstance(order, int) or order < 0:
        raise ValueError("order must be a non-negative integer")

    return EndpointExpansion(
        exponent_multiple=exponent_multiple,
        delta_coefficient=-1 / (exponent_multiple * epsilon),
        plus_coefficients=tuple(
            (-exponent_multiple * epsilon) ** n / factorial(n)
            for n in range(order + 1)
        ),
    )


@app.function
def apply_endpoint_expansion(
    expansion: "EndpointExpansion",
    regular_prefactor: "Expression",
    z: "Expression",
) -> "EndpointDistribution":
    r"""Multiply an endpoint expansion by a prefactor smooth at z=1.

    This implements

    g(z) D_n(z) = g(1) D_n(z)
      + (g(z)-g(1)) log(1-z)^n/(1-z)

    coefficient by coefficient. The second term is returned as the ordinary,
    locally integrable regular_part; no symbolic delta or plus-distribution
    heads are manufactured. The caller is responsible for ensuring that g is
    smooth at the endpoint, so the displayed quotient has a removable limit.
    Its logarithms may still diverge integrably. Epsilon dependence in g is
    allowed.
    """

    from symbolica import E as _E, Expression as _Expression

    if not isinstance(expansion, EndpointExpansion):
        raise TypeError("expansion must be an EndpointExpansion")
    if not isinstance(regular_prefactor, _Expression):
        raise TypeError("regular_prefactor must be a Symbolica Expression")
    if not isinstance(z, _Expression):
        raise TypeError("z must be a Symbolica Expression")

    endpoint_prefactor = regular_prefactor.replace(z, 1)
    if endpoint_prefactor.contains(z):
        raise ValueError("could not evaluate the prefactor at z=1")
    prefactor_remainder = (
        (regular_prefactor - endpoint_prefactor) / (1 - z)
    ).cancel()
    regular_part = sum(
        (
            coefficient
            * prefactor_remainder
            * (1 - z).log() ** n
            for n, coefficient in enumerate(expansion.plus_coefficients)
        ),
        _E("0"),
    ).expand()
    return EndpointDistribution(
        delta_coefficient=(
            endpoint_prefactor * expansion.delta_coefficient
        ).expand(),
        plus_coefficients=tuple(
            (endpoint_prefactor * coefficient).expand()
            for coefficient in expansion.plus_coefficients
        ),
        regular_part=regular_part,
    )


@app.cell
def _(S, canonical_zero, epsilon, spenso_table, z):
    _endpoint_value = S(
        "g1",
        print=scalar_printer(latex=r"g(1)", typst="g(1)"),
    )
    _endpoint_slope = S(
        "gprime",
        print=scalar_printer(latex=r"g'(1)", typst="g'(1)"),
    )
    _expansion = endpoint_distribution_expansion(2, epsilon, order=2)
    _smooth_prefactor = _endpoint_value + _endpoint_slope * (1 - z)
    _applied = apply_endpoint_expansion(
        _expansion,
        _smooth_prefactor,
        z,
    )
    _expected_regular_part = _endpoint_slope * (
        1
        - 2 * epsilon * (1 - z).log()
        + 2 * epsilon**2 * (1 - z).log() ** 2
    )
    _delta_residual = canonical_zero(
        _applied.delta_coefficient
        + _endpoint_value / (2 * epsilon)
    )
    _plus_residuals = tuple(
        canonical_zero(actual - expected)
        for actual, expected in zip(
            _applied.plus_coefficients,
            (
                _endpoint_value,
                -2 * epsilon * _endpoint_value,
                2 * epsilon**2 * _endpoint_value,
            ),
            strict=True,
        )
    )
    _regular_residual = canonical_zero(
        _applied.regular_part - _expected_regular_part
    )
    _exact_constant_test_moment = (
        -_endpoint_value / (2 * epsilon)
        + _endpoint_slope / (1 - 2 * epsilon)
    )
    _expanded_constant_test_moment = _exact_constant_test_moment.series(
        epsilon,
        0,
        2,
    ).to_expression().expand()
    _represented_constant_test_moment = (
        _applied.delta_coefficient
        + _endpoint_slope * (1 + 2 * epsilon + 4 * epsilon**2)
    )
    _constant_test_moment_residual = canonical_zero(
        _expanded_constant_test_moment
        - _represented_constant_test_moment
    )
    assert _applied.order == 2
    assert _delta_residual == 0
    assert all(residual == 0 for residual in _plus_residuals)
    assert _regular_residual == 0
    assert _constant_test_moment_residual == 0

    spenso_table(
        [
            {
                "check": "smooth-prefactor delta coefficient",
                "residual": _delta_residual,
            },
            {
                "check": "smooth-prefactor plus coefficients",
                "residual": _plus_residuals,
            },
            {
                "check": "ordinary regular remainder",
                "residual": _regular_residual,
            },
            {
                "check": "constant test-function moment through epsilon^2",
                "residual": _constant_test_moment_residual,
            },
        ],
        pagination=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Soft endpoint as a plus distribution

    On $z in [0,1]$, define

    $
      cal(D)_n(z) =
      [frac(log^n(1-z), 1-z)]_+, quad
      integral_0^1 upright(d) z cal(D)_n(z) phi(z)
      = integral_0^1 upright(d) z frac(log^n(1-z), 1-z)
       [phi(z)-phi(1)].
    $

    The general endpoint identity is

    $
      (1-z)^(-1-a epsilon)
      = -frac(delta(1-z), a epsilon)
       + sum_(n=0)^infinity
        frac((-a epsilon)^n, n!) cal(D)_n(z).
    $

    The proposed formula is therefore correct for $a=1$.  The unexpanded
    FLU result in PDF equation (129) contains
    $(1-z)^(d-5) = (1-z)^(-1-2 epsilon)$, so that specific expression needs
    $a=2$.  `EndpointExpansion` carries only the coefficients in this
    displayed basis: it is deliberately not a fake Symbolica distribution.
    For a prefactor $g(z)$ smooth at $z=1$,

    $
      g(z) cal(D)_n(z)
      = g(1) cal(D)_n(z)
       + frac(g(z)-g(1), 1-z) log^n(1-z).
    $

    `apply_endpoint_expansion` uses this identity to return rescaled
    delta/plus coefficients together with the ordinary, locally integrable
    remainder.  The notebook validates both the coefficients and exact
    test-function moments.
    """)
    return


@app.cell
def _(mo):
    soft_exponent_multiple = mo.ui.slider(
        start=1,
        stop=2,
        step=1,
        value=2,
        label="Endpoint multiple a",
        show_value=True,
    )
    soft_distribution_order = mo.ui.slider(
        start=0,
        stop=3,
        step=1,
        value=2,
        label="Highest Dₙ term",
        show_value=True,
    )
    mo.hstack(
        [soft_exponent_multiple, soft_distribution_order],
        justify="start",
    )
    return soft_distribution_order, soft_exponent_multiple


@app.cell
def _(epsilon, soft_distribution_order, soft_exponent_multiple):
    _a = soft_exponent_multiple.value
    _endpoint_expansion = endpoint_distribution_expansion(
        _a,
        epsilon,
        order=soft_distribution_order.value,
    )
    soft_distribution_coefficients = [
        {
            "distribution": "δ(1-z)",
            "coefficient": _endpoint_expansion.delta_coefficient,
        }
    ]
    soft_distribution_coefficients.extend(
        {
            "distribution": f"D_{_order}(z)",
            "coefficient": _coefficient,
        }
        for _order, _coefficient in enumerate(
            _endpoint_expansion.plus_coefficients
        )
    )

    assert _endpoint_expansion.exponent_multiple == _a
    assert _endpoint_expansion.order == soft_distribution_order.value
    assert _endpoint_expansion.plus_coefficients[0] == 1
    return (soft_distribution_coefficients,)


@app.cell
def _(E, canonical_zero, epsilon, soft_exponent_multiple):
    _a = soft_exponent_multiple.value

    _z_moment_1 = -1 / (
        _a * epsilon * (1 - _a * epsilon)
    )
    _z_moment_2 = -2 / (
        _a
        * epsilon
        * (1 - _a * epsilon)
        * (2 - _a * epsilon)
    )
    _z_moment_1_series = (
        _z_moment_1.series(epsilon, 0, 1).to_expression().expand()
    )
    _z_moment_2_series = (
        _z_moment_2.series(epsilon, 0, 1).to_expression().expand()
    )
    _z_moment_1_expected = (
        -1 / (_a * epsilon) - 1 - _a * epsilon
    )
    _z_moment_2_expected = (
        -1 / (_a * epsilon)
        - E("3/2")
        - E("7/4") * _a * epsilon
    )
    _moment_1_residual = canonical_zero(
        _z_moment_1_series - _z_moment_1_expected
    )
    _moment_2_residual = canonical_zero(
        _z_moment_2_series - _z_moment_2_expected
    )
    assert _moment_1_residual == 0
    assert _moment_2_residual == 0
    soft_distribution_moments = (
        {
            "test function": "z",
            "exact moment": _z_moment_1,
            "expanded moment": _z_moment_1_series,
            "residual": _moment_1_residual,
        },
        {
            "test function": "z²",
            "exact moment": _z_moment_2,
            "expanded moment": _z_moment_2_series,
            "residual": _moment_2_residual,
        },
    )
    return (soft_distribution_moments,)


@app.cell
def _(
    mo,
    soft_distribution_coefficients,
    soft_distribution_moments,
    spenso_table,
):
    mo.vstack(
        [
            spenso_table(soft_distribution_coefficients, pagination=False),
            spenso_table(soft_distribution_moments, pagination=False),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Numerical evaluation

    The controls choose a real branch with
    $s > m^2 > 0$, $p_1^2,p_2^2 > 0$, and a spacelike argument
    $p^2 = -s$ for the uncut bubble.  The values are useful for spot checks;
    the exact Symbolica expressions above remain the source of truth.
    """)
    return


@app.cell
def _(mo):
    s_value = mo.ui.number(start=1.0, stop=1000.0, step=0.5, value=10.0, label="s")
    mass_value = mo.ui.number(start=0.0, stop=999.0, step=0.25, value=2.0, label="m²")
    p1_value = mo.ui.number(start=0.1, stop=100.0, step=0.1, value=3.0, label="p₁²")
    p2_value = mo.ui.number(start=0.1, stop=100.0, step=0.1, value=4.0, label="p₂²")
    mu_value = mo.ui.number(start=0.1, stop=1000.0, step=0.1, value=10.0, label="μ²")
    epsilon_value = mo.ui.number(start=-0.4, stop=0.4, step=0.01, value=0.05, label="ε")
    numerical_controls = mo.vstack(
        [
            mo.hstack([s_value, mass_value, mu_value], justify="start"),
            mo.hstack([p1_value, p2_value, epsilon_value], justify="start"),
        ]
    )
    numerical_controls
    return epsilon_value, mass_value, mu_value, p1_value, p2_value, s_value


@app.cell
def _(
    epsilon_value,
    mass_value,
    math,
    mo,
    mu_value,
    p1_value,
    p2_value,
    s_value,
):
    _s = float(s_value.value)
    _m2 = float(mass_value.value)
    _p1 = float(p1_value.value)
    _p2 = float(p2_value.value)
    _mu2 = float(mu_value.value)
    _ep = float(epsilon_value.value)
    _d = 4.0 - 2.0 * _ep
    _gamma_e = 0.5772156649015328606

    if not (_s > _m2 > 0 and _p1 > 0 and _p2 > 0 and _mu2 > 0):
        numerical_evaluation = mo.callout(
            "Choose s > m² > 0 and positive p₁², p₂², and μ².",
            kind="warn",
        )
    elif abs(_ep) < 1.0e-12:
        numerical_evaluation = mo.callout(
            "Choose nonzero ε: the uncut bubble has a pole at ε = 0.",
            kind="warn",
        )
    else:
        _loop_norm = (_mu2 * math.exp(_gamma_e) / (4 * math.pi)) ** _ep
        _cut_norm = (_mu2 * math.exp(_gamma_e)) ** _ep
        _uncut = (
            _loop_norm
            / (2 * math.pi) ** _d
            * math.pi ** (_d / 2)
            * math.gamma((_d - 2) / 2) ** 2
            * math.gamma((4 - _d) / 2)
            / math.gamma(_d - 2)
            * _s ** ((_d - 4) / 2)
        )
        _bcut = (
            _loop_norm
            * (2 * math.pi) ** (-_d)
            * 2 ** (2 * _ep)
            * _s ** (-_ep)
            * math.pi ** (3.5 - _ep)
            / math.gamma(1.5 - _ep)
        )
        _tcut = (
            _loop_norm
            * (2 * math.pi) ** (-_d)
            * 4
            * (_p1 * _p2 * _s) ** (-_ep)
            / (_s**2) ** (0.5 - _ep)
            * math.pi ** (4 - _ep)
            / math.gamma(1 - _ep)
        )
        _radius = (_s - _m2) / (2 * math.sqrt(_s))
        _bcutm = -(
            _cut_norm
            / (
                8
                * math.sqrt(math.pi)
                * math.gamma((_d - 1) / 2)
                * math.sqrt(_s)
            )
            * _radius ** (_d - 3)
        )
        _tcutm = (
            _cut_norm
            / (4 * math.gamma((_d - 2) / 2) * _s ** (_d - 3))
            * (_p1 * (_s - _m2) * _m2) ** ((_d - 4) / 2)
        )
        numerical_evaluation = mo.ui.table(
            [
                {"master": "B(-s)", "value": _uncut},
                {"master": "Bcut(s)", "value": _bcut},
                {"master": "Tcut(p₁²,p₂²,-s)", "value": _tcut},
                {"master": "Bcutm(s,m²)", "value": _bcutm},
                {"master": "Tcutm(p₁²,s,m²)", "value": _tcutm},
            ],
            pagination=False,
        )
    numerical_evaluation
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        "Scope: this notebook derives and evaluates the closed-form basis "
        "explicitly present in the retained Mathematica workflow. Preferred "
        "Kira masters without one of the catalogued identifications remain "
        "unevaluated here. Cut 00 is the evaluated analytic maximal-cut "
        "master M00(s), outside the three-propagator Kira families.",
        kind="neutral",
    )
    return


if __name__ == "__main__":
    app.run(defs={"mo": mo})
