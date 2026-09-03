# General research notebooks

This directory contains interactive experiments that use the repository-root
environment. They are deliberately separate from complete, independently
locked calculations under `calculations/`.

- `ludy.py` is both the source of the DY/Kira helper implementations and a
  walkthrough of the native cross-box calculation. Each helper cell appears
  immediately before its first use, so the cross-box derivation exercises the
  implementation directly. Its project builder and resumable runner are
  module-visible for companion notebooks. The graph is
  entered as six `(momentum, mass_squared)` pairs;
  `k` is tagged as a loop momentum, so its four loop-dependent lines are
  discovered automatically. The propagators, four full cut masks, affine
  solve, partial fractions, numerator rewrite, native graph-order Kira
  projects, rule application, cut filter, analytic master evaluation, and
  scalar epsilon check are separate inspectable cells. The historical
  FIRE-order adapter exists only in the final validation appendix. Analytic
  master evaluator implementations come from
  `calculations/dy/python/masters.py`; they are not duplicated in this
  notebook. The physical trace is the default; set the native
  `user_numerator` expression in its input cell to run the same pipeline on a
  custom numerator. The worked numerator is kept separate from the scalar
  numerator used by the Mathematica/FIRE oracle.
  Mixed prose-and-formula outputs use the typed
  `typst("... {expression}", expression=value)` helper, so exact Symbolica
  objects reach Spenso's Typst printer instead of being interpolated into
  Markdown code strings.
  Cuts `11`, `10`, and `01` use twelve projects named from their cut and graph
  sources; fully cut `00` is explicitly routed to the analytic maximal-cut
  master branch outside Kira.
  The Mathematica/FIRE comparisons, generic helper checks, and other oracle
  code are collected in a final validation appendix rather than interleaved
  with the walkthrough.
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

The root project uses `../gammaloop/ludy` and `../symbolica-community`; the
Symbolica Community checkout should track its latest `simplify-spenso-api`
bookmark.
GammaLoop and Symbolica Community contain separately linked Symbolica engines,
so `ludy.py` requires a license that permits both engines in one process. For
the clone-ready DY reduction that has no sibling-checkout dependency, use
[`calculations/dy/python/notebook.py`](../calculations/dy/python/notebook.py)
with the shared root environment. That notebook imports the generic algebraic
helpers from `ludy.py`, defines its complete graph set first, and retains one
explicit batch run control.
