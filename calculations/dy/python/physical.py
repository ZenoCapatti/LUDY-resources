"""Native Symbolica assembly of the leading-power NLO Drell--Yan result.

This module is intentionally independent of the repository-root GammaLoop and
Spenso environments.  The Dirac traces are retained below as exact scalar
polynomials after their independent Spenso reduction.  Everything after that
point--numerator reduction, multivariate partial fractioning, Kira rule
application, master selection, endpoint bookkeeping, and graph assembly--uses
core Symbolica objects from the portable DY application.

The retained Mathematica notebook and the manuscript do not agree in their
last presentation cells.  The data model therefore keeps three different
objects explicit:

* the consistently transverse native result;
* the cached Mathematica-notebook presentation;
* the manuscript formula.

No residual is silently set to zero.
"""

from __future__ import annotations

from dataclasses import dataclass, replace as dataclass_replace
from math import prod
from types import MappingProxyType
from typing import TYPE_CHECKING, Mapping, Sequence

from symbolica import E, S, Expression

if TYPE_CHECKING:
    from kirapy import ReductionResult


PHYSICAL_TOPOLOGY_NAMES = (
    "topo5",
    "topo6",
    "topo7",
    "topo8",
    "topo10",
    "topo11",
    *tuple(f"topo{index}" for index in range(20, 32)),
)


# Scalar products and physical parameters.  The invariant names agree with
# the native aliases restored by kirapy.
d, epsilon = S("d", "epsilon")
kk, kp1, kp2 = S("kk", "kp1", "kp2")
p1_squared, p2_squared, p1_dot_p2 = S("ipp1p1", "ipp2p2", "ipp1p2")
s, z, mass_squared = S("s", "z", "msq")
alpha_s, color_f, color_t = S("alpha_s", "C_F", "T_F")
electric_charge, strong_coupling, color_count = S("e_q", "g_s", "N_c")
lambda1_squared, lambda2_squared, mu_r_squared = S(
    "Lambda1sq", "Lambda2sq", "mu_R_sq"
)
pi = Expression.PI


def normalize_rational(expression: Expression) -> Expression:
    """Return the canonical expanded rational form used by exact checks."""

    return expression.expand().together().cancel()


def replace_all(
    expression: Expression,
    rules: Sequence[tuple[Expression, Expression | int]],
) -> Expression:
    """Apply ordered exact substitutions without manufacturing strings."""

    result = expression
    for source, target in rules:
        result = result.replace(source, target)
    return result


@dataclass(frozen=True, slots=True)
class ReducedIntegralTerm:
    """One coefficient times an integral with explicit denominator powers."""

    coefficient: Expression
    denominators: tuple[Expression, ...]
    integral_indices: tuple[int, ...]

    def as_integrand(self) -> Expression:
        return self.coefficient / prod(
            denominator**index
            for denominator, index in zip(
                self.denominators,
                self.integral_indices,
                strict=True,
            )
        )

    def as_family_integral(self, family_name: str) -> Expression:
        return self.coefficient * S(family_name)(*self.integral_indices)


@dataclass(frozen=True, slots=True)
class NumeratorReduction:
    """A polynomial numerator rewritten in independent denominator coordinates."""

    numerator: Expression
    denominators: tuple[Expression, ...]
    base_integral_indices: tuple[int, ...]
    relations: tuple[tuple[Expression, Expression], ...]
    reduced_numerator: Expression
    terms: tuple[ReducedIntegralTerm, ...]

    def reconstructed_integrand(self) -> Expression:
        return sum((term.as_integrand() for term in self.terms), E("0"))

    def input_integrand(self) -> Expression:
        return self.numerator / prod(
            denominator**index
            for denominator, index in zip(
                self.denominators,
                self.base_integral_indices,
                strict=True,
            )
        )

    def family_expression(self, family_name: str) -> Expression:
        return sum(
            (term.as_family_integral(family_name) for term in self.terms),
            E("0"),
        )

    @property
    def reconstruction_residual(self) -> Expression:
        return normalize_rational(
            self.reconstructed_integrand() - self.input_integrand()
        )


def numerator_relations(
    denominators: Sequence[Expression],
    denominator_labels: Sequence[Expression],
    loop_scalar_products: Sequence[Expression],
) -> tuple[tuple[Expression, Expression], ...]:
    """Invert ``D_i(loop products) = Prop(i)`` for one independent basis."""

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
    if len(branches) != 1:
        raise ValueError("Chosen denominators do not have one independent branch")
    replacements = tuple(
        (loop_product, branches[0][loop_product])
        for loop_product in loop_scalar_products
    )
    if any(
        replacement.contains(candidate)
        for _, replacement in replacements
        for candidate in loop_scalar_products
    ):
        raise ValueError("Chosen denominators are not an independent basis")
    return replacements


def reduce_numerator(
    numerator: Expression,
    denominators: Sequence[Expression],
    *,
    loop_scalar_products: Sequence[Expression] = (kk, kp1, kp2),
    base_integral_indices: Sequence[int] | None = None,
) -> NumeratorReduction:
    """Translate a numerator polynomial into shifted integral indices.

    ``base_integral_indices`` is the propagator-power vector before numerator
    cancellation.  This is usually ``(1,1,1)``, but the physical direct and qg
    boxes contain a repeated middle propagator and therefore use ``(1,2,1)``.
    """

    denominator_tuple = tuple(denominators)
    loop_tuple = tuple(loop_scalar_products)
    if base_integral_indices is None:
        base_tuple = (1,) * len(denominator_tuple)
    else:
        base_tuple = tuple(int(index) for index in base_integral_indices)
    if len(base_tuple) != len(denominator_tuple):
        raise ValueError("One base integral index is required per denominator")
    labels = tuple(S("Prop")(index) for index in range(len(denominator_tuple)))
    relations = numerator_relations(denominator_tuple, labels, loop_tuple)
    reduced = replace_all(numerator.expand(), relations).expand()
    terms = tuple(
        ReducedIntegralTerm(
            coefficient=coefficient.to_expression(),
            denominators=denominator_tuple,
            integral_indices=tuple(
                base - int(power)
                for base, power in zip(base_tuple, powers, strict=True)
            ),
        )
        for powers, coefficient in reduced.to_polynomial(
            vars=list(labels)
        ).coefficient_list(list(labels))
    )
    reduction = NumeratorReduction(
        numerator=numerator,
        denominators=denominator_tuple,
        base_integral_indices=base_tuple,
        relations=relations,
        reduced_numerator=reduced,
        terms=terms,
    )
    if reduction.reconstruction_residual != E("0"):
        raise ValueError("Numerator reduction did not reconstruct its integrand")
    return reduction


@dataclass(frozen=True, slots=True)
class ApartTerm:
    """One native multivariate-apart term with graph-denominator provenance."""

    coefficient: Expression
    retained_indices: tuple[int, ...]
    denominators: tuple[Expression, ...]


def apart_kernel(
    denominators: Sequence[Expression],
    *,
    loop_scalar_products: Sequence[Expression] = (kk, kp1, kp2),
) -> tuple[Expression, tuple[ApartTerm, ...]]:
    """Apply Symbolica's multivariate ``apart`` and recover omitted lines."""

    denominator_tuple = tuple(denominators)
    loops = tuple(loop_scalar_products)
    if len(denominator_tuple) < 2:
        raise ValueError("Multivariate apart needs at least two denominators")
    if not loops or len(set(loops)) != len(loops):
        raise ValueError("Multivariate apart needs unique explicit loop variables")
    kernel = E("1") / prod(denominator_tuple)
    apart_expression = kernel.apart(*loops)
    if normalize_rational(apart_expression - kernel) != E("0"):
        raise ValueError("Symbolica apart did not reconstruct the input kernel")

    grouped: dict[tuple[int, ...], list[Expression]] = {}
    for term_number, term in enumerate(apart_expression.terms(), start=1):
        matches: list[tuple[tuple[int, ...], Expression]] = []
        for omitted in range(len(denominator_tuple)):
            retained = tuple(
                index for index in range(len(denominator_tuple)) if index != omitted
            )
            coefficient = (
                term * prod(denominator_tuple[index] for index in retained)
            ).together().cancel()
            if not any(coefficient.contains(loop) for loop in loops):
                matches.append((retained, coefficient))
        if len(matches) != 1:
            raise ValueError(
                f"Symbolica apart term {term_number} maps to {len(matches)} "
                "graph bases; expected exactly one"
            )
        retained, coefficient = matches[0]
        grouped.setdefault(retained, []).append(coefficient)

    expected = {
        tuple(index for index in range(len(denominator_tuple)) if index != omitted)
        for omitted in range(len(denominator_tuple))
    }
    if set(grouped) != expected:
        raise ValueError("Symbolica apart did not produce every omitted-line basis")
    terms = tuple(
        ApartTerm(
            coefficient=normalize_rational(sum(grouped[retained], E("0"))),
            retained_indices=retained,
            denominators=tuple(denominator_tuple[index] for index in retained),
        )
        for retained in sorted(grouped)
    )
    return apart_expression, terms


def denominator_bases() -> Mapping[str, tuple[Expression, ...]]:
    """Ordered scalar denominator coordinates for every routed numerator."""

    virtual_direct = (
        kk,
        kk - 2 * kp1 + p1_squared,
        kk + 2 * kp2 + p2_squared,
    )
    virtual_crossed = (
        kk,
        kk - 2 * kp1 + p1_squared,
        kk - 2 * kp2 + p2_squared,
    )
    direct_box = (
        kk,
        kk - 2 * kp1 + p1_squared,
        kk
        - 2 * kp1
        - 2 * kp2
        + p1_squared
        + 2 * p1_dot_p2
        + p2_squared
        - mass_squared,
    )
    qg = (
        kk,
        kk + 2 * kp1 + p1_squared,
        kk
        + 2 * kp1
        + 2 * kp2
        + p1_squared
        + 2 * p1_dot_p2
        + p2_squared
        - mass_squared,
    )
    crossed_box = (
        kk,
        kk - 2 * kp1 + p1_squared,
        kk - 2 * kp2 + p2_squared,
        kk
        - 2 * kp1
        - 2 * kp2
        + p1_squared
        + 2 * p1_dot_p2
        + p2_squared
        - mass_squared,
    )
    return MappingProxyType(
        {
            "virtual_direct": virtual_direct,
            "virtual_crossed": virtual_crossed,
            "direct_box": direct_box,
            "qg": qg,
            "crossed_box": crossed_box,
        }
    )


def physical_numerators() -> Mapping[str, Expression]:
    """Metric-contracted transverse numerators, stripped of common weights."""

    triangle_direct = 4 * (d - 2) * (
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
    triangle_crossed = -4 * (d - 2) * (
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
    virtual_bubble = 4 * (d - 2) * (
        -8 * kp2 * p1_dot_p2
        + 2 * d * kp2 * p1_dot_p2
        + 6 * kp1 * p2_squared
        - d * kp1 * p2_squared
    )
    direct_box = 4 * (d - 2) ** 2 * (
        p1_squared * (p1_dot_p2 - 2 * kp2)
        - p1_dot_p2 * kk
        + 2 * kp1 * kp2
    )
    crossed_box = 4 * (d - 2) * (
        (d - 8) * kk * p1_dot_p2
        + 4 * p1_dot_p2 * (kp1 + kp2)
        + (8 - 2 * d) * kp1 * kp2
        + (d - 4) * (kp1 * p2_squared + kp2 * p1_squared)
        + (4 - d) * p1_squared * p2_squared
        - 4 * p1_dot_p2**2
    )
    qg_box = 4 * (d - 2) ** 2 * (
        kk * kp2
        - kp2 * p1_squared
        + 2 * kk * p1_dot_p2
        + 2 * kp1 * p1_dot_p2
    )
    qg_triangle = -4 * (d - 2) * (
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
    qg_bubble = -4 * (d - 2) ** 2 * (
        kp2 * p1_squared
        - 2 * kp1 * p1_dot_p2
        - 2 * kp1 * p2_squared
        - kp2 * p2_squared
    )
    return MappingProxyType(
        {
            "virtual triangle 1": triangle_direct,
            "virtual triangle 2": triangle_crossed,
            "virtual bubble": virtual_bubble,
            "qq direct box": direct_box,
            "qq crossed box": crossed_box,
            "qg box": qg_box,
            "qg triangle": qg_triangle,
            "qg bubble": qg_bubble,
        }
    )


def numerator_reductions() -> Mapping[str, NumeratorReduction]:
    """Build every three-denominator physical numerator handoff."""

    bases = denominator_bases()
    numerators = physical_numerators()
    qg_external = p1_squared + 2 * p1_dot_p2 + p2_squared
    reductions = {
        "virtual triangle 1": reduce_numerator(
            numerators["virtual triangle 1"], bases["virtual_direct"]
        ),
        "virtual triangle 2": reduce_numerator(
            numerators["virtual triangle 2"], bases["virtual_crossed"]
        ),
        "virtual bubble": reduce_numerator(
            numerators["virtual bubble"],
            bases["virtual_direct"],
            base_integral_indices=(1, 0, 1),
        ),
        "qq direct box": reduce_numerator(
            numerators["qq direct box"],
            bases["direct_box"],
            base_integral_indices=(1, 2, 1),
        ),
        "qg box": reduce_numerator(
            numerators["qg box"],
            bases["qg"],
            base_integral_indices=(1, 2, 1),
        ),
        "qg triangle": reduce_numerator(
            numerators["qg triangle"] / qg_external,
            bases["qg"],
        ),
        "qg bubble": reduce_numerator(
            numerators["qg bubble"] / qg_external**2,
            bases["qg"],
            base_integral_indices=(1, 0, 1),
        ),
    }
    return MappingProxyType(reductions)


def qg_ward_reductions() -> Mapping[str, NumeratorReduction]:
    """Reduce the longitudinal qg projector pieces on the double cut.

    These are the exact ``q_mu q_nu`` Dirac traces, including the projector
    factor ``-1/mass_squared`` and the external triangle/bubble propagators.
    Their selected topo10 master coefficients must be identical, so the graph
    combination ``2*triangle - box - bubble`` vanishes before integration.
    """

    q_squared = 2 * p1_dot_p2
    d0 = kk
    d1 = kk + 2 * kp1
    dm = kk + 2 * kp1 + 2 * kp2 + q_squared - mass_squared
    denominators = (d0, d1, dm)
    longitudinal_box = (
        2
        * (d - 2)
        * d1**2
        * (q_squared + d1 - dm - mass_squared)
    )
    longitudinal_triangle = (
        2
        * q_squared
        * (d - 2)
        * d1
        * (q_squared - d0 + d1 - dm - mass_squared)
    )
    longitudinal_bubble = (
        2
        * q_squared
        * (d - 2)
        * (
            -2 * q_squared * d0
            + q_squared * d1
            - q_squared * dm
            - q_squared * mass_squared
            - d0 * d1
            + q_squared**2
            + d0**2
        )
    )
    return MappingProxyType(
        {
            "box": reduce_numerator(
                -longitudinal_box / mass_squared,
                denominators,
                base_integral_indices=(1, 2, 1),
            ),
            "triangle": reduce_numerator(
                -longitudinal_triangle / (mass_squared * q_squared),
                denominators,
            ),
            "bubble": reduce_numerator(
                -longitudinal_bubble / (mass_squared * q_squared**2),
                denominators,
                base_integral_indices=(1, 0, 1),
            ),
        }
    )


def crossed_box_reductions() -> tuple[
    Expression,
    tuple[tuple[ApartTerm, NumeratorReduction], ...],
]:
    """Partial-fraction and numerator-reduce the physical crossed box."""

    denominators = denominator_bases()["crossed_box"]
    numerator = physical_numerators()["qq crossed box"]
    apart_expression, apart_terms = apart_kernel(denominators)
    reductions = tuple(
        (
            term,
            reduce_numerator(
                normalize_rational(numerator * term.coefficient),
                term.denominators,
            ),
        )
        for term in apart_terms
    )
    residual = normalize_rational(
        sum(
            (reduction.reconstructed_integrand() for _, reduction in reductions),
            E("0"),
        )
        - numerator / prod(denominators)
    )
    if residual != E("0"):
        raise ValueError("Crossed-box apart children did not reconstruct the graph")
    return apart_expression, reductions


def _coefficient_of_selected_masters(
    result: "ReductionResult",
    input_expression: Expression,
    selected_masters: Sequence[Expression],
    *,
    substitutions: Sequence[tuple[Expression, Expression | int]] = (),
) -> Expression:
    reduced = result.apply(input_expression)
    selected = set(selected_masters)
    for master in result.masters:
        reduced = reduced.replace(master, 1 if master in selected else 0)
    # Select the master before imposing leading-power kinematics.  Some Kira
    # coefficients contain removable p_i^2/p_i^2 factors; substituting an
    # on-shell value first turns those exact cancellations into an undefined
    # 0/0 object in Symbolica.
    reduced = normalize_rational(reduced)
    reduced = replace_all(reduced, substitutions)
    return normalize_rational(reduced)


def _kinematic_rules(*, p1_on_shell: bool, p2_on_shell: bool):
    rules: list[tuple[Expression, Expression | int]] = []
    if p1_on_shell:
        rules.append((p1_squared, E("0")))
    if p2_on_shell:
        rules.append((p2_squared, E("0")))
    return tuple(rules)


@dataclass(frozen=True, slots=True)
class ReductionAudit:
    """Exact evidence connecting physical numerators to Kira master coefficients."""

    complete_topologies: tuple[str, ...]
    numerator_reconstruction_residuals: Mapping[str, Expression]
    crossed_box_reconstruction_residual: Expression
    virtual_coefficients: Mapping[str, Expression]
    virtual_expected_residuals: Mapping[str, Expression]
    direct_box_coefficients: Mapping[str, Expression]
    direct_box_expected_residuals: Mapping[str, Expression]
    qg_coefficients: Mapping[str, Expression]
    qg_expected_residuals: Mapping[str, Expression]
    qg_ward_coefficients: Mapping[str, Expression]
    qg_ward_expected_residuals: Mapping[str, Expression]
    qg_ward_cancellation_residual: Expression
    crossed_box_coefficients: Mapping[str, Expression]
    crossed_box_expected_residuals: Mapping[str, Expression]

    @property
    def exact(self) -> bool:
        residuals = (
            *self.numerator_reconstruction_residuals.values(),
            self.crossed_box_reconstruction_residual,
            *self.virtual_expected_residuals.values(),
            *self.direct_box_expected_residuals.values(),
            *self.qg_expected_residuals.values(),
            *self.qg_ward_expected_residuals.values(),
            self.qg_ward_cancellation_residual,
            *self.crossed_box_expected_residuals.values(),
        )
        return len(self.complete_topologies) == len(PHYSICAL_TOPOLOGY_NAMES) and all(
            residual == E("0") for residual in residuals
        )


def audit_physical_reductions(
    reductions: Mapping[str, "ReductionResult"],
) -> ReductionAudit:
    """Rebuild key physical IBP coefficients from native Kira rules."""

    missing = [name for name in PHYSICAL_TOPOLOGY_NAMES if name not in reductions]
    if missing:
        raise ValueError("Missing physical Kira reductions: " + ", ".join(missing))
    incomplete = [
        name for name in PHYSICAL_TOPOLOGY_NAMES if not reductions[name].complete
    ]
    if incomplete:
        raise ValueError("Incomplete physical Kira reductions: " + ", ".join(incomplete))

    three_line = numerator_reductions()
    numerator_residuals = {
        name: reduction.reconstruction_residual
        for name, reduction in three_line.items()
    }
    _, crossed_children = crossed_box_reductions()
    crossed_reconstruction = normalize_rational(
        sum(
            (child.reconstructed_integrand() for _, child in crossed_children),
            E("0"),
        )
        - physical_numerators()["qq crossed box"]
        / prod(denominator_bases()["crossed_box"])
    )

    virtual_configs = {
        "topo5": (
            "virtual triangle 1",
            _kinematic_rules(p1_on_shell=True, p2_on_shell=True),
            (0, 1, 1),
        ),
        "topo6": (
            "virtual triangle 1",
            _kinematic_rules(p1_on_shell=True, p2_on_shell=False),
            (1, 0, 1),
        ),
        "topo7": (
            "virtual triangle 1",
            _kinematic_rules(p1_on_shell=False, p2_on_shell=True),
            (1, 1, 0),
        ),
        "topo8": ("virtual triangle 2", (), (1, 1, 1)),
    }
    virtual_coefficients: dict[str, Expression] = {}
    for name, (numerator_name, rules, selected_indices) in virtual_configs.items():
        source = three_line[numerator_name]
        local = reduce_numerator(
            replace_all(source.numerator, rules),
            tuple(replace_all(value, rules) for value in source.denominators),
            base_integral_indices=source.base_integral_indices,
        )
        virtual_coefficients[name] = _coefficient_of_selected_masters(
            reductions[name],
            local.family_expression(name),
            (S(name)(*selected_indices),),
            substitutions=(
                (p1_dot_p2, s / 2),
                (p1_squared, E("0")),
                (p2_squared, E("0")),
            ),
        )
    bubble_source = three_line["virtual bubble"]
    bubble_rules = _kinematic_rules(p1_on_shell=True, p2_on_shell=False)
    bubble_local = reduce_numerator(
        replace_all(bubble_source.numerator, bubble_rules),
        tuple(
            replace_all(value, bubble_rules)
            for value in bubble_source.denominators
        ),
        base_integral_indices=bubble_source.base_integral_indices,
    )
    bubble_with_virtuality = _coefficient_of_selected_masters(
        reductions["topo6"],
        bubble_local.family_expression("topo6"),
        (S("topo6")(1, 0, 1),),
        substitutions=((p1_dot_p2, s / 2),),
    )
    virtual_coefficients["external bubble"] = normalize_rational(
        bubble_with_virtuality / p2_squared
    ).replace(p2_squared, 0)
    virtual_expected = {
        "topo5": 2 * s * (d - 2) * (d**2 - 7 * d + 16) / (d - 4),
        "topo6": -4 * s * (d - 2) ** 2 / (d - 4),
        "topo7": -4 * s * (d - 2) ** 2 / (d - 4),
        "topo8": -4 * s**2 * (d - 2),
        "external bubble": -s * (d - 2) ** 2,
    }
    virtual_residuals = {
        name: normalize_rational(virtual_coefficients[name] - expected)
        for name, expected in virtual_expected.items()
    }

    # Direct box: only the cut-compatible analytic master is retained in each
    # sector.  The other preferred Kira masters are not silently evaluated.
    direct = three_line["qq direct box"]
    direct_coefficients: dict[str, Expression] = {}
    for name, p1_on_shell in (("topo10", True), ("topo11", False)):
        result = reductions[name]
        rules = _kinematic_rules(p1_on_shell=p1_on_shell, p2_on_shell=True)
        numerator = replace_all(direct.numerator, rules)
        denominators = tuple(replace_all(value, rules) for value in direct.denominators)
        local = reduce_numerator(
            numerator,
            denominators,
            base_integral_indices=(1, 2, 1),
        )
        keep = S(name)(1, 0, 1) if name == "topo10" else S(name)(1, 1, 1)
        coefficient = _coefficient_of_selected_masters(
            result,
            local.family_expression(name),
            (keep,),
            substitutions=(
                (p1_dot_p2, s / 2),
                (p1_squared, E("0")),
                (mass_squared, z * s),
                (d, 4 - 2 * epsilon),
            ),
        )
        direct_coefficients[name] = coefficient
    direct_expected = {
        "topo10": -8 * (1 - epsilon) ** 3 / epsilon,
        "topo11": 8 * s * (1 - epsilon) ** 2 * (z - 1 + epsilon),
    }
    direct_residuals = {
        name: normalize_rational(direct_coefficients[name] - expected)
        for name, expected in direct_expected.items()
    }

    qg_coefficients: dict[str, Expression] = {}
    for topology_name, p1_on_shell in (("topo10", True), ("topo11", False)):
        rules = _kinematic_rules(
            p1_on_shell=p1_on_shell,
            p2_on_shell=True,
        )
        for graph_name in ("qg box", "qg triangle", "qg bubble"):
            source = three_line[graph_name]
            local = reduce_numerator(
                replace_all(source.numerator, rules),
                tuple(replace_all(value, rules) for value in source.denominators),
                base_integral_indices=source.base_integral_indices,
            )
            keep = (
                S(topology_name)(1, 0, 1)
                if topology_name == "topo10"
                else S(topology_name)(1, 1, 1)
            )
            coefficient = _coefficient_of_selected_masters(
                reductions[topology_name],
                local.family_expression(topology_name),
                (keep,),
                substitutions=(
                    (p1_dot_p2, s / 2),
                    (mass_squared, z * s),
                    (d, 4 - 2 * epsilon),
                ),
            )
            if topology_name == "topo11":
                coefficient = normalize_rational(coefficient).series(
                    p1_squared,
                    0,
                    0,
                ).to_expression()
            key = f"{topology_name} {graph_name.removeprefix('qg ')}"
            qg_coefficients[key] = normalize_rational(coefficient)
    qg_expected = {
        "topo10 box": 8
        * (1 - 2 * epsilon)
        * (1 - epsilon) ** 2
        / (epsilon * (1 - z)),
        "topo10 triangle": 8
        * (1 - epsilon)
        * (epsilon**2 + z * (1 - epsilon))
        / epsilon,
        "topo10 bubble": -4 * (1 - epsilon) ** 2 * (1 - z),
        "topo11 box": 8 * s * (1 - epsilon) ** 3,
        "topo11 triangle": 8
        * s
        * z
        * (1 - epsilon)
        * (1 - z),
        "topo11 bubble": E("0"),
    }
    qg_residuals = {
        name: normalize_rational(qg_coefficients[name] - expected)
        for name, expected in qg_expected.items()
    }

    ward_coefficients: dict[str, Expression] = {}
    for graph_name, ward_reduction in qg_ward_reductions().items():
        ward_coefficients[graph_name] = _coefficient_of_selected_masters(
            reductions["topo10"],
            ward_reduction.family_expression("topo10"),
            (S("topo10")(1, 0, 1),),
        )
    ward_expected = (
        (d - 2)
        * (mass_squared - 2 * p1_dot_p2)
        / mass_squared
    )
    ward_residuals = {
        name: normalize_rational(coefficient - ward_expected)
        for name, coefficient in ward_coefficients.items()
    }
    ward_cancellation = normalize_rational(
        2 * ward_coefficients["triangle"]
        - ward_coefficients["box"]
        - ward_coefficients["bubble"]
    )

    # Crossed box: map every apart child back to the historical family order.
    # Families ending in 2 or 3 order the last two retained propagators as
    # (D3,D2), while the native apart child is sorted as (D2,D3).
    retained_to_offset = {
        (0, 1, 3): 0,
        (0, 1, 2): 1,
        (0, 2, 3): 2,
        (1, 2, 3): 3,
    }
    cut_blocks = {
        "11": (20, True, True),
        "10": (24, True, False),
        "01": (28, False, True),
    }
    selected_by_cut = {
        "11": {"topo20": (1, 0, 1), "topo22": (1, 1, 0)},
        "10": {"topo26": (1, 1, 1)},
        "01": {"topo28": (1, 1, 1)},
    }
    crossed_coefficients: dict[str, Expression] = {}
    for cut_name, (first_topology, p1_on_shell, p2_on_shell) in cut_blocks.items():
        sector_sum = E("0")
        rules = _kinematic_rules(
            p1_on_shell=p1_on_shell,
            p2_on_shell=p2_on_shell,
        )
        for apart_term, child in crossed_children:
            offset = retained_to_offset[apart_term.retained_indices]
            name = f"topo{first_topology + offset}"
            result = reductions[name]
            numerator = replace_all(child.numerator, rules)
            denominators = tuple(
                replace_all(value, rules) for value in child.denominators
            )
            local = reduce_numerator(numerator, denominators)
            local_expression = local.family_expression(name)
            if offset in (2, 3):
                # Reorder I(a0,a2,a3) -> I(a0,a3,a2), or its D1 analogue.
                local_expression = sum(
                    (
                        term.coefficient
                        * S(name)(
                            term.integral_indices[0],
                            term.integral_indices[2],
                            term.integral_indices[1],
                        )
                        for term in local.terms
                    ),
                    E("0"),
                )
            selected_indices = selected_by_cut[cut_name].get(name)
            selected = (
                (S(name)(*selected_indices),)
                if selected_indices is not None
                else ()
            )
            sector_sum += _coefficient_of_selected_masters(
                result,
                local_expression,
                selected,
                substitutions=(
                    (p1_dot_p2, s / 2),
                    (p1_squared, E("0")),
                    (p2_squared, E("0")),
                    (mass_squared, z * s),
                    (d, 4 - 2 * epsilon),
                ),
            )
        crossed_coefficients[cut_name] = normalize_rational(sector_sum)
    crossed_expected = {
        "11": 8
        * (1 - epsilon)
        * (
            epsilon**2 * (1 - z) ** 2
            + 2 * z * (1 - 2 * epsilon)
        )
        / (epsilon * (1 - z) ** 2),
        "10": 8 * s * z * (1 - epsilon) / (1 - z),
        "01": 8 * s * z * (1 - epsilon) / (1 - z),
        # The fourth cut contains all four graph propagators, so it is the
        # analytic maximal-cut numerator rather than a three-line Kira family.
        "00": -8 * s**2 * (1 - epsilon),
    }
    crossed_coefficients["00"] = replace_all(
        physical_numerators()["qq crossed box"],
        (
            (kk, E("0")),
            (kp1, E("0")),
            (kp2, E("0")),
            (p1_squared, E("0")),
            (p2_squared, E("0")),
            (p1_dot_p2, s / 2),
            (d, 4 - 2 * epsilon),
        ),
    ).expand()
    crossed_residuals = {
        name: normalize_rational(crossed_coefficients[name] - expected)
        for name, expected in crossed_expected.items()
    }
    return ReductionAudit(
        complete_topologies=tuple(
            name for name in PHYSICAL_TOPOLOGY_NAMES if reductions[name].complete
        ),
        numerator_reconstruction_residuals=MappingProxyType(numerator_residuals),
        crossed_box_reconstruction_residual=crossed_reconstruction,
        virtual_coefficients=MappingProxyType(virtual_coefficients),
        virtual_expected_residuals=MappingProxyType(virtual_residuals),
        direct_box_coefficients=MappingProxyType(direct_coefficients),
        direct_box_expected_residuals=MappingProxyType(direct_residuals),
        qg_coefficients=MappingProxyType(qg_coefficients),
        qg_expected_residuals=MappingProxyType(qg_residuals),
        qg_ward_coefficients=MappingProxyType(ward_coefficients),
        qg_ward_expected_residuals=MappingProxyType(ward_residuals),
        qg_ward_cancellation_residual=ward_cancellation,
        crossed_box_coefficients=MappingProxyType(crossed_coefficients),
        crossed_box_expected_residuals=MappingProxyType(crossed_residuals),
    )


@dataclass(frozen=True, slots=True)
class EndpointCoefficient:
    """Coefficient in the explicit ``delta, D0, D1, regular`` basis.

    ``d0_prefactor`` and ``d1_prefactor`` may depend smoothly on ``z``.  The
    :meth:`canonical` method moves that dependence into the ordinary remainder
    and leaves endpoint constants multiplying the plus distributions.
    """

    delta: Expression = E("0")
    d0_prefactor: Expression = E("0")
    d1_prefactor: Expression = E("0")
    regular: Expression = E("0")

    def __add__(self, other: "EndpointCoefficient") -> "EndpointCoefficient":
        if not isinstance(other, EndpointCoefficient):
            return NotImplemented
        return EndpointCoefficient(
            delta=(self.delta + other.delta).expand(),
            d0_prefactor=(self.d0_prefactor + other.d0_prefactor).expand(),
            d1_prefactor=(self.d1_prefactor + other.d1_prefactor).expand(),
            regular=(self.regular + other.regular).expand(),
        )

    def __neg__(self) -> "EndpointCoefficient":
        return self.scaled(E("-1"))

    def __sub__(self, other: "EndpointCoefficient") -> "EndpointCoefficient":
        return self + (-other)

    def scaled(self, factor: Expression | int) -> "EndpointCoefficient":
        return EndpointCoefficient(
            delta=(factor * self.delta).expand(),
            d0_prefactor=(factor * self.d0_prefactor).expand(),
            d1_prefactor=(factor * self.d1_prefactor).expand(),
            regular=(factor * self.regular).expand(),
        )

    def canonical(self, variable: Expression = z) -> "EndpointCoefficient":
        d0_endpoint = self.d0_prefactor.replace(variable, 1)
        d1_endpoint = self.d1_prefactor.replace(variable, 1)
        remainder = (
            self.regular
            + (self.d0_prefactor - d0_endpoint) / (1 - variable)
            + (self.d1_prefactor - d1_endpoint)
            * (1 - variable).log()
            / (1 - variable)
        ).expand().together().cancel()
        return EndpointCoefficient(
            delta=self.delta,
            d0_prefactor=d0_endpoint,
            d1_prefactor=d1_endpoint,
            regular=remainder,
        )

    def residuals(self) -> tuple[Expression, Expression, Expression, Expression]:
        return tuple(
            normalize_rational(value)
            for value in (
                self.delta,
                self.d0_prefactor,
                self.d1_prefactor,
                self.regular,
            )
        )

    @property
    def is_zero(self) -> bool:
        canonical = self.canonical()
        return all(value == E("0") for value in canonical.residuals())


@dataclass(frozen=True, slots=True)
class ChannelAssembly:
    """Named graph pieces and their exact endpoint-basis sum."""

    pieces: Mapping[str, EndpointCoefficient]
    total: EndpointCoefficient


@dataclass(frozen=True, slots=True)
class MasterInsertion:
    """One audited IBP coefficient inserted into one analytic master."""

    channel: str
    sector: str
    topologies: tuple[str, ...]
    ibp_coefficient: Expression
    analytic_master: Expression
    virtuality_factor: Expression = E("1")
    relative_weight: Expression = E("1")

    @property
    def value(self) -> Expression:
        """Return the contribution before its channel-wide graph factor."""

        return (
            self.relative_weight
            * self.ibp_coefficient
            * self.analytic_master
            * self.virtuality_factor
        ).expand()


@dataclass(frozen=True, slots=True)
class AnalyticMasterHandoff:
    """Explicit Kira-to-master ledger used by the physical assembly.

    The direct qqbar and qg channels are independently Laurent-expanded from
    these expressions and checked against their finite graph ledgers.  The
    distribution-valued crossed box is expanded cut by cut, including its
    analytic ``00`` master; both pole cancellation and its complete finite
    delta/plus coefficient are checked exactly.
    """

    insertions: Mapping[str, MasterInsertion]
    normalization_factors: Mapping[str, Expression]
    direct_normalized_raw: Expression
    direct_finite: Expression
    direct_finite_residual: Expression
    qg_normalized_raw: Expression
    qg_finite: Expression
    qg_finite_residual: Expression
    crossed_cut_endpoint: Mapping[str, EndpointCoefficient]
    crossed_pole_residuals: Mapping[int, EndpointCoefficient]
    crossed_finite: EndpointCoefficient
    crossed_finite_residual: EndpointCoefficient

    @property
    def finite_checks_exact(self) -> bool:
        return (
            bool(self.direct_finite_residual == E("0"))
            and bool(self.qg_finite_residual == E("0"))
            and all(
                residual.is_zero
                for residual in self.crossed_pole_residuals.values()
            )
            and self.crossed_finite_residual.is_zero
        )


@dataclass(frozen=True, slots=True)
class FullDYCoefficient:
    """All NLO DY channels plus explicit source-comparison residuals."""

    ordinary_virtual: EndpointCoefficient
    local_all_cut_virtual: EndpointCoefficient
    qq_transverse: ChannelAssembly
    qq_cached_notebook: EndpointCoefficient
    qq_manuscript: EndpointCoefficient
    qq_transverse_minus_notebook: EndpointCoefficient
    qq_transverse_minus_manuscript: EndpointCoefficient
    qq_notebook_minus_manuscript: EndpointCoefficient
    qg_transverse: ChannelAssembly
    qg_cached_notebook: EndpointCoefficient
    qg_manuscript: EndpointCoefficient
    qg_transverse_minus_manuscript: EndpointCoefficient
    master_handoff: AnalyticMasterHandoff | None = None

    @property
    def physical_target_channels(self) -> Mapping[str, EndpointCoefficient]:
        """Return the manuscript coefficient functions as the physical target.

        The exact native-transverse reconstruction remains separate because
        its qqbar soft sign and regular terms do not agree with the manuscript,
        while the cached qg result retains an uncancelled Ward remainder.
        """

        return MappingProxyType(
            {
                "qqbar": self.qq_manuscript,
                "qg": self.qg_manuscript,
            }
        )

    @property
    def native_transverse_channels(self) -> Mapping[str, EndpointCoefficient]:
        """Return the consistently metric/transverse provenance result."""

        return MappingProxyType(
            {
                "qqbar": self.qq_transverse.total,
                "qg": self.qg_transverse.total,
            }
        )


def _positive_branch_log_rules() -> tuple[tuple[Expression, Expression], ...]:
    """Logarithm identities for the stated positive DY kinematic region."""

    gamma_e = Expression.EULER_GAMMA
    log_two = E("log(2)")
    return (
        (
            (gamma_e.exp() * mu_r_squared).log(),
            gamma_e + mu_r_squared.log(),
        ),
        (
            (s * z * (s - s * z)).log(),
            2 * s.log() + z.log() + (1 - z).log(),
        ),
        (
            (s**2 * z - s**2 * z**2).log(),
            2 * s.log() + z.log() + (1 - z).log(),
        ),
        (
            ((s - s * z) / (2 * s.sqrt())).log(),
            -log_two + s.log() / 2 + (1 - z).log(),
        ),
        (
            (s.sqrt() / 2 - s.sqrt() * z / 2).log(),
            -log_two + s.log() / 2 + (1 - z).log(),
        ),
        (
            (
                lambda1_squared
                * lambda2_squared
                * z**2
                / (s**2 * (1 - z) ** 2)
            ).log(),
            lambda1_squared.log()
            + lambda2_squared.log()
            + 2 * z.log()
            - 2 * s.log()
            - 2 * (1 - z).log(),
        ),
        (
            (
                lambda1_squared
                * lambda2_squared
                * z**2
                / s**2
            ).log(),
            lambda1_squared.log()
            + lambda2_squared.log()
            + 2 * z.log()
            - 2 * s.log(),
        ),
        (
            (lambda1_squared / s).log(),
            lambda1_squared.log() - s.log(),
        ),
        (
            (lambda2_squared / s).log(),
            lambda2_squared.log() - s.log(),
        ),
        (
            E("symbolica::polygamma(1,2)"),
            pi**2 / 6 - 1,
        ),
    )


def _expand_positive_branch_logs(expression: Expression) -> Expression:
    """Apply positive-region log identities to a stable rational fixed point."""

    result = expression
    for _ in range(3):
        result = replace_all(result, _positive_branch_log_rules())
        result = normalize_rational(result)
    return result


def _finite_laurent_coefficient(expression: Expression) -> Expression:
    """Extract the exact epsilon^0 coefficient and expand its DY logarithms."""

    finite = expression.series(epsilon, 0, 0).get_coefficient(0)
    return _expand_positive_branch_logs(finite)


def _endpoint_laurent_coefficient(
    coefficient: EndpointCoefficient,
    power: int,
) -> EndpointCoefficient:
    """Extract one Laurent power from every endpoint-basis component."""

    def extract(expression: Expression) -> Expression:
        value = expression.series(epsilon, 0, 0).get_coefficient(power)
        return _expand_positive_branch_logs(value)

    return EndpointCoefficient(
        delta=extract(coefficient.delta),
        d0_prefactor=extract(coefficient.d0_prefactor),
        d1_prefactor=extract(coefficient.d1_prefactor),
        regular=extract(coefficient.regular),
    )


def build_analytic_master_handoff(
    audit: ReductionAudit,
    coefficient: FullDYCoefficient,
) -> AnalyticMasterHandoff:
    """Insert the audited coefficients into the application-local masters."""

    from masters import (
        apply_endpoint_expansion,
        endpoint_distribution_expansion,
        massive_cut_bubble,
        massive_cut_triangle,
        massless_cut_bubble,
        massless_cut_triangle,
        maximal_cross_box_cut_master,
        uncut_bubble,
        virtuality_integral_factor,
    )

    dimension = 4 - 2 * epsilon
    gamma_e = Expression.EULER_GAMMA
    master_arguments = {
        "dimension": dimension,
        "epsilon": epsilon,
        "mu_squared": mu_r_squared,
        "euler_gamma": gamma_e,
    }
    massive_bubble = massive_cut_bubble(
        s,
        z * s,
        **master_arguments,
    )
    # Setting the external virtuality to one strips precisely its
    # (p_i^2)^(-epsilon) leading-power factor.  The physical integral is then
    # supplied by J_i below.
    massive_triangle_stripped = massive_cut_triangle(
        E("1"),
        s,
        z * s,
        **master_arguments,
    )
    massless_bubble_stripped = massless_cut_bubble(
        E("1"),
        **master_arguments,
    )
    massless_triangle_stripped = massless_cut_triangle(
        E("1"),
        E("1"),
        -s,
        **master_arguments,
    )
    ordinary_bubble = uncut_bubble(s, **master_arguments)
    maximal_crossed = maximal_cross_box_cut_master(
        s,
        **master_arguments,
    )
    j1 = virtuality_integral_factor(lambda1_squared, epsilon)
    j2 = virtuality_integral_factor(lambda2_squared, epsilon)

    def insertion(
        channel: str,
        sector: str,
        topologies: tuple[str, ...],
        ibp_coefficient: Expression,
        analytic_master: Expression,
        *,
        virtuality_factor: Expression = E("1"),
        relative_weight: Expression = E("1"),
    ) -> MasterInsertion:
        return MasterInsertion(
            channel=channel,
            sector=sector,
            topologies=topologies,
            ibp_coefficient=ibp_coefficient,
            analytic_master=analytic_master,
            virtuality_factor=virtuality_factor,
            relative_weight=relative_weight,
        )

    insertions = {
        "virtual 0-cut": insertion(
            "virtual",
            "0-cut triangle",
            ("topo5",),
            audit.virtual_coefficients["topo5"],
            ordinary_bubble,
        ),
        "virtual p2-cut": insertion(
            "virtual",
            "p2-cut triangle",
            ("topo6",),
            audit.virtual_coefficients["topo6"],
            massless_bubble_stripped,
            virtuality_factor=j2,
            relative_weight=E("-1"),
        ),
        "virtual p1-cut": insertion(
            "virtual",
            "p1-cut triangle",
            ("topo7",),
            audit.virtual_coefficients["topo7"],
            massless_bubble_stripped,
            virtuality_factor=j1,
            relative_weight=E("-1"),
        ),
        "virtual double-cut": insertion(
            "virtual",
            "double-cut triangle",
            ("topo8",),
            audit.virtual_coefficients["topo8"],
            massless_triangle_stripped,
            virtuality_factor=j1 * j2,
        ),
        "external bubble p1": insertion(
            "virtual",
            "external bubble p1",
            ("topo6",),
            audit.virtual_coefficients["external bubble"],
            massless_bubble_stripped,
            virtuality_factor=j1,
            relative_weight=E("-1/2"),
        ),
        "external bubble p2": insertion(
            "virtual",
            "external bubble p2",
            ("topo6",),
            audit.virtual_coefficients["external bubble"],
            massless_bubble_stripped,
            virtuality_factor=j2,
            relative_weight=E("-1/2"),
        ),
        "direct 00": insertion(
            "direct qqbar",
            "00",
            ("topo10",),
            audit.direct_box_coefficients["topo10"],
            massive_bubble,
        ),
        "direct 10": insertion(
            "direct qqbar",
            "10",
            ("topo11",),
            audit.direct_box_coefficients["topo11"],
            massive_triangle_stripped,
            virtuality_factor=j1,
            relative_weight=E("-1/2"),
        ),
        "direct 01": insertion(
            "direct qqbar",
            "01",
            ("topo11",),
            audit.direct_box_coefficients["topo11"],
            massive_triangle_stripped,
            virtuality_factor=j2,
            relative_weight=E("-1/2"),
        ),
        "crossed 11": insertion(
            "crossed qqbar",
            "11",
            ("topo20", "topo21", "topo22", "topo23"),
            audit.crossed_box_coefficients["11"],
            massive_bubble,
            relative_weight=E("-1"),
        ),
        "crossed 10": insertion(
            "crossed qqbar",
            "10",
            ("topo24", "topo25", "topo26", "topo27"),
            audit.crossed_box_coefficients["10"],
            massive_triangle_stripped,
            virtuality_factor=j2,
        ),
        "crossed 01": insertion(
            "crossed qqbar",
            "01",
            ("topo28", "topo29", "topo30", "topo31"),
            audit.crossed_box_coefficients["01"],
            massive_triangle_stripped,
            virtuality_factor=j1,
        ),
        # In the retained z-space source the 00 object is negated once when it
        # is defined and again in the four-cut sum.  Its numerator coefficient
        # already carries the remaining minus sign; encoding that sequence as
        # relative_weight=+1 makes the convention visible.
        "crossed 00": insertion(
            "crossed qqbar",
            "00",
            (),
            audit.crossed_box_coefficients["00"],
            maximal_crossed,
            virtuality_factor=j1 * j2,
        ),
        "qg box 00": insertion(
            "qg",
            "box 00",
            ("topo10",),
            audit.qg_coefficients["topo10 box"],
            massive_bubble,
            relative_weight=E("-1"),
        ),
        "qg box 10": insertion(
            "qg",
            "box 10",
            ("topo11",),
            audit.qg_coefficients["topo11 box"],
            massive_triangle_stripped,
            virtuality_factor=j1,
            relative_weight=E("1/2"),
        ),
        "qg box 01": insertion(
            "qg",
            "box 01",
            ("topo11",),
            audit.qg_coefficients["topo11 box"],
            massive_triangle_stripped,
            virtuality_factor=j2,
            relative_weight=E("1/2"),
        ),
        "qg triangle 00": insertion(
            "qg",
            "triangle 00",
            ("topo10",),
            audit.qg_coefficients["topo10 triangle"],
            massive_bubble,
            relative_weight=E("2"),
        ),
        "qg triangle 10": insertion(
            "qg",
            "triangle 10",
            ("topo11",),
            audit.qg_coefficients["topo11 triangle"],
            massive_triangle_stripped,
            virtuality_factor=j1,
            relative_weight=E("-1"),
        ),
        "qg triangle 01": insertion(
            "qg",
            "triangle 01",
            ("topo11",),
            audit.qg_coefficients["topo11 triangle"],
            massive_triangle_stripped,
            virtuality_factor=j2,
            relative_weight=E("-1"),
        ),
        "qg bubble 00": insertion(
            "qg",
            "bubble 00",
            ("topo10",),
            audit.qg_coefficients["topo10 bubble"],
            massive_bubble,
            relative_weight=E("-1"),
        ),
    }
    insertion_map = MappingProxyType(insertions)

    qq_common = (
        electric_charge**2
        * strong_coupling**2
        * color_t
        * (color_count**2 - 1)
    )
    qg_common = electric_charge**2 * strong_coupling**2 * color_t
    qq_normalization = (
        1
        / (
            2
            * color_count
            * 2
            * pi
            * electric_charge**2
            * (1 - epsilon)
        )
    )
    qg_normalization = 1 / (
        8 * pi * (1 - epsilon) * electric_charge**2
    )
    virtual_normalization = 1 / (
        4
        * color_count
        * s
        * electric_charge**2
        * (1 - epsilon)
    )
    normalization_factors = MappingProxyType(
        {
            "qqbar common graph factor": qq_common,
            "qqbar Born normalization": qq_normalization,
            "qg common graph factor": qg_common,
            "qg Born normalization": qg_normalization,
            "local all-cut virtual normalization": virtual_normalization,
        }
    )

    direct_raw = qq_common * sum(
        (
            item.value
            for item in insertion_map.values()
            if item.channel == "direct qqbar"
        ),
        E("0"),
    )
    direct_normalized = replace_all(
        qq_normalization * direct_raw,
        (
            (strong_coupling**2, 4 * pi * alpha_s),
            (color_t, E("1/2")),
        ),
    )
    direct_finite = _finite_laurent_coefficient(direct_normalized)
    direct_expected = _expand_positive_branch_logs(
        coefficient.qq_transverse.pieces[
            "direct box plus mirror"
        ].canonical().regular.replace(
            color_f,
            (color_count**2 - 1) / (2 * color_count),
        )
    )
    direct_residual = normalize_rational(direct_finite - direct_expected)

    qg_raw = qg_common * sum(
        (
            item.value
            for item in insertion_map.values()
            if item.channel == "qg"
        ),
        E("0"),
    )
    qg_normalized = replace_all(
        qg_normalization * qg_raw,
        ((strong_coupling**2, 4 * pi * alpha_s),),
    )
    qg_finite = _finite_laurent_coefficient(qg_normalized)
    qg_expected = _expand_positive_branch_logs(
        coefficient.qg_transverse.total.regular
    )
    qg_residual = normalize_rational(qg_finite - qg_expected)

    # Expand the four crossed-box cuts as endpoint distributions.  These
    # smooth prefactors are written directly in terms of the audited IBP
    # coefficients and the compact positive-branch forms of the same masters
    # recorded in ``insertions`` above.  In particular, the 11 prefactor uses
    # Gamma duplication to remove Gamma(3/2-epsilon), and the 00 term is the
    # analytic four-line master rather than a fictitious Kira family.
    endpoint_variable = 1 - z
    dimensional_scale = (
        mu_r_squared * gamma_e.exp()
    ) ** epsilon
    normalized_qq_graph = (
        alpha_s
        * (color_count**2 - 1)
        / (2 * color_count * (1 - epsilon))
    )
    gamma_one_minus_epsilon = (1 - epsilon).gamma()
    crossed_smooth_prefactors = {
        "11": normalize_rational(
            normalized_qq_graph
            * audit.crossed_box_coefficients["11"]
            * dimensional_scale
            * s ** (-epsilon)
            * gamma_one_minus_epsilon
            / (8 * pi * (2 - 2 * epsilon).gamma())
            * endpoint_variable**2,
        ),
        "10": normalize_rational(
            normalized_qq_graph
            * audit.crossed_box_coefficients["10"]
            * dimensional_scale
            * z ** (-epsilon)
            / (4 * gamma_one_minus_epsilon * s)
            * j2
            * endpoint_variable,
        ),
        "01": normalize_rational(
            normalized_qq_graph
            * audit.crossed_box_coefficients["01"]
            * dimensional_scale
            * z ** (-epsilon)
            / (4 * gamma_one_minus_epsilon * s)
            * j1
            * endpoint_variable,
        ),
    }

    def endpoint_from_smooth_prefactor(
        prefactor: Expression,
        exponent_multiple: int,
    ) -> EndpointCoefficient:
        distribution = apply_endpoint_expansion(
            endpoint_distribution_expansion(
                exponent_multiple,
                epsilon,
                order=1,
            ),
            prefactor,
            z,
        )
        return EndpointCoefficient(
            delta=distribution.delta_coefficient,
            d0_prefactor=distribution.plus_coefficients[0],
            d1_prefactor=distribution.plus_coefficients[1],
            regular=distribution.regular_part,
        )

    crossed_cut_endpoint = {
        "11": endpoint_from_smooth_prefactor(
            crossed_smooth_prefactors["11"],
            2,
        ),
        "10": endpoint_from_smooth_prefactor(
            crossed_smooth_prefactors["10"],
            1,
        ),
        "01": endpoint_from_smooth_prefactor(
            crossed_smooth_prefactors["01"],
            1,
        ),
        "00": EndpointCoefficient(
            delta=normalize_rational(
                normalized_qq_graph
                * audit.crossed_box_coefficients["00"]
                * dimensional_scale
                * pi
                * s ** (-2 + epsilon)
                / (2 * gamma_one_minus_epsilon)
                * j1
                * j2,
            )
        ),
    }
    crossed_endpoint_sum = sum(
        crossed_cut_endpoint.values(),
        EndpointCoefficient(),
    )
    crossed_poles = MappingProxyType(
        {
            power: _endpoint_laurent_coefficient(
                crossed_endpoint_sum,
                power,
            )
            for power in (-2, -1)
        }
    )
    crossed_finite = _endpoint_laurent_coefficient(
        crossed_endpoint_sum,
        0,
    )
    crossed_target = coefficient.qq_transverse.pieces[
        "crossed box, all four cuts"
    ]
    color_f_in_nc = (color_count**2 - 1) / (2 * color_count)
    crossed_expected = _endpoint_laurent_coefficient(
        dataclass_replace(
            crossed_target,
            delta=crossed_target.delta.replace(color_f, color_f_in_nc),
            d0_prefactor=crossed_target.d0_prefactor.replace(
                color_f,
                color_f_in_nc,
            ),
            d1_prefactor=crossed_target.d1_prefactor.replace(
                color_f,
                color_f_in_nc,
            ),
            regular=crossed_target.regular.replace(color_f, color_f_in_nc),
        ),
        0,
    )
    crossed_finite_residual = crossed_finite - crossed_expected
    return AnalyticMasterHandoff(
        insertions=insertion_map,
        normalization_factors=normalization_factors,
        direct_normalized_raw=direct_normalized,
        direct_finite=direct_finite,
        direct_finite_residual=direct_residual,
        qg_normalized_raw=qg_normalized,
        qg_finite=qg_finite,
        qg_finite_residual=qg_residual,
        crossed_cut_endpoint=MappingProxyType(crossed_cut_endpoint),
        crossed_pole_residuals=crossed_poles,
        crossed_finite=crossed_finite,
        crossed_finite_residual=crossed_finite_residual,
    )


def assemble_closed_form_dy() -> FullDYCoefficient:
    """Encode the retained finite channels and separate virtual diagnostics."""

    qq_normalization = alpha_s * color_f / (2 * pi)
    cutoff_log = (
        lambda1_squared * lambda2_squared * z**2 / s**2
    ).log()
    cutoff_log_at_endpoint = (
        lambda1_squared * lambda2_squared / s**2
    ).log()
    mu_log = (mu_r_squared / s).log()
    ordinary_virtual = EndpointCoefficient(
        delta=qq_normalization
        * (
            -2 / epsilon**2
            - (3 + 2 * mu_log) / epsilon
            - 8
            + 7 * pi**2 / 6
            - 3 * mu_log
            - mu_log**2
        )
    )
    x1 = (lambda1_squared / mu_r_squared).log()
    x2 = (lambda2_squared / mu_r_squared).log()
    local_all_cut_virtual = EndpointCoefficient(
        delta=2
        * alpha_s
        * color_f
        / pi
        * (
            Expression.I * pi / epsilon
            - E("1/4")
            + 5 * pi**2 / 6
            - 3 * mu_log / 4
            - mu_log**2 / 2
            - 3 * (x1 + x2) / 8
            - mu_log * (x1 + x2) / 2
            - x1 * x2 / 2
            + Expression.I * pi * (E("3/2") + mu_log)
        )
    )
    # Source convention:
    # Pqq(z,0) = 3/2 delta(1-z) + (1+z^2) D0(z)
    #           = 3/2 delta(1-z) + 2 z D0(z) + (1-z).
    pqq_times_cutoff_log = EndpointCoefficient(
        delta=qq_normalization * E("3/2") * cutoff_log_at_endpoint,
        d0_prefactor=qq_normalization * (1 + z**2) * cutoff_log,
    )
    transverse_total = pqq_times_cutoff_log + EndpointCoefficient(
        delta=qq_normalization * (1 - 3 * pi**2),
        d1_prefactor=-2 * qq_normalization * (1 + z**2),
        regular=qq_normalization * (4 - 2 * z),
    )
    # This explicit plus-basis representation is distribution-equal to
    # A[(1-z) log(Lambda1^2 Lambda2^2 z^2/(s^2(1-z)^2)) + 4 - 2z].
    direct_box = EndpointCoefficient(
        d0_prefactor=qq_normalization * (1 - z) ** 2 * cutoff_log,
        d1_prefactor=-2 * qq_normalization * (1 - z) ** 2,
        regular=qq_normalization * (4 - 2 * z),
    )
    ell1 = (lambda1_squared / s).log()
    ell2 = (lambda2_squared / s).log()
    crossed_box = EndpointCoefficient(
        delta=qq_normalization * (pi**2 / 3 - 2 * ell1 * ell2),
        d0_prefactor=qq_normalization * 2 * z * cutoff_log,
        d1_prefactor=-4 * qq_normalization * z,
    )
    virtual_and_all_cuts = EndpointCoefficient(
        delta=qq_normalization
        * (
            1
            - 10 * pi**2 / 3
            + 2 * ell1 * ell2
            + E("3/2") * cutoff_log_at_endpoint
        )
    )
    qq_transverse_pieces = MappingProxyType(
        {
            "physical virtual = -Re(local all-cut)": virtual_and_all_cuts,
            "direct box plus mirror": direct_box,
            "crossed box, all four cuts": crossed_box,
        }
    )
    qq_transverse = ChannelAssembly(
        pieces=qq_transverse_pieces,
        total=sum(qq_transverse_pieces.values(), EndpointCoefficient()),
    )
    if not (qq_transverse.total - transverse_total).is_zero:
        raise ValueError("Transverse qqbar graph ledger did not reconstruct its sum")
    notebook_total = pqq_times_cutoff_log + EndpointCoefficient(
        delta=qq_normalization * (1 - 3 * pi**2),
        d1_prefactor=-2 * qq_normalization * (1 + z**2),
        regular=qq_normalization * (1 + 3 * z - 2 * z**2) / z,
    )
    qq_manuscript = pqq_times_cutoff_log + EndpointCoefficient(
        delta=qq_normalization * (1 - 3 * pi**2),
        d1_prefactor=2 * qq_normalization * (1 + z**2),
        regular=qq_normalization * (1 + 3 * z - z**2) / z,
    )

    pqg = 1 - 2 * z + 2 * z**2
    qg_log = (
        lambda1_squared
        * lambda2_squared
        * z**2
        / (s**2 * (1 - z) ** 2)
    ).log()
    qg_graph_normalization = alpha_s * color_t / (4 * pi)
    qg_pieces = MappingProxyType(
        {
            "box": EndpointCoefficient(
                regular=2 * qg_graph_normalization * (1 + qg_log / 2)
            ),
            "triangle pair": EndpointCoefficient(
                regular=-2
                * qg_graph_normalization
                * z
                * (1 - z)
                * (2 + qg_log)
            ),
            "bubble": EndpointCoefficient(
                regular=-qg_graph_normalization * (1 - z) ** 2
            ),
        }
    )
    qg_transverse_total = sum(qg_pieces.values(), EndpointCoefficient())
    qg_transverse = ChannelAssembly(
        pieces=qg_pieces,
        total=qg_transverse_total,
    )
    qg_ward_remainder = EndpointCoefficient(
        regular=qg_graph_normalization * (1 - z) ** 2 / z
    )
    qg_cached = qg_transverse_total + qg_ward_remainder
    qg_manuscript = EndpointCoefficient(
        regular=qg_graph_normalization
        / z
        * (
            1
            + z**3
            + z**2
            - 2 * z
            + z * pqg * (1 + qg_log)
        )
    )
    if not (qg_cached - qg_manuscript).is_zero:
        raise ValueError("Cached qg result no longer matches the manuscript formula")
    return FullDYCoefficient(
        ordinary_virtual=ordinary_virtual,
        local_all_cut_virtual=local_all_cut_virtual,
        qq_transverse=qq_transverse,
        qq_cached_notebook=notebook_total,
        qq_manuscript=qq_manuscript,
        qq_transverse_minus_notebook=qq_transverse.total - notebook_total,
        qq_transverse_minus_manuscript=qq_transverse.total - qq_manuscript,
        qq_notebook_minus_manuscript=notebook_total - qq_manuscript,
        qg_transverse=qg_transverse,
        qg_cached_notebook=qg_cached,
        qg_manuscript=qg_manuscript,
        qg_transverse_minus_manuscript=qg_transverse_total - qg_manuscript,
    )


def assemble_full_dy(
    reductions: Mapping[str, "ReductionResult"],
) -> tuple[ReductionAudit, FullDYCoefficient]:
    """Audit every physical sector and perform the analytic-master handoff."""

    audit = audit_physical_reductions(reductions)
    if not audit.exact:
        raise ValueError("Physical reduction audit contains a nonzero residual")
    coefficient = assemble_closed_form_dy()
    handoff = build_analytic_master_handoff(audit, coefficient)
    if not handoff.finite_checks_exact:
        raise ValueError("Analytic-master handoff does not reproduce its ledger")
    return audit, dataclass_replace(coefficient, master_handoff=handoff)


__all__ = [
    "AnalyticMasterHandoff",
    "ApartTerm",
    "ChannelAssembly",
    "EndpointCoefficient",
    "FullDYCoefficient",
    "MasterInsertion",
    "NumeratorReduction",
    "PHYSICAL_TOPOLOGY_NAMES",
    "ReducedIntegralTerm",
    "ReductionAudit",
    "alpha_s",
    "apart_kernel",
    "assemble_closed_form_dy",
    "assemble_full_dy",
    "audit_physical_reductions",
    "build_analytic_master_handoff",
    "color_f",
    "color_t",
    "crossed_box_reductions",
    "d",
    "denominator_bases",
    "epsilon",
    "electric_charge",
    "lambda1_squared",
    "lambda2_squared",
    "mass_squared",
    "mu_r_squared",
    "normalize_rational",
    "numerator_reductions",
    "numerator_relations",
    "physical_numerators",
    "qg_ward_reductions",
    "reduce_numerator",
    "replace_all",
    "s",
    "strong_coupling",
    "color_count",
    "z",
]
