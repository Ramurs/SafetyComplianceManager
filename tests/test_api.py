from __future__ import annotations

import pytest

from src.models.framework import ComplianceFrameworkModel


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_frameworks_empty(client):
    resp = await client.get("/api/v1/frameworks")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_risks_crud(client):
    # Create
    resp = await client.post("/api/v1/risks", json={
        "title": "Test Risk",
        "likelihood": 3,
        "impact": 4,
        "category": "Operational",
    })
    assert resp.status_code == 201
    risk = resp.json()
    assert risk["score"] == 12

    # List
    resp = await client.get("/api/v1/risks")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # Get
    resp = await client.get(f"/api/v1/risks/{risk['id']}")
    assert resp.status_code == 200

    # Update
    resp = await client.put(f"/api/v1/risks/{risk['id']}", json={
        "likelihood": 5,
        "impact": 5,
    })
    assert resp.status_code == 200
    assert resp.json()["score"] == 25

    # Matrix
    resp = await client.get("/api/v1/risks/matrix")
    assert resp.status_code == 200
    assert "matrix" in resp.json()


@pytest.mark.asyncio
async def test_audits_crud(client, db_session):
    # Create framework first
    fw = ComplianceFrameworkModel(name="TestFW", version="1.0", description="Test")
    db_session.add(fw)
    await db_session.commit()
    await db_session.refresh(fw)

    resp = await client.post("/api/v1/audits", json={
        "framework_id": fw.id,
        "scope": "Test scope",
    })
    assert resp.status_code == 201
    audit = resp.json()

    resp = await client.get("/api/v1/audits")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await client.get(f"/api/v1/audits/{audit['id']}/findings")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_policies_crud(client):
    resp = await client.post("/api/v1/policies", json={
        "title": "Test Policy",
        "category": "Security",
    })
    assert resp.status_code == 201
    policy = resp.json()

    resp = await client.get("/api/v1/policies")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await client.post(f"/api/v1/policies/{policy['id']}/approve")
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"


@pytest.mark.asyncio
async def test_not_found(client):
    resp = await client.get("/api/v1/risks/nonexistent")
    assert resp.status_code == 404

    resp = await client.get("/api/v1/audits/nonexistent")
    assert resp.status_code == 404

    resp = await client.get("/api/v1/policies/nonexistent")
    assert resp.status_code == 404
