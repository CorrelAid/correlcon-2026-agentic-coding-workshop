"""Checks in ~30 seconds whether everything is ready for the workshop.

    uv run python scripts/check_setup.py

Two endpoints are checked:
- IONOS  – the coding agent's model (OpenCode), incl. tool calling
- the topic model used by project code (default: GLM-5.3 on Scaleway)

Cost: one run uses < 2,000 tokens (well below €0.01).
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from openai import OpenAI  # noqa: E402

from project.llm import ANALYSIS_MODEL, CODING_MODEL, get_client, provider_name  # noqa: E402

IONOS_BASE_URL = "https://openai.inference.de-txl.ionos.com/v1"
OK, FAIL = "\033[32m✔\033[0m", "\033[31m✘\033[0m"


def step(label: str, fn) -> bool:
    try:
        detail = fn()
        print(f"{OK} {label}" + (f" – {detail}" if detail else ""))
        return True
    except Exception as exc:  # noqa: BLE001 – show errors in plain words
        print(f"{FAIL} {label} – {exc}")
        return False


def check_tools() -> str:
    missing = [t for t in ("uv", "opencode", "git") if shutil.which(t) is None]
    if missing:
        raise RuntimeError(f"not found: {', '.join(missing)} (see SETUP.md, step 1)")
    return "uv, opencode, git"


def check_env() -> str:
    if not Path(".env").exists():
        raise RuntimeError("no .env – run `cp .env.example .env` and add the keys")
    missing = [k for k in ("IONOS_API_KEY", "LLM_API_KEY", "LLM_BASE_URL") if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"empty in .env: {', '.join(missing)}")
    return f"topic model provider: {provider_name(os.environ['LLM_BASE_URL'])}"


def ionos() -> OpenAI:
    return OpenAI(base_url=IONOS_BASE_URL, api_key=os.environ["IONOS_API_KEY"])


def check_agent_model() -> str:
    ids = sorted(m.id for m in ionos().models.list().data)
    if CODING_MODEL not in ids:
        raise RuntimeError(f"{CODING_MODEL} not available on IONOS. Available: {', '.join(ids)}")
    return f"IONOS: {CODING_MODEL} available"


def check_tool_calling() -> str:
    """Coding agents need reliable tool calling – so we test it directly."""
    tool = {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads a file",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    }
    resp = ionos().chat.completions.create(
        model=CODING_MODEL,
        messages=[{"role": "user", "content": "Please read the file README.md."}],
        tools=[tool],
        temperature=0,
        max_tokens=200,
    )
    calls = resp.choices[0].message.tool_calls or []
    if not calls or calls[0].function.name != "read_file":
        raise RuntimeError("model did not call a valid tool")
    return f"read_file({json.loads(calls[0].function.arguments)})"


def check_topic_model() -> str:
    resp = get_client().chat.completions.create(
        model=ANALYSIS_MODEL,
        messages=[{"role": "user", "content": 'Answer only with JSON: {"ok": true}'}],
        response_format={"type": "json_object"},
        max_tokens=2000,  # reasoning models think first – leave room
    )
    answer = json.loads(resp.choices[0].message.content or "{}")
    if answer.get("ok") is not True:
        raise RuntimeError(f"unexpected answer: {answer}")
    return f"{ANALYSIS_MODEL} answers with JSON · {resp.usage.total_tokens} tokens"


if __name__ == "__main__":
    print("Workshop setup check\n")
    results = [step("Tools installed", check_tools), step(".env", check_env)]
    if all(results):
        results += [
            step("Coding agent model", check_agent_model),
            step("Tool calling", check_tool_calling),
            step("Topic model", check_topic_model),
        ]
    ready = all(results)
    print("\nAll set – start with: uv run agent" if ready else "\nPlease fix.")
    sys.exit(0 if ready else 1)
