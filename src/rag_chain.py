# src/rag_chain.py

import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder
from datetime import datetime


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

reranker = CrossEncoder("BAAI/bge-reranker-base")

def load_retriever(embedding_dir="embeddings"):
    print("🔹 Loading FAISS index...")
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = FAISS.load_local(embedding_dir, embeddings, allow_dangerous_deserialization=True)
    docs = vectorstore.docstore._dict.values()

    bm25 = BM25Retriever.from_documents(list(docs))
    bm25.k = 5

    hybrid = EnsembleRetriever(
        retrievers=[vectorstore.as_retriever(), bm25],
        weights=[0.7, 0.3]
    )
    return hybrid

def inject_page_numbers(docs):
    return "\n\n".join(
        f"[Page {doc.metadata.get('page_number', 'N/A')}]\n{doc.page_content}"
        for doc in docs
    )

def rerank_chunks(query, docs, top_k=5):
    pairs = [[query, doc.page_content] for doc in docs]
    scores = reranker.predict(pairs)
    reranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in reranked[:top_k]]

def build_rag_chain(retriever):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    system_prompt = """You are an expert in EASA aviation regulations. You answer questions using ONLY the provided context.

    Instructions:
    - Your goal is to provide a detailed and structured explanation, as if training a new pilot or compliance officer.
    - Your answer must be well-developed, informative, and easy to understand.
    - Reference the source page(s) when relevant (e.g., "As stated on Page 102").
    - If the answer is partially addressed in the context, try to summarize it.
    - Only say "I don’t know" if the context clearly does not mention it at all.    - Do NOT make up any information or page numbers.
    - Use bullet points or paragraph form when appropriate.
    - Answer length should be at least 3–6 sentences.

    Context:
    {context}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])

    qa_chain = create_stuff_documents_chain(llm, prompt)
    return qa_chain

def ask_question(question, retriever, qa_chain):
    docs = retriever.invoke(question)
    top_docs = rerank_chunks(question, docs)

    result = qa_chain.invoke({"context": top_docs, "input": question})

    print("\n💬 Question:")
    print(question)

    print("\n🧠 Answer:")
    print(result)
    
    print("\n📄 Pages Used:")
    seen_pages = set()
    for doc in top_docs:
        page = doc.metadata.get("page_number", "N/A")
        if page not in seen_pages:
            print(f"- Page {page}")
            seen_pages.add(page)
            
            
benchmark_questions = [
    "When can a commander extend the flight duty period?",
    "What are the rest requirements after a long-haul duty?",
    "Can a crew member take multiple rest periods during a flight?",
    "What is the maximum number of sectors a flight crew member can operate in a day?",
    "What navigation systems must be checked before departure?",
    "What are the requirements for RNAV operations?",
    "What equipment must be operational before conducting CAT II or CAT III approaches?",
    "What documents must be carried on board before a flight?",
    "When is a technical logbook entry mandatory?",
    "What is the operator's responsibility for fuel planning?",
    "What documents must an operator retain after each flight?",
    "What records must be kept regarding crew duty and rest?",
    "Who is responsible for ensuring the aircraft is airworthy before departure?",
    "What must the commander do after an emergency landing?",
    "What are the procedures for flight crew incapacitation?",
    "How should the operator document and report serious incidents?",
    "What are the responsibilities of the commander before and during a flight?",
    "Can a flight be dispatched if the commander is not fully briefed?",
    "What decisions is the commander allowed to make in case of deviation from the flight plan?",
]

if __name__ == "__main__":
    retriever = load_retriever()
    qa_chain = build_rag_chain(retriever)

    while True:
        q = input("\n❓ Ask a question (or type 'exit'): ")
        if q.lower() == "exit":
            break
        ask_question(q, retriever, qa_chain)
