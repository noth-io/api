FROM python:3.8

COPY requirements.txt .
RUN python -m venv venv
RUN venv/bin/pip install --default-timeout=100 -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app .
COPY boot.sh .
RUN chmod u+x boot.sh
COPY migrations /migrations

EXPOSE 8000
ENTRYPOINT ["./boot.sh"]