"""Step 4 – find topics (categories) on a sample.

TO BE WRITTEN BY THE AGENT – prompt: prompts/04_topics.md
Input:  valid answers (03_clean.csv, else 02_spam.csv, else 01_prepared.csv – see docs/pipeline.md)
Output: data/processed/04_sample.csv, data/processed/categories_v1.json
"""

from __future__ import annotations


def run(sample_size: int = 100, seed: int = 42) -> list[dict]:
    """Draw a fixed sample, ask the topic model for <= 10 neutral categories, save them."""
    raise NotImplementedError("Step 4 – see prompts/04_topics.md")
