from __future__ import annotations

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.audit import AuditCreate
from src.schemas.policy import PolicyCreate
from src.schemas.risk import RiskCreate
from src.services import audit_service, framework_service, policy_service, risk_service


TOOL_DEFINITIONS = [
    {
        "name": "query_frameworks",
        "description": "List all available compliance frameworks and their controls",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Optional framework name to filter by"
                }
            },
            "required": []
        }
    },
    {
        "name": "query_framework_controls",
        "description": "Get controls for a specific compliance framework",
        "input_schema": {
            "type": "object",
            "properties": {
                "framework_name": {
                    "type": "string",
                    "description": "Name of the framework (e.g. GDPR, ISO 27001, SOC 2)"
                }
            },
            "required": ["framework_name"]
        }
    },
    {
        "name": "create_audit",
        "description": "Create a new compliance audit",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Audit title"},
                "framework_id": {"type": "string", "description": "Framework ID to audit against"},
                "scope": {"type": "string", "description": "Audit scope description"}
            },
            "required": ["framework_id"]
        }
    },
    {
        "name": "create_audit_finding",
        "description": "Record a finding from an audit",
        "input_schema": {
            "type": "object",
            "properties": {
                "audit_id": {"type": "string"},
                "control_id": {"type": "string", "description": "Framework control ID"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "severity": {"type": "string", "enum": ["critical", "high", "medium", "low", "info"]},
                "recommendation": {"type": "string"}
            },
            "required": ["audit_id", "title", "severity"]
        }
    },
    {
        "name": "complete_audit",
        "description": "Mark an audit as completed with a summary",
        "input_schema": {
            "type": "object",
            "properties": {
                "audit_id": {"type": "string"},
                "summary": {"type": "string", "description": "Audit summary and conclusions"}
            },
            "required": ["audit_id", "summary"]
        }
    },
    {
        "name": "query_audits",
        "description": "List existing audits",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "assess_risk",
        "description": "Create a new risk assessment entry",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "category": {"type": "string"},
                "likelihood": {"type": "integer", "minimum": 1, "maximum": 5},
                "impact": {"type": "integer", "minimum": 1, "maximum": 5},
                "owner": {"type": "string"}
            },
            "required": ["title", "likelihood", "impact"]
        }
    },
    {
        "name": "query_risks",
        "description": "List existing risks",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_policy_draft",
        "description": "Create a new policy with content",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "framework_id": {"type": "string", "description": "Optional framework ID"},
                "category": {"type": "string"},
                "content": {"type": "string", "description": "Full policy content text"}
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "query_policies",
        "description": "List existing policies",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "generate_document",
        "description": "Generate a Word/Excel/PowerPoint document",
        "input_schema": {
            "type": "object",
            "properties": {
                "doc_type": {"type": "string", "enum": ["audit_report", "risk_register", "policy_document", "executive_summary"]},
                "format": {"type": "string", "enum": ["docx", "xlsx", "pptx"]},
                "source_id": {"type": "string", "description": "ID of audit/risk/policy to generate from"},
                "title": {"type": "string"}
            },
            "required": ["doc_type", "format"]
        }
    },
]


async def execute_tool(db: AsyncSession, name: str, args: dict[str, Any]) -> str:
    """Execute a tool and return a JSON result string."""
    try:
        if name == "query_frameworks":
            if args.get("name"):
                fw = await framework_service.get_framework_by_name(db, args["name"])
                if fw:
                    controls = [{"id": c.control_id, "title": c.title, "category": c.category} for c in fw.controls]
                    return json.dumps({"name": fw.name, "version": fw.version, "id": fw.id, "controls": controls})
                return json.dumps({"error": f"Framework '{args['name']}' not found"})
            frameworks = await framework_service.list_frameworks(db)
            return json.dumps([{"name": f.name, "version": f.version, "id": f.id} for f in frameworks])

        elif name == "query_framework_controls":
            fw = await framework_service.get_framework_by_name(db, args["framework_name"])
            if not fw:
                return json.dumps({"error": f"Framework '{args['framework_name']}' not found"})
            controls = [{"id": c.control_id, "title": c.title, "description": c.description, "category": c.category} for c in fw.controls]
            return json.dumps({"framework": fw.name, "controls": controls})

        elif name == "create_audit":
            audit = await audit_service.create_audit(db, AuditCreate(
                title=args.get("title", ""),
                framework_id=args["framework_id"],
                scope=args.get("scope", ""),
            ))
            return json.dumps({"id": audit.id, "title": audit.title, "status": audit.status})

        elif name == "create_audit_finding":
            finding = await audit_service.add_finding(
                db,
                audit_id=args["audit_id"],
                control_id=args.get("control_id", ""),
                title=args["title"],
                description=args.get("description", ""),
                severity=args["severity"],
                recommendation=args.get("recommendation", ""),
            )
            return json.dumps({"id": finding.id, "title": finding.title, "severity": finding.severity})

        elif name == "complete_audit":
            audit = await audit_service.complete_audit(db, args["audit_id"], args["summary"])
            if not audit:
                return json.dumps({"error": "Audit not found"})
            return json.dumps({"id": audit.id, "status": audit.status})

        elif name == "query_audits":
            audits = await audit_service.list_audits(db)
            return json.dumps([{"id": a.id, "title": a.title, "status": a.status} for a in audits])

        elif name == "assess_risk":
            risk = await risk_service.create_risk(db, RiskCreate(
                title=args["title"],
                description=args.get("description", ""),
                category=args.get("category", ""),
                likelihood=args["likelihood"],
                impact=args["impact"],
                owner=args.get("owner", ""),
            ))
            return json.dumps({"id": risk.id, "title": risk.title, "score": risk.score})

        elif name == "query_risks":
            risks = await risk_service.list_risks(db)
            return json.dumps([{"id": r.id, "title": r.title, "score": r.score, "status": r.status} for r in risks])

        elif name == "create_policy_draft":
            policy = await policy_service.create_policy(
                db,
                PolicyCreate(
                    title=args["title"],
                    framework_id=args.get("framework_id"),
                    category=args.get("category", ""),
                ),
                content=args["content"],
            )
            return json.dumps({"id": policy.id, "title": policy.title, "status": policy.status})

        elif name == "query_policies":
            policies = await policy_service.list_policies(db)
            return json.dumps([{"id": p.id, "title": p.title, "status": p.status} for p in policies])

        elif name == "generate_document":
            from src.office365.word import generate_audit_report, generate_policy_document
            from src.office365.excel import generate_risk_register, generate_audit_excel
            from src.office365.powerpoint import generate_executive_summary
            from src.services.report_service import create_report
            from src.schemas.report import ReportCreate

            doc_type = args["doc_type"]
            fmt = args["format"]
            source_id = args.get("source_id", "")
            title = args.get("title", f"{doc_type} document")

            path = None
            if doc_type == "audit_report" and fmt == "docx" and source_id:
                audit = await audit_service.get_audit(db, source_id)
                if audit:
                    path = generate_audit_report(audit)
            elif doc_type == "audit_report" and fmt == "xlsx" and source_id:
                audit = await audit_service.get_audit(db, source_id)
                if audit:
                    path = generate_audit_excel(audit)
            elif doc_type == "risk_register" and fmt == "xlsx":
                risks = await risk_service.list_risks(db)
                path = generate_risk_register(risks)
            elif doc_type == "policy_document" and fmt == "docx" and source_id:
                policy = await policy_service.get_policy(db, source_id)
                if policy:
                    path = generate_policy_document(policy)
            elif doc_type == "executive_summary" and fmt == "pptx":
                audits = await audit_service.list_audits(db)
                risks = await risk_service.list_risks(db)
                path = generate_executive_summary(audits, risks)

            if path:
                report = await create_report(db, ReportCreate(
                    title=title, report_type=doc_type, format=fmt, source_id=source_id
                ), str(path))
                return json.dumps({"id": report.id, "file_path": str(path)})
            return json.dumps({"error": f"Could not generate {doc_type} in {fmt} format"})

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})
