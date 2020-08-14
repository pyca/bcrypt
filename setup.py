#!/usr/bin/env python
import io
import platform
import sys

from setuptools import setup
from setuptools.command.test import test


CFFI_DEPENDENCY = "cffi>=1.1"
SIX_DEPENDENCY = "six>=1.4.1"


CFFI_MODULES = [
    "src/build_bcrypt.py:ffi",
]


# Manually extract the __about__
__about__ = {}
with open("src/bcrypt/__about__.py") as fp:
    exec (fp.read(), __about__)


if platform.python_implementation() == "PyPy":
    if sys.pypy_version_info < (2, 6):
        raise RuntimeError(
            "bcrypt is not compatible with PyPy < 2.6. Please upgrade PyPy to "
            "use this library."
        )


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name=__about__["__title__"],
    version=__about__["__version__"],
    description=__about__["__summary__"],
    long_description=io.open("README.rst", encoding="utf-8").read(),
    url=__about__["__uri__"],
    license=__about__["__license__"],
    author=__about__["__author__"],
    author_email=__about__["__email__"],
    python_requires=">=3.6",
    setup_requires=[CFFI_DEPENDENCY],
    install_requires=[CFFI_DEPENDENCY, SIX_DEPENDENCY],
    extras_require={"tests": ["pytest>=3.2.1,!=3.3.0"], "typecheck": ["mypy"]},
    tests_require=["pytest>=3.2.1,!=3.3.0"],
    package_dir={"": "src"},
    packages=["bcrypt"],
    package_data={"bcrypt": ["py.typed"]},
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    ext_package="bcrypt",
    cffi_modules=CFFI_MODULES,
    cmdclass={"test": PyTest},
)
