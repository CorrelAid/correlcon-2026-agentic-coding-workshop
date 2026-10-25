"""Tests for step 4 – answer classification."""

import json

import pandas as pd

from project.classify import (
    BATCH_SIZE,
    ClassifyResponse,
    ClassifyResult,
    _build_classify_prompt,
    _cache_key,
    classify_batch,
    run,
)


def test_classify_result_model():
    """Test ClassifyResult pydantic model validation."""
    result = ClassifyResult(row_id=1, polarity="positive", category="Kitaplätze")
    assert result.row_id == 1
    assert result.polarity == "positive"
    assert result.category == "Kitaplätze"


def test_classify_response_model():
    """Test ClassifyResponse pydantic model validation."""
    response = ClassifyResponse(
        results=[
            ClassifyResult(row_id=1, polarity="positive", category="Kitaplätze"),
            ClassifyResult(row_id=2, polarity="negative", category="Grün"),
        ]
    )
    assert len(response.results) == 2
    assert response.results[0].category == "Kitaplätze"


def test_cache_key_consistency():
    """Test that cache keys are consistent for the same batch."""
    categories = [{"name": "Test", "description": "Test desc"}]
    texts1 = ("(1, 'pos', 'neg')",)
    texts2 = ("(1, 'pos', 'neg')",)

    key1 = _cache_key(categories, texts1)
    key2 = _cache_key(categories, texts2)

    assert key1 == key2


def test_cache_key_different():
    """Test that cache keys differ for different batches."""
    categories = [{"name": "Test", "description": "Test desc"}]
    texts1 = ("(1, 'pos1', 'neg1')",)
    texts2 = ("(1, 'pos2', 'neg2')",)

    key1 = _cache_key(categories, texts1)
    key2 = _cache_key(categories, texts2)

    assert key1 != key2


def test_build_classify_prompt():
    """Test prompt building with categories and items."""
    categories = [
        {"name": "Kitaplätze", "description": "Kindergärten und Kitas"},
        {"name": "Grün", "description": "Parks und Grünflächen"},
    ]
    items = [(1, "positive", "Guter Kitaplatz"), (2, "negative", "Keine Parks")]

    prompt = _build_classify_prompt(categories, items)

    assert "Kitaplätze" in prompt
    assert "Kindergärten und Kitas" in prompt
    assert "row_id=1" in prompt
    assert "positive" in prompt
    assert "Guter Kitaplatz" in prompt


def test_classify_batch_empty():
    """Test classify_batch with empty batch."""
    categories = [{"name": "Test", "description": "Test"}]
    result = classify_batch(categories, [])
    assert len(result.results) == 0


def test_classify_batch_single_item():
    """Test classify_batch with a single item."""
    categories = [{"name": "Test", "description": "Test"}]
    items = [(1, "positive", "Some text")]

    result = classify_batch(categories, items)
    assert len(result.results) == 1
    assert result.results[0].row_id == 1


def test_classify_batch_boundary():
    """Test classify_batch handles boundary cases."""
    categories = [{"name": "Test", "description": "Test"}]

    # Single item batch
    items = [(1, "positive", "Text")]
    result = classify_batch(categories, items)
    assert len(result.results) == 1

    # Exact batch size
    items = [(i, "pos" if i % 2 == 0 else "neg", f"text{i}") for i in range(1, BATCH_SIZE + 1)]
    result = classify_batch(categories, items)
    assert len(result.results) == BATCH_SIZE


def test_classify_batch_with_cache(tmp_path, monkeypatch):
    """Test classify_batch uses cache when available."""
    monkeypatch.setattr("project.classify.CACHE_DIR", tmp_path / "cache")

    categories = [{"name": "Test", "description": "Test"}]
    items = [(1, "positive", "Text")]

    # Mock the LLM call
    def mock_chat(*args, **kwargs):
        return '{"results": [{"row_id": 1, "polarity": "positive", "category": "Test"}]}'

    monkeypatch.setattr("project.classify.chat", mock_chat)

    # First call (no cache)
    result1 = classify_batch(categories, items)
    assert len(result1.results) == 1
    assert result1.results[0].row_id == 1
    assert result1.results[0].category == "Test"

    # Second call (should use cache)
    result2 = classify_batch(categories, items)
    assert len(result2.results) == 1

    # Verify cache was saved
    cache_dir = tmp_path / "cache"
    assert cache_dir.exists()
    assert len(list(cache_dir.iterdir())) >= 1


def test_classify_batch_cache_miss(tmp_path, monkeypatch):
    """Test classify_batch cache miss."""
    monkeypatch.setattr("project.classify.CACHE_DIR", tmp_path / "cache")

    categories = [{"name": "Test", "description": "Test"}]
    items = [(1, "positive", "Text")]

    # Mock the LLM call
    def mock_chat(*args, **kwargs):
        return '{"results": [{"row_id": 1, "polarity": "positive", "category": "Test"}]}'

    monkeypatch.setattr("project.classify.chat", mock_chat)

    # No cache exists, so this will use mock LLM
    result = classify_batch(categories, items)
    assert len(result.results) == 1
    assert result.results[0].row_id == 1
    assert result.results[0].category == "Test"


def test_run_mock(tmp_path, monkeypatch):
    """Test run() without calling the actual LLM."""

    # Create mock prepared data
    mock_prepared = tmp_path / "01_prepared.csv"
    mock_prepared.write_text(
        """row_id,month,district,region,district_known,positive,negative
1,2024-04,Mitte,Ost,True,Ich mag Parks,Kitaplätze sind schlecht
2,2024-04,Nord,Mitte,True,-,Kein Grund
"""
    )

    # Mock the classify_batch function
    def mock_classify_batch(category_list, items):
        results = []
        for row_id, polarity, _text in items:
            # Simple mock logic
            if polarity == "positive":
                category = "Grün"
            else:
                category = "Keine inhaltliche Aussage"
            results.append(ClassifyResult(row_id=row_id, polarity=polarity, category=category))
        return ClassifyResponse(results=results)

    monkeypatch.setattr("project.classify.classify_batch", mock_classify_batch)

    # Mock cache functions
    def mock_cache_key(category_list, texts):
        return "mock_key"

    def mock_load_cache(category_list, batch):
        return None

    def mock_save_cache(category_list, batch, result):
        pass

    monkeypatch.setattr("project.classify._cache_key", mock_cache_key)
    monkeypatch.setattr("project.classify._load_cache", mock_load_cache)
    monkeypatch.setattr("project.classify._save_cache", mock_save_cache)

    # Mock data loading
    def mock_load_valid_answers():
        return pd.read_csv(mock_prepared)

    monkeypatch.setattr("project.classify.load_valid_answers", mock_load_valid_answers)

    # Mock categories file
    categories_file = tmp_path / "processed" / "categories_v1.json"
    categories_file.parent.mkdir(parents=True, exist_ok=True)
    with open(categories_file, "w") as f:
        json.dump(
            [
                {"name": "Grün", "description": "Parks"},
                {"name": "Keine inhaltliche Aussage", "description": ""},
            ],
            f,
        )

    # Mock paths
    monkeypatch.setattr("project.classify.PROCESSED", tmp_path / "processed")
    monkeypatch.setattr("project.paths.PROCESSED", tmp_path / "processed")

    # Run
    result_df = run(limit=2)

    # Verify results
    assert len(result_df) == 4  # 2 rows × 2 polarities
    assert "row_id" in result_df.columns
    assert "polarity" in result_df.columns
    assert "text" in result_df.columns
    assert "category" in result_df.columns
    assert "model" in result_df.columns
    assert "prompt_version" in result_df.columns


def test_run_with_empty_answers(tmp_path, monkeypatch):
    """Test run() handles empty answers correctly."""

    # Create mock prepared data with empty answers
    mock_prepared = tmp_path / "01_prepared.csv"
    mock_prepared.write_text(
        """row_id,month,district,region,district_known,positive,negative
1,2024-04,Mitte,Ost,True,,Kein Grund
2,2024-04,Nord,Mitte,True,Ich mag Parks,
"""
    )

    # Mock the classify_batch function
    def mock_classify_batch(category_list, items):
        results = []
        for row_id, _polarity, text in items:
            if text:
                category = "Grün" if "Parks" in text else "Keine inhaltliche Aussage"
            else:
                category = "Keine inhaltliche Aussage"
            # Get polarity from items
            for item in items:
                if item[0] == row_id and item[2] == text:
                    polarity = item[1]
                    break
            results.append(ClassifyResult(row_id=row_id, polarity=polarity, category=category))
        return ClassifyResponse(results=results)

    monkeypatch.setattr("project.classify.classify_batch", mock_classify_batch)

    # Mock cache functions
    monkeypatch.setattr("project.classify._cache_key", lambda *args: "mock_key")
    monkeypatch.setattr("project.classify._load_cache", lambda *args: None)
    monkeypatch.setattr("project.classify._save_cache", lambda *args, **kwargs: None)

    # Mock data loading
    def mock_load_valid_answers():
        return pd.read_csv(mock_prepared)

    monkeypatch.setattr("project.classify.load_valid_answers", mock_load_valid_answers)

    # Mock categories file
    categories_file = tmp_path / "processed" / "categories_v1.json"
    categories_file.parent.mkdir(parents=True, exist_ok=True)
    with open(categories_file, "w") as f:
        json.dump(
            [
                {"name": "Grün", "description": "Parks"},
                {"name": "Keine inhaltliche Aussage", "description": ""},
            ],
            f,
        )

    # Mock paths
    monkeypatch.setattr("project.classify.PROCESSED", tmp_path / "processed")
    monkeypatch.setattr("project.paths.PROCESSED", tmp_path / "processed")

    # Run
    result_df = run(limit=2)

    # Should have 2 answers (one positive, one negative)
    assert len(result_df) == 2


def test_classify_prompt_contains_categories():
    """Test that classify prompt contains category information."""
    categories = [{"name": "Test", "description": "Test desc"}]
    items = [(1, "positive", "Text")]

    prompt = _build_classify_prompt(categories, items)

    assert "Test" in prompt
    assert "Test desc" in prompt


def test_classify_prompt_contains_items():
    """Test that classify prompt contains all items."""
    categories = [{"name": "Test", "description": "Test"}]
    items = [(1, "positive", "Gut"), (2, "negative", "Schlecht")]

    prompt = _build_classify_prompt(categories, items)

    assert "row_id=1" in prompt
    assert "positive" in prompt
    assert "Gut" in prompt
    assert "row_id=2" in prompt
    assert "negative" in prompt
    assert "Schlecht" in prompt
