"""Fail-closed bridge for the two raised-external DIS reductions.

The ordinary DIS numerator handoffs are already reduced by the sixteen
cut-specialized Kira projects in :mod:`calculations.dis.python.physical`.  Two
external--external sectors are different: ``q_bubble`` contains a derivative
cut on ``D6=(p+q)^2`` and ``q_lsz`` contains one on ``D5=p^2``.  Their loop
integrals must therefore be reduced at finite ``x`` and finite ``p_squared``
before either external invariant is put on shell.

This module builds precisely those two side-effect-free Kira projects and
provides typed boundaries for loading their reductions.  It inserts the
analytic ``B``, ``Bcut``, or ``Tcut`` expression in all 28 cut-specialized and
four finite-virtuality records.  It deliberately does not choose the raised-cut
sign convention, apply the derivative distribution at a regulated one-sided
endpoint, choose oriented cut support, or attach graph weights: those inputs
are not fixed by the current source ledger.  Attempting to cross that boundary
raises :class:`UnresolvedPhysicalInputError`.

Importing this module never starts Kira.  :func:`self_check` only derives the
existing exact numerator handoffs and serializes the two projects in memory.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import factorial
from pathlib import Path
from types import MappingProxyType
from typing import Literal

from kirapy import IntegralFamily, KiraProject, ReductionBounds, ReductionResult
from symbolica import E, Expression

from calculations.dis.python.masters import (
    MASTER_SUPPORT,
    massless_cut_bubble,
    massless_cut_triangle,
    uncut_bubble,
)
from calculations.dis.python.physical import (
    DIS_GRAPH_SPECS,
    DIS_INTEGRAND_SOURCE,
    DIS_KINEMATICS,
    HISTORICAL_ALL_CUT_SOURCE,
    DISCutSpec,
    DISKinematics,
    DISKiraNumeratorHandoff,
    DISKiraProjectInput,
    DISMasterCoefficientAudit,
    DISPhysicalReductionAudit,
    NumeratorReductionAudit,
    build_kira_numerator_handoffs,
    build_kira_smoke_projects,
    canonical,
    epsilon,
)


Observable = Literal["F2", "FL"]
RaisedMasterKind = Literal["B((p+q)^2)", "B(p^2)"]
OrdinaryMasterKind = Literal[
    "B(q^2)",
    "Bcut(p^2)",
    "Bcut((p+q)^2)",
    "Tcut(p^2,q^2,(p+q)^2)",
]


@dataclass(frozen=True, slots=True)
class AssemblyBlocker:
    """One source input required beyond the analytic-master boundary."""

    key: str
    description: str
    source: str


class UnresolvedPhysicalInputError(RuntimeError):
    """Raised when code tries to use a deliberately unresolved convention."""

    def __init__(self, blockers: Sequence[AssemblyBlocker]) -> None:
        self.blockers = tuple(blockers)
        detail = "; ".join(
            f"{blocker.key}: {blocker.description}" for blocker in self.blockers
        )
        super().__init__(f"DIS physical assembly is blocked: {detail}")


@dataclass(frozen=True, slots=True)
class ExternalDerivativeCut:
    """Formal raised external cut in the historical paper convention."""

    line: Literal[5, 6]
    invariant: Expression
    order: int
    paper_normalization: Expression
    source: str

    def __post_init__(self) -> None:
        if self.order != 1:
            raise ValueError("The current DIS raised-external boundary expects delta-prime")


@dataclass(frozen=True, slots=True)
class RaisedExternalNumeratorHandoff:
    """One F2/FL numerator translated to a finite-virtuality family."""

    observable: Observable
    kept_indices: tuple[tuple[int, ...], ...]
    family_expression: Expression
    required_targets: tuple[Expression, ...]


@dataclass(frozen=True, slots=True)
class RaisedExternalKiraProject:
    """A generic Kira project plus its raised-cut and numerator provenance."""

    source_project_key: str
    project_input: DISKiraProjectInput
    derivative: ExternalDerivativeCut
    handoffs: tuple[RaisedExternalNumeratorHandoff, ...]

    @property
    def key(self) -> str:
        return self.project_input.key

    @property
    def project(self) -> KiraProject:
        return self.project_input.project


@dataclass(frozen=True, slots=True)
class RaisedExternalReductionAudit:
    """Exact coefficient of the generic bubble for one projected numerator."""

    project_key: str
    graph_name: str
    observable: Observable
    expected_master: Expression
    reduced_expression: Expression
    coefficient: Expression
    residual: Expression

    @property
    def exact(self) -> bool:
        return self.residual == E("0")


@dataclass(frozen=True, slots=True)
class RaisedExternalMasterIdentity:
    """The analytic uncut bubble expected after a generic Kira reduction."""

    kind: RaisedMasterKind
    indices: tuple[int, int, int]
    momentum_squared: Expression
    support_key: Literal["uncut_bubble"] = "uncut_bubble"


@dataclass(frozen=True, slots=True)
class RaisedExternalMasterBoundary:
    """Unweighted analytic master term before applying delta-prime.

    ``unweighted_term`` is mathematically fixed by the Kira coefficient and
    the phase-stripped analytic master.  It is not yet a graph contribution:
    the raised-cut sign, regulated derivative action, and graph weight remain
    explicit blockers.
    """

    audit: RaisedExternalReductionAudit
    identity: RaisedExternalMasterIdentity
    analytic_master: Expression
    unweighted_term: Expression
    cut: DISCutSpec
    external_lines: tuple[ExternalLineState, ExternalLineState]
    derivative: ExternalDerivativeCut
    blockers: tuple[AssemblyBlocker, ...]

    @property
    def physically_ready(self) -> bool:
        return not self.blockers

    def require_physical_inputs(self) -> None:
        if self.blockers:
            raise UnresolvedPhysicalInputError(self.blockers)


@dataclass(frozen=True, slots=True)
class OrdinaryMasterIdentity:
    """One analytic scalar master used by the 28 ordinary cut records."""

    kind: OrdinaryMasterKind
    indices: tuple[int, int, int]
    invariants: tuple[Expression, ...]
    support_key: Literal["uncut_bubble", "cut_bubble", "cut_triangle"]


@dataclass(frozen=True, slots=True)
class ExternalLineState:
    """The explicit D5 or D6 factor left outside the loop reduction.

    ``paper_cut_normalization`` records the historical positive
    ``2*pi*i/n!`` convention only.  It is not yet reconciled with the
    alternating reverse-unitarity sign required by algebraic ``1/D**a``
    cancellation.
    """

    line: Literal[5, 6]
    invariant: Expression
    denominator_power: int
    cut_order: int | None
    paper_cut_normalization: Expression | None

    @property
    def is_cut(self) -> bool:
        return self.cut_order is not None


@dataclass(frozen=True, slots=True)
class OrdinaryMasterBoundary:
    """Exact ordinary Kira coefficient after analytic master insertion.

    The external D5/D6 line states are retained symbolically.  This record is
    therefore the end of the unambiguous IBP/master stage, not an integrated
    or graph-weighted physical contribution.
    """

    audit: DISMasterCoefficientAudit
    identity: OrdinaryMasterIdentity
    analytic_master: Expression
    unweighted_loop_term: Expression
    cut: DISCutSpec
    external_lines: tuple[ExternalLineState, ExternalLineState]
    blockers: tuple[AssemblyBlocker, ...]

    @property
    def physically_ready(self) -> bool:
        return not self.blockers

    def require_physical_inputs(self) -> None:
        if self.blockers:
            raise UnresolvedPhysicalInputError(self.blockers)


@dataclass(frozen=True, slots=True)
class DISMasterInsertionAudit:
    """The complete 28 ordinary plus four raised analytic-master boundary."""

    reductions: DISPhysicalReductionAudit
    ordinary: tuple[OrdinaryMasterBoundary, ...]
    raised: tuple[RaisedExternalMasterBoundary, ...]

    @property
    def exact(self) -> bool:
        ordinary_keys = {
            (
                boundary.audit.handoff.project_key,
                boundary.audit.handoff.observable,
            )
            for boundary in self.ordinary
        }
        raised_keys = {
            (
                boundary.audit.project_key,
                boundary.audit.graph_name,
                boundary.audit.observable,
            )
            for boundary in self.raised
        }
        expected_raised_keys = {
            (spec.key, spec.graph_name, observable)
            for spec in _RAISED_PROJECT_SPECS
            for observable in ("F2", "FL")
        }
        expected_ordinary_keys = {
            (
                audit.handoff.project_key,
                audit.handoff.observable,
            )
            for audit in self.reductions.cut_specialized_coefficients
        }
        return (
            self.reductions.exact
            and len(self.ordinary) == len(expected_ordinary_keys) == 28
            and ordinary_keys == expected_ordinary_keys
            and len(self.raised) == 4
            and raised_keys == expected_raised_keys
            and all(boundary.audit.exact for boundary in self.raised)
        )

    @property
    def blockers(self) -> tuple[AssemblyBlocker, ...]:
        by_key = {
            blocker.key: blocker
            for boundary in (*self.ordinary, *self.raised)
            for blocker in boundary.blockers
        }
        return tuple(by_key[key] for key in sorted(by_key))


@dataclass(frozen=True, slots=True)
class _RaisedProjectSpec:
    source_key: str
    key: str
    family_name: str
    graph_name: Literal["q_bubble", "q_lsz"]
    derivative_line: Literal[5, 6]
    master_kind: RaisedMasterKind
    master_indices: tuple[int, int, int]


_RAISED_PROJECT_SPECS: tuple[_RaisedProjectSpec, ...] = (
    _RaisedProjectSpec(
        source_key="q_bubble__external_external__d123",
        key="q_bubble__external_external_finite_virtuality__d123",
        family_name="dis_q_bubble__external_external_finite_virtuality__d123",
        graph_name="q_bubble",
        derivative_line=6,
        master_kind="B((p+q)^2)",
        master_indices=(1, 0, 1),
    ),
    _RaisedProjectSpec(
        source_key="q_lsz__external_external__d123",
        key="q_lsz__external_external_finite_virtuality__d123",
        family_name="dis_q_lsz__external_external_finite_virtuality__d123",
        graph_name="q_lsz",
        derivative_line=5,
        master_kind="B(p^2)",
        master_indices=(1, 1, 0),
    ),
)


def _ordered(expressions: Sequence[Expression]) -> tuple[Expression, ...]:
    return tuple(
        sorted(
            set(expressions),
            key=lambda expression: expression.format_plain(),
        )
    )


def _translate_family_expression(
    expression: Expression,
    *,
    old_family: IntegralFamily,
    new_family: IntegralFamily,
    indices: Sequence[tuple[int, ...]],
) -> Expression:
    translated = expression
    for integral_indices in indices:
        translated = translated.replace(
            old_family(*integral_indices),
            new_family(*integral_indices),
        )
    return translated


def _derivative_invariant(
    line: Literal[5, 6],
    kinematics: DISKinematics,
) -> Expression:
    if line == 5:
        return kinematics.incoming_virtuality
    return kinematics.final_state_invariant


def build_raised_external_kira_projects(
    *,
    source_projects: Mapping[str, DISKiraProjectInput] | None = None,
    numerator_handoffs: Sequence[DISKiraNumeratorHandoff] | None = None,
    numerator_audits: Sequence[NumeratorReductionAudit] | None = None,
    bounds: ReductionBounds | None = None,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> Mapping[str, RaisedExternalKiraProject]:
    """Build the two finite-virtuality raised-external Kira projects.

    Only loop cut lines are sent to :meth:`DISKinematics.kira_kinematics`.
    Both sectors have no internal cut line, so ``x`` and ``p_squared`` remain
    independent Kira invariants even though their external cut metadata is
    retained on :class:`DISKiraProjectInput`.
    """

    smoke_projects = source_projects or build_kira_smoke_projects(
        bounds=bounds,
        kinematics=kinematics,
    )
    handoffs = tuple(
        numerator_handoffs
        or build_kira_numerator_handoffs(
            projects=smoke_projects,
            numerator_audits=numerator_audits,
        )
    )
    handoffs_by_project: dict[str, list[DISKiraNumeratorHandoff]] = {}
    for handoff in handoffs:
        if handoff.requires_external_derivative:
            handoffs_by_project.setdefault(handoff.project_key, []).append(handoff)

    result: dict[str, RaisedExternalKiraProject] = {}
    for spec in _RAISED_PROJECT_SPECS:
        try:
            source = smoke_projects[spec.source_key]
            source_handoffs = tuple(handoffs_by_project[spec.source_key])
        except KeyError as error:
            raise ValueError(
                f"Missing raised-external source handoff {spec.source_key}"
            ) from error
        if source.graph_name != spec.graph_name or source.cut is None:
            raise ValueError(f"Invalid raised-external source project {spec.source_key}")
        if source.cut.name != "external_external":
            raise ValueError(f"{spec.source_key} is not an external--external cut")
        cut_orders = dict(source.cut.cut_orders)
        if cut_orders.get(spec.derivative_line) != 1:
            raise ValueError(
                f"{spec.source_key} does not have the expected raised D{spec.derivative_line}"
            )
        if {handoff.observable for handoff in source_handoffs} != {"F2", "FL"}:
            raise ValueError(f"{spec.source_key} needs exactly F2 and FL handoffs")

        source_family = source.project.family
        family = IntegralFamily(
            name=spec.family_name,
            loop_momenta=source_family.loop_momenta,
            propagators=source_family.propagators,
            top_level_sectors=source_family.top_level_sectors,
            cut_propagators=source.cut.loop_cut_lines,
            zero_sectors=source_family.zero_sectors,
        )
        translated_handoffs: list[RaisedExternalNumeratorHandoff] = []
        all_targets: list[Expression] = []
        for handoff in sorted(source_handoffs, key=lambda item: item.observable):
            family_expression = _translate_family_expression(
                handoff.family_expression,
                old_family=source_family,
                new_family=family,
                indices=handoff.kept_indices,
            )
            required_targets = _ordered(
                tuple(family(*indices) for indices in handoff.kept_indices)
            )
            all_targets.extend(required_targets)
            translated_handoffs.append(
                RaisedExternalNumeratorHandoff(
                    observable=handoff.observable,
                    kept_indices=handoff.kept_indices,
                    family_expression=family_expression,
                    required_targets=required_targets,
                )
            )

        expected_master = family(*spec.master_indices)
        targets = _ordered((*all_targets, expected_master))
        project = KiraProject(
            family=family,
            # Passing only internal cut lines is the essential distinction
            # from the support-specialized smoke project.
            kinematics=kinematics.kira_kinematics(
                cut_lines=source.cut.loop_cut_lines
            ),
            targets=targets,
            bounds=bounds or source.project.bounds,
            dimension=kinematics.dimension,
            preferred_masters=(expected_master,),
            check_masters=True,
            reconstruct_mass=True,
        )
        project_input = DISKiraProjectInput(
            key=spec.key,
            graph_name=spec.graph_name,
            retained_loop_lines=source.retained_loop_lines,
            cut=source.cut,
            project=project,
            expected_master_indices=spec.master_indices,
            expected_master_name=spec.master_kind,
            targets_explicit=True,
            limitation=(
                "Finite-virtuality IBP input only. The external delta-prime "
                "endpoint rule and physical graph weight remain unresolved."
            ),
        )
        derivative = ExternalDerivativeCut(
            line=spec.derivative_line,
            invariant=_derivative_invariant(spec.derivative_line, kinematics),
            order=1,
            paper_normalization=2 * Expression.PI * Expression.I,
            source=HISTORICAL_ALL_CUT_SOURCE,
        )
        result[spec.key] = RaisedExternalKiraProject(
            source_project_key=spec.source_key,
            project_input=project_input,
            derivative=derivative,
            handoffs=tuple(translated_handoffs),
        )
    return MappingProxyType(result)


def audit_raised_external_reductions(
    reductions: Mapping[str, ReductionResult],
    *,
    projects: Mapping[str, RaisedExternalKiraProject] | None = None,
) -> tuple[RaisedExternalReductionAudit, ...]:
    """Extract the four generic bubble coefficients from completed Kira jobs."""

    project_records = projects or build_raised_external_kira_projects()
    missing_projects = tuple(sorted(set(project_records) - set(reductions)))
    if missing_projects:
        raise ValueError(
            "Missing raised-external Kira reductions: " + ", ".join(missing_projects)
        )

    audits: list[RaisedExternalReductionAudit] = []
    for key, record in sorted(project_records.items()):
        result = reductions[key]
        result.require_complete()
        project_input = record.project_input
        master_indices = project_input.expected_master_indices
        if master_indices is None:
            raise ValueError(f"No expected generic master declared for {key}")
        expected_master = record.project.family(*master_indices)
        if set(result.masters) != {expected_master}:
            raise ValueError(
                f"{key} expected only {expected_master}, got {result.masters}"
            )
        for handoff in record.handoffs:
            missing_targets = tuple(
                target for target in handoff.required_targets if target not in result.rules
            )
            if missing_targets:
                raise ValueError(f"{key}:{handoff.observable} misses {missing_targets}")
            reduced = result.apply(handoff.family_expression)
            coefficient = canonical(reduced.replace(expected_master, E("1")))
            residual = canonical(reduced - coefficient * expected_master)
            audits.append(
                RaisedExternalReductionAudit(
                    project_key=key,
                    graph_name=project_input.graph_name,
                    observable=handoff.observable,
                    expected_master=expected_master,
                    reduced_expression=reduced,
                    coefficient=coefficient,
                    residual=residual,
                )
            )
    if len(audits) != 4:
        raise AssertionError(f"Expected four raised-external audits, got {len(audits)}")
    return tuple(audits)


def _master_identity(
    project: RaisedExternalKiraProject,
    *,
    kinematics: DISKinematics,
) -> RaisedExternalMasterIdentity:
    indices = project.project_input.expected_master_indices
    name = project.project_input.expected_master_name
    if indices is None or len(indices) != 3 or name not in {"B((p+q)^2)", "B(p^2)"}:
        raise ValueError(f"Invalid raised-external master metadata for {project.key}")
    momentum_squared = (
        kinematics.final_state_invariant
        if name == "B((p+q)^2)"
        else kinematics.incoming_virtuality
    )
    return RaisedExternalMasterIdentity(
        kind=name,
        indices=indices,
        momentum_squared=momentum_squared,
    )


def _ordinary_master_identity(
    project: DISKiraProjectInput,
    *,
    kinematics: DISKinematics,
) -> OrdinaryMasterIdentity:
    indices = project.expected_master_indices
    if indices is None or len(indices) != 3:
        raise ValueError(f"Invalid ordinary master indices for {project.key}")
    fixed_indices = (indices[0], indices[1], indices[2])
    name = project.expected_master_name
    if name == "B(q^2)":
        return OrdinaryMasterIdentity(
            kind="B(q^2)",
            indices=fixed_indices,
            invariants=(-kinematics.photon_scale,),
            support_key="uncut_bubble",
        )
    if name == "Bcut(p^2)":
        return OrdinaryMasterIdentity(
            kind="Bcut(p^2)",
            indices=fixed_indices,
            invariants=(kinematics.incoming_virtuality,),
            support_key="cut_bubble",
        )
    if name == "Bcut((p+q)^2)":
        return OrdinaryMasterIdentity(
            kind="Bcut((p+q)^2)",
            indices=fixed_indices,
            invariants=(kinematics.final_state_invariant,),
            support_key="cut_bubble",
        )
    if name == "Tcut(p^2,q^2,(p+q)^2)":
        return OrdinaryMasterIdentity(
            kind="Tcut(p^2,q^2,(p+q)^2)",
            indices=fixed_indices,
            invariants=(
                kinematics.incoming_virtuality,
                -kinematics.photon_scale,
                kinematics.final_state_invariant,
            ),
            support_key="cut_triangle",
        )
    raise ValueError(f"Unknown ordinary analytic master {name!r} for {project.key}")


def _analytic_master_value(
    identity: OrdinaryMasterIdentity,
    *,
    kinematics: DISKinematics,
) -> Expression:
    arguments = {
        "dimension": 4 - 2 * epsilon,
        "epsilon": epsilon,
        "mu_squared": kinematics.renormalization_scale,
        "euler_gamma": Expression.EULER_GAMMA,
    }
    if identity.support_key == "uncut_bubble":
        return uncut_bubble(identity.invariants[0], **arguments)
    if identity.support_key == "cut_bubble":
        return massless_cut_bubble(identity.invariants[0], **arguments)
    return massless_cut_triangle(*identity.invariants, **arguments)


def _external_line_states(
    project: DISKiraProjectInput,
    *,
    kinematics: DISKinematics,
) -> tuple[ExternalLineState, ExternalLineState]:
    if project.cut is None:
        raise ValueError(f"Physical master boundary {project.key} has no cut")
    graph = DIS_GRAPH_SPECS[project.graph_name]
    cut_lines = set(project.cut.initial_cut_lines + project.cut.final_cut_lines)
    cut_orders = dict(project.cut.cut_orders)
    d5_order = cut_orders[5] if 5 in cut_lines else None
    d6_order = cut_orders[6] if 6 in cut_lines else None
    return (
        ExternalLineState(
            line=5,
            invariant=kinematics.incoming_virtuality,
            denominator_power=graph.powers[4],
            cut_order=d5_order,
            paper_cut_normalization=(
                None
                if d5_order is None
                else 2 * Expression.PI * Expression.I / factorial(d5_order)
            ),
        ),
        ExternalLineState(
            line=6,
            invariant=kinematics.final_state_invariant,
            denominator_power=graph.powers[5],
            cut_order=d6_order,
            paper_cut_normalization=(
                None
                if d6_order is None
                else 2 * Expression.PI * Expression.I / factorial(d6_order)
            ),
        ),
    )


def _ordinary_blockers(
    project: DISKiraProjectInput,
    identity: OrdinaryMasterIdentity,
) -> tuple[AssemblyBlocker, ...]:
    cut = project.cut
    if cut is None:
        raise ValueError(f"Physical master boundary {project.key} has no cut")
    blockers = [
        AssemblyBlocker(
            key=f"{project.key}:graph-weight",
            description=(
                "The universal all-cut plus sign and unit embedding symmetry "
                "do not determine this active graph's full color/graph weight."
            ),
            source=DIS_GRAPH_SPECS[project.graph_name].source,
        )
    ]
    raised_lines = tuple(
        line for line, order in cut.cut_orders if order > 0
    )
    if raised_lines:
        blockers.append(
            AssemblyBlocker(
                key=f"{project.key}:raised-cut-sign",
                description=(
                    "The historical positive delta-derivative normalization "
                    "has not been reconciled with the alternating "
                    "reverse-unitarity sign for a raised cut denominator "
                    f"on {tuple(f'D{line}' for line in raised_lines)}."
                ),
                source=HISTORICAL_ALL_CUT_SOURCE,
            )
        )
    support = MASTER_SUPPORT[identity.support_key]
    if support.theta_factors:
        blockers.append(
            AssemblyBlocker(
                key=f"{project.key}:cut-orientation",
                description=(
                    "The analytic cut master is inserted, but selecting its "
                    "theta-function support requires the missing oriented-cut ledger."
                ),
                source=HISTORICAL_ALL_CUT_SOURCE,
            )
        )
    return tuple(blockers)


def build_ordinary_master_boundaries(
    reduction_audit: DISPhysicalReductionAudit,
    *,
    projects: Mapping[str, DISKiraProjectInput] | None = None,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> tuple[OrdinaryMasterBoundary, ...]:
    """Insert the analytic scalar master in all 28 non-raised records."""

    if not reduction_audit.exact:
        raise ValueError("Cannot insert masters into an inexact physical reduction")
    project_records = projects or build_kira_smoke_projects(kinematics=kinematics)
    boundaries: list[OrdinaryMasterBoundary] = []
    for audit in reduction_audit.cut_specialized_coefficients:
        try:
            project = project_records[audit.handoff.project_key]
        except KeyError as error:
            raise ValueError(
                f"Unknown ordinary Kira project {audit.handoff.project_key}"
            ) from error
        if project.cut is None:
            raise ValueError(f"Physical project {project.key} has no cut")
        identity = _ordinary_master_identity(project, kinematics=kinematics)
        expected_master = project.project.family(*identity.indices)
        if audit.expected_master != expected_master or audit.residual != E("0"):
            raise ValueError(
                f"Master mismatch for {audit.handoff.project_key}:"
                f"{audit.handoff.observable}"
            )
        analytic_master = _analytic_master_value(identity, kinematics=kinematics)
        boundaries.append(
            OrdinaryMasterBoundary(
                audit=audit,
                identity=identity,
                analytic_master=analytic_master,
                unweighted_loop_term=canonical(audit.coefficient * analytic_master),
                cut=project.cut,
                external_lines=_external_line_states(project, kinematics=kinematics),
                blockers=_ordinary_blockers(project, identity),
            )
        )
    if len(boundaries) != 28:
        raise AssertionError(
            f"Expected 28 ordinary analytic-master boundaries, got {len(boundaries)}"
        )
    return tuple(boundaries)


def _boundary_blockers(
    project: RaisedExternalKiraProject,
) -> tuple[AssemblyBlocker, ...]:
    endpoint = (
        "The regulated one-sided lower-bound action of delta-prime(p^2), "
        "including cancellation against the bubble, is not fixed."
        if project.derivative.line == 5
        else (
            "The regulated action of delta-prime((p+q)^2), including "
            "cancellation against the bubble and the change of variable to "
            "1-x, is not fixed."
        )
    )
    return (
        AssemblyBlocker(
            key=f"{project.key}:raised-cut-sign",
            description=(
                "The historical positive delta-derivative normalization has "
                "not been reconciled with the alternating reverse-unitarity "
                f"sign for D{project.derivative.line}^2."
            ),
            source=HISTORICAL_ALL_CUT_SOURCE,
        ),
        AssemblyBlocker(
            key=f"{project.key}:delta-prime-endpoint",
            description=endpoint,
            source=HISTORICAL_ALL_CUT_SOURCE,
        ),
        AssemblyBlocker(
            key=f"{project.key}:graph-weight",
            description=(
                "The universal all-cut plus sign and unit embedding symmetry "
                "do not determine this active graph's full color/graph weight."
            ),
            source=DIS_GRAPH_SPECS[project.project_input.graph_name].source,
        ),
    )


def build_raised_external_master_boundaries(
    audits: Sequence[RaisedExternalReductionAudit],
    *,
    projects: Mapping[str, RaisedExternalKiraProject] | None = None,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> tuple[RaisedExternalMasterBoundary, ...]:
    """Insert analytic bubbles but stop before unresolved physical operations."""

    project_records = projects or build_raised_external_kira_projects()
    master_arguments = {
        "dimension": 4 - 2 * epsilon,
        "epsilon": epsilon,
        "mu_squared": kinematics.renormalization_scale,
        "euler_gamma": Expression.EULER_GAMMA,
    }
    boundaries: list[RaisedExternalMasterBoundary] = []
    for audit in audits:
        if not audit.exact:
            raise ValueError(
                f"Cannot insert a non-exact reduction {audit.project_key}:{audit.observable}"
            )
        try:
            project = project_records[audit.project_key]
        except KeyError as error:
            raise ValueError(f"Unknown raised-external project {audit.project_key}") from error
        if project.project_input.cut is None:
            raise ValueError(f"Raised project {project.key} has no cut")
        identity = _master_identity(project, kinematics=kinematics)
        expected_master = project.project.family(*identity.indices)
        if audit.expected_master != expected_master:
            raise ValueError(
                f"Master mismatch for {audit.project_key}:{audit.observable}"
            )
        analytic_master = uncut_bubble(
            identity.momentum_squared,
            **master_arguments,
        )
        boundaries.append(
            RaisedExternalMasterBoundary(
                audit=audit,
                identity=identity,
                analytic_master=analytic_master,
                unweighted_term=canonical(audit.coefficient * analytic_master),
                cut=project.project_input.cut,
                external_lines=_external_line_states(
                    project.project_input,
                    kinematics=kinematics,
                ),
                derivative=project.derivative,
                blockers=_boundary_blockers(project),
            )
        )
    return tuple(boundaries)


def build_master_insertion_audit(
    reductions: DISPhysicalReductionAudit,
    raised_audits: Sequence[RaisedExternalReductionAudit],
    *,
    ordinary_projects: Mapping[str, DISKiraProjectInput] | None = None,
    raised_projects: Mapping[str, RaisedExternalKiraProject] | None = None,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> DISMasterInsertionAudit:
    """Build the complete analytic-master boundary for all 32 handoffs."""

    ordinary = build_ordinary_master_boundaries(
        reductions,
        projects=ordinary_projects,
        kinematics=kinematics,
    )
    raised = build_raised_external_master_boundaries(
        raised_audits,
        projects=raised_projects,
        kinematics=kinematics,
    )
    audit = DISMasterInsertionAudit(
        reductions=reductions,
        ordinary=ordinary,
        raised=raised,
    )
    if not audit.exact:
        raise AssertionError("The complete DIS analytic-master insertion is not exact")
    return audit


def require_resolved_physical_assembly(
    boundaries: Sequence[
        OrdinaryMasterBoundary | RaisedExternalMasterBoundary
    ],
) -> None:
    """Fail unless every sign, support, endpoint, and graph weight is supplied."""

    raised_source_keys = {spec.source_key for spec in _RAISED_PROJECT_SPECS}
    expected_keys = {
        ("cut-specialized", key, observable)
        for key in build_kira_smoke_projects()
        if key not in raised_source_keys
        for observable in ("F2", "FL")
    } | {
        ("finite-virtuality", spec.key, observable)
        for spec in _RAISED_PROJECT_SPECS
        for observable in ("F2", "FL")
    }
    actual_keys = {
        (
            "cut-specialized",
            boundary.audit.handoff.project_key,
            boundary.audit.handoff.observable,
        )
        if isinstance(boundary, OrdinaryMasterBoundary)
        else (
            "finite-virtuality",
            boundary.audit.project_key,
            boundary.audit.observable,
        )
        for boundary in boundaries
    }
    blockers_by_key = {
        blocker.key: blocker
        for boundary in boundaries
        for blocker in boundary.blockers
    }
    if len(boundaries) != 32 or actual_keys != expected_keys:
        missing = tuple(sorted(expected_keys - actual_keys))
        extra = tuple(sorted(actual_keys - expected_keys))
        blockers_by_key["complete-master-boundary"] = AssemblyBlocker(
            key="complete-master-boundary",
            description=(
                "Physical assembly requires exactly the complete 32-record "
                f"master boundary; missing={missing}, extra={extra}."
            ),
            source=DIS_INTEGRAND_SOURCE,
        )
    blockers = tuple(
        blockers_by_key[key] for key in sorted(blockers_by_key)
    )
    if blockers:
        raise UnresolvedPhysicalInputError(blockers)


def self_check() -> Mapping[str, object]:
    """Validate the finite-virtuality projects without launching Kira."""

    projects = build_raised_external_kira_projects()
    expected_keys = tuple(spec.key for spec in _RAISED_PROJECT_SPECS)
    if tuple(projects) != expected_keys:
        raise AssertionError(f"Unexpected raised-external projects: {tuple(projects)}")

    expected_indices = {
        "q_bubble__external_external_finite_virtuality__d123": {
            (0, 0, 1),
            (1, -1, 1),
            (1, 0, 0),
            (1, 0, 1),
        },
        "q_lsz__external_external_finite_virtuality__d123": {
            (0, 1, 0),
            (1, 0, 0),
            (1, 1, -1),
            (1, 1, 0),
        },
    }
    serialized_paths: dict[str, tuple[str, ...]] = {}
    for key, record in projects.items():
        project = record.project
        invariants = {
            invariant.expression for invariant in project.kinematics.kinematic_invariants
        }
        if invariants != {
            DIS_KINEMATICS.bjorken_x,
            DIS_KINEMATICS.incoming_virtuality,
            DIS_KINEMATICS.photon_scale,
        }:
            raise AssertionError(f"{key} did not preserve finite x and p_squared")
        if project.family.cut_propagators:
            raise AssertionError(f"{key} incorrectly sent an external cut to Kira")
        if {handoff.observable for handoff in record.handoffs} != {"F2", "FL"}:
            raise AssertionError(f"{key} does not contain F2 and FL")
        actual_indices = {
            indices for handoff in record.handoffs for indices in handoff.kept_indices
        }
        if actual_indices != expected_indices[key]:
            raise AssertionError(f"Unexpected target indices for {key}: {actual_indices}")
        files = project.serialize()
        paths = tuple(files)
        if "config/kinematics.yaml" not in paths or "targets" not in paths:
            raise AssertionError(f"Incomplete serialization for {key}")
        aliases = set(files.symbol_aliases.values())
        if not {
            DIS_KINEMATICS.bjorken_x,
            DIS_KINEMATICS.incoming_virtuality,
            DIS_KINEMATICS.photon_scale,
        } <= aliases:
            raise AssertionError(f"{key} serialization dropped a finite invariant")
        serialized_paths[key] = paths

    # Exercise coefficient extraction and the analytic-master boundary using
    # complete synthetic identity/zero rules.  This validates the handoff
    # mechanics without manufacturing a physical endpoint convention or
    # starting Kira.
    synthetic_reductions: dict[str, ReductionResult] = {}
    for key, record in projects.items():
        identity = _master_identity(record, kinematics=DIS_KINEMATICS)
        master = record.project.family(*identity.indices)
        rules = {
            target: master if target == master else E("0")
            for target in record.project.targets
        }
        synthetic_reductions[key] = ReductionResult(
            family_name=record.project.family.name,
            arity=record.project.family.arity,
            requested_targets=record.project.targets,
            rules=rules,
            masters=(master,),
            workdir=Path("."),
        )
    synthetic_audits = audit_raised_external_reductions(
        synthetic_reductions,
        projects=projects,
    )
    if len(synthetic_audits) != 4 or not all(
        audit.exact for audit in synthetic_audits
    ):
        raise AssertionError("Synthetic raised-external coefficient audit failed")
    boundaries = build_raised_external_master_boundaries(
        synthetic_audits,
        projects=projects,
    )
    if len(boundaries) != 4 or any(
        boundary.physically_ready or not boundary.blockers
        for boundary in boundaries
    ):
        raise AssertionError("Raised-external boundaries must remain fail-closed")
    expected_external_orders = {
        "q_bubble": {5: 0, 6: 1},
        "q_lsz": {5: 1, 6: 0},
    }
    for boundary in boundaries:
        actual_orders = {
            state.line: state.cut_order for state in boundary.external_lines
        }
        if actual_orders != expected_external_orders[boundary.audit.graph_name]:
            raise AssertionError(
                f"Raised external cut pair changed: {actual_orders}"
            )
        if any(
            state.paper_cut_normalization is None
            for state in boundary.external_lines
            if state.is_cut
        ):
            raise AssertionError("An external cut lost its paper normalization")
    try:
        require_resolved_physical_assembly(boundaries)
    except UnresolvedPhysicalInputError:
        pass
    else:  # pragma: no cover - protects the scientific boundary itself
        raise AssertionError("Unresolved raised-external boundary was accepted")
    if any(
        MASTER_SUPPORT[boundary.identity.support_key].theta_factors
        for boundary in boundaries
    ):
        raise AssertionError("An uncut bubble unexpectedly acquired cut support")

    return MappingProxyType(
        {
            "projects": tuple(projects),
            "targets": MappingProxyType(
                {key: tuple(sorted(indices)) for key, indices in expected_indices.items()}
            ),
            "serialized_paths": MappingProxyType(serialized_paths),
            "preserved_invariants": (
                DIS_KINEMATICS.bjorken_x,
                DIS_KINEMATICS.incoming_virtuality,
                DIS_KINEMATICS.photon_scale,
            ),
            "physical_boundary": "blocked",
            "blockers": tuple(
                blocker
                for boundary in boundaries
                for blocker in boundary.blockers
            ),
        }
    )


__all__ = [
    "AssemblyBlocker",
    "DISMasterInsertionAudit",
    "ExternalDerivativeCut",
    "ExternalLineState",
    "OrdinaryMasterBoundary",
    "OrdinaryMasterIdentity",
    "RaisedExternalKiraProject",
    "RaisedExternalMasterBoundary",
    "RaisedExternalMasterIdentity",
    "RaisedExternalNumeratorHandoff",
    "RaisedExternalReductionAudit",
    "UnresolvedPhysicalInputError",
    "audit_raised_external_reductions",
    "build_master_insertion_audit",
    "build_ordinary_master_boundaries",
    "build_raised_external_kira_projects",
    "build_raised_external_master_boundaries",
    "require_resolved_physical_assembly",
    "self_check",
]
