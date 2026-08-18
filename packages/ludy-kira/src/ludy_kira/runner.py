"""Persistent work-directory management and external Kira execution."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import signal
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, cast

from symbolica import E, Expression, ParseMode, Replacement

from .errors import (
    KiraExecutableError,
    KiraOutputError,
    KiraRunError,
    KiraTimeoutError,
    KiraWorkdirError,
)
from .models import IntegralFamily, Kinematics, KiraProject, ReductionBounds
from .parser import parse_kira2math_file, parse_masters_file
from .result import ReductionResult
from .serialization import ProjectFiles, serialize_project

_MANIFEST_NAME = "ludy-kira.json"
_PROCESS_LOG = "process.log"
_SCHEMA_VERSION = 1
_PACKAGE_VERSION = "0.1.0"
_PROCESS_STARTUP_GRACE = 0.25


def _sha256(contents: str) -> str:
    return hashlib.sha256(contents.encode("utf-8")).hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True, slots=True)
class WorkdirManifest:
    schema_version: int
    package_version: str
    project_fingerprint: str
    family_name: str
    arity: int
    target_file: str
    targets: tuple[str, ...]
    input_hashes: Mapping[str, str]
    invariant_aliases: Mapping[str, str]
    executable: str
    kira_version: str | None
    fermat_path: str | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "targets", tuple(self.targets))
        object.__setattr__(
            self,
            "input_hashes",
            MappingProxyType(dict(sorted(self.input_hashes.items()))),
        )
        object.__setattr__(
            self,
            "invariant_aliases",
            MappingProxyType(dict(sorted(self.invariant_aliases.items()))),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "package_version": self.package_version,
            "project_fingerprint": self.project_fingerprint,
            "project": {
                "family_name": self.family_name,
                "arity": self.arity,
                "target_file": self.target_file,
                "targets": list(self.targets),
                "input_hashes": dict(self.input_hashes),
                "invariant_aliases": dict(self.invariant_aliases),
            },
            "runner": {
                "executable": self.executable,
                "kira_version": self.kira_version,
                "fermat_path": self.fermat_path,
            },
        }

    def to_json(self) -> str:
        return (
            json.dumps(self.to_dict(), sort_keys=True, indent=2, ensure_ascii=True)
            + "\n"
        )

    @classmethod
    def from_dict(cls, value: object, *, workdir: Path) -> WorkdirManifest:
        try:
            if not isinstance(value, dict):
                raise TypeError
            raw = cast(dict[str, Any], value)
            project_value = raw["project"]
            runner_value = raw["runner"]
            if not isinstance(project_value, dict) or not isinstance(
                runner_value, dict
            ):
                raise TypeError
            project = cast(dict[str, Any], project_value)
            runner = cast(dict[str, Any], runner_value)
            input_hashes = project["input_hashes"]
            invariant_aliases = project.get("invariant_aliases", {})
            targets = project["targets"]
            if (
                not isinstance(input_hashes, dict)
                or not isinstance(invariant_aliases, dict)
                or not isinstance(targets, list)
            ):
                raise TypeError
            manifest = cls(
                schema_version=int(raw["schema_version"]),
                package_version=str(raw["package_version"]),
                project_fingerprint=str(raw["project_fingerprint"]),
                family_name=str(project["family_name"]),
                arity=int(project["arity"]),
                target_file=str(project["target_file"]),
                targets=tuple(str(target) for target in targets),
                input_hashes={
                    str(path): str(digest) for path, digest in input_hashes.items()
                },
                invariant_aliases={
                    str(name): str(expression)
                    for name, expression in invariant_aliases.items()
                },
                executable=str(runner["executable"]),
                kira_version=(
                    None
                    if runner.get("kira_version") is None
                    else str(runner["kira_version"])
                ),
                fermat_path=(
                    None
                    if runner.get("fermat_path") is None
                    else str(runner["fermat_path"])
                ),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise KiraWorkdirError(
                "Malformed ludy-kira manifest", workdir=workdir
            ) from exc
        if manifest.schema_version != _SCHEMA_VERSION:
            raise KiraWorkdirError(
                f"Unsupported ludy-kira manifest schema {manifest.schema_version}",
                workdir=workdir,
            )
        if manifest.arity < 1:
            raise KiraWorkdirError("Manifest arity must be positive", workdir=workdir)
        for field_name, identifier in (
            ("family_name", manifest.family_name),
            ("target_file", manifest.target_file),
        ):
            if not _is_identifier(identifier):
                raise KiraWorkdirError(
                    f"Manifest {field_name} is not a safe identifier",
                    workdir=workdir,
                )
        return manifest


def _manifest_difference_fields(
    actual: WorkdirManifest,
    expected: WorkdirManifest,
) -> tuple[str, ...]:
    """Return stable dotted paths for fields that prevent safe resumption."""

    differences: list[str] = []

    def compare(path: tuple[str, ...], left: object, right: object) -> None:
        if isinstance(left, Mapping) and isinstance(right, Mapping):
            for key in sorted(set(left) | set(right), key=str):
                key_string = str(key)
                if key not in left or key not in right:
                    differences.append(".".join((*path, key_string)))
                else:
                    compare((*path, key_string), left[key], right[key])
            return
        if left != right:
            differences.append(".".join(path))

    compare((), actual.to_dict(), expected.to_dict())

    # The fingerprint is derived from the concrete project fields below it.
    # Reporting both obscures the useful cause without adding information.
    if any(field.startswith("project.") for field in differences):
        differences = [
            field for field in differences if field != "project_fingerprint"
        ]
    return tuple(differences)


@dataclass(frozen=True, slots=True)
class PreparedRun:
    project: KiraProject
    workdir: Path
    files: ProjectFiles
    manifest: WorkdirManifest

    @property
    def result_file(self) -> Path:
        return (
            self.workdir
            / "results"
            / self.project.family.name
            / f"kira_{self.project.target_file}.m"
        )

    @property
    def masters_file(self) -> Path:
        return self.workdir / "results" / self.project.family.name / "masters"


@dataclass(frozen=True, slots=True)
class DoctorReport:
    ok: bool
    executable: Path | None
    version: str | None
    fermat_path: Path | None
    issues: tuple[str, ...]

    def raise_for_errors(self) -> DoctorReport:
        if not self.ok:
            raise KiraExecutableError("; ".join(self.issues))
        return self


class KiraDoctor:
    """Read-only diagnostics for an external Kira/Fermat configuration."""

    def __init__(
        self,
        executable: str | os.PathLike[str] = "kira",
        *,
        fermat_path: str | os.PathLike[str] | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        self.executable = os.fspath(executable)
        self.fermat_path = None if fermat_path is None else Path(fermat_path)
        self.env = dict(env or {})

    def check(self, *, timeout: float = 10.0) -> DoctorReport:
        environment = os.environ.copy()
        environment.update(self.env)
        if self.fermat_path is not None:
            environment["FERMATPATH"] = os.fspath(self.fermat_path)

        issues: list[str] = []
        executable = _resolve_executable(self.executable, environment)
        version: str | None = None
        if executable is None:
            issues.append(
                f"Kira executable {self.executable!r} was not found or is not executable"
            )
        else:
            try:
                completed = subprocess.run(
                    [os.fspath(executable), "--version"],
                    env=environment,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                issues.append(f"Could not query Kira version: {exc}")
            else:
                output = "\n".join(
                    part.strip()
                    for part in (completed.stdout, completed.stderr)
                    if part.strip()
                )
                version = output.splitlines()[0] if output else None
                if completed.returncode != 0:
                    issues.append(
                        f"Kira --version exited with status {completed.returncode}"
                    )

        configured_fermat = self.fermat_path
        if configured_fermat is None and environment.get("FERMATPATH"):
            configured_fermat = Path(environment["FERMATPATH"])
        if configured_fermat is not None and not configured_fermat.exists():
            issues.append(f"FERMATPATH does not exist: {configured_fermat}")

        return DoctorReport(
            ok=not issues,
            executable=executable,
            version=version,
            fermat_path=configured_fermat,
            issues=tuple(issues),
        )


def _resolve_executable(executable: str, environment: Mapping[str, str]) -> Path | None:
    has_separator = os.sep in executable or (
        os.altsep is not None and os.altsep in executable
    )
    if has_separator:
        candidate = Path(executable).expanduser().resolve()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
        return None
    found = shutil.which(executable, path=environment.get("PATH"))
    return None if found is None else Path(found).resolve()


def _is_identifier(value: str) -> bool:
    return (
        bool(value)
        and (value[0].isalpha() or value[0] == "_")
        and all(character.isalnum() or character == "_" for character in value)
    )


def _terminate_process_tree(
    process: subprocess.Popen[str], *, force: bool = False
) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL if force else signal.SIGTERM)
        except ProcessLookupError:
            return
    elif force:
        process.kill()
    else:
        process.terminate()


class KiraRunner:
    """Low-level serializer, process runner, and result loader."""

    def __init__(
        self,
        executable: str | os.PathLike[str] = "kira",
        *,
        fermat_path: str | os.PathLike[str] | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        self.executable = os.fspath(executable)
        self.fermat_path = None if fermat_path is None else Path(fermat_path)
        self.env = dict(env or {})

    def _environment(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment.update(self.env)
        if self.fermat_path is not None:
            environment["FERMATPATH"] = os.fspath(self.fermat_path)
        return environment

    def doctor(self, *, timeout: float = 10.0) -> DoctorReport:
        return KiraDoctor(
            self.executable,
            fermat_path=self.fermat_path,
            env=self.env,
        ).check(timeout=timeout)

    def _manifest(self, project: KiraProject, files: ProjectFiles) -> WorkdirManifest:
        input_hashes = {path: _sha256(contents) for path, contents in files.items()}
        environment = self._environment()
        resolved_executable = _resolve_executable(self.executable, environment)
        doctor = self.doctor()
        effective_fermat = environment.get("FERMATPATH")
        fingerprint_payload = {
            "family_name": project.family.name,
            "arity": project.family.arity,
            "target_file": project.target_file,
            "targets": [
                target.to_mathematica(show_namespaces=False)
                for target in project.targets
            ],
            "input_hashes": input_hashes,
            "invariant_aliases": dict(files.invariant_aliases),
        }
        return WorkdirManifest(
            schema_version=_SCHEMA_VERSION,
            package_version=_PACKAGE_VERSION,
            project_fingerprint=_sha256(_canonical_json(fingerprint_payload)),
            family_name=project.family.name,
            arity=project.family.arity,
            target_file=project.target_file,
            targets=tuple(fingerprint_payload["targets"]),
            input_hashes=input_hashes,
            invariant_aliases=files.invariant_aliases,
            executable=(
                self.executable
                if resolved_executable is None
                else os.fspath(resolved_executable)
            ),
            kira_version=doctor.version,
            fermat_path=effective_fermat,
        )

    def prepare(
        self,
        project: KiraProject,
        workdir: str | os.PathLike[str],
        *,
        resume: bool = False,
    ) -> PreparedRun:
        path = Path(workdir).expanduser().resolve()
        files = serialize_project(project)
        expected_manifest = self._manifest(project, files)
        manifest_path = path / _MANIFEST_NAME

        if path.exists() and not path.is_dir():
            raise KiraWorkdirError("Kira workdir is not a directory", workdir=path)
        path.mkdir(parents=True, exist_ok=True)
        entries = tuple(path.iterdir())
        if entries:
            if not manifest_path.is_file():
                raise KiraWorkdirError(
                    "Refusing to use a non-empty directory without ludy-kira.json",
                    workdir=path,
                )
            actual_manifest = _read_manifest(path)
            if actual_manifest.to_dict() != expected_manifest.to_dict():
                differing_fields = _manifest_difference_fields(
                    actual_manifest, expected_manifest
                )
                details = ", ".join(differing_fields) or "unknown"
                raise KiraWorkdirError(
                    f"Workdir manifest at {path} does not match the requested "
                    f"project and runner; differing fields: {details}. "
                    "Existing workdir was not modified",
                    workdir=path,
                )
            if not resume:
                raise KiraWorkdirError(
                    "Workdir already contains this project; pass resume=True to reuse it",
                    workdir=path,
                )
            _verify_inputs(path, actual_manifest)
            return PreparedRun(project, path, files, actual_manifest)

        for relative, contents in files.items():
            destination = path / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(contents, encoding="utf-8")
        manifest_path.write_text(expected_manifest.to_json(), encoding="utf-8")
        return PreparedRun(project, path, files, expected_manifest)

    def run(
        self,
        prepared: PreparedRun,
        *,
        parallel: int | str | None = None,
        timeout: float | None = None,
    ) -> None:
        environment = self._environment()
        executable = _resolve_executable(self.executable, environment)
        if executable is None:
            raise KiraExecutableError(
                f"Kira executable {self.executable!r} was not found or is not executable"
            )
        command = [os.fspath(executable)]
        if parallel is not None:
            if isinstance(parallel, bool) or not (
                (isinstance(parallel, int) and parallel > 0)
                or parallel in {"physical", "logical"}
            ):
                raise ValueError(
                    "parallel must be a positive integer, 'physical', or 'logical'"
                )
            command.append(f"--parallel={parallel}")
        command.append("jobs.yaml")

        log_path = prepared.workdir / _PROCESS_LOG
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"$ {shlex.join(command)}\n")
            log.flush()
            try:
                process = subprocess.Popen(
                    command,
                    cwd=prepared.workdir,
                    env=environment,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    start_new_session=os.name == "posix",
                )
            except OSError as exc:
                log.write(f"[failed to start: {exc}]\n")
                raise KiraExecutableError(f"Could not start Kira: {exc}") from exc
            try:
                effective_timeout = (
                    None if timeout is None else timeout + _PROCESS_STARTUP_GRACE
                )
                process.wait(timeout=effective_timeout)
            except subprocess.TimeoutExpired as exc:
                _terminate_process_tree(process)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    _terminate_process_tree(process, force=True)
                    process.wait()
                log.write("[terminated after timeout]\n")
                raise KiraTimeoutError(
                    f"Kira exceeded timeout {timeout}s; logs are preserved in {log_path}",
                    workdir=prepared.workdir,
                    command=tuple(command),
                    returncode=process.returncode,
                ) from exc
            except BaseException:
                _terminate_process_tree(process)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    _terminate_process_tree(process, force=True)
                    process.wait()
                log.write("[terminated after interruption]\n")
                raise

            log.write(f"[exit {process.returncode}]\n")
        if process.returncode != 0:
            raise KiraRunError(
                f"Kira exited with status {process.returncode}; logs are preserved in {log_path}",
                workdir=prepared.workdir,
                command=tuple(command),
                returncode=process.returncode,
            )
        if not prepared.result_file.is_file() or not prepared.masters_file.is_file():
            missing = [
                os.fspath(path.relative_to(prepared.workdir))
                for path in (prepared.result_file, prepared.masters_file)
                if not path.is_file()
            ]
            raise KiraOutputError(
                "Kira exited successfully but did not create: " + ", ".join(missing),
                workdir=prepared.workdir,
            )

    def reduce(
        self,
        project: KiraProject,
        workdir: str | os.PathLike[str],
        *,
        parallel: int | str | None = None,
        timeout: float | None = None,
        resume: bool = False,
        require_complete: bool = True,
    ) -> ReductionResult:
        prepared = self.prepare(project, workdir, resume=resume)
        if not (
            resume
            and prepared.result_file.is_file()
            and prepared.masters_file.is_file()
        ):
            self.run(prepared, parallel=parallel, timeout=timeout)
        return self.load(prepared.workdir, require_complete=require_complete)

    def load(
        self,
        workdir: str | os.PathLike[str],
        *,
        require_complete: bool = True,
    ) -> ReductionResult:
        path = Path(workdir).expanduser().resolve()
        manifest = _read_manifest(path)
        _verify_inputs(path, manifest)
        result_path = (
            path / "results" / manifest.family_name / f"kira_{manifest.target_file}.m"
        )
        masters_path = path / "results" / manifest.family_name / "masters"
        if not result_path.is_file() or not masters_path.is_file():
            missing = [
                os.fspath(candidate.relative_to(path))
                for candidate in (result_path, masters_path)
                if not candidate.is_file()
            ]
            raise KiraOutputError(
                "Missing Kira output: " + ", ".join(missing),
                workdir=path,
            )

        rules = parse_kira2math_file(
            result_path,
            family_name=manifest.family_name,
            arity=manifest.arity,
        )
        parsed_aliases: dict[str, Expression] = {}
        if manifest.invariant_aliases:
            alias_replacements: list[Replacement] = []
            for name, expression_text in manifest.invariant_aliases.items():
                try:
                    alias = E(name, ParseMode.Mathematica)
                    expression = E(expression_text, ParseMode.Mathematica)
                except Exception as exc:
                    raise KiraWorkdirError(
                        f"Cannot parse invariant alias {name!r} from manifest",
                        workdir=path,
                    ) from exc
                parsed_aliases[name] = expression
                alias_replacements.append(Replacement(alias, expression))
            rules = {
                left: right.replace_multiple(alias_replacements, repeat=False)
                for left, right in rules.items()
            }
        masters = parse_masters_file(
            masters_path,
            family_name=manifest.family_name,
            arity=manifest.arity,
        )
        targets: list[Expression] = []
        for target_text in manifest.targets:
            try:
                targets.append(E(target_text, ParseMode.Mathematica))
            except Exception as exc:
                raise KiraWorkdirError(
                    f"Cannot parse target stored in manifest: {target_text}",
                    workdir=path,
                ) from exc
        result = ReductionResult(
            family_name=manifest.family_name,
            arity=manifest.arity,
            requested_targets=tuple(targets),
            rules=rules,
            masters=masters,
            workdir=path,
            invariant_aliases=parsed_aliases,
            process_log=(
                path / _PROCESS_LOG if (path / _PROCESS_LOG).exists() else None
            ),
            kira_log=(path / "kira.log" if (path / "kira.log").exists() else None),
        )
        if require_complete:
            result.require_complete()
        return result


def _read_manifest(workdir: Path) -> WorkdirManifest:
    manifest_path = workdir / _MANIFEST_NAME
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KiraWorkdirError(
            f"Cannot read valid manifest {manifest_path}",
            workdir=workdir,
        ) from exc
    return WorkdirManifest.from_dict(value, workdir=workdir)


def _verify_inputs(workdir: Path, manifest: WorkdirManifest) -> None:
    for relative, expected_hash in manifest.input_hashes.items():
        relative_path = Path(relative)
        path = (workdir / relative_path).resolve()
        if (
            relative_path.is_absolute()
            or ".." in relative_path.parts
            or not path.is_relative_to(workdir)
        ):
            raise KiraWorkdirError(
                f"Manifest input path escapes the workdir: {relative}",
                workdir=workdir,
            )
        try:
            actual_hash = _sha256(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise KiraWorkdirError(
                f"Missing generated input {relative}", workdir=workdir
            ) from exc
        if actual_hash != expected_hash:
            raise KiraWorkdirError(
                f"Generated input {relative} differs from its manifest",
                workdir=workdir,
            )


class Kira:
    """Small public facade for one-shot Symbolica-to-Kira reductions."""

    def __init__(
        self,
        executable: str | os.PathLike[str] = "kira",
        *,
        fermat_path: str | os.PathLike[str] | None = None,
        env: Mapping[str, str] | None = None,
        runner: KiraRunner | None = None,
    ) -> None:
        if runner is not None and (
            os.fspath(executable) != "kira"
            or fermat_path is not None
            or env is not None
        ):
            raise ValueError(
                "runner cannot be combined with executable, fermat_path, or env"
            )
        self.runner = runner or KiraRunner(
            executable,
            fermat_path=fermat_path,
            env=env,
        )

    def doctor(self, *, timeout: float = 10.0) -> DoctorReport:
        return self.runner.doctor(timeout=timeout)

    def reduce(
        self,
        *,
        family: IntegralFamily,
        kinematics: Kinematics,
        targets: tuple[Expression, ...],
        bounds: ReductionBounds,
        workdir: str | os.PathLike[str],
        parallel: int | str | None = None,
        timeout: float | None = None,
        resume: bool = False,
        require_complete: bool = True,
        preferred_masters: tuple[Expression, ...] = (),
        check_masters: bool = False,
        reconstruct_mass: bool | None = None,
    ) -> ReductionResult:
        project = KiraProject(
            family=family,
            kinematics=kinematics,
            targets=targets,
            bounds=bounds,
            preferred_masters=preferred_masters,
            check_masters=check_masters,
            reconstruct_mass=(
                kinematics.symbol_to_replace_by_one is not None
                if reconstruct_mass is None
                else reconstruct_mass
            ),
        )
        return self.runner.reduce(
            project,
            workdir,
            parallel=parallel,
            timeout=timeout,
            resume=resume,
            require_complete=require_complete,
        )

    def load(
        self,
        workdir: str | os.PathLike[str],
        *,
        require_complete: bool = True,
    ) -> ReductionResult:
        return self.runner.load(workdir, require_complete=require_complete)


__all__ = [
    "DoctorReport",
    "Kira",
    "KiraDoctor",
    "KiraRunner",
    "PreparedRun",
    "WorkdirManifest",
]
