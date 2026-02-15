from __future__ import annotations

import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.audit import Audit, AuditFinding
from src.schemas.audit import AuditCreate


async def create_audit(db: AsyncSession, data: AuditCreate) -> Audit:
    audit = Audit(
        title=data.title or "Compliance Audit",
        framework_id=data.framework_id,
        scope=data.scope,
        status="pending",
    )
    db.add(audit)
    await db.commit()
    return await get_audit(db, audit.id)


async def list_audits(db: AsyncSession) -> list[Audit]:
    result = await db.execute(
        select(Audit).options(selectinload(Audit.findings)).order_by(Audit.created_at.desc())
    )
    return list(result.scalars().all())


async def get_audit(db: AsyncSession, audit_id: str) -> Audit | None:
    result = await db.execute(
        select(Audit)
        .options(selectinload(Audit.findings))
        .where(Audit.id == audit_id)
    )
    return result.scalar_one_or_none()


async def add_finding(
    db: AsyncSession,
    audit_id: str,
    control_id: str,
    title: str,
    description: str,
    severity: str,
    recommendation: str,
) -> AuditFinding:
    finding = AuditFinding(
        audit_id=audit_id,
        control_id=control_id,
        title=title,
        description=description,
        severity=severity,
        recommendation=recommendation,
    )
    db.add(finding)
    await db.commit()
    await db.refresh(finding)
    return finding


async def complete_audit(db: AsyncSession, audit_id: str, summary: str) -> Audit | None:
    audit = await get_audit(db, audit_id)
    if not audit:
        return None
    audit.status = "completed"
    audit.summary = summary
    audit.completed_at = datetime.datetime.now(datetime.UTC)
    await db.commit()
    return await get_audit(db, audit_id)
