#!/usr/bin/env bash

python3 /webchat/manage.py migrate
python3 /webchat/manage.py runserver 0.0.0.0:8000