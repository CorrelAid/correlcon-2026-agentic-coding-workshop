# Pipeline: Babylotse survey, step by step

```
raw survey ─▶ 1 prepare ─▶ 2 spam ─▶ 3 topics ─▶ 4 classify ─▶ 5 report
 (data/raw)   ready-made   agent     agent       agent         agent
              no model     rules or  gpt-oss     gpt-oss       no analysis
                           gpt-oss   1 request   batches of 20 model
                           (bonus)
```

The **agent** (Qwen3-Coder-Next in OpenCode) writes the code for steps 2–5 from the
prompts in `prompts/`. The **code** then calls the analysis model (gpt-oss-120b, also on IONOS) via
`src/project/llm.py`. Each step reads the previous step's file and writes its own, so
steps can be re-run independently.

| Step | Code | Run | Output |
|---|---|---|---|
| 0 | `scripts/get_data.py` | ready | `data/raw/babylotse_survey_2024.csv`, `data/reference/ffmstadtteilewahlen.geojson` |
| 1 | `src/project/prepare.py`, `districts.py` | ready | `data/interim/01_prepared.csv` |
| 2 | `src/project/spam.py` | agent | `data/interim/02_spam.csv` |
| 3 | `src/project/topics.py` | agent | `data/processed/03_sample.csv`, `categories_v1.json` |
| 4 | `src/project/classify.py` | agent | `data/processed/04_classified.csv` |
| 5 | `src/project/report.py` | agent | `outputs/report.html` |

`data/raw/` and `data/interim/` may contain personal data: the agent never reads them
(hooks block it) – it writes code that processes them. Step 1 masks e-mails, phone numbers
and URLs; names or addresses in free text are not masked. From step 3 on, results live in
`data/processed/`, which the agent may inspect – fine for this public demo data; with real
personal data, add a privacy check first (skill `privacy-check`).

## File contracts

**01_prepared.csv** – one row per survey response (987)

| column | meaning |
|---|---|
| `row_id` | 1…987, stable key for all later steps |
| `month` | `YYYY-MM` (date coarsened) |
| `district` | official Frankfurt district, `Frankfurt` (no detail) or `SPAM` (not mappable) |
| `region` | `Nord`, `Mitte`, `Ost`, `West`, `Süd`, `Umland` or empty |
| `district_known` | `False` if district is `SPAM` – a first spam signal |
| `positive`, `negative` | free text, HTML decoded, e-mails/phones/URLs masked |

**02_spam.csv** – all columns of 01, plus

| column | meaning |
|---|---|
| `is_spam` | `True` if the whole response is spam / has no usable content |
| `spam_reason` | short reason (the rule that fired, or the model's reason) |

**Valid answers (input of steps 3–5)** – `load_valid_answers()` (`src/project/data.py`,
written in step 3): `02_spam.csv` with `is_spam == False`; if step 2 was skipped,
`01_prepared.csv` with `district_known == True` – a rough fallback that catches most spam
but also drops some real answers with an unmappable district.

**03_sample.csv** – `row_id`, `polarity` (`positive`/`negative`), `text` – the fixed sample.
**categories_v1.json** – list of `{"name": …, "description": …}`, at most 10, reviewed by a human.

**04_classified.csv** – one row per non-empty answer (long format), multi-label

| column | meaning |
|---|---|
| `row_id`, `polarity`, `text` | the answer |
| `categories` | all names from `categories_v1.json` that apply, joined by `;` (usually 1–3), or only `Keine inhaltliche Aussage` |
| `model`, `prompt_version` | provenance |

## Original

District mapping and regions: the 2024 CorrelAid pipeline
([workshop-babylotse](https://github.com/CorrelAid/workshop-babylotse), GPL-3.0).
