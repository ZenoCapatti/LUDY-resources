"""Channel inputs and their common symbolic reduction pipeline."""

from dataclasses import dataclass
from typing import Literal

from symbolica import Expression

from .colors import ColorContext
from .kinematics import Kinematics, canonical, collinear_coefficient
from .kernels import (
    APKernelName,
    ap_gq_cdr,
    ap_gg_cdr,
    ap_kernel_symbol,
    ap_qg_cdr,
    ap_qq_cdr,
    color_dress_ap_expression,
)
from .tensors import (
    TensorContext,
    gluon_born_reduced_numerator,
    gluon_parent_quark_born_numerator,
    gluon_self_splitting_numerator,
    quark_born_reduced_numerator,
)


BornKind = Literal["quark", "gluon"]


@dataclass(frozen=True)
class ChannelSpec:
    name: str
    born_kind: BornKind
    raw_numerator: Expression
    metric_numerator: Expression
    manuscript_numerator: Expression
    splitting_kernel: Expression
    color_factor: Expression
    color_factor_su_n: Expression
    colored_splitting_kernel: Expression
    spin_factorization_factor: Expression
    phase_space_prefactor: Expression
    born: Expression
    ap_kernel_name: APKernelName
    ap_kernel: Expression
    ap_kernel_symbol: Expression
    ap_numerator: Expression


@dataclass(frozen=True)
class ChannelResult:
    spec: ChannelSpec
    manuscript_difference: Expression
    collinear_coefficient: Expression
    factorized_numerator: Expression
    virtuality_weight: Expression
    boundary_virtuality_weight: Expression
    ap_collinear_coefficient: Expression
    normalized_ap_numerator: Expression
    ap_factorized_numerator: Expression
    ap_virtuality_weight: Expression


def kernel_gq(kinematics: Kinematics) -> Expression:
    x = kinematics.x
    d = kinematics.d
    epsilon_d = (4 - d) / 2
    return canonical(2 * (1 - epsilon_d) * ap_qg_cdr(x, epsilon_d))


def kernel_qg(kinematics: Kinematics) -> Expression:
    x = kinematics.x
    d = kinematics.d
    return ap_gq_cdr(x, (4 - d) / 2)


def kernel_qq(kinematics: Kinematics) -> Expression:
    x = kinematics.x
    d = kinematics.d
    return ap_qq_cdr(x, (4 - d) / 2)


def kernel_gg(kinematics: Kinematics) -> Expression:
    x = kinematics.x
    d = kinematics.d
    return ap_gg_cdr(x, (4 - d) / 2)


def build_gq_channel(
    kinematics: Kinematics,
    tensors: TensorContext,
    colors: ColorContext,
) -> ChannelSpec:
    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2
    epsilon = kinematics.epsilon
    kernel = kernel_gq(kinematics)
    ap_kernel = ap_qg_cdr(x, epsilon)
    ap_symbol = ap_kernel_symbol("qg", x, epsilon)

    polarization_sum = gluon_parent_quark_born_numerator(
        tensors,
        kinematics,
    )
    raw = polarization_sum.massless_polarization_sum
    ap_numerator = (
        4 * cut_fraction * x**2 * p2
        + 2
        * (1 - epsilon)
        * transverse2
        * ap_symbol
        / cut_fraction
    )
    manuscript = polarization_sum.p_transverse_polarization_sum
    prefactor = 1 / (2 * cut_fraction * x**2 * p2)
    return ChannelSpec(
        name="D_gq",
        born_kind="quark",
        raw_numerator=canonical(raw),
        metric_numerator=canonical(polarization_sum.metric_term),
        manuscript_numerator=canonical(manuscript),
        splitting_kernel=kernel,
        color_factor=colors.tr,
        color_factor_su_n=colors.tr_su_n,
        colored_splitting_kernel=canonical(colors.tr * ap_kernel),
        # The parent-gluon average contributes 1/(d-2), while replacing
        # the hard-quark spin sum by the averaged Born contributes 2.
        spin_factorization_factor=canonical(2 / (kinematics.d - 2)),
        phase_space_prefactor=canonical(prefactor),
        born=kinematics.born_quark,
        ap_kernel_name="qg",
        ap_kernel=ap_kernel,
        ap_kernel_symbol=ap_symbol,
        ap_numerator=ap_numerator,
    )


def build_qg_channel(
    kinematics: Kinematics,
    tensors: TensorContext,
    colors: ColorContext,
) -> ChannelSpec:
    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    d = kinematics.d
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2
    epsilon = kinematics.epsilon
    kernel = kernel_qg(kinematics)
    ap_kernel = ap_gq_cdr(x, epsilon)
    ap_symbol = ap_kernel_symbol("gq", x, epsilon)
    tensor_result = gluon_born_reduced_numerator(tensors, kinematics)
    raw = tensor_result.reduced_numerator
    ap_numerator = (
        4 * (1 - epsilon) * cut_fraction * p2
        + 4 * transverse2 * ap_symbol / (x * cut_fraction)
    )

    # This is the first form printed on manuscript line 191.
    manuscript = (
        2 * (d - 2) * cut_fraction * p2
        + 2 * (d - 4) * transverse2 / cut_fraction
        + 4
        * (
            transverse2 / cut_fraction
            + transverse2 / x**2
        )
    )
    # A_g/(2 p_+.p_-) = x sigma(g). Include this flux ratio
    # before applying the common phase-space integration.
    prefactor = 1 / (2 * x * cut_fraction * p2)
    return ChannelSpec(
        name="D_qg",
        born_kind="gluon",
        raw_numerator=canonical(raw),
        metric_numerator=canonical(tensor_result.metric_term),
        manuscript_numerator=canonical(manuscript),
        splitting_kernel=kernel,
        color_factor=colors.cf,
        color_factor_su_n=colors.cf_su_n,
        colored_splitting_kernel=canonical(colors.cf * ap_kernel),
        # The gluon Born scalar is already polarization averaged, leaving
        # the incoming-quark helicity average.
        spin_factorization_factor=Expression.num(1) / 2,
        phase_space_prefactor=canonical(prefactor),
        born=kinematics.born_gluon,
        ap_kernel_name="gq",
        ap_kernel=ap_kernel,
        ap_kernel_symbol=ap_symbol,
        ap_numerator=ap_numerator,
    )


def build_qq_channel(
    kinematics: Kinematics,
    tensors: TensorContext,
    colors: ColorContext,
) -> ChannelSpec:
    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    d = kinematics.d
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2
    epsilon = kinematics.epsilon
    kernel = kernel_qq(kinematics)
    ap_kernel = ap_qq_cdr(x, epsilon)
    ap_symbol = ap_kernel_symbol("qq", x, epsilon)
    four_dimensional_kernel = (1 + x**2) / (2 * cut_fraction)
    tensor_result = quark_born_reduced_numerator(
        tensors,
        kinematics,
    )
    raw = tensor_result.reduced_numerator
    ap_numerator = (
        2 * (1 - epsilon) * x**2 * p2
        + 2 * transverse2 * ap_symbol / cut_fraction
    )
    manuscript = (
        -2 * (d - 2) * x**2 * p2
        + (d - 4) * transverse2
        + 4 * four_dimensional_kernel * transverse2 / cut_fraction
    )
    # The on-shell delta contributes the same factor 1/2 as in the other
    # channels. The parent and reduced hard quark averages cancel.
    prefactor = 1 / (2 * cut_fraction * x**2 * p2)
    return ChannelSpec(
        name="D_qq",
        born_kind="quark",
        raw_numerator=canonical(raw),
        metric_numerator=canonical(tensor_result.metric_term),
        manuscript_numerator=canonical(manuscript),
        splitting_kernel=kernel,
        color_factor=colors.cf,
        color_factor_su_n=colors.cf_su_n,
        colored_splitting_kernel=canonical(colors.cf * ap_kernel),
        spin_factorization_factor=Expression.num(1),
        phase_space_prefactor=canonical(prefactor),
        born=kinematics.born_quark,
        ap_kernel_name="qq",
        ap_kernel=ap_kernel,
        ap_kernel_symbol=ap_symbol,
        ap_numerator=ap_numerator,
    )


def build_gg_channel(
    kinematics: Kinematics,
    tensors: TensorContext,
    colors: ColorContext,
) -> ChannelSpec:
    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2
    epsilon = kinematics.epsilon
    ap_kernel = ap_gg_cdr(x, epsilon)
    ap_symbol = ap_kernel_symbol("gg", x, epsilon)
    tensor_result = gluon_self_splitting_numerator(tensors, kinematics)
    raw = tensor_result.reduced_numerator
    ap_numerator = 2 * transverse2 * ap_symbol / (x * cut_fraction)

    # The parent-gluon average and the conversion of the hard-gluon spin
    # contraction to the averaged Born cancel in the projected numerator.
    # The hard Born flux supplies one power of x to the common Jacobian.
    prefactor = 1 / (2 * x * cut_fraction * p2)
    return ChannelSpec(
        name="D_gg",
        born_kind="gluon",
        raw_numerator=canonical(raw),
        metric_numerator=canonical(tensor_result.metric_term),
        manuscript_numerator=canonical(raw),
        splitting_kernel=kernel_gg(kinematics),
        color_factor=colors.ca,
        color_factor_su_n=colors.ca_su_n,
        colored_splitting_kernel=canonical(colors.ca * ap_kernel),
        spin_factorization_factor=Expression.num(1),
        phase_space_prefactor=canonical(prefactor),
        born=kinematics.born_gluon,
        ap_kernel_name="gg",
        ap_kernel=ap_kernel,
        ap_kernel_symbol=ap_symbol,
        ap_numerator=ap_numerator,
    )


def derive_channel(
    spec: ChannelSpec,
    kinematics: Kinematics,
) -> ChannelResult:
    state_factor = spec.spin_factorization_factor
    leading = canonical(
        state_factor
        * spec.color_factor
        * collinear_coefficient(spec.raw_numerator, kinematics)
    )
    colored_ap_numerator = color_dress_ap_expression(
        spec.ap_numerator,
        spec.ap_kernel_name,
        kinematics.x,
        kinematics.epsilon,
        spec.color_factor,
    )
    normalized_ap_numerator = state_factor * colored_ap_numerator
    ap_leading = canonical(
        collinear_coefficient(normalized_ap_numerator, kinematics)
    )
    return ChannelResult(
        spec=spec,
        manuscript_difference=canonical(
            spec.raw_numerator - spec.manuscript_numerator
        ),
        collinear_coefficient=leading,
        factorized_numerator=canonical(
            state_factor
            * spec.color_factor
            * spec.raw_numerator
            * spec.born
        ),
        virtuality_weight=canonical(
            state_factor
            * spec.color_factor
            * spec.raw_numerator
            * spec.phase_space_prefactor
        ),
        boundary_virtuality_weight=canonical(
            state_factor
            * spec.color_factor
            * spec.metric_numerator
            * spec.phase_space_prefactor
        ),
        ap_collinear_coefficient=ap_leading,
        normalized_ap_numerator=normalized_ap_numerator,
        ap_factorized_numerator=(
            normalized_ap_numerator * spec.born
        ),
        ap_virtuality_weight=(
            normalized_ap_numerator * spec.phase_space_prefactor
        ),
    )
