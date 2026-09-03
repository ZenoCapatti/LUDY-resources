# LUDY resources

This repository contains the calculations, notebooks, manuscript, and source
references for factorisable Local Unitarity. It is organized as a research
monorepo: the root Nix/uv environment runs every Marimo notebook, while the
reusable Kira wrapper retains its own independently locked package environment.

```text
paper/                         manuscript and its local TeX inputs
calculations/
  dis/                         native NLO DIS calculation and validations
  dy/
    python/                    native NLO Drell--Yan calculation and masters
    mathematica/               historical Mathematica/FIRE source snapshot
  splitting/                   splitting counter-term calculation and tests
notebooks/
  ludy.py                      crossed-box walkthrough and shared pipeline
  collinear-cone.py            cone visualization
  typst_marimo.py              small Typst/Marimo display helper
  marimo-steady-state-slowdown.py
                                 focused Marimo performance reproducer
packages/kirapy/               reusable Kira project and result interface
references/                    AEM and Pink Book source material
docs/                          dependency and compatibility notes
reproducers/                   standalone dependency-regression cases
```

## Calculation flow

The crossed-box notebook introduces the common analytic stages: physical
propagators and cuts, traces and projectors, partial fractions, numerator
reduction, Kira/IBP reduction, analytic master insertion, virtuality expansion,
and endpoint distributions. The DIS and Drell--Yan notebooks reuse that
surface with their own physical graph sets, cut ledgers, process weights, and
normalizations.

The native DIS and Drell--Yan assemblies are complete. Their closed
coefficients are produced from topologies, cuts, exact reduction records, and
analytic masters. Reference formulas are introduced only after the native
results have been fixed:

- the DY parton-model branch is compared with the Altarelli--Ellis--Martinelli
  calculation;
- the DIS parton-model branch is compared with the Pink Book coefficient
  functions; and
- the independently assembled DIS and DY multi-partonic-minus-parton-model
  differences test the common one-leg scheme kernel, including the explicit
  incoming-gluon polarization conversion.

The retained Mathematica notebook and manuscript formulas are historical
reference layers, not calculation inputs. Detailed conventions, results, and
audits are recorded in
[`calculations/dis/README.md`](calculations/dis/README.md) and
[`calculations/dy/README.md`](calculations/dy/README.md).

## Reproducible root environment

The root lock uses exact public Git revisions of GammaLoop and Symbolica
Community. A fresh clone therefore does not require sibling source checkouts.
`packages/kirapy` and `calculations/splitting` are editable local sources in the
same root environment.

```console
$ cp .envrc.example .envrc
$ direnv allow
$ direnv exec . nix develop --command uv sync --locked
```

Put a locally configured Symbolica license in the ignored `.envrc.local`; the
example environment loads that file when it is present. Then run licensed
non-interactive commands through direnv:

```console
$ direnv exec . nix develop --command uv run --locked python -c 'import symbolica'
```

Never place a license key or another credential in the repository. A local
`.envrc` or another ignored external environment is appropriate.

## Marimo notebooks

Open any notebook from the repository root after entering the Nix shell:

```console
$ uv run --locked marimo edit notebooks/ludy.py
$ uv run --locked marimo edit notebooks/collinear-cone.py
$ uv run --locked marimo edit notebooks/marimo-steady-state-slowdown.py
$ uv run --locked marimo edit calculations/dy/python/notebook.py
$ uv run --locked marimo edit calculations/dy/python/masters.py
$ uv run --locked marimo edit calculations/dis/python/notebook.py
$ uv run --locked marimo edit calculations/splitting/notebooks/splitting_counter_terms.py
```

The cross-box walkthrough runs or resumes its manifest-checked Kira projects
during a complete evaluation. The full DIS and DY notebooks keep reduction
launches behind explicit controls and can reuse fingerprint-checked records
under the ignored `runs/` directory. Static checks and ordinary imports do not
start Kira. The splitting notebook is symbolic and does not use Kira.

The bundled Kira/Fermat runtime currently supports x86-64 Linux and Apple
Silicon macOS. Other systems can use compatible externally installed
executables.

## Validation

The principal root checks are:

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

Complete notebook execution can be checked without opening an editor:

```console
$ direnv exec . nix develop --command uv run --locked marimo export html notebooks/ludy.py -o /tmp/ludy-cross-box.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/notebook.py -o /tmp/ludy-dy.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/masters.py -o /tmp/ludy-dy-masters.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dis/python/notebook.py -o /tmp/ludy-dis.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/splitting/notebooks/splitting_counter_terms.py -o /tmp/ludy-splitting.html --force
```

`packages/kirapy` has a separate package-development gate:

```console
$ cd packages/kirapy
$ nix flake check
$ nix develop --command uv lock --check
$ nix develop --command uv run --locked pytest
$ nix develop --command uv run --locked ty check src tests
```

## Kira, Fermat, and Mathematica

[`packages/kirapy`](packages/kirapy) generates deterministic, resumable Kira
projects and restores exact Symbolica expressions from checksummed state
artifacts. Its wheel does not contain Kira or Fermat binaries. The Nix shell
supplies pinned executables and `FERMATPATH`, or users may configure compatible
external executables.

Fermat is distributed under an official
[non-business-use restriction](https://home.bway.net/lewis/ferm7.html).
Review those terms before using the bundled runtime on an institutional or
commercial machine.

The Mathematica snapshot under `calculations/dy/mathematica` preserves the
original notebook, its first-party Wolfram packages, trace data, and historical
FIRE fixtures. Mathematica is needed only to evaluate that source. FIRE 6 is
needed only to rerun its historical FIRE cells and is configured through an
external `FIRE_ROOT`; neither is required by the native Python/Kira path.

## Manuscript

The manuscript and its local inputs live under [`paper/`](paper/). See
[`paper/README.md`](paper/README.md) for build instructions and the scientific
source boundary. Source references used for external validation are catalogued
under [`references/`](references/).
