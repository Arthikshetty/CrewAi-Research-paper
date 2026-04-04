import streamlit as st
import plotly.express as px
import pandas as pd

st.title("🕸️ Citation Network")

if "results" not in st.session_state:
    st.info("Run an analysis first from the main page.")
    st.stop()

results = st.session_state["results"]
papers = results.get("papers", [])

if not papers:
    st.warning("No papers available.")
    st.stop()

# Publication trend
st.markdown("### 📈 Publication Trend Over Time")
years_data = {}
for p in papers:
    y = p.get("year")
    if y:
        years_data[y] = years_data.get(y, 0) + 1

if years_data:
    trend_df = pd.DataFrame(
        sorted(years_data.items()), columns=["Year", "Papers"]
    )
    fig = px.bar(trend_df, x="Year", y="Papers", color="Papers",
                 color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)

# Source distribution
st.markdown("### 📊 Papers by Source")
source_counts = {}
for p in papers:
    s = p.get("source", "unknown")
    source_counts[s] = source_counts.get(s, 0) + 1

source_df = pd.DataFrame(
    sorted(source_counts.items(), key=lambda x: x[1], reverse=True),
    columns=["Source", "Count"]
)
fig2 = px.pie(source_df, values="Count", names="Source", title="Distribution by Source")
st.plotly_chart(fig2, use_container_width=True)

# Citation distribution
st.markdown("### 📊 Citation Distribution")
citation_data = [p.get("citations_count", 0) for p in papers if p.get("citations_count", 0) > 0]
if citation_data:
    fig3 = px.histogram(x=citation_data, nbins=30, labels={"x": "Citation Count", "y": "Number of Papers"})
    fig3.update_layout(title="Citation Count Distribution")
    st.plotly_chart(fig3, use_container_width=True)

# Citation network visualization
st.markdown("### 🕸️ Citation Network Graph")
st.markdown("_Interactive graph requires Neo4j connection with paper citation data._")

try:
    import networkx as nx
    from pyvis.network import Network
    import tempfile

    G = nx.DiGraph()
    best_papers = results.get("best_base_papers", [])
    best_ids = {bp["paper_id"] for bp in best_papers}

    # Add nodes
    for p in papers[:50]:  # Limit to 50 for performance
        color = "#FFD700" if p.get("id") in best_ids else "#97c2fc"
        size = max(10, min(50, p.get("citations_count", 0) / 10))
        G.add_node(
            p.get("id", p.get("title", "")[:30]),
            label=p.get("title", "")[:40],
            title=f"{p.get('title')}\nYear: {p.get('year')}\nCitations: {p.get('citations_count', 0)}",
            size=size,
            color=color,
        )

    # Add edges based on DOI references
    doi_to_id = {}
    for p in papers:
        if p.get("doi"):
            doi_to_id[p["doi"].lower()] = p.get("id", "")

    for p in papers[:50]:
        for ref in p.get("references", []):
            target = doi_to_id.get(ref.lower())
            if target and G.has_node(target):
                G.add_edge(p.get("id", ""), target)

    if G.number_of_nodes() > 0:
        net = Network(height="600px", width="100%", directed=True, notebook=False)
        net.from_nx(G)
        net.set_options('{"physics": {"barnesHut": {"gravitationalConstant": -3000}}}')

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            net.save_graph(f.name)
            with open(f.name, "r") as html_file:
                html_content = html_file.read()
            st.components.v1.html(html_content, height=620)
    else:
        st.info("Not enough citation data to build a network visualization.")

except ImportError:
    st.info("Install pyvis and networkx for interactive graph visualization.")
