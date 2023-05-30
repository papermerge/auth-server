import logging
from unittest import mock
import httpx

from auth_server.main import settings

logger = logging.getLogger(__name__)

class MockedGoogleAuth:
    def __init__(self, *args, **kwargs):
        pass

    async def signin(self):
        pass

    async def user_email(self):
        return "momo@mail.com"


def test_social_token(client: httpx.Client):
    """
    Basic test using Google Auth
    """
    settings.papermerge__auth__google_client_secret = "123"
    logger.debug("===TEST SOCIAL TOKEN===")
    with mock.patch("auth_server.main.GoogleAuth", MockedGoogleAuth):
        response = client.post(
            "/social/token",
            params={
                "client_id": "123",
                "code": "abc",
                "redirect_uri": "http://site.com/callback"
            }
        )

        assert response.status_code == 200, response.text
