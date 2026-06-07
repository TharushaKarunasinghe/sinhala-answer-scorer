import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

KB_DIR     = "knowledge_base"
CHROMA_DIR = "chroma_db"
EMBED_MODEL = "nomic-embed-text"


def ingest():
    print("📂 Loading knowledge base files...")
    docs = []
    for fname in os.listdir(KB_DIR):
        if fname.endswith(".txt"):
            fpath = os.path.join(KB_DIR, fname)
            loader = TextLoader(fpath, encoding="utf-8")
            loaded = loader.load()
            # Tag each document with its source era
            era_tag = fname.replace("_era.txt", "").replace("_", " ")
            for doc in loaded:
                doc.metadata["era"] = era_tag
                doc.metadata["source"] = fname
            docs.extend(loaded)
            print(f"  ✅ Loaded: {fname} ({len(loaded)} doc)")

    print(f"\n✂️  Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=80,
        separators=["\n\n", "\n", "।", ".", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"  Total chunks: {len(chunks)}")

    print(f"\n🔢 Generating embeddings with nomic-embed-text (offline)...")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    print(f"\n💾 Saving to ChromaDB at '{CHROMA_DIR}'...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name="colonial_sl"
    )
    print(f"\n✅ Ingestion complete. {len(chunks)} chunks stored in ChromaDB.")
    return vectorstore


if __name__ == "__main__":
    ingest()