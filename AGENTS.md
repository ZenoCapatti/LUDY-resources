# Local Agent Guidance

This repository is a research monorepo. It contains a local Marimo environment
backed by sibling GammaLoop and Symbolica Community working copies, the
standalone `kirapy` package, and the DY Python application. All Marimo notebooks
share the repository-root environment. Keep changes focused on this repository
unless the user explicitly asks to modify a sibling repository.

## Repository Layout

- LUDY: `/Users/lcnbr/dev/work/bern/LUDY-clean`
- Kira wrapper: `packages/kirapy`
- DY calculation overview: `calculations/dy`
- DY/Kira application notebooks: `calculations/dy/python`
- Mathematica source snapshot: `calculations/dy/mathematica`
- Cross-box helper source and walkthrough: `notebooks/ludy.py`
- Analytic master implementations: `calculations/dy/python/masters.py`
- General cone notebook: `notebooks/collinear-cone.py`
- GammaLoop: `/Users/lcnbr/dev/work/bern/gammaloop/ludy`
- Symbolica Community: `/Users/lcnbr/dev/work/bern/symbolica-community`

`packages/kirapy` is a self-contained uv/Nix subproject intended to work
after cloning only this repository. Do not introduce sibling checkout paths or
the notebook dependency graph into its package metadata, lock, or flake.

`calculations/dy/python` contains application notebooks and an importable
assembly module, but no separate uv or Nix environment. Keep notebook-only
dependencies in the root project rather than adding them to the reusable
wrapper.

The root uv sources intentionally use the relative sibling paths
`../gammaloop/ludy` and `../symbolica-community`. The root Nix flake uses a
public, exact GammaLoop revision while uv overlays the editable local source.
If the working copies move, update the uv paths. This root environment serves
the cross-box source/walkthrough, cone visualization, full-DY Kira application,
analytic-master derivation, and DIS application.

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
$ uv run --locked marimo edit notebooks/collinear-cone.py
$ uv run --locked marimo edit calculations/dy/python/notebook.py
$ uv run --locked marimo edit calculations/dy/python/masters.py
$ uv run --locked marimo edit calculations/dis/python/notebook.py
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

Opening or checking `notebook.py` must not launch Kira. Preserve the explicit
run control and resumable, ignored work directory. The DY and DIS applications
import the process-independent helpers from `notebooks/ludy.py`.

`notebooks/ludy.py` owns the reusable cross-box helper implementations and
presents them immediately before first use in the walkthrough. Keep its
Mathematica/FIRE comparisons and other oracle code in the final validation
appendix. Import analytic master evaluators from
`calculations/dy/python/masters.py` rather than duplicating them.

`notebooks/ludy.py` is the root-environment physical cross-box example and the
single public implementation site for generic apart, numerator-reduction,
Kira, cut, and master-routing helpers. Keep process normalization separate from
the loop numerator and do not copy helper implementations into applications.

## uv Dependency Wiring

LUDY is a virtual uv project. Its two native dependencies are editable local
sources:

- the Python distribution `gammaloop` comes from `../gammaloop/ludy`;
- the Python distribution `symbolica` comes from
  `../symbolica-community`.

The reusable `kirapy` package comes from the repository-local
`packages/kirapy` source. Keep its independent package lock and subflake for
package development, while all notebook-only dependencies remain in the root
project.

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

The root Python environment installs the editable sibling checkout at
`../symbolica-community`. Its published integration branch pins compatible
GammaLoop and `symbolica-integrate` forks rather than carrying their obsolete
API shims in Symbolica itself. GammaLoop and Vakint own the strict-linear solve
port, `symbolica-integrate` uses the public polynomial variable APIs, and the
Spynso boundary owns the Python-normalization conversion.

These crates exchange Symbolica and PyO3 types across crate boundaries. Keep
Symbolica Community, GammaLoop, and `example_extension` aligned with the same
Symbolica 2.2 and PyO3 0.28 dependency families. The baseline is exact
official Symbolica `dev` at
`d6bb961d22c026c4866b2e698f56fbb964c4ee0e`. It fixes
printer-independent canonical strings. The rational-polynomial user-data
variable-list MWE still fails, but current LUDY and kirapy state artifacts do
not store rational-polynomial coefficient atoms in symbol user data, so that
edge case does not require a runtime fork. Keep the MWE as an upstream
regression case and make every Symbolica source identity resolve to the exact
official revision. GammaLoop, symbolica-integrate, and Symbolica Community
retain only their caller-side compatibility changes. Their matching published
revisions are `4f44c86382977bade32a230801034b5c37faddbd`,
`306a6f4b7e53eacbc774545c41082d119a22632b`, and
`4f62108b789ec33b25cb259696e6ff67780bab38`, respectively.

When those pins deliberately move, update the Community, GammaLoop, and
symbolica-integrate revisions together and verify the graph:

```console
$ cargo update -p symbolica --precise d6bb961d22c026c4866b2e698f56fbb964c4ee0e
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
therefore requires a license that permits the two engines in one process.
Sharing one uv environment does not itself activate both engines; imports do.
On a restricted clone, run direct-Symbolica and GammaLoop checks in separate
processes and avoid notebooks that import both.

This checkout uses the user's active multi-core license from its ignored
`.envrc`, so combined GammaLoop and Community/Spenso runtime checks are allowed.
Launch non-interactive checks as `direnv exec . nix develop --command ...`;
invoking `nix develop --command` directly does not load `.envrc`. Never print or
commit the license value. On clones without that license, the restricted-build
constraint above still applies.

## Verification

After changing the environment or notebook, run:

```console
$ direnv exec . nix flake check
$ direnv exec . nix develop --command uv lock --check
$ direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/ludy.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/collinear-cone.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/notebook.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/masters.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dis/python/notebook.py
```

After changing `packages/kirapy`, also run from that directory:

```console
$ nix flake check
$ nix develop --command uv lock --check
$ nix develop --command uv run --locked pytest
$ nix develop --command uv run --locked ty check src tests
```

Full notebook executions can be checked from the repository root without
starting the editor or pressing Kira's explicit run controls:

```console
$ direnv exec . nix develop --command uv run --locked marimo export html notebooks/ludy.py -o /tmp/ludy-notebook-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html notebooks/collinear-cone.py -o /tmp/ludy-collinear-cone-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/notebook.py -o /tmp/ludy-dy-notebook-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/masters.py -o /tmp/ludy-dy-masters-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dis/python/notebook.py -o /tmp/ludy-dis-notebook-validation.html --force
```

Do not commit `.venv/`, `.direnv/`, `.marimo/`, `__marimo__/`, Cargo build
outputs, or generated validation exports.
