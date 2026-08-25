#!/usr/bin/env rust-script
//! ```cargo
//! [dependencies]
//! symbolica = { git = "https://github.com/symbolica-dev/symbolica", rev = "11fff3116da997fcc500ae918f052f99e1a40062", default-features = false, features = ["no_gmp"] }
//!
//! [patch.crates-io]
//! numerica = { git = "https://github.com/symbolica-dev/symbolica", rev = "11fff3116da997fcc500ae918f052f99e1a40062" }
//! graphica = { git = "https://github.com/symbolica-dev/symbolica", rev = "11fff3116da997fcc500ae918f052f99e1a40062" }
//! ```

use symbolica::{
    atom::{Atom, AtomCore, UserData},
    coefficient::Coefficient,
    domains::{integer::Z, rational::Q},
    parse, state::State, symbol,
};

fn coefficient_atom() -> Atom {
    let polynomial = parse!("1 + mwe::coefficient_parameter")
        .to_rational_polynomial::<_, _, u16>(&Q, &Z, None);
    Atom::num(Coefficient::RationalPolynomial(polynomial))
}

fn main() {
    let bytes = {
        let owner = symbol!("mwe::owner", data = UserData::Atom(coefficient_atom()));
        let mut bytes = vec![];
        owner.to_atom().export(&mut bytes).unwrap();
        bytes
    };

    unsafe { State::reset() };
    let _padding = parse!("1 + mwe::padding_parameter")
        .to_rational_polynomial::<_, _, u16>(&Q, &Z, None);

    let imported = Atom::import(&mut bytes.as_slice(), None).unwrap();
    let imported_owner = imported.get_symbol().unwrap();
    let expected = UserData::Atom(coefficient_atom());

    assert!(
        imported_owner.get_data() == &expected,
        "loaded coefficient uses the wrong variable"
    );
}
