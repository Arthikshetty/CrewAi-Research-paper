import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from dashboard.components.theme import inject_custom_css, render_source_badge, check_results

inject_custom_css()
results = check_results()
papers = results.get("papers", [])

if not papers:
    st.warning("No papers found.")
    st.stop()

# Header
st.markdown("""
<div class="hero-header" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);">
    <h1>📄 Discovered Papers</h1>
    <p>Browse, filter, and export all papers discovered across academic sources</p>
</div>
""", unsafe_allow_html=True)

topic = st.session_state.get("topic", "")

# KPI row
col1, col2, col3, col4 = st.columns(4)
source_set = set(p.get("source", "") for p in papers)
avg_citations = sum(p.get("citations_count", 0) for p in papers) / len(papers) if papers else 0
with col1:
    st.markdown(f'<div class="metric-card accent-blue"><div class="metric-value">{len(papers)}</div><div class="metric-label">Total Papers</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card accent-green"><div class="metric-value">{len(source_set)}</div><div class="metric-label">Sources Used</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card accent-purple"><div class="metric-value">{avg_citations:.0f}</div><div class="metric-label">Avg Citations</div></div>', unsafe_allow_html=True)
with col4:
    oa_count = sum(1 for p in papers if p.get("open_access"))
    st.markdown(f'<div class="metric-card accent-gold"><div class="metric-value">{oa_count}</div><div class="metric-label">Open Access</div></div>', unsafe_allow_html=True)

st.markdown("")

# Filters
with st.container():
    col1, col2, col3 = st.columns([3, 3, 2])
    sources = sorted(set(p.get("source", "") for p in papers))
    nice_sources = {s: s.replace("_", " ").title() for s in sources}
    selected_sources = col1.multiselect(
        "🏷️ Filter by Source",
        sources,
        default=sources,
        format_func=lambda x: nice_sources.get(x, x),
    )

    all_years = sorted(set(p.get("year") for p in papers if p.get("year")))
    if all_years:
        year_range = col2.slider("📅 Year Range", min(all_years), max(all_years), (min(all_years), max(all_years)))
    else:
        year_range = (0, 9999)

    sort_by = col3.selectbox("↕️ Sort by", ["Citations (high)", "Year (newest)", "Year (oldest)", "Title (A-Z)"])

# Filter + Sort
filtered = [
    p for p in papers
    if p.get("source", "") in selected_sources
    and (p.get("year") or 0) >= year_range[0]
    and (p.get("year") or 9999) <= year_range[1]
]
if sort_by == "Citations (high)":
    filtered.sort(key=lambda p: p.get("citations_count", 0), reverse=True)
elif sort_by == "Year (newest)":
    filtered.sort(key=lambda p: p.get("year") or 0, reverse=True)
elif sort_by == "Year (oldest)":
    filtered.sort(key=lambda p: p.get("year") or 9999)
elif sort_by == "Title (A-Z)":
    filtered.sort(key=lambda p: p.get("title", "").lower())

st.markdown(f"Showing **{len(filtered)}** of {len(papers)} papers")
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# Paper Cards
for i, paper in enumerate(filtered):
    src = paper.get("source", "")
    badge = render_source_badge(src)
    citations = paper.get("citations_count", 0)
    year = paper.get("year", "N/A")
    title = paper.get("title", "Untitled")
    authors = paper.get("authors", [])
    author_str = ", ".join(a.get("name", "") for a in authors[:5])
    if len(authors) > 5:
        author_str += f" + {len(authors) - 5} more"

    with st.expander(f"**{title}**"):
        st.markdown(f"""
        <div style="display:flex; gap:1.5rem; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap;">
            {badge}
            <span style="color:#6c757d; font-size:0.85rem;">📅 {year}</span>
            <span style="color:#6c757d; font-size:0.85rem;">📊 {citations:,} citations</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**Authors:** {author_str}")

        if paper.get("doi"):
            st.markdown(f"**DOI:** [{paper['doi']}](https://doi.org/{paper['doi']})")
        if paper.get("url"):
            st.markdown(f"[🔗 View Paper]({paper['url']})")

        abstract = paper.get("abstract", "")
        if abstract:
            st.markdown(f"**Abstract:** {abstract[:600]}{'...' if len(abstract) > 600 else ''}")

        if paper.get("keywords"):
            kw = " · ".join(paper["keywords"][:8])
            st.markdown(f"**Keywords:** {kw}")

# Export Section
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 📥 Export Data")
col_e1, col_e2 = st.columns(2)

with col_e1:
    df = pd.DataFrame([
        {
            "Title": p.get("title"),
            "Authors": ", ".join(a.get("name", "") for a in p.get("authors", [])[:5]),
            "Year": p.get("year"),
            "Source": p.get("source", "").replace("_", " ").title(),
            "Citations": p.get("citations_count"),
            "DOI": p.get("doi"),
            "URL": p.get("url"),
        }
        for p in filtered
    ])
    st.download_button(
        "📄 Download CSV",
        df.to_csv(index=False),
        "papers.csv",
        "text/csv",
        use_container_width=True,
    )

with col_e2:
    # BibTeX export
    bibtex_lines = []
    for p in filtered[:50]:
        key = (p.get("doi") or p.get("title", "")[:20]).replace(" ", "_").replace("/", "_")
        authors_bib = " and ".join(a.get("name", "") for a in p.get("authors", [])[:5])
        bibtex_lines.append(
            f"@article{{{key},\n  title={{{p.get('title', '')}}},\n"
            f"  author={{{authors_bib}}},\n  year={{{p.get('year', '')}}},\n"
            f"  doi={{{p.get('doi', '')}}}\n}}"
        )
    st.download_button(
        "📚 Download BibTeX",
        "\n\n".join(bibtex_lines),
        "papers.bib",
        "text/plain",
        use_container_width=True,
    )
