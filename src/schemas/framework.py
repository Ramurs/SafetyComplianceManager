from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FrameworkControlResponse(BaseModel):
    id: str
    control_id: str
    title: str
    description: str
    category: str

    model_config = {"from_attributes": True}


class FrameworkResponse(BaseModel):
    id: str
    name: str
    version: str
    description: str
    created_at: datetime
    controls: list[FrameworkControlResponse] = []

    model_config = {"from_attributes": True}
