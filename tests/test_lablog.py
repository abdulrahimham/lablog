

import pytest
from datetime import date
from pathlib import Path
import tempfile

from lablog.models import LabResult, LabPanel
from lablog.parser import parse_csv, ParseError


# LabResult.status tests

def test_status_normal():
    r = LabResult(name="Glucose", value=90.0, unit="mg/dL", low=70.0, high=99.0)
    assert r.status == "normal"

def test_status_high():
    r = LabResult(name="Glucose", value=110.0, unit="mg/dL", low=70.0, high=99.0)
    assert r.status == "high"

def test_status_low():
    r = LabResult(name="Glucose", value=60.0, unit="mg/dL", low=70.0, high=99.0)
    assert r.status == "low"

def test_status_no_range():
    # when no reference range is given, result is always "normal"
    r = LabResult(name="Glucose", value=999.0, unit="mg/dL", low=None, high=None)
    assert r.status == "normal"

def test_status_only_upper_bound():
    r = LabResult(name="Cholesterol", value=210.0, unit="mg/dL", low=None, high=200.0)
    assert r.status == "high"

def test_status_on_boundary():
    # value exactly equal to the upper bound is considered normal
    r = LabResult(name="Glucose", value=99.0, unit="mg/dL", low=70.0, high=99.0)
    assert r.status == "normal"


# parse_csv tests

def _write_csv(lines: list[str]) -> Path:
    """Helper: write lines to a temp CSV file and return its path."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    tmp.write("\n".join(lines) + "\n")
    tmp.flush()
    return Path(tmp.name)


def test_parse_valid_csv():
    path = _write_csv([
        "name,value,unit,low,high",
        "Glucose,95,mg/dL,70,99",
        "Cholesterol,185,mg/dL,,200",
    ])
    panel = parse_csv(path, date(2024, 1, 15))

    assert panel.date == date(2024, 1, 15)
    assert len(panel.results) == 2

    glucose = panel.results[0]
    assert glucose.name == "Glucose"
    assert glucose.value == 95.0
    assert glucose.low == 70.0
    assert glucose.high == 99.0

    cholesterol = panel.results[1]
    assert cholesterol.low is None   # blank 
    assert cholesterol.high == 200.0


def test_parse_missing_column():
    path = _write_csv(["name,value", "Glucose,95"])
    with pytest.raises(ParseError, match="missing required columns"):
        parse_csv(path, date.today())


def test_parse_non_numeric_value():
    path = _write_csv([
        "name,value,unit,low,high",
        "Glucose,high,mg/dL,70,99",
    ])
    with pytest.raises(ParseError, match="not a valid number"):
        parse_csv(path, date.today())


def test_parse_empty_name():
    path = _write_csv([
        "name,value,unit,low,high",
        ",95,mg/dL,70,99",
    ])
    with pytest.raises(ParseError, match="'name' cannot be empty"):
        parse_csv(path, date.today())


def test_parse_empty_file():
    path = _write_csv(["name,value,unit,low,high"])
    with pytest.raises(ParseError, match="no data rows"):
        parse_csv(path, date.today())
