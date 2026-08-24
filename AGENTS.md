# Local Agent Guidance

This repository is a research monorepo. It contains a local Marimo environment
backed by sibling GammaLoop and Symbolica Community working copies, the
standalone `kirapy` package, and an independently locked DY Python
application. Keep changes focused on this repository unless the user explicitly
asks to modify a sibling repository.

## Repository Layout

- LUDY: `/Users/lcnbr/dev/work/bern/LUDY-clean`
- Kira wrapper: `packages/kirapy`
- DY calculation overview: `calculations/dy`
- Portable DY/Kira application: `calculations/dy/python`
- Mathematica source snapshot: `calculations/dy/mathematica`
- Cross-box helper source and walkthrough: `notebooks/ludy.py`
- Root physical DY diagram runner: `notebooks/dy_topologies.py`
- Analytic master implementations: `calculations/dy/python/masters.py`
- General cone notebook: `notebooks/collinear-cone.py`
- GammaLoop: `/Users/lcnbr/dev/work/bern/gammaloop/main`
- Symbolica Community: `/Users/lcnbr/dev/work/bern/symbolica-community`

`packages/kirapy` is a self-contained uv/Nix subproject intended to work
after cloning only this repository. Do not introduce sibling checkout paths or
the notebook dependency graph into its package metadata, lock, or flake.

`calculations/dy/python` is a separately locked application environment. It may
depend on `../../../packages/kirapy`, but must not inherit the root notebook
dependency graph or reference the sibling GammaLoop and Symbolica Community
working copies. Keep application-only dependencies such as Marimo there rather
than adding them to the reusable wrapper.

The root uv sources intentionally use the relative sibling paths
`../gammaloop/main` and `../symbolica-community`. The root Nix flake uses a
public, exact GammaLoop revision while uv overlays the editable local source.
If the working copies move, update the uv paths. This root environment serves
only the general notebooks, including the cross-box source/walkthrough and
physical diagram runner. The DY/Kira application uses its own environment and
requires neither sibling.

The Mathematica directory is a curated source snapshot. Preserve the complete
notebook, first-party packages, `tools/trace_form.log`, and historical FIRE
fixtures. Do not vendor nested version-control metadata, generated databases,
or the large third-party FIRE source/build tree. The fixture files retain
historical paths intentionally and serve as golden evidence, not launchers.

## Version Control

Use Jujutsu for every version-control operation. Do not run Git commands.

```console
$ jj status
$ jj diff
$ jj log --no-pager
$ jj describe -m "<description>"
```

Inspect the current change before editing and preserve unrelated work. In
particular, Symbolica Community may already contain user-owned working-copy
changes; never clean, restore, or fold those into a LUDY change.

## Development Environment

Run project commands inside the Nix development shell. Host-level uv and
Marimo are not assumed to exist.

```console
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit notebooks/ludy.py
$ uv run --locked marimo edit notebooks/dy_topologies.py
```

The equivalent one-shot launch is:

```console
$ nix develop --command uv run --locked marimo edit notebooks/ludy.py
```

The shell inherits GammaLoop's Rust, Python, Maturin, compiler, and native
library toolchain and adds Node.js for Marimo's language-server bridge. It pins
uv to Nix Python 3.13, disables uv-managed Python downloads, and sets
`NO_SYMBOLICA_OEM_LICENSE=1` while compiling local native extensions. Ty is a
locked uv development dependency. Never place a Symbolica license or other
secret in the repository; provide it through the external environment or the
ignored `.envrc` file when needed.

For the standalone Kira wrapper, use its own shell and lock instead:

```console
$ cd packages/kirapy
$ nix develop
$ uv sync --locked
$ uv run --locked pytest
```

The wrapper wheel contains no Kira or Fermat binaries. Its Nix shell supplies
the pinned runtime and `FERMATPATH`; Fermat's restrictive license must remain
explicit in its derivation and documentation.

For the portable DY application, use its application shell and lock:

```console
$ cd calculations/dy/python
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit notebook.py
```

Opening or checking `notebook.py` must not launch Kira. Preserve the explicit
run control and resumable, ignored work directory. This independently locked
portable notebook must not import `notebooks/ludy.py` or
`notebooks/dy_topologies.py`.

`notebooks/ludy.py` owns the reusable cross-box helper implementations and
presents them immediately before first use in the walkthrough. Keep its
Mathematica/FIRE comparisons and other oracle code in the final validation
appendix. Import analytic master evaluators from
`calculations/dy/python/masters.py` rather than duplicating them.

`notebooks/dy_topologies.py` is a root-environment physical diagram runner that
imports the public helper surface from `notebooks/ludy.py`. Keep Kira behind
its explicit run control, keep process normalization separate from the loop
numerator, and do not copy helper implementations into the runner.

## uv Dependency Wiring

LUDY is a virtual uv project. Its two native dependencies are editable local
sources:

- the Python distribution `gammaloop` comes from `../gammaloop/main`;
- the Python distribution `symbolica` comes from
  `../symbolica-community`.

Both source projects declare `tool.uv.package = false` for their own workflows,
so LUDY must retain `package = true` on both `tool.uv.sources` entries. Removing
that override can produce a successful sync without installing the native
module.

GammaLoop's root Cargo manifest is a virtual workspace. The
`config-settings-package` entry in `pyproject.toml` therefore directs Maturin to
`crates/gammaloop-api/Cargo.toml`; keep that override unless GammaLoop's own
packaging layout changes.

Editable installs expose Python changes immediately, but native Rust changes
require a rebuild:

```console
$ uv sync --reinstall-package gammaloop
$ uv sync --reinstall-package symbolica
```

The initial native build is slow. Preserve and reuse the sibling repositories'
ignored Cargo `target/` directories and uv's cache.

## Symbolica Community Cargo Wiring

The root Python environment still installs the editable sibling checkout at
`../symbolica-community`. That checkout is expected to track the
`simplify-spenso-api` branch. Its Cargo manifest pins `idenso`, `spynso3`,
`spenso`, `spenso-hep-lib`, and `vakint` to GammaLoop revision
`092811c505463cca1f1ec9aa9ee90fe51b56a87f`; it does not resolve those crates
from the separate editable GammaLoop checkout.

Do not reapply the older `codex/ludy-spenso-integration` path overrides on top
of this branch. They target the pre-simplification API and would replace the
branch's coherent dependency set. If local Rust development across both
siblings becomes necessary, first move the GammaLoop checkout to the same API
revision and then update every Spenso/Idenso/Vakint path together.

These crates exchange Symbolica and PyO3 types across crate boundaries. Keep
Symbolica Community and its `example_extension` aligned with GammaLoop's
Symbolica 2.2 and PyO3 0.28 dependency families. Both the crates.io source and
GammaLoop's explicit upstream-Git source are patched to the state-registry fork
at revision `e905234770b2cfbcc4f8f8a55274bd9e2b615ecc`. The matching
`codex/kirapy-state-registry` branch is published on `alphal00p/symbolica`.
When that pin deliberately moves, update all six patch entries and verify the
graph:

```console
$ cargo update -p symbolica --precise <symbolica-fork-revision>
$ cargo check --locked
$ cargo tree --locked -i symbolica
$ cargo tree --locked -i pyo3
```

Run those commands from the Symbolica Community working copy inside LUDY's Nix
shell. The trees should contain one Symbolica source identity and one PyO3
version.

## Symbolica Runtime Constraint

GammaLoop and Symbolica Community contain separately linked native Symbolica
engines. A restricted or unlicensed Symbolica build permits only one active
engine, so importing both `gammaloop` and `symbolica.core` in the same process
can abort that process.

`notebooks/ludy.py` uses both the GammaLoop and Community/Spenso APIs and
therefore requires a license that permits the two engines in one process. The
portable `calculations/dy/python/notebook.py` application imports only the
standalone Symbolica distribution. Under a restricted license, use that
application and test GammaLoop separately.

This checkout uses the user's active multi-core license from its ignored
`.envrc`, so combined GammaLoop and Community/Spenso runtime checks are allowed.
Launch non-interactive checks as `direnv exec . nix develop --command ...`;
invoking `nix develop --command` directly does not load `.envrc`. Never print or
commit the license value. On clones without that license, the restricted-build
constraint above still applies.

## Verification

After changing the environment or notebook, run:

```console
$ nix flake check
$ nix develop --command uv lock --check
$ nix develop --command uv run --locked marimo check --strict notebooks/ludy.py
$ nix develop --command uv run --locked marimo check --strict notebooks/dy_topologies.py
$ nix develop --command uv run --locked marimo check --strict notebooks/collinear-cone.py
```

After changing `packages/kirapy`, also run from that directory:

```console
$ nix flake check
$ nix develop --command uv lock --check
$ nix develop --command uv run --locked pytest
$ nix develop --command uv run --locked ty check src tests
```

After changing the DY Python application, also run from
`calculations/dy/python`:

```console
$ nix flake check
$ nix develop --command uv lock --check
$ nix develop --command uv run --locked marimo check --strict notebook.py
$ nix develop --command uv run --locked marimo check --strict masters.py
```

For runtime checks, execute GammaLoop and direct Symbolica imports sequentially,
not concurrently, under a restricted license. A full notebook execution can be
checked without starting the editor:

```console
$ nix develop --command uv run --locked marimo export html notebooks/ludy.py -o /tmp/ludy-notebook-validation.html --force
```

Do not commit `.venv/`, `.direnv/`, `.marimo/`, `__marimo__/`, Cargo build
outputs, or generated validation exports.
