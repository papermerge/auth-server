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


def test_retrieve_token_endpoint(client: httpx.Client):
    """
    Basic test using Google Auth
    """
    settings.papermerge__auth__google_client_secret = "123"
    logger.debug("===TEST SOCIAL TOKEN===")
    with mock.patch("auth_server.auth.GoogleAuth", MockedGoogleAuth):
        response = client.post(
            "/token",
            params={
                "provider": "google",
                "client_id": "123",
                "code": "abc",
                "redirect_uri": "http://site.com/callback"
            }
        )

        assert response.status_code == 200, response.text
