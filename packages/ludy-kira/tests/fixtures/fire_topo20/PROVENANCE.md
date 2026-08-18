# DY topology-20 FIRE oracle provenance

This fixture is regenerated golden evidence; it was not present as files in
the historical `temp/FIRE` snapshot (although the notebook retained its table
as a cached output cell).

- Original calculation repository:
  `https://github.com/ZenoCapatti/DIS_DY_analytic.git`
- Original calculation revision:
  `3bc8d61a7230321ac162c4709daa081236ced750`
- Original notebook SHA-256 before the portable bootstrap edit:
  `59b7406ee30e34a5756916802088dc7334214a0356d633df96020ef16124ebca`
- Curated portable notebook SHA-256 used for this run:
  `e713b5f7d3461cc52d5763bce58d76213f380c65cbaf2b8eca1c0144c1e4e009`
- `mma/IntegralTools.wl` SHA-256:
  `8ea3431f00b4586bf53682e6a07ab6d3a251da36d69d667f44e80c42baa0ffdf`
- FIRE revision: `51bd31ac3496bc0e88399ee32e4429a500fa796d`
- FIRE version: 6.5.2
- Wolfram Engine: 15.0.0 for Linux x86 (64-bit), May 31, 2026
- Regeneration script:
  `calculations/dy/mathematica/regenerate_fire_crossed_box.wls`
- Regeneration-script SHA-256:
  `e25dc0c595c9c7d6349f56926abacd066eb7de1cb6ae95a9282b030b156d865e`

The notebook's partial-fraction construction selects crossed-box propagator
indices `{1,2,3}` for family 20. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 25 explicit rules and selected exactly
`Int[20,{0,0,1}]` and `Int[20,{1,0,1}]` as implicit masters. Every family
integral remaining on a right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=20 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo20.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the existing Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `04141e0305c543ca60fe678f6cea38407b4e843d569d88f06315e4ff643f12d0` |
| `ToReduce.m` | `4c562b7e3c9b4d59423f6da423f0da7bf0414af1819cd49f0481e2629192ec8d` |
| `topo20.tables` | `192851e2e202a0039bbf67f27b8004d5798ac7a3275ed9e9fc1b45acdd842066` |
| `decoded-rules.m` | `d7df7edfc60381ced5e68a72b0419ac1896dff458df9c06356249df592fc3f16` |
| `topo20.rules.m` | `dad55f2557fe222d06e1a1d8cb91b5c22e6fa0ecb66f2965035bd78f2d330cc6` |
