# DY topology-11 FIRE oracle provenance

This fixture is regenerated golden evidence; it was not present in the
historical `temp/FIRE` snapshot.

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
  `calculations/dy/mathematica/regenerate_fire_topo11.wls`
- Regeneration-script SHA-256:
  `0a08c4f41ab2d004b4872c65d880db39eca51e9fa1e7443d393ed68742c74c7b`

The run requested all 125 ordered targets in
`Tuples[{2, 1, 0, -1, -2}, 3]`. FIRE emitted 121 explicit rules and selected
exactly `Int[11,{0,0,1}]`, `Int[11,{1,0,1}]`, `Int[11,{1,1,0}]`, and
`Int[11,{1,1,1}]` as implicit masters. Every family integral remaining on a
right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
wolframscript -file calculations/dy/mathematica/regenerate_fire_topo11.wls
```

`topo11.rules.m` is a lossless syntax conversion of `decoded-rules.m`: it
replaces `Int[11,{a,b,c}]` by `topo11[a,b,c]`, `IP[p[1],p[1]]` by
`ipp1p1`, and `IP[p[1],p[2]]` by `ipp1p2`. This lets the existing exact
Kira-output parser read the oracle without adding a FIRE binary-table parser.

The immutable fixture hashes are:

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `0ab60f59a9370f3f297d6222b204dadddb2551aed161e77c7da62d7c8fb718c9` |
| `ToReduce.m` | `7f237226fa03df3cc6cf9576883fb5632ddbc7101a9d3bab8262a13d8142a406` |
| `topo11.tables` | `10e51a88cd4580f13345a3e2fa09b815db51428bf17e7219f9528df98dcfd068` |
| `decoded-rules.m` | `5d2d324b3bc3d72ba326a80e45e82c27a83e706bc672c656a9208a63d08a35ee` |
| `topo11.rules.m` | `0314c908ac2a2d373b819564bc6a5b4651c3c82237b0f01b3d728902d5f0e8f8` |
