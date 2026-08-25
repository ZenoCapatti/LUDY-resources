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
    atom::{AtomCore, SymbolAttribute, SymbolBuilder},
    function, symbol, wrap_symbol,
};

fn main() {
    let head = SymbolBuilder::new(wrap_symbol!("mwe::head"))
        .with_attributes(&[SymbolAttribute::Symmetric])
        .with_tags(["mwe::tag"])
        .with_print_function(|_, _, _| Some("PRETTY".into()))
        .build()
        .unwrap();
    let expression = function!(head, symbol!("mwe::x"));

    println!("display:   {expression}");
    println!("canonical: {}", expression.to_canonical_string());
    assert_eq!(
        expression.to_canonical_string(),
        "mwe::{symmetric,mwe::tag}::head(mwe::{}::x)"
    );
}
