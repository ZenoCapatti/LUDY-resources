from splitting_kernels.channels import kernel_gg, kernel_qg
from splitting_kernels.kinematics import assert_symbolic_equal, make_kinematics
from splitting_kernels.tensors import (
    gluon_parent_quark_born_numerator,
    gluon_born_reduced_numerator,
    gluon_self_splitting_numerator,
    gluon_virtual_self_energy_numerator,
    make_tensor_context,
    projector_checks,
    quark_born_reduced_numerator,
)


def test_axial_projector_identities() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)

    checks = projector_checks(tensors, kinematics)

    assert checks.momentum_transversality == 0
    assert checks.reference_transversality == 0
    assert checks.signed_idempotence == 0
    assert checks.polarization_trace == 0


def test_gluon_parent_polarization_sum_boundary_term() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    result = gluon_parent_quark_born_numerator(tensors, kinematics)
    x = kinematics.x
    d = kinematics.d
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2

    assert_symbolic_equal(
        result.metric_term,
        (d - 2) * transverse2 / (1 - x),
        "gluon-parent metric polarization piece",
    )
    assert_symbolic_equal(
        result.offshell_transverse_completion,
        -4 * (1 - x) * x**2 * p2,
        "off-shell transverse completion",
    )
    assert result.massless_residual == 0
    assert result.p_transverse_residual == 0
    assert_symbolic_equal(
        result.massless_polarization_sum
        - result.p_transverse_polarization_sum,
        4 * (1 - x) * x**2 * p2,
        "boundary term from projector convention",
    )


def test_gluon_born_trace_reproduces_corrected_numerator() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    x = kinematics.x
    d = kinematics.d
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2

    result = gluon_born_reduced_numerator(tensors, kinematics)
    expected = (
        2 * (d - 2) * (1 - x) * p2
        + 4
        * transverse2
        * kernel_qg(kinematics)
        / (x * (1 - x))
    )

    assert result.residual == 0
    assert_symbolic_equal(
        result.reduced_numerator,
        expected,
        "D_qg tensor trace",
    )


def test_quark_born_open_chain_derives_dqq_numerator() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    result = quark_born_reduced_numerator(tensors, kinematics)
    x = kinematics.x
    d = kinematics.d
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2

    assert_symbolic_equal(
        result.metric_term,
        (d - 2) * (x**2 * p2 + transverse2),
        "D_qq metric projector term",
    )
    assert_symbolic_equal(
        result.axial_mixed_terms,
        4 * x * transverse2 / (1 - x) ** 2,
        "D_qq axial mixed-projector terms",
    )
    assert result.residual == 0

    manuscript = (
        -2 * (d - 2) * x**2 * p2
        + (d - 4) * transverse2
        + 2
        * (1 + x**2)
        * transverse2
        / (1 - x) ** 2
    )
    assert_symbolic_equal(
        result.reduced_numerator - manuscript,
        3 * (d - 2) * x**2 * p2,
        "D_qq manuscript starting-numerator discrepancy",
    )


def test_line_191_difference_is_the_missing_projector_term() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    x = kinematics.x
    transverse2 = kinematics.transverse2
    d = kinematics.d
    p2 = kinematics.p2

    calculated = gluon_born_reduced_numerator(
        tensors,
        kinematics,
    ).reduced_numerator
    manuscript = (
        2 * (d - 2) * (1 - x) * p2
        + 2 * (d - 4) * transverse2 / (1 - x)
        + 4
        * (
            transverse2 / (1 - x)
            + transverse2 / x**2
        )
    )

    assert_symbolic_equal(
        calculated - manuscript,
        4 * transverse2 / x**2,
        "manuscript line 191 discrepancy",
    )


def test_three_gluon_vertices_derive_the_real_dgg_numerator() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    result = gluon_self_splitting_numerator(tensors, kinematics)
    x = kinematics.x

    assert result.residual == 0
    assert_symbolic_equal(
        result.reduced_numerator,
        2
        * kinematics.transverse2
        * kernel_gg(kinematics)
        / (x * (1 - x)),
        "real D_gg three-gluon numerator",
    )
    assert_symbolic_equal(
        result.reduced_numerator,
        result.metric_term + result.axial_terms,
        "real D_gg projector decomposition",
    )


def test_axial_gauge_gluon_self_energy_cuts_reproduce_cdr_kernels() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    result = gluon_virtual_self_energy_numerator(tensors, kinematics)

    assert result.gluon_residual == 0
    assert result.quark_residual == 0
    assert_symbolic_equal(
        result.gluon_loop_coefficient,
        2 * kinematics.p2 * kernel_gg(kinematics),
        "virtual gluon-bubble numerator",
    )
    assert_symbolic_equal(
        result.gluon_loop_coefficient,
        result.gluon_metric_term
        + result.gluon_mixed_term
        + result.gluon_completion_term,
        "virtual gluon projector decomposition",
    )
    assert_symbolic_equal(
        result.quark_loop_coefficient,
        result.quark_metric_term
        + result.quark_mixed_term
        + result.quark_completion_term,
        "virtual quark projector decomposition",
    )
