# kirapy

`kirapy` is a small, private Python wrapper for running
[Kira](https://gitlab.com/kira-pyred/kira) reductions with Symbolica
expressions. Kira and Fermat remain external executables; this package writes a
deterministic Kira project, runs it without a shell, and parses `kira2math`
output back into Symbolica.

From a fresh checkout, enter the package subflake and install the exact Python
environment recorded in `uv.lock`:

```console
$ cd packages/kirapy
$ nix develop
$ uv sync --locked
$ uv run --locked pytest -q tests
```

The portable runnable application is a separate uv project at
[`calculations/dy/python`](../../calculations/dy/python). It depends on this
package through a repository-local editable source and has its own lock and
Nix entry point. The broader
`notebooks/ludy.py` experiment uses Symbolica Community's Spenso extension and
the editable sibling repositories configured by the LUDY root project.

The subflake pins Kira 3.1 at Git revision `dad964c`, its Nix inputs, and the
official Fermat 7.9b binary. Its bundled runtime is available for Apple Silicon
macOS (`aarch64-darwin`) and x86-64 Linux only; other platforms must provide an
external Kira/Fermat runtime to the Python facade. The official Apple Silicon
Fermat executable requires macOS 26 or newer; use an external compatible
runtime on older macOS releases.

[Fermat's upstream terms](https://home.bway.net/lewis/ferm7.html) permit
redistribution, but prohibit business and for-profit use without express
written permission. The Nix package is therefore marked unfree, and users are
responsible for ensuring their use complies with those terms. Kira itself is
GPL-3.0-or-later.

`nix flake check` additionally builds the pinned runtime and runs the unit and
native topology parity checks. Under a restricted single-engine Symbolica license,
close other Symbolica, GammaLoop, or Marimo processes before starting that
check; its Symbolica test phases are serialized automatically.

```python
from pathlib import Path

from symbolica import S

from kirapy import (
    IntegralFamily,
    KinematicInvariant,
    Kinematics,
    Kira,
    Propagator,
    ReductionBounds,
    ScalarProductRule,
)

s = S("s")
k, p = S("k"), S("p")

family = IntegralFamily(
    name="topo1",
    loop_momenta=(k,),
    propagators=(Propagator(k), Propagator(k - p)),
    top_level_sectors=(3,),
)
kinematics = Kinematics(
    incoming_momenta=(p,),
    kinematic_invariants=(KinematicInvariant(s, 2),),
    scalar_products=(ScalarProductRule(p, p, s),),
)

kira = Kira(executable="kira", fermat_path=Path("/path/to/fer64"))
report = kira.doctor()
report.raise_for_errors()

result = kira.reduce(
    family=family,
    kinematics=kinematics,
    targets=(family(1, 1),),
    bounds=ReductionBounds(sectors=(3,), r=2, s=0),
    workdir=Path("build/kira/topo1"),
)
reduced_expression = result.apply(family(1, 1))
```

When Symbolica Community's Spenso extension is available, rank-one tensor
placeholders can be used directly as momenta:

```python
from symbolica import S
from symbolica.community.spenso import Representation, TensorName

mink = Representation.mink(S("D"))
p1 = TensorName.vector("p")(1, mink)
```

Every momentum, invariant, family head, and project dimension is lowered at
the text boundary from a deterministic full SHA-256 digest. Family and
momentum wires retain the full digest. Scalar invariants use a lowercase,
ten-character base-36 projection because they become Fermat polynomial
variables; projected-name collisions are rejected against the full digests.
The native expressions—including composite Spenso dot products—are restored
recursively in parsed rules, targets, and masters. The generated names and
their native expressions are available through `ProjectFiles.symbol_aliases`
and `ReductionResult.symbol_aliases`; callers never choose or handle the wire
aliases themselves.

The work directory is intentionally persistent. It contains the generated
inputs, `kirapy.json`, the checksummed `kirapy.symbolica` native-expression
state, `process.log`, Kira's own `kira.log`, and Kira's results. Pass
`resume=True` only to reuse a matching manifest. A non-empty directory without
the matching manifest is never overwritten.

`Kira.reduce(..., require_complete=True)` is strict by default: every requested
integral must have a rule or be a listed master, and every family integral left
on a right-hand side must be a listed master. Use `require_complete=False` only
when deliberately inspecting a partial run.
