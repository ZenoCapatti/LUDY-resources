# DY topology-30 FIRE oracle provenance

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
indices `{1,3,4}` for family 30. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 24 explicit rules and selected
`Int[30,{0,1,0}]`, `Int[30,{0,1,1}]`, `Int[30,{1,1,0}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=30 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo30.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `14f3aef6276764c45d565494303f1943be3f1cf4c24f3b13ad8faba581e9862c` |
| `ToReduce.m` | `446d4573966cd7f3502cf957de3821a6f385b23c92dc19fbf84a5712106a2415` |
| `topo30.tables` | `18e2546605e673e51f96f4375b212ea3e960b1257a0198f1361e1721b4ed27fc` |
| `decoded-rules.m` | `47d46870fc9d32bd5d47e292990a41c67987957f7d444eb703cdb1876873a4bb` |
| `topo30.rules.m` | `ac5992bece8c4047c43433f7f7b438fae80e227590f688fcd0347d59d614e265` |
