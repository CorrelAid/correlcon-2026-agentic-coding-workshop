# Example project: coding agent + EU-hosted LLM

Reusable template for CorrelAid projects with NGOs. Setup instructions: [`../SETUP.md`](../SETUP.md).
Background on providers, costs and test results: [`docs/infrastructure.md`](docs/infrastructure.md).

```bash
cp .env.example .env          # add token
uv sync
uv run python scripts/check_setup.py
uv run python scripts/get_data.py
uv run --env-file .env opencode
```

Workshop exercises: [`docs/workshop-flow.md`](docs/workshop-flow.md).

## Data

"Family satisfaction in Frankfurt - Babylotse survey 2024" by
[Babylotse Frankfurt](https://babylotse-frankfurt.de/) is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and available
[on GitHub](https://github.com/CorrelAid/workshop-babylotse). Thanks to Kinderschutzbund
Frankfurt / Babylotse for permission to publish and use the data. The data is downloaded by
`scripts/get_data.py` (pinned commit + checksum) and is not stored in this repo.

Layout:

```
AGENTS.md                         project rules for any agent
opencode.json                     IONOS only, permissions, sharing off
.opencode/plugins/guardrails.ts   hooks: privacy blocks, key hiding, ruff feedback
.agents/skills/                   privacy-check, llm-categorization, ngo-handover
src/project/llm.py                single LLM access point, EU endpoints only
scripts/check_setup.py            setup check incl. tool calling
scripts/costs.py                  cost calculator
scripts/get_data.py               downloads the Babylotse survey into data/raw/
data/raw/                         raw data – blocked for the agent, not in git
data/processed/                   pseudonymised data – the agent works here
```
