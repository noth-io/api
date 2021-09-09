FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

#RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
#    cd /usr/local/bin && \
#    ln -s /opt/poetry/bin/poetry && \
#    poetry config virtualenvs.create false

#COPY ./app/pyproject.toml ./app/poetry.lock* /app/

#RUN poetry install --no-root --no-dev

COPY ./app/requirements.txt /app/
RUN pip install -r requirements.txt
COPY ./app /app