"""Data loading utilities for the pipeline."""

from __future__ import annotations

import logging

import pandas as pd

from project.paths import INTERIM

logger = logging.getLogger(__name__)


def load_valid_answers() -> pd.DataFrame:
    """Load valid answers for steps 3–5.

    Uses 02_spam.csv with is_spam == False if it exists; otherwise (step 2 is
    optional) falls back to 01_prepared.csv with district_known == True.

    Returns:
        DataFrame with valid answers (positive and negative columns)
    """
    spam_file = INTERIM / "02_spam.csv"
    prepared_file = INTERIM / "01_prepared.csv"

    if spam_file.exists():
        logger.info(f"Input: {spam_file.name} (step 2 available)")
        df = pd.read_csv(spam_file)
        df = df[df["is_spam"] == False]  # noqa: E712 (false positive, it's a bool column)
        logger.info(f"Loaded {len(df)} rows with is_spam == False")
    else:
        logger.info(f"Input: {prepared_file.name} (step 2 skipped)")
        df = pd.read_csv(prepared_file)
        df = df[df["district_known"] == True]  # noqa: E712 (false positive, it's a bool column)
        logger.info(f"Loaded {len(df)} rows with district_known == True")

    return df
