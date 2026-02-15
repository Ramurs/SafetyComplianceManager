from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RiskCreate(BaseModel):
    title: str
    description: str = ""
    category: str = ""
    likelihood: int = Field(1, ge=1, le=5)
    impact: int = Field(1, ge=1, le=5)
    owner: str = ""


class RiskUpdateScore(BaseModel):
    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    status: str | None = None


class RiskMitigationCreate(BaseModel):
    action: str
    assigned_to: str = ""
    due_date: datetime | None = None


class RiskMitigationResponse(BaseModel):
    id: str
    action: str
    status: str
    assigned_to: str
    due_date: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RiskResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    likelihood: int
    impact: int
    score: int
    status: str
    owner: str
    created_at: datetime
    updated_at: datetime
    mitigations: list[RiskMitigationResponse] = []

    model_config = {"from_attributes": True}
