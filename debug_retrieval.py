#!/usr/bin/env python3
"""
Script debugging untuk diagnosa masalah retrieval tidak menemukan jawaban.
Fokus pada contoh: "Apa saja syarat untuk mendapatkan HGU?"
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import CHUNKS_FILE, TOP_K
from src.hybrid_retriever import BM25Index, MetadataFilter, HybridRetriever, search_similar
from src.vector_store import search_similar as vec_search

# ============================================================
# 1. CHECK CHUNKS
# ============================================================

def check_chunks():
    """Cek apakah chunks.json ada dan valid."""
    print("\n" + "="*80)
    print("1. CHECKING CHUNKS.JSON")
    print("="*80)
    
    if not CHUNKS_FILE.exists():
        print(f"[ERROR] File tidak ditemukan: {CHUNKS_FILE}")
        return None
    
    try:
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except Exception as e:
        print(f"[ERROR] Error membaca chunks.json: {e}")
        return None
    
    print(f"[OK] Chunks loaded: {len(chunks)} chunks total")
    
    # Analisis chunks
    if chunks:
        c = chunks[0]
        print(f"\nSample chunk (first):")
        print(f"  - chunk_id: {c.get('chunk_id')}")
        print(f"  - text preview: {c.get('text', '')[:100]}...")
        print(f"  - metadata: {c.get('metadata')}")
    
    # Cek topik
    topik_counts = {}
    jenis_counts = {}
    for c in chunks:
        meta = c.get("metadata", {})
        topik = meta.get("topik", "")
        jenis = meta.get("jenis", "")
        
        if isinstance(topik, list):
            for t in topik:
                topik_counts[t] = topik_counts.get(t, 0) + 1
        elif topik:
            topik_counts[topik] = topik_counts.get(topik, 0) + 1
        
        if jenis:
            jenis_counts[jenis] = jenis_counts.get(jenis, 0) + 1
    
    print(f"\nTopik tersedia:")
    for topik, count in sorted(topik_counts.items()):
        print(f"  - {topik}: {count} chunks")
    
    print(f"\nJenis regulasi:")
    for jenis, count in sorted(jenis_counts.items()):
        print(f"  - {jenis}: {count} chunks")
    
    # Search untuk keyword "HGU" atau "syarat" di chunks
    hgu_chunks = []
    syarat_chunks = []
    for c in chunks:
        text_lower = c.get("text", "").lower()
        if "hgu" in text_lower:
            hgu_chunks.append(c)
        if "syarat" in text_lower:
            syarat_chunks.append(c)
    
    print(f"\n[INFO] Keyword analysis:")
    print(f"  - Chunks mengandung 'HGU': {len(hgu_chunks)}")
    print(f"  - Chunks mengandung 'syarat': {len(syarat_chunks)}")
    
    if hgu_chunks:
        print(f"\n[OK] Sample chunk dengan 'HGU':")
        c = hgu_chunks[0]
        print(f"  - Dokumen: {c['metadata'].get('dokumen')}")
        print(f"  - Pasal: {c['metadata'].get('pasal')}")
        print(f"  - Text: {c['text'][:150]}...")
    
    return chunks


# ============================================================
# 2. CHECK METADATA FILTERING
# ============================================================

def check_metadata_filtering(question: str = "Apa saja syarat untuk mendapatkan HGU?"):
    """Cek bagaimana metadata filtering mengekstrak filter dari question."""
    print("\n" + "="*80)
    print("2. CHECKING METADATA FILTERING")
    print("="*80)
    
    print(f"Question: {question}")
    
    filters = MetadataFilter.extract_filters(question)
    print(f"\nExtracted filters: {filters}")
    
    vector_where = MetadataFilter.build_vector_where(filters)
    print(f"Vector where clause: {vector_where}")
    
    # Cek keyword detection
    print(f"\nKeyword analysis:")
    q_lower = question.lower()
    print(f"  - Contains 'hgu': {'hgu' in q_lower}")
    print(f"  - Contains 'syarat': {'syarat' in q_lower}")
    print(f"  - Contains 'lahan': {'lahan' in q_lower}")
    print(f"  - Contains 'izin': {'izin' in q_lower}")


# ============================================================
# 3. CHECK SEMANTIC SEARCH
# ============================================================

def check_semantic_search(question: str = "Apa saja syarat untuk mendapatkan HGU?"):
    """Cek semantic search menggunakan vector DB."""
    print("\n" + "="*80)
    print("3. CHECKING SEMANTIC SEARCH (Vector DB)")
    print("="*80)
    
    print(f"Question: {question}")
    print(f"Searching without filter (top 10)...")
    
    try:
        results = search_similar(question, n_results=10, where=None)
        
        if not results or not results.get("ids") or not results["ids"][0]:
            print("[ERROR] Semantic search returned empty results")
            return
        
        print(f"[OK] Found {len(results['ids'][0])} results")
        
        for i, (chunk_id, doc, meta, dist) in enumerate(zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )):
            sim_score = 1 - dist
            print(f"\n  Rank {i+1}:")
            print(f"    - chunk_id: {chunk_id}")
            print(f"    - similarity: {sim_score:.4f}")
            print(f"    - dokumen: {meta.get('dokumen')}")
            print(f"    - pasal: {meta.get('pasal')}")
            print(f"    - preview: {doc[:80]}...")
    
    except Exception as e:
        print(f"[ERROR] Semantic search error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================
# 4. CHECK BM25 SEARCH
# ============================================================

def check_bm25_search(chunks, question: str = "Apa saja syarat untuk mendapatkan HGU?"):
    """Cek BM25 keyword search."""
    print("\n" + "="*80)
    print("4. CHECKING BM25 KEYWORD SEARCH")
    print("="*80)
    
    print(f"Question: {question}")
    
    bm25_index = BM25Index(chunks)
    results = bm25_index.search(question, top_k=10)
    
    if not results:
        print("[ERROR] BM25 search returned empty results")
        return
    
    print(f"[OK] Found {len(results)} results")
    
    for i, r in enumerate(results):
        print(f"\n  Rank {i+1}:")
        print(f"    - chunk_id: {r['chunk_id']}")
        print(f"    - BM25 score: {r['score']:.4f}")
        print(f"    - dokumen: {r['metadata'].get('dokumen')}")
        print(f"    - pasal: {r['metadata'].get('pasal')}")
        print(f"    - preview: {r['text'][:80]}...")
    
    # Cek tokenization
    print(f"\nTokenization test:")
    tokens = bm25_index._tokenize(question)
    print(f"  Tokens: {tokens}")


# ============================================================
# 5. CHECK FULL HYBRID RETRIEVE
# ============================================================

def check_full_retrieval(chunks, question: str = "Apa saja syarat untuk mendapatkan HGU?"):
    """Cek full hybrid retrieval pipeline."""
    print("\n" + "="*80)
    print("5. CHECKING FULL HYBRID RETRIEVAL")
    print("="*80)
    
    print(f"Question: {question}")
    
    retriever = HybridRetriever(chunks)
    results = retriever.retrieve(question, top_k=TOP_K, auto_filter=True)
    
    if not results:
        print("[ERROR] Hybrid retrieval returned empty results")
        return
    
    print(f"[OK] Found {len(results)} results after RRF fusion")
    
    for i, r in enumerate(results[:5]):  # Show top 5
        print(f"\n  Rank {i+1}:")
        print(f"    - chunk_id: {r['chunk_id']}")
        print(f"    - hybrid score: {r['scores'].get('hybrid', 0):.4f}")
        print(f"    - semantic: {r['scores'].get('semantic', 0):.4f}")
        print(f"    - bm25: {r['scores'].get('bm25', 0):.4f}")
        print(f"    - dokumen: {r['metadata'].get('dokumen')}")
        print(f"    - pasal: {r['metadata'].get('pasal')}")
        print(f"    - text: {r['text'][:100]}...")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n" + "DEBUGGING RETRIEVAL SYSTEM" + "\n")
    print(f"Working directory: {Path.cwd()}")
    print(f"CHUNKS_FILE: {CHUNKS_FILE}")
    
    # 1. Check chunks
    chunks = check_chunks()
    if not chunks:
        print("\n[FATAL] Chunks not available. Cannot continue.")
        sys.exit(1)
    
    # 2. Check metadata filtering
    check_metadata_filtering()
    
    # 3. Check semantic search
    check_semantic_search()
    
    # 4. Check BM25 search
    check_bm25_search(chunks)
    
    # 5. Check full retrieval
    check_full_retrieval(chunks)
    
    print("\n" + "="*80)
    print("DEBUG COMPLETE")
    print("="*80)
