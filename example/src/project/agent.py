"""Start OpenCode the right way:  uv run agent

- always from the example/ folder, so opencode.json (IONOS only, policies, hooks) applies
- with the keys from .env, overriding stale values exported in your shell
- with `--standalone`: OpenCode 2 otherwise talks to a shared background service that was
  started without these keys (-> HTTP 401)
"""

from __future__ import annotations

import os
import re
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
    version = subprocess.run(["opencode", "--version"], capture_output=True, text=True).stdout
    major = re.search(r"(\d+)\.\d+", version)
    if not major or major.group(1) != "2":
        sys.exit(
            f"OpenCode {version.strip() or '?'} found – this workshop needs OpenCode 2.\n"
            "Install: curl -fsSL https://opencode.ai/v2/install | bash   (see SETUP.md, step 1)"
        )
    env = {**os.environ, **values, "PWD": str(ROOT)}
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        args = ["--standalone", *args]  # interactive TUI
    elif args[0] == "run":
        args = ["run", "--standalone", *args[1:]]  # one-shot prompt
    sys.exit(subprocess.call(["opencode", *args], cwd=ROOT, env=env))
