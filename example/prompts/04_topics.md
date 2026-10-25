# Step 4 – find topics

```text
Implement step 4 in src/project/topics.py
(contracts in docs/pipeline.md).

- Input: the valid answers – write load_valid_answers() in src/project/data.py that uses
  the first file that exists: data/processed/03_clean.csv (all rows),
  data/interim/02_spam.csv (is_spam == False), data/interim/01_prepared.csv
  (district_known == True). Steps 2 and 3 are optional. Print which file was used.
- Draw a fixed sample (seed 42) of 50 positive and 50 negative non-empty answers; save
  it as data/processed/04_sample.csv.
- Send the whole sample in ONE request to the topic model via src/project/llm.py.
- Ask for at most 10 neutral categories (topics, not complaints – they must fit positive
  and negative answers), in German, each with a description of what belongs in it and
  what does not. Plus the extra category "Keine inhaltliche Aussage".
- JSON via response_format, validate with pydantic, save data/processed/categories_v1.json.
- Versioned prompt in src/project/prompts.py; tests without LLM calls.

Run `uv run pytest`, then `uv run python scripts/04_topics.py`.
```

**Look at:** read the categories together. Would the NGO understand them? Edit
`categories_v1.json` by hand if needed – humans decide, the model suggests.
