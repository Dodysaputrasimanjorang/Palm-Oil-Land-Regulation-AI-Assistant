"""
Script utama untuk menjalankan seluruh pipeline dari nol.
Urutan: Extract PDF → Chunk → Index → Siap digunakan

Jalankan: python run_pipeline.py
"""

import sys
import time
from pathlib import Path


def main():
    start_total = time.time()

    print("=" * 70)
    print("🚀 HYBRID RAG REGULASI LAHAN — FULL PIPELINE")
    print("=" * 70)

    # ==========================================
    # STEP 1: Extract PDF
    # ==========================================
    print("\n" + "=" * 70)
    print("📄 STEP 1: Extracting text from PDFs...")
    print("=" * 70)
    from src.pdf_extractor import extract_all_pdfs
    extracted = extract_all_pdfs()
    print(f"✅ Extracted {len(extracted)} documents")

    # ==========================================
    # STEP 2: Chunking
    # ==========================================
    print("\n" + "=" * 70)
    print("📦 STEP 2: Chunking documents by pasal...")
    print("=" * 70)
    from src.chunker import chunk_all_documents
    chunks = chunk_all_documents(extracted)
    print(f"✅ Created {len(chunks)} chunks")

    # ==========================================
    # STEP 3: Index to Qdrant
    # ==========================================
    print("\n" + "=" * 70)
    print("🧠 STEP 3: Embedding & indexing to Qdrant...")
    print("=" * 70)
    from src.vector_store import index_chunks
    indexed_count = index_chunks(chunks, reset=True)
    print(f"✅ Indexed {indexed_count} chunks")

    # ==========================================
    # DONE
    # ==========================================
    elapsed = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"🎉 PIPELINE SELESAI dalam {elapsed:.1f} detik!")
    print("=" * 70)
    print(f"""
Langkah selanjutnya:
  1. Pastikan OPENROUTER_API_KEY dan OPENROUTER_MODEL sudah diset di file .env
  2. Jalankan aplikasi: streamlit run app.py
  3. Atau jalankan evaluasi: python evaluation.py
    """)


if __name__ == "__main__":
    main()
