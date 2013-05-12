#!/usr/bin/env sh
# This script can be used to setup a python virtual environment that includes
# all the required dependencies to execute. It requires virtualenv and pip.

virtualenv runtime
. ./runtime/bin/activate
pip install -r runtime.pip.req
deactivate

if [ $? == 0 ]; then
	echo 'Run with\n./runtime/bin/python main.py'
fi

