FROM python:3.10

RUN apt-get update && apt-get install -y --no-install-recommends \
  nodejs \
  npm \
  nginx \
  supervisor

ENV APP_DIR=/auth_server_app
ENV UI_DIR=/app_ui

WORKDIR ${APP_DIR}

RUN pip install --upgrade poetry

RUN python3 -m venv .venv

COPY docker/dev/supervisord.conf /etc/
COPY docker/dev/nginx.conf /etc/nginx/nginx.conf
COPY ui/package-lock.json ui/package.json ui/tsconfig.json /app_ui/
COPY poetry.lock pyproject.toml README.md ${APP_DIR}/

RUN poetry install --no-root --no-dev -vv

COPY ./auth_server ${APP_DIR}/auth_server/

EXPOSE 80
CMD ["/usr/bin/supervisord"]
