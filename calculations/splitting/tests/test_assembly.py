from symbolica import Expression, S

from splitting_kernels.assembly import assemble_nlo_counterterm
from splitting_kernels.channels import (
    build_gq_channel,
    build_gg_channel,
    build_qg_channel,
    build_qq_channel,
    derive_channel,
)
from splitting_kernels.colors import make_color_context
from splitting_kernels.kinematics import assert_symbolic_equal, make_kinematics
from splitting_kernels.phase_space import (
    integrate_channel_phase_space,
    integrate_unit_interval_beta,
)
from splitting_kernels.tensors import make_tensor_context
from splitting_kernels.virtual import (
    integrate_gluon_virtual_self_energy,
    integrate_virtual_self_energy,
)


def test_beta_monomials_are_integrated_by_expression_replacement() -> None:
    x, epsilon = S("x", "epsilon")
    integrand = (
        3 * x ** (1 - epsilon) * (1 - x) ** (-1 - epsilon)
        - 2 * x ** (-epsilon) * (1 - x) ** (2 - epsilon)
    )
    expected = (
        3
        * Expression.GAMMA(2 - epsilon)
        * Expression.GAMMA(-epsilon)
        / Expression.GAMMA(2 - 2 * epsilon)
        - 2
        * Expression.GAMMA(1 - epsilon)
        * Expression.GAMMA(3 - epsilon)
        / Expression.GAMMA(4 - 2 * epsilon)
    )

    assert_symbolic_equal(
        integrate_unit_interval_beta(integrand, x),
        expected,
        "unit-interval beta replacement",
    )


def test_assembled_counterterm_matches_compact_formula_entry_by_entry() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    colors = make_color_context()
    specs = (
        build_gq_channel(kinematics, tensors, colors),
        build_qg_channel(kinematics, tensors, colors),
        build_qq_channel(kinematics, tensors, colors),
        build_gg_channel(kinematics, tensors, colors),
    )
    channels = tuple(derive_channel(spec, kinematics) for spec in specs)
    phase_space = tuple(
        integrate_channel_phase_space(channel, kinematics)
        for channel in channels
    )
    quark_virtual = integrate_virtual_self_energy(
        tensors,
        kinematics,
        colors,
    )
    gluon_virtual = integrate_gluon_virtual_self_energy(
        tensors,
        kinematics,
        colors,
    )

    assembly = assemble_nlo_counterterm(
        phase_space,
        quark_virtual,
        gluon_virtual,
        kinematics,
        colors,
    )

    assert assembly.passed
    assert tuple(entry.channel for entry in assembly.entries) == (
        "D_gq",
        "D_qg",
        "D_qq",
        "D_gg",
    )
    assert assembly.residual_matrix == ((0, 0), (0, 0))
    for entry in assembly.entries:
        assert entry.real_residual == 0
        assert entry.virtual_residual == 0
        assert entry.formula_residual == 0
        assert entry.distributional_check.passed
        assert entry.distributional_check.residuals == (0, 0, 0)

    test1, test2 = S("test1", "test2")
    qq_check = next(
        entry.distributional_check
        for entry in assembly.entries
        if entry.channel == "D_qq"
    )
    assert qq_check.derived_coefficients[0] == 0
    assert_symbolic_equal(
        qq_check.derived_coefficients[1],
        -colors.cf * (16 * test1 + 25 * test2) / 12,
        "D_qq plus-distribution action at order 1/epsilon",
    )
