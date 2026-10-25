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
  comments yourself – write code that asks the topic model (rules below).

## Data & pipeline

Babylotse survey 2024 (families with a baby in Frankfurt), CC BY 4.0 – attribution in README.
987 responses, German. Six steps, one file each – **contracts in `docs/pipeline.md`**,
paths in `src/project/paths.py`. Steps 0–1 are ready-made; steps 2–6 are stubs you
implement (`src/project/{spam,pii,topics,classify,report}.py`), run via `scripts/0N_*.py`.
Raw columns (you do not need to open the file to know them): `ID`, `Date Created`,
`Title` (a timestamp), `Ich wohne im Stadtteil`, `Das gefällt mir gut mit Baby in Frankfurt`,
`Das gefällt mir nicht gut mit Baby in Frankfurt`.

## Data protection (non-negotiable)

- `data/raw/` and `data/interim/` may contain personal data. **Never read or print them.**
  Write code that processes them; print only counts.
- You may inspect `data/processed/` (spam removed, PII masked) or synthetic sample data.
- Step 1 masks contact details before any LLM call. For new data sources: `privacy-check` skill.
- LLM calls in code only via `src/project/llm.py` (EU provider, configured in `.env`).
  Do not add other AI APIs or US services.
- Never read, print or commit `.env`.

## LLM calls in code (steps 2–5)

- Always via `src/project/llm.py` (`get_client()`, `ANALYSIS_MODEL`); prompts as versioned
  constants in `src/project/prompts.py`.
- Batches of ~20 numbered items per request – never one request per comment (shared rate limits).
- `response_format={"type": "json_object"}`, validate with pydantic, retry a batch once.
- Cache each batch (`cache/` next to the step's output), respect `--limit`, store model and
  prompt version with the results.
- GLM-5.3 reasons before answering: `max_tokens` 8000 (max 16,384), read `message.content`.
- Tests mock the LLM; scripts print counts, never comment text from raw/interim data.

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
