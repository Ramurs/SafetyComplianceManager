from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.policy import PolicyCreate, PolicyDistributeRequest, PolicyResponse
from src.services import policy_service

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("", response_model=list[PolicyResponse])
async def list_policies(db: AsyncSession = Depends(get_db)):
    return await policy_service.list_policies(db)


@router.post("", response_model=PolicyResponse, status_code=201)
async def create_policy(data: PolicyCreate, db: AsyncSession = Depends(get_db)):
    return await policy_service.create_policy(db, data)


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    policy = await policy_service.get_policy(db, policy_id)
    if not policy:
        raise HTTPException(404, "Policy not found")
    return policy


@router.post("/{policy_id}/approve", response_model=PolicyResponse)
async def approve_policy(policy_id: str, db: AsyncSession = Depends(get_db)):
    policy = await policy_service.approve_policy(db, policy_id)
    if not policy:
        raise HTTPException(404, "Policy not found")
    return policy


@router.post("/{policy_id}/distribute")
async def distribute_policy(
    policy_id: str,
    data: PolicyDistributeRequest,
    db: AsyncSession = Depends(get_db),
):
    distributions = await policy_service.distribute_policy(
        db, policy_id, data.channel, data.recipients
    )
    return {"distributed": len(distributions), "channel": data.channel}
