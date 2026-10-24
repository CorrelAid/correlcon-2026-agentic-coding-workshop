# AGENTS.md

Instructions for coding agents (OpenCode, Mistral Vibe, Cline, Codex, …).
Keep it short: every line is sent with every request.

## Project

Data analysis for a non-profit organisation (NGO). Python, managed with `uv`.
The code will be handed over to people without deep Python knowledge.
Readability beats cleverness.

## Models

- You (the coding agent) run on Qwen3-Coder-Next via IONOS. Your job: write and test code.
- Analysing the comments (topics, classification) is done **by project code** via
  `src/project/llm.py` with the topic model (GLM-5.3 on Scaleway). Don't categorise
  comments yourself – write code that asks the topic model (skill `llm-categorization`).

## Data

Babylotse survey 2024 (families with a baby in Frankfurt), CC BY 4.0 – attribution in README.
Get it with `uv run python scripts/get_data.py` → `data/raw/babylotse_survey_2024.csv`.
987 rows, UTF-8, German. Columns (you do not need to open the file to know them):

- `ID`, `Date Created`, `Title` (a timestamp, not a title)
- `Ich wohne im Stadtteil` – district; contains HTML entities (e.g. `&ouml;`)
- `Das gefällt mir gut mit Baby in Frankfurt` – free text, positive
- `Das gefällt mir nicht gut mit Baby in Frankfurt` – free text, negative

Free text may contain contact details or names → pseudonymise first.

## Data protection (non-negotiable)

- `data/raw/` holds raw data that may contain personal data. **Never read or print it.**
  Write code that processes it locally instead.
- Only work with `data/processed/` (pseudonymised) or synthetic sample data.
- Before data is sent to an LLM: use the `privacy-check` skill.
- LLM calls in code only via `src/project/llm.py` (EU provider, configured in `.env`).
  Do not add other AI APIs or US services.
- Never read, print or commit `.env`.

## Docs to look up (instead of guessing APIs)

- OpenAI Python SDK: https://github.com/openai/openai-python
- Scaleway Generative APIs: https://www.scaleway.com/en/docs/generative-apis/
- pandas: https://pandas.pydata.org/docs/ · pydantic: https://docs.pydantic.dev/latest/
- pytest: https://docs.pytest.org/

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
