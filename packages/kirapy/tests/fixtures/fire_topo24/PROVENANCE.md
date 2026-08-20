# DY topology-24 FIRE oracle provenance

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
indices `{1,2,3}` for family 24. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 24 explicit rules and selected
`Int[24,{0,0,1}]`, `Int[24,{0,1,1}]`, `Int[24,{1,0,1}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=24 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo24.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `c80498f9eb78646452af758fbfee2f224ec9e36b016dea4ae3e96edd507f13f0` |
| `ToReduce.m` | `594948af599333dd6fefc93dcdfeac9691bc6bca60362e8fe9b358d8a188a52a` |
| `topo24.tables` | `e4529faa1e9908b0ecc858532b057490f96ffb80c65f1071f8a9d6be7760ac43` |
| `decoded-rules.m` | `4e7da6cc05ea8855c4a4aa48d1a11afcb52017a69756130570ec24afba419247` |
| `topo24.rules.m` | `94bcf5ff8fefec521ed852bae86797ac8f6048ad301ffbed0291ed58c688485f` |
