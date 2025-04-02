# GenAI Aviation FAQ Chatbot (EASA RAG)

A production-ready Retrieval-Augmented Generation (RAG) chatbot built with LangChain, OpenAI, and Streamlit — designed to answer regulatory questions using the full EASA Air OPS PDF (2400+ pages). Deployed in a Docker container for easy portability and future integration with cloud platforms like Azure.

---

## Features

- ✅ Full-document ingestion with `unstructured` PDF parsing
- ✅ Hybrid Retrieval (FAISS vector search + BM25 keyword search)
- ✅ Cross-encoder Re-Ranking using `bge-reranker-base`
- ✅ RAG pipeline with GPT-4o-mini via LangChain
- ✅ Transparent source traceability (shows referenced pages)
- ✅ Streamlit frontend with live query input
- ✅ Dockerized for production use
- ✅ Modular and testable Python codebase

---

## Project Structure

```
text genai-aviation-faq-chatbot/
├── app/ # Streamlit UI
│ └── streamlit_app.py
├── data/ # Raw PDFs (e.g., EASA Air OPS) 
├── embeddings/ # FAISS index & metadata cache (⚠️ not tracked in Git) 
├── src/ # Ingestion & RAG logic 
│ ├── ingest_docs.py 
│ ├── rag_chain.py 
│ └── config.py ├── Dockerfile # Docker build 
├── requirements.txt 
├── .env # OpenAI key, etc. 
├── README.md └── main.py # CLI question tool
```

---

## Getting Started

### 1. Install Requirements Locally

```bash
python -m venv .venv
source .venv/bin/activate     # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Add Your `.env`

```env
OPENAI_API_KEY=your-openai-key
```

### 3. Ingest the Document

This runs PDF parsing, chunking, embedding, and saves the FAISS index.

```bash
python src/ingest_docs.py
```

---

## Run the Chatbot (Locally)

```bash
streamlit run app/streamlit_app.py
```

Then open: [http://localhost:8501](http://localhost:8501)

---

## Run with Docker (Production-Ready)

### Build the container:

```bash
docker build -t aviation-faq-chatbot .
```

### Run the app:

```bash
docker run -p 8501:8501 -v ${PWD}/embeddings:/app/embeddings --env-file .env aviation-faq-chatbot
```

➡️ App will be available at: [http://localhost:8501](http://localhost:8501)

---

## Technologies Used

| Stack | Tool |
|-------|------|
| 🔗 LLM Framework | LangChain |
| 🧠 LLM | OpenAI GPT-4o / GPT-3.5 |
| 📚 Vector Store | FAISS |
| 🔍 Keyword Search | BM25 (RankBM25) |
| 🎯 Reranking | BGE-Reranker (CrossEncoder) |
| 📄 PDF Parsing | unstructured + pdfminer |
| 🎛️ UI | Streamlit |
| 🐳 Containerization | Docker |

---

##  Example Questions

- When can a commander extend the flight duty period?
- What are the rest requirements after a long-haul duty?
- What navigation systems must be operational before departure?
- What is the operator's responsibility for fuel planning?

![image](https://github.com/user-attachments/assets/0c23ec70-a88a-4252-b63a-e1824213417e)

---

## Notes

- You only need to embed the document once (`src/ingest_docs.py`)
- Embeddings are cached in `/embeddings`
- OpenAI GPT-4o used via `langchain-openai` with clean prompt engineering
- ⚠️ FAISS files are **not pushed to GitHub** due to size limits. Regenerate locally using the ingestion script.

---

## Author

Built by [@aym2020](https://github.com/aym2020) for aviation compliance R&D using GenAI and RAG techniques.
