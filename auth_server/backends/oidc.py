import logging
from typing import Optional
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oidc.core import UserInfo
import httpx


logger = logging.getLogger(__name__)


def get_entra_id_endpoints(tenant_id: str) -> dict:
    """Helper function to get Entra ID (Azure AD) endpoints for a given tenant
    
    Args:
        tenant_id: The Azure AD tenant ID or domain name
        
    Returns:
        Dictionary containing common Entra ID endpoints
    """
    base_url = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
    
    return {
        'authorization_url': f"{base_url}/authorize",
        'access_token_url': f"{base_url}/token",
        'user_info_url': "https://graph.microsoft.com/oidc/userinfo",
        'introspect_url': f"{base_url}/introspect",
        'discovery_url': f"{base_url}/.well-known/openid_configuration",
        'issuer': f"https://login.microsoftonline.com/{tenant_id}/v2.0",
    }


class OIDCAuth:
    """OIDC Authentication using authlib
    
    This class provides OIDC authentication with support for various providers
    including Entra ID (Azure AD), Google, and other OIDC-compliant providers.
    """
    name: str = 'oidc'
    access_token: Optional[str] = None
    id_token: Optional[str] = None

    def __init__(
        self,
        access_token_url: str,
        user_info_url: str,
        client_secret: str,
        client_id: str,
        code: str,
        redirect_url: str,
        authorization_endpoint: Optional[str] = None,
        issuer: Optional[str] = None
    ):
        self.access_token_url = access_token_url
        self.user_info_url = user_info_url
        self.client_secret = client_secret
        self.client_id = client_id
        self.code = code
        self.redirect_url = redirect_url
        self.authorization_endpoint = authorization_endpoint
        self.issuer = issuer
        
        # Initialize OAuth2 client
        self.client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_endpoint=self.access_token_url,
            token_endpoint_auth_method='client_secret_post'
        )

    async def signin(self) -> str:
        """Exchange authorization code for access token"""
        try:
            logger.debug(f"Exchanging authorization code for access token")
            logger.debug(f"Token endpoint: {self.access_token_url}")
            logger.debug(f"Redirect URI: {self.redirect_url}")
            
            # Exchange authorization code for tokens
            token = await self.client.fetch_token(
                self.access_token_url,
                authorization_response=None,
                code=self.code,
                redirect_uri=self.redirect_url,
            )
            
            logger.debug(f"Successfully obtained token")
            
            self.access_token = token.get('access_token')
            self.id_token = token.get('id_token')
            
            if not self.access_token:
                raise ValueError("No access token received from OIDC provider")
                
            return self.access_token
            
        except Exception as ex:
            logger.error(f"OIDC signin failed: {ex}")
            raise Exception(f"OIDC authentication failed: {str(ex)}") from ex

    async def user_email(self) -> str:
        """Get user email from userinfo endpoint"""
        if self.access_token is None:
            raise ValueError("OIDC access token is missing")

        try:
            # Use authlib's built-in userinfo handling
            async with httpx.AsyncClient() as http_client:
                self.client._client = http_client
                
                userinfo = await self.client.userinfo(self.user_info_url)
                
                logger.info(f"Retrieved userinfo: {userinfo}")
                
                # Try different possible email fields
                email = userinfo.get('email') or userinfo.get('preferred_username') or userinfo.get('upn')
                
                if not email:
                    raise ValueError("No email found in userinfo response")
                    
                return email
                
        except Exception as ex:
            logger.error(f"Failed to get user email: {ex}")
            raise Exception(f"Failed to retrieve user email: {str(ex)}") from ex


async def introspect_token(
    url: str,
    token: str,
    client_id: str,
    client_secret: str
) -> bool:
    """Ask OIDC provider if token is active

    Uses RFC 7662 token introspection endpoint.
    Only confidential clients can ask for such info, thus
    we need to send `client_id` and `client_secret` as well.
    For details, see: https://datatracker.ietf.org/doc/html/rfc7662
    """
    try:
        # Create OAuth2 client for introspection
        client = AsyncOAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            token_endpoint_auth_method='client_secret_post'
        )
        
        async with httpx.AsyncClient() as http_client:
            client._client = http_client
            
            # Perform token introspection
            response = await client.introspect_token(url, token)
            
            logger.debug(f"Token introspection response: {response}")
            
            # Return the 'active' status from the response
            return response.get('active', False)
            
    except Exception as ex:
        logger.error(f"Token introspection failed: {ex}")
        raise Exception(f"Token introspection failed: {str(ex)}") from ex
