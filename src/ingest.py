from dotenv import load_dotenv
from openai import OpenAI
import chromadb

from config import (
    RUNBOOKS_DIR,
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

load_dotenv()
client = OpenAI()  # reads OPENAI_API_KEY from the environment


def load_documents():
    """Read every .md file from the runbooks folder."""
    docs = []
    for path in sorted(RUNBOOKS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            print(f"Warning: {path.name} is empty, skipping")
            continue
        docs.append({"source": path.name, "text": text})
    return docs


def split_into_chunks(text, size, overlap):
    """Cut text into overlapping pieces."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def embed(texts):
    """Turn a list of texts into a list of embeddings."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def main():
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")

    ids, texts, metadatas = [], [], []
    for doc in docs:
        for i, chunk in enumerate(split_into_chunks(doc["text"], CHUNK_SIZE, CHUNK_OVERLAP)):
            ids.append(f"{doc['source']}-{i}")
            texts.append(chunk)
            metadatas.append({"source": doc["source"], "chunk": i})
    print(f"Created {len(texts)} chunks")

    chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        chroma.delete_collection(COLLECTION_NAME)  # start clean, no duplicates
    except Exception:
        pass
    collection = chroma.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    embeddings = embed(texts)
    collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    print(f"Stored {len(texts)} chunks in Chroma at {CHROMA_DIR}")


if __name__ == "__main__":
    main()