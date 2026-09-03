from symbolica import Expression

from splitting_kernels.kinematics import (
    assert_symbolic_equal,
    collinear_coefficient,
    complement_momentum_fraction,
    make_kinematics,
    symbols,
)


def test_sudakov_identities_are_symbolica_expressions() -> None:
    kinematics = make_kinematics()

    assert isinstance(kinematics.alpha, Expression)
    assert isinstance(kinematics.p_dot_k, Expression)
    assert isinstance(kinematics.reduced_virtuality, Expression)
    assert isinstance(kinematics.renormalization_scale2, Expression)
    assert_symbolic_equal(
        kinematics.cut_fraction,
        1 - kinematics.x,
        "cut momentum fraction",
    )
    assert_symbolic_equal(
        kinematics.alpha,
        kinematics.transverse2
        / (
            2
            * (1 - kinematics.x)
            * kinematics.lightcone_dot
        ),
        "cut on-shell Sudakov coefficient",
    )
    assert_symbolic_equal(
        kinematics.p_dot_k,
        (1 - kinematics.x) * kinematics.p2 / 2
        + kinematics.transverse2 / (2 * (1 - kinematics.x)),
        "parent-cut scalar product",
    )
    assert_symbolic_equal(
        kinematics.reduced_virtuality,
        kinematics.x * kinematics.p2
        - kinematics.transverse2 / (1 - kinematics.x),
        "hard-daughter virtuality",
    )
    assert_symbolic_equal(
        kinematics.virtuality_root,
        kinematics.transverse2
        / (kinematics.x * (1 - kinematics.x)),
        "virtuality root",
    )
    sigma, quark, gluon = symbols("sigma", "q", "g")
    assert kinematics.born_quark == sigma(quark)
    assert kinematics.born_gluon == sigma(gluon)


def test_joint_collinear_scaling_keeps_p2_and_transverse2_together() -> None:
    kinematics = make_kinematics()
    expression = 3 * kinematics.p2 + 5 * kinematics.transverse2

    coefficient = collinear_coefficient(expression, kinematics)

    assert_symbolic_equal(
        coefficient,
        expression,
        "joint collinear coefficient",
    )


def test_complement_substitution_is_simultaneous() -> None:
    kinematics = make_kinematics()
    expression = kinematics.x**2 + kinematics.x

    complemented = complement_momentum_fraction(expression, kinematics)

    assert_symbolic_equal(
        complemented,
        (1 - kinematics.x) ** 2 + (1 - kinematics.x),
        "x complement",
    )
