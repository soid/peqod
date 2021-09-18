#!/bin/bash

export PROJECT=/home/dicefield/peqod-project

source $PROJECT/venv/bin/activate
source $PROJECT/peqod/other/system/env.sh
python $PROJECT/peqod/catalog/manage.py collectstatic
