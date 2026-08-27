"""Deterministic serialization of native Symbolica projects to Kira text."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, cast

import yaml
from symbolica import E, Expression, Replacement, S

from .errors import KiraConfigurationError
from .models import KiraProject

_ALIAS_DOMAIN = b"kirapy/alias/v1\0"
_ALIAS_TAG = "kirapy::alias"
_ALIAS_DATA_PREFIX = "kirapy::"
_ALIAS_PREFIX = {
    "family": "kp_f_",
    "momentum": "kp_m_",
}
_FERMAT_IDENTIFIER_LIMIT = 10
_FERMAT_ALIAS_PREFIX = "s"
_BASE36_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
_FERMAT_ALIAS_PAYLOAD_LENGTH = _FERMAT_IDENTIFIER_LIMIT - len(
    _FERMAT_ALIAS_PREFIX
)
_FERMAT_ALIAS_MODULUS = len(_BASE36_ALPHABET) ** _FERMAT_ALIAS_PAYLOAD_LENGTH


def _symbolica_atom(expression: Expression) -> Expression:
    """Unwrap structured Expression subclasses before serialization."""

    converter = getattr(expression, "to_expression", None)
    if not callable(converter):
        return expression
    converted = converter()
    return converted if isinstance(converted, Expression) else expression


def _basename(name: str) -> str:
    return name.rsplit("::", 1)[-1]


def _tags(expression: Expression) -> frozenset[str]:
    try:
        return frozenset(str(tag) for tag in _symbolica_atom(expression).get_tags())
    except (TypeError, ValueError):
        return frozenset()


def _arguments(expression: Expression) -> tuple[Expression, ...]:
    try:
        return tuple(_symbolica_atom(expression))
    except (TypeError, ValueError):
        return ()


def _is_variable(expression: Expression) -> bool:
    return str(_symbolica_atom(expression).get_type()).rsplit(".", 1)[-1] == "Var"


def _integer(expression: Expression, *, context: str) -> int:
    try:
        value = int(expression.format_plain())
    except (TypeError, ValueError, OverflowError) as exc:
        raise KiraConfigurationError(f"{context} must be an integer") from exc
    if expression != E(str(value)):
        raise KiraConfigurationError(f"{context} must be an integer")
    return value


def _alias_digest(kind: str, original: Expression) -> str:
    canonical = _symbolica_atom(original).to_canonical_string().encode("utf-8")
    return hashlib.sha256(
        _ALIAS_DOMAIN + kind.encode("ascii") + b"\0" + canonical
    ).hexdigest()


def _base36(value: int, *, width: int) -> str:
    digits: list[str] = []
    for _ in range(width):
        value, remainder = divmod(value, len(_BASE36_ALPHABET))
        digits.append(_BASE36_ALPHABET[remainder])
    if value:
        raise ValueError(f"Value does not fit in {width} base-36 digits")
    return "".join(reversed(digits))


def _alias_wire_name(kind: str, digest: str) -> str:
    """Derive the Kira identifier while retaining ``digest`` as its identity."""

    if kind == "dimension":
        return "d"
    if kind == "invariant":
        payload = _base36(
            int(digest, 16) % _FERMAT_ALIAS_MODULUS,
            width=_FERMAT_ALIAS_PAYLOAD_LENGTH,
        )
        return f"{_FERMAT_ALIAS_PREFIX}{payload}"
    try:
        prefix = _ALIAS_PREFIX[kind]
    except KeyError as exc:
        raise KiraConfigurationError(f"Unsupported alias kind {kind!r}") from exc
    return f"{prefix}{digest}"


def _is_reserved_wire_name(name: str) -> bool:
    if name.startswith("kp_"):
        return True
    return (
        len(name) == _FERMAT_IDENTIFIER_LIMIT
        and name.startswith(_FERMAT_ALIAS_PREFIX)
        and all(character in _BASE36_ALPHABET for character in name[1:])
    )


@dataclass(frozen=True, slots=True)
class _SymbolAlias:
    """One native expression and the identifier used for it at the Kira boundary."""

    kind: str
    digest: str
    wire_name: str
    original: Expression
    wire: Expression

    def manifest_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "digest": self.digest,
            "wire_name": self.wire_name,
        }


def _make_symbol_alias(
    kind: str,
    original: Expression,
    *,
    expected_digest: str | None = None,
    expected_wire_name: str | None = None,
) -> _SymbolAlias:
    """Create and validate the immutable Symbolica symbol for one Kira alias."""

    original = _symbolica_atom(original)
    digest = _alias_digest(kind, original)
    if expected_digest is not None and digest != expected_digest:
        raise KiraConfigurationError(
            f"Digest mismatch for restored {kind} expression {original.format_plain()}"
        )

    wire_name = _alias_wire_name(kind, digest)
    if kind == "dimension":
        wire = S(wire_name)
        if wire.format_plain() != wire_name:
            raise KiraConfigurationError(
                "Kira's reserved dimension symbol d does not render as its wire name"
            )
    else:
        metadata: dict[str | int | Expression, Any] = {
            f"{_ALIAS_DATA_PREFIX}original": original,
            f"{_ALIAS_DATA_PREFIX}kind": kind,
            f"{_ALIAS_DATA_PREFIX}digest": digest,
        }
        try:
            wire = S(wire_name, tags=[_ALIAS_TAG], data=metadata)
        except (TypeError, ValueError) as exc:
            raise KiraConfigurationError(
                f"Kira alias {wire_name!r} was already registered with incompatible metadata"
            ) from exc
        try:
            actual_data = wire.get_symbol_data()
            actual_tags = frozenset(str(tag) for tag in wire.get_tags())
        except (TypeError, ValueError) as exc:
            raise KiraConfigurationError(
                f"Cannot inspect metadata for Kira alias {wire_name!r}"
            ) from exc
        if _ALIAS_TAG not in actual_tags or actual_data != metadata:
            raise KiraConfigurationError(
                f"Kira alias {wire_name!r} has incompatible metadata"
            )
        if wire.format_plain() != wire_name:
            raise KiraConfigurationError(
                f"Kira alias {wire_name!r} does not render as its wire name"
            )

    if expected_wire_name is not None and wire_name != expected_wire_name:
        raise KiraConfigurationError(
            f"Wire-name mismatch for restored {kind} expression: "
            f"expected {expected_wire_name!r}, computed {wire_name!r}"
        )
    return _SymbolAlias(kind, digest, wire_name, original, wire)


class _AliasRegistry:
    """The complete, ordered native-to-wire mapping for one project."""

    def __init__(self, project: KiraProject) -> None:
        records: list[_SymbolAlias] = []
        by_key: dict[tuple[str, Expression], _SymbolAlias] = {}
        by_wire_name: dict[str, _SymbolAlias] = {}

        def add(kind: str, expression: Expression) -> _SymbolAlias:
            original = _symbolica_atom(expression)
            for candidate in _walk(original):
                try:
                    name = _basename(str(candidate.get_name()))
                except (TypeError, ValueError):
                    continue
                if _is_reserved_wire_name(name):
                    raise KiraConfigurationError(
                        f"Native {kind} expressions cannot use reserved Kira wire names: {name}"
                    )
            key = (kind, original)
            existing = by_key.get(key)
            if existing is not None:
                return existing
            digest = _alias_digest(kind, original)
            wire_name = _alias_wire_name(kind, digest)
            colliding = by_wire_name.get(wire_name)
            if colliding is not None:
                raise KiraConfigurationError(
                    f"Kira wire-name collision {wire_name!r} between full digests "
                    f"{colliding.digest} and {digest}"
                )
            alias = _make_symbol_alias(kind, original)
            records.append(alias)
            by_key[key] = alias
            by_wire_name[alias.wire_name] = alias
            return alias

        self.family = add("family", S(project.family.name))
        declared_momenta = (
            project.family.loop_momenta
            + project.kinematics.incoming_momenta
            + project.kinematics.outgoing_momenta
        )
        for momentum in declared_momenta:
            add("momentum", momentum)
        for invariant in project.kinematics.kinematic_invariants:
            add("invariant", invariant.expression)
        self.dimension = add("dimension", project.dimension)

        if any(
            _symbolica_atom(invariant.expression) == self.dimension.original
            for invariant in project.kinematics.kinematic_invariants
        ):
            raise KiraConfigurationError(
                "The project dimension cannot also be a kinematic invariant"
            )
        if self.dimension.original != self.dimension.wire and bool(
            self.dimension.original.contains(self.dimension.wire)
        ):
            raise KiraConfigurationError(
                "A custom project dimension cannot contain Kira's reserved d symbol"
            )
        if any(
            self.dimension.original != self.dimension.wire
            and bool(
                self.dimension.original.contains(
                    _symbolica_atom(invariant.expression)
                )
            )
            for invariant in project.kinematics.kinematic_invariants
        ):
            raise KiraConfigurationError(
                "A custom project dimension cannot contain a kinematic invariant"
            )

        self.records = tuple(records)
        self._by_key = by_key

    def get(self, kind: str, expression: Expression) -> _SymbolAlias:
        try:
            return self._by_key[(kind, _symbolica_atom(expression))]
        except KeyError as exc:
            raise KiraConfigurationError(
                f"Undeclared {kind} expression {expression.format_plain()}"
            ) from exc


@dataclass(frozen=True, slots=True)
class _Momentum:
    expression: Expression
    representation: str | None


class _MomentumAdapter:
    """Validate momenta and flatten rank-one Spenso vectors to wire aliases."""

    def __init__(
        self,
        expressions: tuple[Expression, ...],
        registry: _AliasRegistry | None = None,
    ) -> None:
        momenta: list[_Momentum] = []
        by_expression: dict[Expression, _Momentum] = {}
        representation: str | None = None

        for raw_expression in expressions:
            expression = _symbolica_atom(raw_expression)
            if expression in by_expression:
                continue
            momentum = self._inspect(expression)
            if momentum.representation is not None:
                if representation is None:
                    representation = momentum.representation
                elif representation != momentum.representation:
                    raise KiraConfigurationError(
                        "All Spenso momenta in one Kira project must have compatible representations"
                    )
            by_expression[expression] = momentum
            momenta.append(momentum)

        self._momenta = tuple(momenta)
        self._by_expression = by_expression
        self._registry = registry

    @staticmethod
    def _inspect(expression: Expression) -> _Momentum:
        atom = _symbolica_atom(expression)
        if _is_variable(atom):
            return _Momentum(atom, None)

        expression_name = str(atom.get_name())
        if "spenso::tensor" not in _tags(atom) and not expression_name.startswith(
            "spenso_python::"
        ):
            raise KiraConfigurationError(
                "A momentum must be a bare Symbolica symbol or a rank-one Spenso tensor placeholder"
            )

        arguments = _arguments(atom)
        representations = []
        for argument in arguments:
            try:
                argument_name = str(argument.get_name())
            except (TypeError, ValueError):
                argument_name = ""
            if "spenso::representation" in _tags(argument) or argument_name.startswith(
                "spenso::"
            ):
                representations.append(argument)
        if len(representations) != 1 or arguments[-1:] != tuple(representations):
            raise KiraConfigurationError(
                f"Spenso momentum {expression.format_plain()} needs exactly one final representation"
            )
        if len(arguments[:-1]) > 1:
            raise KiraConfigurationError(
                f"Spenso momentum {expression.format_plain()} has rank greater than one"
            )
        if arguments[:-1]:
            _integer(arguments[0], context=f"label of {expression.format_plain()}")
        return _Momentum(atom, representations[0].format_plain())

    def _alias(self, expression: Expression) -> _SymbolAlias:
        if self._registry is None:
            raise KiraConfigurationError(
                "Momentum wire aliases require a complete project registry"
            )
        return self._registry.get("momentum", expression)

    def name(self, expression: Expression) -> str:
        normalized = _symbolica_atom(expression)
        if normalized not in self._by_expression:
            raise KiraConfigurationError(
                f"Undeclared momentum {expression.format_plain()}"
            )
        return self._alias(normalized).wire_name

    def linear(self, expression: Expression) -> str:
        replacements = [
            Replacement(momentum.expression, self._alias(momentum.expression).wire)
            for momentum in self._momenta
        ]
        converted = _symbolica_atom(expression).replace_multiple(
            replacements, repeat=False
        )
        self._validate_linear(converted)
        plain = _ordered_sum_plain(converted)
        if "::" in plain:
            raise KiraConfigurationError(
                f"Momentum expression was not fully flattened for Kira: {plain}"
            )
        return plain

    def _validate_linear(self, expression: Expression) -> None:
        names = self.names

        def degrees(candidate: Expression) -> set[int]:
            if _is_variable(candidate):
                name = _basename(str(candidate.get_name()))
                if name not in names:
                    raise KiraConfigurationError(
                        f"Undeclared momentum {candidate.format_plain()} in momentum expression"
                    )
                return {1}
            arguments = _arguments(candidate)
            if not arguments:
                return {0}
            atom_type = str(candidate.get_type()).rsplit(".", 1)[-1]
            if atom_type == "Add":
                result: set[int] = set()
                for argument in arguments:
                    result.update(degrees(argument))
                return result
            if atom_type == "Mul":
                result = {0}
                for argument in arguments:
                    result = {
                        left + right for left in result for right in degrees(argument)
                    }
                    if any(degree > 1 for degree in result):
                        raise KiraConfigurationError("Kira momenta must be linear")
                return result
            nested = set().union(*(degrees(argument) for argument in arguments))
            if any(degree > 0 for degree in nested):
                raise KiraConfigurationError("Kira momenta must be linear")
            raise KiraConfigurationError(
                f"Unsupported function in momentum expression {candidate.format_plain()}"
            )

        degrees(expression)

    @property
    def names(self) -> frozenset[str]:
        if self._registry is None:
            return frozenset()
        return frozenset(
            self._alias(momentum.expression).wire_name for momentum in self._momenta
        )


class _InvariantAdapter:
    def __init__(self, project: KiraProject, registry: _AliasRegistry) -> None:
        self._registry = registry
        self._names = {
            _symbolica_atom(invariant.expression): registry.get(
                "invariant", invariant.expression
            )
            for invariant in project.kinematics.kinematic_invariants
        }
        if len(self._names) != len(project.kinematics.kinematic_invariants):
            raise KiraConfigurationError("Duplicate kinematic invariant")

    def name(self, expression: Expression) -> str:
        try:
            return self._names[_symbolica_atom(expression)].wire_name
        except KeyError as exc:
            raise KiraConfigurationError(
                f"Undeclared kinematic invariant {expression.format_plain()}"
            ) from exc

    def scalar(self, expression: Expression, *, context: str) -> str:
        replacements = [
            Replacement(source, alias.wire) for source, alias in self._names.items()
        ]
        dimension = self._registry.dimension
        converted = _symbolica_atom(expression)
        if replacements:
            converted = converted.replace_multiple(replacements, repeat=False)
        if dimension.original != dimension.wire:
            if bool(converted.contains(dimension.wire)):
                raise KiraConfigurationError(
                    f"{context} contains Kira's reserved d symbol outside the "
                    "declared project dimension"
                )
            converted = converted.replace_multiple(
                [Replacement(dimension.original, dimension.wire)], repeat=False
            )
        allowed_variables = {
            str(alias.wire.get_name()) for alias in self._names.values()
        } | {str(dimension.wire.get_name())}
        unknown = sorted(
            {
                candidate.format_plain()
                for candidate in _walk(converted)
                if _is_variable(candidate)
                and str(candidate.get_name()) not in allowed_variables
            }
        )
        if unknown:
            raise KiraConfigurationError(
                f"{context} contains undeclared scalar symbol(s): {', '.join(unknown)}"
            )
        functions = sorted(
            {
                candidate.format_plain()
                for candidate in _walk(converted)
                if str(candidate.get_type()).rsplit(".", 1)[-1] == "Fn"
            }
        )
        if functions:
            raise KiraConfigurationError(
                f"{context} contains unsupported scalar function(s): "
                f"{', '.join(functions)}"
            )
        return _scalar(converted, context=context)


def _validate_identifier(name: str, *, context: str) -> None:
    if not name or not (name[0].isalpha() or name[0] == "_"):
        raise KiraConfigurationError(f"Invalid {context} identifier {name!r}")
    if not all(character.isalnum() or character == "_" for character in name):
        raise KiraConfigurationError(f"Invalid {context} identifier {name!r}")


def _walk(expression: Expression):
    yield expression
    for argument in _arguments(expression):
        yield from _walk(argument)


def _ordered_sum_plain(expression: Expression) -> str:
    """Use Kira's conventional lexical ordering for additive momentum terms."""

    if str(expression.get_type()).rsplit(".", 1)[-1] != "Add":
        return expression.format_plain()
    terms = [term.format_plain() for term in _arguments(expression)]
    terms.sort(key=lambda term: term.lstrip("-"))
    if not terms:
        return "0"
    return terms[0] + "".join(
        term if term.startswith("-") else f"+{term}" for term in terms[1:]
    )


def _atom_type(expression: Expression) -> str:
    return str(expression.get_type()).rsplit(".", 1)[-1]


def _scalar_order_key(expression: Expression) -> str:
    """Order commutative children independently of symbol registration order."""

    return expression.to_canonical_string()


def _negative_integer_power(expression: Expression) -> int | None:
    if _atom_type(expression) != "Pow":
        return None
    _, exponent = tuple(expression)
    try:
        value = int(exponent.format_plain())
    except (TypeError, ValueError, OverflowError):
        return None
    return value if value < 0 and exponent == E(str(value)) else None


def _scalar_plain(expression: Expression, *, parent_precedence: int = 0) -> str:
    """Format rational scalar algebra with canonical Add/Mul ordering.

    Symbolica's ordinary printer follows internal symbol registration order.
    That order may legitimately differ after serializing several projects in
    one process, which used to change Kira input hashes for algebraically
    identical expressions.  Kira scalars are restricted above to rational
    algebra, so a small precedence-aware printer is sufficient here.
    """

    atom_type = _atom_type(expression)
    if atom_type in {"Num", "Var"}:
        return expression.format_plain()

    arguments = tuple(expression)
    if atom_type == "Add":
        parts = [
            _scalar_plain(argument, parent_precedence=1)
            for argument in sorted(arguments, key=_scalar_order_key)
        ]
        plain = parts[0] + "".join(
            part if part.startswith("-") else f"+{part}"
            for part in parts[1:]
        )
        return f"({plain})" if parent_precedence > 1 else plain

    if atom_type == "Mul":
        numbers = [
            argument for argument in arguments if _atom_type(argument) == "Num"
        ]
        factors = [
            argument for argument in arguments if _atom_type(argument) != "Num"
        ]
        numerator = sorted(
            (
                factor
                for factor in factors
                if _negative_integer_power(factor) is None
            ),
            key=_scalar_order_key,
        )
        denominator = sorted(
            (
                factor
                for factor in factors
                if _negative_integer_power(factor) is not None
            ),
            key=_scalar_order_key,
        )

        coefficient = numbers[0].format_plain() if numbers else ""
        numerator_parts: list[str] = []
        if coefficient and (
            coefficient not in {"1", "-1"} or not numerator
        ):
            numerator_parts.append(coefficient)
        elif coefficient == "-1":
            numerator_parts.append("-")
        numerator_parts.extend(
            _scalar_plain(factor, parent_precedence=2)
            for factor in numerator
        )
        if numerator_parts == ["-"]:
            plain = "-1"
        elif numerator_parts and numerator_parts[0] == "-":
            plain = "-" + "*".join(numerator_parts[1:])
        else:
            plain = "*".join(numerator_parts) if numerator_parts else "1"

        denominator_parts: list[str] = []
        for factor in denominator:
            base, _ = tuple(factor)
            power = -cast(int, _negative_integer_power(factor))
            base_plain = _scalar_plain(base, parent_precedence=3)
            denominator_parts.append(
                base_plain if power == 1 else f"{base_plain}^{power}"
            )
        if denominator_parts:
            denominator_plain = "*".join(denominator_parts)
            if len(denominator_parts) > 1:
                denominator_plain = f"({denominator_plain})"
            plain = f"{plain}/{denominator_plain}"
        return f"({plain})" if parent_precedence > 2 else plain

    if atom_type == "Pow":
        base, exponent = arguments
        base_plain = _scalar_plain(base, parent_precedence=3)
        exponent_plain = _scalar_plain(exponent)
        if _atom_type(exponent) in {"Add", "Mul"} or exponent_plain.startswith("-"):
            exponent_plain = f"({exponent_plain})"
        plain = f"{base_plain}^{exponent_plain}"
        return f"({plain})" if parent_precedence > 3 else plain

    raise KiraConfigurationError(
        f"Unsupported rational scalar atom {expression.format_plain()}"
    )


def _scalar(expression: Expression, *, context: str) -> str:
    plain = _scalar_plain(expression)
    if "::" in plain:
        raise KiraConfigurationError(
            f"{context} contains a namespaced function unsupported by Kira"
        )
    return plain


def _sector(value: int, *, width: int) -> str:
    if value <= 0 or value >= 1 << width:
        raise KiraConfigurationError(
            f"Sector {value} does not fit a family with {width} propagators"
        )
    return f"b{value:0{width}b}"


def _family_integral(expression: Expression, project: KiraProject) -> tuple[int, ...]:
    expression = _symbolica_atom(expression)
    if str(expression.get_name()) != str(S(project.family.name).get_name()):
        raise KiraConfigurationError(
            f"Expected an integral in family {project.family.name}, got {expression.format_plain()}"
        )
    arguments = _arguments(expression)
    if len(arguments) != project.family.arity:
        raise KiraConfigurationError(
            f"Integral {expression.format_plain()} has {len(arguments)} indices; "
            f"{project.family.arity} are required"
        )
    return tuple(_integer(argument, context="integral index") for argument in arguments)


def _integral_text(
    expression: Expression,
    project: KiraProject,
    registry: _AliasRegistry,
) -> str:
    indices = _family_integral(expression, project)
    arguments = ",".join(str(index) for index in indices)
    return f"{registry.family.wire_name}[{arguments}]"


def integral_text(expression: Expression, project: KiraProject) -> str:
    """Serialize one logical family integral using its deterministic wire head."""

    return _integral_text(expression, project, _AliasRegistry(project))


def _yaml(data: object) -> str:
    return yaml.safe_dump(
        data,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=False,
        width=160,
    )


@dataclass(frozen=True, slots=True)
class ProjectFiles(Mapping[str, str]):
    """Immutable generated files plus the native expressions behind wire names."""

    _items: tuple[tuple[str, str], ...]
    _alias_records: tuple[_SymbolAlias, ...]

    def __getitem__(self, key: str) -> str:
        for candidate, contents in self._items:
            if candidate == key:
                return contents
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return (path for path, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def as_mapping(self) -> Mapping[str, str]:
        return MappingProxyType(dict(self._items))

    @property
    def symbol_aliases(self) -> Mapping[str, Expression]:
        return MappingProxyType(
            {record.wire_name: record.original for record in self._alias_records}
        )


def serialize_project(project: KiraProject) -> ProjectFiles:
    """Serialize *project* to deterministic Kira input files."""

    if not project.targets:
        raise KiraConfigurationError("A Kira project needs at least one target")
    if project.check_masters and not project.preferred_masters:
        raise KiraConfigurationError("check_masters requires preferred_masters")
    if len(set(project.family.cut_propagators)) != len(project.family.cut_propagators):
        raise KiraConfigurationError("cut_propagators cannot contain duplicates")
    if any(
        index < 1 or index > project.family.arity
        for index in project.family.cut_propagators
    ):
        raise KiraConfigurationError(
            f"cut_propagators must use 1-based positions from 1 through {project.family.arity}"
        )

    registry = _AliasRegistry(project)
    declared_momenta = (
        project.family.loop_momenta
        + project.kinematics.incoming_momenta
        + project.kinematics.outgoing_momenta
    )
    momenta = _MomentumAdapter(declared_momenta, registry)
    invariants = _InvariantAdapter(project, registry)
    width = project.family.arity
    for reduction_sector in project.bounds.sectors:
        _sector(reduction_sector, width=width)
    for target in project.targets:
        indices = _family_integral(target, project)
        target_sector = sum(
            1 << position for position, index in enumerate(indices) if index > 0
        )
        if not any(
            target_sector & ~reduction_sector == 0
            for reduction_sector in project.bounds.sectors
        ):
            raise KiraConfigurationError(
                f"Target {target.format_plain()} is outside the requested reduction sectors"
            )

    wire_family = registry.family.wire_name
    family: dict[str, object] = {
        "name": wire_family,
        "loop_momenta": [
            momenta.name(momentum) for momentum in project.family.loop_momenta
        ],
        "top_level_sectors": [
            _sector(sector, width=width) for sector in project.family.top_level_sectors
        ],
        "propagators": [
            [
                momenta.linear(propagator.momentum),
                invariants.scalar(propagator.mass_squared, context="propagator mass"),
            ]
            for propagator in project.family.propagators
        ],
    }
    if project.family.cut_propagators:
        family["cut_propagators"] = list(project.family.cut_propagators)
    if project.family.zero_sectors:
        family["zero_sectors"] = [
            _sector(sector, width=width) for sector in project.family.zero_sectors
        ]

    kinematics: dict[str, object] = {
        "incoming_momenta": [
            momenta.name(momentum)
            for momentum in project.kinematics.incoming_momenta
        ],
        "outgoing_momenta": [
            momenta.name(momentum)
            for momentum in project.kinematics.outgoing_momenta
        ],
        "kinematic_invariants": [
            [invariants.name(invariant.expression), invariant.mass_dimension]
            for invariant in project.kinematics.kinematic_invariants
        ],
        "scalarproduct_rules": [
            [
                [momenta.linear(rule.left), momenta.linear(rule.right)],
                invariants.scalar(rule.value, context="scalar-product value"),
            ]
            for rule in project.kinematics.scalar_products
        ],
    }
    if project.kinematics.momentum_conservation is not None:
        left, right = project.kinematics.momentum_conservation
        kinematics["momentum_conservation"] = [
            momenta.linear(left),
            momenta.linear(right),
        ]
    if project.kinematics.symbol_to_replace_by_one is not None:
        kinematics["symbol_to_replace_by_one"] = invariants.name(
            project.kinematics.symbol_to_replace_by_one
        )

    reduction: dict[str, object] = {
        "reduce": [
            {
                "sectors": [
                    _sector(sector, width=width) for sector in project.bounds.sectors
                ],
                "r": project.bounds.r,
                "s": project.bounds.s,
                "d": project.bounds.d,
            }
        ],
        "select_integrals": {
            "select_mandatory_list": [[wire_family, project.target_file]]
        },
    }
    if project.preferred_masters:
        reduction["preferred_masters"] = "preferred_masters"
    if project.check_masters:
        reduction["check_masters"] = True
    reduction.update(
        {
            "run_initiate": True,
            "run_triangular": True,
            "run_back_substitution": True,
        }
    )

    exporter: dict[str, object] = {
        "target": [[wire_family, project.target_file]],
    }
    if project.reconstruct_mass:
        exporter["reconstruct_mass"] = True

    files = {
        "config/integralfamilies.yaml": _yaml({"integralfamilies": [family]}),
        "config/kinematics.yaml": _yaml({"kinematics": kinematics}),
        "jobs.yaml": _yaml(
            {"jobs": [{"reduce_sectors": reduction}, {"kira2math": exporter}]}
        ),
        project.target_file: "".join(
            f"{_integral_text(target, project, registry)}\n"
            for target in project.targets
        ),
    }
    if project.preferred_masters:
        files["preferred_masters"] = "".join(
            f"{_integral_text(master, project, registry)}\n"
            for master in project.preferred_masters
        )
    return ProjectFiles(tuple(sorted(files.items())), registry.records)


__all__ = ["ProjectFiles", "integral_text", "serialize_project"]
