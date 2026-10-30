"""
Phase 7 & 8 — Hybrid Retrieval (BM25 + Semantic) + Metadata Filtering.

Hybrid search menggabungkan:
1. Semantic search (embedding similarity via Vector DB)
2. Keyword search (BM25)

Dengan metadata filtering sebelum retrieval.
"""

import json
import re
import numpy as np
from rank_bm25 import BM25Okapi
from tqdm import tqdm

from .config import (
    CHUNKS_FILE, SEMANTIC_WEIGHT, BM25_WEIGHT, TOP_K
)
from .vector_store import search_similar


INDONESIAN_STOPWORDS = {
    "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "pada",
    "adalah", "dari", "dalam", "ke", "tidak", "akan", "atau",
    "juga", "sudah", "saya", "bisa", "ada", "mereka",
    "lebih", "tersebut", "oleh", "setiap", "dapat", "telah",
    "sebagai", "bahwa", "atas", "secara", "kepada", "antara",
    "ia", "serta", "tentang", "hal", "agar", "maka", "pun",
    "apabila", "lain", "masing", "harus", "seperti", "tanpa",
    "bagi", "melalui", "saat", "sebelum", "setelah", "per",
    "huruf", "ayat", "pasal", "dimaksud", "sebagaimana",
}


# ============================================================
# BM25 INDEX
# ============================================================

class BM25Index:
    """BM25 keyword search index untuk semua chunks."""

    def __init__(self, chunks: list[dict] = None):
        if chunks is None:
            chunks = self._load_chunks()
        self.chunks = chunks
        self.corpus = [self._tokenize(c["text"]) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus)
        print(f"[OK] BM25 index built with {len(self.corpus)} documents")

    def _load_chunks(self) -> list[dict]:
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenizer untuk Bahasa Indonesia."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        tokens = text.split()
        tokens = [t for t in tokens if t not in INDONESIAN_STOPWORDS and len(t) > 1]
        return tokens

    def search(self, query: str, top_k: int = TOP_K * 3, 
               chunk_ids: list[str] = None) -> list[dict]:
        """
        BM25 keyword search.
        
        Args:
            query: pertanyaan user
            top_k: jumlah hasil
            chunk_ids: filter hanya chunk dengan id tertentu (untuk metadata filtering)
        
        Returns:
            list of { chunk_id, score, text, metadata }
        """
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Buat list (index, score)
        scored = list(enumerate(scores))

        # Filter by chunk_ids jika ada
        if chunk_ids is not None:
            chunk_id_set = set(chunk_ids)
            scored = [
                (i, s) for i, s in scored
                if self.chunks[i]["chunk_id"] in chunk_id_set
            ]

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        scored = scored[:top_k]

        results = []
        for idx, score in scored:
            chunk = self.chunks[idx]
            results.append({
                "chunk_id": chunk["chunk_id"],
                "score": float(score),
                "text": chunk["text"],
                "metadata": chunk["metadata"],
            })

        return results


# ============================================================
# METADATA FILTERING ENGINE (Phase 8)
# ============================================================

class MetadataFilter:
    """
    Filter chunks berdasarkan metadata sebelum retrieval.
    Meningkatkan relevansi dan akurasi.
    """

    # Mapping keyword -> filter metadata
    JENIS_KEYWORDS = {
        "undang-undang": "UU",
        "undang undang": "UU",
        "uu ": "UU",
        "peraturan pemerintah": "PP",
        "pp ": "PP",
        "perpres": "Perpres",
        "peraturan presiden": "Perpres",
        "permentan": "Permentan",
        "peraturan menteri pertanian": "Permentan",
        "permen atr": "Permen ATR/BPN",
        "peraturan menteri agraria": "Permen ATR/BPN",
    }

    TOPIK_KEYWORDS = {
        "sawit": "kelapa sawit",
        "kelapa sawit": "kelapa sawit",
        "hutan": "hutan",
        "kehutanan": "hutan",
        "izin": "izin usaha",
        "perizinan": "izin usaha",
        "hgu": "hak guna usaha",
        "hak guna usaha": "hak guna usaha",
        "lingkungan": "lingkungan",
        "amdal": "lingkungan",
        "tata ruang": "tata ruang",
        "lahan": "lahan",
        "tanah": "lahan",
        "sanksi": "sanksi",
        "pidana": "sanksi",
        "denda": "sanksi",
        "sertifikasi": "sertifikasi",
        "ispo": "sertifikasi",
        "bpdpks": "dana perkebunan",
        "peremajaan": "peremajaan",
        "replanting": "peremajaan",
        "petani": "petani",
        "plasma": "petani",
        "kemitraan": "petani",
        "pembukaan lahan": "pembukaan lahan",
        "land clearing": "pembukaan lahan",
    }

    @classmethod
    def extract_filters(cls, query: str) -> dict:
        """
        Extract metadata filters dari query user.
        
        Returns:
            dict with optional keys: jenis, topik, tahun_min, tahun_max
        """
        query_lower = query.lower()
        filters = {}

        # Deteksi jenis regulasi
        for keyword, jenis in cls.JENIS_KEYWORDS.items():
            if keyword in query_lower:
                filters["jenis"] = jenis
                break

        # Deteksi topik
        detected_topics = []
        for keyword, topik in cls.TOPIK_KEYWORDS.items():
            if keyword in query_lower:
                if topik not in detected_topics:
                    detected_topics.append(topik)
        if detected_topics:
            filters["topik"] = detected_topics

        # Deteksi tahun
        year_match = re.search(r"tahun\s+(\d{4})", query_lower)
        if year_match:
            filters["tahun"] = int(year_match.group(1))

        # Deteksi range tahun
        range_match = re.search(r"(\d{4})\s*[-–]\s*(\d{4})", query_lower)
        if range_match:
            filters["tahun_min"] = int(range_match.group(1))
            filters["tahun_max"] = int(range_match.group(2))

        return filters

    @classmethod
    def build_vector_where(cls, filters: dict) -> dict | None:
        """Convert filters ke format where clause untuk semantic search."""
        conditions = []

        if "jenis" in filters:
            conditions.append({"jenis": {"$eq": filters["jenis"]}})

        if "tahun" in filters:
            conditions.append({"tahun": {"$eq": filters["tahun"]}})

        if "tahun_min" in filters:
            conditions.append({"tahun": {"$gte": filters["tahun_min"]}})

        if "tahun_max" in filters:
            conditions.append({"tahun": {"$lte": filters["tahun_max"]}})

        if "topik" in filters:
            # Topik difilter dengan $contains, lalu diterjemahkan di vector_store
            topik_conditions = []
            for t in filters["topik"]:
                topik_conditions.append({"topik": {"$contains": t}})
            if len(topik_conditions) == 1:
                conditions.extend(topik_conditions)
            else:
                conditions.append({"$or": topik_conditions})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}


# ============================================================
# HYBRID RETRIEVER
# ============================================================

class HybridRetriever:
    """
    Hybrid Retrieval: menggabungkan semantic search + BM25.
    Dengan metadata filtering sebelum retrieval.
    """

    def __init__(self, chunks: list[dict] = None):
        self.bm25_index = BM25Index(chunks)
        self.chunks = chunks if chunks is not None else self.bm25_index.chunks
        self.metadata_filter = MetadataFilter()
        print("[OK] HybridRetriever initialized")

    def _normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _generate_query_phrases(self, query: str, min_words: int = 2, max_words: int = 4) -> list[str]:
        tokens = self._normalize_text(query).split()
        phrases = []
        seen = set()
        for size in range(max_words, min_words - 1, -1):
            if len(tokens) < size:
                continue
            for i in range(len(tokens) - size + 1):
                phrase = " ".join(tokens[i:i + size]).strip()
                if len(phrase) < 4:
                    continue
                if phrase in seen:
                    continue
                seen.add(phrase)
                phrases.append(phrase)
        return phrases

    def _query_boost(self, query: str, chunk_text: str, metadata: dict, filters: dict | None = None) -> float:
        query_norm = self._normalize_text(query)
        text_norm = self._normalize_text(chunk_text)

        query_tokens = [t for t in query_norm.split() if t not in INDONESIAN_STOPWORDS and len(t) > 1]
        if query_tokens:
            chunk_tokens = set(text_norm.split())
            overlap = len(set(query_tokens) & chunk_tokens) / len(set(query_tokens))
        else:
            overlap = 0.0

        phrase_boost = 0.0
        for phrase in self._generate_query_phrases(query):
            if phrase in text_norm:
                phrase_boost = max(phrase_boost, min(0.45, 0.10 * len(phrase.split())))

        meta_text = " ".join(
            str(metadata.get(k, "")) for k in ("dokumen", "jenis", "tahun", "pasal", "topik")
        ).lower()
        meta_boost = 0.0
        if filters:
            if filters.get("jenis") and str(metadata.get("jenis", "")).lower() == str(filters["jenis"]).lower():
                meta_boost += 0.10
            if filters.get("tahun") and int(metadata.get("tahun", 0)) == int(filters["tahun"]):
                meta_boost += 0.05
            if filters.get("topik"):
                chunk_topik = metadata.get("topik", [])
                if not isinstance(chunk_topik, list):
                    chunk_topik = [chunk_topik]
                if any(t in chunk_topik for t in filters["topik"]):
                    meta_boost += 0.12
        if query_norm and query_norm in meta_text:
            meta_boost += 0.08

        return min(1.0, (0.55 * overlap) + (0.30 * phrase_boost) + (0.15 * meta_boost))

    def _get_filtered_chunk_ids(self, filters: dict) -> list[str]:
        """
        Get list of chunk_ids yang match dengan metadata filters.
        
        Args:
            filters: dict dari metadata filters (e.g., {'jenis': 'UU', 'topik': ['hak guna usaha']})
        
        Returns:
            list of chunk_ids yang match
        """
        filtered_ids = []
        
        for chunk in self.chunks:
            meta = chunk.get("metadata", {})
            
            # Check jenis filter
            if "jenis" in filters:
                if meta.get("jenis") != filters["jenis"]:
                    continue
            
            # Check topik filter
            if "topik" in filters:
                chunk_topik = meta.get("topik", [])
                if not isinstance(chunk_topik, list):
                    chunk_topik = [chunk_topik]
                
                # Check apakah ada intersection antara filter topik dan chunk topik
                has_matching_topik = any(
                    t in chunk_topik for t in filters["topik"]
                )
                if not has_matching_topik:
                    continue
            
            # Check tahun filter
            if "tahun" in filters:
                if meta.get("tahun") != filters["tahun"]:
                    continue
            
            # Check tahun_min filter
            if "tahun_min" in filters:
                if (meta.get("tahun") or 0) < filters["tahun_min"]:
                    continue
            
            # Check tahun_max filter
            if "tahun_max" in filters:
                if (meta.get("tahun") or 0) > filters["tahun_max"]:
                    continue
            
            # If we reach here, chunk matches all filters
            filtered_ids.append(chunk.get("chunk_id"))
        
        return filtered_ids

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
        semantic_weight: float = SEMANTIC_WEIGHT,
        bm25_weight: float = BM25_WEIGHT,
        auto_filter: bool = True,
    ) -> list[dict]:
        """
        Hybrid retrieval dengan metadata filtering.
        
        Flow:
        1. Extract metadata filters dari query
        2. Semantic search (Qdrant) dengan filter
        3. BM25 keyword search
        4. Gabungkan skor (Reciprocal Rank Fusion)
        5. Return top_k hasil
        """
        # Step 1: metadata filtering
        filters = {}
        vector_where = None
        if auto_filter:
            filters = self.metadata_filter.extract_filters(query)
            vector_where = self.metadata_filter.build_vector_where(filters)
            if filters:
                print(f"  [INFO] Metadata filters: {filters}")

        # Step 2: Semantic search via Vector DB
        semantic_scores = {}
        semantic_docs = {}
        used_filter = False

        try:
            # Coba dengan filter dulu
            if vector_where:
                semantic_results = search_similar(
                    query,
                    n_results=top_k * 5,
                    where=vector_where,
                )
                # Cek apakah ada hasil
                if semantic_results["ids"] and semantic_results["ids"][0]:
                    used_filter = True
                    for chunk_id, doc, meta, dist in zip(
                        semantic_results["ids"][0],
                        semantic_results["documents"][0],
                        semantic_results["metadatas"][0],
                        semantic_results["distances"][0]
                    ):
                        sim_score = 1 - dist
                        semantic_scores[chunk_id] = sim_score
                        semantic_docs[chunk_id] = {"text": doc, "metadata": meta}
                else:
                    print("  [WARN] Metadata filter terlalu ketat, fallback tanpa filter")

            # Fallback tanpa filter jika filter tidak menghasilkan apa-apa
            if not semantic_scores:
                semantic_results = search_similar(
                    query,
                    n_results=top_k * 5,
                    where=None,
                )
                if semantic_results["ids"] and semantic_results["ids"][0]:
                    for chunk_id, doc, meta, dist in zip(
                        semantic_results["ids"][0],
                        semantic_results["documents"][0],
                        semantic_results["metadatas"][0],
                        semantic_results["distances"][0]
                    ):
                        sim_score = 1 - dist
                        semantic_scores[chunk_id] = sim_score
                        semantic_docs[chunk_id] = {"text": doc, "metadata": meta}
        except Exception as e:
            print(f"  [WARN] Semantic search error: {e}")
            semantic_scores = {}
            semantic_docs = {}

        # Step 3: BM25 search dengan fallback jika filter terlalu ketat
        bm25_chunk_ids = None
        if filters:
            # Get list of chunk_ids yang match dengan metadata filters
            bm25_chunk_ids = self._get_filtered_chunk_ids(filters)
            if bm25_chunk_ids:
                print(f"  [OK] BM25 filtering to {len(bm25_chunk_ids)} chunks matching {filters}")
            else:
                print(f"  [WARN] BM25 filter terlalu ketat, fallback tanpa filter")
                bm25_chunk_ids = None  # Fallback: search semua chunks
        
        bm25_results = self.bm25_index.search(
            query, top_k=top_k * 5, chunk_ids=bm25_chunk_ids
        )

        bm25_scores = {}
        bm25_docs = {}
        for r in bm25_results:
            bm25_scores[r["chunk_id"]] = r["score"]
            bm25_docs[r["chunk_id"]] = {
                "text": r["text"],
                "metadata": r["metadata"],
            }

        # Step 4: Reciprocal Rank Fusion (RRF) + lexical reranking boost
        all_chunk_ids = set(list(semantic_scores.keys()) + list(bm25_scores.keys()))

        # Normalize scores
        if semantic_scores:
            max_sem = max(semantic_scores.values())
            min_sem = min(semantic_scores.values())
            range_sem = max_sem - min_sem if max_sem != min_sem else 1
            norm_semantic = {k: (v - min_sem) / range_sem for k, v in semantic_scores.items()}
        else:
            norm_semantic = {}

        if bm25_scores:
            max_bm25 = max(bm25_scores.values())
            min_bm25 = min(bm25_scores.values())
            range_bm25 = max_bm25 - min_bm25 if max_bm25 != min_bm25 else 1
            norm_bm25 = {k: (v - min_bm25) / range_bm25 for k, v in bm25_scores.items()}
        else:
            norm_bm25 = {}

        # Final ranking score = hybrid base + lexical boost
        hybrid_scores = {}
        query_boosts = {}
        for cid in all_chunk_ids:
            doc_data = semantic_docs.get(cid) or bm25_docs.get(cid)
            if not doc_data:
                continue
            sem = norm_semantic.get(cid, 0.0)
            bm = norm_bm25.get(cid, 0.0)
            lexical_boost = self._query_boost(query, doc_data["text"], doc_data["metadata"], filters)
            query_boosts[cid] = lexical_boost
            hybrid_scores[cid] = (semantic_weight * sem) + (bm25_weight * bm) + (0.35 * lexical_boost)

        # Sort by hybrid score
        sorted_ids = sorted(hybrid_scores.keys(), key=lambda x: hybrid_scores[x], reverse=True)
        sorted_ids = sorted_ids[:top_k]

        # Step 5: Assemble results
        results = []
        for cid in sorted_ids:
            doc_data = semantic_docs.get(cid) or bm25_docs.get(cid)
            if doc_data:
                results.append({
                    "chunk_id": cid,
                    "text": doc_data["text"],
                    "metadata": doc_data["metadata"],
                        "lexical_boost": query_boosts.get(cid, 0.0),
                    "scores": {
                        "hybrid": hybrid_scores[cid],
                        "semantic": semantic_scores.get(cid, 0.0),
                        "bm25": bm25_scores.get(cid, 0.0),
                        "semantic_norm": norm_semantic.get(cid, 0.0),
                        "bm25_norm": norm_bm25.get(cid, 0.0),
                    },
                })

        return results


# ============================================================
# SINGLETON
# ============================================================

_retriever = None

def get_retriever() -> HybridRetriever:
    """Get global HybridRetriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


# ============================================================
# MAIN — Test
# ============================================================

if __name__ == "__main__":
    retriever = get_retriever()

    test_queries = [
        "Apakah boleh membuka lahan sawit di kawasan hutan?",
        "Apa sanksi pelanggaran izin usaha perkebunan?",
        "Bagaimana aturan sertifikasi ISPO?",
        "Peraturan pemerintah tentang peremajaan kelapa sawit",
        "UU tentang perlindungan lingkungan hidup",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        results = retriever.retrieve(query, top_k=5)

        for i, r in enumerate(results):
            meta = r["metadata"]
            scores = r["scores"]
            # Handle topik yang bisa berupa list atau string
            topik = meta.get("topik", "")
            if isinstance(topik, list):
                topik = ", ".join(topik)
            print(f"\n  [{i+1}] Hybrid: {scores['hybrid']:.4f} "
                  f"(sem: {scores['semantic']:.4f}, bm25: {scores['bm25']:.2f})")
            print(f"      Doc: {meta.get('dokumen', 'N/A')} | {meta.get('pasal', 'N/A')}")
            print(f"      Topik: {topik}")
            print(f"      Text: {r['text'][:150]}...")
