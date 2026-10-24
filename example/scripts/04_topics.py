"""Step 4 – find categories on a sample.  uv run python scripts/04_topics.py"""

from project import topics

for c in topics.run():
    print(f"- {c['name']}: {c['description']}")
print("\nReview data/processed/categories_v1.json before step 5.")
