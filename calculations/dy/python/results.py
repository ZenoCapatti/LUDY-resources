"""Plain-script reporting for the authoritative DY notebook result."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
from types import SimpleNamespace
from typing import Any, Iterator, Mapping, Sequence, TextIO


EXPECTED_KIRA_PROJECTS = 18
EXPECTED_POLE_RECORDS = 8
EXPECTED_COMPACT_RESIDUALS = 4
_EXPECTED_CHANNELS = ("qqbar", "q1g2", "g1q2", "qg_average")


def results_parser() -> argparse.ArgumentParser:
    """Return the CLI parser without evaluating any notebook cells."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the DY Marimo notebook headlessly or print its independently "
            "computed physical coefficient."
        )
    )
    parser.add_argument(
        "--results",
        action="store_true",
        help=(
            "print the native/AEM physical DY result; matching cached Kira "
            "reductions are loaded read-only by default"
        ),
    )
    parser.add_argument(
        "--run-reductions",
        action="store_true",
        help=(
            "with --results, explicitly run or resume every required Kira "
            "project"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="with --results, emit stable machine-readable JSON",
    )
    return parser


def _plain(expression: Any) -> str:
    """Render a Symbolica expression deterministically for text and JSON."""

    factored = expression.factor()
    formatter = getattr(factored, "format_plain", None)
    return formatter() if formatter is not None else str(factored)


def _endpoint_payload(coefficient: Any, variable: Any) -> dict[str, str]:
    """Return the four endpoint components of one exact coefficient."""

    canonical = coefficient.canonical(variable)
    return {
        "delta": _plain(canonical.delta),
        "D0": _plain(canonical.d0_prefactor),
        "D1": _plain(canonical.d1_prefactor),
        "regular": _plain(canonical.regular),
    }


def _format_endpoint(components: Mapping[str, str]) -> str:
    """Format one endpoint coefficient without Python container syntax."""

    return ", ".join(
        f"{name}={components[name]}"
        for name in ("delta", "D0", "D1", "regular")
    )


def build_results_payload(
    definitions: Mapping[str, Any],
    *,
    ran_reductions: bool,
) -> tuple[dict[str, Any], bool]:
    """Build a target-free report from the authoritative physical handoff."""

    projects = definitions["dy_kira_projects"]
    reductions = definitions["full_reductions"]
    completed = len(reductions)
    required = len(projects)
    coverage_complete = (
        completed == required == EXPECTED_KIRA_PROJECTS
    )
    physical = definitions.get("paper_dy_physical")
    context = definitions["dy_context"]

    payload: dict[str, Any] = {
        "calculation": "DY NLO physical coefficient",
        "mode": "run-reductions" if ran_reductions else "load-only",
        "coverage": {
            "completed": completed,
            "required": required,
            "expected": EXPECTED_KIRA_PROJECTS,
            "complete": coverage_complete,
        },
        "convention": None,
        "results": None,
        "checks": {
            "pole_sums": [],
            "pole_summary": {
                "zero": 0,
                "expected": EXPECTED_POLE_RECORDS,
                "complete": False,
            },
            "compact_residuals": {},
            "compact_summary": {
                "zero": 0,
                "expected": EXPECTED_COMPACT_RESIDUALS,
                "complete": False,
            },
            "paper_handoff_consistent": False,
            "reduction_audit": {
                "native_complete": False,
                "reference_targets_exact": False,
            },
            "analytic_masters": {
                "native_checks_exact": False,
                "finite_checks_exact": False,
                "residuals": {},
            },
        },
        "status": "FAIL",
    }
    if required != EXPECTED_KIRA_PROJECTS:
        payload["error"] = (
            "the DY project plan contains "
            f"{required} projects, expected {EXPECTED_KIRA_PROJECTS}"
        )
        return payload, False
    if not coverage_complete or physical is None:
        payload["error"] = (
            "compatible Kira reductions are incomplete "
            f"({completed}/{required}); rerun with --results "
            "--run-reductions"
        )
        return payload, False

    z = context.z
    payload["convention"] = {
        "normalization": physical.normalization_convention,
        "L12": "L_12(z) = log(Lambda_1^2*Lambda_2^2*z^2/s^2)",
        "G_i": "G_i(z) = log(s*(1-z)/(Lambda_i^2*z))",
    }
    payload["results"] = {
        "qqbar": _endpoint_payload(physical.qqbar_finite, z),
        "q1g2": {
            "regular": _plain(physical.qg_ordered_q1g2_finite),
        },
        "g1q2": {
            "regular": _plain(physical.qg_ordered_g1q2_finite),
        },
        "qg_average": {
            "regular": _plain(
                physical.qg_beam_exchange_average_finite
            ),
        },
    }

    pole_keys = {
        (record.channel, record.power) for record in physical.pole_records
    }
    expected_pole_keys = {
        (channel, power)
        for channel in _EXPECTED_CHANNELS
        for power in (-2, -1)
    }
    pole_shape_exact = (
        len(physical.pole_records) == EXPECTED_POLE_RECORDS
        and pole_keys == expected_pole_keys
    )
    pole_zero = 0
    for record in physical.pole_records:
        exact = record.physical_sum.is_zero_for(z)
        pole_zero += exact
        payload["checks"]["pole_sums"].append(
            {
                "channel": record.channel,
                "power": record.power,
                "sum": _endpoint_payload(record.physical_sum, z),
                "zero": exact,
            }
        )
    poles_exact = pole_shape_exact and pole_zero == EXPECTED_POLE_RECORDS
    payload["checks"]["pole_summary"] = {
        "zero": pole_zero,
        "expected": EXPECTED_POLE_RECORDS,
        "complete": poles_exact,
    }

    compact_shape_exact = (
        len(physical.compact_residuals) == EXPECTED_COMPACT_RESIDUALS
        and set(physical.compact_residuals) == set(_EXPECTED_CHANNELS)
    )
    compact_zero = 0
    for channel, residual in physical.compact_residuals.items():
        exact = residual.is_zero_for(z)
        compact_zero += exact
        payload["checks"]["compact_residuals"][channel] = {
            "residual": _endpoint_payload(residual, z),
            "zero": exact,
        }
    compact_exact = (
        compact_shape_exact
        and compact_zero == EXPECTED_COMPACT_RESIDUALS
    )
    payload["checks"]["compact_summary"] = {
        "zero": compact_zero,
        "expected": EXPECTED_COMPACT_RESIDUALS,
        "complete": compact_exact,
    }

    handoff_exact = physical.internally_consistent(
        z,
        context.epsilon,
    )
    payload["checks"]["paper_handoff_consistent"] = handoff_exact

    audit = definitions.get("full_audit")
    audit_native_exact = bool(audit is not None and audit.native_complete)
    audit_reference_exact = bool(
        audit is not None and audit.reference_targets_exact
    )
    payload["checks"]["reduction_audit"] = {
        "native_complete": audit_native_exact,
        "reference_targets_exact": audit_reference_exact,
    }

    full_dy = definitions.get("full_dy")
    master_handoff = (
        full_dy.master_handoff if full_dy is not None else None
    )
    master_native_exact = bool(
        master_handoff is not None
        and master_handoff.native_checks_exact(z)
    )
    master_finite_exact = bool(
        master_handoff is not None
        and master_handoff.finite_checks_exact(z)
    )
    master_residuals: dict[str, Any] = {}
    if master_handoff is not None:
        master_residuals = {
            "direct_finite": _plain(master_handoff.direct_finite_residual),
            "qg_finite": _plain(master_handoff.qg_finite_residual),
            "external_bubble": _endpoint_payload(
                master_handoff.external_bubble_expected_residual,
                z,
            ),
            "crossed_poles": {
                str(power): _endpoint_payload(residual, z)
                for power, residual in sorted(
                    master_handoff.crossed_pole_residuals.items()
                )
            },
            "crossed_finite": _endpoint_payload(
                master_handoff.crossed_finite_residual,
                z,
            ),
        }
    payload["checks"]["analytic_masters"] = {
        "native_checks_exact": master_native_exact,
        "finite_checks_exact": master_finite_exact,
        "residuals": master_residuals,
    }
    succeeded = (
        coverage_complete
        and poles_exact
        and compact_exact
        and handoff_exact
        and audit_native_exact
        and audit_reference_exact
        and master_native_exact
        and master_finite_exact
    )
    payload["status"] = "PASS" if succeeded else "FAIL"
    if not succeeded:
        payload["error"] = "one or more exact DY checks failed"
    return payload, succeeded


def print_results(payload: Mapping[str, Any], *, stream: TextIO) -> None:
    """Print the exact DY report in a compact reader-facing format."""

    print(payload["calculation"], file=stream)
    print(f"mode: {payload['mode']}", file=stream)
    coverage = payload["coverage"]
    print(
        "Kira coverage: "
        f"{coverage['completed']}/{coverage['required']} compatible projects",
        file=stream,
    )
    if payload["results"] is None:
        print(f"error: {payload['error']}", file=stream)
        print("status: FAIL", file=stream)
        return

    convention = payload["convention"]
    print(f"normalization: {convention['normalization']}", file=stream)
    print(convention["L12"], file=stream)
    print(convention["G_i"], file=stream)
    print("results:", file=stream)
    for channel, components in payload["results"].items():
        print(f"  {channel}:", file=stream)
        for component, value in components.items():
            print(f"    {component}: {value}", file=stream)

    print("pole sums:", file=stream)
    for record in payload["checks"]["pole_sums"]:
        status = "zero" if record["zero"] else "NONZERO"
        print(
            f"  {record['channel']} epsilon^{record['power']}: "
            f"{_format_endpoint(record['sum'])} ({status})",
            file=stream,
        )
    pole_summary = payload["checks"]["pole_summary"]
    print(
        "  summary: "
        f"{pole_summary['zero']}/{pole_summary['expected']} zero",
        file=stream,
    )

    print(
        "compact residuals (native physical - paper form):",
        file=stream,
    )
    for channel, record in payload["checks"][
        "compact_residuals"
    ].items():
        status = "zero" if record["zero"] else "NONZERO"
        print(
            f"  {channel}: {_format_endpoint(record['residual'])} ({status})",
            file=stream,
        )
    compact_summary = payload["checks"]["compact_summary"]
    print(
        "  summary: "
        f"{compact_summary['zero']}/{compact_summary['expected']} zero",
        file=stream,
    )
    reduction = payload["checks"]["reduction_audit"]
    print(
        "reduction audit: "
        + (
            "native exact; reference residuals zero"
            if reduction["native_complete"]
            and reduction["reference_targets_exact"]
            else "FAILED"
        ),
        file=stream,
    )
    masters = payload["checks"]["analytic_masters"]
    print(
        "analytic-master handoff: "
        + (
            "native and finite residuals zero"
            if masters["native_checks_exact"]
            and masters["finite_checks_exact"]
            else "FAILED"
        ),
        file=stream,
    )
    print(f"status: {payload['status']}", file=stream)


def _runtime_failure_payload(
    error: Exception,
    *,
    ran_reductions: bool,
) -> dict[str, Any]:
    """Return the normal report envelope when app execution raises."""

    return {
        "calculation": "DY NLO physical coefficient",
        "mode": "run-reductions" if ran_reductions else "load-only",
        "coverage": {
            "completed": None,
            "required": EXPECTED_KIRA_PROJECTS,
            "expected": EXPECTED_KIRA_PROJECTS,
            "complete": False,
        },
        "convention": None,
        "results": None,
        "checks": {
            "pole_sums": [],
            "pole_summary": {
                "zero": 0,
                "expected": EXPECTED_POLE_RECORDS,
                "complete": False,
            },
            "compact_residuals": {},
            "compact_summary": {
                "zero": 0,
                "expected": EXPECTED_COMPACT_RESIDUALS,
                "complete": False,
            },
            "paper_handoff_consistent": False,
            "reduction_audit": {
                "native_complete": False,
                "reference_targets_exact": False,
            },
            "analytic_masters": {
                "native_checks_exact": False,
                "finite_checks_exact": False,
                "residuals": {},
            },
        },
        "error": f"notebook execution failed: {error}",
        "status": "FAIL",
    }


@contextlib.contextmanager
def _app_stdout_on_stderr() -> Iterator[None]:
    """Route Python and subprocess stdout to stderr while the app runs."""

    sys.stdout.flush()
    saved_stdout = os.dup(sys.stdout.fileno())
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
    try:
        with contextlib.redirect_stdout(sys.stderr):
            yield
    finally:
        sys.stdout.flush()
        os.dup2(saved_stdout, sys.stdout.fileno())
        os.close(saved_stdout)


def run_results(
    app: Any,
    *,
    run_reductions: bool,
    json_output: bool,
) -> int:
    """Evaluate the app once and report only authoritative computed results."""

    # The override skips only the run-button cell.  Its boolean value drives
    # the existing run-versus-read-only-load branch used by the interactive UI.
    try:
        with _app_stdout_on_stderr():
            _, definitions = app.run(
                defs={
                    "run_full_dy": SimpleNamespace(value=run_reductions),
                }
            )

        payload, succeeded = build_results_payload(
            definitions,
            ran_reductions=run_reductions,
        )
    except Exception as error:
        print(f"DY result reproduction failed: {error}", file=sys.stderr)
        payload = _runtime_failure_payload(
            error,
            ran_reductions=run_reductions,
        )
        succeeded = False
    if json_output:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        print()
    else:
        print_results(payload, stream=sys.stdout)
    return 0 if succeeded else 1


def main(app: Any, argv: Sequence[str] | None = None) -> int:
    """Dispatch normal headless execution and the explicit results mode."""

    parser = results_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    result_only_options = args.run_reductions or args.json
    if result_only_options and not args.results:
        parser.error("--run-reductions and --json require --results")
    if not args.results:
        app.run()
        return 0
    return run_results(
        app,
        run_reductions=args.run_reductions,
        json_output=args.json,
    )


__all__ = [
    "EXPECTED_KIRA_PROJECTS",
    "EXPECTED_COMPACT_RESIDUALS",
    "EXPECTED_POLE_RECORDS",
    "build_results_payload",
    "main",
    "print_results",
    "results_parser",
    "run_results",
]
