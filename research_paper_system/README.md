<div align="center">

# 🔬 Autonomous Research Paper Discovery & Analysis System

**AI-powered multi-agent system that discovers, analyzes, and synthesizes research papers across 11 academic sources in real-time**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-orange.svg)](https://github.com/joaomdmoura/crewAI)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io)
[![Neo4j](https://img.shields.io/badge/Neo4j-Knowledge%20Graph-green.svg)](https://neo4j.com)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-purple.svg)](https://github.com/facebookresearch/faiss)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Demo Mode](#demo-mode)
- [Docker Deployment](#docker-deployment)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Tech Stack](#tech-stack)

---

## Overview

This system automates the entire research paper discovery and analysis workflow using **7 specialized CrewAI agents** that collaboratively:

1. **Discover** papers from 11 academic databases simultaneously
2. **Rank** papers using a multi-factor scoring algorithm
3. **Summarize** key contributions, methodology, and findings
4. **Extract** limitations with severity ratings
5. **Analyze** citation networks to find the foundational base paper & top authors
6. **Detect** research gaps across methods, data, and theory
7. **Generate** novel problem statements and research ideas

All results are visualized in a professional **8-page Streamlit dashboard** with interactive charts, citation graphs, and export capabilities.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                     │
│  (8 pages: Search · Rankings · Authors · Summaries · …)  │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                 CrewAI Orchestrator                        │
│  Sequential pipeline: 7 agents → 7 tasks → context chain │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬─────────────┘
   │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼
 Search  Summ.  Limit. Citat. Gaps  Probl.  Ideas
 Agent   Agent  Agent  Agent  Agent  Agent  Agent
   │                    │
   ▼                    ▼
┌──────────┐    ┌──────────────┐    ┌──────────────┐
│ 11 Source │    │  Neo4j Graph │    │  FAISS Vector│
│   APIs    │    │  (PageRank)  │    │    Store     │
└──────────┘    └──────────────┘    └──────────────┘
```

---

## Features

| Feature | Description |
|---------|-------------|
| **11 Academic Sources** | ArXiv, Semantic Scholar, IEEE Xplore, Scopus, ScienceDirect, CrossRef, OpenAlex, CORE, PubMed, DBLP, Google Scholar |
| **Smart Deduplication** | Fuzzy title matching + DOI matching to remove duplicates across sources |
| **Multi-Factor Ranking** | Papers scored on citations, recency, relevance, source authority, and methodology |
| **FAISS Semantic Search** | SPECTER2 embeddings for finding semantically related papers |
| **Neo4j Citation Graph** | Knowledge graph with PageRank for base paper identification |
| **Topic Nodes** | Keyword-based topic extraction with `:Topic` nodes and `[:ABOUT]` edges |
| **Author Enrichment** | h-index, affiliations, expertise keywords via Semantic Scholar API |
| **Retry + Caching** | Exponential backoff on failures, 24h disk cache to avoid redundant API calls |
| **Demo Mode** | Pre-computed sample results — explore the dashboard without any API keys |
| **Docker Support** | One-command deployment with `docker compose up` |
| **BibTeX Export** | Export discovered papers in BibTeX format |
| **Professional Dashboard** | Custom CSS theme, Plotly charts, pyvis network graphs, radar charts |

---

## Quick Start

**Option A — Demo mode (no API keys needed):**

```bash
git clone <repo-url> && cd research_paper_system
pip install -r requirements.txt
streamlit run dashboard/app.py
# Click "🎮 Load Demo Data" in the sidebar
```

**Option B — Docker (recommended):**

```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
docker compose up -d
# Open http://localhost:8501
```

**Option C — Full local setup:**

```bash
python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # Edit with your API keys
python -m src.main "federated learning for healthcare" --output results.json
streamlit run dashboard/app.py
```

---

## Installation

### Prerequisites

- Python 3.10+
- (Optional) Neo4j Desktop 5.x or Docker
- (Optional) API keys for paid sources (IEEE, Scopus, etc.)

### Steps

```bash
# 1. Clone
git clone <repo-url>
cd research_paper_system

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — at minimum set OPENAI_API_KEY
```

---

## Configuration

Edit `.env` with your keys:

```env
# Required
OPENAI_API_KEY=sk-...

# Recommended (free registration)
OPENALEX_EMAIL=you@university.edu
CORE_API_KEY=...

# Optional (paid/institutional)
IEEE_API_KEY=...
ELSEVIER_API_KEY=...         # Covers Scopus + ScienceDirect
SERPAPI_KEY=...               # Google Scholar

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# LLM models
LLM_MODEL=gpt-4o-mini
LLM_MODEL_SUMMARIZATION=gpt-4o
```

> **Note:** The system works without paid API keys — free sources (ArXiv, Semantic Scholar, CrossRef, OpenAlex, CORE, PubMed, DBLP) provide substantial coverage. Sources without valid keys are gracefully skipped.

---

## Usage

### CLI

```bash
# Full analysis
python -m src.main "transformer architectures for NLP" --years 5 --num-ideas 5

# Demo mode
python -m src.main --demo

# Custom output path
python -m src.main "graph neural networks" --output gnn_results.json
```

### Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard has 8 pages:

| Page | Content |
|------|---------|
| **Home** | Search config, run pipeline, KPI overview |
| **Search Results** | All papers with filters, CSV + BibTeX export |
| **Best Papers** | Gold hero card for #1 base paper, runner-ups |
| **Top Authors** | Podium view, citations/papers charts, expertise badges |
| **Summaries** | Paper summaries and extracted limitations |
| **Problem Statements** | Gaps, problem statements, citation analysis |
| **Citation Graph** | Interactive pyvis network, publication trends |
| **Ideas** | AI-generated research ideas and full crew output |
| **Rankings** | Heatmap, radar charts, weighted score breakdown |

---

## Demo Mode

The system ships with pre-computed results for **"Federated Learning for Healthcare"** (47 papers, 11 sources). This lets you explore every dashboard page without API keys, Neo4j, or an OpenAI key.

**Dashboard:** Click *"🎮 Load Demo Data"* in the sidebar.

**CLI:**
```bash
python -m src.main --demo
```

---

## Docker Deployment

```bash
# Start Neo4j + app
docker compose up -d

# View logs
docker compose logs -f app

# Stop
docker compose down
```

This starts:
- **Neo4j 5** with Graph Data Science plugin on `localhost:7474`
- **Streamlit app** on `localhost:8501`

---

## Project Structure

```
research_paper_system/
├── dashboard/
│   ├── app.py                    # Main Streamlit shell
│   ├── components/theme.py       # Custom CSS + reusable UI components
│   └── pages/                    # 8 dashboard pages
├── src/
│   ├── config/
│   │   ├── settings.py           # Environment & source configuration
│   │   ├── agents.yaml           # 7 CrewAI agent definitions
│   │   └── tasks.yaml            # 7 task definitions with context chain
│   ├── crew.py                   # Pipeline orchestrator
│   ├── main.py                   # CLI entry point
│   ├── models/
│   │   ├── paper.py              # Paper, Author, Citation models
│   │   └── analysis.py           # Rankings, TopAuthor, Gaps, etc.
│   ├── services/
│   │   ├── graph_service.py      # Neo4j CRUD, PageRank, Topic nodes
│   │   ├── vector_store.py       # FAISS index build & search
│   │   ├── paper_ranker.py       # Multi-factor scoring
│   │   ├── embedding_service.py  # SPECTER2 / MiniLM embeddings
│   │   └── progress_tracker.py   # Live progress callbacks
│   ├── tools/
│   │   ├── arxiv_tool.py         # ArXiv API
│   │   ├── semantic_scholar_tool.py
│   │   ├── ieee_tool.py          # IEEE Xplore API
│   │   ├── scopus_tool.py        # Elsevier Scopus
│   │   ├── sciencedirect_tool.py # Elsevier ScienceDirect
│   │   ├── crossref_tool.py      # CrossRef REST API
│   │   ├── openalex_tool.py      # OpenAlex API
│   │   ├── core_tool.py          # CORE Aggregator
│   │   ├── pubmed_tool.py        # NCBI PubMed/Entrez
│   │   ├── dblp_tool.py          # DBLP Search
│   │   ├── google_scholar_tool.py
│   │   ├── pdf_tool.py           # PyMuPDF extraction
│   │   ├── faiss_tool.py         # Semantic search + find related
│   │   └── neo4j_tool.py         # Citation, author, topic tools
│   └── utils/
│       ├── cache.py              # Disk cache (24h TTL)
│       ├── rate_limiter.py       # Per-source rate limiting
│       ├── text_processing.py    # Text cleaning + keyword extraction
│       └── deduplicator.py       # Fuzzy dedup across sources
├── tests/
│   ├── test_integration.py       # End-to-end with free sources
│   └── ...                       # Unit tests
├── data/
│   └── demo/demo_results.json    # Pre-computed demo dataset
├── docker-compose.yml            # Neo4j + App
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

## Testing

```bash
# Unit tests
pytest tests/ -v

# Integration test (hits ArXiv + CrossRef — needs internet)
pytest tests/test_integration.py -v -s

# Quick smoke test
python -m src.main --demo
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Multi-Agent Framework** | CrewAI (7 agents, sequential process) |
| **LLMs** | GPT-4o-mini (agents) + GPT-4o (summarization) |
| **Vector Database** | FAISS (IndexFlatIP) with SPECTER2 embeddings |
| **Knowledge Graph** | Neo4j 5 with Graph Data Science (PageRank) |
| **Dashboard** | Streamlit + Plotly + pyvis |
| **PDF Processing** | PyMuPDF |
| **Data Validation** | Pydantic v2 |
| **Testing** | pytest |
| **Containerization** | Docker + Docker Compose |

---

## How It Works — CrewAI Agent Pipeline

```
User: "federated learning for healthcare"
         │
         ▼
┌─ Search Agent ──────────────┐  11 source tools
│  Discovers 150+ papers      │  (ArXiv, S2, IEEE, ...)
└───────────┬─────────────────┘
            ▼
┌─ Summarization Agent ──────┐  PDF extraction tool
│  Summarizes each paper      │  GPT-4o
└───────────┬─────────────────┘
            ▼
┌─ Limitation Agent ─────────┐  Categorized + severity rated
│  Extracts limitations       │
└───────────┬─────────────────┘
            ▼
┌─ Citation Agent ───────────┐  Neo4j tools (PageRank)
│  Base paper + top authors   │
└───────────┬─────────────────┘
            ▼
┌─ Gap Detector ─────────────┐  FAISS semantic search
│  Identifies research gaps   │
└───────────┬─────────────────┘
            ▼
┌─ Problem Statement Agent ──┐  Structured with objectives
│  Generates problem stmts    │
└───────────┬─────────────────┘
            ▼
┌─ Idea Generation Agent ────┐  Cross-domain insights
│  Proposes novel ideas       │  Feasibility scored
└─────────────────────────────┘
```

Each agent is an autonomous LLM-powered actor that calls its assigned tools. Tasks are chained via CrewAI's `context` parameter — each task receives the output of its dependencies.

---

<div align="center">

Built with ❤️ using [CrewAI](https://github.com/joaomdmoura/crewAI) · [Streamlit](https://streamlit.io) · [Neo4j](https://neo4j.com) · [FAISS](https://github.com/facebookresearch/faiss)

</div>
