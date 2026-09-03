# Splitting counter-term notebook

The Marimo notebook reconstructs the real collinear calculations from
`splitting_counter_term_computation.tex` with a shared Symbolica pipeline.
Spenso/Idenso derive all three real numerators and the virtual numerator;
Idenso also reduces the color contractions supplying `C_F`, `T_R`, and `C_A`.
The shared Sudakov convention assigns `x` to the daughter entering the hard
interaction and `1-x` to the cut daughter.

Activate the existing environment and open the notebook with:

```bash
source .venv/bin/activate
marimo edit notebooks/splitting_counter_terms.py
```

Run it as a read-only application with:

```bash
marimo run notebooks/splitting_counter_terms.py
```

Run the symbolic regression tests with:

```bash
python -m pytest
```

## Symbolic backend constraint

All mathematical expression construction and manipulation uses Symbolica,
Spenso, or Idenso. The calculation code does not import `re` or SymPy and does
not perform algebra through string or LaTeX rewriting.
