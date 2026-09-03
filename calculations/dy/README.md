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
inputs and tables are golden evidence. Like the cross-box walkthrough, the
Python notebook owns the complete physical input layer: the Spenso symbols and
momenta, the eight explicit raw Dirac chains, the three longitudinal Ward
projections, and every graph as an ordered list of `(momentum, mass_squared)`
pairs built from `p1`, `p2`, and the tagged loop momentum `k`, together with
full cut masks and propagator powers. The shared cross-box trace helper reduces
the chains to scalar products; the previous expanded forms are validation-only
oracles. Other shared helpers derive loop lines, scalar denominators, numerator
reductions, and cut kinematics from that data. The DY project planner then keys
each Kira job by `(graph_name, cut_name, graph_source_indices)` and
structurally deduplicates equivalent physical families, including an explicitly
verified loop reversal when applicable. These declarations are ordinary
editable cells near the top of `notebook.py`, not a hidden collection of Kira
models or legacy family records. Historical `topoN` names occur only in the
retained FIRE evidence and its validation adapter; they are not active
calculation or cache identities. The reusable `physical.py` module owns the
physical graph schema, graph-native project planning, cut-compatible master
selection, normalization ledgers, 20 master insertions, and the final partonic
coefficient data model. The companion
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
site for the generic propagator, cut projection, apart, numerator-reduction,
Kira-project, execution, and master-routing helpers. Its default numerator is
the physical metric-contracted trace, with a native `user_numerator` override.
The DY application imports that surface and adds its visible notebook-owned
symbols, process-specific graph data and Dirac-chain numerator inputs, plus the
physical assembly. Its graph/cut/source project keys extend the cross-box model
directly; no historical family map participates in the calculation.

The corresponding Mathematica section is a semantic validation oracle rather
than an implementation template. The scalar historical route and generic
helper checks remain in the final validation appendix of `notebooks/ludy.py`.
The cross-box example ports the transverse, metric-contracted part of the later
`xboxNumContr` calculation and verifies its maximal-cut limit; it does not port
the warned longitudinal projector. The full application instead
assembles the full quark--antiquark and quark--gluon physical target
coefficients from its structurally deduplicated graph-native Kira projects and
analytic `00` cut. Its final validation appendix keeps the
native transverse reconstruction, recorded Mathematica presentation, and
manuscript targets distinct, displaying the remaining qqbar soft/regular and
qg Ward residuals rather than tuning them away.

The main text also contains two independent physical checks.  First, native
parton-diagram traces and their dimensional phase-space integrals reproduce the
Altarelli--Ellis--Martinelli real-emission results.  Second, a standalone native
DY `MP-PM` builder selects complementary cuts using unsigned `mp_only_cuts`
and `pm_only_cuts`.  Their coefficient is exactly `1_MP-1_PM`; a separate
graph/process phase carries the physical observable sign, and
master-convention cut weights remain independent of both.  The public native
API audits the cached reductions and builds the scheme kernel without first
constructing a closed-form, Mathematica, LaTeX, DIS, or paper target.

The checked-in `graph-v3` state gives, with
`p_qg(z)=1-2z+2z^2`,
`L_z=log(Lambda1^2 Lambda2^2 z^2(1-z)^2/mu_R^4)`,
`A=alpha_s C_F/(2 pi)`, and
`L=log(Lambda1^2 Lambda2^2/mu_R^4)`,

```text
Delta_qg = alpha_s T_F/(4 pi) [2 p_qg/epsilon - 4 - p_qg L_z],

Delta_qq/A = delta(1-z) [3/epsilon + 7 - 2 pi^2/3 - 3 L/2]
             + D0(z) [4/epsilon - 2 L] - 4 D1(z)
             - 2(1+z)/epsilon + 2z - 4 + (1+z)L
             + 2(1+z)log(1-z)
             - 2(1+z^2)log(z)/(1-z).
```

Both double-pole coefficients vanish.  The remaining poles are positive:
`alpha_s T_F p_qg/(2 pi)` and `2 A P_qq`, respectively.  They are exactly the
negative of the independently assembled conventional AEM parton-model poles,
channel by channel and, for `qqbar`, separately in the
`delta/D0/D1/regular` basis.  This pole calibration fixes the physical
`C_MP-C_PM` orientation without feeding a PM formula into the native builder.

The quark derivation includes both half-weighted `valv5` external bubbles that
the old scheme cell multiplied by zero.  The physical quark kernel above is
the graph sum in the AEM/convolution normalization.  Smooth multiplication by
`z` is retained as a separately named historical-normalization transform; it
does not redefine the native result.  Saved-Mathematica and typed DIS formulas
appear only in downstream diagnostic tables.

The ordinary time-like virtual coefficient displayed elsewhere in the
notebook remains a transcribed AEM benchmark: the virtual Kira insertions have
not yet been summed into that complete form-factor coefficient.  The external-
bubble term needed by the scheme check is narrower and is now derived directly
from its audited numerator coefficient, analytic master, two virtuality
integrals, and Born normalization.

## MP--PM source audit

The historical notebook is not a consistent sign oracle.  The native physical
orientation above is therefore calibrated against the independent PM poles,
not chosen to zero a historical residual.  The concrete source conflicts are:

- The full qq coefficient forms `realMP-virtualMP` at
  `mathematica/DY_calculation.nb:39620-39624`, while the later scheme cell
  reverses it to `virtualMP-realMP` at `:42164-42179`.
- In the gluon section `benchG+myPMgluonic=0` around `:40900`; hence the raw
  cut sum is the negative of the conventional benchmark.  The typed DY qg
  output and typed two-beam DIS conversion are consequently both opposite to
  the native physical qg kernel.  Their equality residual is nonzero:
  `Delta_native-Delta_typed=2 Delta_native`; their sum is zero.  This mismatch
  is displayed rather than tuned away.
- The full MP virtual sum contains one half of `valv5` on each incoming leg
  (`:38317-38365` and `:39294-39343`), while the scheme cell explicitly
  multiplies both halves by zero (`:41820-41872`).  Removing `valv1` there is
  correct: `rest1` alone reproduces the conventional PM form factor
  (`:37791-38035`).  `valv5`, by contrast, is the finite-virtuality bubble: its
  derivation expands in the external virtuality, inserts `Bcut`, divides by
  `epsilon*p2sq`, and evaluates at the cutoff (`:14890-14950`).  With the
  executable cell's `1/(1-epsilon)` Born normalization, restoring both halves
  adds
  `alpha_s*C_F/(2*pi) delta(1-z) [-1/epsilon - 1
  + 1/2 log(Lambda1^2/mu^2) + 1/2 log(Lambda2^2/mu^2)]`, exactly the negative
  of the old endpoint residual displayed at `:43042-43068`.
- The final comparison forms `z*MPDY + MPDIStoDY` at `:43023-43031` and then
  globally substitutes `z -> 1` at `:43032-43034`, producing `delta[0]`.
  Multiplication must remain distributional:
  `z*delta(1-z)=delta(1-z)`, `z*D0=D0-1`, and
  `z*D1=D1-log(1-z)`.  The notebook's canonicalizer encodes these rules; the
  final global substitution bypasses them.  The corrected `z` transform is a
  historical convention conversion, not part of the native physical kernel.

One normalization point remains a source caveat rather than a settled repair:
the text says "No (1-ep) normalisation in full result" at `:39282-39290`, but
the immediately following virtual and real cells divide by `1-ep` at
`:39327-39331` and `:39441-39445`.  Since this factor multiplies poles and hence
changes finite endpoint terms, comparisons must declare which convention they
use.

Finally, neither the raw historical table nor arXiv:2506.16489v1 establishes
QCD DY universality.  The typed qq relation is supporting evidence only; the
raw qg sign conflict prevents a universal-equality claim, and a native DIS
assembly is still required.  The paper's
`Submission/introduction.tex:46` describes the same scheme in other processes
as the required test, and `Submission/conclusion.tex:17-20` explicitly leaves
the DY equality open.  Its DY section is a scalar illustration of two-leg
virtuality integration, not an independent oracle for these QCD coefficients.

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
reduction. The graph table remains entirely physical; no `IntegralFamily`,
`Kinematics`, target, bound, or preferred-master object is part of a graph
definition. Its one button runs or resumes all 18 structurally deduplicated,
graph-native Kira projects and
assembles the 20-row Kira-to-analytic-master handoff, including the analytic
four-line `00` cut. The Nix shell supplies the pinned Kira/Fermat executables and
`FERMATPATH`; alternatively configure compatible executables outside Nix.

The master notebook is independent of Kira and of ignored `runs/` state. It
reconstructs the formula factors in the retained Mathematica normalization and
catalogues the explicit historical topology-to-analytic-master identifications
as source provenance; those labels do not feed the graph-native calculation. Its
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
