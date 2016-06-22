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

import six

from bcrypt import _bcrypt

from .__about__ import (
    __author__, __copyright__, __email__, __license__, __summary__, __title__,
    __uri__, __version__,
)


__all__ = [
    "__title__", "__summary__", "__uri__", "__version__", "__author__",
    "__email__", "__license__", "__copyright__",
    "gensalt", "hashpw", "kdf",
]


_normalize_re = re.compile(b"^\$2y\$")


def _normalize_prefix(salt):
    return _normalize_re.sub(b"$2b$", salt)


def gensalt(rounds=12, prefix=b"2b"):
    if prefix not in (b"2a", b"2b"):
        raise ValueError("Supported prefixes are b'2a' or b'2b'")

    if rounds < 4 or rounds > 31:
        raise ValueError("Invalid rounds")

    salt = os.urandom(16)
    output = _bcrypt.ffi.new("unsigned char[]", 30)
    _bcrypt.lib.encode_base64(output, salt, len(salt))

    return (
        b"$" + prefix + b"$" + ("%2.2u" % rounds).encode("ascii") + b"$" +
        _bcrypt.ffi.string(output)
    )


def hashpw(password, salt):
    if isinstance(password, six.text_type) or isinstance(salt, six.text_type):
        raise TypeError("Unicode-objects must be encoded before hashing")

    if b"\x00" in password:
        raise ValueError("password may not contain NUL bytes")

    salt = _normalize_prefix(salt)

    hashed = _bcrypt.ffi.new("unsigned char[]", 128)
    retval = _bcrypt.lib.bcrypt_hashpass(password, salt, hashed, len(hashed))

    if retval != 0:
        raise ValueError("Invalid salt")

    return _bcrypt.ffi.string(hashed)


def kdf(password, salt, desired_key_bytes, rounds):
    if isinstance(password, six.text_type) or isinstance(salt, six.text_type):
        raise TypeError("Unicode-objects must be encoded before hashing")

    if len(password) == 0 or len(salt) == 0:
        raise ValueError("password and salt must not be empty")

    if desired_key_bytes <= 0 or desired_key_bytes > 512:
        raise ValueError("desired_key_bytes must be 1-512")

    if rounds < 1:
        raise ValueError("rounds must be 1 or more")

    key = _bcrypt.ffi.new("uint8_t[]", desired_key_bytes)
    res = _bcrypt.lib.bcrypt_pbkdf(
        password, len(password), salt, len(salt), key, len(key), rounds
    )
    _bcrypt_assert(res == 0)

    return _bcrypt.ffi.buffer(key, desired_key_bytes)[:]


def _bcrypt_assert(ok):
    if not ok:
        raise SystemError("bcrypt assertion failed")
