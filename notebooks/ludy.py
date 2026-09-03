import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup(hide_code=True):
    import marimo as _marimo
    if __package__:
        from . import typst_marimo as typst_renderer
    else:
        import typst_marimo as typst_renderer

    _marimo.md = typst_renderer.typst_md
    globals()["mo"] = _marimo


@app.cell(hide_code=True)
def _():
    from collections.abc import Sequence
    from dataclasses import dataclass
    from math import prod
    from symbolica import (
        E,
        S,
        N,
        Expression,
        PrintMode,
        Replacement,
    )
    from symbolica.community.spenso import (
        Representation,
        TensorName,
        dot,
    )

    return (
        E,
        Expression,
        N,
        Replacement,
        Representation,
        S,
        Sequence,
        TensorName,
        dataclass,
        dot,
        prod,
    )


@app.cell(hide_code=True)
def _(Representation, S):
    dimension = S("d")
    minkd = Representation.mink(dimension=dimension)
    return dimension, minkd


@app.function(hide_code=True)
def momentum_printer(name):
    """Apply the notebook's keyed-vector naming policy to Spenso vectors."""

    from symbolica import AtomType, PrintMode

    _subscript_translation = str.maketrans(
        "-+0123456789",
        "₋₊₀₁₂₃₄₅₆₇₈₉",
    )

    def _print_momentum(expression, mode, **format_options):
        _custom_modes = format_options.get("custom_print_mode", {})
        _spenso_mode = _custom_modes.get("spenso")
        if not isinstance(_spenso_mode, int):
            return None
        if expression.get_type() != AtomType.Fn:
            return None

        _arguments = tuple(expression)
        if len(_arguments) != 2:
            return None

        if mode == PrintMode.Typst:
            _index = _arguments[0].format(
                mode=PrintMode.Typst,
                color_builtin_symbols=False,
                bracket_level_colors=None,
                show_namespaces=False,
                max_terms=None,
            )
            return f"{name}_({_index})"

        _index = _arguments[0].format(color_builtin_symbols=False)
        if mode == PrintMode.Latex:
            return f"{name}_{{{_index}}}"
        if all(_character in "-+0123456789" for _character in _index):
            return name + _index.translate(_subscript_translation)
        return f"{name}_{{{_index}}}"

    return _print_momentum


@app.cell
def _(TensorName):
    # Symbol attributes and custom printers are registered once per Symbolica
    # process. If this initialization cell is deliberately rerun, restart the
    # Marimo kernel first.
    LOOP_MOMENTUM_TAG = "ludy::loop_momentum"
    p = TensorName.vector("p", print=momentum_printer("p"))
    k = TensorName.vector(
        "k",
        tags=[LOOP_MOMENTUM_TAG],
        print=momentum_printer("k"),
    )
    return k, p


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    = The Drell--Yan crossed-box contribution

    This notebook is a walk-through of the calculations done for all the diagrams necessary for DY and DIS. All of the steps are then reused by the other two, full calculation notebooks.

    Here we compute the cross box contribution. By this, we mean the IR-finite set of FS diagrams arising as rooted cuts of the same routed embedding, with the crossed box serving as one representative. The routed embedding is specified as 6 denominators. The 4 cuts are labeled by which cross box incoming leg is cut by the IS cut (11 is the cross-box).

    We tack on a numerator, and then go through the following pipeline:

    - Partial fractioning (to get rid of dependent denominators)
    - Numerator reduction (to correctly count propagator powers)
    - IBP (using kira)
    - Substituting the analytic cut masters and filtering them according to cut support
    - Expanding at leading power in the incoming virtualities
    - Integrating the incoming virtualities $p_1^2$ and $p_2^2$
    - Expanding around the soft endpoint ($z=1$) in $delta(1-z)$, $cal(D)_0(z) = lr([frac(1, 1-z)])_+$, and $cal( D)_1(z)=lr([frac(log(1-z), 1-z)])_+$
    - Summing the four rooted cuts
    """)
    return


@app.cell(hide_code=True)
def _(Expression, dataclass):
    import json as _json
    import string as _string
    from symbolica.community.spenso import (
        format_tensor as _spenso_format_tensor,
        to_typst as _spenso_to_typst,
    )

    def _typst_math(expression):
        try:
            return _spenso_to_typst(expression, show_dimensions=False)
        except TypeError as error:
            _to_typst = getattr(expression, "to_typst", None)
            if not callable(_to_typst):
                raise TypeError(
                    "Typst values must be Symbolica expressions or Spenso objects"
                ) from error
            return _to_typst(show_dimensions=False)

    @dataclass(frozen=True, slots=True)
    class SpensoMath:
        expression: Expression
        font_size: float = 13.0

        @property
        def typst(self):
            return _typst_math(self.expression)

        def _display_(self):
            return typst_renderer.typst_html(
                f"$ {self.typst} $",
                font_size=self.font_size,
            )

        def __repr__(self):
            return _spenso_format_tensor(
                self.expression,
                show_dimensions=False,
            )

    @dataclass(frozen=True, slots=True)
    class TypstFragment:
        source: str
        font_size: float = 13.0

        @classmethod
        def from_template(cls, template, values, font_size=13.0):
            formatter = _string.Formatter()
            source = []
            used = set()
            for literal, field_name, format_spec, conversion in formatter.parse(
                template
            ):
                if literal:
                    source.append(f"#text({_json.dumps(literal, ensure_ascii=False)})")
                if field_name is None:
                    continue
                if conversion is not None:
                    raise ValueError("Typst expression placeholders do not support conversions")
                if field_name not in values:
                    raise KeyError(f"Missing Typst template value: {field_name}")
                value = values[field_name]
                used.add(field_name)
                if isinstance(value, SpensoMath):
                    value = value.expression
                math = _typst_math(value)
                if format_spec in ("", "inline"):
                    source.append(f"${math}$")
                elif format_spec in ("display", "block"):
                    source.append(f"\n$ {math} $\n")
                else:
                    raise ValueError(
                        "Typst expression format must be inline or display"
                    )
            unused = set(values) - used
            if unused:
                raise ValueError(
                    "Unused Typst template values: " + ", ".join(sorted(unused))
                )
            return cls("".join(source), font_size=font_size)

        def _display_(self):
            return typst_renderer.typst_html(
                self.source,
                font_size=self.font_size,
            )

        def __repr__(self):
            return self.source

    return SpensoMath, TypstFragment


@app.cell(hide_code=True)
def _(TypstFragment):
    def typst(template, /, *, font_size=13.0, **expressions):
        """Render escaped prose with typed Symbolica expression placeholders."""

        return TypstFragment.from_template(
            template,
            expressions,
            font_size=font_size,
        )

    return (typst,)


@app.function(hide_code=True)
def spenso_table(data, **kwargs):
    """Render scalar and tensor expressions in one virtualized table.

    Typst and MathML styles are emitted once beside the table rather than
    serialized into every formatted cell. Nonessential controls are disabled
    by default; callers can override every Marimo table option explicitly.
    """

    from html import escape

    import marimo as mo
    from symbolica import Expression
    from symbolica.community.spenso import to_typst as spenso_to_typst

    def is_typst_value(value):
        return isinstance(value, Expression) or callable(
            getattr(value, "to_typst", None)
        )

    def typst_source(value):
        if isinstance(value, Expression):
            return spenso_to_typst(value, show_dimensions=False)
        return value.to_typst(show_dimensions=False)

    def expression_html(expression, *, include_styles=True):
        return mo.Html(
            typst_renderer.render_typst_html(
                f"$ {typst_source(expression)} $",
                font_size=13.0,
                include_styles=include_styles,
            )
        )

    def contains_expression(value):
        return is_typst_value(value) or (
            isinstance(value, (list, tuple))
            and any(contains_expression(item) for item in value)
        )

    def sequence_cell(values, *, include_styles=True):
        opening, closing = (
            ("(", ")") if isinstance(values, tuple) else ("[", "]")
        )
        parts = []
        for index, value in enumerate(values):
            if index:
                parts.append('<span aria-hidden="true">,</span>')
            if is_typst_value(value):
                parts.append(
                    expression_html(
                        value,
                        include_styles=include_styles,
                    ).text
                )
            elif isinstance(value, (list, tuple)) and contains_expression(value):
                parts.append(
                    sequence_cell(
                        value,
                        include_styles=include_styles,
                    ).text
                )
            else:
                parts.append(f"<span>{escape(str(value))}</span>")
        return mo.Html(
            '<div style="display: inline-flex; align-items: baseline; '
            'gap: 0.25rem; white-space: nowrap">'
            f"<span>{opening}</span>{''.join(parts)}<span>{closing}</span>"
            "</div>"
        )

    def table_value(value, *, include_styles=True):
        if is_typst_value(value):
            return expression_html(value, include_styles=include_styles)
        if isinstance(value, (list, tuple)) and contains_expression(value):
            return sequence_cell(value, include_styles=include_styles)
        return value

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
            lambda value: table_value(value, include_styles=False)
        )
        for column in columns
    }
    kwargs.setdefault("selection", None)
    kwargs.setdefault("show_download", False)
    kwargs.setdefault("show_search", False)
    kwargs.setdefault("show_data_types", False)
    return mo.vstack(
        [
            mo.Html(typst_renderer.typst_shared_css()),
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


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class Integrand:
    """An editable numerator and an ordered list of denominator factors."""

    numerator: "Expression"
    denominators: "list[Expression]"

    def as_expression(self) -> "Expression":
        from math import prod

        return self.numerator / prod(self.denominators)


@app.class_definition(hide_code=True)
@__import__("dataclasses").dataclass(slots=True)
class ApartTerm:
    """One native ``apart`` term mapped back to graph propagators."""

    coefficient: "Expression"
    retained_indices: tuple[int, ...]
    integrand: "Integrand"

    @property
    def denominators(self) -> "tuple[Expression, ...]":
        """Return retained denominators for kernel-only adapter consumers."""

        return tuple(self.integrand.denominators)


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class ReducedIntegralTerm:
    """One coefficient times an integral-index vector in a fixed basis."""

    coefficient: "Expression"
    propagators: "list[Expression]"
    integral_indices: tuple[int, ...]

    def as_expression(self) -> "Expression":
        from math import prod

        return self.coefficient / prod(
            propagator**index
            for propagator, index in zip(
                self.propagators, self.integral_indices, strict=True
            )
        )

    def as_integrand(self) -> "Expression":
        """Return this term as an ordinary rational integrand."""

        return self.as_expression()

    def as_family_integral(self, family_name: str) -> "Expression":
        """Return this term as a coefficient times one family atom."""

        from symbolica import S

        return self.coefficient * S(family_name)(*self.integral_indices)


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class NumeratorReduction:
    """A numerator rewritten in one independent propagator basis."""

    terms: "list[ReducedIntegralTerm]"
    relations: "list[tuple[Expression, Expression]]"
    reduced_numerator: "Expression"
    numerator: "Expression"
    denominators: "tuple[Expression, ...]"
    base_integral_indices: tuple[int, ...]

    def reconstructed_integrand(self) -> "Expression":
        """Sum every shifted-index term back into an ordinary integrand."""

        from symbolica import E

        return sum((term.as_integrand() for term in self.terms), E("0"))

    def input_integrand(self) -> "Expression":
        """Return the numerator over its original denominator powers."""

        from math import prod

        return self.numerator / prod(
            denominator**index
            for denominator, index in zip(
                self.denominators,
                self.base_integral_indices,
                strict=True,
            )
        )

    def family_expression(self, family_name: str) -> "Expression":
        """Return all shifted terms in one named integral family."""

        from symbolica import E

        return sum(
            (term.as_family_integral(family_name) for term in self.terms),
            E("0"),
        )

    @property
    def reconstruction_residual(self) -> "Expression":
        """Return the exact difference between reconstructed and input forms."""

        return normalize_rational(
            self.reconstructed_integrand() - self.input_integrand()
        )


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class IntegralContribution:
    """One native Python contribution ready to become an IBP target."""

    source_indices: tuple[int, ...]
    propagators: "list[Expression]"
    integral_indices: tuple[int, ...]
    coefficient: "Expression"

    def as_expression(self) -> "Expression":
        from math import prod

        return self.coefficient / prod(
            propagator**index
            for propagator, index in zip(
                self.propagators, self.integral_indices, strict=True
            )
        )


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class IBPReductionTerm:
    """One family integral together with its exact reduced right-hand side."""

    project_key: tuple[str, tuple[int, ...]]
    coefficient: "Expression"
    target: "Expression"
    reduced_integral: "Expression"

    def input_expression(self) -> "Expression":
        return self.coefficient * self.target

    def reduced_expression(self) -> "Expression":
        return self.coefficient * self.reduced_integral


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class PreIBPResult:
    """All exact intermediate data at the cross-box IBP boundary."""

    denominators: "list[Expression]"
    loop_scalar_products: "list[Expression]"
    delta: "Expression"
    integrand: "Integrand"
    apart_expression: "Expression"
    apart_terms: "list[ApartTerm]"
    numerator_reductions: "list[NumeratorReduction]"
    contributions: "list[IntegralContribution]"


@app.function
def square(momentum: "Expression") -> "Expression":
    """Return a Spenso scalar square without imposing kinematics."""

    from symbolica.community.spenso import dot

    return dot(momentum, momentum)


@app.function
def gamma_trace_to_dots(
    vectors,
    lorentz_labels,
    *,
    lorentz_dimension,
):
    """Close and simplify one even Dirac trace to native Spenso dots.

    ``vectors`` and ``lorentz_labels`` describe one gamma factor per position.
    A vector contracts that gamma into a slash; ``None`` leaves its Lorentz
    index available to contract with a repeated label elsewhere in the chain.
    """

    from symbolica import E
    from symbolica.community.idenso import (
        simplify_gamma,
        simplify_metrics,
        to_dots,
    )
    from symbolica.community.spenso import Representation, TensorName

    vectors = list(vectors)
    lorentz_labels = list(lorentz_labels)
    if not vectors:
        raise ValueError("A Dirac trace needs at least one gamma factor")
    if len(vectors) != len(lorentz_labels):
        raise ValueError("Each gamma factor needs one Lorentz label")
    if len(vectors) % 2:
        raise ValueError("This helper expects an even closed Dirac trace")
    if any(
        vector is not None and not callable(vector)
        for vector in vectors
    ):
        raise TypeError("Slashed vectors must be callable Spenso expressions")

    minkowski = Representation.mink(dimension=lorentz_dimension)
    bispinor = Representation.bis(4)
    gamma = TensorName.gamma()(bispinor, bispinor, minkowski)
    trace_expression = E("1")
    chain_length = len(vectors)
    for index, (vector, label) in enumerate(
        zip(vectors, lorentz_labels, strict=True)
    ):
        lorentz_slot = minkowski(label)
        trace_expression *= gamma(
            bispinor(index),
            bispinor((index + 1) % chain_length),
            lorentz_slot,
        ).to_expression()
        if vector is not None:
            trace_expression *= vector(lorentz_slot).to_expression()

    return to_dots(
        simplify_metrics(
            simplify_gamma(trace_expression).expand()
        ).expand()
    ).expand()


@app.function
def propagator_denominators(
    propagators: "Sequence[tuple[Expression, Expression]]",
) -> "list[Expression]":
    """Convert ordered ``(momentum, mass_squared)`` pairs to denominators."""

    return [
        square(momentum) - mass_squared
        for momentum, mass_squared in propagators
    ]


@app.function
def find_loop_propagator_indices(
    propagators: "Sequence[tuple[Expression, Expression]]",
    *,
    loop_tag: str = "ludy::loop_momentum",
) -> list[int]:
    """Find propagators whose momentum contains a tagged loop momentum."""

    return [
        index
        for index, (momentum, _mass_squared) in enumerate(propagators)
        if any(
            loop_tag in symbol.get_tags()
            for symbol in momentum.get_all_symbols(
                include_function_symbols=True
            )
        )
    ]


@app.function(hide_code=True)
def project_cutset(
    cutset: "Sequence[int]",
    propagator_indices: "Sequence[int]",
) -> tuple[int, ...]:
    """Project one graph-level cut mask onto an ordered propagator subset."""

    if any(value not in (0, 1) for value in cutset):
        raise ValueError("Cut masks must contain only zeroes and ones")
    if len(set(propagator_indices)) != len(propagator_indices):
        raise ValueError("Projected propagator indices must be unique")
    if any(index < 0 or index >= len(cutset) for index in propagator_indices):
        raise IndexError("Projected propagator index is out of range")
    return tuple(cutset[index] for index in propagator_indices)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 1. Physical kinematics, topology, masses, and cuts

    For an oriented line with momentum $ell_i$ and mass $m_i$, write

    $ D_i = ell_i^2-m_i^2. $

    The six crossed-box lines are

    $
      (ell_i,m_i^2) = (
        (p_1,0),
        (p_2,0),
        (k,0),
        (k-p_1,0),
        (p_2-k,0),
        (p_1+p_2-k,q^2)
      ).
    $

    The first two denominators carry the incoming virtualities. The loop
    family is $(D_3,D_4,D_5,D_6)$. With
    $s=2p_1 dot p_2$, $z=q^2/s$, and
    $Delta=q^2-s$, the four discontinuities are

    $
      c_(11)&=(1,1,1,0,0,1), &
      c_(10)&=(1,0,1,0,1,1), \
      c_(01)&=(0,1,1,1,0,1), &
      c_(00)&=(0,0,1,1,1,1).
    $

    Each entry records the discontinuity of the corresponding physical line.
    These data determine the scalar integrand and its four cut sectors.
    """)
    return


@app.cell
def _(
    N,
    S,
    dimension,
    dot,
    find_loop_propagator_indices,
    k,
    minkd,
    p,
    project_cutset,
    propagator_denominators,
    square,
):
    p1 = p(1, minkd)
    p2 = p(2, minkd)
    k1 = k(1, minkd)
    q = S("q")


    propagators = [
        (p1, N(0)),
        (p2, N(0)),
        (k1, N(0)),
        (k1 - p1, N(0)),
        (p2 - k1, N(0)),
        (
            p1 + p2 - k1,
            q**2,
        ),
    ]
    cutsets = {
        "11": (1, 1, 1, 0, 0, 1),
        "10": (1, 0, 1, 0, 1, 1),
        "01": (0, 1, 1, 1, 0, 1),
        "00": (0, 0, 1, 1, 1, 1),
    }
    denominators = propagator_denominators(propagators)
    loop_propagator_indices = find_loop_propagator_indices(
        propagators
    )
    loop_denominators = [
        denominators[_index]
        for _index in loop_propagator_indices
    ]
    projected_cutsets = {
        _name: project_cutset(_mask, loop_propagator_indices)
        for _name, _mask in cutsets.items()
    }

    physical_numerator = gamma_trace_to_dots(
        [p1, None, k1 - p1, None, p2, None, k1 - p2, None],
        [
            "rho1",
            "sigma",
            "rho2",
            "mu",
            "rho3",
            "sigma",
            "rho4",
            "mu",
        ],
        lorentz_dimension=dimension,
    )

    loop_scalar_products = [
        square(k1),
        dot(k1, p1),
        dot(k1, p2),
    ]
    delta = q**2 - 2 * dot(p1, p2)
    return (
        cutsets,
        delta,
        denominators,
        k1,
        loop_denominators,
        loop_propagator_indices,
        loop_scalar_products,
        p1,
        p2,
        physical_numerator,
        projected_cutsets,
        propagators,
        q,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 2. Dirac trace and physical projector

    The metric-contracted crossed-box trace is

    $ upright("Tr") [
      cancel(p_1) gamma^sigma (cancel(k) - cancel(p_1)) gamma^mu
      cancel(p_2) gamma_sigma (cancel(k) - cancel(p_2)) gamma_mu
    ]. $

    Introduce $x=k^2$, $a=k dot p_1$, $b=k dot p_2$,
    $c=p_1 dot p_2$, $u=p_1^2$, and $v=p_2^2$. Clifford reduction gives

    $
      N_("xbox") = 4(d-2) [
        (d-8) x c + 4c(a+b) + (8-2d)a b
        +(d-4)(a v+b u) +(4-d)u v - 4c^2
      ].
    $

    Couplings, colour factors, spin and colour averages, the graph phase, and
    the observable normalization multiply this scalar contribution in the
    physical coefficient.
    """)
    return


@app.cell
def _(Expression, Integrand, loop_denominators, physical_numerator):
    user_numerator = None

    if user_numerator is not None and not isinstance(
        user_numerator,
        Expression,
    ):
        raise TypeError("user_numerator must be a native Symbolica Expression")
    worked_numerator = (
        physical_numerator if user_numerator is None else user_numerator
    )
    using_physical_numerator = user_numerator is None
    integrand = Integrand(
        numerator=worked_numerator,
        denominators=loop_denominators,
    )
    return integrand, using_physical_numerator, worked_numerator


@app.cell(hide_code=True)
def _(
    cutsets,
    denominators,
    integrand,
    loop_propagator_indices,
    mo,
    physical_numerator,
    projected_cutsets,
    propagators,
    typst,
    using_physical_numerator,
    worked_numerator,
):
    mo.vstack(
        [
            spenso_table(
                [
                    {
                        "propagator": f"D{_index + 1}",
                        "momentum": _momentum,
                        "mass squared": _mass_squared,
                        "denominator": denominators[_index],
                        "loop dependent": (
                            _index in loop_propagator_indices
                        ),
                        **{
                            f"cut {_name}": _mask[_index]
                            for _name, _mask in cutsets.items()
                        },
                    }
                    for _index, (_momentum, _mass_squared) in enumerate(
                        propagators
                    )
                ]
            ),
            mo.md("=== Dirac-trace reduction"),
            spenso_table(
                [
                    {
                        "identity": "Clifford algebra and Lorentz contractions",
                        "physical numerator": physical_numerator,
                    }
                ]
            ),
            spenso_table(
                [
                    {
                        "worked numerator": worked_numerator,
                        "source": (
                            "metric-contracted trace"
                            if using_physical_numerator
                            else "chosen scalar numerator"
                        ),
                    }
                ]
            ),
            spenso_table(
                [
                    {
                        "cut": _name,
                        "full six-line mask": _mask,
                        "loop-line cut mask": (
                            projected_cutsets[_name]
                        ),
                    }
                    for _name, _mask in cutsets.items()
                ]
            ),
            typst(
                "Crossed-box scalar integrand:\n{integrand:display}",
                integrand=integrand.as_expression(),
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 3. Denominator decomposition and numerator reduction

    The four loop denominators span the three scalar products

    $ x=(k^2,k dot p_1,k dot p_2) $

    and obey the affine relation

    $ D_3-D_4-D_5+D_6+Delta=0. $

    Their multivariate partial-fraction identity is

    $
      frac(1,D_3D_4D_5D_6)
      = frac(1,Delta) [
        -frac(1,D_3D_4D_5)
        +frac(1,D_3D_4D_6)
        +frac(1,D_3D_5D_6)
        -frac(1,D_4D_5D_6)
      ].
    $

    Multiplication by $N_("xbox")$ gives four three-denominator children. Each
    child has an independent denominator basis for the three loop scalar
    products, which turns every numerator monomial into an integral-index shift.
    """)
    return


@app.function
def normalize_rational(expression: "Expression") -> "Expression":
    """Return a canonical expanded rational expression."""

    return expression.expand().together().cancel()


@app.function
def replace_all(
    expression: "Expression",
    rules: "Sequence[tuple[Expression, Expression | int]]",
) -> "Expression":
    """Apply an ordered sequence of exact replacements."""

    result = expression
    for source, target in rules:
        result = result.replace(source, target)
    return result


@app.function
def apart_integrand(
    integrand: "Integrand",
    *,
    loop_scalar_products: "Sequence[Expression]",
) -> "tuple[Expression, list[ApartTerm]]":
    """Delegate to Symbolica ``apart`` and restore graph provenance."""

    from math import prod
    from symbolica import E

    denominators = list(integrand.denominators)
    loop_scalar_products = list(loop_scalar_products)
    if len(denominators) < 2:
        raise ValueError("Multivariate apart needs at least two denominators")
    if not loop_scalar_products:
        raise ValueError("Multivariate apart needs explicit loop variables")
    if len(set(loop_scalar_products)) != len(loop_scalar_products):
        raise ValueError("Loop variables for apart must be unique")

    kernel = E("1") / prod(denominators)
    apart_expression = kernel.apart(*loop_scalar_products)
    if normalize_rational(apart_expression - kernel) != E("0"):
        raise ValueError("Symbolica apart did not reconstruct the input kernel")

    grouped_coefficients = {}
    for term_number, term in enumerate(apart_expression.terms(), start=1):
        matches = []
        for omitted_index in range(len(denominators)):
            retained_indices = tuple(
                index
                for index in range(len(denominators))
                if index != omitted_index
            )
            retained_denominators = [
                denominators[index] for index in retained_indices
            ]
            coefficient = (
                term * prod(retained_denominators)
            ).together().cancel()
            if not any(
                coefficient.contains(loop_product)
                for loop_product in loop_scalar_products
            ):
                matches.append((retained_indices, coefficient))
        if len(matches) != 1:
            raise ValueError(
                f"Symbolica apart term {term_number} maps to "
                f"{len(matches)} graph bases; expected exactly one"
            )
        retained_indices, coefficient = matches[0]
        grouped_coefficients.setdefault(retained_indices, []).append(
            coefficient
        )

    expected_bases = {
        tuple(
            index
            for index in range(len(denominators))
            if index != omitted_index
        )
        for omitted_index in range(len(denominators))
    }
    if set(grouped_coefficients) != expected_bases:
        raise ValueError(
            "Symbolica apart did not produce every one-propagator-omitted basis"
        )

    terms = []
    for retained_indices in sorted(grouped_coefficients):
        retained_denominators = [
            denominators[index] for index in retained_indices
        ]
        coefficient = normalize_rational(
            sum(grouped_coefficients[retained_indices], E("0"))
        )
        terms.append(
            ApartTerm(
                coefficient=coefficient,
                retained_indices=retained_indices,
                integrand=Integrand(
                    numerator=(integrand.numerator * coefficient).cancel(),
                    denominators=retained_denominators,
                ),
            )
        )
    reconstruction = normalize_rational(
        sum((term.integrand.as_expression() for term in terms), E("0"))
        - integrand.as_expression()
    )
    if reconstruction != E("0"):
        raise ValueError(
            "Graph-labelled apart terms do not reconstruct the integrand"
        )
    return apart_expression, terms


@app.function
def apart_kernel(
    denominators: "Sequence[Expression]",
    *,
    loop_scalar_products: "Sequence[Expression]",
) -> "tuple[Expression, tuple[ApartTerm, ...]]":
    """Apply ``apart`` to a unit-numerator kernel with graph provenance."""

    from symbolica import E

    expression, terms = apart_integrand(
        Integrand(numerator=E("1"), denominators=list(denominators)),
        loop_scalar_products=loop_scalar_products,
    )
    return expression, tuple(terms)


@app.cell
def _(apart_integrand, integrand, loop_scalar_products):
    _, apart_terms = apart_integrand(
        integrand,
        loop_scalar_products=loop_scalar_products,
    )
    return (apart_terms,)


@app.cell(hide_code=True)
def _(apart_terms, loop_denominators, mo):
    mo.vstack(
        [
            mo.md("=== Partial-fraction terms"),
            spenso_table(
                [
                    {
                        "term": _term_number,
                        "omitted propagator": next(
                            _index + 3
                            for _index in range(len(loop_denominators))
                            if _index not in _child.retained_indices
                        ),
                        "coefficient": _child.coefficient,
                        "retained propagators": tuple(
                            _index + 3 for _index in _child.retained_indices
                        ),
                        "child numerator": _child.integrand.numerator,
                        "child term": _child.integrand.as_expression(),
                    }
                    for _term_number, _child in enumerate(
                        apart_terms,
                        start=1,
                    )
                ]
            ),
            mo.md(
                "The four terms sum exactly to the original propagator kernel."
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Denominator coordinates

    Each child has three retained denominators, and its numerator depends on
    the three loop products

    $ x = (k^2, k dot p_1, k dot p_2). $

    Each denominator is affine in these variables. Introduce one formal
    coordinate $P_i$ for every retained denominator and solve

    $ D_i(x) = P_i $

    for the components of $x$. This gives the coordinate transformation

    $ [(x_0, f_0(P)), dots, (x_(r-1), f_(r-1)(P))] $

    used in the numerator polynomial.

    For example, for the local basis

    $ D_0 = k^2, quad
      D_1 = (k-p_1)^2, quad
      D_2 = (p_2-k)^2. $

    solving $D_i=P_i$ gives

    $ k^2 = P_0, quad
      k dot p_1 = frac(P_0-P_1+p_1^2, 2), quad
      k dot p_2 = frac(P_0-P_2+p_2^2, 2). $

    The $P_i$ are local denominator coordinates. Equal numbers of denominators,
    coordinates, and loop products make the system square, and a unique solution
    establishes an independent basis. This change of coordinates is understood
    at generic external kinematics. Cut conditions and IBP identities enter in
    the next stage.
    """)
    return


@app.function
def numerator_relations(
    denominators: "Sequence[Expression]",
    denominator_labels: "Sequence[Expression]",
    loop_scalar_products: "Sequence[Expression]",
) -> "list[tuple[Expression, Expression]]":
    """Invert one independent denominator basis.

    Solves ``D_i(loop products) = P_i`` and returns ordered
    ``(loop product, expression in P_i)`` substitution pairs.
    """

    from symbolica import Expression

    if len(denominators) != len(denominator_labels):
        raise ValueError("Each denominator needs exactly one formal label")
    if len(denominators) != len(loop_scalar_products):
        raise ValueError(
            "Choose one independent denominator for each loop scalar product"
        )

    equations = [
        denominator - label
        for denominator, label in zip(
            denominators,
            denominator_labels,
            strict=True,
        )
    ]
    branches = Expression.solve(
        equations,
        loop_scalar_products,
        warn_if_underdetermined=False,
    )
    replacements = (
        [branches[0][loop_product] for loop_product in loop_scalar_products]
        if len(branches) == 1
        else []
    )
    if len(replacements) != len(loop_scalar_products) or any(
        bool(replacement.contains(loop_product))
        for replacement in replacements
        for loop_product in loop_scalar_products
    ):
        raise ValueError("Chosen denominators are not an independent basis")
    return list(zip(loop_scalar_products, replacements, strict=True))


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Numerator powers as integral-index shifts

    An apart-derived child initially has the form

    $ frac(N(k), D_0 D_1 dots D_(r-1)). $

    The reduction has four algebraic steps:

    1. Introduce the local denominator coordinates $P_i$.
    2. Replace every loop scalar product in $N(k)$ by its expression in
       $P_i$ and the external invariants.
    3. Expand the result as a polynomial in $P_0, dots, P_(r-1)$.
    4. Translate each polynomial monomial into one integral-index vector.

    If a monomial is

    $ c P_0^(n_0) dots P_(r-1)^(n_(r-1)), $

    then $P_i$ stands for $D_i$. With original denominator powers $a_i$,

    $ frac(c product_i P_i^(n_i), product_i D_i^(a_i))
      = frac(c, product_i D_i^(a_i-n_i)). $

    For $a_i=1$, $n_i=0$ leaves index one, $n_i=1$ cancels that
    denominator, and $n_i>1$ produces a negative index—a numerator insertion
    in the integral-family convention. The same relation covers repeated and
    absent propagator powers through general values of $a_i$.

    In the example above, a numerator $N=k dot p_1$ becomes

    $ frac(P_0-P_1+p_1^2, 2). $

    Dividing by $D_0 D_1 D_2$ therefore yields three terms with indices

    $ frac(1,2) I(0,1,1)
      - frac(1,2) I(1,0,1)
      + frac(p_1^2,2) I(1,1,1). $

    The shifted indices follow each child's denominator order and map directly
    to the corresponding graph lines. Every loop-momentum dependence is thereby
    carried by family indices, while external invariants remain in the
    coefficients.
    """)
    return


@app.function
def reduce_numerator(
    integrand_or_numerator: "Integrand | Expression",
    denominators: "Sequence[Expression] | None" = None,
    *,
    loop_scalar_products: "Sequence[Expression]",
    base_integral_indices: "Sequence[int] | None" = None,
) -> "NumeratorReduction":
    """Rewrite a numerator as coefficients times shifted integrals.

    Accept either an :class:`Integrand` or a numerator followed by its ordered
    denominators. A label monomial with powers ``n_i`` shifts an original
    denominator index ``a_i`` to ``a_i - n_i``. The default base is one inverse
    power of every denominator.
    """

    from symbolica import E, S

    if isinstance(integrand_or_numerator, Integrand):
        if denominators is not None:
            raise TypeError(
                "Do not pass denominators separately with an Integrand"
            )
        integrand = integrand_or_numerator
    else:
        if denominators is None:
            raise TypeError(
                "A numerator expression requires an ordered denominator basis"
            )
        integrand = Integrand(
            numerator=integrand_or_numerator,
            denominators=list(denominators),
        )

    if len(integrand.denominators) != len(loop_scalar_products):
        raise ValueError(
            "Choose one independent denominator for each loop scalar product"
        )
    if base_integral_indices is None:
        base_indices = (1,) * len(integrand.denominators)
    else:
        base_indices = tuple(int(index) for index in base_integral_indices)
    if len(base_indices) != len(integrand.denominators):
        raise ValueError("One base integral index is required per denominator")

    labels = [
        S("Prop")(index) for index in range(len(integrand.denominators))
    ]
    relations = numerator_relations(
        integrand.denominators,
        labels,
        loop_scalar_products,
    )
    reduced = replace_all(integrand.numerator.expand(), relations).expand()

    terms = []
    polynomial = reduced.to_polynomial(vars=labels)
    for powers, coefficient in polynomial.coefficient_list(labels):
        terms.append(
            ReducedIntegralTerm(
                coefficient=coefficient.to_expression(),
                propagators=integrand.denominators,
                integral_indices=tuple(
                    base - int(power)
                    for base, power in zip(base_indices, powers, strict=True)
                ),
            )
        )
    reduction = NumeratorReduction(
        terms=terms,
        relations=relations,
        reduced_numerator=reduced,
        numerator=integrand.numerator,
        denominators=tuple(integrand.denominators),
        base_integral_indices=base_indices,
    )
    if reduction.reconstruction_residual != E("0"):
        raise ValueError("Numerator reduction did not reconstruct its integrand")
    return reduction


@app.cell
def _(apart_terms, loop_scalar_products, reduce_numerator):
    numerator_reductions = [
        reduce_numerator(
            _child.integrand,
            loop_scalar_products=loop_scalar_products,
        )
        for _child in apart_terms
    ]
    return (numerator_reductions,)


@app.cell(hide_code=True)
def _(apart_terms, mo, numerator_reductions):
    mo.vstack(
        [
            mo.md("=== Denominator-coordinate bases"),
            spenso_table(
                [
                    {
                        "retained propagators": tuple(
                            _index + 3 for _index in _child.retained_indices
                        ),
                        "label": f"Prop({_position})",
                        "propagator": _propagator,
                    }
                    for _child in apart_terms
                    for _position, _propagator in enumerate(
                        _child.integrand.denominators
                    )
                ]
            ),
            mo.md("=== Scalar products in denominator coordinates"),
            spenso_table(
                [
                    {
                        "retained propagators": tuple(
                            _index + 3 for _index in _child.retained_indices
                        ),
                        "loop product": _target,
                        "replacement": _replacement,
                    }
                    for _child, _reduction in zip(
                        apart_terms,
                        numerator_reductions,
                        strict=True,
                    )
                    for _target, _replacement in _reduction.relations
                ]
            ),
            mo.md("=== Numerator polynomials"),
            spenso_table(
                [
                    {
                        "retained propagators": tuple(
                            _index + 3 for _index in _child.retained_indices
                        ),
                        "original numerator": _child.integrand.numerator,
                        "rewritten polynomial": _reduction.reduced_numerator,
                    }
                    for _child, _reduction in zip(
                        apart_terms,
                        numerator_reductions,
                        strict=True,
                    )
                ]
            ),
            mo.md("=== Shifted family integrals"),
            spenso_table(
                [
                    {
                        "retained propagators": tuple(
                            _index + 3 for _index in _child.retained_indices
                        ),
                        "coefficient": _term.coefficient,
                        "integral indices": _term.integral_indices,
                    }
                    for _child, _reduction in zip(
                        apart_terms,
                        numerator_reductions,
                        strict=True,
                    )
                    for _term in _reduction.terms
                ]
            ),
            mo.md(
                "The shifted terms sum exactly to each original child integrand."
            ),
        ]
    )
    return


@app.function
def prepare_pre_ibp(
    *,
    numerator,
    loop_denominators,
    loop_scalar_products,
    loop_propagator_indices,
    delta,
    propagator_powers=None,
):
    """Run native Symbolica apart and numerator preparation for IBP."""

    loop_denominators = list(loop_denominators)
    loop_scalar_products = list(loop_scalar_products)
    loop_propagator_indices = list(loop_propagator_indices)
    propagator_powers = (
        (1,) * len(loop_denominators)
        if propagator_powers is None
        else tuple(int(power) for power in propagator_powers)
    )
    if len(loop_denominators) != len(loop_scalar_products) + 1:
        raise ValueError(
            "Preparing every apart child needs one more denominator than "
            "independent loop scalar products"
        )
    if len(loop_propagator_indices) != len(loop_denominators):
        raise ValueError("Each loop denominator needs one graph-source index")
    if len(propagator_powers) != len(loop_denominators):
        raise ValueError("Each loop denominator needs one propagator power")
    if len(set(loop_propagator_indices)) != len(loop_propagator_indices):
        raise ValueError("Loop graph-source indices must be unique")

    integrand = Integrand(
        numerator=numerator,
        denominators=loop_denominators,
    )
    apart_expression, apart_terms = apart_integrand(
        integrand,
        loop_scalar_products=loop_scalar_products,
    )
    numerator_reductions = [
        reduce_numerator(
            child.integrand,
            loop_scalar_products=loop_scalar_products,
            base_integral_indices=tuple(
                propagator_powers[index]
                for index in child.retained_indices
            ),
        )
        for child in apart_terms
    ]
    contributions = []
    for child, reduction in zip(
        apart_terms,
        numerator_reductions,
        strict=True,
    ):
        global_sources = tuple(
            loop_propagator_indices[index]
            for index in child.retained_indices
        )
        contributions.extend(
            IntegralContribution(
                source_indices=global_sources,
                propagators=term.propagators,
                integral_indices=term.integral_indices,
                coefficient=term.coefficient,
            )
            for term in reduction.terms
        )

    return PreIBPResult(
        denominators=loop_denominators,
        loop_scalar_products=loop_scalar_products,
        delta=delta,
        integrand=integrand,
        apart_expression=apart_expression,
        apart_terms=apart_terms,
        numerator_reductions=numerator_reductions,
        contributions=contributions,
    )


@app.cell
def _(
    delta,
    loop_denominators,
    loop_propagator_indices,
    loop_scalar_products,
    prepare_pre_ibp,
    worked_numerator,
):
    pre_ibp = prepare_pre_ibp(
        numerator=worked_numerator,
        loop_denominators=loop_denominators,
        loop_scalar_products=loop_scalar_products,
        loop_propagator_indices=loop_propagator_indices,
        delta=delta,
    )
    return (pre_ibp,)


@app.function
def partition_cuts(pre_ibp, projected_cutsets):
    """Partition cuts into apart-derived blocks and boundary masters."""

    reducible_cut_names = []
    direct_cut_names = []
    denominator_count = len(pre_ibp.denominators)
    for cut_name, projected_mask in projected_cutsets.items():
        if len(projected_mask) != denominator_count:
            raise ValueError(
                f"Cut {cut_name!r} has {len(projected_mask)} projected entries; "
                f"expected {denominator_count}"
            )
        if any(value not in (0, 1) for value in projected_mask):
            raise ValueError("Projected cut masks must contain zeroes and ones")
        if sum(projected_mask) < denominator_count:
            reducible_cut_names.append(cut_name)
        else:
            direct_cut_names.append(cut_name)
    return reducible_cut_names, direct_cut_names


@app.cell
def _(pre_ibp, projected_cutsets):
    reducible_cut_names, direct_cut_names = partition_cuts(
        pre_ibp,
        projected_cutsets,
    )
    contributions_by_cut = {
        _cut_name: list(pre_ibp.contributions)
        for _cut_name in reducible_cut_names
    }
    spenso_table(
        [
            {
                "cut": _cut_name,
                "retained graph lines": tuple(
                    _source + 1 for _source in _term.source_indices
                ),
                "indices": _term.integral_indices,
            }
            for _cut_name, _terms in contributions_by_cut.items()
            for _term in _terms
        ]
        + [
            {
                "cut": _cut_name,
                "retained graph lines": "all loop propagators",
                "indices": "analytic boundary master",
            }
            for _cut_name in direct_cut_names
        ]
    )
    return (contributions_by_cut,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 4. Integration-by-parts reduction and cut projection

    Each partial-fraction child defines a three-denominator family in the graph
    order inherited from $(D_3,D_4,D_5,D_6)$. For a family $F_alpha$, the IBP
    identities take the form

    $
      I_(alpha,a) = sum_m R_(alpha,a m)(s,q^2,p_1^2,p_2^2,d)
        M_(alpha,m).
    $

    The cut fixes the corresponding incoming squares:
    $p_1^2=p_2^2=0$ for `11`, $p_1^2=0$ for `10`, and
    $p_2^2=0$ for `01`. The `00` sector retains both virtualities and is
    represented by the analytic four-line maximal-cut master $M_(00)(s)$.

    The three-denominator reductions cover the complete index domain
    $\{1,0,-1\}^3$, including every shift generated by the physical numerator.
    """)
    return


@app.cell
def _():
    from pathlib import Path

    from kirapy import Kira

    return Kira, Path


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Integral families for the reducible cuts

    Every three-line subset inherits its momenta and masses from the physical
    graph. The massive line carries $q^2$ whenever $D_6$ belongs to the family.
    The cut-specific on-shell relations determine the scalar products, and the
    cut incidence selects the corresponding master sector.
    """)
    return


@app.function
def build_kira_project(
    *,
    name,
    loop_momenta,
    propagators,
    incoming_momenta,
    kinematic_invariants,
    scalar_products,
    target_indices,
    preferred_master_indices,
    bounds,
    top_level_sectors=(7,),
    symbol_to_replace_by_one=None,
    check_masters=True,
    reconstruct_mass=None,
):
    """Build one Kira project from graph-native momentum and mass data."""

    from kirapy import (
        IntegralFamily,
        KinematicInvariant,
        Kinematics,
        KiraProject,
        Propagator,
        ReductionBounds,
        ScalarProductRule,
    )

    family = IntegralFamily(
        name=name,
        loop_momenta=tuple(loop_momenta),
        propagators=tuple(
            Propagator(momentum, mass_squared)
            for momentum, mass_squared in propagators
        ),
        top_level_sectors=tuple(top_level_sectors),
    )
    r, s, d = bounds
    return KiraProject(
        family=family,
        kinematics=Kinematics(
            incoming_momenta=tuple(incoming_momenta),
            kinematic_invariants=tuple(
                KinematicInvariant(expression, mass_dimension)
                for expression, mass_dimension in kinematic_invariants
            ),
            scalar_products=tuple(
                ScalarProductRule(left, right, value)
                for left, right, value in scalar_products
            ),
            symbol_to_replace_by_one=symbol_to_replace_by_one,
        ),
        targets=tuple(family(*indices) for indices in target_indices),
        bounds=ReductionBounds(
            sectors=tuple(top_level_sectors),
            r=r,
            s=s,
            d=d,
        ),
        preferred_masters=tuple(
            family(*indices) for indices in preferred_master_indices
        ),
        check_masters=check_masters,
        reconstruct_mass=(
            symbol_to_replace_by_one is not None
            if reconstruct_mass is None
            else reconstruct_mass
        ),
    )


@app.function
def build_cut_kira_project(
    *,
    name,
    loop_momenta,
    graph_propagators,
    source_indices,
    cutset,
    incoming_momenta,
    target_indices,
    preferred_master_indices,
    bounds,
    check_masters=True,
):
    """Derive one cut Kira project from full physical graph data."""

    from symbolica import E
    from symbolica.community.spenso import dot

    graph_propagators = tuple(graph_propagators)
    source_indices = tuple(source_indices)
    cutset = tuple(cutset)
    incoming_momenta = tuple(incoming_momenta)
    if len(incoming_momenta) != 2:
        raise ValueError("Cut project construction expects two incoming momenta")
    if len(cutset) != len(graph_propagators):
        raise ValueError("The cut mask must cover every physical graph line")
    if any(bit not in (0, 1) for bit in cutset):
        raise ValueError("Cut masks may contain only zeroes and ones")
    if len(set(source_indices)) != len(source_indices):
        raise ValueError("Kira family graph-source indices must be unique")
    if any(
        index < 0 or index >= len(graph_propagators)
        for index in source_indices
    ):
        raise IndexError("Kira family graph-source index is out of range")

    p1, p2 = incoming_momenta
    p1_squared = dot(p1, p1)
    p2_squared = dot(p2, p2)
    p1_dot_p2 = dot(p1, p2)
    p1_on_shell = bool(cutset[0])
    p2_on_shell = bool(cutset[1])
    family_propagators = tuple(
        graph_propagators[index] for index in source_indices
    )
    massive_scales = tuple(
        mass_squared
        for _momentum, mass_squared in family_propagators
        if mass_squared != E("0")
    )
    if len(set(massive_scales)) > 1:
        raise ValueError(f"Project {name} has multiple internal mass scales")
    mass_scale = massive_scales[0] if massive_scales else None

    invariants = [(p1_dot_p2, 2)]
    if not p1_on_shell:
        invariants.append((p1_squared, 2))
    if not p2_on_shell:
        invariants.append((p2_squared, 2))
    if mass_scale is not None:
        invariants.insert(0, (mass_scale, 2))

    return build_kira_project(
        name=name,
        loop_momenta=loop_momenta,
        propagators=family_propagators,
        incoming_momenta=incoming_momenta,
        kinematic_invariants=tuple(invariants),
        scalar_products=(
            (p1, p1, E("0") if p1_on_shell else p1_squared),
            (p2, p2, E("0") if p2_on_shell else p2_squared),
            (p1, p2, p1_dot_p2),
        ),
        target_indices=target_indices,
        preferred_master_indices=preferred_master_indices,
        bounds=bounds,
        symbol_to_replace_by_one=mass_scale,
        check_masters=check_masters,
        reconstruct_mass=mass_scale is not None,
    )


@app.function
def build_kira_projects(*, k1, p1, p2, q, propagators, cutsets):
    """Build native graph-order Kira projects for every reducible cut."""

    from itertools import combinations, product

    from kirapy import (
        IntegralFamily,
        KinematicInvariant,
        Kinematics,
        KiraProject,
        Propagator,
        ReductionBounds,
        ScalarProductRule,
    )
    from symbolica import E
    from symbolica.community.spenso import dot

    p1_squared = dot(p1, p1)
    p1_dot_p2 = dot(p1, p2)
    p2_squared = dot(p2, p2)
    all_propagators = tuple(
        Propagator(momentum, mass_squared)
        for momentum, mass_squared in propagators
    )
    loop_source_indices = [
        index
        for index, (momentum, _mass_squared) in enumerate(propagators)
        if bool(momentum.contains(k1))
    ]
    family_source_sets = list(combinations(loop_source_indices, 3))
    target_indices = tuple(product((1, 0, -1), repeat=3))
    bounds = ReductionBounds(sectors=(7,), r=9, s=4, d=2)
    projects = {}
    for cut_name, cutset in cutsets.items():
        required_sources = tuple(
            source for source in loop_source_indices if cutset[source]
        )
        if len(required_sources) > 3:
            continue
        for source_indices in family_source_sets:
            has_internal_mass = 5 in source_indices
            invariants = [KinematicInvariant(p1_dot_p2, 2)]
            scalar_products = [
                ScalarProductRule(p1, p2, p1_dot_p2)
            ]
            if cutset[0]:
                cut_p1_squared = E("0")
            else:
                cut_p1_squared = p1_squared
                invariants.append(KinematicInvariant(p1_squared, 2))
            if cutset[1]:
                cut_p2_squared = E("0")
            else:
                cut_p2_squared = p2_squared
                invariants.append(KinematicInvariant(p2_squared, 2))
            scalar_products[:0] = [
                ScalarProductRule(p1, p1, cut_p1_squared),
                ScalarProductRule(p2, p2, cut_p2_squared),
            ]
            if has_internal_mass:
                invariants.insert(
                    0,
                    KinematicInvariant(q**2, 2),
                )

            family_name = "cut" + cut_name + "_" + "_".join(
                f"d{source + 1}" for source in source_indices
            )
            family = IntegralFamily(
                name=family_name,
                loop_momenta=(k1,),
                propagators=tuple(
                    all_propagators[index] for index in source_indices
                ),
                top_level_sectors=(7,),
            )
            project_key = (cut_name, source_indices)
            cut_master_indices = tuple(
                int(source in required_sources) for source in source_indices
            )
            preferred_masters = (
                (family(*cut_master_indices),)
                if set(required_sources) <= set(source_indices)
                else ()
            )
            projects[project_key] = KiraProject(
                family=family,
                kinematics=Kinematics(
                    incoming_momenta=(p1, p2),
                    kinematic_invariants=tuple(invariants),
                    scalar_products=tuple(scalar_products),
                    symbol_to_replace_by_one=(
                        q**2 if has_internal_mass else None
                    ),
                ),
                targets=tuple(
                    family(*indices) for indices in target_indices
                ),
                bounds=bounds,
                preferred_masters=preferred_masters,
                check_masters=False,
                reconstruct_mass=has_internal_mass,
            )
    return projects


@app.cell
def _(Path, cutsets, k1, p1, p2, propagators, q):
    kira_projects = build_kira_projects(
        k1=k1,
        p1=p1,
        p2=p2,
        q=q,
        propagators=propagators,
        cutsets=cutsets,
    )
    kira_workdir_root = (
        Path(__file__).resolve().parents[1]
        / "runs"
        / "dy-cross-box-physical-kirapy"
    )
    _project_rows = []
    for (_cut_name, _source_indices), _project in sorted(
        kira_projects.items()
    ):
        _project_rows.append(
            {
                "cut": _cut_name,
                "family": _project.family.name,
                "denominator support": tuple(
                    _index + 1 for _index in _source_indices
                ),
                "integrals in reduction domain": len(_project.targets),
                "master basis": tuple(_project.preferred_masters),
            }
        )
    spenso_table(_project_rows)
    return kira_projects, kira_workdir_root


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Cut-family integrands

    For each cut $c$, the numerator-reduced expression is

    $
      cal(I)_c = sum_(alpha,a) C_(c,alpha,a)
        I_(alpha,a).
    $

    The coefficients contain the external invariants and the on-shell relations
    selected by $c$. The sum retains the physical denominator support of every
    family and supplies the left-hand side of the IBP identities.
    """)
    return


@app.cell
def _(Expression, Sequence, replace_all):
    def apply_kinematic_rules(
        expression: Expression,
        rules: Sequence[tuple[Expression, Expression | int]],
    ) -> Expression:
        """Apply an explicit ordered set of kinematic replacements."""

        return replace_all(expression, rules).expand()

    return (apply_kinematic_rules,)


@app.cell
def _(E, p1, p2, square):
    on_shell_rules_by_cut = {
        "11": (
            (square(p1), E("0")),
            (square(p2), E("0")),
        ),
        "10": (
            (square(p1), E("0")),
        ),
        "01": (
            (square(p2), E("0")),
        ),
        "00": (),
    }
    return (on_shell_rules_by_cut,)


@app.function
def contribution_to_kira_expression(
    contribution,
    cut_name: str,
    projects,
):
    """Turn a family/index contribution into an exact Kira integral atom."""

    family = projects[(cut_name, contribution.source_indices)].family
    target = family(*contribution.integral_indices)
    return contribution.coefficient * target


@app.cell
def _(apply_kinematic_rules):
    def assemble_ibp_expression(
        contributions,
        cut_name,
        projects,
        kinematic_rules,
    ):
        """Assemble the on-shell multi-family expression submitted to IBP rules."""

        from symbolica import E

        return sum(
            (
                apply_kinematic_rules(
                    contribution_to_kira_expression(
                        contribution,
                        cut_name,
                        projects,
                    ),
                    kinematic_rules,
                )
                for contribution in contributions
            ),
            E("0"),
        ).expand()

    return (assemble_ibp_expression,)


@app.cell
def _(
    assemble_ibp_expression,
    contributions_by_cut,
    kira_projects,
    on_shell_rules_by_cut,
):
    ibp_inputs_by_cut = {
        _cut_name: assemble_ibp_expression(
            _contributions,
            _cut_name,
            kira_projects,
            on_shell_rules_by_cut[_cut_name],
        )
        for _cut_name, _contributions in contributions_by_cut.items()
    }
    spenso_table(
        [
                    {
                        "cut": _cut_name,
                        "cut-family integrand": _expression,
                    }
            for _cut_name, _expression in ibp_inputs_by_cut.items()
        ]
    )
    return (ibp_inputs_by_cut,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Complete IBP identities

    The twelve three-denominator families supply the coefficients
    $R_(alpha,a m)$ for the full shifted-index domain. Applying these identities
    converts every cut-family integrand into a linear combination of masters
    while preserving its physical cut label and denominator support.
    """)
    return


@app.function
def run_kira_projects(kira, projects, workdir_root):
    """Run or resume all deterministic Kira projects sequentially."""

    doctor = kira.doctor()
    doctor.raise_for_errors()
    reductions = {}
    for project_key in sorted(projects):
        project = projects[project_key]
        reductions[project_key] = kira.reduce(
            family=project.family,
            kinematics=project.kinematics,
            targets=project.targets,
            bounds=project.bounds,
            preferred_masters=project.preferred_masters,
            check_masters=project.check_masters,
            reconstruct_mass=project.reconstruct_mass,
            dimension=project.dimension,
            workdir=workdir_root / project.family.name,
            parallel="physical",
            resume=True,
            require_complete=True,
            timeout=120,
        )
    return doctor, reductions


@app.cell
def _(Kira, kira_projects, kira_workdir_root):
    kira_doctor, kira_reductions = run_kira_projects(
        Kira(),
        kira_projects,
        kira_workdir_root,
    )
    return (kira_reductions,)


@app.cell(hide_code=True)
def _(kira_reductions, mo):
    _kira_status = mo.vstack(
        [
            mo.callout(
                "All twelve three-denominator families have complete IBP "
                "reductions.",
                kind="success",
            ),
            spenso_table(
                [
                    {
                        "family": _result.family_name,
                        "reduced integrals": len(_result.requested_targets),
                        "masters": len(_result.masters),
                        "vanishing integrals": len(_result.zero_integrals),
                    }
                    for _project_key, _result in sorted(
                        kira_reductions.items()
                    )
                ]
            ),
        ]
    )
    _kira_status
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Reduced master coefficients

    Substituting

    $ I_(alpha,a) = sum_m R_(alpha,a m) M_(alpha,m) $

    into $cal(I)_c$ gives

    $ cal(I)_c = sum_(alpha,m) A_(c,alpha,m) M_(alpha,m), quad
      A_(c,alpha,m)=sum_a C_(c,alpha,a)R_(alpha,a m). $

    This form displays each master together with its complete cut-dependent
    coefficient.
    """)
    return


@app.cell
def _(IBPReductionTerm, apply_kinematic_rules):
    def apply_ibp_reductions(
        contributions,
        cut_name,
        projects,
        reductions,
        kinematic_rules,
    ):
        """Apply complete Kira rules term by term without losing provenance."""

        terms = []
        for contribution in contributions:
            project_key = (cut_name, contribution.source_indices)
            project = projects[project_key]
            result = reductions[project_key].require_complete()
            target = project.family(*contribution.integral_indices)
            if target not in result.rules:
                raise ValueError(
                    f"Missing Kira rule for {target.format_plain()}"
                )
            coefficient = apply_kinematic_rules(
                contribution.coefficient,
                kinematic_rules,
            )
            terms.append(
                IBPReductionTerm(
                    project_key=project_key,
                    coefficient=coefficient,
                    target=target,
                    reduced_integral=result.rules[target],
                )
            )
        return terms

    return (apply_ibp_reductions,)


@app.cell
def _(
    E,
    apply_ibp_reductions,
    contributions_by_cut,
    kira_projects,
    kira_reductions,
    normalize_rational,
    on_shell_rules_by_cut,
):
    ibp_terms_by_cut = {
        _cut_name: apply_ibp_reductions(
            _contributions,
            _cut_name,
            kira_projects,
            kira_reductions,
            on_shell_rules_by_cut[_cut_name],
        )
        for _cut_name, _contributions in contributions_by_cut.items()
    }
    master_expressions_by_cut = {
        _cut_name: normalize_rational(
            sum(
                (_term.reduced_expression() for _term in _terms),
                E("0"),
            )
        )
        for _cut_name, _terms in ibp_terms_by_cut.items()
    }
    return ibp_terms_by_cut, master_expressions_by_cut


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Cut projection on the master basis

    Projecting the six-line masks onto $(D_3,D_4,D_5,D_6)$ gives

    $
      c_(11)&=(1,0,0,1), & c_(10)&=(1,0,1,1), \
      c_(01)&=(1,1,0,1), & c_(00)&=(1,1,1,1).
    $

    A reduced master contributes precisely when every required cut line has
    positive exponent. Cuts `11`, `10`, and `01` select masters in the
    three-denominator families. Cut `00` selects the four-line master
    $M_(00)(s)$.
    """)
    return


@app.cell
def _(normalize_rational):
    def cut_filter_masters(
        expression,
        *,
        masters_by_project,
        sources_by_project,
        required_source_indices,
    ):
        """Drop masters incompatible with a cut in global propagator space."""

        from symbolica import E, Replacement

        kept = []
        dropped = []
        replacements = []
        for project_key, masters in sorted(masters_by_project.items()):
            source_indices = sources_by_project[project_key]
            for master in masters:
                powers = tuple(int(argument) for argument in master)
                powers_by_source = dict(
                    zip(source_indices, powers, strict=True)
                )
                survives = all(
                    powers_by_source.get(source_index, 0) > 0
                    for source_index in required_source_indices
                )
                if survives:
                    kept.append((project_key, master))
                else:
                    dropped.append((project_key, master))
                    replacements.append(Replacement(master, E("0")))
        filtered = (
            expression.replace_multiple(replacements, repeat=False)
            if replacements
            else expression
        )
        return normalize_rational(filtered), kept, dropped

    return (cut_filter_masters,)


@app.cell
def _(
    contributions_by_cut,
    cut_filter_masters,
    cutsets,
    kira_reductions,
    loop_propagator_indices,
    master_expressions_by_cut,
):
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
        for _project_key in kira_reductions
    }
    cut_expressions_by_cut = {}
    cut_kept_masters_by_cut = {}
    cut_dropped_masters_by_cut = {}
    for _cut_name in contributions_by_cut:
        _masters_by_project = {
            _project_key: _result.masters
            for _project_key, _result in kira_reductions.items()
            if _project_key[0] == _cut_name
        }
        (
            cut_expressions_by_cut[_cut_name],
            cut_kept_masters_by_cut[_cut_name],
            cut_dropped_masters_by_cut[_cut_name],
        ) = cut_filter_masters(
            master_expressions_by_cut[_cut_name],
            masters_by_project=_masters_by_project,
            sources_by_project=_sources_by_project,
            required_source_indices=(
                required_loop_sources_by_cut[_cut_name]
            ),
        )
    return (
        cut_expressions_by_cut,
        cut_kept_masters_by_cut,
        required_loop_sources_by_cut,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Surviving cut masters

    Each surviving family master is paired with the analytic cut integral that
    has the same denominator support and positive cut exponents. This pairing
    converts the reduced master sum into a closed expression for each cut.
    """)
    return


@app.function
def identify_masters(expression, identifications):
    """Apply explicit analytic identifications to surviving masters."""

    from symbolica import Replacement

    replacements = [
        Replacement(master, value) for master, value in identifications
    ]
    return (
        expression.replace_multiple(replacements, repeat=False)
        if replacements
        else expression
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 5. Analytic master integrals

    Cut `11` contains the massive cut bubble

    $ B_("cutm")(s,m^2) =
      -frac((mu^2 e^(gamma_E))^epsilon,
        8 sqrt(pi) Gamma((d-1)/2) sqrt(s))
      (frac(s-m^2, 2 sqrt(s)))^(d-3). $

    Cuts `10` and `01` contain the corresponding cut triangle

    $ T_("cutm")(p_i^2,s,q^2) =
      frac((mu^2 e^(gamma_E))^epsilon,
        4 Gamma((d-2)/2) s^(d-3))
      [p_i^2 (s-q^2) q^2]^((d-4)/2). $

    The fully cut `00` sector contains the four-line maximal-cut master
    $M_(00)(s)$ multiplied by $N_("xbox")$ evaluated on its cut support.
    The bubble and triangle substitutions give the exact analytic expressions
    for cuts `11`, `10`, and `01`; $M_(00)$ completes cut `00` in the full
    Drell--Yan assembly.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Dimensional-regularization convention

    The analytic formulas use $d$ for the integration dimension,
    $epsilon$ for the dimensional regulator in $d=4-2 epsilon$,
    $mu^2$ for the renormalization scale, and $gamma_E$ for the
    Euler--Mascheroni constant. The common loop factor is

    $ (mu^2 e^(gamma_E))^epsilon, $

    and all master formulas use this convention before the Laurent expansion.
    """)
    return


@app.function(hide_code=True)
def scalar_printer(*, latex: str, typst: str):
    """Build a display-only printer for an otherwise stable scalar name."""

    from symbolica import PrintMode

    def _print_scalar(_expression, mode, **_format_options):
        if mode == PrintMode.Latex:
            return latex
        if mode == PrintMode.Typst:
            return typst
        return None

    return _print_scalar


@app.cell
def _(Expression, S):
    epsilon = S(
        "ep",
        print=scalar_printer(latex=r"\epsilon", typst="epsilon"),
    )
    mu_squared = S(
        "musq",
        print=scalar_printer(latex=r"\mu^{2}", typst="mu^2"),
    )
    euler_gamma = Expression.EULER_GAMMA
    return epsilon, euler_gamma, mu_squared


@app.cell(hide_code=True)
def _(dimension, epsilon, euler_gamma, mu_squared):
    spenso_table(
        [
            {
                "role": "integration dimension",
                "symbol": dimension,
                "relation": "d = 4 − 2ε",
            },
            {
                "role": "dimensional regulator",
                "symbol": epsilon,
                "relation": "d = 4 − 2ε",
            },
            {
                "role": "renormalization scale squared",
                "symbol": mu_squared,
                "relation": "(μ² exp(γ_E))^ε",
            },
            {
                "role": "Euler–Mascheroni constant",
                "symbol": euler_gamma,
                "relation": "γ_E",
            },
        ],
        selection=None,
    )
    return


@app.cell
def _():
    from pathlib import Path as _Path
    import sys as _sys

    _repository_root = str(_Path(__file__).resolve().parents[1])
    if _repository_root not in _sys.path:
        _sys.path.insert(0, _repository_root)

    from calculations.dy.python.masters import (
        massive_cut_bubble,
        massive_cut_triangle,
    )

    return massive_cut_bubble, massive_cut_triangle


@app.cell
def _(
    cut_expressions_by_cut,
    cut_kept_masters_by_cut,
    dimension,
    dot,
    epsilon,
    euler_gamma,
    massive_cut_bubble,
    massive_cut_triangle,
    mu_squared,
    normalize_rational,
    p1,
    p2,
    q,
    required_loop_sources_by_cut,
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
    }
    analytic_identifications_by_cut = {}
    analytic_expressions_by_cut = {}
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
                    "A surviving cut master does not match the physical cut "
                    f"incidence: {_master.format_plain()}"
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
    spenso_table(
        [
            {
                "cut": _cut_name,
                "identified masters": tuple(
                    _master
                    for _project_key, _master in cut_kept_masters_by_cut[
                        _cut_name
                    ]
                ),
                "analytic value": analytic_master_values_by_cut[
                    _cut_name
                ],
                "evaluated expression": analytic_expressions_by_cut[
                    _cut_name
                ],
            }
            for _cut_name in ("11", "10", "01")
        ]
    )
    return analytic_identifications_by_cut, analytic_master_values_by_cut


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 6. Leading virtuality expansion and integration

    Write $v_i=p_i^2$. After the loop integrations, the leading-power parts of
    the four cuts have the common form

    $
      upright("LP") I_(11) &=
        a_(11)(s,z,epsilon,mu^2)
        hat(delta)_partial(v_1) hat(delta)_partial(v_2), \
      upright("LP") I_(10) &=
        a_(10)(s,z,epsilon,mu^2)
        hat(delta)_partial(v_1) v_2^(-1-epsilon), \
      upright("LP") I_(01) &=
        a_(01)(s,z,epsilon,mu^2)
        v_1^(-1-epsilon) hat(delta)_partial(v_2), \
      upright("LP") I_(00) &=
        a_(00)(s,z,epsilon,mu^2)
        v_1^(-1-epsilon) v_2^(-1-epsilon).
    $

    The one-sided cut delta is normalized by

    $ integral_0^(Lambda_i^2) frac(upright(d)v_i,2 pi)
        hat(delta)_partial(v_i)=1. $

    Each continuous incoming virtuality produces

    $
      J_i(Lambda_i^2)
      = integral_0^(Lambda_i^2) frac(upright(d)v_i,2 pi)
          v_i^(-1-epsilon)
      = -frac((Lambda_i^2)^(-epsilon),2 pi epsilon).
    $

    The four cut factors are therefore

    $ w_(11)=1, quad w_(10)=J_2, quad
      w_(01)=J_1, quad w_(00)=J_1J_2. $

    The integrals converge for $upright("Re") epsilon<0$ and define their
    meromorphic continuation in $epsilon$ from that domain.

    These factors turn the analytic cut masters into functions of
    $(s,z,epsilon,mu^2,Lambda_1^2,Lambda_2^2)$.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 7. Endpoint expansion and coefficient assembly

    Define the endpoint distributions by

    $
      cal(D)_n(z)
      = [frac(log^n(1-z),1-z)]_+.
    $

    The distributional identity

    $
      (1-z)^(-1-a epsilon)
      = -frac(delta(1-z),a epsilon)
        + cal(D)_0(z)
        - a epsilon cal(D)_1(z)
        + cal(O)(epsilon^2)
    $

    applies with $a=2$ to cut `11` and with $a=1$ to cuts `10` and `01`.
    Cut `00` contributes directly to $delta(1-z)$. The three analytic sectors
    displayed here and the $M_(00)$ term form the complete crossed-box sum.
    In the full Drell--Yan quark--antiquark assembly, its endpoint components
    join the virtual and direct sectors in the cancellation of the
    $epsilon^(-2)$ and $epsilon^(-1)$ coefficients.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 8. Exact validation

    Exact identities first reconstruct the partial-fraction kernel, the four
    graph-supported children, the numerator polynomials, and the cut-family
    integrands. Their residuals vanish algebraically. For the retained scalar
    numerator $N=1$, cut `11`, the Mathematica/FIRE calculation supplies an
    independent comparison of the partial fractions, family routing, cut
    projection, master identification, and Laurent expansion through
    $epsilon^0$.
    """)
    return


@app.cell
def _(S, dot, p1, p2, square):
    ipp1p1, ipp1p2, ipp2p2 = S(
        "ipp1p1", "ipp1p2", "ipp2p2"
    )
    native_to_historical_kinematics = (
        (square(p1), ipp1p1),
        (dot(p1, p2), ipp1p2),
        (square(p2), ipp2p2),
    )

    def to_historical_kinematics(expression):
        """Translate native Spenso invariants into the historical oracle names."""

        result = expression
        for native, historical in native_to_historical_kinematics:
            result = result.replace(native, historical)
        return result

    return ipp1p2, to_historical_kinematics


@app.cell
def _(Expression, PreIBPResult, normalize_rational):
    def validate_pre_ibp(
        result: PreIBPResult,
    ) -> dict[str, Expression]:
        """Validate every algebraic handoff represented by a pre-IBP result."""

        from math import prod

        from symbolica import E, S

        checks = {
            "denominator relation": normalize_rational(
                result.denominators[0]
                - result.denominators[1]
                - result.denominators[2]
                + result.denominators[3]
                + result.delta
            ),
            "partial-fraction kernel reconstruction": normalize_rational(
                result.apart_expression
                - E("1") / prod(result.denominators)
            ),
            "physical-support partial-fraction reconstruction": normalize_rational(
                sum(
                    (
                        child.integrand.as_expression()
                        for child in result.apart_terms
                    ),
                    E("0"),
                )
                - result.integrand.as_expression()
            ),
            "numerator-rewrite reconstruction": normalize_rational(
                sum(
                    (
                        term.as_expression()
                        for reduction in result.numerator_reductions
                        for term in reduction.terms
                    ),
                    E("0"),
                )
                - result.integrand.as_expression()
            ),
            "cut-family integrand reconstruction": normalize_rational(
                sum(
                    (
                        contribution.as_expression()
                        for contribution in result.contributions
                    ),
                    E("0"),
                )
                - result.integrand.as_expression()
            ),
        }
        for child_index, (child, reduction) in enumerate(zip(
            result.apart_terms,
            result.numerator_reductions,
            strict=True,
        ), start=1):
            labels = [
                S("Prop")(index)
                for index in range(len(child.integrand.denominators))
            ]
            for relation_index, (target, replacement) in enumerate(
                reduction.relations, start=1
            ):
                reconstructed = replacement
                for label, propagator in zip(
                    labels,
                    child.integrand.denominators,
                    strict=True,
                ):
                    reconstructed = reconstructed.replace(label, propagator)
                checks[
                    f"child {child_index} relation {relation_index}"
                ] = normalize_rational(reconstructed - target)

        failures = {
            name: residual
            for name, residual in checks.items()
            if residual != E("0")
        }
        if failures:
            details = ", ".join(
                f"{name}: {value}" for name, value in failures.items()
            )
            raise ValueError(f"Cross-box preprocessing validation failed: {details}")
        return checks

    return (validate_pre_ibp,)


@app.cell
def _(
    E,
    cut_kept_masters_by_cut,
    denominators,
    dimension,
    dot,
    ibp_inputs_by_cut,
    ibp_terms_by_cut,
    k1,
    kira_projects,
    kira_reductions,
    loop_propagator_indices,
    normalize_rational,
    p1,
    p2,
    physical_numerator,
    pre_ibp,
    projected_cutsets,
    required_loop_sources_by_cut,
    square,
    validate_pre_ibp,
):
    _checks = dict(validate_pre_ibp(pre_ibp))
    _k_squared = square(k1)
    _k_dot_p1 = dot(k1, p1)
    _k_dot_p2 = dot(k1, p2)
    _p1_squared = square(p1)
    _p2_squared = square(p2)
    _p1_dot_p2 = dot(p1, p2)
    _expected_trace = 4 * (dimension - 2) * (
        (dimension - 8) * _k_squared * _p1_dot_p2
        + 4 * _p1_dot_p2 * (_k_dot_p1 + _k_dot_p2)
        + (8 - 2 * dimension) * _k_dot_p1 * _k_dot_p2
        + (dimension - 4)
        * (
            _k_dot_p1 * _p2_squared
            + _k_dot_p2 * _p1_squared
        )
        + (4 - dimension) * _p1_squared * _p2_squared
        - 4 * _p1_dot_p2**2
    )
    _checks["metric-contracted physical trace"] = normalize_rational(
        physical_numerator - _expected_trace
    )

    assert len(pre_ibp.apart_terms) == 4
    assert {
        _index
        for _contribution in pre_ibp.contributions
        for _index in _contribution.integral_indices
    } <= {-1, 0, 1}
    assert loop_propagator_indices == [2, 3, 4, 5]
    assert projected_cutsets == {
        "11": (1, 0, 0, 1),
        "10": (1, 0, 1, 1),
        "01": (1, 1, 0, 1),
        "00": (1, 1, 1, 1),
    }
    assert required_loop_sources_by_cut == {
        "11": (2, 5),
        "10": (2, 4, 5),
        "01": (2, 3, 5),
        "00": (2, 3, 4, 5),
    }

    for (_cut_name, _source_indices), _project in kira_projects.items():
        for _actual, _source_index in zip(
            _project.family.propagators,
            _source_indices,
            strict=True,
        ):
            _checks[
                f"cut {_cut_name} sources {_source_indices} D{_source_index + 1}"
            ] = (
                normalize_rational(
                    square(_actual.momentum)
                    - _actual.mass_squared
                    - denominators[_source_index]
                )
            )

    for _cut_name, _terms in ibp_terms_by_cut.items():
        _checks[f"cut {_cut_name} cut-family integrand reconstruction"] = normalize_rational(
            sum((_term.input_expression() for _term in _terms), E("0"))
            - ibp_inputs_by_cut[_cut_name]
        )

    for _cut_name, _kept in cut_kept_masters_by_cut.items():
        _required_sources = required_loop_sources_by_cut[_cut_name]
        _expected_count = sum(
            set(_required_sources) <= set(_source_indices)
            for _project_cut, _source_indices in kira_projects
            if _project_cut == _cut_name
        )
        assert len(_kept) == _expected_count
        for (_project_cut, _source_indices), _master in _kept:
            assert _project_cut == _cut_name
            assert tuple(int(_argument) for _argument in _master) == tuple(
                int(_source in _required_sources)
                for _source in _source_indices
            )

    _native_boundary_expressions = [
        *ibp_inputs_by_cut.values(),
        *(
            _expression
            for _terms in ibp_terms_by_cut.values()
            for _term in _terms
            for _expression in (
                _term.target,
                _term.reduced_integral,
                _term.reduced_expression(),
            )
        ),
        *(
            _expression
            for _result in kira_reductions.values()
            for _expression in (
                *_result.requested_targets,
                *_result.masters,
                *_result.rules.keys(),
                *_result.rules.values(),
            )
        ),
    ]
    _forbidden_aliases = ("ipp1p1", "ipp1p2", "ipp2p2", "kp_")
    _native_boundary_text = [
        *(
            _expression.format_plain()
            for _expression in _native_boundary_expressions
        ),
        *(
            _result.family_name
            for _result in kira_reductions.values()
        ),
    ]
    assert all(
        not any(_alias in _text for _alias in _forbidden_aliases)
        for _text in _native_boundary_text
    )
    _checks["physical graph identities preserved through IBP"] = (
        E("0")
    )
    assert all(_result.complete for _result in kira_reductions.values())
    assert all(_residual == E("0") for _residual in _checks.values())
    native_validation_rows = [
        {"check": _name, "residual": _residual}
        for _name, _residual in _checks.items()
    ]
    return (native_validation_rows,)


@app.cell(hide_code=True)
def _(mo, native_validation_rows):
    mo.vstack(
        [
            mo.md("=== Exact reconstruction identities"),
            spenso_table(native_validation_rows),
            mo.callout(
                "The physical trace, multivariate partial fractions, graph "
                "routing, family integrands, IBP identities, and cut-master "
                "selection satisfy their exact reconstruction equations.",
                kind="success",
            ),
        ]
    )
    return


@app.cell
def _(E, Expression, SpensoMath, mo, typst):
    _gamma_argument = E("3/2-ep")
    _expected_typst = {
        "scalar reciprocal power": "frac(1,pi^2)",
        "gamma reciprocal": 'frac(1,Gamma(3/2-epsilon))',
        "gamma square": 'Gamma(3/2-epsilon)^2',
    }
    _actual_typst = {
        "scalar reciprocal power": SpensoMath(1 / Expression.PI**2).typst,
        "gamma reciprocal": SpensoMath(1 / _gamma_argument.gamma()).typst,
        "gamma square": SpensoMath(_gamma_argument.gamma() ** 2).typst,
    }
    assert _actual_typst == _expected_typst
    _rendered = SpensoMath(1 / _gamma_argument.gamma())._display_()
    _rendered_html = _rendered.text
    assert "<math" in _rendered_html
    _mixed = typst(
        'Mixed prose # $ [] " <script>: {expression}',
        expression=1 / _gamma_argument.gamma(),
    )
    _mixed_html = mo.as_html(_mixed).text
    assert "Mixed prose" in _mixed_html
    assert "<math" in _mixed_html
    assert 'display="block"' not in _mixed_html
    assert "<script>" not in _mixed_html
    try:
        typst("Missing {expression}")
    except KeyError:
        pass
    else:
        raise AssertionError("A missing Typst template value was accepted")
    try:
        typst("No placeholder", expression=E("1"))
    except ValueError as _error:
        assert "Unused Typst template values" in str(_error)
    else:
        raise AssertionError("An unused Typst template value was accepted")
    try:
        typst("Invalid {expression!r}", expression=E("1"))
    except ValueError as _error:
        assert "do not support conversions" in str(_error)
    else:
        raise AssertionError("A Typst template conversion was accepted")
    display_validation_rows = [
        *[
        {
            "check": _name,
            "Typst": _actual_typst[_name],
            "status": "pass",
        }
        for _name in _expected_typst
        ],
        {
            "check": "mixed escaped prose and Symbolica math",
            "Typst": _mixed.source,
            "status": "pass",
        },
    ]
    return (display_validation_rows,)


@app.cell(hide_code=True)
def _(display_validation_rows):
    _ = display_validation_rows
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Affine-family closure tests

    Affine families with two through seven denominators test the general
    multivariate partial-fraction identity. Their coefficients follow directly
    from the defining affine relation. Two numerator examples then verify the
    index-shift formula for unit and general starting powers.
    """)
    return


@app.cell
def _(
    E,
    Integrand,
    S,
    apart_integrand,
    normalize_rational,
    prod,
    reduce_numerator,
):
    _validation_rows = []
    for _count in range(2, 8):
        _loop_products = [
            S(f"validation_x_{_count}_{_index}")
            for _index in range(_count - 1)
        ]
        _delta = S(f"validation_delta_{_count}")
        _numerator = S(f"validation_numerator_{_count}")
        _weights = [
            *[
                E(str((-1) ** _index * (_index + 1)))
                for _index in range(_count - 1)
            ],
            E("1"),
        ]
        _denominators = [
            *_loop_products,
            _delta
            - sum(
                (
                    _weight * _loop_product
                    for _weight, _loop_product in zip(
                        _weights[:-1],
                        _loop_products,
                        strict=True,
                    )
                ),
                E("0"),
            ),
        ]
        _expected_coefficients = [
            _weight / _delta for _weight in _weights
        ]
        _apart_expression, _terms = apart_integrand(
            Integrand(_numerator, _denominators),
            loop_scalar_products=_loop_products,
        )
        assert len(_terms) == _count
        assert normalize_rational(
            _apart_expression - E("1") / prod(_denominators)
        ) == E("0")
        for _term in _terms:
            _omitted_index = next(
                _index
                for _index in range(_count)
                if _index not in _term.retained_indices
            )
            assert normalize_rational(
                _term.coefficient
                - _expected_coefficients[_omitted_index]
            ) == E("0")
        _residual = normalize_rational(
            sum(
                (_term.integrand.as_expression() for _term in _terms),
                E("0"),
            )
            - _numerator / prod(_denominators)
        )
        assert _residual == E("0")
        _validation_rows.append(
            {"case": f"affine partial fractions with N={_count}", "residual": _residual}
        )

    _x = S("validation_x")
    try:
        apart_integrand(
            Integrand(E("1"), [_x, 1 - _x]),
            loop_scalar_products=[],
        )
    except ValueError as _error:
        assert "explicit loop variables" in str(_error)
    else:
        raise AssertionError("An empty apart variable basis was accepted")
    _validation_rows.append(
        {"case": "loop-coordinate basis is nonempty", "residual": E("0")}
    )

    try:
        apart_integrand(
            Integrand(E("1"), [_x, 1 - _x]),
            loop_scalar_products=[_x, _x],
        )
    except ValueError as _error:
        assert "must be unique" in str(_error)
    else:
        raise AssertionError("Duplicate apart variables were accepted")
    _validation_rows.append(
        {"case": "loop-coordinate basis is unique", "residual": E("0")}
    )

    _y = S("validation_y")
    _integrand_reduction = reduce_numerator(
        Integrand(_x + _y, [_x, _y]),
        loop_scalar_products=[_x, _y],
    )
    assert _integrand_reduction.reconstruction_residual == E("0")
    _validation_rows.append(
        {
            "case": "unit starting powers",
            "residual": _integrand_reduction.reconstruction_residual,
        }
    )

    _base_reduction = reduce_numerator(
        _x**2 + _y,
        (_x, _y),
        loop_scalar_products=(_x, _y),
        base_integral_indices=(1, 2),
    )
    _family = S("validation_family")
    _family_residual = normalize_rational(
        _base_reduction.family_expression("validation_family")
        - _family(-1, 2)
        - _family(1, 1)
    )
    assert _base_reduction.reconstruction_residual == E("0")
    assert _family_residual == E("0")
    _validation_rows.append(
        {
            "case": "explicit base powers and family expression",
            "residual": _family_residual,
        }
    )

    apart_validation_rows = _validation_rows
    return (apart_validation_rows,)


@app.cell(hide_code=True)
def _(E, apart_validation_rows):
    assert len(apart_validation_rows) == 10
    assert all(_row["residual"] == E("0") for _row in apart_validation_rows)
    spenso_table(
        [
            {
                "validation": _row["case"],
                "residual": _row["residual"],
            }
            for _row in apart_validation_rows
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Independent scalar preprocessing comparison

    The retained Mathematica calculation gives an independent scalar
    comparison. Its four partial-fraction coefficients, $Delta$ convention,
    sign pattern, and reconstructed integrand agree with the derivation above.
    """)
    return


@app.cell
def _(
    E,
    IntegralContribution,
    Integrand,
    PreIBPResult,
    apart_integrand,
    delta,
    dot,
    loop_denominators,
    loop_propagator_indices,
    loop_scalar_products,
    normalize_rational,
    p1,
    p2,
    q,
    reduce_numerator,
    validate_pre_ibp,
):
    _reference_delta = q**2 - 2 * dot(p1, p2)
    _reference_integrand = Integrand(E("1"), loop_denominators)
    _reference_apart_expression, _reference_children = apart_integrand(
        _reference_integrand,
        loop_scalar_products=loop_scalar_products,
    )
    _reference_reductions = [
        reduce_numerator(
            _child.integrand,
            loop_scalar_products=loop_scalar_products,
        )
        for _child in _reference_children
    ]
    _reference_contributions = []
    for _child, _reduction in zip(
        _reference_children,
        _reference_reductions,
        strict=True,
    ):
        _global_sources = tuple(
            loop_propagator_indices[_index]
            for _index in _child.retained_indices
        )
        _reference_contributions.extend(
            IntegralContribution(
                source_indices=_global_sources,
                propagators=_term.propagators,
                integral_indices=_term.integral_indices,
                coefficient=_term.coefficient,
            )
            for _term in _reduction.terms
        )
    mathematica_reference_pre_ibp = PreIBPResult(
        denominators=loop_denominators,
        loop_scalar_products=loop_scalar_products,
        delta=_reference_delta,
        integrand=_reference_integrand,
        apart_expression=_reference_apart_expression,
        apart_terms=_reference_children,
        numerator_reductions=_reference_reductions,
        contributions=_reference_contributions,
    )

    MATHEMATICA_APART_SLOTS = (
        (1, (2, 3, 4), -1 / _reference_delta),
        (2, (2, 3, 5), 1 / _reference_delta),
        (3, (2, 4, 5), 1 / _reference_delta),
        (4, (3, 4, 5), -1 / _reference_delta),
    )
    _terms_by_sources = {
        _term.source_indices: _term
        for _term in mathematica_reference_pre_ibp.contributions
    }
    assert set(_terms_by_sources) == {
        _sources for _slot, _sources, _coefficient in (
            MATHEMATICA_APART_SLOTS
        )
    }
    assert all(
        _term.integral_indices == (1, 1, 1)
        for _term in _terms_by_sources.values()
    )
    reference_validation = {
        **validate_pre_ibp(mathematica_reference_pre_ibp),
        "Mathematica delta convention": normalize_rational(
            delta - _reference_delta
        ),
        **{
            f"Mathematica apart slot {_slot} coefficient": normalize_rational(
                _terms_by_sources[_sources].coefficient - _expected
            )
            for _slot, _sources, _expected in (
                MATHEMATICA_APART_SLOTS
            )
        },
    }
    assert all(_residual == E("0") for _residual in reference_validation.values())
    scalar_reference_comparison = [
        {
            "Mathematica apart slot": _slot,
            "expected retained lines": tuple(_index + 1 for _index in _sources),
            "derived retained lines": tuple(
                _index + 1
                for _index in _terms_by_sources[_sources].source_indices
            ),
            "expected indices": (1, 1, 1),
            "actual indices": _terms_by_sources[_sources].integral_indices,
            "coefficient residual": normalize_rational(
                _terms_by_sources[_sources].coefficient - _expected
            ),
        }
        for _slot, _sources, _expected in (
            MATHEMATICA_APART_SLOTS
        )
    ]
    return (
        mathematica_reference_pre_ibp,
        reference_validation,
        scalar_reference_comparison,
    )


@app.cell(hide_code=True)
def _(mo, reference_validation, scalar_reference_comparison):
    mo.vstack(
        [
            spenso_table(scalar_reference_comparison),
            spenso_table(
                [
                    {"check": _name, "residual": _residual}
                    for _name, _residual in reference_validation.items()
                ]
            ),
            mo.callout(
                "The four scalar partial-fraction terms, the independent "
                "$Delta$ convention, the sign pattern, and the exact "
                "reconstructions agree with the retained Mathematica result.",
                kind="success",
            ),
        ]
    )
    return


@app.cell
def _(
    E,
    S,
    analytic_identifications_by_cut,
    analytic_master_values_by_cut,
    apply_ibp_reductions,
    assemble_ibp_expression,
    contributions_by_cut,
    cut_filter_masters,
    ipp1p2,
    kira_projects,
    kira_reductions,
    mathematica_reference_pre_ibp,
    normalize_rational,
    on_shell_rules_by_cut,
    q,
    required_loop_sources_by_cut,
    to_historical_kinematics,
):
    mathematica_reference_contributions_by_cut = {
        _cut_name: list(mathematica_reference_pre_ibp.contributions)
        for _cut_name in contributions_by_cut
    }
    mathematica_reference_ibp_inputs_by_cut = {
        _cut_name: assemble_ibp_expression(
            _contributions,
            _cut_name,
            kira_projects,
            on_shell_rules_by_cut[_cut_name],
        )
        for _cut_name, _contributions in (
            mathematica_reference_contributions_by_cut.items()
        )
    }
    mathematica_reference_ibp_terms_by_cut = {
        _cut_name: apply_ibp_reductions(
            _contributions,
            _cut_name,
            kira_projects,
            kira_reductions,
            on_shell_rules_by_cut[_cut_name],
        )
        for _cut_name, _contributions in (
            mathematica_reference_contributions_by_cut.items()
        )
    }
    mathematica_reference_master_expressions_by_cut = {
        _cut_name: normalize_rational(
            sum(
                (_term.reduced_expression() for _term in _terms),
                E("0"),
            )
        )
        for _cut_name, _terms in mathematica_reference_ibp_terms_by_cut.items()
    }

    _sources_by_project = {
        _project_key: _project_key[1]
        for _project_key in kira_projects
    }
    mathematica_reference_cut_expressions_by_cut = {}
    mathematica_reference_kept_masters_by_cut = {}
    _chain_checks = {}
    _source_expression = sum(
        (
            _contribution.as_expression()
            for _contribution in mathematica_reference_pre_ibp.contributions
        ),
        E("0"),
    )
    for _cut_name in contributions_by_cut:
        _mapped = mathematica_reference_contributions_by_cut[_cut_name]
        _chain_checks[f"cut {_cut_name} routing"] = normalize_rational(
            sum((_term.as_expression() for _term in _mapped), E("0"))
            - _source_expression
        )
        _chain_checks[f"cut {_cut_name} cut-family integrand"] = normalize_rational(
            sum(
                (
                    _term.input_expression()
                    for _term in mathematica_reference_ibp_terms_by_cut[
                        _cut_name
                    ]
                ),
                E("0"),
            )
            - mathematica_reference_ibp_inputs_by_cut[_cut_name]
        )
        (
            mathematica_reference_cut_expressions_by_cut[_cut_name],
            mathematica_reference_kept_masters_by_cut[_cut_name],
            _reference_dropped,
        ) = cut_filter_masters(
            mathematica_reference_master_expressions_by_cut[_cut_name],
            masters_by_project={
                _project_key: _result.masters
                for _project_key, _result in kira_reductions.items()
                if _project_key[0] == _cut_name
            },
            sources_by_project=_sources_by_project,
            required_source_indices=(
                required_loop_sources_by_cut[_cut_name]
            ),
        )

    mathematica_reference_analytic_expressions_by_cut = {
        _cut_name: normalize_rational(
            identify_masters(
                mathematica_reference_cut_expressions_by_cut[_cut_name],
                analytic_identifications_by_cut[_cut_name],
            )
        )
        for _cut_name in ("11", "10", "01")
    }
    assert all(_residual == E("0") for _residual in _chain_checks.values())
    mathematica_reference_chain_validation_rows = [
        {"check": _name, "residual": _residual}
        for _name, _residual in _chain_checks.items()
    ]

    mathematica_reference_cut_expression = (
        mathematica_reference_cut_expressions_by_cut["11"]
    )
    cut_bubble = S("Bcutm")(2 * ipp1p2, q**2)
    mathematica_reference_final_expression = to_historical_kinematics(
        normalize_rational(
            identify_masters(
                mathematica_reference_cut_expression,
                [
                    (_master, cut_bubble)
                    for _project_key, _master in (
                        mathematica_reference_kept_masters_by_cut["11"]
                    )
                ],
            )
        )
    )
    mathematica_reference_analytic_expression = to_historical_kinematics(
        mathematica_reference_analytic_expressions_by_cut["11"]
    )
    cut_bubble_analytic = to_historical_kinematics(
        analytic_master_values_by_cut["11"]
    )
    return (
        cut_bubble,
        cut_bubble_analytic,
        mathematica_reference_analytic_expression,
        mathematica_reference_chain_validation_rows,
        mathematica_reference_cut_expression,
        mathematica_reference_final_expression,
    )


@app.cell(hide_code=True)
def _(mathematica_reference_chain_validation_rows):
    spenso_table(mathematica_reference_chain_validation_rows)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Independent scalar master comparison

    The retained calculation uses the scalar numerator $N=1$. Translating its
    loop routing to the six-line graph maps cut `11` to
    $upright("topo20")(1,0,1)$ and $upright("topo22")(1,1,0)$. Both integrals
    represent the same cut bubble. Their exact master coefficient, analytic
    value, and Laurent expansion agree through order $epsilon^0$.
    """)
    return


@app.cell
def _(
    Replacement,
    S,
    ipp1p2,
    kira_projects,
    kira_reductions,
    mathematica_reference_cut_expression,
    q,
    to_historical_kinematics,
):
    FIRE_SOURCE_ORDERS = (
        (2, 3, 5),
        (2, 3, 4),
        (2, 5, 4),
        (3, 5, 4),
    )
    FIRE_FAMILY_BLOCKS = {
        "11": (20, 21, 22, 23),
        "10": (24, 25, 26, 27),
        "01": (28, 29, 30, 31),
    }
    fire_family_oracle = {
        (_cut_name, tuple(sorted(_fire_sources))): {
            "family_id": _family_id,
            "source_order": _fire_sources,
        }
        for _cut_name, _family_ids in FIRE_FAMILY_BLOCKS.items()
        for _family_id, _fire_sources in zip(
            _family_ids,
            FIRE_SOURCE_ORDERS,
            strict=True,
        )
    }
    assert set(fire_family_oracle) == set(kira_projects)

    _fire_replacements = []
    for _project_key, _result in kira_reductions.items():
        _native_sources = _project_key[1]
        _oracle = fire_family_oracle[_project_key]
        _fire_sources = _oracle["source_order"]
        _fire_family = S(f"topo{_oracle['family_id']}")
        for _master in _result.masters:
            _native_indices = tuple(int(_argument) for _argument in _master)
            _fire_indices = tuple(
                _native_indices[_native_sources.index(_source)]
                for _source in _fire_sources
            )
            _fire_replacements.append(
                Replacement(_master, _fire_family(*_fire_indices))
            )
    mathematica_reference_cut_expression_fire = to_historical_kinematics(
        mathematica_reference_cut_expression.replace_multiple(
            _fire_replacements,
            repeat=False,
        )
    )

    _d = S("d")
    _delta = q**2 - 2 * ipp1p2
    _topo20 = S("topo20")
    _topo22 = S("topo22")
    mathematica_scalar_cut_oracle = (
        2
        * (_d - 3)
        * (_topo20(1, 0, 1) + _topo22(1, 1, 0))
        / ((_d - 4) * _delta**2)
    )
    fire_mapping_validation_rows = [
        {
            "cut": _project_key[0],
            "derived family": kira_projects[_project_key].family.name,
            "denominator support": tuple(
                _source + 1 for _source in _project_key[1]
            ),
            "FIRE family": f"topo{_oracle['family_id']}",
            "FIRE propagator order": tuple(
                _source + 1 for _source in _oracle["source_order"]
            ),
        }
        for _project_key, _oracle in sorted(fire_family_oracle.items())
    ]
    return (
        fire_mapping_validation_rows,
        mathematica_reference_cut_expression_fire,
        mathematica_scalar_cut_oracle,
    )


@app.cell
def _(fire_mapping_validation_rows, mathematica_scalar_cut_oracle):
    spenso_table(
        [
            *fire_mapping_validation_rows,
            {
                "cut": "11 (Mathematica label 00)",
                "derived family": "scalar comparison",
                "denominator support": (),
                "FIRE family": "retained expression",
                "FIRE propagator order": mathematica_scalar_cut_oracle,
            },
        ]
    )
    return


@app.cell
def _(
    E,
    S,
    cut_bubble,
    ipp1p2,
    kira_reductions,
    mathematica_reference_cut_expression_fire,
    mathematica_reference_final_expression,
    mathematica_scalar_cut_oracle,
    normalize_rational,
    q,
):
    _d = S("d")
    _delta = q**2 - 2 * ipp1p2
    mathematica_expected_cut_expression = mathematica_scalar_cut_oracle
    mathematica_expected_final_expression = (
        4
        * (_d - 3)
        * cut_bubble
        / ((_d - 4) * _delta**2)
    )
    assert all(
        _result.complete for _result in kira_reductions.values()
    )
    _cut_residual = normalize_rational(
        mathematica_reference_cut_expression_fire
        - mathematica_expected_cut_expression
    )
    _final_residual = normalize_rational(
        mathematica_reference_final_expression
        - mathematica_expected_final_expression
    )
    assert _cut_residual == E("0")
    assert _final_residual == E("0")
    mathematica_ibp_validation_rows = [
        {
            "check": "scalar cut 11 master expression",
            "residual": _cut_residual,
        },
        {
            "check": "scalar cut 11 Bcutm identification",
            "residual": _final_residual,
        },
    ]
    return (
        mathematica_expected_cut_expression,
        mathematica_expected_final_expression,
        mathematica_ibp_validation_rows,
    )


@app.cell
def _(
    E,
    S,
    cut_bubble_analytic,
    dimension,
    epsilon,
    euler_gamma,
    ipp1p2,
    mathematica_reference_analytic_expression,
    mu_squared,
    normalize_rational,
    q,
):
    _s = S("s")
    _delta = q**2 - 2 * ipp1p2
    mathematica_expected_analytic_expression = (
        4
        * (dimension - 3)
        * cut_bubble_analytic
        / ((dimension - 4) * _delta**2)
    )

    _dimensionally_regularized = mathematica_expected_analytic_expression.replace(
        ipp1p2,
        _s / 2,
    ).replace(
        dimension,
        4 - 2 * epsilon,
    )
    _series = _dimensionally_regularized.series(
        epsilon,
        0,
        0,
    ).to_expression().expand()
    _series = _series.replace(
        (euler_gamma.exp() * mu_squared).log(),
        euler_gamma + mu_squared.log(),
    )
    _series = _series.replace(
        (
            (_s - q**2)
            / (2 * _s.sqrt())
        ).log(),
        (
            (_s - q**2)
            / _s.sqrt()
        ).log()
        - E("2").log(),
    )
    mathematica_actual_epsilon_expansion = normalize_rational(_series)
    mathematica_expected_epsilon_expansion = -(
        1
        + epsilon * mu_squared.log()
        - 2
        * epsilon
        * (
            (_s - q**2)
            / _s.sqrt()
        ).log()
    ) / (
        4
        * epsilon
        * E("pi")
        * _s
        * (q**2 - _s)
    )
    _series_residual = normalize_rational(
        mathematica_actual_epsilon_expansion
        - mathematica_expected_epsilon_expansion
    )
    assert _series_residual == E("0")

    _analytic_rows = [
        {
            "check": "Bcutm expansion through epsilon^0",
            "residual": _series_residual,
        }
    ]
    _analytic_residual = normalize_rational(
        mathematica_reference_analytic_expression
        - mathematica_expected_analytic_expression
    )
    assert _analytic_residual == E("0")
    _analytic_rows.insert(
        0,
        {
            "check": "completed analytic scalar result",
            "residual": _analytic_residual,
        },
    )
    mathematica_analytic_validation_rows = _analytic_rows
    return (
        mathematica_analytic_validation_rows,
        mathematica_expected_analytic_expression,
        mathematica_expected_epsilon_expansion,
    )


@app.cell(hide_code=True)
def _(
    mathematica_analytic_validation_rows,
    mathematica_expected_analytic_expression,
    mathematica_expected_cut_expression,
    mathematica_expected_epsilon_expansion,
    mathematica_expected_final_expression,
    mathematica_ibp_validation_rows,
    mo,
    typst,
):
    if not mathematica_ibp_validation_rows:
        _validation_output = mo.vstack(
            [
                spenso_table(mathematica_analytic_validation_rows),
                typst(
                    "Recorded expansion through epsilon^0:\n{expression:display}",
                    expression=mathematica_expected_epsilon_expansion,
                ),
                mo.callout(
                    "The scalar preprocessing and analytic-master comparisons "
                    "cover the retained scalar cut. The twelve cut-family "
                    "identities provide the FIRE and full-chain comparisons.",
                    kind="neutral",
                ),
            ]
        )
    else:
        _validation_output = mo.vstack(
            [
                spenso_table(mathematica_ibp_validation_rows),
                spenso_table(mathematica_analytic_validation_rows),
                typst(
                    "Expected scalar result after the cut:\n{expression:display}",
                    expression=mathematica_expected_cut_expression,
                ),
                typst(
                    "Expected completed scalar result:\n{expression:display}",
                    expression=mathematica_expected_final_expression,
                ),
                typst(
                    "Expected analytic scalar result:\n{expression:display}",
                    expression=mathematica_expected_analytic_expression,
                ),
                typst(
                    "Expansion through epsilon^0:\n{expression:display}",
                    expression=mathematica_expected_epsilon_expansion,
                ),
                mo.callout(
                    "The twelve family reductions are complete. The scalar "
                    "cut-11 reduction, bubble identification, analytic master, "
                    "and $epsilon$ expansion agree exactly with the retained "
                    "Mathematica/FIRE calculation.",
                    kind="success",
                ),
            ]
        )
    _validation_output
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        "Cross-box conclusion: the six-line topology, four cut sectors, physical "
        "Dirac numerator, twelve three-denominator reductions, and analytic "
        "masters form one exact chain for cuts 11, 10, and 01. Cut 00 contributes "
        "through the four-line master M00(s) in the full Drell--Yan assembly. The "
        "leading-virtuality factors and endpoint identity place all four cuts in "
        "the common distribution basis, where they join the remaining physical "
        "graphs and channel normalizations.",
        kind="info",
    )
    return


if __name__ == "__main__":
    app.run()
