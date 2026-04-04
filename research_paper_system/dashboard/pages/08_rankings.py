import streamlit as st
import pandas as pd

st.title("⭐ Paper Rankings")

if "results" not in st.session_state:
    st.info("Run an analysis first from the main page.")
    st.stop()

results = st.session_state["results"]
rankings = results.get("rankings", [])

if not rankings:
    st.warning("No ranking data available.")
    st.stop()

st.markdown(f"### {len(rankings)} papers ranked by multi-signal scoring")

df = pd.DataFrame([
    {
        "Rank": r["rank_position"],
        "Title": r["title"][:80],
        "Overall": f"{r['overall_score']:.3f}",
        "Citations": f"{r['citation_score']:.2f}",
        "Recency": f"{r['recency_score']:.2f}",
        "Relevance": f"{r['relevance_score']:.2f}",
        "Source Auth": f"{r['source_authority_score']:.2f}",
    }
    for r in rankings[:50]
])

st.dataframe(df, use_container_width=True, hide_index=True)

# Score breakdown chart
st.markdown("### Score Breakdown (Top 10)")
import plotly.graph_objects as go

top10 = rankings[:10]
fig = go.Figure()
categories = ["citation_score", "recency_score", "relevance_score", "source_authority_score", "methodology_score"]
labels = ["Citations", "Recency", "Relevance", "Source Auth", "Methodology"]

for cat, label in zip(categories, labels):
    fig.add_trace(go.Bar(
        name=label,
        x=[r["title"][:30] for r in top10],
        y=[r[cat] for r in top10],
    ))

fig.update_layout(barmode="stack", xaxis_tickangle=-45, height=500)
st.plotly_chart(fig, use_container_width=True)
