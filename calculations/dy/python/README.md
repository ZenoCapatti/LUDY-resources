# Drell-Yan reduction and analytic masters in Python

This application directory uses the repository-root environment and is the
Python counterpart of the sibling
[`DY_calculation.nb`](../mathematica/DY_calculation.nb) calculation.
It uses the repository's reusable [`kirapy`](../../../packages/kirapy) package
to run 18 structurally distinct projects derived from physical graph, cut, and
source-line inputs. Historical `topoN` families remain only in the retained
FIRE fixtures and analytic-identification provenance; the notebook does not
instantiate or route through them.

The application contains two Marimo notebooks and one reusable assembly module:

- `notebook.py` directly declares the symbols, the complete physical graph,
  the raw Dirac chains for all eight transverse numerators, and the three
  longitudinal Ward projections before running the physical-sector assembly
  explicitly. The shared cross-box `gamma_trace_to_dots` helper performs every
  trace simplification; the former expanded polynomials survive only as exact
  validation-appendix oracles. Each graph contains only ordered
  `(momentum, mass_squared)` lines in `p1`, `p2`, and tagged loop momentum `k`,
  plus full cut masks and propagator powers;
- `masters.py` derives and evaluates the closed-form `B`, `Bcut`, `Tcut`,
  `Bcutm`, and `Tcutm` basis used by the retained Mathematica substitutions,
  and owns the importable analytic master evaluator implementations used by
  the root cross-box walkthrough;
- `physical.py` holds the physical graph schema and graph-native project plan,
  consumes the explicit notebook context, graphs, and numerators through the
  shared cross-box helpers, and performs cut-compatible master selection,
  normalization and external-virtuality ledgers, and the final partonic
  coefficient data model. Its public colour-stripped one-leg scheme contract is
  checked in the notebook by reconstructing the full native two-leg result in
  both channels; DIS imports that checked interface instead of retyping a DY
  formula. Shared direct/qg projects are deduplicated only when
  their physical cuts and denominators agree, including the verified loop
  reversal `k -> -k`.

From the repository root:

```console
nix develop
uv sync --locked
uv run --locked marimo edit notebooks/ludy.py
uv run --locked marimo edit notebooks/collinear-cone.py
uv run --locked marimo edit calculations/dy/python/notebook.py
uv run --locked marimo edit calculations/dy/python/masters.py
```

Opening the notebook does not launch Kira. Graph definitions do not contain
`IntegralFamily`, `Kinematics`, target, bound, or preferred-master objects;
those are derived downstream from the physical lines and cuts. Each resulting
project has separate persistent state under a generated physical family name
in `runs/kirapy/graph-v3/`, so an interrupted calculation can be resumed;
`runs/` is ignored by version control. This namespace is deliberately distinct
from older family-named caches, whose identities are not compatible with the
graph-native projects. Press the single
**Run/resume all physical reductions and assemble DY** button when ready.
The historical topologies retained as validation evidence are backed by
reproducibly regenerated and hashed FIRE output
documented in their
`packages/kirapy/tests/fixtures/fire_topoN/PROVENANCE.md` files.

That batch loads or computes the 18 Kira projects used by the physical graph set. It
reconstructs all seven three-line graph numerators, applies Symbolica's native
multivariate `apart` to the crossed box, checks every selected Kira coefficient,
and adds the analytic four-line `00` cut without pretending it is a Kira
family. The resulting 20-row handoff inserts the coefficients into the actual
functions from `masters.py`, includes the physical
`dp_i^2/(2*pi)` factors, and independently re-expands the direct qqbar and qg
finite terms with exact zero residuals. For the crossed box it expands the
`11`, `10`, `01`, and analytic `00` terms separately, verifies cancellation of
the `epsilon^-2` and `epsilon^-1` endpoint coefficients, and checks the full
finite delta/plus result against the graph ledger. The longitudinal qg check
also verifies `2 triangle - box - bubble = 0` before integration.

The final validation appendix keeps three scientific objects distinct: the consistently
transverse native reconstruction, the presentation transcribed from saved Mathematica output, and the
manuscript equations 317--318 used as the physical targets. Their nonzero
residuals are displayed rather than tuned away. In particular, the qqbar soft
`D1` sign and regular term remain discrepant, while the recorded Mathematica qg/manuscript
formula differs from the transverse result by the displayed Ward remainder.
The ordinary virtual benchmark and the complex local all-cut virtual object are
also shown separately.

Opening or exporting `masters.py` never launches Kira. It reconstructs the
Feynman-parameter, radial-delta, light-cone/Sudakov, angular-orbit, and
Gram-determinant pieces. It audits the supplied `master_and_dump.pdf`, keeps
physical phase-space and historical sign conventions separate, checks the
closed forms with exact Symbolica residuals, and displays them through the
Spenso-aware Typst/MathML renderer. It also provides configurable epsilon and
plus-distribution expansions, leading-virtuality integrations, and a positive
real numerical point. Its mapping table is deliberately limited to analytic
identifications explicitly present in the source notebook; other preferred
Kira masters remain unevaluated.

The repository-root `notebooks/ludy.py` imports the analytic evaluators from
`masters.py`, including the analytic maximal-cut master `M00(s)`; it does not
maintain a second copy. It is also the single implementation site for the
process-independent propagator, cut projection, apart, numerator-reduction,
Kira-project, execution, and master-routing helpers. The DY application imports
those helpers rather than maintaining another copy.

The repository-root flake provides Python, uv, Kira, Fermat, and `FERMATPATH`;
the root uv lock installs Marimo, Symbolica Community, GammaLoop, Typst, and
the editable `kirapy` package. The package's own subflake remains available for
isolated wrapper development and tests, not for launching these notebooks.

Validate the complete notebook set from the repository root. These exports do
not press the Kira run button:

```console
direnv exec . nix develop --command uv lock --check
direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/ludy.py
direnv exec . nix develop --command uv run --locked marimo check --strict notebooks/collinear-cone.py
direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/notebook.py
direnv exec . nix develop --command uv run --locked marimo check --strict calculations/dy/python/masters.py
direnv exec . nix develop --command uv run --locked marimo export html notebooks/ludy.py \
  -o /tmp/ludy-validation.html --force
direnv exec . nix develop --command uv run --locked marimo export html notebooks/collinear-cone.py \
  -o /tmp/ludy-collinear-cone-validation.html --force
direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/notebook.py \
  -o /tmp/ludy-dy-notebook-validation.html --force
direnv exec . nix develop --command uv run --locked marimo export html calculations/dy/python/masters.py \
  -o /tmp/ludy-dy-masters-validation.html --force
```
