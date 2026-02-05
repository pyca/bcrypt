Changelog
=========

Unreleased
----------

* Bumped MSRV to 1.85.

5.0.0
-----

* Bumped MSRV to 1.74.
* Added support for Python 3.14 and free-threaded Python 3.14.
* Added support for Windows on ARM.
* Passing ``hashpw`` a password longer than 72 bytes now raises a
  ``ValueError``. Previously the password was silently truncated, following the
  behavior of the original OpenBSD ``bcrypt`` implementation.

4.3.0
-----

* Dropped support for Python 3.7.
* We now support free-threaded Python 3.13.
* We now support PyPy 3.11.
* We now publish wheels for free-threaded Python 3.13, for PyPy 3.11 on
  ``manylinux``, and for ARMv7l on ``manylinux``.

4.2.1
-----

* Bump Rust dependency versions - this should resolve crashes on Python 3.13
  free-threaded builds.
* We no longer build ``manylinux`` wheels for PyPy 3.9.

4.2.0
-----

* Bump Rust dependency versions
* Removed the ``BCRYPT_ALLOW_RUST_163`` environment variable.

4.1.3
-----

* Bump Rust dependency versions

4.1.2
-----

* Publish both ``py37`` and ``py39`` wheels. This should resolve some errors
  relating to initializing a module multiple times per process.

4.1.1
-----

* Fixed the type signature on the ``kdf`` method.
* Fixed packaging bug on Windows.
* Fixed incompatibility with passlib package detection assumptions.

4.1.0
-----

* Dropped support for Python 3.6.
* Bumped MSRV to 1.64. (Note: Rust 1.63 can be used by setting the ``BCRYPT_ALLOW_RUST_163`` environment variable)

4.0.1
-----

* We now build PyPy ``manylinux`` wheels.
* Fixed a bug where passing an invalid ``salt`` to ``checkpw`` could result in
  a ``pyo3_runtime.PanicException``. It now correctly raises a ``ValueError``.

4.0.0
-----

* ``bcrypt`` is now implemented in Rust. Users building from source will need
  to have a Rust compiler available. Nothing will change for users downloading
  wheels.
* We no longer ship ``manylinux2010`` wheels. Users should upgrade to the latest
  ``pip`` to ensure this doesn’t cause issues downloading wheels on their
  platform. We now ship ``manylinux_2_28`` wheels for users on new enough platforms.
* ``NUL`` bytes are now allowed in inputs.


3.2.2
-----

* Fixed packaging of ``py.typed`` files in wheels so that ``mypy`` works.

3.2.1
-----

* Added support for compilation on z/OS
* The next release of ``bcrypt`` with be 4.0 and it will require Rust at
  compile time, for users building from source. There will be no additional
  requirement for users who are installing from wheels. Users on most
  platforms will be able to obtain a wheel by making sure they have an up to
  date ``pip``. The minimum supported Rust version will be 1.56.0.
* This will be the final release for which we ship ``manylinux2010`` wheels.
  Going forward the minimum supported manylinux ABI for our wheels will be
  ``manylinux2014``. The vast majority of users will continue to receive
  ``manylinux`` wheels provided they have an up to date ``pip``.


3.2.0
-----

* Added typehints for library functions.
* Dropped support for Python versions less than 3.6 (2.7, 3.4, 3.5).
* Shipped ``abi3`` Windows wheels (requires pip >= 20).

3.1.7
-----

* Set a ``setuptools`` lower bound for PEP517 wheel building.
* We no longer distribute 32-bit ``manylinux1`` wheels. Continuing to produce
  them was a maintenance burden.

3.1.6
-----

* Added support for compilation on Haiku.

3.1.5
-----

* Added support for compilation on AIX.
* Dropped Python 2.6 and 3.3 support.
* Switched to using ``abi3`` wheels for Python 3. If you are not getting a
  wheel on a compatible platform please upgrade your ``pip`` version.

3.1.4
-----

* Fixed compilation with mingw and on illumos.

3.1.3
-----
* Fixed a compilation issue on Solaris.
* Added a warning when using too few rounds with ``kdf``.

3.1.2
-----
* Fixed a compile issue affecting big endian platforms.
* Fixed invalid escape sequence warnings on Python 3.6.
* Fixed building in non-UTF8 environments on Python 2.

3.1.1
-----
* Resolved a ``UserWarning`` when used with ``cffi`` 1.8.3.

3.1.0
-----
* Added support for ``checkpw``, a convenience method for verifying a password.
* Ensure that you get a ``$2y$`` hash when you input a ``$2y$`` salt.
* Fixed a regression where ``$2a`` hashes were vulnerable to a wraparound bug.
* Fixed compilation under Alpine Linux.

3.0.0
-----
* Switched the C backend to code obtained from the OpenBSD project rather than
  openwall.
* Added support for ``bcrypt_pbkdf`` via the ``kdf`` function.

2.0.0
-----
* Added support for an adjustible prefix when calling ``gensalt``.
* Switched to CFFI 1.0+
