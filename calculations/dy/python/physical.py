"""Native Symbolica assembly of the leading-power NLO Drell--Yan result.

The graph layer uses the same native Spenso momentum-and-mass representation as
the repository's cross-box walkthrough.  The notebook simplifies its editable
Dirac chains to exact scalar polynomials before passing them into this assembly
module. Kira objects are derived only at the reduction boundary; they are not
graph inputs.

The retained Mathematica notebook and the manuscript do not agree in their
last presentation cells.  The data model therefore keeps three different
objects explicit:

* the consistently transverse native result;
* the presentation transcribed from saved Mathematica output cells;
* the manuscript formula.

No residual is silently set to zero.
"""

from __future__ import annotations

from dataclasses import dataclass, replace as dataclass_replace
from itertools import combinations, product
from math import prod
from types import MappingProxyType
from typing import TYPE_CHECKING, Mapping, Sequence

from symbolica import E, Expression

from notebooks.ludy import (
    ApartTerm,
    NumeratorReduction,
    build_cut_kira_project,
    find_loop_propagator_indices,
    normalize_rational,
    prepare_pre_ibp,
    project_cutset,
    propagator_denominators,
    reduce_numerator,
    replace_all,
)

if TYPE_CHECKING:
    from kirapy import KiraProject, ReductionResult


@dataclass(frozen=True, slots=True)
class DYContext:
    """Notebook-owned symbols consumed by the DY assembly library."""

    d: Expression
    epsilon: Expression
    p1: object
    p2: object
    k: object
    kk: Expression
    kp1: Expression
    kp2: Expression
    p1_squared: Expression
    p2_squared: Expression
    p1_dot_p2: Expression
    loop_scalar_products: tuple[Expression, ...]
    s: Expression
    z: Expression
    mass_squared: Expression
    alpha_s: Expression
    color_f: Expression
    color_t: Expression
    electric_charge: Expression
    strong_coupling: Expression
    color_count: Expression
    lambda1_squared: Expression
    lambda2_squared: Expression
    mu_r_squared: Expression
    pi: Expression


@dataclass(slots=True)
class DYGraphSpec:
    """Editable physical graph data, independent of Kira model objects.

    ``cut_weights`` contains the cut sign and multiplicity *relative to the
    analytic-master convention in masters.py*.  ``scheme_observable_phase``
    is the independent physical graph/process phase in the DY ``MP - PM``
    observable.  Keeping those two factors separate prevents a cut's scheme
    membership from silently carrying a physical sign.

    The retained Mathematica objects can display the opposite sign because
    they absorb a historical Cutkosky phase into the cut master itself.
    ``mp_only_cuts`` and ``pm_only_cuts`` are unsigned membership data.  Their
    difference coefficient is exactly ``1_MP - 1_PM``; cuts absent from both
    tuples are common to the two prescriptions and cancel.  In the present DY
    graph input every complementary cut is MP-only and therefore has
    membership coefficient ``+1``.
    """

    name: str
    propagators: tuple[tuple[Expression, Expression], ...]
    cutsets: dict[str, tuple[int, ...]]
    propagator_powers: tuple[int, ...]
    numerator_divisor: Expression
    cut_weights: Mapping[str, Expression]
    scheme_observable_phase: Expression
    analytic_cuts: tuple[str, ...] = ()
    mp_only_cuts: tuple[str, ...] = ()
    pm_only_cuts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Reject graph inputs whose physical and projected data cannot agree."""

        loop_count = len(self.loop_propagator_indices)
        if len(self.propagator_powers) != loop_count:
            raise ValueError(
                f"{self.name}: expected {loop_count} propagator powers, got "
                f"{len(self.propagator_powers)}"
            )
        for cut_name, cutset in self.cutsets.items():
            if len(cutset) != len(self.propagators):
                raise ValueError(
                    f"{self.name}/{cut_name}: cut mask has length {len(cutset)}, "
                    f"expected {len(self.propagators)}"
                )
            if any(bit not in (0, 1) for bit in cutset):
                raise ValueError(
                    f"{self.name}/{cut_name}: cut masks may contain only 0 or 1"
                )
        unknown_analytic_cuts = set(self.analytic_cuts) - self.cutsets.keys()
        if unknown_analytic_cuts:
            raise ValueError(
                f"{self.name}: unknown analytic cuts "
                f"{sorted(unknown_analytic_cuts)}"
            )
        declared_cut_weights = set(self.cut_weights)
        expected_cut_weights = set(self.cutsets)
        if declared_cut_weights != expected_cut_weights:
            missing = sorted(expected_cut_weights - declared_cut_weights)
            unknown = sorted(declared_cut_weights - expected_cut_weights)
            raise ValueError(
                f"{self.name}: cut weights must cover exactly the cut masks; "
                f"missing={missing}, unknown={unknown}"
            )
        if len(set(self.mp_only_cuts)) != len(self.mp_only_cuts):
            raise ValueError(f"{self.name}: duplicate MP-only cut membership")
        if len(set(self.pm_only_cuts)) != len(self.pm_only_cuts):
            raise ValueError(f"{self.name}: duplicate PM-only cut membership")
        overlap = set(self.mp_only_cuts) & set(self.pm_only_cuts)
        if overlap:
            raise ValueError(
                f"{self.name}: cuts cannot be both MP-only and PM-only: "
                f"{sorted(overlap)}"
            )
        unknown_scheme_cuts = (
            set(self.mp_only_cuts) | set(self.pm_only_cuts)
        ) - self.cutsets.keys()
        if unknown_scheme_cuts:
            raise ValueError(
                f"{self.name}: unknown MP-PM cuts "
                f"{sorted(unknown_scheme_cuts)}"
            )

    def scheme_membership_coefficient(self, cut_name: str) -> Expression:
        """Return the unsigned-set coefficient ``1_MP - 1_PM`` for a cut."""

        if cut_name not in self.cutsets:
            raise KeyError(f"{self.name}: unknown cut {cut_name!r}")
        return E(
            str(
                int(cut_name in self.mp_only_cuts)
                - int(cut_name in self.pm_only_cuts)
            )
        )

    @property
    def loop_propagator_indices(self) -> tuple[int, ...]:
        """Positions of loop-dependent lines in full graph order."""

        return tuple(find_loop_propagator_indices(self.propagators))

    @property
    def all_denominators(self) -> tuple[Expression, ...]:
        """Every graph denominator, including the external cut lines."""

        return tuple(propagator_denominators(self.propagators))

    @property
    def denominators(self) -> tuple[Expression, ...]:
        """Loop denominators in graph order, derived from momentum and mass."""

        all_denominators = self.all_denominators
        return tuple(
            all_denominators[index]
            for index in self.loop_propagator_indices
        )

    @property
    def projected_cutsets(self) -> dict[str, tuple[int, ...]]:
        """Cut masks projected onto the ordered loop propagators."""

        loop_indices = self.loop_propagator_indices
        return {
            name: project_cutset(mask, loop_indices)
            for name, mask in self.cutsets.items()
        }

    @property
    def requires_apart(self) -> bool:
        """Whether the graph has more loop lines than scalar coordinates."""

        return len(self.loop_propagator_indices) > 3


DYProjectKey = tuple[str, str, tuple[int, ...]]


@dataclass(frozen=True, slots=True)
class DYProjectPlan:
    """Graph-native Kira projects and deduplicated physical routes."""

    projects: Mapping[DYProjectKey, "KiraProject"]
    route_projects: Mapping[DYProjectKey, DYProjectKey]

    def project_key(
        self,
        graph_name: str,
        cut_name: str,
        source_indices: Sequence[int],
    ) -> DYProjectKey:
        route = (graph_name, cut_name, tuple(source_indices))
        try:
            return self.route_projects[route]
        except KeyError as error:
            raise KeyError(f"No Kira project for physical route {route}") from error


def _selected_cut_indices(
    graph: DYGraphSpec,
    cut_name: str,
    source_indices: Sequence[int],
) -> tuple[int, ...] | None:
    cutset = graph.cutsets[cut_name]
    required_sources = {
        source
        for source in graph.loop_propagator_indices
        if cutset[source]
    }
    if not required_sources <= set(source_indices):
        return None
    return project_cutset(cutset, source_indices)


def _project_family_name(project_key: DYProjectKey) -> str:
    graph_name, cut_name, source_indices = project_key
    graph_slug = "_".join(graph_name.replace("-", " ").split())
    sources = "_".join(f"d{index + 1}" for index in source_indices)
    return f"{graph_slug}_cut{cut_name}_{sources}"


def build_dy_kira_projects(
    graphs: Mapping[str, DYGraphSpec],
    context: DYContext,
) -> DYProjectPlan:
    """Build and structurally deduplicate graph-native DY projects."""

    candidates = []
    for graph_name, graph in graphs.items():
        loop_sources = graph.loop_propagator_indices
        has_internal_mass = any(
            mass_squared != E("0")
            for source, (_momentum, mass_squared) in enumerate(graph.propagators)
            if source in loop_sources
        )
        if graph.requires_apart:
            target_values = (1, 0, -1)
            bounds = (9, 4, 2)
        elif has_internal_mass:
            target_values = (2, 1, 0, -1, -2)
            bounds = (9, 6, 3)
        else:
            target_values = (1, 0, -1, -2)
            bounds = (9, 4, 2)
        for cut_name, cutset in graph.cutsets.items():
            if cut_name in graph.analytic_cuts:
                continue
            required_count = sum(cutset[source] for source in loop_sources)
            if required_count > 3:
                continue
            for source_indices in combinations(loop_sources, 3):
                route_key = (graph_name, cut_name, source_indices)
                candidates.append(
                    (
                        route_key,
                        graph,
                        target_values,
                        bounds,
                        _selected_cut_indices(graph, cut_name, source_indices),
                    )
                )

    projects: dict[DYProjectKey, "KiraProject"] = {}
    route_projects: dict[DYProjectKey, DYProjectKey] = {}
    canonical_candidates = []
    loop_reversal = ((context.kp1, -context.kp1), (context.kp2, -context.kp2))
    for candidate in sorted(candidates, key=lambda item: item[0]):
        route_key, graph, target_values, bounds, selected_indices = candidate
        _graph_name, cut_name, source_indices = route_key
        candidate_cut = project_cutset(graph.cutsets[cut_name], source_indices)
        candidate_external_cut = graph.cutsets[cut_name][:2]
        candidate_denominators = tuple(
            graph.all_denominators[index] for index in source_indices
        )
        canonical_key = None
        for canonical in canonical_candidates:
            (
                other_key,
                other_graph,
                other_targets,
                other_bounds,
                other_selected,
            ) = canonical
            if (
                target_values != other_targets
                or bounds != other_bounds
                or selected_indices != other_selected
            ):
                continue
            _other_graph_name, other_cut_name, other_sources = other_key
            if (
                candidate_external_cut
                != other_graph.cutsets[other_cut_name][:2]
            ):
                continue
            if candidate_cut != project_cutset(
                other_graph.cutsets[other_cut_name],
                other_sources,
            ):
                continue
            other_denominators = tuple(
                other_graph.all_denominators[index] for index in other_sources
            )
            equivalent = any(
                all(
                    normalize_rational(
                        replace_all(candidate_value, substitutions)
                        - other_value
                    )
                    == E("0")
                    for candidate_value, other_value in zip(
                        candidate_denominators,
                        other_denominators,
                        strict=True,
                    )
                )
                for substitutions in ((), loop_reversal)
            )
            if equivalent:
                canonical_key = other_key
                break
        if canonical_key is None:
            canonical_key = route_key
            canonical_candidates.append(candidate)
            projects[canonical_key] = build_cut_kira_project(
                name=_project_family_name(canonical_key),
                loop_momenta=(context.k,),
                graph_propagators=graph.propagators,
                source_indices=source_indices,
                cutset=graph.cutsets[cut_name],
                incoming_momenta=(context.p1, context.p2),
                target_indices=tuple(product(target_values, repeat=3)),
                preferred_master_indices=(selected_indices,)
                if selected_indices is not None
                else (),
                bounds=bounds,
                check_masters=False,
            )
        route_projects[route_key] = canonical_key
    return DYProjectPlan(
        projects=MappingProxyType(projects),
        route_projects=MappingProxyType(route_projects),
    )


def numerator_reductions(
    graphs: Mapping[str, DYGraphSpec],
    numerators: Mapping[str, Expression],
    context: DYContext,
) -> Mapping[str, NumeratorReduction]:
    """Build every three-denominator physical numerator handoff."""

    reductions = {}
    for name, graph in graphs.items():
        if graph.requires_apart:
            continue
        reductions[name] = reduce_numerator(
            numerators[name] / graph.numerator_divisor,
            graph.denominators,
            loop_scalar_products=context.loop_scalar_products,
            base_integral_indices=graph.propagator_powers,
        )
    return MappingProxyType(reductions)


def qg_ward_reductions(
    qg_graph: DYGraphSpec,
    ward_numerators: Mapping[str, Expression],
    context: DYContext,
) -> Mapping[str, NumeratorReduction]:
    """Reduce the notebook-owned longitudinal qg numerator inputs."""

    denominators = tuple(
        replace_all(
            denominator,
            (
                (context.p1_squared, E("0")),
                (context.p2_squared, E("0")),
            ),
        )
        for denominator in qg_graph.denominators
    )
    return MappingProxyType(
        {
            "box": reduce_numerator(
                ward_numerators["box"],
                denominators,
                loop_scalar_products=context.loop_scalar_products,
                base_integral_indices=(1, 2, 1),
            ),
            "triangle": reduce_numerator(
                ward_numerators["triangle"],
                denominators,
                loop_scalar_products=context.loop_scalar_products,
            ),
            "bubble": reduce_numerator(
                ward_numerators["bubble"],
                denominators,
                loop_scalar_products=context.loop_scalar_products,
                base_integral_indices=(1, 0, 1),
            ),
        }
    )


def crossed_box_reductions(
    graphs: Mapping[str, DYGraphSpec],
    numerators: Mapping[str, Expression],
    context: DYContext,
) -> tuple[
    Expression,
    tuple[tuple[ApartTerm, NumeratorReduction], ...],
]:
    """Partial-fraction and numerator-reduce the physical crossed box."""

    graph = graphs["qq crossed box"]
    denominators = graph.denominators
    numerator = numerators["qq crossed box"]
    pre_ibp = prepare_pre_ibp(
        numerator=numerator,
        loop_denominators=denominators,
        loop_scalar_products=context.loop_scalar_products,
        loop_propagator_indices=graph.loop_propagator_indices,
        delta=context.mass_squared - 2 * context.p1_dot_p2,
        propagator_powers=graph.propagator_powers,
    )
    reductions = tuple(
        zip(pre_ibp.apart_terms, pre_ibp.numerator_reductions, strict=True)
    )
    residual = normalize_rational(
        sum(
            (reduction.reconstructed_integrand() for _, reduction in reductions),
            E("0"),
        )
        - numerator / prod(denominators)
    )
    if residual != E("0"):
        raise ValueError("Crossed-box apart children did not reconstruct the graph")
    return pre_ibp.apart_expression, reductions


def _coefficient_of_selected_masters(
    result: ReductionResult,
    input_expression: Expression,
    selected_masters: Sequence[Expression],
    *,
    substitutions: Sequence[tuple[Expression, Expression | int]] = (),
) -> Expression:
    reduced = result.apply(input_expression)
    selected = set(selected_masters)
    for master in result.masters:
        reduced = reduced.replace(master, 1 if master in selected else 0)
    # Select the master before imposing leading-power kinematics.  Some Kira
    # coefficients contain removable p_i^2/p_i^2 factors; substituting an
    # on-shell value first turns those exact cancellations into an undefined
    # 0/0 object in Symbolica.
    reduced = normalize_rational(reduced)
    reduced = replace_all(reduced, substitutions)
    return normalize_rational(reduced)


def _kinematic_rules(
    graph: DYGraphSpec,
    cut_name: str,
    context: DYContext,
):
    cutset = graph.cutsets[cut_name]
    rules: list[tuple[Expression, Expression | int]] = []
    if cutset[0]:
        rules.append((context.p1_squared, E("0")))
    if cutset[1]:
        rules.append((context.p2_squared, E("0")))
    return tuple(rules)


def _project_route(
    plan: DYProjectPlan,
    graph_name: str,
    graph: DYGraphSpec,
    cut_name: str,
    source_indices: Sequence[int],
):
    project_key = plan.project_key(graph_name, cut_name, source_indices)
    project = plan.projects[project_key]
    selected_indices = _selected_cut_indices(
        graph,
        cut_name,
        source_indices,
    )
    return project_key, project, selected_indices


@dataclass(frozen=True, slots=True)
class ReductionAudit:
    """Exact evidence connecting physical numerators to Kira master coefficients."""

    required_projects: tuple[DYProjectKey, ...]
    complete_projects: tuple[DYProjectKey, ...]
    numerator_reconstruction_residuals: Mapping[str, Expression]
    crossed_box_reconstruction_residual: Expression
    virtual_coefficients: Mapping[str, Expression]
    virtual_expected_residuals: Mapping[str, Expression]
    direct_box_coefficients: Mapping[str, Expression]
    direct_box_expected_residuals: Mapping[str, Expression]
    qg_coefficients: Mapping[str, Expression]
    qg_expected_residuals: Mapping[str, Expression]
    qg_ward_coefficients: Mapping[str, Expression]
    qg_ward_expected_residuals: Mapping[str, Expression]
    qg_ward_cancellation_residual: Expression
    crossed_box_coefficients: Mapping[str, Expression]
    crossed_box_expected_residuals: Mapping[str, Expression]

    @property
    def native_complete(self) -> bool:
        """Whether graph reconstruction and intrinsic identities are exact.

        This property deliberately excludes every ``*_expected_residuals``
        mapping: those are regression comparisons with historical closed
        coefficients, not inputs or prerequisites of the native result.
        """

        intrinsic_residuals = (
            *self.numerator_reconstruction_residuals.values(),
            self.crossed_box_reconstruction_residual,
            self.qg_ward_cancellation_residual,
            normalize_rational(
                self.virtual_coefficients["virtual triangle 1/10"]
                - self.virtual_coefficients["virtual triangle 1/01"]
            ),
            normalize_rational(
                self.crossed_box_coefficients["10"]
                - self.crossed_box_coefficients["01"]
            ),
        )
        return self.complete_projects == self.required_projects and all(
            residual == E("0") for residual in intrinsic_residuals
        )

    @property
    def reference_targets_exact(self) -> bool:
        """Whether all downstream historical coefficient regressions match."""

        residuals = (
            *self.virtual_expected_residuals.values(),
            *self.direct_box_expected_residuals.values(),
            *self.qg_expected_residuals.values(),
            *self.qg_ward_expected_residuals.values(),
            *self.crossed_box_expected_residuals.values(),
        )
        return all(residual == E("0") for residual in residuals)

    @property
    def exact(self) -> bool:
        """Backward-compatible conjunction of native and regression checks."""

        return self.native_complete and self.reference_targets_exact


def audit_physical_reductions(
    reductions: Mapping[DYProjectKey, ReductionResult],
    *,
    plan: DYProjectPlan,
    context: DYContext,
    graphs: Mapping[str, DYGraphSpec],
    numerators: Mapping[str, Expression],
    ward_numerators: Mapping[str, Expression],
) -> ReductionAudit:
    """Rebuild key physical IBP coefficients from native Kira rules."""

    d = context.d
    epsilon = context.epsilon
    kk = context.kk
    kp1 = context.kp1
    kp2 = context.kp2
    p1_squared = context.p1_squared
    p2_squared = context.p2_squared
    p1_dot_p2 = context.p1_dot_p2
    s = context.s
    z = context.z
    mass_squared = context.mass_squared

    project_keys = tuple(plan.projects)
    missing = [key for key in project_keys if key not in reductions]
    if missing:
        raise ValueError(
            "Missing physical Kira reductions: "
            + ", ".join(map(str, missing))
        )
    incomplete = [
        key for key in project_keys if not reductions[key].complete
    ]
    if incomplete:
        raise ValueError(
            "Incomplete physical Kira reductions: "
            + ", ".join(map(str, incomplete))
        )

    three_line = numerator_reductions(graphs, numerators, context)
    numerator_residuals = {
        name: reduction.reconstruction_residual
        for name, reduction in three_line.items()
    }
    _, crossed_children = crossed_box_reductions(graphs, numerators, context)
    crossed_reconstruction = normalize_rational(
        sum(
            (child.reconstructed_integrand() for _, child in crossed_children),
            E("0"),
        )
        - numerators["qq crossed box"]
        / prod(graphs["qq crossed box"].denominators)
    )

    virtual_configs = (
        ("virtual triangle 1", "11"),
        ("virtual triangle 1", "10"),
        ("virtual triangle 1", "01"),
        ("virtual triangle 2", "00"),
    )
    virtual_coefficients: dict[str, Expression] = {}
    for graph_name, cut_name in virtual_configs:
        label = f"{graph_name}/{cut_name}"
        graph = graphs[graph_name]
        project_key, project, selected_indices = _project_route(
            plan,
            graph_name,
            graph,
            cut_name,
            graph.loop_propagator_indices,
        )
        if selected_indices is None:
            raise ValueError(f"Virtual route {label} has no selected master")
        rules = _kinematic_rules(graph, cut_name, context)
        source = three_line[graph_name]
        local = reduce_numerator(
            replace_all(source.numerator, rules),
            tuple(replace_all(value, rules) for value in source.denominators),
            loop_scalar_products=context.loop_scalar_products,
            base_integral_indices=source.base_integral_indices,
        )
        virtual_coefficients[label] = _coefficient_of_selected_masters(
            reductions[project_key],
            local.family_expression(project.family.name),
            (project.family(*selected_indices),),
            substitutions=(
                (p1_dot_p2, s / 2),
                (p1_squared, E("0")),
                (p2_squared, E("0")),
            ),
        )
    bubble_source = three_line["virtual bubble"]
    bubble_graph = graphs["virtual bubble"]
    bubble_project_key, bubble_project, bubble_selected = _project_route(
        plan,
        "virtual bubble",
        bubble_graph,
        "10",
        bubble_graph.loop_propagator_indices,
    )
    bubble_rules = _kinematic_rules(bubble_graph, "10", context)
    if bubble_selected is None:
        raise ValueError("Virtual-bubble cut has no selected master")
    bubble_local = reduce_numerator(
        replace_all(bubble_source.numerator, bubble_rules),
        tuple(
            replace_all(value, bubble_rules)
            for value in bubble_source.denominators
        ),
        loop_scalar_products=context.loop_scalar_products,
        base_integral_indices=bubble_source.base_integral_indices,
    )
    bubble_with_virtuality = _coefficient_of_selected_masters(
        reductions[bubble_project_key],
        bubble_local.family_expression(bubble_project.family.name),
        (bubble_project.family(*bubble_selected),),
        substitutions=((p1_dot_p2, s / 2),),
    )
    # Scalarize the tagged Spenso contraction before taking its leading-power
    # coefficient.  Symbolica's rational-polynomial normalizer deliberately
    # rejects a tensor contraction in a denominator, even though this audited
    # expression is exactly proportional to p2_squared.
    virtuality_placeholder = E("dy_external_virtuality_placeholder")
    scalar_bubble = bubble_with_virtuality.replace(
        p2_squared,
        virtuality_placeholder,
    )
    if normalize_rational(
        scalar_bubble.replace(virtuality_placeholder, 0)
    ) != E("0"):
        raise ValueError("External-bubble coefficient has a nonzero constant term")
    virtual_coefficients["external bubble"] = normalize_rational(
        normalize_rational(scalar_bubble / virtuality_placeholder).replace(
            virtuality_placeholder,
            0,
        )
    )
    virtual_expected = {
        "virtual triangle 1/11": (
            2 * s * (d - 2) * (d**2 - 7 * d + 16) / (d - 4)
        ),
        "virtual triangle 1/10": -4 * s * (d - 2) ** 2 / (d - 4),
        "virtual triangle 1/01": -4 * s * (d - 2) ** 2 / (d - 4),
        "virtual triangle 2/00": -4 * s**2 * (d - 2),
        "external bubble": -s * (d - 2) ** 2,
    }
    virtual_residuals = {
        name: normalize_rational(virtual_coefficients[name] - expected)
        for name, expected in virtual_expected.items()
    }

    # Direct box: only the cut-compatible analytic master is retained in each
    # sector.  The other preferred Kira masters are not silently evaluated.
    direct = three_line["qq direct box"]
    direct_graph = graphs["qq direct box"]
    direct_coefficients: dict[str, Expression] = {}
    for cut_name in ("11", "01"):
        project_key, project, selected_indices = _project_route(
            plan,
            "qq direct box",
            direct_graph,
            cut_name,
            direct_graph.loop_propagator_indices,
        )
        if selected_indices is None:
            raise ValueError(
                f"Direct-box route qq direct box/{cut_name} has no master"
            )
        result = reductions[project_key]
        rules = _kinematic_rules(direct_graph, cut_name, context)
        numerator = replace_all(direct.numerator, rules)
        denominators = tuple(replace_all(value, rules) for value in direct.denominators)
        local = reduce_numerator(
            numerator,
            denominators,
            loop_scalar_products=context.loop_scalar_products,
            base_integral_indices=(1, 2, 1),
        )
        keep = project.family(*selected_indices)
        coefficient = _coefficient_of_selected_masters(
            result,
            local.family_expression(project.family.name),
            (keep,),
            substitutions=(
                (p1_dot_p2, s / 2),
                (p1_squared, E("0")),
                (mass_squared, z * s),
                (d, 4 - 2 * epsilon),
            ),
        )
        direct_coefficients[cut_name] = coefficient
    direct_expected = {
        "11": -8 * (1 - epsilon) ** 3 / epsilon,
        "01": 8 * s * (1 - epsilon) ** 2 * (z - 1 + epsilon),
    }
    direct_residuals = {
        name: normalize_rational(direct_coefficients[name] - expected)
        for name, expected in direct_expected.items()
    }

    qg_coefficients: dict[str, Expression] = {}
    for graph_name in ("qg box", "qg triangle", "qg bubble"):
        graph = graphs[graph_name]
        for cut_name in ("11", "01"):
            project_key, project, selected_indices = _project_route(
                plan,
                graph_name,
                graph,
                cut_name,
                graph.loop_propagator_indices,
            )
            if selected_indices is None:
                raise ValueError(
                    f"qg route {graph_name}/{cut_name} has no master"
                )
            rules = _kinematic_rules(graph, cut_name, context)
            source = three_line[graph_name]
            local = reduce_numerator(
                replace_all(source.numerator, rules),
                tuple(replace_all(value, rules) for value in source.denominators),
                loop_scalar_products=context.loop_scalar_products,
                base_integral_indices=source.base_integral_indices,
            )
            keep = project.family(*selected_indices)
            coefficient = _coefficient_of_selected_masters(
                reductions[project_key],
                local.family_expression(project.family.name),
                (keep,),
                substitutions=(
                    (p1_dot_p2, s / 2),
                    (mass_squared, z * s),
                ),
            )
            if cut_name == "01":
                coefficient = normalize_rational(coefficient).series(
                    p1_squared,
                    0,
                    0,
                ).to_expression()
            coefficient = replace_all(
                coefficient,
                ((d, 4 - 2 * epsilon),),
            )
            key = f"{cut_name} {graph_name.removeprefix('qg ')}"
            qg_coefficients[key] = normalize_rational(coefficient)
    qg_expected = {
        "11 box": 8
        * (1 - 2 * epsilon)
        * (1 - epsilon) ** 2
        / (epsilon * (1 - z)),
        "11 triangle": 8
        * (1 - epsilon)
        * (epsilon**2 + z * (1 - epsilon))
        / epsilon,
        "11 bubble": -4 * (1 - epsilon) ** 2 * (1 - z),
        "01 box": 8 * s * (1 - epsilon) ** 3,
        "01 triangle": 8
        * s
        * z
        * (1 - epsilon)
        * (1 - z),
        "01 bubble": E("0"),
    }
    qg_residuals = {
        name: normalize_rational(qg_coefficients[name] - expected)
        for name, expected in qg_expected.items()
    }

    ward_coefficients: dict[str, Expression] = {}
    ward_graph = graphs["qg box"]
    ward_project_key, ward_project, ward_selected = _project_route(
        plan,
        "qg box",
        ward_graph,
        "11",
        ward_graph.loop_propagator_indices,
    )
    if ward_selected is None:
        raise ValueError("qg Ward route qg box/11 has no selected master")
    for graph_name, ward_reduction in qg_ward_reductions(
        ward_graph,
        ward_numerators,
        context,
    ).items():
        ward_coefficients[graph_name] = _coefficient_of_selected_masters(
            reductions[ward_project_key],
            ward_reduction.family_expression(ward_project.family.name),
            (ward_project.family(*ward_selected),),
        )
    ward_expected = (
        (d - 2)
        * (mass_squared - 2 * p1_dot_p2)
        / mass_squared
    )
    ward_residuals = {
        name: normalize_rational(coefficient - ward_expected)
        for name, coefficient in ward_coefficients.items()
    }
    ward_cancellation = normalize_rational(
        2 * ward_coefficients["triangle"]
        - ward_coefficients["box"]
        - ward_coefficients["bubble"]
    )

    # Crossed box: every apart child stays in native graph source order.
    crossed_graph = graphs["qq crossed box"]
    crossed_coefficients: dict[str, Expression] = {}
    for cut_name in ("11", "10", "01"):
        sector_sum = E("0")
        for apart_term, child in crossed_children:
            source_indices = tuple(
                crossed_graph.loop_propagator_indices[index]
                for index in apart_term.retained_indices
            )
            project_key, project, selected_indices = _project_route(
                plan,
                "qq crossed box",
                crossed_graph,
                cut_name,
                source_indices,
            )
            result = reductions[project_key]
            rules = _kinematic_rules(crossed_graph, cut_name, context)
            numerator = replace_all(child.numerator, rules)
            denominators = tuple(
                replace_all(value, rules) for value in child.denominators
            )
            local = reduce_numerator(
                numerator,
                denominators,
                loop_scalar_products=context.loop_scalar_products,
            )
            selected = (
                (project.family(*selected_indices),)
                if selected_indices is not None
                else ()
            )
            sector_sum += _coefficient_of_selected_masters(
                result,
                local.family_expression(project.family.name),
                selected,
                substitutions=(
                    (p1_dot_p2, s / 2),
                    (p1_squared, E("0")),
                    (p2_squared, E("0")),
                    (mass_squared, z * s),
                    (d, 4 - 2 * epsilon),
                ),
            )
        crossed_coefficients[cut_name] = normalize_rational(sector_sum)
    crossed_expected = {
        "11": 8
        * (1 - epsilon)
        * (
            epsilon**2 * (1 - z) ** 2
            + 2 * z * (1 - 2 * epsilon)
        )
        / (epsilon * (1 - z) ** 2),
        "10": 8 * s * z * (1 - epsilon) / (1 - z),
        "01": 8 * s * z * (1 - epsilon) / (1 - z),
        # The fourth cut contains all four graph propagators, so it is the
        # analytic maximal-cut numerator rather than a three-line Kira family.
        "00": -8 * s**2 * (1 - epsilon),
    }
    crossed_coefficients["00"] = replace_all(
        numerators["qq crossed box"],
        (
            (kk, E("0")),
            (kp1, E("0")),
            (kp2, E("0")),
            (p1_squared, E("0")),
            (p2_squared, E("0")),
            (p1_dot_p2, s / 2),
            (d, 4 - 2 * epsilon),
        ),
    ).expand()
    crossed_residuals = {
        name: normalize_rational(crossed_coefficients[name] - expected)
        for name, expected in crossed_expected.items()
    }
    return ReductionAudit(
        required_projects=project_keys,
        complete_projects=tuple(
            key for key in project_keys if reductions[key].complete
        ),
        numerator_reconstruction_residuals=MappingProxyType(numerator_residuals),
        crossed_box_reconstruction_residual=crossed_reconstruction,
        virtual_coefficients=MappingProxyType(virtual_coefficients),
        virtual_expected_residuals=MappingProxyType(virtual_residuals),
        direct_box_coefficients=MappingProxyType(direct_coefficients),
        direct_box_expected_residuals=MappingProxyType(direct_residuals),
        qg_coefficients=MappingProxyType(qg_coefficients),
        qg_expected_residuals=MappingProxyType(qg_residuals),
        qg_ward_coefficients=MappingProxyType(ward_coefficients),
        qg_ward_expected_residuals=MappingProxyType(ward_residuals),
        qg_ward_cancellation_residual=ward_cancellation,
        crossed_box_coefficients=MappingProxyType(crossed_coefficients),
        crossed_box_expected_residuals=MappingProxyType(crossed_residuals),
    )


@dataclass(frozen=True, slots=True)
class EndpointCoefficient:
    """Coefficient in the explicit ``delta, D0, D1, regular`` basis.

    ``d0_prefactor`` and ``d1_prefactor`` may depend smoothly on ``z``.  The
    :meth:`canonical` method moves that dependence into the ordinary remainder
    and leaves endpoint constants multiplying the plus distributions.
    """

    delta: Expression = E("0")
    d0_prefactor: Expression = E("0")
    d1_prefactor: Expression = E("0")
    regular: Expression = E("0")

    def __add__(self, other: "EndpointCoefficient") -> "EndpointCoefficient":
        if not isinstance(other, EndpointCoefficient):
            return NotImplemented
        return EndpointCoefficient(
            delta=(self.delta + other.delta).expand(),
            d0_prefactor=(self.d0_prefactor + other.d0_prefactor).expand(),
            d1_prefactor=(self.d1_prefactor + other.d1_prefactor).expand(),
            regular=(self.regular + other.regular).expand(),
        )

    def __neg__(self) -> "EndpointCoefficient":
        return self.scaled(E("-1"))

    def __sub__(self, other: "EndpointCoefficient") -> "EndpointCoefficient":
        return self + (-other)

    def scaled(self, factor: Expression | int) -> "EndpointCoefficient":
        return EndpointCoefficient(
            delta=(factor * self.delta).expand(),
            d0_prefactor=(factor * self.d0_prefactor).expand(),
            d1_prefactor=(factor * self.d1_prefactor).expand(),
            regular=(factor * self.regular).expand(),
        )

    def multiply_smooth(
        self,
        factor: Expression | int,
        variable: Expression,
    ) -> "EndpointCoefficient":
        r"""Multiply the distribution by a function smooth at ``variable=1``.

        The endpoint value multiplies ``delta(1-variable)``.  The plus
        prefactors retain the smooth function until :meth:`canonical` moves
        their non-endpoint parts into the ordinary remainder.  Keeping this
        operation explicit prevents the invalid global ``z -> 1`` replacement
        used by the historical DY scheme-change cell.
        """

        factor_expression = (
            factor if isinstance(factor, Expression) else E(str(factor))
        )
        endpoint_factor = factor_expression.replace(variable, 1)
        if endpoint_factor.contains(variable):
            raise ValueError("Could not evaluate smooth factor at the endpoint")
        return EndpointCoefficient(
            delta=(endpoint_factor * self.delta).expand(),
            d0_prefactor=(factor_expression * self.d0_prefactor).expand(),
            d1_prefactor=(factor_expression * self.d1_prefactor).expand(),
            regular=(factor_expression * self.regular).expand(),
        ).canonical(variable)

    def canonical(self, variable: Expression) -> "EndpointCoefficient":
        d0_endpoint = self.d0_prefactor.replace(variable, 1)
        d1_endpoint = self.d1_prefactor.replace(variable, 1)
        remainder = (
            self.regular
            + (self.d0_prefactor - d0_endpoint) / (1 - variable)
            + (self.d1_prefactor - d1_endpoint)
            * (1 - variable).log()
            / (1 - variable)
        ).expand().together().cancel()
        return EndpointCoefficient(
            delta=self.delta,
            d0_prefactor=d0_endpoint,
            d1_prefactor=d1_endpoint,
            regular=remainder,
        )

    def residuals(self) -> tuple[Expression, Expression, Expression, Expression]:
        return tuple(
            normalize_rational(value)
            for value in (
                self.delta,
                self.d0_prefactor,
                self.d1_prefactor,
                self.regular,
            )
        )

    def is_zero_for(self, variable: Expression) -> bool:
        """Test distributional equality in the supplied endpoint variable."""

        canonical = self.canonical(variable)
        return all(value == E("0") for value in canonical.residuals())


@dataclass(frozen=True, slots=True)
class ChannelAssembly:
    """Named graph pieces and their exact endpoint-basis sum."""

    pieces: Mapping[str, EndpointCoefficient]
    total: EndpointCoefficient


@dataclass(frozen=True, slots=True)
class MasterInsertion:
    """One audited IBP coefficient inserted into one analytic master."""

    graph_name: str
    cut_name: str
    channel: str
    sector: str
    projects: tuple[str, ...]
    ibp_coefficient: Expression
    analytic_master: Expression
    virtuality_factor: Expression = E("1")
    relative_weight: Expression = E("1")

    @property
    def value(self) -> Expression:
        """Return the contribution before its channel-wide graph factor."""

        return (
            self.relative_weight
            * self.ibp_coefficient
            * self.analytic_master
            * self.virtuality_factor
        ).expand()


@dataclass(frozen=True, slots=True)
class NativeDYSchemeChange:
    """DY ``MP - PM`` difference assembled only from native graph sectors.

    The common parton-model cuts are absent by construction.  The retained
    insertion names identify the complementary initial-state and all-cut
    sectors whose analytic masters form the difference.  The physical quark
    result uses the AEM/convolution normalization.  A separate field retains
    the exact smooth multiplication by ``z`` used only to compare with the
    historical scheme-cell normalization.
    """

    insertions: Mapping[str, MasterInsertion]
    insertion_names: Mapping[str, tuple[str, ...]]
    cut_membership_coefficients: Mapping[str, Expression]
    observable_phases: Mapping[str, Expression]
    qg_pieces: Mapping[str, Expression]
    qg_mp_minus_pm: Expression
    qg_double_pole_coefficient: Expression
    qg_single_pole_coefficient: Expression
    qq_virtual_triangle: EndpointCoefficient
    qq_external_bubbles: EndpointCoefficient
    qq_direct: EndpointCoefficient
    qq_crossed: EndpointCoefficient
    qq_mp_minus_pm: EndpointCoefficient
    qq_historical_z_normalization: EndpointCoefficient
    qq_double_pole_coefficient: EndpointCoefficient
    qq_single_pole_coefficient: EndpointCoefficient

    def internally_consistent(self, variable: Expression) -> bool:
        qg_sum = normalize_rational(
            sum(self.qg_pieces.values(), E("0")) - self.qg_mp_minus_pm
        )
        qq_sum = (
            self.qq_virtual_triangle
            + self.qq_external_bubbles
            + self.qq_direct
            + self.qq_crossed
            - self.qq_mp_minus_pm
        )
        historical_normalization_residual = (
            self.qq_mp_minus_pm.multiply_smooth(variable, variable)
            - self.qq_historical_z_normalization
        )
        return (
            qg_sum == E("0")
            and qq_sum.is_zero_for(variable)
            and historical_normalization_residual.is_zero_for(variable)
            and self.qg_double_pole_coefficient == E("0")
            and self.qq_double_pole_coefficient.is_zero_for(variable)
        )


@dataclass(frozen=True, slots=True)
class NativeDYOneLegSchemeKernel:
    """Colour-stripped one-leg output contract of the native DY assembly.

    This object is downstream of :func:`build_native_dy_scheme_change`; it is
    never an input to that graph/master assembly.  The DY notebook proves that
    the sum of two such records reconstructs the native two-leg result exactly,
    allowing another process to compare against a small public interface
    without importing a private Kira cache.
    """

    qq: EndpointCoefficient
    qg: Expression


def native_dy_one_leg_scheme_kernel(
    variable: Expression,
    regulator: Expression,
    hard_scale_squared: Expression,
    cutoff_squared: Expression,
) -> NativeDYOneLegSchemeKernel:
    """Return the canonical one-leg form certified by the native DY notebook."""

    pi = Expression.PI
    scale_log = hard_scale_squared.log() - cutoff_squared.log()
    pqq = EndpointCoefficient(
        delta=E("3/2"),
        d0_prefactor=E("2"),
        regular=-(1 + variable),
    )
    qq = (
        pqq.scaled(1 / regulator + scale_log)
        + EndpointCoefficient(
            delta=E("7/2") - pi**2 / 3,
            d1_prefactor=E("-2"),
            regular=(
                variable
                - 2
                - (1 + variable**2) * variable.log() / (1 - variable)
                + (1 + variable) * (1 - variable).log()
            ),
        )
    ).canonical(variable)
    pqg = variable**2 + (1 - variable) ** 2
    qg = normalize_rational(
        pqg * (1 / regulator + scale_log)
        - 2
        - pqg * (variable.log() + (1 - variable).log())
    )
    return NativeDYOneLegSchemeKernel(qq=qq, qg=qg)


@dataclass(frozen=True, slots=True)
class AnalyticMasterHandoff:
    """Explicit Kira-to-master ledger used by the physical assembly.

    The direct qqbar and qg channels are independently Laurent-expanded from
    these expressions and checked against their finite graph ledgers.  The two
    external-bubble insertions are also summed through finite order and checked
    against the MP/PM endpoint correction.  The
    distribution-valued crossed box is expanded cut by cut, including its
    analytic ``00`` master; both pole cancellation and its complete finite
    delta/plus coefficient are checked exactly.
    """

    insertions: Mapping[str, MasterInsertion]
    normalization_factors: Mapping[str, Expression]
    direct_normalized_raw: Expression
    direct_finite: Expression
    direct_finite_residual: Expression
    qg_normalized_raw: Expression
    qg_finite: Expression
    qg_finite_residual: Expression
    external_bubble_through_finite: EndpointCoefficient
    external_bubble_expected_residual: EndpointCoefficient
    crossed_cut_endpoint: Mapping[str, EndpointCoefficient]
    crossed_pole_residuals: Mapping[int, EndpointCoefficient]
    crossed_finite: EndpointCoefficient
    crossed_finite_residual: EndpointCoefficient
    scheme_change: NativeDYSchemeChange

    def native_checks_exact(self, variable: Expression) -> bool:
        """Check only master identities that do not use a closed target."""

        return (
            self.scheme_change.internally_consistent(variable)
            and all(
                residual.is_zero_for(variable)
                for residual in self.crossed_pole_residuals.values()
            )
        )

    def finite_checks_exact(self, variable: Expression) -> bool:
        """Check native identities and downstream closed-form regressions."""

        return (
            self.native_checks_exact(variable)
            and bool(self.direct_finite_residual == E("0"))
            and bool(self.qg_finite_residual == E("0"))
            and self.external_bubble_expected_residual.is_zero_for(variable)
            and self.crossed_finite_residual.is_zero_for(variable)
        )


@dataclass(frozen=True, slots=True)
class FullDYCoefficient:
    """All NLO DY channels plus explicit source-comparison residuals."""

    ordinary_virtual: EndpointCoefficient
    local_all_cut_virtual: EndpointCoefficient
    qq_transverse: ChannelAssembly
    qq_recorded_mathematica: EndpointCoefficient
    qq_manuscript: EndpointCoefficient
    qq_transverse_minus_recorded_mathematica: EndpointCoefficient
    qq_transverse_minus_manuscript: EndpointCoefficient
    qq_recorded_mathematica_minus_manuscript: EndpointCoefficient
    qg_transverse: ChannelAssembly
    qg_recorded_mathematica: EndpointCoefficient
    qg_manuscript: EndpointCoefficient
    qg_transverse_minus_manuscript: EndpointCoefficient
    master_handoff: AnalyticMasterHandoff | None = None


def _positive_branch_log_rules(
    context: DYContext,
) -> tuple[tuple[Expression, Expression], ...]:
    """Logarithm identities for the stated positive DY kinematic region."""

    mu_r_squared = context.mu_r_squared
    s = context.s
    z = context.z
    lambda1_squared = context.lambda1_squared
    lambda2_squared = context.lambda2_squared
    pi = context.pi
    gamma_e = Expression.EULER_GAMMA
    log_two = E("log(2)")
    return (
        (
            (gamma_e.exp() * mu_r_squared).log(),
            gamma_e + mu_r_squared.log(),
        ),
        (
            (s * z * (s - s * z)).log(),
            2 * s.log() + z.log() + (1 - z).log(),
        ),
        (
            (s**2 * z - s**2 * z**2).log(),
            2 * s.log() + z.log() + (1 - z).log(),
        ),
        (
            ((s - s * z) / (2 * s.sqrt())).log(),
            -log_two + s.log() / 2 + (1 - z).log(),
        ),
        (
            (s.sqrt() / 2 - s.sqrt() * z / 2).log(),
            -log_two + s.log() / 2 + (1 - z).log(),
        ),
        (
            (s**2).sqrt(),
            s,
        ),
        (
            (s**2).log(),
            2 * s.log(),
        ),
        (
            (
                lambda1_squared
                * lambda2_squared
                * z**2
                / (s**2 * (1 - z) ** 2)
            ).log(),
            lambda1_squared.log()
            + lambda2_squared.log()
            + 2 * z.log()
            - 2 * s.log()
            - 2 * (1 - z).log(),
        ),
        (
            (
                lambda1_squared
                * lambda2_squared
                * z**2
                / s**2
            ).log(),
            lambda1_squared.log()
            + lambda2_squared.log()
            + 2 * z.log()
            - 2 * s.log(),
        ),
        (
            (lambda1_squared / s).log(),
            lambda1_squared.log() - s.log(),
        ),
        (
            (lambda2_squared / s).log(),
            lambda2_squared.log() - s.log(),
        ),
        (
            E("symbolica::polygamma(1,2)"),
            pi**2 / 6 - 1,
        ),
        (
            E("symbolica::polygamma(1,3/2)"),
            pi**2 / 2 - 4,
        ),
    )


def _expand_positive_branch_logs(
    expression: Expression,
    context: DYContext,
) -> Expression:
    """Apply positive-region log identities to a stable rational fixed point."""

    result = expression
    for _ in range(3):
        result = replace_all(result, _positive_branch_log_rules(context))
        result = normalize_rational(result)
    return result


def _positive_branch_before_series(
    expression: Expression,
    context: DYContext,
) -> Expression:
    """Expose integer powers of positive ``s`` before a Laurent expansion."""

    s = context.s
    epsilon = context.epsilon
    return replace_all(
        expression,
        (
            (s ** (1 + epsilon), s * s**epsilon),
            (s ** (-1 + epsilon), s**epsilon / s),
            (s ** (-2 + epsilon), s**epsilon / s**2),
        ),
    )


def _finite_laurent_coefficient(
    expression: Expression,
    context: DYContext,
) -> Expression:
    """Extract the exact epsilon^0 coefficient and expand its DY logarithms."""

    finite = _positive_branch_before_series(expression, context).series(
        context.epsilon,
        0,
        0,
    ).get_coefficient(0)
    return _expand_positive_branch_logs(finite, context)


def _endpoint_laurent_coefficient(
    coefficient: EndpointCoefficient,
    power: int,
    context: DYContext,
) -> EndpointCoefficient:
    """Extract one Laurent power from every endpoint-basis component."""

    def extract(expression: Expression) -> Expression:
        value = _positive_branch_before_series(expression, context).series(
            context.epsilon,
            0,
            0,
        ).get_coefficient(power)
        return _expand_positive_branch_logs(value, context)

    return EndpointCoefficient(
        delta=extract(coefficient.delta),
        d0_prefactor=extract(coefficient.d0_prefactor),
        d1_prefactor=extract(coefficient.d1_prefactor),
        regular=extract(coefficient.regular),
    )


def _endpoint_through_finite(
    coefficient: EndpointCoefficient,
    context: DYContext,
) -> EndpointCoefficient:
    """Laurent-expand every endpoint component through ``epsilon^0``."""

    def expand(expression: Expression) -> Expression:
        value = _positive_branch_before_series(expression, context).series(
            context.epsilon,
            0,
            0,
        ).to_expression()
        return _expand_positive_branch_logs(value, context)

    return EndpointCoefficient(
        delta=expand(coefficient.delta),
        d0_prefactor=expand(coefficient.d0_prefactor),
        d1_prefactor=expand(coefficient.d1_prefactor),
        regular=expand(coefficient.regular),
    ).canonical(context.z)


def derive_external_bubble_scheme_correction(
    context: DYContext,
    *,
    bubble_coefficient: Expression,
) -> EndpointCoefficient:
    """Derive the two incoming external-bubble terms through finite order.

    The historical scheme-change cell set both half-weighted ``valv5`` terms
    to zero.  This reconstruction starts instead from the audited bubble IBP
    coefficient, the analytic massless cut-bubble master, the two explicit
    virtuality integrals, and the source Born normalization.  It is therefore
    an independent master-level derivation of the endpoint correction needed
    by the MP/PM universality check.
    """

    from calculations.dy.python.masters import (
        massless_cut_bubble,
        virtuality_integral_factor,
    )

    epsilon = context.epsilon
    s = context.s
    alpha_s = context.alpha_s
    color_f = context.color_f
    color_t = context.color_t
    electric_charge = context.electric_charge
    strong_coupling = context.strong_coupling
    color_count = context.color_count
    lambda1_squared = context.lambda1_squared
    lambda2_squared = context.lambda2_squared
    mu_r_squared = context.mu_r_squared
    pi = context.pi
    dimension = 4 - 2 * epsilon
    stripped_master = massless_cut_bubble(
        E("1"),
        dimension=dimension,
        epsilon=epsilon,
        mu_squared=mu_r_squared,
        euler_gamma=Expression.EULER_GAMMA,
    )
    selected_bubble_coefficient = replace_all(
        bubble_coefficient,
        ((context.d, dimension),),
    )
    bubble_insertions = sum(
        (
            -E("1/2")
            * selected_bubble_coefficient
            * stripped_master
            * virtuality_integral_factor(cutoff, epsilon)
            for cutoff in (lambda1_squared, lambda2_squared)
        ),
        E("0"),
    )
    common_graph_factor = (
        electric_charge**2
        * strong_coupling**2
        * color_t
        * (color_count**2 - 1)
    )
    born_normalization = 1 / (
        4
        * color_count
        * s
        * electric_charge**2
        * (1 - epsilon)
    )
    normalized = replace_all(
        born_normalization * common_graph_factor * bubble_insertions,
        (
            (strong_coupling**2, 4 * pi * alpha_s),
            (color_t, E("1")),
            (color_count**2 - 1, 2 * color_count * color_f),
        ),
    )
    through_finite = normalized.series(epsilon, 0, 0).to_expression()
    return EndpointCoefficient(
        delta=_expand_positive_branch_logs(through_finite, context)
    )


def _native_scheme_master_insertions(
    audit: ReductionAudit,
    context: DYContext,
    graphs: Mapping[str, DYGraphSpec],
) -> Mapping[str, MasterInsertion]:
    """Build only the analytic-master insertions needed by ``MP - PM``.

    Every coefficient comes from ``audit``.  Master functions are imported
    from the application-local analytic-master notebook.  The master-
    convention cut weight and the physical observable phase are independent
    notebook-owned graph inputs.
    """

    from calculations.dy.python.masters import (
        massive_cut_triangle,
        massless_cut_bubble,
        massless_cut_triangle,
        maximal_cross_box_cut_master,
        virtuality_integral_factor,
    )

    epsilon = context.epsilon
    s = context.s
    z = context.z
    dimension = 4 - 2 * epsilon
    master_arguments = {
        "dimension": dimension,
        "epsilon": epsilon,
        "mu_squared": context.mu_r_squared,
        "euler_gamma": Expression.EULER_GAMMA,
    }
    massive_triangle_raw = massive_cut_triangle(
        E("1"),
        s,
        z * s,
        **master_arguments,
    )
    massive_gram = s**2 * z * (1 - z)
    # Resolve the supported 0<z<1, s>0 branch before endpoint algebra so the
    # (1-z)^(-epsilon) factor is explicit rather than hidden in a composite
    # fractional power.
    massive_triangle = normalize_rational(
        massive_triangle_raw
        * massive_gram**epsilon
        / (s ** (2 * epsilon) * z**epsilon * (1 - z) ** epsilon)
    )
    massless_bubble = massless_cut_bubble(E("1"), **master_arguments)
    massless_triangle_raw = massless_cut_triangle(
        E("1"),
        E("1"),
        -s,
        **master_arguments,
    )
    # Choose the declared positive-s branch before any Laurent expansion.
    massless_triangle = normalize_rational(
        massless_triangle_raw
        * (s**2) ** (E("1/2") - epsilon)
        / s ** (1 - 2 * epsilon)
    )
    maximal_crossed_raw = maximal_cross_box_cut_master(
        s,
        **master_arguments,
    )
    maximal_crossed = normalize_rational(
        maximal_crossed_raw
        * (s**2) ** (E("1/2") - epsilon)
        / s ** (1 - 2 * epsilon)
    )
    j1 = virtuality_integral_factor(context.lambda1_squared, epsilon)
    j2 = virtuality_integral_factor(context.lambda2_squared, epsilon)

    def weight(
        graph_name: str,
        cut_name: str,
        *,
        mirror_count: int = 1,
    ) -> Expression:
        graph = graphs[graph_name]
        return (
            graph.scheme_observable_phase
            * graph.cut_weights[cut_name]
            / mirror_count
        )

    def make(
        graph_name: str,
        cut_name: str,
        channel: str,
        sector: str,
        projects: tuple[str, ...],
        coefficient: Expression,
        master: Expression,
        *,
        virtuality_factor: Expression = E("1"),
        mirror_count: int = 1,
    ) -> MasterInsertion:
        return MasterInsertion(
            graph_name=graph_name,
            cut_name=cut_name,
            channel=channel,
            sector=sector,
            projects=projects,
            ibp_coefficient=coefficient,
            analytic_master=master,
            virtuality_factor=virtuality_factor,
            relative_weight=weight(
                graph_name,
                cut_name,
                mirror_count=mirror_count,
            ),
        )

    dimension_rule = ((context.d, dimension),)
    return MappingProxyType(
        {
            "virtual p2-cut": make(
                "virtual triangle 1",
                "10",
                "virtual",
                "p2-cut triangle",
                ("virtual triangle 1/10",),
                replace_all(
                    audit.virtual_coefficients["virtual triangle 1/10"],
                    dimension_rule,
                ),
                massless_bubble,
                virtuality_factor=j2,
            ),
            "virtual p1-cut": make(
                "virtual triangle 1",
                "01",
                "virtual",
                "p1-cut triangle",
                ("virtual triangle 1/01",),
                replace_all(
                    audit.virtual_coefficients["virtual triangle 1/01"],
                    dimension_rule,
                ),
                massless_bubble,
                virtuality_factor=j1,
            ),
            "virtual double-cut": make(
                "virtual triangle 2",
                "00",
                "virtual",
                "double-cut triangle",
                ("virtual triangle 2/00",),
                replace_all(
                    audit.virtual_coefficients["virtual triangle 2/00"],
                    dimension_rule,
                ),
                massless_triangle,
                virtuality_factor=j1 * j2,
            ),
            "external bubble p1": make(
                "virtual bubble",
                "10",
                "virtual",
                "external bubble p1",
                ("virtual bubble/10",),
                replace_all(
                    audit.virtual_coefficients["external bubble"],
                    dimension_rule,
                ),
                massless_bubble,
                virtuality_factor=j1,
                mirror_count=2,
            ),
            "external bubble p2": make(
                "virtual bubble",
                "10",
                "virtual",
                "external bubble p2",
                ("virtual bubble/10",),
                replace_all(
                    audit.virtual_coefficients["external bubble"],
                    dimension_rule,
                ),
                massless_bubble,
                virtuality_factor=j2,
                mirror_count=2,
            ),
            "direct p1-cut": make(
                "qq direct box",
                "01",
                "direct qqbar",
                "p1-cut mirror",
                ("qq direct box/01",),
                audit.direct_box_coefficients["01"],
                massive_triangle,
                virtuality_factor=j1,
                mirror_count=2,
            ),
            "direct p2-cut": make(
                "qq direct box",
                "01",
                "direct qqbar",
                "p2-cut mirror",
                ("qq direct box/01",),
                audit.direct_box_coefficients["01"],
                massive_triangle,
                virtuality_factor=j2,
                mirror_count=2,
            ),
            "crossed 10": make(
                "qq crossed box",
                "10",
                "crossed qqbar",
                "10",
                ("qq crossed box/10 (four apart children)",),
                audit.crossed_box_coefficients["10"],
                massive_triangle,
                virtuality_factor=j2,
            ),
            "crossed 01": make(
                "qq crossed box",
                "01",
                "crossed qqbar",
                "01",
                ("qq crossed box/01 (four apart children)",),
                audit.crossed_box_coefficients["01"],
                massive_triangle,
                virtuality_factor=j1,
            ),
            "crossed 00": make(
                "qq crossed box",
                "00",
                "crossed qqbar",
                "00",
                (),
                audit.crossed_box_coefficients["00"],
                maximal_crossed,
                virtuality_factor=j1 * j2,
            ),
            "qg box p1-cut": make(
                "qg box",
                "01",
                "qg",
                "box p1-cut mirror",
                ("qg box/01",),
                audit.qg_coefficients["01 box"],
                massive_triangle,
                virtuality_factor=j1,
                mirror_count=2,
            ),
            "qg box p2-cut": make(
                "qg box",
                "01",
                "qg",
                "box p2-cut mirror",
                ("qg box/01",),
                audit.qg_coefficients["01 box"],
                massive_triangle,
                virtuality_factor=j2,
                mirror_count=2,
            ),
            "qg triangle p1-cut": make(
                "qg triangle",
                "01",
                "qg",
                "triangle p1-cut mirror",
                ("qg triangle/01",),
                audit.qg_coefficients["01 triangle"],
                massive_triangle,
                virtuality_factor=j1,
                mirror_count=2,
            ),
            "qg triangle p2-cut": make(
                "qg triangle",
                "01",
                "qg",
                "triangle p2-cut mirror",
                ("qg triangle/01",),
                audit.qg_coefficients["01 triangle"],
                massive_triangle,
                virtuality_factor=j2,
                mirror_count=2,
            ),
        }
    )


def build_native_dy_scheme_change(
    audit: ReductionAudit,
    context: DYContext,
    graphs: Mapping[str, DYGraphSpec],
) -> NativeDYSchemeChange:
    """Derive the DY ``MP - PM`` kernel from native cuts and masters only.

    This public boundary deliberately has no ``FullDYCoefficient``,
    Mathematica, LaTeX, or paper argument.  It consumes the graph-derived Kira
    audit, notebook-declared unsigned cut membership, master-convention cut
    weights, observable phases, and analytic master functions.  Reference
    formulas can therefore only be compared downstream.
    """

    if not audit.native_complete:
        raise ValueError(
            "Native DY MP-PM assembly requires complete graph reductions "
            "and exact intrinsic reconstruction identities"
        )

    from calculations.dy.python.masters import (
        apply_endpoint_expansion,
        endpoint_distribution_expansion,
    )

    epsilon = context.epsilon
    z = context.z
    pi = context.pi
    alpha_s = context.alpha_s
    color_f = context.color_f
    insertions = _native_scheme_master_insertions(audit, context, graphs)
    insertion_names = MappingProxyType(
        {
            graph_name: tuple(
                name
                for name, item in insertions.items()
                if item.graph_name == graph_name
                and graph.scheme_membership_coefficient(item.cut_name)
                != E("0")
            )
            for graph_name, graph in graphs.items()
            if graph.mp_only_cuts or graph.pm_only_cuts
        }
    )
    cut_membership_coefficients = MappingProxyType(
        {
            f"{graph_name}/{cut_name}": graph.scheme_membership_coefficient(
                cut_name
            )
            for graph_name, graph in graphs.items()
            for cut_name in graph.mp_only_cuts + graph.pm_only_cuts
        }
    )
    observable_phases = MappingProxyType(
        {
            graph_name: graph.scheme_observable_phase
            for graph_name, graph in graphs.items()
            if graph.mp_only_cuts or graph.pm_only_cuts
        }
    )

    def selected_value(name: str) -> Expression:
        item = insertions[name]
        return (
            graphs[item.graph_name].scheme_membership_coefficient(item.cut_name)
            * item.value
        )

    def scalar_through_finite(value: Expression) -> Expression:
        expanded = _positive_branch_before_series(value, context).series(
            epsilon,
            0,
            0,
        ).to_expression()
        return _expand_positive_branch_logs(expanded, context)

    qg_common = (
        context.electric_charge**2
        * context.strong_coupling**2
        * context.color_t
    )
    qg_normalization = 1 / (
        8 * pi * (1 - epsilon) * context.electric_charge**2
    )
    qg_pieces: dict[str, Expression] = {}
    for graph_name in ("qg box", "qg triangle"):
        raw = qg_common * sum(
            (selected_value(name) for name in insertion_names[graph_name]),
            E("0"),
        )
        normalized = replace_all(
            qg_normalization * raw,
            ((context.strong_coupling**2, 4 * pi * alpha_s),),
        )
        qg_pieces[graph_name] = scalar_through_finite(normalized)
    qg_total = normalize_rational(sum(qg_pieces.values(), E("0")))

    def scalar_laurent_coefficient(
        value: Expression,
        power: int,
    ) -> Expression:
        coefficient = _positive_branch_before_series(value, context).series(
            epsilon,
            0,
            0,
        ).get_coefficient(power)
        return _expand_positive_branch_logs(coefficient, context)

    qg_double_pole = scalar_laurent_coefficient(qg_total, -2)
    qg_single_pole = scalar_laurent_coefficient(qg_total, -1)

    qq_common = (
        context.electric_charge**2
        * context.strong_coupling**2
        * context.color_t
        * (context.color_count**2 - 1)
    )
    virtual_normalization = 1 / (
        4
        * context.color_count
        * context.s
        * context.electric_charge**2
        * (1 - epsilon)
    )
    virtual_replacements = (
        (context.strong_coupling**2, 4 * pi * alpha_s),
        (context.color_t, E("1")),
        (
            context.color_count**2 - 1,
            2 * context.color_count * color_f,
        ),
    )

    def virtual_endpoint(names: tuple[str, ...]) -> EndpointCoefficient:
        raw = qq_common * sum(
            (selected_value(name) for name in names),
            E("0"),
        )
        normalized = replace_all(
            virtual_normalization * raw,
            virtual_replacements,
        )
        return _endpoint_through_finite(
            EndpointCoefficient(delta=normalized),
            context,
        )

    qq_virtual_triangle = virtual_endpoint(
        insertion_names["virtual triangle 1"]
        + insertion_names["virtual triangle 2"]
    )
    qq_external_bubbles = virtual_endpoint(
        insertion_names["virtual bubble"]
    )

    qq_normalization = 1 / (
        4
        * context.color_count
        * pi
        * context.electric_charge**2
        * (1 - epsilon)
    )
    direct_raw = qq_common * sum(
        (
            selected_value(name)
            for name in insertion_names["qq direct box"]
        ),
        E("0"),
    )
    direct_normalized = replace_all(
        qq_normalization * direct_raw,
        (
            (context.strong_coupling**2, 4 * pi * alpha_s),
            (context.color_t, E("1/2")),
            (
                context.color_count**2 - 1,
                2 * context.color_count * color_f,
            ),
        ),
    )
    qq_direct = _endpoint_through_finite(
        EndpointCoefficient(regular=direct_normalized),
        context,
    )

    def endpoint_from_raw_master(
        name: str,
        exponent_multiple: int,
    ) -> EndpointCoefficient:
        # The endpoint expansion helper represents
        # (1-z)^(-1-exponent_multiple*epsilon); strip exactly that factor
        # from the graph-weighted analytic master to obtain its smooth part.
        normalized_raw = (
            alpha_s
            * color_f
            / (1 - epsilon)
            * selected_value(name)
        )
        smooth = normalize_rational(
            normalized_raw
            * (1 - z) ** (1 + exponent_multiple * epsilon)
        )
        distribution = apply_endpoint_expansion(
            endpoint_distribution_expansion(
                exponent_multiple,
                epsilon,
                order=1,
            ),
            smooth,
            z,
        )
        return EndpointCoefficient(
            delta=distribution.delta_coefficient,
            d0_prefactor=distribution.plus_coefficients[0],
            d1_prefactor=distribution.plus_coefficients[1],
            regular=distribution.regular_part,
        )

    qq_crossed_raw = (
        endpoint_from_raw_master("crossed 10", 1)
        + endpoint_from_raw_master("crossed 01", 1)
        + EndpointCoefficient(
            delta=(
                alpha_s
                * color_f
                / (1 - epsilon)
                * selected_value("crossed 00")
            )
        )
    )
    qq_crossed = _endpoint_through_finite(qq_crossed_raw, context)
    qq_total = (
        qq_virtual_triangle
        + qq_external_bubbles
        + qq_direct
        + qq_crossed
    ).canonical(z)
    # The graph/master sum is already in the physical AEM/convolution
    # normalization.  Multiplication by z belongs only to the historical
    # DY-to-DIS comparison convention and must not redefine the native kernel.
    qq_historical_z_normalization = qq_total.multiply_smooth(z, z)
    qq_double_pole = _endpoint_laurent_coefficient(qq_total, -2, context)
    qq_single_pole = _endpoint_laurent_coefficient(qq_total, -1, context)
    result = NativeDYSchemeChange(
        insertions=insertions,
        insertion_names=insertion_names,
        cut_membership_coefficients=cut_membership_coefficients,
        observable_phases=observable_phases,
        qg_pieces=MappingProxyType(qg_pieces),
        qg_mp_minus_pm=qg_total,
        qg_double_pole_coefficient=qg_double_pole,
        qg_single_pole_coefficient=qg_single_pole,
        qq_virtual_triangle=qq_virtual_triangle,
        qq_external_bubbles=qq_external_bubbles,
        qq_direct=qq_direct,
        qq_crossed=qq_crossed,
        qq_mp_minus_pm=qq_total,
        qq_historical_z_normalization=qq_historical_z_normalization,
        qq_double_pole_coefficient=qq_double_pole,
        qq_single_pole_coefficient=qq_single_pole,
    )
    if not result.internally_consistent(z):
        raise ValueError("Native DY MP-PM graph assembly is internally inconsistent")
    return result


def build_analytic_master_handoff(
    audit: ReductionAudit,
    coefficient: FullDYCoefficient,
    context: DYContext,
    graphs: Mapping[str, DYGraphSpec],
    *,
    scheme_change: NativeDYSchemeChange,
) -> AnalyticMasterHandoff:
    """Insert the audited coefficients into the application-local masters."""

    from calculations.dy.python.masters import (
        apply_endpoint_expansion,
        endpoint_distribution_expansion,
        massive_cut_bubble,
        massive_cut_triangle,
        massless_cut_bubble,
        massless_cut_triangle,
        maximal_cross_box_cut_master,
        uncut_bubble,
        virtuality_integral_factor,
    )

    epsilon = context.epsilon
    s = context.s
    z = context.z
    alpha_s = context.alpha_s
    color_f = context.color_f
    color_t = context.color_t
    electric_charge = context.electric_charge
    strong_coupling = context.strong_coupling
    color_count = context.color_count
    lambda1_squared = context.lambda1_squared
    lambda2_squared = context.lambda2_squared
    mu_r_squared = context.mu_r_squared
    pi = context.pi
    dimension = 4 - 2 * epsilon
    gamma_e = Expression.EULER_GAMMA
    master_arguments = {
        "dimension": dimension,
        "epsilon": epsilon,
        "mu_squared": mu_r_squared,
        "euler_gamma": gamma_e,
    }
    massive_bubble = massive_cut_bubble(
        s,
        z * s,
        **master_arguments,
    )
    # Setting the external virtuality to one strips precisely its
    # (p_i^2)^(-epsilon) leading-power factor.  The physical integral is then
    # supplied by J_i below.
    massive_triangle_stripped = massive_cut_triangle(
        E("1"),
        s,
        z * s,
        **master_arguments,
    )
    massless_bubble_stripped = massless_cut_bubble(
        E("1"),
        **master_arguments,
    )
    massless_triangle_stripped_raw = massless_cut_triangle(
        E("1"),
        E("1"),
        -s,
        **master_arguments,
    )
    # In the declared physical region s>0, the triangle Gram factor obeys
    # (s^2)^(1/2-epsilon)=s^(1-2 epsilon).  Make that branch choice before the
    # Laurent expansion; an exact atom replacement cannot see a fractional
    # power after Symbolica has moved it into a rational denominator.
    massless_triangle_stripped = normalize_rational(
        massless_triangle_stripped_raw
        * (s**2) ** (E("1/2") - epsilon)
        / s ** (1 - 2 * epsilon)
    )
    ordinary_bubble = uncut_bubble(s, **master_arguments)
    maximal_crossed = maximal_cross_box_cut_master(
        s,
        **master_arguments,
    )
    j1 = virtuality_integral_factor(lambda1_squared, epsilon)
    j2 = virtuality_integral_factor(lambda2_squared, epsilon)

    def insertion(
        graph_name: str,
        cut_name: str,
        channel: str,
        sector: str,
        projects: tuple[str, ...],
        ibp_coefficient: Expression,
        analytic_master: Expression,
        *,
        virtuality_factor: Expression = E("1"),
        relative_weight: Expression = E("1"),
    ) -> MasterInsertion:
        return MasterInsertion(
            graph_name=graph_name,
            cut_name=cut_name,
            channel=channel,
            sector=sector,
            projects=projects,
            ibp_coefficient=ibp_coefficient,
            analytic_master=analytic_master,
            virtuality_factor=virtuality_factor,
            relative_weight=relative_weight,
        )

    def graph_cut_weight(
        graph_name: str,
        cut_name: str,
        *,
        mirror_count: int = 1,
    ) -> Expression:
        """Return a notebook-declared graph weight for one master insertion."""

        return graphs[graph_name].cut_weights[cut_name] / mirror_count

    insertions = {
        "virtual 0-cut": insertion(
            "virtual triangle 1",
            "11",
            "virtual",
            "0-cut triangle",
            ("virtual triangle 1/11",),
            replace_all(
                audit.virtual_coefficients["virtual triangle 1/11"],
                ((context.d, dimension),),
            ),
            ordinary_bubble,
            relative_weight=graph_cut_weight("virtual triangle 1", "11"),
        ),
        "virtual p2-cut": insertion(
            "virtual triangle 1",
            "10",
            "virtual",
            "p2-cut triangle",
            ("virtual triangle 1/10",),
            replace_all(
                audit.virtual_coefficients["virtual triangle 1/10"],
                ((context.d, dimension),),
            ),
            massless_bubble_stripped,
            virtuality_factor=j2,
            relative_weight=graph_cut_weight("virtual triangle 1", "10"),
        ),
        "virtual p1-cut": insertion(
            "virtual triangle 1",
            "01",
            "virtual",
            "p1-cut triangle",
            ("virtual triangle 1/01",),
            replace_all(
                audit.virtual_coefficients["virtual triangle 1/01"],
                ((context.d, dimension),),
            ),
            massless_bubble_stripped,
            virtuality_factor=j1,
            relative_weight=graph_cut_weight("virtual triangle 1", "01"),
        ),
        "virtual double-cut": insertion(
            "virtual triangle 2",
            "00",
            "virtual",
            "double-cut triangle",
            ("virtual triangle 2/00",),
            replace_all(
                audit.virtual_coefficients["virtual triangle 2/00"],
                ((context.d, dimension),),
            ),
            massless_triangle_stripped,
            virtuality_factor=j1 * j2,
            relative_weight=graph_cut_weight("virtual triangle 2", "00"),
        ),
        "external bubble p1": insertion(
            "virtual bubble",
            "10",
            "virtual",
            "external bubble p1",
            ("virtual bubble/10",),
            replace_all(
                audit.virtual_coefficients["external bubble"],
                ((context.d, dimension),),
            ),
            massless_bubble_stripped,
            virtuality_factor=j1,
            relative_weight=graph_cut_weight(
                "virtual bubble", "10", mirror_count=2
            ),
        ),
        "external bubble p2": insertion(
            "virtual bubble",
            "10",
            "virtual",
            "external bubble p2",
            ("virtual bubble/10",),
            replace_all(
                audit.virtual_coefficients["external bubble"],
                ((context.d, dimension),),
            ),
            massless_bubble_stripped,
            virtuality_factor=j2,
            relative_weight=graph_cut_weight(
                "virtual bubble", "10", mirror_count=2
            ),
        ),
        "direct 00": insertion(
            "qq direct box",
            "11",
            "direct qqbar",
            "00",
            ("qq direct box/11",),
            audit.direct_box_coefficients["11"],
            massive_bubble,
            relative_weight=graph_cut_weight("qq direct box", "11"),
        ),
        "direct 10": insertion(
            "qq direct box",
            "01",
            "direct qqbar",
            "10",
            ("qq direct box/01",),
            audit.direct_box_coefficients["01"],
            massive_triangle_stripped,
            virtuality_factor=j1,
            relative_weight=graph_cut_weight(
                "qq direct box", "01", mirror_count=2
            ),
        ),
        "direct 01": insertion(
            "qq direct box",
            "01",
            "direct qqbar",
            "01",
            ("qq direct box/01",),
            audit.direct_box_coefficients["01"],
            massive_triangle_stripped,
            virtuality_factor=j2,
            relative_weight=graph_cut_weight(
                "qq direct box", "01", mirror_count=2
            ),
        ),
        "crossed 11": insertion(
            "qq crossed box",
            "11",
            "crossed qqbar",
            "11",
            ("qq crossed box/11 (four apart children)",),
            audit.crossed_box_coefficients["11"],
            massive_bubble,
            relative_weight=graph_cut_weight("qq crossed box", "11"),
        ),
        "crossed 10": insertion(
            "qq crossed box",
            "10",
            "crossed qqbar",
            "10",
            ("qq crossed box/10 (four apart children)",),
            audit.crossed_box_coefficients["10"],
            massive_triangle_stripped,
            virtuality_factor=j2,
            relative_weight=graph_cut_weight("qq crossed box", "10"),
        ),
        "crossed 01": insertion(
            "qq crossed box",
            "01",
            "crossed qqbar",
            "01",
            ("qq crossed box/01 (four apart children)",),
            audit.crossed_box_coefficients["01"],
            massive_triangle_stripped,
            virtuality_factor=j1,
            relative_weight=graph_cut_weight("qq crossed box", "01"),
        ),
        # In the retained z-space source the 00 object is negated once when it
        # is defined and again in the four-cut sum.  Its numerator coefficient
        # already carries the remaining minus sign; encoding that sequence as
        # relative_weight=+1 makes the convention visible.
        "crossed 00": insertion(
            "qq crossed box",
            "00",
            "crossed qqbar",
            "00",
            (),
            audit.crossed_box_coefficients["00"],
            maximal_crossed,
            virtuality_factor=j1 * j2,
            relative_weight=graph_cut_weight("qq crossed box", "00"),
        ),
        "qg box 00": insertion(
            "qg box",
            "11",
            "qg",
            "box 00",
            ("qg box/11",),
            audit.qg_coefficients["11 box"],
            massive_bubble,
            relative_weight=graph_cut_weight("qg box", "11"),
        ),
        "qg box 10": insertion(
            "qg box",
            "01",
            "qg",
            "box 10",
            ("qg box/01",),
            audit.qg_coefficients["01 box"],
            massive_triangle_stripped,
            virtuality_factor=j1,
            relative_weight=graph_cut_weight(
                "qg box", "01", mirror_count=2
            ),
        ),
        "qg box 01": insertion(
            "qg box",
            "01",
            "qg",
            "box 01",
            ("qg box/01",),
            audit.qg_coefficients["01 box"],
            massive_triangle_stripped,
            virtuality_factor=j2,
            relative_weight=graph_cut_weight(
                "qg box", "01", mirror_count=2
            ),
        ),
        "qg triangle 00": insertion(
            "qg triangle",
            "11",
            "qg",
            "triangle 00",
            ("qg triangle/11",),
            audit.qg_coefficients["11 triangle"],
            massive_bubble,
            relative_weight=graph_cut_weight("qg triangle", "11"),
        ),
        "qg triangle 10": insertion(
            "qg triangle",
            "01",
            "qg",
            "triangle 10",
            ("qg triangle/01",),
            audit.qg_coefficients["01 triangle"],
            massive_triangle_stripped,
            virtuality_factor=j1,
            relative_weight=graph_cut_weight(
                "qg triangle", "01", mirror_count=2
            ),
        ),
        "qg triangle 01": insertion(
            "qg triangle",
            "01",
            "qg",
            "triangle 01",
            ("qg triangle/01",),
            audit.qg_coefficients["01 triangle"],
            massive_triangle_stripped,
            virtuality_factor=j2,
            relative_weight=graph_cut_weight(
                "qg triangle", "01", mirror_count=2
            ),
        ),
        "qg bubble 00": insertion(
            "qg bubble",
            "11",
            "qg",
            "bubble 00",
            ("qg bubble/11",),
            audit.qg_coefficients["11 bubble"],
            massive_bubble,
            relative_weight=graph_cut_weight("qg bubble", "11"),
        ),
    }
    insertion_map = MappingProxyType(insertions)

    qq_common = (
        electric_charge**2
        * strong_coupling**2
        * color_t
        * (color_count**2 - 1)
    )
    qg_common = electric_charge**2 * strong_coupling**2 * color_t
    qq_normalization = (
        1
        / (
            2
            * color_count
            * 2
            * pi
            * electric_charge**2
            * (1 - epsilon)
        )
    )
    qg_normalization = 1 / (
        8 * pi * (1 - epsilon) * electric_charge**2
    )
    virtual_normalization = 1 / (
        4
        * color_count
        * s
        * electric_charge**2
        * (1 - epsilon)
    )
    normalization_factors = MappingProxyType(
        {
            "qqbar common graph factor": qq_common,
            "qqbar Born normalization": qq_normalization,
            "qg common graph factor": qg_common,
            "qg Born normalization": qg_normalization,
            "local all-cut virtual normalization": virtual_normalization,
        }
    )

    direct_raw = qq_common * sum(
        (
            item.value
            for item in insertion_map.values()
            if item.channel == "direct qqbar"
        ),
        E("0"),
    )
    direct_normalized = replace_all(
        qq_normalization * direct_raw,
        (
            (strong_coupling**2, 4 * pi * alpha_s),
            (color_t, E("1/2")),
        ),
    )
    direct_finite = _finite_laurent_coefficient(direct_normalized, context)
    direct_expected = _expand_positive_branch_logs(
        coefficient.qq_transverse.pieces[
            "direct box plus mirror"
        ].canonical(z).regular.replace(
            color_f,
            (color_count**2 - 1) / (2 * color_count),
        ),
        context,
    )
    direct_residual = normalize_rational(direct_finite - direct_expected)

    qg_raw = qg_common * sum(
        (
            item.value
            for item in insertion_map.values()
            if item.channel == "qg"
        ),
        E("0"),
    )
    qg_normalized = replace_all(
        qg_normalization * qg_raw,
        ((strong_coupling**2, 4 * pi * alpha_s),),
    )
    qg_finite = _finite_laurent_coefficient(qg_normalized, context)
    qg_expected = _expand_positive_branch_logs(
        coefficient.qg_transverse.total.regular,
        context,
    )
    qg_residual = normalize_rational(qg_finite - qg_expected)

    external_bubble_through_finite = (
        derive_external_bubble_scheme_correction(
            context,
            bubble_coefficient=audit.virtual_coefficients["external bubble"],
        )
    )
    external_bubble_expected = EndpointCoefficient(
        delta=alpha_s
        * color_f
        / (2 * pi)
        * (
            -1 / epsilon
            - 1
            + lambda1_squared.log() / 2
            + lambda2_squared.log() / 2
            - mu_r_squared.log()
        )
    )
    external_bubble_expected_residual = (
        external_bubble_through_finite - external_bubble_expected
    )

    # Expand the four crossed-box cuts as endpoint distributions.  These
    # smooth prefactors are written directly in terms of the audited IBP
    # coefficients and the compact positive-branch forms of the same masters
    # recorded in ``insertions`` above.  In particular, the 11 prefactor uses
    # Gamma duplication to remove Gamma(3/2-epsilon), and the 00 term is the
    # analytic four-line master rather than a fictitious Kira family.
    endpoint_variable = 1 - z
    dimensional_scale = (
        mu_r_squared * gamma_e.exp()
    ) ** epsilon
    normalized_qq_graph = (
        alpha_s
        * (color_count**2 - 1)
        / (2 * color_count * (1 - epsilon))
    )
    gamma_one_minus_epsilon = (1 - epsilon).gamma()
    crossed_smooth_prefactors = {
        "11": normalize_rational(
            normalized_qq_graph
            * audit.crossed_box_coefficients["11"]
            * dimensional_scale
            * s ** (-epsilon)
            * gamma_one_minus_epsilon
            / (8 * pi * (2 - 2 * epsilon).gamma())
            * endpoint_variable**2,
        ),
        "10": normalize_rational(
            normalized_qq_graph
            * audit.crossed_box_coefficients["10"]
            * dimensional_scale
            * z ** (-epsilon)
            / (4 * gamma_one_minus_epsilon * s)
            * j2
            * endpoint_variable,
        ),
        "01": normalize_rational(
            normalized_qq_graph
            * audit.crossed_box_coefficients["01"]
            * dimensional_scale
            * z ** (-epsilon)
            / (4 * gamma_one_minus_epsilon * s)
            * j1
            * endpoint_variable,
        ),
    }

    def endpoint_from_smooth_prefactor(
        prefactor: Expression,
        exponent_multiple: int,
    ) -> EndpointCoefficient:
        distribution = apply_endpoint_expansion(
            endpoint_distribution_expansion(
                exponent_multiple,
                epsilon,
                order=1,
            ),
            prefactor,
            z,
        )
        return EndpointCoefficient(
            delta=distribution.delta_coefficient,
            d0_prefactor=distribution.plus_coefficients[0],
            d1_prefactor=distribution.plus_coefficients[1],
            regular=distribution.regular_part,
        )

    crossed_cut_endpoint = {
        "11": endpoint_from_smooth_prefactor(
            crossed_smooth_prefactors["11"],
            2,
        ),
        "10": endpoint_from_smooth_prefactor(
            crossed_smooth_prefactors["10"],
            1,
        ),
        "01": endpoint_from_smooth_prefactor(
            crossed_smooth_prefactors["01"],
            1,
        ),
        "00": EndpointCoefficient(
            delta=normalize_rational(
                normalized_qq_graph
                * audit.crossed_box_coefficients["00"]
                * dimensional_scale
                * pi
                * s ** (-2 + epsilon)
                / (2 * gamma_one_minus_epsilon)
                * j1
                * j2,
            )
        ),
    }
    crossed_endpoint_sum = sum(
        crossed_cut_endpoint.values(),
        EndpointCoefficient(),
    )
    crossed_poles = MappingProxyType(
        {
            power: _endpoint_laurent_coefficient(
                crossed_endpoint_sum,
                power,
                context,
            )
            for power in (-2, -1)
        }
    )
    crossed_finite = _endpoint_laurent_coefficient(
        crossed_endpoint_sum,
        0,
        context,
    )
    crossed_target = coefficient.qq_transverse.pieces[
        "crossed box, all four cuts"
    ]
    color_f_in_nc = (color_count**2 - 1) / (2 * color_count)
    crossed_expected = _endpoint_laurent_coefficient(
        dataclass_replace(
            crossed_target,
            delta=crossed_target.delta.replace(color_f, color_f_in_nc),
            d0_prefactor=crossed_target.d0_prefactor.replace(
                color_f,
                color_f_in_nc,
            ),
            d1_prefactor=crossed_target.d1_prefactor.replace(
                color_f,
                color_f_in_nc,
            ),
            regular=crossed_target.regular.replace(color_f, color_f_in_nc),
        ),
        0,
        context,
    )
    crossed_finite_residual = crossed_finite - crossed_expected

    return AnalyticMasterHandoff(
        insertions=insertion_map,
        normalization_factors=normalization_factors,
        direct_normalized_raw=direct_normalized,
        direct_finite=direct_finite,
        direct_finite_residual=direct_residual,
        qg_normalized_raw=qg_normalized,
        qg_finite=qg_finite,
        qg_finite_residual=qg_residual,
        external_bubble_through_finite=external_bubble_through_finite,
        external_bubble_expected_residual=external_bubble_expected_residual,
        crossed_cut_endpoint=MappingProxyType(crossed_cut_endpoint),
        crossed_pole_residuals=crossed_poles,
        crossed_finite=crossed_finite,
        crossed_finite_residual=crossed_finite_residual,
        scheme_change=scheme_change,
    )


def assemble_closed_form_dy(context: DYContext) -> FullDYCoefficient:
    """Encode the retained finite channels and separate virtual diagnostics."""

    epsilon = context.epsilon
    s = context.s
    z = context.z
    alpha_s = context.alpha_s
    color_f = context.color_f
    color_t = context.color_t
    lambda1_squared = context.lambda1_squared
    lambda2_squared = context.lambda2_squared
    mu_r_squared = context.mu_r_squared
    pi = context.pi
    qq_normalization = alpha_s * color_f / (2 * pi)
    cutoff_log = (
        lambda1_squared * lambda2_squared * z**2 / s**2
    ).log()
    cutoff_log_at_endpoint = (
        lambda1_squared * lambda2_squared / s**2
    ).log()
    mu_log = (mu_r_squared / s).log()
    ordinary_virtual = EndpointCoefficient(
        delta=qq_normalization
        * (
            -2 / epsilon**2
            - (3 + 2 * mu_log) / epsilon
            - 8
            + 7 * pi**2 / 6
            - 3 * mu_log
            - mu_log**2
        )
    )
    x1 = (lambda1_squared / mu_r_squared).log()
    x2 = (lambda2_squared / mu_r_squared).log()
    local_all_cut_virtual = EndpointCoefficient(
        delta=2
        * alpha_s
        * color_f
        / pi
        * (
            Expression.I * pi / epsilon
            - E("1/4")
            + 5 * pi**2 / 6
            - 3 * mu_log / 4
            - mu_log**2 / 2
            - 3 * (x1 + x2) / 8
            - mu_log * (x1 + x2) / 2
            - x1 * x2 / 2
            + Expression.I * pi * (E("3/2") + mu_log)
        )
    )
    # Source convention:
    # Pqq(z,0) = 3/2 delta(1-z) + (1+z^2) D0(z)
    #           = 3/2 delta(1-z) + 2 z D0(z) + (1-z).
    pqq_times_cutoff_log = EndpointCoefficient(
        delta=qq_normalization * E("3/2") * cutoff_log_at_endpoint,
        d0_prefactor=qq_normalization * (1 + z**2) * cutoff_log,
    )
    transverse_total = pqq_times_cutoff_log + EndpointCoefficient(
        delta=qq_normalization * (1 - 3 * pi**2),
        d1_prefactor=-2 * qq_normalization * (1 + z**2),
        regular=qq_normalization * (4 - 2 * z),
    )
    # This explicit plus-basis representation is distribution-equal to
    # A[(1-z) log(Lambda1^2 Lambda2^2 z^2/(s^2(1-z)^2)) + 4 - 2z].
    direct_box = EndpointCoefficient(
        d0_prefactor=qq_normalization * (1 - z) ** 2 * cutoff_log,
        d1_prefactor=-2 * qq_normalization * (1 - z) ** 2,
        regular=qq_normalization * (4 - 2 * z),
    )
    ell1 = (lambda1_squared / s).log()
    ell2 = (lambda2_squared / s).log()
    crossed_box = EndpointCoefficient(
        delta=qq_normalization * (pi**2 / 3 - 2 * ell1 * ell2),
        d0_prefactor=qq_normalization * 2 * z * cutoff_log,
        d1_prefactor=-4 * qq_normalization * z,
    )
    virtual_and_all_cuts = EndpointCoefficient(
        delta=qq_normalization
        * (
            1
            - 10 * pi**2 / 3
            + 2 * ell1 * ell2
            + E("3/2") * cutoff_log_at_endpoint
        )
    )
    qq_transverse_pieces = MappingProxyType(
        {
            "physical virtual = -Re(local all-cut)": virtual_and_all_cuts,
            "direct box plus mirror": direct_box,
            "crossed box, all four cuts": crossed_box,
        }
    )
    qq_transverse = ChannelAssembly(
        pieces=qq_transverse_pieces,
        total=sum(qq_transverse_pieces.values(), EndpointCoefficient()),
    )
    if not (qq_transverse.total - transverse_total).is_zero_for(z):
        raise ValueError("Transverse qqbar graph ledger did not reconstruct its sum")
    recorded_mathematica_total = pqq_times_cutoff_log + EndpointCoefficient(
        delta=qq_normalization * (1 - 3 * pi**2),
        d1_prefactor=-2 * qq_normalization * (1 + z**2),
        regular=qq_normalization * (1 + 3 * z - 2 * z**2) / z,
    )
    qq_manuscript = pqq_times_cutoff_log + EndpointCoefficient(
        delta=qq_normalization * (1 - 3 * pi**2),
        d1_prefactor=2 * qq_normalization * (1 + z**2),
        regular=qq_normalization * (1 + 3 * z - z**2) / z,
    )

    pqg = 1 - 2 * z + 2 * z**2
    qg_log = (
        lambda1_squared
        * lambda2_squared
        * z**2
        / (s**2 * (1 - z) ** 2)
    ).log()
    qg_graph_normalization = alpha_s * color_t / (4 * pi)
    qg_pieces = MappingProxyType(
        {
            "box": EndpointCoefficient(
                regular=2 * qg_graph_normalization * (1 + qg_log / 2)
            ),
            "triangle pair": EndpointCoefficient(
                regular=-2
                * qg_graph_normalization
                * z
                * (1 - z)
                * (2 + qg_log)
            ),
            "bubble": EndpointCoefficient(
                regular=-qg_graph_normalization * (1 - z) ** 2
            ),
        }
    )
    qg_transverse_total = sum(qg_pieces.values(), EndpointCoefficient())
    qg_transverse = ChannelAssembly(
        pieces=qg_pieces,
        total=qg_transverse_total,
    )
    qg_ward_remainder = EndpointCoefficient(
        regular=qg_graph_normalization * (1 - z) ** 2 / z
    )
    qg_recorded_mathematica = qg_transverse_total + qg_ward_remainder
    qg_manuscript = EndpointCoefficient(
        regular=qg_graph_normalization
        / z
        * (
            1
            + z**3
            + z**2
            - 2 * z
            + z * pqg * (1 + qg_log)
        )
    )
    return FullDYCoefficient(
        ordinary_virtual=ordinary_virtual,
        local_all_cut_virtual=local_all_cut_virtual,
        qq_transverse=qq_transverse,
        qq_recorded_mathematica=recorded_mathematica_total,
        qq_manuscript=qq_manuscript,
        qq_transverse_minus_recorded_mathematica=(
            qq_transverse.total - recorded_mathematica_total
        ),
        qq_transverse_minus_manuscript=qq_transverse.total - qq_manuscript,
        qq_recorded_mathematica_minus_manuscript=(
            recorded_mathematica_total - qq_manuscript
        ),
        qg_transverse=qg_transverse,
        qg_recorded_mathematica=qg_recorded_mathematica,
        qg_manuscript=qg_manuscript,
        qg_transverse_minus_manuscript=qg_transverse_total - qg_manuscript,
    )


def assemble_native_dy_scheme(
    reductions: Mapping[DYProjectKey, ReductionResult],
    *,
    plan: DYProjectPlan,
    context: DYContext,
    graphs: Mapping[str, DYGraphSpec],
    numerators: Mapping[str, Expression],
    ward_numerators: Mapping[str, Expression],
) -> tuple[ReductionAudit, NativeDYSchemeChange]:
    """Audit graph reductions and build the native DY scheme kernel only.

    This is the primary physical API.  It has no closed-form coefficient or
    historical-source construction, so a malformed downstream oracle cannot
    prevent the native ``MP - PM`` result from being assembled.
    """

    audit = audit_physical_reductions(
        reductions,
        plan=plan,
        context=context,
        graphs=graphs,
        numerators=numerators,
        ward_numerators=ward_numerators,
    )
    if not audit.native_complete:
        raise ValueError(
            "Physical reduction audit contains a nonzero native residual"
        )
    scheme_change = build_native_dy_scheme_change(audit, context, graphs)
    return audit, scheme_change


def assemble_reference_dy_handoff(
    audit: ReductionAudit,
    scheme_change: NativeDYSchemeChange,
    *,
    context: DYContext,
    graphs: Mapping[str, DYGraphSpec],
) -> FullDYCoefficient:
    """Attach closed-form and historical ledgers downstream of native DY."""

    coefficient = assemble_closed_form_dy(context)
    handoff = build_analytic_master_handoff(
        audit,
        coefficient,
        context,
        graphs,
        scheme_change=scheme_change,
    )
    if not handoff.native_checks_exact(context.z):
        raise ValueError("Analytic-master handoff has a nonzero native residual")
    return dataclass_replace(coefficient, master_handoff=handoff)


def assemble_full_dy(
    reductions: Mapping[DYProjectKey, ReductionResult],
    *,
    plan: DYProjectPlan,
    context: DYContext,
    graphs: Mapping[str, DYGraphSpec],
    numerators: Mapping[str, Expression],
    ward_numerators: Mapping[str, Expression],
) -> tuple[ReductionAudit, FullDYCoefficient]:
    """Backward-compatible native assembly plus downstream reference ledgers."""

    audit, scheme_change = assemble_native_dy_scheme(
        reductions,
        plan=plan,
        context=context,
        graphs=graphs,
        numerators=numerators,
        ward_numerators=ward_numerators,
    )
    coefficient = assemble_reference_dy_handoff(
        audit,
        scheme_change,
        context=context,
        graphs=graphs,
    )
    return audit, coefficient


__all__ = [
    "AnalyticMasterHandoff",
    "ApartTerm",
    "ChannelAssembly",
    "DYContext",
    "DYGraphSpec",
    "DYProjectKey",
    "DYProjectPlan",
    "EndpointCoefficient",
    "FullDYCoefficient",
    "MasterInsertion",
    "NativeDYSchemeChange",
    "NativeDYOneLegSchemeKernel",
    "NumeratorReduction",
    "ReductionAudit",
    "assemble_closed_form_dy",
    "assemble_full_dy",
    "assemble_native_dy_scheme",
    "assemble_reference_dy_handoff",
    "audit_physical_reductions",
    "build_analytic_master_handoff",
    "build_native_dy_scheme_change",
    "build_dy_kira_projects",
    "crossed_box_reductions",
    "derive_external_bubble_scheme_correction",
    "normalize_rational",
    "numerator_reductions",
    "native_dy_one_leg_scheme_kernel",
    "qg_ward_reductions",
    "reduce_numerator",
    "replace_all",
]
