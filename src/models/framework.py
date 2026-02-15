from __future__ import annotations

import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ComplianceFrameworkModel(Base):
    __tablename__ = "compliance_frameworks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), unique=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    controls: Mapped[list[FrameworkControl]] = relationship(back_populates="framework", cascade="all, delete-orphan")


class FrameworkControl(Base):
    __tablename__ = "framework_controls"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    framework_id: Mapped[str] = mapped_column(ForeignKey("compliance_frameworks.id"))
    control_id: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    framework: Mapped[ComplianceFrameworkModel] = relationship(back_populates="controls")
