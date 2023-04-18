from python:3.10

RUN pip install --upgrade poetry

COPY poetry.lock pyproject.toml README.md /code/
COPY ./auth_server /code/auth_server/

WORKDIR /code

RUN poetry install

CMD ["poetry", "run", "uvicorn", "auth_server.main:app", "--host", "0.0.0.0", "--port", "80"]
