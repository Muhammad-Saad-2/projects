"""
Streamlit RAG Chatbot using Pinecone + HuggingFace Embeddings + Google Gemini LLM
-----------------------------------------------------------------------------------
How to run:
  1) Save this file as `app.py`.
  2) Install deps (suggested):
     pip install -r requirements.txt
  3) Create a `.streamlit/secrets.toml` with:

     PINECONE_API_KEY = "your_pinecone_key"
     GOOGLE_API_KEY   = "your_google_api_key"

  4) Run: streamlit run app.py

Notes:
- You can upload a CSV (like your `products-100.csv`) or point to a local CSV path.
- The index uses sentence-transformers `all-MiniLM-L6-v2` (384 dims).
- If an index named `products-index` exists with wrong dim, it will be deleted and recreated.
- Chat supports citations (shows which rows were used) and simple history.
"""

import os
import time
from uuid import uuid4
from typing import List, Dict, Any

import pandas as pd
import streamlit as st

from pinecone import Pinecone, ServerlessSpec

from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# Google Gemini LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# ---------------------------------
# App Config & Helpers
# ---------------------------------
st.set_page_config(page_title="RAG Product Chatbot", page_icon="🧠", layout="wide")

st.title("🧠📦 RAG Product Chatbot (Pinecone + HF Embeddings + Google Gemini)")
st.caption("Upload your product CSV, index to Pinecone, and chat with your data.")

# Sidebar: Secrets & Settings
with st.sidebar:
    st.header("🔐 Keys & Settings")
    pinecone_api_key = st.secrets.get("PINECONE_API_KEY") or os.getenv("PINECONE_API_KEY")
    google_api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not pinecone_api_key:
        st.error("PINECONE_API_KEY missing. Add it in .streamlit/secrets.toml or env var.")
    if not google_api_key:
        st.error("GOOGLE_API_KEY missing. Add it in .streamlit/secrets.toml or env var.")

    index_name = st.text_input("Pinecone Index Name", value="products-index")
    pinecone_region = st.selectbox("Pinecone Region", ["us-east-1", "us-west-2", "eu-central-1"], index=0)
    create_if_missing = st.checkbox("Create index if missing", value=True)

    st.divider()
    st.subheader("Embedding Model")
    model_name = st.text_input("SentenceTransformer model", value="all-MiniLM-L6-v2")
    st.caption("Dim must match index dimension (384 for all-MiniLM-L6-v2)")

    st.subheader("LLM Provider")
    google_model = st.text_input("Gemini Model", value="gemini-2.5-flash")
    temperature = st.slider("LLM Temperature", 0.0, 1.5, 0.2, 0.1)

# Session state for chat
if "history" not in st.session_state:
    st.session_state.history = []

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "pc_index" not in st.session_state:
    st.session_state.pc_index = None

# ---------------------------------
# Initialize Pinecone & Embeddings
# ---------------------------------
@st.cache_resource(show_spinner=False)
def load_embeddings(name: str):
    _ = SentenceTransformer(name)
    return HuggingFaceEmbeddings(model_name=name)

@st.cache_resource(show_spinner=False)
def init_pinecone_client(api_key: str):
    return Pinecone(api_key=api_key)

@st.cache_resource(show_spinner=False)
def ensure_index(pc: Pinecone, name: str, region: str, dim: int = 384) -> Any:
    existing = pc.list_indexes().names()
    if name in existing:
        desc = pc.describe_index(name)
        if getattr(desc, "dimension", None) != dim:
            pc.delete_index(name)
            pc.create_index(name=name, dimension=dim, metric="cosine", spec=ServerlessSpec(cloud="aws", region=region))
    else:
        pc.create_index(name=name, dimension=dim, metric="cosine", spec=ServerlessSpec(cloud="aws", region=region))
    return pc.Index(name)

# ---------------------------------
# LLM setup
# ---------------------------------
@st.cache_resource(show_spinner=False)
def get_llm(google_key: str | None, google_model: str, temperature: float):
    if google_key:
        os.environ["GOOGLE_API_KEY"] = google_key
        return ChatGoogleGenerativeAI(model=google_model, temperature=temperature)
    st.warning("No Google Gemini key provided. Answers will be retrieval-only summaries.")
    return None

# ---------------------------------
# Ingestion utils
# ---------------------------------
def rows_to_text(row: pd.Series) -> str:
    parts = [
        str(row.get("Name", "")),
        str(row.get("Description", "")),
        str(row.get("Brand", "")),
        str(row.get("Category", "")),
        f"Price: {row.get('Price', '')}",
        f"Color: {row.get('Color', '')}",
        f"Size: {row.get('Size', '')}",
        f"Availability: {row.get('Availability', '')}",
    ]
    return " | ".join([p for p in parts if p and p != "nan"]) 


def upsert_dataframe(df: pd.DataFrame, index, embeddings: HuggingFaceEmbeddings, text_key: str = "content", batch_size: int = 128):
    df = df.copy()
    df[text_key] = df.apply(rows_to_text, axis=1)

    texts: List[str] = df[text_key].tolist()
    all_vecs: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        all_vecs.extend(embeddings.embed_documents(texts[i:i+batch_size]))

    items = []
    for i, row in enumerate(df.to_dict(orient="records")):
        metadata = {
            k: (float(v) if k == "Price" and v != "" else v)
            for k, v in row.items()
            if k != text_key
        }
        metadata[text_key] = row[text_key]
        items.append({
            "id": str(uuid4()),
            "values": all_vecs[i],
            "metadata": metadata,
        })

    for i in range(0, len(items), 100):
        index.upsert(items[i:i+100])
    time.sleep(2)

# ---------------------------------
# UI: Ingestion
# ---------------------------------
st.subheader("1) 📥 Ingest your CSV into Pinecone")
left, right = st.columns([2,1])

with left:
    uploaded = st.file_uploader("Upload CSV (e.g., products-100.csv)", type=["csv"]) 
    csv_path = st.text_input("...or path to CSV on server", value="")

with right:
    start_ingest = st.button("Index / Re-index CSV", type="primary", use_container_width=True)

if pinecone_api_key:
    pc = init_pinecone_client(pinecone_api_key)
else:
    pc = None

emb = load_embeddings(model_name)

if start_ingest:
    if not pc:
        st.error("Cannot index without Pinecone API key.")
    else:
        with st.spinner("Preparing Pinecone index..."):
            if create_if_missing:
                pc_index = ensure_index(pc, index_name, pinecone_region, dim=384)
            else:
                pc_index = pc.Index(index_name)
            st.session_state.pc_index = pc_index

        try:
            if uploaded is not None:
                df = pd.read_csv(uploaded)
            elif csv_path:
                df = pd.read_csv(csv_path)
            else:
                st.error("Please upload a CSV or provide a path.")
                df = None
        except Exception as e:
            st.exception(e)
            df = None

        if df is not None and not df.empty:
            with st.spinner("Embedding & upserting vectors to Pinecone..."):
                upsert_dataframe(df, pc_index, emb)
            st.success("Indexing complete!")

            st.session_state.vector_store = PineconeVectorStore(index=pc_index, embedding=emb, text_key="content")
            try:
                stats = pc_index.describe_index_stats()
                total = stats.get("total_vector_count", "?")
            except Exception:
                total = "?"
            st.info(f"Total vectors in Pinecone: {total}")
        else:
            st.error("No data to index.")

if pc and st.session_state.pc_index is None:
    try:
        st.session_state.pc_index = pc.Index(index_name)
        st.session_state.vector_store = PineconeVectorStore(index=st.session_state.pc_index, embedding=emb, text_key="content")
    except Exception:
        pass

# ---------------------------------
# UI: Chat
# ---------------------------------
st.subheader("2) 💬 Chat with your catalog")
retriever = None
if st.session_state.vector_store is not None:
    retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 4})
else:
    st.info("Index your CSV first to enable retrieval.")

llm = get_llm(google_api_key, google_model, temperature)

system_prompt = (
    "You are a helpful product expert. Answer the user's question using ONLY the provided context snippets. "
    "If the answer is not in the context, say you don't have that information. Be concise, factual, and include "
    "specific product names/brands when relevant."
)

with st.container(border=True):
    for turn in st.session_state.history:
        if turn["role"] == "user":
            st.markdown(f"**You:** {turn['content']}")
        else:
            st.markdown(f"**Assistant:** {turn['content']}")

    user_query = st.text_input("Ask about products (pricing, availability, features, etc.)", value="")
    cols = st.columns([1,1,1])
    with cols[0]:
        ask = st.button("Ask", type="primary")
    with cols[1]:
        clear = st.button("Reset chat")
    with cols[2]:
        show_ctx = st.toggle("Show citations", value=True)

    if clear:
        st.session_state.history = []
        st.rerun()

    if ask and user_query.strip():
        st.session_state.history.append({"role": "user", "content": user_query})

        docs = []
        if retriever is not None:
            try:
                docs = retriever.get_relevant_documents(user_query)
            except Exception as e:
                st.warning(f"Retrieval failed: {e}")

        context_blocks = []
        for d in docs:
            meta = d.metadata or {}
            name = meta.get("Name") or "Unknown"
            brand = meta.get("Brand") or ""
            price = meta.get("Price") or ""
            snippet = d.page_content[:300]
            context_blocks.append(f"- {name} {brand} {price}\n  {snippet}")

        context_text = "\n".join(context_blocks) if context_blocks else ""

        if llm is None:
            if context_text:
                answer = "I don't have a generative model configured. Here are the most relevant entries I found:\n\n" + context_text
            else:
                answer = "I couldn't find relevant entries and no LLM is configured."
            st.session_state.history.append({"role": "assistant", "content": answer})
            st.rerun()

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Context:\n{context_text}\n\nQuestion: {user_query}")
        ]

        with st.spinner("Thinking..."):
            try:
                llm_resp = llm.invoke(messages)
                answer = llm_resp.content
            except Exception as e:
                answer = f"LLM error: {e}"

        st.session_state.history.append({"role": "assistant", "content": answer})
        st.rerun()

if st.session_state.history and retriever is not None and show_ctx:
    with st.expander("🔎 Sources / Citations (Top matches)", expanded=False):
        try:
            docs = retriever.get_relevant_documents(st.session_state.history[-2]["content"]) if len(st.session_state.history) >= 2 else []
            for i, d in enumerate(docs, start=1):
                meta = d.metadata or {}
                name = meta.get("Name", "?")
                brand = meta.get("Brand", "?")
                price = meta.get("Price", "?")
                cat = meta.get("Category", "?")
                st.markdown(f"**{i}. {name}**  ")
                st.markdown(f"Brand: {brand} | Category: {cat} | Price: {price}")
                st.code(d.page_content[:600])
        except Exception as e:
            st.write(f"(Could not fetch citations: {e})")

st.divider()
st.caption("Built with ❤️ using Streamlit, Pinecone, LangChain, sentence-transformers, and Google Gemini.")