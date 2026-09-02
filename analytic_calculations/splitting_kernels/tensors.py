"""Spenso/Idenso tensor constructions used by the notebook."""

from dataclasses import dataclass
from functools import lru_cache

from symbolica import Expression, S
from symbolica.community.idenso import (
    expand_mink,
    expand_mink_bis,
    simplify_gamma,
    simplify_metrics,
)
from symbolica.community.spenso import Representation, Slot, TensorName

from .kinematics import Kinematics, canonical
from .kernels import ap_gg_cdr, ap_qg_cdr


def as_expression(value: Expression | Slot) -> Expression:
    if isinstance(value, Expression):
        return value
    return value.to_expression()


@dataclass(frozen=True)
class TensorContext:
    minkowski: Representation
    bispinor: Representation
    gamma: Expression
    p: TensorName
    k: TensorName
    q: TensorName
    n: TensorName

    def vector(self, name: TensorName, index: str) -> Expression:
        return as_expression(name(self.minkowski(index)))

    def gamma_matrix(
        self,
        incoming: int | str,
        outgoing: int | str,
        lorentz: str,
    ) -> Expression:
        return self.gamma(
            as_expression(self.bispinor(incoming)),
            as_expression(self.bispinor(outgoing)),
            as_expression(self.minkowski(lorentz)),
        )


@dataclass(frozen=True)
class ProjectorChecks:
    momentum_transversality: Expression
    reference_transversality: Expression
    signed_idempotence: Expression
    polarization_trace: Expression


@dataclass(frozen=True)
class GluonParentNumeratorResult:
    metric_term: Expression
    axial_mixed_terms: Expression
    offshell_transverse_completion: Expression
    massless_polarization_sum: Expression
    p_transverse_polarization_sum: Expression
    massless_residual: Expression
    p_transverse_residual: Expression


@dataclass(frozen=True)
class GluonBornNumeratorResult:
    metric_term: Expression
    axial_mixed_terms: Expression
    offshell_longitudinal_completion: Expression
    reduced_numerator: Expression
    expected_numerator: Expression
    residual: Expression


@dataclass(frozen=True)
class QuarkParentNumeratorResult:
    metric_term: Expression
    axial_mixed_terms: Expression
    reduced_numerator: Expression
    expected_numerator: Expression
    residual: Expression


@dataclass(frozen=True)
class GluonSelfSplittingNumeratorResult:
    metric_term: Expression
    axial_terms: Expression
    reduced_numerator: Expression
    expected_numerator: Expression
    residual: Expression


@dataclass(frozen=True)
class GluonVirtualNumeratorResult:
    gluon_metric_term: Expression
    gluon_mixed_term: Expression
    gluon_completion_term: Expression
    gluon_loop_coefficient: Expression
    gluon_expected_coefficient: Expression
    gluon_residual: Expression
    quark_metric_term: Expression
    quark_mixed_term: Expression
    quark_completion_term: Expression
    quark_loop_coefficient: Expression
    quark_expected_coefficient: Expression
    quark_residual: Expression


@dataclass(frozen=True)
class VirtualNumeratorResult:
    metric_term: Expression
    mixed_terms: Expression
    gauge_norm_term: Expression
    exact_projected_coefficient: Expression
    leading_coefficient: Expression
    expected_coefficient: Expression
    residual: Expression


def make_tensor_context(kinematics: Kinematics) -> TensorContext:
    return TensorContext(
        minkowski=Representation("mink", kinematics.d),
        bispinor=Representation.bis(4),
        gamma=S("spenso::gamma"),
        p=TensorName("p"),
        k=TensorName("k"),
        q=TensorName("q"),
        n=TensorName("n"),
    )


def axial_projector(
    tensors: TensorContext,
    first: str,
    second: str,
    momentum_dot_reference: Expression,
    momentum_squared: Expression,
) -> Expression:
    q_first = tensors.vector(tensors.q, first)
    q_second = tensors.vector(tensors.q, second)
    n_first = tensors.vector(tensors.n, first)
    n_second = tensors.vector(tensors.n, second)
    metric = as_expression(tensors.minkowski.g(first, second))
    return (
        -metric
        + (q_first * n_second + n_first * q_second)
        / momentum_dot_reference
        - momentum_squared
        * n_first
        * n_second
        / momentum_dot_reference**2
    )


def _replace_contracted_pairs(
    expression: Expression,
    tensors: TensorContext,
    indices: tuple[str, ...],
    pair_values: tuple[tuple[TensorName, TensorName, Expression | int], ...],
) -> Expression:
    result = expression
    for index in indices:
        for first, second, value in pair_values:
            product = tensors.vector(first, index) * tensors.vector(second, index)
            result = result.replace(product, value)
    return canonical(result.expand())


def projector_checks(
    tensors: TensorContext,
    kinematics: Kinematics,
) -> ProjectorChecks:
    q_dot_n = S("q_dot_n")
    q_squared = S("q_squared")
    projector = lambda first, second: axial_projector(
        tensors,
        first,
        second,
        q_dot_n,
        q_squared,
    )
    pair_values = (
        (tensors.q, tensors.q, q_squared),
        (tensors.q, tensors.n, q_dot_n),
        (tensors.n, tensors.n, 0),
    )

    momentum_contraction = simplify_metrics(
        expand_mink(
            tensors.vector(tensors.q, "mu") * projector("mu", "nu")
        )
    )
    momentum_contraction = _replace_contracted_pairs(
        momentum_contraction,
        tensors,
        ("mu", "nu"),
        pair_values,
    )

    reference_contraction = simplify_metrics(
        expand_mink(
            tensors.vector(tensors.n, "mu") * projector("mu", "nu")
        )
    )
    reference_contraction = _replace_contracted_pairs(
        reference_contraction,
        tensors,
        ("mu", "nu"),
        pair_values,
    )

    projector_square = simplify_metrics(
        expand_mink(projector("mu", "rho") * projector("rho", "nu"))
    )
    signed_idempotence = _replace_contracted_pairs(
        projector_square + projector("mu", "nu"),
        tensors,
        ("mu", "nu", "rho"),
        pair_values,
    )

    projector_trace = simplify_metrics(
        expand_mink(projector("mu", "nu") * projector("mu", "nu"))
    )
    projector_trace = _replace_contracted_pairs(
        projector_trace,
        tensors,
        ("mu", "nu"),
        pair_values,
    )

    return ProjectorChecks(
        momentum_transversality=momentum_contraction,
        reference_transversality=reference_contraction,
        signed_idempotence=signed_idempotence,
        polarization_trace=canonical(projector_trace - (kinematics.d - 2)),
    )


def gluon_parent_quark_born_numerator(
    tensors: TensorContext,
    kinematics: Kinematics,
) -> GluonParentNumeratorResult:
    """Project the g -> q qbar numerator onto the opaque quark Born."""

    p = tensors.p
    k = tensors.k
    n = tensors.n
    vector = tensors.vector
    gamma = tensors.gamma_matrix
    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    d = kinematics.d
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2
    lightcone_dot = kinematics.lightcone_dot
    metric = as_expression(tensors.minkowski.g("mu", "nu"))

    def p_minus_k(index: str) -> Expression:
        return vector(p, index) - vector(k, index)

    # Inserting slash(n) as a probe extracts the coefficient of slash(p_+)
    # without inspecting the hard Born object. Tr[slash(n) slash(p_+)]=4 p.n.
    trace_probe = (
        p_minus_k("a")
        * gamma(1, 2, "a")
        * vector(n, "b")
        * gamma(2, 3, "b")
        * p_minus_k("c")
        * gamma(3, 4, "c")
        * gamma(4, 5, "mu")
        * vector(k, "e")
        * gamma(5, 6, "e")
        * gamma(6, 1, "nu")
    )
    projector_pieces = (
        -metric,
        (
            vector(p, "mu") * vector(n, "nu")
            + vector(n, "mu") * vector(p, "nu")
        )
        / lightcone_dot,
        -p2
        * vector(n, "mu")
        * vector(n, "nu")
        / lightcone_dot**2,
    )
    pair_values = (
        (p, p, p2),
        (k, k, 0),
        (n, n, 0),
        (p, k, kinematics.p_dot_k),
        (p, n, lightcone_dot),
        (k, n, cut_fraction * lightcone_dot),
    )

    coefficients = []
    for piece in projector_pieces:
        reduced = simplify_gamma(expand_mink_bis(trace_probe * piece))
        reduced = simplify_metrics(expand_mink(reduced))
        reduced = _replace_contracted_pairs(
            reduced,
            tensors,
            ("a", "b", "c", "e", "mu", "nu"),
            pair_values,
        )
        coefficients.append(canonical(reduced / (4 * lightcone_dot)))

    metric_term, axial_mixed_terms, completion = coefficients
    massless_sum = canonical(metric_term + axial_mixed_terms)
    p_transverse_sum = canonical(massless_sum + completion)
    kernel = 2 * (x**2 + cut_fraction**2) + d - 4
    expected_massless = (
        4 * cut_fraction * x**2 * p2
        + transverse2 * kernel / cut_fraction
    )
    expected_p_transverse = transverse2 * kernel / cut_fraction
    return GluonParentNumeratorResult(
        metric_term=metric_term,
        axial_mixed_terms=axial_mixed_terms,
        offshell_transverse_completion=completion,
        massless_polarization_sum=massless_sum,
        p_transverse_polarization_sum=p_transverse_sum,
        massless_residual=canonical(massless_sum - expected_massless),
        p_transverse_residual=canonical(
            p_transverse_sum - expected_p_transverse
        ),
    )


def gluon_born_reduced_numerator(
    tensors: TensorContext,
    kinematics: Kinematics,
) -> GluonBornNumeratorResult:
    """Compute Tr[p/ gamma_mu k/ gamma_nu] Pi^(mu nu)(p-k,n)."""

    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2
    lightcone_dot = kinematics.lightcone_dot
    p_dot_k = kinematics.p_dot_k
    q_squared = kinematics.reduced_virtuality
    q_dot_n = x * lightcone_dot

    metric = as_expression(tensors.minkowski.g("mu", "nu"))
    projector_pieces = (
        -metric,
        (
            tensors.vector(tensors.q, "mu")
            * tensors.vector(tensors.n, "nu")
            + tensors.vector(tensors.n, "mu")
            * tensors.vector(tensors.q, "nu")
        )
        / q_dot_n,
        -q_squared
        * tensors.vector(tensors.n, "mu")
        * tensors.vector(tensors.n, "nu")
        / q_dot_n**2,
    )
    trace = (
        tensors.vector(tensors.p, "a")
        * tensors.gamma_matrix(1, 2, "a")
        * tensors.gamma_matrix(2, 3, "mu")
        * tensors.vector(tensors.k, "b")
        * tensors.gamma_matrix(3, 4, "b")
        * tensors.gamma_matrix(4, 1, "nu")
    )
    pair_values = (
        (tensors.p, tensors.p, p2),
        (tensors.k, tensors.k, 0),
        (tensors.q, tensors.q, q_squared),
        (tensors.n, tensors.n, 0),
        (tensors.p, tensors.k, p_dot_k),
        (tensors.p, tensors.q, p2 - p_dot_k),
        (tensors.k, tensors.q, p_dot_k),
        (tensors.p, tensors.n, lightcone_dot),
        (tensors.k, tensors.n, cut_fraction * lightcone_dot),
        (tensors.q, tensors.n, q_dot_n),
    )
    coefficients = []
    for projector_piece in projector_pieces:
        reduced = simplify_gamma(
            expand_mink_bis(trace * projector_piece)
        )
        reduced = simplify_metrics(expand_mink(reduced))
        coefficients.append(
            canonical(
                _replace_contracted_pairs(
                    reduced,
                    tensors,
                    ("a", "b", "mu", "nu"),
                    pair_values,
                )
            )
        )

    metric_term, axial_mixed_terms, completion = coefficients
    numerator = canonical(metric_term + axial_mixed_terms + completion)
    expected = canonical(
        2 * (kinematics.d - 2) * cut_fraction * p2
        + 4
        * transverse2
        * (
            (1 + cut_fraction**2) / x
            - (4 - kinematics.d) * x / 2
        )
        / (x * cut_fraction)
    )
    return GluonBornNumeratorResult(
        metric_term=metric_term,
        axial_mixed_terms=axial_mixed_terms,
        offshell_longitudinal_completion=completion,
        reduced_numerator=numerator,
        expected_numerator=expected,
        residual=canonical(numerator - expected),
    )


def quark_born_reduced_numerator(
    tensors: TensorContext,
    kinematics: Kinematics,
) -> QuarkParentNumeratorResult:
    """Project the q -> qg open chain onto the opaque quark Born."""

    p = tensors.p
    k = tensors.k
    n = tensors.n
    vector = tensors.vector
    gamma = tensors.gamma_matrix
    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    d = kinematics.d
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2
    lightcone_dot = kinematics.lightcone_dot
    metric = as_expression(tensors.minkowski.g("mu", "nu"))

    def k_minus_p(index: str) -> Expression:
        return vector(k, index) - vector(p, index)

    # Tr[n/ M]/(4 p.n) extracts the p/ coefficient of the open chain M.
    trace_probe = (
        k_minus_p("a")
        * gamma(1, 2, "a")
        * gamma(2, 3, "mu")
        * vector(p, "b")
        * gamma(3, 4, "b")
        * gamma(4, 5, "nu")
        * k_minus_p("c")
        * gamma(5, 6, "c")
        * vector(n, "e")
        * gamma(6, 1, "e")
    )
    projector_pieces = (
        -metric,
        (
            vector(k, "mu") * vector(n, "nu")
            + vector(n, "mu") * vector(k, "nu")
        )
        / (cut_fraction * lightcone_dot),
    )
    pair_values = (
        (p, p, p2),
        (k, k, 0),
        (n, n, 0),
        (p, k, kinematics.p_dot_k),
        (p, n, lightcone_dot),
        (k, n, cut_fraction * lightcone_dot),
    )

    coefficients = []
    for piece in projector_pieces:
        reduced = simplify_gamma(expand_mink_bis(trace_probe * piece))
        reduced = simplify_metrics(expand_mink(reduced))
        reduced = _replace_contracted_pairs(
            reduced,
            tensors,
            ("a", "b", "c", "e", "mu", "nu"),
            pair_values,
        )
        coefficients.append(canonical(reduced / (4 * lightcone_dot)))

    metric_term, axial_mixed_terms = coefficients
    numerator = canonical(metric_term + axial_mixed_terms)
    expected = (
        (d - 2) * x**2 * p2
        + (d - 2) * transverse2
        + 4 * x * transverse2 / cut_fraction**2
    )
    return QuarkParentNumeratorResult(
        metric_term=metric_term,
        axial_mixed_terms=axial_mixed_terms,
        reduced_numerator=numerator,
        expected_numerator=canonical(expected),
        residual=canonical(numerator - expected),
    )


def _three_gluon_splitting_vertex(
    tensors: TensorContext,
    parent_index: str,
    hard_index: str,
    cut_index: str,
) -> Expression:
    """Return V(parent p, hard -q, cut -k), with q=p-k."""

    metric = lambda first, second: as_expression(
        tensors.minkowski.g(first, second)
    )
    vector = tensors.vector

    def linear(index: str, p_factor: int, k_factor: int) -> Expression:
        return (
            p_factor * vector(tensors.p, index)
            + k_factor * vector(tensors.k, index)
        )

    return (
        metric(parent_index, hard_index)
        * linear(cut_index, 2, -1)
        + metric(hard_index, cut_index)
        * linear(parent_index, -1, 2)
        + metric(cut_index, parent_index)
        * linear(hard_index, -1, -1)
    )


@lru_cache(maxsize=None)
def _cached_gluon_self_splitting_numerator(
    kinematics: Kinematics,
) -> GluonSelfSplittingNumeratorResult:
    """Derive the normalized real g -> gg numerator from two YM vertices."""

    tensors = make_tensor_context(kinematics)
    p = tensors.p
    k = tensors.k
    n = tensors.n
    vector = tensors.vector
    metric = lambda first, second: as_expression(
        tensors.minkowski.g(first, second)
    )
    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    p2 = kinematics.p2
    transverse2 = kinematics.transverse2
    lightcone_dot = kinematics.lightcone_dot
    hard_squared = kinematics.reduced_virtuality

    def hard(index: str) -> Expression:
        return vector(p, index) - vector(k, index)

    def transverse_projector(
        momentum,
        first: str,
        second: str,
        momentum_dot_reference: Expression,
        momentum_squared: Expression,
    ) -> Expression:
        return (
            -metric(first, second)
            + (
                momentum(first) * vector(n, second)
                + vector(n, first) * momentum(second)
            )
            / momentum_dot_reference
            - momentum_squared
            * vector(n, first)
            * vector(n, second)
            / momentum_dot_reference**2
        )

    parent_projector = transverse_projector(
        lambda index: vector(p, index),
        "a",
        "b",
        lightcone_dot,
        p2,
    )
    cut_projector = transverse_projector(
        lambda index: vector(k, index),
        "m",
        "u",
        cut_fraction * lightcone_dot,
        Expression.num(0),
    )
    hard_projector = transverse_projector(
        hard,
        "r",
        "s",
        x * lightcone_dot,
        hard_squared,
    )
    vertex_product = _three_gluon_splitting_vertex(
        tensors,
        "a",
        "r",
        "m",
    ) * _three_gluon_splitting_vertex(
        tensors,
        "b",
        "s",
        "u",
    )
    pair_values = (
        (p, p, p2),
        (k, k, 0),
        (n, n, 0),
        (p, k, kinematics.p_dot_k),
        (p, n, lightcone_dot),
        (k, n, cut_fraction * lightcone_dot),
    )

    def reduce(projectors: Expression) -> Expression:
        reduced = simplify_metrics(
            expand_mink(vertex_product * projectors)
        )
        reduced = _replace_contracted_pairs(
            reduced,
            tensors,
            ("a", "b", "r", "s", "m", "u"),
            pair_values,
        )
        return canonical(reduced / (kinematics.d - 2))

    metric_term = reduce(
        -metric("a", "b")
        * -metric("m", "u")
        * -metric("r", "s")
    )
    numerator = reduce(
        parent_projector * cut_projector * hard_projector
    )
    expected = canonical(
        2
        * transverse2
        * ap_gg_cdr(x, (4 - kinematics.d) / 2)
        / (x * cut_fraction)
    )
    return GluonSelfSplittingNumeratorResult(
        metric_term=metric_term,
        axial_terms=canonical(numerator - metric_term),
        reduced_numerator=numerator,
        expected_numerator=expected,
        residual=canonical(numerator - expected),
    )


def gluon_self_splitting_numerator(
    tensors: TensorContext,
    kinematics: Kinematics,
) -> GluonSelfSplittingNumeratorResult:
    """Return the cached scalar reduction of the real g -> gg numerator."""

    del tensors
    return _cached_gluon_self_splitting_numerator(kinematics)


@lru_cache(maxsize=None)
def _cached_gluon_virtual_self_energy_numerator(
    kinematics: Kinematics,
) -> GluonVirtualNumeratorResult:
    """Project the cut gluon and quark bubbles onto the external gluon Born."""

    tensors = make_tensor_context(kinematics)
    p = tensors.p
    k = tensors.k
    eta = TensorName("eta_virtual")
    vector = tensors.vector
    gamma = tensors.gamma_matrix
    metric = lambda first, second: as_expression(
        tensors.minkowski.g(first, second)
    )
    eta_vector = lambda index: as_expression(
        eta(tensors.minkowski(index))
    )
    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    p2 = kinematics.p2
    lightcone_dot = kinematics.lightcone_dot
    eta_squared = p2 + 2 * lightcone_dot
    p_dot_eta = p2 + lightcone_dot
    k_dot_eta = p2 / 2 + cut_fraction * lightcone_dot
    hard_dot_eta = p2 / 2 + x * lightcone_dot

    def hard(index: str) -> Expression:
        return vector(p, index) - vector(k, index)

    def on_shell_axial_projector(
        momentum,
        first: str,
        second: str,
        momentum_dot_eta: Expression,
    ) -> Expression:
        return (
            -metric(first, second)
            + (
                momentum(first) * eta_vector(second)
                + eta_vector(first) * momentum(second)
            )
            / momentum_dot_eta
            - eta_squared
            * momentum(first)
            * momentum(second)
            / momentum_dot_eta**2
        )

    external_projector_pieces = (
        -metric("a", "b"),
        (
            vector(p, "a") * eta_vector("b")
            + eta_vector("a") * vector(p, "b")
        )
        / p_dot_eta,
        -p2
        * eta_vector("a")
        * eta_vector("b")
        / p_dot_eta**2,
    )
    cut_projector = on_shell_axial_projector(
        lambda index: vector(k, index),
        "m",
        "u",
        k_dot_eta,
    )
    hard_projector = on_shell_axial_projector(
        hard,
        "r",
        "s",
        hard_dot_eta,
    )
    pair_values = (
        (p, p, p2),
        (k, k, 0),
        (eta, eta, eta_squared),
        (p, k, p2 / 2),
        (p, eta, p_dot_eta),
        (k, eta, k_dot_eta),
    )
    vertex_product = _three_gluon_splitting_vertex(
        tensors,
        "a",
        "r",
        "m",
    ) * _three_gluon_splitting_vertex(
        tensors,
        "b",
        "s",
        "u",
    )

    def reduce_gluon(projector_piece: Expression) -> Expression:
        reduced = simplify_metrics(
            expand_mink(
                vertex_product
                * projector_piece
                * cut_projector
                * hard_projector
            )
        )
        reduced = _replace_contracted_pairs(
            reduced,
            tensors,
            ("a", "b", "r", "s", "m", "u"),
            pair_values,
        )
        return canonical(reduced / (kinematics.d - 2))

    gluon_exact_pieces = tuple(
        reduce_gluon(piece) for piece in external_projector_pieces
    )
    gluon_leading_pieces = tuple(
        canonical(piece.series(p2, 0, 1).get_coefficient(1) * p2)
        for piece in gluon_exact_pieces
    )
    gluon_leading = canonical(sum(gluon_leading_pieces))
    gluon_expected = canonical(
        2 * p2 * ap_gg_cdr(x, (4 - kinematics.d) / 2)
    )

    quark_trace = (
        vector(k, "i")
        * gamma(1, 2, "i")
        * gamma(2, 3, "a")
        * hard("j")
        * gamma(3, 4, "j")
        * gamma(4, 1, "b")
    )

    def reduce_quark(projector_piece: Expression) -> Expression:
        reduced = simplify_gamma(
            expand_mink_bis(quark_trace * projector_piece)
        )
        reduced = simplify_metrics(expand_mink(reduced))
        reduced = _replace_contracted_pairs(
            reduced,
            tensors,
            ("a", "b", "i", "j"),
            pair_values,
        )
        return canonical(reduced / (kinematics.d - 2))

    quark_exact_pieces = tuple(
        reduce_quark(piece) for piece in external_projector_pieces
    )
    quark_leading_pieces = tuple(
        canonical(piece.series(p2, 0, 1).get_coefficient(1) * p2)
        for piece in quark_exact_pieces
    )
    quark_leading = canonical(sum(quark_leading_pieces))
    quark_expected = canonical(
        2 * p2 * ap_qg_cdr(x, (4 - kinematics.d) / 2)
    )
    return GluonVirtualNumeratorResult(
        gluon_metric_term=gluon_leading_pieces[0],
        gluon_mixed_term=gluon_leading_pieces[1],
        gluon_completion_term=gluon_leading_pieces[2],
        gluon_loop_coefficient=gluon_leading,
        gluon_expected_coefficient=gluon_expected,
        gluon_residual=canonical(gluon_leading - gluon_expected),
        quark_metric_term=quark_leading_pieces[0],
        quark_mixed_term=quark_leading_pieces[1],
        quark_completion_term=quark_leading_pieces[2],
        quark_loop_coefficient=quark_leading,
        quark_expected_coefficient=quark_expected,
        quark_residual=canonical(quark_leading - quark_expected),
    )


def gluon_virtual_self_energy_numerator(
    tensors: TensorContext,
    kinematics: Kinematics,
) -> GluonVirtualNumeratorResult:
    """Return the cached scalar reduction of the complete gluon self-energy."""

    del tensors
    return _cached_gluon_virtual_self_energy_numerator(kinematics)


def virtual_self_energy_numerator(
    tensors: TensorContext,
    kinematics: Kinematics,
) -> VirtualNumeratorResult:
    """Project the cut quark self-energy numerator onto slash(p1)."""

    p = tensors.p
    k = tensors.k
    probe = TensorName("p2ref")
    eta = TensorName("eta")
    x = kinematics.x
    cut_fraction = kinematics.cut_fraction
    d = kinematics.d
    p2 = kinematics.p2
    lightcone_dot = kinematics.lightcone_dot
    k_dot_eta = cut_fraction * lightcone_dot + p2 / 2
    eta_squared = p2 + 2 * lightcone_dot

    vector = tensors.vector
    gamma = tensors.gamma_matrix
    metric = as_expression(tensors.minkowski.g("mu", "nu"))
    trace_probe = (
        vector(probe, "r")
        * gamma(1, 2, "r")
        * vector(p, "b")
        * gamma(2, 3, "b")
        * gamma(3, 4, "mu")
        * (vector(p, "a") - vector(k, "a"))
        * gamma(4, 5, "a")
        * gamma(5, 6, "nu")
        * vector(p, "c")
        * gamma(6, 1, "c")
    )

    projector_pieces = (
        -metric,
        (
            vector(k, "mu") * vector(eta, "nu")
            + vector(eta, "mu") * vector(k, "nu")
        )
        / k_dot_eta,
        -eta_squared
        * vector(k, "mu")
        * vector(k, "nu")
        / k_dot_eta**2,
    )
    pair_values = (
        (p, p, p2),
        (k, k, 0),
        (probe, probe, 0),
        (eta, eta, eta_squared),
        (p, k, p2 / 2),
        (p, probe, lightcone_dot),
        (p, eta, p2 + lightcone_dot),
        (k, probe, cut_fraction * lightcone_dot),
        (k, eta, k_dot_eta),
        (probe, eta, lightcone_dot),
    )

    projected_pieces: list[Expression] = []
    for projector_piece in projector_pieces:
        reduced = simplify_gamma(
            expand_mink_bis(trace_probe * projector_piece)
        )
        reduced = simplify_metrics(expand_mink(reduced))
        reduced = _replace_contracted_pairs(
            reduced,
            tensors,
            ("r", "a", "b", "c", "mu", "nu"),
            pair_values,
        )
        projected_pieces.append(
            canonical(reduced / (4 * lightcone_dot))
        )

    leading_pieces = tuple(
        canonical(
            piece.series(p2, 0, 1).get_coefficient(1) * p2
        )
        for piece in projected_pieces
    )
    exact = canonical(sum(projected_pieces))
    leading = canonical(sum(leading_pieces))
    expected = canonical(
        p2 * (cut_fraction * (d - 2) + 4 * x / cut_fraction)
    )
    return VirtualNumeratorResult(
        metric_term=leading_pieces[0],
        mixed_terms=leading_pieces[1],
        gauge_norm_term=leading_pieces[2],
        exact_projected_coefficient=exact,
        leading_coefficient=leading,
        expected_coefficient=expected,
        residual=canonical((leading - expected).expand()),
    )
