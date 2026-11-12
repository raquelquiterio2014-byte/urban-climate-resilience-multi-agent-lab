import json
from pathlib import Path
import pandas as pd
import streamlit as st
from engine import run_workflow
from storage import save_review, get_reviews

st.set_page_config(page_title='Urban Climate Resilience Multi-Agent Lab V1.0', page_icon='🏙️', layout='wide')
st.title('🏙️ Urban Climate Resilience Multi-Agent Lab V1.0')
st.caption('COP31 AI Solutions Lab | Day 4 — Independent educational prototype | Synthetic scenarios')
st.info('This is a deterministic educational risk-screening exercise, not a forecast or official assessment. Human review is required.')
source = Path(__file__).parent / 'sample_data' / 'synthetic_districts.csv'
df = pd.read_csv(source)
tabs = st.tabs(['Overview', 'Evidence & Risk', 'Planning & Comparison', 'Multi-Agent Trace & AI', 'Human Review & Export'])
with tabs[0]:
    st.subheader('Synthetic urban scenarios')
    st.dataframe(df, use_container_width=True)
    st.metric('Demonstration districts', len(df))
    st.caption('No measured municipal data or real-world impact is claimed.')
with st.sidebar:
    district = st.selectbox('Select synthetic district', df['district'].tolist())
    st.caption('All values and intervention effects are illustrative.')
record = df.loc[df['district'] == district].iloc[0].to_dict()
workflow = run_workflow(record)
a = workflow['agents']
with tabs[1]:
    st.subheader('Evidence Agent → Risk Agent')
    st.metric('Illustrative risk index (0–100)', a['Risk Agent']['risk_index'])
    st.metric('Screening category', a['Risk Agent']['risk_level'])
    st.json(a['Evidence Agent'])
    st.bar_chart(pd.Series(a['Risk Agent']['components'], name='Component index'))
    st.caption('Weighted illustrative formula: 30% rainfall + 20% imperviousness + 20% drainage deficit + 15% exposure + 15% vulnerability.')
with tabs[2]:
    st.subheader('Planning Agent — hypothetical intervention comparison')
    options = pd.DataFrame(a['Planning Agent']['options'])
    st.dataframe(options, use_container_width=True)
    st.bar_chart(options.set_index('intervention')['illustrative_post_index'])
    st.warning('Intervention reduction points and cost indices are assumptions, not field-validated effectiveness or financial estimates.')
with tabs[3]:
    st.subheader('Agent execution trace')
    for agent_name, result in a.items():
        with st.expander(agent_name, expanded=(agent_name == 'Evaluation Agent')):
            st.json(result)
    st.code(workflow['workflow_sha256'], language='text')
    st.subheader('Optional Gemini 2.5 Flash interpretation')
    if st.button('Request AI interpretation'):
        try:
            from ai_gateway import interpret
            st.write(interpret(workflow))
        except Exception as exc:
            st.error(f'AI interpretation unavailable: {exc}')
    st.caption('Gemini is optional; it does not calculate or modify risk scores.')
with tabs[4]:
    st.subheader('Human Review Gate')
    reviewer = st.text_input('Reviewer')
    decision = st.selectbox('Decision', ['needs_evidence', 'approved', 'rejected'])
    notes = st.text_area('Justification (required)')
    if st.button('Save review'):
        try:
            review_id = save_review(district, workflow['workflow_sha256'], reviewer, decision, notes)
            st.success(f'Review #{review_id} saved in SQLite.')
        except ValueError as exc:
            st.error(str(exc))
    reviews = get_reviews()
    st.dataframe(pd.DataFrame(reviews), use_container_width=True)
    st.download_button('Export workflow JSON', json.dumps(workflow, indent=2, ensure_ascii=False), file_name='urban_resilience_workflow.json', mime='application/json')
    st.download_button('Export intervention comparison CSV', pd.DataFrame(a['Planning Agent']['options']).to_csv(index=False), file_name='intervention_comparison.csv', mime='text/csv')
    st.download_button('Export human review audit CSV', pd.DataFrame(reviews, columns=['id','created_at','district','workflow_sha256','reviewer','decision','notes']).to_csv(index=False), file_name='human_reviews.csv', mime='text/csv')