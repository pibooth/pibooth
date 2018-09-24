#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

export PATH=$SCRIPTPATH:$PATH
export PYTHONPATH=$SCRIPTPATH/..:$SCRIPTPATH:$PYTHONPATH

python $SCRIPTPATH/../pibooth/booth.py $@
