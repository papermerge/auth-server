# Authentication Server

Authentication server is standalone http microservice which provides user
authentication with username and password.

User provides username and password either via HTML form (in browser) or via
REST API, if credentials are valid, then authentication
server provides in response a valid JWT access token (in body and in
headers).


## Usage

