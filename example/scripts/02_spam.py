"""Step 2 – flag spam.  uv run python scripts/02_spam.py [--limit 100]"""

import argparse

from project import spam

ap = argparse.ArgumentParser()
ap.add_argument("--limit", type=int, help="only the first N rows (try small first)")
df = spam.run(limit=ap.parse_args().limit)
print(f"{len(df)} rows, {int(df['is_spam'].sum())} flagged as spam")
