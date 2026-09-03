"""Symbolica/Idenso reductions of the QCD color factors."""

from dataclasses import dataclass

from symbolica import Expression, S
from symbolica.community.idenso import expand_color, simplify_color
from symbolica.community.spenso import Representation, Slot, TensorName

from .kinematics import canonical


def _as_expression(value: Expression | Slot) -> Expression:
    if isinstance(value, Expression):
        return value
    return value.to_expression()


@dataclass(frozen=True)
class ColorReduction:
    raw_contraction: Expression
    reduced_contraction: Expression
    identity_tensor: Expression
    invariant: Expression
    conventional_label: Expression
    labeled_reduction: Expression
    residual: Expression


@dataclass(frozen=True)
class ColorContext:
    nc: Expression
    na: Expression
    nf: Expression
    cf: Expression
    ca: Expression
    tr: Expression
    fundamental: Representation
    adjoint: Representation
    quark_emission: ColorReduction
    gluon_to_quarks: ColorReduction
    gluon_emission: ColorReduction
    cf_su_n: Expression
    ca_su_n: Expression
    tr_su_n: Expression


def _reduction(
    raw: Expression,
    identity: Expression,
    label: Expression,
) -> ColorReduction:
    reduced = simplify_color(expand_color(raw))
    invariant = reduced.coefficient(identity)
    if invariant == 0:
        raise ValueError(f"Could not extract color invariant from {reduced}")
    residual = canonical(reduced - invariant * identity)
    if residual != 0:
        raise ValueError(f"Unreduced color structure remains: {residual}")
    return ColorReduction(
        raw_contraction=raw,
        reduced_contraction=reduced,
        identity_tensor=identity,
        invariant=invariant,
        conventional_label=label,
        labeled_reduction=reduced.replace(invariant, label),
        residual=residual,
    )


def make_color_context() -> ColorContext:
    nc, na, nf, cf, ca, tr = S(
        "N_c",
        "N_A",
        "n_f",
        "C_F",
        "C_A",
        "T_R",
    )
    fundamental = Representation.cof(nc)
    adjoint = Representation.coad(na)
    generator = TensorName.t()
    structure_constant = TensorName.f()

    t_a_i_j = _as_expression(
        generator(
            adjoint("a"),
            fundamental("i"),
            fundamental("j").dual(),
        )
    )
    t_a_j_k = _as_expression(
        generator(
            adjoint("a"),
            fundamental("j"),
            fundamental("k").dual(),
        )
    )
    fundamental_identity = _as_expression(fundamental.id("k", "i"))
    quark_emission = _reduction(
        t_a_i_j * t_a_j_k,
        fundamental_identity,
        cf,
    )

    t_b_j_i = _as_expression(
        generator(
            adjoint("b"),
            fundamental("j"),
            fundamental("i").dual(),
        )
    )
    adjoint_ab_identity = _as_expression(adjoint.g("a", "b"))
    gluon_to_quarks = _reduction(
        t_a_i_j * t_b_j_i,
        adjoint_ab_identity,
        tr,
    )

    f_abc = _as_expression(
        structure_constant(adjoint("a"), adjoint("b"), adjoint("c"))
    )
    f_dbc = _as_expression(
        structure_constant(adjoint("d"), adjoint("b"), adjoint("c"))
    )
    adjoint_ad_identity = _as_expression(adjoint.g("a", "d"))
    gluon_emission = _reduction(
        f_abc * f_dbc,
        adjoint_ad_identity,
        ca,
    )

    tr_su_n = canonical(nc / (2 * nc))
    return ColorContext(
        nc=nc,
        na=na,
        nf=nf,
        cf=cf,
        ca=ca,
        tr=tr,
        fundamental=fundamental,
        adjoint=adjoint,
        quark_emission=quark_emission,
        gluon_to_quarks=gluon_to_quarks,
        gluon_emission=gluon_emission,
        cf_su_n=canonical((nc**2 - 1) / (2 * nc)),
        ca_su_n=nc,
        tr_su_n=tr_su_n,
    )
