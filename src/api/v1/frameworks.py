from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.framework import FrameworkResponse
from src.services import framework_service

router = APIRouter(prefix="/frameworks", tags=["frameworks"])


@router.get("", response_model=list[FrameworkResponse])
async def list_frameworks(db: AsyncSession = Depends(get_db)):
    return await framework_service.list_frameworks(db)


@router.get("/{framework_id}", response_model=FrameworkResponse)
async def get_framework(framework_id: str, db: AsyncSession = Depends(get_db)):
    fw = await framework_service.get_framework(db, framework_id)
    if not fw:
        raise HTTPException(404, "Framework not found")
    return fw
