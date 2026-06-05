# lablog

A command-line tool for tracking personal lab results over time. Import a CSV export from any patient portal, see which values are out of range, and track how a biomarker changes across visits.

## Installation

```bash
uv add "git+https://github.com/<your-username>/lablog.git"
```

## Usage

### Add a lab panel

```bash
lablog add results.csv --date 2024-06-01
```

Ingests a CSV of lab results for a given date. If `--date` is omitted, today's date is used.

**Expected CSV format:**

```
name,value,unit,low,high
Glucose,95,mg/dL,70,99
Cholesterol,185,mg/dL,,200
Hemoglobin,14.2,g/dL,12,17.5
```

`low` and `high` (normal range bounds) are optional — leave blank if unknown.

---

### Show the most recent panel

```bash
lablog show
```

Displays the latest panel with each result color-coded: green = normal, yellow = low, red = high.

To show all recorded panels:

```bash
lablog show --all
```

---

### Track a biomarker over time

```bash
lablog history Glucose
```

Shows every recorded value for a biomarker across all panels, along with a simple trend summary.

---

## Data storage

All data is stored locally in `~/.lablog/panels.json`. Nothing is sent anywhere.
