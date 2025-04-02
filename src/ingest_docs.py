# src/ingest_docs.py
import os
from dotenv import load_dotenv
from unstructured.partition.pdf import partition_pdf
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import logging

logging.getLogger("unstructured").setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfminer.layout").setLevel(logging.ERROR)
logging.getLogger("pdfminer.converter").setLevel(logging.ERROR)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def load_documents(data_path="data/easa_air_ops.pdf"):
    print("🔹 Loading document...")
    elements = partition_pdf(data_path, strategy="fast")
    
    documents = []
    for el in elements:
        if el.text.strip():  # skip empty chunks
            metadata = {
                "source": data_path,
                "page_number": el.metadata.page_number
            }
            documents.append(Document(page_content=el.text, metadata=metadata))
    
    return documents


def chunk_documents(docs, chunk_size=1500, chunk_overlap=200):
    print("🔹 Splitting document into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n## ", "\n## ", "\n• ", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(docs)

def embed_documents(chunks, output_dir="embeddings"):
    print("🔹 Creating embeddings and saving FAISS index...")
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(output_dir)
    print(f"✅ Embeddings saved to: {output_dir}/index.faiss")
    
if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_documents(docs)
    embed_documents(chunks)