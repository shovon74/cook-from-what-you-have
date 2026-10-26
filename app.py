"""Streamlit front end for Personal Chef with PostgreSQL persistence."""

import uuid
import streamlit as st

import db
from agent import ask, build_agent

st.set_page_config(page_title="Personal Chef", page_icon="🍳")

# Ensure PostgreSQL tables exist
db.init_db()


@st.cache_resource
def get_agent():
    return build_agent()


def new_chat():
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())


if "messages" not in st.session_state:
    new_chat()

agent = get_agent()

# Sidebar: User Profile & Saved History
with st.sidebar:
    st.header("🍳 Personal Chef")
    
    # 1. User identification
    user_name = st.text_input("Your Name", value="Shovon")
    user_email = st.text_input("Your Email", value="shovon@example.com")
    
    # Automatically fetch or register user
    user_id = db.get_or_create_user(user_name, user_email)
    
    st.divider()
    st.button("New chat", on_click=new_chat, use_container_width=True)
    
    # 2. Display previous recipes from Postgres
    st.subheader("📜 Saved Recipes")
    saved = db.get_user_recipes(user_id)
    if not saved:
        st.caption("No recipes saved yet.")
    for p, r, dt in saved:
        with st.expander(f"🍽️ {p[:20]}..."):
            st.caption(f"Saved on {dt.strftime('%b %d, %H:%M')}")
            st.write(r)

st.title("Personal Chef")

if not st.session_state.messages:
    st.info("Try: *I have eggs, spinach, feta and half an onion.*")

# Replay current session messages
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
                # 3. Save conversation & recipe to PostgreSQL
                db.save_recipe(user_id, st.session_state.thread_id, prompt, reply)
            except Exception as e:
                reply = f"Sorry, something went wrong: {e}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()  # Refresh sidebar to immediately show the newly saved recipe!
