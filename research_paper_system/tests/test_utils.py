import pytest
from src.utils.text_processing import clean_text, chunk_text, extract_keywords


def test_clean_text():
    text = "  Hello   World  \n\n  Test  "
    result = clean_text(text)
    assert "  " not in result or result == result.strip()


def test_chunk_text():
    text = "word " * 500
    chunks = chunk_text(text, max_chars=100)
    assert len(chunks) > 1


def test_extract_keywords():
    text = "Machine learning deep learning neural network artificial intelligence"
    keywords = extract_keywords(text, max_keywords=3)
    assert len(keywords) <= 3
    assert all(isinstance(k, str) for k in keywords)
