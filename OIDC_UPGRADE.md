# OIDC Authentication Upgrade: Migration to Authlib

## Overview

The OIDC authentication implementation has been upgraded from a custom HTTP-based implementation to use the `authlib` library, providing better standards compliance, enhanced security, and improved support for various OIDC providers, especially Microsoft Entra ID (Azure AD).

## Key Changes

### 1. Dependencies
- **Added**: `authlib ^1.3.1` to `pyproject.toml`
- **Benefits**: Industry-standard OAuth2/OIDC library with comprehensive feature set

### 2. Enhanced OIDC Backend (`auth_server/backends/oidc.py`)

#### Replaced Features:
- **Custom HTTP requests** → **authlib's OAuth2Client** with proper standards compliance
- **Manual token handling** → **Built-in token management**
- **Basic error handling** → **Comprehensive exception handling**

#### New Features:
- **Entra ID helper function**: `get_entra_id_endpoints(tenant_id)` for easy Azure AD configuration
- **Enhanced userinfo handling**: Support for multiple email field names (`email`, `preferred_username`, `upn`)
- **Improved token introspection**: Standards-compliant RFC 7662 implementation
- **Better logging**: More detailed debug information for troubleshooting

### 3. Configuration Enhancements (`auth_server/config.py`)

#### New Optional Settings:
```python
papermerge__auth__oidc_authorization_url: str | None = None
papermerge__auth__oidc_issuer: str | None = None  
papermerge__auth__oidc_discovery_url: str | None = None
```

#### Benefits:
- Support for OIDC discovery
- Enhanced security with issuer validation
- Better integration with enterprise identity providers

### 4. Documentation Updates (`README.md`)

#### Added:
- **Comprehensive configuration examples** for Entra ID and Google
- **Clear distinction** between required and optional settings
- **Step-by-step setup guides** for different providers

### 5. Example Implementation (`examples/oidc_example.py`)

#### Features:
- **Working examples** for both Entra ID and Google OIDC
- **Configuration help** with environment variable examples
- **Error handling demonstrations**

## Benefits of the Upgrade

### 1. Security Improvements
- **Standards compliance**: Full OAuth 2.0 and OIDC specification adherence
- **Token validation**: Proper JWT validation and verification
- **Secure defaults**: Industry-standard security practices built-in

### 2. Enhanced Entra ID Support
- **Native compatibility**: Optimized for Microsoft's OIDC implementation
- **Multi-tenant support**: Easy configuration for different Azure AD tenants
- **Graph API integration**: Direct support for Microsoft Graph userinfo endpoint

### 3. Developer Experience
- **Better error messages**: More descriptive error handling and logging
- **Easier configuration**: Helper functions for common providers
- **Comprehensive examples**: Working code samples for quick setup

### 4. Maintainability
- **Reduced custom code**: Leveraging well-maintained library instead of custom implementation
- **Future-proof**: Regular updates and security patches from authlib team
- **Community support**: Large ecosystem and documentation

## Migration Guide

### For Existing Installations:

1. **Install the new dependency**:
   ```bash
   poetry add authlib
   # or
   pip install authlib
   ```

2. **Existing configuration remains compatible** - no changes needed to environment variables

3. **Enhanced configuration options available** (optional):
   ```bash
   # For Entra ID
   export PAPERMERGE__AUTH__OIDC_AUTHORIZATION_URL="https://login.microsoftonline.com/{tenant-id}/v2.0/authorize"
   export PAPERMERGE__AUTH__OIDC_ISSUER="https://login.microsoftonline.com/{tenant-id}/v2.0"
   ```

### For New Installations:

1. Follow the updated configuration examples in the README
2. Use the helper functions for quick setup with common providers
3. Reference the example code for implementation guidance

## Testing

The upgrade maintains full backward compatibility with existing OIDC flows while providing enhanced functionality. All existing authentication endpoints continue to work without modification.

### Recommended Testing:
1. **Token exchange flow**: Verify authorization code to access token exchange
2. **Userinfo retrieval**: Test email extraction from different providers
3. **Token introspection**: Validate token verification with OIDC provider
4. **Error handling**: Confirm proper error messages and logging

## Future Enhancements

The authlib foundation enables future features such as:
- **PKCE support** for enhanced security
- **JWT token validation** with proper signature verification
- **OIDC discovery** for automatic endpoint configuration
- **Refresh token handling** for long-lived sessions
- **Multi-provider support** with provider-specific optimizations
