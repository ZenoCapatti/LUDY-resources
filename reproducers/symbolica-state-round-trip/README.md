# Minimal Symbolica state-persistence reproductions

Each file is a standalone [`rust-script`](https://rust-script.org/) program:
its exact Symbolica revision and all Cargo metadata are embedded in the source.
There is no Cargo project to clone or edit. From this repository, run a case
inside the existing kirapy development environment with:

```console
$ nix develop ./packages/kirapy --command \
    nix run nixpkgs#rust-script -- \
    reproducers/symbolica-state-round-trip/<case>.rs
```

With `rust-script` and a sufficiently recent Rust toolchain already installed,
the shorter command is simply:

```console
$ rust-script <case>.rs
```

The source files retain their historical failing revisions so the original
reports stay copy-pasteable. Temporary copies were also retargeted to official
Symbolica `dev` at
[`d6bb961`](https://github.com/symbolica-dev/symbolica/commit/d6bb961d22c026c4866b2e698f56fbb964c4ee0e):
the canonical-printer case now passes, while the rational-polynomial
variable-list case still fails.

## Custom printers change the canonical identity

**Issue title:** `to_canonical_string()` uses a custom display printer

[`canonical-printer.rs`](canonical-printer.rs) registers a symmetric, tagged
head whose display callback returns `PRETTY`. On official `dev` at `11fff311`,
ordinary display and canonical display are both `PRETTY(...)`:

```text
display:   PRETTY
canonical: PRETTY(mwe::{}::x)
```

The final assertion expects the registered namespace, attributes, tags, and
head instead. Custom printers are process-local closures and are not restored
with an imported state, so using one in `to_canonical_string()` makes hashes or
aliases derived from that string change across a save/load boundary. Canonical
printing should ignore the display callback; normal formatting should keep
using it.

```console
$ rust-script canonical-printer.rs
```

This was open at the embedded `11fff311` base and was originally fixed by
[`217ae31`](https://github.com/alphal00p/symbolica/commit/217ae31d9feb82bfc0c094b0bbda8cb4e0ddfbf5).
Official `d6bb961` now has the same canonical-printing behavior, so LUDY no
longer needs a printer patch.

## A saved coefficient can come back with the wrong variable

**Issue title:** `UserData::Atom` can load a polynomial with the wrong variable

A rational-polynomial coefficient is an exact expression such as `1 + x`.
Symbolica stores it as two linked pieces:

- polynomial data that uses numbered variable slots;
- a list saying which variable each slot means, for example `slot 0 = x`.

[`user-data-variable-list.rs`](user-data-variable-list.rs) attaches
`1 + coefficient_parameter` to a symbol and saves it. It then clears the state
and creates `1 + padding_parameter`, so the first variable slot now means
`padding_parameter`.

On official `dev` at `11fff311`, loading restores the polynomial data but uses
the new meaning of the slot. The numbers and powers are unchanged, but the
variable is wrong. The script ends with:

```text
loaded coefficient uses the wrong variable
```

The saved state must include the slot-to-variable list used by the coefficient.
Loading must reconnect the coefficient to that saved list.

```console
$ rust-script user-data-variable-list.rs
```

This was open at the embedded `11fff311` base and remains open when the script
is retargeted to official `d6bb961`. That upstream revision collects the
coefficient's referenced symbol, but it still does not persist and remap the
separate variable list. A minimal state-import fork remains necessary.

## Atom-valued user-data keys were read as nested states

**Issue title:** Importing an atom-valued `UserData::Map` key reports
`Invalid magic number`

[`atom-key-invalid-magic.rs`](atom-key-invalid-magic.rs) is pinned to the exact
pre-fix commit `9c7b027`. It exports a symbol whose user-data map has a single
atom-valued key. Import fails with:

```text
called `Result::unwrap()` on an `Err` value: Custom {
    kind: InvalidData,
    error: "Invalid magic number: the file is not exported from Symbolica"
}
```

The atom key is embedded with `AtomView::write`, without a state header, but
that revision reads it with `Atom::import`, which expects a new state header.
It should instead read the embedded atom payload in the already-imported
state.

```console
$ rust-script atom-key-invalid-magic.rs
```

This historical bug is already fixed upstream by
[`215c2bb`](https://github.com/symbolica-dev/symbolica/commit/215c2bbe4e7ab6422d105156c5a1da33df940a27).
