# app/streamlit_app.py

import sys
from streamlit.web.cli import main
import torch
sys.modules['torch.classes'] = None  # Block introspection here

import streamlit as st
from src.rag_chain import load_retriever, build_rag_chain, rerank_chunks, inject_page_numbers

st.set_page_config(page_title="Aviation RAG Chatbot", layout="wide")

st.title("🛫 EASA Aviation FAQ Chatbot")
st.caption("Ask aviation regulatory questions based on the EASA Air OPS document.")

retriever = load_retriever()
qa_chain = build_rag_chain(retriever)

question = st.text_input("❓ Ask your question", placeholder="e.g. When can a commander extend the flight duty period?")

if st.button("🧠 Get Answer") and question:
    with st.spinner("Retrieving answer..."):
        docs = retriever.invoke(question)
        top_docs = rerank_chunks(question, docs)
        result = qa_chain.invoke({"context": top_docs, "input": question})

        st.markdown("### 💬 Answer")
        st.write(result)

        st.markdown("### 📄 Pages Used")
        for doc in top_docs:
            page = doc.metadata.get("page_number", "N/A")
            st.write(f"Page {page}")
