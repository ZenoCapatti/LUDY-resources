from symbolica import Expression, S

from splitting_kernels.kinematics import (
    assert_symbolic_equal,
    make_kinematics,
)
from splitting_kernels.normalization import derive_phase_space_normalization


def test_cut_loop_factors_reproduce_the_normalized_weight() -> None:
    kinematics = make_kinematics()
    mu2 = S("mu2")
    epsilon = kinematics.epsilon
    normalization = derive_phase_space_normalization(kinematics, mu2)

    assert normalization.passed
    assert normalization.residual == 0
    assert_symbolic_equal(
        normalization.coupling_per_as,
        8 * Expression.PI**2,
        "g_s^2/a_s for a_s=alpha_s/(2*pi)",
    )
    assert_symbolic_equal(
        normalization.msbar_scale,
        (
            Expression.EXP(Expression.EULER_GAMMA)
            * mu2
            / (4 * Expression.PI)
        )
        ** epsilon,
        "MS-bar scale factor",
    )


def test_virtuality_spectral_measure_removes_the_last_two_pi() -> None:
    kinematics = make_kinematics()
    normalization = derive_phase_space_normalization(
        kinematics,
        S("mu2"),
    )

    assert_symbolic_equal(
        normalization.factorized_prefactor
        / normalization.virtuality_measure,
        2 * Expression.PI * normalization.normalized_prefactor,
        "normalization without dp^2/(2*pi)",
    )
