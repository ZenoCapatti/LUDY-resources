# Manuscript

This directory contains the manuscript and the local sources it includes:

- `main.tex`: REVTeX manuscript;
- `apssamp.bib`: bibliography;
- `region_xbox.tex` and `region_triangle.tex`: local diagram inputs.

Build from this directory with a TeX installation that provides REVTeX and the
required bibliography tooling, for example:

```console
$ cd paper
$ latexmk -pdf main.tex
```

Generated TeX products and PDFs are not repository sources and must remain
untracked.

## Scientific source

The regularised DIS and Drell--Yan coefficients in `main.tex` are generated and
audited by the native notebooks under `calculations/dis/` and
`calculations/dy/`. Those calculations, their graph and cut records, and their
literature comparisons are the executable source of truth for the manuscript
formulas. The repository history keeps the manuscript transcription separate
from the preceding migration and code changes so that both layers remain
independently reviewable.
