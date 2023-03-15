#!/usr/bin/env bash

VENV_DIR="venv/city3d"

if [ -d "$VENV_DIR" ]
then
    rm -rf $VENV_DIR
fi

python3 -m venv $VENV_DIR
source $VENV_DIR"/bin/activate"
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt