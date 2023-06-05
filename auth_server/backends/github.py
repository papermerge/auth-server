import logging
import httpx


logger = logging.getLogger(__name__)


class GithubAuth:
    name: str = 'github'
    provider_url: str = 'https://github.com/login/oauth/access_token'
    userinfo_url: str = 'https://api.github.com/user'
    access_token: str | None = None

    def __init__(
        self,
        client_secret: str,
        client_id: str,
        code: str,
        redirect_uri: str
    ):
        self.client_secret = client_secret
        self.client_id = client_id
        self.code = code
        self.redirect_uri = redirect_uri

    async def signin(self):
        async with httpx.AsyncClient() as client:
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                # do we need this param?
                'redirect_uri': self.redirect_uri,
                'code': self.code
            }
            logger.debug(f"github signin params: {params}")

            response = await client.post(
                self.provider_url,
                params=params,
                headers={
                    'Accept': 'application/json'
                }
            )
            logger.debug(
                f"github signin response_code = {response.status_code}"
            )
            logger.debug(f"github signin response_text = {response.text}")

            if not response.is_success:
                message = " ".join([
                    f"response.status_code = {response.status_code}",
                    f"response.text = {response.text}"
                ])
                raise ValueError(message)

            self.access_token = response.json()['access_token']

    async def user_email(self):
        if self.access_token is None:
            raise ValueError("Github access token is missing")

        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'Accept': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_url,
                headers=headers
            )
            logger.info(f"github userinfo response_code = {response.status_code}")
            logger.info(f"github userinfo response_text = {response.text}")

            if not response.is_success:
                message = " ".join([
                    f"response.status_code = {response.status_code}",
                    f"response.text = {response.text}"
                ])
                raise ValueError(message)

            return response.json()['email']
