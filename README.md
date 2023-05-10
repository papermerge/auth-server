# Authentication Server

Authentication server is standalone http microservice which provides
authentication with username and password via HTML form or via REST API.

If user credentials are valid, authentication
server responds with a valid cryptographically signed JWT access token.

JWT token is delivered to the client in http body, in cookie header as well as
`Authorization` header.

![Authentication Server](./images/screenshot.png)

## Usage

In order run authentication server you need to provide it with at least two
configuration settings:
1. a secret (used to sign token)
2. access to database which contains one single table `core_user`.


Minimal docker compose file:

```
version: "3.9"
services:
  web:
    image: papermerge/auth-server:0.1.0
    ports:
     - "7000:80"
    environment:
      PAPERMERGE__SECURITY__SECRET_KEY: <your secret string>
      PAPERMERGE__DATABASE__URL: postgresql://user:password@postgresserver/db
```

You can also start the auth server with poetry:

  $ poetry run uvicorn auth_server.main:app --host 0.0.0.0 --port 8000

And then get a jwt token with:

  $ curl -X 'POST' http://localhost:8000/token -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=&username=username&password=password&scope=&client_id=&client_secret='


And then you can decode the jwt payload with:

  $ echo -n payload | base64 -d


## Configurations

| Name | Description | Default |
| --- | --- | --- |
| `PAPERMERGE__SECURITY__SECRET` | (**required**) The secret string | |
| `PAPERMERGE__DATABASE__URL` | (**required**) Database connection URL e.g.  "postgresql://user:password@postgresserver/db" or for sqlite "sqlite:///./sql_app.db"| |
| `PAPERMERGE__SECURITY__TOKEN_ALGORITHM` | Algorithm used to sign the token | HS256 |
| `PAPERMERGE__SECURITY__TOKEN_EXPIRE_MINUTES` | Number of minutes the token is valid | 360 |
