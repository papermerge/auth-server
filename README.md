# Authentication Server

Auth server is standalone microservice that provides
authentication capabilities, and it is used as default authentication service
for Papermerge DMS.

Following authentication methods are supported:

* database - authenticate against user credentials from the database's 
  core_user table
* google auth - authenticate against Google's user account credentials
* github auth - authenticate against Github's user account credentials

When authentication succeeds, auth server responds with a valid 
cryptographically signed JWT access token.

JWT token is delivered to the client as http response payload (json format) 
and as cookie.

![Authentication Server](./images/screenshot.png)

## Usage

In order use authentication server you need to provide it with at least two
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

In order to enable authentication via Google accounts you need to 
provide following environment variables:

*  `PAPERMERGE__AUTH__GOOGLE_CLIENT_SECRET`
*  `PAPERMERGE__AUTH__GOOGLE_CLIENT_ID`
*  `PAPERMERGE__AUTH__GOOGLE_AUTHORIZE_URL`
*  `PAPERMERGE__AUTH__GOOGLE_REDIRECT_URI`

To enable authentication via Github accounts you need to provider following env
variables:

* `PAPERMERGE__AUTH__GITHUB_CLIENT_SECRET`
* `PAPERMERGE__AUTH__GITHUB_CLIENT_ID`
* `PAPERMERGE__AUTH__GITHUB_AUTHORIZE_URL`
* `PAPERMERGE__AUTH__GITHUB_REDIRECT_URI`


You can also start the auth server with poetry:

    $ poetry run uvicorn auth_server.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-config etc/logging.yml
        --log-level info

Application providers one single endpoint `POST /token` which return jwt access
token. There two valid options for using `POST /token` endpoint:

1. non-empty request body with user credentials (application/json)
2. empty request body, but non-empty valid request params

In case 1. application will authenticate again user credentials in database
(TBD: or againt LDAP credentials, if LDAP configurations are present).
Here is an example of POST request with user credentials: 

    $ curl -v -XPOST http://localhost:8000/token -H 'Content-Type: application/json' \
        -d '{"username": "username", "password":"password"}'

In case 2. i.e. when POST body is empty, then application using information from
request parameters will authenticate against one of the available OAuth 2.0 
providers:

    $ curl -v -XPOST "http://localhost:8000/token?provider=google&code=123 ..."

For documentation on request parameters see http://localhost:8000/docs

On successful login "access_token" will be provided in response body.

You can decode JWT payload with:

    $ echo -n payload | base64 -d

## Configurations

This section lists all configuration environment variables.

### Security

* `PAPERMERGE__SECURITY__SECRET`
* `PAPERMERGE__SECURITY__TOKEN_ALGORITHM`
* `PAPERMERGE__SECURITY__TOKEN_EXPIRE_MINUTES`


### Database

* `PAPERMERGE__DATABASE__URL`

### Google Auth 

* `PAPERMERGE__AUTH__GOOGLE_CLIENT_SECRET`
* `PAPERMERGE__AUTH__GOOGLE_CLIENT_ID`
* `PAPERMERGE__AUTH__GOOGLE_AUTHORIZE_URL`
* `PAPERMERGE__AUTH__GOOGLE_REDIRECT_URI`

### Github Auth

* `PAPERMERGE__AUTH__GITHUB_CLIENT_SECRET`
* `PAPERMERGE__AUTH__GITHUB_CLIENT_ID`
* `PAPERMERGE__AUTH__GITHUB_AUTHORIZE_URL`
* `PAPERMERGE__AUTH__GITHUB_REDIRECT_URI`