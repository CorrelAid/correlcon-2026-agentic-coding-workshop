---
name: llm-categorization
description: Categorise free text (e.g. survey comments) with an LLM in a reproducible, cheap and reviewable way. Use for tasks like "suggest categories", "classify comments", "find topics in free-text answers".
---

# LLM-assisted categorisation of free text

## Prerequisites

- Data is pseudonymised in `data/processed/` (otherwise run the `privacy-check` skill first).
- LLM access only via `src/project/llm.py` (`get_client()`, `ANALYSIS_MODEL`).

## Steps

1. **Estimate costs** with `uv run python scripts/costs.py --texts <N>` and tell the person
   at the keyboard before starting a run.
2. **Suggest categories**: give a sample (e.g. 100 comments) to the model and ask for
   8–12 categories with a short description. Save as `data/processed/categories_v1.json`
   and have a human review it.
3. **Assign**: classify each comment into one or more categories.
   - Enforce structured output (`response_format={"type": "json_object"}`) and validate
     with pydantic.
   - `temperature=0`; store model name and prompt version with every result.
   - Cache results to a file so that interruptions cost nothing.
4. **Check quality**: have a human review 30 random assignments; record the agreement in `docs/`.
5. **Analyse**: counts per category, example quotes, a chart in `outputs/`.

## Rules

- Prompts are versioned constants in `src/project/prompts.py`.
- Do not attach metadata to a comment in the prompt unless it is needed.
- The LLM suggests, humans decide: always review categories and samples.
