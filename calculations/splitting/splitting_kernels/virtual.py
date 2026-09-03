"""Virtual quark and gluon self-energy integrations."""

from dataclasses import dataclass

from symbolica import Expression, S

from .channels import kernel_gg, kernel_qq
from .colors import ColorContext
from .kinematics import Kinematics, canonical, set_dimension
from .normalization import derive_phase_space_normalization
from .phase_space import integrate_unit_interval_beta
from .kernels import ap_qg_cdr
from .tensors import (
    GluonVirtualNumeratorResult,
    TensorContext,
    VirtualNumeratorResult,
    gluon_virtual_self_energy_numerator,
    virtual_self_energy_numerator,
)


@dataclass(frozen=True)
class VirtualPhaseSpaceResult:
    numerator: VirtualNumeratorResult
    color_factor: Expression
    cut_transverse_result: Expression
    x_integral_beta_form: Expression
    x_integral: Expression
    reduced_exact_coefficient: Expression
    angular_scheme_factor: Expression
    scheme_adjusted_coefficient: Expression
    epsilon_expansion: Expression
    full_counterterm: Expression


@dataclass(frozen=True)
class GluonVirtualPhaseSpaceResult:
    numerator: GluonVirtualNumeratorResult
    gluon_color_factor: Expression
    quark_color_factor: Expression
    flavors: Expression
    gluon_cut_transverse_result: Expression
    quark_cut_transverse_result: Expression
    gluon_x_integral_beta_form: Expression
    quark_x_integral_beta_form: Expression
    gluon_x_integral: Expression
    quark_x_integral: Expression
    reduced_exact_coefficient: Expression
    angular_scheme_factor: Expression
    scheme_adjusted_coefficient: Expression
    epsilon_expansion: Expression
    full_counterterm: Expression


def beta(first: Expression, second: Expression) -> Expression:
    return canonical(
        Expression.GAMMA(first)
        * Expression.GAMMA(second)
        / Expression.GAMMA(first + second)
    )


def weighted_kernel_integral(
    kernel: Expression,
    kinematics: Kinematics,
    *,
    beta_form: bool = False,
) -> Expression:
    """Integrate the regulated kernel by beta-monomial replacement."""

    x = kinematics.x
    epsilon = kinematics.epsilon
    weight = x ** (-epsilon) * (1 - x) ** (-epsilon)
    return integrate_unit_interval_beta(
        weight * kernel,
        x,
        beta_function=S("Beta") if beta_form else None,
    )


def normalize_integer_trigamma(expression: Expression) -> Expression:
    """Reduce the integer trigamma values produced by gamma-function series."""

    result = expression
    for argument in range(2, 9):
        finite_sum = sum(
            Expression.num(1) / denominator**2
            for denominator in range(1, argument)
        )
        result = result.replace(
            Expression.num(argument).polygamma(1),
            Expression.PI**2 / 6 - finite_sum,
        )
    return canonical(result)


def virtual_x_integral(kinematics: Kinematics) -> Expression:
    """Integrate [x(1-x)]^-epsilon P_qq(x) over the hard fraction x."""

    return weighted_kernel_integral(
        kernel_qq(kinematics),
        kinematics,
    )


def virtual_x_integral_beta_form(kinematics: Kinematics) -> Expression:
    return weighted_kernel_integral(
        kernel_qq(kinematics),
        kinematics,
        beta_form=True,
    )


def integrate_virtual_self_energy(
    tensors: TensorContext,
    kinematics: Kinematics,
    colors: ColorContext,
) -> VirtualPhaseSpaceResult:
    numerator = virtual_self_energy_numerator(tensors, kinematics)
    epsilon = kinematics.epsilon
    exponent = (kinematics.d - 4) / 2
    kernel = set_dimension(
        numerator.leading_coefficient / (2 * kinematics.p2),
        kinematics,
    )
    normalized_prefactor = derive_phase_space_normalization(
        kinematics
    ).normalized_prefactor

    # The two cut deltas set |k_perp|^2=x(1-x)p1^2. The factor two is the
    # projected numerator 2*P_qq times the transverse radial Jacobian.
    cut_transverse = canonical(
        2
        * colors.cf
        * normalized_prefactor
        * (kinematics.x * (1 - kinematics.x)) ** exponent
        * kernel
        * kinematics.p2 ** ((kinematics.d - 6) / 2)
    )

    x_integral_beta_form = weighted_kernel_integral(
        kernel,
        kinematics,
        beta_form=True,
    )
    x_integral = weighted_kernel_integral(kernel, kinematics)

    # A self-energy insertion on one external leg contributes one half.
    # Combining that half with the factor two above and the p1^2 radial
    # integral gives 2/(d-4), or -1/epsilon.
    reduced_exact = canonical(-colors.cf * x_integral / epsilon)

    # Extract (Lambda^2/mu^2)^(-epsilon); the remaining dimensionless
    # MS-bar factor multiplies the exact beta integral.
    angular_scheme = canonical(
        Expression.EXP(Expression.EULER_GAMMA * epsilon)
        / Expression.GAMMA(1 - epsilon)
    )
    scheme_adjusted = canonical(angular_scheme * reduced_exact)
    expansion_series = scheme_adjusted.series(epsilon, 0, 0)
    expansion = sum(
        canonical(expansion_series.get_coefficient(power).expand())
        * epsilon**power
        for power in (-2, -1, 0)
    )
    expansion = normalize_integer_trigamma(expansion)

    full_counterterm = canonical(
        kinematics.delta(1 - kinematics.x)
        * (
            kinematics.cutoff2 / kinematics.renormalization_scale2
        )
        ** (-epsilon)
        * expansion
        * kinematics.born_quark
    )
    return VirtualPhaseSpaceResult(
        numerator=numerator,
        color_factor=colors.cf,
        cut_transverse_result=cut_transverse,
        x_integral_beta_form=x_integral_beta_form,
        x_integral=x_integral,
        reduced_exact_coefficient=reduced_exact,
        angular_scheme_factor=angular_scheme,
        scheme_adjusted_coefficient=scheme_adjusted,
        epsilon_expansion=expansion,
        full_counterterm=full_counterterm,
    )


def gluon_virtual_x_integral(kinematics: Kinematics) -> Expression:
    """Integrate the color-stripped CDR P_gg over the cut bubble."""

    return weighted_kernel_integral(
        kernel_gg(kinematics),
        kinematics,
    )


def gluon_virtual_x_integral_beta_form(
    kinematics: Kinematics,
) -> Expression:
    return weighted_kernel_integral(
        kernel_gg(kinematics),
        kinematics,
        beta_form=True,
    )


def quark_bubble_x_integral(kinematics: Kinematics) -> Expression:
    """Integrate the color-stripped CDR P_qg over one quark flavor."""

    return weighted_kernel_integral(
        ap_qg_cdr(kinematics.x, kinematics.epsilon),
        kinematics,
    )


def quark_bubble_x_integral_beta_form(
    kinematics: Kinematics,
) -> Expression:
    return weighted_kernel_integral(
        ap_qg_cdr(kinematics.x, kinematics.epsilon),
        kinematics,
        beta_form=True,
    )


def integrate_gluon_virtual_self_energy(
    tensors: TensorContext,
    kinematics: Kinematics,
    colors: ColorContext,
) -> GluonVirtualPhaseSpaceResult:
    """Integrate the complete cut axial-gauge gluon self-energy."""

    numerator = gluon_virtual_self_energy_numerator(tensors, kinematics)
    epsilon = kinematics.epsilon
    exponent = (kinematics.d - 4) / 2
    p2_power = kinematics.p2 ** ((kinematics.d - 6) / 2)
    angular = derive_phase_space_normalization(
        kinematics
    ).normalized_prefactor
    gg_kernel = set_dimension(
        numerator.gluon_loop_coefficient / (2 * kinematics.p2),
        kinematics,
    )
    qg_kernel = set_dimension(
        numerator.quark_loop_coefficient / (2 * kinematics.p2),
        kinematics,
    )

    # These are the normalized two-particle cuts before the gluon-bubble
    # symmetry factor and the common one-external-leg factor are applied.
    gluon_cut_transverse = canonical(
        2
        * colors.ca
        * angular
        * (kinematics.x * (1 - kinematics.x)) ** exponent
        * gg_kernel
        * p2_power
    )
    quark_cut_transverse = canonical(
        2
        * colors.nf
        * colors.tr
        * angular
        * (kinematics.x * (1 - kinematics.x)) ** exponent
        * qg_kernel
        * p2_power
    )

    gluon_beta_form = weighted_kernel_integral(
        gg_kernel,
        kinematics,
        beta_form=True,
    )
    quark_beta_form = weighted_kernel_integral(
        qg_kernel,
        kinematics,
        beta_form=True,
    )
    gluon_integral = weighted_kernel_integral(gg_kernel, kinematics)
    quark_integral = weighted_kernel_integral(qg_kernel, kinematics)

    # The 1/2 multiplying I_gg is the identical-gluon bubble symmetry factor.
    # For a quark bubble, the external-leg 1/2 combines with the two q/qbar
    # daughter labels, leaving n_f times the single P_qg integral.
    reduced_exact = canonical(
        -(
            colors.ca * gluon_integral / 2
            + colors.nf * colors.tr * quark_integral
        )
        / epsilon
    )
    angular_scheme = canonical(
        Expression.EXP(Expression.EULER_GAMMA * epsilon)
        / Expression.GAMMA(1 - epsilon)
    )
    scheme_adjusted = canonical(angular_scheme * reduced_exact)
    expansion_series = scheme_adjusted.series(epsilon, 0, 0)
    expansion = sum(
        canonical(expansion_series.get_coefficient(power).expand())
        * epsilon**power
        for power in (-2, -1, 0)
    )
    expansion = normalize_integer_trigamma(expansion)
    full_counterterm = canonical(
        kinematics.delta(1 - kinematics.x)
        * (
            kinematics.cutoff2 / kinematics.renormalization_scale2
        )
        ** (-epsilon)
        * expansion
        * kinematics.born_gluon
    )
    return GluonVirtualPhaseSpaceResult(
        numerator=numerator,
        gluon_color_factor=colors.ca,
        quark_color_factor=colors.tr,
        flavors=colors.nf,
        gluon_cut_transverse_result=gluon_cut_transverse,
        quark_cut_transverse_result=quark_cut_transverse,
        gluon_x_integral_beta_form=gluon_beta_form,
        quark_x_integral_beta_form=quark_beta_form,
        gluon_x_integral=gluon_integral,
        quark_x_integral=quark_integral,
        reduced_exact_coefficient=reduced_exact,
        angular_scheme_factor=angular_scheme,
        scheme_adjusted_coefficient=scheme_adjusted,
        epsilon_expansion=expansion,
        full_counterterm=full_counterterm,
    )
