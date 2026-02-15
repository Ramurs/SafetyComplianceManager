from __future__ import annotations

import datetime
import json
import logging

import anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.context import build_context
from src.agent.prompts import SYSTEM_PROMPT
from src.agent.tools import TOOL_DEFINITIONS, execute_tool
from src.config import get_settings
from src.models.agent_task import AgentTask

logger = logging.getLogger(__name__)


async def run_agent(db: AsyncSession, instruction: str) -> dict:
    """Run the AI agent loop with tool use."""
    settings = get_settings()

    if not settings.anthropic_api_key:
        return {
            "task_id": "",
            "status": "failed",
            "result": "Error: ANTHROPIC_API_KEY not configured. Run 'scm config init' and set your API key.",
            "iterations": 0,
            "tokens_used": 0,
        }

    # Create task record
    task = AgentTask(instruction=instruction, status="running")
    db.add(task)
    await db.commit()
    await db.refresh(task)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    context = await build_context(db)
    system = f"{SYSTEM_PROMPT}\n\nCurrent System State:\n{context}"

    messages = [{"role": "user", "content": instruction}]
    total_tokens = 0
    iterations = 0
    final_text = ""

    try:
        while iterations < settings.agent_max_iterations:
            iterations += 1
            logger.info(f"Agent iteration {iterations}")

            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=settings.agent_max_tokens,
                system=system,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            total_tokens += response.usage.input_tokens + response.usage.output_tokens

            # Collect text and tool use blocks
            tool_uses = []
            text_parts = []

            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            if text_parts:
                final_text = "\n".join(text_parts)

            # If no tool use, we're done
            if response.stop_reason == "end_turn" or not tool_uses:
                break

            # Execute tools and build response
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_use in tool_uses:
                logger.info(f"Executing tool: {tool_use.name}")
                result = await execute_tool(db, tool_use.name, tool_use.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})

        # Update task
        task.status = "completed"
        task.result = final_text
        task.iterations = iterations
        task.tokens_used = total_tokens
        task.completed_at = datetime.datetime.now(datetime.UTC)
        await db.commit()

        return {
            "task_id": task.id,
            "status": "completed",
            "result": final_text,
            "iterations": iterations,
            "tokens_used": total_tokens,
        }

    except Exception as e:
        logger.error(f"Agent error: {e}")
        task.status = "failed"
        task.error = str(e)
        task.iterations = iterations
        task.tokens_used = total_tokens
        task.completed_at = datetime.datetime.now(datetime.UTC)
        await db.commit()

        return {
            "task_id": task.id,
            "status": "failed",
            "result": f"Error: {e}",
            "iterations": iterations,
            "tokens_used": total_tokens,
        }
