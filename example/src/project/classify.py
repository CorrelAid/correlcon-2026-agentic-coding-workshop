"""Step 4 – assign all matching categories to every answer (multi-label).

TO BE WRITTEN BY THE AGENT – prompt: prompts/04_classify.md
Input:  valid answers (see docs/pipeline.md), data/processed/categories_v1.json
Output: data/processed/04_classified.csv
"""

from __future__ import annotations

import pandas as pd


def run(limit: int | None = None) -> pd.DataFrame:
    """Assign one or more categories per answer in batches, cache, write 04_classified.csv."""
    raise NotImplementedError("Step 4 – see prompts/04_classify.md")
