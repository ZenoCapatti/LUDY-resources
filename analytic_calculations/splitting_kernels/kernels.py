"""Unregularized, spin-averaged Altarelli-Parisi kernels in CDR."""

from typing import Literal

from symbolica import Expression, S

from .kinematics import canonical


APKernelName = Literal["qq", "gq", "qg", "gg"]


def ap_qq_cdr(z: Expression, epsilon: Expression) -> Expression:
    """Color-stripped q <- q kernel, P_qq / C_F."""

    return canonical((1 + z**2) / (1 - z) - epsilon * (1 - z))


def ap_gq_cdr(z: Expression, epsilon: Expression) -> Expression:
    """Color-stripped g <- q kernel, P_gq / C_F."""

    return canonical((1 + (1 - z) ** 2) / z - epsilon * z)


def ap_qg_cdr(z: Expression, epsilon: Expression) -> Expression:
    """Color-stripped q <- g kernel, P_qg / T_R."""

    return canonical(
        (z**2 + (1 - z) ** 2 - epsilon) / (1 - epsilon)
    )


def ap_gg_cdr(z: Expression, epsilon: Expression) -> Expression:
    """Color-stripped g <- g kernel, P_gg / C_A."""

    del epsilon
    return canonical(
        2 * (z / (1 - z) + (1 - z) / z + z * (1 - z))
    )


def ap_kernel_cdr(
    name: APKernelName,
    z: Expression,
    epsilon: Expression,
) -> Expression:
    """Return a color-stripped CDR kernel using DGLAP index ordering."""

    if name == "qq":
        return ap_qq_cdr(z, epsilon)
    if name == "gq":
        return ap_gq_cdr(z, epsilon)
    if name == "qg":
        return ap_qg_cdr(z, epsilon)
    return ap_gg_cdr(z, epsilon)


def ap_kernel_symbol(
    name: APKernelName,
    z: Expression,
    epsilon: Expression,
) -> Expression:
    """Symbolica function atom used for compact, verified expressions."""

    return S(f"p{name}CDR")(z, epsilon)


def cdr_kernel_symbol(
    name: APKernelName,
    z: Expression,
    epsilon: Expression,
) -> Expression:
    """Color-dressed CDR kernel atom in DGLAP index ordering."""

    return S(f"P{name}CDR")(z, epsilon)


def expand_ap_kernel(
    expression: Expression,
    name: APKernelName,
    z: Expression,
    epsilon: Expression,
) -> Expression:
    """Expand one compact AP function atom using Symbolica replacement."""

    return canonical(
        expression.replace(
            ap_kernel_symbol(name, z, epsilon),
            ap_kernel_cdr(name, z, epsilon),
        )
    )


def expand_cdr_kernel(
    expression: Expression,
    name: APKernelName,
    z: Expression,
    epsilon: Expression,
    color_factor: Expression,
) -> Expression:
    """Expand one color-dressed CDR kernel atom using Symbolica."""

    return canonical(
        expression.replace(
            cdr_kernel_symbol(name, z, epsilon),
            color_factor * ap_kernel_cdr(name, z, epsilon),
        )
    )


def color_dress_ap_expression(
    expression: Expression,
    name: APKernelName,
    z: Expression,
    epsilon: Expression,
    color_factor: Expression,
) -> Expression:
    """Replace a color-stripped AP atom by the full CDR kernel.

    The regular and kernel-proportional pieces are separated with Symbolica
    before the color factor is applied. This keeps the full kernel compact
    without introducing a spurious ``P/C`` ratio in displayed expressions.
    """

    stripped_kernel = ap_kernel_symbol(name, z, epsilon)
    kernel_coefficient = expression.expand().coefficient(stripped_kernel)
    regular_part = expression.replace(stripped_kernel, 0)
    return (
        color_factor * regular_part
        + kernel_coefficient * cdr_kernel_symbol(name, z, epsilon)
    )
