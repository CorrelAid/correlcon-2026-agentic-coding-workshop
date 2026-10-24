"""Step 3 – flag personal data.  uv run python scripts/03_pii.py [--llm] [--limit 100]"""

import argparse

from project import pii

ap = argparse.ArgumentParser()
ap.add_argument("--llm", action="store_true", help="also ask the topic model (names, addresses)")
ap.add_argument("--limit", type=int)
a = ap.parse_args()
df = pii.run(use_llm=a.llm, limit=a.limit)
print(f"{len(df)} valid rows kept, {int(df['pii_flag'].sum())} with personal data flagged")
