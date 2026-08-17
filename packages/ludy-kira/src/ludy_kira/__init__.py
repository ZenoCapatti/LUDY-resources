"""A Symbolica-native Python facade for the external Kira reducer."""

from .errors import (
    IncompleteReductionError,
    KiraConfigurationError,
    KiraError,
    KiraExecutableError,
    KiraOutputError,
    KiraParseError,
    KiraRunError,
    KiraTimeoutError,
    KiraWorkdirError,
)
from .models import (
    IntegralFamily,
    KinematicInvariant,
    Kinematics,
    KiraProject,
    Propagator,
    ReductionBounds,
    ScalarProductRule,
)
from .parser import (
    parse_kira2math,
    parse_kira2math_file,
    parse_masters,
    parse_masters_file,
)
from .result import ReductionResult
from .runner import (
    DoctorReport,
    Kira,
    KiraDoctor,
    KiraRunner,
    PreparedRun,
    WorkdirManifest,
)
from .serialization import ProjectFiles, serialize_project

__version__ = "0.1.0"

__all__ = [
    "DoctorReport",
    "IncompleteReductionError",
    "IntegralFamily",
    "KinematicInvariant",
    "Kinematics",
    "Kira",
    "KiraConfigurationError",
    "KiraDoctor",
    "KiraError",
    "KiraExecutableError",
    "KiraOutputError",
    "KiraParseError",
    "KiraProject",
    "KiraRunError",
    "KiraRunner",
    "KiraTimeoutError",
    "KiraWorkdirError",
    "PreparedRun",
    "ProjectFiles",
    "Propagator",
    "ReductionBounds",
    "ReductionResult",
    "ScalarProductRule",
    "WorkdirManifest",
    "parse_kira2math",
    "parse_kira2math_file",
    "parse_masters",
    "parse_masters_file",
    "serialize_project",
]
