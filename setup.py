#!/usr/bin/env python
import platform
import sys

from setuptools import setup

from setuptools_rust import RustExtension

if platform.python_implementation() == "PyPy":
    if sys.pypy_version_info < (2, 6):
        raise RuntimeError(
            "bcrypt is not compatible with PyPy < 2.6. Please upgrade PyPy to "
            "use this library."
        )


setup(
    rust_extensions=[
        RustExtension(
            "_bcrypt",
            "src/_bcrypt/Cargo.toml",
            py_limited_api=True,
            # Enable abi3 mode if we're not using PyPy.
            features=(
                []
                if platform.python_implementation() == "PyPy"
                else ["pyo3/abi3-py36"]
            ),
            rust_version=">=1.56.0",
        ),
    ],
)
