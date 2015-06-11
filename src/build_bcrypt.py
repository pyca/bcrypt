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


BLOWFISH_DIR = os.path.join(os.path.dirname(__file__), "crypt_blowfish-1.3")


ffi = FFI()

ffi.cdef(
    """
    char *crypt_gensalt_rn(const char *prefix, unsigned long count,
                const char *input, int size, char *output, int output_size);

    char *crypt_rn(const char *key, const char *setting, void *data, int size);
    """
)

ffi.set_source(
    "_bcrypt",
    """
    #include "ow-crypt.h"
    """,
    sources=[
        os.path.join(BLOWFISH_DIR, "crypt_blowfish.c"),
        os.path.join(BLOWFISH_DIR, "crypt_gensalt.c"),
        os.path.join(BLOWFISH_DIR, "wrapper.c"),
        # How can we get distutils to work with a .S file?
        #   Set bcrypt/crypt_blowfish-1.3/crypt_blowfish.c#57 back to 1 if we
        #   get ASM loaded.
        # os.path.join(BLOWFISH_DIR, "x86.S"),
    ],
    include_dirs=[BLOWFISH_DIR],
)
