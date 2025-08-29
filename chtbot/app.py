import os
import streamlit as st
import pandas as pd
import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Set Google API key
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))

# ---- Initialize session state ----
if "chats" not in st.session_state:
    st.session_state.chats = {}  # {chat_id: {"name": str, "messages": [], "qa": chain}}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

# ---- Helper to create a new chat ----
def create_new_chat():
    st.session_state.chat_counter += 1
    chat_id = f"chat_{st.session_state.chat_counter}"

    # Limit to 5 chats, remove oldest
    if len(st.session_state.chats) >= 5:
        oldest = list(st.session_state.chats.keys())[0]
        del st.session_state.chats[oldest]

    st.session_state.chats[chat_id] = {
        "name": f"Chat {st.session_state.chat_counter}",
        "messages": [],
        "qa": None  # will be set after CSV upload
    }
    st.session_state.active_chat = chat_id

# ---- Sidebar: Chat management ----
with st.sidebar:
    st.button("➕ New Chat", on_click=create_new_chat)

    st.markdown("### Your Chats")
    for chat_id, chat_data in st.session_state.chats.items():
        if st.button(chat_data["name"], key=chat_id):
            st.session_state.active_chat = chat_id

# ---- Main area ----
if st.session_state.active_chat:
    chat = st.session_state.chats[st.session_state.active_chat]
    st.header(chat["name"])

    # If no QA chain yet, allow CSV upload
    if chat["qa"] is None:
        uploaded_file = st.file_uploader("Upload a CSV file for this chat", type="csv", key=f"upload_{st.session_state.active_chat}")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)

            # Convert rows into documents
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            texts = text_splitter.split_text("\n".join(df.astype(str).apply(lambda row: " | ".join(row), axis=1)))

            # Ensure event loop for async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                vectorstore = FAISS.from_texts(texts, embeddings)

                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

                qa = ConversationalRetrievalChain.from_llm(
                    llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash"),
                    retriever=vectorstore.as_retriever(),
                    memory=memory
                )

                chat["qa"] = qa
                st.success("✅ CSV processed and embeddings stored for this chat!")
            finally:
                loop.close()

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

            # Run async operation in the event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(chat["qa"].ainvoke({"question": user_input}))
                answer = response["answer"]
            finally:
                loop.close()

            chat["messages"].append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)
else:
    st.info("Click **New Chat** in the sidebar to start a session.")