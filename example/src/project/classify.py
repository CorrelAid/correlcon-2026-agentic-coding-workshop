"""Step 4 – assign all matching categories to every answer (multi-label).

Input:  valid answers (see docs/pipeline.md), data/processed/categories_v1.json
Output: data/processed/04_classified.csv
"""

from __future__ import annotations

import hashlib
import json
import logging
import pickle

import pandas as pd
from openai import APIError, RateLimitError
from pydantic import BaseModel, ValidationError
from tqdm import tqdm

from project.data import load_valid_answers
from project.llm import ANALYSIS_MODEL, chat
from project.paths import PROCESSED
from project.prompts import TOPICS_V1

logger = logging.getLogger(__name__)

CACHE_DIR = PROCESSED / "cache"
BATCH_SIZE = 20


class ClassifyResult(BaseModel):
    """Result for a single answer classification."""

    row_id: int
    polarity: str
    category: str  # semicolon-separated categories, or "Keine inhaltliche Aussage"


class ClassifyResponse(BaseModel):
    """Response from the analysis model."""

    results: list[ClassifyResult]


def _cache_key(category_list: list[dict], texts: tuple[str, ...]) -> str:
    """Generate a cache key for a batch of answers with categories."""
    categories_str = json.dumps(category_list, sort_keys=True)
    return hashlib.sha256(categories_str.encode() + str(texts).encode()).hexdigest()


def _load_cache(category_list: list[dict], batch: tuple[str, ...]) -> ClassifyResponse | None:
    """Load cached results for a batch if available."""
    if not CACHE_DIR.exists():
        return None

    key = _cache_key(category_list, batch)
    cache_file = CACHE_DIR / f"{key}.pkl"

    if cache_file.exists():
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    return None


def _save_cache(
    category_list: list[dict], batch: tuple[str, ...], result: ClassifyResponse
) -> None:
    """Save results to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    key = _cache_key(category_list, batch)
    cache_file = CACHE_DIR / f"{key}.pkl"

    with open(cache_file, "wb") as f:
        pickle.dump(result, f)


def _build_classify_prompt(category_list: list[dict], items: list[tuple[int, str, str]]) -> str:
    """Build the classification prompt with categories and items."""
    # Build category list with descriptions
    categories_text = "\n".join(
        f"{i + 1}. {c['name']}: {c['description']}" for i, c in enumerate(category_list)
    )

    # Build items text - use numbered list for model reference, but keep original row_id
    items_lines = []
    for i, (row_id, polarity, text) in enumerate(items):
        items_lines.append(f"{i + 1}. [row_id={row_id}, polarity='{polarity}', text='{text}']")
    items_text = "\n".join(items_lines)

    # Build category names for prompt (in prompt, not used as variable)
    ", ".join(f"'{c['name']}'" for c in category_list)

    return f"""{TOPICS_V1}

Kategorie Auswahl:
{categories_text}

Anleitung:
- Lies die Antwort und identifiziere, welche der oben genannten Kategorien darin erwähnt werden
- Eine Antwort kann mehrere Kategorien enthalten
- Gib alle erwähnten Kategorien durch Semikolon getrennt an
- Wenn die Antwort keine inhaltliche Aussage enthält, gib nur "Keine inhaltliche Aussage" an

Eingabe: {len(items)} Antworten zu klassifizieren.
{items_text}

Gib JSON zurück:
{{
  "results": [
    {{"row_id": <integer>, "polarity": "<positive|negative>",
      "category": "<Kategoriename1;Kategoriename2;...>"}},
    ...
  ]
}}"""


def classify_batch(
    category_list: list[dict],
    items: list[tuple[int, str, str]],
    prompt_version: str = "TOPICS_V1",
) -> ClassifyResponse:
    """Classify a batch of answers using the analysis model.

    Args:
        category_list: List of category dictionaries with name and description
        items: List of (row_id, polarity, text) tuples
        prompt_version: Version of the prompt used

    Returns:
        ClassifyResponse with classification results

    Raises:
        APIError: If the LLM call fails after retry
        RateLimitError: If rate limit is hit
    """
    # Build batch texts for cache key
    batch_texts = tuple(str(item) for item in items)

    # Check cache first
    cached = _load_cache(category_list, batch_texts)
    if cached is not None:
        logger.info(f"Cache hit for batch of {len(items)} items")
        return cached

    # Build prompt
    prompt_text = _build_classify_prompt(category_list, items)

    try:
        response_text = chat(
            prompt_text,
            system=(
                "You are a careful content analyst. "
                "Return only valid JSON with exactly one category per answer."
            ),
            model=ANALYSIS_MODEL,
            response_format={"type": "json_object"},
            reasoning_effort="low",
            max_tokens=8000,
        )

        # Parse response
        response_data = json.loads(response_text)

        # Validate with pydantic
        result = ClassifyResponse.model_validate(response_data)

        # The model may return sequential IDs (1, 2, 3...) instead of original row_ids.
        # Map by position: result[i] should use items[i][0]
        fixed_results = []
        for i in range(len(items)):
            if i < len(result.results):
                r = result.results[i]
                original_row_id = items[i][0]  # Get the original row_id from items
                original_polarity = items[i][1]  # Get the original polarity from items
                fixed_results.append(
                    ClassifyResult(
                        row_id=original_row_id, polarity=original_polarity, category=r.category
                    )
                )
            else:
                # Pad with fallback if model returned fewer items
                fixed_results.append(
                    ClassifyResult(
                        row_id=items[i][0],
                        polarity=items[i][1],
                        category="Keine inhaltliche Aussage",
                    )
                )

        result = ClassifyResponse(results=fixed_results)

        # Validate categories are valid (row_ids are guaranteed to match by construction)

        # Save to cache
        _save_cache(category_list, batch_texts, result)

        return result

    except (json.JSONDecodeError, APIError, RateLimitError, ValidationError, ValueError) as e:
        logger.error(f"Error classifying batch: {e}")
        # Retry once
        logger.info("Retrying batch once...")
        try:
            response_text = chat(
                prompt_text,
                system=(
                    "You are a careful content analyst. "
                    "Return only valid JSON with exactly one category per answer."
                ),
                model=ANALYSIS_MODEL,
                response_format={"type": "json_object"},
                reasoning_effort="low",
                max_tokens=8000,
            )

            response_data = json.loads(response_text)
            result = ClassifyResponse.model_validate(response_data)

            # Map results by position to fix sequential IDs
            fixed_results = []
            for i in range(len(items)):
                if i < len(result.results):
                    r = result.results[i]
                    original_row_id = items[i][0]
                    original_polarity = items[i][1]
                    fixed_results.append(
                        ClassifyResult(
                            row_id=original_row_id, polarity=original_polarity, category=r.category
                        )
                    )
                else:
                    # Pad with fallback if model returned fewer items
                    fixed_results.append(
                        ClassifyResult(
                            row_id=items[i][0],
                            polarity=items[i][1],
                            category="Keine inhaltliche Aussage",
                        )
                    )

            result = ClassifyResponse(results=fixed_results)

            # Re-validate categories (row_ids are guaranteed to match by construction)

            _save_cache(category_list, batch_texts, result)

            return result

        except Exception as retry_error:
            logger.error(f"Retry failed: {retry_error}")
            raise


def run(limit: int | None = None) -> pd.DataFrame:
    """Assign categories to answers in batches (~20 items), cache results, write 04_classified.csv.

    Args:
        limit: Only process the first N survey rows (for testing)

    Returns:
        DataFrame with classification results
    """
    # Load valid answers
    df = load_valid_answers()
    original_row_count = len(df)

    if limit is not None:
        df = df.iloc[:limit]
        logger.info(f"Input: valid answers (limited to first {limit} survey rows)")
    else:
        logger.info(f"Input: valid answers ({original_row_count} survey rows)")

    # Load categories
    categories_file = PROCESSED / "categories_v1.json"
    with open(categories_file, encoding="utf-8") as f:
        category_list = json.load(f)
    logger.info(f"Categories loaded: {len(category_list)} categories from {categories_file.name}")

    # Build positive and negative items separately for classification
    positive_items = []
    negative_items = []
    for _, row in df.iterrows():
        # Add positive answer if not empty
        if pd.notna(row["positive"]) and row["positive"].strip():
            positive_items.append((row["row_id"], row["positive"].strip()))

        # Add negative answer if not empty
        if pd.notna(row["negative"]) and row["negative"].strip():
            negative_items.append((row["row_id"], row["negative"].strip()))

    logger.info(f"Positive answers: {len(positive_items)}")
    logger.info(f"Negative answers: {len(negative_items)}")

    # Process positive and negative separately
    all_results = []

    # Process positive answers
    if positive_items:
        logger.info("Processing positive answers...")
        total_batches = (len(positive_items) + BATCH_SIZE - 1) // BATCH_SIZE
        logger.info(f"Positive batches: {total_batches}")

        for i in tqdm(
            range(0, len(positive_items), BATCH_SIZE),
            total=total_batches,
            desc="Classifying positive",
        ):
            batch = positive_items[i : i + BATCH_SIZE]
            # Convert to (row_id, polarity, text) format for classify_batch
            batch_with_polarity = [(r[0], "positive", r[1]) for r in batch]

            try:
                result = classify_batch(category_list, batch_with_polarity)
                all_results.extend(result.results)
            except Exception as e:
                logger.error(f"Failed to process positive batch: {e}")
                for row_id, polarity, _ in batch_with_polarity:
                    all_results.append(
                        ClassifyResult(
                            row_id=row_id, polarity=polarity, category="Keine inhaltliche Aussage"
                        )
                    )

    # Process negative answers
    if negative_items:
        logger.info("Processing negative answers...")
        total_batches = (len(negative_items) + BATCH_SIZE - 1) // BATCH_SIZE
        logger.info(f"Negative batches: {total_batches}")

        for i in tqdm(
            range(0, len(negative_items), BATCH_SIZE),
            total=total_batches,
            desc="Classifying negative",
        ):
            batch = negative_items[i : i + BATCH_SIZE]
            # Convert to (row_id, polarity, text) format for classify_batch
            batch_with_polarity = [(r[0], "negative", r[1]) for r in batch]

            try:
                result = classify_batch(category_list, batch_with_polarity)
                all_results.extend(result.results)
            except Exception as e:
                logger.error(f"Failed to process negative batch: {e}")
                for row_id, polarity, _ in batch_with_polarity:
                    all_results.append(
                        ClassifyResult(
                            row_id=row_id, polarity=polarity, category="Keine inhaltliche Aussage"
                        )
                    )

    # Build results dataframe using row_id ordering from original items
    # Create a lookup: {(row_id, polarity): category}
    result_lookup = {(r.row_id, r.polarity): r.category for r in all_results}

    classified_data = []
    # First positive, then negative, maintaining original row_id order
    for _, row in df.iterrows():
        row_id = row["row_id"]
        # Add positive if exists
        if pd.notna(row["positive"]) and row["positive"].strip():
            text = row["positive"].strip()
            category = result_lookup.get((row_id, "positive"), "Keine inhaltliche Aussage")
            classified_data.append(
                {"row_id": row_id, "polarity": "positive", "text": text, "category": category}
            )
        # Add negative if exists
        if pd.notna(row["negative"]) and row["negative"].strip():
            text = row["negative"].strip()
            category = result_lookup.get((row_id, "negative"), "Keine inhaltliche Aussage")
            classified_data.append(
                {"row_id": row_id, "polarity": "negative", "text": text, "category": category}
            )

    classified_df = pd.DataFrame(classified_data)

    # Add provenance columns
    classified_df["model"] = ANALYSIS_MODEL
    classified_df["prompt_version"] = "TOPICS_V1"

    # Write output
    output_file = PROCESSED / "04_classified.csv"
    classified_df.to_csv(output_file, index=False)
    logger.info(f"Output: {output_file.name} written")

    # Log counts
    category_counts = pd.Series(
        [c.strip() for cat in classified_df["category"] for c in cat.split(";")]
    ).value_counts()
    logger.info(f"Classification counts: {dict(category_counts)}")
    logger.info(f"Total: {len(classified_df)} classified answers")

    return classified_df
