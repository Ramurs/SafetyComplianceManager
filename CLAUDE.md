# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SafetyComplianceManager is an AI-powered Safety & Compliance Management agent for Microsoft Office 365. It acts as an autonomous agent that executes compliance tasks — audits, risk assessments, policy creation, and report generation — using the Claude API and integrating with the Office 365 ecosystem.

**Repository:** https://github.com/Ramurs/SafetyComplianceManager

## Stack

- **Python 3.12** with **FastAPI** (async REST API)
- **CLI:** Typer + Rich (command: `scm`)
- **AI:** Anthropic Python SDK with tool-use loop (Claude Sonnet)
- **Database:** SQLite via async SQLAlchemy + Alembic
- **Office:** python-docx, openpyxl, python-pptx (local generation) + Microsoft Graph API (Outlook, SharePoint, Teams)
- **Auth:** MSAL (client credentials flow)

## Project Structure

```
SafetyComplianceManager/
├── src/
│   ├── main.py                  # FastAPI app with lifespan
│   ├── config.py                # pydantic-settings (reads .env)
│   ├── database.py              # async SQLAlchemy engine + session
│   ├── models/                  # ORM models (audit, risk, policy, report, framework, agent_task)
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── api/v1/                  # REST endpoints (audits, risks, policies, reports, frameworks, agent)
│   ├── services/                # Business logic (audit_service, risk_service, policy_service, etc.)
│   ├── agent/
│   │   ├── engine.py            # Agent loop (Claude API + tool calls, max 20 iterations)
│   │   ├── tools.py             # 11 tool definitions + executor
│   │   ├── prompts.py           # System prompt for compliance expertise
│   │   └── context.py           # Builds current DB state context for agent
│   ├── frameworks/              # Abstract ComplianceFramework base + YAML loader + registry
│   ├── office365/               # Graph API client, Outlook, SharePoint, Teams, Word, Excel, PowerPoint
│   ├── cli/main.py              # All CLI commands (audit, risk, policy, report, framework, config, serve)
│   └── migrations/              # Alembic (async SQLite)
├── tests/                       # pytest-asyncio tests (services, API, frameworks)
├── data/
│   ├── templates/               # Document templates
│   └── frameworks/              # YAML control definitions (GDPR, ISO 27001, SOC 2)
├── pyproject.toml               # Package config with `scm` entry point
└── requirements.txt
```

## Build & Run Commands

```bash
# Install
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Start API server
scm serve                        # or: uvicorn src.main:app --reload

# CLI usage
scm config init                  # Create .env from .env.example
scm config test                  # Validate configuration
scm framework list               # Show GDPR, ISO 27001, SOC 2
scm framework show "GDPR"        # Show framework controls
scm audit run GDPR --scope "..." # AI-powered audit
scm risk assess --category "..." # AI risk assessment
scm risk matrix                  # Display 5x5 risk matrix
scm policy create "Title" -f GDPR
scm report generate audit -f docx
scm ask "question"               # AI Q&A
scm agent execute "instruction"  # Free-form AI task
```

## Key Architecture Patterns

- **All database queries use `selectinload`** for relationships to avoid lazy loading errors on async sessions. After create/update operations, re-fetch the object with eager loading rather than using `db.refresh()`.
- **Agent tool-use loop** (`src/agent/engine.py`): sends messages to Claude with tool definitions, executes tool calls against services, feeds results back, repeats until `end_turn` or max iterations (20).
- **Framework definitions** are YAML files in `data/frameworks/`. They are auto-imported into the database on app startup and on CLI commands.
- **Services layer** (`src/services/`) contains all business logic. API endpoints and CLI commands are thin wrappers around services.
- **Office 365 integration** requires Azure AD app registration. Set `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` in `.env`.

## Environment Variables

Required in `.env` (copy from `.env.example`):
- `ANTHROPIC_API_KEY` — required for AI agent features
- `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` — required for Office 365 integration
- `DATABASE_URL` — defaults to `sqlite+aiosqlite:///./data/scm.db`

## Testing

Tests use in-memory SQLite and override FastAPI's `get_db` dependency. Run with:
```bash
pytest tests/ -v
```

Test files:
- `tests/test_services.py` — service layer (audits, risks, policies)
- `tests/test_api.py` — REST API endpoints
- `tests/test_frameworks.py` — YAML framework import
