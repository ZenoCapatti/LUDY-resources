# DY topology-22 FIRE oracle provenance

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
indices `{1,3,4}` for family 22. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 25 explicit rules and selected
`Int[22,{0,1,0}]`, `Int[22,{1,1,0}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=22 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo22.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `1d7dd9a70da4aa13e40eb827660f580ad3ad97df6c05680d6376af0bb4515d7e` |
| `ToReduce.m` | `137d63ea35cc96f9b8c32c949467018e961c7e71db62456e4aaa37d9815bbc9b` |
| `topo22.tables` | `16f01d7cbe16055f8faa1b5bc73b47812475e9a24f67576edee7b9b7d34a7d8a` |
| `decoded-rules.m` | `fc73f4e6bef0cfc900b6abdb8672a4f0f94a17a4b8e8496cf987c6c1c4808ea1` |
| `topo22.rules.m` | `d2c6b181cb3892e2215a3b694cf79d9e5a0752415cc62dd732811260b03ac799` |
