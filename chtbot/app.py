import streamlit as st
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone
import os

# ==========================
# 1. Load API keys
# ==========================
google_api_key = os.getenv("GOOGLE_API_KEY")  # stored in colab secrets
pinecone_api_key = os.getenv("PINECONE_API_KEY")

if not google_api_key or not pinecone_api_key:
    st.error("API keys not found. Please set GOOGLE_API_KEY and PINECONE_API_KEY.")
    st.stop()

# ==========================
# 2. Setup Pinecone
# ==========================
pc = Pinecone(api_key=pinecone_api_key)
index_name = "products-index"
pc_index = pc.Index(index_name)

vector_store = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=None,  # embeddings not needed at query time
    text_key="content"
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# ==========================
# 3. Setup Gemini LLM
# ==========================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=google_api_key,
    temperature=0.2
)

# ==========================
# 4. Streamlit App
# ==========================
st.set_page_config(page_title="Product Chatbot", page_icon="🤖")
st.title("🛍️ Product RAG Chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_query = st.chat_input("Ask me about a product...")

if user_query:
    # Retrieve context
    docs = retriever.get_relevant_documents(user_query)
    context = "\n\n".join([d.page_content for d in docs])

    # Format prompt
    prompt = f"""
    You are a helpful product assistant. 
    Use the context below to answer the question.

    Context:
    {context}

    Question:
    {user_query}
    """

    response = llm.invoke(prompt)

    # Save chat history
    st.session_state.chat_history.append(("user", user_query))
    st.session_state.chat_history.append(("assistant", response.content))

# Display chat
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)
