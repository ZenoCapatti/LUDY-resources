# DY topology-29 FIRE oracle provenance

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
indices `{1,2,4}` for family 29. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 25 explicit rules and selected
`Int[29,{0,1,1}]`, `Int[29,{1,1,0}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=29 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo29.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `ba3348f8ea0336cbeae3d847d14e5d68680b2c6a6d6d75482db7ed113f6204dc` |
| `ToReduce.m` | `9968f071f1c074fc1ed6e6d7eb49289a34a03891d78e789dace34a5c44bcf50c` |
| `topo29.tables` | `02b38c9b7d18f4577c2ad544fcaca1738fef8afd165386cbb94ed56f3c011de1` |
| `decoded-rules.m` | `de6e1c4683b31f62da78442322983ac926f3dc59d47d02596fbc96ce0e4b424d` |
| `topo29.rules.m` | `69bb6d48aa70e502e983456439f60a2421d9feeaa0f300c1449b8e0c43fbb119` |
