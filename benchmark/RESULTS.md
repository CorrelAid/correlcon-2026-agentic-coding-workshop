# Model benchmark: OpenCode + EU-hosted models (2026-10-24)

Four open-weight models, each driving **OpenCode** with the unchanged `example/` setup
(AGENTS.md, skills, hooks, permissions). The agent got one prompt per task and worked
autonomously – it wrote all code itself. Raw results: `results_2026-10-24.json`.

| Model | Provider | € in / out per 1M tokens |
|---|---|---|
| Qwen3-Coder-Next 80B | IONOS (DE) | 0.15 / 0.80 |
| Qwen3.8-27B | IONOS (DE) | 0.40 / 2.70 |
| DeepSeek V4 Flash (0731) | Scaleway (FR) | 0.40 / 0.80 · cached input 0.08 |
| GLM-5.3 | Scaleway (FR) | 1.80 / 5.50 |

## Tasks

1. **Privacy** – use the `privacy-check` skill to pseudonymise all 987 survey answers:
   mask e-mails, phone numbers and URLs in both free-text columns, decode HTML entities in
   the district column, drop/hash the ID, coarsen the date, add a test.
   Ground truth in the raw data: 1 e-mail, 2 phone numbers (Latvian format, e.g.
   `+371 25 …`), 36 URLs.
2. **Categories** – use the `llm-categorization` skill: from a **fixed** sample of 100
   negative comments (same file for every model, seed 20261114) let the LLM propose at most
   10 top-level categories, save as JSON, add a test. The project code calls the same model.

2 runs per model and task (GLM-5.3 privacy: 3, see below). Total cost of all 17 runs: **€11.24**.

## Results

| Model | Task | Median time | Avg steps | Avg cost | Tests green | Result correct |
|---|---|---|---|---|---|---|
| Qwen3-Coder-Next | privacy | 104 s | 23 | €0.08 | 2/2 | **2/2** – all PII masked |
| Qwen3.8-27B | privacy | 415 s | 26 | €0.27 | 2/2 | 1/2 – phone numbers left in one run |
| DeepSeek V4 Flash | privacy | 95 s | 17 | €0.12 | 2/2 | 0/2 – 1–2 phone numbers left |
| GLM-5.3 | privacy | 157 s | 16 | €1.07 | 3/3 | 1/3 – run 1 no output*, run 2 phone numbers left |
| Qwen3-Coder-Next | categories | 97 s | 28 | €0.10 | 2/2 | 2/2 (10 categories) |
| Qwen3.8-27B | categories | 282 s | 22 | €0.22 | 2/2 | 2/2 (9–10) |
| DeepSeek V4 Flash | categories | 318 s | 24 | €0.19 | 2/2 | 2/2 (10) |
| GLM-5.3 | categories | 492 s | 48 | €3.03 | 2/2 | 2/2 (10) |

\* GLM-5.3 run 1 hit the output-token limit while reasoning (benchmark config had no
output limit set; Scaleway caps GLM-5.3 at 16,384 output tokens). Fixed for run 3.

Across **all 17 runs**: tests passed, `ruff` clean, every run stayed on the configured EU
provider, and **no raw PII ever reached the agent's context** – in 6 runs the agent tried
to look at `data/raw/` and the privacy hook blocked it.

### Categories (fixed sample, first run per model)

| Qwen3-Coder-Next | Qwen3.8-27B | DeepSeek V4 Flash | GLM-5.3 |
|---|---|---|---|
| Kinderbetreuung | Betreuung & Kita | Kita & Betreuung | Kinderbetreuung & Kita-Plätze |
| Barrierefreiheit | Barrierefreiheit & Mobilität | Barrierefreiheit & Mobilität | Mobilität & Verkehr |
| Spielplätze und Freizeitangebote | Spielplätze & Freiräume | Spielplätze & Freizeit | Spielplätze |
| Öffentlicher Raum und Sauberkeit | Sauberkeit & Sicherheit | Sauberkeit & Sicherheit | Sauberkeit & Sicherheit |
| Mobilität und Verkehr | Kurse & Aktivitäten | Verkehr & Straßen | Angebote, Kurse & Indoor-Spielplätze |
| Wohnen und Lebenshaltungskosten | Wohnen & Kosten | Wohnen | Wohnen & Lebenshaltungskosten |
| Gesundheit und med. Versorgung | Gesundheit & Versorgung | Gesundheitsversorgung | Gesundheitsversorgung |
| Gastronomie und öffentl. Einrichtungen | Gastronomie & Örtlichkeiten | Gastronomie & Stillmöglichkeiten | Gastronomie & Cafés |
| Sicherheit und gesellschaftl. Klima | Sonstiges | Gesellschaft & Akzeptanz | Wickeln, Stillen & Toiletten |
| Information und Transparenz | – | Angebote & Kurse | Keine inhaltliche Aussage |

The category sets are **very similar** – childcare, accessibility/mobility, playgrounds,
cleanliness/safety, housing, health and gastronomy appear everywhere. Differences are in
the long tail (e.g. GLM-5.3 separates changing/nursing facilities and adds a bucket for
non-answers). Qwen3-Coder-Next's second run used problem-framed names
("Kita/Krippen-Platzmangel") instead of neutral ones.

## Findings

1. **For these tasks, the cheapest model did as well as the most expensive one.**
   Qwen3-Coder-Next was fastest, cheapest and the only one that masked all phone numbers in
   both runs. GLM-5.3 was 10–30× more expensive without better results here.
2. **Green tests ≠ correct result.** In 4 of the 8 privacy runs that produced output, the agent wrote its own regex
   and its own test – both passed – yet unusual phone formats slipped through. The fix is
   not a better model but a **human-written test with the hard cases** (spec first).
3. **Guardrails worked with every model.** Hooks and permissions kept raw data and secrets
   out of the context regardless of model quality.
4. **Rate limits matter more than model choice for a workshop.** Scaleway limits
   *tokens per minute* per organisation: 200k with a payment method, 1–2M after identity
   verification (Organisation quotas). An agent sends 20–60k tokens per step, so 20
   participants need identity verification or an agreed quota. IONOS limits requests
   (5/s per model) and did not throttle 20 simulated agents.

## Caveats

- 2 runs per cell – enough to see big differences, not to rank close ones.
- Agent token cost only; the LLM calls made by the generated code (categories task) are
  not counted (≈100 short comments per run, a few cents).
- GLM-5.3 cached tokens are billed at the full input price (Scaleway lists no cache price).
- Benchmarks used OpenCode 1.19.4 with the `example/` configuration of 2026-10-24.

## Reproduce

```bash
cd benchmark
python prepare_reference.py
IONOS_API_KEY=... SCALEWAY_API_KEY=... SCALEWAY_PROJECT_ID=... python run_bench.py --reps 2
python analyze.py
```
