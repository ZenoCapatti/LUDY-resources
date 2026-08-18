# DY topology-21 FIRE oracle provenance

This regenerated golden evidence comes from the original calculation revision
`3bc8d61a7230321ac162c4709daa081236ced750` and its curated portable notebook
(SHA-256 `e713b5f7d3461cc52d5763bce58d76213f380c65cbaf2b8eca1c0144c1e4e009`).
It used FIRE revision `51bd31ac3496bc0e88399ee32e4429a500fa796d`
(FIRE 6.5.2), Wolfram Engine 15.0.0 for Linux x86 (64-bit), and
`calculations/dy/mathematica/regenerate_fire_crossed_box.wls` (SHA-256
`e25dc0c595c9c7d6349f56926abacd066eb7de1cb6ae95a9282b030b156d865e`).

The notebook partial-fraction ordering selects crossed-box propagator indices
`{1,2,4}`. All 27 ordered targets in `Tuples[{1,0,-1},3]` were requested.
FIRE emitted 26 explicit rules and selected `Int[21,{0,1,1}]` as its only
master; no other family integral remains on a right-hand side.

Regenerate externally with `FIRE_ROOT`, `LUDY_FIRE_GOLDEN_ROOT`, and
`LUDY_FIRE_TOPOLOGY_ID=21`, then run
`wolframscript -file calculations/dy/mathematica/regenerate_fire_crossed_box.wls`.

| File | SHA-256 |
| --- | --- |
| `FIREinput.m` | `45a6e57c099f461181e5a5b1cde7eddde0cef45b9002ed2a327aed21f3a87d61` |
| `ToReduce.m` | `cd3a19a8f046e83d9cc2db1d5a60b00ef2452b0a3d139c040f2ed9b93a98155b` |
| `topo21.tables` | `c14ae5ef81e515f4c94f2dd92ff90113aed9215cc22c29983117556812c0f4c3` |
| `decoded-rules.m` | `f03f62825ace32360586032eaeb60126e6ae0b8ffd3c5e8318f77bd38b4a0b0b` |
| `topo21.rules.m` | `f18d395123cb7fd2eb9ae6fe70db78c991aca6d569134d49e91b731b2e13ee79` |
