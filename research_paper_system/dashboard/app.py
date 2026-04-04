import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

st.set_page_config(
    page_title="Research Paper Discovery & Analysis",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔬 Autonomous Research Paper Discovery & Analysis")

# Sidebar
st.sidebar.title("Search Configuration")
topic = st.sidebar.text_input("Research Topic", placeholder="e.g., Federated Learning for Healthcare")
years = st.sidebar.slider("Years to search", 1, 20, 5)
min_papers = st.sidebar.slider("Min papers per source", 5, 50, 20)
num_ideas = st.sidebar.slider("Number of ideas to generate", 1, 10, 5)

# Source selection
st.sidebar.markdown("### Sources")
sources_enabled = {
    "ArXiv": st.sidebar.checkbox("ArXiv", value=True),
    "Semantic Scholar": st.sidebar.checkbox("Semantic Scholar", value=True),
    "CrossRef": st.sidebar.checkbox("CrossRef", value=True),
    "OpenAlex": st.sidebar.checkbox("OpenAlex", value=True),
    "CORE": st.sidebar.checkbox("CORE", value=True),
    "PubMed": st.sidebar.checkbox("PubMed", value=True),
    "DBLP": st.sidebar.checkbox("DBLP", value=True),
    "IEEE Xplore": st.sidebar.checkbox("IEEE Xplore", value=True),
    "Scopus": st.sidebar.checkbox("Scopus", value=True),
    "ScienceDirect": st.sidebar.checkbox("ScienceDirect", value=True),
    "Google Scholar": st.sidebar.checkbox("Google Scholar", value=False),
}

run_button = st.sidebar.button("🚀 Run Analysis", type="primary", use_container_width=True)

if run_button and topic:
    from dotenv import load_dotenv
    load_dotenv()
    from src.crew import ResearchPaperCrew
    from src.services.progress_tracker import progress_tracker

    with st.status("Analyzing research papers...", expanded=True) as status:
        progress_placeholder = st.empty()

        def update_progress(progress_data):
            lines = []
            for step in progress_data["steps"]:
                if step["status"] == "completed":
                    lines.append(f"✅ {step['name']}: {step['message']}")
                elif step["status"] == "running":
                    lines.append(f"⏳ {step['name']}...")
                elif step["status"] == "error":
                    lines.append(f"❌ {step['name']}: {step['message']}")

            if lines:
                progress_placeholder.markdown("\n\n".join(lines))

        progress_tracker.add_callback(update_progress)

        crew = ResearchPaperCrew()
        results = crew.run(
            topic=topic,
            years=years,
            min_papers=min_papers,
            num_ideas=num_ideas,
        )

        st.session_state["results"] = results
        st.session_state["topic"] = topic

        status.update(label="✅ Analysis complete!", state="complete")

    st.success(f"Found **{results.get('paper_count', 0)}** unique papers across all sources.")
    st.info("Navigate to the pages in the sidebar to explore results.")

elif run_button and not topic:
    st.warning("Please enter a research topic.")

# Show existing results summary
if "results" in st.session_state:
    results = st.session_state["results"]
    st.markdown("---")
    st.subheader(f"Current Results: {st.session_state.get('topic', '')}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Papers Found", results.get("paper_count", 0))
    col2.metric("Best Base Paper", results["best_base_papers"][0]["title"][:40] + "..." if results.get("best_base_papers") else "N/A")
    col3.metric("Top Author", results["top_authors"][0]["author_name"] if results.get("top_authors") else "N/A")
    col4.metric("Rankings", len(results.get("rankings", [])))
else:
    st.markdown("---")
    st.markdown(
        """
        ### How it works
        1. Enter a research topic in the sidebar
        2. Click **Run Analysis** — the system makes LIVE API calls to 10+ academic sources
        3. Papers are fetched, deduplicated, ranked, summarized, and analyzed in real-time
        4. Explore results across 8 dashboard pages

        **Sources:** ArXiv, Semantic Scholar, IEEE Xplore, Scopus, ScienceDirect,
        CrossRef, OpenAlex, CORE, PubMed, DBLP, Google Scholar

        **Features:** Best base paper identification, top author discovery,
        limitation extraction, research gap detection, problem statement generation
        """
    )
