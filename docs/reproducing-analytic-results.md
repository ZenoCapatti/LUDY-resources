# Reproducible analytic calculations

The DIS and Drell--Yan calculations can be run as ordinary Python programs.
They print analytic coefficients and exact checks in the terminal; opening a
notebook editor is optional.
The same files provide the mathematical walkthroughs when opened interactively.
An independent notebook derives the quark and gluon collinear splitting
counterterms from real and virtual diagrams.

The commands below use `uv` to select the repository's Python environment.
Run them from the repository root, containing `pyproject.toml` and `uv.lock`.
Obtain a checkout of [LUDY-resources](https://github.com/ZenoCapatti/LUDY-resources)
and record its revision when sharing results.

[GammaLoop](https://github.com/alphal00p/gammaloop) was used to generate the
starting graphs.
The symbolic calculations use [Symbolica](https://symbolica.io), with
[Spenso and Idenso](https://github.com/alphal00p/spenso) for tensor contractions,
Dirac traces, and colour algebra.
The pinned Symbolica Community build obtains these tensor-algebra libraries
from the [GammaLoop source distribution](https://github.com/alphal00p/gammaloop).

## Set up the environment

The repository supplies a preconfigured environment containing Python 3.13,
`uv`, the native build tools, Kira, and Fermat.
This is the established route for running the calculations; using it requires
no familiarity with the Nix language.
Install [Nix](https://nixos.org/download/) using the instructions for your
operating system, then enter the environment from the repository root:

```sh
nix --extra-experimental-features 'nix-command flakes' develop
uv sync --locked
```

The first run downloads dependencies and can build native extensions.
Later runs reuse the installed environment.
Keep the locked versions: `uv sync --locked` installs the Python dependencies
specified by this checkout, including its pinned Symbolica and GammaLoop sources.
The bundled Kira/Fermat runtime supports x86-64 Linux and Apple Silicon macOS;
the Apple Silicon Fermat executable requires macOS 26 or newer.
See the [runtime documentation](../packages/kirapy/README.md) for platform and
external-runtime details.
Fermat permits non-business use under its
[upstream licence terms](https://home.bway.net/lewis/ferm7.html); check these
before using it.

Provide your Symbolica licence through the `SYMBOLICA_LICENSE` environment
variable before running a calculation.
Alternatively, create a local shell file `.envrc.local` containing the export
of that variable, then load it in the environment above:

```sh
source .envrc.local
```

This file is ignored by version control; keep the key out of committed files
and shared output.
The notebooks load separately linked Symbolica and GammaLoop engines, so the
licence must permit both to be active in one process.
A restricted single-engine licence can cause the process to abort.
Direnv is optional: users who already have direnv and nix-direnv can use the
root [environment instructions](../README.md#reproducible-root-environment)
to load the shell and licence automatically.

### Using an existing installation without Nix

If your system already has the compatible native prerequisites, install
[`uv`](https://docs.astral.sh/uv/getting-started/installation/) and use
`uv sync --locked`, followed by the same calculation commands below.
The current configuration requires an existing Python 3.13 installation and
disables uv's automatic Python downloads.
The pinned Symbolica Community and GammaLoop sources also need compatible Rust
and native compilation tools; Kira and Fermat remain external executables.
The wrapper looks for `kira` on `PATH`; set `FERMATPATH` to the compatible Fermat
executable.
The bundled runtime versions are documented in
[`packages/kirapy`](../packages/kirapy/README.md).
A fresh-machine, uv-only installation has not been validated; the preconfigured
environment above supplies these prerequisites together.

## Compute the DIS and Drell--Yan results

For the first run, allow the programs to perform their required IBP reductions:

```sh
uv run --locked python calculations/dis/python/notebook.py --results --run-reductions
uv run --locked python calculations/dy/python/notebook.py --results --run-reductions
```

These commands execute the native graph, numerator, reduction, master-integral,
virtuality-expansion, and endpoint-distribution calculations.
They run or resume all required Kira projects: 16 ordinary and two
raised-external projects for DIS, and 18 projects for DY.
The reports give the normalisation convention alongside the coefficients.
DIS prints the quark and gluon contributions to both structure functions,
`F2q`, `F2g`, `FLq`, and `FLg`.
DY prints the `qqbar` channel, the ordered `q1g2` and `g1q2` channels, and their
`qg_average`.
Distribution-valued results are separated into the coefficients of
`delta`, `D0`, `D1`, and the regular part, where
`D0(t) = [1/(1-t)]_+` and `D1(t) = [log(1-t)/(1-t)]_+`.

For example, the DIS report contains the following quark coefficient of `F2`:

```text
M_2,q (F2q):
  delta(1-x) = 1/6*(-6+9*log(Q_squared)-9*log(Lambda_squared)-4*𝜋^2)
  D0(x)      = 1/2*(-3+4*log(Q_squared)-4*log(Lambda_squared))
  D1(x)      = 0
  regular    = (-1-2*x+2*log(x)+log(Q_squared)-log(Lambda_squared)+3*x^2+2*x^2*log(x)-x^2*log(Q_squared)+x^2*log(Lambda_squared))/(-1+x)
```

Here `Q_squared = Q^2`, `Lambda_squared = Lambda^2`, and
`F_2q^(1) = e_q^2*C_F*x*M_2,q`, in the expansion
`F = F^(0) + alpha_s/(2*pi)*F^(1) + O(alpha_s^2)`.
The result is at leading power in the incoming virtuality cutoffs.
The manuscript reproduces this excerpt with line wrapping for the column layout.

The reports include exact reduction and pole-cancellation checks.
Their comparisons use the reference expressions encoded in the checkout;
they do not parse the current manuscript or establish agreement with every
formula in it.
The native calculation is assembled before reference comparisons are made.
The notebooks also compare independently assembled parton-model results with
R. K. Ellis, W. J. Stirling, and B. R. Webber,
[*QCD and Collider Physics*, Chapter 4](https://doi.org/10.1017/CBO9780511628788.005)
(Cambridge University Press, 1996) for DIS, and with G. Altarelli, R. K. Ellis,
and G. Martinelli,
[*Large Perturbative Corrections to the Drell--Yan Process in QCD*](https://doi.org/10.1016/0550-3213(79)90116-0),
Nuclear Physics B **157** (1979) 461--497, for DY.
They also provide a DIS--DY incoming-leg scheme test.
Mathematica and FIRE are needed only to rerun their historical source files,
not for these Python calculations.
Further conventions and reference audits are described in the
[DIS](../calculations/dis/README.md) and [DY](../calculations/dy/README.md) guides.

## Repeat a calculation or save its report

Reduction records are stored locally in `runs/dis-paper-kirapy/`,
`runs/dis-paper-raised-external-kirapy/`, and
`calculations/dy/python/runs/kirapy/graph-v3/`.
The programs reuse records only when the declared inputs match their manifests
and fingerprints.
Once the reductions are complete, omit `--run-reductions` to load them without
launching Kira:

```sh
uv run --locked python calculations/dis/python/notebook.py --results
uv run --locked python calculations/dy/python/notebook.py --results
```

Missing or incomplete records produce a failed report; rerun with
`--run-reductions` to compute or resume the required projects.
If a manifest mismatch is reported, preserve the affected project directory
elsewhere before computing a fresh reduction from the current inputs.
Inspect any remaining failed checks before using the coefficients.
For machine-readable output, add `--json` (also compatible with
`--run-reductions`):

```sh
uv run --locked python calculations/dis/python/notebook.py --results --json
uv run --locked python calculations/dy/python/notebook.py --results --json
```

JSON is written to standard output and calculation diagnostics to standard
error, so standard shell redirection can save the report separately.
Each program also accepts `--help`.

## Evaluate the splitting counterterms

The independent [splitting calculation](../calculations/splitting/README.md)
derives `D_qq`, `D_gq`, `D_qg`, and `D_gg` from real and virtual collinear
diagrams, including colour contractions, phase-space integration, and endpoint
terms.
The first index labels the daughter entering the hard interaction and the
second the parent parton.
The derivation supplies a separate check of the splitting counterterms used
in the scheme transformation.

Evaluate the notebook as a Python program from the repository root:

```sh
uv run --locked python calculations/splitting/notebooks/splitting_counter_terms.py
```

For a terminal summary of its symbolic regression checks, run:

```sh
uv run --locked pytest calculations/splitting/tests
```

The interactive notebook displays the derived expressions and comparison
tables at each stage.

## Read the calculation interactively

For the derivation, intermediate expressions, and comparison tables, open the
same files in Marimo:

```sh
uv run --locked marimo edit calculations/dis/python/notebook.py
uv run --locked marimo edit calculations/dy/python/notebook.py
uv run --locked marimo edit calculations/splitting/notebooks/splitting_counter_terms.py
```

For a first interactive DIS calculation, activate both "Evaluate the 16 DIS
scalar reductions" and "Evaluate the 2 raised-external reductions".
For DY, activate "Evaluate cut-sector IBP reductions and the DY coefficient".
These controls run or resume the reductions; compatible completed records are
loaded automatically on subsequent evaluations.

The [crossed-box walkthrough](../notebooks/ludy.py) introduces the shared
analytic stages, and the [splitting notebook](../calculations/splitting/notebooks/splitting_counter_terms.py)
provides the independent splitting-counterterm calculation.
Their launch commands are listed in the root [notebook guide](../README.md#marimo-notebooks).
