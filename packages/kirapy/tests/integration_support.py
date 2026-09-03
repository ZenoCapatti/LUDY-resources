from __future__ import annotations

import json
from pathlib import Path

from symbolica import Expression

from kirapy.models import IntegralFamily
from kirapy.parser import parse_masters_file


def load_native_final_masters(
    workdir: Path,
    family: IntegralFamily,
) -> tuple[Expression, ...]:
    """Parse Kira's wire-family list and reconstruct logical family calls."""

    manifest = json.loads((workdir / "kirapy.json").read_text(encoding="utf-8"))
    wire_family = manifest["project"]["wire_family_name"]
    wire_masters = parse_masters_file(
        workdir / "results" / wire_family / "masters.final",
        family_name=wire_family,
        arity=family.arity,
    )
    return tuple(
        family(*(int(argument.format_plain()) for argument in master))
        for master in wire_masters
    )


__all__ = ["load_native_final_masters"]
