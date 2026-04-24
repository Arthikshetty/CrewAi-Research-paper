import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from dashboard.components.theme import inject_custom_css, check_results

inject_custom_css()
results = check_results()
task_outputs = results.get("task_outputs", [])

# Header
st.markdown("""
<div class="hero-header" style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);">
    <h1>📝 Paper Summaries & Limitations</h1>
    <p>AI-generated summaries with key contributions, methodology, findings, and extracted limitations</p>
</div>
""", unsafe_allow_html=True)

# Find outputs
summary_output = ""
limitation_output = ""
for task in task_outputs:
    desc = task.get("task", "").lower()
    if "summarize" in desc or "summary" in desc:
        summary_output = task.get("output", "")
    if "limitation" in desc:
        limitation_output = task.get("output", "")

tab1, tab2 = st.tabs(["📝 Summaries", "⚠️ Limitations"])

with tab1:
    if summary_output:
        st.markdown("""
        <div class="info-banner">
            <h4>📝 AI-Generated Paper Summaries</h4>
            <p>Each paper has been analyzed by a specialized AI agent that extracts key contributions, methodology, main findings, and keywords.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(summary_output)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📝</div>
            <h3>No Summaries Available</h3>
            <p>Run an analysis to generate AI-powered paper summaries.</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    if limitation_output:
        st.markdown("""
        <div class="info-banner">
            <h4>⚠️ Extracted Limitations</h4>
            <p>Limitations are categorized as Methodological, Data, Scope, Generalizability, Reproducibility, or Scalability, with severity rated 1-5.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(limitation_output)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">⚠️</div>
            <h3>No Limitations Extracted</h3>
            <p>Run an analysis to extract limitations from discovered papers.</p>
        </div>
        """, unsafe_allow_html=True)
