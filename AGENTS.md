# Local Agent Guidance

This repository is a research monorepo for factorisable Local Unitarity. Keep
changes within this repository unless the user explicitly expands the scope.
All paths in documentation and commands must be repository-relative; do not
record workstation-specific checkout paths.

## Repository layout

- `paper/`: manuscript, bibliography, and local TeX inputs.
- `calculations/dis/`: complete native DIS calculation and reference audits.
- `calculations/dy/python/`: complete native DY calculation and analytic
  masters.
- `calculations/dy/mathematica/`: curated historical Mathematica/FIRE source
  snapshot.
- `calculations/splitting/`: Symbolica splitting counter-term package,
  notebook, and tests.
- `notebooks/ludy.py`: crossed-box walkthrough and the public implementation
  of generic apart, numerator-reduction, Kira, cut, and master-routing helpers.
- `notebooks/collinear-cone.py`: general cone visualization.
- `notebooks/typst_marimo.py`: small Typst/Marimo helper and showcase.
- `notebooks/marimo-steady-state-slowdown.py`: focused Marimo performance
  reproducer.
- `packages/kirapy/`: self-contained reusable Kira wrapper.
- `references/`: AEM and Pink Book validation sources.
- `docs/` and `reproducers/`: dependency notes and standalone regression cases.

The Mathematica tree is curated evidence. Preserve the complete notebook,
first-party packages, `tools/trace_form.log`, and historical FIRE fixtures.
Do not vendor nested version-control metadata, generated databases, or the
third-party FIRE source/build tree. Historical paths inside fixtures are
provenance and need not be executable.

## Migration and manuscript boundary

The migration history establishes the organized repository, portable dependency
graph, and fully validated native code before the subsequent paper-only
correction. Preserve that review boundary when rewriting or moving the history.
Keep future calculation changes and manuscript transcriptions independently
reviewable, and treat the native calculations as the scientific source of truth.

## Version control

Use Jujutsu for every version-control operation. Do not run Git commands.

```console
$ jj status
$ jj diff
$ jj log --no-pager
$ jj describe -m "<description>"
```

Inspect the current change before editing and preserve unrelated work. Keep
repository organization, code changes, validation, and paper corrections
reviewable as distinct changes.

## Root development environment

Run every Marimo notebook from the repository-root Nix/uv environment. Host
`uv`, Marimo, compilers, Kira, and Fermat are not assumed to exist.

```console
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit notebooks/ludy.py
$ uv run --locked marimo edit notebooks/collinear-cone.py
$ uv run --locked marimo edit notebooks/marimo-steady-state-slowdown.py
$ uv run --locked marimo edit calculations/dy/python/notebook.py
$ uv run --locked marimo edit calculations/dy/python/masters.py
$ uv run --locked marimo edit calculations/dis/python/notebook.py
$ uv run --locked marimo edit calculations/splitting/notebooks/splitting_counter_terms.py
```

The root project uses exact public Git revisions for GammaLoop and Symbolica
Community. A fresh clone must not require sibling checkouts. Keep the revisions
in `pyproject.toml`, `uv.lock`, `flake.nix`, and `flake.lock` aligned when they
move. Local editable development overlays may be used outside the committed
configuration, but workstation paths must never enter project metadata or
documentation.

Bootstrap direnv in a fresh clone with `cp .envrc.example .envrc` followed by
`direnv allow`. Put licenses and other local-only values in the ignored
`.envrc.local`; never add them to `.envrc.example`.

The root environment also installs repository-local editable sources for
`packages/kirapy` and `calculations/splitting`. Keep notebook-only dependencies
at the root. Do not give the DY or DIS applications separate uv or Nix
environments.

## Independent kirapy package

`packages/kirapy` is independently locked so it works after cloning this
repository without the notebook dependency graph:

```console
$ cd packages/kirapy
$ nix develop
$ uv sync --locked
$ uv run --locked pytest
```

Do not add root notebooks or application packages to its metadata. Its wheel
contains only the Python interface; Kira and Fermat remain external executables
supplied by its Nix shell or configured by the user.

Fermat has a restrictive non-business-use license. Preserve that fact in its
derivation and documentation. Do not vendor or redistribute it outside the
existing licensed Nix packaging arrangement.

## Calculation architecture

`notebooks/ludy.py` is both the physical crossed-box walkthrough and the single
public implementation site for the shared algebraic pipeline. Present each
helper immediately before its first mathematical use. Keep process
normalization separate from loop numerators. Import analytic master evaluators
from `calculations/dy/python/masters.py`; do not duplicate them.

The DIS and DY applications supply process-specific physical inputs:
topologies, ordered momentum/mass lines, cuts, traces, projectors, phases,
multiplicities, and channel normalization. Their native closed results must be
assembled only from those inputs, exact Kira coefficients, and analytic
masters. Preserve the boundary that keeps LaTeX, Mathematica, AEM, Pink Book,
and typed historical formulas downstream as validation references.

The complete native calculations include the virtuality expansion and endpoint
distribution assembly. Their independently constructed parton-model branches
are separate starting graph selections. The DIS and DY `MP-PM` records compare
the common incoming-leg scheme kernel only after both branches are fixed. Keep
the incoming-gluon `d-2` versus two-helicity/PDF polarization conversion
explicit; it has a finite effect when multiplied by a pole.

The splitting counter-term package is an independent symbolic calculation and
validation layer. It uses the root environment but retains its local Python
package structure and tests. Do not silently substitute its results into the
native DIS/DY assembly or deduplicate the two derivations without an explicit
scientific comparison.

## Notebook execution behavior

Opening or statically checking the complete DIS and DY notebooks must not
launch Kira. Preserve their explicit run controls and resumable ignored work
directories. `notebooks/ludy.py` may run or resume its twelve manifest-checked
crossed-box projects during complete evaluation. The masters, cone, display,
performance, and splitting notebooks do not launch Kira.

Persisted reduction data under `runs/` is local and ignored. Reuse it only when
its manifests and fingerprints match the declared inputs. Missing caches are an
operational requirement to run reductions, not permission to inject a
reference coefficient into the native result.

Keep Mathematica/FIRE comparisons and other oracle code in final validation
sections. Historical `topoN` labels may appear in provenance adapters but must
not become active physical graph identities.

## Public dependency pins

The compatible source family currently consists of:

- GammaLoop `4f44c86382977bade32a230801034b5c37faddbd`;
- Symbolica Community `4f62108b789ec33b25cb259696e6ff67780bab38`;
- `symbolica-integrate` `306a6f4b7e53eacbc774545c41082d119a22632b`;
- official Symbolica `d6bb961d22c026c4866b2e698f56fbb964c4ee0e`.

These crates exchange Symbolica and PyO3 types across boundaries. Keep them on
the same Symbolica 2.2 and PyO3 0.28 families. When the pins deliberately move,
update the public revisions together and verify one Symbolica source identity
and one PyO3 version in the resulting Cargo graph. The rational-polynomial
user-data variable-list reproducer remains an upstream regression case;
current LUDY and kirapy artifacts do not store that unsupported form.

GammaLoop's root Cargo manifest is a virtual workspace. Retain the
`config-settings-package` entry that points Maturin at
`crates/gammaloop-api/Cargo.toml` unless upstream packaging changes.

## Symbolica runtime constraint and secrets

GammaLoop and Symbolica Community contain separately linked native Symbolica
engines. A restricted or unlicensed build may permit only one active engine,
so a process that imports both can abort. The crossed-box notebook requires a
license permitting both engines. On restricted installations, keep direct
Symbolica and GammaLoop checks in separate processes and avoid combined-engine
notebooks.

Provide any license through the external environment or an ignored `.envrc`.
Use `direnv exec . nix develop --command ...` for non-interactive licensed
checks. Never print, commit, copy into documentation, or otherwise expose a
license key or credential.

## Verification

After changing root code, dependencies, or notebooks, run:

```console
$ direnv exec . nix flake check
$ direnv exec . nix develop --command uv lock --check
$ direnv exec . nix develop --command uv run --locked pytest calculations/splitting/tests
$ direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/ludy.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/collinear-cone.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/marimo-steady-state-slowdown.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/notebook.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/masters.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dis/python/notebook.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/splitting/notebooks/splitting_counter_terms.py
```

The side-effect-free DIS module checks are:

```console
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.ancillary import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.masters import normalization_self_checks; normalization_self_checks()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.physical import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.assembly import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.native_scheme import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.mathematica_reference import self_check; self_check()'
```

Full notebook execution uses export commands so it does not require an editor:

```console
$ direnv exec . nix develop --command uv run --locked marimo export html notebooks/ludy.py -o /tmp/ludy-cross-box.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html notebooks/collinear-cone.py -o /tmp/ludy-cone.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/notebook.py -o /tmp/ludy-dy.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/masters.py -o /tmp/ludy-dy-masters.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dis/python/notebook.py -o /tmp/ludy-dis.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/splitting/notebooks/splitting_counter_terms.py -o /tmp/ludy-splitting.html --force
```

After changing `packages/kirapy`, also run from that directory:

```console
$ nix flake check
$ nix develop --command uv lock --check
$ nix develop --command uv run --locked pytest
$ nix develop --command uv run --locked ty check src tests
```

Do not commit `.envrc`, `.venv/`, `.direnv/`, `.marimo/`, `__marimo__/`,
`__pycache__/`, `/runs/`, Cargo outputs, generated notebook HTML, or generated
LaTeX build products.
