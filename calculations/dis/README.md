# Deep-inelastic-scattering calculation

This directory contains the standalone NLO DIS calculation used to test the
multi-partonic (MP) scheme in *The KLN theorem meets collinear factorisation:
Local Unitarity for Hadronic Cross-Sections*. It uses the repository-root
Nix/uv environment shared by the DY and general notebooks; it has no separate
lock or virtual environment.

```text
dis/
  ancillary/
    README.md                  official arXiv URLs, hashes, counts, and schema
  python/
    ancillary.py              pinned metadata, exact-byte audit, explicit fetch
    assembly.py               finite-virtuality Kira jobs and master insertion
    mathematica_reference.py reference-only historical scheme expressions
    masters.py                paper-phase and reusable B/Bcut/Tcut formulas
    native_scheme.py          standalone native MP assembler and scheme audit
    physical.py               topology compiler, cuts, traces, and reductions
    notebook.py               focused executable Marimo presentation
```

## Scope and evidence

There are three distinct reference layers:

1. The checked-in manuscript source [`paper/main.tex`](../../paper/main.tex)
   specifies the integral families, normalizations, and coefficient functions
   intended for the paper. It is provenance, not an input to the native MP
   assembly. The inspected 50,527-byte artifact is pinned in `physical.py` by
   SHA-256
   `28936e580a651ff58a21f7b9f43abf51abdbaea7fb05105594fa79f202d42870`.
2. [arXiv:2506.16489v1](https://arxiv.org/abs/2506.16489v1), *Multi-partonic
   interactions, iterated discontinuities and the virtuality expansion in
   deep inelastic scattering*, supplies the historical derivation and official
   Mathematica ancillary integrands described in
   [`ancillary/README.md`](ancillary/README.md).
3. Ellis, Stirling, and Webber,
   [*QCD and Collider Physics*, Chapter 4](https://doi.org/10.1017/CBO9780511628788.005),
   supplies the independent conventional parton-model benchmark. The notebook
   uses the corrected fermion flow for Fig. 4.8(c,d), as recorded in the
   [official corrections](https://www.hep.phy.cam.ac.uk/theory/webber/QCDupdates.html),
   and checks Eqs. 4.63, 4.71, 4.75, 4.82, 4.85, and 4.86.

None of these references is an input to the native MP assembly. The physical
inputs are the declared topologies and cuts; the computational boundary is the
exact Kira coefficients together with the analytic `B`, `Bcut`, and `Tcut`
masters. LaTeX, Mathematica, the paper targets, and the conventional
parton-model coefficients are imported only downstream for comparisons. The
public native assembler has no argument through which a closed coefficient
function can be supplied.

Importing the Python modules or evaluating the notebook does not download
ancillary files or launch Kira. `ancillary.fetch_ancillary()` is the explicit
network-writing operation and verifies the pinned hash and inventory before
replacing a local destination.

## Exact native MP result

Let

```math
L = \log\!\frac{Q^2}{\Lambda^2}, \qquad
\mathcal D_n(x)=\left[\frac{\log^n(1-x)}{1-x}\right]_+,
```

and use the coefficient convention

```math
\widehat F_{i,a}^{\mathrm{MP}}
=\widehat F_{i,a}^{(0)}
+a_s\widehat F_{i,a}^{(1),\mathrm{MP}}+\mathcal O(a_s^2),
\qquad
\widehat F_{i,a}^{(1),\mathrm{MP}}
=e_q^2 x C_a M_{i,a}^{\mathrm{MP}},
\qquad C_q=C_F,\quad C_g=T_F.
```

The standalone topology/cut/master assembly gives

```math
\begin{aligned}
M_{2,q}^{\mathrm{MP}}={}&
\left(-1-\frac{2\pi^2}{3}+\frac32L\right)\delta(1-x)
+\left(2L-\frac32\right)\mathcal D_0(x) \\
&+1+3x-\frac{2(1+x^2)}{1-x}\log x-(1+x)L,\\[2mm]
M_{2,g}^{\mathrm{MP}}={}&
P_{qg}(x)\bigl(L-2\log x\bigr)+6x(1-x)-2,\\
M_{L,q}^{\mathrm{MP}}={}&2x,\\
M_{L,g}^{\mathrm{MP}}={}&4x(1-x),
\end{aligned}
```

where

```math
P_{qg}(x)=x^2+(1-x)^2.
```

The gluon formulas above are for one term in the sum over `q` and `bar(q)`.
A complete one-flavour `gamma* g` coefficient contains the two equal terms and
is therefore twice this expression. The native Laurent audit finds zero in
every `epsilon^-2` and `epsilon^-1` component of all four MP functions. It also
finds zero residual for each of the four finite-virtuality raised-external
identities (`q_bubble` and `q_lsz`, for both `F2` and `FL`).

## Universal DIS--DY scheme change

The conventional DIS coefficient is derived independently from the parton
diagrams. Only after the MP result above is fixed does the notebook form the
one-leg bare scheme kernel

```math
K_a^{\mathrm{DIS}}
=\frac{2\pi}{e_q^2\alpha_s x}
\left(\widehat F_{2,a}^{\mathrm{MP}}
-\widehat F_{2,a}^{\mathrm{PM,bare}}\right)
```

so that the channel color factor remains explicit. Define the color-stripped
splitting distribution

```math
P_{qq}(x)=\frac32\delta(1-x)+2\mathcal D_0(x)-(1+x).
```

The quark result is

```math
\begin{aligned}
\frac{K_q^{\mathrm{DIS}}}{C_F}={}&
P_{qq}(x)\left(\frac1\epsilon+L\right)
+\left(\frac72-\frac{\pi^2}{3}\right)\delta(1-x)
-2\mathcal D_1(x)\\
&+x-2-\frac{1+x^2}{1-x}\log x
+(1+x)\log(1-x).
\end{aligned}
```

Its delta, `D0`, `D1`, pole, logarithmic, and regular components agree exactly
with one incoming leg of the independently assembled native DY result. The DIS
notebook imports the small one-leg output contract from `dy/python/physical.py`;
the DY notebook proves that two such records, with its native channel factors,
reconstruct the full topology/cut/master assembly exactly. The DY formula is
therefore not retyped in the DIS notebook.

For an incoming gluon, the raw DIS trace uses the `d-2=2(1-epsilon)`
polarization average. Before comparing it with the two-helicity/PDF convention
one must retain the finite effect of multiplying by `1-epsilon`:

```math
(1-\epsilon)\left(\frac{P_{qg}}{\epsilon}+F\right)
=\frac{P_{qg}}{\epsilon}+F-P_{qg}+\mathcal O(\epsilon).
```

Thus `K_g = K_{g,raw}-P_qg`, and the converted result is

```math
\frac{K_g^{\mathrm{DIS}}}{T_F}
=P_{qg}(x)\left(\frac1\epsilon+L\right)
-2-P_{qg}(x)\bigl[\log x+\log(1-x)\bigr].
```

This equals the independently assembled native DY `qg` kernel exactly. Before
the declared polarization conversion the DIS-minus-DY residual is precisely
`P_qg(x)`; after it, the residual is zero. The equality is proved by expanding
and normalizing the difference, not by matching the displayed form.

## What is assembled and checked

The executable path is entirely on the Python side:

- five compact topology declarations encode the fermion-cycle momenta, vertex
  identities, six denominator powers, Feynman phase, rooted multiplicity, and
  channel coupling/color/spin factor; the compiler produces six rooted graph
  specifications and their traces and weights;
- the structural cut ledger produces 15 unit-multiplicity oriented sectors.
  The external--external relative phase is `-1`, all other relative phases are
  `+1`, and the raised-cut factor follows from
  `Disc[D^-a] = 2*pi*i*(-1)^(a-1)*delta^(a-1)/(a-1)!`;
- the shared Symbolica/Spenso helpers derive the projected numerators, Ward
  contractions, apart children, and exact numerator reconstructions;
- 16 cut-specialized Kira projects and two finite-virtuality projects provide
  28 ordinary and four raised-external coefficient records. Exact analytic
  masters are inserted only after every Kira reconstruction residual vanishes;
- the native assembler combines graph weights, cut phases and support, performs
  the external-virtuality integrations and endpoint expansion, and verifies
  all-cut pole cancellation before exposing the four finite brackets above;
  and
- a separate conventional calculation assembles `gamma* q -> q g`,
  `gamma* g -> q bar(q)`, and the appendix quark virtual graph. Its traces,
  normalized beta moments, endpoint distributions, and MS-bar subtraction
  reproduce the complete Pink Book quark and gluon `F2` results and both
  longitudinal coefficients with exact zero residuals.

The validated native run used 16/16 complete cut-specialized jobs and 2/2
complete finite-virtuality jobs, yielding 32/32 exact coefficient/master
records. The repository ignores `/runs/`, so cache presence is local to a
checkout. If those artifacts are absent, they must be regenerated or restored;
that is an operational reduction prerequisite, not an unresolved physical
normalization or an invitation to substitute a reference formula.

## Reference-only source audit

The historical and active sources remain valuable comparisons, but the native
answer is fixed before either is read:

- the current manuscript labels the four functions directly at
  `paper/main.tex:287-302`. `physical.PAPER_TARGETS` transcribes those lines
  literally, expands their colour-stripped kernel notation only for the
  downstream comparison, and never supplies a native calculation input;
- `Submission/Discontinuities.tex:80-94` defines
  `disc_s f=f(s-i0)-f(s+i0)`, so the raised-cut definition at `:143-154`
  is missing the alternating `(-1)^(a-1)` factor. The intermediate examples at
  `:109-119` also lose a minus sign when changing from `x-1` to `s=1-x`.
  The implementation derives every phase in the denominator variables rather
  than transcribing these formulas;
- the endpoint expansion at `Submission/Discontinuities.tex:216-220` starts at
  the wrong index and uses `epsilon^i` instead of `(-epsilon)^i`, omitting
  `D0` and reversing the `D1` sign;
- `Submission/DIS_setup.tex:103-108` prints `F_L=F_1-2*x*F_2`; the projector
  definitions require `F_L=F_2-2*x*F_1`, which is what the native tensor
  decomposition uses;
- `Submission/DIS_setup.tex:94-100` puts a plus sign on
  `W_1(g^{mu nu}-q^mu q^nu/q^2)`, but the projector printed immediately after
  it returns `-W_1` for that decomposition. The tensor decomposition needs the
  conventional transverse minus sign;
- the historical source calls `x^2+(1-x)^2` both `P_gq` and `P_qg`; the code
  consistently uses the latter for the color-stripped incoming-gluon kernel;
- in the final source comparison, the finite class-1/class-2 quark coefficient
  printed in the LaTeX has the opposite overall sign from the native graph
  phase, although its `+P_qq log(Q^2/Lambda^2)` scale term is preserved; and
- `Submission/NLO_calculation.tex:77-85` uses a colourless gluon scale term,
  which is full-flavour at `T_F=1/2`, while its finite MP, PM, and longitudinal
  terms are normalized per quark-or-antiquark summand. Independently, the raw
  `d-2`-polarization kernel differs from the PDF-normalized result by `P_qg`.
  The historical Mathematica expression includes the explicit `(1-epsilon)`
  conversion and its gluon expression agrees with the corrected native result;
- the historical `MPDISfermionic` pole at
  `DY_calculation.nb:42637-42789` is
  `9 delta + 6 x(1-x) + 12 x^2 D0`. Canonical distribution multiplication
  differs from `6 P_qq` by the ordinary term `-6(1+x^2)`. The direct native
  DIS--DY comparison therefore exposes a real quark mismatch hidden by the
  internally correlated Mathematica-vs-Mathematica check. Replacing
  `6 x(1-x)` by `6(1+x)` would repair this pole bracket, but the Python result
  is not tuned with that repair. In the common one-leg normalization the full
  ordinary residual is
  `(1+x^2)[1/epsilon+L-log(x)-log(1-x)]-(1-x)(2-x)`, so the finite part also
  disagrees;
- `DY_calculation.nb:41845-41854` multiplies both half-weighted `valv5`
  external-leg bubbles by zero, so its raw quark scheme residual omits an
  endpoint term;
- the same Mathematica notebook uses `realMP-virtualMP` at `:39621-39624` but
  defines the later `MPDY` scheme object as `virtualMP-realMPnosimpl` at
  `:42164-42179`; and
- `DY_calculation.nb:43028-43050` applies `z->1` while `delta(1-z)` is still
  present, producing the recorded but meaningless output `delta(0)`.

The arXiv source includes classes 3 and 4 of the full multi-partonic
construction. The universal comparison above uses the minimal class-1/class-2
one-leg scheme kernel, so those two scopes must not be identified. The
Mathematica material retained in the DY snapshot is likewise a historical
scheme regression, not a graph-by-graph DIS derivation, cut ledger, master
coefficient source, or normalization oracle.

## Root environment

Run DIS work from the repository root so it uses the root lock and the editable
GammaLoop and Symbolica Community sources:

```console
$ nix develop
$ uv sync --locked
```

### Reproduce the result as a plain Python command

The focused notebook is also an ordinary Python entry point. A reader can
reproduce the result without starting the Marimo editor, server, or CLI by
explicitly allowing all required Kira reductions to run or resume:

```console
$ direnv exec . nix develop --command uv run --locked python calculations/dis/python/notebook.py --results --run-reductions
```

This creates fingerprinted reduction data under the ignored
`runs/dis-paper-kirapy/` and `runs/dis-paper-raised-external-kirapy/`
directories. A later invocation can use those compatible caches in load-only
mode and will not launch Kira:

```console
$ direnv exec . nix develop --command uv run --locked python calculations/dis/python/notebook.py --results
```

Add `--json` to either command for deterministic machine-readable output. The
native coefficient functions and exact validation checks are the only content
written to standard output; notebook diagnostics and Kira progress go to
standard error. The command exits successfully only when all 16 ordinary and
two raised-external reductions are compatible and complete, every required
native audit passes, and all reported residuals vanish. Missing or
incompatible caches in load-only mode, an incomplete reduction, or an
inconsistent result produces a `FAIL` report and a nonzero exit status. The
report never substitutes the paper target for a missing native result.

The local source, master, topology, and API checks are side-effect-free and do
not launch Kira:

```console
$ direnv exec . nix develop --command uv lock --check
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.ancillary import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.masters import normalization_self_checks; normalization_self_checks()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.physical import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.assembly import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.native_scheme import self_check; self_check()'
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.mathematica_reference import self_check; self_check()'
```

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

Opening, checking, or exporting the notebook never starts Kira. It loads
fingerprint-verified caches under `runs/dis-paper-kirapy` and
`runs/dis-paper-raised-external-kirapy` when present. The explicit run buttons
create or resume the 16 cut-specialized and two finite-virtuality reductions.

Do not run the general GammaLoop module and the separately linked Symbolica
Community engine in one process unless the configured Symbolica license permits
multiple engines.
