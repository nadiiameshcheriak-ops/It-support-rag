from dotenv import load_dotenv
from openai import OpenAI
import chromadb

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K

load_dotenv()
client = OpenAI()
collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(COLLECTION_NAME)


def retrieve(question, top_k=TOP_K):
    """Find the chunks closest in meaning to the question."""
    embedding = client.embeddings.create(model=EMBEDDING_MODEL, input=[question]).data[0].embedding
    result = collection.query(query_embeddings=[embedding], n_results=top_k)
    hits = []
    for text, meta, distance in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        hits.append({"text": text, "source": meta["source"], "distance": distance})
    return hits