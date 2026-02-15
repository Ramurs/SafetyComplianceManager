from __future__ import annotations

from pydantic import BaseModel


class AgentExecuteRequest(BaseModel):
    instruction: str


class AgentExecuteResponse(BaseModel):
    task_id: str
    status: str
    result: str
    iterations: int
    tokens_used: int
