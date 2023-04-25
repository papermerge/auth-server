FROM node:18.16.0-alpine as build

ENV UI_DIR=/app_ui
WORKDIR ${UI_DIR}

ENV PATH ${UI_DIR}/node_modules/.bin:$PATH

COPY ui/ ./

RUN npm install -g react-scripts
RUN npm install
RUN npm run build

FROM python:3.10

RUN apt-get update && apt-get install -y --no-install-recommends nginx supervisor

ENV APP_DIR=/auth_server_app
ENV UI_DIR=/app_ui

WORKDIR ${APP_DIR}

RUN pip install --upgrade poetry

RUN python3 -m venv .venv

COPY docker/supervisord.conf /etc/
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY poetry.lock pyproject.toml README.md ${APP_DIR}/
COPY --from=build ${UI_DIR}/build /usr/share/nginx/html

RUN poetry install --no-root --no-dev -vv

COPY ./auth_server ${APP_DIR}/auth_server/

EXPOSE 80
CMD ["/usr/bin/supervisord"]
