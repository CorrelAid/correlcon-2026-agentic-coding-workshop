# Setup: OpenCode + IONOS AI Model Hub

Hands-on setup for the CorrelCon 2026 session *Coding Agents and Best Practices*.

| Part | For whom | Time |
|---|---|---|
| [1. Participants](#1-participants) | everyone in the workshop | ~10 min |
| [2. Organisers: IONOS](#2-organisers-ionos) | whoever owns the IONOS contract | ~20 min, once |
| [3. What's in `example/`](#3-whats-in-example) | anyone reusing this in an NGO project | reading |
| [4. Troubleshooting](#4-troubleshooting) | everyone | – |

Background (provider comparison, costs, load test, cost control):
[`example/docs/infrastructure.md`](example/docs/infrastructure.md).

**Two models, two jobs – one provider (IONOS), one key:**

| Job | Model | Hosted by | Why |
|---|---|---|---|
| **Coding agent** – writes wrappers, scaffolds, tests | `Qwen/Qwen3-Coder-Next` in [OpenCode](https://opencode.ai) | IONOS, Germany | fastest and cheapest agent in our benchmark |
| **Analysis model** – spam check, categories, classification (called from project code) | `openai/gpt-oss-120b` | IONOS, Germany | fast, clean JSON answers; fractions of a cent per call |

Both: open-weight models, EU data centres, no training on your data, pay per token, no GPU
needed. Benchmark: [`benchmark/RESULTS.md`](benchmark/RESULTS.md).

---

## 1. Participants

### Step 1 – Install two tools (before the workshop, please)

macOS / Linux / Windows with WSL:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh     # Python tooling (uv)
curl -fsSL https://opencode.ai/v2/install | bash    # coding agent (OpenCode 2)
```

Alternatives: `brew install anomalyco/tap/opencode-v2` (macOS) · `npm install -g @opencode/cli`
· Windows: `winget install --id Anomaly.OpenCode -e`. Already on OpenCode 1.x? `opencode upgrade --major`.
WSL is recommended on Windows – the example's hooks are tested on Linux/macOS.

Windows without WSL, uv: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`.

Restart your terminal, then check: `uv --version` and `opencode --version` (must show 2.x).

### Step 2 – Get the code and add the key

```bash
git clone https://github.com/CorrelAid/correlcon-2026-agentic-coding-workshop
cd correlcon-2026-agentic-coding-workshop/example
cp .env.example .env
```

Open `.env` and paste the workshop key (you get it on site) after `IONOS_API_KEY=`. The coding
agent and the code it writes both use it (`LLM_API_KEY=${IONOS_API_KEY}`).

### Step 3 – Check and start

```bash
uv sync
uv run python scripts/check_setup.py
```

All green? Then start the agent:

```bash
uv run agent
```

`uv run agent` starts OpenCode 2 from the `example/` folder with the keys from `.env` and
`--standalone` – on every OS, from any subfolder, even if your shell exports older keys.
(Plain `opencode` fails with `401`: it does not read `.env`, and OpenCode 2 normally talks to
a shared background service that knows nothing about this project's keys.)

Try it: *"Write a function in src/project/text.py that masks email addresses and phone
numbers, add tests and run them."* (≈ 45 s, ≈ €0.02)

> **Please:** only use public or synthetic data with the workshop keys. They run on
> CorrelAid's accounts and expire at the end of the day.

---

## 2. Organisers: IONOS

### 2.1 Contract

- IONOS Cloud account **on CorrelAid** (not a private person) with a payment method.
- Check / sign the **data processing agreement (DPA / AVV)** in the customer area.

### 2.2 A restricted user for the AI Model Hub (do not skip)

The **Token Manager cannot restrict permissions** – a token always carries the rights of
the user who created it. A token created as contract owner can manage *everything* on the
contract (data centres, Kubernetes, DNS, …) – and the workshop token is shared with ~20
people. A separate user takes ~5 minutes once, can be reused for later projects, and
deactivating it invalidates all its tokens immediately. So:

1. As owner: **User Manager → Groups → Create** – e.g. `ai-model-hub-only`, tick only
   **"Access and manage AI Model Hub"**.
2. **Users → Create** – e.g. `correlcon-workshop`, add it to the group.
3. **Log in as that user** → Management → **Token Manager** → choose a **TTL** →
   *Generate Token* → copy it right away (shown only once).

**TTL** (time to live) = how long the token is valid. Suggested values:

| Use | TTL |
|---|---|
| Quick tests | 1 h |
| Workshop | the workshop day only (6–8 h), created the day before |
| NGO project | a few months + calendar reminder to renew |

**Check the token:** it is a JWT starting with `eyJ`. Decode the middle part (e.g. on
[jwt.io](https://jwt.io)): it should contain `"role":"user"` and only
`ACCESS_AND_MANAGE_AI_MODEL_HUB` – **not** `"role":"owner"`. The short UUID shown in the
Token Manager is only the token *ID* (for deleting it), not the API key.

### 2.3 Cost control

IONOS has **no self-service hard spending cap** (as of Oct 2026). Do this instead:

1. **Cost Alert** (DCD → Management → Cost alert): e-mail at e.g. **€40**. It fires
   **once** and **does not block** anything.
2. **Short TTL** – limits how long a token works. The only technical ceiling is the rate
   limit (5 requests/s per model); a leaked token could theoretically burn **~€690/hour**.
3. **But TTL alone is not enough:** any valid token can mint *new* tokens for the same user
   via the Auth API (`/auth/v1/tokens/generate`, tested 2026-10-23), with their own TTL.
   So after the workshop **deactivate the workshop user** (or delete all its tokens) –
   that stops every token, including any minted ones.
4. Ask the IONOS account manager about a contractual cost limit (mentioned in their FAQ).

Expected workshop cost (measured ~€0.01 per agent step, see
[`infrastructure.md`](example/docs/infrastructure.md#workshop-20-people-hands-on-part)):
**~€40 typical, ~€65 heavy** for 20 people; the analysis model adds only cents.

### 2.4 Smoke test (no Python needed)

```bash
curl -s https://openai.inference.de-txl.ionos.com/v1/models \
  -H "Authorization: Bearer $TOKEN" | grep -o '"id":"[^"]*"'
```

`Qwen/Qwen3-Coder-Next` must be in the list.

### 2.5 Checklist

- [ ] Restricted user + group created, token decoded and checked (`"role":"user"`)
- [ ] Cost Alert set
- [ ] Workshop token created the day before, TTL = workshop day
- [ ] Participants e-mailed: please do step 1 beforehand
- [ ] Token shared on site only (slide / whiteboard), never committed or posted publicly
- [ ] Afterwards: workshop user **deactivated** (not just waiting for the TTL), actual cost
      added to `example/docs/infrastructure.md`

---

## 3. What's in `example/`

Three layers of control – the core message of the talk:

| Layer | File | Behaviour |
|---|---|---|
| **Instructions** | `AGENTS.md` | Tells the agent the project rules. Usually followed – not guaranteed. Cross-tool standard. |
| **Skills** | `.agents/skills/*/SKILL.md` | Procedures loaded on demand: `privacy-check`. Cross-tool folder. |
| **Policies** | `opencode.json` → `policies` | Hard rules nothing can override: only the IONOS provider; no reading `.env`, `data/raw/`, `data/interim/` – not even via the shell; no running the pipeline scripts (paid API calls on real data); no editing the workshop prompts in `prompts/`; no Code Mode; no web search. |
| **Permissions** | `opencode.json` → `permissions` | Shell commands need approval (except tests, ruff, the setup check, `git status`, …); web fetches ask; sharing off. |
| **Hooks** | `.opencode/plugins/guardrails.ts` | What policies can't express: blocks glob/grep searches in protected folders, hides both API keys from the agent's shell, runs `ruff` after every Python edit and feeds errors back to the agent. |

Supporting code:

- `src/project/llm.py` – the only way project code talks to an LLM (the analysis model, set in
  `.env`); refuses non-approved (non-EU) endpoints.
- `scripts/check_setup.py` – checks both models incl. tool calling (< €0.01).
- `scripts/costs.py` – cost calculator for workshop, projects and batch runs.

**Why OpenCode restricts providers:** OpenCode offers its own "Zen" models and any provider it
finds credentials for (e.g. AWS keys in your environment). The policy `provider.use: * → deny,
ionos → allow` turns everything else off – verify with `opencode models` inside `example/`.

**Models configured** (verified 2026-10-23/24; config tested with OpenCode 2.1.4):

| Model | Role | € in/out per 1M tokens |
|---|---|---|
| `Qwen/Qwen3-Coder-Next` | default coding agent | 0.15 / 0.80 |
| `openai/gpt-oss-120b` | analysis model in project code (`LLM_MODEL_ANALYSIS`) | 0.15 / 0.65 |
| `Qwen/Qwen3.5-397B-A17B` | hard tasks (`/models` in OpenCode) | 0.60 / 3.60 |

---

## 4. Troubleshooting

| Symptom | Fix |
|---|---|
| You see your own / other providers' models | OpenCode was started outside `example/` – the project config is only found from that folder. `cd example` first, then check with `opencode models` (only `ionos/…` should appear). Your global `~/.config/opencode` config can stay as it is. |
| `401 Unauthorized` | Token expired (TTL) or you pasted the token ID (UUID) instead of the token (`eyJ…`). |
| `401` when starting OpenCode | Started without the keys: use `uv run agent`. Plain `opencode` doesn't read `.env`, and OpenCode 2's background service doesn't see keys from your shell (`uv run agent` uses `--standalone`). |
| `429 Too Many Requests` | Rate limit (5 req/s per model, shared by everyone). OpenCode retries automatically after ~1 s. |
| Analysis model returns empty content (`finish_reason: length`) | The model thought until the output limit: pass `reasoning_effort="low"` and `max_tokens=8000`. |
| `529 … server_overloaded` | IONOS platform load – wait, or switch model with `/models` (e.g. `gpt-oss-120b`). |
| Agent says "Blocked by configuration policy" | Working as intended: a policy in `opencode.json` forbids the command (e.g. reading `data/interim/`). |
| Agent says "Access denied (privacy hook)" | Working as intended: it tried to read `data/raw/` or `.env`. |
| First start hangs for a minute | OpenCode installs plugin dependencies once; needs access to the npm registry. |
