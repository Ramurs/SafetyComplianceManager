# SafetyComplianceManager

AI-powered Safety & Compliance Management agent for Microsoft Office 365.

An autonomous agent that executes compliance tasks — audits, risk assessments, policy creation, and report generation — using the Claude API and integrating with the full Office 365 ecosystem.

## Features

- **AI-Powered Audits** — Run compliance audits against GDPR, ISO 27001, or SOC 2 frameworks. The AI agent analyzes controls, identifies gaps, and records findings with severity levels.
- **Risk Management** — AI-assisted risk identification and assessment with a 5×5 risk matrix (Likelihood × Impact). Track mitigations and risk owners.
- **Policy Management** — AI-generated policy drafts based on framework requirements. Version tracking with approval and distribution workflows.
- **Document Generation** — Export to Word (.docx), Excel (.xlsx), and PowerPoint (.pptx). Audit reports, risk registers, policy documents, and executive summaries.
- **Office 365 Integration** — Send reports via Outlook, upload to SharePoint, post notifications to Teams.
- **Dual Interface** — Full CLI (`scm`) and REST API (FastAPI).

## Quick Start

### Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/) for AI features
- Azure AD app registration for Office 365 integration (optional)

### Installation

```bash
git clone https://github.com/Ramurs/SafetyComplianceManager.git
cd SafetyComplianceManager
pip install -e ".[dev]"
```

### Configuration

```bash
scm config init          # Creates .env from .env.example
```

Edit `.env` and set your API keys:

```env
ANTHROPIC_API_KEY=sk-ant-...

# Optional — for Office 365 integration
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
```

Verify your configuration:

```bash
scm config test
```

## Usage

### CLI

```bash
# Compliance Frameworks
scm framework list                          # List available frameworks
scm framework show "GDPR"                   # Show framework controls

# Audits
scm audit run GDPR --scope "Customer data"  # Run AI-powered audit
scm audit list                              # List all audits
scm audit show <audit-id>                   # View audit findings
scm audit export <audit-id> -f docx         # Export to Word

# Risk Management
scm risk assess --category "Data breach"    # AI risk assessment
scm risk list                               # List risks by score
scm risk matrix                             # Display 5x5 risk matrix
scm risk update <risk-id> -l 3 -i 4         # Update risk scores

# Policies
scm policy create "Data Protection Policy" -f GDPR
scm policy list
scm policy approve <policy-id>
scm policy distribute <policy-id> -c email -t user@example.com

# Reports
scm report generate audit -f docx           # Generate Word report
scm report generate risk -f xlsx            # Generate Excel register
scm report list

# AI Assistant
scm ask "What are the key GDPR requirements?"
scm agent execute "Assess our data breach risks and create a mitigation plan"
```

### REST API

```bash
scm serve                    # Start at http://127.0.0.1:8000
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `GET/POST` | `/api/v1/frameworks` | List frameworks |
| `GET/POST` | `/api/v1/audits` | Manage audits |
| `GET` | `/api/v1/audits/{id}/findings` | Audit findings |
| `GET/POST` | `/api/v1/risks` | Manage risks |
| `GET` | `/api/v1/risks/matrix` | Risk matrix |
| `GET/POST` | `/api/v1/policies` | Manage policies |
| `POST` | `/api/v1/policies/{id}/approve` | Approve policy |
| `POST` | `/api/v1/policies/{id}/distribute` | Distribute policy |
| `GET/POST` | `/api/v1/reports` | Manage reports |
| `GET` | `/api/v1/reports/{id}/download` | Download report file |
| `POST` | `/api/v1/agent/execute` | Execute AI agent task |

Interactive API docs available at `http://127.0.0.1:8000/docs`.

## Compliance Frameworks

Three frameworks are included out of the box:

| Framework | Version | Controls |
|-----------|---------|----------|
| **GDPR** | 2016/679 | 20 controls across 8 categories |
| **ISO 27001** | 2022 | 20 controls across 4 categories |
| **SOC 2** | 2017 | 20 controls across 8 categories |

Add custom frameworks by creating YAML files in `data/frameworks/`:

```yaml
name: My Framework
version: "1.0"
description: Custom compliance framework
controls:
  - id: MF-1
    title: Access Control
    description: Implement access control measures
    category: Security
```

## Architecture

```
src/
├── main.py              # FastAPI app
├── config.py            # Settings from .env
├── database.py          # Async SQLAlchemy
├── models/              # ORM models
├── schemas/             # Pydantic schemas
├── api/v1/              # REST endpoints
├── services/            # Business logic
├── agent/               # AI agent (engine, tools, prompts)
├── frameworks/          # Framework base class + registry
├── office365/           # Graph API, Outlook, SharePoint, Teams, doc generators
└── cli/                 # Typer CLI commands
```

The AI agent uses Claude's tool-use API in an agentic loop. It has access to 11 tools for querying and modifying audits, risks, policies, frameworks, and documents. The loop runs up to 20 iterations with token budget tracking.

## Testing

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database and cover:
- Service layer (audits, risks, policies)
- REST API endpoints
- Framework YAML import

## License

MIT
