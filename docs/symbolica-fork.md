# Why LUDY can use official Symbolica dev

The current upstream baseline is official Symbolica `dev` at
[`d6bb961`](https://github.com/symbolica-dev/symbolica/commit/d6bb961d22c026c4866b2e698f56fbb964c4ee0e).
Standalone state round trips were retested against that exact revision:

- canonical strings now correctly ignore custom display printers;
- atom-valued map keys no longer produce `Invalid magic number`; and
- an atom-valued user-data coefficient can still reload with the wrong
  rational-polynomial variable list in a deliberately constructed edge case.

LUDY and kirapy do not construct the failing representation: they do not put an
`Atom::num(Coefficient::RationalPolynomial(...))` inside another symbol's user
data. Their persisted aliases use ordinary expressions, with the original
expressions stored separately. Official `d6bb961` is therefore sufficient for
the current calculation and is the revision pinned by kirapy and the dependent
Rust graph. The rational-polynomial reproducer remains useful as an upstream
API regression case, but it is not a runtime requirement for LUDY.

## What upstream fixed

A custom printer is a process-local display callback. It is useful for normal
formatting, but it is not serialized and therefore cannot define a persistent
identity. At `d6bb961`, `to_canonical_string()` bypasses that callback while
ordinary formatting still uses it. Kirapy aliases derived from canonical
strings are therefore stable across this boundary without a local printer
patch.

Upstream had already fixed the smaller atom-key import failure in
[`215c2bb`](https://github.com/symbolica-dev/symbolica/commit/215c2bbe4e7ab6422d105156c5a1da33df940a27):
an atom embedded as a `UserData::Map` key is no longer mistaken for a nested
state header and no longer reports `Invalid magic number`.

`d6bb961` also collects symbols referenced by rational-polynomial
coefficients. That is necessary, but it does not by itself preserve the
coefficient's variable mapping.

## The remaining upstream edge case

A rational polynomial such as `1 + x` contains two related pieces of state:

- coefficients and exponent columns, where a column is addressed by a numeric
  slot; and
- a variable list saying what each slot means, for example `slot 0 = x`.

The expression stored in user data is an atom, but its rational-polynomial
payload still refers to that separate variable-list registry. Exporting the
referenced symbol is not enough. The state must also export the referenced
list, and import must reconnect the polynomial to the imported list rather
than to whichever list happens to occupy the same process-local index.

The
[`user-data-variable-list.rs`](../reproducers/symbolica-state-round-trip/user-data-variable-list.rs)
MWE deliberately changes allocation order between save and load. Retargeted to
`d6bb961`, it still reloads `1 + coefficient_parameter` as a polynomial in
`padding_parameter`. This matters to callers that serialize this precise
coefficient payload in user data; current LUDY and kirapy code does not.

## Compatibility now lives with the callers

The former Symbolica compatibility layer mixed this state fix with adapters
for several dependent crates. Those adapters have been ported to the callers:

- GammaLoop and Vakint use their explicit strict-linear contract over the new
  solve API;
- the `symbolica-integrate` fork reads variables through `variables()` and
  changes them with `rename_variable()` rather than mutating a private
  polynomial context; and
- the Spynso/Community fork performs the `PythonNormalization` conversion at
  its Rust boundary.

GammaLoop, symbolica-integrate, and Symbolica Community retain their
caller-side compatibility changes at `4f44c863`, `306a6f4b`, and `4f62108b`,
respectively, but all Symbolica, Numerica, and Graphica source identities in
that graph resolve to exact official `d6bb961`.

## Reproducer policy

The copy-pasteable Rust scripts under
[`reproducers/symbolica-state-round-trip`](../reproducers/symbolica-state-round-trip)
keep their embedded historical revisions so each original failure remains
reproducible. Temporary copies retargeted to `d6bb961` establish the current
split described above. The variable-list MWE should stay in the repository
until upstream makes the loaded coefficient use `coefficient_parameter`
regardless of variable-list allocation order; passing it is no longer a
condition for LUDY's dependency pin.
