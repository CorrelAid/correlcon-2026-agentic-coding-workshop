"""Step 2 – flag spam and non-answers with plain Python (no LLM).

TO BE WRITTEN BY THE AGENT – prompt: prompts/02_spam.md
Input:  data/interim/01_prepared.csv   Output: data/interim/02_spam.csv
"""

from __future__ import annotations

import pandas as pd


def detect_spam(positive: str, negative: str, district_known: bool) -> list[str]:
    """Return the reasons why a response is spam – an empty list means: not spam."""
    raise NotImplementedError("Step 2 – see prompts/02_spam.md")


def run(limit: int | None = None) -> pd.DataFrame:
    """Read 01_prepared.csv, add is_spam / spam_reason, write 02_spam.csv, print counts."""
    raise NotImplementedError("Step 2 – see prompts/02_spam.md")
