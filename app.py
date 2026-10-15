"""Streamlit front end for Personal Chef. Run with: uv run streamlit run app.py"""

import uuid

import streamlit as st

from agent import ask, build_agent

st.set_page_config(page_title="Personal Chef", page_icon="🍳")


@st.cache_resource
def get_agent():
    # Built once and shared across reruns, so the in-memory chat history survives.
    return build_agent()


def new_chat():
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())


if "messages" not in st.session_state:
    new_chat()

agent = get_agent()

with st.sidebar:
    st.header("🍳 Personal Chef")
    st.write("Tell me what's in your kitchen and I'll suggest a recipe.")
    st.button("New chat", on_click=new_chat, use_container_width=True)

st.title("Personal Chef")

if not st.session_state.messages:
    st.info("Try: *I have eggs, spinach, feta and half an onion.*")

# Replay history (Streamlit reruns the whole script on every interaction).
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("What ingredients do you have?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Cooking something up..."):
            try:
                reply = ask(agent, prompt, st.session_state.thread_id)
            except Exception as e:
                reply = f"Sorry, something went wrong: {e}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})