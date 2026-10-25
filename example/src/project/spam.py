"""Step 2 – flag spam and non-answers.

Input:  data/interim/01_prepared.csv   Output: data/interim/02_spam.csv
"""

from __future__ import annotations

import hashlib
import json
import logging
import pickle

import pandas as pd
from openai import APIError, RateLimitError
from pydantic import BaseModel
from tqdm import tqdm

from project.llm import ANALYSIS_MODEL, chat
from project.paths import INTERIM, SPAM
from project.prompts import SPAM_V1

logger = logging.getLogger(__name__)

BATCH_SIZE = 20


class SpamResult(BaseModel):
    row_id: int
    is_spam: bool
    reason: str


class SpamResponse(BaseModel):
    results: list[SpamResult]


def _cache_key(texts: tuple[str, ...]) -> str:
    """Generate a cache key for a batch of texts."""
    return hashlib.sha256(str(texts).encode()).hexdigest()


def _load_cache(batch: tuple[str, ...]) -> SpamResponse | None:
    """Load cached results for a batch if available."""
    cache_dir = INTERIM / "cache"
    if not cache_dir.exists():
        return None

    key = _cache_key(batch)
    cache_file = cache_dir / f"{key}.pkl"

    if cache_file.exists():
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    return None


def _save_cache(batch: tuple[str, ...], result: SpamResponse) -> None:
    """Save results to cache."""
    cache_dir = INTERIM / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    key = _cache_key(batch)
    cache_file = cache_dir / f"{key}.pkl"

    with open(cache_file, "wb") as f:
        pickle.dump(result, f)


def classify_spam(texts: list[tuple[int, str, str]]) -> SpamResponse:
    """Ask the analysis model which answers are spam / non-answers (batches of ~20).

    Args:
        texts: List of (row_id, positive_answer, negative_answer) tuples

    Returns:
        SpamResponse with results for each input
    """
    # Check cache first
    batch_key = tuple(str(t) for t in texts)
    cached = _load_cache(batch_key)
    if cached is not None:
        logger.info(f"Cache hit for batch of {len(texts)} items")
        return cached

    # Build prompt for this batch
    items_text = "\n".join(
        f"{i + 1}. row_id={row_id}, positive='{pos}', negative='{neg}'"
        for i, (row_id, pos, neg) in enumerate(texts)
    )

    prompt = f"""{SPAM_V1}

Please classify the following {len(texts)} survey responses:
{items_text}"""

    try:
        response_text = chat(
            prompt,
            system="You are a careful content reviewer. Return only valid JSON.",
            model=ANALYSIS_MODEL,
            response_format={"type": "json_object"},
            reasoning_effort="low",
            max_tokens=8000,
        )

        # Parse and validate response
        response_data = json.loads(response_text)
        result = SpamResponse.model_validate(response_data)

        # Save to cache
        _save_cache(batch_key, result)

        return result

    except (json.JSONDecodeError, APIError, RateLimitError) as e:
        logger.error(f"Error classifying batch: {e}")
        raise


def run(limit: int | None = None) -> pd.DataFrame:
    """Read 01_prepared.csv, add is_spam / spam_reason, write 02_spam.csv.

    Args:
        limit: Only process the first N rows (for testing)

    Returns:
        DataFrame with spam classification results
    """
    input_file = INTERIM / "01_prepared.csv"
    df = pd.read_csv(input_file)

    if limit is not None:
        df = df.iloc[:limit]

    logger.info(f"Input: {input_file.name} with {len(df)} rows")

    # Prepare batch inputs
    batch_inputs = [(row["row_id"], row["positive"], row["negative"]) for _, row in df.iterrows()]

    # Process in batches
    results = []
    total_batches = (len(batch_inputs) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in tqdm(
        range(0, len(batch_inputs), BATCH_SIZE), total=total_batches, desc="Classifying spam"
    ):
        batch = batch_inputs[i : i + BATCH_SIZE]

        try:
            response = classify_spam(batch)
            results.extend(response.results)
        except Exception as e:
            logger.error(f"Failed to process batch starting at row {batch[0][0]}: {e}")
            # Add placeholder results for failed batch
            for row_id, _, _ in batch:
                results.append(
                    SpamResult(row_id=row_id, is_spam=False, reason="Batch processing failed")
                )

    # Build result dataframe
    spam_df = pd.DataFrame(
        [{"row_id": r.row_id, "is_spam": r.is_spam, "spam_reason": r.reason} for r in results]
    )

    # Merge with original dataframe
    output_df = df.merge(spam_df, on="row_id", how="left")

    # Fill any missing values
    output_df["is_spam"] = output_df["is_spam"].fillna(False).astype(bool)
    output_df["spam_reason"] = output_df["spam_reason"].fillna("")

    # Write output
    output_df.to_csv(SPAM, index=False)
    logger.info(f"Output: {SPAM.name} written")

    spam_count = int(output_df["is_spam"].sum())
    logger.info(f"Total: {len(output_df)} rows, {spam_count} flagged as spam")

    return output_df
