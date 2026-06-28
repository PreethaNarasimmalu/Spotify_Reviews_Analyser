import chromadb
from chromadb.utils import embedding_functions
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHROMA_DIR = "data/chroma"
COLLECTION_NAME = "spotify_reviews"

# Lightweight, fast, free — no API key needed
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        # EphemeralClient (in-memory) avoids PersistentClient tenant init
        # issues on ephemeral filesystems (Streamlit Cloud). Data is rebuilt
        # each session, which is fine since runs are manual and on-demand.
        _client = chromadb.EphemeralClient()
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def index_reviews(reviews: list[dict], run_id: str):
    """Embed and store reviews in ChromaDB."""
    collection = _get_collection()

    documents, metadatas, ids = [], [], []

    for i, r in enumerate(reviews):
        text = r.get("text", "").strip()
        if not text:
            continue
        uid = f"{run_id}_{i}"
        documents.append(text)
        metadatas.append({
            "source": r.get("source", ""),
            "platform": r.get("platform", ""),
            "rating": str(r.get("rating") or ""),
            "date": r.get("date", "")[:10] if r.get("date") else "",
            "run_id": run_id,
            "topics": ",".join(r.get("analysis", {}).get("topics", []) or []),
            "sentiment": r.get("analysis", {}).get("sentiment", ""),
            "user_segment": r.get("analysis", {}).get("user_segment", ""),
        })
        ids.append(uid)

    if not documents:
        return 0

    # Add in sub-batches to avoid ChromaDB limits
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size],
        )

    print(f"[RAG] Indexed {len(documents)} reviews into ChromaDB")
    return len(documents)


def retrieve(query: str, top_k: int = 15, filters: dict = None) -> list[dict]:
    """Retrieve top-K most semantically similar reviews for a query."""
    collection = _get_collection()

    where = filters if filters else None

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count() or 1),
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text": doc,
            "source": meta.get("source", ""),
            "date": meta.get("date", ""),
            "rating": meta.get("rating", ""),
            "sentiment": meta.get("sentiment", ""),
            "user_segment": meta.get("user_segment", ""),
            "relevance_score": round(1 - dist, 3),
        })

    return hits


def get_index_count() -> int:
    try:
        return _get_collection().count()
    except Exception:
        return 0
