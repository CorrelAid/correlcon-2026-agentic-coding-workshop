"""Step 4 – classify all answers.  uv run python scripts/04_classify.py [--limit 100]"""

import argparse

from project import classify

ap = argparse.ArgumentParser()
ap.add_argument("--limit", type=int, help="only the first N rows (try small first)")
df = classify.run(limit=ap.parse_args().limit)
print(df.groupby(["polarity", "category"]).size().to_string())
