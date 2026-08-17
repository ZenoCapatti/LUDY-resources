"""Parsers for Kira's Mathematica exporter and master-integral list."""

from __future__ import annotations

from pathlib import Path

from symbolica import E, Expression, ParseMode

from .errors import KiraParseError


def _without_mathematica_comments(text: str) -> str:
    output: list[str] = []
    depth = 0
    index = 0
    while index < len(text):
        pair = text[index : index + 2]
        if pair == "(*":
            depth += 1
            index += 2
            continue
        if pair == "*)" and depth:
            depth -= 1
            index += 2
            continue
        if depth == 0:
            output.append(text[index])
        index += 1
    if depth:
        raise KiraParseError("Unterminated Mathematica comment in kira2math output")
    return "".join(output)


def _scan_top_level(text: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    start = 0
    stack: list[str] = []
    quote: str | None = None
    escaped = False
    pairs = {"]": "[", ")": "(", "}": "{"}

    for index, character in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
            continue
        if character in "[({":
            stack.append(character)
            continue
        if character in "]) }".replace(" ", ""):
            if not stack or stack.pop() != pairs[character]:
                raise KiraParseError("Unbalanced delimiters in kira2math output")
            continue
        if character == delimiter and not stack:
            parts.append(text[start:index].strip())
            start = index + 1
    if quote is not None or stack:
        raise KiraParseError("Unbalanced delimiters in kira2math output")
    parts.append(text[start:].strip())
    return parts


def _split_rule(text: str) -> tuple[str, str]:
    stack: list[str] = []
    quote: str | None = None
    escaped = False
    pairs = {"]": "[", ")": "(", "}": "{"}
    arrow: int | None = None
    index = 0
    while index < len(text):
        character = text[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            index += 1
            continue
        if character in {'"', "'"}:
            quote = character
        elif character in "[({":
            stack.append(character)
        elif character in "]) }".replace(" ", ""):
            if not stack or stack.pop() != pairs[character]:
                raise KiraParseError("Unbalanced delimiters in kira2math rule")
        elif not stack and text[index : index + 2] == "->":
            if arrow is not None:
                raise KiraParseError(f"Multiple top-level arrows in rule: {text}")
            arrow = index
            index += 1
        index += 1
    if arrow is None:
        raise KiraParseError(f"Missing top-level arrow in rule: {text}")
    left, right = text[:arrow].strip(), text[arrow + 2 :].strip()
    if not left or not right:
        raise KiraParseError(f"Empty side in rule: {text}")
    return left, right


def _parse_expression(text: str, *, context: str) -> Expression:
    try:
        return E(text, ParseMode.Mathematica)
    except Exception as exc:
        raise KiraParseError(f"Cannot parse {context}: {text}") from exc


def _basename(name: str) -> str:
    return name.rsplit("::", 1)[-1]


def _arguments(expression: Expression) -> tuple[Expression, ...]:
    try:
        return tuple(expression)
    except (TypeError, ValueError):
        return ()


def _walk(expression: Expression):
    yield expression
    for argument in _arguments(expression):
        yield from _walk(argument)


def _validate_integral(
    expression: Expression,
    *,
    family_name: str,
    arity: int,
    context: str,
) -> None:
    try:
        name = _basename(str(expression.get_name()))
        arguments = tuple(expression)
    except (TypeError, ValueError) as exc:
        raise KiraParseError(
            f"{context} is not a family integral: {expression.format_plain()}"
        ) from exc
    if name != family_name or len(arguments) != arity:
        raise KiraParseError(
            f"{context} is not a {family_name} integral of arity {arity}: "
            f"{expression.format_plain()}"
        )
    for argument in arguments:
        try:
            value = int(argument.format_plain())
        except (TypeError, ValueError, OverflowError) as exc:
            raise KiraParseError(
                f"Non-integer integral index in {expression.format_plain()}"
            ) from exc
        if argument != E(str(value)):
            raise KiraParseError(
                f"Non-integer integral index in {expression.format_plain()}"
            )


def _is_family_call(expression: Expression, *, family_name: str) -> bool:
    try:
        return _basename(str(expression.get_name())) == family_name
    except (TypeError, ValueError):
        return False


def _validate_rhs(
    expression: Expression,
    *,
    family_name: str,
    arity: int,
) -> None:
    for candidate in _walk(expression):
        if _is_family_call(candidate, family_name=family_name):
            _validate_integral(
                candidate,
                family_name=family_name,
                arity=arity,
                context="Right-hand-side family call",
            )

    def degrees(candidate: Expression) -> set[int]:
        if _is_family_call(candidate, family_name=family_name):
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
                    raise KiraParseError(
                        "Nonlinear product of family integrals in rule right-hand side"
                    )
            return result
        nested_degrees = set().union(*(degrees(argument) for argument in arguments))
        if any(degree > 0 for degree in nested_degrees):
            if atom_type == "Pow":
                raise KiraParseError(
                    "Family integral in a power or denominator in rule right-hand side"
                )
            raise KiraParseError(
                "Family integral nested in a nonlinear function in rule right-hand side"
            )
        return {0}

    degrees(expression)


def parse_kira2math(
    text: str,
    *,
    family_name: str,
    arity: int,
) -> dict[Expression, Expression]:
    """Parse the contents of one ``kira_*.m`` result file."""

    body = _without_mathematica_comments(text).strip()
    if not (body.startswith("{") and body.endswith("}")):
        raise KiraParseError("kira2math output must be a Mathematica list")
    body = body[1:-1].strip()
    if not body:
        return {}

    rules: dict[Expression, Expression] = {}
    for raw_rule in _scan_top_level(body, ","):
        if not raw_rule:
            continue
        left_text, right_text = _split_rule(raw_rule)
        left = _parse_expression(left_text, context="rule left-hand side")
        right = _parse_expression(right_text, context="rule right-hand side")
        _validate_integral(
            left,
            family_name=family_name,
            arity=arity,
            context="Rule left-hand side",
        )
        _validate_rhs(right, family_name=family_name, arity=arity)
        previous = rules.get(left)
        if previous is not None and previous != right:
            raise KiraParseError(
                f"Conflicting duplicate rules for {left.format_plain()}"
            )
        rules[left] = right
    return rules


def parse_kira2math_file(
    path: str | Path,
    *,
    family_name: str,
    arity: int,
) -> dict[Expression, Expression]:
    result_path = Path(path)
    try:
        text = result_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise KiraParseError(f"Cannot read kira2math output {result_path}") from exc
    return parse_kira2math(text, family_name=family_name, arity=arity)


def parse_masters(
    text: str,
    *,
    family_name: str,
    arity: int,
) -> tuple[Expression, ...]:
    """Parse Kira's ``results/<family>/masters`` contents."""

    masters: list[Expression] = []
    seen: set[Expression] = set()
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        master = _parse_expression(line, context=f"master on line {line_number}")
        _validate_integral(
            master,
            family_name=family_name,
            arity=arity,
            context=f"Master on line {line_number}",
        )
        if master not in seen:
            seen.add(master)
            masters.append(master)
    return tuple(masters)


def parse_masters_file(
    path: str | Path,
    *,
    family_name: str,
    arity: int,
) -> tuple[Expression, ...]:
    masters_path = Path(path)
    try:
        text = masters_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise KiraParseError(f"Cannot read master list {masters_path}") from exc
    return parse_masters(text, family_name=family_name, arity=arity)


__all__ = [
    "parse_kira2math",
    "parse_kira2math_file",
    "parse_masters",
    "parse_masters_file",
]
