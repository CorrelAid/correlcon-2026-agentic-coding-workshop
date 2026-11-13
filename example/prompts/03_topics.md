# Step 3 – find topics

```text
Implement step 3 in src/project/topics.py
(contracts in docs/pipeline.md).
Read only these files (no need to explore other steps): src/project/topics.py,
docs/pipeline.md, src/project/llm.py, src/project/paths.py.

- Input: the valid answers – write load_valid_answers() in src/project/data.py:
  data/interim/02_spam.csv with is_spam == False if it exists, otherwise (step 2 is
  optional) data/interim/01_prepared.csv with district_known == True. Print which file
  was used.
- Draw a fixed sample (seed 42) of 50 positive and 50 negative non-empty answers; save
  it as data/processed/03_sample.csv.
- Send the whole sample in ONE request to the analysis model via src/project/llm.py.
- Ask for at most 10 neutral categories (topics, not complaints – they must fit positive
  and negative answers), in German, each with a description of what belongs in it and
  what does not. Plus the extra category "Keine inhaltliche Aussage".
- Answer format {"categories": [{"name": …, "description": …}]} via response_format,
  validate with pydantic, save data/processed/categories_v1.json.
- gpt-oss-120b: reasoning_effort="low", max_tokens=8000.
- The prompt for the analysis model goes into src/project/prompts.py as TOPICS_V1 (the files
  in prompts/ are instructions for you, not for the analysis model).
- End the script with sanity checks on its own output and print them (e.g. all row_ids
  present, values from the allowed set, counts plausible). No tests that mock the LLM.
- Show the user what is happening: logging (INFO: input file and row count, sample size,
  request duration and tokens, output file, counts).
  No comment text in logs.

Run `uv run pytest -q` (checks that everything imports), then tell me the command to run
the step.
```

**Look at:** read the categories together. Would the NGO understand them? Edit
`categories_v1.json` by hand if needed – humans decide, the model suggests.
