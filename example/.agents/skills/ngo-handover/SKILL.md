---
name: ngo-handover
description: Prepares handing the project over to the NGO – documentation, the NGO's own LLM access, cost overview, operating instructions. Use when the project is finished or handed over to non-developers.
---

# Handover to the NGO

Goal: the NGO can run the project without CorrelAid, understands the costs and stays in
control of its data.

## Checklist (work through it item by item, track status in `docs/handover.md`)

1. **README**: does it work on a fresh machine in < 15 minutes? Every command copy-pasteable,
   no implicit prior knowledge.
2. **The NGO's own LLM access**: link the IONOS section of `SETUP.md`. No CorrelAid token
   left in the project; is `.env.example` up to date?
3. **Costs**: run `uv run python scripts/costs.py` for the expected regular usage and copy
   the result into `docs/handover.md`.
4. **Data protection**: is `docs/data-processing.md` complete? Provider, location, DPA,
   which data is sent to the LLM.
5. **Reproducibility**: a single command regenerates the analysis
   (e.g. `uv run python scripts/analysis.py`). Tests pass.
6. **Dependencies**: `uv.lock` committed, Python version in `.python-version`.
7. **Contacts & limits**: what can the NGO change itself (categories, prompts), what needs support?

Result: a short summary for the NGO in plain language.
