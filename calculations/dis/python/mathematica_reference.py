"""Typed DIS reference expressions retained in the Mathematica DY notebook.

The notebook cells are historical inputs to a DY scheme-change check, not a
graph-by-graph DIS derivation.  This module preserves them as executable,
provenance-labelled regression data and uses the same typed endpoint basis as
the native DIS calculation.  In particular, no ``z -> 1`` substitution is
ever applied to a distribution.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from symbolica import E, S, Expression

from calculations.dis.python.physical import (
    DistributionCoefficient,
    alpha_s,
    canonical,
    color_count,
    color_f,
    color_t,
    electric_charge,
    epsilon,
    lambda_squared,
    mu_r_squared,
    pi,
    strong_coupling,
    x,
)


MATHEMATICA_NOTEBOOK_SOURCE = (
    "../LUDY/DIS_DY_analytic/DY_calculation.nb"
)
MATHEMATICA_NOTEBOOK_SHA256 = (
    "59b7406ee30e34a5756916802088dc733"
    "4214a0356d633df96020ef16124ebca"
)
MATHEMATICA_NOTEBOOK_BYTES = 1_805_887
MATHEMATICA_GLUON_SOURCE = f"{MATHEMATICA_NOTEBOOK_SOURCE}:41429-41718"
MATHEMATICA_FERMION_SOURCE = f"{MATHEMATICA_NOTEBOOK_SOURCE}:42636-42865"


lambda1_squared = S("Lambda1_squared")
lambda2_squared = S("Lambda2_squared")
factorization_pole = S("epsilon_IR")


@dataclass(frozen=True, slots=True)
class MathematicaDISReference:
    """The two notebook DIS inputs with their convention boundaries exposed."""

    gluon_all_epsilon: Expression
    gluon_through_finite: Expression
    fermion_pole_bracket: DistributionCoefficient
    fermion_finite_bracket: DistributionCoefficient
    source: Mapping[str, str]


def _gluon_kernel(variable: Expression = x) -> Expression:
    return 1 - 2 * variable + 2 * variable**2


def _scale_argument(
    cutoff_squared: Expression,
    *,
    variable: Expression = x,
    scale_squared: Expression = mu_r_squared,
) -> Expression:
    return cutoff_squared * variable * (1 - variable) / scale_squared


def mathematica_gluon_all_epsilon(
    *,
    cutoff_squared: Expression = lambda_squared,
    variable: Expression = x,
    scale_squared: Expression = mu_r_squared,
) -> Expression:
    """Return the compact all-epsilon gluonic DIS input from the notebook."""

    kernel = _gluon_kernel(variable)
    scale_argument = _scale_argument(
        cutoff_squared,
        variable=variable,
        scale_squared=scale_squared,
    )
    return (
        Expression.I
        * electric_charge**2
        * strong_coupling**2
        * color_t
        * variable
        / pi
        * (kernel - 2 * epsilon)
        / ((1 - epsilon) * epsilon)
        * scale_argument ** (-epsilon)
    )


def mathematica_gluon_through_finite(
    *,
    cutoff_squared: Expression = lambda_squared,
    variable: Expression = x,
    scale_squared: Expression = mu_r_squared,
) -> Expression:
    """Return the notebook's explicit pole plus finite gluonic expression."""

    kernel = _gluon_kernel(variable)
    scale_argument = _scale_argument(
        cutoff_squared,
        variable=variable,
        scale_squared=scale_squared,
    )
    return (
        Expression.I
        * electric_charge**2
        * strong_coupling**2
        * color_t
        * variable
        / pi
        * (
            kernel / epsilon
            - 1
            + 2 * (variable - 1) * variable
            - kernel * scale_argument.log()
        )
    )


def mathematica_fermion_brackets(
    *,
    cutoff_squared: Expression = lambda_squared,
    variable: Expression = x,
    scale_squared: Expression = mu_r_squared,
) -> tuple[DistributionCoefficient, DistributionCoefficient]:
    """Return the pole and finite brackets of the final fermionic assignment."""

    delta = DistributionCoefficient.delta_basis(variable)
    d0 = DistributionCoefficient.plus_basis(variable, 0)
    d1 = DistributionCoefficient.plus_basis(variable, 1)
    scale_argument = _scale_argument(
        cutoff_squared,
        variable=variable,
        scale_squared=scale_squared,
    )
    pole = (
        delta.scaled(9)
        + DistributionCoefficient(
            variable=variable,
            regular=6 * variable * (1 - variable),
        )
        + d0.multiply_smooth(12 * variable**2)
    )
    finite = (
        delta.scaled(
            21
            - 2 * pi**2
            + 9 * (scale_squared / cutoff_squared).log()
        )
        + DistributionCoefficient(
            variable=variable,
            regular=(
                6
                * variable
                * (
                    -2
                    + variable
                    + (variable - 1) * scale_argument.log()
                )
            ),
        )
        + d0.multiply_smooth(
            -12
            * variable**2
            * (cutoff_squared * variable / scale_squared).log()
        )
        + d1.multiply_smooth(-12 * variable**2)
    )
    return pole, finite


def mathematica_dis_reference() -> MathematicaDISReference:
    pole, finite = mathematica_fermion_brackets()
    return MathematicaDISReference(
        gluon_all_epsilon=mathematica_gluon_all_epsilon(),
        gluon_through_finite=mathematica_gluon_through_finite(),
        fermion_pole_bracket=pole,
        fermion_finite_bracket=finite,
        source=MappingProxyType(
            {
                "gluon": MATHEMATICA_GLUON_SOURCE,
                "fermion": MATHEMATICA_FERMION_SOURCE,
            }
        ),
    )


def mathematica_dy_gluon_conversion() -> Expression:
    """Return the notebook's two-beam gluonic conversion regression."""

    kernel = _gluon_kernel()
    return alpha_s / (8 * pi) * (
        2 * kernel / factorization_pole
        - 4
        - kernel
        * (
            _scale_argument(lambda1_squared).log()
            + _scale_argument(lambda2_squared).log()
        )
    )


def mathematica_dy_fermion_conversion() -> DistributionCoefficient:
    """Return the valid typed two-beam fermionic conversion regression."""

    first_pole, first_finite = mathematica_fermion_brackets(
        cutoff_squared=lambda1_squared
    )
    second_pole, second_finite = mathematica_fermion_brackets(
        cutoff_squared=lambda2_squared
    )
    if first_pole != second_pole:
        raise AssertionError("The fermion pole bracket unexpectedly depends on cutoff")
    return (
        first_pole.scaled(2 / factorization_pole)
        + first_finite
        + second_finite
    ).scaled(-alpha_s * color_f / (12 * pi))


def self_check() -> Mapping[str, object]:
    """Verify the compact gluon expansion and distribution canonicalization."""

    expanded = mathematica_gluon_all_epsilon().series(
        epsilon,
        0,
        0,
    ).to_expression()
    gluon_residual = canonical(
        expanded - mathematica_gluon_through_finite()
    )
    if gluon_residual != E("0"):
        raise AssertionError(
            f"Mathematica gluon reference expansion changed: {gluon_residual}"
        )

    pole, finite = mathematica_fermion_brackets()
    expected_pole = DistributionCoefficient(
        variable=x,
        delta=E("9"),
        plus=(E("12"),),
        regular=6 * x * (1 - x) - 12 * (1 + x),
    )
    pole_residual = pole - expected_pole
    if not pole_residual.is_zero:
        raise AssertionError(
            f"Mathematica fermion pole canonicalization changed: "
            f"{pole_residual.residuals()}"
        )
    if len(finite.plus) != 2:
        raise AssertionError("Expected explicit D0 and D1 fermion coefficients")
    return MappingProxyType(
        {
            "gluon expansion residual": gluon_residual,
            "fermion pole residual": pole_residual,
            "fermion finite": finite,
            "notebook SHA-256": MATHEMATICA_NOTEBOOK_SHA256,
        }
    )


MATHEMATICA_REFERENCE = mathematica_dis_reference()
MATHEMATICA_REFERENCE_SELF_CHECKS = self_check()


__all__ = [
    "MATHEMATICA_FERMION_SOURCE",
    "MATHEMATICA_GLUON_SOURCE",
    "MATHEMATICA_NOTEBOOK_BYTES",
    "MATHEMATICA_NOTEBOOK_SHA256",
    "MATHEMATICA_NOTEBOOK_SOURCE",
    "MATHEMATICA_REFERENCE",
    "MATHEMATICA_REFERENCE_SELF_CHECKS",
    "MathematicaDISReference",
    "factorization_pole",
    "lambda1_squared",
    "lambda2_squared",
    "mathematica_dis_reference",
    "mathematica_dy_fermion_conversion",
    "mathematica_dy_gluon_conversion",
    "mathematica_fermion_brackets",
    "mathematica_gluon_all_epsilon",
    "mathematica_gluon_through_finite",
    "self_check",
]
