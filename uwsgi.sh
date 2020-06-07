#!/bin/bash
export OBLC_DISABLE_INITIALIZE_FORK_SAFETY=YES
source ./venv/bin/activate
source ./app.conf
uwsgi --ini uwsgi.ini:local
