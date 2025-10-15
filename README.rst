bcrypt
======

.. image:: https://img.shields.io/pypi/v/bcrypt.svg
    :target: https://pypi.org/project/bcrypt/
    :alt: Latest Version

.. image:: https://github.com/pyca/bcrypt/workflows/CI/badge.svg?branch=main
    :target: https://github.com/pyca/bcrypt/actions?query=workflow%3ACI+branch%3Amain

Acceptable password hashing for your software and your servers (but you should
really use argon2id or scrypt)


Installation
============

To install bcrypt, simply:

.. code:: console

    $ pip install bcrypt

Note that bcrypt should build very easily on Linux provided you have a C
compiler and a Rust compiler (the minimum supported Rust version is 1.56.0).

For Debian and Ubuntu, the following command will ensure that the required dependencies are installed:

.. code:: console

    $ sudo apt-get install build-essential cargo

For Fedora and RHEL-derivatives, the following command will ensure that the required dependencies are installed:

.. code:: console

    $ sudo yum install gcc cargo

For Alpine, the following command will ensure that the required dependencies are installed:

.. code:: console

    $ apk add --update musl-dev gcc cargo


Alternatives
============

While bcrypt remains an acceptable choice for password storage, depending on your specific use case you may also want to consider using scrypt (either via `standard library`_ or `cryptography`_) or argon2id via `argon2_cffi`_.

Changelog
=========

The changelog is maintained in `CHANGELOG.rst <https://github.com/pyca/bcrypt/blob/main/CHANGELOG.rst>`_

Usage
=====

Password Hashing
~~~~~~~~~~~~~~~~

Hashing and then later checking that a password matches the previous hashed
password is very simple:

.. code:: pycon

    >>> import bcrypt
    >>> password = b"super secret password"
    >>> # Hash a password for the first time, with a randomly-generated salt
    >>> hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    >>> # Check that an unhashed password matches one that has previously been
    >>> # hashed
    >>> if bcrypt.checkpw(password, hashed):
    ...     print("It Matches!")
    ... else:
    ...     print("It Does not Match :(")

KDF
~~~

As of 3.0.0 ``bcrypt`` now offers a ``kdf`` function which does ``bcrypt_pbkdf``.
This KDF is used in OpenSSH's newer encrypted private key format.

.. code:: pycon

    >>> import bcrypt
    >>> key = bcrypt.kdf(
    ...     password=b'password',
    ...     salt=b'salt',
    ...     desired_key_bytes=32,
    ...     rounds=100)


Adjustable Work Factor
~~~~~~~~~~~~~~~~~~~~~~
One of bcrypt's features is an adjustable logarithmic work factor. To adjust
the work factor merely pass the desired number of rounds to
``bcrypt.gensalt(rounds=12)`` which defaults to 12):

.. code:: pycon

    >>> import bcrypt
    >>> password = b"super secret password"
    >>> # Hash a password for the first time, with a certain number of rounds
    >>> hashed = bcrypt.hashpw(password, bcrypt.gensalt(14))
    >>> # Check that a unhashed password matches one that has previously been
    >>> #   hashed
    >>> if bcrypt.checkpw(password, hashed):
    ...     print("It Matches!")
    ... else:
    ...     print("It Does not Match :(")


Adjustable Prefix
~~~~~~~~~~~~~~~~~

Another one of bcrypt's features is an adjustable prefix to let you define what
libraries you'll remain compatible with. To adjust this, pass either ``2a`` or
``2b`` (the default) to ``bcrypt.gensalt(prefix=b"2b")`` as a bytes object.

As of 3.0.0 the ``$2y$`` prefix is still supported in ``hashpw`` but deprecated.

Maximum Password Length
~~~~~~~~~~~~~~~~~~~~~~~

The bcrypt algorithm only handles passwords up to 72 characters; any characters
beyond that are ignored. The best solution to this problem is to stop using
bcrypt and use a modern algorithm such as argon2id or scrypt. Seriously.

If you must use bcrypt, you can work around bcrypt's character limit by first
hashing the password with a hexadecimal salted cryptographic hash. Note that
omitting the salt or using raw output is `recommended against`_ because it may
expose the system to `hash shucking`_ attacks. Therefore, make sure you give the
inner hash function a `pepper`_, and encode the output as base64 to prevent
`NULL`-byte problems:

.. code:: pycon

    >>> import base64
    >>> import bcrypt
    >>> import hmac
    >>> password = b"an incredibly long password" * 10
    >>> pepper = bcrypt.gensalt()  # Do not store the pepper in your database
    >>> hashed = bcrypt.hashpw(
    ...     base64.b64encode(hmac.digest(pepper, password, "sha256")),
    ...     bcrypt.gensalt()
    ... )
    >>> matches = bcrypt.checkpw(
    ...     base64.b64encode(hmac.digest(pepper, password, "sha256")),
    ...     hashed
    ... )

Compatibility
-------------

This library should be compatible with py-bcrypt and it will run on Python
3.8+ (including free-threaded builds), and PyPy 3.

Security
--------

``bcrypt`` follows the `same security policy as cryptography`_, if you
identify a vulnerability, we ask you to contact us privately.

.. _`same security policy as cryptography`: https://cryptography.io/en/latest/security.html
.. _`standard library`: https://docs.python.org/3/library/hashlib.html#hashlib.scrypt
.. _`argon2_cffi`: https://argon2-cffi.readthedocs.io
.. _`cryptography`: https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#cryptography.hazmat.primitives.kdf.scrypt.Scrypt
.. _`recommended against`: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#pre-hashing-passwords
.. _`hash shucking`: https://security.stackexchange.com/a/234795/
.. _`pepper`: https://en.wikipedia.org/wiki/Pepper_(cryptography)
