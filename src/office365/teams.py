from __future__ import annotations

import logging

from src.office365.graph_client import graph_request

logger = logging.getLogger(__name__)


async def send_channel_message(
    team_id: str,
    channel_id: str,
    content: str,
    content_type: str = "html",
) -> dict:
    """Send a message to a Teams channel."""
    result = await graph_request(
        "POST",
        f"/teams/{team_id}/channels/{channel_id}/messages",
        json_data={
            "body": {"contentType": content_type, "content": content}
        },
    )
    logger.info(f"Message sent to Teams channel {channel_id}")
    return result


async def send_chat_message(
    chat_id: str,
    content: str,
    content_type: str = "html",
) -> dict:
    """Send a message to a Teams chat."""
    result = await graph_request(
        "POST",
        f"/chats/{chat_id}/messages",
        json_data={
            "body": {"contentType": content_type, "content": content}
        },
    )
    return result


async def list_teams() -> list[dict]:
    """List teams the app has access to."""
    result = await graph_request("GET", "/me/joinedTeams")
    return result.get("value", [])


async def list_channels(team_id: str) -> list[dict]:
    """List channels in a team."""
    result = await graph_request("GET", f"/teams/{team_id}/channels")
    return result.get("value", [])
