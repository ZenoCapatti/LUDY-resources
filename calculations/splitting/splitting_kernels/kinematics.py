"""Shared Sudakov kinematics and collinear power counting."""

from dataclasses import dataclass

from symbolica import Expression, S


@dataclass(frozen=True)
class Kinematics:
    """Sudakov identities with x assigned to the hard daughter."""

    d: Expression
    epsilon: Expression
    x: Expression
    p2: Expression
    transverse2: Expression
    lightcone_dot: Expression
    cutoff2: Expression
    renormalization_scale2: Expression
    collinear_parameter: Expression
    born_quark: Expression
    born_gluon: Expression
    theta: Expression
    delta: Expression

    @property
    def alpha(self) -> Expression:
        return self.transverse2 / (
            2 * (1 - self.x) * self.lightcone_dot
        )

    @property
    def cut_fraction(self) -> Expression:
        return 1 - self.x

    @property
    def p_dot_k(self) -> Expression:
        return canonical(
            self.cut_fraction * self.p2 / 2
            + self.transverse2 / (2 * self.cut_fraction)
        )

    @property
    def reduced_virtuality(self) -> Expression:
        return self.x * self.p2 - self.transverse2 / self.cut_fraction

    @property
    def virtuality_root(self) -> Expression:
        return self.transverse2 / (self.x * (1 - self.x))

    @property
    def transverse_cutoff(self) -> Expression:
        return self.x * (1 - self.x) * self.cutoff2


def make_kinematics() -> Kinematics:
    d, epsilon, x, p2, transverse2, lightcone_dot, cutoff2, mu2, lam = S(
        "d",
        "epsilon",
        "x",
        "p2",
        "kperp2",
        "pplusdotpminus",
        "Lambda2",
        "mu2",
        "lambda",
    )
    sigma, quark, gluon = S("sigma", "q", "g")
    born_quark, born_gluon = sigma(quark), sigma(gluon)
    theta, delta = S("Theta", "Delta")
    return Kinematics(
        d=d,
        epsilon=epsilon,
        x=x,
        p2=p2,
        transverse2=transverse2,
        lightcone_dot=lightcone_dot,
        cutoff2=cutoff2,
        renormalization_scale2=mu2,
        collinear_parameter=lam,
        born_quark=born_quark,
        born_gluon=born_gluon,
        theta=theta,
        delta=delta,
    )


def canonical(expression: Expression) -> Expression:
    """Canonicalize a rational Symbolica expression without string conversion."""

    return expression.together().cancel()


def symbolic_difference(left: Expression, right: Expression) -> Expression:
    return canonical(left - right)


def assert_symbolic_equal(
    left: Expression,
    right: Expression,
    label: str,
) -> None:
    difference = symbolic_difference(left, right)
    if difference != 0:
        raise AssertionError(f"{label}: non-zero symbolic difference {difference}")


def joint_collinear_scale(expression: Expression, kinematics: Kinematics) -> Expression:
    """Apply p^2 ~ |k_perp|^2 ~ lambda^2 simultaneously."""

    lam = kinematics.collinear_parameter
    return expression.replace(
        kinematics.p2,
        lam**2 * kinematics.p2,
    ).replace(
        kinematics.transverse2,
        lam**2 * kinematics.transverse2,
    )


def collinear_coefficient(
    expression: Expression,
    kinematics: Kinematics,
    power: int = 2,
) -> Expression:
    scaled = joint_collinear_scale(expression, kinematics).expand()
    return canonical(scaled.coefficient(kinematics.collinear_parameter**power))


def set_dimension(expression: Expression, kinematics: Kinematics) -> Expression:
    return canonical(
        expression.replace(
            kinematics.d,
            4 - 2 * kinematics.epsilon,
        )
    )


def complement_momentum_fraction(
    expression: Expression,
    kinematics: Kinematics,
) -> Expression:
    """Apply x -> 1-x simultaneously using a temporary Symbolica symbol."""

    temporary = S("x_complement_swap")
    return expression.replace(kinematics.x, temporary).replace(
        temporary,
        1 - kinematics.x,
    )
