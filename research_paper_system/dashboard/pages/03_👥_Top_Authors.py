import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from dashboard.components.theme import inject_custom_css, check_results

inject_custom_css()
results = check_results()
top_authors = results.get("top_authors", [])

# Header
st.markdown("""
<div class="hero-header" style="background: linear-gradient(135deg, #0d7377 0%, #14919b 50%, #0d7377 100%);">
    <h1>👤 Top Authors</h1>
    <p>Leading researchers ranked by publication count and citation impact on this topic</p>
</div>
""", unsafe_allow_html=True)

if not top_authors:
    st.markdown("""
    <div class="info-banner">
        <h4>⚠️ No Author Data Available</h4>
        <p>Author analysis requires Neo4j to be running. The system identifies top authors by counting papers and citations within the discovered paper set.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

topic = st.session_state.get("topic", "")

# Author Podium (Top 3)
st.markdown(f"### 🏅 Top {len(top_authors)} Authors on: _{topic}_")
st.markdown("")

if len(top_authors) >= 3:
    col1, col2, col3 = st.columns([1, 1, 1])
    podium = [(top_authors[1], "🥈", 2, "rank-2"), (top_authors[0], "🥇", 1, "rank-1"), (top_authors[2], "🥉", 3, "rank-3")]
    for col, (a, medal, rank, rank_class) in zip([col1, col2, col3], podium):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding:1.5rem; background:white; border-radius:12px; border:1px solid #e8eaed;
                        {'box-shadow: 0 4px 20px rgba(247,183,49,0.2); border-color: #f7b731;' if rank == 1 else ''}">
                <div style="font-size:2.5rem;">{medal}</div>
                <div style="font-size:1.1rem; font-weight:700; margin:0.5rem 0;">{a['author_name']}</div>
                <div style="color:#6c757d; font-size:0.85rem;">
                    {a['total_papers_on_topic']} papers · {a['total_citations']:,} citations
                </div>
                <div style="color:#adb5bd; font-size:0.75rem; margin-top:0.3rem;">{a.get('year_range_active', '')}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# Visualization Tabs
tab1, tab2 = st.tabs(["📊 Charts", "📋 Detailed Profiles"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        # Papers by Author
        chart_df = pd.DataFrame([
            {"Author": a["author_name"].split(",")[0], "Papers": a["total_papers_on_topic"]}
            for a in top_authors
        ])
        fig = px.bar(chart_df, x="Papers", y="Author", orientation="h",
                     color="Papers", color_continuous_scale="Teal")
        fig.update_layout(title="📚 Papers per Author", height=400,
                          margin=dict(l=0, r=0, t=40, b=0), yaxis=dict(autorange="reversed"), showlegend=False)
        st.plotly_chart(fig, width='stretch')

    with c2:
        # Citations by Author
        cite_df = pd.DataFrame([
            {"Author": a["author_name"].split(",")[0], "Citations": a["total_citations"]}
            for a in top_authors
        ])
        fig2 = px.bar(cite_df, x="Citations", y="Author", orientation="h",
                      color="Citations", color_continuous_scale="Purples")
        fig2.update_layout(title="📊 Citations per Author", height=400,
                           margin=dict(l=0, r=0, t=40, b=0), yaxis=dict(autorange="reversed"), showlegend=False)
        st.plotly_chart(fig2, width='stretch')

    # Bubble chart: Papers vs Citations
    bubble_df = pd.DataFrame([
        {
            "Author": a["author_name"],
            "Papers": a["total_papers_on_topic"],
            "Citations": a["total_citations"],
            "h-index": a.get("h_index") or 10,
        }
        for a in top_authors
    ])
    fig3 = px.scatter(bubble_df, x="Papers", y="Citations", size="h-index",
                      color="Author", hover_name="Author",
                      size_max=40)
    fig3.update_layout(title="🔬 Papers vs Citations (size = h-index)", height=400,
                       margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig3, width='stretch')

with tab2:
    # Full ranking table
    df = pd.DataFrame([
        {
            "Rank": i,
            "Author": a["author_name"],
            "Papers": a["total_papers_on_topic"],
            "Citations": f"{a['total_citations']:,}",
            "h-index": a.get("h_index") or "—",
            "Active Years": a.get("year_range_active", "—"),
            "Most Cited Paper": (a.get("most_cited_paper") or "—")[:60],
        }
        for i, a in enumerate(top_authors, 1)
    ])
    st.dataframe(df, width='stretch', hide_index=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Detailed Author Cards
    for i, author in enumerate(top_authors, 1):
        rank_class = f"rank-{i}" if i <= 3 else "rank-other"
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"

        st.markdown(f"""
        <div class="author-card">
            <div class="author-rank {rank_class}">{i}</div>
            <div style="flex:1;">
                <strong style="font-size:1.1rem;">{medal} {author['author_name']}</strong><br>
                <span style="color:#6c757d; font-size:0.85rem;">
                    {author['total_papers_on_topic']} papers · {author['total_citations']:,} citations
                    · h-index: {author.get('h_index') or '—'}
                    · Active: {author.get('year_range_active', '—')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"View details for {author['author_name']}"):
            dc1, dc2, dc3 = st.columns(3)
            dc1.metric("Papers", author["total_papers_on_topic"])
            dc2.metric("Citations", f"{author['total_citations']:,}")
            dc3.metric("h-index", author.get("h_index") or "—")

            if author.get("affiliations"):
                st.markdown(f"**Affiliations:** {', '.join(author['affiliations'])}")
            if author.get("most_cited_paper"):
                st.markdown(f"**Most Cited Paper:** {author['most_cited_paper']}")
            if author.get("recent_paper"):
                st.markdown(f"**Most Recent Paper:** {author['recent_paper']}")
            if author.get("expertise_keywords"):
                kw_html = " ".join(f'<span class="source-badge badge-default">{k}</span>' for k in author["expertise_keywords"][:10])
                st.markdown(f"**Expertise:** {kw_html}", unsafe_allow_html=True)
