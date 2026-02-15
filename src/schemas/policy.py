from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PolicyCreate(BaseModel):
    title: str
    framework_id: str | None = None
    category: str = ""


class PolicyDistributeRequest(BaseModel):
    channel: str  # email, teams, sharepoint
    recipients: list[str]


class PolicyVersionResponse(BaseModel):
    id: str
    version_number: int
    content: str
    change_summary: str
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PolicyResponse(BaseModel):
    id: str
    title: str
    framework_id: str | None = None
    category: str
    status: str
    current_version: int
    created_at: datetime
    updated_at: datetime
    versions: list[PolicyVersionResponse] = []

    model_config = {"from_attributes": True}
