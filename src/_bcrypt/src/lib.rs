// This file is dual licensed under the terms of the Apache License, Version
// 2.0, and the BSD License. See the LICENSE file in the root of this repository
// for complete details.

#![deny(rust_2018_idioms)]

use std::convert::TryInto;

#[pyo3::prelude::pyfunction]
fn encode_base64<'p>(py: pyo3::Python<'p>, data: &[u8]) -> &'p pyo3::types::PyBytes {
    let output = base64::encode_config(data, base64::BCRYPT);
    pyo3::types::PyBytes::new(py, output.as_bytes())
}

#[pyo3::prelude::pyfunction]
fn hashpass<'p>(
    py: pyo3::Python<'p>,
    password: &[u8],
    salt: &[u8],
) -> pyo3::PyResult<&'p pyo3::types::PyBytes> {
    // salt here is not just the salt bytes, but rather an encoded value
    // containing a version number, number of rounds, and the salt.
    // Should be [prefix, cost, hash]. This logic is copied from `bcrypt`
    let raw_parts: Vec<_> = salt
        .split(|&b| b == b'$')
        .filter(|s| !s.is_empty())
        .collect();
    if raw_parts.len() != 3 {
        return Err(pyo3::exceptions::PyValueError::new_err("Invalid salt"));
    }
    let version = match raw_parts[0] {
        b"2y" => bcrypt::Version::TwoY,
        b"2b" => bcrypt::Version::TwoB,
        b"2a" => bcrypt::Version::TwoA,
        b"2x" => bcrypt::Version::TwoX,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err("Invalid salt"));
        }
    };
    let cost = std::str::from_utf8(raw_parts[1])
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid salt"))?
        .parse::<u32>()
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid salt"))?;
    // The last component can contain either just the salt, or the salt and
    // the result hash, depending on if the `salt` value come from `hashpw` or
    // `gensalt`.
    let raw_salt = base64::decode_config(&raw_parts[2][..22], base64::BCRYPT)
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid salt"))?
        .try_into()
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid salt"))?;

    let hashed = py
        .allow_threads(|| bcrypt::hash_with_salt(password, cost, raw_salt))
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid salt"))?;
    Ok(pyo3::types::PyBytes::new(
        py,
        hashed.format_for_version(version).as_bytes(),
    ))
}

#[pyo3::prelude::pyfunction]
fn pbkdf<'p>(
    py: pyo3::Python<'p>,
    password: &[u8],
    salt: &[u8],
    rounds: u32,
    desired_key_bytes: usize,
) -> pyo3::PyResult<&'p pyo3::types::PyBytes> {
    pyo3::types::PyBytes::new_with(py, desired_key_bytes, |output| {
        py.allow_threads(|| {
            bcrypt_pbkdf::bcrypt_pbkdf(password, salt, rounds, output).unwrap();
        });
        Ok(())
    })
}

#[pyo3::prelude::pymodule]
fn _bcrypt(_py: pyo3::Python<'_>, m: &pyo3::types::PyModule) -> pyo3::PyResult<()> {
    m.add_function(pyo3::wrap_pyfunction!(encode_base64, m)?)?;
    m.add_function(pyo3::wrap_pyfunction!(hashpass, m)?)?;
    m.add_function(pyo3::wrap_pyfunction!(pbkdf, m)?)?;

    Ok(())
}
