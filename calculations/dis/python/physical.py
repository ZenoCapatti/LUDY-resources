"""Exact, side-effect-free input model for the NLO DIS validation.

This module deliberately stops before claiming a physical result.  It records
the kinematics, the six graph integrands printed in the manuscript, the four
reported structure functions, the known normalization ownership, and native
``kirapy`` project templates.  The manuscript does not contain the complete
Cutkosky-cut ledger, graph weights, IBP master map, or the dimension-dependent
splitting kernels needed for the LU-to-MSbar conversion.  Those missing inputs
are represented by blocked validation checks rather than inferred silently.

Importing this module never starts Kira.  :func:`self_check` performs only
exact Symbolica checks and deterministic in-memory Kira serialization.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from itertools import combinations, product
from types import MappingProxyType
from typing import Any, Literal, cast

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


MANUSCRIPT_SOURCE = (
    "../LUDY/references/factorisable-local-unitarity/source/main.tex"
)
MANUSCRIPT_SOURCE_SHA256 = (
    "6a9a8b1c926e646933dd4ab65b7f2b7644486d5dee112528de5e392a4804fd5a"
)
MANUSCRIPT_SOURCE_BYTES = 52_260
HISTORICAL_SOURCE = "arXiv:2506.16489v1"
DIS_DEFINITION_SOURCE = f"{MANUSCRIPT_SOURCE}:166-175,223-229"
DIS_RESULT_SOURCE = f"{MANUSCRIPT_SOURCE}:293-311"
DIS_INTEGRAND_SOURCE = f"{MANUSCRIPT_SOURCE}:394-412"


def _expression(value: Expression | int | str) -> Expression:
    """Convert a scalar input to one exact Symbolica expression."""

    return value if isinstance(value, Expression) else E(str(value))


def canonical(expression: Expression | int) -> Expression:
    """Canonical expanded rational form used by exact scalar checks."""

    return _expression(expression).expand().together().cancel()


# Plain native symbols are intentional.  Pretty printing belongs to the
# notebook; calculations and persisted Kira inputs retain stable names.
d = S("d")
epsilon = S("epsilon")
x = S("x")
p_squared = S("p_squared")
Q_squared = S("Q_squared")
lambda_squared = S("Lambda_squared")
mu_r_squared = S("mu_R_squared")
kk = S("kk")
kp = S("kp")
kq = S("kq")
k = S("k")
p = S("p")
q = S("q")
electric_charge = S("e_q")
strong_coupling = S("g_s")
alpha_s = S("alpha_s")
color_f = S("C_F")
color_t = S("T_F")
color_count = S("N_c")
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

    @property
    def leading_power_rules(self) -> tuple[tuple[Expression, Expression], ...]:
        """The named leading-power step; it is never imposed implicitly."""

        return ((self.incoming_virtuality, E("0")),)

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


@dataclass(frozen=True, slots=True)
class DISGraphSpec:
    """One graph numerator and its powers in the common ``D1,...,D6`` basis."""

    name: str
    channel: Channel
    powers: tuple[int, int, int, int, int, int]
    trace: GammaTraceSpec
    relative_weight: Expression | None = None
    source: str = DIS_INTEGRAND_SOURCE

    def __post_init__(self) -> None:
        if len(self.powers) != 6 or any(power < 0 for power in self.powers):
            raise ValueError("A DIS graph needs six non-negative denominator powers")

    @property
    def loop_powers(self) -> tuple[int, int, int, int]:
        return self.powers[:4]

    def external_denominator_factor(
        self,
        kinematics: DISKinematics = DIS_KINEMATICS,
    ) -> Expression:
        """Return the explicit ``D5,D6`` factor left outside Kira."""

        d5, d6 = kinematics.scalar_denominators[4:]
        return 1 / (d5 ** self.powers[4] * d6 ** self.powers[5])


def _trace(
    vectors: Sequence[MomentumCombination | None],
    labels: Sequence[str],
    photon_slots: tuple[int, int],
) -> GammaTraceSpec:
    return GammaTraceSpec(tuple(vectors), tuple(labels), photon_slots)


DIS_GRAPH_SPECS: Mapping[str, DISGraphSpec] = MappingProxyType(
    {
        "q_triangle": DISGraphSpec(
            name="q_triangle",
            channel="q",
            powers=(1, 1, 1, 0, 1, 1),
            trace=_trace(
                (P, None, KP, None, KPQ, None, PQ, None),
                ("rho1", "mu", "rho2", "sigma", "rho3", "nu", "rho4", "sigma"),
                (1, 5),
            ),
        ),
        "q_box": DISGraphSpec(
            name="q_box",
            channel="q",
            powers=(1, 2, 1, 0, 1, 0),
            trace=_trace(
                (P, None, KP, None, KPQ, None, KP, None),
                ("rho1", "sigma", "rho2", "mu", "rho3", "nu", "rho4", "sigma"),
                (3, 5),
            ),
        ),
        "q_bubble": DISGraphSpec(
            name="q_bubble",
            channel="q",
            powers=(1, 0, 1, 0, 1, 2),
            trace=_trace(
                (P, None, PQ, None, KPQ, None, PQ, None),
                ("rho1", "mu", "rho2", "sigma", "rho3", "sigma", "rho4", "nu"),
                (1, 7),
            ),
        ),
        "q_lsz": DISGraphSpec(
            name="q_lsz",
            channel="q",
            powers=(1, 1, 0, 0, 2, 1),
            trace=_trace(
                (P, None, PQ, None, P, None, KP, None),
                ("rho1", "mu", "rho2", "nu", "rho3", "sigma", "rho4", "sigma"),
                (1, 3),
            ),
        ),
        "g_box": DISGraphSpec(
            name="g_box",
            channel="g",
            powers=(1, 2, 1, 0, 1, 0),
            trace=_trace(
                (K, None, KP, None, KPQ, None, KP, None),
                ("rho1", "sigma", "rho2", "mu", "rho3", "nu", "rho4", "sigma"),
                (3, 5),
            ),
        ),
        "g_crossed_box": DISGraphSpec(
            name="g_crossed_box",
            channel="g",
            powers=(1, 1, 1, 1, 1, 0),
            trace=_trace(
                (K, None, KP, None, KPQ, None, KQ, None),
                ("rho1", "sigma", "rho2", "mu", "rho3", "sigma", "rho4", "nu"),
                (3, 7),
            ),
        ),
    }
)


@dataclass(frozen=True, slots=True)
class ProjectedNumerators:
    """One Spenso-derived trace in the paper's scalar projector basis.

    The returned expressions have already been translated from native Spenso
    dots to the stable scalar coordinates ``kk``, ``kp``, and ``kq``.  ``F2``
    follows the projector printed in the active manuscript.  The cited DIS
    source uses an additional normalization in its historical ``W2 -> F2``
    map; that convention difference remains a source issue below.
    """

    metric: Expression
    transverse_vector_square: Expression
    longitudinal: Expression
    F1: Expression
    F2: Expression
    FL: Expression
    ward: Expression


def _spenso_gamma_trace(vectors, labels, *, dimension: Expression) -> Expression:
    """Close one even gamma trace and convert it to native Spenso dots."""

    from symbolica.community.idenso import simplify_gamma, simplify_metrics, to_dots
    from symbolica.community.spenso import Representation, TensorName

    minkowski = Representation.mink(dimension=dimension)
    bispinor = Representation.bis(4)
    gamma = TensorName.gamma()(bispinor, bispinor, minkowski)
    result = E("1")
    chain_length = len(vectors)
    for index, (vector, label) in enumerate(zip(vectors, labels, strict=True)):
        slot = minkowski(label)
        result *= gamma(
            bispinor(index),
            bispinor((index + 1) % chain_length),
            slot,
        ).to_expression()
        if vector is not None:
            result *= vector(slot).to_expression()
    return to_dots(
        simplify_metrics(simplify_gamma(result).expand()).expand()
    ).expand()


def derive_projected_numerators(
    graph: DISGraphSpec | str,
    *,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> ProjectedNumerators:
    """Derive the metric, longitudinal, ``F1``, ``F2``, and ``FL`` traces.

    The historical source defines
    ``P^mu = p^mu - (p.q/q^2) q^mu``.  Linearity of the two photon slashes is
    used explicitly: four native Spenso traces build ``P_mu P_nu N^munu``.
    This avoids hiding the projector in an opaque composite-vector atom.
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
    metric = _spenso_gamma_trace(
        source_vectors,
        metric_labels,
        dimension=kinematics.dimension,
    )

    def contracted(left_vector, right_vector, label: str) -> Expression:
        vectors = list(source_vectors)
        labels = list(source_labels)
        vectors[left_slot] = left_vector
        vectors[right_slot] = right_vector
        labels[left_slot] = f"dis_{label}_left"
        labels[right_slot] = f"dis_{label}_right"
        return _spenso_gamma_trace(
            vectors,
            labels,
            dimension=kinematics.dimension,
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
    f2 = canonical(
        (
            metric_scalar
            + (1 - kinematics.dimension) * longitudinal
        )
        / (2 - kinematics.dimension)
    )
    fl = canonical(f1 - 2 * kinematics.bjorken_x * f2)
    return ProjectedNumerators(
        metric=metric_scalar,
        transverse_vector_square=transverse_square,
        longitudinal=longitudinal,
        F1=f1,
        F2=f2,
        FL=fl,
        ward=qq_scalar,
    )


def derive_all_projected_numerators() -> Mapping[str, ProjectedNumerators]:
    """Derive all six physical numerator records deterministically."""

    return MappingProxyType(
        {
            name: derive_projected_numerators(graph)
            for name, graph in DIS_GRAPH_SPECS.items()
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


def crossed_box_apart():
    """Return Symbolica's exact four-child crossed-box decomposition."""

    # These helpers are process independent but presently live at the single
    # tested implementation site used by the DY pipeline.
    from calculations.dy.python.physical import apart_kernel

    return apart_kernel(
        DIS_KINEMATICS.scalar_denominators[:4],
        loop_scalar_products=(kk, kp, kq),
    )


def audit_projected_numerator_reductions(
    projected: Mapping[str, ProjectedNumerators] | None = None,
) -> tuple[NumeratorReductionAudit, ...]:
    """Reconstruct both physical numerators for every graph exactly.

    The calculation is kept at finite incoming virtuality.  Five graphs use
    ``D1,D2,D3`` directly.  The crossed box is first decomposed by Symbolica's
    native multivariate ``apart`` and each of its four three-line children is
    reduced with the graph's actual base powers.
    """

    from calculations.dy.python.physical import reduce_numerator

    numerators = projected or derive_all_projected_numerators()
    denominators = DIS_KINEMATICS.scalar_denominators
    _apart_expression, apart_terms = crossed_box_apart()
    audits: list[NumeratorReductionAudit] = []
    for graph_name, graph in DIS_GRAPH_SPECS.items():
        for observable in ("F2", "FL"):
            numerator = getattr(numerators[graph_name], observable)
            if graph_name != "g_crossed_box":
                reduction = reduce_numerator(
                    numerator,
                    denominators[:3],
                    loop_scalar_products=(kk, kp, kq),
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
                    loop_scalar_products=(kk, kp, kq),
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
    def zero(cls, variable: Expression) -> DistributionCoefficient:
        return cls(variable=variable)

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
    """Encode the four reported LU-scheme targets with explicit assumptions.

    Lines 296--297 label the first pair ``F_L`` and lines 302--303 then provide
    a second, different ``F_L`` pair.  The logarithmic first pair is interpreted
    as ``F_2``.  The undefined ``P_ij(x,0)`` symbols are expanded using the
    color-stripped leading-order kernels, since the printed equations already
    carry ``C_F`` or ``T_F`` outside.  Both assumptions remain attached issues;
    this object is a comparison target, not a literal source AST.
    """

    normalization = electric_charge**2 * alpha_s / (2 * pi)
    cutoff_log = (lambda_squared * x**2 / Q_squared).log()
    p_gq = 1 - 2 * x + 2 * x**2
    delta_x = DistributionCoefficient.delta_basis(x)
    d0_x = DistributionCoefficient.plus_basis(x, 0)
    p_qq = delta_x.scaled(E("3/2")) + d0_x.multiply_smooth(1 + x**2)

    f2g = DistributionCoefficient(
        variable=x,
        regular=normalization
        * x
        * color_t
        * (p_gq * (cutoff_log + 1) + 2 * x * (x - 1)),
    )
    f2q_bracket = (
        p_qq.multiply_smooth(cutoff_log)
        + delta_x.scaled(1 + 2 * pi**2 / 3)
        + d0_x.multiply_smooth((6 * x**2 - 4 * x + 1) / 2)
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
                "F2g": "F_Lg at manuscript line 296 (interpreted as F_2g)",
                "F2q": "F_Lq at manuscript line 297 (interpreted as F_2q)",
                "FLg": "F_Lg at manuscript line 302",
                "FLq": "F_Lq at manuscript line 303",
            }
        ),
        issues=(
            SourceIssue(
                key="duplicate-longitudinal-labels",
                severity="warning",
                description=(
                    "The logarithmic formulas at lines 296--297 and the ordinary "
                    "formulas at lines 302--303 are all labelled F_L. The first "
                    "pair is interpreted as F_2 but needs source confirmation."
                ),
                source=DIS_RESULT_SOURCE,
            ),
            SourceIssue(
                key="historical-projector-vector",
                severity="note",
                description=(
                    "The active manuscript leaves uppercase P undefined. The cited "
                    "DIS source defines P = p - (p.q/q^2) q, which is adopted here."
                ),
                source=(
                    f"{MANUSCRIPT_SOURCE}:305; {HISTORICAL_SOURCE}, "
                    "Submission/DIS_setup.tex:94-104"
                ),
            ),
            SourceIssue(
                key="color-stripped-kernel-convention",
                severity="warning",
                description=(
                    "P_gq(x,0) and P_qq(x,0) are not defined in the active "
                    "manuscript. The target assumes their color-stripped LO forms "
                    "because C_F and T_F are already printed outside."
                ),
                source=f"{MANUSCRIPT_SOURCE}:252-254,296-297",
            ),
            SourceIssue(
                key="f2-projector-normalization",
                severity="blocker",
                description=(
                    "The active P2/F2 definition and the cited historical W2-to-F2 "
                    "normalization are not the same. They require an explicit map "
                    "before an integrated residual is meaningful."
                ),
                source=(
                    f"{MANUSCRIPT_SOURCE}:305; {HISTORICAL_SOURCE}, "
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
    """Return known normalization ownership without inventing graph weights."""

    common = (
        NormalizationEntry(
            name="loop integration measure",
            value=1 / (2 * pi) ** d,
            owner="analytic_master",
            applied_in_physical_handoff=False,
            source=f"{MANUSCRIPT_SOURCE}:398",
            note="Must already be present in each analytic master.",
        ),
        NormalizationEntry(
            name="per-cut-edge phase-space factor",
            value=2 * pi,
            owner="analytic_master",
            applied_in_physical_handoff=False,
            source=f"{MANUSCRIPT_SOURCE}:207-208,229",
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
            source=f"{MANUSCRIPT_SOURCE}:173,226",
            note="The singular p^2 integration supplies the remaining epsilon factor.",
        ),
        NormalizationEntry(
            name="DIS observable factor",
            value=1 / (4 * pi),
            owner="external_measure",
            applied_in_physical_handoff=True,
            source=f"{MANUSCRIPT_SOURCE}:173,226",
            note="Together with dp^2/(2pi), this gives dp^2/(8pi^2).",
        ),
        NormalizationEntry(
            name="stripped graph coupling",
            value=electric_charge**2 * strong_coupling**2,
            owner="graph",
            applied_in_physical_handoff=True,
            source=f"{MANUSCRIPT_SOURCE}:398",
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
                name="incoming quark spin-colour average",
                value=1 / (2 * color_count),
                owner="channel",
                applied_in_physical_handoff=True,
                source=f"{MANUSCRIPT_SOURCE}:229",
            ),
            NormalizationEntry(
                name="target quark-channel colour factor",
                value=color_f,
                owner="channel",
                applied_in_physical_handoff=True,
                source=f"{MANUSCRIPT_SOURCE}:297,303",
                note="Raw per-graph colour sums are not supplied in the manuscript.",
            ),
        ),
        limitations=(
            "Per-graph signs, multiplicities, and raw colour sums are missing.",
            "The external LSZ/LU-apex note at manuscript line 228 is unresolved.",
        ),
    )
    gluon = DISNormalization(
        channel="g",
        entries=common
        + (
            NormalizationEntry(
                name="incoming gluon spin-colour average",
                value=1 / ((d - 2) * (color_count**2 - 1)),
                owner="channel",
                applied_in_physical_handoff=True,
                source=f"{MANUSCRIPT_SOURCE}:229",
            ),
            NormalizationEntry(
                name="target gluon-channel colour factor",
                value=color_t,
                owner="channel",
                applied_in_physical_handoff=True,
                source=f"{MANUSCRIPT_SOURCE}:296,302",
                note="Raw per-graph colour sums are not supplied in the manuscript.",
            ),
        ),
        limitations=(
            "Per-graph signs, multiplicities, and raw colour sums are missing.",
            "The external LSZ/LU-apex note at manuscript line 228 is unresolved.",
        ),
    )
    return MappingProxyType({"q": quark, "g": gluon})


NORMALIZATION_LEDGER = known_normalization_ledger()


@dataclass(frozen=True, slots=True)
class DISCutSpec:
    """One authoritative double-discontinuity sector, once supplied.

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
        if self.graph_name not in DIS_GRAPH_SPECS:
            raise ValueError(f"Unknown DIS graph {self.graph_name!r}")
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


# These six channel pairings are the four-term all-cut formula made explicit
# for D1,...,D6.  Compatibility with a graph is purely structural: every cut
# line must occur with positive power in that graph.  The source does not ship
# orientations, relative signs, or multiplicities, so those remain ``None``.
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


def _build_structural_cut_ledger() -> tuple[DISCutSpec, ...]:
    cuts: list[DISCutSpec] = []
    source = (
        f"{HISTORICAL_SOURCE}, Submission/Discontinuities.tex:143-168; "
        f"{DIS_INTEGRAND_SOURCE}"
    )
    for graph in DIS_GRAPH_SPECS.values():
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
                    relative_sign=None,
                    multiplicity=None,
                    source=source,
                )
            )
    return tuple(cuts)


KNOWN_DIS_CUTS: tuple[DISCutSpec, ...] = _build_structural_cut_ledger()


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
        cuts_by_graph.setdefault(cut.graph_name, []).append(cut)

    for graph in DIS_GRAPH_SPECS.values():
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
    bounds: ReductionBounds | None = None,
    kinematics: DISKinematics = DIS_KINEMATICS,
) -> Mapping[str, DISKiraProjectInput]:
    """Build the complete 16-project scalar-master smoke set.

    Each cut-compatible three-line family receives the cut-preserving
    ``{1, 0, -1}^3`` target cube plus its source graph's raised base target.
    The expected scalar master is supplied as a checked preferred master.  The
    cube deliberately tests serialization, cut kinematics, and the scalar
    master basis; it is not a substitute for translating every projected
    numerator monomial into graph-level Kira targets.
    """

    prototypes = build_kira_projects(
        cut_specs=cut_specs,
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
        graph = DIS_GRAPH_SPECS[project_input.graph_name]
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
        target_indices_by_key=target_indices_by_key,
        preferred_master_indices_by_key=preferred_master_indices_by_key,
        bounds=bounds,
        kinematics=kinematics,
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
    projected_numerators: Mapping[str, ProjectedNumerators] | None = None,
    numerator_audits: Sequence[NumeratorReductionAudit] | None = None,
    apart_child_count: int | None = None,
    kira_reductions: Mapping[str, ReductionResult] | None = None,
) -> DISValidationLedger:
    """Report exactly what the current module proves and what remains missing."""

    project_inputs = projects or build_kira_projects()
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
    actual_powers = {name: graph.powers for name, graph in DIS_GRAPH_SPECS.items()}
    expected_trace_lengths = {name: 8 for name in DIS_GRAPH_SPECS}
    actual_trace_lengths = {
        name: len(graph.trace.vectors)
        for name, graph in DIS_GRAPH_SPECS.items()
    }
    actual_cut_signatures = _structural_cut_signatures(KNOWN_DIS_CUTS)
    expected_master_names = (
        "B(q^2)",
        "Bcut(p^2)",
        "Bcut((p+q)^2)",
        "Tcut(p^2,q^2,(p+q)^2)",
    )
    actual_master_names = tuple(
        dict.fromkeys(
            project.expected_master_name
            for project in project_inputs.values()
            if project.expected_master_name is not None
        )
    )
    master_normalizations_ok = all(
        residual == E("0")
        for residual in NORMALIZATION_SELF_CHECKS.values()
    )
    kinematic_residual = canonical(
        p_squared - Q_squared + 2 * DIS_KINEMATICS.p_dot_q
        - DIS_KINEMATICS.final_state_invariant
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
                if set(projected_numerators) == set(DIS_GRAPH_SPECS)
                else "fail"
            ),
            expected=tuple(DIS_GRAPH_SPECS),
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
            key="active-to-historical F2 projector normalization",
            stage="projector",
            status="blocked",
            reason=(
                "The active printed P2/F2 definition omits factors present in "
                "the cited source; an explicit convention map is still needed."
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
                and all(audit.residual == E("0") for audit in numerator_audits)
                else "fail"
            ),
            expected="18 exact zero residuals",
            actual=(
                None
                if numerator_audits is None
                else (
                    len(numerator_audits),
                    sum(
                        int(bool(audit.residual == E("0")))
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
            key="structural initial/final all-cut coverage",
            stage="cut_coverage",
            status=(
                "pass"
                if actual_cut_signatures == EXPECTED_STRUCTURAL_CUT_SIGNATURES
                else "fail"
            ),
            expected=EXPECTED_STRUCTURAL_CUT_SIGNATURES,
            actual=actual_cut_signatures,
            reason=(
                "Exact topology-level comparison of every graph, channel, "
                "initial/final mask, and raised-cut derivative order."
            ),
        ),
        ValidationCheck(
            key="oriented cut signs and multiplicities",
            stage="cut_coverage",
            status="blocked",
            expected="one weight for every structural cut sector",
            actual=sum(
                cut.relative_sign is not None and cut.multiplicity is not None
                for cut in KNOWN_DIS_CUTS
            ),
            reason=(
                "The source does not ship the oriented Cutkosky ledger or its "
                "relative graph weights."
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
                "These jobs check the scalar basis and cut kinematics only; "
                "they do not contain the full projected-numerator target set."
            ),
            required_for_physical_result=False,
        ),
        ValidationCheck(
            key="graph-level projected-numerator Kira reductions",
            stage="kira_reduction",
            status="blocked",
            reason=(
                "The 18 exact numerator reconstructions have not yet been "
                "translated into complete per-child integral target sets and "
                "combined with authoritative graph weights."
            ),
        ),
        ValidationCheck(
            key="one-loop analytic master basis",
            stage="master",
            status=(
                "pass"
                if actual_master_names == expected_master_names
                and master_normalizations_ok
                else "fail"
            ),
            expected={
                "basis": expected_master_names,
                "normalization residuals": "all zero",
            },
            actual={
                "basis": actual_master_names,
                "normalization residuals": NORMALIZATION_SELF_CHECKS,
            },
            reason=(
                "The exact basis and nine analytic normalization identities "
                "pass; graph-level coefficients remain a separate Kira check."
            ),
        ),
        ValidationCheck(
            key="oriented cut-master branch/support compatibility",
            stage="master",
            status="blocked",
            reason=(
                "Theta support and square-root branches require the missing "
                "energy orientations and signed Cutkosky ledger."
            ),
        ),
        ValidationCheck(
            key="leading p^2 integration",
            stage="virtuality",
            status="not-run",
            reason="It can only follow insertion of the cut masters and raised-cut terms.",
        ),
        ValidationCheck(
            key="all-cut epsilon-pole cancellation",
            stage="poles",
            status="blocked",
            reason="Requires every initial- and final-state cut contribution.",
        ),
        ValidationCheck(
            key="quark and gluon graph sums",
            stage="channel_sum",
            status="blocked",
            reason="Per-graph weights and complete cut contributions are missing.",
        ),
        ValidationCheck(
            key="native result minus four paper targets",
            stage="paper",
            status="blocked",
            reason=(
                "The paper targets are transcribed, but no native integrated result "
                "exists yet; target transcription is not validation."
            ),
        ),
        ValidationCheck(
            key="LU to MSbar conversion",
            stage="scheme",
            status="blocked",
            reason=(
                "The required d-dimensional splitting kernels and confirmed "
                "boundary conventions are not specified in the source excerpt."
            ),
        ),
    )
    return DISValidationLedger(checks=checks)


LIMITATIONS = (
    "Cut-compatible sectors are known, but their oriented signs and multiplicities are not.",
    "The scalar master basis is known, but graph-level DIS IBP coefficients are not.",
    "No graph signs, multiplicities, or raw colour sums have been supplied.",
    "The cited source defines P, but the active and historical F2 normalizations differ.",
    "The first two DIS formulas duplicate the F_L labels and are interpreted as F_2.",
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
    if any(len(graph.trace.vectors) != 8 for graph in DIS_GRAPH_SPECS.values()):
        raise AssertionError("A DIS trace does not contain eight gamma factors")
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

    targets = paper_targets().functions
    cutoff_log_at_endpoint = (lambda_squared / Q_squared).log()
    expected_f2q_delta = (
        electric_charge**2
        * alpha_s
        * color_f
        / (2 * pi)
        * (E("3/2") * cutoff_log_at_endpoint + 1 + 2 * pi**2 / 3)
    )
    expected_f2q_d0 = (
        electric_charge**2
        * alpha_s
        * color_f
        / (2 * pi)
        * (2 * cutoff_log_at_endpoint + E("3/2"))
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
        if canonical(numerator.FL - (numerator.F1 - 2 * x * numerator.F2)) != E("0"):
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
        raise AssertionError("Scaffolding must not claim a validated physical result")
    return MappingProxyType(
        {
            "denominators": denominators,
            "graphs": tuple(DIS_GRAPH_SPECS),
            "cut_counts": MappingProxyType(cut_counts),
            "paper_targets": targets,
            "projected_numerators": tuple(projected_numerators),
            "numerator_reductions": len(numerator_audits),
            "kira_projects": tuple(projects),
            "serialized_paths": MappingProxyType(serialized_paths),
            "validation": ledger,
            "limitations": LIMITATIONS,
        }
    )


__all__ = [
    "DISCutSpec",
    "DISGraphSpec",
    "DISKinematics",
    "DISKiraProjectInput",
    "DISNormalization",
    "DISStructureFunctions",
    "DISValidationLedger",
    "DIS_GRAPH_SPECS",
    "DIS_KINEMATICS",
    "DistributionCoefficient",
    "GammaTraceSpec",
    "HISTORICAL_SOURCE",
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
    "SourceIssue",
    "STRUCTURAL_CUT_CHANNELS",
    "ValidationCheck",
    "alpha_s",
    "audit_projected_numerator_reductions",
    "build_kira_projects",
    "build_kira_smoke_projects",
    "build_validation_ledger",
    "canonical",
    "color_count",
    "color_f",
    "color_t",
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
