# Infrastructure: why IONOS, what it costs, how it performed

As of 2026-10-23. Prices are net list prices per 1M tokens. Not legal advice – each
organisation must check the DPA and terms itself.

## Requirements (in this order)

1. **Data stays in the EU** – contractually guaranteed, not "usually"
2. **No training on our data**, ideally no storage of prompts
3. **DPA (Art. 28 GDPR)** available, transparent sub-processors
4. **Coding-capable model** with reliable tool calling
5. **Cost**: pay-per-use, no base fee, affordable for NGOs in the long run
6. **Reusable by NGOs**: the same setup works with an NGO's own contract – no CorrelAid-specific parts

No local models: participants' laptops have no suitable GPUs, and renting GPU instances
means fixed costs and operations work – not a setup a typical NGO could run.

## Provider comparison

| Provider | Processing location | Training / storage | Coding model (in/out) | Verdict |
|---|---|---|---|---|
| **IONOS AI Model Hub** | German data centres only | no training; prompts neither logged nor stored; no sub-processors; BSI C5, ISO 27001 | Qwen3-Coder-Next 80B: €0.15 / €0.80 | ✅ **chosen** |
| **STACKIT AI Model Serving** | Germany (eu01) | not stored, not used for training; BSI C5 | no dedicated coding model; Qwen3.8 27B / gpt-oss-120b: €0.45 / €0.65 | ✅ German alternative |
| **OVHcloud AI Endpoints** | France (Gravelines) | per OVH: not stored, not used for training | gpt-oss-120b: €0.08 / €0.40 | ✅ cheapest, good fallback |
| **Scaleway Generative APIs** | France (Paris) | not used for training; prompts not stored (except up to 2 weeks for abuse investigation) | glm-5.3: €1.80 / €5.50; deepseek-v4-flash: €0.40 / €0.80 | ✅ good alternative (GLM-5.3 gave the cleanest categories in our benchmark); limits *tokens per minute* per organisation |
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

A coding agent resends the whole conversation with every step (tool call), so **input
tokens dominate**. IONOS has no prompt caching (`opencode stats`: cached input 0 %), so every
step pays for the full context. Providers with caching would be cheaper than shown below.

**Measured** (`opencode stats --cost`, IONOS, Qwen3-Coder-Next, fresh session per pipeline step):

| Run | Agent steps | Tokens | Cost |
|---|---|---|---|
| 2026-10-25, prep day | 526 | 28.7M in + 172k out | €4.44 |
| 2026-10-26, finishing step 4 (multi-label rework + error fixes) | 302 | 19.6M in + 55k out | €2.99 |
| Both days, 21 sessions, steps 2–5 incl. retries | ~1,500 | 90.9M | ≈ €13.60 |

So **~60k input tokens per agent step ≈ €0.01** on average – but that average comes from long
sessions with debugging and rework. **A clean run of one pipeline step costs €0.08–0.15**
(2026-10-26, step 4 run twice from a fresh session: 23 and 30 agent steps, context growing from
7k to 28–35k tokens, €0.08 and €0.12; step 3 in the full run: €0.15). A step where the agent
struggles with errors can cost €1–3. A participant with smooth steps 2–5 therefore costs ~€0.50,
20 people ~€10; the estimates below are the upper bound when many get stuck.

A lower context limit (64k instead of 256k, so OpenCode compacts earlier) made no difference:
clean runs never got near it.

Only ~7k tokens of that are fixed (OpenCode system prompt, 12 tool definitions, AGENTS.md –
measured with a mock server). The rest is file contents, test and command output that pile
up within a session. Levers: a fresh session per pipeline step, short outputs (`pytest -q`),
reading only the files needed.

### Workshop: 20 people, hands-on part

Assumption: 100 / 200 / 350 agent steps per person. Time caps it: at ~5–10 s per step, 40 min of
active work is at most ~250–350 steps.

| Provider | Model | In/Out per 1M | Workshop light | Workshop typical | Workshop heavy |
|---|---|---|---|---|---|
| IONOS (DE) | Qwen3-Coder-Next 80B | €0.15 / €0.80 | €18.48 | €36.96 | €64.68 |
| IONOS (DE) | gpt-oss-120b | €0.15 / €0.65 | €18.39 | €36.78 | €64.36 |
| IONOS (DE) | Qwen3.5-397B-A17B | €0.60 / €3.60 | €74.16 | €148.32 | €259.56 |
| STACKIT (DE) | Qwen3.8 27B | €0.45 / €0.65 | €54.39 | €108.78 | €190.37 |
| STACKIT (DE) | gpt-oss-120b | €0.45 / €0.65 | €54.39 | €108.78 | €190.37 |
| Scaleway (FR) | qwen3.6-35b-a3b | €0.25 / €1.50 | €30.90 | €61.80 | €108.15 |
| Scaleway (FR) | glm-5.3 | €1.80 / €5.50 | €219.30 | €438.60 | €767.55 |
| OVHcloud (FR) | gpt-oss-120b | €0.08 / €0.40 | €9.84 | €19.68 | €34.44 |
| OVHcloud (FR) | Qwen3.5-397B-A17B | €0.60 / €3.60 | €74.16 | €148.32 | €259.56 |
| Mistral (FR) | Devstral 2 | $0.40 / $2.00 | $49.20 | $98.40 | $172.20 |

**Budget:** ~€40 typical, **€65** covers the heavy scenario. The analysis model (gpt-oss-120b on
IONOS, steps 2–4 with `--limit 100`) adds only cents per person.

### NGO project

≈ **€8.50 per 1,000 agent steps** on IONOS. Three volunteers with ~300 steps each per month
(a few focused sessions) ≈ €8/month; heavy use (1,000 steps each) ≈ €25/month.

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
`Qwen3.5-9B` (`small_model`, OpenCode 1.x only) so they don't count against the coding model's limit.

### Parallel agents: IONOS vs. Scaleway (2026-11-13)

Simulated agents: each sends a request with ~20k tokens of context, then waits 4–8 s (tool
execution), like OpenCode during a pipeline step. No retries, so every 429 is counted.

| Parallel agents | IONOS (Qwen3-Coder-Next) | Scaleway (deepseek-v4-flash-0731) |
|---|---|---|
| 1 | 0 errors, 158k tokens/min | 0 errors |
| 2 | – | 0 errors, 309k tokens/min |
| 4–5 | 0 errors, 780k tokens/min | **12 of 21 requests rate-limited** |
| 10 | 0 errors, 1.4M tokens/min | – |
| 20 | **0 errors, 2.9M tokens/min**, latency 0.3 s | – |

Scaleway's response headers show the account limit: `x-ratelimit-limit-tokens: 200000` per
minute (300 requests/min) for this model – enough for ~2 active agents. More needs identity
verification or a quota request. Scaleway also reported `cached_tokens: 0` for repeated
prefixes, so the advertised cached-input price did not apply in our test.

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
