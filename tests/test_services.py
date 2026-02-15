from __future__ import annotations

import pytest

from src.schemas.audit import AuditCreate
from src.schemas.risk import RiskCreate, RiskUpdateScore
from src.schemas.policy import PolicyCreate
from src.services import audit_service, risk_service, policy_service


@pytest.mark.asyncio
async def test_create_and_list_audits(db_session):
    # Need a framework first
    from src.models.framework import ComplianceFrameworkModel
    fw = ComplianceFrameworkModel(name="Test Framework", version="1.0", description="Test")
    db_session.add(fw)
    await db_session.flush()

    audit = await audit_service.create_audit(
        db_session, AuditCreate(title="Test Audit", framework_id=fw.id, scope="Test scope")
    )
    assert audit.title == "Test Audit"
    assert audit.status == "pending"

    audits = await audit_service.list_audits(db_session)
    assert len(audits) == 1

    # Add finding
    finding = await audit_service.add_finding(
        db_session,
        audit_id=audit.id,
        control_id="TC-1",
        title="Test Finding",
        description="A test finding",
        severity="high",
        recommendation="Fix it",
    )
    assert finding.severity == "high"

    # Complete audit
    completed = await audit_service.complete_audit(db_session, audit.id, "Summary")
    assert completed.status == "completed"
    assert completed.summary == "Summary"


@pytest.mark.asyncio
async def test_create_and_score_risk(db_session):
    risk = await risk_service.create_risk(
        db_session, RiskCreate(title="Data Breach", likelihood=4, impact=5, category="Security")
    )
    assert risk.score == 20
    assert risk.category == "Security"

    updated = await risk_service.update_risk_score(
        db_session, risk.id, RiskUpdateScore(likelihood=2, impact=3)
    )
    assert updated.score == 6

    risks = await risk_service.list_risks(db_session)
    assert len(risks) == 1


@pytest.mark.asyncio
async def test_risk_matrix(db_session):
    await risk_service.create_risk(
        db_session, RiskCreate(title="R1", likelihood=1, impact=1)
    )
    await risk_service.create_risk(
        db_session, RiskCreate(title="R2", likelihood=5, impact=5)
    )
    matrix = await risk_service.get_risk_matrix(db_session)
    assert len(matrix) == 5
    assert len(matrix[0]) == 5
    # R1 at [0][0], R2 at [4][4]
    assert len(matrix[0][0]) == 1
    assert len(matrix[4][4]) == 1


@pytest.mark.asyncio
async def test_create_and_approve_policy(db_session):
    policy = await policy_service.create_policy(
        db_session,
        PolicyCreate(title="Test Policy", category="Security"),
        content="Policy content here",
    )
    assert policy.status == "draft"
    assert policy.current_version == 1

    approved = await policy_service.approve_policy(db_session, policy.id)
    assert approved.status == "approved"

    # Add version
    version = await policy_service.add_version(
        db_session, policy.id, "Updated content", "Minor update"
    )
    assert version.version_number == 2
