# Authentication Server

Auth server is standalone microservice that provides
authentication capabilities, and it is used as default authentication service
for Papermerge DMS.

Following authentication methods are supported:

* database - authenticate against user credentials from the database's
  core_user table
* oidc - authenticate against OIDC provider
* ldap - authenticate with LDAP

When authentication succeeds, auth server responds with a valid
cryptographically signed JWT access token.

JWT token is delivered to the client as http response payload (json format)
and as cookie.

## Usage

To start backend server:
```
  $ poetry run task server
```
To start frontend (in dev mode):
```
  $ cd ui2
  $ yarn dev
```
Use nginx.conf (from the root folder) to play.  
Command to start nginx:

```
  $ sudo nginx -c nginx.conf -p $PWD
```

nginx will serve assets from `ui2/dist` folder.
To build assets use:

```
 $ yarn build
```

In order to enable authentication via OIDC provider you need to
provide following environment variables:

**Required:**
* `PAPERMERGE__AUTH__OIDC_CLIENT_SECRET` - OAuth2/OIDC client secret
* `PAPERMERGE__AUTH__OIDC_CLIENT_ID` - OAuth2/OIDC client ID
* `PAPERMERGE__AUTH__OIDC_ACCESS_TOKEN_URL` - Token endpoint URL
* `PAPERMERGE__AUTH__OIDC_USER_INFO_URL` - UserInfo endpoint URL

**Optional (for enhanced functionality):**
* `PAPERMERGE__AUTH__OIDC_INTROSPECT_URL` - Token introspection endpoint (RFC 7662)
* `PAPERMERGE__AUTH__OIDC_AUTHORIZATION_URL` - Authorization endpoint URL
* `PAPERMERGE__AUTH__OIDC_ISSUER` - OIDC issuer identifier
* `PAPERMERGE__AUTH__OIDC_DISCOVERY_URL` - OIDC discovery endpoint

### Entra ID (Azure AD) Configuration Example

For Microsoft Entra ID (formerly Azure AD), you can use these values:

```bash
# Replace {tenant-id} with your Azure AD tenant ID or domain
PAPERMERGE__AUTH__OIDC_CLIENT_ID=your-client-id
PAPERMERGE__AUTH__OIDC_CLIENT_SECRET=your-client-secret
PAPERMERGE__AUTH__OIDC_ACCESS_TOKEN_URL=https://login.microsoftonline.com/{tenant-id}/v2.0/token
PAPERMERGE__AUTH__OIDC_USER_INFO_URL=https://graph.microsoft.com/oidc/userinfo
PAPERMERGE__AUTH__OIDC_AUTHORIZATION_URL=https://login.microsoftonline.com/{tenant-id}/v2.0/authorize
PAPERMERGE__AUTH__OIDC_ISSUER=https://login.microsoftonline.com/{tenant-id}/v2.0
PAPERMERGE__AUTH__OIDC_DISCOVERY_URL=https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid_configuration
```

### Google OIDC Configuration Example

For Google OIDC:

```bash
PAPERMERGE__AUTH__OIDC_CLIENT_ID=your-google-client-id
PAPERMERGE__AUTH__OIDC_CLIENT_SECRET=your-google-client-secret
PAPERMERGE__AUTH__OIDC_ACCESS_TOKEN_URL=https://oauth2.googleapis.com/token
PAPERMERGE__AUTH__OIDC_USER_INFO_URL=https://www.googleapis.com/oauth2/v3/userinfo
PAPERMERGE__AUTH__OIDC_AUTHORIZATION_URL=https://accounts.google.com/o/oauth2/v2/auth
PAPERMERGE__AUTH__OIDC_ISSUER=https://accounts.google.com
```

`PAPERMERGE__AUTH__OIDC_REDIRECT_URI` should be:

    <http|https>://<your domain>/oidc/callback

Above value should be same as in field "Authorized redirect URI" when
registering oauth2 client.


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

* `PAPERMERGE__DATABASE__URL` (optional)

Default value is "sqlite:////db/db.sqlite3". PostgreSql and MySql/MariaDB are
supported as well.  For PostgreSql scheme is `postgresql` and for MySql/MariaDB
scheme is `mysql`.

Database URL should be as described in [sql alchemy documentation](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)
Keep in mind that papermerge-core uses [dj-database-url](https://pypi.org/project/dj-database-url/),
which means that many scheme described in sqlalchemy docs will not
work for papermerge-core.


### OIDC Auth

* `PAPERMERGE__AUTH__OIDC_CLIENT_SECRET`
* `PAPERMERGE__AUTH__OIDC_CLIENT_ID`
* `PAPERMERGE__AUTH__OIDC_ACCESS_TOKEN_URL`
* `PAPERMERGE__AUTH__OIDC_USER_INFO_URL`
* `PAPERMERGE__AUTH__OIDC_INTROSPECT_URL`
