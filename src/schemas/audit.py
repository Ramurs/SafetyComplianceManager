from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AuditCreate(BaseModel):
    title: str = ""
    framework_id: str
    scope: str = ""


class AuditFindingResponse(BaseModel):
    id: str
    control_id: str
    title: str
    description: str
    severity: str
    status: str
    recommendation: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditResponse(BaseModel):
    id: str
    title: str
    framework_id: str
    scope: str
    status: str
    summary: str
    created_at: datetime
    completed_at: datetime | None = None
    findings: list[AuditFindingResponse] = []

    model_config = {"from_attributes": True}
