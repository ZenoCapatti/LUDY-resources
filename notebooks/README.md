# General research notebooks

This directory contains interactive experiments that use the repository-root
environment. They are deliberately separate from complete, independently
locked calculations under `calculations/`.

- `ludy.py` is the local GammaLoop/Symbolica Community/Spenso research
  notebook. It also demonstrates the `ludy-kira` API with native Spenso
  momentum expressions.
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
with its own environment.
