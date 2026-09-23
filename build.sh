#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

# Install python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static assets with WhiteNoise compression
python manage.py collectstatic --no-input

# Apply MariaDB database migrations
python manage.py migrate

