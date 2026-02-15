from __future__ import annotations

import logging
from pathlib import Path

from src.office365.graph_client import graph_request

logger = logging.getLogger(__name__)


async def upload_file(
    file_path: str,
    site_name: str = "",
    folder: str = "General",
) -> str:
    """Upload a file to SharePoint via Microsoft Graph API."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "rb") as f:
        content = f.read()

    if site_name:
        endpoint = f"/sites/{site_name}/drive/root:/{folder}/{path.name}:/content"
    else:
        endpoint = f"/me/drive/root:/{folder}/{path.name}:/content"

    result = await graph_request(
        "PUT",
        endpoint,
        data=content,
        content_type="application/octet-stream",
    )

    url = result.get("webUrl", "")
    logger.info(f"Uploaded {path.name} to SharePoint: {url}")
    return url


async def download_file(
    site_name: str,
    file_path: str,
    local_path: str,
) -> str:
    """Download a file from SharePoint."""
    endpoint = f"/sites/{site_name}/drive/root:/{file_path}:/content"
    result = await graph_request("GET", endpoint)
    Path(local_path).write_bytes(result)
    return local_path


async def list_files(site_name: str, folder: str = "General") -> list[dict]:
    """List files in a SharePoint folder."""
    endpoint = f"/sites/{site_name}/drive/root:/{folder}:/children"
    result = await graph_request("GET", endpoint)
    return result.get("value", [])
