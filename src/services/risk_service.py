from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.risk import Risk, RiskMitigation
from src.schemas.risk import RiskCreate, RiskMitigationCreate, RiskUpdateScore


async def create_risk(db: AsyncSession, data: RiskCreate) -> Risk:
    risk = Risk(
        title=data.title,
        description=data.description,
        category=data.category,
        likelihood=data.likelihood,
        impact=data.impact,
        score=data.likelihood * data.impact,
        owner=data.owner,
    )
    db.add(risk)
    await db.commit()
    return await get_risk(db, risk.id)


async def list_risks(db: AsyncSession) -> list[Risk]:
    result = await db.execute(
        select(Risk).options(selectinload(Risk.mitigations)).order_by(Risk.score.desc())
    )
    return list(result.scalars().all())


async def get_risk(db: AsyncSession, risk_id: str) -> Risk | None:
    result = await db.execute(
        select(Risk).options(selectinload(Risk.mitigations)).where(Risk.id == risk_id)
    )
    return result.scalar_one_or_none()


async def update_risk_score(db: AsyncSession, risk_id: str, data: RiskUpdateScore) -> Risk | None:
    risk = await get_risk(db, risk_id)
    if not risk:
        return None
    risk.likelihood = data.likelihood
    risk.impact = data.impact
    risk.score = data.likelihood * data.impact
    if data.status:
        risk.status = data.status
    await db.commit()
    return await get_risk(db, risk_id)


async def add_mitigation(db: AsyncSession, risk_id: str, data: RiskMitigationCreate) -> RiskMitigation:
    mitigation = RiskMitigation(
        risk_id=risk_id,
        action=data.action,
        assigned_to=data.assigned_to,
        due_date=data.due_date,
    )
    db.add(mitigation)
    await db.commit()
    await db.refresh(mitigation)
    return mitigation


async def get_risk_matrix(db: AsyncSession) -> list[list[list[Risk]]]:
    """Return 5x5 matrix [impact][likelihood] with lists of risks."""
    risks = await list_risks(db)
    matrix: list[list[list[Risk]]] = [[[] for _ in range(5)] for _ in range(5)]
    for risk in risks:
        li = max(0, min(4, risk.likelihood - 1))
        im = max(0, min(4, risk.impact - 1))
        matrix[im][li].append(risk)
    return matrix
