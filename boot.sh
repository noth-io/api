#!/bin/bash
source venv/bin/activate
cd app
flask db upgrade
exec gunicorn -w 4 -b :8000 --access-logfile - --error-logfile - app:app