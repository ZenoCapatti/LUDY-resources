# DY topology-25 FIRE oracle provenance

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
indices `{1,2,4}` for family 25. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 25 explicit rules and selected
`Int[25,{0,1,1}]`, `Int[25,{1,0,1}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=25 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo25.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `5ff7d0985c053b9e1583247209034e266774ea7d34dab705b23ee8b48ee19d19` |
| `ToReduce.m` | `833187caa630ec5d91dd76402ee8c6b38219d0fdabd2091fc427c7d34c4f0b6c` |
| `topo25.tables` | `5f903e52024e996881f5c594e2ff417cb03b78e76212aabadcc723c1e54568e2` |
| `decoded-rules.m` | `0f904cd01b32ad608e86e81cc5c5f2d0ca680cc5327bb4a1e2f96a55c7a7e5f3` |
| `topo25.rules.m` | `47a36bd2628278118a7aaaaf8b5829f7edbcdc2c6ea9b7fdb999919756eec3d7` |
