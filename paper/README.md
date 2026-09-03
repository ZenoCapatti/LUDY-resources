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

## Integration status

The repository migration deliberately lands and validates the organized native
calculations before updating the paper. At this point in the integration stack,
`main.tex` still represents the pre-correction manuscript. The corrected DIS
and Drell--Yan coefficients are produced and audited by the native notebooks;
their manuscript transcription belongs to the subsequent isolated paper-only
commit. This sequencing keeps repository migration, executable evidence, and
scientific prose independently reviewable.
