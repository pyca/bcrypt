#!/usr/bin/env python
import platform
import sys

from setuptools import setup


CFFI_MODULES = [
    "src/build_bcrypt.py:ffi",
]


if platform.python_implementation() == "PyPy":
    if sys.pypy_version_info < (2, 6):
        raise RuntimeError(
            "bcrypt is not compatible with PyPy < 2.6. Please upgrade PyPy to "
            "use this library."
        )


setup(
    cffi_modules=CFFI_MODULES,
)
