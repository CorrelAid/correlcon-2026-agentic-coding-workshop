"""Step 3 – flag (and mask) personal data, keep only valid answers.

TO BE WRITTEN BY THE AGENT – prompt: prompts/03_pii.md
Input:  data/interim/02_spam.csv (is_spam), or – if step 2 was skipped –
        data/interim/01_prepared.csv (district_known)
Output: data/processed/03_clean.csv
"""

from __future__ import annotations

import pandas as pd


def run(use_llm: bool = False, limit: int | None = None) -> pd.DataFrame:
    """Drop spam rows, flag remaining personal data (pii_flag, pii_types), write 03_clean.csv."""
    raise NotImplementedError("Step 3 – see prompts/03_pii.md")
