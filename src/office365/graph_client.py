from __future__ import annotations

import logging
from typing import Any

import httpx

from src.office365.auth import get_access_token

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


async def graph_request(
    method: str,
    endpoint: str,
    json_data: dict | None = None,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    content_type: str | None = None,
) -> dict[str, Any]:
    """Make an authenticated request to Microsoft Graph API."""
    token = get_access_token()
    req_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type or "application/json",
    }
    if headers:
        req_headers.update(headers)

    url = f"{GRAPH_BASE}{endpoint}"

    async with httpx.AsyncClient() as client:
        if method.upper() == "GET":
            resp = await client.get(url, headers=req_headers)
        elif method.upper() == "POST":
            if data:
                resp = await client.post(url, headers=req_headers, content=data)
            else:
                resp = await client.post(url, headers=req_headers, json=json_data)
        elif method.upper() == "PUT":
            if data:
                resp = await client.put(url, headers=req_headers, content=data)
            else:
                resp = await client.put(url, headers=req_headers, json=json_data)
        elif method.upper() == "PATCH":
            resp = await client.patch(url, headers=req_headers, json=json_data)
        elif method.upper() == "DELETE":
            resp = await client.delete(url, headers=req_headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        resp.raise_for_status()
        if resp.status_code == 204:
            return {}
        return resp.json()
