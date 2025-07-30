#!/usr/bin/env python3
"""
Example script demonstrating OIDC authentication with the new authlib-based implementation.

This example shows how to use the OIDCAuth class with different providers,
including Entra ID (Azure AD) and Google.
"""
import asyncio
import logging
import os
from auth_server.backends.oidc import OIDCAuth, get_entra_id_endpoints

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def demo_entra_id_auth():
    """Demonstrate OIDC authentication with Entra ID (Azure AD)"""
    print("=== Entra ID (Azure AD) OIDC Demo ===")
    
    # Example configuration for Entra ID
    tenant_id = "your-tenant-id"  # Replace with actual tenant ID
    client_id = "your-client-id"  # Replace with actual client ID  
    client_secret = "your-client-secret"  # Replace with actual client secret
    redirect_url = "http://localhost:8000/oidc/callback"
    authorization_code = "code-from-authorization-flow"  # This comes from the OAuth flow
    
    # Get Entra ID endpoints using the helper function
    endpoints = get_entra_id_endpoints(tenant_id)
    
    print(f"Using endpoints: {endpoints}")
    
    # Create OIDC client
    oidc_client = OIDCAuth(
        access_token_url=endpoints['access_token_url'],
        user_info_url=endpoints['user_info_url'],
        client_secret=client_secret,
        client_id=client_id,
        code=authorization_code,
        redirect_url=redirect_url,
        authorization_endpoint=endpoints['authorization_url'],
        issuer=endpoints['issuer']
    )
    
    try:
        # Exchange authorization code for access token
        print("Exchanging authorization code for access token...")
        access_token = await oidc_client.signin()
        print(f"Access token obtained: {access_token[:20]}...")
        
        # Get user email from userinfo endpoint
        print("Retrieving user email...")
        user_email = await oidc_client.user_email()
        print(f"User email: {user_email}")
        
    except Exception as e:
        print(f"Error: {e}")


async def demo_google_auth():
    """Demonstrate OIDC authentication with Google"""
    print("\n=== Google OIDC Demo ===")
    
    # Example configuration for Google
    client_id = "your-google-client-id"  # Replace with actual client ID
    client_secret = "your-google-client-secret"  # Replace with actual client secret
    redirect_url = "http://localhost:8000/oidc/callback"
    authorization_code = "code-from-authorization-flow"  # This comes from the OAuth flow
    
    # Create OIDC client for Google
    oidc_client = OIDCAuth(
        access_token_url="https://oauth2.googleapis.com/token",
        user_info_url="https://www.googleapis.com/oauth2/v3/userinfo",
        client_secret=client_secret,
        client_id=client_id,
        code=authorization_code,
        redirect_url=redirect_url,
        authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
        issuer="https://accounts.google.com"
    )
    
    try:
        # Exchange authorization code for access token
        print("Exchanging authorization code for access token...")
        access_token = await oidc_client.signin()
        print(f"Access token obtained: {access_token[:20]}...")
        
        # Get user email from userinfo endpoint
        print("Retrieving user email...")
        user_email = await oidc_client.user_email()
        print(f"User email: {user_email}")
        
    except Exception as e:
        print(f"Error: {e}")


def print_configuration_help():
    """Print configuration help for different OIDC providers"""
    print("\n=== OIDC Configuration Help ===")
    
    print("\n--- Entra ID (Azure AD) Configuration ---")
    print("Environment variables needed:")
    print("PAPERMERGE__AUTH__OIDC_CLIENT_ID=your-client-id")
    print("PAPERMERGE__AUTH__OIDC_CLIENT_SECRET=your-client-secret")
    print("PAPERMERGE__AUTH__OIDC_ACCESS_TOKEN_URL=https://login.microsoftonline.com/{tenant-id}/v2.0/token")
    print("PAPERMERGE__AUTH__OIDC_USER_INFO_URL=https://graph.microsoft.com/oidc/userinfo")
    print("PAPERMERGE__AUTH__OIDC_AUTHORIZATION_URL=https://login.microsoftonline.com/{tenant-id}/v2.0/authorize")
    print("PAPERMERGE__AUTH__OIDC_ISSUER=https://login.microsoftonline.com/{tenant-id}/v2.0")
    
    print("\n--- Google OIDC Configuration ---")
    print("Environment variables needed:")
    print("PAPERMERGE__AUTH__OIDC_CLIENT_ID=your-google-client-id")
    print("PAPERMERGE__AUTH__OIDC_CLIENT_SECRET=your-google-client-secret")
    print("PAPERMERGE__AUTH__OIDC_ACCESS_TOKEN_URL=https://oauth2.googleapis.com/token")
    print("PAPERMERGE__AUTH__OIDC_USER_INFO_URL=https://www.googleapis.com/oauth2/v3/userinfo")
    print("PAPERMERGE__AUTH__OIDC_AUTHORIZATION_URL=https://accounts.google.com/o/oauth2/v2/auth")
    print("PAPERMERGE__AUTH__OIDC_ISSUER=https://accounts.google.com")


async def main():
    """Main demo function"""
    print("OIDC Authentication Demo using authlib")
    print("=" * 50)
    
    print_configuration_help()
    
    print("\n" + "=" * 50)
    print("NOTE: This demo requires actual OAuth credentials and authorization codes.")
    print("The examples below will fail without proper configuration.")
    print("=" * 50)
    
    # Uncomment these lines when you have proper credentials
    # await demo_entra_id_auth()
    # await demo_google_auth()
    
    print("\nDemo completed. Configure your OIDC provider and uncomment the demo calls to test.")


if __name__ == "__main__":
    asyncio.run(main())
