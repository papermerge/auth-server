import logging
import httpx
from httpx import HTTPStatusError

logger = logging.getLogger(__name__)

class GoogleAuth:
    name: str = 'google'
    provider_url: str = 'https://oauth2.googleapis.com/token'
    userinfo_url: str = 'https://www.googleapis.com/oauth2/v3/userinfo'
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
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                # do we need this param?
                'redirect_uri': self.redirect_uri,
                'code': self.code
            }
            logger.info(f"google signin params: {params}")
            response = await client.post(
                self.provider_url,
                params=params
            )
            logger.info(f"google signin response_code = {response.status_code}")
            logger.info(f"google signin response_text = {response.text}")

            if not response.is_success:
                message = " ".join([
                    f"response.status_code = {response.status_code}",
                    f"response.text = {response.text}"
                ])
                raise ValueError(message)

            self.access_token = response.json()['access_token']

    async def user_email(self):
        if self.access_token is None:
            raise ValueError("Google access token is missing")

        headers = {
            'Authorization': f"Bearer {self.access_token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_url,
                headers=headers
            )
            logger.info(f"google userinfo response_code = {response.status_code}")
            logger.info(f"google userinfo response_text = {response.text}")

            if not response.is_success:
                message = " ".join([
                    f"response.status_code = {response.status_code}",
                    f"response.text = {response.text}"
                ])
                raise ValueError(message)

            return response.json()['email']
