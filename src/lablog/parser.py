import csv
from datetime import date
from pathlib import Path

from lablog.models import LabPanel, LabResult


class ParseError(Exception):
    pass


def parse_csv(path: Path, panel_date: date) -> LabPanel:
    required_columns = {"name", "value", "unit"}

    with path.open(newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ParseError("CSV file appears to be empty.")

        # strip whitespace and lowercase all column names
        reader.fieldnames = [col.strip().lower() for col in reader.fieldnames]

        missing = required_columns - set(reader.fieldnames)
        if missing:
            raise ParseError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        results = []
        for i, row in enumerate(reader, start=2):
            # strip whitespace from all values
            row = {k: (v.strip() if v else "") for k, v in row.items()}

            name = row.get("name", "")
            unit = row.get("unit", "")
            raw_value = row.get("value", "")

            if not name:
                raise ParseError(f"Row {i}: 'name' cannot be empty.")
            if not raw_value:
                raise ParseError(f"Row {i} ({name}): 'value' cannot be empty.")

            try:
                value = float(raw_value)
            except ValueError:
                raise ParseError(f"Row {i} ({name}): '{raw_value}' is not a valid number.")

            # low and high are optional and blank cells become None
            def parse_optional(val: str) -> float | None:
                if val == "":
                    return None
                try:
                    return float(val)
                except ValueError:
                    raise ParseError(f"Row {i} ({name}): '{val}' is not a valid number.")

            low = parse_optional(row.get("low", ""))
            high = parse_optional(row.get("high", ""))

            results.append(LabResult(name=name, value=value, unit=unit, low=low, high=high))

    if not results:
        raise ParseError("CSV file has no data rows.")

    return LabPanel(date=panel_date, results=results)
