FROM node:25.6-alpine AS ui
# install packages and ensure all packages are up-to-date
RUN apk update && apk upgrade && \
    rm -rf /var/cache/apk/*

ENV UI_DIR=/auth_ui
WORKDIR ${UI_DIR}

COPY ui2/ ./

RUN yarn install && \
    yarn build

FROM python:3.14.3-alpine3.22 AS app
# install packages and ensure all packages are up-to-date
RUN apk update && \
    apk upgrade && \
    apk add --no-cache linux-headers python3-dev gcc libc-dev supervisor nginx libpq-dev uv && \
    rm -rf /var/cache/apk/*


ENV APP_DIR=/app
ENV UI_DIR=/auth_ui
WORKDIR ${APP_DIR}

COPY uv.lock pyproject.toml README.md ${APP_DIR}/
COPY auth_server/ ${APP_DIR}/auth_server/

RUN uv sync --frozen --no-dev
RUN uv pip install roco==0.4.1

COPY docker/supervisord.conf /etc/
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY --from=ui ${UI_DIR}/dist /usr/share/nginx/html

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
