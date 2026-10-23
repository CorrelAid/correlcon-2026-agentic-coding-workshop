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

## 3. Suggest categories (10 min) – *skill `llm-categorization`, EU LLM from code*

> Use the llm-categorization skill: estimate the cost first, then let the LLM suggest
> 8–12 categories for the negative comments, based on a random sample of 100.

What to notice: cost estimate before the run; the call goes through `src/project/llm.py`
(EU endpoints only); categories are saved for human review.

## 4. Classify (10 min)

> Classify 200 random negative comments into these categories. Send 20 comments per
> request, validate the JSON with pydantic, cache results.

**Rate limit:** all participants share 5 requests/s per model. Batching 20 comments per
request plus a sample of 200 means ~10 requests per person and ~€0.01. Do **not** classify
all 1,974 texts one by one during the workshop.

## 5. Analyse & discuss (5 min)

> Plot the share of each category, overall and for the 5 most frequent districts.
> Save the chart to outputs/.

Discussion: Would you trust the categories? What would an NGO need to run this itself
(→ skill `ngo-handover`)? What did the session cost? (`opencode stats`)

## Reference

The original 2024 workshop with notebooks and prompts:
[CorrelAid/workshop-babylotse](https://github.com/CorrelAid/workshop-babylotse) (code GPL-3.0,
data CC BY 4.0).
