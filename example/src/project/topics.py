"""Step 4 – find topics (categories) on a sample.

TO BE WRITTEN BY THE AGENT – prompt: prompts/04_topics.md
Input:  data/processed/03_clean.csv
Output: data/processed/04_sample.csv, data/processed/categories_v1.json
"""

from __future__ import annotations


def run(sample_size: int = 100, seed: int = 42) -> list[dict]:
    """Draw a fixed sample, ask the topic model for <= 10 neutral categories, save them."""
    raise NotImplementedError("Step 4 – see prompts/04_topics.md")
