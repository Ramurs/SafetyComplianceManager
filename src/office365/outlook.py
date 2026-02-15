from __future__ import annotations

import base64
import logging
from pathlib import Path

from src.office365.graph_client import graph_request

logger = logging.getLogger(__name__)


async def send_email(
    to_addresses: list[str],
    subject: str,
    body: str,
    attachments: list[Path] | None = None,
    sender: str = "me",
) -> dict:
    """Send an email via Microsoft Graph API."""
    message = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": body},
        "toRecipients": [
            {"emailAddress": {"address": addr}} for addr in to_addresses
        ],
    }

    if attachments:
        message["attachments"] = []
        for path in attachments:
            with open(path, "rb") as f:
                content = base64.b64encode(f.read()).decode()
            message["attachments"].append({
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": path.name,
                "contentBytes": content,
            })

    result = await graph_request(
        "POST",
        f"/users/{sender}/sendMail",
        json_data={"message": message, "saveToSentItems": True},
    )
    logger.info(f"Email sent to {to_addresses}")
    return result
