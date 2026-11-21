import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).parent / "src"))
from answer import answer  # noqa: E402

st.set_page_config(page_title="IT Support Assistant", page_icon="🛠️")
st.title("🛠️ IT Support Assistant")
st.caption("Answers come only from the internal runbooks and always show their sources.")

question = st.text_input("Ask an IT support question:")

if question:
    with st.spinner("Searching the knowledge base..."):
        text, sources = answer(question)
    st.markdown(text)
    if sources:
        st.markdown("**Sources:** " + ", ".join(f"`{s}`" for s in sources))