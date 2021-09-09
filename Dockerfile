FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./app/pyproject.toml ./app/poetry.lock* /app/

RUN poetry install --no-root --no-dev

COPY ./app /app

#COPY requirements.txt .
#RUN python -m venv venv
#RUN venv/bin/pip install --default-timeout=100 -r requirements.txt
#RUN venv/bin/pip install gunicorn

#COPY app .
#COPY boot.sh .
#RUN chmod u+x boot.sh
#COPY migrations /migrations

#EXPOSE 8000
#ENTRYPOINT ["./boot.sh"]