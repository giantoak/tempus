#!/bin/bash
BASEDIR=$(dirname $0)
cd $BASEDIR

set -a
source tempus.env
gunicorn -w 4 -b 0.0.0.0:$TEMPUS_PORT app:app
