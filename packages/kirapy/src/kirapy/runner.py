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

from symbolica import E, Expression, Replacement, S

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
from .serialization import (
    ProjectFiles,
    _SymbolAlias,
    _alias_wire_name,
    _family_integral,
    _is_reserved_wire_name,
    _make_symbol_alias,
    serialize_project,
)

_MANIFEST_NAME = "kirapy.json"
_STATE_NAME = "kirapy.symbolica"
_PROCESS_LOG = "process.log"
_PACKAGE_VERSION = "0.1.0"
_PROCESS_STARTUP_GRACE = 0.25


def _sha256(contents: str) -> str:
    return hashlib.sha256(contents.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _project_fingerprint_payload(
    *,
    logical_family_name: str,
    wire_family_name: str,
    arity: int,
    target_file: str,
    targets: tuple[tuple[int, ...], ...],
    input_hashes: Mapping[str, str],
    aliases: tuple[_AliasManifest, ...],
) -> dict[str, object]:
    return {
        "logical_family_name": logical_family_name,
        "wire_family_name": wire_family_name,
        "arity": arity,
        "target_file": target_file,
        "targets": [list(target) for target in targets],
        "input_hashes": dict(input_hashes),
        "aliases": [alias.to_dict() for alias in aliases],
    }


@dataclass(frozen=True, slots=True)
class _AliasManifest:
    kind: str
    digest: str
    wire_name: str

    def __post_init__(self) -> None:
        if self.kind not in {"family", "momentum", "invariant", "dimension"}:
            raise ValueError(f"Unsupported alias kind {self.kind!r}")
        if len(self.digest) != 64 or any(
            character not in "0123456789abcdef" for character in self.digest
        ):
            raise ValueError("Alias digest must be a lowercase SHA-256 digest")
        expected = _alias_wire_name(self.kind, self.digest)
        if self.wire_name != expected:
            raise ValueError(
                f"Alias wire name {self.wire_name!r} does not match its kind and digest"
            )

    @classmethod
    def from_alias(cls, alias: _SymbolAlias) -> _AliasManifest:
        return cls(alias.kind, alias.digest, alias.wire_name)

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "digest": self.digest,
            "wire_name": self.wire_name,
        }


@dataclass(frozen=True, slots=True)
class WorkdirManifest:
    package_version: str
    project_fingerprint: str
    logical_family_name: str
    wire_family_name: str
    arity: int
    target_file: str
    targets: tuple[tuple[int, ...], ...]
    input_hashes: Mapping[str, str]
    _aliases: tuple[_AliasManifest, ...]
    state_file: str
    state_sha256: str
    executable: str
    kira_version: str | None
    fermat_path: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "targets", tuple(tuple(target) for target in self.targets)
        )
        object.__setattr__(
            self,
            "input_hashes",
            MappingProxyType(dict(sorted(self.input_hashes.items()))),
        )
        object.__setattr__(self, "_aliases", tuple(self._aliases))

    def to_dict(self) -> dict[str, object]:
        return {
            "package_version": self.package_version,
            "project_fingerprint": self.project_fingerprint,
            "project": {
                "logical_family_name": self.logical_family_name,
                "wire_family_name": self.wire_family_name,
                "arity": self.arity,
                "target_file": self.target_file,
                "targets": [list(target) for target in self.targets],
                "input_hashes": dict(self.input_hashes),
                "aliases": [alias.to_dict() for alias in self._aliases],
            },
            "state": {
                "file": self.state_file,
                "sha256": self.state_sha256,
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
            state_value = raw["state"]
            runner_value = raw["runner"]
            if not isinstance(project_value, dict) or not isinstance(
                state_value, dict
            ) or not isinstance(runner_value, dict):
                raise TypeError
            project = cast(dict[str, Any], project_value)
            state = cast(dict[str, Any], state_value)
            runner = cast(dict[str, Any], runner_value)
            input_hashes = project["input_hashes"]
            targets = project["targets"]
            aliases = project["aliases"]
            if (
                not isinstance(input_hashes, dict)
                or not isinstance(targets, list)
                or not isinstance(aliases, list)
            ):
                raise TypeError
            required_strings = (
                raw["package_version"],
                raw["project_fingerprint"],
                project["logical_family_name"],
                project["wire_family_name"],
                project["target_file"],
                state["file"],
                state["sha256"],
                runner["executable"],
            )
            if any(not isinstance(item, str) for item in required_strings):
                raise TypeError
            arity = project["arity"]
            if isinstance(arity, bool) or not isinstance(arity, int):
                raise TypeError
            if any(
                not isinstance(path, str) or not isinstance(digest, str)
                for path, digest in input_hashes.items()
            ):
                raise TypeError
            for optional in (runner.get("kira_version"), runner.get("fermat_path")):
                if optional is not None and not isinstance(optional, str):
                    raise TypeError
            parsed_targets: list[tuple[int, ...]] = []
            for target in targets:
                if not isinstance(target, list) or any(
                    isinstance(index, bool) or not isinstance(index, int)
                    for index in target
                ):
                    raise TypeError
                parsed_targets.append(tuple(target))
            parsed_aliases: list[_AliasManifest] = []
            for alias_value in aliases:
                if not isinstance(alias_value, dict):
                    raise TypeError
                alias = cast(dict[str, Any], alias_value)
                if any(
                    not isinstance(alias[field], str)
                    for field in ("kind", "digest", "wire_name")
                ):
                    raise TypeError
                parsed_aliases.append(
                    _AliasManifest(
                        kind=alias["kind"],
                        digest=alias["digest"],
                        wire_name=alias["wire_name"],
                    )
                )
            manifest = cls(
                package_version=raw["package_version"],
                project_fingerprint=raw["project_fingerprint"],
                logical_family_name=project["logical_family_name"],
                wire_family_name=project["wire_family_name"],
                arity=arity,
                target_file=project["target_file"],
                targets=tuple(parsed_targets),
                input_hashes=input_hashes,
                _aliases=tuple(parsed_aliases),
                state_file=state["file"],
                state_sha256=state["sha256"],
                executable=runner["executable"],
                kira_version=runner.get("kira_version"),
                fermat_path=runner.get("fermat_path"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise KiraWorkdirError("Malformed kirapy manifest", workdir=workdir) from exc
        if manifest.package_version != _PACKAGE_VERSION:
            raise KiraWorkdirError(
                f"Unsupported kirapy manifest package version {manifest.package_version!r}; "
                f"expected {_PACKAGE_VERSION!r}",
                workdir=workdir,
            )
        if manifest.arity < 1:
            raise KiraWorkdirError("Manifest arity must be positive", workdir=workdir)
        if any(len(target) != manifest.arity for target in manifest.targets):
            raise KiraWorkdirError(
                "Manifest target arity does not match the family", workdir=workdir
            )
        for field_name, identifier in (
            ("logical_family_name", manifest.logical_family_name),
            ("wire_family_name", manifest.wire_family_name),
            ("target_file", manifest.target_file),
        ):
            if not _is_identifier(identifier):
                raise KiraWorkdirError(
                    f"Manifest {field_name} is not a safe identifier",
                    workdir=workdir,
                )
        if len(manifest.project_fingerprint) != 64 or any(
            character not in "0123456789abcdef"
            for character in manifest.project_fingerprint
        ):
            raise KiraWorkdirError(
                "Manifest project fingerprint is not a SHA-256 digest",
                workdir=workdir,
            )
        for relative, digest in manifest.input_hashes.items():
            if not relative or len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise KiraWorkdirError(
                    "Manifest contains a malformed input hash", workdir=workdir
                )
        if manifest.state_file != _STATE_NAME:
            raise KiraWorkdirError(
                f"Manifest state file must be {_STATE_NAME}", workdir=workdir
            )
        if len(manifest.state_sha256) != 64 or any(
            character not in "0123456789abcdef"
            for character in manifest.state_sha256
        ):
            raise KiraWorkdirError(
                "Manifest state checksum is not a SHA-256 digest", workdir=workdir
            )
        if not manifest.targets:
            raise KiraWorkdirError(
                "Manifest needs at least one requested target", workdir=workdir
            )
        family_aliases = [
            alias for alias in manifest._aliases if alias.kind == "family"
        ]
        dimension_aliases = [
            alias for alias in manifest._aliases if alias.kind == "dimension"
        ]
        if len(family_aliases) != 1 or len(dimension_aliases) != 1:
            raise KiraWorkdirError(
                "Manifest needs exactly one family and one dimension alias",
                workdir=workdir,
            )
        if family_aliases[0].wire_name != manifest.wire_family_name:
            raise KiraWorkdirError(
                "Manifest family alias does not match wire_family_name",
                workdir=workdir,
            )
        if len({alias.wire_name for alias in manifest._aliases}) != len(
            manifest._aliases
        ) or len(
            {
                (alias.kind, alias.digest, alias.wire_name)
                for alias in manifest._aliases
            }
        ) != len(manifest._aliases):
            raise KiraWorkdirError(
                "Manifest contains duplicate alias records", workdir=workdir
            )
        fingerprint_payload = _project_fingerprint_payload(
            logical_family_name=manifest.logical_family_name,
            wire_family_name=manifest.wire_family_name,
            arity=manifest.arity,
            target_file=manifest.target_file,
            targets=manifest.targets,
            input_hashes=manifest.input_hashes,
            aliases=manifest._aliases,
        )
        if manifest.project_fingerprint != _sha256(
            _canonical_json(fingerprint_payload)
        ):
            raise KiraWorkdirError(
                "Manifest project fingerprint does not match its contents",
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
            left_mapping = cast(Mapping[object, object], left)
            right_mapping = cast(Mapping[object, object], right)
            for key in sorted(set(left_mapping) | set(right_mapping), key=str):
                key_string = str(key)
                if key not in left_mapping or key not in right_mapping:
                    differences.append(".".join((*path, key_string)))
                else:
                    compare(
                        (*path, key_string),
                        left_mapping[key],
                        right_mapping[key],
                    )
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
            / self.manifest.wire_family_name
            / f"kira_{self.project.target_file}.m"
        )

    @property
    def masters_file(self) -> Path:
        return self.workdir / "results" / self.manifest.wire_family_name / "masters"


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


def _write_symbol_state(aliases: tuple[_SymbolAlias, ...], path: Path) -> None:
    """Persist only the ordered native expressions, never their wire aliases."""

    registry = S("kirapy::state_registry")(
        *(alias.original for alias in aliases)
    )
    try:
        registry.save(os.fspath(path))
    except (OSError, TypeError, ValueError) as exc:
        raise KiraWorkdirError(
            f"Cannot write Symbolica state {path}", workdir=path.parent
        ) from exc


def _verify_state(workdir: Path, manifest: WorkdirManifest) -> Path:
    relative = Path(manifest.state_file)
    path = (workdir / relative).resolve()
    if relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(
        workdir
    ):
        raise KiraWorkdirError(
            f"Manifest state path escapes the workdir: {manifest.state_file}",
            workdir=workdir,
        )
    try:
        actual_hash = _sha256_file(path)
    except OSError as exc:
        raise KiraWorkdirError(
            f"Missing Symbolica state {manifest.state_file}", workdir=workdir
        ) from exc
    if actual_hash != manifest.state_sha256:
        raise KiraWorkdirError(
            f"Symbolica state {manifest.state_file} differs from its manifest",
            workdir=workdir,
        )
    return path


def _load_symbol_aliases(
    state_path: Path,
    manifest: WorkdirManifest,
    *,
    workdir: Path,
) -> tuple[_SymbolAlias, ...]:
    try:
        registry = Expression.load(os.fspath(state_path))
        registry_name = str(registry.get_name())
        originals = tuple(registry)
    except (OSError, TypeError, ValueError) as exc:
        raise KiraWorkdirError(
            f"Cannot load Symbolica state {manifest.state_file}", workdir=workdir
        ) from exc
    if registry_name != "kirapy::state_registry":
        raise KiraWorkdirError(
            "Symbolica state does not contain a kirapy registry", workdir=workdir
        )
    if len(originals) != len(manifest._aliases):
        raise KiraWorkdirError(
            "Symbolica state and manifest contain different alias counts",
            workdir=workdir,
        )

    aliases: list[_SymbolAlias] = []
    for original, stored in zip(originals, manifest._aliases, strict=True):
        try:
            alias = _make_symbol_alias(
                stored.kind,
                original,
                expected_digest=stored.digest,
                expected_wire_name=stored.wire_name,
            )
        except Exception as exc:
            raise KiraWorkdirError(
                f"Cannot restore alias {stored.wire_name!r} from Symbolica state",
                workdir=workdir,
            ) from exc
        aliases.append(alias)
    family_alias = next(alias for alias in aliases if alias.kind == "family")
    if family_alias.original != S(manifest.logical_family_name):
        raise KiraWorkdirError(
            "Symbolica state family does not match the manifest's logical family",
            workdir=workdir,
        )
    return tuple(aliases)


def _project_aliases(
    project: KiraProject,
    files: ProjectFiles,
    manifest: WorkdirManifest,
    *,
    workdir: Path,
) -> tuple[_SymbolAlias, ...]:
    aliases = tuple(_AliasManifest.from_alias(alias) for alias in files._alias_records)
    family_alias = next(alias for alias in aliases if alias.kind == "family")
    targets = tuple(_family_integral(target, project) for target in project.targets)
    input_hashes = {path: _sha256(contents) for path, contents in files.items()}
    payload = _project_fingerprint_payload(
        logical_family_name=project.family.name,
        wire_family_name=family_alias.wire_name,
        arity=project.family.arity,
        target_file=project.target_file,
        targets=targets,
        input_hashes=input_hashes,
        aliases=aliases,
    )
    if (
        manifest.project_fingerprint != _sha256(_canonical_json(payload))
        or aliases != manifest._aliases
    ):
        raise KiraWorkdirError(
            "Workdir manifest does not match the supplied project",
            workdir=workdir,
        )
    return files._alias_records


def _walk(expression: Expression):
    yield expression
    try:
        arguments = tuple(expression)
    except (TypeError, ValueError):
        return
    for argument in arguments:
        yield from _walk(argument)


def _replacement_rules(aliases: tuple[_SymbolAlias, ...]) -> list[Replacement]:
    replacements: list[Replacement] = []
    wildcard = E("kirapy_args__")
    for alias in aliases:
        if alias.kind == "family":
            replacements.append(
                Replacement(alias.wire(wildcard), alias.original(wildcard))
            )
        elif alias.wire != alias.original:
            replacements.append(Replacement(alias.wire, alias.original))
    return replacements


def _restore_expression(
    expression: Expression,
    replacements: list[Replacement],
    *,
    workdir: Path,
) -> Expression:
    restored = (
        expression.replace_multiple(replacements, repeat=False)
        if replacements
        else expression
    )
    survivors: set[str] = set()
    for candidate in _walk(restored):
        try:
            name = str(candidate.get_name()).rsplit("::", 1)[-1]
        except (TypeError, ValueError):
            continue
        if _is_reserved_wire_name(name):
            survivors.add(name)
    if survivors:
        raise KiraWorkdirError(
            "Unrestored Kira wire alias(es): " + ", ".join(sorted(survivors)),
            workdir=workdir,
        )
    return restored


def _restore_rules(
    rules: Mapping[Expression, Expression],
    replacements: list[Replacement],
    *,
    workdir: Path,
) -> dict[Expression, Expression]:
    restored: dict[Expression, Expression] = {}
    for left, right in rules.items():
        native_left = _restore_expression(left, replacements, workdir=workdir)
        native_right = _restore_expression(right, replacements, workdir=workdir)
        previous = restored.get(native_left)
        if previous is not None and previous != native_right:
            raise KiraWorkdirError(
                f"Alias restoration produced conflicting rules for {native_left}",
                workdir=workdir,
            )
        restored[native_left] = native_right
    return restored


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

    def _manifest(
        self,
        project: KiraProject,
        files: ProjectFiles,
        *,
        state_sha256: str,
    ) -> WorkdirManifest:
        input_hashes = {path: _sha256(contents) for path, contents in files.items()}
        environment = self._environment()
        resolved_executable = _resolve_executable(self.executable, environment)
        doctor = self.doctor()
        effective_fermat = environment.get("FERMATPATH")
        aliases = tuple(_AliasManifest.from_alias(alias) for alias in files._alias_records)
        family_alias = next(alias for alias in aliases if alias.kind == "family")
        targets = tuple(_family_integral(target, project) for target in project.targets)
        fingerprint_payload = _project_fingerprint_payload(
            logical_family_name=project.family.name,
            wire_family_name=family_alias.wire_name,
            arity=project.family.arity,
            target_file=project.target_file,
            targets=targets,
            input_hashes=input_hashes,
            aliases=aliases,
        )
        return WorkdirManifest(
            package_version=_PACKAGE_VERSION,
            project_fingerprint=_sha256(_canonical_json(fingerprint_payload)),
            logical_family_name=project.family.name,
            wire_family_name=family_alias.wire_name,
            arity=project.family.arity,
            target_file=project.target_file,
            targets=targets,
            input_hashes=input_hashes,
            _aliases=aliases,
            state_file=_STATE_NAME,
            state_sha256=state_sha256,
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
        manifest_path = path / _MANIFEST_NAME

        if path.exists() and not path.is_dir():
            raise KiraWorkdirError("Kira workdir is not a directory", workdir=path)
        path.mkdir(parents=True, exist_ok=True)
        entries = tuple(path.iterdir())
        if entries:
            if not manifest_path.is_file():
                raise KiraWorkdirError(
                    "Refusing to use a non-empty directory without kirapy.json",
                    workdir=path,
                )
            actual_manifest = _read_manifest(path)
            _verify_state(path, actual_manifest)
            expected_manifest = self._manifest(
                project,
                files,
                state_sha256=actual_manifest.state_sha256,
            )
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
        state_path = path / _STATE_NAME
        _write_symbol_state(files._alias_records, state_path)
        expected_manifest = self._manifest(
            project,
            files,
            state_sha256=_sha256_file(state_path),
        )
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
        return self.load(
            prepared.workdir,
            project=project,
            require_complete=require_complete,
        )

    def load(
        self,
        workdir: str | os.PathLike[str],
        *,
        project: KiraProject | None = None,
        require_complete: bool = True,
    ) -> ReductionResult:
        path = Path(workdir).expanduser().resolve()
        manifest = _read_manifest(path)
        _verify_inputs(path, manifest)
        state_path = _verify_state(path, manifest)

        if project is None:
            aliases = _load_symbol_aliases(state_path, manifest, workdir=path)
            requested_targets = None
        else:
            project_files = serialize_project(project)
            aliases = _project_aliases(
                project,
                project_files,
                manifest,
                workdir=path,
            )
            requested_targets = tuple(project.targets)

        result_path = (
            path
            / "results"
            / manifest.wire_family_name
            / f"kira_{manifest.target_file}.m"
        )
        masters_path = path / "results" / manifest.wire_family_name / "masters"
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
            family_name=manifest.wire_family_name,
            arity=manifest.arity,
        )
        masters = parse_masters_file(
            masters_path,
            family_name=manifest.wire_family_name,
            arity=manifest.arity,
        )

        replacements = _replacement_rules(aliases)
        native_rules = _restore_rules(rules, replacements, workdir=path)
        native_masters = tuple(
            _restore_expression(master, replacements, workdir=path)
            for master in masters
        )
        if requested_targets is None:
            family_alias = next(alias for alias in aliases if alias.kind == "family")
            try:
                requested_targets = tuple(
                    family_alias.original(*indices) for indices in manifest.targets
                )
            except (TypeError, ValueError) as exc:
                raise KiraWorkdirError(
                    "Cannot reconstruct requested targets from Symbolica state",
                    workdir=path,
                ) from exc
        native_targets = tuple(
            _restore_expression(target, replacements, workdir=path)
            for target in requested_targets
        )
        result = ReductionResult(
            family_name=manifest.logical_family_name,
            arity=manifest.arity,
            requested_targets=native_targets,
            rules=native_rules,
            masters=native_masters,
            workdir=path,
            symbol_aliases={alias.wire_name: alias.original for alias in aliases},
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
        dimension: Expression = S("d"),
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
            dimension=dimension,
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
        project: KiraProject | None = None,
        require_complete: bool = True,
    ) -> ReductionResult:
        return self.runner.load(
            workdir,
            project=project,
            require_complete=require_complete,
        )


__all__ = [
    "DoctorReport",
    "Kira",
    "KiraDoctor",
    "KiraRunner",
    "PreparedRun",
]
