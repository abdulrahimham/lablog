from dataclasses import dataclass, field
from datetime import date


@dataclass
class LabResult:
    name: str           
    value: float        
    unit: str           
    low: float | None   
    high: float | None  

    @property
    def status(self) -> str:
        # returns 'low', 'high', or 'normal' based on reference range
        if self.low is not None and self.value < self.low:
            return "low"
        if self.high is not None and self.value > self.high:
            return "high"
        return "normal"


@dataclass
class LabPanel:
    # one lab visit's worth of results
    date: date
    results: list[LabResult] = field(default_factory=list)
