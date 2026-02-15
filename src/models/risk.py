from __future__ import annotations

import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Risk(Base):
    __tablename__ = "risks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="")
    likelihood: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    impact: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    score: Mapped[int] = mapped_column(Integer, default=1)  # likelihood * impact
    status: Mapped[str] = mapped_column(String(20), default="identified")  # identified, assessed, mitigated, accepted
    owner: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    mitigations: Mapped[list[RiskMitigation]] = relationship(back_populates="risk", cascade="all, delete-orphan")


class RiskMitigation(Base):
    __tablename__ = "risk_mitigations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    risk_id: Mapped[str] = mapped_column(ForeignKey("risks.id"))
    action: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="planned")  # planned, in_progress, completed
    assigned_to: Mapped[str] = mapped_column(String(100), default="")
    due_date: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    risk: Mapped[Risk] = relationship(back_populates="mitigations")
