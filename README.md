# Urban Climate Resilience Multi-Agent Lab V1.0

**COP31 AI Solutions Lab — Day 4 | November 12, 2026**

An independent educational Streamlit application demonstrating a four-agent deterministic urban climate screening workflow with a human-review gate. Optional Gemini 2.5 Flash provides a separate natural-language interpretation; it does not change computed results.

## Modules
1. Overview — synthetic districts and input data
2. Evidence & Risk — validated inputs, SHA-256, reproducible weighted risk index
3. Planning & Comparison — hypothetical interventions and cost-effectiveness screening
4. Multi-Agent Trace & AI — transparent agent outputs, optional Gemini interpretation
5. Human Review & Export — SQLite audit log, CSV and JSON exports

## Installation (Windows PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```
Optional Gemini: copy `.env.example` to `.env` and replace the placeholder with your API key. Never commit `.env`.

## Methodology
Risk index (0–100) = 0.30 × min(rainfall mm / 200, 1) × 100 + 0.20 × impervious % + 0.20 × (100 − drainage capacity %) + 0.15 × min(exposed population / 5000, 1) × 100 + 0.15 × vulnerability %. High ≥65, Moderate ≥35, otherwise Low. Intervention reduction points and relative cost indices are **illustrative assumptions**.

Each agent is a separate, testable Python class. The workflow is deterministic; it is not an autonomous LLM multi-agent orchestration. Optional Gemini is only an interpretation layer.

## Limitations
All data are synthetic; no measured municipal observations, geospatial flood model, calibrated hazard probabilities, verified intervention effectiveness, real-world cost estimates, or actual emissions/impact claims. No decisions should be made from this prototype without independent validation and local experts. SHA-256 supports change detection, not proof that source data are accurate. Human decisions are stored with reviewer name and justification; this is an educational local audit, not authenticated enterprise access control.