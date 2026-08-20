# LUDY research workspace

This repository is a small research monorepo. Reusable Python code lives under
`packages/`, complete calculations live under `calculations/`, and general
interactive experiments live under `notebooks/`.

```text
packages/
  ludy-kira/                  reusable Python wrapper and pinned Kira runtime
calculations/
  dy/
    mathematica/              original DY calculation and FIRE reference data
    python/                   portable Kira and analytic-master notebooks
notebooks/
  ludy.py                     cross-box helpers, walkthrough, and validation
  dy_topologies.py            multi-topology runner reusing ludy.py helpers
  collinear-cone.py           independent cone visualization
pyproject.toml, flake.nix     local environment for the general notebooks
```

The two DY implementations are intentionally siblings. The Mathematica tree
retains the scientific source and historical FIRE fixtures; the Python
application recreates the reduction through the reusable `ludy-kira` package.
See [`calculations/dy/README.md`](calculations/dy/README.md) for the mapping
between them.

## Run the portable DY calculation

The DY Python application has its own uv lock and Nix shell. It depends on the
local `packages/ludy-kira` checkout but not on the sibling GammaLoop or
Symbolica Community repositories:

```console
$ cd calculations/dy/python
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit notebook.py
$ uv run --locked marimo edit masters.py
```

`notebook.py` defines and displays the selectable topology but does not launch
Kira until its run button is pressed. `masters.py` derives and evaluates the
closed-form `B`, `Bcut`, `Tcut`, `Bcutm`, and `Tcutm` basis in radial and
light-cone coordinates, with exact normalization, virtuality, and soft-endpoint
checks, without launching Kira or reading a reduction work directory.

This is the recommended workflow after cloning the repository on a remote
machine. The bundled native runtime currently supports x86-64 Linux and Apple
Silicon macOS. Other systems can use the same Python application with a
separately installed Kira 3.1-compatible executable.

## Reusable Kira wrapper

[`packages/ludy-kira`](packages/ludy-kira) is an independently locked uv/Nix
project. Its wheel contains only the Python interface; Kira and Fermat are
external executables supplied by its Nix shell or configured by the user.

```console
$ cd packages/ludy-kira
$ nix develop
$ uv sync --locked
$ uv run --locked pytest
```

The wrapper exposes deterministic Kira project generation, resumable runs,
exact Symbolica parsing, and completeness checks. Its tests compare the full
27-integral topology-1 result against the retained FIRE oracle. API and
work-directory details are in
[`packages/ludy-kira/README.md`](packages/ludy-kira/README.md).

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

## General research notebooks

The repository root remains a separate local environment for
[`notebooks/ludy.py`](notebooks/ludy.py),
[`notebooks/dy_topologies.py`](notebooks/dy_topologies.py), and
[`notebooks/collinear-cone.py`](notebooks/collinear-cone.py). It intentionally
uses editable sibling checkouts at `../gammaloop/main` and
`../symbolica-community`.

`ludy.py` is both the source of the DY/Kira helper implementations and a
cell-by-cell cross-box walkthrough. Each helper is defined immediately before
the walkthrough first needs it, while the Mathematica/FIRE comparisons and
other validation checks are collected in a final appendix. Its Kira project
builder and resumable runner are module-visible for companion notebooks.
Analytic master evaluators are imported from
[`calculations/dy/python/masters.py`](calculations/dy/python/masters.py), which
is their single implementation site. `dy_topologies.py` imports those public
Kira helpers from `ludy.py` to inspect and run several topologies without
copying the cross-box implementation.

The Symbolica Community checkout should track its latest
`simplify-spenso-api` bookmark; the root lock records the resulting 2.2.0
editable distribution.

```console
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit notebooks/ludy.py
$ uv run --locked marimo edit notebooks/dy_topologies.py
```

GammaLoop and Symbolica Community contain separately linked Symbolica engines.
Use them in one process only when the configured license permits multiple
engines. The independently locked portable DY application at
`calculations/dy/python/notebook.py` does not import either root notebook; it
imports only the standalone Symbolica distribution and avoids that coupling.

Keep `SYMBOLICA_LICENSE` and other credentials in the ignored `.envrc.local`,
never in tracked files. Use Jujutsu for version-control operations in this
repository.
