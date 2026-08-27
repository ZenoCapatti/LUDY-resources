"""One-loop scalar masters used by the DIS reverse-unitarity calculation.

The formulas in this module are the three one-loop inputs listed in
``NLO_masters.tex``: the virtual massless bubble, the two-particle cut bubble,
and the fully three-mass three-particle cut triangle.  The ``paper_*``
functions retain the paper's Minkowski/Cutkosky phases exactly.  The shorter
reusable functions strip those phases and include the retained MS-bar loop
factor, matching the real scalar-master convention used by the DY pipeline.

The cut functions return analytic factors only.  Their theta-function support
is deliberately kept in :data:`MASTER_SUPPORT`, because the energy components
needed to evaluate it are not arguments of a scalar function of invariants.
Virtuality-integration measures, the DIS-only observable factor, and
spin/colour averages are not part of any scalar master; see
:func:`normalization_ledger`.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from symbolica import E, S, Expression


__all__ = (
    "MASTER_SUPPORT",
    "NORMALIZATION_SELF_CHECKS",
    "PAPER_PHASES",
    "MasterSupport",
    "NormalizationLedgerEntry",
    "kallen",
    "loop_normalization",
    "massless_cut_bubble",
    "massless_cut_triangle",
    "normalization_ledger",
    "normalization_self_checks",
    "paper_cut_bubble",
    "paper_cut_triangle",
    "paper_uncut_bubble",
    "uncut_bubble",
    "virtuality_integral_factor",
)


@dataclass(frozen=True, slots=True)
class MasterSupport:
    """Distributional support and branch data not encoded in an invariant."""

    theta_factors: tuple[str, ...]
    branch: str


@dataclass(frozen=True, slots=True)
class NormalizationLedgerEntry:
    """One exact factor in the scalar-master/observable normalization ledger."""

    name: str
    factor: Expression
    included_in: tuple[str, ...]
    convention: str
    note: str


MASTER_SUPPORT: Mapping[str, MasterSupport] = MappingProxyType(
    {
        "uncut_bubble": MasterSupport(
            theta_factors=(),
            branch="Feynman continuation of (-p_squared)^((d-4)/2)",
        ),
        "cut_bubble": MasterSupport(
            theta_factors=("Theta(p^0)", "Theta(p_squared)"),
            branch="future-directed timelike p; the cut vanishes off support",
        ),
        "cut_triangle": MasterSupport(
            theta_factors=(
                "Theta(-p1^0)",
                "Theta(p1_squared)",
                "Theta(p3^0)",
                "Theta(p3_squared)",
            ),
            branch=(
                "paper momentum routing with the physical square-root branch "
                "of lambda(p1_squared,p2_squared,p3_squared)"
            ),
        ),
    }
)


# The raw paper result is PAPER_PHASES[name] times the corresponding reusable
# real scalar master after removing its MS-bar loop factor.
PAPER_PHASES: Mapping[str, Expression] = MappingProxyType(
    {
        "uncut_bubble": Expression.I,
        "cut_bubble": E("-1"),
        "cut_triangle": -Expression.I,
    }
)


def kallen(x: Expression, y: Expression, z: Expression) -> Expression:
    """Return the Kallen polynomial ``lambda(x,y,z)``."""

    return x**2 + y**2 + z**2 - 2 * x * y - 2 * x * z - 2 * y * z


def loop_normalization(
    mu_squared: Expression,
    epsilon: Expression,
    euler_gamma: Expression,
) -> Expression:
    """Return the retained MS-bar factor for one loop.

    This factor is not printed in the appendix formulas themselves.  It is
    included in the reusable phase-stripped masters below, as in the existing
    DY scalar-master convention.
    """

    return (
        mu_squared * euler_gamma.exp() / (4 * Expression.PI)
    ) ** epsilon


def _paper_uncut_bubble_without_phase(
    momentum_squared: Expression,
    *,
    dimension: Expression,
) -> Expression:
    pi = Expression.PI
    return (
        pi ** (dimension / 2)
        * ((dimension - 2) / 2).gamma() ** 2
        * ((4 - dimension) / 2).gamma()
        / ((2 * pi) ** dimension * (dimension - 2).gamma())
        * (-momentum_squared) ** ((dimension - 4) / 2)
    )


def paper_uncut_bubble(
    momentum_squared: Expression,
    *,
    dimension: Expression,
) -> Expression:
    r"""Return the virtual bubble exactly in the paper convention.

    This is
    ``i*pi^(d/2)*Gamma((d-2)/2)^2*Gamma((4-d)/2)`` divided by
    ``(2*pi)^d*Gamma(d-2)``, times
    ``(-momentum_squared)^((d-4)/2)``.
    """

    return PAPER_PHASES["uncut_bubble"] * _paper_uncut_bubble_without_phase(
        momentum_squared,
        dimension=dimension,
    )


def uncut_bubble(
    momentum_squared: Expression,
    *,
    dimension: Expression,
    epsilon: Expression,
    mu_squared: Expression,
    euler_gamma: Expression,
) -> Expression:
    """Return the phase-stripped, MS-bar-normalized virtual bubble."""

    return loop_normalization(
        mu_squared,
        epsilon,
        euler_gamma,
    ) * _paper_uncut_bubble_without_phase(
        momentum_squared,
        dimension=dimension,
    )


def _paper_cut_bubble_without_phase(
    momentum_squared: Expression,
    *,
    dimension: Expression,
) -> Expression:
    pi = Expression.PI
    return (
        2 ** (4 - dimension)
        * momentum_squared ** ((dimension - 4) / 2)
        * pi ** ((dimension + 3) / 2)
        / ((2 * pi) ** dimension * ((dimension - 1) / 2).gamma())
    )


def paper_cut_bubble(
    momentum_squared: Expression,
    *,
    dimension: Expression,
) -> Expression:
    r"""Return the cut bubble exactly in the paper's ``2*pi*i`` convention.

    The returned analytic factor includes the paper's minus sign.  Multiply it
    by the two theta factors in ``MASTER_SUPPORT["cut_bubble"]``.  The sign is
    the phase from the two Cutkosky factors, not a negative phase-space
    Jacobian.
    """

    return PAPER_PHASES["cut_bubble"] * _paper_cut_bubble_without_phase(
        momentum_squared,
        dimension=dimension,
    )


def massless_cut_bubble(
    momentum_squared: Expression,
    *,
    dimension: Expression,
    epsilon: Expression,
    mu_squared: Expression,
    euler_gamma: Expression,
) -> Expression:
    """Return the positive, phase-stripped massless cut bubble.

    The internal lines are massless.  The result is nonzero only on the
    support recorded in ``MASTER_SUPPORT["cut_bubble"]``.
    """

    return loop_normalization(
        mu_squared,
        epsilon,
        euler_gamma,
    ) * _paper_cut_bubble_without_phase(
        momentum_squared,
        dimension=dimension,
    )


def _paper_cut_triangle_without_phase(
    p1_squared: Expression,
    p2_squared: Expression,
    p3_squared: Expression,
    *,
    dimension: Expression,
) -> Expression:
    pi = Expression.PI
    return (
        4
        * (-p1_squared * p2_squared * p3_squared)
        ** ((dimension - 4) / 2)
        * pi ** (dimension / 2 + 2)
        / (
            (2 * pi) ** dimension
            * (dimension / 2 - 1).gamma()
            * kallen(p1_squared, p2_squared, p3_squared)
            ** ((dimension - 3) / 2)
        )
    )


def paper_cut_triangle(
    p1_squared: Expression,
    p2_squared: Expression,
    p3_squared: Expression,
    *,
    dimension: Expression,
) -> Expression:
    r"""Return the general three-mass cut triangle in the paper convention.

    This preserves the paper's overall ``-i`` and its full
    ``lambda(p1_squared,p2_squared,p3_squared)`` dependence.  Multiply by the
    four theta factors in ``MASTER_SUPPORT["cut_triangle"]``; they correspond
    to the routing ``delta^-(k) delta^+(k+p1) delta^+(k-p3)``.
    """

    return PAPER_PHASES["cut_triangle"] * _paper_cut_triangle_without_phase(
        p1_squared,
        p2_squared,
        p3_squared,
        dimension=dimension,
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
    """Return the positive general three-mass cut triangle.

    ``massless`` describes its three internal cut lines; none of the external
    invariants is set to zero.  In particular, this intentionally uses
    ``kallen(p1_squared,p2_squared,p3_squared)`` rather than the specialized DY
    Gram determinant ``kallen(0,0,p3_squared)``.
    """

    return loop_normalization(
        mu_squared,
        epsilon,
        euler_gamma,
    ) * _paper_cut_triangle_without_phase(
        p1_squared,
        p2_squared,
        p3_squared,
        dimension=dimension,
    )


def virtuality_integral_factor(
    cutoff_squared: Expression,
    epsilon: Expression,
) -> Expression:
    r"""Integrate the universal leading-power virtuality singularity.

    For the physical region and the dimensional regulator used here,

    ``integral_0^Lambda^2 dp^2 (p^2)^(-1-epsilon)``
    ``= -(Lambda^2)^(-epsilon)/epsilon``.

    The argument is already the squared cutoff ``Lambda^2``.  The external
    measure ``1/(2*pi)`` and DIS factor ``1/(4*pi)`` are deliberately not
    included.
    """

    return -(cutoff_squared) ** (-epsilon) / epsilon


def normalization_ledger(
    *,
    dimension: Expression,
    epsilon: Expression,
    mu_squared: Expression,
    euler_gamma: Expression,
) -> tuple[NormalizationLedgerEntry, ...]:
    """Return an exact ledger of included and excluded normalization factors.

    The closed forms already contain the appropriate power of each included
    factor.  ``included_in=()`` marks factors which belong to the observable,
    not to a scalar master.  Spin and colour averages are also observable
    dependent and therefore intentionally absent from the scalar formulas.
    """

    pi = Expression.PI
    reusable = ("uncut_bubble", "cut_bubble", "cut_triangle")
    return (
        NormalizationLedgerEntry(
            name="one-loop measure",
            factor=(2 * pi) ** (-dimension),
            included_in=(
                "paper_uncut_bubble",
                "paper_cut_bubble",
                "paper_cut_triangle",
                *reusable,
            ),
            convention="both master conventions",
            note="one factor 1/(2*pi)^d per loop",
        ),
        NormalizationLedgerEntry(
            name="retained MS-bar loop factor",
            factor=loop_normalization(mu_squared, epsilon, euler_gamma),
            included_in=reusable,
            convention="phase-stripped reusable masters",
            note="not included in the literal paper_* appendix formulas",
        ),
        NormalizationLedgerEntry(
            name="phase-space cut edge",
            factor=2 * pi,
            included_in=("cut_bubble", "cut_triangle"),
            convention="phase-stripped reusable masters",
            note="one factor per cut edge after stripping Cutkosky phases",
        ),
        NormalizationLedgerEntry(
            name="paper Cutkosky cut edge",
            factor=2 * pi * Expression.I,
            included_in=("paper_cut_bubble", "paper_cut_triangle"),
            convention="raw paper Cutkosky masters",
            note="one factor per cut edge; net phases are in PAPER_PHASES",
        ),
        NormalizationLedgerEntry(
            name="virtuality integration measure",
            factor=1 / (2 * pi),
            included_in=(),
            convention="phase-stripped physical assembly",
            note="one factor per external p_i^2 integration",
        ),
        NormalizationLedgerEntry(
            name="DIS observable factor",
            factor=1 / (4 * pi),
            included_in=(),
            convention="phase-stripped physical assembly",
            note="apply after scalar-master assembly",
        ),
    )


def _canonical_zero(expression: Expression) -> Expression:
    return expression.expand().together().cancel()


def normalization_self_checks() -> Mapping[str, Expression]:
    """Run exact algebraic checks and return their zero residuals.

    Besides permutation symmetry and the dimensional exponents, these checks
    verify the complete paper/phase-stripped relation for all three masters
    and the known four-dimensional phase-space normalizations
    ``Bcut=1/(8*pi)`` and ``Tcut=1/(4*sqrt(lambda))``.
    """

    # Spell these out individually because the current Symbolica stub's
    # variadic ``S`` overload puts keyword-only attributes before ``*names``;
    # the runtime accepts the compact form but static type checkers do not.
    x = S("_dis_master_check_x")
    y = S("_dis_master_check_y")
    z = S("_dis_master_check_z")
    epsilon = S("_dis_master_check_epsilon")
    mu_squared = S("_dis_master_check_mu_squared")
    euler_gamma = S("_dis_master_check_euler_gamma")
    dimension = 4 - 2 * epsilon
    one = E("1")
    zero = E("0")
    pi = Expression.PI

    retained_loop_factor = loop_normalization(
        mu_squared,
        epsilon,
        euler_gamma,
    )
    reusable_arguments = {
        "dimension": dimension,
        "epsilon": epsilon,
        "mu_squared": mu_squared,
        "euler_gamma": euler_gamma,
    }
    lambda_xyz = kallen(x, y, z)

    checks = {
        "kallen x-y symmetry": _canonical_zero(
            lambda_xyz - kallen(y, x, z)
        ),
        "kallen cyclic symmetry": _canonical_zero(
            lambda_xyz - kallen(y, z, x)
        ),
        "d=4-2epsilon numerator exponent": _canonical_zero(
            (dimension - 4) / 2 + epsilon
        ),
        "d=4-2epsilon Kallen exponent": _canonical_zero(
            (dimension - 3) / 2 - (E("1/2") - epsilon)
        ),
        "paper uncut phase": _canonical_zero(
            retained_loop_factor * paper_uncut_bubble(x, dimension=dimension)
            - PAPER_PHASES["uncut_bubble"]
            * uncut_bubble(x, **reusable_arguments)
        ),
        "paper cut-bubble phase": _canonical_zero(
            retained_loop_factor * paper_cut_bubble(x, dimension=dimension)
            - PAPER_PHASES["cut_bubble"]
            * massless_cut_bubble(x, **reusable_arguments)
        ),
        "paper cut-triangle phase": _canonical_zero(
            retained_loop_factor
            * paper_cut_triangle(x, y, z, dimension=dimension)
            - PAPER_PHASES["cut_triangle"]
            * massless_cut_triangle(x, y, z, **reusable_arguments)
        ),
        "four-dimensional cut bubble": _canonical_zero(
            massless_cut_bubble(
                x,
                dimension=E("4"),
                epsilon=zero,
                mu_squared=one,
                euler_gamma=zero,
            )
            - 1 / (8 * pi)
        ),
        "four-dimensional cut triangle": _canonical_zero(
            massless_cut_triangle(
                x,
                y,
                z,
                dimension=E("4"),
                epsilon=zero,
                mu_squared=one,
                euler_gamma=zero,
            )
            - 1 / (4 * lambda_xyz ** E("1/2"))
        ),
        "leading virtuality integral": _canonical_zero(
            epsilon * virtuality_integral_factor(mu_squared, epsilon)
            + mu_squared ** (-epsilon)
        ),
    }

    failures = {name: residual for name, residual in checks.items() if residual != zero}
    if failures:
        details = "; ".join(f"{name}: {residual}" for name, residual in failures.items())
        raise AssertionError(f"DIS master normalization checks failed: {details}")

    return MappingProxyType(checks)


NORMALIZATION_SELF_CHECKS = normalization_self_checks()
