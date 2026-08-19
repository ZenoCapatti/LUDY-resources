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
    notebook.py                portable selectable-topology Kira workflow
    masters.py                 analytic master derivations and evaluation
    pyproject.toml, uv.lock    application dependencies
    flake.nix, flake.lock      Kira/Fermat development runtime
```

The Mathematica notebook is the scientific source context. Its retained FIRE
inputs and tables are golden evidence. The portable Python notebook expresses
the selectable topology through `packages/ludy-kira` and parses the Kira result
as exact Symbolica expressions. The companion `masters.py` notebook derives
the closed-form bubble and triangle basis used by the historical substitutions,
checks it in both radial and light-cone coordinates, audits the supplied PDF's
normalization ambiguities, expands it around `d = 4 - 2 epsilon`, performs the
leading virtuality and soft plus-distribution bookkeeping, and exposes a
positive-kinematics numerical evaluator with rich Typst/MathML display.

The cross-box algebra before IBP is defined and presented directly in
`notebooks/ludy.py`. Its sole graph input is the ordered six-tuple of
`(momentum, mass_squared)` pairs
`p1, p2, k, k-p1, p2-k, p1+p2-k`, with mass squared `q**2` on the final line.
The Symbolica head `k` carries a `ludy::loop_momentum` tag, so the four
loop-dependent propagators are inferred rather than listed separately. The
four full graph masks are named `11`, `10`, `01`, and `00` by their two
external-line bits.

The notebook solves the affine linear system `sum(c_i D_i) = 1`, constructs
the partial-fraction terms, and rewrites each numerator. A visible checked
adapter maps graph order `(D3,D4,D5,D6)` to the historical FIRE order
`(D3,D4,D6,D5)`. It then constructs the twelve complete Kira projects
`topo20`--`topo31`, applies the exact reductions for cuts `11`, `10`, and
`01`, filters masters in global graph space, and evaluates the surviving
`Bcutm`/`Tcutm` masters. Cut `00` requires all four loop lines and is therefore
shown as a direct branch rather than incorrectly represented by a
three-propagator IBP child. The affine solver accepts any number of propagators
when the system is unique; an explicit coefficient tuple can select a relation
for an overcomplete set. Each scientific helper is isolated in its own
notebook cell and exercised by a showcase or an exact derivation assertion.

The corresponding Mathematica section is a semantic validation oracle rather
than an implementation template: the editable Python numerator differs, while
the independent validation path uses Mathematica's active scalar numerator
`1` and validates the routed cut-`11` bubble result. This is deliberately not
a claim that the later historical `xboxNumContr` calculation (whose notebook
also carries a projector warning) has been ported in full. Because it uses
Community/Spenso, run it from the repository-root environment rather than the
portable Kira app.

## Python/Kira implementation

The Python directory is an application, not another reusable library. Its
editable dependency on `../../../packages/ludy-kira` keeps wrapper development
local while its own lock makes the notebook reproducible after cloning this
repository. It does not require the sibling GammaLoop or Symbolica Community
working copies.

```console
$ cd calculations/dy/python
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit notebook.py
$ uv run --locked marimo edit masters.py
```

Opening or statically checking the notebook does not start a reduction. Press
the run button to create or resume its ignored Kira work directory. The Nix
shell supplies the pinned Kira/Fermat executables and `FERMATPATH`; alternatively
configure compatible executables outside Nix.

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

The three environments are intentionally checked independently:

```console
$ cd packages/ludy-kira
$ nix develop --command uv run --locked pytest

$ cd ../..
$ direnv exec . uv run --locked marimo check --strict notebooks/ludy.py
$ direnv exec . uv run --locked marimo export html notebooks/ludy.py -o /tmp/ludy-validation.html --force

$ cd calculations/dy/python
$ nix flake check
$ nix develop --command uv lock --check
$ nix develop --command uv run --locked marimo check --strict notebook.py
$ nix develop --command uv run --locked marimo check --strict masters.py
$ nix develop --command uv run --locked marimo export html masters.py \
    -o /tmp/ludy-dy-masters-validation.html --force
```

The package tests own the exact FIRE/Kira parity oracle. Executing the root
notebook export runs the native Symbolica/Spenso linear-system decomposition,
all inline tooling showcases, generic-arity checks, and scalar pre-IBP oracle;
it then runs or exactly resumes the twelve manifest-checked Kira projects,
checks all three reducible cut survivor sets, and verifies the routed scalar
cut-`11` `Bcutm` result and epsilon expansion against Mathematica/FIRE. The
independently locked portable application keeps its explicit run button, and
its static checks ensure both notebooks remain structurally runnable without
launching Kira. Exporting `masters.py` executes its exact derivation, dimension,
finite-term, series, and numerical-evaluation cells.
