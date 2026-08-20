# DY topology-23 FIRE oracle provenance

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
indices `{2,3,4}` for family 23. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 24 explicit rules and selected
`Int[23,{0,1,0}]`, `Int[23,{1,0,1}]`, `Int[23,{1,1,1}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=23 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo23.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `c292a19d7069c413be46f72b6ad70fefb7040376cc944dabfb8e18ed98a823eb` |
| `ToReduce.m` | `aedcebb796f68ac54cef91e5165da908356f6656153be71d5c7f893b763b86ef` |
| `topo23.tables` | `8388442e8919f760f6165c0dd6f0b05ae086e8b16f7671b25ecba50b7f633077` |
| `decoded-rules.m` | `311dedd2f5ad5339d9c4c54d92f79574653ec6511e23efdecfd5b2fd51e5f62b` |
| `topo23.rules.m` | `b69fcc669f7bd692903566bd3bf543ba595bd7256debbd16d58fafad91fc5647` |
