"""Checks in ~30 seconds whether everything is ready for the workshop.

    uv run python scripts/check_setup.py

Cost: one run uses < 1,000 tokens (well below €0.01).
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from project.llm import CODING_MODEL, get_client, provider_name  # noqa: E402

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
        raise RuntimeError("no .env – run `cp .env.example .env` and add the token")
    if not os.getenv("LLM_API_KEY", ""):
        raise RuntimeError("LLM_API_KEY in .env is empty")
    return f"provider: {provider_name(os.environ['LLM_BASE_URL'])}"


def check_models() -> str:
    ids = sorted(m.id for m in get_client().models.list().data)
    if CODING_MODEL not in ids:
        raise RuntimeError(f"{CODING_MODEL} not available. Available: {', '.join(ids)}")
    return f"{len(ids)} models available, including {CODING_MODEL}"


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
    resp = get_client().chat.completions.create(
        model=CODING_MODEL,
        messages=[{"role": "user", "content": "Please read the file README.md."}],
        tools=[tool],
        temperature=0,
        max_tokens=200,
    )
    calls = resp.choices[0].message.tool_calls or []
    if not calls or calls[0].function.name != "read_file":
        raise RuntimeError("model did not call a valid tool")
    args = json.loads(calls[0].function.arguments)
    usage = resp.usage
    return f"read_file({args}) · {usage.prompt_tokens}+{usage.completion_tokens} tokens"


if __name__ == "__main__":
    print("Workshop setup check\n")
    results = [step("Tools installed", check_tools), step(".env & EU provider", check_env)]
    if all(results):
        results += [
            step("Connection & model", check_models),
            step("Tool calling", check_tool_calling),
        ]
    ready = all(results)
    print("\nAll set – start with: uv run --env-file .env opencode" if ready else "\nPlease fix.")
    sys.exit(0 if ready else 1)
