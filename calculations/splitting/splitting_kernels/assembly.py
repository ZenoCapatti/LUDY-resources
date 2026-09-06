"""Executable assembly of the NLO splitting counterterm matrix."""

from dataclasses import dataclass

from symbolica import Expression, S

from .colors import ColorContext
from .kinematics import (
    Kinematics,
    canonical,
    complement_momentum_fraction,
    set_dimension,
    symbols,
)
from .kernels import ap_gq_cdr, ap_gg_cdr, ap_qg_cdr, ap_qq_cdr
from .normalization import (
    PhaseSpaceNormalization,
    derive_phase_space_normalization,
)
from .phase_space import PhaseSpaceResult, integrate_unit_interval_beta
from .virtual import (
    GluonVirtualPhaseSpaceResult,
    VirtualPhaseSpaceResult,
    normalize_integer_trigamma,
)


@dataclass(frozen=True)
class DistributionalCheck:
    test_function: Expression
    derived_action: Expression
    formula_action: Expression
    powers: tuple[int, ...]
    derived_coefficients: tuple[Expression, ...]
    formula_coefficients: tuple[Expression, ...]
    residuals: tuple[Expression, ...]

    @property
    def passed(self) -> bool:
        return all(residual == 0 for residual in self.residuals)


@dataclass(frozen=True)
class NLOCountertermEntry:
    channel: str
    derived_real_integrand: Expression
    formula_real_integrand: Expression
    real_residual: Expression
    derived_virtual_integrand: Expression
    formula_virtual_integrand: Expression
    virtual_residual: Expression
    derived_counterterm: Expression
    formula_counterterm: Expression
    formula_residual: Expression
    distributional_check: DistributionalCheck

    @property
    def passed(self) -> bool:
        return all(
            residual == 0
            for residual in (
                self.real_residual,
                self.virtual_residual,
                self.formula_residual,
            )
        ) and self.distributional_check.passed


@dataclass(frozen=True)
class NLOCountertermAssembly:
    xi: Expression
    mu2: Expression
    integration_variable: Expression
    entries: tuple[NLOCountertermEntry, ...]
    derived_matrix: tuple[tuple[Expression, Expression], ...]
    formula_matrix: tuple[tuple[Expression, Expression], ...]
    residual_matrix: tuple[tuple[Expression, Expression], ...]
    normalization: PhaseSpaceNormalization

    @property
    def passed(self) -> bool:
        return self.normalization.passed and all(
            entry.passed for entry in self.entries
        )


def _formal_unit_interval_integral(
    integrand: Expression,
    variable: Expression,
) -> Expression:
    return S("Integral01")(canonical(integrand), variable)


def _normalized_weight(
    kinematics: Kinematics,
    normalization: PhaseSpaceNormalization,
) -> Expression:
    x = kinematics.x
    epsilon = kinematics.epsilon
    return canonical(
        normalization.normalized_prefactor
        * kinematics.cutoff2 ** (-epsilon)
        * x ** (-epsilon)
        * (1 - x) ** (-epsilon)
    )


def _distributional_test_function(
    channel: str,
    xi: Expression,
) -> Expression:
    test0, test1, test2, test3 = symbols(
        "test0",
        "test1",
        "test2",
        "test3",
    )
    if channel in ("D_gq", "D_gg"):
        # These entries contain a 1/x small-x singularity, so use smooth test
        # functions that vanish at x=0.
        return test1 * xi + test2 * xi**2 + test3 * xi**3
    return test0 + test1 * xi + test2 * xi**2


def _distributional_action(
    boundary: Expression,
    bulk_kernel: Expression,
    virtual_sum: Expression,
    test_function: Expression,
    xi: Expression,
    kinematics: Kinematics,
    normalization: PhaseSpaceNormalization,
) -> Expression:
    x = kinematics.x
    epsilon = kinematics.epsilon
    test_at_x = test_function.replace(xi, x)
    test_at_one = test_function.replace(xi, 1)
    endpoint_weight = x ** (-epsilon) * (1 - x) ** (-epsilon)
    common_scale = canonical(
        normalization.normalized_prefactor
        * kinematics.cutoff2 ** (-epsilon)
    )
    action_integrand = (
        common_scale
        * endpoint_weight
        * (
            test_at_x * (boundary + bulk_kernel / epsilon)
            - test_at_one * virtual_sum / (2 * epsilon)
        )
    )
    return integrate_unit_interval_beta(action_integrand, x)


def _laurent_coefficients(
    expression: Expression,
    epsilon: Expression,
    powers: tuple[int, ...],
) -> tuple[Expression, ...]:
    expansion = expression.series(epsilon, 0, 0)
    return tuple(
        normalize_integer_trigamma(
            canonical(expansion.get_coefficient(power).expand())
        )
        for power in powers
    )


def assemble_nlo_counterterm(
    phase_space_results: tuple[PhaseSpaceResult, ...],
    quark_virtual: VirtualPhaseSpaceResult,
    gluon_virtual: GluonVirtualPhaseSpaceResult,
    kinematics: Kinematics,
    colors: ColorContext,
) -> NLOCountertermAssembly:
    """Assemble the daughter-first D_ij matrix and compact flavor-sum formula.

    The first channel index is the daughter entering the hard interaction and
    the second is the parent parton represented by the PDF.

    The counterterm convention is
    ``D = -I_real_bulk + I_real_boundary + I_virtual``.  Since the raw radial
    bulk integral is ``-P/epsilon``, its contribution to ``D`` is
    ``+P/epsilon``.  The virtual self-energy retains its computed minus sign.
    """

    xi = S("xi")
    mu2 = kinematics.renormalization_scale2
    x = kinematics.x
    epsilon = kinematics.epsilon
    delta = kinematics.delta
    normalization = derive_phase_space_normalization(kinematics)
    weight = _normalized_weight(kinematics, normalization)
    phase_by_name = {
        result.channel.spec.name: result for result in phase_space_results
    }

    derived_real_data = {
        name: (
            result.boundary_coefficient,
            set_dimension(result.bulk_coefficient, kinematics),
        )
        for name, result in phase_by_name.items()
    }

    derived_quark_kernel = set_dimension(
        colors.cf
        * quark_virtual.numerator.leading_coefficient
        / (2 * kinematics.p2),
        kinematics,
    )
    derived_quark_complement = complement_momentum_fraction(
        derived_quark_kernel,
        kinematics,
    )
    derived_gluon_virtual_sum = set_dimension(
        colors.ca
        * gluon_virtual.numerator.gluon_loop_coefficient
        / (2 * kinematics.p2)
        + 2
        * colors.nf
        * colors.tr
        * gluon_virtual.numerator.quark_loop_coefficient
        / (2 * kinematics.p2),
        kinematics,
    )
    derived_virtual_data = {
        "D_gq": Expression.num(0),
        "D_qg": Expression.num(0),
        "D_qq": canonical(derived_quark_kernel + derived_quark_complement),
        "D_gg": derived_gluon_virtual_sum,
    }

    formula_data = {
        "D_qg": (
            colors.tr,
            ap_qg_cdr(x, epsilon),
            Expression.num(1),
            Expression.num(0),
        ),
        "D_gq": (
            colors.cf,
            ap_gq_cdr(x, epsilon),
            1 - epsilon,
            Expression.num(0),
        ),
        "D_qq": (
            colors.cf,
            ap_qq_cdr(x, epsilon),
            1 - epsilon,
            colors.cf
            * (ap_qq_cdr(x, epsilon) + ap_gq_cdr(x, epsilon)),
        ),
        "D_gg": (
            colors.ca,
            ap_gg_cdr(x, epsilon),
            -3 * (3 - 2 * epsilon) / (4 * (1 - epsilon)),
            colors.ca * ap_gg_cdr(x, epsilon)
            + 2 * colors.nf * colors.tr * ap_qg_cdr(x, epsilon),
        ),
    }

    entries = []
    for channel in ("D_qg", "D_gq", "D_qq", "D_gg"):
        boundary, bulk_kernel = derived_real_data[channel]
        derived_real = canonical(
            weight
            * delta(xi - x)
            * (boundary + bulk_kernel / epsilon)
        )
        derived_virtual_sum = derived_virtual_data[channel]
        derived_virtual = canonical(
            -weight
            * delta(1 - xi)
            * derived_virtual_sum
            / (2 * epsilon)
        )

        color, stripped_kernel, stripped_boundary, formula_virtual_sum = (
            formula_data[channel]
        )
        formula_real = canonical(
            weight
            * delta(xi - x)
            * color
            * (stripped_boundary + stripped_kernel / epsilon)
        )
        formula_virtual = canonical(
            -weight
            * delta(1 - xi)
            * formula_virtual_sum
            / (2 * epsilon)
        )

        test_function = _distributional_test_function(channel, xi)
        derived_action = _distributional_action(
            boundary,
            bulk_kernel,
            derived_virtual_sum,
            test_function,
            xi,
            kinematics,
            normalization,
        )
        formula_action = _distributional_action(
            color * stripped_boundary,
            color * stripped_kernel,
            formula_virtual_sum,
            test_function,
            xi,
            kinematics,
            normalization,
        )
        laurent_powers = (-2, -1, 0)
        derived_coefficients = _laurent_coefficients(
            derived_action,
            epsilon,
            laurent_powers,
        )
        formula_coefficients = _laurent_coefficients(
            formula_action,
            epsilon,
            laurent_powers,
        )
        distributional_check = DistributionalCheck(
            test_function=test_function,
            derived_action=derived_action,
            formula_action=formula_action,
            powers=laurent_powers,
            derived_coefficients=derived_coefficients,
            formula_coefficients=formula_coefficients,
            residuals=tuple(
                canonical(derived - formula)
                for derived, formula in zip(
                    derived_coefficients,
                    formula_coefficients,
                )
            ),
        )

        derived_counterterm = _formal_unit_interval_integral(
            derived_real + derived_virtual,
            x,
        )
        formula_counterterm = _formal_unit_interval_integral(
            formula_real + formula_virtual,
            x,
        )
        entries.append(
            NLOCountertermEntry(
                channel=channel,
                derived_real_integrand=derived_real,
                formula_real_integrand=formula_real,
                real_residual=canonical(derived_real - formula_real),
                derived_virtual_integrand=derived_virtual,
                formula_virtual_integrand=formula_virtual,
                virtual_residual=canonical(
                    derived_virtual - formula_virtual
                ),
                derived_counterterm=derived_counterterm,
                formula_counterterm=formula_counterterm,
                formula_residual=canonical(
                    derived_counterterm - formula_counterterm
                ),
                distributional_check=distributional_check,
            )
        )

    by_name = {entry.channel: entry for entry in entries}
    derived_matrix = (
        (
            by_name["D_qq"].derived_counterterm,
            by_name["D_qg"].derived_counterterm,
        ),
        (
            by_name["D_gq"].derived_counterterm,
            by_name["D_gg"].derived_counterterm,
        ),
    )
    formula_matrix = (
        (
            by_name["D_qq"].formula_counterterm,
            by_name["D_qg"].formula_counterterm,
        ),
        (
            by_name["D_gq"].formula_counterterm,
            by_name["D_gg"].formula_counterterm,
        ),
    )
    residual_matrix = tuple(
        (
            canonical(row[0] - other[0]),
            canonical(row[1] - other[1]),
        )
        for row, other in zip(derived_matrix, formula_matrix)
    )
    return NLOCountertermAssembly(
        xi=xi,
        mu2=mu2,
        integration_variable=x,
        entries=tuple(entries),
        derived_matrix=derived_matrix,
        formula_matrix=formula_matrix,
        residual_matrix=residual_matrix,
        normalization=normalization,
    )
