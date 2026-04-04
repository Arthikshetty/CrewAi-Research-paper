import streamlit as st

st.title("🏆 Best Base Paper")

if "results" not in st.session_state:
    st.info("Run an analysis first from the main page.")
    st.stop()

results = st.session_state["results"]
best_papers = results.get("best_base_papers", [])

if not best_papers:
    st.warning("No base paper data available. This requires Neo4j to be running.")
    st.stop()

# Hero card: #1 Best Base Paper
top = best_papers[0]
st.markdown("### 🥇 The Most-Referenced Foundational Paper")

st.markdown(
    f"""
    <div style="border: 2px solid gold; border-radius: 10px; padding: 20px; background-color: #fffbe6;">
        <h3>{top['title']}</h3>
        <p><strong>Year:</strong> {top.get('year', 'N/A')} | <strong>Source:</strong> {top.get('source', 'N/A')}</p>
        <p><strong>Cited by {top['total_incoming_citations']} discovered papers</strong> |
           Global citations: {top['total_global_citations']}</p>
        <p><strong>PageRank Score:</strong> {top['pagerank_score']:.4f}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if top.get("why_base_paper"):
    st.markdown(f"**Why it's foundational:** {top['why_base_paper']}")

# Referenced by section
if top.get("referenced_by"):
    with st.expander(f"📚 Referenced by ({len(top['referenced_by'])} papers)"):
        for ref in top["referenced_by"]:
            st.markdown(f"- {ref}")

# Runner-up base papers
if len(best_papers) > 1:
    st.markdown("---")
    st.markdown("### Runner-up Base Papers")
    for i, bp in enumerate(best_papers[1:], 2):
        with st.expander(f"#{i} {bp['title']}"):
            col1, col2, col3 = st.columns(3)
            col1.metric("In-degree", bp["total_incoming_citations"])
            col2.metric("Global Citations", bp["total_global_citations"])
            col3.metric("PageRank", f"{bp['pagerank_score']:.4f}")
            if bp.get("referenced_by"):
                st.markdown("**Referenced by:** " + ", ".join(bp["referenced_by"][:5]))
