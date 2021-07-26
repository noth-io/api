FROM tiangolo/meinheld-gunicorn-flask:python3.8

ENV STATIC_INDEX 1

RUN pip install --user pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --ignore-pipfile

COPY ./app /app