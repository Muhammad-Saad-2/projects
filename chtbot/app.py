import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone, ServerlessSpec
import uuid

# Load secrets
load_dotenv()
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY", os.getenv("PINECONE_API_KEY"))

# Pinecone setup (shared index with namespaces)
pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "rag-chatbot"
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,  # For sentence-transformers/all-MiniLM-L6-v2
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # Adjust region if needed
    )
index = pc.Index(INDEX_NAME)

# Embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ---- Initialize session state ----
if "chats" not in st.session_state:
    st.session_state.chats = {}  # {chat_id: {"name": str, "messages": [], "qa": chain, "pdf_uploaded": bool, "namespace": str}}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

# ---- Helper to create a new chat ----
def create_new_chat():
    st.session_state.chat_counter += 1
    chat_id = f"chat_{uuid.uuid4().hex[:8]}"  # Unique ID
    namespace = chat_id  # Namespace for Pinecone isolation
    st.session_state.chats[chat_id] = {
        "name": f"Chat {st.session_state.chat_counter}",
        "messages": [],
        "qa": None,
        "pdf_uploaded": False,
        "namespace": namespace
    }
    st.session_state.active_chat = chat_id

# ---- Helper to delete a chat ----
def delete_chat(chat_id):
    namespace = st.session_state.chats[chat_id]["namespace"]
    # Delete from Pinecone
    index.delete(delete_all=True, namespace=namespace)
    # Remove from session state
    del st.session_state.chats[chat_id]
    if st.session_state.active_chat == chat_id:
        st.session_state.active_chat = None

# ---- Sidebar: Chat management (like modern apps: New Chat at top) ----
with st.sidebar:
    st.button("➕ New Chat", on_click=create_new_chat, key="new_chat_top")

    st.markdown("### Your Chats")
    for chat_id in list(st.session_state.chats.keys()):
        chat = st.session_state.chats[chat_id]
        col1, col2 = st.columns([3, 1])
        new_name = col1.text_input("Rename", value=chat["name"], key=f"rename_{chat_id}")
        if new_name != chat["name"]:
            chat["name"] = new_name
        if col2.button("🗑️", key=f"delete_{chat_id}"):
            delete_chat(chat_id)
            st.experimental_rerun()
        if st.button(chat["name"], key=chat_id):
            st.session_state.active_chat = chat_id

# ---- Main area ----
if st.session_state.active_chat:
    chat = st.session_state.chats[st.session_state.active_chat]
    st.header(chat["name"])

    # If no QA chain yet (no PDF processed)
    if chat["qa"] is None:
        uploaded_file = st.file_uploader("Upload a PDF for this chat", type="pdf", key=f"upload_{st.session_state.active_chat}")
        if uploaded_file:
            if chat["pdf_uploaded"]:
                st.error("Per PDF per session allowed. To chat with another PDF, create a new chat from the sidebar.")
            else:
                # Save PDF name as chat name
                chat["name"] = uploaded_file.name
                chat["pdf_uploaded"] = True

                # Process PDF with progress indicator
                with st.spinner("Processing PDF..."):
                    progress_bar = st.progress(0)
                    # Save uploaded file temporarily
                    temp_pdf_path = f"/tmp/{uploaded_file.name}"
                    with open(temp_pdf_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    # Load and split
                    loader = PyPDFLoader(temp_pdf_path)
                    documents = loader.load()
                    progress_bar.progress(0.3)  # 30% after loading

                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    texts = text_splitter.split_documents(documents)
                    progress_bar.progress(0.6)  # 60% after splitting

                    # Embed and store in Pinecone with namespace
                    vectorstore = PineconeVectorStore.from_documents(
                        texts,
                        embedding=embeddings,
                        index_name=INDEX_NAME,
                        namespace=chat["namespace"]
                    )
                    progress_bar.progress(0.9)  # 90% after embedding

                    # Setup memory and chain
                    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                    qa = ConversationalRetrievalChain.from_llm(
                        llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY),
                        retriever=vectorstore.as_retriever(),
                        memory=memory
                    )
                    chat["qa"] = qa
                    progress_bar.progress(1.0)  # Complete

                    st.success("✅ PDF processed and embeddings stored for this chat!")
                    os.remove(temp_pdf_path)  # Clean up temp file
                    st.experimental_rerun()  # Refresh UI

    else:
        # Show chat history
        for msg in chat["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
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
    st.info("Click **New Chat** in the sidebar to start a session.")