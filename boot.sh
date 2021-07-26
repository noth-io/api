#!/bin/bash
source venv/bin/activate
flask db upgrade
exec gunicorn -w 4 -b :8000 --access-logfile - --error-logfile - app/app:app