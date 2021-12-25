# Author:: Donald Stufft (<donald@stufft.io>)
# Copyright:: Copyright (c) 2013 Donald Stufft
# License:: Apache License, Version 2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import
from __future__ import division

import os
import re
import warnings

from . import _bcrypt  # type: ignore
from .__about__ import (
    __author__,
    __copyright__,
    __email__,
    __license__,
    __summary__,
    __title__,
    __uri__,
    __version__,
)


NULL_BYTE = b"\x00"

HASHED_BYTES = 128
OUTPUT_BYTES = 30
SALT_BYTES = 16
SUPPORTED_PREFIXES = (b"2a", b"2b")

__all__ = [
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
    "gensalt",
    "hashpw",
    "kdf",
    "checkpw",
]


_normalize_re = re.compile(br"^\$2y\$")


def gensalt(rounds: int = 12, prefix: bytes = b"2b") -> bytes:
    if not _supported(prefix):
        raise ValueError("Supported prefixes are b'2a' or b'2b'")

    if not _valid(rounds):
        raise ValueError("Invalid rounds")

    output = _get_encoded_salted_output()

    return (
        b"$"
        + prefix
        + b"$"
        + ("%2.2u" % rounds).encode("ascii")
        + b"$"
        + _bcrypt.ffi.string(output)
    )


def _supported(prefix: bytes) -> bool:
    return prefix in SUPPORTED_PREFIXES


def _valid(rounds: int) -> bool:
    return 4 <= rounds <= 31


def _get_encoded_salted_output() -> bytes:
    salt = os.urandom(SALT_BYTES)
    output = _bcrypt.ffi.new("char[]", OUTPUT_BYTES)
    _bcrypt.lib.encode_base64(output, salt, len(salt))

    return output


def hashpw(password: bytes, salt: bytes) -> bytes:
    if _unencoded(password, salt):
        raise TypeError("Strings must be encoded before hashing")

    if _contains_null_bytes(password):
        raise ValueError("password may not contain NUL bytes")

    # bcrypt originally suffered from a wraparound bug:
    # http://www.openwall.com/lists/oss-security/2012/01/02/4
    # This bug was corrected in the OpenBSD source by truncating inputs to 72
    # bytes on the updated prefix $2b$, but leaving $2a$ unchanged for
    # compatibility. However, pyca/bcrypt 2.0.0 *did* correctly truncate inputs
    # on $2a$, so we do it here to preserve compatibility with 2.0.0
    password = password[:72]

    # When the original 8bit bug was found the original library we supported
    # added a new prefix, $2y$, that fixes it. This prefix is exactly the same
    # as the $2b$ prefix added by OpenBSD other than the name. Since the
    # OpenBSD library does not support the $2y$ prefix, if the salt given to us
    # is for the $2y$ prefix, we'll just mugne it so that it's a $2b$ prior to
    # passing it into the C library.
    original_salt, salt = salt, _normalize_re.sub(b"$2b$", salt)

    hashed = _bcrypt.ffi.new("char[]", HASHED_BYTES)
    retval = _bcrypt.lib.bcrypt_hashpass(password, salt, hashed, len(hashed))

    if retval != 0:
        raise ValueError("Invalid salt")

    # Now that we've gotten our hashed password, we want to ensure that the
    # prefix we return is the one that was passed in, so we'll use the prefix
    # from the original salt and concatenate that with the return value (minus
    # the return value's prefix). This will ensure that if someone passed in a
    # salt with a $2y$ prefix, that they get back a hash with a $2y$ prefix
    # even though we munged it to $2b$.
    return original_salt[:4] + _bcrypt.ffi.string(hashed)[4:]


def _unencoded(*args: bytes) -> bool:
    return any(isinstance(input_, str) for input_ in args)


def _contains_null_bytes(*args: bytes) -> bool:
    return any(NULL_BYTE in input_ for input_ in args)


def checkpw(password: bytes, hashed_password: bytes) -> bool:
    if _unencoded(password, hashed_password):
        raise TypeError("Strings must be encoded before checking")

    if _contains_null_bytes(password, hashed_password):
        raise ValueError(
            "password and hashed_password may not contain NUL bytes"
        )

    ret = hashpw(password, hashed_password)

    if len(ret) != len(hashed_password):
        return False

    return _bcrypt.lib.timingsafe_bcmp(ret, hashed_password, len(ret)) == 0


def kdf(
    password: bytes,
    salt: bytes,
    desired_key_bytes: int,
    rounds: int,
    ignore_few_rounds: bool = False,
) -> bytes:
    if _unencoded(password, salt):
        raise TypeError("Strings must be encoded before hashing")

    if len(password) == 0 or len(salt) == 0:
        raise ValueError("password and salt must not be empty")

    if not (1 <= desired_key_bytes <= 512):
        raise ValueError("desired_key_bytes must be 1-512")

    if rounds < 1:
        raise ValueError("rounds must be 1 or more")

    if rounds < 50 and not ignore_few_rounds:
        # They probably think bcrypt.kdf()'s rounds parameter is logarithmic,
        # expecting this value to be slow enough (it probably would be if this
        # were bcrypt). Emit a warning.
        warnings.warn(
            (
                "Warning: bcrypt.kdf() called with only {0} round(s). "
                "This few is not secure: the parameter is linear, like PBKDF2."
            ).format(rounds),
            UserWarning,
            stacklevel=2,
        )

    key = _generate_key(desired_key_bytes)

    return _bcrypt.ffi.buffer(key, desired_key_bytes)[:]


def _generate_key(
    password: bytes,
    salt: bytes,
    desired_key_bytes: int,
    rounds: int
) -> bytes:
    key = _bcrypt.ffi.new("uint8_t[]", desired_key_bytes)
    result = _bcrypt.lib.bcrypt_pbkdf(
        password, len(password), salt, len(salt), key, len(key), rounds
    )

    _bcrypt_assert(result == 0)

    return result


def _bcrypt_assert(ok: bool) -> None:
    if not ok:
        raise SystemError("bcrypt assertion failed")
