from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.report import Report
from src.schemas.report import ReportCreate


async def create_report(db: AsyncSession, data: ReportCreate, file_path: str) -> Report:
    report = Report(
        title=data.title or f"{data.report_type.title()} Report",
        report_type=data.report_type,
        format=data.format,
        file_path=file_path,
        source_id=data.source_id,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def list_reports(db: AsyncSession) -> list[Report]:
    result = await db.execute(select(Report).order_by(Report.created_at.desc()))
    return list(result.scalars().all())


async def get_report(db: AsyncSession, report_id: str) -> Report | None:
    result = await db.execute(select(Report).where(Report.id == report_id))
    return result.scalar_one_or_none()
