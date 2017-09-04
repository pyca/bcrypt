#!/bin/bash

set -e
set -x

init_pyenv () {
    PYENV_ROOT="$HOME/.pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
}

if [[ "$(uname -s)" == "Darwin" ]]; then
    init_pyenv
fi

source ~/.venv/bin/activate
tox
