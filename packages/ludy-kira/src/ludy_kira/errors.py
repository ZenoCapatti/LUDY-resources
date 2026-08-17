"""Typed failures raised by :mod:`ludy_kira`."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from symbolica import Expression


class KiraError(RuntimeError):
    """Base class for wrapper and Kira runtime failures."""


class KiraConfigurationError(KiraError, ValueError):
    """The requested family, kinematics, or reduction is not serializable."""


class KiraExecutableError(KiraError):
    """Kira or its configured Fermat executable cannot be used."""


class KiraWorkdirError(KiraError):
    """A work directory is unowned, corrupt, or belongs to another project."""

    def __init__(self, message: str, *, workdir: Path) -> None:
        super().__init__(message)
        self.workdir = workdir


class KiraRunError(KiraError):
    """The Kira subprocess exited unsuccessfully."""

    def __init__(
        self,
        message: str,
        *,
        workdir: Path,
        command: tuple[str, ...],
        returncode: int | None,
    ) -> None:
        super().__init__(message)
        self.workdir = workdir
        self.command = command
        self.returncode = returncode


class KiraTimeoutError(KiraRunError, TimeoutError):
    """The Kira subprocess exceeded its timeout."""


class KiraOutputError(KiraError):
    """A successful Kira process did not produce the expected output."""

    def __init__(self, message: str, *, workdir: Path | None = None) -> None:
        super().__init__(message)
        self.workdir = workdir


class KiraParseError(KiraOutputError):
    """A Kira result file is syntactically or structurally invalid."""


class IncompleteReductionError(KiraOutputError):
    """Kira output does not completely reduce the requested integrals."""

    def __init__(
        self,
        message: str,
        *,
        missing_targets: tuple[Expression, ...] = (),
        unresolved_integrals: tuple[Expression, ...] = (),
    ) -> None:
        super().__init__(message)
        self.missing_targets = missing_targets
        self.unresolved_integrals = unresolved_integrals
