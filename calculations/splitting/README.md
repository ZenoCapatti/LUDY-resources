# Splitting counter-term calculation

This calculation reconstructs the real and virtual collinear splitting
counter-terms with Symbolica, Spenso, and Idenso. The reusable
`splitting_kernels` package derives the three real numerators and the virtual
numerator, reduces the color contractions supplying `C_F`, `T_R`, and `C_A`,
and performs the phase-space and normalization checks. The shared Sudakov
convention assigns `x` to the daughter entering the hard interaction and
`1-x` to the cut daughter. Counterterms and splitting kernels use standard
daughter-first DGLAP ordering: in `D_ij` and `P_ij`, `i` is the daughter
entering the hard interaction and `j` is the parent parton.

The calculation is an independent validation layer. Its symbolic results are
not inputs to the native DIS or Drell--Yan assemblies.

## Environment

The package is installed as an editable local source by the repository-root
uv project. Use the root lock and Nix shell; no separate `.venv` is required.

From the repository root:

```console
$ nix develop
$ uv sync --locked
$ uv run --locked marimo edit calculations/splitting/notebooks/splitting_counter_terms.py
```

Run the notebook as a read-only application with:

```console
$ uv run --locked marimo run calculations/splitting/notebooks/splitting_counter_terms.py
```

Run its symbolic regression suite with:

```console
$ uv run --locked pytest calculations/splitting/tests
```

For a licensed non-interactive environment, prefix these commands with
`direnv exec . nix develop --command` as shown in the root README. Keep the
license outside the repository.

## Symbolic backend boundary

Mathematical expression construction and manipulation use Symbolica, Spenso,
or Idenso. The calculation does not implement algebra through regular
expressions, SymPy, or string/LaTeX rewriting. Preserve exact expression-level
comparisons in the tests when extending the calculation.
