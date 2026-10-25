# Step 2 – flag spam (plain Python, no LLM)

```text
Implement step 2 in src/project/spam.py: a fast spam detector in plain Python – no LLM
calls. The file contract is in docs/pipeline.md.

Read data/interim/01_prepared.csv with code – do not open the file yourself. What we know
about the data: real answers are in German (a few in English). Spam is e.g. text in other
languages, keyboard mashing, a made-up name as the whole answer, advertising with links
(already masked as [URL]), or only punctuation ("..", "-"). A response is spam only if it
has no usable content at all – short real answers ("Kitaplätze", "nichts") are NOT spam.
district_known == False is a hint, not enough on its own.

- One small, readable function per rule; spam_reason lists the rules that fired.
- Choose a simple, robust approach (a library is fine) and explain your choice briefly.
- The script prints only counts per reason – never comment text.
- Tests in tests/test_spam.py with made-up examples, including real answers that must
  NOT be flagged.
- Also write scripts/inspect_spam.py for ME to review the result: show flagged and
  unflagged rows with their reasons, filterable by reason. Do NOT run it yourself – it
  shows personal data.

Then run `uv run pytest` and `uv run python scripts/02_spam.py`.
```

**Look at:** run `uv run python scripts/inspect_spam.py` **in your own terminal**, not in
OpenCode. Look for real answers that were flagged and spam that got through. Then tell
the agent the *pattern*, not the text – e.g. *"short German answers are flagged as foreign
language – fix the rule and add a test"* – and re-run. It takes a second.

Try asking the agent to "show me 5 raw rows" – the hooks block it.
