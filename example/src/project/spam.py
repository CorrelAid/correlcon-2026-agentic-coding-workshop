"""Step 2 – flag spam and non-answers.

TO BE WRITTEN BY THE AGENT – prompt: prompts/02_spam.md
Input:  data/interim/01_prepared.csv   Output: data/interim/02_spam.csv
"""

from __future__ import annotations

import pandas as pd


def classify_spam(texts: list[str]) -> list[dict]:
    """Ask the topic model which answers are spam / non-answers (batches of ~20)."""
    raise NotImplementedError("Step 2 – see prompts/02_spam.md")


def run(limit: int | None = None) -> pd.DataFrame:
    """Read 01_prepared.csv, add is_spam / spam_reason / spam_source, write 02_spam.csv."""
    raise NotImplementedError("Step 2 – see prompts/02_spam.md")
