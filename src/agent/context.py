from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.services import audit_service, framework_service, policy_service, risk_service


async def build_context(db: AsyncSession) -> str:
    """Build context string with current state for the agent."""
    parts = []

    frameworks = await framework_service.list_frameworks(db)
    if frameworks:
        parts.append("Available Compliance Frameworks:")
        for fw in frameworks:
            parts.append(f"  - {fw.name} (v{fw.version}, id={fw.id})")

    audits = await audit_service.list_audits(db)
    if audits:
        parts.append(f"\nRecent Audits ({len(audits)}):")
        for a in audits[:5]:
            parts.append(f"  - [{a.status}] {a.title} (id={a.id})")

    risks = await risk_service.list_risks(db)
    if risks:
        parts.append(f"\nCurrent Risks ({len(risks)}):")
        for r in risks[:5]:
            parts.append(f"  - [Score: {r.score}] {r.title} (id={r.id})")

    policies = await policy_service.list_policies(db)
    if policies:
        parts.append(f"\nPolicies ({len(policies)}):")
        for p in policies[:5]:
            parts.append(f"  - [{p.status}] {p.title} (id={p.id})")

    return "\n".join(parts) if parts else "No existing data."
