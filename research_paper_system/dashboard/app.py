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

from dashboard.components.theme import inject_custom_css, render_metric_card

inject_custom_css()

# === Hero Header ===
st.markdown("""
<div class="hero-header">
    <h1>🔬 Research Paper Discovery & Analysis</h1>
    <p>AI-powered multi-agent system that discovers, analyzes, and synthesizes research across 10+ academic sources in real-time</p>
</div>
""", unsafe_allow_html=True)

# === Sidebar ===
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    topic = st.text_input("🔎 Research Topic", placeholder="e.g., Federated Learning for Healthcare")

    with st.expander("🎛️ Advanced Settings", expanded=False):
        years = st.slider("Years to search", 1, 20, 5)
        min_papers = st.slider("Min papers per source", 5, 50, 20)
        num_ideas = st.slider("Ideas to generate", 1, 10, 5)

    st.markdown("#### 📚 Sources")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        src_arxiv = st.checkbox("ArXiv", value=True)
        src_ss = st.checkbox("Semantic Scholar", value=True)
        src_cr = st.checkbox("CrossRef", value=True)
        src_oa = st.checkbox("OpenAlex", value=True)
        src_core = st.checkbox("CORE", value=True)
        src_pm = st.checkbox("PubMed", value=True)
    with col_s2:
        src_dblp = st.checkbox("DBLP", value=True)
        src_ieee = st.checkbox("IEEE Xplore", value=True)
        src_scopus = st.checkbox("Scopus", value=True)
        src_sd = st.checkbox("ScienceDirect", value=True)
        src_gs = st.checkbox("Google Scholar", value=False)

    st.markdown("")
    run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

    st.markdown("---")
    demo_button = st.button("🎮 Load Demo Data", use_container_width=True,
                            help="Load pre-computed results to explore the dashboard without API keys")

    # Check for latest_results.json from a previous run
    _latest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "latest_results.json")
    if os.path.exists(_latest_path) and "results" not in st.session_state:
        load_last = st.button("📂 Load Last Run", use_container_width=True,
                              help="Reload results from your most recent analysis")
    else:
        load_last = False

# === Demo Mode ===
if demo_button:
    import json as _json
    _demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "demo", "demo_results.json")
    if os.path.exists(_demo_path):
        with open(_demo_path, "r", encoding="utf-8") as _f:
            st.session_state["results"] = _json.load(_f)
            st.session_state["topic"] = st.session_state["results"].get("topic", "Demo Topic")
        st.rerun()
    else:
        st.error("Demo data not found. Place demo_results.json in data/demo/.")

# === Load Last Run ===
if load_last:
    import json as _json
    _latest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "latest_results.json")
    with open(_latest_path, "r", encoding="utf-8") as _f:
        st.session_state["results"] = _json.load(_f)
        st.session_state["topic"] = st.session_state["results"].get("topic", "Previous Run")
    st.rerun()

# === Run Pipeline ===
if run_button and topic:
    from dotenv import load_dotenv
    load_dotenv()
    from src.crew import ResearchPaperCrew
    from src.services.progress_tracker import progress_tracker

    with st.status("🔬 Analyzing research papers...", expanded=True) as status:
        progress_container = st.container()

        def update_progress(progress_data):
            lines = []
            for step in progress_data["steps"]:
                if step["status"] == "completed":
                    lines.append(f'<div class="progress-step"><span class="step-icon step-done">✓</span> <strong>{step["name"]}</strong> — {step["message"]}</div>')
                elif step["status"] == "running":
                    lines.append(f'<div class="progress-step"><span class="step-icon step-running">●</span> <strong>{step["name"]}</strong></div>')
                elif step["status"] == "error":
                    lines.append(f'<div class="progress-step"><span class="step-icon step-error">✕</span> <strong>{step["name"]}</strong> — {step["message"]}</div>')
            if lines:
                progress_container.markdown("".join(lines), unsafe_allow_html=True)

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

    st.balloons()

elif run_button and not topic:
    st.warning("Please enter a research topic to begin.")

# === Results Dashboard ===
if "results" in st.session_state:
    results = st.session_state["results"]
    topic_display = st.session_state.get("topic", "")

    st.markdown(f"### 📊 Results Dashboard — _{topic_display}_")

    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_metric_card(results.get("paper_count", 0), "Papers Found", "blue")
    with col2:
        bp = results.get("best_base_papers", [])
        bp_text = bp[0]["title"][:25] + "..." if bp else "—"
        render_metric_card(bp_text, "Best Base Paper", "gold")
    with col3:
        ta = results.get("top_authors", [])
        ta_text = ta[0]["author_name"].split(",")[0] if ta else "—"
        render_metric_card(ta_text, "Top Author", "green")
    with col4:
        render_metric_card(len(results.get("rankings", [])), "Ranked Papers", "purple")
    with col5:
        tasks = results.get("task_outputs", [])
        render_metric_card(len(tasks), "AI Tasks Done", "red")

    st.markdown("")

    # Quick Glance Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "🏆 Highlights", "📋 Task Outputs"])

    with tab1:
        import pandas as pd
        import plotly.express as px

        papers = results.get("papers", [])
        if papers:
            # Source distribution + trend side by side
            c1, c2 = st.columns(2)
            with c1:
                source_counts = {}
                for p in papers:
                    s = p.get("source", "unknown").replace("_", " ").title()
                    source_counts[s] = source_counts.get(s, 0) + 1
                sdf = pd.DataFrame(sorted(source_counts.items(), key=lambda x: x[1], reverse=True), columns=["Source", "Papers"])
                fig = px.bar(sdf, x="Papers", y="Source", orientation="h",
                             color="Papers", color_continuous_scale="Blues")
                fig.update_layout(title="Papers by Source", height=350, showlegend=False,
                                  margin=dict(l=0, r=0, t=40, b=0), yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                years_data = {}
                for p in papers:
                    y = p.get("year")
                    if y:
                        years_data[y] = years_data.get(y, 0) + 1
                if years_data:
                    tdf = pd.DataFrame(sorted(years_data.items()), columns=["Year", "Papers"])
                    fig2 = px.area(tdf, x="Year", y="Papers", color_discrete_sequence=["#4361ee"])
                    fig2.update_layout(title="Publication Trend", height=350,
                                       margin=dict(l=0, r=0, t=40, b=0))
                    st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🏆 Best Base Paper")
            bp = results.get("best_base_papers", [])
            if bp:
                top = bp[0]
                st.markdown(f"""
                <div class="gold-hero-card">
                    <div class="trophy">🏆</div>
                    <h2>{top['title']}</h2>
                    <div class="stats-row">
                        <div class="stat-item"><span class="stat-value">{top['total_incoming_citations']}</span><span class="stat-label">Internal Citations</span></div>
                        <div class="stat-item"><span class="stat-value">{top['total_global_citations']:,}</span><span class="stat-label">Global Citations</span></div>
                        <div class="stat-item"><span class="stat-value">{top['pagerank_score']:.4f}</span><span class="stat-label">PageRank</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Requires Neo4j connection")

        with c2:
            st.markdown("#### 👤 Top Authors")
            ta = results.get("top_authors", [])
            if ta:
                for i, a in enumerate(ta[:5], 1):
                    rank_class = f"rank-{i}" if i <= 3 else "rank-other"
                    st.markdown(f"""
                    <div class="author-card">
                        <div class="author-rank {rank_class}">{i}</div>
                        <div>
                            <strong>{a['author_name']}</strong><br>
                            <span style="color:#6c757d;font-size:0.85rem">{a['total_papers_on_topic']} papers · {a['total_citations']:,} citations</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Requires Neo4j connection")

    with tab3:
        for i, task in enumerate(results.get("task_outputs", []), 1):
            with st.expander(f"Task {i}: {task.get('task', '')[:80]}"):
                st.markdown(task.get("output", "No output"))

else:
    # === Landing Page ===
    st.markdown("")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="info-banner">
            <h4>🔍 Multi-Source Discovery</h4>
            <p>Search 10+ academic databases simultaneously — ArXiv, Semantic Scholar, Scopus, PubMed, IEEE, and more.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-banner">
            <h4>🤖 AI-Powered Analysis</h4>
            <p>7 specialized AI agents summarize, extract limitations, detect gaps, and generate novel problem statements.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="info-banner">
            <h4>🕸️ Citation Intelligence</h4>
            <p>Neo4j-powered citation graphs with PageRank to find the foundational base paper and top researchers.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding: 2rem 0;">
        <h3 style="color: #6c757d; font-weight: 400;">Enter a research topic in the sidebar and click <strong>Run Analysis</strong> to begin</h3>
    </div>
    """, unsafe_allow_html=True)
