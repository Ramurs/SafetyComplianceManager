from __future__ import annotations

import datetime
import uuid

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    report_type: Mapped[str] = mapped_column(String(50))  # audit, risk, compliance, executive
    format: Mapped[str] = mapped_column(String(10))  # docx, xlsx, pptx
    file_path: Mapped[str] = mapped_column(String(500), default="")
    source_id: Mapped[str] = mapped_column(String(36), default="")  # audit_id, etc.
    status: Mapped[str] = mapped_column(String(20), default="generated")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
