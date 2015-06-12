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

import six

from bcrypt import _bcrypt

from .__about__ import (
    __author__, __copyright__, __email__, __license__, __summary__, __title__,
    __uri__, __version__,
)


__all__ = [
    "__title__", "__summary__", "__uri__", "__version__", "__author__",
    "__email__", "__license__", "__copyright__",
    "gensalt", "hashpw",
]


def gensalt(rounds=12, prefix=b"2b"):
    if prefix not in (b"2a", b"2b"):
        raise ValueError("Supported prefixes are b'2a' or b'2b'")

    salt = os.urandom(16)
    output = _bcrypt.ffi.new("unsigned char[]", 30)

    retval = _bcrypt.lib.crypt_gensalt_rn(
        b"$" + prefix + b"$", rounds, salt, len(salt), output, len(output),
    )

    if not retval:
        raise ValueError("Invalid rounds")

    return _bcrypt.ffi.string(output)


def hashpw(password, salt):
    if isinstance(password, six.text_type) or isinstance(salt, six.text_type):
        raise TypeError("Unicode-objects must be encoded before hashing")

    if b"\x00" in password:
        raise ValueError("password may not contain NUL bytes")

    hashed = _bcrypt.ffi.new("unsigned char[]", 128)
    retval = _bcrypt.lib.crypt_rn(password, salt, hashed, len(hashed))

    if not retval:
        raise ValueError("Invalid salt")

    return _bcrypt.ffi.string(hashed)
