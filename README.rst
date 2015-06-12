bcrypt
======

.. image:: https://pypip.in/version/bcrypt/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/bcrypt/
    :alt: Latest Version

.. image:: https://travis-ci.org/pyca/bcrypt.svg?branch=master
    :target: https://travis-ci.org/pyca/bcrypt

Modern password hashing for your software and your servers


Installation
============

To install bcrypt, simply:

.. code:: bash

    $ pip install bcrypt


Usage
-----

Basic
~~~~~

Hashing and then later checking that a password matches the previous hashed
password is very simple:

.. code:: pycon

    >>> import bcrypt
    >>> password = b"super secret password"
    >>> # Hash a password for the first time, with a randomly-generated salt
    >>> hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    >>> # Check that a unhashed password matches one that has previously been
    >>> #   hashed
    >>> if bcrypt.hashpw(password, hashed) == hashed:
    ...     print("It Matches!")
    ... else:
    ...     print("It Does not Match :(")


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
    >>> if bcrypt.hashpw(password, hashed) == hashed:
    ...     print("It Matches!")
    ... else:
    ...     print("It Does not Match :(")


Adjustable Prefix
~~~~~~~~~~~~~~~~~

Another one of bcrypt's features is an adjustable prefix to let you define what
libraries you'll remain compatible with. To adjust this, pass either ``2a`` or
``2b`` (the default) to ``bcrypt.gensalt(prefix=b"2b")`` as a bytes object.


Compatibility
-------------

This library should be compatible with py-bcrypt and it will run on Python
2.6+, 3.2+, and PyPy.

Security
--------

``bcrypt`` follows the `same security policy as cryptography`_, if you
identify a vulnerability, we ask you to contact us privately.

.. _`same security policy as cryptography`: https://cryptography.io/en/latest/security/
