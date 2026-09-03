"""Regression audit for the change from cut to hard momentum fraction."""

from dataclasses import dataclass

from symbolica import Expression

from .channels import ChannelResult
from .colors import ColorContext
from .kinematics import (
    Kinematics,
    canonical,
    complement_momentum_fraction,
    set_dimension,
)
from .kernels import ap_gq_cdr, ap_qg_cdr, ap_qq_cdr
from .phase_space import PhaseSpaceResult


@dataclass(frozen=True)
class CoordinateReference:
    """A result written with the former convention x = cut fraction."""

    channel: str
    raw_numerator: Expression
    bulk_coefficient: Expression
    boundary_coefficient: Expression


@dataclass(frozen=True)
class CoordinateRelabelingAudit:
    """Residuals after applying x_old -> 1-x to an old result."""

    channel: str
    numerator_residual: Expression
    bulk_residual: Expression
    boundary_residual: Expression

    @property
    def passed(self) -> bool:
        return all(
            residual == 0
            for residual in (
                self.numerator_residual,
                self.bulk_residual,
                self.boundary_residual,
            )
        )


def old_cut_fraction_references(
    kinematics: Kinematics,
    colors: ColorContext,
) -> tuple[CoordinateReference, ...]:
    """Return the pre-change formulas, used only as regression references."""

    x = kinematics.x
    d = kinematics.d
    epsilon = kinematics.epsilon
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2

    return (
        CoordinateReference(
            channel="D_gq",
            raw_numerator=canonical(
                4 * x * (1 - x) ** 2 * p2
                + transverse2
                * (2 * ((1 - x) ** 2 + x**2) + d - 4)
                / x
            ),
            bulk_coefficient=canonical(
                colors.tr
                * ap_qg_cdr(x, epsilon)
            ),
            boundary_coefficient=canonical(
                colors.tr
            ),
        ),
        CoordinateReference(
            channel="D_qg",
            raw_numerator=canonical(
                2 * (d - 2) * x * p2
                + 4
                * transverse2
                * ap_qq_cdr(x, (4 - d) / 2)
                / (x * (1 - x))
            ),
            bulk_coefficient=canonical(
                colors.cf * ap_qq_cdr(x, epsilon)
            ),
            boundary_coefficient=canonical(
                colors.cf * (1 - epsilon)
            ),
        ),
        CoordinateReference(
            channel="D_qq",
            raw_numerator=canonical(
                (d - 2) * (1 - x) ** 2 * p2
                + (d - 2) * transverse2
                + 4 * (1 - x) * transverse2 / x**2
            ),
            bulk_coefficient=canonical(
                colors.cf * ap_gq_cdr(x, epsilon)
            ),
            boundary_coefficient=canonical(
                colors.cf * (1 - epsilon)
            ),
        ),
    )


def audit_coordinate_relabeling(
    channels: tuple[ChannelResult, ...],
    phase_space: tuple[PhaseSpaceResult, ...],
    kinematics: Kinematics,
    colors: ColorContext,
) -> tuple[CoordinateRelabelingAudit, ...]:
    """Compare new results with old ones after x_old -> 1-x."""

    channel_by_name = {
        result.spec.name: result
        for result in channels
    }
    phase_space_by_name = {
        result.channel.spec.name: result
        for result in phase_space
    }
    audits = []
    for reference in old_cut_fraction_references(kinematics, colors):
        channel = channel_by_name[reference.channel]
        integrated = phase_space_by_name[reference.channel]
        audits.append(
            CoordinateRelabelingAudit(
                channel=reference.channel,
                numerator_residual=canonical(
                    channel.spec.raw_numerator
                    - complement_momentum_fraction(
                        reference.raw_numerator,
                        kinematics,
                    )
                ),
                bulk_residual=canonical(
                    set_dimension(integrated.bulk_coefficient, kinematics)
                    - complement_momentum_fraction(
                        reference.bulk_coefficient,
                        kinematics,
                    )
                ),
                boundary_residual=canonical(
                    integrated.boundary_coefficient
                    - complement_momentum_fraction(
                        reference.boundary_coefficient,
                        kinematics,
                    )
                ),
            )
        )
    return tuple(audits)
