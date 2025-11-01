async def oidc_auth(
    session: Session, client_id: str, code: str, redirect_url: str
) -> str | None:
    if settings.papermerge__auth__oidc_client_secret is None:
        raise HTTPException(status_code=400, detail="OIDC client secret is empty")

    client = OIDCAuth(
        client_secret=settings.papermerge__auth__oidc_client_secret,
        access_token_url=settings.papermerge__auth__oidc_access_token_url,
        user_info_url=settings.papermerge__auth__oidc_user_info_url,
        client_id=client_id,
        code=code,
        redirect_url=redirect_url,
        scope=settings.papermerge__auth__oidc_scope,
        tenant_id=settings.papermerge__auth__oidc_tenant_id,
    )

    logger.debug("Auth:oidc: sign in")

    try:
        result = await client.signin()
    except Exception as ex:
        logger.warning(f"Auth:oidc: sign in failed with {ex}")

        raise HTTPException(
            status_code=401, detail=f"401 Unauthorized. Auth provider error: {ex}."
        )

    return result
