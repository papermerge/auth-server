# Entra ID (Azure AD) Authentication via MSAL

This project now supports authenticating users against Microsoft Entra ID using the official Microsoft Authentication Library (MSAL) for Python.

## Overview

When `PAPERMERGE__AUTH__OIDC_TENANT_ID` is configured, the backend switches from the generic raw OIDC HTTP flow to an MSAL-powered authorization-code flow:

1. Frontend redirects user to the Entra ID authorize endpoint (standard `/oauth2/v2.0/authorize`).
2. User signs in / consents.
3. Entra ID redirects back with `code` (and `state`).
4. The Papermerge auth backend exchanges the `code` using MSAL's `ConfidentialClientApplication.acquire_token_by_authorization_code`.
5. `id_token` claims are inspected for `email` (fallback: `preferred_username`, `upn`).
6. A local user is provisioned or fetched by email and a standard Papermerge JWT is issued.

If no tenant id is set, the legacy generic OIDC HTTP client is still used (returning the third-party access token directly).

## Added Settings

Environment variables (map to `Settings` fields):

| Environment Variable | Purpose | Required for MSAL path |
|----------------------|---------|------------------------|
| `PAPERMERGE__AUTH__OIDC_CLIENT_ID` | Entra ID app (client) id | yes |
| `PAPERMERGE__AUTH__OIDC_CLIENT_SECRET` | Client secret (web app) | yes |
| `PAPERMERGE__AUTH__OIDC_TENANT_ID` | Directory (tenant) id | yes |
| `PAPERMERGE__AUTH__OIDC_REDIRECT_URL` | Redirect URI matching app registration | yes |
| `PAPERMERGE__AUTH__OIDC_SCOPE` | Space-separated scopes (default includes `openid profile email offline_access`) | optional |
| `PAPERMERGE__AUTH__OIDC_AUTHORITY` | Override authority (defaults to `https://login.microsoftonline.com/{tenant}`) | optional |

Legacy generic OIDC (non-MSAL) still uses:
`PAPERMERGE__AUTH__OIDC_ACCESS_TOKEN_URL`, `PAPERMERGE__AUTH__OIDC_USER_INFO_URL`, (optional) `PAPERMERGE__AUTH__OIDC_INTROSPECT_URL`.

## Frontend Redirect URL

Register the redirect URI in Azure App Registration (Web platform) matching the value of `PAPERMERGE__AUTH__OIDC_REDIRECT_URL` used by the frontend when initiating the flow.

Example authorize URL template (frontend):

```text
https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize?client_id=${CLIENT_ID}&response_type=code&redirect_uri=${ENCODED_REDIRECT}&response_mode=query&scope=openid%20profile%20email%20offline_access&state=${STATE}
```

## How the Backend Decides the Flow

- If `tenant_id` is present -> MSAL branch (returns a local `schema.User` to the caller; the `/token` endpoint will issue a Papermerge JWT)
- Else -> generic OIDC HTTP flow (returns a provider access token directly)

## Token Verification Behavior

If you keep setting `PAPERMERGE__AUTH__OIDC_INTROSPECT_URL`, `/verify` will attempt remote introspection first. For MSAL (local JWT issuance) you typically do NOT need introspection, so omit the introspect URL to rely on local JWT verification.

## Installation

Add dependency (already added in `pyproject.toml`):

```toml
msal = "^1.30.0"
```

Install with Poetry:

```bash
poetry install
```

Or with pip (if managing environment manually):

```bash
pip install msal
```

## Minimal Backend Environment Example

```env
PAPERMERGE__AUTH__OIDC_CLIENT_ID=00000000-0000-0000-0000-000000000000
PAPERMERGE__AUTH__OIDC_CLIENT_SECRET=your-secret
PAPERMERGE__AUTH__OIDC_TENANT_ID=11111111-1111-1111-1111-111111111111
PAPERMERGE__AUTH__OIDC_REDIRECT_URL=https://localhost:4010/oidc/callback
PAPERMERGE__AUTH__OIDC_SCOPE=openid profile email offline_access
```
(Do not set the access token / userinfo URLs in MSAL mode.)

## Extending Claim Handling
If you need Graph API email fallback (e.g., cloud-only accounts without `email` claim) you can request `User.Read` scope and call `/v1.0/me` after acquiring tokens. This is not yet implemented; add it inside the MSAL branch after `result` is returned when `email` is still blank.

## Security Notes
- Ensure `state` & (optionally) PKCE are enforced in the frontend. Backend currently trusts MSAL library for signature validation.
- Consider adding `nonce` support (supply in authorize request; validate in returned `id_token_claims`).
- Limit scopes to only what you need; `offline_access` is optional unless you need refresh tokens client-side.

## Next Hardening Steps (Recommended)
1. Add PKCE (frontend code challenge + verifier; pass verifier to MSAL via `code_verifier`).
2. Enforce `nonce` (store in session; compare with `id_token_claims['nonce']`).
3. Cache / persist external `sub` in a dedicated column to guard against email changes.
4. Optional Graph profile load for robust email retrieval.

## Rollback
Remove `PAPERMERGE__AUTH__OIDC_TENANT_ID` (and optional authority) to revert to legacy generic OIDC HTTP flow.

---
Generated guidance for integrating MSAL on 2025-09-25.
