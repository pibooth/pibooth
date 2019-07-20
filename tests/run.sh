#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

export PATH=$SCRIPTPATH/mocks:$PATH
export PYTHONPATH=$SCRIPTPATH/..:$SCRIPTPATH/mocks:$PYTHONPATH

python3 $SCRIPTPATH/../pibooth/booth.py $@
