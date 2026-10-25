"""Inspect some classifications from the output file."""

import pandas as pd

df = pd.read_csv("data/processed/04_classified.csv")

print("Sample classifications (first 10 rows):")
print(df[["row_id", "polarity", "text", "category"]].head(10).to_string())
print()

print("Summary by individual category:")
all_counts = []
for _, row in df.iterrows():
    categories = [c.strip() for c in row["category"].split(";")]
    for cat in categories:
        all_counts.append((row["polarity"], cat))

counts_df = pd.DataFrame(all_counts, columns=["polarity", "category"])
counts = counts_df.groupby(["polarity", "category"]).size()
counts_sorted = counts.groupby(level=0, group_keys=False).apply(
    lambda x: x.sort_values(ascending=False)
)
print(counts_sorted.to_string())
