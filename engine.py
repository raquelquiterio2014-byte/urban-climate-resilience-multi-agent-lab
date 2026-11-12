"""Deterministic, auditable educational multi-agent climate workflow."""
from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

REQUIRED = ('district', 'rainfall_mm', 'impervious_pct', 'drainage_capacity_pct', 'population_exposed', 'vulnerability_pct')
INTERVENTIONS = {
    'Drainage maintenance': {'risk_reduction_points': 12, 'cost_index': 2},
    'Rain gardens and permeable surfaces': {'risk_reduction_points': 9, 'cost_index': 2},
    'Early warning and evacuation planning': {'risk_reduction_points': 7, 'cost_index': 1},
    'Drainage infrastructure upgrade': {'risk_reduction_points': 18, 'cost_index': 5},
}

def canonical_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

@dataclass
class AgentResult:
    agent: str
    output: dict[str, Any]

class EvidenceAgent:
    def run(self, row: dict) -> AgentResult:
        missing = [k for k in REQUIRED if k not in row or row[k] is None or str(row[k]).strip() == '']
        if missing:
            raise ValueError(f'Missing required fields: {", ".join(missing)}')
        if not str(row['district']).strip():
            raise ValueError('District name is required')
        for key in REQUIRED[1:]:
            try:
                value = float(row[key])
            except (TypeError, ValueError):
                raise ValueError(f'Invalid numeric value: {key}') from None
            if not 0 <= value <= (10000 if key == 'population_exposed' else 500 if key == 'rainfall_mm' else 100):
                raise ValueError(f'Out-of-range value: {key}')
        clean = {'district': str(row['district']).strip(), **{k: float(row[k]) for k in REQUIRED[1:]}}
        return AgentResult('Evidence Agent', {'record': clean, 'sha256': canonical_hash(clean), 'quality': 'valid_synthetic_record', 'source_type': 'synthetic_demo'})

class RiskAgent:
    def run(self, evidence: AgentResult) -> AgentResult:
        d = evidence.output['record']
        # Illustrative index, not a calibrated flood model.
        rainfall = min(d['rainfall_mm'] / 200, 1) * 100
        exposure = min(d['population_exposed'] / 5000, 1) * 100
        score = round(.30 * rainfall + .20 * d['impervious_pct'] + .20 * (100 - d['drainage_capacity_pct']) + .15 * exposure + .15 * d['vulnerability_pct'], 2)
        level = 'High' if score >= 65 else 'Moderate' if score >= 35 else 'Low'
        return AgentResult('Risk Agent', {'risk_index': score, 'risk_level': level, 'components': {'rainfall': round(rainfall, 2), 'imperviousness': d['impervious_pct'], 'drainage_deficit': 100-d['drainage_capacity_pct'], 'population_exposure': round(exposure, 2), 'vulnerability': d['vulnerability_pct']}})

class PlanningAgent:
    def run(self, risk: AgentResult) -> AgentResult:
        baseline = risk.output['risk_index']
        options = [{'intervention': name, 'baseline_index': baseline, 'illustrative_post_index': round(max(0, baseline - x['risk_reduction_points']), 2), 'assumed_reduction_points': x['risk_reduction_points'], 'relative_cost_index': x['cost_index'], 'screening_score': round(x['risk_reduction_points'] / x['cost_index'], 2)} for name, x in INTERVENTIONS.items()]
        options.sort(key=lambda x: (-x['screening_score'], x['intervention']))
        return AgentResult('Planning Agent', {'options': options, 'recommended_for_review': options[0]['intervention']})

class EvaluationAgent:
    def run(self, evidence: AgentResult, risk: AgentResult, plan: AgentResult) -> AgentResult:
        warnings = ['Synthetic demonstration data; no official flood-risk assessment.', 'Weights and intervention effects are illustrative assumptions, not calibrated estimates.', 'Human approval and independent local evidence are required before real-world use.']
        return AgentResult('Evaluation Agent', {'checks_passed': all(0 <= o['illustrative_post_index'] <= 100 for o in plan.output['options']) and 0 <= risk.output['risk_index'] <= 100, 'warnings': warnings, 'evidence_sha256': evidence.output['sha256']})

def run_workflow(record: dict) -> dict:
    evidence = EvidenceAgent().run(record)
    risk = RiskAgent().run(evidence)
    planning = PlanningAgent().run(risk)
    evaluation = EvaluationAgent().run(evidence, risk, planning)
    if not evaluation.output['checks_passed']:
        raise ValueError('Evaluation checks failed')
    return {'district': evidence.output['record']['district'], 'agents': {a.agent: a.output for a in (evidence, risk, planning, evaluation)}, 'workflow_sha256': canonical_hash({'evidence': evidence.output, 'risk': risk.output, 'planning': planning.output, 'evaluation': evaluation.output})}