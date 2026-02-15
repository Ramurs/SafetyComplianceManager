from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.agent import AgentExecuteRequest, AgentExecuteResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/execute", response_model=AgentExecuteResponse)
async def execute_agent(data: AgentExecuteRequest, db: AsyncSession = Depends(get_db)):
    from src.agent.engine import run_agent
    result = await run_agent(db, data.instruction)
    return result
