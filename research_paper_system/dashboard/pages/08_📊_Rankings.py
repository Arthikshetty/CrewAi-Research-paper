import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from dashboard.components.theme import inject_custom_css, render_metric_card, check_results

inject_custom_css()
results = check_results()
rankings = results.get("rankings", [])

# Header
st.markdown("""
<div class="hero-header" style="background: linear-gradient(135deg, #1b1464 0%, #3d1f91 50%, #6c3ec1 100%);">
    <h1>⭐ Paper Rankings</h1>
    <p>Multi-signal scoring combining citation impact, recency, relevance, source authority, and methodology quality</p>
</div>
""", unsafe_allow_html=True)

if not rankings:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">⭐</div>
        <h3>No Rankings Available</h3>
        <p>Run an analysis to compute multi-signal paper rankings.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# KPI
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card(len(rankings), "Papers Ranked", "purple")
with c2:
    render_metric_card(f"{rankings[0]['overall_score']:.3f}", "Top Score", "gold")
with c3:
    avg = sum(r["overall_score"] for r in rankings) / len(rankings)
    render_metric_card(f"{avg:.3f}", "Average Score", "blue")
with c4:
    render_metric_card(rankings[0]["title"][:20] + "...", "#1 Paper", "green")

st.markdown("")

# Scoring weights legend
st.markdown("""
<div class="info-banner">
    <h4>📐 Scoring Formula</h4>
    <p>
        <strong>30%</strong> Citation Impact · <strong>25%</strong> Relevance · <strong>20%</strong> Recency
        · <strong>15%</strong> Source Authority · <strong>10%</strong> Methodology
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Full Rankings", "📊 Score Charts", "🔬 Detailed View"])

with tab1:
    df = pd.DataFrame([
        {
            "Rank": r["rank_position"],
            "Title": r["title"][:70],
            "Overall": r["overall_score"],
            "Citation": r["citation_score"],
            "Recency": r["recency_score"],
            "Relevance": r["relevance_score"],
            "Source Auth.": r["source_authority_score"],
            "Method.": r["methodology_score"],
        }
        for r in rankings[:100]
    ])

    st.dataframe(
        df.style.background_gradient(subset=["Overall"], cmap="YlOrRd")
                .background_gradient(subset=["Citation"], cmap="Blues")
                .background_gradient(subset=["Recency"], cmap="Greens")
                .format({"Overall": "{:.3f}", "Citation": "{:.2f}", "Recency": "{:.2f}",
                         "Relevance": "{:.2f}", "Source Auth.": "{:.2f}", "Method.": "{:.2f}"}),
        width='stretch',
        hide_index=True,
    )

with tab2:
    # Stacked bar: Score breakdown for top 15
    top15 = rankings[:15]
    fig = go.Figure()

    colors = {"Citations": "#4361ee", "Recency": "#26de81", "Relevance": "#f7b731",
              "Source Auth": "#a55eea", "Methodology": "#fc5c65"}
    fields = [("citation_score", "Citations", 0.30), ("recency_score", "Recency", 0.20),
              ("relevance_score", "Relevance", 0.25), ("source_authority_score", "Source Auth", 0.15),
              ("methodology_score", "Methodology", 0.10)]

    for field, label, weight in fields:
        fig.add_trace(go.Bar(
            name=f"{label} ({int(weight*100)}%)",
            y=[r["title"][:30] + "..." for r in top15],
            x=[r[field] * weight for r in top15],
            orientation="h",
            marker_color=colors[label],
        ))

    fig.update_layout(
        barmode="stack", height=550,
        title="📊 Weighted Score Breakdown (Top 15)",
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis_title="Weighted Score",
    )
    st.plotly_chart(fig, width='stretch')

    # Radar chart for top 5
    st.markdown("### 🎯 Radar Comparison (Top 5)")
    categories = ["Citation", "Recency", "Relevance", "Source Auth", "Methodology"]

    fig2 = go.Figure()
    color_list = ["#4361ee", "#26de81", "#f7b731", "#a55eea", "#fc5c65"]
    for i, r in enumerate(rankings[:5]):
        values = [r["citation_score"], r["recency_score"], r["relevance_score"],
                  r["source_authority_score"], r["methodology_score"]]
        fig2.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            name=r["title"][:30] + "...",
            fill="toself",
            opacity=0.6,
            line=dict(color=color_list[i]),
        ))

    fig2.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        height=500,
        margin=dict(l=40, r=40, t=20, b=20),
    )
    st.plotly_chart(fig2, width='stretch')

with tab3:
    # Detailed cards for top 10
    for i, r in enumerate(rankings[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"

        with st.expander(f"{medal} {r['title']}", expanded=(i == 1)):
            mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
            mc1.metric("Overall", f"{r['overall_score']:.3f}")
            mc2.metric("Citation", f"{r['citation_score']:.2f}")
            mc3.metric("Recency", f"{r['recency_score']:.2f}")
            mc4.metric("Relevance", f"{r['relevance_score']:.2f}")
            mc5.metric("Source Auth", f"{r['source_authority_score']:.2f}")
            mc6.metric("Methodology", f"{r['methodology_score']:.2f}")

            # Mini bar
            scores = {
                "Citation (30%)": r["citation_score"] * 0.30,
                "Relevance (25%)": r["relevance_score"] * 0.25,
                "Recency (20%)": r["recency_score"] * 0.20,
                "Source (15%)": r["source_authority_score"] * 0.15,
                "Method (10%)": r["methodology_score"] * 0.10,
            }
            sdf = pd.DataFrame(list(scores.items()), columns=["Signal", "Contribution"])
            fig3 = px.bar(sdf, x="Contribution", y="Signal", orientation="h",
                         color="Signal", color_discrete_sequence=["#4361ee", "#f7b731", "#26de81", "#a55eea", "#fc5c65"])
            fig3.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
            st.plotly_chart(fig3, width='stretch')
