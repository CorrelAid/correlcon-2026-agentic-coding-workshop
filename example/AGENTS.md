# AGENTS.md

Instructions for coding agents (OpenCode, Mistral Vibe, Cline, Codex, …).
Keep it short: every line is sent with every request.

## Project

Data analysis for a non-profit organisation (NGO). Python, managed with `uv`.
The code will be handed over to people without deep Python knowledge.
Readability beats cleverness.

## Data protection (non-negotiable)

- `data/raw/` holds raw data that may contain personal data. **Never read or print it.**
  Write code that processes it locally instead.
- Only work with `data/processed/` (pseudonymised) or synthetic sample data.
- Before data is sent to an LLM: use the `privacy-check` skill.
- LLM calls in code only via `src/project/llm.py` (EU provider, configured in `.env`).
  Do not add other AI APIs or US services.
- Never read, print or commit `.env`.

## Commands

- Dependencies: `uv sync` · add a package: `uv add <package>`
- Tests: `uv run pytest`
- Lint/format: `uv run ruff check --fix . && uv run ruff format .`
- Check setup: `uv run python scripts/check_setup.py`
- Estimate costs: `uv run python scripts/costs.py`

## Layout

- `src/project/` – reusable code (functions with docstrings and type hints)
- `scripts/` – executable entry points
- `notebooks/` – exploration; logic that stays moves to `src/`
- `tests/` – pytest; every new function gets at least one test

## Way of working

- Start with a 3–5 point plan, then implement in small steps; run `uv run pytest` after each.
- Before LLM batch runs: estimate costs with `scripts/costs.py` and state them.
- If unsure, ask instead of guessing.
