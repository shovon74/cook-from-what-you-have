"""Streamlit front end: Dispatches cooking jobs to Redis and displays results."""

import json
import os
import time
import uuid
import redis
import streamlit as st

import db

st.set_page_config(page_title="Personal Chef", page_icon="🍳")

# Ensure PostgreSQL tables exist
db.init_db()

# Connect to Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL)


def new_chat():
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())


if "messages" not in st.session_state:
    new_chat()

# Sidebar: User Profile & Saved History
with st.sidebar:
    st.header("🍳 Personal Chef")

    # 1. User identification
    user_name = st.text_input("Your Name", value="Shovon")
    user_email = st.text_input("Your Email", value="shovon@example.com")

    # Automatically fetch or register user in Postgres
    user_id = db.get_or_create_user(user_name, user_email)

    st.divider()
    st.button("New chat", on_click=new_chat, use_container_width=True)

    # 2. Display previous recipes from Postgres
    st.subheader("📜 Saved Recipes")
    saved = db.get_user_recipes(user_id)
    if not saved:
        st.caption("No recipes saved yet.")
    for p, r_text, dt in saved:
        with st.expander(f"🍽️ {p[:20]}..."):
            st.caption(f"Saved on {dt.strftime('%b %d, %H:%M')}")
            st.write(r_text)

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

    # 3. Create a unique job and dispatch it to Redis
    job_id = str(uuid.uuid4())
    payload = {
        "job_id": job_id,
        "user_id": user_id,
        "thread_id": st.session_state.thread_id,
        "prompt": prompt,
    }

    # LPUSH: Put ticket on the Redis queue
    r.lpush("cooking_tasks", json.dumps(payload))

    # 4. Wait for the background worker to finish the recipe
    with st.chat_message("assistant"):
        with st.spinner("Ticket sent to kitchen! Chef is cooking..."):
            reply = None
            # Poll Redis every 1 second (up to 45 seconds)
            for _ in range(45):
                time.sleep(1)
                status_raw = r.get(f"job:{job_id}")
                if status_raw:
                    job_info = json.loads(status_raw.decode("utf-8"))
                    status = job_info.get("status")
                    if status == "completed":
                        reply = job_info.get("response")
                        break
                    elif status == "failed":
                        reply = f"Sorry, something went wrong: {job_info.get('error')}"
                        break

            if not reply:
                reply = "Cooking timed out. Please try again."

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
