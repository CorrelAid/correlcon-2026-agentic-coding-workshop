# Pipeline: Babylotse survey, step by step

```
raw survey ─▶ 1 prepare ─▶ 2 spam ─▶ 3 PII ─▶ 4 topics ─▶ 5 classify ─▶ 6 report
 (data/raw)   ready-made   agent     agent    agent       agent         agent
              no LLM       GLM-5.3   regex    GLM-5.3     GLM-5.3       no LLM
                                     (+GLM)   1 request   batches of 20
```

The **agent** (Qwen3-Coder-Next in OpenCode) writes the code for steps 2–6 from the
prompts in `prompts/`. The **code** then calls the topic model (GLM-5.3) via
`src/project/llm.py`. Each step reads the previous step's file and writes its own, so
steps can be re-run independently.

| Step | Code | Run | Output |
|---|---|---|---|
| 0 | `scripts/get_data.py` | ready | `data/raw/babylotse_survey_2024.csv`, `data/reference/ffmstadtteilewahlen.geojson` |
| 1 | `src/project/prepare.py`, `districts.py` | ready | `data/interim/01_prepared.csv` |
| 2 | `src/project/spam.py` | agent | `data/interim/02_spam.csv` |
| 3 | `src/project/pii.py` | agent | `data/processed/03_clean.csv` |
| 4 | `src/project/topics.py` | agent | `data/processed/04_sample.csv`, `categories_v1.json` |
| 5 | `src/project/classify.py` | agent | `data/processed/05_classified.csv` |
| 6 | `src/project/report.py` | agent | `outputs/report.html` |

`data/raw/` and `data/interim/` may contain personal data: the agent never reads them
(hooks block it) – it writes code that processes them. From step 3 on, data lives in
`data/processed/`, which the agent may inspect.

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
| `spam_reason` | short reason from the model (or `unknown district`) |
| `spam_source` | `llm`, `district`, `both` or empty |

**03_clean.csv** – only rows with `is_spam == False`, columns of 01 (without
`district_known`), plus `pii_flag` (bool) and `pii_types` (e.g. `phone;name`).

**04_sample.csv** – `row_id`, `polarity` (`positive`/`negative`), `text` – the fixed sample.
**categories_v1.json** – list of `{"name": …, "description": …}`, at most 10, reviewed by a human.

**05_classified.csv** – one row per non-empty answer (long format)

| column | meaning |
|---|---|
| `row_id`, `polarity`, `text` | the answer |
| `category` | one name from `categories_v1.json` or `Keine inhaltliche Aussage` |
| `model`, `prompt_version` | provenance |

## Original

District mapping and regions: the 2024 CorrelAid pipeline
([workshop-babylotse](https://github.com/CorrelAid/workshop-babylotse), GPL-3.0).
