import pytest
from storage import save_review, get_reviews

def test_persistence(tmp_path):
    db = tmp_path / 'audit.sqlite3'
    i = save_review('Demo A', 'abc', 'Reviewer', 'needs_evidence', 'Synthetic values need verification', db)
    assert i == 1
    assert get_reviews(db)[0]['decision'] == 'needs_evidence'

def test_invalid_decision(tmp_path):
    with pytest.raises(ValueError): save_review('Demo A', 'abc', 'Reviewer', 'maybe', 'note', tmp_path/'a.sqlite3')

def test_missing_justification(tmp_path):
    with pytest.raises(ValueError): save_review('Demo A', 'abc', 'Reviewer', 'approved', '', tmp_path/'a.sqlite3')