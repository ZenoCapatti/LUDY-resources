# Drell--Yan calculation

This directory keeps the original Mathematica calculation and its new
Python/Kira counterpart together as two implementations of the same scientific
workflow:

```text
dy/
  mathematica/
    DY_calculation.nb          original calculation
    mma/, tools/               local Wolfram packages and trace data
    temp/FIRE/                 historical topology 1--8 FIRE fixtures
  python/
    notebook.py                declarative graph-set and full-DY workflow
    physical.py                exact physical-sector and channel assembly
    masters.py                 analytic master derivations and evaluation
```

The Mathematica notebook is the scientific source context. Its retained FIRE
inputs and tables are golden evidence. The Python notebook defines all physical
graphs, denominators, Kira routes, and numerators first, then explicitly runs or resumes
the 18 Kira families in that graph set and assembles their exact
Symbolica results. The reusable `physical.py` module applies the shared cross-box
numerator-reduction helpers, owns cut-compatible master selection, normalization ledgers, 20 master
insertions, and final partonic coefficient data model. The companion
`masters.py` notebook derives
the closed-form bubble and triangle basis used by the historical substitutions,
checks it in both radial and light-cone coordinates, audits the supplied PDF's
normalization ambiguities, expands it around `d = 4 - 2 epsilon`, performs the
leading virtuality and soft plus-distribution bookkeeping, and exposes a
positive-kinematics numerical evaluator with rich Typst/MathML display.

The cross-box helper implementations and calculation walkthrough are defined
directly in `notebooks/ludy.py`. Each helper appears immediately before its
first use, so the cross-box calculation itself exercises the reusable helper
surface. Its sole graph input is the ordered list of six
`(momentum, mass_squared)` pairs
`p1, p2, k, k-p1, p2-k, p1+p2-k`, with mass squared `q**2` on the final line.
The Symbolica head `k` carries a `ludy::loop_momentum` tag, so the four
loop-dependent propagators are inferred rather than listed separately. The
four full graph masks are named `11`, `10`, `01`, and `00` by their two
external-line bits.

The notebook delegates the propagator-kernel decomposition to Symbolica's
multivariate `Expression.apart(*loop_scalar_products)`. A thin adapter maps the
returned summands back to their original graph propagators; it performs no
affine solve. The physical Spenso/Idenso numerator is then rewritten in each
apart-derived basis. The notebook constructs twelve complete Kira projects in
native graph order, names each project from its cut and retained graph sources,
applies the exact reductions for cuts `11`, `10`, and `01`, filters masters in
global graph space, and evaluates the surviving cut bubble or triangle. Cut
`00` requires all four loop lines and is therefore the analytic maximal-cut
master `M00(s)`, rather than being incorrectly represented by a
three-propagator IBP child. The analytic bubble, triangle, and maximal-cut
evaluators are imported from `python/masters.py`, their single source of
implementation. Only the final validation appendix maps native graph order
`(D3,D4,D5,D6)` to the historical FIRE order `(D3,D4,D6,D5)` and names
`topo20`--`topo31`.

`notebooks/ludy.py` is itself the crossed-box example and the only implementation
site for the generic apart, numerator-reduction, project, Kira, and master-routing
helpers. Its default numerator is the physical metric-contracted trace, with a
native `user_numerator` override. `python/notebook.py` imports that helper surface
and owns the broader 18-family graph-set assembly.

The corresponding Mathematica section is a semantic validation oracle rather
than an implementation template. The scalar historical route and generic
helper checks remain in the final validation appendix of `notebooks/ludy.py`.
The cross-box example ports the transverse, metric-contracted part of the later
`xboxNumContr` calculation and verifies its maximal-cut limit; it does not port
the warned longitudinal projector. The full application instead
assembles the full quark--antiquark and quark--gluon physical target
coefficients from its 18 Kira sectors and analytic `00` cut. Its final validation appendix keeps the
native transverse reconstruction, recorded Mathematica presentation, and
manuscript targets distinct, displaying the remaining qqbar soft/regular and
qg Ward residuals rather than tuning them away.

## Python/Kira implementation

The Python directory contains application notebooks and their reusable
assembly module; it is not another package or environment. All Marimo
notebooks use the repository-root uv lock and Nix shell. The root project keeps
`packages/kirapy`, GammaLoop, and Symbolica Community editable while the root
flake supplies Kira, Fermat, and `FERMATPATH`.

```console
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit calculations/dy/python/notebook.py
$ uv run --locked marimo edit calculations/dy/python/masters.py
```

Opening, statically checking, or exporting the notebook does not start a
reduction. Its one button runs or resumes all 18 physical Kira families and assembles the
20-row Kira-to-analytic-master handoff, including the analytic four-line `00`
cut. The Nix shell supplies the pinned Kira/Fermat executables and
`FERMATPATH`; alternatively configure compatible executables outside Nix.

The master notebook is independent of Kira and of ignored `runs/` state. It
reconstructs the formula factors in the retained Mathematica normalization and
catalogues only the explicit topology-to-analytic-master identifications. Its
normalization ledger separately tracks loop measures, real cut deltas,
virtuality measures, the DIS prefactor, and historical Cutkosky signs; it does
not imply that every preferred Kira master has an analytic value.

Fermat is distributed under an official non-business-use restriction. Review
the terms linked from the repository and package READMEs before using the
bundled executable.

## Mathematica/FIRE implementation

Open [`mathematica/DY_calculation.nb`](mathematica/DY_calculation.nb) in
Wolfram Mathematica. Its local packages load relative to the notebook. To
rerun FIRE cells, set `FIRE_ROOT` to an external FIRE 6 installation; FIRE is
not vendored here and is not needed by the Python implementation.

See [`mathematica/README.md`](mathematica/README.md) for source revision,
snapshot contents, exclusions, and FIRE configuration.

## Verification scopes

Package development retains the independently locked `packages/kirapy`
environment. Every notebook is checked and exported from the repository root:

```console
$ cd packages/kirapy
$ nix develop --command uv run --locked pytest

$ cd ../..
$ direnv exec . nix develop --command uv lock --check
$ direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/ludy.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/collinear-cone.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/notebook.py
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/masters.py
$ direnv exec . nix develop --command uv run --locked marimo export html notebooks/ludy.py \
    -o /tmp/ludy-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html notebooks/collinear-cone.py \
    -o /tmp/ludy-collinear-cone-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/notebook.py \
    -o /tmp/ludy-dy-notebook-validation.html --force
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/masters.py \
    -o /tmp/ludy-dy-masters-validation.html --force
```

The package tests own the exact FIRE/Kira parity oracle. Executing the root
cross-box notebook export runs the native Symbolica/Spenso linear-system
decomposition and the twelve manifest-checked Kira projects, then its final
validation appendix performs the generic-arity, scalar pre-IBP, cut-survivor,
Mathematica/FIRE, and epsilon-expansion checks. The full-DY application keeps
its explicit run button. Static checks cover the entire shared notebook set
without launching a new reduction.
Exporting `notebook.py` validates the dormant full-assembly interface and its
Typst-rendered report without launching Kira. Exporting `masters.py` executes
its exact derivation, dimension, finite-term, series, and numerical-evaluation
cells.
