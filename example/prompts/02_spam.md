# Step 2 – flag spam (bonus)

There is no single right way here – that's what makes this step interesting. Spam can be
caught with simple rules, with an NLP library or with the analysis model as a judge. Let the
agent propose, you decide.

```text
Implement step 2 in src/project/spam.py (the file contracts are in docs/pipeline.md).
Read only these files (no need to explore other steps): src/project/spam.py,
docs/pipeline.md, src/project/llm.py, src/project/paths.py.

Read data/interim/01_prepared.csv with code – do not open the file yourself.
A response is spam if it has no usable content: empty answers, "-", "xx", keyboard
mashing, random names, test entries, advertising, text in other languages or unrelated to
families in Frankfurt. Short but real answers ("Kitaplätze", "nichts") are NOT spam.

First propose 2–3 approaches in a few lines each – e.g. rules/regex, an NLP library such as
language detection, or the analysis model as a judge (LLM, batches of ~20) – with pros, cons
and cost. Wait for my choice, then implement it:
- Rules or a library: plain Python, `uv add` for any package, runs in seconds, no API cost.
- LLM as judge: via src/project/llm.py, ~20 numbered responses per request, JSON
  {"results": [{"row_id": …, "is_spam": …, "reason": "…"}]} with response_format and pydantic,
  reasoning_effort="low", max_tokens=8000, prompt as a versioned constant in
  src/project/prompts.py, cache each batch in data/interim/cache/, respect --limit.
- Either way: write 02_spam.csv with is_spam and spam_reason; end the script with sanity
  checks on its own output; log progress (no comment text in logs).

Run `uv run pytest -q` (checks that everything imports), then tell me the command to run it.
```

**Look at:** how many responses are flagged, and why? Compare with your neighbour: rules vs.
LLM – which catches more real spam, which flags real answers by mistake? Without step 2,
steps 3–5 use the district check from step 1 as a spam filter.
