import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import importlib.metadata as metadata
    import json

    import gammaloop
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from collections.abc import Sequence
    from dataclasses import dataclass, field
    from math import prod
    from symbolica import (
        AtomType,
        E,
        S,
        Expression,
        ParseMode,
        PrintMode,
        Replacement,
    )
    from symbolica.community.spenso import (
        Representation,
        TensorExpression,
        TensorName,
        dot,
        to_typst,
    )

    return (
        AtomType,
        E,
        Expression,
        ParseMode,
        PrintMode,
        Replacement,
        Representation,
        S,
        Sequence,
        TensorExpression,
        TensorName,
        dataclass,
        dot,
        field,
        prod,
        to_typst,
    )


@app.cell
def _(Representation, S):
    minkd = Representation.mink(dimension=S("D"))
    return (minkd,)


@app.cell
def _(AtomType, PrintMode):
    def momentum_printer(name):
        """Build the small keyed-vector printer not yet provided by Spenso."""

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

    return (momentum_printer,)


@app.cell
def _(TensorName, momentum_printer):
    import symbolica as _symbolica

    LOOP_MOMENTUM_TAG = "ludy::loop_momentum"
    _cache_name = "_ludy_tagged_momentum_names_v3"
    _momentum_names = getattr(_symbolica, _cache_name, None)
    if _momentum_names is None:
        for _legacy_cache_name in (
            "_ludy_tagged_momentum_heads_v2",
            "_ludy_tagged_momentum_heads_v1",
        ):
            _legacy_heads = getattr(_symbolica, _legacy_cache_name, None)
            if _legacy_heads is not None and (
                "spenso::rank1" not in _legacy_heads[0].get_tags()
                or "spenso::rank1" not in _legacy_heads[1].get_tags()
                or LOOP_MOMENTUM_TAG not in _legacy_heads[1].get_tags()
            ):
                raise RuntimeError(
                    "The existing p/k heads predate TensorName.vector. Restart "
                    "this Marimo kernel once; Symbolica symbol tags are immutable "
                    "within a running process."
                )
        _momentum_names = (
            TensorName.vector("p", print=momentum_printer("p")),
            TensorName.vector(
                "k",
                tags=[LOOP_MOMENTUM_TAG],
                print=momentum_printer("k"),
            ),
        )
        setattr(_symbolica, _cache_name, _momentum_names)

    p, k = _momentum_names
    if not p.has_tag("spenso::rank1") or not k.has_tag("spenso::rank1"):
        raise RuntimeError(
            "The cached p/k names are not rank-one tensors; restart the Marimo "
            "kernel once."
        )
    if not k.has_tag(LOOP_MOMENTUM_TAG):
        raise RuntimeError(
            "The cached k name is missing its loop-momentum tag; restart the "
            "Marimo kernel once."
        )
    return LOOP_MOMENTUM_TAG, k, p


@app.cell
def _(TensorExpression, minkd, mo, p, spenso_table):
    _p1 = p(1, minkd)
    assert isinstance(_p1, TensorExpression)
    assert spenso_disp(_p1) == "p₁"
    assert _p1.format(color_builtin_symbols=False) == "p(1,mink(D))"
    assert "spenso::tensor" in _p1.to_canonical_string()
    assert "spenso::rank1" in _p1.to_canonical_string()
    assert "spenso::representation" in _p1.to_canonical_string()
    momentum_p_showcase = {
        "constructor": "p(1, minkd)",
        "compact display": spenso_disp(_p1),
        "default display": _p1.format(color_builtin_symbols=False),
    }
    spenso_table([momentum_p_showcase])
    return


@app.cell
def _(LOOP_MOMENTUM_TAG, TensorExpression, k, minkd, mo, spenso_table):
    _k1 = k(1, minkd)
    assert isinstance(_k1, TensorExpression)
    assert spenso_disp(_k1) == "k₁"
    assert _k1.format(color_builtin_symbols=False) == "k(1,mink(D))"
    assert "spenso::tensor" in _k1.to_canonical_string()
    assert "spenso::rank1" in _k1.to_canonical_string()
    assert k.has_tag(LOOP_MOMENTUM_TAG)
    momentum_k_showcase = {
        "constructor": "k(1, minkd)",
        "compact display": spenso_disp(_k1),
        "default display": _k1.format(color_builtin_symbols=False),
        "loop tag": LOOP_MOMENTUM_TAG,
    }
    spenso_table([momentum_k_showcase])
    return


@app.function
def spenso_disp(expr):
    from symbolica.community.spenso import format_tensor

    _method = getattr(expr, "format_tensor", None)
    return _method() if callable(_method) else format_tensor(expr)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rich Symbolica display

    `SpensoMath` keeps the exact native Symbolica expression for algebra while
    rendering its Spenso-aware Typst form as semantic HTML/MathML. Typst's SVG
    exporter is retained as a fallback while HTML export remains experimental.
    """)
    return


@app.cell
def _(E, Expression, dataclass, mo, to_typst):
    from functools import lru_cache as _lru_cache
    import re as _re

    import typst as _typst

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
        """Make Symbolica's operator applications atomic for Typst."""

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
        _method = getattr(expression, "to_typst", None)
        formatted = _method() if callable(_method) else to_typst(expression)
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

    @dataclass(frozen=True, slots=True)
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

    return (SpensoMath,)


@app.cell
def _(Expression, SpensoMath):
    def spenso_math(expression: Expression) -> SpensoMath:
        """Return a rich Marimo display view of an exact Symbolica expression."""

        if not isinstance(expression, Expression):
            raise TypeError("spenso_math expects a Symbolica Expression")
        return SpensoMath(expression)

    return (spenso_math,)


@app.cell
def _(Expression, mo, spenso_math):
    def spenso_math_cell(expression: Expression):
        """Return a Marimo HTML MIME value suitable for a table cell."""

        return mo.as_html(spenso_math(expression))

    return (spenso_math_cell,)


@app.cell
def _(Expression, mo, spenso_math_cell):
    from html import escape as _escape_html

    def _contains_spenso_expression(value):
        return isinstance(value, Expression) or (
            isinstance(value, (list, tuple))
            and any(_contains_spenso_expression(item) for item in value)
        )

    def _spenso_sequence_cell(values):
        opening, closing = ("(", ")") if isinstance(values, tuple) else ("[", "]")
        parts = []
        for index, value in enumerate(values):
            if index:
                parts.append('<span aria-hidden="true">,</span>')
            if isinstance(value, Expression):
                parts.append(spenso_math_cell(value).text)
            elif isinstance(value, (list, tuple)) and _contains_spenso_expression(
                value
            ):
                parts.append(_spenso_sequence_cell(value).text)
            else:
                parts.append(
                    f"<span>{_escape_html(str(value))}</span>"
                )
        return mo.Html(
            '<div style="display: inline-flex; align-items: baseline; '
            'gap: 0.25rem; white-space: nowrap">'
            f"<span>{opening}</span>{''.join(parts)}<span>{closing}</span>"
            "</div>"
        )

    def _spenso_table_value(value):
        if isinstance(value, Expression):
            return spenso_math_cell(value)
        if isinstance(value, (list, tuple)) and _contains_spenso_expression(value):
            return _spenso_sequence_cell(value)
        return value

    def spenso_table(data, **kwargs):
        """Render Symbolica expressions richly while retaining raw table data."""

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
            column: _spenso_table_value for column in columns
        }
        return mo.ui.table(
            data,
            format_mapping={**automatic_formatting, **explicit_formatting},
            **kwargs,
        )

    return (spenso_table,)


@app.cell
def _(
    S,
    dot,
    k,
    minkd,
    mo,
    p,
    spenso_math,
    spenso_math_cell,
    spenso_table,
):
    spenso_math_showcase = spenso_math(
        dot(p(1, minkd), k(2, minkd)) + S("x") ** 2 / 3
    )
    assert "p_(1)" in spenso_math_showcase.typst
    assert "k_(2)" in spenso_math_showcase.typst
    assert " dot " in spenso_math_showcase.typst
    _table_cell = spenso_math_cell(spenso_math_showcase.expression)
    assert "<math" in _table_cell.text
    mo.vstack(
        [
            mo.md("**Spenso-aware Typst → HTML/MathML**"),
            spenso_math_showcase,
            spenso_table(
                [
                    {
                        "location": "Marimo table cell",
                        "expression": spenso_math_showcase.expression,
                    }
                ],
                selection=None,
                show_download=False,
                show_search=False,
                show_column_summaries=False,
                show_data_types=False,
            ),
        ]
    )
    return (spenso_math_showcase,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data Structures
    """)
    return


@app.cell
def _(Expression, SpensoMath, dataclass, field, prod):
    @dataclass(slots=True)
    class Integrand:
        """An editable numerator and an ordered tuple of denominator factors."""

        numerator: Expression
        denominators: tuple[Expression, ...]

        def as_expression(self) -> Expression:
            return self.numerator / prod(self.denominators)

        def _display_(self):
            return SpensoMath(self.as_expression())


    @dataclass(slots=True)
    class PartialFractionTerm:
        """One child produced by omitting a propagator from an affine relation."""

        removed_index: int
        retained_indices: tuple[int, ...]
        integrand: Integrand


    @dataclass(slots=True)
    class ReducedIntegralTerm:
        """One coefficient times an integral-index vector in a fixed basis."""

        coefficient: Expression
        propagators: tuple[Expression, ...]
        integral_indices: tuple[int, ...]

        def as_expression(self) -> Expression:
            return self.coefficient / prod(
                propagator**index
                for propagator, index in zip(
                    self.propagators, self.integral_indices, strict=True
                )
            )


    @dataclass(slots=True)
    class NumeratorReduction:
        """A numerator rewritten in one independent propagator basis."""

        terms: tuple[ReducedIntegralTerm, ...]
        relations: tuple[tuple[Expression, Expression], ...]
        reduced_numerator: Expression


    @dataclass(slots=True)
    class IntegralContribution:
        """One native Python contribution ready to become an IBP target."""

        family_id: int
        source_indices: tuple[int, ...]
        propagators: tuple[Expression, ...]
        integral_indices: tuple[int, ...]
        coefficient: Expression

        def as_expression(self) -> Expression:
            return self.coefficient / prod(
                propagator**index
                for propagator, index in zip(
                    self.propagators, self.integral_indices, strict=True
                )
            )


    @dataclass(slots=True)
    class IBPReductionTerm:
        """One family integral together with its exact reduced right-hand side."""

        family_id: int
        coefficient: Expression
        target: Expression
        reduced_integral: Expression

        def input_expression(self) -> Expression:
            return self.coefficient * self.target

        def reduced_expression(self) -> Expression:
            return self.coefficient * self.reduced_integral


    @dataclass(slots=True)
    class CrossBoxPreIBP:
        """All exact intermediate data at the cross-box IBP boundary."""

        propagators: tuple[Expression, ...]
        loop_scalar_products: tuple[Expression, ...]
        delta: Expression
        integrand: Integrand
        partial_fractions: tuple[PartialFractionTerm, ...]
        numerator_reductions: tuple[NumeratorReduction, ...]
        contributions: tuple[IntegralContribution, ...]
        checks: dict[str, Expression] = field(default_factory=dict)


    return (
        CrossBoxPreIBP,
        IBPReductionTerm,
        IntegralContribution,
        Integrand,
        NumeratorReduction,
        PartialFractionTerm,
        ReducedIntegralTerm,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Inspectable tooling functions

    Every scientific transformation below lives in its own code cell. Each is
    exercised by an executable showcase or by the exact derivation cells that
    consume it, so implementation, intermediate values, and checks remain
    inspectable together.
    """)
    return


@app.cell
def _():
    PARTIAL_FRACTION_SLOTS: tuple[tuple[int, tuple[int, ...]], ...] = (
        (1, (0, 1, 2)),
        (2, (0, 1, 3)),
        (3, (0, 2, 3)),
        (4, (1, 2, 3)),
    )
    return (PARTIAL_FRACTION_SLOTS,)


@app.cell
def _(
    PARTIAL_FRACTION_SLOTS: tuple[tuple[int, tuple[int, ...]], ...],
    Sequence,
):
    def partial_fraction_slot_id(source_indices: Sequence[int]) -> int:
        """Return the display slot for one ordered three-line subset."""

        source_indices = tuple(source_indices)
        for slot_id, slot_sources in PARTIAL_FRACTION_SLOTS:
            if source_indices == slot_sources:
                return slot_id
        raise ValueError(f"Unknown cross-box propagator subset: {source_indices}")

    return (partial_fraction_slot_id,)


@app.cell
def _(
    PARTIAL_FRACTION_SLOTS: tuple[tuple[int, tuple[int, ...]], ...],
    mo,
    partial_fraction_slot_id,
    spenso_table,
):
    partial_fraction_slot_id_showcase = tuple(
        {
            "retained propagators": tuple(index + 1 for index in sources),
            "partial-fraction slot": partial_fraction_slot_id(sources),
        }
        for _, sources in PARTIAL_FRACTION_SLOTS
    )
    assert tuple(
        row["partial-fraction slot"]
        for row in partial_fraction_slot_id_showcase
    ) == (1, 2, 3, 4)
    spenso_table(partial_fraction_slot_id_showcase)
    return


@app.cell
def _(Expression, dot):
    def square(momentum: Expression) -> Expression:
        """Return a Spenso scalar square without imposing kinematics."""

        return dot(momentum, momentum)

    return (square,)


@app.cell
def _(dot, minkd, mo, p, square, spenso_table):
    _showcase_momentum = p(1, minkd)
    square_showcase = {
        "operation": "square(p1)",
        "result": square(_showcase_momentum),
        "direct dot": dot(_showcase_momentum, _showcase_momentum),
    }
    assert square(_showcase_momentum) == dot(
        _showcase_momentum, _showcase_momentum
    )
    spenso_table([square_showcase])
    return


@app.cell
def _(Expression, Sequence, square):
    def propagator_denominators(
        propagators: Sequence[tuple[Expression, Expression]],
    ) -> tuple[Expression, ...]:
        """Convert ordered ``(momentum, mass_squared)`` pairs to denominators."""

        return tuple(
            square(momentum) - mass_squared
            for momentum, mass_squared in propagators
        )

    return (propagator_denominators,)


@app.cell
def _(E, S, canonical_zero, minkd, mo, p, propagator_denominators, square, spenso_table):
    _showcase_p1 = p(1, minkd)
    _showcase_mass_squared = S("propagator_mass_squared")
    _showcase_denominator = propagator_denominators(
        ((_showcase_p1, _showcase_mass_squared),)
    )[0]
    _showcase_residual = canonical_zero(
        _showcase_denominator
        - square(_showcase_p1)
        + _showcase_mass_squared
    )
    assert _showcase_residual == E("0")
    propagator_denominators_showcase = {
        "input momentum": _showcase_p1,
        "input mass squared": _showcase_mass_squared,
        "denominator": _showcase_denominator,
        "residual": _showcase_residual,
    }
    spenso_table([propagator_denominators_showcase])
    return


@app.cell
def _(Expression):
    def has_symbol_tag(expression: Expression, tag: str) -> bool:
        """Return whether any symbol head inside an expression carries `tag`."""

        return any(
            tag in symbol.get_tags()
            for symbol in expression.get_all_symbols(
                include_function_symbols=True
            )
        )

    return (has_symbol_tag,)


@app.cell
def _(LOOP_MOMENTUM_TAG, has_symbol_tag, k, minkd, mo, p, spenso_table):
    _showcase_loop = k(7, minkd)
    _showcase_external = p(1, minkd)
    _showcase_composite = _showcase_loop - _showcase_external
    assert has_symbol_tag(_showcase_loop, LOOP_MOMENTUM_TAG)
    assert has_symbol_tag(_showcase_composite, LOOP_MOMENTUM_TAG)
    assert not has_symbol_tag(_showcase_external, LOOP_MOMENTUM_TAG)
    has_symbol_tag_showcase = {
        "expression": _showcase_composite,
        "tag": LOOP_MOMENTUM_TAG,
        "found": True,
    }
    spenso_table([has_symbol_tag_showcase])
    return


@app.cell
def _(Expression, LOOP_MOMENTUM_TAG, Sequence, has_symbol_tag):
    def find_loop_propagator_indices(
        propagators: Sequence[tuple[Expression, Expression]],
        *,
        loop_tag: str = LOOP_MOMENTUM_TAG,
    ) -> tuple[int, ...]:
        """Find propagators whose momentum contains a tagged loop momentum."""

        return tuple(
            index
            for index, (momentum, _mass_squared) in enumerate(propagators)
            if has_symbol_tag(momentum, loop_tag)
        )

    return (find_loop_propagator_indices,)


@app.cell
def _(E, find_loop_propagator_indices, k, minkd, mo, p, spenso_table):
    _showcase_p1 = p(1, minkd)
    _showcase_k1 = k(1, minkd)
    _showcase_propagators = (
        (_showcase_p1, E("0")),
        (_showcase_k1, E("0")),
        (_showcase_k1 - _showcase_p1, E("0")),
    )
    _showcase_indices = find_loop_propagator_indices(_showcase_propagators)
    assert _showcase_indices == (1, 2)
    find_loop_propagator_indices_showcase = {
        "propagators": len(_showcase_propagators),
        "loop-dependent indices": _showcase_indices,
    }
    spenso_table([find_loop_propagator_indices_showcase])
    return


@app.cell
def _(Sequence):
    def project_cutset(
        cutset: Sequence[int],
        propagator_indices: Sequence[int],
    ) -> tuple[int, ...]:
        """Project one graph-level cut mask onto an ordered propagator subset."""

        cutset = tuple(cutset)
        propagator_indices = tuple(propagator_indices)
        if any(value not in (0, 1) for value in cutset):
            raise ValueError("Cut masks must contain only zeroes and ones")
        if len(set(propagator_indices)) != len(propagator_indices):
            raise ValueError("Projected propagator indices must be unique")
        if any(index < 0 or index >= len(cutset) for index in propagator_indices):
            raise IndexError("Projected propagator index is out of range")
        return tuple(cutset[index] for index in propagator_indices)

    return (project_cutset,)


@app.cell
def _(mo, project_cutset, spenso_table):
    _showcase_cut = (1, 0, 1, 0, 1, 1)
    _showcase_projection = project_cutset(_showcase_cut, (2, 3, 4, 5))
    assert _showcase_projection == (1, 0, 1, 1)
    project_cutset_showcase = {
        "full cut": _showcase_cut,
        "selected positions": (2, 3, 4, 5),
        "projected cut": _showcase_projection,
    }
    spenso_table([project_cutset_showcase])
    return


@app.cell
def _(Expression):
    def canonical_zero(expression: Expression) -> Expression:
        """Normalize a rational expression for an exact zero comparison."""

        return expression.expand().together().cancel()

    return (canonical_zero,)


@app.cell
def _(E, S, canonical_zero, mo, spenso_table):
    _showcase_x, _showcase_y = S("canonical_x", "canonical_y")
    _showcase_residual = canonical_zero(
        (_showcase_x**2 - _showcase_y**2) / (_showcase_x - _showcase_y)
        - _showcase_x
        - _showcase_y
    )
    assert _showcase_residual == E("0")
    canonical_zero_showcase = {
        "identity": "(x^2-y^2)/(x-y) - x - y",
        "residual": _showcase_residual,
    }
    spenso_table([canonical_zero_showcase])
    return


@app.cell
def _(E, Expression, S, Sequence):
    def partial_fraction_coefficients(
        propagators: Sequence[Expression],
        loop_scalar_products: Sequence[Expression],
        *,
        target: Expression | None = None,
    ) -> tuple[Expression, ...]:
        """Solve ``sum(a_i D_i) = target`` for a unique affine relation."""

        propagators = tuple(propagators)
        loop_scalar_products = tuple(loop_scalar_products)
        if len(propagators) < 2:
            raise ValueError(
                "Affine partial fractioning needs at least two denominators"
            )
        target = E("1") if target is None else target
        weights = tuple(S(f"__pf_{index}") for index in range(len(propagators)))
        relation = sum(
            (
                weight * propagator
                for weight, propagator in zip(
                    weights, propagators, strict=True
                )
            ),
            -target,
        ).expand()
        equations = tuple(
            coefficient
            for _, coefficient in relation.coefficient_list(*loop_scalar_products)
        )
        solution = tuple(Expression.solve_linear_system(equations, weights))
        if len(solution) != len(weights) or any(
            bool(coefficient.contains(weight))
            for coefficient in solution
            for weight in weights
        ):
            raise ValueError("Propagators do not define a unique affine relation")
        return solution

    return (partial_fraction_coefficients,)


@app.cell
def _(E, S, canonical_zero, mo, partial_fraction_coefficients, spenso_table):
    _coefficient_rows = []
    for _count in range(2, 8):
        _loop_products = tuple(
            S(f"coefficient_x_{_count}_{_index}")
            for _index in range(_count - 1)
        )
        _delta = S(f"coefficient_delta_{_count}")
        _weights = (
            *(
                E(str((-1) ** _index * (_index + 1)))
                for _index in range(_count - 1)
            ),
            E("1"),
        )
        _denominators = (
            *_loop_products,
            _delta
            - sum(
                (
                    _weight * _loop_product
                    for _weight, _loop_product in zip(
                        _weights[:-1], _loop_products, strict=True
                    )
                ),
                E("0"),
            ),
        )
        _coefficients = partial_fraction_coefficients(
            _denominators,
            _loop_products,
        )
        _residual = canonical_zero(
            sum(
                (
                    _coefficient * _denominator
                    for _coefficient, _denominator in zip(
                        _coefficients, _denominators, strict=True
                    )
                ),
                E("-1"),
            )
        )
        assert _residual == E("0")
        assert all(
            canonical_zero(_actual - _weight / _delta) == E("0")
            for _actual, _weight in zip(_coefficients, _weights, strict=True)
        )
        _coefficient_rows.append(
            {
                "propagators": _count,
                "solved coefficients": len(_coefficients),
                "residual": _residual,
            }
        )
    partial_fraction_coefficients_showcase = tuple(_coefficient_rows)
    spenso_table(partial_fraction_coefficients_showcase)
    return


@app.cell
def _(
    E,
    Expression,
    Integrand,
    PartialFractionTerm,
    Sequence,
    canonical_zero,
    partial_fraction_coefficients,
):
    def partial_fraction(
        integrand: Integrand,
        *,
        removed_indices: Sequence[int],
        loop_scalar_products: Sequence[Expression],
        coefficients: Sequence[Expression] | None = None,
    ) -> tuple[PartialFractionTerm, ...]:
        """Remove denominators using ``sum(c_i D_i) = 1`` directly."""

        removed_indices = tuple(removed_indices)
        loop_scalar_products = tuple(loop_scalar_products)
        if len(set(removed_indices)) != len(removed_indices):
            raise ValueError("Removed denominator indices must be unique")
        if any(
            index < 0 or index >= len(integrand.denominators)
            for index in removed_indices
        ):
            raise IndexError("Removed denominator index is out of range")

        selected = tuple(
            integrand.denominators[index] for index in removed_indices
        )
        coefficients = (
            partial_fraction_coefficients(selected, loop_scalar_products)
            if coefficients is None
            else tuple(coefficients)
        )
        if len(coefficients) != len(selected):
            raise ValueError("Each selected denominator needs one coefficient")
        if any(
            bool(coefficient.contains(loop_product))
            for coefficient in coefficients
            for loop_product in loop_scalar_products
        ):
            raise ValueError(
                "Partial-fraction coefficients must be independent of loop momenta"
            )
        relation_residual = canonical_zero(
            sum(
                (
                    coefficient * denominator
                    for coefficient, denominator in zip(
                        coefficients, selected, strict=True
                    )
                ),
                E("-1"),
            )
        )
        if relation_residual != E("0"):
            raise ValueError(
                "Partial-fraction coefficients do not solve sum(c_i D_i) = 1: "
                f"{relation_residual}"
            )

        terms = []
        for removed_index, coefficient in zip(
            removed_indices,
            coefficients,
            strict=True,
        ):
            retained_indices = tuple(
                index
                for index in range(len(integrand.denominators))
                if index != removed_index
            )
            retained_denominators = tuple(
                integrand.denominators[index] for index in retained_indices
            )
            terms.append(
                PartialFractionTerm(
                    removed_index=removed_index,
                    retained_indices=retained_indices,
                    integrand=Integrand(
                        numerator=canonical_zero(
                            integrand.numerator * coefficient
                        ),
                        denominators=retained_denominators,
                    ),
                )
            )
        decomposition = tuple(terms)
        residual = canonical_zero(
            sum(
                (term.integrand.as_expression() for term in decomposition),
                E("0"),
            )
            - integrand.as_expression()
        )
        if residual != E("0"):
            raise ValueError(
                "Partial-fraction decomposition does not reconstruct input: "
                f"{residual}"
            )
        return decomposition

    return (partial_fraction,)


@app.cell
def _(E, Integrand, S, canonical_zero, mo, partial_fraction, prod, spenso_table):
    _partial_fraction_rows = []
    for _count in range(2, 8):
        _loop_products = tuple(
            S(f"partial_fraction_x_{_count}_{_index}")
            for _index in range(_count - 1)
        )
        _delta = S(f"partial_fraction_delta_{_count}")
        _numerator = S(f"partial_fraction_numerator_{_count}")
        _weights = (
            *(
                E(str((-1) ** _index * (_index + 1)))
                for _index in range(_count - 1)
            ),
            E("1"),
        )
        _denominators = (
            *_loop_products,
            _delta
            - sum(
                (
                    _weight * _loop_product
                    for _weight, _loop_product in zip(
                        _weights[:-1], _loop_products, strict=True
                    )
                ),
                E("0"),
            ),
        )
        _requested_order = tuple(reversed(range(_count)))
        _terms = partial_fraction(
            Integrand(_numerator, _denominators),
            removed_indices=_requested_order,
            loop_scalar_products=_loop_products,
        )
        _residual = canonical_zero(
            sum(
                (_term.integrand.as_expression() for _term in _terms),
                E("0"),
            )
            - _numerator / prod(_denominators)
        )
        assert tuple(_term.removed_index for _term in _terms) == _requested_order
        assert len(_terms) == _count
        assert _residual == E("0")
        _partial_fraction_rows.append(
            {
                "propagators": _count,
                "terms": len(_terms),
                "requested removal order preserved": True,
                "residual": _residual,
            }
        )
    partial_fraction_showcase = tuple(_partial_fraction_rows)
    spenso_table(partial_fraction_showcase)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Cross Box

    This is a native Python/Spenso preprocessing model. The historical
    `DY_calculation.nb` cross-box section is used as a semantic validation
    oracle, not translated cell by cell. Its active scalar example fixes the
    reference signs and family mapping; the Python functions remain reusable
    for other numerators and any number of affinely related propagators. The
    partial fractioning is the solved linear identity itself, matching the
    Mathematica workflow. No on-shell replacement is used in this stage.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Define the cross-box integrand

    The graph input is the ordered list of six `(momentum, mass_squared)`
    pairs. The loop head `k` carries a Symbolica tag, so loop-dependent lines
    are discovered from the expressions themselves. The external squares
    (p_1^2,p_2^2) specify which incoming legs are cut, but are not sent to an
    IBP reducer as loop propagators.

    No on-shell identity or integral-reduction rule has been applied here.
    """)
    return


@app.cell
def _(
    E,
    Integrand,
    S,
    dot,
    find_loop_propagator_indices,
    k,
    minkd,
    p,
    project_cutset,
    propagator_denominators,
    square,
):
    cross_box_p1 = p(1, minkd)
    cross_box_p2 = p(2, minkd)
    cross_box_k1 = k(1, minkd)
    cross_box_q = S("q")

    cross_box_propagators = (
        (cross_box_p1, E("0")),
        (cross_box_p2, E("0")),
        (cross_box_k1, E("0")),
        (cross_box_k1 - cross_box_p1, E("0")),
        (cross_box_p2 - cross_box_k1, E("0")),
        (
            cross_box_p1 + cross_box_p2 - cross_box_k1,
            cross_box_q**2,
        ),
    )
    cross_box_cutsets = {
        "11": (1, 1, 1, 0, 0, 1),
        "10": (1, 0, 1, 0, 1, 1),
        "01": (0, 1, 1, 1, 0, 1),
        "00": (0, 0, 1, 1, 1, 1),
    }
    cross_box_mathematica_cut_names = {
        "11": "00",
        "10": "10",
        "01": "01",
        "00": "11",
    }
    cross_box_denominators = propagator_denominators(cross_box_propagators)
    cross_box_loop_propagator_indices = find_loop_propagator_indices(
        cross_box_propagators
    )
    assert cross_box_loop_propagator_indices == (2, 3, 4, 5)
    cross_box_loop_propagators = tuple(
        cross_box_propagators[_index]
        for _index in cross_box_loop_propagator_indices
    )
    cross_box_loop_denominators = tuple(
        cross_box_denominators[_index]
        for _index in cross_box_loop_propagator_indices
    )
    cross_box_projected_cutsets = {
        _name: project_cutset(_mask, cross_box_loop_propagator_indices)
        for _name, _mask in cross_box_cutsets.items()
    }
    assert cross_box_projected_cutsets == {
        "11": (1, 0, 0, 1),
        "10": (1, 0, 1, 1),
        "01": (1, 1, 0, 1),
        "00": (1, 1, 1, 1),
    }

    # This is the native Python example's editable numerator. The independent
    # Mathematica validation below uses a separate historical numerator.
    cross_box_numerator = dot(
        cross_box_k1,
        cross_box_p1 + cross_box_p2,
    )

    cross_box_loop_scalar_products = (
        square(cross_box_k1),
        dot(cross_box_k1, cross_box_p1),
        dot(cross_box_k1, cross_box_p2),
    )
    cross_box_delta = cross_box_q**2 - 2 * dot(cross_box_p1, cross_box_p2)
    cross_box_integrand = Integrand(
        numerator=cross_box_numerator,
        denominators=cross_box_loop_denominators,
    )
    return (
        cross_box_cutsets,
        cross_box_delta,
        cross_box_denominators,
        cross_box_integrand,
        cross_box_k1,
        cross_box_loop_denominators,
        cross_box_loop_propagator_indices,
        cross_box_loop_scalar_products,
        cross_box_mathematica_cut_names,
        cross_box_p1,
        cross_box_p2,
        cross_box_projected_cutsets,
        cross_box_propagators,
        cross_box_q,
    )


@app.cell(hide_code=True)
def _(
    cross_box_cutsets,
    cross_box_denominators,
    cross_box_integrand,
    cross_box_loop_propagator_indices,
    cross_box_mathematica_cut_names,
    cross_box_projected_cutsets,
    cross_box_propagators,
    mo,
    spenso_table,
):
    mo.vstack(
        [
            spenso_table(
                [
                    {
                        "propagator": f"D{_index + 1}",
                        "momentum": _momentum,
                        "mass squared": _mass_squared,
                        "denominator": cross_box_denominators[_index],
                        "loop dependent": (
                            _index in cross_box_loop_propagator_indices
                        ),
                        **{
                            f"cut {_name}": _mask[_index]
                            for _name, _mask in cross_box_cutsets.items()
                        },
                    }
                    for _index, (_momentum, _mass_squared) in enumerate(
                        cross_box_propagators
                    )
                ]
            ),
            spenso_table(
                [
                    {
                        "Python cut": _name,
                        "Mathematica label": cross_box_mathematica_cut_names[
                            _name
                        ],
                        "full six-line mask": _mask,
                        "inferred loop projection": (
                            cross_box_projected_cutsets[_name]
                        ),
                    }
                    for _name, _mask in cross_box_cutsets.items()
                ]
            ),
            mo.md(
                "Loop integrand before cut or IBP: "
                f"`{spenso_disp(cross_box_integrand.as_expression())}`"
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Solve the affine relation

    We solve the linear system for
    loop-independent coefficients \(c_i\) such that

    \[
    \sum_{i=1}^{N} c_i D_i=1.
    \]

    This is not tied to four propagators: the same coefficient solve accepts any
    number \(N\geq2\) of affine denominator factors whenever the system has a
    unique solution. The partial fractions follow directly from this identity.
    """)
    return


@app.cell
def _(
    E,
    canonical_zero,
    cross_box_loop_denominators,
    cross_box_loop_scalar_products,
    partial_fraction_coefficients,
):
    cross_box_affine_coefficients = partial_fraction_coefficients(
        cross_box_loop_denominators,
        cross_box_loop_scalar_products,
    )
    cross_box_affine_terms = tuple(
        _coefficient * _propagator
        for _coefficient, _propagator in zip(
            cross_box_affine_coefficients,
            cross_box_loop_denominators,
            strict=True,
        )
    )
    cross_box_affine_relation = sum(cross_box_affine_terms, E("0"))
    cross_box_affine_residual = canonical_zero(
        cross_box_affine_relation - E("1")
    )
    assert cross_box_affine_residual == E("0")
    return (
        cross_box_affine_coefficients,
        cross_box_affine_relation,
        cross_box_affine_residual,
        cross_box_affine_terms,
    )


@app.cell(hide_code=True)
def _(
    cross_box_affine_coefficients,
    cross_box_affine_relation,
    cross_box_affine_residual,
    cross_box_affine_terms,
    cross_box_loop_denominators,
    mo,
    spenso_table,
):
    mo.vstack(
        [
            spenso_table(
                [
                    {
                        "factor": f"D{_index + 3}",
                        "D_i": _propagator,
                        "c_i": _coefficient,
                        "c_i D_i": _term,
                    }
                    for _index, (_propagator, _coefficient, _term) in enumerate(
                        zip(
                            cross_box_loop_denominators,
                            cross_box_affine_coefficients,
                            cross_box_affine_terms,
                            strict=True,
                        )
                    )
                ]
            ),
            mo.md(
                "Affine sum: "
                f"`{spenso_disp(cross_box_affine_relation)}`; "
                "exact residual: "
                f"`{spenso_disp(cross_box_affine_residual)}`."
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Construct and map the partial-fraction terms

    Divide the solved identity \(\sum_i c_iD_i=1\) by the complete denominator
    product and multiply by the editable numerator:

    \[
    \frac{N}{\prod_iD_i}
    =N\sum_i\frac{c_i}{\prod_{j\ne i}D_j}.
    \]

    The propagator objects and their original positions are retained. We label
    the four children with temporary partial-fraction slots 1--4; these are
    display/provenance ids, not Kira topology numbers. The later FIRE adapter
    maps them by their actual global propagator sets.
    """)
    return


@app.cell
def _(
    E,
    PARTIAL_FRACTION_SLOTS: tuple[tuple[int, tuple[int, ...]], ...],
    canonical_zero,
    cross_box_affine_coefficients,
    cross_box_integrand,
    cross_box_loop_scalar_products,
    partial_fraction,
):
    _unsorted_partial_fractions = partial_fraction(
        cross_box_integrand,
        removed_indices=range(len(cross_box_integrand.denominators)),
        loop_scalar_products=cross_box_loop_scalar_products,
        coefficients=cross_box_affine_coefficients,
    )
    cross_box_family_by_sources = {
        _sources: _family_id
        for _family_id, _sources in PARTIAL_FRACTION_SLOTS
    }
    cross_box_partial_fractions = tuple(
        sorted(
            _unsorted_partial_fractions,
            key=lambda _child: cross_box_family_by_sources[
                _child.retained_indices
            ],
        )
    )
    cross_box_partial_fraction_residual = canonical_zero(
        sum(
            (
                _child.integrand.as_expression()
                for _child in cross_box_partial_fractions
            ),
            E("0"),
        )
        - cross_box_integrand.as_expression()
    )
    assert cross_box_partial_fraction_residual == E("0")
    return (
        cross_box_family_by_sources,
        cross_box_partial_fraction_residual,
        cross_box_partial_fractions,
    )


@app.cell(hide_code=True)
def _(
    cross_box_affine_coefficients,
    cross_box_family_by_sources,
    cross_box_partial_fraction_residual,
    cross_box_partial_fractions,
    mo,
    spenso_table,
):
    mo.vstack(
        [
            mo.md("### Explicit partial-fraction slot mapping"),
            spenso_table(
                [
                    {
                        "retained propagators": tuple(
                            _index + 1 for _index in _sources
                        ),
                        "partial-fraction slot": _family_id,
                    }
                    for _sources, _family_id in sorted(
                        cross_box_family_by_sources.items(),
                        key=lambda _item: _item[1],
                    )
                ]
            ),
            mo.md("### Restored partial-fraction terms"),
            spenso_table(
                [
                    {
                        "partial-fraction slot": (
                            cross_box_family_by_sources[_child.retained_indices]
                        ),
                        "removed propagator": _child.removed_index + 1,
                        "c_i": cross_box_affine_coefficients[
                            _child.removed_index
                        ],
                        "retained propagators": tuple(
                            _index + 1 for _index in _child.retained_indices
                        ),
                        "child numerator": _child.integrand.numerator,
                        "child term": _child.integrand.as_expression(),
                    }
                    for _child in cross_box_partial_fractions
                ]
            ),
            mo.md(
                "Exact partial-fraction residual: "
                f"`{spenso_disp(cross_box_partial_fraction_residual)}`."
            ),
        ]
    )
    return


@app.cell
def _(E, Expression, S, Sequence, canonical_zero):
    def numerator_relations(
        propagators: Sequence[Expression],
        propagator_labels: Sequence[Expression],
        loop_scalar_products: Sequence[Expression],
    ) -> tuple[tuple[Expression, Expression], ...]:
        """Solve each loop scalar product in one propagator basis."""

        propagators = tuple(propagators)
        propagator_labels = tuple(propagator_labels)
        loop_scalar_products = tuple(loop_scalar_products)
        if len(propagators) != len(propagator_labels):
            raise ValueError("Each propagator needs exactly one formal label")
        if len(propagators) != len(loop_scalar_products):
            raise ValueError(
                "Choose one independent propagator for each loop scalar product"
            )

        weights = tuple(S(f"__nr_{index}") for index in range(len(propagators)))
        combination = sum(
            (
                weight * propagator
                for weight, propagator in zip(
                    weights, propagators, strict=True
                )
            ),
            E("0"),
        ).expand()

        relations = []
        for target_index, target in enumerate(loop_scalar_products):
            equations = tuple(
                combination.coefficient(loop_product)
                - (1 if loop_index == target_index else 0)
                for loop_index, loop_product in enumerate(loop_scalar_products)
            )
            solution = tuple(Expression.solve_linear_system(equations, weights))
            if len(solution) != len(weights) or any(
                bool(coefficient.contains(weight))
                for coefficient in solution
                for weight in weights
            ):
                raise ValueError("Chosen propagators are not an independent basis")

            remainder = canonical_zero(
                sum(
                    (
                        coefficient * propagator
                        for coefficient, propagator in zip(
                            solution, propagators, strict=True
                        )
                    ),
                    E("0"),
                )
                - target
            )
            replacement = (
                sum(
                    (
                        coefficient * label
                        for coefficient, label in zip(
                            solution, propagator_labels, strict=True
                        )
                    ),
                    E("0"),
                )
                - remainder
            ).expand()
            relations.append((target, replacement))
        return tuple(relations)

    return (numerator_relations,)


@app.cell
def _(E, S, canonical_zero, mo, numerator_relations, spenso_table):
    _relation_x, _relation_y, _relation_a, _relation_b = S(
        "relation_x", "relation_y", "relation_a", "relation_b"
    )
    _relation_labels = S("relation_D1", "relation_D2")
    _relation_propagators = (
        _relation_x + _relation_a,
        _relation_y + _relation_b,
    )
    _relations = numerator_relations(
        _relation_propagators,
        _relation_labels,
        (_relation_x, _relation_y),
    )
    _relation_rows = []
    for _target, _replacement in _relations:
        _reconstructed = _replacement
        for _label, _propagator in zip(
            _relation_labels, _relation_propagators, strict=True
        ):
            _reconstructed = _reconstructed.replace(_label, _propagator)
        _residual = canonical_zero(_reconstructed - _target)
        assert _residual == E("0")
        _relation_rows.append(
            {
                "loop product": _target,
                "propagator-basis replacement": _replacement,
                "reconstruction residual": _residual,
            }
        )
    numerator_relations_showcase = tuple(_relation_rows)
    spenso_table(numerator_relations_showcase)
    return


@app.cell
def _(
    Expression,
    Integrand,
    NumeratorReduction,
    ReducedIntegralTerm,
    S,
    Sequence,
    numerator_relations,
):
    def reduce_numerator(
        integrand: Integrand,
        *,
        loop_scalar_products: Sequence[Expression],
    ) -> NumeratorReduction:
        """Rewrite a numerator and structurally cancel propagator factors."""

        if len(integrand.denominators) != len(tuple(loop_scalar_products)):
            raise ValueError(
                "Choose one independent propagator for each loop scalar product"
            )
        labels = tuple(
            S(f"__prop_{index}") for index in range(len(integrand.denominators))
        )
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
        for powers, coefficient in polynomial.coefficient_list(list(labels)):
            terms.append(
                ReducedIntegralTerm(
                    coefficient=coefficient.to_expression(),
                    propagators=integrand.denominators,
                    integral_indices=tuple(1 - int(power) for power in powers),
                )
            )
        return NumeratorReduction(tuple(terms), relations, reduced)

    return (reduce_numerator,)


@app.cell
def _(E, Integrand, S, canonical_zero, mo, reduce_numerator, spenso_table):
    _reduction_x, _reduction_y, _reduction_a, _reduction_b = S(
        "reduction_x", "reduction_y", "reduction_a", "reduction_b"
    )
    _reduction_integrand = Integrand(
        _reduction_x * _reduction_y + _reduction_x,
        (_reduction_x + _reduction_a, _reduction_y + _reduction_b),
    )
    _reduction = reduce_numerator(
        _reduction_integrand,
        loop_scalar_products=(_reduction_x, _reduction_y),
    )
    _reduction_residual = canonical_zero(
        sum((_term.as_expression() for _term in _reduction.terms), E("0"))
        - _reduction_integrand.as_expression()
    )
    assert _reduction_residual == E("0")
    reduce_numerator_showcase = tuple(
        {
            "coefficient": _term.coefficient,
            "integral indices": _term.integral_indices,
            "reconstruction residual": _reduction_residual,
        }
        for _term in _reduction.terms
    )
    spenso_table(reduce_numerator_showcase)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Rewrite each numerator in its three-propagator basis

    The four children have different bases. For each one we solve the three
    loop scalar products in terms of formal propagator labels, rewrite the
    numerator, and read off the resulting integral powers.
    """)
    return


@app.cell
def _(
    E,
    canonical_zero,
    cross_box_integrand,
    cross_box_loop_scalar_products,
    cross_box_partial_fractions,
    reduce_numerator,
):
    cross_box_numerator_reductions = tuple(
        reduce_numerator(
            _child.integrand,
            loop_scalar_products=cross_box_loop_scalar_products,
        )
        for _child in cross_box_partial_fractions
    )
    cross_box_numerator_reduction_residual = canonical_zero(
        sum(
            (
                _term.as_expression()
                for _reduction in cross_box_numerator_reductions
                for _term in _reduction.terms
            ),
            E("0"),
        )
        - cross_box_integrand.as_expression()
    )
    assert cross_box_numerator_reduction_residual == E("0")
    return (
        cross_box_numerator_reduction_residual,
        cross_box_numerator_reductions,
    )


@app.cell(hide_code=True)
def _(
    cross_box_family_by_sources,
    cross_box_numerator_reduction_residual,
    cross_box_numerator_reductions,
    cross_box_partial_fractions,
    mo,
    spenso_table,
):
    mo.vstack(
        [
            mo.md("### Family-local propagator-label bases"),
            spenso_table(
                [
                    {
                        "family": (
                            f"topo{cross_box_family_by_sources[_child.retained_indices]}"
                        ),
                        "label": f"__prop_{_position}",
                        "propagator": _propagator,
                    }
                    for _child in cross_box_partial_fractions
                    for _position, _propagator in enumerate(
                        _child.integrand.denominators
                    )
                ]
            ),
            mo.md("### Scalar-product relations"),
            spenso_table(
                [
                    {
                        "family": (
                            f"topo{cross_box_family_by_sources[_child.retained_indices]}"
                        ),
                        "loop product": _target,
                        "replacement": _replacement,
                    }
                    for _child, _reduction in zip(
                        cross_box_partial_fractions,
                        cross_box_numerator_reductions,
                        strict=True,
                    )
                    for _target, _replacement in _reduction.relations
                ]
            ),
            mo.md("### Rewritten child numerators"),
            spenso_table(
                [
                    {
                        "family": (
                            f"topo{cross_box_family_by_sources[_child.retained_indices]}"
                        ),
                        "input numerator": _child.integrand.numerator,
                        "rewritten polynomial": _reduction.reduced_numerator,
                    }
                    for _child, _reduction in zip(
                        cross_box_partial_fractions,
                        cross_box_numerator_reductions,
                        strict=True,
                    )
                ]
            ),
            mo.md("### Terms after numerator cancellation"),
            spenso_table(
                [
                    {
                        "family": (
                            f"topo{cross_box_family_by_sources[_child.retained_indices]}"
                        ),
                        "coefficient": _term.coefficient,
                        "integral indices": _term.integral_indices,
                    }
                    for _child, _reduction in zip(
                        cross_box_partial_fractions,
                        cross_box_numerator_reductions,
                        strict=True,
                    )
                    for _term in _reduction.terms
                ]
            ),
            mo.md(
                "Exact numerator-reduction residual: "
                f"`{spenso_disp(cross_box_numerator_reduction_residual)}`."
            ),
        ]
    )
    return


@app.cell
def _(
    CrossBoxPreIBP,
    E,
    Expression,
    S,
    canonical_zero,
    partial_fraction_slot_id,
):
    def validate_pre_ibp(result: CrossBoxPreIBP) -> dict[str, Expression]:
        """Validate every algebraic handoff represented by a pre-IBP result."""

        checks = {
            "affine propagator relation": canonical_zero(
                result.propagators[0]
                - result.propagators[1]
                - result.propagators[2]
                + result.propagators[3]
                + result.delta
            ),
            "partial-fraction reconstruction": canonical_zero(
                sum(
                    (
                        child.integrand.as_expression()
                        for child in result.partial_fractions
                    ),
                    E("0"),
                )
                - result.integrand.as_expression()
            ),
            "numerator-rewrite reconstruction": canonical_zero(
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
            "IBP-input reconstruction": canonical_zero(
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
        for child, reduction in zip(
            result.partial_fractions,
            result.numerator_reductions,
            strict=True,
        ):
            family_id = partial_fraction_slot_id(child.retained_indices)
            labels = tuple(
                S(f"__prop_{index}")
                for index in range(len(child.integrand.denominators))
            )
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
                checks[f"PF slot {family_id} relation {relation_index}"] = canonical_zero(
                    reconstructed - target
                )

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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Assemble the IBP inputs

    The final objects below are coefficients times family/index vectors. This
    is the boundary object consumed by an IBP reducer; no reduction rule has
    been applied yet.
    """)
    return


@app.cell
def _(
    CrossBoxPreIBP,
    IntegralContribution,
    cross_box_delta,
    cross_box_family_by_sources,
    cross_box_integrand,
    cross_box_loop_denominators,
    cross_box_loop_scalar_products,
    cross_box_numerator_reductions,
    cross_box_partial_fractions,
    validate_pre_ibp,
):
    _contributions = []
    for _child, _reduction in zip(
        cross_box_partial_fractions,
        cross_box_numerator_reductions,
        strict=True,
    ):
        _family_id = cross_box_family_by_sources[_child.retained_indices]
        _contributions.extend(
            IntegralContribution(
                family_id=_family_id,
                source_indices=_child.retained_indices,
                propagators=_term.propagators,
                integral_indices=_term.integral_indices,
                coefficient=_term.coefficient,
            )
            for _term in _reduction.terms
        )
    cross_box_contributions = tuple(_contributions)
    _unchecked_pre_ibp = CrossBoxPreIBP(
        propagators=cross_box_loop_denominators,
        loop_scalar_products=cross_box_loop_scalar_products,
        delta=cross_box_delta,
        integrand=cross_box_integrand,
        partial_fractions=cross_box_partial_fractions,
        numerator_reductions=cross_box_numerator_reductions,
        contributions=cross_box_contributions,
    )
    cross_box_checks = validate_pre_ibp(_unchecked_pre_ibp)
    cross_box_pre_ibp = CrossBoxPreIBP(
        propagators=cross_box_loop_denominators,
        loop_scalar_products=cross_box_loop_scalar_products,
        delta=cross_box_delta,
        integrand=cross_box_integrand,
        partial_fractions=cross_box_partial_fractions,
        numerator_reductions=cross_box_numerator_reductions,
        contributions=cross_box_contributions,
        checks=cross_box_checks,
    )
    return cross_box_checks, cross_box_contributions, cross_box_pre_ibp


@app.cell(hide_code=True)
def _(cross_box_checks, cross_box_contributions, mo, spenso_table):
    mo.vstack(
        [
            spenso_table(
                [
                    {
                        "partial-fraction slot": _term.family_id,
                        "source propagators": tuple(
                            _index + 1 for _index in _term.source_indices
                        ),
                        "integral indices": _term.integral_indices,
                        "coefficient": _term.coefficient,
                    }
                    for _term in cross_box_contributions
                ]
            ),
            mo.md("### Exact boundary checks"),
            spenso_table(
                [
                    {
                        "check": _name,
                        "residual": _residual,
                    }
                    for _name, _residual in cross_box_checks.items()
                ]
            ),
        ]
    )
    return


@app.cell
def _(
    CrossBoxPreIBP,
    E,
    Expression,
    IntegralContribution,
    Integrand,
    dot,
    partial_fraction,
    partial_fraction_slot_id,
    reduce_numerator,
    square,
    validate_pre_ibp,
):
    def preprocess_cross_box(
        *,
        k1: Expression,
        p1: Expression,
        p2: Expression,
        q: Expression,
        numerator: Expression | None = None,
    ) -> CrossBoxPreIBP:
        """Run the visible cross-box stages as one regression convenience."""

        numerator = E("1") if numerator is None else numerator
        propagators = (
            square(k1),
            square(k1 - p1),
            square(p2 - k1),
            square(p1 + p2 - k1) - q**2,
        )
        loop_scalar_products = (square(k1), dot(k1, p1), dot(k1, p2))
        delta = q**2 - 2 * dot(p1, p2)
        integrand = Integrand(numerator, propagators)
        children = tuple(
            sorted(
                partial_fraction(
                    integrand,
                    removed_indices=range(len(propagators)),
                    loop_scalar_products=loop_scalar_products,
                ),
                key=lambda child: partial_fraction_slot_id(
                    child.retained_indices
                ),
            )
        )
        reductions = tuple(
            reduce_numerator(
                child.integrand,
                loop_scalar_products=loop_scalar_products,
            )
            for child in children
        )

        mapped = []
        for child, reduction in zip(children, reductions, strict=True):
            family_id = partial_fraction_slot_id(child.retained_indices)
            mapped.extend(
                IntegralContribution(
                    family_id=family_id,
                    source_indices=child.retained_indices,
                    propagators=term.propagators,
                    integral_indices=term.integral_indices,
                    coefficient=term.coefficient,
                )
                for term in reduction.terms
            )

        result = CrossBoxPreIBP(
            propagators=propagators,
            loop_scalar_products=loop_scalar_products,
            delta=delta,
            integrand=integrand,
            partial_fractions=children,
            numerator_reductions=reductions,
            contributions=tuple(mapped),
        )
        result.checks = validate_pre_ibp(result)
        return result


    return (preprocess_cross_box,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Validate the linear-system partial fractioner

    First we exercise the same solve and reconstruction for two through seven
    propagators, an overcomplete relation supplied explicitly, spectator
    denominators, and rejected invalid inputs. These checks execute whenever
    the notebook executes.
    """)
    return


@app.cell
def _(
    E,
    Integrand,
    S,
    canonical_zero,
    partial_fraction,
    partial_fraction_coefficients,
    prod,
):
    _validation_rows = []
    for _count in range(2, 8):
        _loop_products = tuple(
            S(f"validation_x_{_count}_{_index}")
            for _index in range(_count - 1)
        )
        _delta = S(f"validation_delta_{_count}")
        _numerator = S(f"validation_numerator_{_count}")
        _weights = (
            *(
                E(str((-1) ** _index * (_index + 1)))
                for _index in range(_count - 1)
            ),
            E("1"),
        )
        _denominators = (
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
        )
        _expected_coefficients = tuple(
            _weight / _delta for _weight in _weights
        )
        _solved_coefficients = partial_fraction_coefficients(
            _denominators,
            _loop_products,
        )
        assert all(
            canonical_zero(_actual - _expected) == E("0")
            for _actual, _expected in zip(
                _solved_coefficients,
                _expected_coefficients,
                strict=True,
            )
        )

        _requested_order = tuple(reversed(range(_count)))
        _terms = partial_fraction(
            Integrand(_numerator, _denominators),
            removed_indices=_requested_order,
            loop_scalar_products=_loop_products,
        )
        assert tuple(_term.removed_index for _term in _terms) == _requested_order
        for _term in _terms:
            _expected_retained = tuple(
                _index
                for _index in range(_count)
                if _index != _term.removed_index
            )
            assert _term.retained_indices == _expected_retained
            assert _term.integrand.denominators == tuple(
                _denominators[_index] for _index in _expected_retained
            )
            assert canonical_zero(
                _term.integrand.numerator
                - _numerator * _expected_coefficients[_term.removed_index]
            ) == E("0")
        _residual = canonical_zero(
            sum(
                (_term.integrand.as_expression() for _term in _terms),
                E("0"),
            )
            - _numerator / prod(_denominators)
        )
        assert _residual == E("0")
        _validation_rows.append(
            {"case": f"linear relation with N={_count}", "residual": _residual}
        )

    _x, _a, _b = S("validation_x", "validation_a", "validation_b")
    _overcomplete_denominators = (_x, _x + _a, _x + _b)
    _overcomplete_coefficients = (
        -2 / (_a + _b),
        1 / (_a + _b),
        1 / (_a + _b),
    )
    _overcomplete_terms = partial_fraction(
        Integrand(E("1"), _overcomplete_denominators),
        removed_indices=range(3),
        loop_scalar_products=(_x,),
        coefficients=_overcomplete_coefficients,
    )
    _overcomplete_residual = canonical_zero(
        sum(
            (_term.integrand.as_expression() for _term in _overcomplete_terms),
            E("0"),
        )
        - 1 / prod(_overcomplete_denominators)
    )
    assert _overcomplete_residual == E("0")
    _validation_rows.append(
        {"case": "explicit overcomplete relation", "residual": _overcomplete_residual}
    )

    _spectator0, _spectator1, _spectator2 = S(
        "validation_s0", "validation_s1", "validation_s2"
    )
    _spectator_delta = S("validation_sdelta")
    _spectator_denominators = (
        _spectator0,
        _x,
        _spectator1,
        _spectator_delta - 3 * _x,
        _spectator2,
    )
    _spectator_terms = partial_fraction(
        Integrand(E("1"), _spectator_denominators),
        removed_indices=(3, 1),
        loop_scalar_products=(_x,),
    )
    assert tuple(_term.removed_index for _term in _spectator_terms) == (3, 1)
    assert tuple(_term.retained_indices for _term in _spectator_terms) == (
        (0, 1, 2, 4),
        (0, 2, 3, 4),
    )
    _spectator_residual = canonical_zero(
        sum(
            (_term.integrand.as_expression() for _term in _spectator_terms),
            E("0"),
        )
        - 1 / prod(_spectator_denominators)
    )
    assert _spectator_residual == E("0")
    _validation_rows.append(
        {"case": "spectators and global indices", "residual": _spectator_residual}
    )

    try:
        partial_fraction(
            Integrand(E("1"), (_x, _spectator_delta - _x)),
            removed_indices=(0, 0),
            loop_scalar_products=(_x,),
        )
    except ValueError as _error:
        assert "must be unique" in str(_error)
    else:
        raise AssertionError("Duplicate denominator indices were accepted")
    _validation_rows.append(
        {"case": "duplicate indices rejected", "residual": E("0")}
    )

    try:
        partial_fraction(
            Integrand(E("1"), (_x, _spectator_delta - _x)),
            removed_indices=(0, 1),
            loop_scalar_products=(_x,),
            coefficients=(E("1"), E("2")),
        )
    except ValueError as _error:
        assert "do not solve" in str(_error)
    else:
        raise AssertionError("Invalid affine coefficients were accepted")
    _validation_rows.append(
        {"case": "invalid coefficients rejected", "residual": E("0")}
    )

    linear_system_validation_rows = tuple(_validation_rows)
    return (linear_system_validation_rows,)


@app.cell(hide_code=True)
def _(E, linear_system_validation_rows, mo, spenso_table):
    assert len(linear_system_validation_rows) == 10
    assert all(_row["residual"] == E("0") for _row in linear_system_validation_rows)
    spenso_table(
        [
            {
                "validation": _row["case"],
                "residual": _row["residual"],
            }
            for _row in linear_system_validation_rows
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Historical scalar cross-box oracle

    The following one-way check compares the native derivation with the retained
    Mathematica result. It supplies no propagator, coefficient, family mapping,
    or control-flow input to the calculation above.
    """)
    return


@app.cell
def _(
    E,
    canonical_zero,
    cross_box_k1,
    cross_box_p1,
    cross_box_p2,
    cross_box_q,
    dot,
    preprocess_cross_box,
):
    _reference_delta = cross_box_q**2 - 2 * dot(
        cross_box_p1, cross_box_p2
    )
    mathematica_reference_pre_ibp = preprocess_cross_box(
        k1=cross_box_k1,
        p1=cross_box_p1,
        p2=cross_box_p2,
        q=cross_box_q,
        numerator=E("1"),
    )
    _expected_family_ids = (1, 2, 3, 4)
    _expected_sources = (
        (0, 1, 2),
        (0, 1, 3),
        (0, 2, 3),
        (1, 2, 3),
    )
    _expected_coefficients = (
        -1 / _reference_delta,
        1 / _reference_delta,
        1 / _reference_delta,
        -1 / _reference_delta,
    )
    assert tuple(
        _term.family_id for _term in mathematica_reference_pre_ibp.contributions
    ) == _expected_family_ids
    assert tuple(
        _term.source_indices
        for _term in mathematica_reference_pre_ibp.contributions
    ) == _expected_sources
    assert all(
        _term.integral_indices == (1, 1, 1)
        for _term in mathematica_reference_pre_ibp.contributions
    )
    reference_validation = {
        **mathematica_reference_pre_ibp.checks,
        "delta convention": canonical_zero(
            mathematica_reference_pre_ibp.delta - _reference_delta
        ),
        **{
            f"PF slot {_family_id} coefficient": canonical_zero(
                _term.coefficient - _expected
            )
            for _family_id, (_term, _expected) in enumerate(
                zip(
                    mathematica_reference_pre_ibp.contributions,
                    _expected_coefficients,
                    strict=True,
                ),
                start=1,
            )
        },
    }
    assert all(_residual == E("0") for _residual in reference_validation.values())
    scalar_reference_comparison = [
        {
            "expected PF slot": _expected_family,
            "actual PF slot": _term.family_id,
            "expected sources": tuple(_index + 1 for _index in _expected_source),
            "actual sources": tuple(_index + 1 for _index in _term.source_indices),
            "expected indices": (1, 1, 1),
            "actual indices": _term.integral_indices,
            "coefficient residual": canonical_zero(
                _term.coefficient - _expected_coefficient
            ),
        }
        for _expected_family, _expected_source, _expected_coefficient, _term in zip(
            _expected_family_ids,
            _expected_sources,
            _expected_coefficients,
            mathematica_reference_pre_ibp.contributions,
            strict=True,
        )
    ]
    return (
        mathematica_reference_pre_ibp,
        reference_validation,
        scalar_reference_comparison,
    )


@app.cell(hide_code=True)
def _(mo, reference_validation, scalar_reference_comparison, spenso_table):
    mo.vstack(
        [
            spenso_table(scalar_reference_comparison),
            mo.callout(
                "Historical scalar validation passed: all four partial-fraction "
                "slots, the independent delta convention, sign pattern, "
                "and exact reconstructions agree with the retained Mathematica "
                "result. "
                + " ".join(
                    f"{_name}={spenso_disp(_residual)};"
                    for _name, _residual in reference_validation.items()
                ),
                kind="success",
            ),
        ]
    )
    return


@app.cell
def _():
    CROSS_BOX_FIRE_SOURCE_ORDERS = (
        (2, 3, 5),
        (2, 3, 4),
        (2, 5, 4),
        (3, 5, 4),
    )
    CROSS_BOX_KIRA_FAMILY_BLOCKS = {
        "11": (20, 21, 22, 23),
        "10": (24, 25, 26, 27),
        "01": (28, 29, 30, 31),
    }
    return CROSS_BOX_FIRE_SOURCE_ORDERS, CROSS_BOX_KIRA_FAMILY_BLOCKS


@app.cell
def _(IntegralContribution):
    def map_contributions_to_kira_block(
        contributions,
        *,
        loop_source_indices,
        family_ids,
        family_source_orders,
    ):
        """Map native graph-order children to one historical Kira block."""

        loop_source_indices = tuple(loop_source_indices)
        if len(family_ids) != len(family_source_orders):
            raise ValueError("Every family id needs one ordered source tuple")
        family_by_sources = {
            frozenset(source_order): (family_id, tuple(source_order))
            for family_id, source_order in zip(
                family_ids, family_source_orders, strict=True
            )
        }
        if len(family_by_sources) != len(family_ids):
            raise ValueError("Kira family source sets must be unique")

        mapped = []
        for contribution in contributions:
            global_sources = tuple(
                loop_source_indices[index]
                for index in contribution.source_indices
            )
            try:
                family_id, ordered_sources = family_by_sources[
                    frozenset(global_sources)
                ]
            except KeyError as error:
                raise ValueError(
                    "No Kira family matches graph sources "
                    f"{global_sources}"
                ) from error
            permutation = tuple(
                global_sources.index(source) for source in ordered_sources
            )
            mapped.append(
                IntegralContribution(
                    family_id=family_id,
                    source_indices=ordered_sources,
                    propagators=tuple(
                        contribution.propagators[index]
                        for index in permutation
                    ),
                    integral_indices=tuple(
                        contribution.integral_indices[index]
                        for index in permutation
                    ),
                    coefficient=contribution.coefficient,
                )
            )
        return tuple(mapped)

    return (map_contributions_to_kira_block,)


@app.cell
def _(
    CROSS_BOX_FIRE_SOURCE_ORDERS,
    CROSS_BOX_KIRA_FAMILY_BLOCKS,
    E,
    canonical_zero,
    cross_box_loop_propagator_indices,
    cross_box_pre_ibp,
    map_contributions_to_kira_block,
    mathematica_reference_pre_ibp,
    mo,
    spenso_table,
):
    cross_box_contributions_by_cut = {
        _cut_name: map_contributions_to_kira_block(
            cross_box_pre_ibp.contributions,
            loop_source_indices=cross_box_loop_propagator_indices,
            family_ids=_family_ids,
            family_source_orders=CROSS_BOX_FIRE_SOURCE_ORDERS,
        )
        for _cut_name, _family_ids in CROSS_BOX_KIRA_FAMILY_BLOCKS.items()
    }
    mathematica_reference_contributions_by_cut = {
        _cut_name: map_contributions_to_kira_block(
            mathematica_reference_pre_ibp.contributions,
            loop_source_indices=cross_box_loop_propagator_indices,
            family_ids=_family_ids,
            family_source_orders=CROSS_BOX_FIRE_SOURCE_ORDERS,
        )
        for _cut_name, _family_ids in CROSS_BOX_KIRA_FAMILY_BLOCKS.items()
    }
    for _source, _mapped_by_cut in (
        (cross_box_pre_ibp.contributions, cross_box_contributions_by_cut),
        (
            mathematica_reference_pre_ibp.contributions,
            mathematica_reference_contributions_by_cut,
        ),
    ):
        _source_expression = sum(
            (_term.as_expression() for _term in _source), E("0")
        )
        for _mapped in _mapped_by_cut.values():
            assert canonical_zero(
                sum((_term.as_expression() for _term in _mapped), E("0"))
                - _source_expression
            ) == E("0")

    map_contributions_to_kira_block_showcase = tuple(
        {
            "cut": _cut_name,
            "family": f"topo{_term.family_id}",
            "ordered graph sources": tuple(
                _source + 1 for _source in _term.source_indices
            ),
            "indices": _term.integral_indices,
        }
        for _cut_name, _terms in cross_box_contributions_by_cut.items()
        for _term in _terms
    )
    spenso_table(map_contributions_to_kira_block_showcase)
    return (
        cross_box_contributions_by_cut,
        mathematica_reference_contributions_by_cut,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 7. Solve the three reducible cut blocks with Kira

    The inferred graph loop order is \((D_3,D_4,D_5,D_6)\). The retained FIRE
    evidence uses \((D_3,D_4,D_6,D_5)\), so the cell above performs a visible,
    checked permutation before assigning the historical family blocks:
    `topo20`--`topo23` for cut `11`, `topo24`--`topo27` for `10`, and
    `topo28`--`topo31` for `01`. Cut `00` requires all four loop propagators
    and is evaluated directly rather than through a three-propagator child.

    Every Kira project requests the fixed complete domain
    \(\{1,0,-1\}^3\). This keeps manifests stable while the editable numerator
    changes.

    Evaluation is automatic and resumable. On a fresh checkout this cell runs
    Kira; later evaluations reuse the complete result only when the generated
    project still matches its persisted manifest exactly. Changed inputs are
    rejected instead of silently consuming stale reductions.
    """)
    return


@app.cell
def _():
    from itertools import product
    from pathlib import Path

    from ludy_kira import (
        IntegralFamily,
        KinematicInvariant,
        Kinematics,
        Kira,
        KiraProject,
        Propagator,
        ReductionBounds,
        ReductionResult,
        ScalarProductRule,
    )

    return (
        IntegralFamily,
        KinematicInvariant,
        Kinematics,
        Kira,
        KiraProject,
        Path,
        Propagator,
        ReductionBounds,
        ReductionResult,
        ScalarProductRule,
        product,
    )


@app.cell
def _(
    CROSS_BOX_FIRE_SOURCE_ORDERS,
    CROSS_BOX_KIRA_FAMILY_BLOCKS,
    E,
    IntegralFamily,
    KinematicInvariant,
    Kinematics,
    KiraProject,
    Propagator,
    ReductionBounds,
    S,
    ScalarProductRule,
    product,
):
    def build_cross_box_kira_projects(*, k1, p1, p2, q, propagators):
        """Build all fixed Kira projects for the three reducible cut blocks."""

        ipp1p1, ipp1p2, ipp2p2 = S("ipp1p1", "ipp1p2", "ipp2p2")
        all_propagators = tuple(
            Propagator(momentum, mass_squared)
            for momentum, mass_squared in propagators
        )
        preferred_indices = {
            20: ((0, 0, 1), (1, 0, 1)),
            21: ((0, 1, 1),),
            22: ((0, 1, 0), (1, 1, 0)),
            23: ((0, 1, 0), (1, 0, 1), (1, 1, 1)),
            24: ((0, 0, 1), (0, 1, 1), (1, 0, 1)),
            25: ((0, 1, 1), (1, 0, 1)),
            26: ((0, 1, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
            27: ((0, 1, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
            28: ((0, 0, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
            29: ((0, 1, 1), (1, 1, 0)),
            30: ((0, 1, 0), (0, 1, 1), (1, 1, 0)),
            31: ((0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)),
        }
        target_indices = tuple(product((1, 0, -1), repeat=3))
        bounds = ReductionBounds(sectors=(7,), r=9, s=4, d=2)
        projects = {}
        for cut_name, family_ids in CROSS_BOX_KIRA_FAMILY_BLOCKS.items():
            for family_id, source_indices in zip(
                family_ids, CROSS_BOX_FIRE_SOURCE_ORDERS, strict=True
            ):
                has_internal_mass = 5 in source_indices
                invariants = [KinematicInvariant(ipp1p2, 2)]
                scalar_products = [
                    ScalarProductRule(p1, p2, ipp1p2),
                ]
                if cut_name == "11":
                    scalar_products[:0] = [
                        ScalarProductRule(p1, p1, E("0")),
                        ScalarProductRule(p2, p2, E("0")),
                    ]
                elif cut_name == "10":
                    invariants.append(KinematicInvariant(ipp2p2, 2))
                    scalar_products[:0] = [
                        ScalarProductRule(p1, p1, E("0")),
                        ScalarProductRule(p2, p2, ipp2p2),
                    ]
                elif cut_name == "01":
                    invariants.insert(0, KinematicInvariant(ipp1p1, 2))
                    scalar_products[:0] = [
                        ScalarProductRule(p1, p1, ipp1p1),
                        ScalarProductRule(p2, p2, E("0")),
                    ]
                else:
                    raise ValueError(f"Unsupported Kira cut block {cut_name}")
                if has_internal_mass:
                    invariants.insert(
                        0,
                        KinematicInvariant(q**2, 2, kira_name="q2"),
                    )

                family = IntegralFamily(
                    name=f"topo{family_id}",
                    loop_momenta=(k1,),
                    propagators=tuple(
                        all_propagators[index] for index in source_indices
                    ),
                    top_level_sectors=(7,),
                )
                projects[family_id] = KiraProject(
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
                    preferred_masters=tuple(
                        family(*indices)
                        for indices in preferred_indices[family_id]
                    ),
                    check_masters=True,
                    reconstruct_mass=has_internal_mass,
                )
        return projects

    return (build_cross_box_kira_projects,)


@app.cell
def _(
    CROSS_BOX_FIRE_SOURCE_ORDERS,
    CROSS_BOX_KIRA_FAMILY_BLOCKS,
    E,
    Path,
    build_cross_box_kira_projects,
    canonical_zero,
    cross_box_denominators,
    cross_box_k1,
    cross_box_p1,
    cross_box_p2,
    cross_box_propagators,
    cross_box_q,
    mo,
    square,
    spenso_table,
):
    cross_box_kira_projects = build_cross_box_kira_projects(
        k1=cross_box_k1,
        p1=cross_box_p1,
        p2=cross_box_p2,
        q=cross_box_q,
        propagators=cross_box_propagators,
    )
    cross_box_kira_workdir_root = (
        Path(__file__).resolve().parents[1] / "runs"
    )
    _source_by_family = {
        _family_id: _source_indices
        for _family_ids in CROSS_BOX_KIRA_FAMILY_BLOCKS.values()
        for _family_id, _source_indices in zip(
            _family_ids, CROSS_BOX_FIRE_SOURCE_ORDERS, strict=True
        )
    }
    _cut_by_family = {
        _family_id: _cut_name
        for _cut_name, _family_ids in CROSS_BOX_KIRA_FAMILY_BLOCKS.items()
        for _family_id in _family_ids
    }
    _project_rows = []
    for _family_id, _project in sorted(cross_box_kira_projects.items()):
        _source_indices = _source_by_family[_family_id]
        _actual_propagators = tuple(
            square(_propagator.momentum) - _propagator.mass_squared
            for _propagator in _project.family.propagators
        )
        _expected_propagators = tuple(
            cross_box_denominators[_index] for _index in _source_indices
        )
        assert all(
            canonical_zero(_actual - _expected) == E("0")
            for _actual, _expected in zip(
                _actual_propagators, _expected_propagators, strict=True
            )
        )
        _project_rows.append(
            {
                "cut": _cut_by_family[_family_id],
                "family": _project.family.name,
                "source propagators": tuple(
                    _index + 1 for _index in _source_indices
                ),
                "targets": len(_project.targets),
                "preferred masters": tuple(_project.preferred_masters),
                "workdir": str(
                    cross_box_kira_workdir_root
                    / f"dy-cross-box-topo{_family_id}"
                ),
            }
        )
    cross_box_kira_project_showcase = tuple(_project_rows)
    spenso_table(cross_box_kira_project_showcase)
    return cross_box_kira_projects, cross_box_kira_workdir_root


@app.cell
def _(Expression, Sequence):
    def apply_kinematic_rules(
        expression: Expression,
        rules: Sequence[tuple[Expression, Expression]],
    ) -> Expression:
        """Apply an explicit ordered set of kinematic replacements."""

        result = expression
        for source, target in rules:
            result = result.replace(source, target)
        return result.expand()

    return (apply_kinematic_rules,)


@app.cell
def _(E, S, apply_kinematic_rules, canonical_zero, dot, minkd, mo, p, square, spenso_table):
    _kinematic_p1, _kinematic_p2 = p(1, minkd), p(2, minkd)
    _kinematic_invariant = S("kinematic_ipp1p2")
    _kinematic_rules = (
        (square(_kinematic_p1), E("0")),
        (square(_kinematic_p2), E("0")),
        (dot(_kinematic_p1, _kinematic_p2), _kinematic_invariant),
    )
    _kinematic_input = (
        square(_kinematic_p1)
        + square(_kinematic_p2)
        + 2 * dot(_kinematic_p1, _kinematic_p2)
    )
    _kinematic_output = apply_kinematic_rules(
        _kinematic_input, _kinematic_rules
    )
    _kinematic_residual = canonical_zero(
        _kinematic_output - 2 * _kinematic_invariant
    )
    assert _kinematic_residual == E("0")
    apply_kinematic_rules_showcase = {
        "input": _kinematic_input,
        "output": _kinematic_output,
        "residual": _kinematic_residual,
    }
    spenso_table([apply_kinematic_rules_showcase])
    return


@app.cell
def _(E, S, cross_box_p1, cross_box_p2, dot, square):
    cross_box_ipp1p1, cross_box_ipp1p2, cross_box_ipp2p2 = S(
        "ipp1p1", "ipp1p2", "ipp2p2"
    )
    cross_box_ibp_kinematic_rules_by_cut = {
        "11": (
            (square(cross_box_p1), E("0")),
            (square(cross_box_p2), E("0")),
            (dot(cross_box_p1, cross_box_p2), cross_box_ipp1p2),
        ),
        "10": (
            (square(cross_box_p1), E("0")),
            (square(cross_box_p2), cross_box_ipp2p2),
            (dot(cross_box_p1, cross_box_p2), cross_box_ipp1p2),
        ),
        "01": (
            (square(cross_box_p1), cross_box_ipp1p1),
            (square(cross_box_p2), E("0")),
            (dot(cross_box_p1, cross_box_p2), cross_box_ipp1p2),
        ),
        "00": (
            (square(cross_box_p1), cross_box_ipp1p1),
            (square(cross_box_p2), cross_box_ipp2p2),
            (dot(cross_box_p1, cross_box_p2), cross_box_ipp1p2),
        ),
    }
    return (
        cross_box_ibp_kinematic_rules_by_cut,
        cross_box_ipp1p1,
        cross_box_ipp1p2,
        cross_box_ipp2p2,
    )


@app.cell
def _(IntegralContribution):
    def contribution_to_kira_expression(
        contribution: IntegralContribution,
        projects,
    ):
        """Turn a family/index contribution into an exact Kira integral atom."""

        family = projects[contribution.family_id].family
        target = family(*contribution.integral_indices)
        return contribution.coefficient * target

    return (contribution_to_kira_expression,)


@app.cell
def _(
    E,
    canonical_zero,
    contribution_to_kira_expression,
    cross_box_contributions_by_cut,
    cross_box_kira_projects,
    mo,
    spenso_table,
):
    contribution_to_kira_expression_showcase = tuple(
        {
            "cut": _cut_name,
            "family": f"topo{_contribution.family_id}",
            "indices": _contribution.integral_indices,
            "expression": contribution_to_kira_expression(
                _contribution, cross_box_kira_projects
            ),
        }
        for _cut_name, _contributions in cross_box_contributions_by_cut.items()
        for _contribution in _contributions
    )
    assert all(
        canonical_zero(
            contribution_to_kira_expression(
                _contribution, cross_box_kira_projects
            )
        ) != E("0")
        for _contributions in cross_box_contributions_by_cut.values()
        for _contribution in _contributions
    )
    spenso_table(contribution_to_kira_expression_showcase)
    return


@app.cell
def _(E, apply_kinematic_rules, contribution_to_kira_expression):
    def assemble_ibp_expression(contributions, projects, kinematic_rules):
        """Assemble the on-shell multi-family expression submitted to IBP rules."""

        return sum(
            (
                apply_kinematic_rules(
                    contribution_to_kira_expression(contribution, projects),
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
    cross_box_contributions_by_cut,
    cross_box_ibp_kinematic_rules_by_cut,
    cross_box_kira_projects,
    mathematica_reference_contributions_by_cut,
    mo,
    spenso_table,
):
    cross_box_ibp_inputs_by_cut = {
        _cut_name: assemble_ibp_expression(
            _contributions,
            cross_box_kira_projects,
            cross_box_ibp_kinematic_rules_by_cut[_cut_name],
        )
        for _cut_name, _contributions in cross_box_contributions_by_cut.items()
    }
    mathematica_reference_ibp_inputs_by_cut = {
        _cut_name: assemble_ibp_expression(
            _contributions,
            cross_box_kira_projects,
            cross_box_ibp_kinematic_rules_by_cut[_cut_name],
        )
        for _cut_name, _contributions in (
            mathematica_reference_contributions_by_cut.items()
        )
    }
    assemble_ibp_expression_showcase = tuple(
        {
            "cut": _cut_name,
            "editable numerator IBP input": cross_box_ibp_inputs_by_cut[
                _cut_name
            ],
            "scalar validation IBP input": (
                mathematica_reference_ibp_inputs_by_cut[_cut_name]
            ),
        }
        for _cut_name in cross_box_contributions_by_cut
    )
    spenso_table(assemble_ibp_expression_showcase)
    return cross_box_ibp_inputs_by_cut, mathematica_reference_ibp_inputs_by_cut


@app.function
def run_kira_projects(kira, projects, workdir_root):
    """Run or resume all deterministic Kira projects sequentially."""

    doctor = kira.doctor()
    doctor.raise_for_errors()
    reductions = {}
    for family_id in sorted(projects):
        project = projects[family_id]
        reductions[family_id] = kira.reduce(
            family=project.family,
            kinematics=project.kinematics,
            targets=project.targets,
            bounds=project.bounds,
            preferred_masters=project.preferred_masters,
            check_masters=project.check_masters,
            reconstruct_mass=project.reconstruct_mass,
            workdir=workdir_root / f"dy-cross-box-topo{family_id}",
            parallel="physical",
            resume=True,
            require_complete=True,
            timeout=120,
        )
    return doctor, reductions


@app.cell
def _(Path, cross_box_kira_projects, mo, spenso_table):
    class _ShowcaseDoctor:
        version = "showcase"

        def raise_for_errors(self):
            return None


    class _ShowcaseKira:
        def __init__(self):
            self.calls = []

        def doctor(self):
            return _ShowcaseDoctor()

        def reduce(self, **arguments):
            self.calls.append(arguments)
            return arguments["family"].name


    _showcase_kira = _ShowcaseKira()
    _showcase_doctor, _showcase_reductions = run_kira_projects(
        _showcase_kira,
        cross_box_kira_projects,
        Path("/tmp/ludy-kira-showcase"),
    )
    assert _showcase_doctor.version == "showcase"
    assert tuple(_showcase_reductions) == tuple(range(20, 32))
    assert all(_call["resume"] is True for _call in _showcase_kira.calls)
    run_kira_projects_showcase = tuple(
        {
            "family": _call["family"].name,
            "targets": len(_call["targets"]),
            "resume": _call["resume"],
            "workdir": str(_call["workdir"]),
        }
        for _call in _showcase_kira.calls
    )
    spenso_table(run_kira_projects_showcase)
    return


@app.cell
def _(Kira, cross_box_kira_projects, cross_box_kira_workdir_root):
    cross_box_kira_doctor, cross_box_kira_reductions = run_kira_projects(
        Kira(),
        cross_box_kira_projects,
        cross_box_kira_workdir_root,
    )
    return cross_box_kira_doctor, cross_box_kira_reductions


@app.cell(hide_code=True)
def _(cross_box_kira_doctor, cross_box_kira_reductions, mo, spenso_table):
    _kira_status = mo.vstack(
        [
            mo.callout(
                f"Kira `{cross_box_kira_doctor.version}` completed or resumed "
                "all twelve families with complete reductions.",
                kind="success",
            ),
            spenso_table(
                [
                    {
                        "family": f"topo{_family_id}",
                        "targets": len(_result.requested_targets),
                        "masters": len(_result.masters),
                        "zeros": len(_result.zero_integrals),
                    }
                    for _family_id, _result in sorted(
                        cross_box_kira_reductions.items()
                    )
                ]
            ),
        ]
    )
    _kira_status
    return


@app.cell
def _(IBPReductionTerm, apply_kinematic_rules):
    def apply_ibp_reductions(
        contributions,
        projects,
        reductions,
        kinematic_rules,
    ):
        """Apply complete Kira rules term by term without losing provenance."""

        terms = []
        for contribution in contributions:
            project = projects[contribution.family_id]
            result = reductions[contribution.family_id].require_complete()
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
                    family_id=contribution.family_id,
                    coefficient=coefficient,
                    target=target,
                    reduced_integral=result.rules[target],
                )
            )
        return tuple(terms)

    return (apply_ibp_reductions,)


@app.cell
def _(
    E,
    Path,
    ReductionResult,
    S,
    apply_ibp_reductions,
    canonical_zero,
    cross_box_ibp_kinematic_rules_by_cut,
    cross_box_kira_projects,
    mathematica_reference_contributions_by_cut,
    mo,
    spenso_table,
):
    _showcase_contribution = mathematica_reference_contributions_by_cut["11"][0]
    _showcase_project = cross_box_kira_projects[
        _showcase_contribution.family_id
    ]
    _showcase_target = _showcase_project.family(
        *_showcase_contribution.integral_indices
    )
    _showcase_master = S("ibp_showcase_master")
    _showcase_result = ReductionResult(
        family_name=_showcase_project.family.name,
        arity=3,
        requested_targets=(_showcase_target,),
        rules={_showcase_target: _showcase_master},
        masters=(),
        workdir=Path("/tmp/ludy-ibp-showcase"),
    )
    _showcase_terms = apply_ibp_reductions(
        (_showcase_contribution,),
        {_showcase_contribution.family_id: _showcase_project},
        {_showcase_contribution.family_id: _showcase_result},
        cross_box_ibp_kinematic_rules_by_cut["11"],
    )
    _showcase_term = _showcase_terms[0]
    _showcase_residual = canonical_zero(
        _showcase_term.reduced_expression()
        - _showcase_term.coefficient * _showcase_master
    )
    assert _showcase_residual == E("0")
    apply_ibp_reductions_showcase = {
        "target": _showcase_term.target,
        "reduced": _showcase_term.reduced_expression(),
        "residual": _showcase_residual,
    }
    spenso_table([apply_ibp_reductions_showcase])
    return


@app.cell
def _(
    E,
    apply_ibp_reductions,
    canonical_zero,
    cross_box_contributions_by_cut,
    cross_box_ibp_inputs_by_cut,
    cross_box_ibp_kinematic_rules_by_cut,
    cross_box_kira_projects,
    cross_box_kira_reductions,
    mathematica_reference_contributions_by_cut,
    mathematica_reference_ibp_inputs_by_cut,
):
    cross_box_ibp_terms_by_cut = {
        _cut_name: apply_ibp_reductions(
            _contributions,
            cross_box_kira_projects,
            cross_box_kira_reductions,
            cross_box_ibp_kinematic_rules_by_cut[_cut_name],
        )
        for _cut_name, _contributions in cross_box_contributions_by_cut.items()
    }
    mathematica_reference_ibp_terms_by_cut = {
        _cut_name: apply_ibp_reductions(
            _contributions,
            cross_box_kira_projects,
            cross_box_kira_reductions,
            cross_box_ibp_kinematic_rules_by_cut[_cut_name],
        )
        for _cut_name, _contributions in (
            mathematica_reference_contributions_by_cut.items()
        )
    }
    for _cut_name, _terms in cross_box_ibp_terms_by_cut.items():
        assert canonical_zero(
            sum(
                (_term.input_expression() for _term in _terms),
                E("0"),
            )
            - cross_box_ibp_inputs_by_cut[_cut_name]
        ) == E("0")
    for _cut_name, _terms in mathematica_reference_ibp_terms_by_cut.items():
        assert canonical_zero(
            sum(
                (_term.input_expression() for _term in _terms),
                E("0"),
            )
            - mathematica_reference_ibp_inputs_by_cut[_cut_name]
        ) == E("0")
    cross_box_master_expressions_by_cut = {
        _cut_name: canonical_zero(
            sum(
                (_term.reduced_expression() for _term in _terms),
                E("0"),
            )
        )
        for _cut_name, _terms in cross_box_ibp_terms_by_cut.items()
    }
    mathematica_reference_master_expressions_by_cut = {
        _cut_name: canonical_zero(
            sum(
                (_term.reduced_expression() for _term in _terms),
                E("0"),
            )
        )
        for _cut_name, _terms in mathematica_reference_ibp_terms_by_cut.items()
    }
    return (
        cross_box_ibp_terms_by_cut,
        cross_box_master_expressions_by_cut,
        mathematica_reference_master_expressions_by_cut,
    )


@app.cell(hide_code=True)
def _(cross_box_ibp_terms_by_cut, cross_box_master_expressions_by_cut, mo, spenso_table):
    _ibp_output = mo.vstack(
        [
            spenso_table(
                [
                    {
                        "cut": _cut_name,
                        "family": f"topo{_term.family_id}",
                        "coefficient": _term.coefficient,
                        "target": _term.target,
                        "Kira right-hand side": _term.reduced_integral,
                    }
                    for _cut_name, _terms in cross_box_ibp_terms_by_cut.items()
                    for _term in _terms
                ]
            ),
            spenso_table(
                [
                    {
                        "cut": _cut_name,
                        "combined editable-numerator master expression": _expression,
                    }
                    for _cut_name, _expression in (
                        cross_box_master_expressions_by_cut.items()
                    )
                ]
            ),
        ]
    )
    _ibp_output
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Apply the cut after IBP

    Each six-line mask is projected onto the automatically discovered loop
    lines. The cut is then applied to the reduced masters in global graph
    space: a family or master that lacks any required positive exponent is set
    to zero. Cuts `11`, `10`, and `01` have three-propagator children. Cut `00`
    requires all four loop lines and therefore has a separate direct branch.
    """)
    return


@app.cell
def _(E, Replacement, canonical_zero):
    def cut_filter_masters(
        expression,
        *,
        masters_by_family,
        family_sources,
        required_source_indices,
    ):
        """Drop masters incompatible with a cut in global propagator space."""

        kept = []
        dropped = []
        replacements = []
        for family_id, masters in sorted(masters_by_family.items()):
            source_indices = tuple(family_sources[family_id])
            for master in masters:
                powers = tuple(int(argument) for argument in master)
                survives = all(
                    source_index in source_indices
                    and powers[source_indices.index(source_index)] > 0
                    for source_index in required_source_indices
                )
                if survives:
                    kept.append(master)
                else:
                    dropped.append(master)
                    replacements.append(Replacement(master, E("0")))
        filtered = (
            expression.replace_multiple(replacements, repeat=False)
            if replacements
            else expression
        )
        return canonical_zero(filtered), tuple(kept), tuple(dropped)

    return (cut_filter_masters,)


@app.cell
def _(
    CROSS_BOX_FIRE_SOURCE_ORDERS,
    E,
    canonical_zero,
    cross_box_kira_projects,
    cut_filter_masters,
    mo,
    spenso_table,
):
    _showcase_sources = dict(
        zip((20, 21, 22, 23), CROSS_BOX_FIRE_SOURCE_ORDERS, strict=True)
    )
    _showcase_topo20 = cross_box_kira_projects[20].family
    _showcase_topo22 = cross_box_kira_projects[22].family
    _showcase_expression = (
        _showcase_topo20(1, 0, 1)
        + _showcase_topo20(0, 0, 1)
        + _showcase_topo22(1, 1, 0)
    )
    _showcase_filtered, _showcase_kept, _showcase_dropped = cut_filter_masters(
        _showcase_expression,
        masters_by_family={
            20: (_showcase_topo20(1, 0, 1), _showcase_topo20(0, 0, 1)),
            22: (_showcase_topo22(1, 1, 0),),
        },
        family_sources=_showcase_sources,
        required_source_indices=(2, 5),
    )
    _showcase_residual = canonical_zero(
        _showcase_filtered
        - _showcase_topo20(1, 0, 1)
        - _showcase_topo22(1, 1, 0)
    )
    assert _showcase_residual == E("0")
    cut_filter_masters_showcase = {
        "kept": tuple(_showcase_kept),
        "dropped": tuple(_showcase_dropped),
        "residual": _showcase_residual,
    }
    spenso_table([cut_filter_masters_showcase])
    return


@app.cell
def _(
    CROSS_BOX_FIRE_SOURCE_ORDERS,
    CROSS_BOX_KIRA_FAMILY_BLOCKS,
    cross_box_cutsets,
    cross_box_kira_reductions,
    cross_box_loop_propagator_indices,
    cross_box_master_expressions_by_cut,
    cut_filter_masters,
    mathematica_reference_master_expressions_by_cut,
):
    cross_box_required_loop_sources_by_cut = {
        _cut_name: tuple(
            _source
            for _source in cross_box_loop_propagator_indices
            if _mask[_source]
        )
        for _cut_name, _mask in cross_box_cutsets.items()
    }
    _family_sources = {
        _family_id: _source_indices
        for _family_ids in CROSS_BOX_KIRA_FAMILY_BLOCKS.values()
        for _family_id, _source_indices in zip(
            _family_ids, CROSS_BOX_FIRE_SOURCE_ORDERS, strict=True
        )
    }
    cross_box_cut_expressions_by_cut = {}
    cross_box_cut_kept_masters_by_cut = {}
    cross_box_cut_dropped_masters_by_cut = {}
    mathematica_reference_cut_expressions_by_cut = {}
    for _cut_name, _family_ids in CROSS_BOX_KIRA_FAMILY_BLOCKS.items():
        _masters_by_family = {
            _family_id: cross_box_kira_reductions[_family_id].masters
            for _family_id in _family_ids
        }
        (
            cross_box_cut_expressions_by_cut[_cut_name],
            cross_box_cut_kept_masters_by_cut[_cut_name],
            cross_box_cut_dropped_masters_by_cut[_cut_name],
        ) = cut_filter_masters(
            cross_box_master_expressions_by_cut[_cut_name],
            masters_by_family=_masters_by_family,
            family_sources=_family_sources,
            required_source_indices=(
                cross_box_required_loop_sources_by_cut[_cut_name]
            ),
        )
        (
            mathematica_reference_cut_expressions_by_cut[_cut_name],
            _reference_kept,
            _reference_dropped,
        ) = cut_filter_masters(
            mathematica_reference_master_expressions_by_cut[_cut_name],
            masters_by_family=_masters_by_family,
            family_sources=_family_sources,
            required_source_indices=(
                cross_box_required_loop_sources_by_cut[_cut_name]
            ),
        )

    _expected_kept = {
        "11": {"topo20(1,0,1)", "topo22(1,1,0)"},
        "10": {"topo26(1,1,1)"},
        "01": {"topo28(1,1,1)"},
    }
    assert {
        _cut_name: {
            _master.format_plain()
            for _master in cross_box_cut_kept_masters_by_cut[_cut_name]
        }
        for _cut_name in CROSS_BOX_KIRA_FAMILY_BLOCKS
    } == _expected_kept
    assert cross_box_required_loop_sources_by_cut["00"] == (2, 3, 4, 5)
    return (
        cross_box_cut_dropped_masters_by_cut,
        cross_box_cut_expressions_by_cut,
        cross_box_cut_kept_masters_by_cut,
        cross_box_required_loop_sources_by_cut,
        mathematica_reference_cut_expressions_by_cut,
    )


@app.cell(hide_code=True)
def _(
    cross_box_cut_dropped_masters_by_cut,
    cross_box_cut_expressions_by_cut,
    cross_box_cut_kept_masters_by_cut,
    cross_box_required_loop_sources_by_cut,
    mo,
    spenso_table,
):
    spenso_table(
        [
            *(
                {
                    "cut": _cut_name,
                    "required graph propagators": tuple(
                        _source + 1
                        for _source in cross_box_required_loop_sources_by_cut[
                            _cut_name
                        ]
                    ),
                    "kept masters": tuple(
                        cross_box_cut_kept_masters_by_cut[_cut_name]
                    ),
                    "dropped masters": tuple(
                        cross_box_cut_dropped_masters_by_cut[_cut_name]
                    ),
                    "cut-filtered expression": cross_box_cut_expressions_by_cut[
                        _cut_name
                    ],
                    "evaluation": "Kira IBP then cut filter",
                }
                for _cut_name in ("11", "10", "01")
            ),
            {
                "cut": "00",
                "required graph propagators": (3, 4, 5, 6),
                "kept masters": (),
                "dropped masters": (),
                "cut-filtered expression": "direct four-line cut",
                "evaluation": "no three-propagator IBP child",
            },
        ]
    )
    return


@app.cell
def _(Replacement):
    def identify_masters(expression, identifications):
        """Apply explicit analytic identifications to surviving masters."""

        replacements = tuple(
            Replacement(master, value) for master, value in identifications
        )
        return (
            expression.replace_multiple(replacements, repeat=False)
            if replacements
            else expression
        )

    return (identify_masters,)


@app.cell
def _(E, S, canonical_zero, identify_masters, mo, spenso_table):
    _identify_m1, _identify_m2, _identify_b = S(
        "identify_M1", "identify_M2", "identify_B"
    )
    _identify_result = identify_masters(
        _identify_m1 + 2 * _identify_m2,
        ((_identify_m1, _identify_b), (_identify_m2, _identify_b)),
    )
    _identify_residual = canonical_zero(_identify_result - 3 * _identify_b)
    assert _identify_residual == E("0")
    identify_masters_showcase = {
        "input": "M1 + 2*M2",
        "identification": "M1 = M2 = B",
        "output": _identify_result,
        "residual": _identify_residual,
    }
    spenso_table([identify_masters_showcase])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Evaluate the surviving cut masters

    The master names are useful for inspecting the IBP output, but the
    Mathematica calculation continues one step further. Cut `11` contains the
    massive cut bubble

    \[
    B_{\mathrm{cutm}}(s,m^2)=-\frac{(\mu^2e^{\gamma_E})^\epsilon}
    {8\sqrt{\pi}\,\Gamma((d-1)/2)\sqrt{s}}
    \left(\frac{s-m^2}{2\sqrt{s}}\right)^{d-3}.
    \]

    Cuts `10` and `01` contain the corresponding cut triangle

    \[
    T_{\mathrm{cutm}}(p_i^2,s,q^2)=
    \frac{(\mu^2e^{\gamma_E})^\epsilon}
    {4\,\Gamma((d-2)/2)\,s^{d-3}}
    \left[p_i^2(s-q^2)q^2\right]^{(d-4)/2}.
    \]

    We keep every symbolic master identification visible, then substitute its
    analytic value into both the editable-numerator and scalar-validation
    paths. The fully cut `00` sector remains a direct four-line calculation.
    """)
    return


@app.cell
def _(E, Expression, S):
    def bcutm(
        momentum_squared: Expression,
        mass_squared: Expression,
        *,
        dimension: Expression,
        epsilon: Expression,
        mu_squared: Expression,
        euler_gamma: Expression,
    ) -> Expression:
        """Return the massive cut-bubble master used by the DY notebook."""

        _argument = S("__bcutm_gamma_argument")
        gamma_factor = E("gamma(__bcutm_gamma_argument)").replace(
            _argument,
            (dimension - 1) / 2,
        )
        return -(
            (mu_squared * euler_gamma.exp()) ** epsilon
            / (
                8
                * E("pi").sqrt()
                * gamma_factor
                * momentum_squared.sqrt()
            )
            * (
                (momentum_squared - mass_squared)
                / (2 * momentum_squared.sqrt())
            )
            ** (dimension - 3)
        )

    return (bcutm,)


@app.cell
def _(E, ParseMode, S, bcutm, canonical_zero, mo, spenso_table):
    _bubble_s, _bubble_m2, _bubble_ep, _bubble_mu2 = S(
        "bubble_s", "bubble_m2", "bubble_ep", "bubble_mu2"
    )
    _bubble_euler_gamma = E("EulerGamma", ParseMode.Mathematica)
    _bubble_at_three_dimensions = bcutm(
        _bubble_s,
        _bubble_m2,
        dimension=E("3"),
        epsilon=_bubble_ep,
        mu_squared=_bubble_mu2,
        euler_gamma=_bubble_euler_gamma,
    )
    _bubble_expected = -(
        (_bubble_mu2 * _bubble_euler_gamma.exp()) ** _bubble_ep
        / (8 * E("pi").sqrt() * _bubble_s.sqrt())
    )
    _bubble_residual = canonical_zero(
        _bubble_at_three_dimensions - _bubble_expected
    )
    assert _bubble_residual == E("0")
    bcutm_showcase = {
        "specialization": "d = 3",
        "value": _bubble_at_three_dimensions,
        "expected": _bubble_expected,
        "residual": _bubble_residual,
    }
    spenso_table([bcutm_showcase])
    return


@app.cell
def _(E, Expression, S):
    def tcutm(
        external_virtuality: Expression,
        momentum_squared: Expression,
        mass_squared: Expression,
        *,
        dimension: Expression,
        epsilon: Expression,
        mu_squared: Expression,
        euler_gamma: Expression,
    ) -> Expression:
        """Return the massive cut-triangle master used by the DY notebook."""

        _argument = S("__tcutm_gamma_argument")
        gamma_factor = E("gamma(__tcutm_gamma_argument)").replace(
            _argument,
            (dimension - 2) / 2,
        )
        return (
            (mu_squared * euler_gamma.exp()) ** epsilon
            / (4 * gamma_factor * momentum_squared ** (dimension - 3))
            * (
                external_virtuality
                * (momentum_squared - mass_squared)
                * mass_squared
            )
            ** ((dimension - 4) / 2)
        )

    return (tcutm,)


@app.cell
def _(E, ParseMode, S, canonical_zero, mo, tcutm, spenso_table):
    _triangle_v, _triangle_s, _triangle_m2 = S(
        "triangle_v", "triangle_s", "triangle_m2"
    )
    _triangle_ep, _triangle_mu2 = S("triangle_ep", "triangle_mu2")
    _triangle_euler_gamma = E("EulerGamma", ParseMode.Mathematica)
    _triangle_at_four_dimensions = tcutm(
        _triangle_v,
        _triangle_s,
        _triangle_m2,
        dimension=E("4"),
        epsilon=_triangle_ep,
        mu_squared=_triangle_mu2,
        euler_gamma=_triangle_euler_gamma,
    )
    _triangle_expected = (
        (_triangle_mu2 * _triangle_euler_gamma.exp()) ** _triangle_ep
        / (4 * _triangle_s)
    )
    _triangle_residual = canonical_zero(
        _triangle_at_four_dimensions - _triangle_expected
    )
    assert _triangle_residual == E("0")
    tcutm_showcase = {
        "specialization": "d = 4",
        "value": _triangle_at_four_dimensions,
        "expected": _triangle_expected,
        "residual": _triangle_residual,
    }
    spenso_table([tcutm_showcase])
    return


@app.cell
def _(E, ParseMode, S):
    cross_box_dimension = S("d")
    cross_box_epsilon = S("ep")
    cross_box_mu_squared = S("musq")
    cross_box_euler_gamma = E("EulerGamma", ParseMode.Mathematica)
    return (
        cross_box_dimension,
        cross_box_epsilon,
        cross_box_euler_gamma,
        cross_box_mu_squared,
    )


@app.cell
def _(
    S,
    canonical_zero,
    cross_box_cut_dropped_masters_by_cut,
    cross_box_cut_expressions_by_cut,
    cross_box_cut_kept_masters_by_cut,
    cross_box_ipp1p1,
    cross_box_ipp1p2,
    cross_box_ipp2p2,
    cross_box_kira_projects,
    cross_box_q,
    identify_masters,
    mathematica_reference_cut_expressions_by_cut,
):
    cross_box_cut_expression = cross_box_cut_expressions_by_cut["11"]
    cross_box_cut_kept_masters = cross_box_cut_kept_masters_by_cut["11"]
    cross_box_cut_dropped_masters = cross_box_cut_dropped_masters_by_cut["11"]
    mathematica_reference_cut_expression = (
        mathematica_reference_cut_expressions_by_cut["11"]
    )
    cross_box_cut_master_symbols_by_cut = {
        "11": S("Bcutm")(2 * cross_box_ipp1p2, cross_box_q**2),
        "10": S("Tcutm")(
            cross_box_ipp2p2,
            2 * cross_box_ipp1p2,
            cross_box_q**2,
        ),
        "01": S("Tcutm")(
            cross_box_ipp1p1,
            2 * cross_box_ipp1p2,
            cross_box_q**2,
        ),
    }
    cross_box_master_identifications_by_cut = {
        "11": (
            (
                cross_box_kira_projects[20].family(1, 0, 1),
                cross_box_cut_master_symbols_by_cut["11"],
            ),
            (
                cross_box_kira_projects[22].family(1, 1, 0),
                cross_box_cut_master_symbols_by_cut["11"],
            ),
        ),
        "10": (
            (
                cross_box_kira_projects[26].family(1, 1, 1),
                cross_box_cut_master_symbols_by_cut["10"],
            ),
        ),
        "01": (
            (
                cross_box_kira_projects[28].family(1, 1, 1),
                cross_box_cut_master_symbols_by_cut["01"],
            ),
        ),
    }
    cross_box_final_expressions_by_cut = {
        _cut_name: canonical_zero(
            identify_masters(
                cross_box_cut_expressions_by_cut[_cut_name],
                cross_box_master_identifications_by_cut[_cut_name],
            )
        )
        for _cut_name in ("11", "10", "01")
    }
    mathematica_reference_final_expressions_by_cut = {
        _cut_name: canonical_zero(
            identify_masters(
                mathematica_reference_cut_expressions_by_cut[_cut_name],
                cross_box_master_identifications_by_cut[_cut_name],
            )
        )
        for _cut_name in ("11", "10", "01")
    }
    cross_box_cut_bubble = cross_box_cut_master_symbols_by_cut["11"]
    cross_box_master_identifications = (
        cross_box_master_identifications_by_cut["11"]
    )
    cross_box_final_expression = cross_box_final_expressions_by_cut["11"]
    mathematica_reference_final_expression = (
        mathematica_reference_final_expressions_by_cut["11"]
    )
    return (
        cross_box_cut_bubble,
        cross_box_cut_master_symbols_by_cut,
        cross_box_final_expressions_by_cut,
        mathematica_reference_cut_expression,
        mathematica_reference_final_expression,
        mathematica_reference_final_expressions_by_cut,
    )


@app.cell
def _(
    bcutm,
    canonical_zero,
    cross_box_cut_master_symbols_by_cut,
    cross_box_dimension,
    cross_box_epsilon,
    cross_box_euler_gamma,
    cross_box_final_expressions_by_cut,
    cross_box_ipp1p1,
    cross_box_ipp1p2,
    cross_box_ipp2p2,
    cross_box_mu_squared,
    cross_box_q,
    identify_masters,
    mathematica_reference_final_expressions_by_cut,
    tcutm,
):
    cross_box_analytic_master_values_by_cut = {
        "11": bcutm(
            2 * cross_box_ipp1p2,
            cross_box_q**2,
            dimension=cross_box_dimension,
            epsilon=cross_box_epsilon,
            mu_squared=cross_box_mu_squared,
            euler_gamma=cross_box_euler_gamma,
        ),
        "10": tcutm(
            cross_box_ipp2p2,
            2 * cross_box_ipp1p2,
            cross_box_q**2,
            dimension=cross_box_dimension,
            epsilon=cross_box_epsilon,
            mu_squared=cross_box_mu_squared,
            euler_gamma=cross_box_euler_gamma,
        ),
        "01": tcutm(
            cross_box_ipp1p1,
            2 * cross_box_ipp1p2,
            cross_box_q**2,
            dimension=cross_box_dimension,
            epsilon=cross_box_epsilon,
            mu_squared=cross_box_mu_squared,
            euler_gamma=cross_box_euler_gamma,
        ),
    }
    cross_box_analytic_expressions_by_cut = {
        _cut_name: canonical_zero(
            identify_masters(
                cross_box_final_expressions_by_cut[_cut_name],
                (
                    (
                        cross_box_cut_master_symbols_by_cut[_cut_name],
                        cross_box_analytic_master_values_by_cut[_cut_name],
                    ),
                ),
            )
        )
        for _cut_name in ("11", "10", "01")
    }
    mathematica_reference_analytic_expressions_by_cut = {
        _cut_name: canonical_zero(
            identify_masters(
                mathematica_reference_final_expressions_by_cut[_cut_name],
                (
                    (
                        cross_box_cut_master_symbols_by_cut[_cut_name],
                        cross_box_analytic_master_values_by_cut[_cut_name],
                    ),
                ),
            )
        )
        for _cut_name in ("11", "10", "01")
    }
    cross_box_cut_bubble_analytic = (
        cross_box_analytic_master_values_by_cut["11"]
    )
    cross_box_analytic_expression = cross_box_analytic_expressions_by_cut["11"]
    mathematica_reference_analytic_expression = (
        mathematica_reference_analytic_expressions_by_cut["11"]
    )
    return (
        cross_box_analytic_expressions_by_cut,
        cross_box_cut_bubble_analytic,
        mathematica_reference_analytic_expression,
    )


@app.cell(hide_code=True)
def _(
    cross_box_analytic_expressions_by_cut,
    cross_box_cut_dropped_masters_by_cut,
    cross_box_cut_expressions_by_cut,
    cross_box_cut_kept_masters_by_cut,
    cross_box_final_expressions_by_cut,
    mo,
    spenso_table,
):
    _cut_output = spenso_table(
        [
            {
                "cut": _cut_name,
                "kept masters": tuple(
                    cross_box_cut_kept_masters_by_cut[_cut_name]
                ),
                "dropped masters": tuple(
                    cross_box_cut_dropped_masters_by_cut[_cut_name]
                ),
                "after cut": cross_box_cut_expressions_by_cut[_cut_name],
                "after master identification": cross_box_final_expressions_by_cut[
                    _cut_name
                ],
                "after analytic master": cross_box_analytic_expressions_by_cut[
                    _cut_name
                ],
            }
            for _cut_name in ("11", "10", "01")
        ]
    )
    _cut_output
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Validate the completed scalar result against Mathematica/FIRE

    This independent oracle uses the historical scalar numerator `1`. After
    translating its loop routing to the six-line graph, cut `11` must retain
    `topo20(1,0,1)` and `topo22(1,1,0)`. We check the exact master expression,
    identify both with the same cut bubble, evaluate that master, and reproduce
    the recorded expansion through order \(\epsilon^0\).
    """)
    return


@app.cell
def _(S, cross_box_ipp1p2, cross_box_kira_projects, cross_box_q):
    _d = S("d")
    _delta = cross_box_q**2 - 2 * cross_box_ipp1p2
    _topo20 = cross_box_kira_projects[20].family
    _topo22 = cross_box_kira_projects[22].family
    mathematica_scalar_cut_oracle = (
        2
        * (_d - 3)
        * (_topo20(1, 0, 1) + _topo22(1, 1, 0))
        / ((_d - 4) * _delta**2)
    )
    return (mathematica_scalar_cut_oracle,)


@app.cell
def _(mathematica_scalar_cut_oracle, mo, spenso_table):
    mathematica_scalar_cut_oracle_showcase = {
        "cut": "11 (Mathematica label 00)",
        "retained FIRE master expression": mathematica_scalar_cut_oracle,
    }
    spenso_table([mathematica_scalar_cut_oracle_showcase])
    return


@app.cell
def _(
    E,
    S,
    canonical_zero,
    cross_box_cut_bubble,
    cross_box_ipp1p2,
    cross_box_kira_reductions,
    cross_box_q,
    mathematica_reference_cut_expression,
    mathematica_reference_final_expression,
    mathematica_scalar_cut_oracle,
):
    _d = S("d")
    _delta = cross_box_q**2 - 2 * cross_box_ipp1p2
    mathematica_expected_cut_expression = mathematica_scalar_cut_oracle
    mathematica_expected_final_expression = (
        4
        * (_d - 3)
        * cross_box_cut_bubble
        / ((_d - 4) * _delta**2)
    )
    assert all(
        _result.complete for _result in cross_box_kira_reductions.values()
    )
    _cut_residual = canonical_zero(
        mathematica_reference_cut_expression
        - mathematica_expected_cut_expression
    )
    _final_residual = canonical_zero(
        mathematica_reference_final_expression
        - mathematica_expected_final_expression
    )
    assert _cut_residual == E("0")
    assert _final_residual == E("0")
    mathematica_ibp_validation_rows = (
        {
            "check": "scalar cut 11 master expression",
            "residual": _cut_residual,
        },
        {
            "check": "scalar cut 11 Bcutm identification",
            "residual": _final_residual,
        },
    )
    return (
        mathematica_expected_cut_expression,
        mathematica_expected_final_expression,
        mathematica_ibp_validation_rows,
    )


@app.cell
def _(
    E,
    S,
    canonical_zero,
    cross_box_cut_bubble_analytic,
    cross_box_dimension,
    cross_box_epsilon,
    cross_box_euler_gamma,
    cross_box_ipp1p2,
    cross_box_mu_squared,
    cross_box_q,
    mathematica_reference_analytic_expression,
):
    _s = S("s")
    _delta = cross_box_q**2 - 2 * cross_box_ipp1p2
    mathematica_expected_analytic_expression = (
        4
        * (cross_box_dimension - 3)
        * cross_box_cut_bubble_analytic
        / ((cross_box_dimension - 4) * _delta**2)
    )

    _dimensionally_regularized = mathematica_expected_analytic_expression.replace(
        cross_box_ipp1p2,
        _s / 2,
    ).replace(
        cross_box_dimension,
        4 - 2 * cross_box_epsilon,
    )
    _series = _dimensionally_regularized.series(
        cross_box_epsilon,
        0,
        0,
    ).to_expression().expand()
    _series = _series.replace(
        (cross_box_euler_gamma.exp() * cross_box_mu_squared).log(),
        cross_box_euler_gamma + cross_box_mu_squared.log(),
    )
    _series = _series.replace(
        (
            (_s - cross_box_q**2)
            / (2 * _s.sqrt())
        ).log(),
        (
            (_s - cross_box_q**2)
            / _s.sqrt()
        ).log()
        - E("2").log(),
    )
    mathematica_actual_epsilon_expansion = canonical_zero(_series)
    mathematica_expected_epsilon_expansion = -(
        1
        + cross_box_epsilon * cross_box_mu_squared.log()
        - 2
        * cross_box_epsilon
        * (
            (_s - cross_box_q**2)
            / _s.sqrt()
        ).log()
    ) / (
        4
        * cross_box_epsilon
        * E("pi")
        * _s
        * (cross_box_q**2 - _s)
    )
    _series_residual = canonical_zero(
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
    _analytic_residual = canonical_zero(
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
    mathematica_analytic_validation_rows = tuple(_analytic_rows)
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
    spenso_table,
):
    if not mathematica_ibp_validation_rows:
        _validation_output = mo.vstack(
            [
                spenso_table(mathematica_analytic_validation_rows),
                mo.md(
                    "Recorded expansion through epsilon^0: "
                    f"`{spenso_disp(mathematica_expected_epsilon_expansion)}`"
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
                mo.md(
                    "Expected scalar result after the cut: "
                    f"`{spenso_disp(mathematica_expected_cut_expression)}`"
                ),
                mo.md(
                    "Expected completed scalar result: "
                    f"`{spenso_disp(mathematica_expected_final_expression)}`"
                ),
                mo.md(
                    "Expected analytic scalar result: "
                    f"`{spenso_disp(mathematica_expected_analytic_expression)}`"
                ),
                mo.md(
                    "Expansion through epsilon^0: "
                    f"`{spenso_disp(mathematica_expected_epsilon_expansion)}`"
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
        "topo20--31 reductions, and the Bcutm/Tcutm evaluations for cuts 11, "
        "10, and 01 are complete. Cut 00 is a direct four-line contribution, "
        "not a missing Kira rule and not zero by default. Reproducing the later "
        "physical Mathematica sum still requires porting its contracted "
        "xboxNumContr numerator, direct cut measure, and distribution dressing.",
        kind="info",
    )
    return


if __name__ == "__main__":
    app.run()
