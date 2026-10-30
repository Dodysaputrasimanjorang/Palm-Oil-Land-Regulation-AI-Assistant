"""
Phase 6 — Embedding + Vector Database (Qdrant).
Menyimpan semua chunks ke Qdrant dengan metadata filtering support.
"""

import json
import hashlib
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    Range,
)

from .config import (
    CHUNKS_FILE,
    EMBEDDING_MODEL,
    QDRANT_PATH,
    QDRANT_COLLECTION_NAME,
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

_model = None

def get_embedding_model() -> SentenceTransformer:
    """Load embedding model (singleton)."""
    global _model
    if _model is None:
        print(f"🔄 Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✅ Model loaded. Embedding dimension: {_model.get_sentence_embedding_dimension()}")
    return _model


def embed_texts(texts: list[str], batch_size: int = 64, is_query: bool = False) -> list[list[float]]:
    """Generate embeddings untuk list of texts.
    
    Args:
        texts: list of texts to embed
        batch_size: batch size for encoding
        is_query: True untuk query, False untuk dokumen/passage
    """
    model = get_embedding_model()
    # Prefix untuk model e5: "query: " untuk pertanyaan, "passage: " untuk dokumen
    if "e5" in EMBEDDING_MODEL.lower():
        prefix = "query: " if is_query else "passage: "
        texts = [f"{prefix}{t}" for t in texts]

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


# ============================================================
# QDRANT SETUP
# ============================================================

_client = None

def get_qdrant_client() -> QdrantClient:
    """Get Qdrant persistent local client."""
    global _client
    if _client is None:
        QDRANT_PATH.mkdir(parents=True, exist_ok=True)
        _client = QdrantClient(path=str(QDRANT_PATH))
    return _client


def ensure_collection(reset: bool = False) -> None:
    """Create (or recreate) Qdrant collection with cosine distance."""
    client = get_qdrant_client()
    embedding_dim = get_embedding_model().get_sentence_embedding_dimension()

    if reset:
        try:
            client.delete_collection(QDRANT_COLLECTION_NAME)
            print(f"🗑️ Collection '{QDRANT_COLLECTION_NAME}' deleted for reset.")
        except Exception:
            pass

    collections = client.get_collections().collections
    existing_names = {c.name for c in collections}
    if QDRANT_COLLECTION_NAME in existing_names:
        return

    client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=VectorParams(
            size=embedding_dim,
            distance=Distance.COSINE,
        ),
    )


# ============================================================
# TRUNCATE TEXT yang terlalu panjang
# ============================================================

def truncate_text(text: str, max_chars: int = 8000) -> str:
    """Truncate text yang terlalu panjang untuk embedding."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def _to_qdrant_point_id(chunk_id: str) -> int:
    """Convert arbitrary chunk_id string to deterministic int64 for Qdrant."""
    digest = hashlib.sha1(chunk_id.encode("utf-8")).hexdigest()
    value = int(digest[:16], 16)
    return value & 0x7FFFFFFFFFFFFFFF


# ============================================================
# INDEX ALL CHUNKS KE QDRANT
# ============================================================

def index_chunks(chunks: list[dict] = None, reset: bool = True, batch_size: int = 64):
    """
    Index semua chunks ke Qdrant.
    - Generate embeddings
    - Store di Qdrant dengan metadata
    """
    # Load chunks jika tidak diberikan
    if chunks is None:
        if not CHUNKS_FILE.exists():
            raise FileNotFoundError(f"File {CHUNKS_FILE} tidak ditemukan. Jalankan chunker.py dulu.")
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            chunks = json.load(f)

    print(f"📦 Total chunks to index: {len(chunks)}")

    # Siapkan collection
    ensure_collection(reset=reset)

    # Prepare data for Qdrant
    ids = []
    documents = []
    metadatas = []
    embeddings_texts = []

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        text = chunk["text"]
        meta = chunk["metadata"]

        # Truncate text terlalu panjang
        text_for_embed = truncate_text(text)

        # Simpan topik sebagai list agar filtering MatchAny lebih presisi
        topik_val = meta["topik"]
        if isinstance(topik_val, list):
            topik_data = topik_val
        else:
            topik_data = [topik_val]

        qdrant_meta = {
            "dokumen": meta["dokumen"],
            "jenis": meta["jenis"],
            "tahun": meta["tahun"],
            "pasal": meta["pasal"],
            "topik": topik_data,
            "filename": meta["filename"],
            "chunk_index": meta["chunk_index"],
            "token_estimate": meta["token_estimate"],
        }

        ids.append(chunk_id)
        documents.append(text)
        metadatas.append(qdrant_meta)
        embeddings_texts.append(text_for_embed)

    # Generate embeddings in batches (is_query=False karena ini dokumen/passage)
    print("🧠 Generating embeddings...")
    all_embeddings = embed_texts(embeddings_texts, batch_size=batch_size, is_query=False)

    # Insert to Qdrant in batches
    print("💾 Inserting into Qdrant...")
    qdrant_batch_size = 500
    client = get_qdrant_client()
    for i in tqdm(range(0, len(ids), qdrant_batch_size), desc="Indexing"):
        end = min(i + qdrant_batch_size, len(ids))
        points = []
        for j in range(i, end):
            payload = {
                "chunk_id": ids[j],
                "text": documents[j],
                **metadatas[j],
            }
            points.append(
                PointStruct(
                    id=_to_qdrant_point_id(ids[j]),
                    vector=all_embeddings[j],
                    payload=payload,
                )
            )

        client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points,
        )

    total = client.count(collection_name=QDRANT_COLLECTION_NAME, exact=True).count
    print(f"✅ Indexed {total} chunks in Qdrant")
    return total


def _where_to_qdrant_filter(where: dict | None) -> Filter | None:
    """Convert simple Chroma-like where clause into Qdrant Filter."""
    if not where:
        return None

    conditions = []

    def parse_condition(cond: dict):
        if "$and" in cond:
            for sub in cond["$and"]:
                parse_condition(sub)
            return
        if "$or" in cond:
            # Untuk kebutuhan saat ini, $or hanya dipakai untuk topik.
            # Kita flatten menjadi MatchAny pada field yang sama.
            topik_values = []
            for sub in cond["$or"]:
                if "topik" in sub and "$contains" in sub["topik"]:
                    topik_values.append(sub["topik"]["$contains"])
            if topik_values:
                conditions.append(
                    FieldCondition(
                        key="topik",
                        match=MatchAny(any=topik_values),
                    )
                )
            return

        for key, value in cond.items():
            if not isinstance(value, dict):
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                continue

            if "$eq" in value:
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value["$eq"])))
            elif "$gte" in value or "$lte" in value:
                conditions.append(
                    FieldCondition(
                        key=key,
                        range=Range(
                            gte=value.get("$gte"),
                            lte=value.get("$lte"),
                        ),
                    )
                )
            elif "$contains" in value:
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchAny(any=[value["$contains"]]),
                    )
                )

    parse_condition(where)
    if not conditions:
        return None
    return Filter(must=conditions)


def search_similar(query: str, n_results: int = 5, where: dict = None) -> dict:
    """
    Cari chunks yang mirip berdasarkan semantic similarity.
    
    Args:
        query: pertanyaan user
        n_results: jumlah hasil
        where: filter metadata style ChromaDB (optional)
    
    Returns:
        dict dengan keys: ids, documents, metadatas, distances
    """
    ensure_collection(reset=False)
    client = get_qdrant_client()

    # Embed query (is_query=True)
    query_embedding = embed_texts([query], is_query=True)

    # Search
    query_filter = _where_to_qdrant_filter(where)
    points = client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_embedding[0],
        limit=n_results,
        with_payload=True,
        query_filter=query_filter,
    )

    ids = []
    documents = []
    metadatas = []
    distances = []

    for p in points:
        payload = p.payload or {}
        doc_text = payload.get("text", "")
        metadata = {k: v for k, v in payload.items() if k != "text"}
        sim_score = float(p.score) if p.score is not None else 0.0
        chunk_id = payload.get("chunk_id", str(p.id))

        ids.append(str(chunk_id))
        documents.append(doc_text)
        metadatas.append(metadata)
        distances.append(1.0 - sim_score)

    # Keep return format compatible with existing Chroma-based caller
    return {
        "ids": [ids],
        "documents": [documents],
        "metadatas": [metadatas],
        "distances": [distances],
    }


if __name__ == "__main__":
    # Index semua chunks
    total = index_chunks(reset=True)

    # Test search
    print("\n" + "=" * 60)
    print("🔍 Test semantic search")
    print("=" * 60)

    test_queries = [
        "izin usaha perkebunan kelapa sawit",
        "pembukaan lahan di kawasan hutan",
        "sanksi pelanggaran lingkungan perkebunan",
    ]

    for query in test_queries:
        print(f"\n❓ Query: {query}")
        results = search_similar(query, n_results=3)
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )):
            print(f"  [{i+1}] Score: {1-dist:.4f} | {meta['dokumen']} | {meta['pasal']}")
            print(f"      Topik: {meta['topik']}")
            print(f"      Preview: {doc[:120]}...")
