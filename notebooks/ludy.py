import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import importlib.metadata as metadata
    import json

    import gammaloop
    import marimo as mo

    return gammaloop, json, metadata, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Things currently broken

    - cannot do dot products easily
    - cannot display tensors nicely (! with typst support)
    - cannot construct vectors (rank one tagged)
    - no easy way to construct broadcasting functions
    -
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Local GammaLoop + Symbolica Community

    This notebook runs in the uv environment defined by `pyproject.toml`.
    Both native packages are built from the sibling working copies.
    """)
    return


@app.cell
def _(gammaloop, json, metadata, mo):
    gammaloop_distribution = metadata.distribution("gammaloop")
    symbolica_distribution = metadata.distribution("symbolica")
    gammaloop_source = json.loads(
        gammaloop_distribution.read_text("direct_url.json") or "{}"
    ).get("url", "<unknown>")
    symbolica_source = json.loads(
        symbolica_distribution.read_text("direct_url.json") or "{}"
    ).get("url", "<unknown>")

    mo.md(
        f"""
    | package | version | editable source |
    | --- | --- | --- |
    | `gammaloop` | `{gammaloop_distribution.version}` | `{gammaloop_source}` |
    | `symbolica` | `{symbolica_distribution.version}` | `{symbolica_source}` |

    GammaLoop imported successfully from `{gammaloop.__file__}`.
    """
    )
    return


@app.cell
def _():
    import symbolica
    from symbolica import E,S,Expression,N
    from symbolica.community.spenso import Representation,TensorName as T

    def dot(p,q):
        return S("spenso::dot")(p,q)

    def sq(p):
        return dot(p,p)

    return Expression, Representation, S, T, dot, sq


@app.cell
def _(Representation, S, T):

    minkd = Representation.mink(dimension=S("D")).to_expression()

    def p(i):
        return T("p").to_expression()(i,minkd)
    def k(i):
        return T("k").to_expression()(i,minkd)

    p(1) +p(2)
    return k, p


@app.cell
def _(dot, p):
    a = dot(p(1),p(2)+p(3))
    return


@app.cell
def _(Expression):
    from dataclasses import dataclass
    import math
    def spenso_disp(expr):
        return expr.format(custom_print_mode={"spenso":111},color_builtin_symbols=False)
    @dataclass(slots=True)
    class Integrand:
        numerator: Expression
        denominator: tuple[Expression]

        def to_expr(self):
            return self.numerator/(math.prod(self.denominator))
        def __repr__(self):
            return spenso_disp(self.to_expr())



    return (Integrand,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Cross Box
    """)
    return


@app.cell
def _(k, p, sq):
    p1 = p(1)
    p2 = p(2)
    p12 = p1+p2
    k1  = k(1)


    props = [
        sq(p1),sq(p2),sq(k1-p1),sq(p2-k1),sq(p12-k1),sq(k1)
    ]
    return k1, p12, props


@app.cell
def _(Integrand, dot, k1, p12, props):
    xb = Integrand(
        numerator=dot(k1,p12),
        denominator=tuple(props)
    )
    return (xb,)


@app.cell
def _(Expression, Integrand, S):
    from collections.abc import Sequence


    def partial_fraction_coefficients(
          propagators: Sequence[Expression],
          loop_scalar_products: Sequence[Expression],
    ) -> tuple[Expression, ...]:
          weights = tuple(
              S(f"__pf_{i}") for i in range(len(propagators))
          )

          # Require sum_i weights[i] * propagators[i] == 1.
          relation = sum(
              (weight * propagator
               for weight, propagator in zip(weights, propagators)),
              -1,
          ).expand()

          equations = [
              coefficient
              for _, coefficient in relation.coefficient_list(
                  *loop_scalar_products
              )
          ]

          return tuple(
              Expression.solve_linear_system(equations, weights)
          )


    def partial_fraction(
          integrand: Integrand,
          denominator_indices: Sequence[int],
          loop_scalar_products: Sequence[Expression],
      ) -> tuple[Integrand, ...]:
          indices = tuple(denominator_indices)
          selected = tuple(
              integrand.denominator[i] for i in indices
          )

          coefficients = partial_fraction_coefficients(
              selected,
              loop_scalar_products,
          )

          return tuple(
              Integrand(
                  numerator=(integrand.numerator * coefficient).cancel(),
                  denominator=tuple(
                      denominator
                      for j, denominator in enumerate(integrand.denominator)
                      if j != removed_index
                  ),
              )
              for removed_index, coefficient in zip(indices, coefficients)
          )

    return (partial_fraction,)


@app.cell
def _(dot, k1, p, partial_fraction, sq, xb):
    loop_scalar_products = (
          sq(k1),
          dot(k1, p(1)),
          dot(k1, p(2)),
      )

    xb_partial_fractions = partial_fraction(
          xb,
          denominator_indices=range(2, 6),
          loop_scalar_products=loop_scalar_products,
      )
    return (xb_partial_fractions,)


@app.cell
def _(xb_partial_fractions):
    xb_partial_fractions
    return


@app.cell
def _(Expression, Integrand, S):
    from collections.abc import Sequence as _Sequence


    def numerator_relations(
        propagators: _Sequence[Expression],
        propagator_labels: _Sequence[Expression],
        loop_scalar_products: _Sequence[Expression],
    ) -> tuple[tuple[Expression, Expression], ...]:
        propagators = tuple(propagators)
        propagator_labels = tuple(propagator_labels)
        loop_scalar_products = tuple(loop_scalar_products)

        if len(propagators) != len(propagator_labels):
            raise ValueError(
                "Each propagator needs exactly one formal propagator label"
            )
        if len(propagators) != len(loop_scalar_products):
            raise ValueError(
                "Choose one independent propagator for each loop scalar product"
            )

        weights = tuple(
            S(f"__nr_{i}") for i in range(len(propagators))
        )
        combination = sum(
            (
                weight * propagator
                for weight, propagator in zip(weights, propagators)
            ),
            0,
        ).expand()

        relations = []
        for target_index, target in enumerate(loop_scalar_products):
            equations = [
                combination.coefficient(loop_product)
                - (1 if loop_index == target_index else 0)
                for loop_index, loop_product in enumerate(
                    loop_scalar_products
                )
            ]
            solution = tuple(
                Expression.solve_linear_system(equations, weights)
            )
            if any(
                bool(coefficient.contains(weight))
                for coefficient in solution
                for weight in weights
            ):
                raise ValueError(
                    "Chosen propagators are not an independent basis"
                )

            remainder = (
                sum(
                    (
                        coefficient * propagator
                        for coefficient, propagator in zip(
                            solution, propagators
                        )
                    ),
                    0,
                )
                - target
            ).expand()
            replacement = (
                sum(
                    (
                        coefficient * label
                        for coefficient, label in zip(
                            solution, propagator_labels
                        )
                    ),
                    0,
                )
                - remainder
            ).expand()
            relations.append((target, replacement))

        return tuple(relations)


    def reduce_numerator(
        numerator: Expression,
        relations: _Sequence[tuple[Expression, Expression]],
    ) -> Expression:
        reduced = numerator.expand()
        for loop_product, replacement in relations:
            reduced = reduced.replace(loop_product, replacement)
        return reduced.expand()


    def numerator_reduce(
        integrand: Integrand,
        denominator_indices: _Sequence[int],
        loop_scalar_products: _Sequence[Expression],
    ) -> tuple[
        tuple[Integrand, ...],
        tuple[tuple[Expression, Expression], ...],
        Expression,
    ]:
        indices = tuple(denominator_indices)
        if len(set(indices)) != len(indices):
            raise ValueError("Denominator indices must be unique")

        propagators = tuple(
            integrand.denominator[index] for index in indices
        )
        propagator_labels = tuple(
            S(f"__prop_{index}") for index in indices
        )
        relations = numerator_relations(
            propagators,
            propagator_labels,
            loop_scalar_products,
        )
        reduced = reduce_numerator(integrand.numerator, relations)

        terms = []
        polynomial = reduced.to_polynomial(vars=propagator_labels)
        for powers, coefficient in polynomial.coefficient_list(
            list(propagator_labels)
        ):
            term_numerator = coefficient.to_expression()
            removed_indices = set()

            for index, power in zip(indices, powers):
                if power > 0:
                    removed_indices.add(index)
                    term_numerator *= (
                        integrand.denominator[index] ** (power - 1)
                    )

            terms.append(
                Integrand(
                    numerator=term_numerator,
                    denominator=tuple(
                        denominator
                        for index, denominator in enumerate(
                            integrand.denominator
                        )
                        if index not in removed_indices
                    ),
                )
            )

        return tuple(terms), relations, reduced

    return (numerator_reduce,)


@app.cell
def _(dot, k1, numerator_reduce, p, sq, xb):
    xb_numerator_terms, xb_numerator_relations, xb_reduced_numerator = (
        numerator_reduce(
            xb,
            denominator_indices=(2, 3, 5),
            loop_scalar_products=(
                sq(k1),
                dot(k1, p(1)),
                dot(k1, p(2)),
            ),
        )
    )
    return (
        xb_numerator_relations,
        xb_numerator_terms,
        xb_reduced_numerator,
    )


@app.cell
def _(
    xb_numerator_relations,
    xb_numerator_terms,
    xb_reduced_numerator,
):
    xb_numerator_relations, xb_reduced_numerator, xb_numerator_terms
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DY topology 1 reduction with Kira

    This is the Python replacement for the first FIRE reduction in the
    retained `DY_calculation.nb`. The wrapper accepts the Spenso momentum
    placeholders constructed above directly, serializes a deterministic Kira
    project, and returns exact Symbolica reduction rules.

    The reduction is deliberately gated by a button; opening or exporting the
    notebook never starts Kira on its own.
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
        Propagator,
        ReductionBounds,
        ScalarProductRule,
    )

    return (
        IntegralFamily,
        KinematicInvariant,
        Kinematics,
        Kira,
        Path,
        Propagator,
        ReductionBounds,
        ScalarProductRule,
        product,
    )


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
    k,
    p,
    product,
):
    _m, _ipp1p2 = S("m", "ipp1p2")
    _p1, _p2, _q1 = p(1), p(2), k(1)

    topo1_family = IntegralFamily(
        name="topo1",
        loop_momenta=(_q1,),
        propagators=(
            Propagator(_q1, _m**2),
            Propagator(_q1 - _p1),
            Propagator(_q1 - _p2),
        ),
        top_level_sectors=(7,),
    )
    topo1_kinematics = Kinematics(
        incoming_momenta=(_p1, _p2),
        kinematic_invariants=(
            KinematicInvariant(_m**2, 2, kira_name="m2"),
            KinematicInvariant(_ipp1p2, 2),
        ),
        scalar_products=(
            ScalarProductRule(_p1, _p1, 0),
            ScalarProductRule(_p2, _p2, 0),
            ScalarProductRule(_p1, _p2, _ipp1p2),
        ),
        symbol_to_replace_by_one=_m**2,
    )
    topo1_targets = tuple(
        topo1_family(*_indices)
        for _indices in product((1, 0, -1), repeat=3)
    )
    topo1_bounds = ReductionBounds(sectors=(7,), r=9, s=4, d=2)
    topo1_preferred_masters = tuple(
        topo1_family(*_indices)
        for _indices in ((1, 1, 1), (0, 1, 1), (1, 0, 0))
    )
    topo1_workdir = (
        Path(__file__).resolve().parents[1] / "runs" / "dy-topo1-spenso"
    )
    return (
        topo1_bounds,
        topo1_family,
        topo1_kinematics,
        topo1_preferred_masters,
        topo1_targets,
        topo1_workdir,
    )


@app.cell(hide_code=True)
def _(mo, topo1_bounds, topo1_targets, topo1_workdir):
    mo.md(
        f"""
    Prepared `{len(topo1_targets)}` targets with seed
    `r={topo1_bounds.r}, s={topo1_bounds.s}, d={topo1_bounds.d}`.
    Persistent inputs, logs, and results will live in `{topo1_workdir}`.
    """
    )
    return


@app.cell
def _(mo):
    run_topo1_kira = mo.ui.run_button(label="Run DY topology 1 with Kira")
    run_topo1_kira
    return (run_topo1_kira,)


@app.cell
def _(
    Kira,
    run_topo1_kira,
    topo1_bounds,
    topo1_family,
    topo1_kinematics,
    topo1_preferred_masters,
    topo1_targets,
    topo1_workdir,
):
    if run_topo1_kira.value:
        _kira = Kira()
        topo1_doctor = _kira.doctor()
        topo1_doctor.raise_for_errors()
        topo1_reduction = _kira.reduce(
            family=topo1_family,
            kinematics=topo1_kinematics,
            targets=topo1_targets,
            bounds=topo1_bounds,
            preferred_masters=topo1_preferred_masters,
            check_masters=True,
            workdir=topo1_workdir,
            parallel="physical",
            resume=True,
        )
    else:
        topo1_doctor = None
        topo1_reduction = None
    return topo1_doctor, topo1_reduction


@app.cell(hide_code=True)
def _(mo, topo1_doctor, topo1_reduction):
    if topo1_reduction is None:
        _topo1_status = mo.callout(
            "Ready. No Kira subprocess has been started.",
            kind="neutral",
        )
    else:
        _topo1_status = mo.callout(
            f"Kira `{topo1_doctor.version}` completed all "
            f"{len(topo1_reduction.requested_targets)} targets with "
            f"{len(topo1_reduction.masters)} masters and "
            f"{len(topo1_reduction.zero_integrals)} zeros.",
            kind="success",
        )
    _topo1_status
    return


@app.cell(hide_code=True)
def _(mo, topo1_reduction):
    if topo1_reduction is None:
        _topo1_rules = mo.md("Reduction rules will appear here after the run.")
    else:
        _topo1_rules = mo.ui.table(
            [
                {
                    "target": _target.format_plain(),
                    "reduction": topo1_reduction.rules[_target].format_plain(),
                }
                for _target in topo1_reduction.requested_targets
            ]
        )
    _topo1_rules
    return


if __name__ == "__main__":
    app.run()
