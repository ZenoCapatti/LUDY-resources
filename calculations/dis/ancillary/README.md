# Official DIS ancillary integrands

The authoritative ancillary files for
[arXiv:2506.16489v1](https://arxiv.org/abs/2506.16489v1) are hosted by arXiv:

- [`dataDT.m`](https://arxiv.org/src/2506.16489v1/anc/dataDT.m)
- [`dataSE.m`](https://arxiv.org/src/2506.16489v1/anc/dataSE.m)

The version-qualified URLs are intentional. A later arXiv version may change
the files and must be reviewed and recorded as a new source rather than being
accepted under the v1 hashes below.

## Integrity and counts

The official v1 files inspected for this calculation have:

| file | bytes | `wc -l` | embeddings | `a1` records | `a2` records | SHA-256 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `dataDT.m` | 301518 | 449 | 20 | 12 | 20 | `bea50339af20ec52cb52ddd620b3eebadba080f8ad6eed18d60312b225e8224b` |
| `dataSE.m` | 241701 | 741 | 34 | 26 | 26 | `2cd5e6b0e8337ed1036079f493eca11e920df18c0c2dcd578908ea66b89f2b60` |

Thus the double-triangle (`DT`) data contains 20 embeddings and 32 rooted
initial-electron choices, while the self-energy (`SE`) data contains 34
embeddings and 52 choices. The paper reports the corresponding generation
inventory as 70 rooted DT cuts and 124 rooted SE cuts before quotienting to
these 54 non-isomorphic embeddings; every retained embedding has symmetry
factor one.

To download and verify exact local copies deliberately, run from the repository
root:

```console
$ curl -fL https://arxiv.org/src/2506.16489v1/anc/dataDT.m -o calculations/dis/ancillary/dataDT.m
$ curl -fL https://arxiv.org/src/2506.16489v1/anc/dataSE.m -o calculations/dis/ancillary/dataSE.m
$ shasum -a 256 calculations/dis/ancillary/dataDT.m calculations/dis/ancillary/dataSE.m
```

Do not reformat the downloaded Mathematica expressions before checking their
hashes. If exact copies are retained locally, changes in byte count or hash
must be treated as a source update, not as a harmless formatting edit.

## Mathematica schema

Each file is a Mathematica list of associations. A normalized outline is:

```mathematica
{
  <|
    "embedding" -> {w1, w2, w3, w4},
    "a1" -> <|
      "Cut content" -> qGamma,
      "Denominator" -> denominator,
      "Numerator" -> <|
        "F2" -> projectedF2,
        "FL" -> projectedFL,
        "zero" -> wardContraction
      |>
    |>,
    "a2" -> <| ... |>
  |>,
  ...
}
```

`"embedding"` is the four-component winding vector for one non-isomorphic
vacuum-graph embedding. `"a1"` and `"a2"` select the possible initial-state
electron; either key may be absent when no compatible rooted cut exists. Each
such record contains:

- `"Cut content"`: the cut-content label of the embedding;
- `"Denominator"`: the propagator expression, written with `prop[m, momentum]`
  and possibly raised propagator powers. The source appendix defines
  `prop[m, momentum] = 1/(momentum^2-m^2)`; importers must nevertheless
  preserve literal powers such as `prop[...]^-1` exactly as stored;
- `"Numerator"["F2"]`: the numerator after the `F_2` projection;
- `"Numerator"["FL"]`: the numerator after the `F_L` projection; and
- `"Numerator"["zero"]`: the contraction with `q^mu q^nu`, supplied as a Ward
  identity check.

The integration momentum is named `k[2]` or `k[3]` according to the embedding.
The source documentation uses the Mathematica replacement
`/. {k[x_] :> k}` when a uniform loop-momentum name is wanted. Couplings and
parameters remain symbolic: `G`, `eq`, `Nc`, `TF`, and `dim = d = 4-2 epsilon`.

## Python audit API

`../python/ancillary.py` exposes the pinned information as
`ANCILLARY_SPECS`. `audit_ancillary_bytes()` and `audit_ancillary_file()` check
the exact SHA-256, byte and `wc -l` counts, and the documented association-key
inventory. `fetch_ancillary()` downloads one requested fixture atomically and
refuses bytes that do not match the pinned v1 specification. It is the module's
only network-writing operation and is never called by import or automatic
notebook evaluation.

The metadata-only inventory check requires no network access:

```console
$ direnv exec . nix develop --command uv run --locked python -c 'from calculations.dis.python.ancillary import self_check; self_check()'
```

## Provenance and validation boundary

The ancillary schema is documented in the arXiv source appendix “Embedding
tables and description of supplementary material.” The paper states that the
embedding generation code is available at
[`lcnbr/dis`](https://github.com/lcnbr/dis) and that the generated
forward-scattering diagrams were independently compared with GammaLoop v0.3.3.

These files are authoritative source data for the embedding ledger,
propagators, projected numerators, and Ward contractions. They do **not**
contain:

- numerator-reduction or IBP replacement rules;
- Kira/FIRE jobs or reduction tables;
- the rational coefficients multiplying the cut master integrals;
- master substitutions or virtuality/distribution expansions; or
- assembled physical `F_2` and `F_L` coefficient functions.

Consequently, reproducing an ancillary expression or using the `"zero"`
channel to demonstrate the required Ward cancellation is source-transcription
or algebraic-validation evidence. It is not by itself a physical validation of
the DIS result. The additional requirements are tracked in
[`../README.md`](../README.md).
