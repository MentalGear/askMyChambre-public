# app.py (Refactored for immediate UI update)

import streamlit as st
import pandas as pd
from PIL import Image

# Import service functions that now handle DB interactions internally
from services import clarify, process_user_query

# ---------- Page layout & Logo Setup ----------
try:
    logo_image = Image.open("logo1.png")
except FileNotFoundError:
    st.error("Logo file 'GovTech_logo.png' not found. Please check the path.")
    logo_image = None

st.set_page_config(
    page_title="Chat with political data",
    page_icon=logo_image if logo_image else "📄",
    layout="centered",
    initial_sidebar_state="auto",
)

if logo_image:
    st.image(logo_image, width=200)

st.title("AskMyChambre")
st.caption("SEMANTIC SEARCH FOR PARLIAMENTARY DATA IN LUXEMBOURG")
st.markdown("---")

# ---------- Session state initialization ----------
# We add new stages: 'clarifying' and 'processing'
if "stage" not in st.session_state:
    st.session_state.stage = "query1"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "initial_query" not in st.session_state:
    st.session_state.initial_query = ""
if "clarification_prompt" not in st.session_state:
    st.session_state.clarification_prompt = ""
# Add a state to hold the user's response to the clarification
if "clarification_response" not in st.session_state:
    st.session_state.clarification_response = ""


# ---------- Render chat history (runs on every script execution) ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "table" in msg and msg.get("table") is not None and not msg["table"].empty:
            st.dataframe(msg["table"])

# ---------- Main Interaction Logic (The "State Machine") ----------

# --- Part 1: Handle long-running processes based on the current stage ---
# This logic runs *outside* the input handling, triggered by a rerun.

# Stage to process the first user query and generate a clarification
if st.session_state.stage == "clarifying":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                clarification_text: str = clarify(st.session_state.initial_query)
                st.session_state.clarification_prompt = clarification_text
                st.session_state.messages.append({"role": "assistant", "content": clarification_text})
                st.session_state.stage = "query2" # Move to the next stage
                st.rerun()
            except Exception as e:
                error_message = f"An error occurred during clarification: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error. {error_message}"})
                st.session_state.stage = "query1" # Reset to try again


# Stage to process the user's clarification and get the final answer
if st.session_state.stage == "processing":
    with st.chat_message("assistant"):
        with st.spinner("Processing your request... ⚙️"):
            try:
                response_text, response_df = process_user_query(
                    st.session_state.initial_query,
                    st.session_state.clarification_prompt,
                    st.session_state.clarification_response, # Use the saved response
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "table": response_df,
                })
                st.session_state.stage = "done" # Final stage
                st.rerun()
            except Exception as e:
                error_message = f"An error occurred while processing your query: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error. {error_message}"})
                st.session_state.stage = "query2" # Go back to allow re-trying the clarification


# --- Part 2: Handle the user's direct input ---
# This block's only job is to capture input, update the state, and trigger a rerun.

user_prompt_text = "What can I help you with?"
if st.session_state.stage == "query2":
    user_prompt_text = "Please provide more details or refine your query."
elif st.session_state.stage == "done":
    user_prompt_text = "Type here to start a new search, or use the button below."

# Disable input while processing
is_processing = st.session_state.stage in ["clarifying", "processing"]

if user_input := st.chat_input(user_prompt_text, disabled=(is_processing or st.session_state.stage == "done")):

    if st.session_state.stage == "query1":
        # 1. Immediately add user message to state
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.initial_query = user_input
        # 2. Set the next stage for processing
        st.session_state.stage = "clarifying"
        # 3. Rerun to show the user's message and trigger the 'clarifying' block
        st.rerun()

    elif st.session_state.stage == "query2":
        # 1. Immediately add user's clarification to state
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.clarification_response = user_input # Save clarification
        # 2. Set the next stage for processing
        st.session_state.stage = "processing"
        # 3. Rerun to show the message and trigger the 'processing' block
        st.rerun()

# ---------- Reset / New Search Button ----------
if st.session_state.stage == "done":
    st.markdown("---")
    if st.button("🔄 Start a New Search", type="primary", use_container_width=True):
        # A more robust way to clear state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()