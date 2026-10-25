# Step 2 – flag spam

```text
Implement step 2 in src/project/spam.py (the stub describes the functions; the file
contracts are in docs/pipeline.md).

Read data/interim/01_prepared.csv with code – do not open the file yourself.
A response is spam if it has no usable content: empty answers, "-", "xx", keyboard
mashing, random names, test entries, advertising or text unrelated to families in
Frankfurt. Short but real answers ("Kitaplätze") are NOT spam.

- Send positive + negative answer of each response together, ~20 responses per request,
  numbered by row_id, to the topic model via src/project/llm.py (ANALYSIS_MODEL).
- Ask for JSON {"results": [{"row_id": …, "is_spam": true/false, "reason": "…"}]},
  use response_format={"type": "json_object"} and validate with pydantic.
- GLM-5.3 is a reasoning model: pass reasoning_effort="low" and max_tokens=8000.
- Leave the decision to the LLM: is_spam and spam_reason come from its answer, nothing else.
- Cache each batch in data/interim/cache/ so a re-run costs nothing; respect --limit.
- Put the prompt as a versioned constant in src/project/prompts.py.
- Add tests in tests/test_spam.py that do not call the LLM (mock it).
- Show the user what is happening: logging (INFO: input file and row count, batches,
  cache hits, output file, counts) and a tqdm progress bar over the batches. No comment
  text in logs.

Then run `uv run pytest -q` and tell me the command for a first run with --limit 100.
```

**Look at:** the agent never reads `data/interim/` (try asking it to – the hook blocks it).
How many responses are spam? Do the reasons make sense?
