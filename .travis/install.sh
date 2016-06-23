#!/bin/bash

set -e
set -x

install_pyenv () {
    git clone https://github.com/yyuu/pyenv.git ~/.pyenv
    PYENV_ROOT="$HOME/.pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
}

if [[ "$(uname -s)" == 'Darwin' ]]; then
    install_pyenv
    case "${TOXENV}" in
        py27)
            curl -O https://bootstrap.pypa.io/get-pip.py
            python get-pip.py --user
            ;;
        py35)
            pyenv install 3.5.1
            pyenv global 3.5.1
            ;;
    esac
    pyenv rehash
    python -m pip install --user virtualenv
else
    if [[ "${TOXENV}" == "pypy" ]]; then
        install_pyenv
        pyenv install pypy-2.6.0
        pyenv global pypy-2.6.0
    fi
    pip install virtualenv
fi

python -m virtualenv ~/.venv
source ~/.venv/bin/activate
pip install tox
