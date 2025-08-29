# app.py
import os
from typing import List
import pandas as pd
import streamlit as st

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


google_api_key = st.secrets.get("GOOGLE_API_KEY")

# ---------------------------
# Config / UI
# ---------------------------
st.set_page_config(page_title="CSV Chatbot (multi-chat)", layout="wide", page_icon="🤖")
st.title("📊 CSV Chatbot — Multiple Chats (FAISS per upload)")

with st.sidebar:
    st.header("Settings")
    hf_model = "all-MiniLM-L6-v2"
    chunk_size = st.number_input("Chunk size", min_value=256, max_value=4000, value=1000, step=100)
    chunk_overlap = st.number_input("Chunk overlap", min_value=0, max_value=1000, value=200, step=50)
    k = st.number_input("Retriever k (top matches)", min_value=1, max_value=10, value=4, step=1)

    st.divider()
    st.subheader("Google Gemini LLM")
    google_model = "gemini-2.5-flash"
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)

# ---------------------------
# Session state
# ---------------------------
if "chats" not in st.session_state:
    # chats = {chat_id: {"name": str, "vectorstore": FAISS, "history": []}}
    st.session_state.chats = {}

if "active_chat" not in st.session_state:
    st.session_state.active_chat = None

embeddings = HuggingFaceEmbeddings(model_name=hf_model)

# ---------------------------
# Helpers
# ---------------------------
def df_to_documents(df: pd.DataFrame) -> List[Document]:
    texts = []
    for idx, row in df.iterrows():
        parts = [f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])]
        txt = " | ".join(parts)
        texts.append(Document(page_content=txt, metadata={"row": str(idx)}))
    return texts

def build_faiss_from_df(df: pd.DataFrame) -> FAISS:
    docs = df_to_documents(df)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splitted = []
    for d in docs:
        splitted.extend([Document(page_content=t, metadata=d.metadata) for t in splitter.split_text(d.page_content)])
    return FAISS.from_documents(splitted, embeddings)

# ---------------------------
# Upload + New Chat
# ---------------------------
st.subheader("1) Upload CSV to start a new chat")
uploaded = st.file_uploader("Upload CSV", type=["csv"], key="file_uploader")

if uploaded:
    try:
        df = pd.read_csv(uploaded)
        if not df.empty:
            vs = build_faiss_from_df(df)
            chat_id = str(len(st.session_state.chats) + 1)
            chat_name = getattr(uploaded, "name", f"Chat {chat_id}")
            st.session_state.chats[chat_id] = {
                "name": chat_name,
                "vectorstore": vs,
                "history": []
            }
            st.session_state.active_chat = chat_id
            st.success(f"✅ Created new chat with `{chat_name}`")
        else:
            st.error("Uploaded CSV is empty.")
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")

# ---------------------------
# Switch between chats
# ---------------------------
if st.session_state.chats:
    chat_options = {cid: chat["name"] for cid, chat in st.session_state.chats.items()}
    chosen = st.selectbox("Active Chat", options=list(chat_options.keys()), format_func=lambda cid: chat_options[cid])
    st.session_state.active_chat = chosen

    # enforce max 5 chats
    if len(st.session_state.chats) > 5:
        oldest = list(st.session_state.chats.keys())[0]
        del st.session_state.chats[oldest]
        st.info("♻️ Oldest chat removed (limit: 5).")

# ---------------------------
# Chat Area
# ---------------------------
st.subheader("2) Chat with your CSV")

if not st.session_state.active_chat:
    st.info("Upload a CSV to start chatting.")
else:
    chat = st.session_state.chats[st.session_state.active_chat]
    retriever = chat["vectorstore"].as_retriever(search_kwargs={"k": k})

    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
    try:
        llm = ChatGoogleGenerativeAI(model=google_model, temperature=temperature)
    except Exception as e:
        st.warning(f"Could not initialize Gemini LLM: {e}")
        llm = None

    # Conversation UI
    for turn in chat["history"]:
        if turn["role"] == "user":
            st.markdown(f"**You:** {turn['content']}")
        else:
            st.markdown(f"**Assistant:** {turn['content']}")

    # modern chat input
    user_input = st.chat_input("Ask something about this CSV...")
    if user_input:
        chat["history"].append({"role": "user", "content": user_input})

        docs = []
        try:
            docs = retriever.get_relevant_documents(user_input)
        except Exception as e:
            st.warning(f"Retrieval error: {e}")

        context_blocks = []
        for d in docs:
            context_blocks.append(f"- Row {d.metadata.get('row','?')}: {d.page_content[:200]}")
        context_text = "\n".join(context_blocks)

        if llm is None:
            if context_text:
                answer = "Top matches:\n" + context_text
            else:
                answer = "No relevant info found."
        else:
            system_prompt = (
                "You are a CSV assistant. Answer ONLY using the provided CSV context. "
                "If the answer is not present, say you don't know."
            )
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Context:\n{context_text}\n\nQuestion: {user_input}")
            ]
            try:
                resp = llm.invoke(messages)
                answer = resp.content
            except Exception as e:
                answer = f"LLM error: {e}\n\nTop matches:\n{context_text}"

        chat["history"].append({"role": "assistant", "content": answer})
        st.rerun()  # refresh UI to show new message

# Footer
st.divider()
st.caption("Built with Streamlit — Supports up to 5 parallel chats (one per CSV).")
