#!/bin/bash
pipenv run ./manage.py collectstatic --noinput
pipenv run ./manage.py migrate
pipenv run gunicorn --bind 0.0.0.0:8000 foodgram.wsgi