"""Deterministic serialization of the public models to a Kira project."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType

import yaml
from symbolica import E, Expression, Replacement, S

from .errors import KiraConfigurationError
from .models import KiraProject


def _symbolica_atom(expression: Expression) -> Expression:
    """Unwrap structured Expression subclasses before atom introspection."""

    converter = getattr(expression, "to_expression", None)
    if not callable(converter):
        return expression
    converted = converter()
    return converted if isinstance(converted, Expression) else expression


def _basename(name: str) -> str:
    return name.rsplit("::", 1)[-1]


def _tags(expression: Expression) -> frozenset[str]:
    try:
        return frozenset(
            str(tag) for tag in _symbolica_atom(expression).get_tags()
        )
    except (TypeError, ValueError):
        return frozenset()


def _arguments(expression: Expression) -> tuple[Expression, ...]:
    try:
        return tuple(_symbolica_atom(expression))
    except (TypeError, ValueError):
        return ()


def _is_variable(expression: Expression) -> bool:
    return (
        str(_symbolica_atom(expression).get_type()).rsplit(".", 1)[-1]
        == "Var"
    )


def _integer(expression: Expression, *, context: str) -> int:
    try:
        value = int(expression.format_plain())
    except (TypeError, ValueError, OverflowError) as exc:
        raise KiraConfigurationError(f"{context} must be an integer") from exc
    if expression != E(str(value)):
        raise KiraConfigurationError(f"{context} must be an integer")
    return value


@dataclass(frozen=True, slots=True)
class _Momentum:
    expression: Expression
    name: str
    representation: str | None


class _MomentumAdapter:
    """Flatten rank-one Spenso vectors to Kira momentum identifiers."""

    def __init__(self, expressions: tuple[Expression, ...]) -> None:
        momenta: list[_Momentum] = []
        by_expression: dict[Expression, _Momentum] = {}
        by_name: dict[str, Expression] = {}
        representation: str | None = None

        for expression in expressions:
            if expression in by_expression:
                continue
            momentum = self._inspect(expression)
            previous = by_name.get(momentum.name)
            if previous is not None and previous != expression:
                raise KiraConfigurationError(
                    f"Momentum name collision for {momentum.name!r}: "
                    f"{previous.format_plain()} and {expression.format_plain()}"
                )
            if momentum.representation is not None:
                if representation is None:
                    representation = momentum.representation
                elif representation != momentum.representation:
                    raise KiraConfigurationError(
                        "All Spenso momenta in one Kira project must have compatible representations"
                    )
            by_name[momentum.name] = expression
            by_expression[expression] = momentum
            momenta.append(momentum)

        self._momenta = tuple(momenta)
        self._by_expression = by_expression

    @staticmethod
    def _inspect(expression: Expression) -> _Momentum:
        atom = _symbolica_atom(expression)
        if _is_variable(atom):
            name = _basename(str(atom.get_name()))
            _validate_identifier(name, context="momentum")
            return _Momentum(expression, name, None)

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
        labels = arguments[:-1]
        if len(labels) > 1:
            raise KiraConfigurationError(
                f"Spenso momentum {expression.format_plain()} has rank greater than one"
            )

        head = _basename(expression_name)
        _validate_identifier(head, context="Spenso momentum head")
        if labels:
            label = _integer(labels[0], context=f"label of {expression.format_plain()}")
            name = f"{head}{label}"
        else:
            name = head
        _validate_identifier(name, context="derived momentum")
        return _Momentum(expression, name, representations[0].format_plain())

    def name(self, expression: Expression) -> str:
        try:
            return self._by_expression[expression].name
        except KeyError as exc:
            raise KiraConfigurationError(
                f"Undeclared momentum {expression.format_plain()}"
            ) from exc

    def linear(self, expression: Expression) -> str:
        replacements = [
            Replacement(momentum.expression, S(momentum.name))
            for momentum in self._momenta
        ]
        converted = expression.replace_multiple(replacements, repeat=False)
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
        return frozenset(momentum.name for momentum in self._momenta)


class _InvariantAdapter:
    def __init__(
        self, project: KiraProject, *, forbidden_names: frozenset[str]
    ) -> None:
        self._names: dict[Expression, str] = {}
        self._explicit_aliases: dict[str, Expression] = {}
        claimed = set(forbidden_names)
        for invariant in project.kinematics.kinematic_invariants:
            expression = invariant.expression
            if expression in self._names:
                raise KiraConfigurationError(
                    f"Duplicate kinematic invariant {expression.format_plain()}"
                )
            if invariant.kira_name is not None:
                name = invariant.kira_name
                self._explicit_aliases[name] = expression
            elif _is_variable(expression):
                name = _basename(str(expression.get_name()))
                _validate_identifier(name, context="kinematic invariant")
            else:
                raise KiraConfigurationError(
                    f"Composite invariant {expression.format_plain()} needs kira_name"
                )
            if name in claimed:
                raise KiraConfigurationError(
                    f"Kira identifier {name!r} is used by more than one momentum or invariant"
                )
            claimed.add(name)
            self._names[expression] = name

    def name(self, expression: Expression) -> str:
        try:
            return self._names[expression]
        except KeyError as exc:
            raise KiraConfigurationError(
                f"Undeclared kinematic invariant {expression.format_plain()}"
            ) from exc

    def scalar(self, expression: Expression, *, context: str) -> str:
        replacements = [
            Replacement(source, S(name)) for source, name in self._names.items()
        ]
        converted = (
            expression.replace_multiple(replacements, repeat=False)
            if replacements
            else expression
        )
        unknown = sorted(
            {
                _basename(str(candidate.get_name()))
                for candidate in _walk(converted)
                if _is_variable(candidate)
            }
            - set(self._names.values())
            - {"d"}
        )
        if unknown:
            raise KiraConfigurationError(
                f"{context} contains undeclared scalar symbol(s): {', '.join(unknown)}"
            )
        return _scalar(converted, context=context)

    @property
    def explicit_aliases(self) -> Mapping[str, Expression]:
        return MappingProxyType(dict(sorted(self._explicit_aliases.items())))


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


def _scalar(expression: Expression, *, context: str) -> str:
    plain = expression.format_plain()
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
    if _basename(str(expression.get_name())) != project.family.name:
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


def integral_text(expression: Expression, project: KiraProject) -> str:
    _family_integral(expression, project)
    return expression.to_mathematica(show_namespaces=False)


def _yaml(data: object) -> str:
    return yaml.safe_dump(
        data,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=False,
        width=120,
    )


@dataclass(frozen=True, slots=True)
class ProjectFiles(Mapping[str, str]):
    """Immutable, path-sorted collection of generated project files."""

    _items: tuple[tuple[str, str], ...]
    _invariant_aliases: tuple[tuple[str, str], ...] = ()

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
    def invariant_aliases(self) -> Mapping[str, str]:
        """Map Kira-only names to original Mathematica-form expressions."""

        return MappingProxyType(dict(self._invariant_aliases))


def serialize_project(project: KiraProject) -> ProjectFiles:
    """Serialize *project* to deterministic Kira input files."""

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

    declared_momenta = (
        project.family.loop_momenta
        + project.kinematics.incoming_momenta
        + project.kinematics.outgoing_momenta
    )
    adapter = _MomentumAdapter(declared_momenta)
    invariants = _InvariantAdapter(project, forbidden_names=adapter.names)
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

    family: dict[str, object] = {
        "name": project.family.name,
        "loop_momenta": [
            adapter.name(momentum) for momentum in project.family.loop_momenta
        ],
        "top_level_sectors": [
            _sector(sector, width=width) for sector in project.family.top_level_sectors
        ],
        "propagators": [
            [
                adapter.linear(propagator.momentum),
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
            adapter.name(momentum) for momentum in project.kinematics.incoming_momenta
        ],
        "outgoing_momenta": [
            adapter.name(momentum) for momentum in project.kinematics.outgoing_momenta
        ],
        "kinematic_invariants": [
            [
                invariants.name(invariant.expression),
                invariant.mass_dimension,
            ]
            for invariant in project.kinematics.kinematic_invariants
        ],
        "scalarproduct_rules": [
            [
                [adapter.linear(rule.left), adapter.linear(rule.right)],
                invariants.scalar(rule.value, context="scalar-product value"),
            ]
            for rule in project.kinematics.scalar_products
        ],
    }
    if project.kinematics.momentum_conservation is not None:
        left, right = project.kinematics.momentum_conservation
        kinematics["momentum_conservation"] = [
            adapter.linear(left),
            adapter.linear(right),
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
            "select_mandatory_list": [[project.family.name, project.target_file]]
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
        "target": [[project.family.name, project.target_file]],
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
            f"{integral_text(target, project)}\n" for target in project.targets
        ),
    }
    if project.preferred_masters:
        files["preferred_masters"] = "".join(
            f"{integral_text(master, project)}\n"
            for master in project.preferred_masters
        )
    aliases = tuple(
        sorted(
            (
                name,
                expression.to_mathematica(show_namespaces=False),
            )
            for name, expression in invariants.explicit_aliases.items()
        )
    )
    return ProjectFiles(tuple(sorted(files.items())), aliases)


__all__ = ["ProjectFiles", "integral_text", "serialize_project"]
