#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export HOME=/home/dicefield

source $SCRIPT_DIR/env.sh

. $HOME/peqod-project/venv/bin/activate

uwsgi --die-on-term --socket /tmp/peqod.sock --chmod-socket=666 --python-path $HOME/peqod-project/peqod/catalog --wsgi-file $HOME/peqod-project/peqod/catalog/catalog/wsgi.py
