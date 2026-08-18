from __future__ import annotations

import json
import os
import sys
import textwrap
from dataclasses import replace
from pathlib import Path

import pytest

from ludy_kira.errors import (
    KiraOutputError,
    KiraRunError,
    KiraTimeoutError,
    KiraWorkdirError,
)
from ludy_kira.models import KiraProject
from ludy_kira.runner import KiraRunner


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
                "custom": os.environ.get("LUDY_KIRA_FAKE_VALUE"),
            }}), encoding="utf-8")
            mode = os.environ.get("LUDY_KIRA_FAKE_MODE", "success")
            print(f"fake Kira mode={{mode}}", flush=True)
            if mode == "sleep":
                time.sleep(30)
            if mode == "fail":
                raise SystemExit(7)
            if mode == "missing-output":
                raise SystemExit(0)

            targets = [line.strip() for line in Path("targets").read_text().splitlines() if line.strip()]
            result_dir = Path("results/topo1")
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
    assert (workdir / "ludy-kira.json").is_file()
    assert (workdir / "config/integralfamilies.yaml").is_file()
    assert (workdir / "config/kinematics.yaml").is_file()
    assert (workdir / "jobs.yaml").is_file()
    manifest = json.loads((workdir / "ludy-kira.json").read_text(encoding="utf-8"))
    assert manifest["project"]["family_name"] == "topo1"
    assert manifest["project"]["arity"] == 3
    assert set(manifest["project"]["input_hashes"]) == set(prepared.files)

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
        env={"LUDY_KIRA_FAKE_VALUE": "forwarded"},
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
    runner = KiraRunner(fake_kira, env={"LUDY_KIRA_FAKE_MODE": "fail"})
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
    runner = KiraRunner(fake_kira, env={"LUDY_KIRA_FAKE_MODE": "sleep"})
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
    runner = KiraRunner(fake_kira, env={"LUDY_KIRA_FAKE_MODE": "missing-output"})

    with pytest.raises(KiraOutputError, match="did not create"):
        runner.reduce(topo1_project, tmp_path / "run")
