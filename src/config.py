from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RUNBOOKS_DIR = BASE_DIR / "data" / "runbooks"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "runbooks"

EMBEDDING_MODEL = "text-embedding-3-small"

CHUNK_SIZE = 400      # characters per chunk
CHUNK_OVERLAP = 80    # characters shared between neighbouring chunks
TOP_K = 3             # how many chunks to retrieve (used in the next step)
CHAT_MODEL = "gpt-4o-mini"   
MAX_DISTANCE = 0.5
RELATIVE_MARGIN = 0.1   # keep only chunks within 0.1 of the best match