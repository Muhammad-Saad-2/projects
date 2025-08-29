# app.py
import os
import time
from uuid import uuid4
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
st.set_page_config(page_title="CSV → RAG Chat (FAISS, rebuild on upload)", layout="wide", page_icon="🤖")
st.title("CSV Chatbot — fresh FAISS per upload")
# st.caption("Upload a CSV and chat only with that CSV. Old FAISS won't leak answers.")

with st.sidebar:
    st.header("Settings")
    hf_model = "all-MiniLM-L6-v2"
    chunk_size = st.number_input("Chunk size", min_value=256, max_value=4000, value=1000, step=100)
    chunk_overlap = st.number_input("Chunk overlap", min_value=0, max_value=1000, value=200, step=50)
    k = st.number_input("Retriever k (top matches)", min_value=1, max_value=10, value=4, step=1)
    persist_index = st.checkbox("Persist FAISS index to disk (db/faiss_index)", value=False)
    persist_path = "db/faiss_index"

    st.divider()
    st.subheader("Google Gemini LLM")
    google_model = "gemini-2.5-flash"
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    # google_api_key = st.text_input("GOOGLE_API_KEY (or set as env var)", value=os.getenv("GOOGLE_API_KEY") or "")

# ensure db dir exists if persisting
if persist_index:
    os.makedirs(os.path.dirname(persist_path), exist_ok=True)

# ---------------------------
# Session state
# ---------------------------
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------
# Helpers
# ---------------------------
@st.cache_resource(show_spinner=False)
def load_embeddings(model_name: str):
    # Use local sentence-transformers embedding model (no external API)
    return HuggingFaceEmbeddings(model_name=model_name)

def df_to_documents(df: pd.DataFrame) -> List[Document]:
    # Convert each row to a single text document; adjust as needed for your CSV schema
    texts = []
    for _, row in df.iterrows():
        # join column_name: value pairs
        parts = [f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])]
        txt = " | ".join(parts)
        texts.append(Document(page_content=txt, metadata={"source_row": _.__str__()}))
    return texts

def build_faiss_from_df(df: pd.DataFrame, embeddings, chunk_size: int, chunk_overlap: int) -> FAISS:
    docs = df_to_documents(df)

    # split into chunks (so long description rows get chunked)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splitted_texts = []
    for d in docs:
        splitted_texts.extend([Document(page_content=t, metadata=d.metadata) for t in splitter.split_text(d.page_content)])

    vs = FAISS.from_documents(splitted_texts, embeddings)
    return vs

def safe_persist(vectorstore: FAISS, path: str):
    # FAISS.save_local will overwrite the directory contents if called
    vectorstore.save_local(path)

def safe_load(path: str, embeddings) -> FAISS | None:
    if os.path.exists(path) and os.path.isdir(path):
        try:
            return FAISS.load_local(path, embeddings)
        except Exception as e:
            st.warning(f"Could not load saved FAISS index: {e}")
            return None
    return None

# ---------------------------
# Ingestion area
# ---------------------------
st.subheader("1) Upload CSV (every upload creates a fresh FAISS index)")
left, right = st.columns([2,1])

with left:
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    csv_path = st.text_input("...or path to CSV on the server (optional)", value="")

with right:
    reindex_btn = st.button("Index / Re-index", type="primary", use_container_width=True)
    load_saved_btn = st.button("Load saved FAISS (if exists)", use_container_width=True)

embeddings = load_embeddings(hf_model)

# When user chooses to index (or uploads and clicks reindex), rebuild fresh
def ingest_and_build(file_like):
    try:
        df = pd.read_csv(file_like)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return None

    if df.empty:
        st.error("CSV is empty.")
        return None

    with st.spinner("Building embeddings and FAISS index..."):
        vs = build_faiss_from_df(df, embeddings, chunk_size, chunk_overlap)

        # persist if requested
        if persist_index:
            try:
                safe_persist(vs, persist_path)
                st.info(f"Persisted FAISS to {persist_path}")
            except Exception as e:
                st.warning(f"Failed to persist index: {e}")

    return vs

# Decide action: index from upload, index from path, or load existing
if reindex_btn:
    # prefer file-like upload if present
    if uploaded is not None:
        st.session_state.vectorstore = ingest_and_build(uploaded)
        st.session_state.last_uploaded_name = getattr(uploaded, "name", str(time.time()))
        st.session_state.history = []
        st.success("Indexed uploaded CSV; chat context reset.")
    elif csv_path:
        if os.path.exists(csv_path):
            st.session_state.vectorstore = ingest_and_build(csv_path)
            st.session_state.last_uploaded_name = csv_path
            st.session_state.history = []
            st.success("Indexed CSV from path; chat context reset.")
        else:
            st.error("Provided csv_path does not exist.")
    else:
        st.error("No CSV provided. Upload a file or provide a local path.")

# Allow explicit loading of previously saved FAISS (only used when user wants it)
if load_saved_btn:
    loaded = safe_load(persist_path, embeddings)
    if loaded:
        st.session_state.vectorstore = loaded
        st.session_state.last_uploaded_name = f"loaded:{persist_path}"
        st.session_state.history = []
        st.success("Loaded persisted FAISS index and reset chat.")
    else:
        st.warning("No persisted FAISS index found or failed to load.")

# If user uploaded a file but didn't press reindex yet, show preview and offer to index
if uploaded is not None and not reindex_btn:
    st.info(f"Detected uploaded file: {getattr(uploaded, 'name', 'uploaded.csv')}. Press **Index / Re-index** to build a fresh index from it.")
    st.dataframe(pd.read_csv(uploaded).head(5))

# Also allow loading persisted index automatically only if no upload and no reindex clicked
if (uploaded is None and not reindex_btn and st.session_state.vectorstore is None and persist_index):
    # Try to auto-load only if user asked to persist and no upload occurred and there is no vectorstore in session
    maybe = safe_load(persist_path, embeddings)
    if maybe:
        st.session_state.vectorstore = maybe
        st.session_state.last_uploaded_name = f"auto_loaded:{persist_path}"
        st.info("Auto-loaded persisted FAISS index (no new CSV uploaded).")

# ---------------------------
# Chat UI
# ---------------------------
st.subheader("2) Chat with the current CSV (fresh index only)")
if st.session_state.vectorstore is None:
    st.info("No FAISS vectorstore in memory. Upload a CSV and press 'Index / Re-index' or load a saved index.")
else:
    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": k})

    # Prepare LLM
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
    llm = None
    try:
        llm = ChatGoogleGenerativeAI(model=google_model, temperature=temperature)
    except Exception as e:
        st.warning(f"Could not initialize Gemini LLM (answers will be retrieval-only): {e}")
        llm = None

    user_input = st.text_input("Ask a question about your uploaded CSV", value="")
    ask_btn = st.button("Ask")

    if ask_btn and user_input.strip():
        # append user turn
        st.session_state.history.append({"role": "user", "content": user_input})

        # retrieval
        docs = []
        try:
            docs = retriever.get_relevant_documents(user_input)
        except Exception as e:
            st.warning(f"Retrieval error: {e}")

        # build context string from retrieved docs
        context_blocks = []
        for d in docs:
            meta = d.metadata or {}
            snippet = d.page_content[:800]
            context_blocks.append(f"- {meta.get('source_row','?')}: {snippet}")

        context_text = "\n".join(context_blocks)

        if llm is None:
            # simple retrieval-only answer
            if context_text:
                answer = "No generative model configured or LLM failed to init. Top matches:\n\n" + context_text
            else:
                answer = "No relevant context found and no LLM configured."
        else:
            system_prompt = (
                "You are a factual product/CSV assistant. Answer ONLY from the provided CSV context snippets. "
                "If the answer is not present, say you don't have that information."
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

        st.session_state.history.append({"role": "assistant", "content": answer})

    # display chat
    for turn in st.session_state.history:
        role = turn["role"]
        content = turn["content"]
        if role == "user":
            st.markdown(f"**You:** {content}")
        else:
            st.markdown(f"**Assistant:** {content}")

    # Show citations / sources
    with st.expander("🔎 Last retrieved context (top matches)"):
        try:
            # try to show context for last user question
            if st.session_state.history:
                last_user = next((t for t in reversed(st.session_state.history) if t["role"]=="user"), None)
                if last_user:
                    docs = retriever.get_relevant_documents(last_user["content"])
                    for i, d in enumerate(docs, start=1):
                        meta = d.metadata or {}
                        st.markdown(f"**{i}. Row:** {meta.get('source_row', '?')}")
                        st.code(d.page_content[:800])
                else:
                    st.write("No queries yet.")
            else:
                st.write("No conversation yet.")
        except Exception as e:
            st.write(f"(Could not fetch citations: {e})")

# Footer
st.divider()
st.caption("Built with Streamlit — this app rebuilds FAISS when you upload a CSV so answers always come from the latest file.")
