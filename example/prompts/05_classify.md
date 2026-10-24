# Step 5 – classify every answer

```text
Use the llm-categorization skill, phase 2. Implement step 5 in src/project/classify.py
(contracts in docs/pipeline.md).

- Input: data/processed/03_clean.csv and the reviewed data/processed/categories_v1.json.
- Long format: one row per non-empty positive or negative answer (row_id, polarity, text).
- Batches of 20 answers per request to the topic model; the prompt contains the category
  list with descriptions; exactly one category per answer, names only from the list.
- Validate with pydantic (every id present, every category valid); retry a batch once.
- Cache per batch, respect --limit (number of survey rows), store model and prompt_version.
- Write data/processed/05_classified.csv. Tests without LLM calls.

Run `uv run pytest`, then `uv run python scripts/05_classify.py --limit 100`.
```

**Look at:** pick 10 random rows of `05_classified.csv` – would you agree with the model?
