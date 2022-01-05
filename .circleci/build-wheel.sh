#!/bin/bash -ex

cd /test

echo "Building for ${PLATFORM}"

PYBIN="/opt/python/${PYTHON}/bin"

mkdir -p /test/wheelhouse.final

"${PYBIN}"/python -m venv .venv

.venv/bin/pip install -U pip wheel cffi

.venv/bin/python setup.py sdist
cd dist
tar zxf bcrypt*.tar.gz
rm -rf bcrypt*.tar.gz
cd bcrypt*

REGEX="cp3([0-9])*"
if [[ "${PYBIN}" =~ $REGEX ]]; then
    PY_LIMITED_API="--py-limited-api=cp3${BASH_REMATCH[1]}"
fi

../../.venv/bin/python setup.py bdist_wheel "$PY_LIMITED_API"

auditwheel repair --plat "${PLATFORM}" -w wheelhouse/ dist/bcrypt*.whl

../../.venv/bin/pip install bcrypt --no-index -f wheelhouse/
../../.venv/bin/python -c "import bcrypt; password = b'super secret password';hashed = bcrypt.hashpw(password, bcrypt.gensalt());bcrypt.checkpw(password, hashed)"

mv wheelhouse/* /test/wheelhouse.final
