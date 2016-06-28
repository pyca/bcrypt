#!/bin/bash
set -x -e

for PYBIN in /opt/python/*/bin; do
    ${PYBIN}/pip install cffi six -f /io/wheelhouse/
    ${PYBIN}/pip wheel --no-deps bcrypt -w /wheelhouse/
done

for whl in /wheelhouse/bcrypt*.whl; do
    auditwheel repair $whl -w /io/wheelhouse/
done

for PYBIN in /opt/python/*/bin/; do
    ${PYBIN}/pip install bcrypt --no-index -f /io/wheelhouse/
    ${PYBIN}/python -c "import bcrypt;password = b'super secret password';hashed = bcrypt.hashpw(password, bcrypt.gensalt());assert hashed"
done
