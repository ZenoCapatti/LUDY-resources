# General research notebooks

This directory contains interactive experiments that use the repository-root
environment. They are deliberately separate from complete, independently
locked calculations under `calculations/`.

- `ludy.py` is the local GammaLoop/Symbolica Community/Spenso research
  notebook. Its native cross-box model is validated against the Mathematica
  calculation. The graph is entered as six `(momentum, mass_squared)` pairs;
  `k` is tagged as a loop momentum, so its four loop-dependent lines are
  discovered automatically. The propagators, four full cut masks, affine
  solve, partial fractions, numerator rewrite, historical FIRE-order adapter,
  Kira mapping, rule application, cut filter, `Bcutm`/`Tcutm` identification,
  analytic master evaluation, and scalar epsilon check are separate
  inspectable cells. Every scientific helper is exercised by an executable
  showcase or an exact derivation assertion. The editable Python numerator is
  kept separate from the scalar numerator used by the Mathematica/FIRE oracle.
  Cuts `11`, `10`, and `01` use the twelve topo20--31 Kira projects; fully cut
  `00` is explicitly routed to a direct four-line branch.
  The implementation is defined directly in the notebook rather than a
  separate preprocessing module.
  Evaluating this root notebook automatically runs or resumes its twelve Kira
  projects. Complete outputs are reused only when their persisted project
  manifests still match the notebook inputs exactly.
- `collinear-cone.py` is the independent interactive cone visualization.

Run either notebook from the repository root so the editable sibling sources
and generated paths resolve consistently:

```console
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit notebooks/ludy.py
```

The root project uses `../gammaloop/main` and `../symbolica-community`.
GammaLoop and Symbolica Community contain separately linked Symbolica engines,
so `ludy.py` requires a license that permits both engines in one process. For
the clone-ready DY reduction that has no sibling-checkout dependency, use
[`calculations/dy/python/notebook.py`](../calculations/dy/python/notebook.py)
with its own environment. That portable notebook retains an explicit run
button; the root research notebook does not.
