import streamlit as st
import requests
import time
import random

API_BASE_URL="http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Enterprise RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

# Title and header
st.title("🤖 Enterprise Document Intelligence System")
st.markdown("### Chat with your internal documents securely.")

# Sidebar
with st.sidebar:
    st.header("📂 Document Ingestion")
    uploaded_file=st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Ingesting document... (Chunking & Embedding)"):
                try:
                    # File ko backend bhejna
                    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                    response = requests.post(f"{API_BASE_URL}/ingest", files=files)
                    
                    if response.status_code == 200:
                        st.success("✅ Document processed successfully!")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: Is Backend running? \n {e}")

        st.divider()
        st.markdown("**System Status:**")
        st.info("Backend: Localhost:8000 \nLLM: Llama-3 (Ollama)")

# main chat interface
# Initialize chat history
# Session State to store chat history (Refresh hone pe chat gayab na ho)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about your documents..."):
    # 1. User ka message display karo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Backend se answer laao
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Backend API call
                payload = {"query": prompt}
                response = requests.post(f"{API_BASE_URL}/ask", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer found.")
                    sources = data.get("sources", [])
                    
                    # Answer display karo
                    st.markdown(answer)
                    
                    # Sources display karo (Expandable view mein)
                    if sources:
                        with st.expander("📚 View Source Documents"):
                            for source in sources:
                                st.caption(f"**Page {source['page']}**: {source['text'][:100]}...")
                    
                    # History mein add karo
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                
                else:
                    st.error("Error generating response.")
            
            except Exception as e:
                st.error(f"Connection Failed. Make sure FastAPI backend is running. \n {e}")