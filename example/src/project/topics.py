"""Step 3 – find topics (categories) on a sample.

Input:  valid answers (02_spam.csv, else 01_prepared.csv – see docs/pipeline.md)
Output: data/processed/03_sample.csv, data/processed/categories_v1.json
"""

from __future__ import annotations

import hashlib
import json
import logging
import pickle

import pandas as pd
from openai import APIError, RateLimitError
from pydantic import BaseModel

from project.data import load_valid_answers
from project.llm import ANALYSIS_MODEL, chat
from project.paths import PROCESSED
from project.prompts import TOPICS_V1

logger = logging.getLogger(__name__)

CACHE_DIR = PROCESSED / "cache"


class Category(BaseModel):
    name: str
    description: str


class TopicsResponse(BaseModel):
    categories: list[Category]


def _cache_key(sample_text: str) -> str:
    """Generate a cache key for the sample."""
    return hashlib.sha256(sample_text.encode()).hexdigest()


def _load_cache(sample_text: str) -> TopicsResponse | None:
    """Load cached results if available."""
    if not CACHE_DIR.exists():
        return None

    key = _cache_key(sample_text)
    cache_file = CACHE_DIR / f"{key}.pkl"

    if cache_file.exists():
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    return None


def _save_cache(sample_text: str, result: TopicsResponse) -> None:
    """Save results to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    key = _cache_key(sample_text)
    cache_file = CACHE_DIR / f"{key}.pkl"

    with open(cache_file, "wb") as f:
        pickle.dump(result, f)


def _build_sample_prompt(df: pd.DataFrame) -> str:
    """Build the prompt with the sample for topic analysis."""
    items_lines = []
    for i, (_, row) in enumerate(df.iterrows()):
        polarity = row["polarity"]
        text = row["text"]
        items_lines.append(f"{i + 1}. row_id={row['row_id']}, polarity='{polarity}', text='{text}'")

    items_text = "\n".join(items_lines)
    return f"""{TOPICS_V1}

Bitte analysieren Sie die folgenden {len(df)} survey Antworten:
{items_text}"""


def draw_sample(df: pd.DataFrame, sample_size: int = 100, seed: int = 42) -> pd.DataFrame:
    """Draw a fixed sample of positive and negative answers.

    Args:
        df: DataFrame with valid answers (positive and negative columns)
        sample_size: Total sample size (default 100)
        seed: Random seed for reproducibility (default 42)

    Returns:
        DataFrame with sampled answers (row_id, polarity, text columns)
    """
    # Separate positive and negative answers
    positive_rows = []
    negative_rows = []

    for _, row in df.iterrows():
        # Add positive answer if not empty
        if pd.notna(row["positive"]) and row["positive"].strip():
            positive_rows.append(
                {
                    "row_id": row["row_id"],
                    "polarity": "positive",
                    "text": row["positive"].strip(),
                }
            )

        # Add negative answer if not empty
        if pd.notna(row["negative"]) and row["negative"].strip():
            negative_rows.append(
                {
                    "row_id": row["row_id"],
                    "polarity": "negative",
                    "text": row["negative"].strip(),
                }
            )

    positive_df = pd.DataFrame(positive_rows)
    negative_df = pd.DataFrame(negative_rows)

    # Sample from each polarity (50 each)
    n_per_polarity = sample_size // 2

    if len(positive_df) < n_per_polarity:
        logger.warning(f"Only {len(positive_df)} positive answers available, sampling all")
        positive_sample = positive_df
    else:
        positive_sample = positive_df.sample(n=n_per_polarity, random_state=seed)

    if len(negative_df) < n_per_polarity:
        logger.warning(f"Only {len(negative_df)} negative answers available, sampling all")
        negative_sample = negative_df
    else:
        negative_sample = negative_df.sample(n=n_per_polarity, random_state=seed)

    # Combine samples
    sample_df = pd.concat([positive_sample, negative_sample], ignore_index=True)

    # Reset index and add sequential numbering
    sample_df = sample_df.reset_index(drop=True)
    sample_df["sample_idx"] = range(1, len(sample_df) + 1)

    return sample_df


def find_topics(sample_df: pd.DataFrame) -> TopicsResponse:
    """Ask the analysis model for topic categories.

    Args:
        sample_df: DataFrame with sampled answers (row_id, polarity, text)

    Returns:
        TopicsResponse with category definitions
    """
    # Build prompt
    prompt_text = _build_sample_prompt(sample_df)

    # Check cache first
    cached = _load_cache(prompt_text)
    if cached is not None:
        logger.info("Cache hit for topic analysis")
        return cached

    try:
        response_text = chat(
            prompt_text,
            system="You are a careful content analyst. Return only valid JSON.",
            model=ANALYSIS_MODEL,
            response_format={"type": "json_object"},
            reasoning_effort="low",
            max_tokens=8000,
        )

        # Parse and validate response
        response_data = json.loads(response_text)
        result = TopicsResponse.model_validate(response_data)

        # Save to cache
        _save_cache(prompt_text, result)

        return result

    except (json.JSONDecodeError, APIError, RateLimitError) as e:
        logger.error(f"Error finding topics: {e}")
        raise


def run(sample_size: int = 100, seed: int = 42) -> list[dict]:
    """Draw a fixed sample, ask the topic model for <= 10 neutral categories, save them.

    Args:
        sample_size: Total sample size (default 100, split 50/50 positive/negative)
        seed: Random seed for reproducibility (default 42)

    Returns:
        List of category dictionaries with name and description
    """
    import time

    # Load valid answers
    df = load_valid_answers()

    # Draw sample
    logger.info(f"Drawing sample of {sample_size} answers (seed={seed})")
    sample_start = time.time()
    sample_df = draw_sample(df, sample_size, seed)
    _ = time.time() - sample_start  # Track duration (not used yet)
    pos_count = len(sample_df[sample_df["polarity"] == "positive"])
    neg_count = len(sample_df[sample_df["polarity"] == "negative"])
    logger.info(
        f"Sample drawn: {len(sample_df)} answers (positive={pos_count}, negative={neg_count})"
    )

    # Save sample
    sample_df[["row_id", "polarity", "text"]].to_csv(PROCESSED / "03_sample.csv", index=False)
    logger.info("Output: 03_sample.csv written")

    # Find topics
    logger.info("Sending sample to analysis model for topic discovery")
    find_start = time.time()
    result = find_topics(sample_df)
    find_duration = time.time() - find_start

    # Save categories
    categories_list = [c.model_dump() for c in result.categories]
    categories_file = PROCESSED / "categories_v1.json"
    with open(categories_file, "w", encoding="utf-8") as f:
        json.dump(categories_list, f, indent=2, ensure_ascii=False)
    logger.info("Output: categories_v1.json written")

    # Log counts
    logger.info(
        f"Request duration: {find_duration:.1f}s, {len(result.categories)} categories found"
    )

    return categories_list
