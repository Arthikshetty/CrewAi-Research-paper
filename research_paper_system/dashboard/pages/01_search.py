import streamlit as st
import pandas as pd

st.title("📄 Discovered Papers")

if "results" not in st.session_state:
    st.info("Run an analysis first from the main page.")
    st.stop()

results = st.session_state["results"]
papers = results.get("papers", [])

if not papers:
    st.warning("No papers found.")
    st.stop()

st.markdown(f"**{len(papers)} papers** discovered for: _{st.session_state.get('topic', '')}_")

# Filters
col1, col2, col3 = st.columns(3)
sources = sorted(set(p.get("source", "") for p in papers))
selected_sources = col1.multiselect("Filter by Source", sources, default=sources)

years = sorted(set(p.get("year") for p in papers if p.get("year")))
if years:
    year_range = col2.slider("Year Range", min(years), max(years), (min(years), max(years)))
else:
    year_range = (0, 9999)

sort_by = col3.selectbox("Sort by", ["Citations (high)", "Year (newest)", "Title (A-Z)"])

# Filter papers
filtered = [
    p for p in papers
    if p.get("source", "") in selected_sources
    and (p.get("year") or 0) >= year_range[0]
    and (p.get("year") or 9999) <= year_range[1]
]

# Sort
if sort_by == "Citations (high)":
    filtered.sort(key=lambda p: p.get("citations_count", 0), reverse=True)
elif sort_by == "Year (newest)":
    filtered.sort(key=lambda p: p.get("year") or 0, reverse=True)
elif sort_by == "Title (A-Z)":
    filtered.sort(key=lambda p: p.get("title", "").lower())

st.markdown(f"Showing **{len(filtered)}** of {len(papers)} papers")

# Display papers
for i, paper in enumerate(filtered):
    with st.expander(f"**{paper.get('title', 'Untitled')}** ({paper.get('year', 'N/A')}) — {paper.get('source', '')}"):
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Citations", paper.get("citations_count", 0))
        col_b.metric("Source", paper.get("source", "N/A"))
        col_c.metric("Year", paper.get("year", "N/A"))

        authors = paper.get("authors", [])
        author_names = ", ".join(a.get("name", "") for a in authors[:10])
        st.markdown(f"**Authors:** {author_names}")

        if paper.get("doi"):
            st.markdown(f"**DOI:** [{paper['doi']}](https://doi.org/{paper['doi']})")
        if paper.get("url"):
            st.markdown(f"**URL:** [{paper['url']}]({paper['url']})")

        abstract = paper.get("abstract", "")
        if abstract:
            st.markdown(f"**Abstract:** {abstract[:500]}{'...' if len(abstract) > 500 else ''}")

# Export
st.markdown("---")
if st.button("📥 Export to CSV"):
    df = pd.DataFrame([
        {
            "Title": p.get("title"),
            "Authors": ", ".join(a.get("name", "") for a in p.get("authors", [])[:5]),
            "Year": p.get("year"),
            "Source": p.get("source"),
            "Citations": p.get("citations_count"),
            "DOI": p.get("doi"),
            "URL": p.get("url"),
        }
        for p in filtered
    ])
    st.download_button("Download CSV", df.to_csv(index=False), "papers.csv", "text/csv")
