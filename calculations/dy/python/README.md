# Drell-Yan reduction in Python

This self-contained uv application is the Python counterpart of the sibling
[`DY_calculation.nb`](../mathematica/DY_calculation.nb) calculation.
It uses the repository's reusable
[`ludy-kira`](../../../packages/ludy-kira) package to reproduce the topology-1
IBP reduction with Kira.

From the repository root:

```console
cd calculations/dy/python
nix develop
uv sync --locked
uv run --locked marimo edit notebook.py
```

Opening the notebook does not launch Kira. Reduction state is persisted below
`runs/dy-topo1/`, so an interrupted calculation can be resumed; `runs/` is
ignored by version control. Press **Run the complete Kira reduction** in the
notebook when ready.

The local flake delegates its development shell to the standalone
`ludy-kira` subflake. That shell provides Python, uv, Kira, Fermat, and
`FERMATPATH`; uv installs Marimo and the editable wrapper package according to
this application's lock file.
