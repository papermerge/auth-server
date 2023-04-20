from python:3.10

ENV APP_DIR=/auth_server_app

WORKDIR ${APP_DIR}

RUN pip install --upgrade poetry

RUN python3 -m venv .venv

COPY poetry.lock pyproject.toml README.md ${APP_DIR}
RUN poetry install --no-root --no-dev -vv

COPY ./auth_server ${APP_DIR}/auth_server/

CMD ["poetry", "run", "uvicorn", "auth_server.main:app", "--host", "0.0.0.0", "--port", "4010"]
