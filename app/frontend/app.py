import streamlit as st
import requests
import os
import shutil

import time

def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

# Config
API_URL = "http://localhost:8000/query"
DATA_DIR = "data"

st.set_page_config(page_title="Agentic RAG Assistant", layout="wide")

st.title("🤖 Agentic RAG Assistant")
st.markdown("Ask questions about your documents (PDF) or data (Excel).")

# Sidebar - File Upload
with st.sidebar:
    st.header("📂 Data Management")
    uploaded_files = st.file_uploader(
        "Upload your Knowledge Base", 
        type=["pdf", "xlsx", "xls", "txt", "csv", "pptx", "docx"], 
        accept_multiple_files=True
    )
    
    existing_files = os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else []
    
    if existing_files:
        st.info(f"📚 {len(existing_files)} files available in Knowledge Base.")
    
    if st.button("Ingest Files"):
        if uploaded_files:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
            
            for uploaded_file in uploaded_files:
                file_path = os.path.join(DATA_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Saved: {uploaded_file.name}")
        
        # Ingest if files exist (either uploaded or pre-existing)
        if existing_files or uploaded_files:
            with st.spinner("Ingesting documents into Milvus (this may take a while)..."):
                import subprocess
                subprocess.run(["python", "-m", "app.ingestion.ingest"], check=True)
            st.success("Ingestion Complete!")
        else:
            st.warning("No files found to ingest. Please upload data.")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"question": prompt})
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer.")
                    datasource = data.get("datasource", "unknown")
                    docs = data.get("documents", [])
                    
                    st.write_stream(stream_data(answer))
                    
                    if docs:
                        with st.expander(f"📚 Sources ({datasource})"):
                            for doc in docs:
                                st.markdown(f"**{doc['source']}** ({doc['type']})")
                                st.caption(doc['content'][:200] + "...")
                                st.divider()
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to Backend API. Is it running?")

