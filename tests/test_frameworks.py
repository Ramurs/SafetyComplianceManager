from __future__ import annotations

from pathlib import Path

import pytest

from src.services.framework_service import import_framework, list_frameworks, get_framework_by_name


FIXTURES_DIR = Path(__file__).parent.parent / "data" / "frameworks"


@pytest.mark.asyncio
async def test_import_gdpr(db_session):
    gdpr_path = FIXTURES_DIR / "gdpr.yaml"
    if not gdpr_path.exists():
        pytest.skip("GDPR YAML not found")

    fw = await import_framework(db_session, gdpr_path)
    assert fw.name == "GDPR"
    assert len(fw.controls) > 0

    # Import again should return existing
    fw2 = await import_framework(db_session, gdpr_path)
    assert fw2.id == fw.id


@pytest.mark.asyncio
async def test_list_frameworks(db_session):
    gdpr_path = FIXTURES_DIR / "gdpr.yaml"
    if not gdpr_path.exists():
        pytest.skip("GDPR YAML not found")

    await import_framework(db_session, gdpr_path)
    frameworks = await list_frameworks(db_session)
    assert len(frameworks) >= 1
    assert any(f.name == "GDPR" for f in frameworks)


@pytest.mark.asyncio
async def test_get_framework_by_name(db_session):
    gdpr_path = FIXTURES_DIR / "gdpr.yaml"
    if not gdpr_path.exists():
        pytest.skip("GDPR YAML not found")

    await import_framework(db_session, gdpr_path)
    fw = await get_framework_by_name(db_session, "GDPR")
    assert fw is not None
    assert fw.name == "GDPR"

    missing = await get_framework_by_name(db_session, "NonExistent")
    assert missing is None
