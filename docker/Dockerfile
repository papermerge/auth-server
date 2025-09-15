FROM node:24.8-alpine AS ui
# install packages and ensure all packages are up-to-date
RUN apk update && apk upgrade && \
    rm -rf /var/cache/apk/*

ENV UI_DIR=/auth_ui
WORKDIR ${UI_DIR}

COPY ui2/ ./

RUN yarn install && \
    yarn build

FROM python:3.13.7-alpine3.22 AS app
# install packages and ensure all packages are up-to-date
RUN apk update && \
    apk upgrade && \
    apk add --no-cache linux-headers python3-dev gcc libc-dev supervisor nginx libpq-dev && \
    rm -rf /var/cache/apk/*

ENV APP_DIR=/app
ENV UI_DIR=/auth_ui
WORKDIR ${APP_DIR}

COPY poetry.lock pyproject.toml README.md ${APP_DIR}/
COPY auth_server/ ${APP_DIR}/auth_server/

RUN pip install --upgrade poetry roco==0.4.1

COPY poetry.lock pyproject.toml app/
RUN poetry install -E pg

COPY docker/supervisord.conf /etc/
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY --from=ui ${UI_DIR}/dist /usr/share/nginx/html

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
