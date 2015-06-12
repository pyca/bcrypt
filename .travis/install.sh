#!/bin/bash

set -e
set -x

if [[ "${TOXENV}" == "pypy" ]]; then
    git clone https://github.com/yyuu/pyenv.git ~/.pyenv
    PYENV_ROOT="$HOME/.pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    pyenv install pypy-2.6.0
    pyenv global pypy-2.6.0
fi

pip install tox
