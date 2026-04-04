import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from dashboard.components.theme import inject_custom_css, render_metric_card, check_results

inject_custom_css()
results = check_results()
papers = results.get("papers", [])

# Header
st.markdown("""
<div class="hero-header" style="background: linear-gradient(135deg, #0c0c1d 0%, #1a1a3e 50%, #2d2d5e 100%);">
    <h1>🕸️ Citation Network & Analytics</h1>
    <p>Interactive visualizations of publication trends, source distribution, citation patterns, and knowledge graphs</p>
</div>
""", unsafe_allow_html=True)

if not papers:
    st.warning("No papers available.")
    st.stop()

# KPI Row
total_cites = sum(p.get("citations_count", 0) for p in papers)
max_cites = max((p.get("citations_count", 0) for p in papers), default=0)
years_all = [p.get("year") for p in papers if p.get("year")]
year_span = f"{min(years_all)}-{max(years_all)}" if years_all else "—"

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card(f"{total_cites:,}", "Total Citations", "blue")
with c2:
    render_metric_card(f"{max_cites:,}", "Max Citations", "gold")
with c3:
    render_metric_card(year_span, "Year Span", "green")
with c4:
    render_metric_card(len(set(p.get("source", "") for p in papers)), "Sources", "purple")

st.markdown("")

# Tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Distribution", "🕸️ Network Graph", "📉 Citation Analysis"])

with tab1:
    # Publication trend
    years_data = {}
    for p in papers:
        y = p.get("year")
        if y:
            years_data[y] = years_data.get(y, 0) + 1

    if years_data:
        c1, c2 = st.columns(2)
        with c1:
            trend_df = pd.DataFrame(sorted(years_data.items()), columns=["Year", "Papers"])
            fig = px.area(trend_df, x="Year", y="Papers", color_discrete_sequence=["#4361ee"],
                         title="📈 Papers Published Per Year")
            fig.update_layout(height=380, margin=dict(l=0, r=0, t=40, b=0))
            fig.update_traces(fill="tozeroy", line=dict(width=3))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Cumulative trend
            cum_df = trend_df.copy()
            cum_df["Cumulative"] = cum_df["Papers"].cumsum()
            fig2 = px.line(cum_df, x="Year", y="Cumulative", color_discrete_sequence=["#a55eea"],
                          title="📈 Cumulative Paper Count")
            fig2.update_layout(height=380, margin=dict(l=0, r=0, t=40, b=0))
            fig2.update_traces(line=dict(width=3))
            st.plotly_chart(fig2, use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)

    with c1:
        # Source distribution
        source_counts = {}
        for p in papers:
            s = p.get("source", "unknown").replace("_", " ").title()
            source_counts[s] = source_counts.get(s, 0) + 1

        source_df = pd.DataFrame(
            sorted(source_counts.items(), key=lambda x: x[1], reverse=True),
            columns=["Source", "Count"]
        )
        fig3 = px.pie(source_df, values="Count", names="Source",
                      title="📊 Papers by Source",
                      color_discrete_sequence=px.colors.qualitative.Set3,
                      hole=0.4)
        fig3.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig3, use_container_width=True)

    with c2:
        # Source bar chart
        fig4 = px.bar(source_df, x="Count", y="Source", orientation="h",
                      title="📊 Paper Count by Source",
                      color="Count", color_continuous_scale="Viridis")
        fig4.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0),
                           yaxis=dict(autorange="reversed"), showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.markdown("""
    <div class="info-banner">
        <h4>🕸️ Interactive Citation Network</h4>
        <p>Nodes represent papers (size = citations). Gold nodes are base papers. Edges represent citation relationships. Drag to rearrange, scroll to zoom.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        import networkx as nx
        from pyvis.network import Network
        import tempfile

        G = nx.DiGraph()
        best_papers = results.get("best_base_papers", [])
        best_ids = {bp["paper_id"] for bp in best_papers}

        # Color palette by source
        source_colors = {
            "arxiv": "#e65100", "semantic_scholar": "#1565c0", "ieee": "#2e7d32",
            "scopus": "#7b1fa2", "crossref": "#c62828", "openalex": "#00695c",
            "pubmed": "#4e342e", "core": "#558b2f", "dblp": "#283593",
            "sciencedirect": "#ad1457", "google_scholar": "#f57f17",
        }

        for p in papers[:60]:
            is_base = p.get("id") in best_ids
            src = p.get("source", "")
            color = "#FFD700" if is_base else source_colors.get(src, "#97c2fc")
            size = 30 if is_base else max(8, min(40, (p.get("citations_count", 0) ** 0.5) * 2))
            border_width = 3 if is_base else 1

            G.add_node(
                p.get("id", p.get("title", "")[:30]),
                label=p.get("title", "")[:35] + ("..." if len(p.get("title", "")) > 35 else ""),
                title=(f"<b>{p.get('title')}</b><br>"
                       f"Year: {p.get('year')}<br>"
                       f"Citations: {p.get('citations_count', 0):,}<br>"
                       f"Source: {src.replace('_', ' ').title()}<br>"
                       f"{'⭐ BASE PAPER' if is_base else ''}"),
                size=size,
                color=color,
                borderWidth=border_width,
                borderWidthSelected=4,
            )

        doi_to_id = {}
        for p in papers:
            if p.get("doi"):
                doi_to_id[p["doi"].lower()] = p.get("id", "")

        for p in papers[:60]:
            for ref in p.get("references", []):
                target = doi_to_id.get(ref.lower())
                if target and G.has_node(target):
                    G.add_edge(p.get("id", ""), target, color="#cccccc", arrows="to")

        if G.number_of_nodes() > 0:
            net = Network(height="650px", width="100%", directed=True, notebook=False,
                         bgcolor="#0f0f1a", font_color="white")
            net.from_nx(G)
            net.set_options("""
            {
                "physics": {
                    "barnesHut": {
                        "gravitationalConstant": -4000,
                        "centralGravity": 0.3,
                        "springLength": 120,
                        "damping": 0.09
                    },
                    "maxVelocity": 50,
                    "minVelocity": 0.1
                },
                "nodes": {
                    "font": {"size": 11, "face": "Inter"},
                    "shape": "dot"
                },
                "edges": {
                    "smooth": {"type": "continuous"},
                    "width": 0.5
                },
                "interaction": {
                    "hover": true,
                    "tooltipDelay": 100,
                    "zoomView": true
                }
            }
            """)

            with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
                net.save_graph(f.name)
                with open(f.name, "r", encoding="utf-8") as html_file:
                    html_content = html_file.read()
                os.unlink(f.name)
            st.components.v1.html(html_content, height=670)

            # Legend
            st.markdown("""
            <div style="display:flex; gap:1.5rem; flex-wrap:wrap; justify-content:center; margin-top:0.5rem;">
                <span style="font-size:0.8rem;">⭐ <strong style="color:#FFD700;">Gold</strong> = Base Paper</span>
                <span style="font-size:0.8rem;">🔵 <strong style="color:#1565c0;">Blue</strong> = Semantic Scholar</span>
                <span style="font-size:0.8rem;">🟠 <strong style="color:#e65100;">Orange</strong> = ArXiv</span>
                <span style="font-size:0.8rem;">🟢 <strong style="color:#2e7d32;">Green</strong> = IEEE</span>
                <span style="font-size:0.8rem;">🟣 <strong style="color:#7b1fa2;">Purple</strong> = Scopus</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Not enough data for network visualization.")

    except ImportError:
        st.warning("Install `pyvis` and `networkx` for the interactive graph.")

with tab4:
    # Citation Distribution
    citation_data = [p.get("citations_count", 0) for p in papers if p.get("citations_count", 0) > 0]
    if citation_data:
        c1, c2 = st.columns(2)
        with c1:
            fig5 = px.histogram(x=citation_data, nbins=40, color_discrete_sequence=["#4361ee"],
                                title="📊 Citation Count Distribution")
            fig5.update_layout(xaxis_title="Citation Count", yaxis_title="Number of Papers",
                              height=380, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig5, use_container_width=True)

        with c2:
            # Log scale scatter: Year vs Citations
            scatter_data = [
                {"Year": p.get("year"), "Citations": p.get("citations_count", 0),
                 "Title": p.get("title", "")[:40], "Source": p.get("source", "").replace("_", " ").title()}
                for p in papers if p.get("year") and p.get("citations_count", 0) > 0
            ]
            if scatter_data:
                sdf = pd.DataFrame(scatter_data)
                fig6 = px.scatter(sdf, x="Year", y="Citations", color="Source",
                                  hover_name="Title", log_y=True,
                                  title="📊 Citations vs Year (log scale)")
                fig6.update_layout(height=380, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig6, use_container_width=True)
