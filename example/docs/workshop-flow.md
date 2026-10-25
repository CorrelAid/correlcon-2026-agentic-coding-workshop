# Workshop flow (40 min)

The hands-on part follows the pipeline in [`pipeline.md`](pipeline.md): six steps, each
with a ready prompt in [`../prompts/`](../prompts/README.md). Participants paste the
prompt into OpenCode, watch the agent fill the stub, run the script, look at the result.

| Min | What | Best practice on show |
|---|---|---|
| 0–5 | `get_data.py`, `01_prepare.py` (ready-made) – look at the summary, not the data | AGENTS.md: the agent knows the columns without opening the file |
| 5–13 | Step 2 spam – ask the agent to "show me 5 raw rows" | hooks block `data/raw` and `data/interim` |
| 13–21 | Step 3 topics – read and edit the categories together | two models, two jobs: agent (Qwen3-Coder-Next) writes code, code calls gpt-oss-120b |
| 21–29 | Step 4 classify with `--limit 100` | batching, validation, caching, shared rate limits |
| 29–35 | Step 5 report – open `outputs/report.html` | ruff hook + sanity checks on real output; discuss: when are tests worth it in a data pipeline? |
| 35–40 | Discussion: trust, costs (`opencode stats`) | |

Step 2 (spam) is optional – without it, steps 3–5 use the district check from step 1.

**Why two models?** Different jobs: Qwen3-Coder-Next is the cheapest model that works well as
a coding agent; gpt-oss-120b answers analysis prompts quickly and cleanly (100 answers →
10 categories in 4 s for €0.001, tested 2026-10-25). Both on IONOS: one provider, one key.
(GLM-5.3 on Scaleway gave the cleanest categories in our benchmark, but a second provider
made the setup more complex and it often thought until the output limit.)

**Rate limits:** all participants share IONOS' 5 requests/s per model. Analysis calls cost a
participant only cents with `--limit 100`.
