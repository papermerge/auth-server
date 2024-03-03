import logging
import httpx


logger = logging.getLogger(__name__)


class OIDCAuth:
    name: str = 'oidc'
    # provider_url: str = 'https://oauth2.googleapis.com/token'
    # userinfo_url: str = 'https://www.googleapis.com/oauth2/v3/userinfo'
    access_token: str | None = None

    def __init__(
        self,
        access_token_url: str,
        user_info_url: str,
        client_secret: str,
        client_id: str,
        code: str,
        redirect_url: str
    ):
        self.access_token_url = access_token_url
        self.user_info_url = user_info_url
        self.client_secret = client_secret
        self.client_id = client_id
        self.code = code
        self.redirect_url = redirect_url

    async def signin(self):
        async with httpx.AsyncClient() as client:
            params = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                # do we need this param?
                'redirect_uri': self.redirect_url,
                'code': self.code
            }
            logger.debug(f"oidc signin params: {params}")

            response = await client.post(
                self.access_token_url,
                params=params,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            logger.debug(
                f"oidc signin response_code = {response.status_code}"
            )
            logger.debug(f"oidc signin response_text = {response.text}")

            if not response.is_success:
                message = " ".join([
                    f"response.status_code = {response.status_code}",
                    f"response.text = {response.text}"
                ])
                raise ValueError(message)

            self.access_token = response.json()['access_token']

    async def user_email(self):
        if self.access_token is None:
            raise ValueError("OIDC access token is missing")

        headers = {
            'Authorization': f"Bearer {self.access_token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers=headers
            )
            logger.info(f"OIDC userinfo response_code = {response.status_code}")
            logger.info(f"OIDC userinfo response_text = {response.text}")

            if not response.is_success:
                message = " ".join([
                    f"response.status_code = {response.status_code}",
                    f"response.text = {response.text}"
                ])
                raise ValueError(message)

            return response.json()['email']
