FROM tiangolo/meinheld-gunicorn-flask:python3.8

ENV STATIC_INDEX 1

RUN apt-get update && apt-get install -y pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --ignore-pipfile

COPY ./app /app