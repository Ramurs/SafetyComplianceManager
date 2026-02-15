from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.report import ReportResponse
from src.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportResponse])
async def list_reports(db: AsyncSession = Depends(get_db)):
    return await report_service.list_reports(db)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await report_service.get_report(db, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    return report


@router.get("/{report_id}/download")
async def download_report(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await report_service.get_report(db, report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    path = Path(report.file_path)
    if not path.exists():
        raise HTTPException(404, "Report file not found on disk")
    media_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    return FileResponse(
        path=str(path),
        media_type=media_types.get(report.format, "application/octet-stream"),
        filename=path.name,
    )
