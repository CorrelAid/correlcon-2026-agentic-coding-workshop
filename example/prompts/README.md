# Workshop prompts – copy, paste, run

Start OpenCode **inside `example/`**: `uv run agent`.

**Order:** warm-up → step 1 (ready-made) → 3 → 4 → 5 → step 2 (spam) as a bonus if time is left.

**Warm-up** (tests your setup, ≈ 45 s, ≈ €0.02): *"Write a function in src/project/text.py that
masks email addresses and phone numbers, add tests and run them."*
Then, step by step: paste the prompt, watch the agent fill the stub in `src/project/`,
run the command it tells you, look at the result.

| Step | Prompt | Then run | Time | Analysis-model cost* |
|---|---|---|---|---|
| 0 | – | `uv run python scripts/get_data.py` | 1 min | – |
| 1 | – (ready-made) | `uv run python scripts/01_prepare.py` | 1 min | – |
| 2 | [02_spam.md](02_spam.md) *(optional)* | `uv run python scripts/02_spam.py --limit 100` | 8 min | < €0.01 |
| 3 | [03_topics.md](03_topics.md) | `uv run python scripts/03_topics.py` | 8 min | < €0.01 |
| 4 | [04_classify.md](04_classify.md) | `uv run python scripts/04_classify.py --limit 100` | 8 min | ~€0.01 |
| 5 | [05_report.md](05_report.md) | `uv run python scripts/05_report.py` | 8 min | – |

\* per participant with `--limit 100`; the coding agent itself adds ~€0.01 per agent step: a clean
pipeline step €0.08–0.15, one with many fixes €1–3 – start a fresh session for each step.
Full data set (all 987 rows): run without `--limit` after the workshop.

**Skipped step 2?** Steps 3–5 then use the district check from step 1 to filter spam
(see `docs/pipeline.md`, "Valid answers").

**Stuck?** Every step only needs the previous step's file (see `docs/pipeline.md`).
Ask the agent: *"The step failed with this error: … – fix it."*

**Saving tokens:** every agent step resends the whole session. A fresh session per step and
short fix rounds keep it cheap (€0.08–0.15 per step); a long debugging session costs €1–3.
After two failed fix attempts, take the finished step instead.

**Still stuck? Take the finished step.** The branch `demo-solution` holds a complete run
(code written by the agent + outputs). Copy one step from it and carry on with the next:

```bash
git fetch origin demo-solution
B=origin/demo-solution
# step 2 – code only (its output contains raw comments and is not in git; re-run the script)
git checkout $B -- src/project/spam.py src/project/prompts.py
# step 3 – code + categories
git checkout $B -- src/project/topics.py src/project/data.py src/project/prompts.py \
  data/processed/03_sample.csv data/processed/categories_v1.json
# step 4 – code + classified answers
git checkout $B -- src/project/classify.py src/project/data.py src/project/prompts.py \
  scripts/04_classify.py data/processed/04_classified.csv
# step 5 – code + finished report
git checkout $B -- src/project/report.py outputs/report.html
```

Run these inside `example/`. Just want to show the result? `git checkout demo-solution` and open
`example/outputs/report.html`.
