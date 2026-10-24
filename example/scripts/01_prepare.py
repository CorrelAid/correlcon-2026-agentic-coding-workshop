"""Step 1 – prepare the survey (ready-made). Prints a summary only, never comment text.

uv run python scripts/01_prepare.py
"""

from project import paths
from project.prepare import run

df = run()
print(f"Saved {paths.PREPARED.relative_to(paths.ROOT)}: {len(df)} rows")
print("\nRows per region:\n" + df["region"].fillna("(none)").value_counts().to_string())
print(f"\nUnknown district (first spam signal): {(~df['district_known']).sum()}")
for col in ("positive", "negative"):
    empty = (df[col].str.len() < 3).sum()
    print(f"{col}: {empty} empty/very short answers")
