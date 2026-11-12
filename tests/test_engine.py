import pytest
from engine import EvidenceAgent, RiskAgent, PlanningAgent, EvaluationAgent, run_workflow, canonical_hash

@pytest.fixture
def record():
    return dict(district='Demo A', rainfall_mm=180, impervious_pct=85, drainage_capacity_pct=30, population_exposed=4200, vulnerability_pct=75)

def test_valid_evidence(record): assert EvidenceAgent().run(record).output['quality'] == 'valid_synthetic_record'
def test_missing_field(record):
    del record['rainfall_mm']
    with pytest.raises(ValueError): run_workflow(record)
def test_negative_rainfall(record):
    record['rainfall_mm'] = -1
    with pytest.raises(ValueError): run_workflow(record)
def test_invalid_percent(record):
    record['impervious_pct'] = 110
    with pytest.raises(ValueError): run_workflow(record)
def test_invalid_numeric(record):
    record['rainfall_mm'] = 'bad'
    with pytest.raises(ValueError): run_workflow(record)
def test_risk_range(record): assert 0 <= run_workflow(record)['agents']['Risk Agent']['risk_index'] <= 100
def test_high_risk(record): assert run_workflow(record)['agents']['Risk Agent']['risk_level'] == 'High'
def test_four_options(record): assert len(run_workflow(record)['agents']['Planning Agent']['options']) == 4
def test_post_scores_nonnegative(record): assert all(x['illustrative_post_index'] >= 0 for x in run_workflow(record)['agents']['Planning Agent']['options'])
def test_evaluation_pass(record): assert run_workflow(record)['agents']['Evaluation Agent']['checks_passed']
def test_hash_stable(record): assert run_workflow(record)['workflow_sha256'] == run_workflow(record)['workflow_sha256']
def test_hash_changes(record):
    h = run_workflow(record)['workflow_sha256']; record['rainfall_mm'] += 1
    assert run_workflow(record)['workflow_sha256'] != h
def test_risk_increases_with_rainfall(record):
    a = run_workflow(record)['agents']['Risk Agent']['risk_index']; record['rainfall_mm'] = 200
    assert run_workflow(record)['agents']['Risk Agent']['risk_index'] > a
def test_recommendation_is_option(record):
    p = run_workflow(record)['agents']['Planning Agent']
    assert p['recommended_for_review'] in [x['intervention'] for x in p['options']]
def test_no_real_world_claim(record): assert 'not calibrated' in ' '.join(run_workflow(record)['agents']['Evaluation Agent']['warnings'])