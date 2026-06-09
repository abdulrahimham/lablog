import json
from datetime import date
from pathlib import Path

from lablog.models import LabPanel, LabResult

home = Path.home() / ".lablog"
data = home / "panels.json"


def load_panels() -> list[LabPanel]:
    if not data.exists():
        return []

    with data.open() as f:
        raw = json.load(f)

    panels = []
    for panel_data in raw:
        results = [
            LabResult(
                name=r["name"],
                value=r["value"],
                unit=r["unit"],
                low=r.get("low"),
                high=r.get("high"),
            )
            for r in panel_data["results"]
        ]
        panels.append(LabPanel(date=date.fromisoformat(panel_data["date"]), results=results))

    # return sorted oldest to newest
    return sorted(panels, key=lambda p: p.date)


def save_panels(panels: list[LabPanel]) -> None:
    home.mkdir(exist_ok=True)

    raw = [
        {
            "date": panel.date.isoformat(),
            "results": [
                {
                    "name": r.name,
                    "value": r.value,
                    "unit": r.unit,
                    "low": r.low,
                    "high": r.high,
                }
                for r in panel.results
            ],
        }
        for panel in panels
    ]

    with data.open("w") as f:
        json.dump(raw, f, indent=2)
