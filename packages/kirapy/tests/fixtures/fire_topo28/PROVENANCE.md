# DY topology-28 FIRE oracle provenance

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
indices `{1,2,3}` for family 28. The run requested all 27 ordered targets in
`Tuples[{1, 0, -1}, 3]`. FIRE emitted 23 explicit rules and selected
`Int[28,{0,0,1}]`, `Int[28,{1,0,1}]`, `Int[28,{1,1,0}]`, `Int[28,{1,1,1}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
LUDY_FIRE_TOPOLOGY_ID=28 \
wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls
```

`topo28.rules.m` is a lossless syntax conversion of `decoded-rules.m` into
the exact Mathematica syntax consumed by the Kira-output parser.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `c9fd85fdf72cb6cc56e9a3826f96bfac01d2a02f7d9163d239b6e13ea6e896d0` |
| `ToReduce.m` | `424354ca0d7d2f3b529c27a3aab932c71bad937cdfbcfa68601cb94b11b7bc1f` |
| `topo28.tables` | `6161e434db236f9134a04646b1f1175bc8febfe1008c023dcccb58145b3a4fea` |
| `decoded-rules.m` | `a1a81d82d2cab205f81f94961702fa13af5c537d9750b51a9a7655e4b357b28e` |
| `topo28.rules.m` | `fa4cfba273ad4b8a5cb5e65e95f99a2ea0be97cc8e6e2acc7cc4808f9ef5ba4b` |
