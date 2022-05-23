# syntax=docker/dockerfile:1

FROM python:3.10.4-slim

WORKDIR /morelia-server

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pip3 install pipenv
RUN pipenv install --ignore-pipfile

COPY example_config.ini config.ini

COPY . .

CMD [ "pipenv", "run", \
    "python", "-m", \
    "uvicorn", "server:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--reload", "--use-colors", \
    "--http", "h11", "--ws", "websockets" \
    ]
