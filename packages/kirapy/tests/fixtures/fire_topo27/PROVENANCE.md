# DY topology-27 FIRE oracle provenance

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
indices `{2,3,4}` for family 27. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 23 explicit rules and selected
`Int[27,{0,1,0}]`, `Int[27,{1,0,1}]`, `Int[27,{1,1,0}]`, `Int[27,{1,1,1}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=27 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo27.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `63a33102c6bdc3d7360d936d2ca347011c0b8df68aa57ff66f508b6334a1b85d` |
| `ToReduce.m` | `fa073dbd911f9ed39edd2843c7cd817669630a911c6fb2112a70925cd85e0807` |
| `topo27.tables` | `82383a3975cb50a5f93adb7dbb7d092bc26602dd9a8864b8e9346d8f496f7c3c` |
| `decoded-rules.m` | `fcaa0d83fb458d4b6efd6f0cf2d563ed56d75f273f8f8d6e2f3269679971777e` |
| `topo27.rules.m` | `1a91a0ccbcd691c387243f97a996fbf9dc2f18c201c037beaf2474a1a4af9fad` |
