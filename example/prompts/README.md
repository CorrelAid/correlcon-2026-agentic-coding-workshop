# Workshop prompts – copy, paste, run

Start OpenCode **inside `example/`**: `uv run agent`.
Then, step by step: paste the prompt, watch the agent fill the stub in `src/project/`,
run the command it tells you, look at the result.

| Step | Prompt | Then run | Time | Topic-model cost* |
|---|---|---|---|---|
| 0 | – | `uv run python scripts/get_data.py` | 1 min | – |
| 1 | – (ready-made) | `uv run python scripts/01_prepare.py` | 1 min | – |
| 2 | [02_spam.md](02_spam.md) *(optional)* | `uv run python scripts/02_spam.py --limit 100` | 8 min | ~€0.10 |
| 3 | [03_topics.md](03_topics.md) | `uv run python scripts/03_topics.py` | 8 min | ~€0.05 |
| 4 | [04_classify.md](04_classify.md) | `uv run python scripts/04_classify.py --limit 100` | 8 min | ~€0.15 |
| 5 | [05_report.md](05_report.md) | `uv run python scripts/05_report.py` | 8 min | – |

\* per participant with `--limit 100`; the coding agent itself adds ~€0.30–1 per pipeline step
(40–100 agent steps × ~€0.0085 – start a fresh session for each step).
Full data set (all 987 rows): run without `--limit` after the workshop.

**Skipped step 2?** Steps 3–5 then use the district check from step 1 to filter spam
(see `docs/pipeline.md`, "Valid answers").

**Stuck?** Every step only needs the previous step's file (see `docs/pipeline.md`).
Ask the agent: *"The step failed with this error: … – fix it."*
