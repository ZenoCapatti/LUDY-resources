import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup(hide_code=True):
    from html import escape as _escape_html
    from inspect import cleandoc as _cleandoc
    import re as _re
    from threading import Lock as _Lock

    import marimo as _marimo
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

    # Marimo eagerly renders bare positional ``mo.md(...)`` cells as Markdown
    # only when a regular cell statically exports ``mo``.  Installing the
    # patched module in setup and exposing its conventional name dynamically
    # keeps those cells editable as Markdown while executing this Typst path.
    _marimo.md = typst_md
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
        PrintMode,
        Replacement,
        Representation,
        S,
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
    = DY cross-box: implementation and worked reduction

    This notebook is both the readable source of the reusable helper
    implementations and a complete walkthrough of the cross-box calculation.
    Each transformation is defined where the calculation first needs it. The
    worked graph exercises native multivariate `apart`, numerator reduction,
    Kira IBP reduction, cut filtering, and analytic master
    evaluation; all tests and Mathematica/FIRE comparisons are collected at
    the end.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Rich Symbolica display

    `SpensoMath` keeps the exact native Symbolica expression for algebra while
    rendering its Spenso-aware Typst form as semantic HTML/MathML. Notebook
    prose and expression displays share the same responsive HTML renderer.

    - `spenso_math(expression)` wraps one exact expression for rich output.
    - `typst(template, **expressions)` safely combines prose with inline or
      display mathematics without first converting expressions to strings.
    - `spenso_table(rows)` installs the same renderer for expression-valued
      cells while emitting Typst and MathML styles only once per table.
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
            return typst_html(f"$ {self.typst} $", font_size=self.font_size)

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
            return typst_html(self.source, font_size=self.font_size)

        def __repr__(self):
            return self.source

    return SpensoMath, TypstFragment


@app.cell
def _(Expression, SpensoMath):
    def spenso_math(expression: Expression) -> SpensoMath:
        """Return a rich Marimo display view of an exact Symbolica expression."""

        if not isinstance(expression, Expression):
            raise TypeError("spenso_math expects a Symbolica Expression")
        return SpensoMath(expression)

    return


@app.cell
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
            render_typst_html(
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Data Structures

    `Integrand` is the editable algebraic object. `ApartTerm` records how one
    summand returned by Symbolica maps back to retained graph propagators. The
    later records keep the rewritten numerator terms and finally their global
    graph-source identities. `PreIBPResult` bundles the complete inspectable
    handoff immediately before Kira; it does not contain validation results or
    historical topology labels.
    """)
    return


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class Integrand:
    """An editable numerator and an ordered list of denominator factors."""

    numerator: "Expression"
    denominators: list["Expression"]

    def as_expression(self) -> "Expression":
        from math import prod

        return self.numerator / prod(self.denominators)


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class ApartTerm:
    """One native ``apart`` term mapped back to graph propagators."""

    coefficient: "Expression"
    retained_indices: tuple[int, ...]
    integrand: "Integrand"


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class ReducedIntegralTerm:
    """One coefficient times an integral-index vector in a fixed basis."""

    coefficient: "Expression"
    propagators: list["Expression"]
    integral_indices: tuple[int, ...]

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
class NumeratorReduction:
    """A numerator rewritten in one independent propagator basis."""

    terms: list["ReducedIntegralTerm"]
    relations: list[tuple["Expression", "Expression"]]
    reduced_numerator: "Expression"


@app.class_definition
@__import__("dataclasses").dataclass(slots=True)
class IntegralContribution:
    """One native Python contribution ready to become an IBP target."""

    source_indices: tuple[int, ...]
    propagators: list["Expression"]
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

    denominators: list["Expression"]
    loop_scalar_products: list["Expression"]
    delta: "Expression"
    integrand: "Integrand"
    apart_expression: "Expression"
    apart_terms: list["ApartTerm"]
    numerator_reductions: list["NumeratorReduction"]
    contributions: list["IntegralContribution"]


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
    == 1. Define the cross-box integrand

    The graph input is the ordered list of six `(momentum, mass_squared)`
    pairs. The loop head `k` carries a Symbolica tag, so loop-dependent lines
    are discovered from the expressions themselves. The external squares
    $p_1^2, p_2^2$ specify which incoming legs are cut, but are not sent to an
    IBP reducer as loop propagators.

    The numerator is the paper's metric-contracted trace

    $ upright("Tr") [
      cancel(p_1) gamma^sigma (cancel(k) - cancel(p_1)) gamma^mu
      cancel(p_2) gamma_sigma (cancel(k) - cancel(p_2)) gamma_mu
    ]. $

    `gamma_trace_to_dots` constructs the typed gamma matrices and vectors with
    Spenso, applies Idenso's Clifford and metric simplifiers, and converts the
    result back to native Spenso scalar products. Couplings, colour factors,
    spin/colour averages, the graph sign, and observable normalizations are not
    part of this trace. No on-shell identity or integral-reduction rule has
    been applied here.
    """)
    return


@app.cell
def _(N, S, dimension, dot, gamma_trace_to_dots, k, minkd, p):
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
    integrand = Integrand(
        numerator=physical_numerator,
        denominators=loop_denominators,
    )
    return (
        cutsets,
        delta,
        denominators,
        integrand,
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
            mo.md("=== Spenso/Idenso gamma reduction"),
            spenso_table(
                [
                    {
                        "stage": "simplify_gamma → simplify_metrics → to_dots",
                        "physical numerator": physical_numerator,
                    }
                ]
            ),
            spenso_table(
                [
                    {
                        "Python cut": _name,
                        "full six-line mask": _mask,
                        "inferred loop projection": (
                            projected_cutsets[_name]
                        ),
                    }
                    for _name, _mask in cutsets.items()
                ]
            ),
            typst(
                "Loop integrand before cut or IBP:\n{integrand:display}",
                integrand=integrand.as_expression(),
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 2. Decompose the propagator kernel with Symbolica

    The four loop denominators are affine but not independent. We now delegate
    their multivariate partial-fraction decomposition directly to Symbolica:

    $ A(x) = upright("apart")_(x)
      [frac(1, product_i D_i)], quad
      x = (k^2, k dot p_1, k dot p_2). $

    `Expression.apart(*loop_scalar_products)` performs the multivariate
    Gröbner-basis decomposition. We apply it to the propagator kernel and only
    then attach the physical numerator, so the following numerator-reduction
    step remains explicit instead of being folded into lower-topology contact
    terms.

    Symbolica returns an expression rather than graph metadata.
    `apart_integrand` therefore performs one non-algebraic bookkeeping step:
    for each returned summand, it identifies the unique product of original
    propagators whose cancellation leaves a loop-independent coefficient. It
    does not solve an affine system or construct a decomposition itself.
    """)
    return


@app.function
def normalize_rational(expression: "Expression") -> "Expression":
    """Return a canonical expanded rational expression."""

    return expression.expand().together().cancel()


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


@app.cell
def _(integrand, loop_scalar_products):
    apart_expression, apart_terms = apart_integrand(
        integrand,
        loop_scalar_products=loop_scalar_products,
    )
    return apart_expression, apart_terms


@app.cell(hide_code=True)
def _(apart_terms, loop_denominators, mo):
    mo.vstack(
        [
            mo.md("=== Native multivariate-apart terms"),
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
                "Exact reconstruction is checked in the final validation section."
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 3. Rewrite numerators in each denominator basis

    === `numerator_relations`: invert the denominator coordinates

    After Symbolica's `apart`, each child has three retained denominators and
    its numerator can depend on the three independent loop products

    $ x = (k^2, k dot p_1, k dot p_2). $

    Each denominator is affine in these variables. The helper introduces one
    _formal_ label $P_i$ for every retained denominator and solves

    $ D_i(x) = P_i $

    for the components of $x$. In the code, `denominators` supplies the
    $D_i$, `denominator_labels` supplies the matching $P_i$, and
    `loop_scalar_products` specifies both the unknowns and their returned
    order. The result is an ordered list

    $ [(x_0, f_0(P)), dots, (x_(r-1), f_(r-1)(P))] $

    that can be used directly as substitution rules.

    For example, for the local basis

    $ D_0 = k^2, quad
      D_1 = (k-p_1)^2, quad
      D_2 = (p_2-k)^2. $

    solving $D_i=P_i$ gives

    $ k^2 = P_0, quad
      k dot p_1 = frac(P_0-P_1+p_1^2, 2), quad
      k dot p_2 = frac(P_0-P_2+p_2^2, 2). $

    The $P_i$ are only local bookkeeping variables—created as `Prop(i)`—not
    extra propagators or Kira family names. Requiring equally many
    denominators, labels, and loop products makes the system square; requiring
    exactly one solved branch with no loop product left on the right-hand side
    checks that this particular denominator set is an independent basis.
    This is only a change of algebraic coordinates: no cut condition or IBP
    rule is applied here. If the solution divides by an external invariant, it
    is understood at generic kinematics where that invariant is nonzero.
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
    === `reduce_numerator`: turn numerator factors into index shifts

    An apart-derived child initially has the form

    $ frac(N(k), D_0 D_1 dots D_(r-1)). $

    `reduce_numerator` performs four explicit steps:

    1. Create the local labels $P_i = "Prop"(i)$.
    2. Use `numerator_relations` to replace every chosen loop scalar product in
       $N(k)$ by an expression in those labels and external invariants.
    3. Expand the result as a polynomial in $P_0, dots, P_(r-1)$.
    4. Translate each polynomial monomial into one integral-index vector.

    If a monomial is

    $ c P_0^(n_0) dots P_(r-1)^(n_(r-1)), $

    then $P_i$ stands for $D_i$, while the child started with one inverse
    power of every denominator. Therefore

    $ frac(c product_i P_i^(n_i), product_i D_i)
      = frac(c, product_i D_i^(1-n_i)), quad a_i = 1-n_i. $

    Thus $n_i=0$ leaves index $a_i=1$, $n_i=1$ cancels that denominator
    and gives $a_i=0$, and $n_i>1$ produces a negative index—a numerator
    insertion in the integral-family convention.

    In the example above, a numerator $N=k dot p_1$ becomes

    $ frac(P_0-P_1+p_1^2, 2). $

    Dividing by $D_0 D_1 D_2$ therefore yields three terms with indices

    $ frac(1,2) I(0,1,1)
      - frac(1,2) I(1,0,1)
      + frac(p_1^2,2) I(1,1,1). $

    The returned `NumeratorReduction` keeps all three useful views: `relations`
    records the coordinate change, `reduced_numerator` records the complete
    polynomial, and `terms` records each coefficient together with its shifted
    integral indices. Those indices follow this child's local denominator
    order; the later contribution-building step maps that order back to graph
    propagator positions. The helper assumes that the numerator is polynomial
    in the declared loop products and that they contain all of its loop-momentum
    dependence; external invariants remain in the coefficients. Exact
    reconstruction is checked in the final validation section.
    """)
    return


@app.function
def reduce_numerator(
    integrand: "Integrand",
    *,
    loop_scalar_products: "Sequence[Expression]",
) -> "NumeratorReduction":
    """Rewrite a numerator as coefficients times shifted integrals.

    A label monomial with powers ``n_i`` cancels the corresponding
    denominator powers and therefore produces indices ``1 - n_i``.
    """

    from symbolica import S

    if len(integrand.denominators) != len(loop_scalar_products):
        raise ValueError(
            "Choose one independent denominator for each loop scalar product"
        )
    labels = [
        S("Prop")(index) for index in range(len(integrand.denominators))
    ]
    relations = numerator_relations(
        integrand.denominators,
        labels,
        loop_scalar_products,
    )
    reduced = integrand.numerator.expand()
    for loop_product, replacement in relations:
        reduced = reduced.replace(loop_product, replacement)
    reduced = reduced.expand()

    terms = []
    polynomial = reduced.to_polynomial(vars=labels)
    for powers, coefficient in polynomial.coefficient_list(labels):
        terms.append(
            ReducedIntegralTerm(
                coefficient=coefficient.to_expression(),
                propagators=integrand.denominators,
                integral_indices=tuple(1 - int(power) for power in powers),
            )
        )
    return NumeratorReduction(terms, relations, reduced)


@app.cell
def _(apart_terms, loop_scalar_products):
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
            mo.md("=== Family-local propagator-label bases"),
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
            mo.md("=== Scalar-product relations"),
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
            mo.md("=== Rewritten child numerators"),
            spenso_table(
                [
                    {
                        "retained propagators": tuple(
                            _index + 3 for _index in _child.retained_indices
                        ),
                        "input numerator": _child.integrand.numerator,
                        "rewritten polynomial": _reduction.reduced_numerator,
                    }
                    for _child, _reduction in zip(
                        apart_terms,
                        numerator_reductions,
                        strict=True,
                    )
                ]
            ),
            mo.md("=== Terms after numerator cancellation"),
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
                "Exact reconstruction is checked in the final validation section."
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
) -> "PreIBPResult":
    """Run native Symbolica apart and numerator preparation for IBP."""

    loop_denominators = list(loop_denominators)
    loop_scalar_products = list(loop_scalar_products)
    loop_propagator_indices = list(loop_propagator_indices)
    if len(loop_denominators) != len(loop_scalar_products) + 1:
        raise ValueError(
            "Preparing every apart child needs one more denominator than "
            "independent loop scalar products"
        )
    if len(loop_propagator_indices) != len(loop_denominators):
        raise ValueError("Each loop denominator needs one graph-source index")
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
    physical_numerator,
):
    pre_ibp = prepare_pre_ibp(
        numerator=physical_numerator,
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
                "graph sources": tuple(
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
                "graph sources": "all loop propagators",
                "indices": "analytic boundary master",
            }
            for _cut_name in direct_cut_names
        ]
    )
    return (contributions_by_cut,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == 4. Solve the three reducible cut blocks with Kira

    Each project is keyed by its cut and its retained graph propagators in the
    native order $(D_3,D_4,D_5,D_6)$. Cut `00` requires all four loop
    propagators and is evaluated as the analytic maximal-cut master rather than
    through a three-propagator child.

    Every Kira project requests the fixed complete domain
    $\{1,0,-1\}^3$. This keeps manifests stable while the editable numerator
    changes. This physical walkthrough uses `mink(d)` and therefore reuses the
    physical project cache; the older `mink(D)` cache is left untouched.

    Evaluation is automatic and resumable. On a fresh checkout this cell runs
    Kira; later evaluations reuse the complete result only when the generated
    project still matches its persisted manifest exactly. Changed inputs are
    rejected instead of silently consuming stale reductions.
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
    === Build the Kira projects

    `build_kira_projects` enumerates every three-propagator subset of the
    inferred loop lines for each reducible cut. It preserves graph order,
    derives the on-shell kinematics from the cut mask while retaining native
    Spenso squares and dot products, enables mass reconstruction only when the
    massive line is present, and requests the complete target cube. The
    returned dictionary is keyed by
    `(cut_name, graph_source_indices)`; no historical topology label is needed.
    """)
    return


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
                "source propagators": tuple(
                    _index + 1 for _index in _source_indices
                ),
                "targets": len(_project.targets),
                "preferred masters": tuple(_project.preferred_masters),
                "workdir": str(
                    kira_workdir_root / _project.family.name
                ),
            }
        )
    spenso_table(_project_rows)
    return kira_projects, kira_workdir_root


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Build the exact IBP input

    The algebraic contributions still carry Spenso scalar products and global
    graph sources. `apply_kinematic_rules` performs only the explicit
    cut-dependent on-shell replacement of external squares. Uncut squares and
    $p_1 dot p_2$ remain native Spenso expressions.
    `contribution_to_kira_expression` then selects the project with the matching
    `(cut, sources)` key and constructs its family atom from the integral-index
    vector. `assemble_ibp_expression` applies both steps term by term and sums
    the different families into one exact expression.
    """)
    return


@app.function
def apply_kinematic_rules(
    expression: "Expression",
    rules: "Sequence[tuple[Expression, Expression]]",
) -> "Expression":
    """Apply an explicit ordered set of kinematic replacements."""

    result = expression
    for source, target in rules:
        result = result.replace(source, target)
    return result.expand()


@app.cell
def _(E, p1, p2):
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
    contribution: "IntegralContribution",
    cut_name: str,
    projects,
):
    """Turn a family/index contribution into an exact Kira integral atom."""

    family = projects[(cut_name, contribution.source_indices)].family
    target = family(*contribution.integral_indices)
    return contribution.coefficient * target


@app.function
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


@app.cell
def _(contributions_by_cut, kira_projects, on_shell_rules_by_cut):
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
                "physical-numerator IBP input": _expression,
            }
            for _cut_name, _expression in ibp_inputs_by_cut.items()
        ]
    )
    return (ibp_inputs_by_cut,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Run or resume the Kira projects

    `run_kira_projects` checks the runtime once, processes project keys in a
    deterministic order, and gives every family its own manifest-backed work
    directory. A matching complete result is resumed; changed project inputs
    are rejected by `kirapy` instead of being silently reused. The helper
    requires complete rule sets and returns both the doctor report and the
    reduction indexed by the original project key.
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
    return kira_doctor, kira_reductions


@app.cell(hide_code=True)
def _(kira_doctor, kira_reductions, mo):
    _kira_status = mo.vstack(
        [
            mo.callout(
                f"Kira `{kira_doctor.version}` completed or resumed "
                "all twelve families with complete reductions.",
                kind="success",
            ),
            spenso_table(
                [
                    {
                        "family": _result.family_name,
                        "targets": len(_result.requested_targets),
                        "masters": len(_result.masters),
                        "zeros": len(_result.zero_integrals),
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
    === Apply the reduction rules without losing provenance

    `apply_ibp_reductions` reconstructs each contribution's native project key,
    requires that project's complete result, and looks up the exact requested
    integral. It applies the cut kinematics to the coefficient but keeps the
    original target beside its reduced right-hand side in an
    `IBPReductionTerm`, making every term of the final sum inspectable.
    """)
    return


@app.function
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


@app.cell
def _(
    E,
    contributions_by_cut,
    kira_projects,
    kira_reductions,
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
    == 5. Apply the cut after IBP

    Each six-line mask is projected onto the automatically discovered loop
    lines. The cut is then applied to the reduced masters in global graph
    space: a family or master that lacks any required positive exponent is set
    to zero. Cuts `11`, `10`, and `01` have three-propagator children. Cut `00`
    requires all four loop lines and therefore has a separate analytic
    maximal-cut master branch outside these three-propagator Kira families.

    `cut_filter_masters` converts each local master-index vector back to a map
    from global graph source to exponent. A master survives only when every
    source required by the full cut mask has positive power. The function
    returns the filtered expression together with the kept and dropped masters,
    retaining their project keys for the analytic step.
    """)
    return


@app.function
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


@app.cell
def _(
    contributions_by_cut,
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
    === Identify surviving masters

    `identify_masters` is a deliberately small boundary: it replaces only the
    master atoms explicitly paired with analytic values. The replacement is
    simultaneous and non-repeating, so evaluating one master cannot trigger an
    accidental second rule. Keeping this step separate makes the IBP result
    inspectable before any closed-form formula is inserted.
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
    == 6. Evaluate the surviving cut masters

    The master names are useful for inspecting the IBP output, but the cut
    result requires their analytic values. Cut `11` contains the massive cut
    bubble

    $ B_("cutm")(s,m^2) =
      -frac((mu^2 e^(gamma_E))^epsilon,
        8 sqrt(pi) Gamma((d-1)/2) sqrt(s))
      (frac(s-m^2, 2 sqrt(s)))^(d-3). $

    Cuts `10` and `01` contain the corresponding cut triangle

    $ T_("cutm")(p_i^2,s,q^2) =
      frac((mu^2 e^(gamma_E))^epsilon,
        4 Gamma((d-2)/2) s^(d-3))
      [p_i^2 (s-q^2) q^2]^((d-4)/2). $

    We keep every master identification visible and substitute the analytic
    values imported from `masters.py`. The fully cut `00` sector is the
    unit-numerator maximal-cut master `M00(s)` multiplied by the numerator
    evaluated on its four-line cut support; it does not require Kira.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    === Analytic symbols

    The analytic formulas use $d$ for the integration dimension,
    $epsilon$ for the dimensional regulator in $d=4-2 epsilon$,
    $mu^2$ for the renormalization scale, and $gamma_E$ for the
    Euler--Mascheroni constant. The latter is Symbolica's built-in constant.
    The regulator and scale retain the stable Symbolica identities `ep` and
    `musq`, but a small display-only printer emits structured `epsilon` and
    `mu^2` Typst (and the corresponding LaTeX). This keeps parsing and
    replacements unambiguous while rendering ε and μ² correctly.

    Symbolica printer attributes are immutable. The registration cell below is
    therefore a run-once initialization cell; restart the Marimo kernel before
    deliberately rerunning it after an edit.
    """)
    return


@app.cell
def _(PrintMode):
    def scalar_printer(*, latex: str, typst: str):
        """Build a display-only printer for an otherwise stable scalar name."""

        def _print_scalar(_expression, mode, **_format_options):
            if mode == PrintMode.Latex:
                return latex
            if mode == PrintMode.Typst:
                return typst
            return None

        return _print_scalar

    return (scalar_printer,)


@app.cell
def _(Expression, S, scalar_printer):
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
                "Python name": "dimension",
                "symbol": dimension,
                "meaning": "integration dimension",
            },
            {
                "Python name": "epsilon",
                "symbol": epsilon,
                "meaning": "dimensional regulator",
            },
            {
                "Python name": "mu_squared",
                "symbol": mu_squared,
                "meaning": "renormalization scale squared",
            },
            {
                "Python name": "euler_gamma",
                "symbol": euler_gamma,
                "meaning": "Euler–Mascheroni constant",
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
    = Validation

    The walkthrough above is the implementation. This appendix now exercises
    that complete native path, the reusable helper edge cases, and finally the
    retained Mathematica/FIRE results as independent one-way oracles. None of
    the expected historical expressions feed the calculation above.

    `validate_pre_ibp` is an invariant checker, not an input to the derivation.
    It reconstructs the propagator kernel from Symbolica's native `apart`
    result, then reconstructs the physical integrand from the graph-labelled
    apart terms, numerator-reduced terms, and IBP contributions. Every residual
    must vanish exactly before the historical oracles are considered.
    """)
    return


@app.cell
def _(S, dot, p1, p2):
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


@app.function
def validate_pre_ibp(
    result: "PreIBPResult",
) -> "dict[str, Expression]":
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
        "native apart kernel reconstruction": normalize_rational(
            result.apart_expression
            - E("1") / prod(result.denominators)
        ),
        "graph-labelled apart reconstruction": normalize_rational(
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
        "IBP-input reconstruction": normalize_rational(
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
    p1,
    p2,
    physical_numerator,
    pre_ibp,
    projected_cutsets,
    required_loop_sources_by_cut,
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
        _checks[f"cut {_cut_name} IBP input reconstruction"] = normalize_rational(
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
    _checks["native Kira round trip contains no wire or historical aliases"] = (
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
            mo.md("== Native cross-box workflow"),
            spenso_table(native_validation_rows),
            mo.callout(
                "The Spenso/Idenso physical trace, multivariate apart check, "
                "graph routing, Kira project definitions, IBP inputs, and "
                "cut-master selection all pass their exact checks.",
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
    spenso_table(display_validation_rows)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    == Validation 1 — native multivariate apart delegation

    We exercise Symbolica's decomposition and the graph-provenance adapter for
    affine families with two through seven propagators. The expected
    coefficients follow from how each synthetic family is constructed; they
    are validation data, not inputs to `apart_integrand`.
    """)
    return


@app.cell
def _(E, S, prod):
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
            {"case": f"native apart with N={_count}", "residual": _residual}
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
        {"case": "empty apart variables rejected", "residual": E("0")}
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
        {"case": "duplicate apart variables rejected", "residual": E("0")}
    )

    apart_validation_rows = _validation_rows
    return (apart_validation_rows,)


@app.cell(hide_code=True)
def _(E, apart_validation_rows):
    assert len(apart_validation_rows) == 8
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
    == Validation 2 — historical scalar cross-box preprocessing

    The following one-way check compares the native derivation with the retained
    Mathematica result. It supplies no propagator, coefficient, family mapping,
    or control-flow input to the calculation above.
    """)
    return


@app.cell
def _(
    E,
    delta,
    dot,
    loop_denominators,
    loop_propagator_indices,
    loop_scalar_products,
    p1,
    p2,
    q,
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
            "expected sources": tuple(_index + 1 for _index in _sources),
            "actual sources": tuple(
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
                "Historical scalar validation passed: all four Symbolica "
                "apart slots, the independent delta convention, sign pattern, "
                "and exact reconstructions agree with the retained Mathematica "
                "result.",
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
    contributions_by_cut,
    ipp1p2,
    kira_projects,
    kira_reductions,
    mathematica_reference_pre_ibp,
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
        _chain_checks[f"cut {_cut_name} IBP input"] = normalize_rational(
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
    == Validation 3 — completed scalar result against Mathematica/FIRE

    This independent oracle uses the historical scalar numerator `1`. After
    translating its loop routing to the six-line graph, cut `11` must retain
    `topo20(1,0,1)` and `topo22(1,1,0)`. We check the exact master expression,
    identify both with the same cut bubble, evaluate that master, and reproduce
    the recorded expansion through order $epsilon^0$.
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
            "native family": kira_projects[_project_key].family.name,
            "native sources": tuple(
                _source + 1 for _source in _project_key[1]
            ),
            "FIRE family": f"topo{_oracle['family_id']}",
            "FIRE source order": tuple(
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
                "native family": "scalar oracle",
                "native sources": (),
                "FIRE family": "retained expression",
                "FIRE source order": mathematica_scalar_cut_oracle,
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
                    "The scalar pre-IBP and analytic-master oracles are "
                    "complete, but the automatic Kira results are unavailable "
                    "for the independent FIRE, cut, and full-chain checks.",
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
                    "All twelve Kira projects are complete. The routed scalar "
                    "cut-11 reduction, bubble identification, analytic master, "
                    "and epsilon expansion agree exactly with the retained "
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
        "Current boundary: the six-line graph, all four cut masks, all twelve "
        "native graph-order reductions, the physical gamma-trace numerator, "
        "and the analytic master evaluations for cuts 11, 10, and 01 are "
        "complete. The final appendix maps those projects to the historical "
        "topo20--31 oracle. Cut 00 is the analytic maximal-cut master M00(s), "
        "not a missing Kira rule and not zero by default. The companion "
        "dy_topologies.py notebook evaluates the physical numerator on that "
        "maximal-cut support and supplies virtuality integrations and endpoint "
        "distribution dressing for all four cuts.",
        kind="info",
    )
    return


if __name__ == "__main__":
    app.run()
