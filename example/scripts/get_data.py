"""Download the Babylotse survey 2024 into data/raw/.

    uv run python scripts/get_data.py

"Family satisfaction in Frankfurt - Babylotse survey 2024" by Babylotse Frankfurt
(https://babylotse-frankfurt.de/) is licensed under CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/) and available on GitHub:
https://github.com/CorrelAid/workshop-babylotse

The file is pinned to a commit and checked by SHA-256, so everyone works on identical data.
Only a summary is printed – never cell contents (raw data stays out of the agent's context).
"""

from __future__ import annotations

import csv
import hashlib
import io
import sys
import urllib.request
from pathlib import Path

URL = (
    "https://raw.githubusercontent.com/CorrelAid/workshop-babylotse/"
    "83a0507eeb4fa240d8b4b6cda6c797035183517c/data/"
    "Umfrage%20DE%20submissions%202024-07-31%2000_25.csv"
)
SHA256 = "d98d099ccd126507db24327508a160c36b5a7e3a2fc9bd5ddc380a2c36d92b85"
TARGET = Path(__file__).resolve().parents[1] / "data" / "raw" / "babylotse_survey_2024.csv"


def main() -> None:
    if TARGET.exists() and hashlib.sha256(TARGET.read_bytes()).hexdigest() == SHA256:
        print(f"Already there: {TARGET.relative_to(Path.cwd())}")
    else:
        with urllib.request.urlopen(URL, timeout=60) as resp:
            content = resp.read()
        digest = hashlib.sha256(content).hexdigest()
        if digest != SHA256:
            sys.exit(f"Checksum mismatch ({digest}) – file changed upstream, not saved.")
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(content)
        print(f"Saved: {TARGET.relative_to(Path.cwd())}")

    rows = list(csv.reader(io.StringIO(TARGET.read_text(encoding="utf-8"))))
    print(f"{len(rows) - 1} rows, {len(rows[0])} columns: {rows[0]}")


if __name__ == "__main__":
    main()
