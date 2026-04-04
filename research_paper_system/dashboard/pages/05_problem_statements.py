import streamlit as st

st.title("📋 Problem Statements & Research Gaps")

if "results" not in st.session_state:
    st.info("Run an analysis first from the main page.")
    st.stop()

results = st.session_state["results"]
task_outputs = results.get("task_outputs", [])

# Find relevant outputs
gaps_output = ""
problems_output = ""
for task in task_outputs:
    desc = task.get("task", "").lower()
    if "gap" in desc:
        gaps_output = task.get("output", "")
    if "problem" in desc:
        problems_output = task.get("output", "")

st.markdown("### 🔍 Identified Research Gaps")
if gaps_output:
    st.markdown(gaps_output)
else:
    st.warning("No research gap data available yet.")

st.markdown("---")

st.markdown("### 📋 Generated Problem Statements")
if problems_output:
    st.markdown(problems_output)
else:
    st.warning("No problem statement data available yet.")
