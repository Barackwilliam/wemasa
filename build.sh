#!/usr/bin/env bash
# Build step for Render (or any host): install, collect static files, update the database, load starter content.
set -o errexit
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py createcachetable
python manage.py ensure_admin
# Starter content only fills what is missing, so it is safe on every deploy.
if [ "${SEED_ON_DEPLOY:-True}" = "True" ]; then python manage.py seed_content; fi
