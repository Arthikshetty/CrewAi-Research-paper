import streamlit as st
import pandas as pd

st.title("👤 Top Authors")

if "results" not in st.session_state:
    st.info("Run an analysis first from the main page.")
    st.stop()

results = st.session_state["results"]
top_authors = results.get("top_authors", [])

if not top_authors:
    st.warning("No author data available. This requires Neo4j to be running.")
    st.stop()

st.markdown(f"### Top {len(top_authors)} Authors on: _{st.session_state.get('topic', '')}_")

# Leaderboard table
df = pd.DataFrame([
    {
        "Rank": i,
        "Author": a["author_name"],
        "Papers": a["total_papers_on_topic"],
        "Citations": a["total_citations"],
        "h-index": a.get("h_index") or "N/A",
        "Active Years": a.get("year_range_active", "N/A"),
    }
    for i, a in enumerate(top_authors, 1)
])

st.dataframe(df, use_container_width=True, hide_index=True)

# Bar chart
st.markdown("### Papers by Author")
import plotly.express as px

chart_df = pd.DataFrame([
    {"Author": a["author_name"], "Paper Count": a["total_papers_on_topic"]}
    for a in top_authors
])
fig = px.bar(chart_df, x="Author", y="Paper Count", color="Paper Count",
             color_continuous_scale="Blues")
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# Author detail cards
st.markdown("---")
st.markdown("### Author Profiles")
for i, author in enumerate(top_authors, 1):
    with st.expander(f"#{i} {author['author_name']}"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Papers on Topic", author["total_papers_on_topic"])
        col2.metric("Total Citations", author["total_citations"])
        col3.metric("h-index", author.get("h_index") or "N/A")

        if author.get("affiliations"):
            st.markdown(f"**Affiliations:** {', '.join(author['affiliations'])}")
        if author.get("most_cited_paper"):
            st.markdown(f"**Most Cited Paper:** {author['most_cited_paper']}")
        if author.get("recent_paper"):
            st.markdown(f"**Most Recent Paper:** {author['recent_paper']}")
        if author.get("expertise_keywords"):
            st.markdown(f"**Expertise:** {', '.join(author['expertise_keywords'])}")
