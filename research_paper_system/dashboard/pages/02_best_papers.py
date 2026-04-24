import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from dashboard.components.theme import inject_custom_css, render_metric_card, check_results

inject_custom_css()
results = check_results()
best_papers = results.get("best_base_papers", [])

# Header
st.markdown("""
<div class="hero-header" style="background: linear-gradient(135deg, #2d1b69 0%, #5b2c8e 50%, #8e44ad 100%);">
    <h1>🏆 Best Base Paper</h1>
    <p>The most-referenced foundational paper identified via PageRank and citation in-degree analysis</p>
</div>
""", unsafe_allow_html=True)

if not best_papers:
    st.markdown("""
    <div class="info-banner">
        <h4>⚠️ No Base Paper Data</h4>
        <p>This feature requires Neo4j to be running. Base paper detection uses citation graph analysis (PageRank + in-degree) to find the foundational paper that other discovered papers reference most.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# === #1 Gold Hero Card ===
top = best_papers[0]
st.markdown(f"""
<div class="gold-hero-card">
    <div class="trophy">🏆</div>
    <h2>🥇 {top['title']}</h2>
    <div class="stats-row">
        <div class="stat-item">
            <span class="stat-value">{top['total_incoming_citations']}</span>
            <span class="stat-label">Cited by Discovered Papers</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{top['total_global_citations']:,}</span>
            <span class="stat-label">Global Citations</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{top['pagerank_score']:.4f}</span>
            <span class="stat-label">PageRank Score</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{top.get('year', 'N/A')}</span>
            <span class="stat-label">Year Published</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if top.get("why_base_paper"):
    st.markdown(f"""
    <div class="info-banner">
        <h4>💡 Why It's Foundational</h4>
        <p>{top['why_base_paper']}</p>
    </div>
    """, unsafe_allow_html=True)

# Referenced by
if top.get("referenced_by"):
    with st.expander(f"📚 Referenced by {len(top['referenced_by'])} discovered papers", expanded=True):
        for ref in top["referenced_by"]:
            st.markdown(f"- {ref}")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# === Runner-ups ===
if len(best_papers) > 1:
    st.markdown("### Runner-up Base Papers")
    st.markdown("")

    for i, bp in enumerate(best_papers[1:], 2):
        medal = "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        border_class = "silver" if i == 2 else "bronze" if i == 3 else ""

        st.markdown(f"""
        <div class="runner-card {border_class}">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <strong style="font-size:1.1rem;">{medal} {bp['title']}</strong><br>
                    <span style="color:#6c757d; font-size:0.85rem;">
                        Year: {bp.get('year', 'N/A')} · Source: {bp.get('source', 'N/A')}
                    </span>
                </div>
                <div style="display:flex; gap:2rem; text-align:center;">
                    <div><strong style="font-size:1.2rem; color:#4361ee;">{bp['total_incoming_citations']}</strong><br><span style="font-size:0.7rem; color:#6c757d;">IN-DEGREE</span></div>
                    <div><strong style="font-size:1.2rem; color:#26de81;">{bp['total_global_citations']:,}</strong><br><span style="font-size:0.7rem; color:#6c757d;">GLOBAL</span></div>
                    <div><strong style="font-size:1.2rem; color:#a55eea;">{bp['pagerank_score']:.4f}</strong><br><span style="font-size:0.7rem; color:#6c757d;">PAGERANK</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Comparison Chart
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("### 📊 Base Paper Comparison")

    import plotly.graph_objects as go

    fig = go.Figure()
    names = [bp["title"][:35] + "..." for bp in best_papers]
    fig.add_trace(go.Bar(name="In-Degree", x=names, y=[bp["total_incoming_citations"] for bp in best_papers], marker_color="#4361ee"))
    fig.add_trace(go.Bar(name="PageRank ×100", x=names, y=[bp["pagerank_score"] * 100 for bp in best_papers], marker_color="#a55eea"))
    fig.update_layout(barmode="group", height=400, margin=dict(l=0, r=0, t=20, b=0), xaxis_tickangle=-20,
                       legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, width='stretch')
