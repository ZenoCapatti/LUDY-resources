import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import math

    import marimo as mo
    from symbolica import E, S, Expression

    return E, Expression, S, math, mo


@app.cell
def _(E, Expression, mo):
    from dataclasses import dataclass as _dataclass
    from functools import lru_cache as _lru_cache
    from html import escape as _escape_html
    import re as _re

    import typst as _typst
    from symbolica import PrintMode as _PrintMode

    _typst_compiler = _typst.Compiler(ignore_system_fonts=True)
    _body_pattern = _re.compile(
        r"<body(?:\s[^>]*)?>(.*?)</body>",
        _re.DOTALL,
    )
    _style_pattern = _re.compile(
        r"<style(?:\s[^>]*)?>.*?</style>",
        _re.DOTALL,
    )
    _function_call_pattern = _re.compile(
        r'op\("(?:[^"\\]|\\.)*"\)\('
    )

    def _group_typst_function_applications(math):
        """Make Symbolica's operator applications atomic for Typst.

        Typst otherwise parses ``1/op("gamma")(x)`` as ``(1/gamma) x``.
        Insert grouping parentheses around every complete application, while
        respecting nested calls and quoted Symbolica names.
        """

        spans = []
        for match in _function_call_pattern.finditer(math):
            argument_start = match.end() - 1
            depth = 0
            quoted = False
            escaped = False
            for index in range(argument_start, len(math)):
                character = math[index]
                if quoted:
                    if escaped:
                        escaped = False
                    elif character == "\\":
                        escaped = True
                    elif character == '"':
                        quoted = False
                    continue
                if character == '"':
                    quoted = True
                elif character == "(":
                    depth += 1
                elif character == ")":
                    depth -= 1
                    if depth == 0:
                        spans.append((match.start(), index + 1))
                        break
            else:
                raise ValueError("unbalanced Typst function application")

        opening_at = {}
        closing_at = {}
        for start, end in spans:
            opening_at[start] = opening_at.get(start, 0) + 1
            closing_at[end] = closing_at.get(end, 0) + 1

        grouped = []
        for index, character in enumerate(math):
            grouped.append("(" * opening_at.get(index, 0))
            grouped.append(character)
            grouped.append(")" * closing_at.get(index + 1, 0))
        return "".join(grouped)

    def _typst_math(expression):
        formatted = expression.format(
            mode=_PrintMode.Typst,
            color_builtin_symbols=False,
            bracket_level_colors=None,
            show_namespaces=False,
            max_terms=None,
            num_exp_as_superscript=False,
        )
        # Symbolica's scalar middot needs spaces to be a Typst operator rather
        # than part of a variable name such as ``pi·s``.
        formatted = formatted.replace("·", " dot ")
        return _group_typst_function_applications(formatted)

    @_lru_cache(maxsize=256)
    def _render_typst_html(math):
        document = _typst_compiler.compile(
            input=f"$ {math} $\n".encode(),
            format="html",
        ).decode()
        body = _body_pattern.search(document)
        if body is None or "<math" not in body.group(1):
            raise ValueError("Typst HTML output did not contain MathML")
        styles = "".join(_style_pattern.findall(document))
        return styles, body.group(1)

    @_lru_cache(maxsize=256)
    def _render_typst_svg(math, font_size):
        document = (
            "#set page(width: auto, height: auto, margin: 2pt, fill: none)\n"
            f"#set text(size: {font_size}pt)\n"
            f"$ {math} $\n"
        )
        svg = _typst_compiler.compile(
            input=document.encode(),
            format="svg",
        ).decode()
        return svg.replace("#000000", "currentColor")

    @_dataclass(frozen=True, slots=True)
    class SpensoMath:
        expression: Expression
        font_size: float = 13.0

        @property
        def typst(self):
            return _typst_math(self.expression)

        def _display_(self):
            try:
                styles, body = _render_typst_html(self.typst)
                return mo.Html(
                    f'{styles}<div style="color: inherit; '
                    f'font-size: {self.font_size}pt">{body}</div>'
                )
            except Exception:
                return mo.Html(_render_typst_svg(self.typst, self.font_size))

        def _repr_svg_(self):
            return _render_typst_svg(self.typst, self.font_size)

        def __repr__(self):
            return self.expression.format_plain()

    def spenso_math(expression: Expression) -> SpensoMath:
        """Return a rich display view without changing the exact expression."""

        if not isinstance(expression, Expression):
            raise TypeError("spenso_math expects a Symbolica Expression")
        return SpensoMath(expression)

    def _spenso_math_cell(expression):
        return mo.as_html(spenso_math(expression))

    def _contains_expression(value):
        return isinstance(value, Expression) or (
            isinstance(value, (list, tuple))
            and any(_contains_expression(item) for item in value)
        )

    def _sequence_cell(values):
        opening, closing = ("(", ")") if isinstance(values, tuple) else ("[", "]")
        parts = []
        for index, value in enumerate(values):
            if index:
                parts.append('<span aria-hidden="true">,</span>')
            if isinstance(value, Expression):
                parts.append(_spenso_math_cell(value).text)
            elif isinstance(value, (list, tuple)) and _contains_expression(value):
                parts.append(_sequence_cell(value).text)
            else:
                parts.append(f"<span>{_escape_html(str(value))}</span>")
        return mo.Html(
            '<div style="display: inline-flex; align-items: baseline; '
            'gap: 0.25rem; white-space: nowrap">'
            f"<span>{opening}</span>{''.join(parts)}<span>{closing}</span>"
            "</div>"
        )

    def _table_value(value):
        if isinstance(value, Expression):
            return _spenso_math_cell(value)
        if isinstance(value, (list, tuple)) and _contains_expression(value):
            return _sequence_cell(value)
        return value

    def spenso_table(data, **kwargs):
        """Render exact Symbolica expressions richly inside a Marimo table."""

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
        automatic_formatting = {column: _table_value for column in columns}
        return mo.ui.table(
            data,
            format_mapping={**automatic_formatting, **explicit_formatting},
            **kwargs,
        )

    _scalar_power_probe = _typst_math(1 / Expression.PI**2)
    _gamma_argument_probe = E("3/2-ep")
    _gamma_reciprocal_probe = _typst_math(
        1 / _gamma_argument_probe.gamma()
    )
    _gamma_square_probe = _typst_math(_gamma_argument_probe.gamma() ** 2)
    assert _scalar_power_probe == "1/pi^2"
    assert _gamma_reciprocal_probe == (
        '1/(op("gamma")(3/2-"ep"))'
    )
    assert _gamma_square_probe == '(op("gamma")(3/2-"ep"))^2'
    _scalar_power_mathml = _render_typst_html(_scalar_power_probe)[1]
    _gamma_reciprocal_mathml = _render_typst_html(
        _gamma_reciprocal_probe
    )[1]
    _gamma_square_mathml = _render_typst_html(_gamma_square_probe)[1]
    assert "<math" in _scalar_power_mathml
    assert "<mfrac><mn>1</mn><mrow><mo" in _gamma_reciprocal_mathml
    assert "<msup><mrow><mo>(</mo><mrow><mo" in _gamma_square_mathml

    return spenso_math, spenso_table


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Analytic master integrals for the DY calculation

    This notebook isolates the closed-form master integrals used after the
    Kira/FIRE reduction.  It reconstructs their radial, light-cone, angular,
    Feynman-parameter, and Gram-determinant factors; checks the resulting
    expressions exactly with Symbolica; audits the physical normalization;
    expands them around \(d=4-2\epsilon\); and handles the leading virtuality
    and soft-endpoint distributions before providing a numerical evaluator.
    Exact expressions remain native Symbolica objects and are displayed with
    the same Spenso-aware Typst-to-MathML renderer used in `notebooks/ludy.py`.

    The definitions are faithful to
    [`DY_calculation.nb`](../mathematica/DY_calculation.nb).  Opening or
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
    d, epsilon, mu_squared = S("d", "ep", "musq")
    p_squared, s, mass_squared = S("psq", "s", "msq")
    p1_squared, p2_squared = S("p1sq", "p2sq")
    x, beta, kappa_squared = S("x", "beta", "kappasq")
    z, lambda_squared, s_lightcone = S("z", "Lambdasq", "sLC")
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


@app.cell
def _(Expression, pi):
    def kallen(x: Expression, y: Expression, z: Expression) -> Expression:
        """Return the Källén polynomial λ(x,y,z)."""

        return x**2 + y**2 + z**2 - 2 * x * y - 2 * x * z - 2 * y * z

    def loop_normalization(
        mu_squared: Expression,
        epsilon: Expression,
        euler_gamma: Expression,
    ) -> Expression:
        """Retained MS-bar loop factor with the standard +gamma_E sign."""

        return (
            mu_squared * euler_gamma.exp() / (4 * pi)
        ) ** epsilon

    def cut_normalization(
        mu_squared: Expression,
        epsilon: Expression,
        euler_gamma: Expression,
    ) -> Expression:
        """Closed-form factor after the explicit 4pi powers cancel."""

        return (mu_squared * euler_gamma.exp()) ** epsilon

    def sphere_volume(dimension: Expression) -> Expression:
        """Return the area of the unit sphere S^dimension."""

        return (
            2
            * pi ** ((dimension + 1) / 2)
            / ((dimension + 1) / 2).gamma()
        )

    return cut_normalization, kallen, loop_normalization, sphere_volume


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Audit of `master_and_dump.pdf`

    The reusable master calculations are concentrated on PDF pages 1--3.
    Equation (7) gives the massive cut bubble.  The first triangle route ends
    at equation (25), while the independent transverse derivation in equations
    (31)--(37) exposes
    $\kappa_\perp^2=x(1-x)p_1^2$ and reproduces the retained Mathematica
    master after the scheme conversion displayed below.

    Two inconsistencies in the draft are kept visible rather than silently
    resolved:

    - equation (25) is smaller than equation (37) by a factor of four;
    - pages 1--3 use $e^{-\gamma_E}$, while the FLU formulas on pages 9--10
      and the Mathematica snapshot use $e^{+\gamma_E}$.

    The notebook therefore uses equation (37) and the retained
    $e^{+\gamma_E}$ convention.  The printed leading-$p_1^2$ triangle
    retaining $p_2^2$ is not copied because its equations (42)--(46) omit a
    required $\sqrt{s}$; a new exact two-virtuality light-cone extension is
    derived below.  The
    maximal-box, LU, zero-bin, and FLU notes remain context rather than new
    completed analytic masters.
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
            "status": "context or unfinished work; not a master definition",
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
    ## Normalization ledger

    The physical phase-space convention is

    \[
      \int\frac{d^dk}{(2\pi)^d},\qquad
      \widehat\delta_\pm(q^2-m^2)
      =2\pi\,\theta(\pm q^0)\delta(q^2-m^2),\qquad
      \int\frac{dp_i^2}{2\pi}.
    \]

    Consequently a one-loop object with \(N_c\) real cut edges and \(N_v\)
    virtuality integrations carries
    \((2\pi)^{N_c-d-N_v}\) before angular and delta-function Jacobians.
    Spin and colour averages remain observable-dependent prefactors and are
    not folded into a scalar master.  DIS receives the additional \(1/(4\pi)\)
    factor recorded in PDF equations (125) and (132).

    The early PDF master pages instead write \((2\pi i)^{N_c}\).  Its \(i^2\)
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
            "object": "DIS-only observable factor",
            "loops": 0,
            "cut edges": 0,
            "virtuality integrals": 0,
            "2π factor": 1 / (4 * pi),
        },
    )
    spenso_table(normalization_ledger, pagination=False)
    return


@app.cell
def _(E, Expression, cut_normalization, kallen, loop_normalization, pi):
    def uncut_bubble(
        momentum_squared: Expression,
        *,
        dimension: Expression,
        epsilon: Expression,
        mu_squared: Expression,
        euler_gamma: Expression,
    ) -> Expression:
        """Massless uncut bubble B(p²) in the Mathematica normalization."""

        return (
            loop_normalization(mu_squared, epsilon, euler_gamma)
            / (2 * pi) ** dimension
            * pi ** (dimension / 2)
            * ((dimension - 2) / 2).gamma() ** 2
            * ((4 - dimension) / 2).gamma()
            / (dimension - 2).gamma()
            * (-momentum_squared) ** ((dimension - 4) / 2)
        )

    def massless_cut_bubble(
        momentum_squared: Expression,
        *,
        dimension: Expression,
        epsilon: Expression,
        mu_squared: Expression,
        euler_gamma: Expression,
    ) -> Expression:
        """Massless cut bubble Bcut(p²)."""

        two_power = (-dimension).expand()
        pi_power = (E("7/2") - dimension - 2 * epsilon).expand()
        return (
            cut_normalization(mu_squared, epsilon, euler_gamma)
            * 2**two_power
            * momentum_squared ** (-epsilon)
            * pi**pi_power
            / (E("3/2") - epsilon).gamma()
        )

    def massless_cut_triangle(
        p1_squared: Expression,
        p2_squared: Expression,
        p3_squared: Expression,
        *,
        dimension: Expression,
        epsilon: Expression,
        mu_squared: Expression,
        euler_gamma: Expression,
    ) -> Expression:
        """Massless cut triangle Tcut(p1²,p2²,p3²)."""

        two_power = (2 - dimension - 2 * epsilon).expand()
        pi_power = (4 - dimension - 2 * epsilon).expand()
        kallen_power = (E("1/2") - epsilon).expand()
        return (
            cut_normalization(mu_squared, epsilon, euler_gamma)
            * 2**two_power
            * (-p1_squared * p2_squared * p3_squared) ** (-epsilon)
            / kallen(0, 0, p3_squared) ** kallen_power
            * pi**pi_power
            / (1 - epsilon).gamma()
        )

    def massive_cut_bubble(
        momentum_squared: Expression,
        mass_squared: Expression,
        *,
        dimension: Expression,
        epsilon: Expression,
        mu_squared: Expression,
        euler_gamma: Expression,
    ) -> Expression:
        """Massive cut bubble Bcutm(s,m²)."""

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
                * pi.sqrt()
                * gamma_argument.gamma()
                * momentum_squared.sqrt()
            )
            * cut_radius ** radial_power
        )

    def massive_cut_triangle(
        external_virtuality: Expression,
        momentum_squared: Expression,
        mass_squared: Expression,
        *,
        dimension: Expression,
        epsilon: Expression,
        mu_squared: Expression,
        euler_gamma: Expression,
    ) -> Expression:
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

    return (
        massive_cut_bubble,
        massive_cut_triangle,
        massless_cut_bubble,
        massless_cut_triangle,
        uncut_bubble,
    )


@app.cell
def _(
    d,
    epsilon,
    euler_gamma,
    mass_squared,
    massive_cut_bubble,
    massive_cut_triangle,
    massless_cut_bubble,
    massless_cut_triangle,
    mu_squared,
    p1_squared,
    p2_squared,
    p_squared,
    s,
    uncut_bubble,
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
    )
    return (analytic_master_formulas,)


@app.cell(hide_code=True)
def _(analytic_master_formulas, mo, spenso_table):
    mo.vstack(
        [
            mo.md("## Closed-form basis"),
            spenso_table(analytic_master_formulas, pagination=False),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Derive the uncut bubble

    For the massless two-point integral, Feynman parametrization gives

    \[
    \frac1{ab}=\int_0^1\!\frac{dx}{[xa+(1-x)b]^2}.
    \]

    Shifting the loop momentum leaves a radial loop integral and a beta
    integral,

    \[
    \int d^d\ell\,(\ell^2+\Delta)^{-2}
      =\pi^{d/2}\Gamma(2-d/2)\Delta^{d/2-2},\qquad
    \int_0^1 [x(1-x)]^{d/2-2}dx
      =\frac{\Gamma((d-2)/2)^2}{\Gamma(d-2)}.
    \]

    Multiplying these factors by the historical loop normalization produces
    `B(psq)` exactly.
    """)
    return


@app.cell
def _(
    E,
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    loop_normalization,
    mu_squared,
    p_squared,
    pi,
    uncut_bubble,
):
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
    ## Derive the cut bubbles

    In the rest frame of a timelike momentum \(P^2=s\), the two cut
    constraints \(k^2=0\) and \((P-k)^2=m^2\) fix

    \[
      k^0=|\mathbf k|=r_* = \frac{s-m^2}{2\sqrt{s}}.
    \]

    With \(\Omega_n=2\pi^{(n+1)/2}/\Gamma((n+1)/2)\), the exact two-body
    phase space is

    \[
      \Phi_2^{(d)}(s;0,m^2)=
      \frac{\Omega_{d-2}}{4(2\pi)^{d-2}\sqrt{s}}\,r_*^{d-3}.
    \]

    Multiplication by
    \(\bar S_\epsilon=(\mu^2e^{\gamma_E}/4\pi)^\epsilon\), followed by
    \(d=4-2\epsilon\), reduces the measure prefactor to
    \((\mu^2e^{\gamma_E})^\epsilon/
    [8\sqrt\pi\,\Gamma((d-1)/2)]\).  The retained historical sign convention gives
    \(B_{\rm cutm}=-\bar S_\epsilon\Phi_2^{(d)}\).

    The retained formulas assign opposite overall signs to `Bcut` and
    `Bcutm`; with that historical sign convention,
    \(B_{\rm cut}(s)=-B_{\rm cutm}(s,0)\).  The equality of the complete
    all-\(\epsilon\) expressions is asserted below.
    """)
    return


@app.cell
def _(
    E,
    canonical_zero,
    cut_normalization,
    d,
    epsilon,
    euler_gamma,
    loop_normalization,
    mass_squared,
    massless_cut_bubble,
    massive_cut_bubble,
    mu_squared,
    pi,
    s,
    sphere_volume,
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
    ## Light-cone coordinates and preferred DY variables

    Let $Q=2p_+\!\cdot p_-$, with $p_+^2=p_-^2=0$, and write

    \[
      p_1=p_++\frac{p_1^2}{Q}p_-,\qquad
      p_2=p_-+\frac{p_2^2}{Q}p_+.
    \]

    This gives the exact relations

    \[
      2p_1\!\cdot p_2=Q+\frac{p_1^2p_2^2}{Q},\qquad
      (p_1+p_2)^2=Q+p_1^2+p_2^2+\frac{p_1^2p_2^2}{Q}.
    \]

    Thus the basis scale $Q$ may be identified with the preferred DY
    variable $s$ only after the leading-virtuality expansion.  This is also
    distinct from silently treating the second historical `Tcutm` argument as
    the exact pair invariant.  The preferred variables used below are
    $z=m^2/s\in(0,1)$, $s$, $p_1^2$, $p_2^2$, and, after virtuality
    integration, $\Lambda^2$ and optionally $\mu_R^2$.
    """)
    return


@app.cell
def _(
    canonical_zero,
    p1_squared,
    p2_squared,
    s_lightcone,
    spenso_table,
):
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
    ### Light-cone derivation of the massive cut triangle

    Use the mostly-minus metric and decompose the cut momentum as

    \[
      k=x p_+ + k_\perp+\beta p_-,\qquad
      \kappa_\perp^2\equiv-k_\perp^2\ge0,
    \]
    so that

    \[
      d^dk=\frac Q2\,dx\,d\beta\,d^{d-2}k_\perp,
      \qquad k^2=Qx\beta-\kappa_\perp^2.
    \]

    The early PDF pages route a negative-energy momentum $k_{\rm PDF}$
    through $(k_{\rm PDF}+p_1)^2$ and
    $(k_{\rm PDF}+p_1+p_2)^2-m^2$.  Here we set
    $k=-k_{\rm PDF}$, so the same constraints appear as
    $(p_1-k)^2$ and $(p_1+p_2-k)^2-m^2$.  This routing change is separate
    from the historical Cutkosky phases discussed above.

    The first cut fixes
    $\beta=\kappa_\perp^2/(Qx)=-k_\perp^2/(Qx)$.  On that support the
    second cut is

    \[
      (p_1-k)^2=(1-x)p_1^2-\frac{\kappa_\perp^2}{x}=0,
      \qquad \kappa_\perp^2=x(1-x)p_1^2.
    \]

    The positive relation is therefore for the Euclidean transverse norm;
    the Minkowski quantity obeys
    $k_\perp^2=-x(1-x)p_1^2$.  For $p_2^2=0$, the massive third cut
    $(p_1+p_2-k)^2=m^2$ then fixes $x=1-m^2/Q=1-z$.  This makes the
    collinear localization $\kappa_\perp^2\to0$ as $p_1^2\to0$
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
    loop_normalization,
    mass_squared,
    mu_squared,
    p1_squared,
    pi,
    s_lightcone,
    sphere_volume,
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
    ### Keeping both beam virtualities

    As a new extension beyond the PDF's leading-$p_1^2$ calculation, the
    Sudakov construction can retain both $p_1^2$ and $p_2^2$ exactly.  If
    $S=(p_1+p_2)^2$, the remaining third-cut
    Jacobian is

    \[
      J_3=Q-\frac{p_1^2p_2^2}{Q},\qquad
      J_3^2=\lambda(S,p_1^2,p_2^2),
    \]

    and the cut fixes

    \[
      x_*=\frac{Q+p_2^2-m^2}{J_3}.
    \]

    On the displayed physical branch,
    $Q=[S-p_1^2-p_2^2+\sqrt{\lambda(S,p_1^2,p_2^2)}]/2$.
    The phase-space formula below assumes $J_3>0$, $0<x_*<1$, and the routed
    positive-energy theta-function support.  It vanishes when that support is
    absent; on a reversed algebraic branch its Jacobian is $|J_3|$ rather than
    $J_3$.  Thus the expression shown in the table is the exact integrand
    factor on the stated supported branch, not a global analytic continuation
    of the phase space.

    The exact expression below is kept as a transparent pre-expansion
    cross-check; the historical Tcutm substitution is its
    $p_2^2\to0$, leading-$p_1^2$ limit.
    """)
    return


@app.cell
def _(
    canonical_zero,
    d,
    epsilon,
    euler_gamma,
    kallen,
    lightcone_transverse_radius_squared,
    loop_normalization,
    mass_squared,
    mu_squared,
    p1_squared,
    p2_squared,
    pi,
    s,
    s_lightcone,
    sphere_volume,
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
    ## Geometric cross-check and generic cut triangles

    The third on-shell constraint fixes one more longitudinal component.  The
    remaining transverse orbit is controlled by a Gram determinant.  For the
    massive triangle,

    \[
      \Delta_m=p_i^2(s-m^2)m^2,
      \qquad
      R_m^2=\frac{\Delta_m}{s^2},
    \]

    and the geometric cut is

    \[
      \mathcal C_3=\bar S_\epsilon(2\pi)^{3-d}
      \frac{\Omega_{d-3}}{4s}R_m^{d-4}.
    \]

    Here the historical second argument is \(s=2p_1\!\cdot p_2\); it is not
    \((p_1+p_2)^2\) when the displayed external virtuality is nonzero.

    For a generic massless triple cut,
    \(R^2=-xyz/\lambda(x,y,z)\), and the longitudinal Jacobian contains
    \(1/\sqrt{\lambda(x,y,z)}\):

    \[
      \mathcal C_3^{\rm generic}=\bar S_\epsilon(2\pi)^{3-d}
      \frac{\Omega_{d-3}}{4\sqrt{\lambda(x,y,z)}}
      \left(\frac{-xyz}{\lambda(x,y,z)}\right)^{(d-4)/2}.
    \]

    The retained `Tcut` formula deliberately
    replaces this full Gram determinant by \(\lambda(0,0,z)\), as appropriate
    to its leading-regulator use.  Both forms are kept visible below.
    """)
    return


@app.cell
def _(
    E,
    canonical_zero,
    cut_normalization,
    d,
    epsilon,
    euler_gamma,
    kallen,
    lightcone_transverse_radius_squared,
    loop_normalization,
    mass_squared,
    massless_cut_triangle,
    massive_cut_triangle,
    mu_squared,
    p1_squared,
    p2_squared,
    pi,
    s,
    s_lightcone,
    sphere_volume,
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
    ## Explicit reduction-to-master identifications

    These are the canonical/effective analytic substitutions used by the
    retained Mathematica calculation.  They are a catalog of *known analytic
    identifications*, not a claim that every preferred Kira master in the
    reduction notebook has already been evaluated.

    The literal legacy line `Int[6,{1,1,0}] -> B[p1]` is deliberately omitted:
    the surrounding routing has already remapped that sector to topology 7,
    whose following evaluation is the `Bcut(p1²)` entry below.  For the
    cross-box labels, current cut `11` is Mathematica `resxbox00`, current `10`
    is `resxbox10`, and current `01` is `resxbox01`.  Current cut `00`
    (Mathematica `resxbox11`) is a direct four-line cut, rather than one of
    these three-propagator analytic master identifications.
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
    )
    mo.ui.table(master_identifications, pagination=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Dimensional regularization and exact checks

    Set \(d=4-2\epsilon\).  The cut bubbles are dimensionless, while both cut
    triangles have mass dimension \(-2\).  At \(\epsilon=0\), the massive
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
    massive_cut_bubble,
    massive_cut_triangle,
    massless_cut_bubble,
    massless_cut_triangle,
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
    ### Reparametrize the massive masters by \(z=m^2/s\)

    In the positive DY region \(0<z<1\), the light-cone radius becomes
    \(R_\perp^2=p_1^2z(1-z)\).  The dimensionally regulated triangle is
    therefore

    \[
      T_{\rm cutm}(p_1^2,s,z)=
      \frac{1}{4s\,\Gamma(1-\epsilon)}
      \left[
        \frac{\mu^2e^{\gamma_E}}
             {p_1^2z(1-z)}
      \right]^\epsilon .
    \]

    Keeping this compact form separate from the exact finite-virtuality
    expression makes the point at which the leading-\(p_i^2\) expansion was
    taken explicit.
    """)
    return


@app.cell
def _(
    canonical_zero,
    cut_normalization,
    epsilon,
    euler_gamma,
    massive_bubble_dimreg,
    massive_triangle_dimreg,
    mass_squared,
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

    \[
    \begin{aligned}
    B(p^2) &= \frac{1}{16\pi^2}
      \left[\frac1\epsilon+2+\log\frac{\mu^2}{-p^2}
      +\mathcal O(\epsilon)\right],\\
    B_{\rm cut}(s) &= \frac{1}{8\pi}
      \left[1+\epsilon\left(2+\log\frac{\mu^2}{s}\right)
      +\mathcal O(\epsilon^2)\right],\\
    B_{\rm cutm}(s,m^2) &= -\frac{s-m^2}{8\pi s}
      \left[1+\epsilon\left(2+
      \log\frac{\mu^2s}{(s-m^2)^2}\right)
      +\mathcal O(\epsilon^2)\right].
    \end{aligned}
    \]

    In particular, the retained historical sign convention obeys
    \(B_{\rm cut}(s)=-B_{\rm cutm}(s,0)\).  Both triangle families take
    the common form

    \[
      T=\frac1{4s}\left[1+\epsilon L+
      \frac{\epsilon^2}{2}\left(L^2-\frac{\pi^2}{6}\right)
      +\mathcal O(\epsilon^3)\right],
    \]

    with
    \(L=\log[\mu^2s/(p_1^2p_2^2)]\) for
    \(T_{\rm cut}(p_1^2,p_2^2,-s)\), and
    \(L=\log[\mu^2s^2/(p_i^2(s-m^2)m^2)]\) for
    \(T_{\rm cutm}(p_i^2,s,m^2)\).
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
    uncut_bubble,
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Leading virtuality expansion and endpoint integration

    Write \(v_i=p_i^2\).  After the analytic loop integrations, retain the
    leading-power operator explicitly:

    \[
    \begin{aligned}
      {\rm LP}\,I_4 &=
        a_4(s,z,\epsilon,\mu_R^2)\,
        v_1^{-1-\epsilon}v_2^{-1-\epsilon},\\
      {\rm LP}\,I_3 &=
        a_3(s,z,\epsilon,\mu_R^2)\,
        v_1^{-1-\epsilon}\widehat\delta_\partial(v_2),\\
      {\rm LP}\,I_2 &=
        a_2(s,z,\epsilon,\mu_R^2)\,
        v_2^{-1-\epsilon}\widehat\delta_\partial(v_1),\\
      {\rm LP}\,I_1 &=
        a_1(s,z,\epsilon,\mu_R^2)\,
        \widehat\delta_\partial(v_1)\widehat\delta_\partial(v_2).
    \end{aligned}
    \]

    Here the one-sided cut delta is defined by
    \(\int_0^{\Lambda^2}dv\,\widehat\delta_\partial(v)/(2\pi)=1\).
    This avoids the convention-dependent factor \(1/2\) of an ordinary delta
    placed exactly at the boundary.  Equivalently, retain the PDF's original
    domain \((-\infty,\Lambda^2]\) for delta-supported channels.

    For the continuous singularity,

    \[
      J(\Lambda^2)=
      \int_0^{\Lambda^2}\frac{dv}{2\pi}\,v^{-1-\epsilon}
      =-\frac{(\Lambda^2)^{-\epsilon}}{2\pi\epsilon}.
    \]

    The integral first converges for \({\rm Re}\,\epsilon<0\), followed by
    analytic continuation.  Relative remainders should be written as
    \(1+\mathcal O(v_1/s)+\mathcal O(v_2/s)\), rather than with the same
    scaling as the displayed leading term.  Differentiated cut deltas can
    generate cutoff-boundary contributions, as the PDF notes around
    equations (64)--(68), so those terms must be expanded separately.
    """)
    return


@app.cell
def _(
    S,
    canonical_zero,
    epsilon,
    lambda_squared,
    pi,
    spenso_table,
):
    _virtuality, _a1, _a2, _a3, _a4 = S("v", "a1", "a2", "a3", "a4")
    _antiderivative = -_virtuality ** (-epsilon) / epsilon
    _antiderivative_residual = canonical_zero(
        _antiderivative.derivative(_virtuality)
        - _virtuality ** (-1 - epsilon)
    )
    assert _antiderivative_residual == 0

    _virtuality_factor = -(
        lambda_squared ** (-epsilon) / (2 * pi * epsilon)
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Soft endpoint as a plus distribution

    On \(z\in[0,1]\), define

    \[
      \mathcal D_n(z)=
      \left[\frac{\log^n(1-z)}{1-z}\right]_+,\qquad
      \int_0^1 dz\,\mathcal D_n(z)\,\varphi(z)
      =\int_0^1 dz\,\frac{\log^n(1-z)}{1-z}
       [\varphi(z)-\varphi(1)].
    \]

    The general endpoint identity is

    \[
      (1-z)^{-1-a\epsilon}
      =-\frac{\delta(1-z)}{a\epsilon}
       +\sum_{n=0}^{\infty}
        \frac{(-a\epsilon)^n}{n!}\mathcal D_n(z).
    \]

    The proposed formula is therefore correct for \(a=1\).  The unexpanded
    FLU result in PDF equation (129) contains
    \((1-z)^{d-5}=(1-z)^{-1-2\epsilon}\), so that specific expression needs
    \(a=2\).  Since Symbolica does not natively encode plus distributions, the
    notebook validates the expansion through exact test-function moments.
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
def _(
    E,
    canonical_zero,
    epsilon,
    math,
    soft_distribution_order,
    soft_exponent_multiple,
):
    _a = soft_exponent_multiple.value
    soft_distribution_coefficients = [
        {
            "distribution": "δ(1-z)",
            "coefficient": -1 / (_a * epsilon),
        }
    ]
    soft_distribution_coefficients.extend(
        {
            "distribution": f"D_{_order}(z)",
            "coefficient": (
                (-_a * epsilon) ** _order
                / math.factorial(_order)
            ),
        }
        for _order in range(soft_distribution_order.value + 1)
    )

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
    return soft_distribution_coefficients, soft_distribution_moments


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
    ## Numerical evaluation

    The controls choose a real branch with
    \(s>m^2>0\), \(p_1^2,p_2^2>0\), and a spacelike argument
    \(p^2=-s\) for the uncut bubble.  The values are useful for spot checks;
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
        "unevaluated here; cut 00 remains a direct four-line contribution.",
        kind="neutral",
    )
    return


if __name__ == "__main__":
    app.run()
