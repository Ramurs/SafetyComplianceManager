from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from src.config import get_settings

app = typer.Typer(name="scm", help="Safety Compliance Manager CLI")
console = Console()

# Sub-command groups
audit_app = typer.Typer(help="Audit management")
risk_app = typer.Typer(help="Risk management")
policy_app = typer.Typer(help="Policy management")
report_app = typer.Typer(help="Report generation")
framework_app = typer.Typer(help="Compliance frameworks")
config_app = typer.Typer(help="Configuration")

app.add_typer(audit_app, name="audit")
app.add_typer(risk_app, name="risk")
app.add_typer(policy_app, name="policy")
app.add_typer(report_app, name="report")
app.add_typer(framework_app, name="framework")
app.add_typer(config_app, name="config")


def _run(coro):
    return asyncio.run(coro)


async def _get_db():
    from src.database import async_session
    async with async_session() as session:
        return session


# ── Config ──────────────────────────────────────────────────────────

@config_app.command("init")
def config_init():
    """Initialize configuration by creating a .env file."""
    settings = get_settings()
    env_example = Path(settings.data_dir).parent / ".env.example"
    env_file = Path(settings.data_dir).parent / ".env"
    if env_file.exists():
        console.print("[yellow]⚠ .env already exists[/yellow]")
        return
    if env_example.exists():
        env_file.write_text(env_example.read_text())
        console.print("[green]✓ Created .env from .env.example[/green]")
    else:
        console.print("[red]✗ .env.example not found[/red]")


@config_app.command("test")
def config_test():
    """Test configuration and connections."""
    settings = get_settings()
    table = Table(title="Configuration Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Status", style="green")

    table.add_row("Anthropic API Key", "✓ Set" if settings.anthropic_api_key else "✗ Not set")
    table.add_row("Azure Tenant ID", "✓ Set" if settings.azure_tenant_id else "✗ Not set")
    table.add_row("Azure Client ID", "✓ Set" if settings.azure_client_id else "✗ Not set")
    table.add_row("Database URL", settings.database_url[:60])
    table.add_row("Environment", settings.app_env)
    console.print(table)


@config_app.command("show")
def config_show():
    """Show current configuration."""
    config_test()


# ── Framework ───────────────────────────────────────────────────────

@framework_app.command("list")
def framework_list():
    """List available compliance frameworks."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.framework_service import import_all_frameworks, list_frameworks
        settings = get_settings()
        await init_db()
        async with async_session() as db:
            await import_all_frameworks(db, settings.frameworks_dir)
            frameworks = await list_frameworks(db)
        return frameworks

    frameworks = _run(_run_it())
    if not frameworks:
        console.print("[yellow]No frameworks found. Add YAML files to data/frameworks/[/yellow]")
        return

    table = Table(title="Compliance Frameworks")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Name", style="cyan")
    table.add_column("Version")
    table.add_column("Description")
    for fw in frameworks:
        table.add_row(fw.id[:8], fw.name, fw.version, fw.description[:60])
    console.print(table)


@framework_app.command("show")
def framework_show(name: str = typer.Argument(..., help="Framework name")):
    """Show framework details and controls."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.framework_service import import_all_frameworks, get_framework_by_name
        settings = get_settings()
        await init_db()
        async with async_session() as db:
            await import_all_frameworks(db, settings.frameworks_dir)
            return await get_framework_by_name(db, name)

    fw = _run(_run_it())
    if not fw:
        console.print(f"[red]Framework '{name}' not found[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]{fw.name}[/bold cyan] v{fw.version}")
    console.print(f"{fw.description}\n")

    table = Table(title="Controls")
    table.add_column("Control ID", style="cyan")
    table.add_column("Title")
    table.add_column("Category", style="dim")
    for ctrl in fw.controls:
        table.add_row(ctrl.control_id, ctrl.title, ctrl.category)
    console.print(table)


@framework_app.command("import")
def framework_import(path: str = typer.Argument(..., help="Path to YAML file")):
    """Import a framework from a YAML file."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.framework_service import import_framework
        await init_db()
        async with async_session() as db:
            return await import_framework(db, Path(path))

    fw = _run(_run_it())
    console.print(f"[green]✓ Imported framework: {fw.name}[/green]")


# ── Audit ───────────────────────────────────────────────────────────

@audit_app.command("run")
def audit_run(
    framework: str = typer.Argument(..., help="Framework name (e.g. GDPR)"),
    scope: str = typer.Option("", "--scope", "-s", help="Audit scope"),
):
    """Run an AI-powered compliance audit."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.framework_service import import_all_frameworks, get_framework_by_name
        from src.agent.engine import run_agent
        settings = get_settings()
        await init_db()
        async with async_session() as db:
            await import_all_frameworks(db, settings.frameworks_dir)
            fw = await get_framework_by_name(db, framework)
            if not fw:
                return None, f"Framework '{framework}' not found"
            instruction = f"Run a compliance audit against the {fw.name} framework."
            if scope:
                instruction += f" Scope: {scope}"
            instruction += " Create the audit, analyze each control, record findings with severity levels, and complete the audit with a summary."
            result = await run_agent(db, instruction)
            return result, None

    with console.status("[bold green]Running audit..."):
        result, error = _run(_run_it())

    if error:
        console.print(f"[red]✗ {error}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[green]✓ Audit completed[/green]")
    console.print(f"Iterations: {result['iterations']}, Tokens: {result['tokens_used']}")
    console.print(f"\n{result['result']}")


@audit_app.command("list")
def audit_list():
    """List all audits."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.audit_service import list_audits
        await init_db()
        async with async_session() as db:
            return await list_audits(db)

    audits = _run(_run_it())
    if not audits:
        console.print("[yellow]No audits found[/yellow]")
        return

    table = Table(title="Audits")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Title", style="cyan")
    table.add_column("Status")
    table.add_column("Created")
    for a in audits:
        status_color = {"pending": "yellow", "in_progress": "blue", "completed": "green"}.get(a.status, "white")
        table.add_row(a.id[:8], a.title, f"[{status_color}]{a.status}[/{status_color}]", str(a.created_at)[:16])
    console.print(table)


@audit_app.command("show")
def audit_show(audit_id: str = typer.Argument(..., help="Audit ID")):
    """Show audit details and findings."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.audit_service import get_audit
        await init_db()
        async with async_session() as db:
            return await get_audit(db, audit_id)

    audit = _run(_run_it())
    if not audit:
        console.print(f"[red]Audit '{audit_id}' not found[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]{audit.title}[/bold cyan]")
    console.print(f"Status: {audit.status} | Scope: {audit.scope}")
    if audit.summary:
        console.print(f"\nSummary: {audit.summary}")

    if audit.findings:
        table = Table(title="Findings")
        table.add_column("Severity", style="bold")
        table.add_column("Control")
        table.add_column("Title")
        table.add_column("Status")
        for f in audit.findings:
            sev_colors = {"critical": "red", "high": "red", "medium": "yellow", "low": "green", "info": "dim"}
            color = sev_colors.get(f.severity, "white")
            table.add_row(f"[{color}]{f.severity}[/{color}]", f.control_id, f.title, f.status)
        console.print(table)


@audit_app.command("export")
def audit_export(
    audit_id: str = typer.Argument(..., help="Audit ID"),
    format: str = typer.Option("docx", "--format", "-f", help="Export format (docx, xlsx)"),
):
    """Export audit to a document."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.audit_service import get_audit
        from src.office365.word import generate_audit_report
        from src.office365.excel import generate_audit_excel
        from src.services.report_service import create_report
        from src.schemas.report import ReportCreate
        await init_db()
        async with async_session() as db:
            audit = await get_audit(db, audit_id)
            if not audit:
                return None
            if format == "xlsx":
                path = generate_audit_excel(audit)
            else:
                path = generate_audit_report(audit)
            report = await create_report(db, ReportCreate(
                title=f"{audit.title} Report",
                report_type="audit",
                format=format,
                source_id=audit.id,
            ), str(path))
            return report

    report = _run(_run_it())
    if not report:
        console.print(f"[red]Audit '{audit_id}' not found[/red]")
        raise typer.Exit(1)
    console.print(f"[green]✓ Exported to {report.file_path}[/green]")


# ── Risk ────────────────────────────────────────────────────────────

@risk_app.command("assess")
def risk_assess(
    category: str = typer.Option("", "--category", "-c", help="Risk category"),
):
    """Run AI-assisted risk assessment."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.agent.engine import run_agent
        await init_db()
        async with async_session() as db:
            instruction = "Perform a risk assessment."
            if category:
                instruction += f" Focus on the category: {category}."
            instruction += " Identify risks, assess likelihood (1-5) and impact (1-5), and record them."
            return await run_agent(db, instruction)

    with console.status("[bold green]Assessing risks..."):
        result = _run(_run_it())

    console.print(f"\n[green]✓ Assessment completed[/green]")
    console.print(f"\n{result['result']}")


@risk_app.command("list")
def risk_list():
    """List all risks."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.risk_service import list_risks
        await init_db()
        async with async_session() as db:
            return await list_risks(db)

    risks = _run(_run_it())
    if not risks:
        console.print("[yellow]No risks found[/yellow]")
        return

    table = Table(title="Risk Register")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Title", style="cyan")
    table.add_column("L", justify="center")
    table.add_column("I", justify="center")
    table.add_column("Score", justify="center", style="bold")
    table.add_column("Status")
    for r in risks:
        score_color = "green" if r.score <= 5 else "yellow" if r.score <= 15 else "red"
        table.add_row(r.id[:8], r.title, str(r.likelihood), str(r.impact),
                       f"[{score_color}]{r.score}[/{score_color}]", r.status)
    console.print(table)


@risk_app.command("show")
def risk_show(risk_id: str = typer.Argument(..., help="Risk ID")):
    """Show risk details."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.risk_service import get_risk
        await init_db()
        async with async_session() as db:
            return await get_risk(db, risk_id)

    risk = _run(_run_it())
    if not risk:
        console.print(f"[red]Risk '{risk_id}' not found[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]{risk.title}[/bold cyan]")
    console.print(f"Category: {risk.category} | Owner: {risk.owner}")
    console.print(f"Likelihood: {risk.likelihood} | Impact: {risk.impact} | Score: {risk.score}")
    console.print(f"Status: {risk.status}")
    if risk.description:
        console.print(f"\n{risk.description}")

    if risk.mitigations:
        table = Table(title="Mitigations")
        table.add_column("Action")
        table.add_column("Status")
        table.add_column("Assigned To")
        for m in risk.mitigations:
            table.add_row(m.action, m.status, m.assigned_to)
        console.print(table)


@risk_app.command("matrix")
def risk_matrix():
    """Display risk matrix."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.risk_service import get_risk_matrix
        await init_db()
        async with async_session() as db:
            return await get_risk_matrix(db)

    matrix = _run(_run_it())

    table = Table(title="Risk Matrix (Impact × Likelihood)")
    table.add_column("Impact ↓ / Likelihood →", style="bold")
    for i in range(1, 6):
        table.add_column(str(i), justify="center")

    for impact in range(4, -1, -1):
        row = [str(impact + 1)]
        for likelihood in range(5):
            risks = matrix[impact][likelihood]
            score = (impact + 1) * (likelihood + 1)
            if risks:
                color = "green" if score <= 5 else "yellow" if score <= 15 else "red"
                cell = f"[{color}]{len(risks)} risk(s)[/{color}]"
            else:
                cell = "·"
            row.append(cell)
        table.add_row(*row)
    console.print(table)


@risk_app.command("update")
def risk_update(
    risk_id: str = typer.Argument(..., help="Risk ID"),
    likelihood: int = typer.Option(..., "--likelihood", "-l"),
    impact: int = typer.Option(..., "--impact", "-i"),
    status: str = typer.Option(None, "--status", "-s"),
):
    """Update risk score."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.risk_service import update_risk_score
        from src.schemas.risk import RiskUpdateScore
        await init_db()
        async with async_session() as db:
            return await update_risk_score(db, risk_id, RiskUpdateScore(
                likelihood=likelihood, impact=impact, status=status
            ))

    risk = _run(_run_it())
    if not risk:
        console.print(f"[red]Risk '{risk_id}' not found[/red]")
        raise typer.Exit(1)
    console.print(f"[green]✓ Updated risk score to {risk.score}[/green]")


# ── Policy ──────────────────────────────────────────────────────────

@policy_app.command("create")
def policy_create(
    title: str = typer.Argument(..., help="Policy title"),
    framework: str = typer.Option(None, "--framework", "-f", help="Framework name"),
    category: str = typer.Option("", "--category", "-c"),
):
    """Create a policy with AI-generated content."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.framework_service import import_all_frameworks, get_framework_by_name
        from src.agent.engine import run_agent
        settings = get_settings()
        await init_db()
        async with async_session() as db:
            await import_all_frameworks(db, settings.frameworks_dir)
            fw_id = None
            if framework:
                fw = await get_framework_by_name(db, framework)
                if fw:
                    fw_id = fw.id
            instruction = f'Create a compliance policy titled "{title}".'
            if framework:
                instruction += f" Base it on the {framework} framework requirements."
            if category:
                instruction += f" Category: {category}."
            instruction += " Generate comprehensive policy content and save it."
            return await run_agent(db, instruction)

    with console.status("[bold green]Generating policy..."):
        result = _run(_run_it())

    console.print(f"\n[green]✓ Policy created[/green]")
    console.print(f"\n{result['result']}")


@policy_app.command("list")
def policy_list():
    """List all policies."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.policy_service import list_policies
        await init_db()
        async with async_session() as db:
            return await list_policies(db)

    policies = _run(_run_it())
    if not policies:
        console.print("[yellow]No policies found[/yellow]")
        return

    table = Table(title="Policies")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Title", style="cyan")
    table.add_column("Status")
    table.add_column("Version")
    table.add_column("Updated")
    for p in policies:
        table.add_row(p.id[:8], p.title, p.status, f"v{p.current_version}", str(p.updated_at)[:16])
    console.print(table)


@policy_app.command("show")
def policy_show(policy_id: str = typer.Argument(..., help="Policy ID")):
    """Show policy details."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.policy_service import get_policy
        await init_db()
        async with async_session() as db:
            return await get_policy(db, policy_id)

    policy = _run(_run_it())
    if not policy:
        console.print(f"[red]Policy '{policy_id}' not found[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]{policy.title}[/bold cyan]")
    console.print(f"Status: {policy.status} | Version: v{policy.current_version}")
    if policy.versions:
        latest = max(policy.versions, key=lambda v: v.version_number)
        console.print(f"\n{latest.content[:500]}")
        if len(latest.content) > 500:
            console.print("[dim]... (truncated)[/dim]")


@policy_app.command("approve")
def policy_approve(policy_id: str = typer.Argument(..., help="Policy ID")):
    """Approve a policy."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.policy_service import approve_policy
        await init_db()
        async with async_session() as db:
            return await approve_policy(db, policy_id)

    policy = _run(_run_it())
    if not policy:
        console.print(f"[red]Policy '{policy_id}' not found[/red]")
        raise typer.Exit(1)
    console.print(f"[green]✓ Policy approved[/green]")


@policy_app.command("distribute")
def policy_distribute(
    policy_id: str = typer.Argument(..., help="Policy ID"),
    channel: str = typer.Option("email", "--channel", "-c", help="Distribution channel"),
    recipients: list[str] = typer.Option([], "--to", "-t", help="Recipients"),
):
    """Distribute a policy via email/teams/sharepoint."""
    if not recipients:
        console.print("[red]Specify at least one recipient with --to[/red]")
        raise typer.Exit(1)

    async def _run_it():
        from src.database import init_db, async_session
        from src.services.policy_service import distribute_policy
        await init_db()
        async with async_session() as db:
            return await distribute_policy(db, policy_id, channel, recipients)

    dists = _run(_run_it())
    console.print(f"[green]✓ Distributed to {len(dists)} recipient(s) via {channel}[/green]")


# ── Report ──────────────────────────────────────────────────────────

@report_app.command("generate")
def report_generate(
    report_type: str = typer.Argument(..., help="Report type (audit, risk, compliance, executive)"),
    format: str = typer.Option("docx", "--format", "-f", help="Output format"),
    source_id: str = typer.Option("", "--source", "-s", help="Source ID (audit/risk ID)"),
):
    """Generate a report document."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.agent.engine import run_agent
        await init_db()
        async with async_session() as db:
            instruction = f"Generate a {report_type} report in {format} format."
            if source_id:
                instruction += f" Source ID: {source_id}."
            return await run_agent(db, instruction)

    with console.status("[bold green]Generating report..."):
        result = _run(_run_it())

    console.print(f"\n[green]✓ Report generated[/green]")
    console.print(f"\n{result['result']}")


@report_app.command("list")
def report_list():
    """List all reports."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.report_service import list_reports
        await init_db()
        async with async_session() as db:
            return await list_reports(db)

    reports = _run(_run_it())
    if not reports:
        console.print("[yellow]No reports found[/yellow]")
        return

    table = Table(title="Reports")
    table.add_column("ID", style="dim", max_width=8)
    table.add_column("Title", style="cyan")
    table.add_column("Type")
    table.add_column("Format")
    table.add_column("Created")
    for r in reports:
        table.add_row(r.id[:8], r.title, r.report_type, r.format, str(r.created_at)[:16])
    console.print(table)


@report_app.command("upload")
def report_upload(
    report_id: str = typer.Argument(..., help="Report ID"),
    site: str = typer.Option("", "--site", help="SharePoint site"),
):
    """Upload report to SharePoint."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.services.report_service import get_report
        from src.office365.sharepoint import upload_file
        await init_db()
        async with async_session() as db:
            report = await get_report(db, report_id)
            if not report:
                return None
            url = await upload_file(report.file_path, site)
            return url

    url = _run(_run_it())
    if url is None:
        console.print(f"[red]Report '{report_id}' not found[/red]")
        raise typer.Exit(1)
    console.print(f"[green]✓ Uploaded: {url}[/green]")


# ── AI Commands ─────────────────────────────────────────────────────

@app.command("ask")
def ask(question: str = typer.Argument(..., help="Question for the AI")):
    """Ask the AI a compliance question."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.agent.engine import run_agent
        await init_db()
        async with async_session() as db:
            return await run_agent(db, question)

    with console.status("[bold green]Thinking..."):
        result = _run(_run_it())

    console.print(f"\n{result['result']}")


@app.command("agent")
def agent_execute(instruction: str = typer.Argument(..., help="Instruction for the AI agent")):
    """Execute a free-form AI agent task."""
    async def _run_it():
        from src.database import init_db, async_session
        from src.agent.engine import run_agent
        await init_db()
        async with async_session() as db:
            return await run_agent(db, instruction)

    with console.status("[bold green]Executing..."):
        result = _run(_run_it())

    console.print(f"\n[green]✓ Completed ({result['iterations']} iterations)[/green]")
    console.print(f"\n{result['result']}")


# ── Serve ───────────────────────────────────────────────────────────

@app.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
):
    """Start the API server."""
    import uvicorn
    console.print(f"[bold green]Starting server at http://{host}:{port}[/bold green]")
    uvicorn.run("src.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    app()
