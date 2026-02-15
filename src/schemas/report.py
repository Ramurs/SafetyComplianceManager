from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReportCreate(BaseModel):
    title: str = ""
    report_type: str  # audit, risk, compliance, executive
    format: str = "docx"  # docx, xlsx, pptx
    source_id: str = ""


class ReportResponse(BaseModel):
    id: str
    title: str
    report_type: str
    format: str
    file_path: str
    source_id: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
