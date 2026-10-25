# Step 4 – classify every answer

```text
Implement step 4 in src/project/classify.py
(contracts in docs/pipeline.md).

- Input: load_valid_answers() from src/project/data.py (step 3) and the reviewed
  data/processed/categories_v1.json.
- Long format: one row per non-empty positive or negative answer (row_id, polarity, text).
- Batches of 20 answers per request to the topic model; the prompt contains the category
  list with descriptions; exactly one category per answer, names only from the list.
- Validate with pydantic (every id present, every category valid); retry a batch once.
- Cache per batch, respect --limit (number of survey rows), store model and prompt_version.
- Write data/processed/04_classified.csv. Tests without LLM calls.
- Show the user what is happening: logging (INFO: input file and row count, batches,
  cache hits, output file, counts) and a tqdm progress bar over the batches. No comment
  text in logs.

Run `uv run pytest -q`, then tell me the command for a first run with --limit 100.
```

**Look at:** pick 10 random rows of `04_classified.csv` – would you agree with the model?
