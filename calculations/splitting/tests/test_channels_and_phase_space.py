from symbolica import Expression

from splitting_kernels.channels import (
    build_gq_channel,
    build_gg_channel,
    build_qg_channel,
    build_qq_channel,
    derive_channel,
    kernel_gq,
    kernel_gg,
    kernel_qg,
    kernel_qq,
)
from splitting_kernels.colors import make_color_context
from splitting_kernels.kinematics import (
    assert_symbolic_equal,
    complement_momentum_fraction,
    make_kinematics,
    set_dimension,
)
from splitting_kernels.kernels import (
    ap_gq_cdr,
    ap_gg_cdr,
    ap_qg_cdr,
    ap_qq_cdr,
    cdr_kernel_symbol,
    expand_ap_kernel,
    expand_cdr_kernel,
)
from splitting_kernels.normalization import derive_phase_space_normalization
from splitting_kernels.phase_space import (
    epsilon_series,
    integrate_channel_phase_space,
)
from splitting_kernels.tensors import make_tensor_context


def _results():
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
    return kinematics, channels, phase_space


def test_all_channels_factorize_their_declared_black_box_born() -> None:
    kinematics, channels, _ = _results()

    for channel in channels:
        assert_symbolic_equal(
            channel.factorized_numerator,
            channel.spec.spin_factorization_factor
            * channel.spec.color_factor
            * channel.spec.raw_numerator
            * channel.spec.born,
            f"{channel.spec.name} Born factorization",
        )
        assert_symbolic_equal(
            channel.boundary_virtuality_weight,
            channel.spec.spin_factorization_factor
            * channel.spec.color_factor
            * channel.spec.metric_numerator
            * channel.spec.phase_space_prefactor,
            f"{channel.spec.name} metric-only boundary weight",
        )
        assert channel.spec.born in (
            kinematics.born_quark,
            kinematics.born_gluon,
        )


def test_all_channels_use_the_reduced_color_factors() -> None:
    _, channels, _ = _results()
    colors = make_color_context()
    by_name = {channel.spec.name: channel.spec for channel in channels}

    assert_symbolic_equal(by_name["D_gq"].color_factor, colors.tr, "g -> qqbar")
    assert_symbolic_equal(by_name["D_qg"].color_factor, colors.cf, "q -> gq")
    assert_symbolic_equal(by_name["D_qq"].color_factor, colors.cf, "q -> qg")
    assert_symbolic_equal(by_name["D_gg"].color_factor, colors.ca, "g -> gg")
    for spec in by_name.values():
        assert_symbolic_equal(
            spec.colored_splitting_kernel,
            spec.color_factor * spec.ap_kernel,
            f"{spec.name} color-dressed splitting kernel",
        )


def test_initial_state_spin_averages_are_explicit() -> None:
    kinematics, channels, _ = _results()
    by_name = {channel.spec.name: channel.spec for channel in channels}

    assert_symbolic_equal(
        set_dimension(
            by_name["D_gq"].spin_factorization_factor,
            kinematics,
        ),
        1 / (1 - kinematics.epsilon),
        "gluon-parent to quark-Born spin normalization",
    )
    assert_symbolic_equal(
        by_name["D_qg"].spin_factorization_factor,
        Expression.num(1) / 2,
        "incoming-quark helicity average",
    )
    assert_symbolic_equal(
        by_name["D_qq"].spin_factorization_factor,
        1,
        "quark-parent and quark-Born spin averages cancel",
    )
    assert_symbolic_equal(
        by_name["D_qq"].phase_space_prefactor,
        by_name["D_gq"].phase_space_prefactor,
        "common on-shell and delta-prime Jacobians",
    )
    assert_symbolic_equal(
        by_name["D_gg"].spin_factorization_factor,
        1,
        "gluon-parent and gluon-Born spin averages cancel",
    )
    assert_symbolic_equal(
        by_name["D_qg"].phase_space_prefactor,
        kinematics.x * by_name["D_gq"].phase_space_prefactor,
        "gluon-Born flux conversion",
    )


def test_delta_prime_bulk_coefficients() -> None:
    kinematics, _, phase_space = _results()
    x = kinematics.x
    transverse2 = kinematics.transverse2
    by_name = {
        result.channel.spec.name: result
        for result in phase_space
    }

    assert_symbolic_equal(
        set_dimension(by_name["D_gq"].bulk_coefficient, kinematics),
        by_name["D_gq"].channel.spec.color_factor
        * ap_qg_cdr(x, kinematics.epsilon),
        "D_gq bulk coefficient",
    )
    assert_symbolic_equal(
        set_dimension(by_name["D_qg"].bulk_coefficient, kinematics),
        by_name["D_qg"].channel.spec.color_factor
        * ap_gq_cdr(x, kinematics.epsilon),
        "D_qg bulk coefficient",
    )
    assert_symbolic_equal(
        set_dimension(by_name["D_qq"].bulk_coefficient, kinematics),
        by_name["D_qq"].channel.spec.color_factor
        * ap_qq_cdr(x, kinematics.epsilon),
        "D_qq bulk coefficient",
    )
    assert_symbolic_equal(
        set_dimension(by_name["D_gg"].bulk_coefficient, kinematics),
        by_name["D_gg"].channel.spec.color_factor
        * ap_gg_cdr(x, kinematics.epsilon),
        "D_gg bulk coefficient",
    )

    for result in phase_space:
        density_without_support = result.bulk_density.replace(
            kinematics.theta(
                kinematics.cutoff2 - kinematics.virtuality_root
            ),
            1,
        )
        assert_symbolic_equal(
            density_without_support,
            result.bulk_coefficient / transverse2,
            f"{result.channel.spec.name} 1/|k_perp|^2 density",
        )


def test_integrated_results_have_dimensional_poles() -> None:
    kinematics, _, phase_space = _results()

    for result in phase_space:
        expanded = epsilon_series(result.integrated_bulk, kinematics, depth=0)
        pole = expanded.coefficient(kinematics.epsilon ** -1)
        assert pole != 0


def test_probability_relation_between_qq_and_qg_kernels() -> None:
    kinematics = make_kinematics()
    x = kinematics.x
    temporary = kinematics.delta
    qg_at_complement = kernel_qg(kinematics).replace(x, temporary).replace(
        temporary,
        1 - x,
    )

    assert_symbolic_equal(
        kernel_qq(kinematics),
        qg_at_complement,
        "P_qq(x) = P_gq(1-x)",
    )


def test_cdr_altarelli_parisi_kernels() -> None:
    kinematics = make_kinematics()
    x = kinematics.x
    epsilon = kinematics.epsilon

    assert_symbolic_equal(
        ap_qq_cdr(x, epsilon),
        (1 + x**2) / (1 - x) - epsilon * (1 - x),
        "CDR p_qq",
    )
    assert_symbolic_equal(
        ap_gq_cdr(x, epsilon),
        (1 + (1 - x) ** 2) / x - epsilon * x,
        "CDR p_gq",
    )
    assert_symbolic_equal(
        ap_qg_cdr(x, epsilon),
        (x**2 + (1 - x) ** 2 - epsilon) / (1 - epsilon),
        "CDR p_qg",
    )
    assert_symbolic_equal(
        ap_gg_cdr(x, epsilon),
        2 * (x / (1 - x) + (1 - x) / x + x * (1 - x)),
        "CDR p_gg",
    )
    colors = make_color_context()
    for name, color_factor, stripped_kernel in (
        ("qq", colors.cf, ap_qq_cdr(x, epsilon)),
        ("gq", colors.cf, ap_gq_cdr(x, epsilon)),
        ("qg", colors.tr, ap_qg_cdr(x, epsilon)),
        ("gg", colors.ca, ap_gg_cdr(x, epsilon)),
    ):
        assert_symbolic_equal(
            expand_cdr_kernel(
                cdr_kernel_symbol(name, x, epsilon),
                name,
                x,
                epsilon,
                color_factor,
            ),
            color_factor * stripped_kernel,
            f"color-dressed CDR P_{name}",
        )
    assert_symbolic_equal(
        set_dimension(kernel_gq(kinematics), kinematics),
        2 * (1 - epsilon) * ap_qg_cdr(x, epsilon),
        "manuscript tilde P_gq mapping",
    )
    assert_symbolic_equal(
        set_dimension(kernel_qg(kinematics), kinematics),
        ap_gq_cdr(x, epsilon),
        "manuscript tilde P_qg mapping",
    )
    assert_symbolic_equal(
        set_dimension(kernel_qq(kinematics), kinematics),
        ap_qq_cdr(x, epsilon),
        "manuscript tilde P_qq mapping",
    )


def test_compact_ap_forms_expand_to_direct_channel_results() -> None:
    kinematics, channels, phase_space = _results()

    for channel, integrated in zip(channels, phase_space, strict=True):
        spec = channel.spec
        exponent = (kinematics.d - 4) / 2
        radial_factor = set_dimension(
            derive_phase_space_normalization(kinematics).normalized_prefactor
            * kinematics.transverse_cutoff**exponent,
            kinematics,
        )

        def expand_stripped(expression):
            return expand_ap_kernel(
                expression,
                spec.ap_kernel_name,
                kinematics.x,
                kinematics.epsilon,
            )

        assert_symbolic_equal(
            expand_stripped(spec.ap_numerator),
            set_dimension(spec.raw_numerator, kinematics),
            f"{spec.name} compact AP numerator",
        )

        def expand_full(expression):
            return expand_cdr_kernel(
                expression,
                spec.ap_kernel_name,
                kinematics.x,
                kinematics.epsilon,
                spec.color_factor,
            )

        assert_symbolic_equal(
            set_dimension(
                expand_full(channel.normalized_ap_numerator),
                kinematics,
            ),
            set_dimension(
                spec.spin_factorization_factor
                * spec.color_factor
                * spec.raw_numerator,
                kinematics,
            ),
            f"{spec.name} full CDR normalized numerator",
        )
        assert_symbolic_equal(
            expand_full(integrated.ap_bulk_coefficient),
            set_dimension(integrated.bulk_coefficient, kinematics),
            f"{spec.name} compact AP bulk coefficient",
        )
        assert_symbolic_equal(
            expand_full(integrated.ap_integrated_bulk),
            set_dimension(integrated.integrated_bulk, kinematics),
            f"{spec.name} compact AP integrated bulk",
        )
        assert_symbolic_equal(
            integrated.ap_integrated_bulk,
            -radial_factor
            * integrated.ap_bulk_coefficient
            * spec.born
            / kinematics.epsilon,
            f"{spec.name} common radial bulk form",
        )
        assert_symbolic_equal(
            expand_full(integrated.ap_integrated_boundary),
            set_dimension(integrated.integrated_boundary, kinematics),
            f"{spec.name} compact AP integrated boundary",
        )
        assert_symbolic_equal(
            integrated.ap_integrated_boundary,
            radial_factor
            * integrated.ap_boundary_coefficient
            * spec.born,
            f"{spec.name} common radial boundary form",
        )
        assert_symbolic_equal(
            expand_full(integrated.ap_boundary_coefficient),
            integrated.boundary_coefficient,
            f"{spec.name} derived cutoff boundary coefficient",
        )


def test_cutoff_boundary_normalizations() -> None:
    kinematics, _, phase_space = _results()
    x = kinematics.x
    epsilon = kinematics.epsilon
    by_name = {
        result.channel.spec.name: result
        for result in phase_space
    }

    assert_symbolic_equal(
        by_name["D_gq"].boundary_coefficient,
        by_name["D_gq"].channel.spec.color_factor,
        "D_gq cutoff boundary",
    )
    assert_symbolic_equal(
        by_name["D_qg"].boundary_coefficient,
        by_name["D_qg"].channel.spec.color_factor
        * (1 - epsilon),
        "D_qg cutoff boundary",
    )
    assert_symbolic_equal(
        by_name["D_qq"].boundary_coefficient,
        by_name["D_qq"].channel.spec.color_factor
        * (1 - epsilon),
        "D_qq cutoff boundary",
    )
    assert_symbolic_equal(
        by_name["D_gg"].boundary_coefficient,
        -3
        * by_name["D_gg"].channel.spec.color_factor
        * (3 - 2 * epsilon)
        / (4 * (1 - epsilon)),
        "D_gg all-metric cutoff boundary",
    )


def test_dgg_kernel_is_symmetric_under_daughter_exchange() -> None:
    kinematics = make_kinematics()
    assert_symbolic_equal(
        kernel_gg(kinematics),
        complement_momentum_fraction(kernel_gg(kinematics), kinematics),
        "P_gg(x) = P_gg(1-x)",
    )


def test_dqq_dqg_complementarity_includes_metric_boundary() -> None:
    kinematics, _, phase_space = _results()
    by_name = {
        result.channel.spec.name: result
        for result in phase_space
    }
    qq = by_name["D_qq"]
    qg = by_name["D_qg"]

    assert_symbolic_equal(
        set_dimension(qq.bulk_coefficient, kinematics),
        complement_momentum_fraction(
            set_dimension(qg.bulk_coefficient, kinematics),
            kinematics,
        ),
        "D_qq(x) = D_qg(1-x) bulk",
    )
    assert_symbolic_equal(
        qq.boundary_coefficient,
        complement_momentum_fraction(
            qg.boundary_coefficient,
            kinematics,
        ),
        "D_qq(x) = D_qg(1-x) boundary",
    )
