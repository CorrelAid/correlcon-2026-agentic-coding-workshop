"""Tests for step 2 – spam classification."""

import pytest
from pydantic import ValidationError

from project.spam import (
    BATCH_SIZE,
    SpamResponse,
    SpamResult,
    _cache_key,
    classify_spam,
    run,
)


def test_spam_result_model():
    """Test SpamResult pydantic model validation."""
    result = SpamResult(row_id=1, is_spam=True, reason="Empty answer")
    assert result.row_id == 1
    assert result.is_spam is True
    assert result.reason == "Empty answer"


def test_spam_response_model():
    """Test SpamResponse pydantic model validation."""
    response = SpamResponse(
        results=[
            SpamResult(row_id=1, is_spam=True, reason="Empty"),
            SpamResult(row_id=2, is_spam=False, reason="Valid content"),
        ]
    )
    assert len(response.results) == 2
    assert response.results[0].is_spam is True


def test_spam_response_model_invalid():
    """Test SpamResponse validation rejects invalid data."""
    with pytest.raises(ValidationError):
        SpamResponse(results=[{"row_id": "not_an_int", "is_spam": "yes"}])


def test_cache_key_consistency():
    """Test that cache keys are consistent for the same batch."""
    batch1 = [(1, "pos1", "neg1"), (2, "pos2", "neg2")]
    batch2 = [(1, "pos1", "neg1"), (2, "pos2", "neg2")]

    key1 = _cache_key(tuple(str(b) for b in batch1))
    key2 = _cache_key(tuple(str(b) for b in batch2))

    assert key1 == key2


def test_cache_key_different():
    """Test that cache keys differ for different batches."""
    batch1 = [(1, "pos1", "neg1")]
    batch2 = [(1, "pos2", "neg2")]

    key1 = _cache_key(tuple(str(b) for b in batch1))
    key2 = _cache_key(tuple(str(b) for b in batch2))

    assert key1 != key2


def test_classify_spam_empty_batch():
    """Test classify_spam with empty batch."""
    # Empty batch is actually valid - returns empty results
    result = classify_spam([])
    assert len(result.results) == 0


def test_classify_spam_batch_boundary():
    """Test that batch processing handles boundary cases."""
    # Single item batch
    texts = [(1, "Positive answer", "Negative answer")]
    result = classify_spam(texts)
    assert len(result.results) == 1
    assert result.results[0].row_id == 1

    # Exact batch size
    texts = [(i, f"pos{i}", f"neg{i}") for i in range(1, BATCH_SIZE + 1)]
    result = classify_spam(texts)
    assert len(result.results) == BATCH_SIZE

    # Batch size + 1 (tests multiple batches)
    texts = [(i, f"pos{i}", f"neg{i}") for i in range(1, BATCH_SIZE + 2)]
    result = classify_spam(texts)
    assert len(result.results) == BATCH_SIZE + 1


def test_run_mock(tmp_path, monkeypatch):
    """Test run() without calling the actual LLM."""
    # Create mock prepared data
    mock_prepared = tmp_path / "01_prepared.csv"
    mock_prepared.write_text(
        """row_id,month,district,region,district_known,positive,negative
1,2024-04,Mitte,Ost,True,Ich mag die Parks,Kita-Plätze sind schlecht
2,2024-04,Nord,Mitte,True,-,xx
3,2024-04,Ost,Umland,False,Gut,Kein Grund
"""
    )

    # Mock the classify_spam function
    def mock_classify_spam(texts):
        results = []
        for row_id, pos, neg in texts:
            # Simple mock logic for testing
            if pos == "-" or "xx" in neg:
                results.append(
                    SpamResult(row_id=row_id, is_spam=True, reason="Placeholder content")
                )
            else:
                results.append(SpamResult(row_id=row_id, is_spam=False, reason="Valid content"))
        return SpamResponse(results=results)

    monkeypatch.setattr("project.spam.classify_spam", mock_classify_spam)

    # Mock cache functions
    def mock_cache_key(texts):
        return "mock_key"

    def mock_load_cache(batch):
        return None

    def mock_save_cache(batch, result):
        pass

    monkeypatch.setattr("project.spam._cache_key", mock_cache_key)
    monkeypatch.setattr("project.spam._load_cache", mock_load_cache)
    monkeypatch.setattr("project.spam._save_cache", mock_save_cache)

    # Mock paths
    monkeypatch.setattr("project.spam.INTERIM", tmp_path)
    monkeypatch.setattr("project.spam.SPAM", tmp_path / "02_spam.csv")

    # Run
    result_df = run(limit=3)

    # Verify results
    assert len(result_df) == 3
    assert "is_spam" in result_df.columns
    assert "spam_reason" in result_df.columns
    assert result_df["is_spam"].sum() == 1  # Row 2 is spam


def test_run_with_cache(tmp_path, monkeypatch):
    """Test that run() properly merges spam classification results."""
    # Create mock prepared data
    mock_prepared = tmp_path / "01_prepared.csv"
    mock_prepared.write_text(
        """row_id,month,district,region,district_known,positive,negative
1,2024-04,Mitte,Ost,True,Pos,Neg
"""
    )

    # Mock classify_spam to return known results
    def mock_classify_spam(texts):
        assert len(texts) == 1
        row_id, pos, neg = texts[0]
        assert row_id == 1
        assert pos == "Pos"
        assert neg == "Neg"
        return SpamResponse(results=[SpamResult(row_id=row_id, is_spam=False, reason="Valid")])

    # Mock cache functions to avoid actual file I/O
    def mock_load_cache(batch):
        return None  # No cache for this test

    def mock_save_cache(batch, result):
        pass

    monkeypatch.setattr("project.spam._load_cache", mock_load_cache)
    monkeypatch.setattr("project.spam._save_cache", mock_save_cache)
    monkeypatch.setattr("project.spam.classify_spam", mock_classify_spam)
    monkeypatch.setattr("project.spam.INTERIM", tmp_path)
    monkeypatch.setattr("project.spam.SPAM", tmp_path / "02_spam.csv")

    # Run
    result_df = run(limit=1)

    # Verify results
    assert len(result_df) == 1
    assert not result_df.loc[0, "is_spam"]
    assert result_df.loc[0, "spam_reason"] == "Valid"
