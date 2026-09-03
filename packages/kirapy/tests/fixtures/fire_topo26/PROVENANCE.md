# DY topology-26 FIRE oracle provenance

This fixture is regenerated golden evidence for a DY family whose historical
FIRE directory was not retained.

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
indices `{1,3,4}` for family 26. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 23 explicit rules and selected
`Int[26,{0,1,0}]`, `Int[26,{1,0,1}]`, `Int[26,{1,1,0}]`, `Int[26,{1,1,1}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=26 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo26.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `2d9223ced53595047e70dd3e06ca81d6851f17454e4546a2bb2dd5cd216e2025` |
| `ToReduce.m` | `bb750c981e70ad96bb67188415d812fbca4d1257cb4b8f7bdc341b13fc493a89` |
| `topo26.tables` | `890dcfbefb71188755bcd5e816c7aa5fc7128da022c040f6a0de39f5b55ffd72` |
| `decoded-rules.m` | `070289c3166da4aee8f61a7b665ca459d77772efe76e0ec34229803bc9c20edd` |
| `topo26.rules.m` | `a673963193812cdeae8b7007b6b22f14205391572031935c0c1bb1697d6b3a45` |
