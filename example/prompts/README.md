# Workshop prompts – copy, paste, run

Start OpenCode **inside `example/`**: `uv run agent`.
Then, step by step: paste the prompt, watch the agent fill the stub in `src/project/`,
run the command it tells you, look at the result.

| Step | Prompt | Then run | Time | Topic-model cost* |
|---|---|---|---|---|
| 0 | – | `uv run python scripts/get_data.py` | 1 min | – |
| 1 | – (ready-made) | `uv run python scripts/01_prepare.py` | 1 min | – |
| 2 | [02_spam.md](02_spam.md) *(optional)* | `uv run python scripts/02_spam.py` | 8 min | €0 (no LLM) |
| 3 | [03_pii.md](03_pii.md) *(optional)* | `uv run python scripts/03_pii.py` | 5 min | €0 (regex) |
| 4 | [04_topics.md](04_topics.md) | `uv run python scripts/04_topics.py` | 8 min | ~€0.05 |
| 5 | [05_classify.md](05_classify.md) | `uv run python scripts/05_classify.py --limit 100` | 8 min | ~€0.15 |
| 6 | [06_report.md](06_report.md) | `uv run python scripts/06_report.py` | 8 min | – |

\* per participant with `--limit 100`; the coding agent itself adds ~€0.05–0.15 per step.
Full data set (all 987 rows): run without `--limit` after the workshop.

**Skipped steps 2 or 3?** Steps 3–5 fall back to the previous file; without step 2 the
district check from step 1 filters the spam (see `docs/pipeline.md`, "Valid answers").

**Stuck?** Every step only needs the previous step's file (see `docs/pipeline.md`).
Ask the agent: *"The step failed with this error: … – fix it."*
