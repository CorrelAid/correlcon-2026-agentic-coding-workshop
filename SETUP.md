# Setup: OpenCode + IONOS AI Model Hub

Hands-on setup for the CorrelCon 2026 session *Coding Agents and Best Practices*.

| Part | For whom | Time |
|---|---|---|
| [1. Participants](#1-participants) | everyone in the workshop | ~10 min |
| [2. Organisers: IONOS](#2-organisers-ionos) | whoever owns the IONOS contract | ~20 min, once |
| [3. What's in `example/`](#3-whats-in-example) | anyone reusing this in an NGO project | reading |
| [4. Troubleshooting](#4-troubleshooting) | everyone | – |

Background (provider comparison, costs, load test, cost control, NGO handover):
[`example/docs/infrastructure.md`](example/docs/infrastructure.md).

**Stack in one line:** [OpenCode](https://opencode.ai) (open-source coding agent, MIT) talks
to `Qwen/Qwen3-Coder-Next` (open-weight model) hosted by IONOS in German data centres:
no prompt logging, no training on your data, pay per token, no GPU needed.

---

## 1. Participants

### Step 1 – Install two tools (before the workshop, please)

macOS / Linux / Windows with WSL:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh     # Python tooling (uv)
curl -fsSL https://opencode.ai/install | bash       # coding agent (OpenCode)
```

Windows without WSL: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` and
`npm install -g opencode-ai` (needs Node.js) or `scoop install opencode`.
WSL is recommended – the example's shell hooks are tested on Linux/macOS.

Restart your terminal, then check: `uv --version` and `opencode --version`.

### Step 2 – Get the code and add the token

```bash
git clone https://github.com/CorrelAid/correlcon-2026-agentic-coding-workshop
cd correlcon-2026-agentic-coding-workshop/example
cp .env.example .env
```

Open `.env` and paste the workshop token after `LLM_API_KEY=` (you get it on site).

### Step 3 – Check and start

```bash
uv sync
uv run python scripts/check_setup.py
```

All green? Then start the agent:

```bash
uv run --env-file .env opencode
```

`uv run --env-file .env` passes the token to OpenCode on every OS. The first start takes a
little longer (OpenCode installs the hook dependencies into `.opencode/`).

Try it: *"Write a function in src/project/text.py that masks email addresses and phone
numbers, add tests and run them."* (≈ 45 s, ≈ €0.02)

> **Please:** only use public or synthetic data with the workshop token. The token runs on
> CorrelAid's contract and expires at the end of the day.

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

1. **Cost Alert** (DCD → Management → Cost alert): e-mail at e.g. **€20**. It fires
   **once** and **does not block** anything.
2. **Short TTL** – limits how long a token works. The only technical ceiling is the rate
   limit (5 requests/s per model); a leaked token could theoretically burn **~€690/hour**.
3. **But TTL alone is not enough:** any valid token can mint *new* tokens for the same user
   via the Auth API (`/auth/v1/tokens/generate`, tested 2026-10-23), with their own TTL.
   So after the workshop **deactivate the workshop user** (or delete all its tokens) –
   that stops every token, including any minted ones.
4. Ask the IONOS account manager about a contractual cost limit (mentioned in their FAQ).

Expected workshop cost: **~€15 typical, ~€35 worst realistic case** for 20 people × 1.5 h.

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
| **Skills** | `.agents/skills/*/SKILL.md` | Procedures loaded on demand: `privacy-check`, `llm-categorization`, `ngo-handover`. Cross-tool folder. |
| **Permissions** | `opencode.json` | Only the IONOS provider is enabled; `.env` and `data/raw/` cannot be read; shell commands need approval (except `uv run …`, `git status`, …); session sharing off. |
| **Hooks** | `.opencode/plugins/guardrails.ts` | Deterministic: blocks raw data and secrets even via shell (`cat data/raw/…`), hides the API key from the agent's shell, runs `ruff` after every Python edit and feeds errors back to the agent. |

Supporting code:

- `src/project/llm.py` – the only way project code talks to an LLM; refuses non-approved
  (non-EU) endpoints.
- `scripts/check_setup.py` – setup check incl. tool calling (< €0.01).
- `scripts/costs.py` – cost calculator for workshop, projects and batch runs.

**Why OpenCode restricts providers:** out of the box OpenCode offers free "Zen" models
served via OpenCode's own servers. `"enabled_providers": ["ionos"]` turns everything else
off – verify with `opencode models` inside `example/`.

**Models configured** (all verified on 2026-10-23):

| Model | Role | € in/out per 1M tokens |
|---|---|---|
| `Qwen/Qwen3-Coder-Next` | default coding agent | 0.15 / 0.80 |
| `openai/gpt-oss-120b` | fallback, analysis in project code | 0.15 / 0.65 |
| `Qwen/Qwen3.5-397B-A17B` | hard tasks (`/models` in OpenCode) | 0.60 / 3.60 |
| `Qwen/Qwen3.5-9B` | `small_model` for session titles – keeps helper calls off the coding model's rate limit | 0.10 / 0.15 |

---

## 4. Troubleshooting

| Symptom | Fix |
|---|---|
| `401 Unauthorized` | Token expired (TTL) or you pasted the token ID (UUID) instead of the token (`eyJ…`). |
| `Invalid URL` / no provider | OpenCode was started without the env: use `uv run --env-file .env opencode`. |
| `429 Too Many Requests` | Rate limit (5 req/s per model, shared by everyone). OpenCode retries automatically after ~1 s. |
| `529 … server_overloaded` | IONOS platform load – wait, or switch model with `/models` (e.g. `gpt-oss-120b`). |
| Agent says "Access denied (privacy hook)" | Working as intended: it tried to read `data/raw/` or `.env`. |
| First start hangs for a minute | OpenCode installs plugin dependencies once; needs access to the npm registry. |
