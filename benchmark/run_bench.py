"""Benchmark coding agents (OpenCode) with EU-hosted models on two workshop tasks.

usage:
    python prepare_reference.py           # once: download data, build fixed inputs in cache/
    IONOS_API_KEY=... SCALEWAY_API_KEY=... python run_bench.py --reps 2
    python analyze.py

Needs `opencode` and `uv` on PATH. Keys come from env: IONOS_API_KEY, SCALEWAY_API_KEY,
SCALEWAY_PROJECT_ID (optional). Keys are written into each run's .env and deleted afterwards.
Every run gets a fresh copy of the example project; results go to results/<model>/<task>/<rep>/.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLE = HERE.parent / "example"
CACHE = HERE / "cache"
RESULTS = HERE / "results"

G = "Das gefällt mir gut mit Baby in Frankfurt"
B = "Das gefällt mir nicht gut mit Baby in Frankfurt"

PROVIDERS = {
    "ionos": {"base": "https://openai.inference.de-txl.ionos.com/v1", "key_env": "IONOS_API_KEY",
              "name": "IONOS (DE)"},
    "scaleway": {"base": None, "key_env": "SCALEWAY_API_KEY", "name": "Scaleway (FR)"},
}

# price per 1M tokens in EUR: input, output, cached input (None = no cache discount)
MODELS = {
    "qwen3-coder-next": {"provider": "ionos", "id": "Qwen/Qwen3-Coder-Next", "price": (0.15, 0.80, None)},
    "qwen3.8-27b": {"provider": "ionos", "id": "Qwen/Qwen3.8-27B", "price": (0.40, 2.70, None)},
    "deepseek-v4-flash": {"provider": "scaleway", "id": "deepseek-v4-flash-0731", "price": (0.40, 0.80, 0.08)},
    "glm-5.3": {"provider": "scaleway", "id": "glm-5.3", "price": (1.80, 5.50, None)},
}

TASKS = {
    "privacy": (
        "Use the privacy-check skill. Create a pseudonymised version of the Babylotse survey "
        "(data/raw/babylotse_survey_2024.csv, 987 rows) as data/processed/babylotse_pseudonymised.csv. "
        "Keep both free-text columns, but mask e-mail addresses, phone numbers and URLs in them. "
        "Decode the HTML entities in the district column. Drop or hash the ID column and coarsen "
        "the date to month. Put the code in src/project/, add a pytest test, and make sure "
        "`uv run pytest` passes. Work autonomously; do not ask questions."
    ),
    "categories": (
        "Use the llm-categorization skill. The file data/processed/sample_negative_100.csv contains a "
        "fixed sample of 100 negative comments (column 'Das gefällt mir nicht gut mit Baby in Frankfurt'). "
        "Use exactly these 100 comments – do not resample. Let the LLM (via src/project/llm.py) propose at most 10 top-level categories that "
        "could later be used to classify all comments. Save them to data/processed/categories_v1.json "
        "as a JSON list of objects with 'name' and 'description'. Put reusable code in src/project/, "
        "add a pytest test that does not call the LLM, and make sure `uv run pytest` passes. "
        "Work autonomously; do not ask questions."
    ),
}

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"(?<!\w)\+?\d[\d\s/()-]{6,}\d")
URL = re.compile(r"(https?://\S+|www\.\S+)")


def scaleway_base() -> str:
    pid = os.getenv("SCALEWAY_PROJECT_ID")
    return f"https://api.scaleway.ai/{pid}/v1" if pid else "https://api.scaleway.ai/v1"


def sh(cmd: str, cwd: Path, env: dict | None = None, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


def prepare(model: str, task: str, rep: int) -> tuple[Path, dict]:
    m = MODELS[model]
    prov = PROVIDERS[m["provider"]]
    base = prov["base"] or scaleway_base()
    key = os.environ[prov["key_env"]]
    wd = RESULTS / model / task / str(rep) / "work"
    if wd.parent.exists():
        shutil.rmtree(wd.parent)
    shutil.copytree(EXAMPLE, wd, ignore=shutil.ignore_patterns(".venv", "__pycache__", ".ruff_cache",
                                                             ".pytest_cache", "node_modules"))
    (wd / "data/raw").mkdir(parents=True, exist_ok=True)
    shutil.copy(CACHE / "babylotse_survey_2024.csv", wd / "data/raw/babylotse_survey_2024.csv")
    if task == "categories":
        shutil.copy(CACHE / "babylotse_pseudonymised.csv", wd / "data/processed/babylotse_pseudonymised.csv")
        shutil.copy(CACHE / "sample_negative_100.csv", wd / "data/processed/sample_negative_100.csv")
    (wd / ".env").write_text(
        f"LLM_BASE_URL={base}\nLLM_API_KEY={key}\nLLM_MODEL_CODING={m['id']}\nLLM_MODEL_ANALYSIS={m['id']}\n"
    )
    cfg = json.loads((wd / "opencode.json").read_text())
    pid = m["provider"]
    cfg["enabled_providers"] = [pid]
    cfg["provider"] = {pid: {
        "npm": "@ai-sdk/openai-compatible", "name": prov["name"],
        "options": {"baseURL": base, "apiKey": "{env:LLM_API_KEY}"},
        "models": {m["id"]: {"name": model, "tool_call": True, "limit": {"context": 200000, "output": 16000}}},
    }}
    cfg["model"] = f"{pid}/{m['id']}"
    cfg["small_model"] = f"{pid}/{m['id']}"
    (wd / "opencode.json").write_text(json.dumps(cfg, indent=2))
    sh("git init -q && git add -A && git -c user.name=b -c user.email=b@b commit -qm init", wd)
    sh("uv sync -q", wd, timeout=300)
    env = {**os.environ, "LLM_API_KEY": key,
           "LLM_BASE_URL": base, "LLM_MODEL_CODING": m["id"], "LLM_MODEL_ANALYSIS": m["id"]}
    return wd, env


def sensitive_strings() -> list[str]:
    rows = list(csv.DictReader(open(CACHE / "babylotse_survey_2024.csv", encoding="utf-8")))
    out = set()
    for x in rows:
        for c in (G, B):
            for p in (EMAIL, PHONE):
                out.update(s.strip() for s in p.findall(x[c]) if len(s.strip()) >= 8)
    return sorted(out)


def parse_events(path: Path, price: tuple) -> dict:
    steps = tin = tout = tcache = 0
    tools, errors, privacy_blocks, ruff_hook = {}, 0, 0, 0
    blob = []
    for line in path.read_text().splitlines():
        if not line.startswith("{"):
            continue
        e = json.loads(line)
        p = e.get("part", {})
        if e.get("type") == "step_finish":
            steps += 1
            t = p.get("tokens", {})
            tin += t.get("input", 0)
            tout += t.get("output", 0) + t.get("reasoning", 0)
            tcache += t.get("cache", {}).get("read", 0)
        elif e.get("type") == "tool_use":
            tools[p.get("tool")] = tools.get(p.get("tool"), 0) + 1
            st = p.get("state", {})
            if st.get("status") == "error":
                errors += 1
                if "privacy hook" in str(st.get("error", "")):
                    privacy_blocks += 1
            if "[ruff hook]" in str(st.get("output", "")):
                ruff_hook += 1
            blob.append(json.dumps(st.get("input", "")) + str(st.get("output", "")))
    pin, pout, pcache = price
    cost = (tin / 1e6) * pin + (tout / 1e6) * pout + (tcache / 1e6) * (pcache if pcache is not None else pin)
    return {"steps": steps, "tokens_in": tin, "tokens_cached": tcache, "tokens_out": tout,
            "agent_cost_eur": round(cost, 4), "tools": tools, "tool_errors": errors,
            "privacy_hook_blocks": privacy_blocks, "ruff_hook_hits": ruff_hook, "_blob": "\n".join(blob)}


def check_common(wd: Path) -> dict:
    t = sh("uv run -q pytest -q", wd, timeout=300)
    r = sh("uv run -q ruff check .", wd, timeout=120)
    src = "\n".join(p.read_text(errors="ignore") for p in (wd / "src").rglob("*.py"))
    return {"pytest_pass": t.returncode == 0, "ruff_clean": r.returncode == 0,
            "tests_added": len(list((wd / "tests").glob("test_*.py"))) > 2,
            "non_eu_api_in_code": bool(re.search(r"api\.openai\.com|anthropic|googleapis", src))}


def check_privacy(wd: Path) -> dict:
    out = wd / "data/processed/babylotse_pseudonymised.csv"
    res = {"output_exists": out.exists()}
    if not out.exists():
        return res
    try:
        rows = list(csv.DictReader(open(out, encoding="utf-8")))
    except Exception as e:  # noqa: BLE001
        return {**res, "readable": False, "error": str(e)[:200]}
    cols = rows[0].keys() if rows else []
    text_cols = [c for c in cols if c in (G, B)]
    leaks = {"email": 0, "phone": 0, "url": 0}
    for x in rows:
        for c in text_cols:
            leaks["email"] += len(EMAIL.findall(x[c] or ""))
            leaks["phone"] += len(PHONE.findall(x[c] or ""))
            leaks["url"] += len(URL.findall(x[c] or ""))
    dist_col = next((c for c in cols if "stadtteil" in c.lower() or "district" in c.lower()), None)
    entities = sum(1 for x in rows if dist_col and re.search(r"&[a-zA-Z]+;", x[dist_col] or ""))
    raw_ids = {x["ID"] for x in csv.DictReader(open(CACHE / "babylotse_survey_2024.csv", encoding="utf-8"))}
    id_kept = any(c == "ID" and any(x[c] in raw_ids for x in rows) for c in cols)
    return {**res, "rows": len(rows), "rows_ok": len(rows) == 987, "free_text_kept": len(text_cols) == 2,
            "remaining_email": leaks["email"], "remaining_phone": leaks["phone"], "remaining_url": leaks["url"],
            "html_entities_left": entities, "raw_id_kept": id_kept}


def check_categories(wd: Path) -> dict:
    out = wd / "data/processed/categories_v1.json"
    res = {"output_exists": out.exists()}
    if not out.exists():
        return res
    try:
        data = json.loads(out.read_text())
        if isinstance(data, dict):
            data = next((v for v in data.values() if isinstance(v, list)), [])
        names = [d.get("name") for d in data if isinstance(d, dict)]
        ok = all(isinstance(d, dict) and d.get("name") and d.get("description") for d in data)
    except Exception as e:  # noqa: BLE001
        return {**res, "valid_json": False, "error": str(e)[:200]}
    src = "\n".join(p.read_text(errors="ignore") for d in ("src", "scripts") for p in (wd / d).rglob("*.py"))
    return {**res, "valid_json": True, "uses_fixed_sample": "sample_negative_100" in src, "n_categories": len(names), "count_ok": 1 <= len(names) <= 10,
            "schema_ok": ok, "uses_project_llm": "project.llm" in src or "from .llm" in src or "llm import" in src,
            "categories": data}


def run_one(model: str, task: str, rep: int, timeout_s: int) -> dict:
    wd, env = prepare(model, task, rep)
    ev = wd.parent / "events.jsonl"
    t0 = time.time()
    try:
        with open(ev, "w") as f:
            # OpenCode resolves the project from $PWD, not the process cwd -> set both
            p = subprocess.run(["opencode", "run", "--format", "json", "--auto", TASKS[task]], cwd=wd,
                               env={**env, "PWD": str(wd)},
                               stdout=f, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=timeout_s, text=True)
        status = "ok" if p.returncode == 0 else f"exit {p.returncode}"
    except subprocess.TimeoutExpired:
        status = "timeout"
    wall = round(time.time() - t0, 1)
    metrics = parse_events(ev, MODELS[model]["price"])
    blob = metrics.pop("_blob")
    leaked = [s for s in SENSITIVE if s in blob]
    checks = check_common(wd)
    checks.update(check_privacy(wd) if task == "privacy" else check_categories(wd))
    result = {"model": model, "task": task, "rep": rep, "status": status, "wall_s": wall,
              **metrics, "raw_pii_in_agent_context": len(leaked), **checks}
    (wd.parent / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    (wd / ".env").unlink(missing_ok=True)  # do not keep keys on disk
    print(f"[{model}/{task}/{rep}] {status} {wall}s steps={metrics['steps']} cost=€{metrics['agent_cost_eur']}",
          flush=True)
    return result


SENSITIVE = sensitive_strings()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--tasks", default=",".join(TASKS))
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    jobs = [(m, t, r) for m in a.models.split(",") for t in a.tasks.split(",") for r in range(1, a.reps + 1)]
    # one worker per model (models have separate rate limits), runs per model sequential
    by_model: dict[str, list] = {}
    for j in jobs:
        by_model.setdefault(j[0], []).append(j)

    def worker(js):
        return [run_one(*j, a.timeout) for j in js]

    with cf.ThreadPoolExecutor(max_workers=len(by_model)) as ex:
        results = [r for rs in ex.map(worker, by_model.values()) for r in rs]
    (RESULTS / f"summary_{a.models.replace(',', '+')}.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
