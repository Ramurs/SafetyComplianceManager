from __future__ import annotations

import logging

import msal

from src.config import get_settings

logger = logging.getLogger(__name__)

_token_cache = msal.SerializableTokenCache()


def get_confidential_client() -> msal.ConfidentialClientApplication:
    settings = get_settings()
    return msal.ConfidentialClientApplication(
        client_id=settings.azure_client_id,
        client_credential=settings.azure_client_secret,
        authority=f"https://login.microsoftonline.com/{settings.azure_tenant_id}",
        token_cache=_token_cache,
    )


def get_access_token(scopes: list[str] | None = None) -> str:
    """Acquire token for Microsoft Graph API."""
    if scopes is None:
        scopes = ["https://graph.microsoft.com/.default"]

    client = get_confidential_client()
    result = client.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        return result["access_token"]

    error = result.get("error_description", result.get("error", "Unknown error"))
    raise RuntimeError(f"Failed to acquire token: {error}")
