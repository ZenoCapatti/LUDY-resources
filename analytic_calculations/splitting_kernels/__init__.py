"""Symbolica-only tools for the splitting counter-term notebook."""

from .assembly import (
    DistributionalCheck,
    NLOCountertermAssembly,
    NLOCountertermEntry,
    assemble_nlo_counterterm,
)
from .channels import (
    ChannelResult,
    ChannelSpec,
    build_gq_channel,
    build_gg_channel,
    build_qg_channel,
    build_qq_channel,
    derive_channel,
)
from .colors import ColorContext, ColorReduction, make_color_context
from .kinematics import Kinematics, canonical, make_kinematics
from .kernels import (
    ap_gq_cdr,
    ap_gg_cdr,
    ap_qg_cdr,
    ap_qq_cdr,
    cdr_kernel_symbol,
    expand_cdr_kernel,
)
from .phase_space import (
    PhaseSpaceResult,
    integrate_channel_phase_space,
    integrate_unit_interval_beta,
)
from .normalization import (
    PhaseSpaceNormalization,
    derive_phase_space_normalization,
)
from .relabeling import (
    CoordinateReference,
    CoordinateRelabelingAudit,
    audit_coordinate_relabeling,
    old_cut_fraction_references,
)
from .tensors import (
    GluonParentNumeratorResult,
    GluonSelfSplittingNumeratorResult,
    GluonVirtualNumeratorResult,
    QuarkParentNumeratorResult,
    TensorContext,
    VirtualNumeratorResult,
    make_tensor_context,
    gluon_parent_quark_born_numerator,
    gluon_self_splitting_numerator,
    gluon_virtual_self_energy_numerator,
    quark_born_reduced_numerator,
    virtual_self_energy_numerator,
)
from .virtual import (
    GluonVirtualPhaseSpaceResult,
    VirtualPhaseSpaceResult,
    integrate_gluon_virtual_self_energy,
    integrate_virtual_self_energy,
)

__all__ = [
    "ChannelResult",
    "ChannelSpec",
    "ColorContext",
    "ColorReduction",
    "CoordinateReference",
    "CoordinateRelabelingAudit",
    "DistributionalCheck",
    "GluonParentNumeratorResult",
    "GluonSelfSplittingNumeratorResult",
    "GluonVirtualNumeratorResult",
    "GluonVirtualPhaseSpaceResult",
    "Kinematics",
    "NLOCountertermAssembly",
    "NLOCountertermEntry",
    "PhaseSpaceNormalization",
    "PhaseSpaceResult",
    "QuarkParentNumeratorResult",
    "TensorContext",
    "VirtualNumeratorResult",
    "VirtualPhaseSpaceResult",
    "ap_gq_cdr",
    "ap_gg_cdr",
    "ap_qg_cdr",
    "ap_qq_cdr",
    "assemble_nlo_counterterm",
    "audit_coordinate_relabeling",
    "build_gq_channel",
    "build_gg_channel",
    "build_qg_channel",
    "build_qq_channel",
    "canonical",
    "cdr_kernel_symbol",
    "derive_channel",
    "derive_phase_space_normalization",
    "expand_cdr_kernel",
    "integrate_channel_phase_space",
    "integrate_gluon_virtual_self_energy",
    "integrate_virtual_self_energy",
    "integrate_unit_interval_beta",
    "gluon_parent_quark_born_numerator",
    "gluon_self_splitting_numerator",
    "gluon_virtual_self_energy_numerator",
    "make_color_context",
    "make_kinematics",
    "make_tensor_context",
    "old_cut_fraction_references",
    "quark_born_reduced_numerator",
    "virtual_self_energy_numerator",
]
