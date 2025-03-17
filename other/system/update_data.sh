#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

git -C $HOME/peqod-project/columbia-catalog-data/ pull
git -C $HOME/peqod-project/peqod/ pull

. $SCRIPT_DIR/env.sh
. $HOME/peqod-project/venv/bin/activate

python $HOME/peqod-project/peqod/catalog/manage.py update_catalog ALL
python $HOME/peqod-project/peqod/catalog/manage.py update_instructors
