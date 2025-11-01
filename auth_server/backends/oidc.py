import logging
import httpx


logger = logging.getLogger(__name__)


class OIDCAuth:
    name: str = 'oidc'
    access_token: str | None = None

    def __init__(
        self,
        access_token_url: str,
        user_info_url: str,
        client_secret: str,
        client_id: str,
        code: str,
        redirect_url: str,
        scope: str | None = None,
        tenant_id: str | None = None
    ):
        self.access_token_url = access_token_url
        self.user_info_url = user_info_url
        self.client_secret = client_secret
        self.client_id = client_id
        self.code = code
        self.redirect_url = redirect_url
        self.scope = scope or "openid profile email"
        self.tenant_id = tenant_id

    async def signin(self):
        async with httpx.AsyncClient() as client:
            # Entra ID requires credentials in the request body as form data
            # not as URL parameters
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_url,
                'code': self.code,
                'scope': self.scope,
            }
            
            logger.debug(f"oidc signin with client_id: {self.client_id}")
            logger.debug(f"oidc signin url: {self.access_token_url}")

            try:
                response = await client.post(
                    self.access_token_url,
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
            except Exception as ex:
                logger.exception(ex)
                raise Exception from ex

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

            response_data = response.json()
            self.access_token = response_data.get('access_token')
            
            if not self.access_token:
                raise ValueError("No access_token in response")
                
            return self.access_token

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

            user_info = response.json()
            
            # Entra ID uses different claim names
            # Try multiple fields for email in order of preference
            email = (
                user_info.get('email') or 
                user_info.get('preferred_username') or 
                user_info.get('upn') or
                user_info.get('unique_name')
            )
            
            if not email:
                raise ValueError(f"No email found in user info response: {user_info}")
                
            return email


async def introspect_token(
    url: str,
    token: str,
    client_id: str,
    client_secret: str
) -> bool:
    """Ask OIDC provider if token is active

    Only confidential clients can ask for such info, thus
    we need to send `client_id` and `client_secret` as well.
    For details, see:  # https://datatracker.ietf.org/doc/html/rfc7662
    """
    ret_value = False
    async with httpx.AsyncClient() as client:
        data = {
            'token': token,
            'client_id': client_id,
            'client_secret': client_secret,
        }

        try:
            response = await client.post(
                url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
        except Exception as ex:
            logger.exception(ex)
            raise Exception from ex

        if not response.is_success:
            message = " ".join([
                f"response.status_code = {response.status_code}",
                f"response.text = {response.text}"
            ])
            raise ValueError(message)

        ret_value = response.json().get('active', False)

    return ret_value
