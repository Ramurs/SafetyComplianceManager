from __future__ import annotations

import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    framework_id: Mapped[str] = mapped_column(ForeignKey("compliance_frameworks.id"))
    scope: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, in_progress, completed
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)

    findings: Mapped[list[AuditFinding]] = relationship(back_populates="audit", cascade="all, delete-orphan")


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    audit_id: Mapped[str] = mapped_column(ForeignKey("audits.id"))
    control_id: Mapped[str] = mapped_column(String(50), default="")
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(String(20), default="medium")  # critical, high, medium, low, info
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, remediated, accepted
    recommendation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    audit: Mapped[Audit] = relationship(back_populates="findings")
