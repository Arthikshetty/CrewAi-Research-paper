"""Professional CSS theme and reusable UI components for the dashboard."""
import streamlit as st


def inject_custom_css():
    """Inject professional CSS styling into the Streamlit app."""
    st.markdown("""
    <style>
    /* === Global === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
    }

    /* === Hero Header === */
    .hero-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 60%);
    }
    .hero-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
    }
    .hero-header p {
        font-size: 1.05rem;
        opacity: 0.85;
        margin: 0;
        font-weight: 300;
    }

    /* === Metric Cards === */
    .metric-card {
        background: white;
        border: 1px solid #e8eaed;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6c757d;
        margin-top: 0.3rem;
        font-weight: 600;
    }
    .metric-card.accent-blue { border-top: 3px solid #4361ee; }
    .metric-card.accent-gold { border-top: 3px solid #f7b731; }
    .metric-card.accent-green { border-top: 3px solid #26de81; }
    .metric-card.accent-purple { border-top: 3px solid #a55eea; }
    .metric-card.accent-red { border-top: 3px solid #fc5c65; }

    /* === Gold Hero Card (Best Paper) === */
    .gold-hero-card {
        background: linear-gradient(135deg, #fff9e6 0%, #fff3cc 100%);
        border: 2px solid #f7b731;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        position: relative;
        box-shadow: 0 4px 20px rgba(247, 183, 49, 0.15);
    }
    .gold-hero-card .trophy {
        position: absolute;
        top: -15px;
        right: 20px;
        font-size: 3rem;
        opacity: 0.3;
    }
    .gold-hero-card h2 {
        color: #1a1a2e;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 0.8rem 0;
        padding-right: 60px;
    }
    .gold-hero-card .stats-row {
        display: flex;
        gap: 2rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    .gold-hero-card .stat-item {
        display: flex;
        flex-direction: column;
    }
    .gold-hero-card .stat-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #b8860b;
    }
    .gold-hero-card .stat-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #8b7355;
    }

    /* === Paper Card === */
    .paper-card {
        background: white;
        border: 1px solid #e8eaed;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    .paper-card:hover {
        border-color: #4361ee;
        box-shadow: 0 4px 16px rgba(67, 97, 238, 0.1);
    }
    .paper-card .paper-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    .paper-card .paper-meta {
        font-size: 0.85rem;
        color: #6c757d;
        margin-bottom: 0.5rem;
    }
    .paper-card .paper-abstract {
        font-size: 0.9rem;
        color: #495057;
        line-height: 1.6;
    }

    /* === Author Card === */
    .author-card {
        background: white;
        border: 1px solid #e8eaed;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    .author-rank {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.2rem;
        color: white;
        flex-shrink: 0;
    }
    .rank-1 { background: linear-gradient(135deg, #f7b731, #e6a100); }
    .rank-2 { background: linear-gradient(135deg, #a5b1c2, #8e99a4); }
    .rank-3 { background: linear-gradient(135deg, #cd7f32, #b8722e); }
    .rank-other { background: linear-gradient(135deg, #4361ee, #3651d4); }

    /* === Tag / Badge === */
    .source-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-arxiv { background: #fff3e0; color: #e65100; }
    .badge-semantic { background: #e3f2fd; color: #1565c0; }
    .badge-ieee { background: #e8f5e9; color: #2e7d32; }
    .badge-scopus { background: #f3e5f5; color: #7b1fa2; }
    .badge-crossref { background: #fce4ec; color: #c62828; }
    .badge-openalex { background: #e0f7fa; color: #00695c; }
    .badge-pubmed { background: #efebe9; color: #4e342e; }
    .badge-core { background: #f1f8e9; color: #558b2f; }
    .badge-dblp { background: #e8eaf6; color: #283593; }
    .badge-default { background: #f5f5f5; color: #616161; }

    /* === Section Divider === */
    .section-divider {
        border: 0;
        height: 1px;
        background: linear-gradient(to right, transparent, #dee2e6, transparent);
        margin: 2rem 0;
    }

    /* === Progress Steps === */
    .progress-step {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
        font-size: 0.92rem;
    }
    .progress-step .step-icon {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        flex-shrink: 0;
    }
    .step-done { background: #26de81; color: white; }
    .step-running { background: #4361ee; color: white; animation: pulse 1.5s infinite; }
    .step-error { background: #fc5c65; color: white; }
    .step-waiting { background: #e8eaed; color: #adb5bd; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* === Sidebar Styling === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a3e 40%, #24243e 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    /* Sidebar brand logo area */
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        background: transparent;
        padding: 0.5rem 1rem;
    }

    /* Navigation links */
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        padding: 0.5rem 0.75rem;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        display: flex;
        align-items: center;
        padding: 0.6rem 1rem;
        margin: 3px 0;
        border-radius: 10px;
        text-decoration: none !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a span {
        text-transform: capitalize !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.3px;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: rgba(67, 97, 238, 0.15) !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover span {
        color: #7c9aff !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-selected="true"],
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a.active {
        background: linear-gradient(135deg, rgba(67,97,238,0.25) 0%, rgba(54,81,212,0.18) 100%) !important;
        border-left: 3px solid #4361ee;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-selected="true"] span,
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a.active span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Sidebar headings */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"] h2 {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stSidebar"] h4 {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #8888aa !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Sidebar section dividers */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 0.75rem 0 !important;
    }

    /* Sidebar text inputs */
    [data-testid="stSidebar"] .stTextInput > div > div {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stTextInput > div > div:focus-within {
        border-color: #4361ee !important;
        box-shadow: 0 0 0 2px rgba(67,97,238,0.2) !important;
        background: rgba(255,255,255,0.08) !important;
    }
    [data-testid="stSidebar"] .stTextInput input {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: rgba(255,255,255,0.35) !important;
    }
    [data-testid="stSidebar"] .stTextInput label {
        color: #b0b0cc !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
    }

    /* Sidebar sliders */
    [data-testid="stSidebar"] .stSlider label {
        color: #b0b0cc !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
        background: #4361ee !important;
        border-color: #4361ee !important;
    }

    /* Sidebar checkboxes */
    [data-testid="stSidebar"] .stCheckbox label {
        color: #c8c8e0 !important;
        font-size: 0.84rem !important;
    }
    [data-testid="stSidebar"] .stCheckbox [data-testid="stCheckbox"] span[role="checkbox"][aria-checked="true"] {
        background-color: #4361ee !important;
        border-color: #4361ee !important;
    }

    /* Sidebar expander */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: #c8c8e0 !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background: rgba(255,255,255,0.08) !important;
    }
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }

    /* Primary button (Run Analysis) */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%) !important;
        border: none !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        border-radius: 10px !important;
        padding: 0.7rem 1rem !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 15px rgba(67,97,238,0.3) !important;
        transition: all 0.3s ease !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(67,97,238,0.5) !important;
        transform: translateY(-1px);
    }

    /* Secondary buttons (Demo, Load Last) */
    [data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: #c8c8e0 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 0.55rem 1rem !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {
        background: rgba(255,255,255,0.12) !important;
        border-color: rgba(255,255,255,0.2) !important;
        color: #ffffff !important;
    }

    /* Sidebar scrollbar */
    [data-testid="stSidebar"]::-webkit-scrollbar {
        width: 4px;
    }
    [data-testid="stSidebar"]::-webkit-scrollbar-track {
        background: transparent;
    }
    [data-testid="stSidebar"]::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
    }
    [data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.2);
    }

    /* === Info Banner === */
    .info-banner {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4361ee;
    }
    .info-banner h4 {
        margin: 0 0 0.5rem 0;
        color: #1a1a2e;
    }
    .info-banner p {
        margin: 0;
        color: #495057;
        font-size: 0.92rem;
    }

    /* === Data Table Enhancement === */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* === Tab Styling === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-weight: 500;
    }

    /* === Empty State === */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #adb5bd;
    }
    .empty-state .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .empty-state h3 {
        color: #6c757d;
        margin-bottom: 0.5rem;
    }
    .empty-state p {
        font-size: 0.95rem;
    }

    /* === Runner-up Card === */
    .runner-card {
        background: white;
        border: 1px solid #e8eaed;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #a5b1c2;
    }
    .runner-card.silver { border-left-color: #a5b1c2; }
    .runner-card.bronze { border-left-color: #cd7f32; }
    </style>
    """, unsafe_allow_html=True)


def render_metric_card(value, label, accent="blue"):
    """Render a styled metric card."""
    st.markdown(f"""
    <div class="metric-card accent-{accent}">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_source_badge(source):
    """Render a colored source badge."""
    badge_map = {
        "arxiv": "badge-arxiv", "semantic_scholar": "badge-semantic",
        "ieee": "badge-ieee", "scopus": "badge-scopus",
        "crossref": "badge-crossref", "openalex": "badge-openalex",
        "pubmed": "badge-pubmed", "core": "badge-core",
        "dblp": "badge-dblp",
    }
    css_class = badge_map.get(source, "badge-default")
    nice_name = source.replace("_", " ").title()
    return f'<span class="source-badge {css_class}">{nice_name}</span>'


def render_empty_state(icon, title, description):
    """Render a professional empty state."""
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)


def check_results():
    """Check if results exist in session state, show empty state if not."""
    if "results" not in st.session_state:
        inject_custom_css()
        render_empty_state(
            "🔬",
            "No Analysis Results Yet",
            "Go to the main page, enter a research topic, and click Run Analysis to get started."
        )
        st.stop()
    return st.session_state["results"]
