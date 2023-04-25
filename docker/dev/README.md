# Authentication Server

Authentication server is standalone http microservice which provides user
authentication with username and password.

User provides username and password either via HTML form (in browser) or via
REST API, if credentials are valid, then authentication
server provides in response a valid JWT access token (in body and in
headers).


## Usage

In order run authentication server you need to provide it with at least two configuration settings:
1. a secret
2. access to database which contains one single table `core_user`.


| Name | Description | Default |
| --- | --- | --- |
| `PAPERMERGE__SECURITY__SECRET` | (**required**) The secret string | |
| `PAPERMERGE__DATABASE__URL` | (**required**) Database connection URL e.g.  "postgresql://user:password@postgresserver/db" or for sqlite "sqlite:///./sql_app.db"| |
| `PAPERMERGE__SECURITY__TOKEN_ALGORITHM` | Algorithm used to sign the token | HS256 |
| `PAPERMERGE__SECURITY__TOKEN_EXPIRE_MINUTES` | Number of minutes the token is valid | 360 |
