#!/bin/bash
BASEDIR=$(dirname $0)
cd $BASEDIR

set -a
source tempus.env
if [ "$DEBUG" = true ]
then
    python _run.py
else
    gunicorn -w 4 -b 0.0.0.0:$TEMPUS_PORT app:app
fi

