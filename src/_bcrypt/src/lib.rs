// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#![deny(rust_2018_idioms)]

use base64::Engine;
use pyo3::types::PyBytesMethods;
use pyo3::PyTypeInfo;
use std::convert::TryInto;
use std::ffi::CString;
use std::io::Write;
use subtle::ConstantTimeEq;

pub const BASE64_ENGINE: base64::engine::GeneralPurpose = base64::engine::GeneralPurpose::new(
    &base64::alphabet::BCRYPT,
    base64::engine::general_purpose::NO_PAD,
);

#[pyo3::pyfunction]
#[pyo3(signature = (rounds=12, prefix=None), text_signature = "(rounds=12, prefix=b'2b')")]
fn gensalt<'p>(
    py: pyo3::Python<'p>,
    rounds: u16,
    prefix: Option<&[u8]>,
) -> pyo3::PyResult<pyo3::Bound<'p, pyo3::types::PyBytes>> {
    let prefix = prefix.unwrap_or(b"2b");

    if prefix != b"2a" && prefix != b"2b" {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Supported prefixes are b'2a' or b'2b'",
        ));
    }

    if !(4..=31).contains(&rounds) {
        return Err(pyo3::exceptions::PyValueError::new_err("Invalid rounds"));
    }

    let mut salt = [0; 16];
    getrandom::fill(&mut salt).unwrap();

    let encoded_salt = BASE64_ENGINE.encode(salt);

    pyo3::types::PyBytes::new_with(
        py,
        1 + prefix.len() + 1 + 2 + 1 + encoded_salt.len(),
        |mut b| {
            write!(b, "$").unwrap();
            b.write_all(prefix).unwrap();
            write!(b, "$").unwrap();
            write!(b, "{:02.2}", rounds).unwrap();
            write!(b, "$").unwrap();
            b.write_all(encoded_salt.as_bytes()).unwrap();

            Ok(())
        },
    )
}

#[pyo3::pyfunction]
fn hashpw<'p>(
    py: pyo3::Python<'p>,
    password: &[u8],
    salt: &[u8],
) -> pyo3::PyResult<pyo3::Bound<'p, pyo3::types::PyBytes>> {
    // bcrypt originally suffered from a wraparound bug:
    // http://www.openwall.com/lists/oss-security/2012/01/02/4
    // This bug was corrected in the OpenBSD source by truncating inputs to 72
    // bytes on the updated prefix $2b$, but leaving $2a$ unchanged for
    // compatibility. However, pyca/bcrypt 2.0.0 *did* correctly truncate inputs
    // on $2a$, so we do it here to preserve compatibility with 2.0.0
    // Silent truncation is _probably_ not the best idea, even if the "original"
    // OpenBSD implementation did/does this.
    // We prefer to raise a ValueError in this case - if the user _wants_ to truncate,
    // they can always do so manually by passing s[:72] instead of s into hashpw().

    if password.len() > 72 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])",
        ));
    }

    // salt here is not just the salt bytes, but rather an encoded value
    // containing a version number, number of rounds, and the salt.
    // Should be [prefix, cost, hash]. This logic is copied from `bcrypt`
    let [raw_version, raw_cost, remainder]: [&[u8]; 3] = salt
        .split(|&b| b == b'$')
        .filter(|s| !s.is_empty())
        .collect::<Vec<_>>()
        .try_into()
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid salt"))?;

    let version = match raw_version {
        b"2y" => bcrypt::Version::TwoY,
        b"2b" => bcrypt::Version::TwoB,
        b"2a" => bcrypt::Version::TwoA,
        b"2x" => bcrypt::Version::TwoX,
        _ => {
            return Err(pyo3::exceptions::PyValueError::new_err("Invalid salt"));
        }
    };
    let cost = std::str::from_utf8(raw_cost)
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid salt"))?
        .parse::<u32>()
        .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid salt"))?;

    if remainder.len() < 22 {
        return Err(pyo3::exceptions::PyValueError::new_err("Invalid salt"));
    }

    // The last component can contain either just the salt, or the salt and
    // the result hash, depending on if the `salt` value come from `hashpw` or
    // `gensalt`.
    let raw_salt = BASE64_ENGINE
        .decode(&remainder[..22])
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

#[pyo3::pyfunction]
fn checkpw(py: pyo3::Python<'_>, password: &[u8], hashed_password: &[u8]) -> pyo3::PyResult<bool> {
    Ok(hashpw(py, password, hashed_password)?
        .as_bytes()
        .ct_eq(hashed_password)
        .into())
}

#[pyo3::pyfunction]
#[pyo3(signature = (password, salt, desired_key_bytes, rounds, ignore_few_rounds=false))]
fn kdf<'p>(
    py: pyo3::Python<'p>,
    password: &[u8],
    salt: &[u8],
    desired_key_bytes: usize,
    rounds: u32,
    ignore_few_rounds: bool,
) -> pyo3::PyResult<pyo3::Bound<'p, pyo3::types::PyBytes>> {
    if password.is_empty() || salt.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "password and salt must not be empty",
        ));
    }

    if desired_key_bytes == 0 || desired_key_bytes > 512 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "desired_key_bytes must be 1-512",
        ));
    }

    if rounds < 1 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "rounds must be 1 or more",
        ));
    }

    if rounds < 50 && !ignore_few_rounds {
        // They probably think bcrypt.kdf()'s rounds parameter is logarithmic,
        // expecting this value to be slow enough (it probably would be if this
        // were bcrypt). Emit a warning.
        pyo3::PyErr::warn(
            py,
            &pyo3::exceptions::PyUserWarning::type_object(py),
            &CString::new(format!("Warning: bcrypt.kdf() called with only {rounds} round(s). This few is not secure: the parameter is linear, like PBKDF2.")).unwrap(),
            3
        )?;
    }

    pyo3::types::PyBytes::new_with(py, desired_key_bytes, |output| {
        py.allow_threads(|| {
            bcrypt_pbkdf::bcrypt_pbkdf(password, salt, rounds, output).unwrap();
        });
        Ok(())
    })
}

#[pyo3::pymodule(gil_used = false)]
mod _bcrypt {
    use pyo3::types::PyModuleMethods;

    #[pymodule_export]
    use super::{checkpw, gensalt, hashpw, kdf};

    // Not yet possible to add constants declaratively.
    #[pymodule_init]
    fn init(m: &pyo3::Bound<'_, pyo3::types::PyModule>) -> pyo3::PyResult<()> {
        m.add("__title__", "bcrypt")?;
        m.add(
            "__summary__",
            "Modern(-ish) password hashing for your software and your servers",
        )?;
        m.add("__uri__", "https://github.com/pyca/bcrypt/")?;

        // When updating this, also update pyproject.toml
        // This isn't named __version__ because passlib treats the existence of
        // that attribute as proof that we're a different module
        m.add("__version_ex__", "4.3.0")?;

        let author = "The Python Cryptographic Authority developers";
        m.add("__author__", author)?;
        m.add("__email__", "cryptography-dev@python.org")?;

        m.add("__license__", "Apache License, Version 2.0")?;
        m.add("__copyright__", format!("Copyright 2013-2025 {author}"))?;

        Ok(())
    }
}
