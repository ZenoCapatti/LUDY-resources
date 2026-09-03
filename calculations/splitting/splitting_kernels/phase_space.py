"""Distributional virtuality and transverse phase-space integration."""

from dataclasses import dataclass

from symbolica import Expression, S

from .channels import ChannelResult
from .kinematics import Kinematics, canonical, set_dimension
from .normalization import derive_phase_space_normalization


@dataclass(frozen=True)
class PhaseSpaceResult:
    channel: ChannelResult
    bulk_density: Expression
    bulk_coefficient: Expression
    boundary_density: Expression
    boundary_coefficient: Expression
    integrated_bulk: Expression
    integrated_boundary: Expression
    ap_bulk_coefficient: Expression
    ap_integrated_bulk: Expression
    ap_boundary_density: Expression
    ap_boundary_coefficient: Expression
    ap_integrated_boundary: Expression


def angular_factor(kinematics: Kinematics) -> Expression:
    dimension = kinematics.d
    return canonical(
        Expression.PI ** ((dimension - 2) / 2)
        / Expression.GAMMA((dimension - 2) / 2)
    )


def loop_measure_normalization(kinematics: Kinematics) -> Expression:
    return canonical(1 / (2 * Expression.PI) ** kinematics.d)


def integrate_unit_interval_beta(
    integrand: Expression,
    variable: Expression,
    *,
    beta_function: Expression | None = None,
) -> Expression:
    """Integrate a sum of ``c*x**a*(1-x)**b`` terms on the unit interval.

    This is an explicit integrand replacement, not a table of kernel
    integrals.  Exponents and coefficients are extracted from every Symbolica
    term and ``x**a*(1-x)**b`` is replaced by ``B(a+1,b+1)``.
    """

    exponent_wildcard = S("beta_exponent_")

    def factor_power(factor: Expression, base: Expression) -> Expression | None:
        matches = list(factor.match(base**exponent_wildcard))
        if len(matches) == 1:
            return matches[0][exponent_wildcard]
        return None

    result = Expression.num(0)
    for term in integrand.expand().terms():
        variable_power = Expression.num(0)
        complement_power = Expression.num(0)
        coefficient = Expression.num(1)
        for factor in term:
            power = factor_power(factor, variable)
            if power is not None:
                variable_power += power
                continue
            power = factor_power(factor, 1 - variable)
            if power is not None:
                complement_power += power
                continue
            # Symbolica canonically writes some rational factors with x-1.
            power = factor_power(factor, variable - 1)
            if power is not None:
                complement_power += power
                coefficient *= (-1) ** power
                continue
            coefficient *= factor

        variable_power = canonical(variable_power.expand()).expand()
        complement_power = canonical(complement_power.expand()).expand()
        coefficient = canonical(coefficient)
        if variable in coefficient.get_all_indeterminates():
            raise ValueError(
                "Unit-interval integrand is not a beta monomial: "
                f"{term} leaves coefficient {coefficient}"
            )

        first = canonical(variable_power + 1).expand()
        second = canonical(complement_power + 1).expand()
        total = canonical(first + second).expand()
        if beta_function is None:
            beta_value = (
                Expression.GAMMA(first)
                * Expression.GAMMA(second)
                / Expression.GAMMA(total)
            )
        else:
            beta_value = beta_function(first, second)
        result += coefficient * beta_value

    return canonical(result)


def integrate_delta_prime_bulk(
    weight: Expression,
    kinematics: Kinematics,
) -> Expression:
    root = kinematics.virtuality_root
    support = kinematics.theta(kinematics.cutoff2 - root)
    derivative = weight.derivative(kinematics.p2)
    return canonical(-derivative.replace(kinematics.p2, root) * support)


def delta_prime_boundary_density(
    weight: Expression,
    kinematics: Kinematics,
) -> Expression:
    root = kinematics.virtuality_root
    return canonical(
        weight.replace(kinematics.p2, kinematics.cutoff2)
        * kinematics.delta(kinematics.cutoff2 - root)
    )


def integrate_transverse_bulk(
    bulk_density: Expression,
    kinematics: Kinematics,
) -> tuple[Expression, Expression]:
    support = kinematics.theta(
        kinematics.cutoff2 - kinematics.virtuality_root
    )
    without_support = bulk_density.replace(support, 1)
    coefficient = canonical(kinematics.transverse2 * without_support)
    residual = canonical(
        without_support - coefficient / kinematics.transverse2
    )
    if residual != 0:
        raise ValueError(
            "Transverse bulk integrand is not proportional to 1/|k_perp|^2: "
            f"{residual}"
        )

    exponent = (kinematics.d - 4) / 2
    normalized_prefactor = derive_phase_space_normalization(
        kinematics
    ).normalized_prefactor
    integrated = (
        normalized_prefactor
        * coefficient
        * 2
        * kinematics.transverse_cutoff**exponent
        / (kinematics.d - 4)
    )
    return coefficient, canonical(integrated)


def integrate_transverse_boundary(
    weight: Expression,
    kinematics: Kinematics,
) -> Expression:
    exponent = (kinematics.d - 4) / 2
    coefficient = transverse_boundary_coefficient(weight, kinematics)
    normalized_prefactor = derive_phase_space_normalization(
        kinematics
    ).normalized_prefactor
    return canonical(
        normalized_prefactor
        * kinematics.transverse_cutoff**exponent
        * coefficient
    )


def transverse_boundary_coefficient(
    weight: Expression,
    kinematics: Kinematics,
) -> Expression:
    jacobian = kinematics.x * (1 - kinematics.x)
    on_boundary = kinematics.transverse_cutoff
    boundary_weight = weight.replace(
        kinematics.p2,
        kinematics.cutoff2,
    ).replace(
        kinematics.transverse2,
        on_boundary,
    )
    return canonical(jacobian * boundary_weight)


def integrate_channel_phase_space(
    channel: ChannelResult,
    kinematics: Kinematics,
) -> PhaseSpaceResult:
    weight = channel.virtuality_weight
    bulk_density = integrate_delta_prime_bulk(weight, kinematics)
    boundary_weight = channel.boundary_virtuality_weight
    boundary_density = delta_prime_boundary_density(
        boundary_weight,
        kinematics,
    )
    boundary_coefficient = transverse_boundary_coefficient(
        boundary_weight,
        kinematics,
    )
    bulk_coefficient, integrated_bulk = integrate_transverse_bulk(
        bulk_density,
        kinematics,
    )
    integrated_boundary = integrate_transverse_boundary(
        boundary_weight,
        kinematics,
    )

    ap_weight = channel.ap_virtuality_weight
    ap_bulk_density = integrate_delta_prime_bulk(ap_weight, kinematics)
    ap_bulk_coefficient, ap_integrated_bulk = integrate_transverse_bulk(
        ap_bulk_density,
        kinematics,
    )
    ap_boundary_density = delta_prime_boundary_density(
        boundary_weight,
        kinematics,
    )
    ap_integrated_boundary = integrate_transverse_boundary(
        boundary_weight,
        kinematics,
    )
    ap_boundary_coefficient = transverse_boundary_coefficient(
        boundary_weight,
        kinematics,
    )
    return PhaseSpaceResult(
        channel=channel,
        bulk_density=bulk_density,
        bulk_coefficient=bulk_coefficient,
        boundary_density=boundary_density,
        boundary_coefficient=set_dimension(
            boundary_coefficient,
            kinematics,
        ),
        integrated_bulk=canonical(integrated_bulk * channel.spec.born),
        integrated_boundary=canonical(
            integrated_boundary * channel.spec.born
        ),
        ap_bulk_coefficient=set_dimension(
            ap_bulk_coefficient,
            kinematics,
        ),
        ap_integrated_bulk=set_dimension(
            ap_integrated_bulk * channel.spec.born,
            kinematics,
        ),
        ap_boundary_density=set_dimension(
            ap_boundary_density,
            kinematics,
        ),
        ap_boundary_coefficient=set_dimension(
            ap_boundary_coefficient,
            kinematics,
        ),
        ap_integrated_boundary=set_dimension(
            ap_integrated_boundary * channel.spec.born,
            kinematics,
        ),
    )


def epsilon_series(
    expression: Expression,
    kinematics: Kinematics,
    depth: int = 0,
) -> Expression:
    dimensionally_regularized = set_dimension(expression, kinematics)
    return dimensionally_regularized.series(
        kinematics.epsilon,
        0,
        depth,
    ).to_expression()
