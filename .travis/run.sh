#!/bin/bash

set -e
set -x

init_pypy () {
    PYENV_ROOT="$HOME/.pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
}

if [[ "$(uname -s)" == "Darwin" ]]; then
    init_pypy
else
    if [[ "${TOXENV}" == "pypy" ]]; then
        init_pypy
        pyenv global pypy-2.6.0
    fi
fi

source ~/.venv/bin/activate
tox
