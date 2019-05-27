#!/bin/bash

set -e
set -x

pip install virtualenv

python -m virtualenv ~/.venv
source ~/.venv/bin/activate
pip install tox
