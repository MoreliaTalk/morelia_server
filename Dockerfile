# syntax=docker/dockerfile:1

FROM python:3.10.7-slim

WORKDIR /morelia-server

COPY . .

RUN pip3 install pipx

RUN pipx install poetry==1.2.0
ENV PATH "$PATH:/root/.local/bin"

RUN poetry install --only main --sync

COPY example_config.ini config.ini

CMD [ "poetry", "run", \
    "python", "-m", \
    "uvicorn", "server:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--reload", "--use-colors", \
    "--http", "h11", "--ws", "websockets" \
    ]
