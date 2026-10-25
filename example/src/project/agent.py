"""Start OpenCode the right way:  uv run agent

- always from the example/ folder, so opencode.json (IONOS only, hooks, permissions) applies
- with the keys from .env, overriding stale values exported in your shell
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

from dotenv import dotenv_values

from project.paths import ROOT


def main() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        sys.exit("No .env – run `cp .env.example .env` and add the keys (see SETUP.md).")
    values = {k: v for k, v in dotenv_values(env_file).items() if v}
    if not values.get("IONOS_API_KEY"):
        sys.exit("IONOS_API_KEY is empty in .env.")
    for key, value in values.items():
        if os.environ.get(key) not in (None, value):
            print(f"Note: {key} from your shell is ignored – using the value from .env.")
    if shutil.which("opencode") is None:
        sys.exit("opencode not found – see SETUP.md, step 1.")
    env = {**os.environ, **values, "PWD": str(ROOT)}
    sys.exit(subprocess.call(["opencode", *sys.argv[1:]], cwd=ROOT, env=env))
