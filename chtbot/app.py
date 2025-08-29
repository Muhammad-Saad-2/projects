import streamlit as st
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import DataFrameLoader
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Streamlit App
st.set_page_config(page_title="Chat with your CSV", layout="wide")
st.title("📊 Chat with your CSV")

# Session states
if "chain" not in st.session_state:
    st.session_state.chain = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    # Load CSV into DataFrame
    df = pd.read_csv(uploaded_file)

    # Show preview
    with st.expander("🔎 Preview Data"):
        st.dataframe(df.head())

    # Convert DataFrame into LangChain Documents
    loader = DataFrameLoader(df, page_content_column=df.columns[0])  # pick first column as content
    documents = loader.load()

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

    # Vector Store (new FAISS for each upload)
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Memory for chat
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)

    # Conversational chain
    st.session_state.chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

    st.success("✅ CSV processed! You can now ask questions about it.")

# Chat Interface
if st.session_state.chain:
    query = st.chat_input("Ask something about your CSV...")
    if query:
        result = st.session_state.chain({"question": query})
        answer = result["answer"]

        # Save chat history
        st.session_state.chat_history.append(("You", query))
        st.session_state.chat_history.append(("Bot", answer))

    # Display chat
    for speaker, msg in st.session_state.chat_history:
        with st.chat_message("user" if speaker == "You" else "assistant"):
            st.markdown(msg)
