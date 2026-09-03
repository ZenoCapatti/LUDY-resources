from symbolica import Expression

from splitting_kernels.channels import kernel_qq
from splitting_kernels.colors import make_color_context
from splitting_kernels.kinematics import assert_symbolic_equal, make_kinematics
from splitting_kernels.tensors import (
    make_tensor_context,
    virtual_self_energy_numerator,
)
from splitting_kernels.virtual import (
    integrate_gluon_virtual_self_energy,
    integrate_virtual_self_energy,
)


def test_virtual_numerator_is_derived_from_the_tensor_trace() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    result = virtual_self_energy_numerator(tensors, kinematics)
    x = kinematics.x
    d = kinematics.d
    p2 = kinematics.p2

    assert_symbolic_equal(
        result.metric_term,
        (1 - x) * (d - 2) * p2,
        "virtual metric term",
    )
    assert_symbolic_equal(
        result.mixed_terms,
        4 * x * p2 / (1 - x),
        "virtual mixed axial-gauge terms",
    )
    assert result.gauge_norm_term == 0
    assert result.residual == 0
    assert_symbolic_equal(
        result.leading_coefficient,
        2 * kernel_qq(kinematics) * p2,
        "virtual splitting kernel",
    )


def test_virtual_beta_integral_reproduces_the_manuscript_poles() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    colors = make_color_context()
    result = integrate_virtual_self_energy(tensors, kinematics, colors)
    epsilon = kinematics.epsilon
    expected = colors.cf * (
        2 / epsilon**2
        + 3 / (2 * epsilon)
        + (7 - Expression.PI**2) / 2
    )

    assert_symbolic_equal(
        result.epsilon_expansion,
        expected,
        "virtual epsilon expansion",
    )
    assert_symbolic_equal(
        result.full_counterterm,
        kinematics.delta(1 - kinematics.x)
        * (
            kinematics.cutoff2 / kinematics.renormalization_scale2
        )
        ** (-epsilon)
        * expected
        * kinematics.born_quark,
        "normalized virtual D_qq counterterm",
    )


def test_manuscript_line_322_is_still_zero_after_coordinate_change() -> None:
    kinematics = make_kinematics()
    x = kinematics.x

    assert_symbolic_equal(
        -2 / (1 - x) + 2 + 2 * x / (1 - x),
        0,
        "line 322 left-hand side after x_old -> 1-x",
    )


def test_complete_gluon_self_energy_has_cdr_poles_and_finite_part() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    colors = make_color_context()
    result = integrate_gluon_virtual_self_energy(
        tensors,
        kinematics,
        colors,
    )
    epsilon = kinematics.epsilon
    expected = (
        2 * colors.ca / epsilon**2
        + (11 * colors.ca - 4 * colors.tr * colors.nf)
        / (6 * epsilon)
        + colors.ca * (67 - 9 * Expression.PI**2) / 18
        - 10 * colors.tr * colors.nf / 9
    )

    assert result.numerator.gluon_residual == 0
    assert result.numerator.quark_residual == 0
    assert_symbolic_equal(
        result.epsilon_expansion,
        expected,
        "complete virtual D_gg epsilon expansion",
    )
    assert_symbolic_equal(
        result.full_counterterm,
        kinematics.delta(1 - kinematics.x)
        * (
            kinematics.cutoff2 / kinematics.renormalization_scale2
        )
        ** (-epsilon)
        * expected
        * kinematics.born_gluon,
        "normalized virtual D_gg counterterm",
    )
