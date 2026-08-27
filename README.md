# LUDY research workspace

This repository is a small research monorepo. Reusable Python code lives under
`packages/`, complete calculations live under `calculations/`, and general
interactive experiments live under `notebooks/`.

```text
packages/
  kirapy/                     reusable Python wrapper and pinned Kira runtime
calculations/
  dis/
    ancillary/                 official arXiv fixture provenance and schema
    python/                    DIS source model, masters, and validation notebook
  dy/
    mathematica/              original DY calculation and FIRE reference data
    python/                   Kira and analytic-master notebooks
notebooks/
  ludy.py                     physical/editable cross-box and all shared helpers
  collinear-cone.py           independent cone visualization
docs/symbolica-fork.md        Symbolica pin and state-round-trip scope
reproducers/                  standalone dependency-regression programs
pyproject.toml, flake.nix     shared environment for every Marimo notebook
```

The two DY implementations are intentionally siblings. The Mathematica tree
retains the scientific source and historical FIRE fixtures; the Python
application recreates the reduction through the reusable `kirapy` package.
See [`calculations/dy/README.md`](calculations/dy/README.md) for the mapping
between them.

[`calculations/dis`](calculations/dis) is a focused NLO DIS paper-validation
workspace. It transcribes the six printed graph integrands, derives projected
numerators with Spenso, records the analytic one-loop master basis, and builds
cut-specialized Kira smoke projects. Its validation ledger keeps the missing
cut weights, graph-level IBP coefficients, and integrated channel results
explicit, so this scaffold does not claim a completed physical coefficient.

## Run the notebooks

All Marimo notebooks use the repository-root uv lock and Nix shell. The root
environment includes the editable `packages/kirapy` checkout, the sibling
GammaLoop and Symbolica Community checkouts, and the pinned Kira/Fermat
runtime:

```console
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit notebooks/ludy.py
$ uv run --locked marimo edit notebooks/collinear-cone.py
$ uv run --locked marimo edit calculations/dy/python/notebook.py
$ uv run --locked marimo edit calculations/dy/python/masters.py
$ uv run --locked marimo edit calculations/dis/python/notebook.py
```

The DY `notebook.py` defines the full editable graph/routing/numerator set and
does not launch Kira until its batch run button is pressed. `masters.py` derives and evaluates the
closed-form `B`, `Bcut`, `Tcut`, `Bcutm`, `Tcutm`, and maximal-cut `M00` basis
in radial and light-cone coordinates, with exact normalization, virtuality, and
soft-endpoint checks, without launching Kira or reading a reduction work
directory.

The DIS notebook executes the source-transcription and native-algebra layers:
six graph traces and their projectors, a four-child Symbolica crossed-box
partial fraction, 18 exact numerator-reconstruction checks, 15 structurally
compatible all-cut sectors, and 16 serializable cut-specialized Kira smoke
projects. It also displays the paper and reusable `B`, `Bcut`, and `Tcut`
masters and an explicit validation ledger. Kira runs only when its button is
pressed, and those smoke reductions are not assembled into a physical DIS
result.

The bundled native runtime currently supports x86-64 Linux and Apple Silicon
macOS. Other systems can use the same notebooks with a separately installed
Kira 3.1-compatible executable.

## Reusable Kira wrapper

[`packages/kirapy`](packages/kirapy) is an independently locked uv/Nix
project. Its wheel contains only the Python interface; Kira and Fermat are
external executables supplied by its Nix shell or configured by the user.

```console
$ cd packages/kirapy
$ nix develop
$ uv sync --locked
$ uv run --locked pytest
```

The wrapper exposes deterministic Kira project generation, resumable runs,
exact Symbolica parsing, and completeness checks. Native Symbolica and Spenso
objects cross Kira's text interface through aliases backed by full SHA-256
digests; Fermat-facing scalar names use a collision-checked ten-character
projection. Native expressions are restored from a checksummed Symbolica state
artifact before results are returned. Its tests compare the full 27-integral
topology-1 result against the retained FIRE oracle. API and work-directory
details are in [`packages/kirapy/README.md`](packages/kirapy/README.md).
The exact official Symbolica pin, the out-of-scope state-import edge case, and
the dependent compatibility ports are documented in
[`docs/symbolica-fork.md`](docs/symbolica-fork.md).

Fermat is downloaded from its official distribution and has a
[non-business-use restriction](https://home.bway.net/lewis/ferm7.html). Review
those terms before using the bundled runtime on an institutional or commercial
machine. The official Apple Silicon Fermat binary requires macOS 26 or newer;
on older macOS versions, configure a compatible external Kira/Fermat runtime.

## Mathematica source context

[`calculations/dy/mathematica/DY_calculation.nb`](calculations/dy/mathematica/DY_calculation.nb)
is the complete original calculation with a small portability edit to its
initialization cell. The local Wolfram packages, gamma-trace data, and topology
1--8 FIRE fixtures are retained beside it.

Wolfram Mathematica is required to evaluate the notebook. FIRE is required
only to rerun the historical FIRE cells; set `FIRE_ROOT` to a FIRE 6 directory
containing `FIRE6.m` and `bin/FIRE6`. The Python/Kira implementation does not
require FIRE. Snapshot provenance and exact inclusions are documented in
[`calculations/dy/mathematica/README.md`](calculations/dy/mathematica/README.md).

## Notebook architecture

The shared root environment intentionally uses editable sibling checkouts at
`../gammaloop/ludy` and `../symbolica-community`. It serves
[`notebooks/ludy.py`](notebooks/ludy.py),
[`notebooks/collinear-cone.py`](notebooks/collinear-cone.py), and both notebooks
under [`calculations/dy/python`](calculations/dy/python), together with
[`calculations/dis/python/notebook.py`](calculations/dis/python/notebook.py).

`ludy.py` is both the source of the DY/Kira helper implementations and a
cell-by-cell cross-box walkthrough. Each helper is defined immediately before
the walkthrough first needs it, while the Mathematica/FIRE comparisons and
other validation checks are collected in a final appendix. Its Kira project
builder, algebraic reduction pipeline, and resumable runner are module-visible
for companion notebooks.
The physical trace is the default worked numerator; assigning a native
Symbolica expression to `user_numerator` runs the same helper pipeline on an
editable numerator. Analytic master evaluators are imported from
[`calculations/dy/python/masters.py`](calculations/dy/python/masters.py), which
is their single implementation site. The complete DY notebook imports the
same cross-box apart and numerator-reduction helpers, defines all eight graphs
and their Kira routes first, and then processes that graph set as one batch.
Every independent FIRE, Mathematica, and manuscript comparison is confined to
its final validation appendix.

The DIS implementation is split by evidence layer. `ancillary.py` pins and
audits the two official arXiv source fixtures without fetching them on import;
`masters.py` implements the paper-phase and reusable one-loop scalar masters;
and `physical.py` owns the finite-virtuality kinematics, six source traces,
projectors, numerator reductions, typed paper targets, Kira serialization, and
validation ledger. The notebook presents those layers and retains the missing
oriented cut weights, full reductions, virtuality integration, pole
cancellation, and channel sums as blockers.

Validate and export the complete notebook set from the repository root:

```console
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.ancillary import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.masters import normalization_self_checks; normalization_self_checks()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.physical import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/ludy.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/collinear-cone.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/notebook.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/masters.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dis/python/notebook.py
$ direnv exec . nix develop --command uv run --locked marimo export html notebooks/ludy.py -o /tmp/ludy-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html notebooks/collinear-cone.py -o /tmp/ludy-collinear-cone-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/notebook.py -o /tmp/ludy-dy-notebook-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/masters.py -o /tmp/ludy-dy-masters-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dis/python/notebook.py -o /tmp/ludy-dis-validation.html --force
```

GammaLoop and Symbolica Community contain separately linked Symbolica engines.
Use them in one process only when the configured license permits multiple
engines.

This checkout loads the active multi-engine license from its ignored `.envrc`.
Use `direnv exec . nix develop --command ...` for non-interactive commands so
that license is present, and never print or commit its value. Keep any other
credentials in ignored environment files as well. Use Jujutsu for
version-control operations in this repository.
