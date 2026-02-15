from fastapi import APIRouter

from src.api.v1 import audits, frameworks, risks, policies, reports, agent

router = APIRouter(prefix="/api/v1")
router.include_router(frameworks.router)
router.include_router(audits.router)
router.include_router(risks.router)
router.include_router(policies.router)
router.include_router(reports.router)
router.include_router(agent.router)
