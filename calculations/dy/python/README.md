# Drell-Yan reduction and analytic masters in Python

This self-contained uv application is the Python counterpart of the sibling
[`DY_calculation.nb`](../mathematica/DY_calculation.nb) calculation.
It uses the repository's reusable
[`ludy-kira`](../../../packages/ludy-kira) package to reproduce the validated
topology-1 through topology-8, topology-10 through topology-11, and topology-20
through topology-31 IBP reductions with Kira.

The application contains two Marimo notebooks:

- `notebook.py` prepares, runs, resumes, and inspects the Kira reductions;
- `masters.py` derives and evaluates the closed-form `B`, `Bcut`, `Tcut`,
  `Bcutm`, and `Tcutm` basis used by the retained Mathematica substitutions,
  and owns the importable analytic master evaluator implementations used by
  the root cross-box walkthrough.

From the repository root:

```console
cd calculations/dy/python
nix develop
uv sync --locked
uv run --locked marimo edit notebook.py
uv run --locked marimo edit masters.py
```

Opening the notebook does not launch Kira. Each topology has separate persistent
state under `runs/dy-topoN/`, so an interrupted calculation can be resumed;
`runs/` is ignored by version control. Select a topology and press its
**Run the complete Kira reduction** button when ready. Topologies 10, 11, and
20–31 are backed by reproducibly regenerated and hashed FIRE evidence
documented in their
`packages/ludy-kira/tests/fixtures/fire_topoN/PROVENANCE.md` files.

Opening or exporting `masters.py` never launches Kira. It reconstructs the
Feynman-parameter, radial-delta, light-cone/Sudakov, angular-orbit, and
Gram-determinant pieces. It audits the supplied `master_and_dump.pdf`, keeps
physical phase-space and historical sign conventions separate, checks the
closed forms with exact Symbolica residuals, and displays them through the
Spenso-aware Typst/MathML renderer. It also provides configurable epsilon and
plus-distribution expansions, leading-virtuality integrations, and a positive
real numerical point. Its mapping table is deliberately limited to analytic
identifications explicitly present in the source notebook; other preferred
Kira masters remain unevaluated.

The repository-root `notebooks/ludy.py` imports the analytic evaluators from
`masters.py`; it does not maintain a second copy. This portable application's
`notebook.py` remains independently locked and does not import `ludy.py` or the
root multi-topology runner.

The local flake delegates its development shell to the standalone
`ludy-kira` subflake. That shell provides Python, uv, Kira, Fermat, and
`FERMATPATH`; uv installs Marimo, Symbolica, Typst, and the editable wrapper
package according to this application's lock file.

Validate both notebooks from this directory with:

```console
nix flake check
nix develop --command uv lock --check
nix develop --command uv run --locked marimo check --strict notebook.py
nix develop --command uv run --locked marimo check --strict masters.py
nix develop --command uv run --locked marimo export html masters.py \
  -o /tmp/ludy-dy-masters-validation.html --force
```
