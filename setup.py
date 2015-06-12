#!/usr/bin/env python
import sys
from distutils.command.build import build

from setuptools import setup
from setuptools.command.install import install
from setuptools.command.test import test


CFFI_DEPENDENCY = "cffi>=1.1"
SIX_DEPENDENCY = "six>=1.4.1"


CFFI_MODULES = [
    "src/build_bcrypt.py:ffi",
]


# Manually extract the __about__
__about__ = {}
with open("src/bcrypt/__about__.py") as fp:
    exec(fp.read(), __about__)


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


def keywords_with_side_effects(argv):
    """
    Get a dictionary with setup keywords that (can) have side effects.

    :param argv: A list of strings with command line arguments.
    :returns: A dictionary with keyword arguments for the ``setup()`` function.

    This setup.py script uses the setuptools 'setup_requires' feature because
    this is required by the cffi package to compile extension modules. The
    purpose of ``keywords_with_side_effects()`` is to avoid triggering the cffi
    build process as a result of setup.py invocations that don't need the cffi
    module to be built (setup.py serves the dual purpose of exposing package
    metadata).

    All of the options listed by ``python setup.py --help`` that print
    information should be recognized here. The commands ``clean``,
    ``egg_info``, ``register``, ``sdist`` and ``upload`` are also recognized.
    Any combination of these options and commands is also supported.

    This function was originally based on the `setup.py script`_ of SciPy (see
    also the discussion in `pip issue #25`_).

    .. _pip issue #25: https://github.com/pypa/pip/issues/25
    .. _setup.py script: https://github.com/scipy/scipy/blob/master/setup.py
    """
    no_setup_requires_arguments = (
        '-h', '--help',
        '-n', '--dry-run',
        '-q', '--quiet',
        '-v', '--verbose',
        '-V', '--version',
        '--author',
        '--author-email',
        '--classifiers',
        '--contact',
        '--contact-email',
        '--description',
        '--egg-base',
        '--fullname',
        '--help-commands',
        '--keywords',
        '--licence',
        '--license',
        '--long-description',
        '--maintainer',
        '--maintainer-email',
        '--name',
        '--no-user-cfg',
        '--obsoletes',
        '--platforms',
        '--provides',
        '--requires',
        '--url',
        'clean',
        'egg_info',
        'register',
        'sdist',
        'upload',
    )

    def is_short_option(argument):
        """Check whether a command line argument is a short option."""
        return len(argument) >= 2 and argument[0] == '-' and argument[1] != '-'

    def expand_short_options(argument):
        """Expand combined short options into canonical short options."""
        return ('-' + char for char in argument[1:])

    def argument_without_setup_requirements(argv, i):
        """Check whether a command line argument needs setup requirements."""
        if argv[i] in no_setup_requires_arguments:
            # Simple case: An argument which is either an option or a command
            # which doesn't need setup requirements.
            return True
        elif (is_short_option(argv[i]) and
              all(option in no_setup_requires_arguments
                  for option in expand_short_options(argv[i]))):
            # Not so simple case: Combined short options none of which need
            # setup requirements.
            return True
        elif argv[i - 1:i] == ['--egg-base']:
            # Tricky case: --egg-info takes an argument which should not make
            # us use setup_requires (defeating the purpose of this code).
            return True
        else:
            return False

    if all(argument_without_setup_requirements(argv, i)
           for i in range(1, len(argv))):
        return {
            "cmdclass": {
                "build": DummyCFFIBuild,
                "install": DummyCFFIInstall,
                "test": DummyPyTest,
            }
        }
    else:
        return {
            "setup_requires": [CFFI_DEPENDENCY],
            "cmdclass": {
                "test": PyTest,
            },
            "cffi_modules": CFFI_MODULES,
        }


setup_requires_error = ("Requested setup command that needs 'setup_requires' "
                        "while command line arguments implied a side effect "
                        "free command or option.")


class DummyCFFIBuild(build):
    """
    This class makes it very obvious when ``keywords_with_side_effects()`` has
    incorrectly interpreted the command line arguments to ``setup.py build`` as
    one of the 'side effect free' commands or options.
    """

    def run(self):
        raise RuntimeError(setup_requires_error)


class DummyCFFIInstall(install):
    """
    This class makes it very obvious when ``keywords_with_side_effects()`` has
    incorrectly interpreted the command line arguments to ``setup.py install``
    as one of the 'side effect free' commands or options.
    """

    def run(self):
        raise RuntimeError(setup_requires_error)


class DummyPyTest(test):
    """
    This class makes it very obvious when ``keywords_with_side_effects()`` has
    incorrectly interpreted the command line arguments to ``setup.py test`` as
    one of the 'side effect free' commands or options.
    """

    def run_tests(self):
        raise RuntimeError(setup_requires_error)


setup(
    name=__about__["__title__"],
    version=__about__["__version__"],

    description=__about__["__summary__"],
    long_description=open("README.rst").read(),
    url=__about__["__uri__"],
    license=__about__["__license__"],

    author=__about__["__author__"],
    author_email=__about__["__email__"],

    install_requires=[
        CFFI_DEPENDENCY,
        SIX_DEPENDENCY,
    ],
    extras_require={
        "tests": [
            "pytest",
        ],
    },
    tests_require=[
        "pytest",
    ],

    package_dir={"": "src"},
    packages=[
        "bcrypt",
    ],

    zip_safe=False,

    classifiers=[
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],

    ext_package="bcrypt",

    **keywords_with_side_effects(sys.argv)
)
