
import streamlit as st
import requests
import json
from pathlib import Path

# --- PATH SETTINGS ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "assets" / "style.css"

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- CSS STYLING ---
with open(css_file) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.header("About")
st.sidebar.markdown(
    "This AI Research Assistant is designed to help you with your research by "
    "fetching and summarizing academic papers from Arxiv."
)
st.sidebar.header("How to use")
st.sidebar.markdown(
    "Simply ask a question about a research topic, and the assistant will "
    "find relevant papers and provide a summary."
)

# --- HEADER ---
st.title("🤖 AI Research Assistant")
st.markdown("Welcome! I can help you with your research by fetching and summarizing academic papers. What topic are you interested in today?")

# --- CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- USER INPUT ---
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        # This is where the backend call will be made
        try:
            payload = {"query": prompt, "top_k": 3, "summarize": True}
            response = requests.post("http://localhost:8000/api/query", json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            response_data = response.json()
            
            summary = response_data.get("summary", "Sorry, I couldn't generate a summary.")
            sources = response_data.get("sources", [])
            
            full_response = summary
            if sources:
                full_response += "\n\n**Sources:**\n"
                for source in sources:
                    full_response += f"- {source}\n"
            
            message_placeholder.markdown(full_response)

        except requests.exceptions.RequestException as e:
            full_response = f"An error occurred: {e}"
            message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
