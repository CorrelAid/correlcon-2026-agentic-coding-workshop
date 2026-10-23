# Example project: coding agent + EU-hosted LLM

Reusable template for CorrelAid projects with NGOs. Setup instructions: [`../SETUP.md`](../SETUP.md).
Background on providers, costs and test results: [`docs/infrastructure.md`](docs/infrastructure.md).

```bash
cp .env.example .env          # add token
uv sync
uv run python scripts/check_setup.py
uv run --env-file .env opencode
```

Layout:

```
AGENTS.md                         project rules for any agent
opencode.json                     IONOS only, permissions, sharing off
.opencode/plugins/guardrails.ts   hooks: privacy blocks, key hiding, ruff feedback
.agents/skills/                   privacy-check, llm-categorization, ngo-handover
src/project/llm.py                single LLM access point, EU endpoints only
scripts/check_setup.py            setup check incl. tool calling
scripts/costs.py                  cost calculator
data/raw/                         raw data – blocked for the agent, not in git
data/processed/                   pseudonymised data – the agent works here
```
