"""Standalone native assembly of the NLO DIS multi-partonic coefficient.

The public assembler consumes only the exact coefficient/master boundary, the
compiled physical topologies, and their cut ledger. Paper, LaTeX, Mathematica,
and conventional parton-model coefficient functions are downstream comparison
data only and cannot be supplied as arguments.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

from symbolica import E, Expression

from calculations.dis.python.assembly import (
    DISMasterInsertionAudit,
    OrdinaryMasterBoundary,
)
from calculations.dis.python.masters import (
    loop_normalization,
    massless_cut_bubble,
    uncut_bubble,
    virtuality_integral_factor,
)
from calculations.dis.python.physical import (
    DIS_GRAPH_SPECS,
    DIS_GRAPH_TOPOLOGIES,
    DIS_KINEMATICS,
    EXPECTED_STRUCTURAL_CUT_SIGNATURES,
    KNOWN_DIS_CUTS,
    STRUCTURAL_CUT_SUPPORT_PAIRS,
    DISCutSpec,
    DISGraphSpec,
    DISKinematics,
    DISStructureFunctions,
    DistributionCoefficient,
    alpha_s,
    canonical,
    color_f,
    color_t,
    electric_charge,
    strong_coupling,
)
from notebooks.ludy import replace_all


SchemePrimitiveKind = Literal["master_boundary", "graph_weight", "cut_phase"]


@dataclass(frozen=True, slots=True)
class NativeSchemePrimitive:
    """One primitive input missing from the native assembly boundary."""

    key: str
    kind: SchemePrimitiveKind
    affected_records: tuple[str, ...]
    description: str
    source: str


@dataclass(frozen=True, slots=True)
class NativeSchemeAssemblyStage:
    """One executable native assembly stage and its completion state."""

    key: str
    affected_records: tuple[str, ...]
    description: str
    source: str


@dataclass(frozen=True, slots=True)
class NativeCutConventionEvidence:
    """Graph-independent phase and derivative metadata for one cut sector."""

    cut_key: str
    total_derivative_order: int
    relative_phase: Literal[-1, 1]
    formal_reverse_unitarity_sign: Literal[-1, 1]
    derivative_application: Literal["none", "external_endpoint", "encoded_in_kira"]
    oriented_multiplicity: Literal[1] = 1


@dataclass(frozen=True, slots=True)
class NativeDISMPResult:
    """Finite native MP brackets and their exact Laurent audit.

    The brackets multiply ``e_q^2 alpha_s/(2 pi) x`` and the channel colour
    factor ``C_F`` or ``T_F``. No conventional coefficient enters assembly.
    """

    brackets: DISStructureFunctions
    laurent: Mapping[int, DISStructureFunctions]
    graph_weights: Mapping[str, Expression]
    cut_phases: Mapping[str, Expression]
    raised_external_residuals: Mapping[str, Expression]
    assembly_components: Mapping[str, Expression]

    @property
    def poles_cancel(self) -> bool:
        for power in (-2, -1):
            functions = self.laurent[power]
            if not functions.F2q.is_zero or not functions.F2g.is_zero:
                return False
            if not functions.FLq.is_zero or not functions.FLg.is_zero:
                return False
        return True

    @property
    def raised_external_exact(self) -> bool:
        return all(
            canonical(value).format_plain() == "0"
            for value in self.raised_external_residuals.values()
        )


class NativeDISSchemeUnavailableError(RuntimeError):
    """Raised when the exact 32-record master boundary is unavailable."""

    def __init__(self, blockers: Sequence[NativeSchemePrimitive]) -> None:
        self.blockers = tuple(blockers)
        detail = "; ".join(
            f"{blocker.key}: {blocker.description}" for blocker in self.blockers
        )
        super().__init__(f"Native DIS MP coefficient is unavailable: {detail}")


@dataclass(frozen=True, slots=True)
class NativeDISDerivationEvidence:
    """Machine-readable provenance of the topology/master/cut derivation."""

    declared_topologies: tuple[str, ...]
    declared_graphs: tuple[str, ...]
    declared_cut_signatures: tuple[
        tuple[
            str,
            str,
            tuple[int, ...],
            tuple[int, ...],
            tuple[tuple[int, int], ...],
        ],
        ...,
    ]
    cut_conventions: tuple[NativeCutConventionEvidence, ...]
    cut_support_pairs: tuple[tuple[str, tuple[int, int]], ...]
    topology_owned_fields: tuple[str, ...]
    master_records_expected: int
    master_records_present: int
    master_records_exact: int
    master_boundary_exact: bool
    sign_convention: Literal["MP-PM"] = "MP-PM"
    incoming_legs: Literal[1] = 1
    distribution_basis: tuple[str, ...] = (
        "delta(1-x)",
        "D_n(x)=[log(1-x)^n/(1-x)]_+",
        "regular(x)",
    )


@dataclass(frozen=True, slots=True)
class NativeDISSchemeChangeAudit:
    """Native MP readiness plus the result when its master boundary is exact."""

    evidence: NativeDISDerivationEvidence
    blockers: tuple[NativeSchemePrimitive, ...]
    unimplemented_stages: tuple[NativeSchemeAssemblyStage, ...]
    mp_result: NativeDISMPResult | None

    @property
    def primitive_inputs_resolved(self) -> bool:
        return not self.blockers

    @property
    def ready(self) -> bool:
        return self.mp_result is not None and not self.blockers

    @property
    def accepts_closed_result(self) -> bool:
        return False

    def require_result(self) -> NativeDISMPResult:
        if self.mp_result is None:
            raise NativeDISSchemeUnavailableError(self.blockers)
        return self.mp_result


def _cut_key(cut: DISCutSpec) -> str:
    return f"{cut.graph_name}:{cut.name}"


def _cut_signature(cut: DISCutSpec):
    return (
        cut.graph_name,
        cut.name,
        cut.initial_cut_lines,
        cut.final_cut_lines,
        cut.cut_orders,
    )


def _exact_zero(value: Expression) -> bool:
    return canonical(value).format_plain() == "0"


def _master_boundary_state(
    audit: DISMasterInsertionAudit | None,
) -> tuple[int, int, bool]:
    if audit is None:
        return 0, 0, False
    present = len(audit.ordinary) + len(audit.raised)
    exact = sum(
        int(_exact_zero(boundary.audit.residual)) for boundary in audit.ordinary
    )
    exact += sum(
        int(_exact_zero(boundary.audit.residual)) for boundary in audit.raised
    )
    return present, exact, audit.exact and present == exact == 32


def _cut_convention(cut: DISCutSpec) -> NativeCutConventionEvidence:
    total_order = sum(order for _line, order in cut.cut_orders)
    raised_lines = tuple(line for line, order in cut.cut_orders if order)
    if cut.relative_sign is None:
        raise ValueError(f"Cut {_cut_key(cut)} has no phase-stripped orientation")
    phase_plain = canonical(cut.relative_sign).format_plain()
    if phase_plain not in {"-1", "1"}:
        raise ValueError(f"Cut {_cut_key(cut)} has non-unit relative phase")
    return NativeCutConventionEvidence(
        cut_key=_cut_key(cut),
        total_derivative_order=total_order,
        relative_phase=-1 if phase_plain == "-1" else 1,
        formal_reverse_unitarity_sign=-1 if total_order % 2 else 1,
        derivative_application=(
            "none"
            if not raised_lines
            else "external_endpoint"
            if any(line in (5, 6) for line in raised_lines)
            else "encoded_in_kira"
        ),
    )


def _series_rules(
    *, mu_squared: Expression, pi: Expression
) -> tuple[tuple[Expression, Expression], ...]:
    gamma = Expression.EULER_GAMMA
    log_two = E("2").log()
    return (
        ((2 * pi).log(), log_two + pi.log()),
        (
            (gamma.exp() / (4 * pi)).log(),
            gamma - 2 * log_two - pi.log(),
        ),
        (
            (mu_squared * gamma.exp() / (4 * pi)).log(),
            mu_squared.log() + gamma - 2 * log_two - pi.log(),
        ),
        ((gamma.exp() * mu_squared).log(), gamma + mu_squared.log()),
        (E("symbolica::polygamma(1,2)"), pi**2 / 6 - 1),
        (E("symbolica::polygamma(1,3/2)"), pi**2 / 2 - 4),
    )


def _laurent_coefficient(
    expression: Expression,
    power: int,
    *,
    epsilon: Expression,
    rules: Sequence[tuple[Expression, Expression]],
) -> Expression:
    coefficient = expression.series(epsilon, 0, 0).get_coefficient(power)
    for _ in range(5):
        coefficient = canonical(replace_all(coefficient, rules))
    return coefficient


def _distribution_laurent_coefficient(
    coefficient: DistributionCoefficient,
    power: int,
    *,
    epsilon: Expression,
    rules: Sequence[tuple[Expression, Expression]],
) -> DistributionCoefficient:
    return DistributionCoefficient(
        variable=coefficient.variable,
        delta=_laurent_coefficient(
            coefficient.delta, power, epsilon=epsilon, rules=rules
        ),
        plus=tuple(
            _laurent_coefficient(value, power, epsilon=epsilon, rules=rules)
            for value in coefficient.plus
        ),
        regular=_laurent_coefficient(
            coefficient.regular, power, epsilon=epsilon, rules=rules
        ),
    )


def assemble_native_dis_mp(
    master_insertion_audit: DISMasterInsertionAudit,
    *,
    graphs: Mapping[str, DISGraphSpec] = DIS_GRAPH_SPECS,
    cuts: Sequence[DISCutSpec] = KNOWN_DIS_CUTS,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> NativeDISMPResult:
    """Assemble finite MP brackets from masters, topologies, and cuts only."""

    if not master_insertion_audit.exact:
        raise ValueError("Native DIS assembly requires an exact 32-record boundary")
    if tuple(_cut_signature(cut) for cut in cuts) != EXPECTED_STRUCTURAL_CUT_SIGNATURES:
        raise ValueError("Native DIS cut signatures do not match the topology basis")
    if any(graph.relative_weight is None for graph in graphs.values()):
        raise ValueError("Every rooted topology needs a graph phase/multiplicity")
    if any(cut.relative_sign is None or cut.multiplicity is None for cut in cuts):
        raise ValueError("Every cut needs a relative phase and multiplicity")

    epsilon = kinematics.regulator
    dimension = kinematics.dimension
    physical_dimension = 4 - 2 * epsilon
    variable = kinematics.bjorken_x
    incoming_virtuality = kinematics.incoming_virtuality
    photon_scale = kinematics.photon_scale
    cutoff = kinematics.cutoff
    mu_squared = kinematics.renormalization_scale
    pi = Expression.PI
    master_arguments = {
        "dimension": physical_dimension,
        "epsilon": epsilon,
        "mu_squared": mu_squared,
        "euler_gamma": Expression.EULER_GAMMA,
    }
    unit_cut_bubble = massless_cut_bubble(E("1"), **master_arguments)
    triangle_leading_prefactor = (
        loop_normalization(mu_squared, epsilon, Expression.EULER_GAMMA)
        * 4
        * pi ** (physical_dimension / 2 + 2)
        / (
            (2 * pi) ** physical_dimension
            * (physical_dimension / 2 - 1).gamma()
        )
    )
    virtuality_factor = virtuality_integral_factor(cutoff, epsilon)
    external_measure = 1 / (8 * pi**2)

    def channel_bracket_factor(channel: str) -> Expression:
        """Strip the declared channel factor to the displayed bracket basis."""

        channel_graphs = tuple(
            graph for graph in graphs.values() if graph.channel == channel
        )
        prefactors = {
            canonical(graph.channel_prefactor).format_plain(): graph.channel_prefactor
            for graph in channel_graphs
        }
        if not channel_graphs or len(prefactors) != 1:
            raise ValueError(f"Channel {channel} has inconsistent topology prefactors")
        declared_prefactor = next(iter(prefactors.values()))
        declared_prefactor = replace_all(
            declared_prefactor,
            ((strong_coupling**2, 4 * pi * alpha_s),),
        ).replace(dimension, physical_dimension)
        colour = color_f if channel == "q" else color_t
        displayed_prefactor = (
            electric_charge**2 * alpha_s * variable * colour / (2 * pi)
        )
        return canonical(declared_prefactor / displayed_prefactor)

    quark_bracket_factor = channel_bracket_factor("q")
    gluon_bracket_factor = channel_bracket_factor("g")

    ordinary: dict[tuple[str, str, str], list[OrdinaryMasterBoundary]] = {}
    for boundary in master_insertion_audit.ordinary:
        key = (
            boundary.audit.handoff.graph_name,
            boundary.cut.name,
            boundary.audit.handoff.observable,
        )
        ordinary.setdefault(key, []).append(boundary)
    cuts_by_key = {(cut.graph_name, cut.name): cut for cut in cuts}

    def cut_weight(graph_name: str, cut_name: str) -> Expression:
        graph = graphs[graph_name]
        cut = cuts_by_key[(graph_name, cut_name)]
        if cut.relative_sign is None or cut.multiplicity is None:
            raise AssertionError(f"Unresolved cut weight for {_cut_key(cut)}")
        return canonical(
            graph.relative_weight * cut.relative_sign * cut.multiplicity
        )

    def coefficient(boundary: OrdinaryMasterBoundary) -> Expression:
        return canonical(
            boundary.audit.coefficient.replace(dimension, physical_dimension)
        )

    def coefficient_at_leading_virtuality(
        boundary: OrdinaryMasterBoundary,
    ) -> Expression:
        return canonical(coefficient(boundary).replace(incoming_virtuality, 0))

    def sum_coefficients(
        graph_name: str, cut_name: str, observable: str
    ) -> Expression:
        return sum(
            (
                coefficient_at_leading_virtuality(boundary)
                for boundary in ordinary.get(
                    (graph_name, cut_name, observable), ()
                )
            ),
            E("0"),
        )

    def final_state_cut_bubble() -> Expression:
        return (
            unit_cut_bubble
            * photon_scale ** (-epsilon)
            * variable**epsilon
            * (1 - variable) ** (-epsilon)
        )

    def cut_triangle_leading() -> Expression:
        return (
            triangle_leading_prefactor
            * photon_scale ** (-1)
            * variable ** (1 - epsilon)
            * (1 - variable) ** (-epsilon)
        )

    def final_state_denominator(graph_name: str) -> Expression:
        power = graphs[graph_name].powers[5]
        return (
            photon_scale ** (-power)
            * variable**power
            * (1 - variable) ** (-power)
        )

    def external_initial(graph_name: str, observable: str) -> Expression:
        cut_name = "external_initial_internal13"
        return canonical(
            cut_weight(graph_name, cut_name)
            * external_measure
            * 2
            * pi
            * sum_coefficients(graph_name, cut_name, observable)
            * final_state_cut_bubble()
            * final_state_denominator(graph_name)
        )

    def triple(graph_name: str, cut_name: str, observable: str) -> Expression:
        return canonical(
            cut_weight(graph_name, cut_name)
            * external_measure
            * sum_coefficients(graph_name, cut_name, observable)
            * cut_triangle_leading()
            * final_state_denominator(graph_name)
            * virtuality_factor
        )

    def initial_cut_delta(
        graph_name: str,
        observable: str,
        *,
        coefficient_power: int = 0,
    ) -> Expression:
        cut_name = "internal12_external_final"
        records = ordinary[(graph_name, cut_name, observable)]
        if len(records) != 1:
            raise AssertionError((graph_name, observable, len(records)))
        reduced_coefficient = coefficient(records[0])
        if coefficient_power:
            reduced_coefficient = canonical(
                reduced_coefficient / incoming_virtuality**coefficient_power
            )
        on_endpoint = canonical(
            reduced_coefficient.replace(incoming_virtuality, 0).replace(
                variable, 1
            )
        )
        return canonical(
            cut_weight(graph_name, cut_name)
            * external_measure
            * 2
            * pi
            / photon_scale
            * on_endpoint
            * unit_cut_bubble
            * virtuality_factor
        )

    def virtual_delta(observable: str) -> Expression:
        graph_name = "q_triangle"
        cut_name = "external_external"
        records = ordinary[(graph_name, cut_name, observable)]
        if len(records) != 1:
            raise AssertionError((graph_name, observable, len(records)))
        on_shell = canonical(
            coefficient(records[0])
            .replace(incoming_virtuality, 0)
            .replace(variable, 1)
        )
        return canonical(
            cut_weight(graph_name, cut_name)
            * external_measure
            * (2 * pi) ** 2
            / photon_scale
            * on_shell
            * uncut_bubble(-photon_scale, **master_arguments)
        )

    quark_triangle_endpoint = (
        external_initial("q_triangle", "F2")
        + triple("q_triangle", "triple123", "F2")
    )
    quark_bubble_endpoint = external_initial("q_bubble", "F2")
    quark_endpoint_smooth = canonical(
        (quark_triangle_endpoint + quark_bubble_endpoint)
        * (1 - variable) ** (1 + epsilon)
    )
    quark_box_regular = (
        external_initial("q_box", "F2")
        + triple("q_box", "triple123", "F2")
    )
    quark_delta = (
        virtual_delta("F2")
        + initial_cut_delta("q_triangle", "F2")
        + initial_cut_delta("q_lsz", "F2", coefficient_power=1)
    )
    endpoint_basis = (
        DistributionCoefficient.delta_basis(variable, -1 / epsilon)
        + DistributionCoefficient.plus_basis(variable, 0)
        + DistributionCoefficient.plus_basis(variable, 1, -epsilon)
    )
    quark_f2_exact = (
        endpoint_basis.multiply_smooth(quark_endpoint_smooth)
        + DistributionCoefficient.delta_basis(variable, quark_delta)
        + DistributionCoefficient(variable=variable, regular=quark_box_regular)
    ).multiply_smooth(quark_bracket_factor)

    quark_fl_exact = sum(
        (
            external_initial(graph_name, "FL")
            for graph_name in ("q_triangle", "q_box", "q_bubble")
        ),
        E("0"),
    )
    quark_fl_exact += triple("q_triangle", "triple123", "FL")
    quark_fl_exact += triple("q_box", "triple123", "FL")
    quark_fl_exact = canonical(quark_fl_exact * quark_bracket_factor)

    gluon_f2_exact = external_initial("g_box", "F2")
    gluon_f2_exact += triple("g_box", "triple123", "F2")
    gluon_f2_exact += external_initial("g_crossed_box", "F2")
    gluon_f2_exact += triple("g_crossed_box", "triple123", "F2")
    gluon_f2_exact += triple("g_crossed_box", "triple134", "F2")
    gluon_f2_exact = canonical(gluon_f2_exact * gluon_bracket_factor)

    gluon_fl_exact = external_initial("g_box", "FL")
    gluon_fl_exact += triple("g_box", "triple123", "FL")
    gluon_fl_exact += external_initial("g_crossed_box", "FL")
    gluon_fl_exact += triple("g_crossed_box", "triple123", "FL")
    gluon_fl_exact += triple("g_crossed_box", "triple134", "FL")
    gluon_fl_exact = canonical(gluon_fl_exact * gluon_bracket_factor)

    rules = _series_rules(mu_squared=mu_squared, pi=pi)
    laurent: dict[int, DISStructureFunctions] = {}
    for power in (-2, -1, 0):
        laurent[power] = DISStructureFunctions(
            F2q=_distribution_laurent_coefficient(
                quark_f2_exact, power, epsilon=epsilon, rules=rules
            ),
            F2g=DistributionCoefficient(
                variable=variable,
                regular=_laurent_coefficient(
                    gluon_f2_exact, power, epsilon=epsilon, rules=rules
                ),
            ),
            FLq=DistributionCoefficient(
                variable=variable,
                regular=_laurent_coefficient(
                    quark_fl_exact, power, epsilon=epsilon, rules=rules
                ),
            ),
            FLg=DistributionCoefficient(
                variable=variable,
                regular=_laurent_coefficient(
                    gluon_fl_exact, power, epsilon=epsilon, rules=rules
                ),
            ),
        )

    raised_residuals: dict[str, Expression] = {}
    for boundary in master_insertion_audit.raised:
        graph_name = boundary.audit.graph_name
        observable = boundary.audit.observable
        raised_coefficient = canonical(
            boundary.audit.coefficient.replace(dimension, physical_dimension)
        )
        if graph_name == "q_bubble":
            ordinary_coefficient = sum_coefficients(
                graph_name, "external_initial_internal13", observable
            )
            residual = canonical(
                raised_coefficient.replace(incoming_virtuality, 0)
                - ordinary_coefficient
            )
        else:
            ordinary_record = ordinary[
                (graph_name, "internal12_external_final", observable)
            ][0]
            ordinary_coefficient = coefficient(ordinary_record)
            residual = canonical(
                raised_coefficient.replace(variable, 1)
                - ordinary_coefficient.replace(variable, 1)
            )
        raised_residuals[f"{graph_name}:{observable}"] = residual

    resolved_cut_phases: dict[str, Expression] = {}
    for cut in cuts:
        if cut.relative_sign is None:
            raise AssertionError(f"Unresolved cut phase for {_cut_key(cut)}")
        resolved_cut_phases[_cut_key(cut)] = cut.relative_sign

    result = NativeDISMPResult(
        brackets=laurent[0],
        laurent=MappingProxyType(laurent),
        graph_weights=MappingProxyType(
            {name: graph.relative_weight for name, graph in graphs.items()}
        ),
        cut_phases=MappingProxyType(resolved_cut_phases),
        raised_external_residuals=MappingProxyType(raised_residuals),
        assembly_components=MappingProxyType(
            {
                "q:F2 endpoint smooth": quark_endpoint_smooth,
                "q:F2 hard delta": quark_delta,
                "q:F2 box regular": quark_box_regular,
                "q:FL all cuts": quark_fl_exact,
                "g:F2 all cuts": gluon_f2_exact,
                "g:FL all cuts": gluon_fl_exact,
                "q:declared-to-bracket factor": quark_bracket_factor,
                "g:declared-to-bracket factor": gluon_bracket_factor,
            }
        ),
    )
    if not result.poles_cancel:
        raise AssertionError("Native DIS all-cut sum did not cancel epsilon poles")
    if not result.raised_external_exact:
        raise AssertionError("Raised external branch completion is not exact")
    return result


def audit_native_dis_scheme_change(
    *,
    master_insertion_audit: DISMasterInsertionAudit | None = None,
    graphs: Mapping[str, DISGraphSpec] = DIS_GRAPH_SPECS,
    cuts: Sequence[DISCutSpec] = KNOWN_DIS_CUTS,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> NativeDISSchemeChangeAudit:
    """Build the native MP result when the exact master boundary is present."""

    present, exact, boundary_exact = _master_boundary_state(master_insertion_audit)
    blockers: list[NativeSchemePrimitive] = []
    if not boundary_exact:
        blockers.append(
            NativeSchemePrimitive(
                key="complete-master-boundary",
                kind="master_boundary",
                affected_records=(f"{present}/32 present; {exact} exact",),
                description=(
                    "The assembler requires 28 ordinary and four raised exact "
                    "master records."
                ),
                source="native Kira reductions and calculations.dis.python.masters",
            )
        )
    for graph in graphs.values():
        if graph.relative_weight is None:
            blockers.append(
                NativeSchemePrimitive(
                    key=f"graph-weight:{graph.name}",
                    kind="graph_weight",
                    affected_records=(graph.name,),
                    description="The rooted topology has no phase/multiplicity.",
                    source=graph.source,
                )
            )
    for cut in cuts:
        if cut.relative_sign is None or cut.multiplicity is None:
            blockers.append(
                NativeSchemePrimitive(
                    key=f"cut-phase:{_cut_key(cut)}",
                    kind="cut_phase",
                    affected_records=(_cut_key(cut),),
                    description="The phase-stripped cut orientation is undeclared.",
                    source=cut.source,
                )
            )

    result = None
    if not blockers and master_insertion_audit is not None:
        result = assemble_native_dis_mp(
            master_insertion_audit,
            graphs=graphs,
            cuts=cuts,
            kinematics=kinematics,
        )
    evidence = NativeDISDerivationEvidence(
        declared_topologies=tuple(
            topology.name for topology in DIS_GRAPH_TOPOLOGIES
        ),
        declared_graphs=tuple(graphs),
        declared_cut_signatures=tuple(_cut_signature(cut) for cut in cuts),
        cut_conventions=tuple(_cut_convention(cut) for cut in cuts),
        cut_support_pairs=STRUCTURAL_CUT_SUPPORT_PAIRS,
        topology_owned_fields=(
            "fermion-cycle momenta and vertex identities",
            "six denominator powers",
            "Feynman phase and rooted multiplicity",
            "channel coupling, colour, and spin factor",
        ),
        master_records_expected=32,
        master_records_present=present,
        master_records_exact=exact,
        master_boundary_exact=boundary_exact,
    )
    return NativeDISSchemeChangeAudit(
        evidence=evidence,
        blockers=tuple(blockers),
        unimplemented_stages=(),
        mp_result=result,
    )


def self_check() -> Mapping[str, object]:
    """Check the fail-closed no-cache path and topology/cut provenance."""

    audit = audit_native_dis_scheme_change()
    if audit.ready or audit.accepts_closed_result or audit.mp_result is not None:
        raise AssertionError("An absent master boundary exposed a native result")
    if len(audit.blockers) != 1 or audit.blockers[0].kind != "master_boundary":
        raise AssertionError("Topology/cut inputs should leave only the cache blocker")
    if audit.evidence.declared_cut_signatures != EXPECTED_STRUCTURAL_CUT_SIGNATURES:
        raise AssertionError("Native scheme audit lost structural cut coverage")
    expected_weights = {
        "q_triangle": "-2",
        "q_box": "-1",
        "q_bubble": "-1",
        "q_lsz": "-1",
        "g_box": "1",
        "g_crossed_box": "1",
    }
    if any(
        canonical(DIS_GRAPH_SPECS[name].relative_weight).format_plain() != weight
        for name, weight in expected_weights.items()
    ):
        raise AssertionError("Native topology phases/multiplicities changed")
    for cut, convention in zip(KNOWN_DIS_CUTS, audit.evidence.cut_conventions):
        expected_phase = -1 if cut.name == "external_external" else 1
        if convention.relative_phase != expected_phase:
            raise AssertionError("A phase-stripped cut orientation changed")
        raised_lines = tuple(line for line, order in cut.cut_orders if order)
        expected_application = (
            "none"
            if not raised_lines
            else "external_endpoint"
            if any(line in (5, 6) for line in raised_lines)
            else "encoded_in_kira"
        )
        if convention.derivative_application != expected_application:
            raise AssertionError("A raised-cut sign was assigned at the wrong stage")
    try:
        audit.require_result()
    except NativeDISSchemeUnavailableError:
        pass
    else:  # pragma: no cover
        raise AssertionError("An absent master boundary was accepted")
    return MappingProxyType(
        {
            "native_result": None,
            "blockers": audit.blockers,
            "evidence": audit.evidence,
        }
    )


__all__ = [
    "NativeCutConventionEvidence",
    "NativeDISDerivationEvidence",
    "NativeDISMPResult",
    "NativeDISSchemeChangeAudit",
    "NativeDISSchemeUnavailableError",
    "NativeSchemeAssemblyStage",
    "NativeSchemePrimitive",
    "SchemePrimitiveKind",
    "assemble_native_dis_mp",
    "audit_native_dis_scheme_change",
    "self_check",
]
