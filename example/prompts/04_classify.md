# Step 4 – assign categories to every answer

```text
Implement step 4 in src/project/classify.py
(contracts in docs/pipeline.md).
Read only these files (no need to explore other steps): src/project/classify.py,
src/project/data.py, docs/pipeline.md, src/project/llm.py, src/project/paths.py.

- Input: load_valid_answers() from src/project/data.py (step 3) and the reviewed
  data/processed/categories_v1.json.
- Long format: one row per non-empty positive or negative answer (row_id, polarity, text).
- Batches of 20 answers per request to the analysis model; the prompt contains the category
  list with descriptions.
- Multi-label: one answer often mentions several topics ("Kita-Platz gefunden, aber kaum
  Hebammen") – assign ALL categories that clearly apply (usually 1–3), names only from the
  list. "Keine inhaltliche Aussage" only alone.
- Validate with pydantic (every id present, every category valid, at least one per answer);
  retry a batch once.
- Cache per batch, respect --limit (number of survey rows), store model and prompt_version.
- Write data/processed/04_classified.csv.
- End the script with sanity checks on its own output and print them (e.g. all row_ids
  present, values from the allowed set, categories per answer plausible). No tests that mock the LLM.
- Show the user what is happening: logging (INFO: input file and row count, batches,
  cache hits, output file, counts) and a tqdm progress bar over the batches. No comment
  text in logs.

Then tell me the command for a first run with --limit 100.
```

**Look at:** pick 10 random rows of `04_classified.csv` – would you agree with the model?
Are answers with several topics really getting several categories?
