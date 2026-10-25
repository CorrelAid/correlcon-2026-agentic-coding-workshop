"""Tests for step 3 – topic analysis."""

import pandas as pd
import pytest

from project.prompts import TOPICS_V1
from project.topics import (
    Category,
    TopicsResponse,
    _build_sample_prompt,
    _cache_key,
    _load_cache,
    _save_cache,
    draw_sample,
)


def test_topic_categories_model():
    """Test Category pydantic model validation."""
    category = Category(name="Kitaplätze", description="Alle Antworten zu Kindergärten und Kitas")
    assert category.name == "Kitaplätze"
    assert "Kindergärten" in category.description


def test_topics_response_model():
    """Test TopicsResponse pydantic model validation."""
    response = TopicsResponse(
        categories=[
            Category(name="Kitaplätze", description="Kita und Kindergarten"),
            Category(name="Grün", description="Parks und Grünflächen"),
        ]
    )
    assert len(response.categories) == 2
    assert response.categories[0].name == "Kitaplätze"


def test_cache_key_consistency():
    """Test that cache keys are consistent for the same sample."""
    sample1 = "test sample text"
    sample2 = "test sample text"

    key1 = _cache_key(sample1)
    key2 = _cache_key(sample2)

    assert key1 == key2


def test_cache_key_different():
    """Test that cache keys differ for different samples."""
    sample1 = "test sample text 1"
    sample2 = "test sample text 2"

    key1 = _cache_key(sample1)
    key2 = _cache_key(sample2)

    assert key1 != key2


def test_build_sample_prompt():
    """Test prompt building with sample data."""
    sample_df = pd.DataFrame(
        {
            "row_id": [1, 2],
            "polarity": ["positive", "negative"],
            "text": ["Gut", "Schlecht"],
        }
    )

    prompt = _build_sample_prompt(sample_df)

    assert TOPICS_V1 in prompt
    assert "row_id=1" in prompt
    assert "polarity='positive'" in prompt
    assert "Gut" in prompt


def test_draw_sample_basic():
    """Test basic sampling functionality."""
    df = pd.DataFrame(
        {
            "row_id": [1, 2, 3, 4],
            "positive": ["Gut", "Sehr gut", "", "OK"],
            "negative": ["Schlecht", "", "Sehr schlecht", "Schlecht"],
        }
    )

    sample = draw_sample(df, sample_size=4, seed=42)

    assert len(sample) == 4
    assert "row_id" in sample.columns
    assert "polarity" in sample.columns
    assert "text" in sample.columns


def test_draw_sample_balance():
    """Test that sampling balances positive and negative answers."""
    df = pd.DataFrame(
        {
            "row_id": [1, 2, 3, 4, 5],
            "positive": ["Pos1", "Pos2", "Pos3", "Pos4", "Pos5"],
            "negative": ["Neg1", "Neg2", "Neg3", "Neg4", "Neg5"],
        }
    )

    sample = draw_sample(df, sample_size=4, seed=42)

    # Should have 2 positive and 2 negative
    positive_count = len(sample[sample["polarity"] == "positive"])
    negative_count = len(sample[sample["polarity"] == "negative"])

    assert positive_count == 2
    assert negative_count == 2


def test_draw_sample_reproducibility():
    """Test that sampling is reproducible with same seed."""
    df = pd.DataFrame(
        {
            "row_id": range(1, 21),
            "positive": [f"Pos{i}" for i in range(1, 21)],
            "negative": [f"Neg{i}" for i in range(1, 21)],
        }
    )

    sample1 = draw_sample(df, sample_size=10, seed=42)
    sample2 = draw_sample(df, sample_size=10, seed=42)

    pd.testing.assert_frame_equal(sample1, sample2)


def test_draw_sample_empty_answers():
    """Test that empty answers are excluded."""
    df = pd.DataFrame(
        {
            "row_id": [1, 2, 3],
            "positive": ["Gut", "", "Auch gut"],
            "negative": ["Schlecht", "Auch schlecht", ""],
        }
    )

    sample = draw_sample(df, sample_size=4, seed=42)

    # Should only have 2 positive and 2 negative (empty ones excluded)
    assert len(sample) == 4

    # Verify no empty text
    assert "" not in sample["text"].values
    assert None not in sample["text"].values


def test_cache_save_and_load(tmp_path, monkeypatch):
    """Test cache save and load functionality."""
    monkeypatch.setattr("project.topics.CACHE_DIR", tmp_path / "cache")

    response = TopicsResponse(categories=[Category(name="Test", description="Test description")])

    sample_text = "test sample for caching"

    # Save to cache
    _save_cache(sample_text, response)

    # Load from cache
    loaded = _load_cache(sample_text)

    assert loaded is not None
    assert len(loaded.categories) == 1
    assert loaded.categories[0].name == "Test"


def test_cache_miss(tmp_path, monkeypatch):
    """Test cache miss returns None."""
    monkeypatch.setattr("project.topics.CACHE_DIR", tmp_path / "cache")

    result = _load_cache("nonexistent sample")

    assert result is None


def test_cache_directory_creation(tmp_path, monkeypatch):
    """Test that cache directory is created if it doesn't exist."""
    cache_dir = tmp_path / "new_cache" / "topics"
    monkeypatch.setattr("project.topics.CACHE_DIR", cache_dir)

    response = TopicsResponse(categories=[])
    _save_cache("test", response)

    assert cache_dir.exists()
    assert len(list(cache_dir.iterdir())) == 1


def test_topics_prompt_contains_instructions():
    """Test that TOPICS_V1 prompt contains required instructions."""
    assert "bis zu 10 neutrale Themenkategorien" in TOPICS_V1
    assert "Keine inhaltliche Aussage" in TOPICS_V1
    assert "categories" in TOPICS_V1


def test_draw_sample_sample_size_larger_than_data():
    """Test sampling when sample size is larger than available data."""
    df = pd.DataFrame(
        {
            "row_id": [1, 2],
            "positive": ["Pos1", "Pos2"],
            "negative": ["Neg1", "Neg2"],
        }
    )

    sample = draw_sample(df, sample_size=100, seed=42)

    # Should return all available answers
    assert len(sample) == 4


def test_category_model_validation():
    """Test that Category model validates required fields."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Category(name="Test")  # Missing description

    with pytest.raises(ValidationError):
        Category(description="Test")  # Missing name

    with pytest.raises(ValidationError):
        Category()  # Missing both
