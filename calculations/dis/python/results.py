"""Plain-command reporting for the executable DIS Marimo notebook.

This module is deliberately downstream of the notebook calculation.  It only
selects whether the existing Kira run controls are active, executes the app,
and serializes definitions produced by the native calculation.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stdout
import json
import os
from types import SimpleNamespace
from typing import Any, Iterator, Mapping, Sequence, TextIO
import sys


_FUNCTION_NAMES = ("F2q", "F2g", "FLq", "FLg")
_EXPECTED_ORDINARY_PROJECTS = 16
_EXPECTED_RAISED_PROJECTS = 2


@contextmanager
def app_stdout_on_stderr() -> Iterator[None]:
    """Route Python and native/subprocess stdout to stderr temporarily."""

    sys.stdout.flush()
    saved_stdout = os.dup(sys.stdout.fileno())
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
    try:
        with redirect_stdout(sys.stderr):
            yield
    finally:
        sys.stdout.flush()
        os.dup2(saved_stdout, sys.stdout.fileno())
        os.close(saved_stdout)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the DIS notebook headlessly or print its independently "
            "assembled native result."
        )
    )
    parser.add_argument(
        "--results",
        action="store_true",
        help=(
            "print the native DIS coefficients and exact validation checks; "
            "matching cached Kira reductions are required"
        ),
    )
    parser.add_argument(
        "--run-reductions",
        action="store_true",
        help=(
            "with --results, explicitly run or resume all 16 ordinary and "
            "2 raised-external Kira projects"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="with --results, emit the same report as deterministic JSON",
    )
    return parser


def print_dis_notebook_help() -> None:
    """Print CLI help without evaluating the notebook's app cells."""

    _parser().print_help()


def _plain(value: Any) -> str:
    formatter = getattr(value, "format_plain", None)
    return formatter() if formatter is not None else str(value)


def _plus(coefficient: Any, order: int) -> Any:
    if order < len(coefficient.plus):
        return coefficient.plus[order]
    # delta - delta is a typed zero in the same symbolic engine.
    return coefficient.delta - coefficient.delta


def _distribution_payload(coefficient: Any) -> dict[str, Any]:
    return {
        "delta": _plain(coefficient.delta),
        "D0": _plain(_plus(coefficient, 0)),
        "D1": _plain(_plus(coefficient, 1)),
        "regular": _plain(coefficient.regular),
    }


def _structure_payload(functions: Any) -> dict[str, Any]:
    return {
        name: _distribution_payload(getattr(functions, name))
        for name in _FUNCTION_NAMES
    }


def _paper_residuals(definitions: Mapping[str, Any], native_result: Any):
    """Compare the normalized native result with the downstream paper model."""

    paper_targets = definitions.get("PAPER_TARGETS")
    symbols = definitions.get("dis_symbols")
    if paper_targets is None or symbols is None:
        return None
    target_functions = paper_targets.functions

    electric_charge, _strong_coupling, alpha_s = symbols["couplings"]
    color_f, color_t, _color_count = symbols["colour"]
    variable = symbols["Bjorken variable"]
    photon_scale = symbols["photon scale"]
    cutoff = symbols["virtuality cutoff"]
    pi = symbols["pi"]
    common = electric_charge**2 * alpha_s * variable / (2 * pi)
    factors = {
        "F2q": common * color_f,
        "F2g": common * color_t,
        "FLq": common * color_f,
        "FLg": common * color_t,
    }
    cutoff_log = (photon_scale / cutoff).log()
    expanded_cutoff_log = photon_scale.log() - cutoff.log()

    def normalize_cutoff_log(coefficient: Any) -> Any:
        coefficient_type = type(coefficient)

        def normalize(expression: Any) -> Any:
            return (
                expression.replace(cutoff_log, expanded_cutoff_log)
                .expand()
                .together()
                .cancel()
            )

        return coefficient_type(
            variable=coefficient.variable,
            delta=normalize(coefficient.delta),
            plus=tuple(normalize(value) for value in coefficient.plus),
            regular=normalize(coefficient.regular),
        )

    return {
        name: normalize_cutoff_log(
            getattr(native_result.brackets, name).multiply_smooth(factors[name])
            - getattr(target_functions, name)
        )
        for name in _FUNCTION_NAMES
    }


def _build_report(
    definitions: Mapping[str, Any],
    *,
    ran_reductions: bool,
) -> tuple[dict[str, Any], bool]:
    ordinary_projects = definitions.get("smoke_projects", {})
    ordinary_reductions = definitions.get("kira_reductions", {})
    raised_projects = definitions.get("raised_external_projects", {})
    raised_reductions = definitions.get("raised_kira_reductions", {})
    raised_audits = definitions.get("raised_external_audits", ())
    physical_audit = definitions.get("physical_reduction_audit")
    master_audit = definitions.get("master_insertion_audit")
    native_result = definitions.get("native_mp_result")
    validation_ledger = definitions.get("validation_ledger")

    ordinary_complete = sum(
        bool(result.complete) for result in ordinary_reductions.values()
    )
    raised_complete = sum(
        bool(result.complete) for result in raised_reductions.values()
    )
    ordinary_required = len(ordinary_projects)
    raised_required = len(raised_projects)
    ordinary_exact = (
        ordinary_required == _EXPECTED_ORDINARY_PROJECTS
        and set(ordinary_reductions) == set(ordinary_projects)
        and ordinary_complete == ordinary_required
    )
    raised_exact = (
        raised_required == _EXPECTED_RAISED_PROJECTS
        and set(raised_reductions) == set(raised_projects)
        and raised_complete == raised_required
    )

    failures: list[str] = []
    if ordinary_required != _EXPECTED_ORDINARY_PROJECTS:
        failures.append(
            "the ordinary DIS project plan contains "
            f"{ordinary_required} projects, expected "
            f"{_EXPECTED_ORDINARY_PROJECTS}"
        )
    if (
        ordinary_required == _EXPECTED_ORDINARY_PROJECTS
        and not ordinary_exact
    ):
        failures.append(
            "compatible ordinary Kira reductions are incomplete "
            f"({ordinary_complete}/{ordinary_required})"
        )
    if raised_required != _EXPECTED_RAISED_PROJECTS:
        failures.append(
            "the raised-external DIS project plan contains "
            f"{raised_required} projects, expected "
            f"{_EXPECTED_RAISED_PROJECTS}"
        )
    if raised_required == _EXPECTED_RAISED_PROJECTS and not raised_exact:
        failures.append(
            "compatible raised-external Kira reductions are incomplete "
            f"({raised_complete}/{raised_required})"
        )
    if physical_audit is None or not physical_audit.exact:
        failures.append("the projected-numerator reduction audit is not exact")
    if master_audit is None or not master_audit.exact:
        failures.append("the 32-record analytic-master boundary is not exact")

    raised_residuals = {
        f"{audit.project_key}:{audit.graph_name}:{audit.observable}": audit.residual
        for audit in raised_audits
    }
    raised_zero = sum(
        _plain(residual) == "0" for residual in raised_residuals.values()
    )
    if len(raised_residuals) != 4 or raised_zero != 4:
        failures.append(
            "raised-external coefficient residuals are not all zero "
            f"({raised_zero}/4)"
        )

    results_payload = None
    pole_payload: dict[str, Any] = {}
    pole_zero = 0
    paper_payload: dict[str, Any] = {}
    paper_zero = 0
    if native_result is None:
        failures.append("the authoritative native DIS result is unavailable")
    else:
        results_payload = _structure_payload(native_result.brackets)
        for power in (-2, -1):
            functions = native_result.laurent[power]
            power_payload = _structure_payload(functions)
            pole_payload[str(power)] = power_payload
            pole_zero += sum(
                getattr(functions, name).is_zero for name in _FUNCTION_NAMES
            )
        if pole_zero != 8 or not native_result.poles_cancel:
            failures.append(
                "dimensional poles do not all cancel " f"({pole_zero}/8 zero)"
            )
        if not native_result.raised_external_exact:
            failures.append("the native raised-cut endpoint identities are not exact")

        paper_residuals = _paper_residuals(definitions, native_result)
        if paper_residuals is None:
            failures.append("the downstream manuscript comparison is unavailable")
        else:
            paper_payload = {
                name: _distribution_payload(residual)
                for name, residual in paper_residuals.items()
            }
            paper_zero = sum(
                residual.is_zero for residual in paper_residuals.values()
            )
            if paper_zero != 4:
                failures.append(
                    "native-minus-paper residuals are not all zero "
                    f"({paper_zero}/4)"
                )

    ledger_validated = bool(
        validation_ledger is not None
        and validation_ledger.physical_result_validated
    )
    if not ledger_validated:
        failures.append("the consolidated physical validation ledger did not pass")

    report = {
        "calculation": "DIS NLO LU/MP",
        "mode": "run-reductions" if ran_reductions else "load-only",
        "convention": {
            "coupling": "a_s = alpha_s/(2*pi)",
            "expansion": "F = F^(0) + a_s F^(1) + O(a_s^2)",
            "cutoff_log": "L = log(Q^2/Lambda^2)",
            "normalization": (
                "F_i,a^(1) = e_q^2*x*C_a*M_i,a, "
                "C_q=C_F, C_g=T_F"
            ),
        },
        "results": results_payload,
        "checks": {
            "kira": {
                "ordinary": {
                    "complete": ordinary_complete,
                    "required": ordinary_required,
                    "expected": _EXPECTED_ORDINARY_PROJECTS,
                },
                "raised": {
                    "complete": raised_complete,
                    "required": raised_required,
                    "expected": _EXPECTED_RAISED_PROJECTS,
                },
            },
            "projected_numerator_reductions_exact": bool(
                physical_audit is not None and physical_audit.exact
            ),
            "master_insertions_exact": bool(
                master_audit is not None and master_audit.exact
            ),
            "poles": {
                "zero": pole_zero,
                "expected": 8,
                "residuals": pole_payload,
            },
            "raised_external": {
                "zero": raised_zero,
                "expected": 4,
                "residuals": {
                    name: _plain(value)
                    for name, value in sorted(raised_residuals.items())
                },
            },
            "native_minus_paper": {
                "zero": paper_zero,
                "expected": 4,
                "residuals": paper_payload,
            },
            "physical_validation_ledger": ledger_validated,
        },
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    return report, not failures


def _write_text(report: Mapping[str, Any], stream: TextIO) -> None:
    print(report["calculation"], file=stream)
    print(f"mode: {report['mode']}", file=stream)
    convention = report["convention"]
    print(f"convention: {convention['expansion']}", file=stream)
    print(convention["coupling"], file=stream)
    print(convention["cutoff_log"], file=stream)
    print(f"normalization: {convention['normalization']}", file=stream)
    print(file=stream)

    results = report["results"]
    if results is not None:
        for name in _FUNCTION_NAMES:
            index = name[1]
            parton = name[2].lower()
            label = f"M_{index},{parton} ({name})"
            coefficient = results[name]
            print(f"{label}:", file=stream)
            print(f"  delta(1-x) = {coefficient['delta']}", file=stream)
            print(f"  D0(x)      = {coefficient['D0']}", file=stream)
            print(f"  D1(x)      = {coefficient['D1']}", file=stream)
            print(f"  regular    = {coefficient['regular']}", file=stream)
            print(file=stream)

    checks = report["checks"]
    ordinary = checks["kira"]["ordinary"]
    raised = checks["kira"]["raised"]
    print("checks:", file=stream)
    print(
        "  Kira ordinary reductions: "
        f"{ordinary['complete']}/{ordinary['expected']}",
        file=stream,
    )
    print(
        "  Kira raised reductions:   "
        f"{raised['complete']}/{raised['expected']}",
        file=stream,
    )
    print(
        "  projected numerators:     "
        + ("exact" if checks["projected_numerator_reductions_exact"] else "FAILED"),
        file=stream,
    )
    print(
        "  analytic master boundary: "
        + ("exact" if checks["master_insertions_exact"] else "FAILED"),
        file=stream,
    )
    print(
        "  dimensional poles:        "
        f"{checks['poles']['zero']}/{checks['poles']['expected']} zero",
        file=stream,
    )
    print(
        "  raised-cut residuals:      "
        f"{checks['raised_external']['zero']}/"
        f"{checks['raised_external']['expected']} zero",
        file=stream,
    )
    paper = checks["native_minus_paper"]
    if paper["residuals"]:
        paper_summary = " ".join(
            f"{name}={'0' if all(value == '0' for value in residual.values()) else 'nonzero'}"
            for name, residual in paper["residuals"].items()
        )
    else:
        paper_summary = "unavailable"
    print(f"  native - paper:            {paper_summary}", file=stream)
    print(
        "  validation ledger:        "
        + ("exact" if checks["physical_validation_ledger"] else "FAILED"),
        file=stream,
    )
    if report["failures"]:
        print(file=stream)
        print("failures:", file=stream)
        for failure in report["failures"]:
            print(f"  - {failure}", file=stream)
    print(file=stream)
    print(f"status: {report['status']}", file=stream)


def run_dis_notebook_cli(
    app: Any,
    marimo_module: Any,
    argv: Sequence[str] | None = None,
) -> int:
    """Run the notebook normally, or emit its strict native-result report."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments:
        # Supplying ``mo`` fixes direct execution while retaining the existing
        # false-by-default run buttons and cache-loading behavior.
        app.run(defs={"mo": marimo_module})
        return 0

    parser = _parser()
    options = parser.parse_args(arguments)
    if not options.results:
        parser.error("--run-reductions and --json require --results")

    run_control = SimpleNamespace(value=options.run_reductions)
    definitions: Mapping[str, Any]
    try:
        # Marimo and Kira may report progress.  Result stdout remains a stable
        # human- or machine-readable stream by routing that progress to stderr.
        with app_stdout_on_stderr():
            _outputs, definitions = app.run(
                defs={
                    "mo": marimo_module,
                    "run_kira": run_control,
                    "run_raised_kira": run_control,
                }
            )
        report, success = _build_report(
            definitions,
            ran_reductions=options.run_reductions,
        )
    except Exception as error:
        report = {
            "calculation": "DIS NLO LU/MP",
            "mode": (
                "run-reductions" if options.run_reductions else "load-only"
            ),
            "results": None,
            "failures": [f"notebook execution failed: {error}"],
            "status": "FAIL",
        }
        success = False
        print(f"DIS result reproduction failed: {error}", file=sys.stderr)

    if options.json_output:
        json.dump(report, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
        print()
    elif "checks" in report:
        _write_text(report, sys.stdout)
    else:
        print("DIS NLO LU/MP result", file=sys.stdout)
        print(file=sys.stdout)
        print(f"status: {report['status']}", file=sys.stdout)
        for failure in report["failures"]:
            print(f"error: {failure}", file=sys.stderr)
    return 0 if success else 1


__all__ = [
    "app_stdout_on_stderr",
    "print_dis_notebook_help",
    "run_dis_notebook_cli",
]
