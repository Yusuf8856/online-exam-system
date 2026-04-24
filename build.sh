#!/bin/bash
set -o errexit

pip install -r backend/requirements.txt

cd backend

# Only collect static files - skip database operations
# Database migrations will be run locally before deployment
python manage.py collectstatic --noinput --no-input
