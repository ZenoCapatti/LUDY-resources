"""Exact, side-effect-free input model for the NLO DIS validation.

This module records the finite-virtuality kinematics, five physical topology
inputs, their six rooted graph records, and the compact cut ledger.  Gamma
chains, denominator powers, channel factors, and Kira handoffs are compiled
from those topology records; neither a Kira object nor a closed coefficient
function is a graph input.  The 18 numerator reconstructions map to 48
cut-preserving targets covered by the 16 cut-specialized Kira projects.

Importing this module never starts Kira.  :func:`self_check` performs only
exact Symbolica checks and deterministic in-memory Kira serialization.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from itertools import combinations, product
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, cast

from kirapy import (
    IntegralFamily,
    KinematicInvariant,
    Kinematics,
    KiraProject,
    Propagator,
    ReductionBounds,
    ReductionResult,
    ScalarProductRule,
)
from symbolica import E, S, Expression

from calculations.dis.python.masters import NORMALIZATION_SELF_CHECKS
from notebooks.ludy import (
    apart_kernel,
    gamma_trace_to_dots,
    reduce_numerator,
    scalar_printer,
)

if TYPE_CHECKING:
    from calculations.dis.python.assembly import (
        DISMasterInsertionAudit,
        RaisedExternalReductionAudit,
    )


MANUSCRIPT_SOURCE = "paper/main.tex"
MANUSCRIPT_SOURCE_SHA256 = (
    "f03be253167e7b65f774a499c0aa14a3a70c2896ca632ea0a6480187a1c0e60b"
)
MANUSCRIPT_SOURCE_BYTES = 53_784
HISTORICAL_SOURCE = "arXiv:2506.16489v1"
DIS_RESULT_SOURCE = f"{MANUSCRIPT_SOURCE}:285-308"
DIS_INTEGRAND_SOURCE = f"{MANUSCRIPT_SOURCE}:433-449"
HISTORICAL_ALL_CUT_SOURCE = (
    f"{HISTORICAL_SOURCE}, Submission/Discontinuities.tex:127-168,180-193"
)


def _expression(value: Expression | int | str) -> Expression:
    """Convert a scalar input to one exact Symbolica expression."""

    return value if isinstance(value, Expression) else E(str(value))


def canonical(expression: Expression | int) -> Expression:
    """Canonical expanded rational form used by exact scalar checks."""

    return _expression(expression).expand().together().cancel()


def _is_zero(expression: Expression | int) -> bool:
    """Return a Python bool for an exact Symbolica zero comparison."""

    return canonical(expression).format_plain() == "0"


# Stable internal names retain deterministic Kira serialization; display-only
# printers make the same symbols readable in Marimo, LaTeX, and Typst.
d = S("d")
epsilon = S(
    "epsilon",
    print=scalar_printer(latex=r"\epsilon", typst="epsilon"),
)
x = S("x", print=scalar_printer(latex="x", typst="x"))
p_squared = S(
    "p_squared",
    print=scalar_printer(latex=r"p^2", typst="p^2"),
)
Q_squared = S(
    "Q_squared",
    print=scalar_printer(latex=r"Q^2", typst="Q^2"),
)
lambda_squared = S(
    "Lambda_squared",
    print=scalar_printer(latex=r"\Lambda^2", typst="Lambda^2"),
)
mu_r_squared = S(
    "mu_R_squared",
    print=scalar_printer(latex=r"\mu_R^2", typst="mu_R^2"),
)
kk = S("kk", print=scalar_printer(latex=r"k^2", typst="k^2"))
kp = S(
    "kp",
    print=scalar_printer(latex=r"k\!\cdot\!p", typst="k dot p"),
)
kq = S(
    "kq",
    print=scalar_printer(latex=r"k\!\cdot\!q", typst="k dot q"),
)
k = S("k", print=scalar_printer(latex="k", typst="k"))
p = S("p", print=scalar_printer(latex="p", typst="p"))
q = S("q", print=scalar_printer(latex="q", typst="q"))
electric_charge = S(
    "e_q",
    print=scalar_printer(latex=r"e_q", typst="e_q"),
)
strong_coupling = S(
    "g_s",
    print=scalar_printer(latex=r"g_s", typst="g_s"),
)
alpha_s = S(
    "alpha_s",
    print=scalar_printer(latex=r"\alpha_s", typst="alpha_s"),
)
color_f = S(
    "C_F",
    print=scalar_printer(latex=r"C_F", typst="C_F"),
)
color_t = S(
    "T_F",
    print=scalar_printer(latex=r"T_F", typst="T_F"),
)
color_count = S(
    "N_c",
    print=scalar_printer(latex=r"N_c", typst="N_c"),
)
pi = Expression.PI


@dataclass(frozen=True, slots=True)
class DISKinematics:
    """Finite-virtuality DIS invariants in the manuscript parametrization."""

    dimension: Expression = d
    regulator: Expression = epsilon
    bjorken_x: Expression = x
    incoming_virtuality: Expression = p_squared
    photon_scale: Expression = Q_squared
    cutoff: Expression = lambda_squared
    renormalization_scale: Expression = mu_r_squared
    loop_square: Expression = kk
    loop_dot_p: Expression = kp
    loop_dot_q: Expression = kq
    loop_momentum: Expression = k
    incoming_momentum: Expression = p
    photon_momentum: Expression = q

    @property
    def p_dot_q(self) -> Expression:
        """Exact ``p.q`` implied by the stated light-cone momentum."""

        return (
            self.photon_scale / self.bjorken_x
            - self.bjorken_x * self.incoming_virtuality
        ) / 2

    @property
    def final_state_invariant(self) -> Expression:
        """Exact ``(p+q)^2``, with its discontinuity factor exposed."""

        return (1 - self.bjorken_x) * (
            self.photon_scale / self.bjorken_x
            + self.incoming_virtuality
        )

    @property
    def scalar_denominators(self) -> tuple[Expression, ...]:
        """The ordered scalar denominators ``D1,...,D6`` of the paper."""

        return (
            self.loop_square,
            self.loop_square
            + 2 * self.loop_dot_p
            + self.incoming_virtuality,
            self.loop_square
            + 2 * self.loop_dot_p
            + 2 * self.loop_dot_q
            + self.final_state_invariant,
            self.loop_square + 2 * self.loop_dot_q - self.photon_scale,
            self.incoming_virtuality,
            self.final_state_invariant,
        )

    def kira_kinematics(
        self,
        *,
        cut_lines: Sequence[int] = (),
    ) -> Kinematics:
        """Return exact off-shell or cut-specialized Kira kinematics.

        Cutting ``D5`` imposes ``p^2=0``.  Cutting ``D6=(p+q)^2`` imposes
        ``x=1`` in the exact finite-virtuality parametrization.  These are
        algebraic consequences of the declared denominators; cut orientation
        and relative weights remain separate metadata.
        """

        cut_set = set(cut_lines)
        if any(line < 1 or line > 6 for line in cut_set):
            raise ValueError("DIS cut lines must be one-based D1,...,D6 positions")
        p2_value = E("0") if 5 in cut_set else self.incoming_virtuality
        x_value = E("1") if 6 in cut_set else self.bjorken_x
        p_dot_q_value = (
            self.photon_scale / x_value - x_value * p2_value
        ) / 2
        invariants = [KinematicInvariant(self.photon_scale, 2)]
        if 5 not in cut_set:
            invariants.append(KinematicInvariant(self.incoming_virtuality, 2))
        if 6 not in cut_set:
            invariants.insert(0, KinematicInvariant(self.bjorken_x, 0))

        return Kinematics(
            incoming_momenta=(self.incoming_momentum, self.photon_momentum),
            kinematic_invariants=tuple(invariants),
            scalar_products=(
                ScalarProductRule(
                    self.incoming_momentum,
                    self.incoming_momentum,
                    p2_value,
                ),
                ScalarProductRule(
                    self.photon_momentum,
                    self.photon_momentum,
                    -self.photon_scale,
                ),
                ScalarProductRule(
                    self.incoming_momentum,
                    self.photon_momentum,
                    p_dot_q_value,
                ),
            ),
            symbol_to_replace_by_one=self.photon_scale,
        )


DIS_KINEMATICS = DISKinematics()


@dataclass(frozen=True, slots=True)
class MomentumCombination:
    """A representation-independent linear combination of ``k``, ``p``, ``q``."""

    k_coefficient: int = 0
    p_coefficient: int = 0
    q_coefficient: int = 0

    def __post_init__(self) -> None:
        if all(
            coefficient == 0
            for coefficient in (
                self.k_coefficient,
                self.p_coefficient,
                self.q_coefficient,
            )
        ):
            raise ValueError("A slashed momentum combination cannot be zero")

    def evaluate(self, k_value, p_value, q_value):
        """Instantiate the combination with scalar or Spenso momenta."""

        terms = [
            coefficient * value
            for coefficient, value in (
                (self.k_coefficient, k_value),
                (self.p_coefficient, p_value),
                (self.q_coefficient, q_value),
            )
            if coefficient
        ]
        return sum(terms[1:], terms[0])

    @property
    def plain(self) -> str:
        terms: list[str] = []
        for coefficient, name in (
            (self.k_coefficient, "k"),
            (self.p_coefficient, "p"),
            (self.q_coefficient, "q"),
        ):
            if coefficient == 1:
                terms.append(name)
            elif coefficient == -1:
                terms.append(f"-{name}")
            elif coefficient:
                terms.append(f"{coefficient}*{name}")
        return "+".join(terms).replace("+-", "-")


K = MomentumCombination(k_coefficient=1)
P = MomentumCombination(p_coefficient=1)
Q = MomentumCombination(q_coefficient=1)
KP = MomentumCombination(k_coefficient=1, p_coefficient=1)
KQ = MomentumCombination(k_coefficient=1, q_coefficient=1)
PQ = MomentumCombination(p_coefficient=1, q_coefficient=1)
KPQ = MomentumCombination(k_coefficient=1, p_coefficient=1, q_coefficient=1)


@dataclass(frozen=True, slots=True)
class GammaTraceSpec:
    """One closed eight-gamma trace with two distinguished photon slots.

    ``None`` denotes an unslashed gamma carrying its corresponding Lorentz
    label.  A :class:`MomentumCombination` denotes a slash contracted into that
    gamma.  Repeated non-photon labels encode the contracted gluon index.
    """

    vectors: tuple[MomentumCombination | None, ...]
    lorentz_labels: tuple[str, ...]
    photon_slots: tuple[int, int]

    def __post_init__(self) -> None:
        if len(self.vectors) != 8 or len(self.lorentz_labels) != 8:
            raise ValueError("Every manuscript DIS numerator has eight gamma factors")
        if len(set(self.photon_slots)) != 2:
            raise ValueError("The two photon slots must be distinct")
        if any(slot < 0 or slot >= 8 for slot in self.photon_slots):
            raise ValueError("Photon slot is outside the gamma chain")
        if any(self.vectors[slot] is not None for slot in self.photon_slots):
            raise ValueError("Photon slots must be unslashed in the source trace")

    def instantiated_vectors(self, k_value, p_value, q_value) -> tuple[object, ...]:
        """Instantiate slash momenta for ``gamma_trace_to_dots``."""

        return tuple(
            None if vector is None else vector.evaluate(k_value, p_value, q_value)
            for vector in self.vectors
        )


Channel = Literal["q", "g"]
VertexKind = Literal["gluon", "photon_mu", "photon_nu"]


@dataclass(frozen=True, slots=True)
class DISRootedTopology:
    """One rooted fermion cycle compiled from a physical topology.

    ``fermion_momenta`` and ``vertices`` alternate around the cycle.  This is
    the editable numerator input: the gamma chain is generated from it rather
    than separately transcribed.  ``multiplicity`` counts equivalent rooted
    embeddings of the same compact topology.
    """

    name: str
    powers: tuple[int, int, int, int, int, int]
    fermion_momenta: tuple[
        MomentumCombination,
        MomentumCombination,
        MomentumCombination,
        MomentumCombination,
    ]
    vertices: tuple[VertexKind, VertexKind, VertexKind, VertexKind]
    multiplicity: int = 1

    def __post_init__(self) -> None:
        if len(self.powers) != 6 or any(power < 0 for power in self.powers):
            raise ValueError("A rooted DIS topology needs six non-negative powers")
        if self.multiplicity < 1:
            raise ValueError("A rooted topology multiplicity must be positive")
        if set(self.vertices) != {"gluon", "photon_mu", "photon_nu"}:
            raise ValueError(
                "A DIS fermion cycle needs one repeated gluon vertex and "
                "the mu/nu photon vertices"
            )
        if self.vertices.count("gluon") != 2:
            raise ValueError("The NLO DIS cycle needs exactly two gluon vertices")


@dataclass(frozen=True, slots=True)
class DISGraphTopology:
    """One compact graph topology and its physically distinct rootings.

    The phase is the Feynman-rule phase after stripping the common scalar-loop
    master convention.  For an open-quark cycle it is ``-1``; the gluon
    channel cycles use ``+1``.  Colour, coupling, and incoming-state averages
    are kept in :attr:`channel_prefactor` and are not duplicated in rootings.
    """

    name: str
    channel: Channel
    graph_phase: Expression
    rootings: tuple[DISRootedTopology, ...]
    source: str = DIS_INTEGRAND_SOURCE

    def __post_init__(self) -> None:
        object.__setattr__(self, "graph_phase", _expression(self.graph_phase))
        if not self.rootings:
            raise ValueError("A compact DIS topology needs at least one rooting")

    @property
    def channel_prefactor(self) -> Expression:
        """Full common trace/colour/spin factor before scalar integration."""

        if self.channel == "q":
            return electric_charge**2 * strong_coupling**2 * color_f / 2
        return (
            electric_charge**2
            * strong_coupling**2
            * color_t
            / (d - 2)
        )


@dataclass(frozen=True, slots=True)
class DISGraphSpec:
    """One compiled rooted graph in the common ``D1,...,D6`` basis."""

    name: str
    channel: Channel
    powers: tuple[int, int, int, int, int, int]
    trace: GammaTraceSpec
    relative_weight: Expression
    channel_prefactor: Expression
    parent_topology: str
    source: str = DIS_INTEGRAND_SOURCE

    def __post_init__(self) -> None:
        if len(self.powers) != 6 or any(power < 0 for power in self.powers):
            raise ValueError("A DIS graph needs six non-negative denominator powers")
        object.__setattr__(self, "relative_weight", _expression(self.relative_weight))
        object.__setattr__(self, "channel_prefactor", _expression(self.channel_prefactor))


def _root(
    name: str,
    powers: tuple[int, int, int, int, int, int],
    fermion_momenta: tuple[
        MomentumCombination,
        MomentumCombination,
        MomentumCombination,
        MomentumCombination,
    ],
    vertices: tuple[VertexKind, VertexKind, VertexKind, VertexKind],
    *,
    multiplicity: int = 1,
) -> DISRootedTopology:
    return DISRootedTopology(
        name=name,
        powers=powers,
        fermion_momenta=fermion_momenta,
        vertices=vertices,
        multiplicity=multiplicity,
    )


# Five editable physical inputs.  The quark self-energy topology has two
# inequivalent roots, giving the six compiled graph records used downstream.
DIS_GRAPH_TOPOLOGIES: tuple[DISGraphTopology, ...] = (
    DISGraphTopology(
        name="q_triangle_topology",
        channel="q",
        graph_phase=E("-1"),
        rootings=(
            _root(
                "q_triangle",
                (1, 1, 1, 0, 1, 1),
                (P, KP, KPQ, PQ),
                ("gluon", "photon_mu", "gluon", "photon_nu"),
                multiplicity=2,
            ),
        ),
    ),
    DISGraphTopology(
        name="q_box_topology",
        channel="q",
        graph_phase=E("-1"),
        rootings=(
            _root(
                "q_box",
                (1, 2, 1, 0, 1, 0),
                (P, KP, KPQ, KP),
                ("gluon", "photon_mu", "photon_nu", "gluon"),
            ),
        ),
    ),
    DISGraphTopology(
        name="q_self_energy_topology",
        channel="q",
        graph_phase=E("-1"),
        rootings=(
            _root(
                "q_bubble",
                (1, 0, 1, 0, 1, 2),
                (P, PQ, KPQ, PQ),
                ("photon_mu", "gluon", "gluon", "photon_nu"),
            ),
            _root(
                "q_lsz",
                (1, 1, 0, 0, 2, 1),
                (P, PQ, P, KP),
                ("photon_mu", "photon_nu", "gluon", "gluon"),
            ),
        ),
    ),
    DISGraphTopology(
        name="g_box_topology",
        channel="g",
        graph_phase=E("1"),
        rootings=(
            _root(
                "g_box",
                (1, 2, 1, 0, 1, 0),
                (K, KP, KPQ, KP),
                ("gluon", "photon_mu", "photon_nu", "gluon"),
            ),
        ),
    ),
    DISGraphTopology(
        name="g_crossed_box_topology",
        channel="g",
        graph_phase=E("1"),
        rootings=(
            _root(
                "g_crossed_box",
                (1, 1, 1, 1, 1, 0),
                (K, KP, KPQ, KQ),
                ("gluon", "photon_mu", "gluon", "photon_nu"),
            ),
        ),
    ),
)


def _compile_trace(rooting: DISRootedTopology) -> GammaTraceSpec:
    vertex_labels = {
        "gluon": "sigma",
        "photon_mu": "mu",
        "photon_nu": "nu",
    }
    vectors: list[MomentumCombination | None] = []
    labels: list[str] = []
    photon_slots: list[int] = []
    for index, (momentum, vertex) in enumerate(
        zip(rooting.fermion_momenta, rooting.vertices, strict=True),
        start=1,
    ):
        vectors.extend((momentum, None))
        labels.extend((f"rho{index}", vertex_labels[vertex]))
        if vertex.startswith("photon_"):
            photon_slots.append(2 * index - 1)
    return GammaTraceSpec(
        vectors=tuple(vectors),
        lorentz_labels=tuple(labels),
        photon_slots=(photon_slots[0], photon_slots[1]),
    )


def compile_dis_graph_specs(
    topologies: Sequence[DISGraphTopology] = DIS_GRAPH_TOPOLOGIES,
) -> Mapping[str, DISGraphSpec]:
    """Compile rooted traces and weights from the five topology inputs."""

    graphs: dict[str, DISGraphSpec] = {}
    for topology in topologies:
        for rooting in topology.rootings:
            if rooting.name in graphs:
                raise ValueError(f"Duplicate rooted DIS graph {rooting.name}")
            graphs[rooting.name] = DISGraphSpec(
                name=rooting.name,
                channel=topology.channel,
                powers=rooting.powers,
                trace=_compile_trace(rooting),
                relative_weight=topology.graph_phase * rooting.multiplicity,
                channel_prefactor=topology.channel_prefactor,
                parent_topology=topology.name,
                source=topology.source,
            )
    return MappingProxyType(graphs)


DIS_GRAPH_SPECS: Mapping[str, DISGraphSpec] = compile_dis_graph_specs()


@dataclass(frozen=True, slots=True)
class ProjectedNumerators:
    """One Spenso-derived trace in the paper's scalar projector basis.

    The returned expressions have already been translated from native Spenso
    dots to the stable scalar coordinates ``kk``, ``kp``, and ``kq``.  The
    transverse-vector contraction obeys the leading-power DIS decomposition
    ``L = F2/(2*x) - F1 = FL/(2*x)``.  Both ``F2_over_2x`` and the physical
    ``F2`` are retained so that the factor ``2*x`` is explicit.
    """

    metric: Expression
    transverse_vector_square: Expression
    longitudinal: Expression
    F1: Expression
    F2_over_2x: Expression
    F2: Expression
    FL: Expression
    ward: Expression


def derive_projected_numerators(
    graph: DISGraphSpec | str,
    *,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> ProjectedNumerators:
    """Derive the metric, longitudinal, ``F1``, ``F2``, and ``FL`` traces.

    The historical source defines
    ``P^mu = p^mu - (p.q/q^2) q^mu``.  Linearity of the two photon slashes is
    used explicitly: four native Spenso traces build ``P_mu P_nu N^munu``.
    This avoids hiding the projector in an opaque composite-vector atom.  The
    generic closed-trace implementation remains owned by ``notebooks.ludy``.
    """

    from symbolica.community.spenso import Representation, TensorName, dot

    graph_spec = DIS_GRAPH_SPECS[graph] if isinstance(graph, str) else graph
    minkowski = Representation.mink(dimension=kinematics.dimension)
    momentum = TensorName.vector("dis_p")
    loop_momentum = TensorName.vector(
        "dis_k",
        tags=["ludy::loop_momentum"],
    )
    p_vector = momentum(1, minkowski)
    q_vector = momentum(2, minkowski)
    k_vector = loop_momentum(1, minkowski)
    source_vectors = list(
        graph_spec.trace.instantiated_vectors(k_vector, p_vector, q_vector)
    )
    source_labels = list(graph_spec.trace.lorentz_labels)
    left_slot, right_slot = graph_spec.trace.photon_slots

    metric_labels = list(source_labels)
    metric_labels[left_slot] = "dis_photon_metric"
    metric_labels[right_slot] = "dis_photon_metric"
    metric = gamma_trace_to_dots(
        source_vectors,
        metric_labels,
        lorentz_dimension=kinematics.dimension,
    )

    def contracted(left_vector, right_vector, label: str) -> Expression:
        vectors = list(source_vectors)
        labels = list(source_labels)
        vectors[left_slot] = left_vector
        vectors[right_slot] = right_vector
        labels[left_slot] = f"dis_{label}_left"
        labels[right_slot] = f"dis_{label}_right"
        return gamma_trace_to_dots(
            vectors,
            labels,
            lorentz_dimension=kinematics.dimension,
        )

    pp_trace = contracted(p_vector, p_vector, "pp")
    pq_trace = contracted(p_vector, q_vector, "pq")
    qp_trace = contracted(q_vector, p_vector, "qp")
    qq_trace = contracted(q_vector, q_vector, "qq")

    dot_rules = (
        (cast(Expression, dot(k_vector, k_vector)), kinematics.loop_square),
        (cast(Expression, dot(k_vector, p_vector)), kinematics.loop_dot_p),
        (cast(Expression, dot(p_vector, k_vector)), kinematics.loop_dot_p),
        (cast(Expression, dot(k_vector, q_vector)), kinematics.loop_dot_q),
        (cast(Expression, dot(q_vector, k_vector)), kinematics.loop_dot_q),
        (cast(Expression, dot(p_vector, p_vector)), kinematics.incoming_virtuality),
        (cast(Expression, dot(q_vector, q_vector)), -kinematics.photon_scale),
        (cast(Expression, dot(p_vector, q_vector)), kinematics.p_dot_q),
        (cast(Expression, dot(q_vector, p_vector)), kinematics.p_dot_q),
    )

    def scalarize(expression: Expression) -> Expression:
        result = expression
        for source, target in dot_rules:
            result = result.replace(source, target)
        return canonical(result)

    metric_scalar = scalarize(metric)
    pp_scalar = scalarize(pp_trace)
    pq_scalar = scalarize(pq_trace)
    qp_scalar = scalarize(qp_trace)
    qq_scalar = scalarize(qq_trace)
    q_square = -kinematics.photon_scale
    projector_coefficient = kinematics.p_dot_q / q_square
    transverse_square = canonical(
        kinematics.incoming_virtuality
        - kinematics.p_dot_q**2 / q_square
    )
    projected_pp = canonical(
        pp_scalar
        - projector_coefficient * (pq_scalar + qp_scalar)
        + projector_coefficient**2 * qq_scalar
    )
    longitudinal = canonical(projected_pp / transverse_square)
    f1 = canonical(
        (metric_scalar - longitudinal) / (2 - kinematics.dimension)
    )
    f2_over_2x = canonical(
        (
            metric_scalar
            + (1 - kinematics.dimension) * longitudinal
        )
        / (2 - kinematics.dimension)
    )
    f2 = canonical(2 * kinematics.bjorken_x * f2_over_2x)
    fl = canonical(2 * kinematics.bjorken_x * longitudinal)
    return ProjectedNumerators(
        metric=metric_scalar,
        transverse_vector_square=transverse_square,
        longitudinal=longitudinal,
        F1=f1,
        F2_over_2x=f2_over_2x,
        F2=f2,
        FL=fl,
        ward=qq_scalar,
    )


def derive_all_projected_numerators(
    graphs: Mapping[str, DISGraphSpec] = DIS_GRAPH_SPECS,
    *,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> Mapping[str, ProjectedNumerators]:
    """Derive all six physical numerator records deterministically."""

    return MappingProxyType(
        {
            name: derive_projected_numerators(graph, kinematics=kinematics)
            for name, graph in graphs.items()
        }
    )


@dataclass(frozen=True, slots=True)
class NumeratorReductionAudit:
    """One exact projected-numerator reconstruction in a three-line family."""

    graph_name: str
    observable: Literal["F2", "FL"]
    retained_loop_lines: tuple[int, ...]
    apart_coefficient: Expression
    reduction: Any

    @property
    def term_count(self) -> int:
        return len(self.reduction.terms)

    @property
    def residual(self) -> Expression:
        return self.reduction.reconstruction_residual


@dataclass(frozen=True, slots=True)
class DISKiraNumeratorHandoff:
    """One projected numerator written in a cut-specialized Kira family.

    Terms that cancel a protected cut propagator are zero in reverse
    unitarity and are retained separately rather than being sent to Kira.
    ``requires_external_derivative`` flags raised external cuts: their
    derivative distribution must act before the corresponding invariant is
    specialized to zero.
    """

    project_key: str
    graph_name: str
    observable: Literal["F2", "FL"]
    retained_loop_lines: tuple[int, ...]
    kept_indices: tuple[tuple[int, ...], ...]
    cut_cancelled_indices: tuple[tuple[int, ...], ...]
    family_expression: Expression
    required_targets: tuple[Expression, ...]
    requires_external_derivative: bool


@dataclass(frozen=True, slots=True)
class DISMasterCoefficientAudit:
    """Exact Kira coefficient of the declared scalar master for one handoff."""

    handoff: DISKiraNumeratorHandoff
    expected_master: Expression
    reduced_expression: Expression
    coefficient: Expression
    residual: Expression

    @property
    def uses_cut_specialized_project(self) -> bool:
        """Whether the coefficient needs no finite-virtuality replacement.

        This says nothing about physical raised-cut signs, support, or graph
        weights; those are later assembly boundaries.
        """

        return not self.handoff.requires_external_derivative


@dataclass(frozen=True, slots=True)
class DISPhysicalReductionAudit:
    """Complete graph-level bridge from projected numerators to Kira masters."""

    coefficients: tuple[DISMasterCoefficientAudit, ...]
    unique_required_targets: int
    missing_targets: tuple[tuple[str, Expression], ...]

    @property
    def exact(self) -> bool:
        return (
            len(self.coefficients) == 32
            and self.unique_required_targets == 48
            and not self.missing_targets
            and all(record.residual == E("0") for record in self.coefficients)
        )

    @property
    def cut_specialized_coefficients(
        self,
    ) -> tuple[DISMasterCoefficientAudit, ...]:
        return tuple(
            record
            for record in self.coefficients
            if record.uses_cut_specialized_project
        )

    @property
    def raised_external_coefficients(
        self,
    ) -> tuple[DISMasterCoefficientAudit, ...]:
        return tuple(
            record
            for record in self.coefficients
            if not record.uses_cut_specialized_project
        )


def crossed_box_apart(
    *,
    kinematics: DISKinematics = DIS_KINEMATICS,
):
    """Return Symbolica's exact four-child crossed-box decomposition."""

    return apart_kernel(
        kinematics.scalar_denominators[:4],
        loop_scalar_products=(
            kinematics.loop_square,
            kinematics.loop_dot_p,
            kinematics.loop_dot_q,
        ),
    )


def audit_projected_numerator_reductions(
    projected: Mapping[str, ProjectedNumerators] | None = None,
    *,
    graphs: Mapping[str, DISGraphSpec] = DIS_GRAPH_SPECS,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> tuple[NumeratorReductionAudit, ...]:
    """Reconstruct both physical numerators for every graph exactly.

    The calculation is kept at finite incoming virtuality.  Five graphs use
    ``D1,D2,D3`` directly.  The crossed box is first decomposed by Symbolica's
    native multivariate ``apart`` and each of its four three-line children is
    reduced with the graph's actual base powers.
    """

    numerators = projected or derive_all_projected_numerators(
        graphs,
        kinematics=kinematics,
    )
    denominators = kinematics.scalar_denominators
    loop_scalar_products = (
        kinematics.loop_square,
        kinematics.loop_dot_p,
        kinematics.loop_dot_q,
    )
    _apart_expression, apart_terms = crossed_box_apart(kinematics=kinematics)
    audits: list[NumeratorReductionAudit] = []
    for graph_name, graph in graphs.items():
        for observable in ("F2", "FL"):
            numerator = getattr(numerators[graph_name], observable)
            if graph_name != "g_crossed_box":
                reduction = reduce_numerator(
                    numerator,
                    denominators[:3],
                    loop_scalar_products=loop_scalar_products,
                    base_integral_indices=graph.powers[:3],
                )
                audits.append(
                    NumeratorReductionAudit(
                        graph_name=graph_name,
                        observable=observable,
                        retained_loop_lines=(1, 2, 3),
                        apart_coefficient=E("1"),
                        reduction=reduction,
                    )
                )
                continue
            for term in apart_terms:
                retained_lines = tuple(index + 1 for index in term.retained_indices)
                reduction = reduce_numerator(
                    numerator * term.coefficient,
                    term.denominators,
                    loop_scalar_products=loop_scalar_products,
                    base_integral_indices=tuple(
                        graph.powers[index] for index in term.retained_indices
                    ),
                )
                audits.append(
                    NumeratorReductionAudit(
                        graph_name=graph_name,
                        observable=observable,
                        retained_loop_lines=retained_lines,
                        apart_coefficient=term.coefficient,
                        reduction=reduction,
                    )
                )
    failures = tuple(audit for audit in audits if audit.residual != E("0"))
    if failures:
        raise AssertionError(
            "Projected DIS numerator reconstruction failed for "
            + ", ".join(
                f"{audit.graph_name}:{audit.observable}:{audit.retained_loop_lines}"
                for audit in failures
            )
        )
    return tuple(audits)


@dataclass(frozen=True, slots=True)
class DistributionCoefficient:
    """Canonical ``delta(1-x), D_n(x), regular`` distribution metadata.

    ``plus[n]`` multiplies ``D_n=[log(1-x)^n/(1-x)]_+``.  Plus coefficients
    are endpoint constants.  Multiplication by a smooth function uses the
    distribution identity explicitly and moves the non-endpoint part into
    :attr:`regular`.
    """

    variable: Expression
    delta: Expression = field(default_factory=lambda: E("0"))
    plus: tuple[Expression, ...] = ()
    regular: Expression = field(default_factory=lambda: E("0"))

    def __post_init__(self) -> None:
        object.__setattr__(self, "variable", _expression(self.variable))
        object.__setattr__(self, "delta", _expression(self.delta))
        object.__setattr__(
            self,
            "plus",
            tuple(_expression(coefficient) for coefficient in self.plus),
        )
        object.__setattr__(self, "regular", _expression(self.regular))
        if any(coefficient.contains(self.variable) for coefficient in self.plus):
            raise ValueError("Canonical plus coefficients cannot depend on the endpoint variable")

    @classmethod
    def delta_basis(
        cls,
        variable: Expression,
        coefficient: Expression | int = 1,
    ) -> DistributionCoefficient:
        return cls(variable=variable, delta=_expression(coefficient))

    @classmethod
    def plus_basis(
        cls,
        variable: Expression,
        order: int,
        coefficient: Expression | int = 1,
    ) -> DistributionCoefficient:
        if isinstance(order, bool) or not isinstance(order, int) or order < 0:
            raise ValueError("Plus-distribution order must be a non-negative integer")
        return cls(
            variable=variable,
            plus=(E("0"),) * order + (_expression(coefficient),),
        )

    def _aligned_plus(self, length: int) -> tuple[Expression, ...]:
        return self.plus + (E("0"),) * (length - len(self.plus))

    def __add__(self, other: DistributionCoefficient) -> DistributionCoefficient:
        if not isinstance(other, DistributionCoefficient):
            return NotImplemented
        if self.variable != other.variable:
            raise ValueError("Cannot add endpoint distributions in different variables")
        length = max(len(self.plus), len(other.plus))
        return DistributionCoefficient(
            variable=self.variable,
            delta=canonical(self.delta + other.delta),
            plus=tuple(
                canonical(left + right)
                for left, right in zip(
                    self._aligned_plus(length),
                    other._aligned_plus(length),
                    strict=True,
                )
            ),
            regular=canonical(self.regular + other.regular),
        )

    def __neg__(self) -> DistributionCoefficient:
        return self.scaled(-1)

    def __sub__(self, other: DistributionCoefficient) -> DistributionCoefficient:
        return self + (-other)

    def scaled(self, factor: Expression | int) -> DistributionCoefficient:
        """Multiply by a constant, or delegate a smooth variable factor safely."""

        factor_expression = _expression(factor)
        if factor_expression.contains(self.variable):
            return self.multiply_smooth(factor_expression)
        return DistributionCoefficient(
            variable=self.variable,
            delta=canonical(factor_expression * self.delta),
            plus=tuple(
                canonical(factor_expression * coefficient)
                for coefficient in self.plus
            ),
            regular=canonical(factor_expression * self.regular),
        )

    def multiply_smooth(self, factor: Expression | int) -> DistributionCoefficient:
        r"""Multiply by a function smooth at ``x=1``.

        This applies ``g D_n = g(1) D_n + (g-g(1)) log(1-x)^n/(1-x)``.
        """

        factor_expression = _expression(factor)
        endpoint_factor = factor_expression.replace(self.variable, 1)
        if endpoint_factor.contains(self.variable):
            raise ValueError("Could not evaluate smooth factor at the endpoint")
        remainder_prefactor = canonical(
            (factor_expression - endpoint_factor) / (1 - self.variable)
        )
        regular_correction = sum(
            (
                coefficient
                * remainder_prefactor
                * (1 - self.variable).log() ** order
                for order, coefficient in enumerate(self.plus)
            ),
            E("0"),
        )
        return DistributionCoefficient(
            variable=self.variable,
            delta=canonical(endpoint_factor * self.delta),
            plus=tuple(
                canonical(endpoint_factor * coefficient)
                for coefficient in self.plus
            ),
            regular=canonical(
                factor_expression * self.regular + regular_correction
            ),
        )

    def residuals(self) -> tuple[Expression, ...]:
        return (
            canonical(self.delta),
            *(canonical(coefficient) for coefficient in self.plus),
            canonical(self.regular),
        )

    @property
    def is_zero(self) -> bool:
        return all(residual == E("0") for residual in self.residuals())


@dataclass(frozen=True, slots=True)
class DISStructureFunctions:
    """The four NLO DIS functions displayed in the manuscript."""

    F2q: DistributionCoefficient
    F2g: DistributionCoefficient
    FLq: DistributionCoefficient
    FLg: DistributionCoefficient


@dataclass(frozen=True, slots=True)
class SourceIssue:
    key: str
    severity: Literal["note", "warning", "blocker"]
    description: str
    source: str


@dataclass(frozen=True, slots=True)
class PaperDISTargets:
    """Paper formulas with source labels kept separate from interpretation."""

    functions: DISStructureFunctions
    source_labels: Mapping[str, str]
    issues: tuple[SourceIssue, ...]


def paper_targets() -> PaperDISTargets:
    """Encode the four current paper targets as reference-only expressions.

    The current source labels the two transverse and two longitudinal lines
    directly and writes colour-stripped leading-order kernels because the
    displayed equations put ``C_F`` and ``T_F`` outside.  This function is
    deliberately downstream of the native topology/cut/master assembly.
    """

    normalization = electric_charge**2 * alpha_s / (2 * pi)
    cutoff_log = (Q_squared / lambda_squared).log()
    p_qg = x**2 + (1 - x) ** 2

    f2g = DistributionCoefficient(
        variable=x,
        regular=normalization
        * x
        * color_t
        * (p_qg * (cutoff_log - 2 * x.log()) + 6 * x * (1 - x) - 2),
    )
    f2q_bracket = DistributionCoefficient(
        variable=x,
        delta=-1 - 2 * pi**2 / 3 + E("3/2") * cutoff_log,
        plus=(2 * cutoff_log - E("3/2"),),
        regular=(
            1
            + 3 * x
            - 2 * (1 + x**2) * x.log() / (1 - x)
            - (1 + x) * cutoff_log
        ),
    )
    f2q = f2q_bracket.multiply_smooth(normalization * x * color_f)
    flg = DistributionCoefficient(
        variable=x,
        regular=normalization * x * (4 * color_t * x * (1 - x)),
    )
    flq = DistributionCoefficient(
        variable=x,
        regular=normalization * x * (2 * color_f * x),
    )
    return PaperDISTargets(
        functions=DISStructureFunctions(F2q=f2q, F2g=f2g, FLq=flq, FLg=flg),
        source_labels=MappingProxyType(
            {
                "F2q": f"{MANUSCRIPT_SOURCE}:294-298",
                "F2g": f"{MANUSCRIPT_SOURCE}:305",
                "FLq": f"{MANUSCRIPT_SOURCE}:300-301",
                "FLg": f"{MANUSCRIPT_SOURCE}:306",
            }
        ),
        issues=(
            SourceIssue(
                key="historical-raised-cut-sign",
                severity="warning",
                description=(
                    "The printed raised-cut rule omits the alternating "
                    "(-1)^(a-1) fixed by the source's own discontinuity "
                    "definition.  The native cut ledger derives that sign "
                    "instead of copying the printed rule."
                ),
                source=(
                    f"{HISTORICAL_SOURCE}, "
                    "Submission/Discontinuities.tex:80-94,143-154"
                ),
            ),
            SourceIssue(
                key="historical-discontinuity-variable-sign",
                severity="warning",
                description=(
                    "With the source definition disc f=f(s-i0)-f(s+i0) and "
                    "s=1-x, the displayed discontinuities of h1/(x-1) and "
                    "c2*(x-1)^(-epsilon)/(1-x) lose a minus sign.  Native cut "
                    "phases are derived in the denominator variables instead "
                    "of copying those equations."
                ),
                source=(
                    f"{HISTORICAL_SOURCE}, "
                    "Submission/Discontinuities.tex:80-119"
                ),
            ),
            SourceIssue(
                key="historical-plus-expansion",
                severity="warning",
                description=(
                    "The printed expansion of y^(-1-epsilon) starts at n=1 "
                    "and uses +epsilon^n.  It therefore omits D0 and gives "
                    "the wrong alternating signs; the native endpoint code "
                    "uses -delta/epsilon + D0 - epsilon*D1 + ...."
                ),
                source=(
                    f"{HISTORICAL_SOURCE}, "
                    "Submission/Discontinuities.tex:216-220"
                ),
            ),
            SourceIssue(
                key="historical-longitudinal-definition",
                severity="warning",
                description=(
                    "The historical setup prints FL=F1-2*x*F2, whereas its "
                    "projectors and the native calculation use the physical "
                    "relation FL=F2-2*x*F1."
                ),
                source=(
                    f"{HISTORICAL_SOURCE}, "
                    "Submission/DIS_setup.tex:103-108"
                ),
            ),
            SourceIssue(
                key="historical-splitting-kernel-label",
                severity="warning",
                description=(
                    "The same x^2+(1-x)^2 kernel is labelled P_gq in the NLO "
                    "calculation and P_qg in the setup.  Comparisons use its "
                    "explicit polynomial rather than trusting either label."
                ),
                source=(
                    f"{HISTORICAL_SOURCE}, "
                    "Submission/NLO_calculation.tex:74-85; "
                    "Submission/DIS_setup.tex"
                ),
            ),
            SourceIssue(
                key="historical-quark-class12-sign",
                severity="warning",
                description=(
                    "The finite class-1/2 quark coefficient printed in the "
                    "LaTeX has the opposite overall sign from the native "
                    "topology/master assembly.  Its separately printed "
                    "+P_qq*log(Q^2/Lambda^2) term has the native sign, so the "
                    "line is a hybrid rather than a consistent global phase "
                    "choice.  Flipping graph phases cannot repair it without "
                    "also reversing the correctly reproduced F_L result."
                ),
                source=(
                    f"{HISTORICAL_SOURCE}, "
                    "Submission/NLO_calculation.tex:89-97"
                ),
            ),
            SourceIssue(
                key="historical-gluon-normalization",
                severity="warning",
                description=(
                    "The printed gluon scale term has the full-flavour "
                    "normalization at T_F=1/2, whereas its finite MP, PM, and "
                    "F_L terms are normalized per quark-or-antiquark summand. "
                    "The historical Mathematica comparison explicitly "
                    "multiplies MPDISgluonic by (1-epsilon), converting the "
                    "d-2 polarization average to the two-helicity PDF "
                    "convention and removing the otherwise residual P_qg."
                ),
                source=(
                    f"{HISTORICAL_SOURCE}, "
                    "Submission/NLO_calculation.tex:68-85; "
                    "calculations/dy/mathematica/DY_calculation.nb:41598,41689-41696"
                ),
            ),
            SourceIssue(
                key="mathematica-fermion-pole-not-pqq",
                severity="warning",
                description=(
                    "The historical MPDISfermionic pole bracket is "
                    "9*delta + 6*x*(1-x) + 12*x^2*D0. Exact smooth "
                    "distribution multiplication canonicalizes this to a "
                    "coefficient differing from 6*P_qq by the ordinary term "
                    "-6*(1+x^2). Replacing 6*x*(1-x) by 6*(1+x) would give "
                    "the required collinear pole; the native calculation does "
                    "not make that repair."
                ),
                source=(
                    "calculations/dy/mathematica/DY_calculation.nb:"
                    "42637-42789"
                ),
            ),
            SourceIssue(
                key="mathematica-omitted-external-leg-bubbles",
                severity="warning",
                description=(
                    "The historical DY scheme cell multiplies both half-weighted "
                    "valv5 external-leg bubbles by zero even though the earlier "
                    "virtual assembly contains them. Restoring the pair is "
                    "required for its quark distributional residual to vanish."
                ),
                source=(
                    "calculations/dy/mathematica/DY_calculation.nb:"
                    "15179-15577,41820-41855"
                ),
            ),
            SourceIssue(
                key="mathematica-dy-global-sign-flip",
                severity="warning",
                description=(
                    "The earlier full DY assembly uses realMP-virtualMP, while "
                    "the later scheme-change definition assigns MPDY as "
                    "virtualMP-realMPnosimpl. This is an explicit global sign "
                    "change between two source cells."
                ),
                source=(
                    "calculations/dy/mathematica/DY_calculation.nb:"
                    "39605-39628,42161-42182"
                ),
            ),
            SourceIssue(
                key="mathematica-delta-zero-substitution",
                severity="warning",
                description=(
                    "A final scheme cell replaces z by 1 in an expression that "
                    "still contains delta(1-z), and the recorded output contains "
                    "delta(0). Typed distribution coefficients never perform "
                    "this substitution."
                ),
                source=(
                    "calculations/dy/mathematica/DY_calculation.nb:"
                    "43024-43050"
                ),
            ),
            SourceIssue(
                key="historical-projector-vector",
                severity="note",
                description=(
                    "The active manuscript leaves uppercase P undefined. The cited "
                    "DIS source defines P = p - (p.q/q^2) q, which is adopted here."
                ),
                source=(
                    f"{MANUSCRIPT_SOURCE}:285; {HISTORICAL_SOURCE}, "
                    "Submission/DIS_setup.tex:94-104"
                ),
            ),
            SourceIssue(
                key="historical-transverse-decomposition-sign",
                severity="warning",
                description=(
                    "The displayed tensor decomposition uses "
                    "+W1*(g-qq/q^2), but the projector printed immediately "
                    "after it returns -W1 for that decomposition.  The "
                    "decomposition needs the conventional minus sign; the "
                    "native projector is verified algebraically and does not "
                    "copy this pair of equations."
                ),
                source=(
                    f"{HISTORICAL_SOURCE}, "
                    "Submission/DIS_setup.tex:92-100"
                ),
            ),
            SourceIssue(
                key="color-stripped-kernel-convention",
                severity="warning",
                description=(
                    "The paper refers to regularised P_ij kernels rather than "
                    "writing their distributional forms.  The target expands the "
                    "colour-stripped LO kernels because C_F and T_F are printed "
                    "outside."
                ),
                source=f"{MANUSCRIPT_SOURCE}:287-308",
            ),
            SourceIssue(
                key="f2-reference-only",
                severity="note",
                description=(
                    "The physical projector is fixed here by "
                    "F2 = 2*x*[F2/(2*x)] and FL = F2 - 2*x*F1. The active "
                    "cutoff/LU formula is retained only as a reference target. "
                    "The native finite-virtuality result and its PM subtraction "
                    "are assembled independently from topologies, cuts, and "
                    "masters before this target is inspected."
                ),
                source=(
                    f"{MANUSCRIPT_SOURCE}:285; {HISTORICAL_SOURCE}, "
                    "Submission/DIS_setup.tex:94-113"
                ),
            ),
        ),
    )


PAPER_TARGETS = paper_targets()


NormalizationOwner = Literal[
    "analytic_master",
    "external_measure",
    "graph",
    "channel",
    "convention",
]


@dataclass(frozen=True, slots=True)
class NormalizationEntry:
    name: str
    value: Expression
    owner: NormalizationOwner
    applied_in_physical_handoff: bool
    source: str
    note: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _expression(self.value))


@dataclass(frozen=True, slots=True)
class DISNormalization:
    channel: Channel
    entries: tuple[NormalizationEntry, ...]
    limitations: tuple[str, ...]


def known_normalization_ledger() -> Mapping[Channel, DISNormalization]:
    """Return the normalization ownership used by the topology compiler.

    The graph coupling, colour contraction, and incoming-state average are one
    channel prefactor on :class:`DISGraphSpec`.  Keeping that product in one
    row prevents the physical assembler from applying any of its factors a
    second time.
    """

    common = (
        NormalizationEntry(
            name="loop integration measure",
            value=1 / (2 * pi) ** d,
            owner="analytic_master",
            applied_in_physical_handoff=False,
            source=f"{MANUSCRIPT_SOURCE}:435",
            note="Must already be present in each analytic master.",
        ),
        NormalizationEntry(
            name="per-cut-edge phase-space factor",
            value=2 * pi,
            owner="analytic_master",
            applied_in_physical_handoff=False,
            source=f"{MANUSCRIPT_SOURCE}:201-204",
            note=(
                "Phase-stripped physical convention. The literal paper_* "
                "masters instead use 2*pi*i per edge; PAPER_PHASES records "
                "the conversion."
            ),
        ),
        NormalizationEntry(
            name="incoming virtuality measure",
            value=1 / (2 * pi),
            owner="external_measure",
            applied_in_physical_handoff=True,
            source=f"{MANUSCRIPT_SOURCE}:170,231",
            note="The singular p^2 integration supplies the remaining epsilon factor.",
        ),
        NormalizationEntry(
            name="DIS observable factor",
            value=1 / (4 * pi),
            owner="external_measure",
            applied_in_physical_handoff=True,
            source=f"{MANUSCRIPT_SOURCE}:231-233",
            note="Together with dp^2/(2pi), this gives dp^2/(8pi^2).",
        ),
        NormalizationEntry(
            name="strong-coupling convention",
            value=4 * pi * alpha_s,
            owner="convention",
            applied_in_physical_handoff=True,
            source="g_s^2 = 4 pi alpha_s",
            note="This is a replacement for g_s^2, not an additional factor.",
        ),
    )
    quark = DISNormalization(
        channel="q",
        entries=common
        + (
            NormalizationEntry(
                name="compiled quark channel prefactor",
                value=electric_charge**2 * strong_coupling**2 * color_f / 2,
                owner="channel",
                applied_in_physical_handoff=True,
                source="native topology declaration",
                note=(
                    "One electromagnetic and two strong vertices, the "
                    "quark spin average, and the C_F colour contraction."
                ),
            ),
        ),
        limitations=(
            "The topology phase and rooting multiplicity are separate typed fields.",
            "No additional field-renormalization factor is inserted.",
        ),
    )
    gluon = DISNormalization(
        channel="g",
        entries=common
        + (
            NormalizationEntry(
                name="compiled gluon channel prefactor",
                value=(
                    electric_charge**2
                    * strong_coupling**2
                    * color_t
                    / (d - 2)
                ),
                owner="channel",
                applied_in_physical_handoff=True,
                source="native topology declaration",
                note=(
                    "One electromagnetic and two strong vertices, the d-2 "
                    "polarization average, and the T_F colour contraction."
                ),
            ),
        ),
        limitations=(
            "The topology phase and rooting multiplicity are separate typed fields.",
            "Comparison with a two-helicity PDF kernel retains the pole and "
            "finite terms of (1-epsilon) K through epsilon^0.",
        ),
    )
    return MappingProxyType({"q": quark, "g": gluon})


NORMALIZATION_LEDGER = known_normalization_ledger()


@dataclass(frozen=True, slots=True)
class DISCutSpec:
    """One authoritative double-discontinuity sector.

    Line numbers refer to the global one-based ``D1,...,D6`` ordering.
    Derivative order zero is an ordinary cut delta; positive values denote
    derivatives generated by raised propagators.
    """

    name: str
    graph_name: str
    initial_cut_lines: tuple[int, ...]
    final_cut_lines: tuple[int, ...]
    cut_orders: tuple[tuple[int, int], ...] = ()
    relative_sign: Expression | None = None
    multiplicity: Expression | None = None
    analytic_direct_master: str | None = None
    source: str = ""

    def __post_init__(self) -> None:
        all_lines = self.initial_cut_lines + self.final_cut_lines
        if any(line < 1 or line > 6 for line in all_lines):
            raise ValueError("DIS cut lines must be one-based D1,...,D6 positions")
        if len(set(self.initial_cut_lines)) != len(self.initial_cut_lines):
            raise ValueError("An initial-channel cut line cannot be duplicated")
        if len(set(self.final_cut_lines)) != len(self.final_cut_lines):
            raise ValueError("A final-channel cut line cannot be duplicated")
        # The two iterated cuts are allowed (and for triple cuts required) to
        # share one edge.  This is the connected three-component cutting rule.
        if any(line < 1 or line > 6 or order < 0 for line, order in self.cut_orders):
            raise ValueError("Invalid differentiated-cut metadata")
        if self.relative_sign is not None:
            object.__setattr__(self, "relative_sign", _expression(self.relative_sign))
        if self.multiplicity is not None:
            object.__setattr__(self, "multiplicity", _expression(self.multiplicity))

    @property
    def loop_cut_lines(self) -> tuple[int, ...]:
        return tuple(
            dict.fromkeys(
                line
                for line in self.initial_cut_lines + self.final_cut_lines
                if line <= 4
            )
        )

    @property
    def total_derivative_order(self) -> int:
        return sum(order for _line, order in self.cut_orders)

    @property
    def reverse_unitarity_sign(self) -> Expression:
        r"""Sign from ``Disc[D^-a] = 2*pi*i*(-1)^(a-1)*delta^(a-1)/(a-1)!``."""

        return E("-1") if self.total_derivative_order % 2 else E("1")


# These six channel pairings make the four-term all-cut formula explicit in the
# common D basis.  The external--external branch has the relative Cutkosky
# phase ``-1`` after converting every analytic master to the real,
# phase-stripped convention in ``masters.py``; ordinary internal-cut branches
# have phase ``+1``.  A raised *external* D5/D6 cut supplies that same minus
# through its derivative distribution.  Raised internal Kira lines need no
# second sign here: their coefficient already belongs to the cut-specialized
# family.  Each row is one oriented sector with unit multiplicity.
STRUCTURAL_CUT_SUPPORT_PAIRS = (
    ("p-flow D1/D2", (1, 2)),
    ("p-flow D3/D4", (3, 4)),
    ("(p+q)-flow D1/D3", (1, 3)),
)


STRUCTURAL_CUT_CHANNELS: Mapping[
    str,
    tuple[tuple[int, ...], tuple[int, ...]],
] = MappingProxyType(
    {
        "external_external": ((5,), (6,)),
        "internal12_external_final": ((1, 2), (6,)),
        "internal34_external_final": ((3, 4), (6,)),
        "external_initial_internal13": ((5,), (1, 3)),
        "triple123": ((1, 2), (1, 3)),
        "triple134": ((3, 4), (1, 3)),
    }
)


def build_structural_cut_ledger(
    graphs: Mapping[str, DISGraphSpec] = DIS_GRAPH_SPECS,
) -> tuple[DISCutSpec, ...]:
    """Derive the explicit compact physical sectors from the graph powers."""

    cuts: list[DISCutSpec] = []
    source = (
        f"{HISTORICAL_ALL_CUT_SOURCE}; "
        f"{DIS_INTEGRAND_SOURCE}"
    )
    for graph in graphs.values():
        support = {
            line
            for line, power in enumerate(graph.powers, start=1)
            if power > 0
        }
        for name, (initial_lines, final_lines) in STRUCTURAL_CUT_CHANNELS.items():
            required = set(initial_lines) | set(final_lines)
            if not required <= support:
                continue
            cuts.append(
                DISCutSpec(
                    name=name,
                    graph_name=graph.name,
                    initial_cut_lines=initial_lines,
                    final_cut_lines=final_lines,
                    cut_orders=tuple(
                        (line, graph.powers[line - 1] - 1)
                        for line in sorted(required)
                    ),
                    relative_sign=(
                        E("-1") if name == "external_external" else E("1")
                    ),
                    multiplicity=E("1"),
                    source=source,
                )
            )
    return tuple(cuts)


KNOWN_DIS_CUTS: tuple[DISCutSpec, ...] = build_structural_cut_ledger()


def _structural_cut_signatures(
    cuts: Sequence[DISCutSpec],
) -> tuple[
    tuple[
        str,
        str,
        tuple[int, ...],
        tuple[int, ...],
        tuple[tuple[int, int], ...],
    ],
    ...,
]:
    return tuple(
        (
            cut.graph_name,
            cut.name,
            cut.initial_cut_lines,
            cut.final_cut_lines,
            cut.cut_orders,
        )
        for cut in cuts
    )


EXPECTED_STRUCTURAL_CUT_SIGNATURES = (
    ("q_triangle", "external_external", (5,), (6,), ((5, 0), (6, 0))),
    (
        "q_triangle",
        "internal12_external_final",
        (1, 2),
        (6,),
        ((1, 0), (2, 0), (6, 0)),
    ),
    (
        "q_triangle",
        "external_initial_internal13",
        (5,),
        (1, 3),
        ((1, 0), (3, 0), (5, 0)),
    ),
    (
        "q_triangle",
        "triple123",
        (1, 2),
        (1, 3),
        ((1, 0), (2, 0), (3, 0)),
    ),
    (
        "q_box",
        "external_initial_internal13",
        (5,),
        (1, 3),
        ((1, 0), (3, 0), (5, 0)),
    ),
    (
        "q_box",
        "triple123",
        (1, 2),
        (1, 3),
        ((1, 0), (2, 1), (3, 0)),
    ),
    ("q_bubble", "external_external", (5,), (6,), ((5, 0), (6, 1))),
    (
        "q_bubble",
        "external_initial_internal13",
        (5,),
        (1, 3),
        ((1, 0), (3, 0), (5, 0)),
    ),
    ("q_lsz", "external_external", (5,), (6,), ((5, 1), (6, 0))),
    (
        "q_lsz",
        "internal12_external_final",
        (1, 2),
        (6,),
        ((1, 0), (2, 0), (6, 0)),
    ),
    (
        "g_box",
        "external_initial_internal13",
        (5,),
        (1, 3),
        ((1, 0), (3, 0), (5, 0)),
    ),
    (
        "g_box",
        "triple123",
        (1, 2),
        (1, 3),
        ((1, 0), (2, 1), (3, 0)),
    ),
    (
        "g_crossed_box",
        "external_initial_internal13",
        (5,),
        (1, 3),
        ((1, 0), (3, 0), (5, 0)),
    ),
    (
        "g_crossed_box",
        "triple123",
        (1, 2),
        (1, 3),
        ((1, 0), (2, 0), (3, 0)),
    ),
    (
        "g_crossed_box",
        "triple134",
        (3, 4),
        (1, 3),
        ((1, 0), (3, 0), (4, 0)),
    ),
)


@dataclass(frozen=True, slots=True)
class DISKiraProjectInput:
    """One deterministic Kira input plus its global graph provenance."""

    key: str
    graph_name: str
    retained_loop_lines: tuple[int, ...]
    cut: DISCutSpec | None
    project: KiraProject
    expected_master_indices: tuple[int, ...] | None
    expected_master_name: str | None
    targets_explicit: bool
    limitation: str | None


def _identifier(value: str) -> str:
    converted = "".join(
        character if character.isalnum() or character == "_" else "_"
        for character in value
    )
    if not converted or not (converted[0].isalpha() or converted[0] == "_"):
        converted = f"dis_{converted}"
    return converted


def _retained_bases(graph: DISGraphSpec) -> tuple[tuple[int, ...], ...]:
    if graph.name == "g_crossed_box":
        return tuple(combinations((1, 2, 3, 4), 3))
    return ((1, 2, 3),)


def _expected_scalar_master(
    retained_lines: tuple[int, ...],
    cut: DISCutSpec | None,
) -> tuple[tuple[int, ...] | None, str | None]:
    """Return the one-loop master expected from the cut geometry."""

    if cut is None:
        return None, None
    if cut.name == "external_external":
        if retained_lines == (1, 2, 3):
            return (0, 1, 1), "B(q^2)"
        return None, None
    indices = tuple(
        int(line in set(cut.loop_cut_lines))
        for line in retained_lines
    )
    if len(cut.loop_cut_lines) == 2:
        if cut.name in {
            "internal12_external_final",
            "internal34_external_final",
        }:
            return indices, "Bcut(p^2)"
        return indices, "Bcut((p+q)^2)"
    if len(cut.loop_cut_lines) == 3:
        return indices, "Tcut(p^2,q^2,(p+q)^2)"
    return None, None


def build_kira_projects(
    *,
    cut_specs: Sequence[DISCutSpec] = KNOWN_DIS_CUTS,
    graphs: Mapping[str, DISGraphSpec] = DIS_GRAPH_SPECS,
    target_indices_by_key: Mapping[str, Sequence[tuple[int, ...]]] | None = None,
    preferred_master_indices_by_key: Mapping[
        str, Sequence[tuple[int, ...]]
    ]
    | None = None,
    bounds: ReductionBounds | None = None,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> Mapping[str, DISKiraProjectInput]:
    """Build serializable three-line Kira projects without running Kira.

    With an explicitly empty cut list this returns nine *prototype* projects: one for each of
    the five three-line graphs and four omitted-line children for the crossed
    box.  Prototype targets contain only the graph's base indices and are not a
    complete physical numerator reduction.  Once authoritative cuts and
    numerator-derived target indices are supplied, the same builder attaches
    local ``cut_propagators`` and marks those explicit target sets complete.

    A crossed-box cut requiring all four loop lines produces no three-line
    project and must provide ``analytic_direct_master`` in its cut record.
    """

    target_indices_by_key = target_indices_by_key or {}
    preferred_master_indices_by_key = preferred_master_indices_by_key or {}
    project_bounds = bounds or ReductionBounds(sectors=(7,), r=9, s=6, d=3)
    all_line_momenta = {
        1: kinematics.loop_momentum,
        2: kinematics.loop_momentum + kinematics.incoming_momentum,
        3: (
            kinematics.loop_momentum
            + kinematics.incoming_momentum
            + kinematics.photon_momentum
        ),
        4: kinematics.loop_momentum + kinematics.photon_momentum,
    }
    projects: dict[str, DISKiraProjectInput] = {}
    cuts_by_graph: dict[str, list[DISCutSpec]] = {}
    for cut in cut_specs:
        if cut.graph_name not in graphs:
            raise ValueError(f"Unknown DIS graph {cut.graph_name!r}")
        cuts_by_graph.setdefault(cut.graph_name, []).append(cut)

    for graph in graphs.values():
        graph_cuts: Sequence[DISCutSpec | None]
        if cut_specs:
            graph_cuts = tuple(cuts_by_graph.get(graph.name, ()))
        else:
            graph_cuts = (None,)
        for cut in graph_cuts:
            for retained_lines in _retained_bases(graph):
                required_loop_lines = set(() if cut is None else cut.loop_cut_lines)
                if not required_loop_lines <= set(retained_lines):
                    continue
                cut_name = "prototype" if cut is None else cut.name
                basis_name = "d" + "".join(str(line) for line in retained_lines)
                key = f"{graph.name}__{cut_name}__{basis_name}"
                family_name = _identifier(f"dis_{key}")
                local_cut_propagators = tuple(
                    local_position
                    for local_position, global_line in enumerate(
                        retained_lines,
                        start=1,
                    )
                    if global_line in required_loop_lines
                )
                family = IntegralFamily(
                    name=family_name,
                    loop_momenta=(kinematics.loop_momentum,),
                    propagators=tuple(
                        Propagator(all_line_momenta[line])
                        for line in retained_lines
                    ),
                    top_level_sectors=(7,),
                    cut_propagators=local_cut_propagators,
                )
                base_indices = tuple(graph.powers[line - 1] for line in retained_lines)
                explicit_targets = key in target_indices_by_key
                index_targets = tuple(
                    tuple(int(index) for index in indices)
                    for indices in target_indices_by_key.get(key, (base_indices,))
                )
                if not index_targets or any(
                    len(indices) != len(retained_lines) for indices in index_targets
                ):
                    raise ValueError(f"Invalid target indices for {key}")
                preferred_indices = tuple(
                    tuple(int(index) for index in indices)
                    for indices in preferred_master_indices_by_key.get(key, ())
                )
                if any(
                    len(indices) != len(retained_lines)
                    for indices in preferred_indices
                ):
                    raise ValueError(f"Invalid preferred-master indices for {key}")
                cut_lines = (
                    ()
                    if cut is None
                    else tuple(
                        dict.fromkeys(
                            cut.initial_cut_lines + cut.final_cut_lines
                        )
                    )
                )
                project = KiraProject(
                    family=family,
                    kinematics=kinematics.kira_kinematics(cut_lines=cut_lines),
                    targets=tuple(family(*indices) for indices in index_targets),
                    bounds=project_bounds,
                    dimension=kinematics.dimension,
                    preferred_masters=tuple(
                        family(*indices) for indices in preferred_indices
                    ),
                    check_masters=bool(preferred_indices),
                    reconstruct_mass=True,
                )
                limitation: str | None
                if cut is None:
                    limitation = (
                        "Uncut serialization prototype; it is not a physical "
                        "double-discontinuity project."
                    )
                elif not explicit_targets:
                    limitation = (
                        "Only the base graph index is requested; projected "
                        "numerator target coverage has not been supplied."
                    )
                else:
                    limitation = None
                expected_master_indices, expected_master_name = (
                    _expected_scalar_master(retained_lines, cut)
                )
                projects[key] = DISKiraProjectInput(
                    key=key,
                    graph_name=graph.name,
                    retained_loop_lines=retained_lines,
                    cut=cut,
                    project=project,
                    expected_master_indices=expected_master_indices,
                    expected_master_name=expected_master_name,
                    targets_explicit=bool(cut is not None and explicit_targets),
                    limitation=limitation,
                )
    return MappingProxyType(projects)


def build_kira_smoke_projects(
    *,
    cut_specs: Sequence[DISCutSpec] = KNOWN_DIS_CUTS,
    graphs: Mapping[str, DISGraphSpec] = DIS_GRAPH_SPECS,
    bounds: ReductionBounds | None = None,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> Mapping[str, DISKiraProjectInput]:
    """Build the complete 16-project scalar-master smoke set.

    Each cut-compatible three-line family receives the cut-preserving
    ``{1, 0, -1}^3`` target cube plus its source graph's raised base target.
    The expected scalar master is supplied as a checked preferred master.  The
    cube deliberately tests serialization, cut kinematics, and the scalar
    master basis. :func:`build_kira_numerator_handoffs` separately translates
    every projected numerator and asserts that its physical targets are a
    subset of this overcomplete cube.
    """

    prototypes = build_kira_projects(
        cut_specs=cut_specs,
        graphs=graphs,
        bounds=bounds,
        kinematics=kinematics,
    )
    target_indices_by_key: dict[str, tuple[tuple[int, ...], ...]] = {}
    preferred_master_indices_by_key: dict[
        str, tuple[tuple[int, ...], ...]
    ] = {}
    for key, project_input in prototypes.items():
        cut_positions = set(project_input.project.family.cut_propagators)
        cube = tuple(
            indices
            for indices in product((1, 0, -1), repeat=3)
            if all(indices[position - 1] > 0 for position in cut_positions)
        )
        graph = graphs[project_input.graph_name]
        base_indices = tuple(
            graph.powers[line - 1]
            for line in project_input.retained_loop_lines
        )
        target_indices_by_key[key] = tuple(
            dict.fromkeys((*cube, base_indices))
        )
        if project_input.expected_master_indices is not None:
            preferred_master_indices_by_key[key] = (
                project_input.expected_master_indices,
            )

    return build_kira_projects(
        cut_specs=cut_specs,
        graphs=graphs,
        target_indices_by_key=target_indices_by_key,
        preferred_master_indices_by_key=preferred_master_indices_by_key,
        bounds=bounds,
        kinematics=kinematics,
    )


def build_kira_numerator_handoffs(
    *,
    projects: Mapping[str, DISKiraProjectInput] | None = None,
    numerator_audits: Sequence[NumeratorReductionAudit] | None = None,
    graphs: Mapping[str, DISGraphSpec] = DIS_GRAPH_SPECS,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> tuple[DISKiraNumeratorHandoff, ...]:
    """Translate all projected numerators into the cached Kira families.

    The scalar-master smoke cube was intentionally chosen broad enough to
    contain these targets.  This function proves that fact explicitly and
    constructs the 16 projects times two observables graph-level expressions.
    It does not run or load Kira.
    """

    project_inputs = projects or build_kira_smoke_projects(
        graphs=graphs,
        kinematics=kinematics,
    )
    audits = tuple(
        numerator_audits
        or audit_projected_numerator_reductions(
            graphs=graphs,
            kinematics=kinematics,
        )
    )
    audit_by_key = {
        (audit.graph_name, audit.observable, audit.retained_loop_lines): audit
        for audit in audits
    }
    if len(audit_by_key) != len(audits):
        raise AssertionError("Projected-numerator handoff keys are not unique")

    handoffs: list[DISKiraNumeratorHandoff] = []
    for project_key, project_input in sorted(project_inputs.items()):
        cut = project_input.cut
        if cut is None:
            raise ValueError("Physical numerator handoffs require cut projects")
        family = project_input.project.family
        local_cut_positions = set(family.cut_propagators)
        available_targets = set(project_input.project.targets)
        requires_external_derivative = any(
            line > 4 and order > 0 for line, order in cut.cut_orders
        )
        for observable in ("F2", "FL"):
            try:
                numerator_audit = audit_by_key[
                    (
                        project_input.graph_name,
                        observable,
                        project_input.retained_loop_lines,
                    )
                ]
            except KeyError as error:
                raise AssertionError(
                    "Missing projected-numerator audit for "
                    f"{project_key}:{observable}"
                ) from error
            kept_terms = tuple(
                term
                for term in numerator_audit.reduction.terms
                if all(
                    term.integral_indices[position - 1] > 0
                    for position in local_cut_positions
                )
            )
            cancelled_terms = tuple(
                term
                for term in numerator_audit.reduction.terms
                if term not in kept_terms
            )
            family_expression = sum(
                (
                    term.as_family_integral(family.name)
                    for term in kept_terms
                ),
                E("0"),
            )
            required_targets = tuple(
                sorted(
                    {
                        family(*term.integral_indices)
                        for term in kept_terms
                    },
                    key=lambda target: target.format_plain(),
                )
            )
            missing = tuple(
                target for target in required_targets if target not in available_targets
            )
            if missing:
                raise AssertionError(
                    f"Smoke project {project_key} misses numerator targets {missing}"
                )
            handoffs.append(
                DISKiraNumeratorHandoff(
                    project_key=project_key,
                    graph_name=project_input.graph_name,
                    observable=observable,
                    retained_loop_lines=project_input.retained_loop_lines,
                    kept_indices=tuple(
                        sorted(
                            {term.integral_indices for term in kept_terms}
                        )
                    ),
                    cut_cancelled_indices=tuple(
                        sorted(
                            {term.integral_indices for term in cancelled_terms}
                        )
                    ),
                    family_expression=family_expression,
                    required_targets=required_targets,
                    requires_external_derivative=requires_external_derivative,
                )
            )
    if len(handoffs) != 32:
        raise AssertionError(
            f"Expected 32 DIS numerator/Kira handoffs, got {len(handoffs)}"
        )
    unique_targets = {
        (handoff.project_key, target)
        for handoff in handoffs
        for target in handoff.required_targets
    }
    if len(unique_targets) != 48:
        raise AssertionError(
            f"Expected 48 unique physical Kira targets, got {len(unique_targets)}"
        )
    return tuple(handoffs)


def audit_kira_master_coefficients(
    reductions: Mapping[str, ReductionResult],
    *,
    projects: Mapping[str, DISKiraProjectInput] | None = None,
    numerator_handoffs: Sequence[DISKiraNumeratorHandoff] | None = None,
) -> DISPhysicalReductionAudit:
    """Apply cached Kira rules to all 32 graph/observable handoffs exactly."""

    project_inputs = projects or build_kira_smoke_projects()
    handoffs = tuple(
        numerator_handoffs
        or build_kira_numerator_handoffs(projects=project_inputs)
    )
    records: list[DISMasterCoefficientAudit] = []
    missing_targets: list[tuple[str, Expression]] = []
    for handoff in handoffs:
        try:
            project_input = project_inputs[handoff.project_key]
            result = reductions[handoff.project_key]
        except KeyError as error:
            raise ValueError(
                f"Missing cached DIS Kira reduction {handoff.project_key}"
            ) from error
        result.require_complete()
        if project_input.expected_master_indices is None:
            raise ValueError(
                f"No analytic master declared for {handoff.project_key}"
            )
        expected_master = project_input.project.family(
            *project_input.expected_master_indices
        )
        if set(result.masters) != {expected_master}:
            raise ValueError(
                f"{handoff.project_key} expected only {expected_master}, "
                f"got {result.masters}"
            )
        for target in handoff.required_targets:
            if target not in result.rules:
                missing_targets.append((handoff.project_key, target))
        reduced = result.apply(handoff.family_expression)
        coefficient = canonical(reduced.replace(expected_master, E("1")))
        residual = canonical(reduced - coefficient * expected_master)
        records.append(
            DISMasterCoefficientAudit(
                handoff=handoff,
                expected_master=expected_master,
                reduced_expression=reduced,
                coefficient=coefficient,
                residual=residual,
            )
        )
    unique_targets = {
        (handoff.project_key, target)
        for handoff in handoffs
        for target in handoff.required_targets
    }
    return DISPhysicalReductionAudit(
        coefficients=tuple(records),
        unique_required_targets=len(unique_targets),
        missing_targets=tuple(missing_targets),
    )


ValidationStatus = Literal["pass", "fail", "not-run", "blocked"]
ValidationStage = Literal[
    "source",
    "kinematics",
    "trace",
    "projector",
    "apart",
    "numerator",
    "cut_coverage",
    "kira_serialization",
    "kira_reduction",
    "master",
    "virtuality",
    "poles",
    "channel_sum",
    "paper",
    "scheme",
]


@dataclass(frozen=True, slots=True)
class ValidationCheck:
    key: str
    stage: ValidationStage
    status: ValidationStatus
    expected: object | None = None
    actual: object | None = None
    residual: Expression | DistributionCoefficient | None = None
    reason: str | None = None
    required_for_physical_result: bool = True


@dataclass(frozen=True, slots=True)
class DISValidationLedger:
    checks: tuple[ValidationCheck, ...]

    @property
    def physical_result_validated(self) -> bool:
        required = tuple(
            check for check in self.checks if check.required_for_physical_result
        )
        return bool(required) and all(check.status == "pass" for check in required)

    @property
    def blockers(self) -> tuple[ValidationCheck, ...]:
        return tuple(
            check
            for check in self.checks
            if check.required_for_physical_result
            and check.status != "pass"
        )


def build_validation_ledger(
    projects: Mapping[str, DISKiraProjectInput] | None = None,
    *,
    graphs: Mapping[str, DISGraphSpec] = DIS_GRAPH_SPECS,
    kinematics: DISKinematics = DIS_KINEMATICS,
    cut_specs: Sequence[DISCutSpec] = KNOWN_DIS_CUTS,
    projected_numerators: Mapping[str, ProjectedNumerators] | None = None,
    numerator_audits: Sequence[NumeratorReductionAudit] | None = None,
    apart_child_count: int | None = None,
    kira_reductions: Mapping[str, ReductionResult] | None = None,
    physical_reduction_audit: DISPhysicalReductionAudit | None = None,
    raised_external_audits: Sequence[RaisedExternalReductionAudit] | None = None,
    master_insertion_audit: DISMasterInsertionAudit | None = None,
    native_mp_result: object | None = None,
    native_scheme_exact: bool | None = None,
) -> DISValidationLedger:
    """Report the native derivation and keep source comparisons non-normative."""

    project_inputs = projects or build_kira_projects(
        graphs=graphs,
        kinematics=kinematics,
    )
    serialization_failures: list[str] = []
    for key, project_input in project_inputs.items():
        try:
            project_input.project.serialize()
        except Exception as error:  # pragma: no cover - retained in the audit
            serialization_failures.append(f"{key}: {error}")
    serialization_ok = not serialization_failures
    kira_missing = tuple(
        sorted(set(project_inputs) - set(kira_reductions or {}))
    )
    kira_extra = tuple(
        sorted(set(kira_reductions or {}) - set(project_inputs))
    )
    kira_incomplete = tuple(
        sorted(
            key
            for key, result in (kira_reductions or {}).items()
            if not result.complete
        )
    )
    kira_master_mismatches: list[str] = []
    for key, result in (kira_reductions or {}).items():
        project_input = project_inputs.get(key)
        if project_input is None or project_input.expected_master_indices is None:
            continue
        expected_master = project_input.project.family(
            *project_input.expected_master_indices
        )
        if set(result.masters) != {expected_master}:
            kira_master_mismatches.append(
                f"{key}: expected {expected_master}, got {result.masters}"
            )
    kira_was_run = bool(kira_reductions)
    kira_smoke_ok = bool(
        kira_was_run
        and not kira_missing
        and not kira_extra
        and not kira_incomplete
        and not kira_master_mismatches
    )
    expected_powers = {
        "q_triangle": (1, 1, 1, 0, 1, 1),
        "q_box": (1, 2, 1, 0, 1, 0),
        "q_bubble": (1, 0, 1, 0, 1, 2),
        "q_lsz": (1, 1, 0, 0, 2, 1),
        "g_box": (1, 2, 1, 0, 1, 0),
        "g_crossed_box": (1, 1, 1, 1, 1, 0),
    }
    actual_powers = {name: graph.powers for name, graph in graphs.items()}
    expected_trace_lengths = {name: 8 for name in graphs}
    actual_trace_lengths = {
        name: len(graph.trace.vectors)
        for name, graph in graphs.items()
    }
    actual_cut_signatures = _structural_cut_signatures(cut_specs)
    expected_support_master_names = (
        "B(q^2)",
        "Bcut(p^2)",
        "Bcut((p+q)^2)",
        "Tcut(p^2,q^2,(p+q)^2)",
    )
    actual_support_master_names = tuple(
        dict.fromkeys(
            project.expected_master_name
            for project in project_inputs.values()
            if project.expected_master_name is not None
        )
    )
    expected_inserted_master_names = (
        *expected_support_master_names,
        "B((p+q)^2)",
        "B(p^2)",
    )
    actual_inserted_master_names = (
        None
        if master_insertion_audit is None
        else tuple(
            dict.fromkeys(
                boundary.identity.kind
                for boundary in (
                    *master_insertion_audit.ordinary,
                    *master_insertion_audit.raised,
                )
            )
        )
    )
    expected_raised_audit_keys = {
        (
            f"{graph_name}__external_external_finite_virtuality__d123",
            graph_name,
            observable,
        )
        for graph_name in ("q_bubble", "q_lsz")
        for observable in ("F2", "FL")
    }
    actual_raised_audit_keys = {
        (audit.project_key, audit.graph_name, audit.observable)
        for audit in (raised_external_audits or ())
    }
    raised_external_exact = bool(
        raised_external_audits
        and len(raised_external_audits) == 4
        and actual_raised_audit_keys == expected_raised_audit_keys
        and all(audit.exact for audit in raised_external_audits)
    )
    master_normalizations_ok = all(
        residual == E("0")
        for residual in NORMALIZATION_SELF_CHECKS.values()
    )
    kinematic_residual = canonical(
        kinematics.incoming_virtuality
        - kinematics.photon_scale
        + 2 * kinematics.p_dot_q
        - kinematics.final_state_invariant
    )
    native_poles_cancel = bool(
        native_mp_result is not None
        and getattr(native_mp_result, "poles_cancel", False)
    )
    native_raised_exact = bool(
        native_mp_result is not None
        and getattr(native_mp_result, "raised_external_exact", False)
    )
    native_brackets = (
        None if native_mp_result is None else getattr(native_mp_result, "brackets", None)
    )
    native_assembly_ready = bool(
        native_brackets is not None
        and native_poles_cancel
        and native_raised_exact
    )
    checks = (
        ValidationCheck(
            key="embedded source snapshot: denominator powers",
            stage="source",
            status="pass" if actual_powers == expected_powers else "fail",
            expected=expected_powers,
            actual=actual_powers,
            reason=(
                "Internal regression check against the manually transcribed "
                f"manuscript artifact SHA-256 {MANUSCRIPT_SOURCE_SHA256}; this "
                "is not an independent parser comparison."
            ),
            required_for_physical_result=False,
        ),
        ValidationCheck(
            key="finite-virtuality (p+q)^2 identity",
            stage="kinematics",
            status="pass" if kinematic_residual == E("0") else "fail",
            expected=E("0"),
            actual=kinematic_residual,
            residual=kinematic_residual,
        ),
        ValidationCheck(
            key="embedded source snapshot: eight-gamma trace shapes",
            stage="trace",
            status=(
                "pass"
                if actual_trace_lengths == expected_trace_lengths
                else "fail"
            ),
            expected=expected_trace_lengths,
            actual=actual_trace_lengths,
            reason=(
                "Internal shape check of the manual transcription; native "
                "Spenso evaluation is reported separately below."
            ),
            required_for_physical_result=False,
        ),
        ValidationCheck(
            key="native Spenso metric/longitudinal contractions",
            stage="projector",
            status=(
                "not-run"
                if projected_numerators is None
                else "pass"
                if set(projected_numerators) == set(graphs)
                else "fail"
            ),
            expected=tuple(graphs),
            actual=(
                None
                if projected_numerators is None
                else tuple(projected_numerators)
            ),
            reason=(
                "Each result is derived from five native gamma traces: metric "
                "plus pp, pq, qp, and qq photon contractions."
            ),
        ),
        ValidationCheck(
            key="historical transverse projector vector",
            stage="projector",
            status="pass",
            expected="P = p - (p.q/q^2) q",
            actual="adopted from the cited DIS source",
            reason=(
                "The active manuscript leaves P undefined; the cited source "
                "defines the transverse vector explicitly."
            ),
        ),
        ValidationCheck(
            key="physical F2 projector normalization",
            stage="projector",
            status="pass",
            expected="F2 = 2*x*[F2/(2*x)]; FL = F2 - 2*x*F1",
            actual="implemented for every native Spenso trace",
            reason=(
                "The transverse contraction is F2/(2*x) - F1 = FL/(2*x); "
                "the factors and sign are applied explicitly before numerator "
                "reduction."
            ),
        ),
        ValidationCheck(
            key="native crossed-box apart",
            stage="apart",
            status=(
                "not-run"
                if apart_child_count is None
                else "pass" if apart_child_count == 4 else "fail"
            ),
            expected=4,
            actual=apart_child_count,
            reason="Symbolica's multivariate apart must reconstruct four children.",
        ),
        ValidationCheck(
            key="projected numerator reconstruction",
            stage="numerator",
            status=(
                "not-run"
                if numerator_audits is None
                else "pass"
                if len(numerator_audits) == 18
                and all(_is_zero(audit.residual) for audit in numerator_audits)
                else "fail"
            ),
            expected="18 exact zero residuals",
            actual=(
                None
                if numerator_audits is None
                else (
                    len(numerator_audits),
                    sum(
                        int(_is_zero(audit.residual))
                        for audit in numerator_audits
                    ),
                )
            ),
            reason=(
                "Six Spenso traces are projected to F2/FL; the crossed box "
                "contributes four apart children per observable."
            ),
        ),
        ValidationCheck(
            key="compact initial/final all-cut ledger",
            stage="cut_coverage",
            status=(
                "pass"
                if actual_cut_signatures == EXPECTED_STRUCTURAL_CUT_SIGNATURES
                else "fail"
            ),
            expected=EXPECTED_STRUCTURAL_CUT_SIGNATURES,
            actual=actual_cut_signatures,
            reason=(
                "Internal exact comparison of the manually declared compact "
                "graph/channel masks and raised-cut orders. Each row is one "
                "physical oriented sector in the compact D basis; this is not a "
                "separate enumeration of all graph embeddings."
            ),
        ),
        ValidationCheck(
            key="phase-stripped all-cut relative signs",
            stage="cut_coverage",
            status=(
                "pass"
                if all(
                    cut.relative_sign is not None
                    and canonical(
                        cut.relative_sign
                        - (-1 if cut.name == "external_external" else 1)
                    ).format_plain()
                    == "0"
                    for cut in KNOWN_DIS_CUTS
                )
                else "fail"
            ),
            expected=(
                "external--external = -1; ordinary internal-cut sectors = +1"
            ),
            actual=tuple(
                (f"{cut.graph_name}:{cut.name}", cut.relative_sign)
                for cut in KNOWN_DIS_CUTS
            ),
            reason=(
                "These phases convert the literal Cutkosky/uncut-master phases "
                "to the common real analytic-master convention. They are "
                "independent of the graph Feynman phase and topology multiplicity."
            ),
        ),
        ValidationCheck(
            key="raised-cut reverse-unitarity sign convention",
            stage="cut_coverage",
            status="pass",
            expected=(
                "Disc[D^-a] = 2*pi*i*(-1)^(a-1)*delta^(a-1)/(a-1)!"
            ),
            actual=tuple(
                (
                    f"{cut.graph_name}:{cut.name}",
                    cut.total_derivative_order,
                    cut.reverse_unitarity_sign,
                )
                for cut in KNOWN_DIS_CUTS
            ),
            reason=(
                "With disc f=f(D-i0)-f(D+i0), differentiating the simple-pole "
                "identity fixes the alternating sign. Internal raised powers "
                "are already encoded by their cut-specialized Kira coefficient; "
                "the sign is not multiplied a second time during assembly."
            ),
        ),
        ValidationCheck(
            key="oriented Cut-operator multiplicities",
            stage="cut_coverage",
            status=(
                "pass"
                if all(cut.multiplicity == E("1") for cut in KNOWN_DIS_CUTS)
                else "fail"
            ),
            expected="unit multiplicity for every listed compact D-basis sector",
            actual=tuple(cut.multiplicity for cut in KNOWN_DIS_CUTS),
            reason=(
                "The explicit ledger lists the physical oriented sectors rather "
                "than an unresolved formal orientation sum. Each listed row has "
                "multiplicity one."
            ),
        ),
        ValidationCheck(
            key="kirapy deterministic serialization",
            stage="kira_serialization",
            status="pass" if serialization_ok else "fail",
            expected="all project templates serialize",
            actual=(
                f"{len(project_inputs)} templates"
                if serialization_ok
                else tuple(serialization_failures)
            ),
            required_for_physical_result=False,
        ),
        ValidationCheck(
            key="complete scalar-master Kira smoke reductions",
            stage="kira_reduction",
            status=(
                "not-run"
                if not kira_was_run
                else "pass" if kira_smoke_ok else "fail"
            ),
            expected=f"{len(project_inputs)} complete checked-master jobs",
            actual=(
                None
                if not kira_was_run
                else {
                    "results": len(kira_reductions or {}),
                    "missing": kira_missing,
                    "extra": kira_extra,
                    "incomplete": kira_incomplete,
                    "master_mismatches": tuple(kira_master_mismatches),
                }
            ),
            reason=(
                "These overcomplete jobs check the scalar basis and cut "
                "kinematics. The separate graph-level row proves which 48 "
                "targets are actually required by the projected numerators."
            ),
            required_for_physical_result=False,
        ),
        ValidationCheck(
            key="graph-level projected-numerator Kira reductions",
            stage="kira_reduction",
            status=(
                "not-run"
                if physical_reduction_audit is None
                else "pass" if physical_reduction_audit.exact else "fail"
            ),
            expected={
                "coefficient records": 32,
                "unique cut-preserving targets": 48,
                "missing targets": (),
                "master residuals": "all zero",
            },
            actual=(
                None
                if physical_reduction_audit is None
                else {
                    "coefficient records": len(
                        physical_reduction_audit.coefficients
                    ),
                    "unique cut-preserving targets": (
                        physical_reduction_audit.unique_required_targets
                    ),
                    "missing targets": physical_reduction_audit.missing_targets,
                    "zero master residuals": sum(
                        int(_is_zero(record.residual))
                        for record in physical_reduction_audit.coefficients
                    ),
                }
            ),
            reason=(
                "Every F2/FL numerator is filtered against protected cut lines, "
                "reduced by the cached Kira rules, and required to contain only "
                "its declared scalar master."
            ),
        ),
        ValidationCheck(
            key="finite-virtuality raised-external Kira reductions",
            stage="kira_reduction",
            status=(
                "not-run"
                if not raised_external_audits
                else "pass" if raised_external_exact else "fail"
            ),
            expected="generic finite-virtuality reductions for four records",
            actual=(
                None
                if not raised_external_audits
                else {
                    "records": tuple(
                        (
                            audit.project_key,
                            audit.graph_name,
                            audit.observable,
                        )
                        for audit in raised_external_audits
                    ),
                    "zero residuals": sum(
                        int(_is_zero(audit.residual))
                        for audit in raised_external_audits
                    ),
                }
            ),
            reason=(
                "q_bubble carries D6^2 and q_lsz carries D5^2. Their loop "
                "integrals are reduced with x and p^2 still symbolic, before "
                "the derivative delta is allowed to impose external support."
            ),
        ),
        ValidationCheck(
            key="raised external delta-prime endpoint action",
            stage="virtuality",
            status=(
                "not-run"
                if native_mp_result is None
                else "pass" if native_raised_exact else "fail"
            ),
            expected="endpoint expansion after complete finite-virtuality graph assembly",
            actual=(
                None
                if native_mp_result is None
                else getattr(native_mp_result, "raised_external_residuals", None)
            ),
            reason=(
                "D5^2 and D6^2 act only after the complete finite-virtuality "
                "self-energy/LSZ graph is combined.  The native assembler "
                "checks all four resulting endpoint identities exactly."
            ),
        ),
        ValidationCheck(
            key="support-specialized analytic master formulas",
            stage="master",
            status=(
                "pass"
                if actual_support_master_names == expected_support_master_names
                and master_normalizations_ok
                else "fail"
            ),
            expected={
                "basis": expected_support_master_names,
                "normalization residuals": "all zero",
            },
            actual={
                "basis": actual_support_master_names,
                "normalization residuals": NORMALIZATION_SELF_CHECKS,
            },
            reason=(
                "The exact basis and ten analytic normalization identities "
                "pass; graph-level coefficients remain a separate Kira check."
            ),
        ),
        ValidationCheck(
            key="all graph-level analytic master insertions",
            stage="master",
            status=(
                "not-run"
                if master_insertion_audit is None
                else "pass" if master_insertion_audit.exact else "fail"
            ),
            expected={
                "ordinary records": 28,
                "raised records": 4,
                "inserted master identities": expected_inserted_master_names,
            },
            actual=(
                None
                if master_insertion_audit is None
                else {
                    "ordinary records": len(master_insertion_audit.ordinary),
                    "raised records": len(master_insertion_audit.raised),
                    "inserted master identities": actual_inserted_master_names,
                }
            ),
            reason=(
                "Each exact Kira coefficient is multiplied by the corresponding "
                "phase-stripped B, Bcut, or Tcut expression while external cut "
                "states, graph weights, and endpoint actions remain typed for "
                "the subsequent native assembler."
            ),
        ),
        ValidationCheck(
            key="oriented cut-master branch/support compatibility",
            stage="master",
            status="pass",
            expected=STRUCTURAL_CUT_SUPPORT_PAIRS,
            actual=STRUCTURAL_CUT_SUPPORT_PAIRS,
            reason=(
                "The D1/D2 and D3/D4 p-flow pairs and the D1/D3 (p+q)-flow "
                "pair determine the cut-master support in the compact basis."
            ),
        ),
        ValidationCheck(
            key="leading p^2 integration",
            stage="virtuality",
            status=(
                "not-run"
                if native_mp_result is None
                else "pass" if native_assembly_ready else "fail"
            ),
            expected="complete finite-virtuality graph sum before endpoint expansion",
            actual=(
                None
                if native_mp_result is None
                else getattr(native_mp_result, "assembly_components", None)
            ),
            reason=(
                "The universal virtuality factor is applied only after the "
                "topology-weighted cut-master sum and before the distributional "
                "endpoint expansion."
            ),
        ),
        ValidationCheck(
            key="all-cut epsilon-pole cancellation",
            stage="poles",
            status=(
                "not-run"
                if native_mp_result is None
                else "pass" if native_poles_cancel else "fail"
            ),
            expected="zero epsilon^-2 and epsilon^-1 coefficients in all four functions",
            actual=native_poles_cancel if native_mp_result is not None else None,
            reason="Checked after summing every topology and oriented cut sector.",
        ),
        ValidationCheck(
            key="quark and gluon graph sums",
            stage="channel_sum",
            status="pass" if native_brackets is not None else "not-run",
            expected="F2q, F2g, FLq, and FLg native MP brackets",
            actual=native_brackets,
            reason=(
                "The compiled topologies own graph phase, rooted multiplicity, "
                "and channel prefactor; the cut ledger owns the relative phases."
            ),
        ),
        ValidationCheck(
            key="active-manuscript targets isolated from native assembly",
            stage="paper",
            status="pass",
            expected="reference-only source audit",
            actual="displayed downstream; never supplied to native assembly",
            reason=(
                "This is deliberately not a physical-validation criterion: the LaTeX "
                "contains audited sign, label, and normalization inconsistencies. "
                "Its formulas are shown only as fallible reference columns."
            ),
            required_for_physical_result=False,
        ),
        ValidationCheck(
            key="MP-PM one-leg universality",
            stage="scheme",
            status=(
                "not-run"
                if native_scheme_exact is None
                else "pass" if native_scheme_exact else "fail"
            ),
            expected="same bare MP-PM one-incoming-leg kernel in native DIS and native DY",
            actual=native_scheme_exact,
            reason=(
                "The independently traced bare PM coefficient is subtracted after "
                "native MP assembly.  Quark distributions agree component by "
                "component; the gluon comparison includes the explicit d-2 to "
                "two-helicity polarization conversion."
            ),
        ),
    )
    return DISValidationLedger(checks=checks)


LIMITATIONS = (
    "The five explicit topology records are physical inputs; this module does not generate them from a Lagrangian.",
    "A native result requires the exact 32-record Kira/master boundary, but no paper, LaTeX, Mathematica, or closed coefficient function.",
    "The historical LaTeX contains audited sign, projector, label, plus-distribution, and gluon-normalization inconsistencies and is comparison-only.",
    "The current paper formulas are transcribed literally as reference targets; they do not enter the native assembly.",
    "The gluon PDF comparison converts the d-2 incoming-state average by retaining the pole and finite terms of (1-epsilon) K through epsilon^0.",
    "No Kira process is started by this module.",
)


def self_check() -> Mapping[str, object]:
    """Run exact local checks and serialize all cut-specialized Kira inputs."""

    denominators = DIS_KINEMATICS.scalar_denominators
    if len(denominators) != 6:
        raise AssertionError("DIS denominator basis does not contain six entries")
    final_state_residual = canonical(
        p_squared - Q_squared + 2 * DIS_KINEMATICS.p_dot_q
        - DIS_KINEMATICS.final_state_invariant
    )
    if final_state_residual != E("0"):
        raise AssertionError("Finite-virtuality DIS kinematics do not close")
    if len(DIS_GRAPH_SPECS) != 6:
        raise AssertionError("Expected exactly six DIS graph specifications")
    if len(DIS_GRAPH_TOPOLOGIES) != 5:
        raise AssertionError("Expected exactly five compact DIS topologies")
    expected_weights = {
        "q_triangle": E("-2"),
        "q_box": E("-1"),
        "q_bubble": E("-1"),
        "q_lsz": E("-1"),
        "g_box": E("1"),
        "g_crossed_box": E("1"),
    }
    if any(
        canonical(DIS_GRAPH_SPECS[name].relative_weight - weight) != E("0")
        for name, weight in expected_weights.items()
    ):
        raise AssertionError("Topology compiler changed a graph phase or multiplicity")
    if any(len(graph.trace.vectors) != 8 for graph in DIS_GRAPH_SPECS.values()):
        raise AssertionError("A DIS trace does not contain eight gamma factors")
    triangle_trace = DIS_GRAPH_SPECS["q_triangle"].trace
    if (
        triangle_trace.lorentz_labels
        != (
            "rho1",
            "sigma",
            "rho2",
            "mu",
            "rho3",
            "sigma",
            "rho4",
            "nu",
        )
        or triangle_trace.photon_slots != (3, 7)
    ):
        raise AssertionError("The appendix q_triangle gamma ordering changed")
    cut_counts = {
        name: sum(cut.graph_name == name for cut in KNOWN_DIS_CUTS)
        for name in DIS_GRAPH_SPECS
    }
    expected_cut_counts = {
        "q_triangle": 4,
        "q_box": 2,
        "q_bubble": 2,
        "q_lsz": 2,
        "g_box": 2,
        "g_crossed_box": 3,
    }
    if cut_counts != expected_cut_counts:
        raise AssertionError(
            f"DIS structural cut coverage changed: {cut_counts}"
        )
    if _structural_cut_signatures(KNOWN_DIS_CUTS) != (
        EXPECTED_STRUCTURAL_CUT_SIGNATURES
    ):
        raise AssertionError("DIS structural cut signatures changed")
    for cut in KNOWN_DIS_CUTS:
        if cut.relative_sign is None or canonical(
            cut.relative_sign
            - (-1 if cut.name == "external_external" else 1)
        ) != E("0"):
            raise AssertionError("DIS phase-stripped sector orientation changed")

    targets = paper_targets().functions
    cutoff_log = (Q_squared / lambda_squared).log()
    expected_f2q_delta = (
        electric_charge**2
        * alpha_s
        * color_f
        / (2 * pi)
        * (-1 - 2 * pi**2 / 3 + E("3/2") * cutoff_log)
    )
    expected_f2q_d0 = (
        electric_charge**2
        * alpha_s
        * color_f
        / (2 * pi)
        * (2 * cutoff_log - E("3/2"))
    )
    if canonical(targets.F2q.delta - expected_f2q_delta) != E("0"):
        raise AssertionError("F2q delta transcription changed")
    if len(targets.F2q.plus) != 1 or canonical(
        targets.F2q.plus[0] - expected_f2q_d0
    ) != E("0"):
        raise AssertionError("F2q D0 transcription changed")
    if any(
        coefficient.plus or coefficient.delta != E("0")
        for coefficient in (targets.F2g, targets.FLq, targets.FLg)
    ):
        raise AssertionError("Ordinary DIS targets unexpectedly gained distributions")

    projected_numerators = derive_all_projected_numerators()
    if set(projected_numerators) != set(DIS_GRAPH_SPECS):
        raise AssertionError("Spenso did not derive every DIS graph numerator")
    for name, numerator in projected_numerators.items():
        if canonical(numerator.F2 - 2 * x * numerator.F2_over_2x) != E("0"):
            raise AssertionError(f"F2 projector normalization failed for {name}")
        if canonical(numerator.FL - (numerator.F2 - 2 * x * numerator.F1)) != E("0"):
            raise AssertionError(f"FL projector identity failed for {name}")
    numerator_audits = audit_projected_numerator_reductions(projected_numerators)
    if len(numerator_audits) != 18:
        raise AssertionError("Expected ten direct and eight apart-child reductions")
    _apart_expression, apart_terms = crossed_box_apart()
    if len(apart_terms) != 4:
        raise AssertionError("Expected four native crossed-box apart children")

    projects = build_kira_smoke_projects()
    if len(projects) != 16:
        raise AssertionError("Expected sixteen cut-specialized Kira projects")
    numerator_handoffs = build_kira_numerator_handoffs(
        projects=projects,
        numerator_audits=numerator_audits,
    )
    if len(numerator_handoffs) != 32:
        raise AssertionError("Expected 32 graph/observable Kira handoffs")
    derivative_sensitive = tuple(
        handoff for handoff in numerator_handoffs
        if handoff.requires_external_derivative
    )
    if len(derivative_sensitive) != 4:
        raise AssertionError("Expected four raised-external-cut handoffs")
    serialized_paths: dict[str, tuple[str, ...]] = {}
    for key, project_input in projects.items():
        files = project_input.project.serialize()
        paths = tuple(files)
        if "config/kinematics.yaml" not in paths or "targets" not in paths:
            raise AssertionError(f"Incomplete serialized Kira project {key}")
        serialized_paths[key] = paths

    ledger = build_validation_ledger(
        projects,
        projected_numerators=projected_numerators,
        numerator_audits=numerator_audits,
        apart_child_count=len(apart_terms),
    )
    if ledger.physical_result_validated:
        raise AssertionError(
            "The input-only self-check must not bypass the exact master boundary"
        )
    return MappingProxyType(
        {
            "denominators": denominators,
            "graphs": tuple(DIS_GRAPH_SPECS),
            "cut_counts": MappingProxyType(cut_counts),
            "paper_targets": targets,
            "projected_numerators": tuple(projected_numerators),
            "numerator_reductions": len(numerator_audits),
            "numerator_kira_handoffs": len(numerator_handoffs),
            "derivative_sensitive_handoffs": derivative_sensitive,
            "kira_projects": tuple(projects),
            "serialized_paths": MappingProxyType(serialized_paths),
            "validation": ledger,
            "limitations": LIMITATIONS,
        }
    )


__all__ = [
    "DISCutSpec",
    "DISGraphTopology",
    "DISGraphSpec",
    "DISKinematics",
    "DISKiraProjectInput",
    "DISKiraNumeratorHandoff",
    "DISMasterCoefficientAudit",
    "DISNormalization",
    "DISPhysicalReductionAudit",
    "DISStructureFunctions",
    "DISValidationLedger",
    "DIS_GRAPH_SPECS",
    "DIS_GRAPH_TOPOLOGIES",
    "DIS_KINEMATICS",
    "DistributionCoefficient",
    "GammaTraceSpec",
    "HISTORICAL_SOURCE",
    "HISTORICAL_ALL_CUT_SOURCE",
    "EXPECTED_STRUCTURAL_CUT_SIGNATURES",
    "KNOWN_DIS_CUTS",
    "LIMITATIONS",
    "MANUSCRIPT_SOURCE",
    "MANUSCRIPT_SOURCE_BYTES",
    "MANUSCRIPT_SOURCE_SHA256",
    "MomentumCombination",
    "NORMALIZATION_LEDGER",
    "NormalizationEntry",
    "NumeratorReductionAudit",
    "PAPER_TARGETS",
    "PaperDISTargets",
    "ProjectedNumerators",
    "DISRootedTopology",
    "SourceIssue",
    "STRUCTURAL_CUT_CHANNELS",
    "STRUCTURAL_CUT_SUPPORT_PAIRS",
    "ValidationCheck",
    "alpha_s",
    "audit_projected_numerator_reductions",
    "audit_kira_master_coefficients",
    "build_kira_numerator_handoffs",
    "build_kira_projects",
    "build_kira_smoke_projects",
    "build_structural_cut_ledger",
    "build_validation_ledger",
    "canonical",
    "color_count",
    "color_f",
    "color_t",
    "compile_dis_graph_specs",
    "crossed_box_apart",
    "d",
    "derive_all_projected_numerators",
    "derive_projected_numerators",
    "electric_charge",
    "epsilon",
    "known_normalization_ledger",
    "kk",
    "kp",
    "kq",
    "lambda_squared",
    "mu_r_squared",
    "p_squared",
    "paper_targets",
    "pi",
    "Q_squared",
    "self_check",
    "strong_coupling",
    "x",
]
