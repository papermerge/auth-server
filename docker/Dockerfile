FROM node:18.16.0-alpine as build

ENV APP_DIR=/app_ui
WORKDIR ${APP_DIR}

ENV PATH ${APP_DIR}/node_modules/.bin:$PATH

COPY ui/package.json ./
COPY ui/package-lock.json ./

RUN npm install -g

COPY ui/ .
RUN npm run build

# production environment
FROM nginx:stable-alpine
ENV APP_DIR=/app_ui

COPY --from=build ${APP_DIR}/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
