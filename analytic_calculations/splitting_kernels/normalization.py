"""Explicit normalization from cut loop measure to the ``a_s`` convention."""

from dataclasses import dataclass

from symbolica import Expression

from .kinematics import Kinematics, canonical


@dataclass(frozen=True)
class PhaseSpaceNormalization:
    loop_measure: Expression
    cut_delta_factors: Expression
    virtuality_measure: Expression
    coupling_per_as: Expression
    transverse_solid_angle: Expression
    msbar_scale: Expression
    factorized_prefactor: Expression
    normalized_prefactor: Expression
    residual: Expression

    @property
    def passed(self) -> bool:
        return self.residual == 0


def derive_phase_space_normalization(
    kinematics: Kinematics,
    mu2: Expression | None = None,
) -> PhaseSpaceNormalization:
    """Restore every common factor suppressed in the stripped integrals.

    The virtuality integral is a dispersive integral ``dp^2/(2*pi)``.  Each
    cut propagator supplies ``2*pi*delta_+``.  With
    ``a_s = alpha_s/(2*pi)``, ``g_s^2/a_s = 8*pi^2``.  The MS-bar scale
    convention used here is ``(exp(gamma_E)*mu^2/(4*pi))^epsilon``.
    """

    epsilon = kinematics.epsilon
    if mu2 is None:
        mu2 = kinematics.renormalization_scale2
    pi = Expression.PI
    gamma_e = Expression.EULER_GAMMA

    loop_measure = 1 / (2 * pi) ** kinematics.d
    cut_delta_factors = (2 * pi) ** 2
    virtuality_measure = 1 / (2 * pi)
    coupling_per_as = 8 * pi**2
    transverse_solid_angle = (
        pi ** (1 - epsilon) / Expression.GAMMA(1 - epsilon)
    )
    msbar_scale = (
        Expression.EXP(gamma_e) * mu2 / (4 * pi)
    ) ** epsilon

    # Write the same factors over the independent bases 2 and pi so that
    # Symbolica can cancel their symbolic powers exactly after d=4-2 epsilon.
    expanded_loop_measure = 2 ** (-4 + 2 * epsilon) * pi ** (
        -4 + 2 * epsilon
    )
    expanded_msbar_scale = (
        Expression.EXP(gamma_e * epsilon)
        * mu2**epsilon
        * 2 ** (-2 * epsilon)
        * pi ** (-epsilon)
    )
    factorized_prefactor = canonical(
        expanded_loop_measure
        * cut_delta_factors
        * virtuality_measure
        * coupling_per_as
        * transverse_solid_angle
        * expanded_msbar_scale
    )
    normalized_prefactor = canonical(
        Expression.EXP(gamma_e * epsilon)
        * mu2**epsilon
        / Expression.GAMMA(1 - epsilon)
    )
    return PhaseSpaceNormalization(
        loop_measure=loop_measure,
        cut_delta_factors=cut_delta_factors,
        virtuality_measure=virtuality_measure,
        coupling_per_as=coupling_per_as,
        transverse_solid_angle=transverse_solid_angle,
        msbar_scale=msbar_scale,
        factorized_prefactor=factorized_prefactor,
        normalized_prefactor=normalized_prefactor,
        residual=canonical(factorized_prefactor - normalized_prefactor),
    )
