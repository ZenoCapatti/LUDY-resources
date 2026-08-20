"""Symbolica reduction results and independent completeness checks."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

from symbolica import E, Expression, Replacement, S

from .errors import IncompleteReductionError


def _walk(expression: Expression):
    yield expression
    try:
        arguments = tuple(expression)
    except (TypeError, ValueError):
        return
    for argument in arguments:
        yield from _walk(argument)


def _family_integrals(
    expression: Expression,
    *,
    family_name: str,
    arity: int,
) -> set[Expression]:
    result: set[Expression] = set()
    expected_head = str(S(family_name).get_name())
    for candidate in _walk(expression):
        try:
            name = str(candidate.get_name())
            arguments = tuple(candidate)
        except (TypeError, ValueError):
            continue
        if name == expected_head and len(arguments) == arity:
            result.add(candidate)
    return result


def _ordered(expressions) -> tuple[Expression, ...]:
    return tuple(
        sorted(set(expressions), key=lambda expression: expression.format_plain())
    )


@dataclass(frozen=True, slots=True)
class ReductionResult:
    """Parsed rules plus completeness information for one Kira run."""

    family_name: str
    arity: int
    requested_targets: tuple[Expression, ...]
    rules: Mapping[Expression, Expression]
    masters: tuple[Expression, ...]
    workdir: Path
    symbol_aliases: Mapping[str, Expression] = field(default_factory=dict)
    process_log: Path | None = None
    kira_log: Path | None = None
    missing_targets: tuple[Expression, ...] = field(init=False)
    unresolved_integrals: tuple[Expression, ...] = field(init=False)
    zero_integrals: tuple[Expression, ...] = field(init=False)

    def __post_init__(self) -> None:
        requested = tuple(self.requested_targets)
        masters = _ordered(self.masters)
        normalized_rules = dict(self.rules)
        for master in masters:
            normalized_rules.setdefault(master, master)

        missing = _ordered(
            target for target in requested if target not in normalized_rules
        )
        master_set = set(masters)
        unresolved: set[Expression] = set()
        for right in normalized_rules.values():
            unresolved.update(
                integral
                for integral in _family_integrals(
                    right,
                    family_name=self.family_name,
                    arity=self.arity,
                )
                if integral not in master_set
            )
        zeros = _ordered(
            left for left, right in normalized_rules.items() if right == E("0")
        )

        object.__setattr__(self, "requested_targets", requested)
        object.__setattr__(self, "masters", masters)
        object.__setattr__(self, "rules", MappingProxyType(normalized_rules))
        object.__setattr__(
            self,
            "symbol_aliases",
            MappingProxyType(dict(sorted(self.symbol_aliases.items()))),
        )
        object.__setattr__(self, "workdir", Path(self.workdir))
        if self.process_log is not None:
            object.__setattr__(self, "process_log", Path(self.process_log))
        if self.kira_log is not None:
            object.__setattr__(self, "kira_log", Path(self.kira_log))
        object.__setattr__(self, "missing_targets", missing)
        object.__setattr__(self, "unresolved_integrals", _ordered(unresolved))
        object.__setattr__(self, "zero_integrals", zeros)

    @property
    def requested(self) -> tuple[Expression, ...]:
        return self.requested_targets

    @property
    def complete(self) -> bool:
        return not self.missing_targets and not self.unresolved_integrals

    def require_complete(self) -> ReductionResult:
        if self.complete:
            return self
        details: list[str] = []
        if self.missing_targets:
            details.append(
                f"{len(self.missing_targets)} requested target(s) have no rule"
            )
        if self.unresolved_integrals:
            details.append(
                f"{len(self.unresolved_integrals)} right-hand-side integral(s) are not masters"
            )
        raise IncompleteReductionError(
            "Incomplete Kira reduction: " + "; ".join(details),
            missing_targets=self.missing_targets,
            unresolved_integrals=self.unresolved_integrals,
        )

    def apply(
        self, expression: Expression, *, allow_incomplete: bool = False
    ) -> Expression:
        """Apply all exact Kira rules simultaneously to *expression*."""

        if not allow_incomplete:
            self.require_complete()
        present = _family_integrals(
            expression,
            family_name=self.family_name,
            arity=self.arity,
        )
        unknown = _ordered(
            integral for integral in present if integral not in self.rules
        )
        if unknown and not allow_incomplete:
            raise IncompleteReductionError(
                f"Expression contains {len(unknown)} family integral(s) absent from this result",
                missing_targets=unknown,
            )
        replacements = [
            Replacement(left, right)
            for left, right in self.rules.items()
            if left != right
        ]
        if not replacements:
            return expression
        return expression.replace_multiple(replacements, repeat=False)


__all__ = ["ReductionResult"]
