from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from lablog.models import LabPanel
from lablog.parser import parse_csv, ParseError
from lablog.storage import load_panels, save_panels

app = typer.Typer(help="Track and analyze personal lab results over time.")
console = Console()


def _status_style(status: str) -> str:
    return {"low": "yellow", "high": "red", "normal": "green"}.get(status, "white")


def _range_str(r) -> str:
    if r.low is not None and r.high is not None:
        return f"{r.low} – {r.high}"
    if r.low is not None:
        return f"≥ {r.low}"
    if r.high is not None:
        return f"≤ {r.high}"
    return "—"


def _print_panel(panel: LabPanel) -> None:
    table = Table(title=f"Lab Results — {panel.date}", box=box.SIMPLE_HEAD)
    table.add_column("Biomarker", style="bold")
    table.add_column("Value", justify="right")
    table.add_column("Unit")
    table.add_column("Normal Range")
    table.add_column("Status", justify="center")

    for r in panel.results:
        style = _status_style(r.status)
        table.add_row(
            r.name,
            str(r.value),
            r.unit,
            _range_str(r),
            f"[{style}]{r.status.upper()}[/{style}]",
        )

    console.print(table)


@app.command()
def add(
    file: Annotated[Path, typer.Argument(help="Path to a CSV file of lab results.")],
    date_str: Annotated[str, typer.Option("--date", "-d", help="Date of the lab visit (YYYY-MM-DD). Defaults to today.")] = "",
) -> None:
    panel_date = date.today()
    if date_str:
        try:
            panel_date = date.fromisoformat(date_str)
        except ValueError:
            console.print(f"[red]Error:[/red] '{date_str}' is not a valid date. Use YYYY-MM-DD.")
            raise typer.Exit(1)

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    try:
        panel = parse_csv(file, panel_date)
    except ParseError as e:
        console.print(f"[red]Parse error:[/red] {e}")
        raise typer.Exit(1)

    panels = load_panels()

    # replace existing panel for the same date if one exists
    if any(p.date == panel_date for p in panels):
        console.print(f"[yellow]Warning:[/yellow] A panel for {panel_date} already exists. Replacing it.")
        panels = [p for p in panels if p.date != panel_date]

    panels.append(panel)
    save_panels(panels)

    console.print(f"[green]✓[/green] Added {len(panel.results)} results for {panel_date}.")
    _print_panel(panel)


@app.command()
def show(
    all_panels: Annotated[bool, typer.Option("--all", "-a", help="Show all panels, not just the most recent.")] = False,
) -> None:
    panels = load_panels()

    if not panels:
        console.print("No lab results found. Use [bold]lablog add[/bold] to get started.")
        raise typer.Exit()

    for panel in (panels if all_panels else [panels[-1]]):
        _print_panel(panel)


@app.command()
def history(
    biomarker: Annotated[str, typer.Argument(help="Biomarker name to track (case-insensitive).")],
) -> None:
    panels = load_panels()

    if not panels:
        console.print("No lab results found. Use [bold]lablog add[/bold] to get started.")
        raise typer.Exit()

    rows = [
        (panel.date, r)
        for panel in panels
        for r in panel.results
        if r.name.lower() == biomarker.lower()
    ]

    if not rows:
        console.print(f"No results found for '[bold]{biomarker}[/bold]'.")
        raise typer.Exit()

    table = Table(title=f"History — {rows[0][1].name}", box=box.SIMPLE_HEAD)
    table.add_column("Date")
    table.add_column("Value", justify="right")
    table.add_column("Unit")
    table.add_column("Normal Range")
    table.add_column("Status", justify="center")

    for panel_date, r in rows:
        style = _status_style(r.status)
        table.add_row(
            str(panel_date),
            str(r.value),
            r.unit,
            _range_str(r),
            f"[{style}]{r.status.upper()}[/{style}]",
        )

    console.print(table)

    if len(rows) >= 2:
        delta = rows[-1][1].value - rows[0][1].value
        direction = "↑ up" if delta > 0 else "↓ down" if delta < 0 else "→ unchanged"
        console.print(f"\nTrend: [bold]{direction}[/bold] {abs(delta):.2f} {rows[0][1].unit} since {rows[0][0]}")
