"""
Data models for lablog.

A LabPanel is one visit's worth of results (e.g., an annual blood panel).
A LabResult is a single biomarker measurement within a panel.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class LabResult:
    """A single biomarker measurement."""
    name: str           # e.g. "Glucose"
    value: float        # e.g. 95.0
    unit: str           # e.g. "mg/dL"
    low: float | None   # normal range lower bound (optional)
    high: float | None  # normal range upper bound (optional)

    @property
    def status(self) -> str:
        """Returns 'low', 'high', or 'normal' based on reference range."""
        if self.low is not None and self.value < self.low:
            return "low"
        if self.high is not None and self.value > self.high:
            return "high"
        return "normal"


@dataclass
class LabPanel:
    """A collection of results from a single lab visit."""
    date: date
    results: list[LabResult] = field(default_factory=list)
