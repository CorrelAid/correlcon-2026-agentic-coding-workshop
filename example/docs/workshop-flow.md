# Workshop flow: Babylotse survey with a coding agent

Five exercises, each one a prompt for OpenCode (started in `example/`). Each step
shows one best practice from the talk. Times are rough guides for 40 minutes.

Before you start: `uv run python scripts/get_data.py` (prints row count and column names only).

## 1. Explore without looking (5 min) – *AGENTS.md*

> Write `src/project/explore.py` that prints for the Babylotse survey: number of rows,
> missing values per column, the 10 most frequent districts and the length distribution of
> both free-text columns. Do not print any free-text content. Run it.

What to notice: the agent knows the columns from `AGENTS.md` without opening the raw file.
It will likely spot the HTML entities in the district column (`H&ouml;chst`).

## 2. Pseudonymise (10 min) – *skill `privacy-check` + hooks*

> Use the privacy-check skill to create a pseudonymised version of the survey in
> data/processed/. Decode the HTML entities in the district column, too.

What to notice:
- The skill is loaded on demand and drives the procedure (summary first, mask emails and
  phone numbers, add a test, document).
- Ask the agent to "show me the first rows of the raw file": the **privacy hook** blocks it.
- The **ruff hook** feeds lint errors back to the agent after each edit.

## 3. Suggest categories (10 min) – *skill `llm-categorization`, two models*

> Use the llm-categorization skill, phase 1: draw a sample of 100 negative comments from
> the pseudonymised data (seed 42, save it), send it to the topic model and save at most 10
> categories. Estimate the cost first.

What to notice: **two models, two jobs.** The agent (Qwen3-Coder-Next on IONOS) writes the
code; the code asks the topic model (GLM-5.3 on Scaleway) – one request, a few cents.
In our benchmark (`../benchmark/RESULTS.md`) the cheap coder was the best value as agent,
while GLM-5.3 produced the cleanest category sets in our review (fewer overlaps). The
skill now also asks for a bucket for non-answers – ~20 % of the comments are spam or empty.

## 4. Classify (10 min) – *follow-up task*

> Phase 2: classify the negative comments of 200 random rows into the reviewed categories.
> Send 20 comments per request, validate with pydantic, cache results.

**Rate limit:** Scaleway limits tokens per minute for the whole organisation, shared by all
participants. 200 comments = ~10 requests per person. For all ~990 comments use the Batch
API (no limit, −50 %) – a good discussion point, not a live exercise.

## 5. Analyse & discuss (5 min)

> Plot the share of each category, overall and for the 5 most frequent districts.
> Save the chart to outputs/.

Discussion: Would you trust the categories? What would an NGO need to run this itself
(→ skill `ngo-handover`)? What did the session cost? (`opencode stats`)

## Reference

The original 2024 workshop with notebooks and prompts:
[CorrelAid/workshop-babylotse](https://github.com/CorrelAid/workshop-babylotse) (code GPL-3.0,
data CC BY 4.0).
