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

import os.path

from cffi import FFI


BLOWFISH_DIR = os.path.join(os.path.dirname(__file__), "_csrc")
SOURCE_FILENAMES = [
    "blf.c",
    "bcrypt.c",
    "bcrypt_pbkdf.c",
    "sha2.c",
    "timingsafe_bcmp.c",
]
SOURCES = [
    os.path.join(BLOWFISH_DIR, filename) for filename in SOURCE_FILENAMES
]

ffi = FFI()

ffi.cdef(
    """
int bcrypt_hashpass(const char *, const char *, char *, size_t);
int encode_base64(char *, const uint8_t *, size_t);
int bcrypt_pbkdf(const char *, size_t, const uint8_t *, size_t,
                 uint8_t *, size_t, unsigned int);
int timingsafe_bcmp(const void *, const void *, size_t);
"""
)

ffi.set_source(
    "_bcrypt",
    """
    #include "pycabcrypt.h"
    """,
    sources=SOURCES,
    include_dirs=[BLOWFISH_DIR],
)
