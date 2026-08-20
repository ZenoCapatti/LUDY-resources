import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    from ludy import (
        build_kira_projects,
        momentum_printer,
        run_kira_projects,
        spenso_table,
    )
    from kirapy import Kira
    from symbolica import N, S
    from symbolica.community.spenso import Representation, TensorName

    return (
        Kira,
        N,
        Path,
        Representation,
        S,
        TensorName,
        build_kira_projects,
        mo,
        momentum_printer,
        run_kira_projects,
        spenso_table,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DY cross-box topology runner

    This companion notebook is a small control surface for the twelve Kira
    families used by the cross-box walkthrough.  The project builder and
    resumable runner are imported directly from [`ludy.py`](ludy.py), which
    remains the source of their implementations and the worked cross-box test.

    Project construction is side-effect free and uses the same native rank-one
    Spenso momenta, Minkowski representation, project builder, and shared
    `runs/dy-cross-box-kirapy/` workdirs as the walkthrough. Select any
    combination of graph-order families, inspect the exact project definitions,
    and use the run control below when you deliberately want to start or resume
    Kira. Merely importing, checking, or exporting this notebook never launches
    Kira.
    """)
    return


@app.cell
def _(
    N,
    Path,
    Representation,
    S,
    TensorName,
    build_kira_projects,
    momentum_printer,
):
    _minkd = Representation.mink(dimension=S("D"))
    _p = TensorName.vector("p", print=momentum_printer("p"))
    _k = TensorName.vector(
        "k",
        tags=["ludy::loop_momentum"],
        print=momentum_printer("k"),
    )
    p1 = _p(1, _minkd)
    p2 = _p(2, _minkd)
    k1 = _k(1, _minkd)
    q = S("q")
    _zero = N(0)
    propagators = [
        (p1, _zero),
        (p2, _zero),
        (k1, _zero),
        (k1 - p1, _zero),
        (p2 - k1, _zero),
        (p1 + p2 - k1, q**2),
    ]
    cutsets = {
        "11": (1, 1, 1, 0, 0, 1),
        "10": (1, 0, 1, 0, 1, 1),
        "01": (0, 1, 1, 1, 0, 1),
        "00": (0, 0, 1, 1, 1, 1),
    }
    topology_projects = build_kira_projects(
        k1=k1,
        p1=p1,
        p2=p2,
        q=q,
        propagators=propagators,
        cutsets=cutsets,
    )
    project_keys_by_name = {
        project.family.name: project_key
        for project_key, project in topology_projects.items()
    }
    project_names = sorted(project_keys_by_name)
    topology_workdir_root = (
        Path(__file__).resolve().parents[1]
        / "runs"
        / "dy-cross-box-kirapy"
    )
    return (
        project_keys_by_name,
        project_names,
        topology_projects,
        topology_workdir_root,
    )


@app.cell(hide_code=True)
def _(mo, project_names):
    topology_selector = mo.ui.multiselect(
        options=project_names,
        value=project_names,
        label="Kira families to inspect and run",
        full_width=True,
    )
    topology_selector
    return (topology_selector,)


@app.cell
def _(
    mo,
    project_keys_by_name,
    spenso_table,
    topology_projects,
    topology_selector,
    topology_workdir_root,
):
    selected_project_names = sorted(topology_selector.value)
    selected_topology_projects = {
        project_keys_by_name[_name]: topology_projects[
            project_keys_by_name[_name]
        ]
        for _name in selected_project_names
    }

    _project_rows = [
        {
            "cut": _project_key[0],
            "family": _project.family.name,
            "graph sources": [
                f"D{_source + 1}" for _source in _project_key[1]
            ],
            "propagator momenta": [
                _propagator.momentum
                for _propagator in _project.family.propagators
            ],
            "mass squared": [
                _propagator.mass_squared
                for _propagator in _project.family.propagators
            ],
            "targets": len(_project.targets),
            "preferred masters": list(_project.preferred_masters),
            "reconstruct mass": _project.reconstruct_mass,
            "workdir": str(
                topology_workdir_root / _project.family.name
            ),
        }
        for _project_key, _project in selected_topology_projects.items()
    ]
    if _project_rows:
        _inspection = spenso_table(
            _project_rows,
            selection=None,
            pagination=True,
            page_size=12,
        )
    else:
        _inspection = mo.callout(
            "Select at least one topology to inspect it.",
            kind="neutral",
        )
    _inspection
    return selected_project_names, selected_topology_projects


@app.cell(hide_code=True)
def _(mo, selected_project_names):
    _selection = ", ".join(selected_project_names)
    run_selected_topologies = mo.ui.run_button(
        label=(
            f"Run/resume selected Kira projects ({_selection})"
            if _selection
            else "Select a Kira project before running"
        ),
        disabled=not selected_project_names,
        kind="warn",
        full_width=True,
    )
    run_selected_topologies
    return (run_selected_topologies,)


@app.cell
def _(
    Kira,
    run_kira_projects,
    run_selected_topologies,
    selected_topology_projects,
    topology_workdir_root,
):
    if run_selected_topologies.value:
        topology_kira_doctor, topology_kira_reductions = run_kira_projects(
            Kira(),
            selected_topology_projects,
            topology_workdir_root,
        )
    else:
        topology_kira_doctor = None
        topology_kira_reductions = {}
    return topology_kira_doctor, topology_kira_reductions


@app.cell(hide_code=True)
def _(mo, spenso_table, topology_kira_doctor, topology_kira_reductions):
    if topology_kira_doctor is None:
        _run_status = mo.callout(
            "Ready. No Kira subprocess has been started by this notebook run.",
            kind="neutral",
        )
    else:
        _result_rows = [
            {
                "family": _reduction.family_name,
                "complete": _reduction.complete,
                "rules": len(_reduction.rules),
                "masters": list(_reduction.masters),
                "missing targets": len(_reduction.missing_targets),
                "unresolved integrals": len(_reduction.unresolved_integrals),
                "workdir": str(_reduction.workdir),
            }
            for _project_key, _reduction in sorted(
                topology_kira_reductions.items()
            )
        ]
        _run_status = mo.vstack(
            [
                mo.callout(
                    f"Kira {topology_kira_doctor.version} completed the "
                    f"{len(_result_rows)} selected project(s).",
                    kind="success",
                ),
                spenso_table(
                    _result_rows,
                    selection=None,
                    pagination=True,
                    page_size=12,
                ),
            ]
        )
    _run_status
    return


if __name__ == "__main__":
    app.run()
