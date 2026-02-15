from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.risk import RiskCreate, RiskResponse, RiskUpdateScore
from src.services import risk_service

router = APIRouter(prefix="/risks", tags=["risks"])


@router.get("", response_model=list[RiskResponse])
async def list_risks(db: AsyncSession = Depends(get_db)):
    return await risk_service.list_risks(db)


@router.post("", response_model=RiskResponse, status_code=201)
async def create_risk(data: RiskCreate, db: AsyncSession = Depends(get_db)):
    return await risk_service.create_risk(db, data)


@router.get("/matrix")
async def get_risk_matrix(db: AsyncSession = Depends(get_db)):
    matrix = await risk_service.get_risk_matrix(db)
    result = []
    for impact_row in matrix:
        row = []
        for cell in impact_row:
            row.append([{"id": r.id, "title": r.title, "score": r.score} for r in cell])
        result.append(row)
    return {"matrix": result}


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(risk_id: str, db: AsyncSession = Depends(get_db)):
    risk = await risk_service.get_risk(db, risk_id)
    if not risk:
        raise HTTPException(404, "Risk not found")
    return risk


@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(risk_id: str, data: RiskUpdateScore, db: AsyncSession = Depends(get_db)):
    risk = await risk_service.update_risk_score(db, risk_id, data)
    if not risk:
        raise HTTPException(404, "Risk not found")
    return risk
