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
from __future__ import unicode_literals

import hashlib
import os
import sys

from cffi import FFI

from . import __about__
from .__about__ import *


__all__ = ["gensalt", "hashpw"] + __about__.__all__


# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3:
    text_type = str
else:
    text_type = unicode


_crypt_blowfish_dir = "crypt_blowfish-1.2"
_bundled_dir = os.path.join(os.path.dirname(__file__), _crypt_blowfish_dir)

_ffi = FFI()
_ffi.cdef("""
    char *crypt_gensalt_rn(const char *prefix, unsigned long count,
                const char *input, int size, char *output, int output_size);

    char *crypt_rn(const char *key, const char *setting, void *data, int size);
""")

_bcrypt_lib = _ffi.verify('#include "ow-crypt.h"',
    sources=[
        str(os.path.join(_bundled_dir, "crypt_blowfish.c")),
        str(os.path.join(_bundled_dir, "crypt_gensalt.c")),
        str(os.path.join(_bundled_dir, "wrapper.c")),
        # How can we get distutils to work with a .S file?
        # str(os.path.join(_bundled_dir, "x86.S")),
    ],
    include_dirs=[str(_bundled_dir)],
    modulename=str("_".join([
                    "_cffi",
                    hashlib.sha1(
                        "".join(_ffi._cdefsources).encode("utf-8")
                    ).hexdigest()[:6],
                    hashlib.sha1(
                        _crypt_blowfish_dir.encode("utf-8")
                    ).hexdigest()[:6],
                ])),
)


def gensalt(rounds=12):
    salt = os.urandom(16)
    output = _ffi.new("unsigned char[]", 30)

    retval = _bcrypt_lib.crypt_gensalt_rn(
                    b"$2a$", rounds, salt, len(salt), output, len(output))

    if not retval:
        raise ValueError("Invalid rounds")

    return _ffi.string(output)


def hashpw(password, salt):
    if isinstance(password, text_type) or isinstance(salt, text_type):
        raise TypeError("Unicode-objects must be encoded before hashing")

    hashed = _ffi.new("unsigned char[]", 128)
    retval = _bcrypt_lib.crypt_rn(password, salt, hashed, len(hashed))

    if not retval:
        raise ValueError("Invalid salt")

    return _ffi.string(hashed)
