from splitting_kernels.channels import (
    build_gq_channel,
    build_qg_channel,
    build_qq_channel,
    derive_channel,
)
from splitting_kernels.colors import make_color_context
from splitting_kernels.kinematics import make_kinematics
from splitting_kernels.phase_space import integrate_channel_phase_space
from splitting_kernels.relabeling import audit_coordinate_relabeling
from splitting_kernels.tensors import make_tensor_context


def test_old_cut_fraction_results_equal_new_hard_fraction_results() -> None:
    kinematics = make_kinematics()
    tensors = make_tensor_context(kinematics)
    colors = make_color_context()
    specs = (
        build_gq_channel(kinematics, tensors, colors),
        build_qg_channel(kinematics, tensors, colors),
        build_qq_channel(kinematics, tensors, colors),
    )
    channels = tuple(derive_channel(spec, kinematics) for spec in specs)
    phase_space = tuple(
        integrate_channel_phase_space(channel, kinematics)
        for channel in channels
    )

    audits = audit_coordinate_relabeling(
        channels,
        phase_space,
        kinematics,
        colors,
    )

    assert {audit.channel for audit in audits} == {"D_gq", "D_qg", "D_qq"}
    assert all(audit.passed is True for audit in audits), audits
