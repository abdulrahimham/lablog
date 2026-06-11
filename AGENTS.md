# Agent Instructions

## Setup

This is a Python CLI project managed with `uv`.

To install dependencies:
```bash
uv sync
```

To run the CLI:
```bash
uv run lablog --help
```

## Running tests

```bash
uv run pytest
```

## Running the linter / formatter

```bash
uv run ruff check .
uv run ruff format .
```

## Project structure

```
src/lablog/
  __init__.py   — package init
  models.py     — LabResult and LabPanel dataclasses
  parser.py     — CSV parsing logic
  storage.py    — read/write panels to ~/.lablog/panels.json
  cli.py        — typer CLI (add, show, history commands)
tests/
  test_lablog.py
```

## Notes

- All data is stored in `~/.lablog/panels.json`.
- Do not add any external API calls or network requests.
- Keep the code readable — this is a portfolio project.
- Run tests after every change.
