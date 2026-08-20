from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
import textwrap
from dataclasses import replace
from pathlib import Path

import pytest
from symbolica import S

from kirapy.errors import (
    KiraOutputError,
    KiraRunError,
    KiraTimeoutError,
    KiraWorkdirError,
)
from kirapy.models import KiraProject
from kirapy.runner import KiraRunner
from kirapy.serialization import _alias_wire_name


def _write_result(
    prepared,
    *,
    left: str,
    right: str,
    master: str,
) -> None:
    prepared.result_file.parent.mkdir(parents=True, exist_ok=True)
    prepared.result_file.write_text(
        f"{{\n{left} -> {right}\n}}\n", encoding="utf-8"
    )
    prepared.masters_file.write_text(f"{master}\n", encoding="utf-8")


def _refresh_state_checksum(workdir: Path) -> None:
    manifest_path = workdir / "kirapy.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["state"]["sha256"] = hashlib.sha256(
        (workdir / "kirapy.symbolica").read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


@pytest.fixture
def fake_kira(tmp_path: Path) -> Path:
    executable = tmp_path / "fake-kira"
    executable.write_text(
        textwrap.dedent(
            f"""\
            #!{sys.executable}
            import json
            import os
            from pathlib import Path
            import sys
            import time

            if "--version" in sys.argv:
                print("Kira version: 3.1 (fake)")
                raise SystemExit(0)

            Path("observed.json").write_text(json.dumps({{
                "argv": sys.argv[1:],
                "fermat": os.environ.get("FERMATPATH"),
                "custom": os.environ.get("KIRAPY_FAKE_VALUE"),
            }}), encoding="utf-8")
            mode = os.environ.get("KIRAPY_FAKE_MODE", "success")
            print(f"fake Kira mode={{mode}}", flush=True)
            if mode == "sleep":
                time.sleep(30)
            if mode == "fail":
                raise SystemExit(7)
            if mode == "missing-output":
                raise SystemExit(0)

            targets = [line.strip() for line in Path("targets").read_text().splitlines() if line.strip()]
            family_name = targets[0].split("[", 1)[0]
            result_dir = Path("results") / family_name
            result_dir.mkdir(parents=True, exist_ok=True)
            rules = ",\\n".join(f"{{target}} -> 0" for target in targets)
            (result_dir / "kira_targets.m").write_text("{{\\n" + rules + "\\n}}\\n", encoding="utf-8")
            (result_dir / "masters").write_text("", encoding="utf-8")
            (result_dir / "masters.final").write_text("", encoding="utf-8")
            Path("kira.log").write_text("fake Kira log\\n", encoding="utf-8")
            """
        ),
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return executable


def test_prepare_writes_owned_deterministic_workdir(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    workdir = tmp_path / "run"
    runner = KiraRunner(fake_kira)

    prepared = runner.prepare(topo1_project, workdir)

    assert prepared.workdir == workdir.resolve()
    assert (workdir / "kirapy.json").is_file()
    assert (workdir / "kirapy.symbolica").is_file()
    assert (workdir / "config/integralfamilies.yaml").is_file()
    assert (workdir / "config/kinematics.yaml").is_file()
    assert (workdir / "jobs.yaml").is_file()
    manifest = json.loads((workdir / "kirapy.json").read_text(encoding="utf-8"))
    assert manifest["project"]["logical_family_name"] == "topo1"
    assert manifest["project"]["wire_family_name"].startswith("kp_f_")
    invariant_records = [
        alias
        for alias in manifest["project"]["aliases"]
        if alias["kind"] == "invariant"
    ]
    assert all(len(alias["digest"]) == 64 for alias in invariant_records)
    assert all(len(alias["wire_name"]) <= 10 for alias in invariant_records)
    assert manifest["project"]["arity"] == 3
    assert set(manifest["project"]["input_hashes"]) == set(prepared.files)
    assert manifest["state"]["file"] == "kirapy.symbolica"

    with pytest.raises(KiraWorkdirError, match="pass resume=True"):
        runner.prepare(topo1_project, workdir)
    resumed = runner.prepare(topo1_project, workdir, resume=True)
    assert resumed.manifest.to_dict() == prepared.manifest.to_dict()


def test_prepare_refuses_nonempty_unowned_directory(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    workdir = tmp_path / "run"
    workdir.mkdir()
    (workdir / "user-data").write_text("preserve me", encoding="utf-8")

    with pytest.raises(KiraWorkdirError, match="non-empty"):
        KiraRunner(fake_kira).prepare(topo1_project, workdir)
    assert (workdir / "user-data").read_text(encoding="utf-8") == "preserve me"


def test_resume_rejects_changed_project_and_changed_generated_input(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    runner = KiraRunner(fake_kira)
    project_workdir = tmp_path / "project-change"
    runner.prepare(topo1_project, project_workdir)
    changed = replace(
        topo1_project,
        bounds=replace(topo1_project.bounds, r=topo1_project.bounds.r + 1),
    )
    with pytest.raises(KiraWorkdirError, match="does not match") as caught:
        runner.prepare(changed, project_workdir, resume=True)
    assert str(project_workdir.resolve()) in str(caught.value)
    assert "project.input_hashes.jobs.yaml" in str(caught.value)
    assert "project_fingerprint" not in str(caught.value)
    assert "Existing workdir was not modified" in str(caught.value)

    input_workdir = tmp_path / "input-change"
    runner.prepare(topo1_project, input_workdir)
    (input_workdir / "targets").write_text("topo1[1,1,1]\n", encoding="utf-8")
    with pytest.raises(KiraWorkdirError, match="differs from its manifest"):
        runner.prepare(topo1_project, input_workdir, resume=True)


def test_resume_reports_changed_runner_field(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    first_fermat = tmp_path / "first-fermat"
    first_fermat.write_text("fake", encoding="utf-8")
    second_fermat = tmp_path / "second-fermat"
    second_fermat.write_text("fake", encoding="utf-8")
    workdir = tmp_path / "runner-change"

    KiraRunner(fake_kira, fermat_path=first_fermat).prepare(
        topo1_project, workdir
    )
    with pytest.raises(KiraWorkdirError, match="does not match") as caught:
        KiraRunner(fake_kira, fermat_path=second_fermat).prepare(
            topo1_project, workdir, resume=True
        )

    assert "runner.fermat_path" in str(caught.value)
    assert "project_fingerprint" not in str(caught.value)


def test_fake_runner_constructs_command_forwards_environment_and_loads(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    fermat = tmp_path / "fer64"
    fermat.write_text("fake", encoding="utf-8")
    runner = KiraRunner(
        fake_kira,
        fermat_path=fermat,
        env={"KIRAPY_FAKE_VALUE": "forwarded"},
    )
    workdir = tmp_path / "run"

    result = runner.reduce(topo1_project, workdir, parallel="logical")

    observed = json.loads((workdir / "observed.json").read_text(encoding="utf-8"))
    assert observed == {
        "argv": ["--parallel=logical", "jobs.yaml"],
        "fermat": os.fspath(fermat),
        "custom": "forwarded",
    }
    assert result.complete
    assert len(result.zero_integrals) == 27
    assert result.process_log == workdir / "process.log"
    assert result.kira_log == workdir / "kira.log"
    assert "fake Kira mode=success" in result.process_log.read_text(encoding="utf-8")
    assert runner.load(workdir).rules == result.rules


def test_nonzero_exit_preserves_log_and_error_context(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    runner = KiraRunner(fake_kira, env={"KIRAPY_FAKE_MODE": "fail"})
    workdir = tmp_path / "run"

    with pytest.raises(KiraRunError) as caught:
        runner.reduce(topo1_project, workdir)

    assert caught.value.returncode == 7
    assert caught.value.workdir == workdir.resolve()
    log = (workdir / "process.log").read_text(encoding="utf-8")
    assert "fake Kira mode=fail" in log
    assert "[exit 7]" in log


def test_timeout_terminates_process_and_preserves_log(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    runner = KiraRunner(fake_kira, env={"KIRAPY_FAKE_MODE": "sleep"})
    workdir = tmp_path / "run"

    with pytest.raises(KiraTimeoutError) as caught:
        runner.reduce(topo1_project, workdir, timeout=0.05)

    assert caught.value.workdir == workdir.resolve()
    log = (workdir / "process.log").read_text(encoding="utf-8")
    assert "fake Kira mode=sleep" in log
    assert "terminated after timeout" in log


def test_zero_exit_without_results_is_an_output_error(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    runner = KiraRunner(fake_kira, env={"KIRAPY_FAKE_MODE": "missing-output"})

    with pytest.raises(KiraOutputError, match="did not create"):
        runner.reduce(topo1_project, tmp_path / "run")


def test_load_restores_family_invariants_dimension_targets_and_masters(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    epsilon = S("roundtrip_epsilon")
    family = topo1_project.family
    target = family(1, 1, 1)
    master = family(0, 1, 1)
    dimension = 4 - 2 * epsilon
    project = replace(
        topo1_project,
        targets=(target,),
        preferred_masters=(master,),
        check_masters=False,
        dimension=dimension,
    )
    runner = KiraRunner(fake_kira)
    prepared = runner.prepare(project, tmp_path / "roundtrip")
    aliases = {alias.original: alias for alias in prepared.files._alias_records}
    family_alias = aliases[S(family.name)]
    invariant = project.kinematics.kinematic_invariants[1].expression
    wire_target = f"{family_alias.wire_name}[1,1,1]"
    wire_master = f"{family_alias.wire_name}[0,1,1]"
    _write_result(
        prepared,
        left=wire_target,
        right=f"({aliases[invariant].wire_name}+d)*{wire_master}",
        master=wire_master,
    )

    expected_right = (invariant + dimension) * master
    live = runner.load(prepared.workdir, project=project)
    standalone = runner.load(prepared.workdir)

    for result in (live, standalone):
        assert result.family_name == family.name
        assert result.requested_targets == (target,)
        assert result.masters == (master,)
        assert result.rules[target] == expected_right
        assert result.symbol_aliases["d"] == dimension
        assert all(
            "kp_" not in expression.format_plain()
            for expression in (
                *result.requested_targets,
                *result.masters,
                *result.rules.keys(),
                *result.rules.values(),
            )
        )


@pytest.mark.parametrize("mode", ("missing", "corrupt"))
def test_load_rejects_missing_or_corrupt_symbolica_state(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
    mode: str,
) -> None:
    workdir = tmp_path / mode
    runner = KiraRunner(fake_kira)
    runner.prepare(topo1_project, workdir)
    state = workdir / "kirapy.symbolica"
    if mode == "missing":
        state.unlink()
    else:
        state.write_bytes(b"not a Symbolica state")

    with pytest.raises(KiraWorkdirError, match="Symbolica state"):
        runner.load(workdir)


def test_standalone_load_recomputes_alias_digests(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    workdir = tmp_path / "digest-mismatch"
    runner = KiraRunner(fake_kira)
    runner.prepare(topo1_project, workdir)
    manifest_path = workdir / "kirapy.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    invariant = next(
        alias
        for alias in manifest["project"]["aliases"]
        if alias["kind"] == "invariant"
    )
    invariant["digest"] = "0" * 64
    invariant["wire_name"] = _alias_wire_name("invariant", "0" * 64)
    manifest["project_fingerprint"] = hashlib.sha256(
        json.dumps(
            manifest["project"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(KiraWorkdirError, match="Cannot restore alias"):
        runner.load(workdir)


def test_project_aware_load_rejects_a_different_live_project(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    workdir = tmp_path / "wrong-project"
    runner = KiraRunner(fake_kira)
    runner.prepare(topo1_project, workdir)
    changed = replace(topo1_project, dimension=4 - 2 * S("other_epsilon"))

    with pytest.raises(KiraWorkdirError, match="supplied project"):
        runner.load(workdir, project=changed)


def test_load_rejects_a_manifest_from_another_package_version(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    workdir = tmp_path / "old-package"
    runner = KiraRunner(fake_kira)
    runner.prepare(topo1_project, workdir)
    manifest_path = workdir / "kirapy.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["package_version"] = "0.0.0"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(KiraWorkdirError, match="package version"):
        runner.load(workdir)


def test_load_rejects_coerced_manifest_scalar_types(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    workdir = tmp_path / "coerced-manifest"
    runner = KiraRunner(fake_kira)
    runner.prepare(topo1_project, workdir)
    manifest_path = workdir / "kirapy.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["project"]["arity"] = "3"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(KiraWorkdirError, match="Malformed kirapy manifest"):
        runner.load(workdir)


@pytest.mark.parametrize("malformation", ("head", "count"))
def test_standalone_load_rejects_a_malformed_state_registry(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
    malformation: str,
) -> None:
    workdir = tmp_path / f"bad-registry-{malformation}"
    runner = KiraRunner(fake_kira)
    prepared = runner.prepare(topo1_project, workdir)
    originals = tuple(alias.original for alias in prepared.files._alias_records)
    head = S("wrong::state_registry") if malformation == "head" else S(
        "kirapy::state_registry"
    )
    if malformation == "count":
        originals = originals[:-1]
    head(*originals).save(os.fspath(workdir / "kirapy.symbolica"))
    _refresh_state_checksum(workdir)

    with pytest.raises(KiraWorkdirError, match="registry|alias counts"):
        runner.load(workdir)


def test_load_rejects_an_unknown_wire_alias_in_kira_output(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    family = topo1_project.family
    project = replace(
        topo1_project,
        targets=(family(1, 1, 1),),
        preferred_masters=(family(0, 1, 1),),
        check_masters=False,
    )
    runner = KiraRunner(fake_kira)
    prepared = runner.prepare(project, tmp_path / "unknown-wire")
    family_alias = next(
        alias for alias in prepared.files._alias_records if alias.kind == "family"
    )
    wire_target = f"{family_alias.wire_name}[1,1,1]"
    wire_master = f"{family_alias.wire_name}[0,1,1]"
    _write_result(
        prepared,
        left=wire_target,
        right=f"s000000001*{wire_master}",
        master=wire_master,
    )

    with pytest.raises(KiraWorkdirError, match="Unrestored Kira wire alias"):
        runner.load(workdir=prepared.workdir, project=project)


@pytest.mark.skipif(
    not os.environ.get("SYMBOLICA_LICENSE"),
    reason="subprocess Symbolica tests require a multi-core license",
)
def test_standalone_load_works_in_a_polluted_fresh_process(
    tmp_path: Path,
    topo1_project: KiraProject,
    fake_kira: Path,
) -> None:
    def callback_printer(_expression, **_options):
        return "CALLBACK_ONLY"

    callback_mass = S(
        "standalone_callback_mass",
        print=callback_printer,
    )
    original_mass = topo1_project.kinematics.kinematic_invariants[0].expression
    family = replace(
        topo1_project.family,
        propagators=tuple(
            replace(propagator, mass_squared=callback_mass)
            if propagator.mass_squared == original_mass
            else propagator
            for propagator in topo1_project.family.propagators
        ),
    )
    invariants = tuple(
        replace(invariant, expression=callback_mass)
        if invariant.expression == original_mass
        else invariant
        for invariant in topo1_project.kinematics.kinematic_invariants
    )
    kinematics = replace(
        topo1_project.kinematics,
        kinematic_invariants=invariants,
        symbol_to_replace_by_one=callback_mass,
    )
    project = replace(topo1_project, family=family, kinematics=kinematics)
    runner = KiraRunner(fake_kira)
    workdir = tmp_path / "fresh-process"
    expected = runner.reduce(project, workdir)
    script = f"""
import json
from symbolica import S
from kirapy import KiraRunner
S("pollution_z", "pollution_a", "pollution_m")
result = KiraRunner().load({os.fspath(workdir)!r})
print(json.dumps({{
    "family": result.family_name,
    "targets": len(result.requested_targets),
    "zeros": len(result.zero_integrals),
    "wire_survivors": sum(
        "kp_" in expression.format_plain()
        for expression in (*result.rules.keys(), *result.rules.values())
    ),
    "callback_originals": sum(
        "standalone_callback_mass" in expression.to_canonical_string()
        for expression in result.symbol_aliases.values()
    ),
}}))
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = "src"
    completed = subprocess.run(
        [sys.executable, "-c", script],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout.splitlines()[-1])

    assert payload == {
        "family": project.family.name,
        "targets": len(expected.requested_targets),
        "zeros": len(expected.zero_integrals),
        "wire_survivors": 0,
        "callback_originals": 1,
    }
