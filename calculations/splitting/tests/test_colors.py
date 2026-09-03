from splitting_kernels.colors import make_color_context
from splitting_kernels.kinematics import assert_symbolic_equal


def test_idenso_reduces_qcd_color_contractions() -> None:
    colors = make_color_context()

    for reduction in (
        colors.quark_emission,
        colors.gluon_to_quarks,
        colors.gluon_emission,
    ):
        assert reduction.residual == 0
        assert_symbolic_equal(
            reduction.labeled_reduction,
            reduction.conventional_label * reduction.identity_tensor,
            "labeled color reduction",
        )


def test_standard_su_n_color_values() -> None:
    colors = make_color_context()

    assert_symbolic_equal(
        colors.cf_su_n,
        (colors.nc**2 - 1) / (2 * colors.nc),
        "fundamental Casimir",
    )
    assert_symbolic_equal(colors.ca_su_n, colors.nc, "adjoint Casimir")
    assert_symbolic_equal(colors.tr_su_n, colors.nc / (2 * colors.nc), "index")
    assert_symbolic_equal(
        colors.cf_su_n * colors.nc,
        colors.tr_su_n * (colors.nc**2 - 1),
        "C_F N_c = T_R N_A",
    )
