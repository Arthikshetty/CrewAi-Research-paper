import streamlit as st

st.title("📝 Paper Summaries")

if "results" not in st.session_state:
    st.info("Run an analysis first from the main page.")
    st.stop()

results = st.session_state["results"]
task_outputs = results.get("task_outputs", [])

# Find summarize task output
summary_output = ""
limitation_output = ""
for task in task_outputs:
    desc = task.get("task", "").lower()
    if "summarize" in desc or "summary" in desc:
        summary_output = task.get("output", "")
    if "limitation" in desc:
        limitation_output = task.get("output", "")

if summary_output:
    st.markdown("### Paper Summaries")
    st.markdown(summary_output)
else:
    st.warning("No summary data available yet.")

st.markdown("---")

if limitation_output:
    st.markdown("### Extracted Limitations")
    st.markdown(limitation_output)
