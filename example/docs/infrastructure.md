# Infrastructure: why IONOS, what it costs, how it performed

As of 2026-10-23. Prices are net list prices per 1M tokens. Not legal advice – each
organisation must check the DPA and terms itself.

## Requirements (in this order)

1. **Data stays in the EU** – contractually guaranteed, not "usually"
2. **No training on our data**, ideally no storage of prompts
3. **DPA (Art. 28 GDPR)** available, transparent sub-processors
4. **Coding-capable model** with reliable tool calling
5. **Cost**: pay-per-use, no base fee, affordable for NGOs in the long run
6. **Handover**: an NGO can sign its own contract and keep running the project

No local models: participants' laptops have no suitable GPUs, and renting GPU instances
means fixed costs, operations work and nothing an NGO could take over.

## Provider comparison

| Provider | Processing location | Training / storage | Coding model (in/out) | Verdict |
|---|---|---|---|---|
| **IONOS AI Model Hub** | German data centres only | no training; prompts neither logged nor stored; no sub-processors; BSI C5, ISO 27001 | Qwen3-Coder-Next 80B: €0.15 / €0.80 | ✅ **chosen** |
| **STACKIT AI Model Serving** | Germany (eu01) | not stored, not used for training; BSI C5 | no dedicated coding model; Qwen3.8 27B / gpt-oss-120b: €0.45 / €0.65 | ✅ German alternative |
| **OVHcloud AI Endpoints** | France (Gravelines) | per OVH: not stored, not used for training | gpt-oss-120b: €0.08 / €0.40 | ✅ cheapest, good fallback |
| **Scaleway Generative APIs** | France (Paris) | not used for training; prompts not stored (except up to 2 weeks for abuse investigation) | glm-5.3: €1.80 / €5.50; deepseek-v4-flash: €0.40 / €0.80 | ✅ **chosen for the topic model** (GLM-5.3); limits *tokens per minute* per organisation |
| **Mistral La Plateforme** | EU by default, US endpoint optional | **free plan may train on data**; opt-out on paid plan; some sub-processors outside EU (SCCs) | Devstral 2: ~$0.40 / $2.00 | 🟡 paid plan + documented opt-out only |
| **Nebius Token Factory** | public endpoints: **location dynamic, no region guarantee** | no training; without zero-data-retention, inputs/outputs stored (Finland) | many, cheap | ❌ EU-bound only with (pricey) dedicated endpoints |
| GitHub Copilot, OpenAI, Anthropic, OpenCode Zen | US / not guaranteed | – | – | ❌ out |

**On model origin:** the cheap, strong open-weight models mostly come from Chinese labs
(Qwen, GLM, DeepSeek) or OpenAI (gpt-oss). With EU hosting the *data* never leaves the EU –
the weights run on the provider's hardware. If the model itself should be European, use
Mistral (Devstral) with the caveats above. Worth a slide and a discussion.

## Costs

The only variable cost is tokens. OpenCode, uv and the Python packages are free; no
servers, no base fee.

A coding agent resends the conversation context with every step, so **input tokens
dominate**. EU providers barely offer cheaper cached input, so we calculate without
caching. Assumptions per person and hour of active use:

| Scenario | Input tokens | Output tokens |
|---|---|---|
| light | 1M | 30k |
| typical | 3M | 80k |
| heavy | 6M | 150k |

Reference measurement: one small real task (write function + tests, run pytest) took 46 s
and ~120k input + ~2k output tokens = **€0.02**.

### Workshop: 20 people × 1.5 h hands-on

| Provider | Model | In/Out per 1M | Workshop light | Workshop typical | Workshop heavy |
|---|---|---|---|---|---|
| IONOS (DE) | Qwen3-Coder-Next 80B | €0.15 / €0.80 | €5.22 | €15.42 | €30.60 |
| IONOS (DE) | gpt-oss-120b | €0.15 / €0.65 | €5.08 | €15.06 | €29.93 |
| IONOS (DE) | Qwen3.5-397B-A17B | €0.60 / €3.60 | €21.24 | €62.64 | €124.20 |
| STACKIT (DE) | Qwen3.8 27B | €0.45 / €0.65 | €14.09 | €42.06 | €83.92 |
| STACKIT (DE) | gpt-oss-120b | €0.45 / €0.65 | €14.09 | €42.06 | €83.92 |
| Scaleway (FR) | qwen3.6-35b-a3b | €0.25 / €1.50 | €8.85 | €26.10 | €51.75 |
| Scaleway (FR) | glm-5.3 | €1.80 / €5.50 | €58.95 | €175.20 | €348.75 |
| OVHcloud (FR) | gpt-oss-120b | €0.08 / €0.40 | €2.76 | €8.16 | €16.20 |
| OVHcloud (FR) | Qwen3.5-397B-A17B | €0.60 / €3.60 | €21.24 | €62.64 | €124.20 |
| Mistral (FR) | Devstral 2 | $0.40 / $2.00 | $13.80 | $40.80 | $81.00 |

**Budget:** ~€15 typical, **€35** covers the heavy scenario with margin.

### NGO project

Three volunteers × 10 h agent use per month = 30 person-hours, i.e. the same table:
roughly €5–30/month on IONOS.

### Analysis: LLM categorisation (Babylotse survey)

987 responses × 2 free-text fields = 1,974 texts, ~800 input + 40 output tokens each:

| Provider | Model | Cost |
|---|---|---|
| IONOS (DE) | Qwen3-Coder-Next 80B | €0.30 |
| IONOS (DE) | gpt-oss-120b | €0.29 |
| IONOS (DE) | Qwen3.5-397B-A17B | €1.23 |
| STACKIT (DE) | Qwen3.8 27B | €0.76 |
| STACKIT (DE) | gpt-oss-120b | €0.76 |
| Scaleway (FR) | qwen3.6-35b-a3b | €0.51 |
| Scaleway (FR) | glm-5.3 | €3.28 |
| OVHcloud (FR) | gpt-oss-120b | €0.16 |
| OVHcloud (FR) | Qwen3.5-397B-A17B | €1.23 |
| Mistral (FR) | Devstral 2 | $0.79 |

The analysis itself costs cents – the money goes into interactive agent work.

Regenerate these tables: `uv run python scripts/costs.py --markdown --texts 1974`.

## IONOS test results (2026-10-23, 1-hour test token, total test cost < €1)

### Models (from `/v1/models`) and tool calling

| Model ID | Tool calling | Response time* | €/1M in/out |
|---|---|---|---|
| `Qwen/Qwen3-Coder-Next` | ✅ | 0.4–1.2 s | 0.15 / 0.80 |
| `openai/gpt-oss-120b` | ✅ | 0.6 s | 0.15 / 0.65 |
| `Qwen/Qwen3.8-27B` | ✅ | 0.8 s | 0.40 / 2.70 |
| `Qwen/Qwen3.5-397B-A17B` | ✅ | 0.8–2.8 s | 0.60 / 3.60 |
| `Qwen/Qwen3.5-9B` | not tested | – | 0.10 / 0.15 |
| `mistralai/Mistral-Small-24B-Instruct` | not tested | – | 0.10 / 0.30 |

\* short request with one tool call. Also available: embeddings (`BAAI/bge-m3`, …),
reranker, OCR, image models.

### OpenCode end-to-end

Task "write `mask_contacts()` + tests, run pytest until green": done in **46 s**, 9 tests
green, one malformed tool call that the agent corrected itself, **~€0.02**.

### Rate limits

[IONOS docs](https://docs.ionos.com/cloud/ai/ai-model-hub/how-tos/rate-limits): **5 requests/s
per model per contract**, burst up to 10 (header `x-ratelimit-limit-requests: 5` confirms).
The limit is shared by everything on the contract.

| Test | Result |
|---|---|
| 20 requests at exactly the same moment (~12k tokens each) | 10 × OK after 3.4 s, 10 × `429` with `Retry-After: 1` |
| 20 simulated agents for 75 s, 2–8 s pause between steps, ~17k tokens context | **232 requests, 0 errors**, 3.1 req/s, wait per step median 1.7 s, max 4.4 s |

The simulation is harsher than reality (people read, think and type between tasks):
**the default limit is enough for 20 participants.** Session-title requests go to
`Qwen3.5-9B` (`small_model`) so they don't count against the coding model's limit.

## Restricted user test (2026-10-23)

Token of a user in a group with only "Access and manage AI Model Hub"
(`"role":"user"`, privileges `["ACCESS_AND_MANAGE_AI_MODEL_HUB"]`):

| Check | Result |
|---|---|
| AI Model Hub: list models, chat completion | ✅ 200 |
| Cloud API reads (data centres, k8s, IP blocks) | 200 but **empty** – only sees its own resources |
| User management reads | sees only itself and its own group |
| Create data centre / k8s cluster / IP block / user / group | ❌ **403 Access Denied** (missing privilege) |
| Contract info (`/contracts`) | readable (contract number, resource limits) – unavoidable |
| **Mint new tokens** (`/auth/v1/tokens/generate`) | ⚠️ **possible**, same rights, own TTL – tested with 60 s TTL, then deleted |

Conclusion: the restricted user cannot create infrastructure, so the cost exposure is
limited to AI Model Hub usage. Because a leaked token can mint fresh tokens, **TTL is not a
reliable kill switch – deactivating the user is.**

## Cost control on IONOS

There is **no self-service hard spending cap**.

| Feature | What it does | Limits |
|---|---|---|
| Cost Alert (DCD → Management → Cost alert) | e-mail when the invoice amount (net) reaches a threshold | fires **once**, one address, **blocks nothing**, owner/admin only |
| Cost & Usage (DCD → Management → Cost & Usage) | cost per product, current or past month | monthly only, no split per user/token, up to **24 h delay** |
| Billing API (`usage-alert` endpoints) | automate alerts and usage queries | same delay, no real-time stop |
| Cost limit via account manager | mentioned in IONOS FAQ | details unclear – **ask** |

**Worst case for a leaked token:** 5 req/s × 256k context × €0.15/1M ≈ **€0.19/s ≈ €690/h**.
Hence: restricted user, short TTL, and **deactivate the user after use** (tokens can mint
new tokens, so TTL alone does not stop a leaked token). For long-running projects a
gateway (e.g. LiteLLM proxy with per-key budgets) gives a real cap – but needs its own
server and maintenance.

## Open questions

| Question | Status |
|---|---|
| Cost breakdown per project/user/token? | not in the docs – ask IONOS; workaround: one IONOS user per project |
| Hard spending limit? | ask the account manager |
| DPA signed / where stored? | check customer area |
| Burst: docs say 10 and 20 requests per 2 s | measured ≈ 10 |

## Handover to an NGO

1. The NGO opens its own IONOS Cloud account and signs the DPA.
2. Restricted user + token as in `SETUP.md` §2.2, token into `.env`, run `check_setup.py`.
3. CorrelAid removes / deactivates its own tokens.

For the NGO's record of processing activities: processor IONOS (Germany); processing in
German data centres; purpose: categorising pseudonymised free text and coding assistance;
no content stored by the provider (metadata only: time, model, token count); no training.

Running costs for the NGO: analyses cost cents; developing further with the agent costs
roughly €0.50 per hour of active use.

## Sources

- IONOS data handling: <https://docs.ionos.com/cloud/ai/ai-model-hub/governance-and-compliance/data-handling>
- IONOS price list: <https://docs.ionos.com/cloud/support/general-information/price-list/ionos-cloud-gmbh-de>
- IONOS Qwen3-Coder-Next: <https://docs.ionos.com/cloud/ai/ai-model-hub/models/coding-models/qwen3-coder-next-80b>
- IONOS access management: <https://docs.ionos.com/cloud/ai/ai-model-hub/how-tos/access-management>
- IONOS rate limits: <https://docs.ionos.com/cloud/ai/ai-model-hub/how-tos/rate-limits>
- IONOS cost alert: <https://docs.ionos.com/cloud/set-up-ionos-cloud/management/usage/cost-alert>
- IONOS cost & usage: <https://docs.ionos.com/cloud/set-up-ionos-cloud/management/usage/cost-and-usage>
- IONOS billing FAQ: <https://docs.ionos.com/cloud/support/faq/costs-and-billing>
- STACKIT: <https://stackit.com/en/products/data-ai/stackit-ai-model-serving>
- OVHcloud catalogue: <https://www.ovhcloud.com/nl/public-cloud/ai-endpoints/catalog>
- OVHcloud capabilities: <https://docs.ovhcloud.com/en/guides/public-cloud/ai-machine-learning/ai-endpoints-capabilities>
- Scaleway pricing: <https://scaleway.com/en/pricing/model-as-a-service>
- Mistral training opt-out: <https://help.mistral.ai/en/articles/347614-can-i-opt-out-of-my-input-or-output-data-being-used-for-training>
- Nebius legal quick guide: <https://docs.tokenfactory.nebius.com/legal/legal-quick-guide>
- European LLM API comparison (WZ-IT): <https://wz-it.com/en/blog/european-llm-api-comparison/>
