"""Step 4 – classify all answers.  uv run python scripts/04_classify.py [--limit 100]"""

import argparse

import pandas as pd

from project import classify

ap = argparse.ArgumentParser()
ap.add_argument("--limit", type=int, help="only the first N rows (try small first)")
df = classify.run(limit=ap.parse_args().limit)
# Split multi-label categories and count individual categories
all_counts = []
for _, row in df.iterrows():
    categories = [c.strip() for c in row["category"].split(";")]
    for cat in categories:
        all_counts.append((row["polarity"], cat))

counts_df = pd.DataFrame(all_counts, columns=["polarity", "category"])
counts = counts_df.groupby(["polarity", "category"]).size()
# Sort within each polarity group
counts_sorted = counts.groupby(level=0, group_keys=False).apply(
    lambda x: x.sort_values(ascending=False)
)
print(counts_sorted.to_string())
