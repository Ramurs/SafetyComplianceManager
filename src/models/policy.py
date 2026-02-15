from __future__ import annotations

import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    framework_id: Mapped[str | None] = mapped_column(ForeignKey("compliance_frameworks.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, review, approved, published
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    versions: Mapped[list[PolicyVersion]] = relationship(back_populates="policy", cascade="all, delete-orphan")
    distributions: Mapped[list[PolicyDistribution]] = relationship(back_populates="policy", cascade="all, delete-orphan")


class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id: Mapped[str] = mapped_column(ForeignKey("policies.id"))
    version_number: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text, default="")
    change_summary: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[str] = mapped_column(String(100), default="system")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    policy: Mapped[Policy] = relationship(back_populates="versions")


class PolicyDistribution(Base):
    __tablename__ = "policy_distributions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id: Mapped[str] = mapped_column(ForeignKey("policies.id"))
    channel: Mapped[str] = mapped_column(String(20))  # email, teams, sharepoint
    recipient: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, sent, failed
    sent_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    policy: Mapped[Policy] = relationship(back_populates="distributions")
