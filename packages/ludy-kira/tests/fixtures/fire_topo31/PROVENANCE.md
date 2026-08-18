# DY topology-31 FIRE oracle provenance

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
indices `{2,3,4}` for family 31. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 23 explicit rules and selected
`Int[31,{0,1,0}]`, `Int[31,{0,1,1}]`, `Int[31,{1,0,1}]`, `Int[31,{1,1,1}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=31 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo31.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `02fae93a5a5b768f9528a5b2c6ec738f6509310a6dbcc055d73cc957c6d8a91d` |
| `ToReduce.m` | `d95d7e90b5b7322774f3cebb5f5478ec786c7de3d56ed2b27f0f113c4c5d52b5` |
| `topo31.tables` | `92db1ca64114f8cbabed180ec4400d5f5776eabd96b5e5c60304340acaad0b24` |
| `decoded-rules.m` | `115825595a5f2a1ef1f10d068324b15244dfadd92a3f570d9a745910ddd7c19d` |
| `topo31.rules.m` | `7b2d51f82ba33fe22383fc789e7656d96a0e77d4cf80b94d0e84d301acdf9cef` |
