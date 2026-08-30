"""Typed DIS reference expressions retained in the Mathematica DY notebook.

The notebook cells are historical inputs to a DY scheme-change check, not a
graph-by-graph DIS derivation.  This module preserves them as executable,
provenance-labelled regression data and uses the same typed endpoint basis as
the native DIS calculation.  In particular, no ``z -> 1`` substitution is
ever applied to a distribution.  It also reconstructs the DY side of that
check independently from the displayed ``MP - PM`` coefficients.  The typed
reconstruction exposes, and then restores, the external-leg virtual pair that
the historical scheme-change cell multiplied by zero.
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
    color_f,
    color_t,
    electric_charge,
    epsilon,
    lambda_squared,
    mu_r_squared,
    pi,
    scalar_printer,
    strong_coupling,
    x,
)


MATHEMATICA_NOTEBOOK_SOURCE = "calculations/dy/mathematica/DY_calculation.nb"
MATHEMATICA_NOTEBOOK_SHA256 = (
    "e713b5f7d3461cc52d5763bce58d7621"
    "3f380c65cbaf2b8eca1c0144c1e4e009"
)
MATHEMATICA_ORIGINAL_NOTEBOOK_SHA256 = (
    "59b7406ee30e34a5756916802088dc733"
    "4214a0356d633df96020ef16124ebca"
)
MATHEMATICA_NOTEBOOK_BYTES = 1_805_831
MATHEMATICA_GLUON_SOURCE = f"{MATHEMATICA_NOTEBOOK_SOURCE}:41429-41718"
MATHEMATICA_FERMION_SOURCE = f"{MATHEMATICA_NOTEBOOK_SOURCE}:42636-42865"
MATHEMATICA_DY_GLUON_SCHEME_SOURCE = (
    f"{MATHEMATICA_NOTEBOOK_SOURCE}:41309-41818"
)
MATHEMATICA_DY_FERMION_SCHEME_SOURCE = (
    f"{MATHEMATICA_NOTEBOOK_SOURCE}:41820-43090"
)
MATHEMATICA_DY_EXTERNAL_LEG_SOURCE = (
    f"{MATHEMATICA_NOTEBOOK_SOURCE}:15179-15557,41820-41955"
)


lambda1_squared = S(
    "Lambda1_squared",
    print=scalar_printer(latex=r"\Lambda_1^2", typst="Lambda_1^2"),
)
lambda2_squared = S(
    "Lambda2_squared",
    print=scalar_printer(latex=r"\Lambda_2^2", typst="Lambda_2^2"),
)
factorization_pole = S(
    "epsilon_IR",
    print=scalar_printer(
        latex=r"\epsilon_{\mathrm{IR}}",
        typst="epsilon_(upright(I R))",
    ),
)


@dataclass(frozen=True, slots=True)
class MathematicaDISReference:
    """The two notebook DIS inputs with their convention boundaries exposed."""

    gluon_all_epsilon: Expression
    gluon_through_finite: Expression
    fermion_pole_bracket: DistributionCoefficient
    fermion_finite_bracket: DistributionCoefficient
    source: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class MathematicaSchemeChangeAudit:
    """Closed two-beam identity in the historical, correlated conventions.

    Both sides are transcribed from the same Mathematica notebook.  A zero
    residual checks the transcription and the notebook's internal algebra; it
    is not an independent physical universality check.
    """

    gluon_dis_pm_minus_mp: Expression
    gluon_dy_mp_minus_pm: Expression
    gluon_residual: Expression
    fermion_dis_pm_minus_mp: DistributionCoefficient
    fermion_dy_mp_minus_pm_incomplete: DistributionCoefficient
    fermion_external_leg_virtual: DistributionCoefficient
    fermion_dy_mp_minus_pm: DistributionCoefficient
    fermion_incomplete_residual: DistributionCoefficient
    fermion_residual: DistributionCoefficient
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


def mathematica_one_leg_gluon_conversion(
    *,
    cutoff_squared: Expression = lambda_squared,
    variable: Expression = x,
    scale_squared: Expression = mu_r_squared,
) -> Expression:
    """Return the historical gluon ``MPDIStoDY`` source object.

    This is a convention-bound regression extracted from the Mathematica
    scheme-change cells.  It retains the source sign as written.  Because the
    quark and gluon cells do not share a reliable global orientation, callers
    comparing with a native MP-PM kernel must declare their normalization and
    sign map explicitly.
    """

    kernel = _gluon_kernel(variable)
    return alpha_s / (8 * pi) * (
        kernel / factorization_pole
        - 2
        - kernel
        * _scale_argument(
            cutoff_squared,
            variable=variable,
            scale_squared=scale_squared,
        ).log()
    )


def mathematica_one_leg_fermion_conversion(
    *,
    cutoff_squared: Expression = lambda_squared,
    variable: Expression = x,
    scale_squared: Expression = mu_r_squared,
) -> DistributionCoefficient:
    """Return the historical fermion ``MPDIStoDY`` source object.

    The pole and finite brackets retain the typed endpoint basis, so this
    helper can be summed over incoming legs without ever substituting the
    endpoint variable inside a delta or plus distribution.  Its source sign is
    preserved rather than interpreted as a reliable physical orientation.
    """

    pole, finite = mathematica_fermion_brackets(
        cutoff_squared=cutoff_squared,
        variable=variable,
        scale_squared=scale_squared,
    )
    return (
        pole.scaled(1 / factorization_pole) + finite
    ).scaled(-alpha_s * color_f / (12 * pi))


def mathematica_dy_gluon_conversion() -> Expression:
    """Return the notebook's two-beam gluonic conversion regression."""

    return canonical(
        mathematica_one_leg_gluon_conversion(
            cutoff_squared=lambda1_squared,
        )
        + mathematica_one_leg_gluon_conversion(
            cutoff_squared=lambda2_squared,
        )
    )


def mathematica_dy_fermion_conversion() -> DistributionCoefficient:
    """Return the valid typed two-beam fermionic conversion regression."""

    first = mathematica_one_leg_fermion_conversion(
        cutoff_squared=lambda1_squared
    )
    second = mathematica_one_leg_fermion_conversion(
        cutoff_squared=lambda2_squared
    )
    return first + second


def mathematica_dy_gluon_mp_minus_pm() -> Expression:
    """Transcribe the independent DY ``MP - PM`` gluon graph difference.

    This is the compact form of Mathematica ``Out[412]`` in the positive
    region ``0 < x < 1``.  It is deliberately assembled from the DY-side
    output rather than by negating :func:`mathematica_dy_gluon_conversion`.
    """

    kernel = _gluon_kernel()
    two_leg_log = (
        _scale_argument(lambda1_squared).log()
        + _scale_argument(lambda2_squared).log()
    )
    return alpha_s / (8 * pi) * (
        -2 * kernel / factorization_pole
        + 4
        + kernel * two_leg_log
    )


def mathematica_dy_fermion_mp_minus_pm_incomplete(
) -> DistributionCoefficient:
    """Transcribe the historical DY quark difference before its omitted bubbles.

    The delta term is Mathematica ``Out[422]`` and the remaining distribution
    is ``Out[423]``.  Positive-region logarithms are written as sums of
    dimensionless one-leg logs so that Symbolica can compare the result
    without assuming a generic complex logarithm product rule.  This is the
    raw ``MPDY`` normalization; the scheme comparison subsequently applies the
    source's smooth factor ``x`` with exact distribution algebra.
    """

    normalization = alpha_s * color_f / (2 * pi)
    cutoff_log = (
        (lambda1_squared / mu_r_squared).log()
        + (lambda2_squared / mu_r_squared).log()
    )
    phase_log = (
        _scale_argument(lambda1_squared).log()
        + _scale_argument(lambda2_squared).log()
    )
    collinear_log = (
        (lambda1_squared * x / mu_r_squared).log()
        + (lambda2_squared * x / mu_r_squared).log()
    )
    delta_part = DistributionCoefficient(
        variable=x,
        delta=normalization
        * (
            4 / factorization_pole
            + 8
            - 2 * pi**2 / 3
            - 2 * cutoff_log
        ),
    )
    pole_part = (
        DistributionCoefficient(variable=x, regular=2 - 2 * x)
        + DistributionCoefficient.plus_basis(x, 0).multiply_smooth(4 * x)
    ).scaled(normalization / factorization_pole)
    finite_part = (
        DistributionCoefficient(
            variable=x,
            regular=2 * (-2 + x) + (x - 1) * phase_log,
        )
        + DistributionCoefficient.plus_basis(x, 0).multiply_smooth(
            -2 * x * collinear_log
        )
        + DistributionCoefficient.plus_basis(x, 1).multiply_smooth(-4 * x)
    ).scaled(normalization)
    return delta_part + pole_part + finite_part


def mathematica_dy_fermion_external_leg_virtual(
) -> DistributionCoefficient:
    """Return the two half-weighted ``valv5`` bubbles omitted by the old cell.

    ``valv5`` is an external-leg cut bubble.  The full DY virtual assembly
    contains one half from each incoming leg, while the historical
    scheme-change cell explicitly multiplied both by zero.  Expanding its
    displayed ``1/(1-epsilon_IR)`` Born normalization through the finite term
    gives this endpoint-supported correction.
    """

    normalization = alpha_s * color_f / (2 * pi)
    cutoff_log = (
        (lambda1_squared / mu_r_squared).log()
        + (lambda2_squared / mu_r_squared).log()
    )
    return DistributionCoefficient(
        variable=x,
        delta=normalization
        * (
            -1 / factorization_pole
            - 1
            + cutoff_log / 2
        ),
    )


def mathematica_dy_fermion_mp_minus_pm() -> DistributionCoefficient:
    """Return the corrected DY ``MP - PM`` quark difference.

    Multiplication by ``x`` is part of the source's DY-to-DIS convolution
    normalization.  It is performed as a smooth distribution multiplication,
    never by replacing ``x`` with one inside a delta or plus distribution.
    """

    corrected_raw = (
        mathematica_dy_fermion_mp_minus_pm_incomplete()
        + mathematica_dy_fermion_external_leg_virtual()
    )
    return corrected_raw.multiply_smooth(x)


def _positive_cutoff_log_basis(
    coefficient: DistributionCoefficient,
) -> DistributionCoefficient:
    """Rewrite reciprocal cutoff logs in the declared positive scale region."""

    def rewrite(value: Expression) -> Expression:
        result = value
        for cutoff_squared in (lambda1_squared, lambda2_squared):
            result = result.replace(
                (mu_r_squared / cutoff_squared).log(),
                -(cutoff_squared / mu_r_squared).log(),
            )
        return canonical(result)

    return DistributionCoefficient(
        variable=coefficient.variable,
        delta=rewrite(coefficient.delta),
        plus=tuple(rewrite(value) for value in coefficient.plus),
        regular=rewrite(coefficient.regular),
    )


def mathematica_scheme_change_audit() -> MathematicaSchemeChangeAudit:
    """Reproduce the notebook's closed two-beam identity component by component.

    This intentionally compares historical expressions with other historical
    expressions.  Native DIS--DY universality is established elsewhere from
    independent topology/cut/master assemblies.
    """

    gluon_dis = mathematica_dy_gluon_conversion()
    gluon_dy = mathematica_dy_gluon_mp_minus_pm()
    gluon_residual = canonical(gluon_dy + gluon_dis)

    fermion_dis = _positive_cutoff_log_basis(
        mathematica_dy_fermion_conversion()
    )
    fermion_incomplete = (
        mathematica_dy_fermion_mp_minus_pm_incomplete().multiply_smooth(x)
    )
    fermion_external_leg = (
        mathematica_dy_fermion_external_leg_virtual().multiply_smooth(x)
    )
    fermion_dy = fermion_incomplete + fermion_external_leg
    fermion_incomplete_residual = fermion_incomplete + fermion_dis
    fermion_residual = fermion_dy + fermion_dis
    return MathematicaSchemeChangeAudit(
        gluon_dis_pm_minus_mp=gluon_dis,
        gluon_dy_mp_minus_pm=gluon_dy,
        gluon_residual=gluon_residual,
        fermion_dis_pm_minus_mp=fermion_dis,
        fermion_dy_mp_minus_pm_incomplete=fermion_incomplete,
        fermion_external_leg_virtual=fermion_external_leg,
        fermion_dy_mp_minus_pm=fermion_dy,
        fermion_incomplete_residual=fermion_incomplete_residual,
        fermion_residual=fermion_residual,
        source=MappingProxyType(
            {
                "gluon DY MP - PM": MATHEMATICA_DY_GLUON_SCHEME_SOURCE,
                "fermion DY MP - PM": MATHEMATICA_DY_FERMION_SCHEME_SOURCE,
                "external-leg virtual": MATHEMATICA_DY_EXTERNAL_LEG_SOURCE,
                "DIS gluon legs": MATHEMATICA_GLUON_SOURCE,
                "DIS fermion legs": MATHEMATICA_FERMION_SOURCE,
            }
        ),
    )


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

    kernel = _gluon_kernel()
    expected_dy_gluon = alpha_s / (8 * pi) * (
        2 * kernel / factorization_pole
        - 4
        - kernel
        * (
            _scale_argument(lambda1_squared).log()
            + _scale_argument(lambda2_squared).log()
        )
    )
    gluon_leg_sum_residual = canonical(
        mathematica_dy_gluon_conversion() - expected_dy_gluon
    )
    if gluon_leg_sum_residual != E("0"):
        raise AssertionError(
            "One-leg gluon conversions no longer reconstruct the historical "
            f"two-beam expression: {gluon_leg_sum_residual}"
        )

    first_pole, first_finite = mathematica_fermion_brackets(
        cutoff_squared=lambda1_squared
    )
    second_pole, second_finite = mathematica_fermion_brackets(
        cutoff_squared=lambda2_squared
    )
    if first_pole != second_pole:
        raise AssertionError("The fermion pole bracket unexpectedly depends on cutoff")
    expected_dy_fermion = (
        first_pole.scaled(2 / factorization_pole)
        + first_finite
        + second_finite
    ).scaled(-alpha_s * color_f / (12 * pi))
    fermion_leg_sum_residual = (
        mathematica_dy_fermion_conversion() - expected_dy_fermion
    )
    if not fermion_leg_sum_residual.is_zero:
        raise AssertionError(
            "One-leg fermion conversions no longer reconstruct the historical "
            f"two-beam expression: {fermion_leg_sum_residual.residuals()}"
        )

    scheme_audit = mathematica_scheme_change_audit()
    if scheme_audit.gluon_residual != E("0"):
        raise AssertionError(
            "The gluon MP/PM scheme residual is nonzero: "
            f"{scheme_audit.gluon_residual}"
        )
    expected_incomplete_delta = alpha_s * color_f / (2 * pi) * (
        1 / factorization_pole
        + 1
        - (lambda1_squared / mu_r_squared).log() / 2
        - (lambda2_squared / mu_r_squared).log() / 2
    )
    incomplete_residual_check = (
        scheme_audit.fermion_incomplete_residual
        - DistributionCoefficient(
            variable=x,
            delta=expected_incomplete_delta,
        )
    )
    if not incomplete_residual_check.is_zero:
        raise AssertionError(
            "The omitted external-leg signature changed: "
            f"{incomplete_residual_check.residuals()}"
        )
    if not scheme_audit.fermion_residual.is_zero:
        raise AssertionError(
            "The corrected fermion MP/PM scheme residual is nonzero: "
            f"{scheme_audit.fermion_residual.residuals()}"
        )
    return MappingProxyType(
        {
            "gluon expansion residual": gluon_residual,
            "gluon one-leg sum residual": gluon_leg_sum_residual,
            "gluon universal scheme residual": scheme_audit.gluon_residual,
            "fermion pole residual": pole_residual,
            "fermion finite": finite,
            "fermion one-leg sum residual": fermion_leg_sum_residual,
            "fermion omitted-virtual signature": incomplete_residual_check,
            "fermion universal scheme residual": scheme_audit.fermion_residual,
            "notebook SHA-256": MATHEMATICA_NOTEBOOK_SHA256,
        }
    )


MATHEMATICA_REFERENCE = mathematica_dis_reference()
MATHEMATICA_REFERENCE_SELF_CHECKS = self_check()


__all__ = [
    "MATHEMATICA_FERMION_SOURCE",
    "MATHEMATICA_GLUON_SOURCE",
    "MATHEMATICA_DY_EXTERNAL_LEG_SOURCE",
    "MATHEMATICA_DY_FERMION_SCHEME_SOURCE",
    "MATHEMATICA_DY_GLUON_SCHEME_SOURCE",
    "MATHEMATICA_NOTEBOOK_BYTES",
    "MATHEMATICA_ORIGINAL_NOTEBOOK_SHA256",
    "MATHEMATICA_NOTEBOOK_SHA256",
    "MATHEMATICA_NOTEBOOK_SOURCE",
    "MATHEMATICA_REFERENCE",
    "MATHEMATICA_REFERENCE_SELF_CHECKS",
    "MathematicaDISReference",
    "MathematicaSchemeChangeAudit",
    "factorization_pole",
    "lambda1_squared",
    "lambda2_squared",
    "mathematica_dis_reference",
    "mathematica_dy_fermion_conversion",
    "mathematica_dy_fermion_external_leg_virtual",
    "mathematica_dy_fermion_mp_minus_pm",
    "mathematica_dy_fermion_mp_minus_pm_incomplete",
    "mathematica_dy_gluon_conversion",
    "mathematica_dy_gluon_mp_minus_pm",
    "mathematica_fermion_brackets",
    "mathematica_gluon_all_epsilon",
    "mathematica_gluon_through_finite",
    "mathematica_one_leg_fermion_conversion",
    "mathematica_one_leg_gluon_conversion",
    "mathematica_scheme_change_audit",
    "self_check",
]
