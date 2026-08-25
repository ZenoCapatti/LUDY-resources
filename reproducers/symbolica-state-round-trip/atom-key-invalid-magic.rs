#!/usr/bin/env rust-script
//! ```cargo
//! [dependencies]
//! symbolica = { git = "https://github.com/symbolica-dev/symbolica", rev = "9c7b0274980ea9a05802fca41f0888bcbbcd0a8c", default-features = false, features = ["no_gmp"] }
//!
//! [patch.crates-io]
//! numerica = { git = "https://github.com/symbolica-dev/symbolica", rev = "9c7b0274980ea9a05802fca41f0888bcbbcd0a8c" }
//! graphica = { git = "https://github.com/symbolica-dev/symbolica", rev = "9c7b0274980ea9a05802fca41f0888bcbbcd0a8c" }
//! ```

use symbolica::{
    atom::{Atom, AtomCore, UserData, UserDataKey},
    parse, state::State, symbol,
};

fn main() {
    let bytes = {
        let key = UserDataKey::Atom(parse!("mwe::key(mwe::x)"));
        let data = UserData::Map([(key, UserData::Integer(1))].into_iter().collect());
        let owner = symbol!("mwe::owner", data = data);
        let mut bytes = vec![];
        owner.to_atom().export(&mut bytes).unwrap();
        bytes
    };

    unsafe { State::reset() };
    let _ = Atom::import(&mut bytes.as_slice(), None).unwrap();
}
