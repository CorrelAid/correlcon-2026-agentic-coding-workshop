# Workshop flow (40 min)

The hands-on part follows the pipeline in [`pipeline.md`](pipeline.md): six steps, each
with a ready prompt in [`../prompts/`](../prompts/README.md). Participants paste the
prompt into OpenCode, watch the agent fill the stub, run the script, look at the result.

| Min | What | Best practice on show |
|---|---|---|
| 0–5 | `get_data.py`, `01_prepare.py` (ready-made) – look at the summary, not the data | AGENTS.md: the agent knows the columns without opening the file |
| 5–13 | Step 2 spam (no LLM) – review with `inspect_spam.py`, give the agent the pattern, re-run; ask it to "show me 5 raw rows" | hooks block `data/raw` and `data/interim`; human review loop |
| 13–21 | Step 4 topics – read and edit the categories together | two models, two jobs: agent writes code, code calls GLM-5.3 |
| 21–29 | Step 5 classify with `--limit 100` | batching, validation, caching, shared rate limits |
| 29–35 | Step 6 report – open `outputs/report.html` | ruff hook + tests keep the generated code clean |
| 35–40 | Discussion: trust, costs (`opencode stats`) | |

Step 3 (PII) is optional – a good extra for fast groups; otherwise use the one-line
fallback prompt in `prompts/03_pii.md`.

**Why two models?** In our benchmark (`../../benchmark/RESULTS.md`) Qwen3-Coder-Next was the
best-value coding agent, while GLM-5.3 produced the cleanest topics – and as topic model it
costs only a few cents per call.

**Rate limits:** all participants share Scaleway's tokens-per-minute limit for the
organisation. With `--limit 100` a full run costs a participant ~€0.30 in topic-model calls.
