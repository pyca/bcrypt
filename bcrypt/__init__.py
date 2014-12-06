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

import binascii
import os
import sys
import threading

from cffi import FFI
from cffi.verifier import Verifier

import six

from .__about__ import (
    __author__, __copyright__, __email__, __license__, __summary__, __title__,
    __uri__, __version__,
)


__all__ = [
    "__title__", "__summary__", "__uri__", "__version__", "__author__",
    "__email__", "__license__", "__copyright__",
    "gensalt", "hashpw",
]


def _create_modulename(cdef_sources, source, sys_version):
    """
    This is the same as CFFI's create modulename except we don't include the
    CFFI version.
    """
    key = '\x00'.join([sys_version[:3], source, cdef_sources])
    key = key.encode('utf-8')
    k1 = hex(binascii.crc32(key[0::2]) & 0xffffffff)
    k1 = k1.lstrip('0x').rstrip('L')
    k2 = hex(binascii.crc32(key[1::2]) & 0xffffffff)
    k2 = k2.lstrip('0').rstrip('L')
    return '_bcrypt_cffi_{0}{1}'.format(k1, k2)


def _compile_module(*args, **kwargs):
    raise RuntimeError(
        "Attempted implicit compile of a cffi module. All cffi modules should "
        "be pre-compiled at installation time."
    )


class LazyLibrary(object):
    def __init__(self, ffi):
        self._ffi = ffi
        self._lib = None
        self._lock = threading.Lock()

    def __getattr__(self, name):
        if self._lib is None:
            with self._lock:
                # We no cover this because this guard is here just to protect
                # against concurrent loads of this library. This is pretty
                # hard to test and the logic is simple and should hold fine
                # without testing (famous last words).
                if self._lib is None:  # pragma: no cover
                    self._lib = self._ffi.verifier.load_library()

        return getattr(self._lib, name)


_crypt_blowfish_dir = "crypt_blowfish-1.3"
_bundled_dir = os.path.join(os.path.dirname(__file__), _crypt_blowfish_dir)


CDEF = """
    char *crypt_gensalt_rn(const char *prefix, unsigned long count,
                const char *input, int size, char *output, int output_size);

    char *crypt_rn(const char *key, const char *setting, void *data, int size);
"""

SOURCE = """
    #include "ow-crypt.h"
"""

_ffi = FFI()
_ffi.cdef(CDEF)
_ffi.verifier = Verifier(
    _ffi,
    SOURCE,
    sources=[
        str(os.path.join(_bundled_dir, "crypt_blowfish.c")),
        str(os.path.join(_bundled_dir, "crypt_gensalt.c")),
        str(os.path.join(_bundled_dir, "wrapper.c")),
        # How can we get distutils to work with a .S file?
        #   Set bcrypt/crypt_blowfish-1.3/crypt_blowfish.c#57 back to 1 if we
        #   get ASM loaded.
        # str(os.path.join(_bundled_dir, "x86.S")),
    ],
    include_dirs=[str(_bundled_dir)],
    modulename=_create_modulename(CDEF, SOURCE, sys.version),
)

# Patch the Verifier() instance to prevent CFFI from compiling the module
_ffi.verifier.compile_module = _compile_module
_ffi.verifier._compile_module = _compile_module


_bcrypt_lib = LazyLibrary(_ffi)


def gensalt(rounds=12):
    salt = os.urandom(16)
    output = _ffi.new("unsigned char[]", 30)

    retval = _bcrypt_lib.crypt_gensalt_rn(
        b"$2a$", rounds, salt, len(salt), output, len(output),
    )

    if not retval:
        raise ValueError("Invalid rounds")

    return _ffi.string(output)


def hashpw(password, salt):
    if isinstance(password, six.text_type) or isinstance(salt, six.text_type):
        raise TypeError("Unicode-objects must be encoded before hashing")

    hashed = _ffi.new("unsigned char[]", 128)
    retval = _bcrypt_lib.crypt_rn(password, salt, hashed, len(hashed))

    if not retval:
        raise ValueError("Invalid salt")

    return _ffi.string(hashed)
