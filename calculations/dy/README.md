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
    notebook.py                portable topology-1 Kira workflow
    pyproject.toml, uv.lock    application dependencies
    flake.nix, flake.lock      Kira/Fermat development runtime
```

The Mathematica notebook is the scientific source context. Its topology-1 FIRE
input and table are retained as golden evidence. The Python notebook expresses
that topology through `packages/ludy-kira`, requests the same 27 target
integrals, and parses the Kira result as exact Symbolica expressions.

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
```

Opening or statically checking the notebook does not start a reduction. Press
the run button to create or resume its ignored Kira work directory. The Nix
shell supplies the pinned Kira/Fermat executables and `FERMATPATH`; alternatively
configure compatible executables outside Nix.

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

$ cd ../../calculations/dy/python
$ nix flake check
$ nix develop --command uv lock --check
$ nix develop --command uv run --locked marimo check --strict notebook.py
```

The package tests own the exact FIRE/Kira parity oracle; the application check
ensures the complete notebook remains structurally runnable.
