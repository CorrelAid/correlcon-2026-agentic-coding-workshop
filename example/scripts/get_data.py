"""Download the Babylotse survey 2024 (data/raw/) and the district polygons (data/reference/).

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

BASE = (
    "https://raw.githubusercontent.com/CorrelAid/workshop-babylotse/"
    "83a0507eeb4fa240d8b4b6cda6c797035183517c/data/"
)
ROOT = Path(__file__).resolve().parents[1]
FILES = [
    # (remote name, local path, sha256)
    (
        "Umfrage%20DE%20submissions%202024-07-31%2000_25.csv",
        ROOT / "data" / "raw" / "babylotse_survey_2024.csv",
        "d98d099ccd126507db24327508a160c36b5a7e3a2fc9bd5ddc380a2c36d92b85",
    ),
    (  # Frankfurt district polygons (Stadt Frankfurt am Main), used for the district mapping
        "ffmstadtteilewahlen.geojson",
        ROOT / "data" / "reference" / "ffmstadtteilewahlen.geojson",
        "889bfb30d2ad9046750df925e0fff16fdcaf7407f4fc3335df5e6fb467db62f6",
    ),
]


def download(remote: str, target: Path, sha256: str) -> None:
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == sha256:
        print(f"Already there: {target.relative_to(ROOT)}")
        return
    with urllib.request.urlopen(BASE + remote, timeout=60) as resp:
        content = resp.read()
    digest = hashlib.sha256(content).hexdigest()
    if digest != sha256:
        sys.exit(f"Checksum mismatch for {remote} ({digest}) – file changed upstream, not saved.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    print(f"Saved: {target.relative_to(ROOT)}")


def main() -> None:
    for remote, target, sha256 in FILES:
        download(remote, target, sha256)
    survey = FILES[0][1]
    rows = list(csv.reader(io.StringIO(survey.read_text(encoding="utf-8"))))
    print(f"Survey: {len(rows) - 1} rows, {len(rows[0])} columns: {rows[0]}")


if __name__ == "__main__":
    main()
