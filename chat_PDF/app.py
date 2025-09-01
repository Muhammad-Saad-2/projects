import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pinecone import Pinecone, ServerlessSpec
import uuid
import time

# Load secrets
load_dotenv()
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY", os.getenv("PINECONE_API_KEY"))
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))  # Hugging Face token

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HF_TOKEN

# Pinecone setup (shared index with namespaces)
pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "rag-chatbot"
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,  # Matches all-MiniLM-L6-v2
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    time.sleep(5)  # Wait for index creation
index = pc.Index(INDEX_NAME)

# ---- Initialize session state ----
if "chats" not in st.session_state:
    st.session_state.chats = {}  # {chat_id: {"name": str, "messages": [], "qa": chain, "pdf_uploaded": bool, "namespace": str, "pinned": bool, "created_at": float}}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None

# ---- Helper to create a new chat ----
def create_new_chat():
    chat_id = f"chat_{uuid.uuid4().hex[:8]}"
    namespace = chat_id
    st.session_state.chats[chat_id] = {
        "name": "New Chat",
        "messages": [],
        "qa": None,
        "pdf_uploaded": False,
        "namespace": namespace,
        "pinned": False,
        "created_at": time.time()
    }
    st.session_state.active_chat = chat_id

# ---- Helper to delete a chat ----
def delete_chat(chat_id):
    namespace = st.session_state.chats[chat_id]["namespace"]
    index.delete(delete_all=True, namespace=namespace)
    del st.session_state.chats[chat_id]
    if st.session_state.active_chat == chat_id:
        st.session_state.active_chat = None

# ---- Helper to pin/unpin a chat ----
def toggle_pin(chat_id):
    st.session_state.chats[chat_id]["pinned"] = not st.session_state.chats[chat_id]["pinned"]

# ---- Helper to select a chat ----
def select_chat(chat_id):
    st.session_state.active_chat = chat_id

# ---- Sidebar: Enhanced Chat management ----
with st.sidebar:
    st.button("➕ New Chat", on_click=create_new_chat, use_container_width=True, key="new_chat_top")

    st.markdown("### Your Chats", unsafe_allow_html=True)
    st.markdown("<style> .chat-item:hover { background-color: #e0e0e0; } </style>", unsafe_allow_html=True)

    sorted_chats = sorted(st.session_state.chats.items(), key=lambda x: (-x[1]["pinned"], -x[1]["created_at"]))
    
    for chat_id, chat in sorted_chats:
        with st.container():
            st.markdown(f'<div class="chat-item">', unsafe_allow_html=True)
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                if st.button(chat["name"], key=f"select_{chat_id}", use_container_width=True):
                    select_chat(chat_id)
            with col2:
                with st.popover("⋮", use_container_width=True):
                    new_name = st.text_input("Rename", value=chat["name"], key=f"rename_input_{chat_id}")
                    if st.button("Save", key=f"save_rename_{chat_id}"):
                        chat["name"] = new_name if new_name else chat["name"]
                        st.rerun()
                    pin_label = "Unpin" if chat["pinned"] else "Pin"
                    if st.button(pin_label, key=f"pin_btn_{chat_id}"):
                        toggle_pin(chat_id)
                        st.rerun()
                    if st.button("Delete", key=f"delete_btn_{chat_id}"):
                        delete_chat(chat_id)
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ---- Main area ----
if st.session_state.active_chat:
    chat = st.session_state.chats[st.session_state.active_chat]
    st.header(chat["name"])

    if chat["qa"] is None:
        uploaded_file = st.file_uploader("Upload a PDF for this chat", type="pdf", key=f"upload_{st.session_state.active_chat}")
        if uploaded_file:
            if chat["pdf_uploaded"]:
                st.error("One PDF per chat allowed. Create a new chat for another PDF.")
            else:
                chat["name"] = uploaded_file.name
                chat["pdf_uploaded"] = True

                with st.spinner("Processing PDF..."):
                    progress_bar = st.progress(0)
                    temp_pdf_path = f"/tmp/{uploaded_file.name}"
                    with open(temp_pdf_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    loader = PyPDFLoader(temp_pdf_path)
                    documents = loader.load()
                    progress_bar.progress(0.3)

                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
                    texts = text_splitter.split_documents(documents)
                    progress_bar.progress(0.6)

                    try:
                        embeddings = HuggingFaceEmbeddings(
                            model_name="sentence-transformers/all-MiniLM-L6-v2",
                            model_kwargs={"device": "cpu"},
                            cache_folder="/tmp/hf_cache"
                        )
                        vectorstore = PineconeVectorStore.from_documents(
                            texts,
                            embedding=embeddings,
                            index_name=INDEX_NAME,
                            namespace=chat["namespace"]
                        )
                        time.sleep(15)
                        progress_bar.progress(0.9)
                    except Exception as e:
                        st.error(f"Embedding error: {str(e)}. Check Hugging Face token and Pinecone setup.")
                        chat["pdf_uploaded"] = False
                        os.remove(temp_pdf_path)
                        st.rerun()
                        raise

                    system_prompt = (
                        "You are an assistant for question-answering. Use ONLY the retrieved context from the uploaded PDF. "
                        "Do not use external knowledge or invent answers. If the answer isn’t in the context, say 'I don’t know based on the PDF.' "
                        "Be concise and relevant. Context: {context}"
                    )
                    qa_prompt = ChatPromptTemplate.from_messages([
                        ("system", system_prompt),
                        ("human", "{question}")
                    ])

                    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                    qa = ConversationalRetrievalChain.from_llm(
                        llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY),
                        retriever=vectorstore.as_retriever(search_kwargs={"k": 15}),
                        memory=memory,
                        combine_docs_chain_kwargs={"prompt": qa_prompt}
                    )
                    chat["qa"] = qa
                    progress_bar.progress(1.0)

                    st.success("✅ PDF processed!")
                    os.remove(temp_pdf_path)
                    st.rerun()

    else:
        for msg in chat["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask something...")
        if user_input:
            chat["messages"].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.spinner("Thinking..."):
                response = chat["qa"]({"question": user_input})
                answer = response["answer"]

            chat["messages"].append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)
else:
    st.info("Click **New Chat** in the sidebar to start.")

# CSS for better UI
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        padding: 10px;
    }
    .chat-item {
        padding: 5px 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    .chat-item:hover {
        background-color: #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        justify-content: left;
    }
    </style>
""", unsafe_allow_html=True)