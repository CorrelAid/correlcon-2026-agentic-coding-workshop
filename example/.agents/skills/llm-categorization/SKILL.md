---
name: llm-categorization
description: Find topics in free text (e.g. survey comments) with an LLM and classify every comment – reproducible, cheap and reviewable. Use for "suggest categories", "find topics", "classify comments", "topic modelling".
---

# LLM-assisted topic finding and classification

Two models, two jobs: **you** (the coding agent) write the code; the **topic model**
(`ANALYSIS_MODEL` in `src/project/llm.py`, default GLM-5.3 on Scaleway) reads the comments.
Do not invent categories yourself – the code asks the topic model.

## Prerequisites

- Data is pseudonymised in `data/processed/` (otherwise run the `privacy-check` skill first).
- LLM access only via `src/project/llm.py` (`get_client()`, `ANALYSIS_MODEL`).

## Phase 1 – suggest categories (on a sample)

1. **Estimate costs** with `uv run python scripts/costs.py --texts <N>` and state them.
2. Use the fixed sample file if one exists (e.g. `data/processed/sample_negative_100.csv`);
   otherwise draw a sample with a fixed seed and save it, so the run is reproducible.
3. Send all sample comments **in one request**, numbered, and ask for:
   - at most 10 **neutral** category names (a topic, not a complaint: "Kinderbetreuung",
     not "Kita-Platzmangel"), in the language of the comments;
   - a description per category saying what belongs in it **and what does not**;
   - one extra category for **non-answers** (empty, "-", spam, off-topic) – survey data
     always has them.
4. Structured output: `response_format={"type": "json_object"}`, validate with pydantic,
   save to `data/processed/categories_v1.json` as a list of `{name, description}`.
5. Stop and ask a human to review the categories before Phase 2.

## Phase 2 – classify every comment (follow-up task)

1. Load the reviewed categories and send the comments in **batches of ~20** (numbered)
   with the category list; ask for exactly one category per comment (plus an optional
   second one if clearly needed). Never one request per comment.
2. Validate each answer with pydantic: every comment number present, every category name
   from the list. Retry a batch once if not.
3. Cache results per batch in a file, so an interruption costs nothing.
4. Store model name, prompt version and date with the results
   (`data/processed/classified_v1.csv`).
5. **Rate limits** are shared by everyone on the contract (Scaleway: tokens per minute per
   organisation). For the full data set prefer Scaleway's **Batch API** (no rate limit,
   −50 % price) – or classify a sample first.

## Phase 3 – check and analyse

- A human reviews 30 random assignments; record the agreement in `docs/`.
- Counts per category, 2–3 example quotes each, a chart in `outputs/`.

## Rules

- Prompts are versioned constants in `src/project/prompts.py`.
- Reasoning models (GLM-5.3, DeepSeek) think before answering: set `max_tokens` high enough
  (GLM-5.3 allows up to 16,384) and read the answer from `message.content`.
- The LLM suggests, humans decide.

## References

- OpenAI Python SDK (works with every OpenAI-compatible provider): https://github.com/openai/openai-python
- Scaleway Generative APIs – structured outputs, batch: https://www.scaleway.com/en/docs/generative-apis/
- pydantic: https://docs.pydantic.dev/latest/
