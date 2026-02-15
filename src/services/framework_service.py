from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.framework import ComplianceFrameworkModel, FrameworkControl


async def list_frameworks(db: AsyncSession) -> list[ComplianceFrameworkModel]:
    result = await db.execute(
        select(ComplianceFrameworkModel).order_by(ComplianceFrameworkModel.name)
    )
    return list(result.scalars().all())


async def get_framework(db: AsyncSession, framework_id: str) -> ComplianceFrameworkModel | None:
    result = await db.execute(
        select(ComplianceFrameworkModel)
        .options(selectinload(ComplianceFrameworkModel.controls))
        .where(ComplianceFrameworkModel.id == framework_id)
    )
    return result.scalar_one_or_none()


async def get_framework_by_name(db: AsyncSession, name: str) -> ComplianceFrameworkModel | None:
    result = await db.execute(
        select(ComplianceFrameworkModel)
        .options(selectinload(ComplianceFrameworkModel.controls))
        .where(ComplianceFrameworkModel.name == name)
    )
    return result.scalar_one_or_none()


async def import_framework(db: AsyncSession, yaml_path: Path) -> ComplianceFrameworkModel:
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    existing = await get_framework_by_name(db, data["name"])
    if existing:
        return existing

    framework = ComplianceFrameworkModel(
        name=data["name"],
        version=data.get("version", "1.0"),
        description=data.get("description", ""),
    )
    db.add(framework)
    await db.flush()

    for ctrl in data.get("controls", []):
        control = FrameworkControl(
            framework_id=framework.id,
            control_id=ctrl["id"],
            title=ctrl["title"],
            description=ctrl.get("description", ""),
            category=ctrl.get("category", ""),
        )
        db.add(control)

    await db.commit()
    return await get_framework(db, framework.id)


async def import_all_frameworks(db: AsyncSession, frameworks_dir: Path) -> list[ComplianceFrameworkModel]:
    imported = []
    for yaml_file in sorted(frameworks_dir.glob("*.yaml")):
        fw = await import_framework(db, yaml_file)
        imported.append(fw)
    return imported
