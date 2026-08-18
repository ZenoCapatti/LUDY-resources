# Drell-Yan reduction in Python

This self-contained uv application is the Python counterpart of the sibling
[`DY_calculation.nb`](../mathematica/DY_calculation.nb) calculation.
It uses the repository's reusable
[`ludy-kira`](../../../packages/ludy-kira) package to reproduce the validated
topology-1 through topology-8, topology-10 through topology-11, and topology-20
through topology-31 IBP reductions with Kira.

From the repository root:

```console
cd calculations/dy/python
nix develop
uv sync --locked
uv run --locked marimo edit notebook.py
```

Opening the notebook does not launch Kira. Each topology has separate persistent
state under `runs/dy-topoN/`, so an interrupted calculation can be resumed;
`runs/` is ignored by version control. Select a topology and press its
**Run the complete Kira reduction** button when ready. Topologies 10, 11, and
20–31 are backed by reproducibly regenerated and hashed FIRE evidence
documented in their
`packages/ludy-kira/tests/fixtures/fire_topoN/PROVENANCE.md` files.

The local flake delegates its development shell to the standalone
`ludy-kira` subflake. That shell provides Python, uv, Kira, Fermat, and
`FERMATPATH`; uv installs Marimo and the editable wrapper package according to
this application's lock file.
