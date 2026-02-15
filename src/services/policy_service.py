from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.policy import Policy, PolicyDistribution, PolicyVersion
from src.schemas.policy import PolicyCreate


async def create_policy(db: AsyncSession, data: PolicyCreate, content: str = "") -> Policy:
    policy = Policy(
        title=data.title,
        framework_id=data.framework_id,
        category=data.category,
    )
    db.add(policy)
    await db.flush()

    version = PolicyVersion(
        policy_id=policy.id,
        version_number=1,
        content=content,
        change_summary="Initial draft",
    )
    db.add(version)
    await db.commit()
    return await get_policy(db, policy.id)


async def list_policies(db: AsyncSession) -> list[Policy]:
    result = await db.execute(
        select(Policy)
        .options(selectinload(Policy.versions), selectinload(Policy.distributions))
        .order_by(Policy.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_policy(db: AsyncSession, policy_id: str) -> Policy | None:
    result = await db.execute(
        select(Policy)
        .options(selectinload(Policy.versions), selectinload(Policy.distributions))
        .where(Policy.id == policy_id)
    )
    return result.scalar_one_or_none()


async def approve_policy(db: AsyncSession, policy_id: str) -> Policy | None:
    policy = await get_policy(db, policy_id)
    if not policy:
        return None
    policy.status = "approved"
    await db.commit()
    return await get_policy(db, policy_id)


async def add_version(db: AsyncSession, policy_id: str, content: str, summary: str) -> PolicyVersion:
    policy = await get_policy(db, policy_id)
    if not policy:
        raise ValueError(f"Policy {policy_id} not found")
    new_version = policy.current_version + 1
    policy.current_version = new_version
    version = PolicyVersion(
        policy_id=policy_id,
        version_number=new_version,
        content=content,
        change_summary=summary,
    )
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return version


async def distribute_policy(
    db: AsyncSession, policy_id: str, channel: str, recipients: list[str]
) -> list[PolicyDistribution]:
    distributions = []
    for recipient in recipients:
        dist = PolicyDistribution(
            policy_id=policy_id,
            channel=channel,
            recipient=recipient,
        )
        db.add(dist)
        distributions.append(dist)
    await db.commit()
    return distributions
