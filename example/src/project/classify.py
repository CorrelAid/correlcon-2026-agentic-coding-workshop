"""Step 5 – assign every answer to one category.

TO BE WRITTEN BY THE AGENT – prompt: prompts/05_classify.md
Input:  data/processed/03_clean.csv, data/processed/categories_v1.json
Output: data/processed/05_classified.csv
"""

from __future__ import annotations

import pandas as pd


def run(limit: int | None = None) -> pd.DataFrame:
    """Classify positive and negative answers in batches of ~20, cache, write 05_classified.csv."""
    raise NotImplementedError("Step 5 – see prompts/05_classify.md")
