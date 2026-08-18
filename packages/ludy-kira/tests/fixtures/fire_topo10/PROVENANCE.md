# DY topology-10 FIRE oracle provenance

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
  `calculations/dy/mathematica/regenerate_fire_topo10.wls`
- Regeneration-script SHA-256:
  `59da9f7a4c0a1f35c299acda3a2a698abf01a40c8f14dc54e9084d34099326bd`

The run requested all 125 ordered targets in
`Tuples[{2, 1, 0, -1, -2}, 3]`. FIRE emitted 123 explicit rules and selected
exactly `Int[10,{0,0,1}]` and `Int[10,{1,0,1}]` as implicit masters. Every
family integral remaining on a right-hand side is one of those masters.

The portable regeneration command is:

```console
FIRE_ROOT=/absolute/path/to/FIRE6 \
LUDY_FIRE_GOLDEN_ROOT=/absolute/path/to/external/output \
wolframscript -file calculations/dy/mathematica/regenerate_fire_topo10.wls
```

`topo10.rules.m` is a lossless syntax conversion of `decoded-rules.m`: it
replaces `Int[10,{a,b,c}]` by `topo10[a,b,c]` and
`IP[p[1],p[2]]` by `ipp1p2`, allowing the existing exact Kira-output parser to
read the oracle without adding a FIRE binary-table parser.

The immutable fixture hashes are:

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `37f890f88aadd91e19378514e2f3e4ff4fa94ead4ab0356ab548d93a51fd209a` |
| `ToReduce.m` | `0767735cff6f21119f2ea25142f9807d7d6e505c2e504f42a8850ee71a491ab6` |
| `topo10.tables` | `6d57d07b1ba42285815d61bcd96059f856df1c9160d1e8a7765eb0acde4f0799` |
| `decoded-rules.m` | `c1676fa44aea303105b4e86744af6fe133fa77135f8b63086ef8d9880d2e1e5a` |
| `topo10.rules.m` | `7809c30d2f0942cfbd0e31290f34a52d4a2d2e49482892abc8ca9ae17acfb669` |
