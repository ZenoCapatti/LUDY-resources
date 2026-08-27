# Deep-inelastic-scattering calculation

This directory is the focused workspace for transcribing and validating the
next-to-leading-order DIS calculation used by *The KLN theorem meets collinear
factorisation: Local Unitarity for Hadronic Cross-Sections*. It deliberately
uses the same repository-root Nix/uv environment as every DY and general
notebook in this checkout; no additional lock or virtual environment is
introduced.

```text
dis/
  ancillary/
    README.md                  official arXiv URLs, hashes, counts, and schema
  python/
    ancillary.py              pinned metadata, exact-byte audit, explicit fetch
    assembly.py               finite-virtuality Kira jobs and master boundary
    mathematica_reference.py provenance-labelled scheme-regression inputs
    masters.py                paper-phase and reusable B/Bcut/Tcut formulas
    physical.py               side-effect-free source model and validation ledger
    notebook.py               focused executable Marimo presentation
```

## Scope and evidence

There are two distinct source layers:

1. The active manuscript source inspected in the sibling research checkout at
   `../LUDY/references/factorisable-local-unitarity/source/main.tex` specifies
   the integral families, Dirac numerators, normalizations, and coefficient
   functions currently intended for the paper. It is provenance, not a runtime
   dependency of this clean checkout. The inspected 52,260-byte artifact is
   pinned in `physical.py` by SHA-256
   `6a9a8b1c926e646933dd4ab65b7f2b7644486d5dee112528de5e392a4804fd5a`.
   Power-vector and trace-shape checks are internal regressions of that manual
   transcription, not an independent source parser.
2. [arXiv:2506.16489v1](https://arxiv.org/abs/2506.16489v1), *Multi-partonic
   interactions, iterated discontinuities and the virtuality expansion in
   deep inelastic scattering*, supplies the historical analytic derivation and
   the official Mathematica ancillary integrands described in
   [`ancillary/README.md`](ancillary/README.md).

Importing the Python modules or evaluating the notebook does not download the
ancillary files. `ancillary.fetch_ancillary()` is the explicit network-writing
operation; it verifies the pinned hash and inventory before replacing a local
destination.

The arXiv source is an independent historical oracle, not an instruction to
translate every expression verbatim. Its conventions and scope can differ
from the active manuscript. In particular, it includes classes 3 and 4 of the
multi-partonic construction, whereas the paper's LU scheme keeps the minimal
class-1/class-2 completion of the parton-model diagrams.

No complete executable Mathematica DIS derivation is retained in this clean
checkout or in the cited ancillary material. The DIS expressions preserved in
the similarly named `../LUDY/DIS_DY_analytic/DY_calculation.nb` belong to a
Drell--Yan scheme-change calculation. `mathematica_reference.py` keeps those
expressions as typed, provenance-labelled **scheme regressions only**: they are
not graph-by-graph DIS reductions, cut weights, master coefficients, or an
oracle for the native physical assembly.

## Source-label caveat

The active manuscript currently labels both scale-dependent equations at
`main.tex:296-297` as `F_L`. Their logarithmic structure and the historical
formulas identify them as the intended `F_2g` and `F_2q` results; the actual
longitudinal results are then written separately at `main.tex:302-303`.

Code and tests must preserve this distinction explicitly:

- record the labels exactly as they appear in the source transcription;
- attach a separate intended-observable name when comparing with physics;
- do not silently repair the manuscript label in imported source data; and
- do not compare the scale-dependent formulas until the definitions of
  `P_ij(x, 0)`, color factors, plus distributions, and logarithm conventions
  have been made explicit.

The safest first physical targets are therefore the longitudinal functions

```text
F_Lq^(1) = e_q^2 alpha_s/(2 pi) x [2 C_F x]
F_Lg^(1) = e_q^2 alpha_s/(2 pi) x [4 T_F x (1-x)].
```

For the quark `F_2` finite term, the historical minimal class-1/class-2 target
is

```text
C_2q^(1,2)(x) = C_F [
  (1 + 2 pi^2/3) delta(1-x)
  + 2 (1+x^2)/(1-x) log(x)
  - (1+3x)
  + 3/2 [1/(1-x)]_+
].
```

This becomes a target for the active paper only after its conventions have
been reconciled, rather than merely because the formula can be transcribed.
All four printed formulas are represented in `physical.PAPER_TARGETS` as typed
regular, delta, and plus-distribution coefficients. Their literal manuscript
labels remain separate metadata, and the assumed color-stripped kernels and
the unresolved `F_2` projector normalization remain attached source issues;
these targets are not derived answers.

## Source transcription versus physical validation

Source transcription means that an expression has been copied or parsed
without loss, its origin is recorded, and its literal structure agrees with
the source. Examples include importing an ancillary numerator, preserving a
propagator power, or encoding a printed coefficient function. This establishes
provenance, not correctness of the calculation.

Physical validation requires, at minimum:

- the complete intended quark or gluon graph set and all relevant cuts;
- spin/color averages, couplings, loop and cut measures, and the DIS
  `1/(4 pi)` observable factor;
- numerator reduction and IBP reduction to a declared master basis;
- substitution of masters with compatible branch and normalization
  conventions;
- the leading-virtuality expansion and the `p^2` integration from zero to
  `Lambda^2`;
- distributional expansion at `x=1`, including delta and plus-distribution
  terms; and
- equality with a coefficient-function target after an explicit convention
  map.

A successful parser round trip, gamma-trace simplification, Ward contraction,
or individual master check is useful intermediate evidence, but none alone is
a physical validation of `F_2` or `F_L`.

## Implemented evidence and current blockers

The current implementation executes or records the following bounded checks:

- exact finite-`p^2` kinematics and all six printed denominator-power vectors;
- six native Spenso traces and their metric, transverse, `F_2`, `F_L`, and Ward
  contractions;
- four Symbolica multivariate-apart children for the gluon crossed box and 18
  exact zero-residual numerator reconstructions;
- an internal ledger of 15 candidate initial/final all-cut sectors, including
  raised cut orders, checked as exact graph/channel/mask/derivative signatures
  rather than by count alone. The historical definition fixes a **plus sign
  between the four formal all-cut classes**; every candidate row inherits that
  sign rather than independently proving it. The ledger does not establish all
  physical orientations or active multiplicities;
- 16 cut-specialized Kira projects and 32 exact graph/observable reductions
  (one `F_2` and one `F_L` reduction for each project), covering all 48 unique
  cut-preserving numerator targets with zero master-reconstruction residuals;
- canonical kirapy scalar serialization whose hashes are independent of
  Symbolica symbol-registration order. Fingerprint-mismatched caches are
  rejected rather than loaded without their in-memory project;
- 28 of those 32 master coefficients use the cut-specialized reductions. Four
  within that set, the `F_2`/`F_L` coefficients of the `q_box` and `g_box`
  `D2^2` sectors, remain raised-cut convention boundaries. The other four
  records have raised external cuts: `q_bubble` contains `D6^2` and `q_lsz`
  contains `D5^2`. Two additional Kira jobs keep `x` and `p^2` generic and
  produce four exact, nonzero bubble coefficients before either support
  condition is imposed;
- exact analytic `B`, `Bcut`, or `Tcut` insertion for all 32 coefficient
  records. External `D5`/`D6` states, raised-cut orders, and unresolved graph
  weights remain typed metadata rather than being folded into the loop master;
- all-epsilon paper-phase and reusable `B`, `Bcut`, and fully three-mass `Tcut`
  formulas with `d = 4 - 2 epsilon`, exact phase and four-dimensional
  normalization checks, and separately labelled raw-Cutkosky and
  phase-stripped physical ledgers; and
- the four typed paper comparison targets and a stage-by-stage validation
  ledger.

All 32 declared graph/observable handoffs have exact cached coefficients and
analytic masters inserted. The remaining blockers are physical conventions and
downstream assembly steps:

- the active-to-historical `F_2` projector normalization;
- oriented Cut-operator multiplicities, the active six-graph sign/weight map,
  and raw per-graph colour sums;
- the raised-cut convention map: the historical positive
  `2 pi i delta^(n)/n!` definition must be reconciled with the alternating
  `(-1)^(a-1)` sign implied by Kira's algebraic `1/D^a` reverse-unitarity map.
  Until then, the `D2^2`, `D5^2`, and `D6^2` records are exact IBP/master
  boundaries, not physical cut coefficients;
- the external LSZ/LU-apex normalization noted but unresolved in the active
  manuscript;
- the regulated cancellation and one-sided endpoint action for the `delta'`
  terms on the raised `D5`/`D6` cuts;
- oriented cut-master support/branch choices, followed by the leading `p^2`
  integration, all-cut epsilon-pole cancellation, and the quark/gluon channel
  sums; and
- the dimension-dependent splitting kernels and confirmed boundary
  conventions needed for the LU-to-`MSbar` conversion.

The Mathematica expressions can serve as scheme regressions only after native
assembly and an explicit scheme/convention map. They supply none of the missing
physical inputs above.

## Root environment

Run DIS work from the repository root so it uses the root lock and the editable
GammaLoop and Symbolica Community sources:

```console
$ nix develop
$ uv sync --locked
```

The local source, master, and physical-model checks are side-effect-free and do
not launch Kira:

```console
$ direnv exec . nix develop --command uv lock --check
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.ancillary import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.masters import normalization_self_checks; normalization_self_checks()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.physical import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.assembly import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.mathematica_reference import self_check; self_check()'
```

The physical self-check derives all projected numerators, verifies the apart
and reconstruction residuals, and serializes the 16 cut-specialized projects
in memory. Cached Kira results are audited separately to obtain the 32 exact
master coefficients described above. The ledger does not claim a validated
physical result while the convention and assembly blockers remain.

Launch the focused notebook from an interactive root shell:

```console
$ uv run --locked marimo edit calculations/dis/python/notebook.py
```

For non-interactive validation and export, retain the license-bearing root
environment:

```console
$ direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dis/python/notebook.py
$ direnv exec . nix develop --command uv run --locked marimo export html calculations/dis/python/notebook.py -o /tmp/ludy-dis-validation.html --force
```

Opening, checking, or exporting the notebook never starts Kira. It loads the
verified caches under `runs/dis-paper-kirapy` and
`runs/dis-paper-raised-external-kirapy` when present. Its explicit run buttons
create or resume the 16 cut-specialized and two finite-virtuality reductions;
those exact IBP and master-insertion results do not clear the physical
convention blockers above.

Do not run the general GammaLoop module and the separately linked Symbolica
Community engine in one process unless the configured Symbolica license permits
multiple engines.
