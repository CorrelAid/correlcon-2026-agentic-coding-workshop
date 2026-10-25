"""Inspect spam cases from step 2 output."""

import pandas as pd

df = pd.read_csv("data/interim/02_spam.csv")
spam = df[df["is_spam"]]

print(f"Total responses: {len(df)}")
print(f"Spam cases: {len(spam)} ({len(spam) / len(df) * 100:.1f}%)\n")

if len(spam) > 0:
    print("Spam cases:")
    for _, row in spam.iterrows():
        print(f"Row {row['row_id']}: {row['spam_reason']}")
        print(f"  Positive: {row['positive'][:80] if row['positive'] else '(empty)'}")
        print(f"  Negative: {row['negative'][:80] if row['negative'] else '(empty)'}")
        print()
else:
    print("No spam cases found.")
