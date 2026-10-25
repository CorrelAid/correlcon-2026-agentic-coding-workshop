# Example project: coding agent + EU-hosted LLM

Reusable template for CorrelAid projects with NGOs. Setup instructions: [`../SETUP.md`](../SETUP.md).
Background on providers, costs and test results: [`docs/infrastructure.md`](docs/infrastructure.md).

```bash
cp .env.example .env          # add the two keys
uv sync
uv run python scripts/check_setup.py
uv run python scripts/get_data.py
uv run python scripts/01_prepare.py
uv run agent
```

Workshop exercises: [`docs/workshop-flow.md`](docs/workshop-flow.md).

## Data

"Family satisfaction in Frankfurt - Babylotse survey 2024" by
[Babylotse Frankfurt](https://babylotse-frankfurt.de/) is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and available
[on GitHub](https://github.com/CorrelAid/workshop-babylotse). Thanks to Kinderschutzbund
Frankfurt / Babylotse for permission to publish and use the data. The data is downloaded by
`scripts/get_data.py` (pinned commit + checksum) and is not stored in this repo.

District polygons (`ffmstadtteilewahlen.geojson`, Stadt Frankfurt am Main) and the district
mapping in `src/project/districts.py` come from the same 2024 repo; that code is GPL-3.0.

Workshop: follow [`prompts/README.md`](prompts/README.md) – five steps, ready prompts.
Pipeline and file contracts: [`docs/pipeline.md`](docs/pipeline.md).

Layout:

```
AGENTS.md                         project rules for any agent
opencode.json                     IONOS only, permissions, sharing off
.opencode/plugins/guardrails.ts   hooks: privacy blocks, key hiding, ruff feedback
.agents/skills/                   privacy-check
prompts/                          copy-paste prompts for steps 2–5
src/project/                      prepare.py + districts.py (ready), stubs for steps 2–5,
                                  llm.py (single LLM access point, EU endpoints only)
scripts/                          get_data.py, 01_prepare.py … 05_report.py, check_setup.py, costs.py
data/raw/, data/interim/          blocked for the agent, not in git
data/processed/                   sample, categories, results – the agent may look here
```
