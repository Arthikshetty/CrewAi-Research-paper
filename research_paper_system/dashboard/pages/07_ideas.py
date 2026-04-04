import streamlit as st

st.title("💡 Research Ideas")

if "results" not in st.session_state:
    st.info("Run an analysis first from the main page.")
    st.stop()

results = st.session_state["results"]
task_outputs = results.get("task_outputs", [])

# Find ideas task output
ideas_output = ""
for task in task_outputs:
    desc = task.get("task", "").lower()
    if "idea" in desc:
        ideas_output = task.get("output", "")

if ideas_output:
    st.markdown("### 💡 Generated Research Ideas")
    st.markdown(ideas_output)
else:
    st.warning("No research ideas generated yet.")

st.markdown("---")

# Full crew output
st.markdown("### 📋 Full Analysis Output")
crew_output = results.get("crew_output", "")
if crew_output:
    with st.expander("View complete CrewAI output"):
        st.markdown(crew_output)
