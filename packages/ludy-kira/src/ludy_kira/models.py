"""Symbolica-native input models for Kira projects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from symbolica import E, Expression, S

from .errors import KiraConfigurationError

if TYPE_CHECKING:
    from .serialization import ProjectFiles


def _expression(value: Expression | int | str) -> Expression:
    if isinstance(value, Expression):
        return value
    try:
        return E(str(value))
    except Exception as exc:  # pragma: no cover - Symbolica supplies the detail
        raise KiraConfigurationError(
            f"Cannot convert {value!r} to an expression"
        ) from exc


def _expressions(values: Any) -> tuple[Expression, ...]:
    return tuple(_expression(value) for value in values)


def _integers(values: Any, *, field_name: str) -> tuple[int, ...]:
    result = tuple(values)
    if any(isinstance(value, bool) or not isinstance(value, int) for value in result):
        raise KiraConfigurationError(f"{field_name} must contain integers")
    return result


def _plain_name(name: str, *, field_name: str = "name") -> str:
    if not name or not (name[0].isalpha() or name[0] == "_"):
        raise KiraConfigurationError(f"{field_name} must be a non-empty identifier")
    if not all(character.isalnum() or character == "_" for character in name):
        raise KiraConfigurationError(f"{field_name} must be an unqualified identifier")
    return name


@dataclass(frozen=True, slots=True)
class Propagator:
    """One inverse propagator, represented as ``momentum**2 - mass_squared``."""

    momentum: Expression
    mass_squared: Expression = field(default_factory=lambda: E("0"))

    def __post_init__(self) -> None:
        object.__setattr__(self, "momentum", _expression(self.momentum))
        object.__setattr__(self, "mass_squared", _expression(self.mass_squared))


@dataclass(frozen=True, slots=True)
class KinematicInvariant:
    expression: Expression
    mass_dimension: int
    kira_name: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "expression", _expression(self.expression))
        if isinstance(self.mass_dimension, bool) or not isinstance(
            self.mass_dimension, int
        ):
            raise KiraConfigurationError("mass_dimension must be an integer")
        if self.kira_name is not None:
            object.__setattr__(
                self,
                "kira_name",
                _plain_name(self.kira_name, field_name="invariant kira_name"),
            )

    @property
    def symbol(self) -> Expression:
        """Compatibility alias for :attr:`expression`."""

        return self.expression


@dataclass(frozen=True, slots=True, init=False)
class ScalarProductRule:
    left: Expression
    right: Expression
    value: Expression

    def __init__(
        self,
        left: Expression | int | str,
        right: Expression | int | str,
        value: Expression | int | str,
    ) -> None:
        object.__setattr__(self, "left", _expression(left))
        object.__setattr__(self, "right", _expression(right))
        object.__setattr__(self, "value", _expression(value))


@dataclass(frozen=True, slots=True)
class Kinematics:
    incoming_momenta: tuple[Expression, ...]
    kinematic_invariants: tuple[KinematicInvariant, ...] = ()
    scalar_products: tuple[ScalarProductRule, ...] = ()
    outgoing_momenta: tuple[Expression, ...] = ()
    momentum_conservation: tuple[Expression, Expression] | None = None
    symbol_to_replace_by_one: Expression | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "incoming_momenta", _expressions(self.incoming_momenta)
        )
        object.__setattr__(
            self, "outgoing_momenta", _expressions(self.outgoing_momenta)
        )
        object.__setattr__(
            self, "kinematic_invariants", tuple(self.kinematic_invariants)
        )
        object.__setattr__(self, "scalar_products", tuple(self.scalar_products))
        if self.momentum_conservation is not None:
            if len(self.momentum_conservation) != 2:
                raise KiraConfigurationError(
                    "momentum_conservation must contain two expressions"
                )
            object.__setattr__(
                self,
                "momentum_conservation",
                (
                    _expression(self.momentum_conservation[0]),
                    _expression(self.momentum_conservation[1]),
                ),
            )
        if self.symbol_to_replace_by_one is not None:
            object.__setattr__(
                self,
                "symbol_to_replace_by_one",
                _expression(self.symbol_to_replace_by_one),
            )

    @property
    def scalarproduct_rules(self) -> tuple[ScalarProductRule, ...]:
        """Alias matching Kira's spelling of the YAML key."""

        return self.scalar_products


@dataclass(frozen=True, slots=True)
class IntegralFamily:
    name: str
    loop_momenta: tuple[Expression, ...]
    propagators: tuple[Propagator, ...]
    top_level_sectors: tuple[int, ...]
    cut_propagators: tuple[int, ...] = ()
    zero_sectors: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "name", _plain_name(self.name, field_name="family name")
        )
        object.__setattr__(self, "loop_momenta", _expressions(self.loop_momenta))
        object.__setattr__(self, "propagators", tuple(self.propagators))
        object.__setattr__(
            self,
            "top_level_sectors",
            _integers(self.top_level_sectors, field_name="top_level_sectors"),
        )
        object.__setattr__(
            self,
            "cut_propagators",
            _integers(self.cut_propagators, field_name="cut_propagators"),
        )
        object.__setattr__(
            self,
            "zero_sectors",
            _integers(self.zero_sectors, field_name="zero_sectors"),
        )
        if not self.loop_momenta:
            raise KiraConfigurationError(
                "An integral family needs at least one loop momentum"
            )
        if not self.propagators:
            raise KiraConfigurationError(
                "An integral family needs at least one propagator"
            )
        if not self.top_level_sectors:
            raise KiraConfigurationError(
                "An integral family needs at least one top-level sector"
            )

    @property
    def arity(self) -> int:
        return len(self.propagators)

    def __call__(self, *indices: int) -> Expression:
        if len(indices) != self.arity:
            raise KiraConfigurationError(
                f"{self.name} expects {self.arity} indices, received {len(indices)}"
            )
        if any(
            isinstance(index, bool) or not isinstance(index, int) for index in indices
        ):
            raise KiraConfigurationError("Integral indices must be integers")
        return S(self.name)(*indices)


@dataclass(frozen=True, slots=True)
class ReductionBounds:
    sectors: tuple[int, ...]
    r: int
    s: int
    d: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "sectors", _integers(self.sectors, field_name="sectors")
        )
        for name in ("r", "s", "d"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise KiraConfigurationError(f"{name} must be a non-negative integer")
        if not self.sectors:
            raise KiraConfigurationError("At least one reduction sector is required")


@dataclass(frozen=True, slots=True, kw_only=True)
class KiraProject:
    family: IntegralFamily
    kinematics: Kinematics
    targets: tuple[Expression, ...]
    bounds: ReductionBounds
    preferred_masters: tuple[Expression, ...] = ()
    check_masters: bool = False
    reconstruct_mass: bool = False
    target_file: str = "targets"

    def __post_init__(self) -> None:
        object.__setattr__(self, "targets", _expressions(self.targets))
        object.__setattr__(
            self, "preferred_masters", _expressions(self.preferred_masters)
        )
        object.__setattr__(
            self, "target_file", _plain_name(self.target_file, field_name="target_file")
        )
        if not self.targets:
            raise KiraConfigurationError("At least one target integral is required")
        if not isinstance(self.check_masters, bool):
            raise KiraConfigurationError("check_masters must be a bool")
        if not isinstance(self.reconstruct_mass, bool):
            raise KiraConfigurationError("reconstruct_mass must be a bool")

    def serialize(self) -> ProjectFiles:
        """Return the immutable deterministic collection of Kira input files."""

        from .serialization import serialize_project

        return serialize_project(self)


__all__ = [
    "IntegralFamily",
    "KinematicInvariant",
    "Kinematics",
    "KiraProject",
    "Propagator",
    "ReductionBounds",
    "ScalarProductRule",
]
