"""Explicit incoming-leg factorization records for Drell--Yan.

The records in this module describe collinear factorization of a *bare
parton-model* hard coefficient.  Their sign convention is deliberately
encoded in the public API::

    factorized_hard = bare_hard + sum(record.hard_shift_added_to_bare)

They are therefore neither cut-graph contributions nor the ``MP - PM`` (or
``LU -> MSbar``) transition.  In particular, the two operations must be
assembled and audited separately.

All kernels accepted by the builders are one-leg, colour-and-coupling-stripped
``EndpointCoefficient`` objects.  A ``*_pole_residue`` is the residue of the
simple collinear pole; the builders place the explicit ``+1/epsilon`` in the
record.  This convention makes it difficult to accidentally supply a pole
with the opposite sign or count ``alpha_s C_i/(2*pi)`` twice.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping, Sequence

from symbolica import E, Expression

from calculations.dy.python.physical import DYContext, EndpointCoefficient


OrderedDYChannel = Literal["qqbar", "qg", "gq"]
ConvolutionSide = Literal["left", "right"]
FactorizationScheme = Literal["MSbar", "AEM-DIS-1979"]
FactorizationKernel = Literal["q<-q", "q<-g"]


MSBAR_DIMENSIONAL_CONVENTION = (
    "CDR, d=4-2*epsilon, a_s=alpha_s/(2*pi); common dimensional "
    "factor stripped; pole stores +residue/epsilon"
)
AEM_DIS_1979_DIMENSIONAL_CONVENTION = (
    "AEM DIS (1979), d=4-2*epsilon, a_s=alpha_s/(2*pi); the common "
    "AEM dimensional factor is stripped; pole stores +residue/epsilon"
)


def _sum_endpoint_coefficients(
    coefficients: Sequence[EndpointCoefficient],
) -> EndpointCoefficient:
    total = EndpointCoefficient()
    for coefficient in coefficients:
        total = total + coefficient
    return total


def _expressions_equal(left: Expression, right: Expression) -> bool:
    return (left - right).expand().together().cancel() == E("0")


@dataclass(frozen=True, slots=True)
class FactorizationLegRecord:
    """One incoming-leg hard shift added to a bare DY coefficient.

    ``pole`` is the actual pole contribution and includes ``+1/epsilon``;
    ``finite`` is its epsilon-to-zero finite companion.  Both are stripped of
    the coupling and colour factor held in ``coupling_color_prefactor``.
    ``ordered_channel`` is never a qg/gq average.
    """

    name: str
    ordered_channel: OrderedDYChannel
    beam: Literal[1, 2]
    incoming_parton: Literal["q", "qbar", "g"]
    born_parton: Literal["q", "qbar", "g"]
    factorization_kernel: FactorizationKernel
    convolution_side: ConvolutionSide
    scheme: FactorizationScheme
    pole: EndpointCoefficient
    finite: EndpointCoefficient
    coupling_color_prefactor: Expression
    dimensional_convention: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("A factorization-leg record needs a name")
        if self.convolution_side != ("left" if self.beam == 1 else "right"):
            raise ValueError(
                f"{self.name}: beam {self.beam} must use the corresponding "
                "left/right convolution side"
            )
        if not isinstance(self.provenance, tuple) or not self.provenance:
            raise ValueError(
                f"{self.name}: provenance must be a non-empty immutable tuple"
            )
        if self.factorization_kernel == "q<-q":
            if self.incoming_parton != self.born_parton:
                raise ValueError(
                    f"{self.name}: q<-q must preserve the incoming species"
                )
            if self.incoming_parton not in ("q", "qbar"):
                raise ValueError(f"{self.name}: q<-q requires a quark leg")
        elif not (
            self.incoming_parton == "g"
            and self.born_parton in ("q", "qbar")
        ):
            raise ValueError(
                f"{self.name}: q<-g requires an incoming gluon and a Born quark"
            )

    @property
    def stripped_hard_shift_added_to_bare(self) -> EndpointCoefficient:
        """Return ``pole + finite`` before coupling and colour are restored."""

        return self.pole + self.finite

    @property
    def hard_shift_added_to_bare(self) -> EndpointCoefficient:
        """Return this leg's signed contribution in the hard-coefficient units."""

        return self.stripped_hard_shift_added_to_bare.scaled(
            self.coupling_color_prefactor
        )

    def factorize_bare(
        self,
        bare: EndpointCoefficient,
        variable: Expression,
    ) -> EndpointCoefficient:
        """Apply this record using ``factorized = bare + hard_shift``."""

        return (bare + self.hard_shift_added_to_bare).canonical(variable)


@dataclass(frozen=True, slots=True)
class DYFactorizationRecords:
    """The standard ordered-channel DY factorization ledger for one scheme."""

    records: tuple[FactorizationLegRecord, ...]

    def __post_init__(self) -> None:
        if not self.records:
            raise ValueError("A DY factorization ledger cannot be empty")
        names = tuple(record.name for record in self.records)
        if len(names) != len(set(names)):
            raise ValueError("Factorization-leg record names must be unique")
        schemes = {record.scheme for record in self.records}
        if len(schemes) != 1:
            raise ValueError("One factorization ledger must use exactly one scheme")

    @property
    def scheme(self) -> FactorizationScheme:
        return self.records[0].scheme

    def for_ordered_channel(
        self,
        channel: OrderedDYChannel,
    ) -> tuple[FactorizationLegRecord, ...]:
        """Select records for one ordered channel, without qg/gq averaging."""

        return tuple(
            record
            for record in self.records
            if record.ordered_channel == channel
        )

    def pole_shift_added_to_bare(
        self,
        channel: OrderedDYChannel,
        variable: Expression,
    ) -> EndpointCoefficient:
        return _sum_endpoint_coefficients(
            tuple(
                record.pole.scaled(record.coupling_color_prefactor)
                for record in self.for_ordered_channel(channel)
            )
        ).canonical(variable)

    def finite_shift_added_to_bare(
        self,
        channel: OrderedDYChannel,
        variable: Expression,
    ) -> EndpointCoefficient:
        return _sum_endpoint_coefficients(
            tuple(
                record.finite.scaled(record.coupling_color_prefactor)
                for record in self.for_ordered_channel(channel)
            )
        ).canonical(variable)

    def hard_shift_added_to_bare(
        self,
        channel: OrderedDYChannel,
        variable: Expression,
    ) -> EndpointCoefficient:
        """Sum the leg records for exactly one ordered incoming channel."""

        return _sum_endpoint_coefficients(
            tuple(
                record.hard_shift_added_to_bare
                for record in self.for_ordered_channel(channel)
            )
        ).canonical(variable)

    def factorize_bare(
        self,
        channel: OrderedDYChannel,
        bare: EndpointCoefficient,
        variable: Expression,
    ) -> EndpointCoefficient:
        """Return the selected factorized hard coefficient."""

        return (
            bare + self.hard_shift_added_to_bare(channel, variable)
        ).canonical(variable)

    def ordered_channel_shifts(
        self,
        variable: Expression,
    ) -> Mapping[OrderedDYChannel, EndpointCoefficient]:
        """Return distinct qqbar, qg, and gq shifts (never a qg average)."""

        return MappingProxyType(
            {
                channel: self.hard_shift_added_to_bare(channel, variable)
                for channel in ("qqbar", "qg", "gq")
            }
        )

    def assert_exact_invariants(self, context: DYContext) -> None:
        """Require the standard two-quark-leg/one-gluon-leg DY layout."""

        expected_layout: Mapping[
            OrderedDYChannel,
            set[tuple[object, ...]],
        ] = {
            "qqbar": {(1, "q", "q", "q<-q", "left"),
                      (2, "qbar", "qbar", "q<-q", "right")},
            "qg": {(2, "g", "qbar", "q<-g", "right")},
            "gq": {(1, "g", "qbar", "q<-g", "left")},
        }
        for channel, expected in expected_layout.items():
            actual = {
                (
                    record.beam,
                    record.incoming_parton,
                    record.born_parton,
                    record.factorization_kernel,
                    record.convolution_side,
                )
                for record in self.for_ordered_channel(channel)
            }
            if actual != expected:
                raise AssertionError(
                    f"{self.scheme}/{channel}: factorizing-leg layout is {actual}, "
                    f"expected {expected}"
                )

        qq_prefactor = context.alpha_s * context.color_f / (2 * context.pi)
        qg_prefactor = context.alpha_s * context.color_t / (2 * context.pi)
        for record in self.records:
            expected_prefactor = (
                qq_prefactor
                if record.factorization_kernel == "q<-q"
                else qg_prefactor
            )
            if not _expressions_equal(
                record.coupling_color_prefactor,
                expected_prefactor,
            ):
                raise AssertionError(
                    f"{record.name}: coupling/color prefactor is inconsistent"
                )
            for value in record.finite.residuals():
                if value.contains(context.epsilon):
                    raise AssertionError(
                        f"{record.name}: finite coefficient still contains epsilon"
                    )
            for value in record.pole.residuals():
                residue = (context.epsilon * value).expand().together().cancel()
                if residue.contains(context.epsilon):
                    raise AssertionError(
                        f"{record.name}: pole is not a pure simple 1/epsilon pole"
                    )

        qq_records = self.for_ordered_channel("qqbar")
        qq_leg_residual = (
            qq_records[0].hard_shift_added_to_bare
            - qq_records[1].hard_shift_added_to_bare
        )
        if not qq_leg_residual.is_zero_for(context.z):
            raise AssertionError("The charge-conjugate qqbar leg shifts differ")

        qg_gq_residual = (
            self.hard_shift_added_to_bare("qg", context.z)
            - self.hard_shift_added_to_bare("gq", context.z)
        )
        if not qg_gq_residual.is_zero_for(context.z):
            raise AssertionError("The ordered qg and gq leg shifts differ")


def _build_standard_records(
    context: DYContext,
    *,
    scheme: FactorizationScheme,
    qq_pole_residue: EndpointCoefficient,
    qq_finite: EndpointCoefficient,
    qg_pole_residue: EndpointCoefficient,
    qg_finite: EndpointCoefficient,
    dimensional_convention: str,
    provenance: Sequence[str],
) -> DYFactorizationRecords:
    provenance_tuple = tuple(provenance)
    qq_pole = qq_pole_residue.scaled(1 / context.epsilon)
    qg_pole = qg_pole_residue.scaled(1 / context.epsilon)
    qq_prefactor = context.alpha_s * context.color_f / (2 * context.pi)
    qg_prefactor = context.alpha_s * context.color_t / (2 * context.pi)

    records = DYFactorizationRecords(
        records=(
            FactorizationLegRecord(
                name=f"{scheme}:qqbar:beam1:q<-q",
                ordered_channel="qqbar",
                beam=1,
                incoming_parton="q",
                born_parton="q",
                factorization_kernel="q<-q",
                convolution_side="left",
                scheme=scheme,
                pole=qq_pole,
                finite=qq_finite,
                coupling_color_prefactor=qq_prefactor,
                dimensional_convention=dimensional_convention,
                provenance=provenance_tuple,
            ),
            FactorizationLegRecord(
                name=f"{scheme}:qqbar:beam2:qbar<-qbar",
                ordered_channel="qqbar",
                beam=2,
                incoming_parton="qbar",
                born_parton="qbar",
                factorization_kernel="q<-q",
                convolution_side="right",
                scheme=scheme,
                pole=qq_pole,
                finite=qq_finite,
                coupling_color_prefactor=qq_prefactor,
                dimensional_convention=dimensional_convention,
                provenance=provenance_tuple,
            ),
            FactorizationLegRecord(
                name=f"{scheme}:qg:beam2:qbar<-g",
                ordered_channel="qg",
                beam=2,
                incoming_parton="g",
                born_parton="qbar",
                factorization_kernel="q<-g",
                convolution_side="right",
                scheme=scheme,
                pole=qg_pole,
                finite=qg_finite,
                coupling_color_prefactor=qg_prefactor,
                dimensional_convention=dimensional_convention,
                provenance=provenance_tuple,
            ),
            FactorizationLegRecord(
                name=f"{scheme}:gq:beam1:qbar<-g",
                ordered_channel="gq",
                beam=1,
                incoming_parton="g",
                born_parton="qbar",
                factorization_kernel="q<-g",
                convolution_side="left",
                scheme=scheme,
                pole=qg_pole,
                finite=qg_finite,
                coupling_color_prefactor=qg_prefactor,
                dimensional_convention=dimensional_convention,
                provenance=provenance_tuple,
            ),
        )
    )
    records.assert_exact_invariants(context)
    return records


def build_msbar_factorization_records(
    context: DYContext,
    *,
    qq_pole_residue: EndpointCoefficient,
    qg_pole_residue: EndpointCoefficient,
    provenance: Sequence[str],
) -> DYFactorizationRecords:
    """Build the MSbar hard shifts ``+P^(0)/epsilon`` for all DY legs.

    The supplied residues are single-leg, colour-and-coupling-stripped
    endpoint coefficients.  At this order the MSbar finite shift vanishes in
    the stated stripped dimensional convention.
    """

    return _build_standard_records(
        context,
        scheme="MSbar",
        qq_pole_residue=qq_pole_residue,
        qq_finite=EndpointCoefficient(),
        qg_pole_residue=qg_pole_residue,
        qg_finite=EndpointCoefficient(),
        dimensional_convention=MSBAR_DIMENSIONAL_CONVENTION,
        provenance=provenance,
    )


def build_aem_dis_1979_factorization_records(
    context: DYContext,
    *,
    qq_pole_residue: EndpointCoefficient,
    qq_finite: EndpointCoefficient,
    qg_pole_residue: EndpointCoefficient,
    qg_finite: EndpointCoefficient,
    provenance: Sequence[str],
) -> DYFactorizationRecords:
    """Build the AEM 1979 DIS-prescription hard shifts for ordered DY.

    Each input is a *single-leg* stripped coefficient.  In particular, a
    published two-leg qqbar counterterm must be divided into its two equal
    incoming-leg contributions before it is passed here.  The ordered qg and
    gq records each receive one gluon-leg contribution; no averaging factor is
    introduced.
    """

    return _build_standard_records(
        context,
        scheme="AEM-DIS-1979",
        qq_pole_residue=qq_pole_residue,
        qq_finite=qq_finite,
        qg_pole_residue=qg_pole_residue,
        qg_finite=qg_finite,
        dimensional_convention=AEM_DIS_1979_DIMENSIONAL_CONVENTION,
        provenance=provenance,
    )


__all__ = (
    "AEM_DIS_1979_DIMENSIONAL_CONVENTION",
    "ConvolutionSide",
    "DYFactorizationRecords",
    "FactorizationKernel",
    "FactorizationLegRecord",
    "FactorizationScheme",
    "MSBAR_DIMENSIONAL_CONVENTION",
    "OrderedDYChannel",
    "build_aem_dis_1979_factorization_records",
    "build_msbar_factorization_records",
)
