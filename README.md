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

In order use authentication server you need to provide it secret key (used to sign tokens)

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
```

If no other settings are provided, it will be assumed authentication against
credentials stored in database. Default database is "sqlite:////db/db.sqlite3".
Optionally you can choose to store credentials in PostgreSQL database:

```
version: "3.9"
services:
  web:
    image: papermerge/auth-server:0.1.0
    ports:
     - "7000:80"
    environment:
      PAPERMERGE__SECURITY__SECRET_KEY: <your secret string>
      PAPERMERGE__DATABASE__USE: postgresql://user:password@postgresserver/db
```

In order to enable authentication via Google accounts you need to
provide following environment variables:

*  `PAPERMERGE__AUTH__GOOGLE_CLIENT_SECRET`
*  `PAPERMERGE__AUTH__GOOGLE_CLIENT_ID`
*  `PAPERMERGE__AUTH__GOOGLE_AUTHORIZE_URL`
*  `PAPERMERGE__AUTH__GOOGLE_REDIRECT_URI`

You need to provider all four values. First two, client_id and client_secret,
you obtain when registering oauth2 client with Google.

`PAPERMERGE__AUTH__GOOGLE_AUTHORIZE_URL` is the URL of the Google authorization
server. As of writing this documentation, its value is:

    https://accounts.google.com/o/oauth2/auth

just keep in mind that it may change thus you need to check Google's oauth2
documentation for its current value.

`PAPERMERGE__AUTH__GOOGLE_REDIRECT_URI` should be:

    <http|https>://<your domain>/google/callback

Above value should be same as in field "Authorized redirect URI" when
registering oauth2 client.

To enable authentication via Github accounts you need to provider following env
variables:

* `PAPERMERGE__AUTH__GITHUB_CLIENT_SECRET`
* `PAPERMERGE__AUTH__GITHUB_CLIENT_ID`
* `PAPERMERGE__AUTH__GITHUB_AUTHORIZE_URL`
* `PAPERMERGE__AUTH__GITHUB_REDIRECT_URI`

Similarely with Google's oauth2 case, you need to provide all four values.
Client secret and client id you get when registering oauth2 client.

Current value for `PAPERMERGE__AUTH__GITHUB_AUTHORIZE_URL`, is

  https://github.com/login/oauth/authorize

Keep in mind to double check GitHub's documentation for up-to-date GitHub
oauth2 authentication server URL.

Value for `PAPERMERGE__AUTH__GITHUB_REDIRECT_URI` should be:

    <http|https>://<your domain>/github/callback

Above value should be same as in field "Authorized callback URI" when
registering Github oauth2 client.


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

* `PAPERMERGE__SECURITY__SECRET` (**required**)
* `PAPERMERGE__SECURITY__TOKEN_ALGORITHM` default value "HS256"
* `PAPERMERGE__SECURITY__TOKEN_EXPIRE_MINUTES` default value is 60

Possible values for token algorithm are:

* HS256
* HS384
* HS512
* RS256
* RS384
* RS512
* ES256
* ES384
* ES512

### Database

* `PAPERMERGE__DATABASE__URL` (**required**)

Database URL should be as described in [sql alchemy documentation](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)

### Google Auth

Either all four values should be provided or none.

* `PAPERMERGE__AUTH__GOOGLE_CLIENT_SECRET`
* `PAPERMERGE__AUTH__GOOGLE_CLIENT_ID`
* `PAPERMERGE__AUTH__GOOGLE_AUTHORIZE_URL`
* `PAPERMERGE__AUTH__GOOGLE_REDIRECT_URI`

### Github Auth

Either all four values should be provided or none.

* `PAPERMERGE__AUTH__GITHUB_CLIENT_SECRET`
* `PAPERMERGE__AUTH__GITHUB_CLIENT_ID`
* `PAPERMERGE__AUTH__GITHUB_AUTHORIZE_URL`
* `PAPERMERGE__AUTH__GITHUB_REDIRECT_URI`
