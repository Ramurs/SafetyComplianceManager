from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.audit import AuditCreate, AuditFindingResponse, AuditResponse
from src.services import audit_service

router = APIRouter(prefix="/audits", tags=["audits"])


@router.get("", response_model=list[AuditResponse])
async def list_audits(db: AsyncSession = Depends(get_db)):
    return await audit_service.list_audits(db)


@router.post("", response_model=AuditResponse, status_code=201)
async def create_audit(data: AuditCreate, db: AsyncSession = Depends(get_db)):
    return await audit_service.create_audit(db, data)


@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit(audit_id: str, db: AsyncSession = Depends(get_db)):
    audit = await audit_service.get_audit(db, audit_id)
    if not audit:
        raise HTTPException(404, "Audit not found")
    return audit


@router.get("/{audit_id}/findings", response_model=list[AuditFindingResponse])
async def get_audit_findings(audit_id: str, db: AsyncSession = Depends(get_db)):
    audit = await audit_service.get_audit(db, audit_id)
    if not audit:
        raise HTTPException(404, "Audit not found")
    return audit.findings
