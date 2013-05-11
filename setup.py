#!/usr/bin/env python
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class _AttrDict(dict):

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # to conform with __getattr__ spec
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value


try:
    from bcrypt import __about__, _ffi
except ImportError:
    # installing - there is no cffi yet
    ext_modules = []

    # Manually extract the __about__
    __about__ = _AttrDict()
    with open("bcrypt/__about__.py") as fp:
        exec(fp.read(), __about__)
else:
    # building bdist - cffi is here!
    ext_modules = [_ffi.verifier.get_extension()]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name=__about__.__title__,
    version=__about__.__version__,

    description=__about__.__summary__,
    long_description=open("README.rst").read(),
    url=__about__.__uri__,
    license=__about__.__license__,

    author=__about__.__author__,
    author_email=__about__.__email__,

    install_requires=[
        "cffi",
    ],
    extras_require={
        "tests": [
            "pytest",
            "mock",
        ],
    },
    tests_require=[
        "pytest",
        "mock",
    ],

    packages=[
        "bcrypt",
    ],

    package_data={
        "bcrypt": ["crypt_blowfish-1.2/*"],
    },

    ext_package="bcrypt",
    ext_modules=ext_modules,

    zip_safe=False,
    cmdclass={"test": PyTest},

    classifiers=[
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ]
)
