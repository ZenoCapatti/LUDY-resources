"""Tests for the Ward-completion hypothesis for the D_qq cutoff surface."""

from symbolica import Expression

from splitting_kernels.channels import (
    build_gq_channel,
    build_qq_channel,
    derive_channel,
)
from splitting_kernels.colors import make_color_context
from splitting_kernels.kinematics import (
    assert_symbolic_equal,
    canonical,
    make_kinematics,
    set_dimension,
)
from splitting_kernels.kernels import ap_qq_cdr
from splitting_kernels.phase_space import (
    integrate_delta_prime_bulk,
    integrate_channel_phase_space,
    transverse_boundary_coefficient,
)
from splitting_kernels.tensors import (
    make_tensor_context,
    quark_born_reduced_numerator,
)


def test_axial_mixed_projector_is_bulk_contact_plus_cutoff_derivative() -> None:
    """The disputed surface is the total-derivative part of the axial term.

    For w(p^2) multiplying delta'(p^2-p_0^2),

        w delta' = d(w delta)/d p^2 - w' delta.

    The second term is the interior contact contribution.  The first term has
    no interior support after integration and contributes only at the cutoff.
    """

    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    colors = make_color_context()
    numerator = quark_born_reduced_numerator(tensors, kinematics)
    channel = build_qq_channel(kinematics, tensors, colors)

    metric_weight = canonical(
        colors.cf
        * numerator.metric_term
        * channel.phase_space_prefactor
    )
    mixed_weight = canonical(
        colors.cf
        * numerator.axial_mixed_terms
        * channel.phase_space_prefactor
    )

    metric_surface = set_dimension(
        transverse_boundary_coefficient(metric_weight, kinematics),
        kinematics,
    )
    mixed_surface = set_dimension(
        transverse_boundary_coefficient(mixed_weight, kinematics),
        kinematics,
    )
    assert_symbolic_equal(
        metric_surface,
        colors.cf * (1 - kinematics.epsilon),
        "D_qq metric cutoff surface",
    )
    assert_symbolic_equal(
        mixed_surface,
        2 * colors.cf * kinematics.x / (1 - kinematics.x),
        "D_qq axial mixed cutoff surface",
    )

    # The contact term -w'(p_0^2) delta(p^2-p_0^2) is exactly the
    # fixed-x bulk obtained by integrating the delta-prime in the interior.
    support = kinematics.theta(
        kinematics.cutoff2 - kinematics.virtuality_root
    )
    contact_density = canonical(
        -mixed_weight.derivative(kinematics.p2).replace(
            kinematics.p2,
            kinematics.virtuality_root,
        )
        * support
    )
    mixed_bulk_density = integrate_delta_prime_bulk(
        mixed_weight,
        kinematics,
    )
    metric_bulk_density = integrate_delta_prime_bulk(
        metric_weight,
        kinematics,
    )
    assert_symbolic_equal(
        contact_density,
        mixed_bulk_density,
        "D_qq axial mixed contact equals its AP bulk",
    )

    eikonal_bulk_coefficient = canonical(
        kinematics.transverse2
        * mixed_bulk_density.replace(support, Expression.num(1))
    )
    assert_symbolic_equal(
        eikonal_bulk_coefficient,
        2 * colors.cf * kinematics.x / (1 - kinematics.x),
        "D_qq axial mixed contact is the eikonal AP kernel",
    )
    assert_symbolic_equal(
        mixed_surface,
        eikonal_bulk_coefficient,
        "D_qq disputed surface is the mixed total-derivative coefficient",
    )

    metric_bulk_coefficient = canonical(
        kinematics.transverse2
        * metric_bulk_density.replace(support, Expression.num(1))
    )
    assert_symbolic_equal(
        set_dimension(metric_bulk_coefficient, kinematics),
        colors.cf
        * (1 - kinematics.epsilon)
        * (1 - kinematics.x),
        "D_qq Feynman-gauge squared graph gives the regular AP bulk",
    )
    assert_symbolic_equal(
        set_dimension(metric_bulk_coefficient, kinematics)
        + eikonal_bulk_coefficient,
        colors.cf
        * ap_qq_cdr(kinematics.x, kinematics.epsilon),
        "D_qq regular and eikonal pieces reconstruct the full AP bulk",
    )

    # A Ward-completing contribution -d(w delta)/d p^2 removes the mixed
    # surface without changing the interior contact term.
    ward_completed_surface = canonical(
        metric_surface + mixed_surface - eikonal_bulk_coefficient
    )
    assert_symbolic_equal(
        ward_completed_surface,
        colors.cf * (1 - kinematics.epsilon),
        "D_qq Ward-completed cutoff surface",
    )


def test_phase_space_keeps_only_metric_surface_for_quark_channels() -> None:
    """The crossed q -> qg assignments use only the metric surface."""

    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    colors = make_color_context()
    qq = integrate_channel_phase_space(
        derive_channel(
            build_qq_channel(kinematics, tensors, colors),
            kinematics,
        ),
        kinematics,
    )
    gq = integrate_channel_phase_space(
        derive_channel(
            build_gq_channel(kinematics, tensors, colors),
            kinematics,
        ),
        kinematics,
    )

    regular_surface = colors.cf * (1 - kinematics.epsilon)
    assert_symbolic_equal(
        qq.boundary_coefficient,
        regular_surface,
        "D_qq metric surface",
    )
    assert_symbolic_equal(
        gq.boundary_coefficient,
        regular_surface,
        "D_gq metric surface",
    )
