import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from dashboard.components.theme import inject_custom_css, check_results

inject_custom_css()
results = check_results()
task_outputs = results.get("task_outputs", [])

# Header
st.markdown("""
<div class="hero-header" style="background: linear-gradient(135deg, #c0392b 0%, #e74c3c 50%, #c0392b 100%);">
    <h1>📋 Research Gaps & Problem Statements</h1>
    <p>AI-identified gaps in the literature and automatically generated research problem statements</p>
</div>
""", unsafe_allow_html=True)

# Find outputs
gaps_output = ""
problems_output = ""
citation_output = ""
for task in task_outputs:
    desc = task.get("task", "").lower()
    if "gap" in desc:
        gaps_output = task.get("output", "")
    if "problem" in desc:
        problems_output = task.get("output", "")
    if "citation" in desc:
        citation_output = task.get("output", "")

tab1, tab2, tab3 = st.tabs(["🔍 Research Gaps", "📋 Problem Statements", "📊 Citation Analysis"])

with tab1:
    if gaps_output:
        st.markdown("""
        <div class="info-banner">
            <h4>🔍 Identified Research Gaps</h4>
            <p>Gaps are classified as Methodological, Topical, Application, Data, or Theoretical — each with a confidence score and supporting evidence from the literature.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(gaps_output)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <h3>No Research Gaps Detected</h3>
            <p>Run an analysis to identify gaps in the research landscape.</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    if problems_output:
        st.markdown("""
        <div class="info-banner">
            <h4>📋 AI-Generated Problem Statements</h4>
            <p>Each problem statement includes a title, background, objectives, scope, and significance — derived from identified gaps and paper limitations.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(problems_output)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📋</div>
            <h3>No Problem Statements Generated</h3>
            <p>Run an analysis to auto-generate research problem statements.</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    if citation_output:
        st.markdown("""
        <div class="info-banner">
            <h4>📊 Citation Network Analysis</h4>
            <p>Analysis of citation relationships including best base paper, top authors, research clusters, and publication trends.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(citation_output)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <h3>No Citation Analysis Available</h3>
            <p>Run an analysis with Neo4j running to get citation network insights.</p>
        </div>
        """, unsafe_allow_html=True)
