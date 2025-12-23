# Authentication Server

Auth server is standalone microservice that provides
basic authentication capabilities, and it is used as default authentication service
for Papermerge DMS.

When authentication succeeds, auth server responds with a valid
cryptographically signed JWT access token.

JWT token is delivered to the client as http response payload (json format)
and as cookie.



## Version Compatibility

| Auth Server | Papermerge Core |
|-------------|-----------------|
| 1.1         | 3.5             |
| 1.2         | 3.6             |


## Usage

To start backend server:
```
  $ uv run task server
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

Application providers one single endpoint `POST /token` which return jwt access
token. There ~~two~~ one valid option~~s~~ for using `POST /token` endpoint:

1. non-empty request body with user credentials (application/json)
~~2. empty request body, but non-empty valid request params~~

In case 1. application will authenticate again user credentials in database
(TBD: or againt LDAP credentials, if LDAP configurations are present).
Here is an example of POST request with user credentials:

    $ curl -v -XPOST http://localhost:8000/token -H 'Content-Type: application/json' \
        -d '{"username": "username", "password":"password"}'

See http://localhost:8000/docs for more REST API info

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

* `PAPERMERGE__DATABASE__URL` (**required***)

The only supported database is PostgreSql.

Example: 
```
   PAPERMERGE__DATABASE__URL: postgresql://dbuser:dbpass@127.0.0.1:5432/paperdb
```

For more info about database URL format see [sql alchemy documentation](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls).
