"""
Konfigurasi utama sistem Hybrid RAG Regulasi Lahan.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# === PATHS ===
BASE_DIR = Path(__file__).parent.parent  # Project root (parent of src/)
PDF_DIR = BASE_DIR / "UU"
DATA_DIR = BASE_DIR / "data"
RAGAS_RESULTS_DIR = BASE_DIR / "HASIL RAGAS"
CHUNKS_FILE = DATA_DIR / "chunks.json"
QDRANT_PATH = BASE_DIR / os.getenv("QDRANT_PATH", "qdrant_db")

# === PDF EXTRACTION ===
PDF_EXTRACTION_METHOD = "pdfplumber"  # "pdfplumber" or "pymupdf"

# === CHUNKING ===
MIN_CHUNK_TOKENS = 50
MAX_CHUNK_TOKENS = 700
OVERLAP_SENTENCES = 1

# === EMBEDDING ===
# Model multilingual untuk Bahasa Indonesia dan regulasi
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"

# === VECTOR DB ===
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "regulasi_lahan")

# === HYBRID SEARCH ===
# Optimized weights: Turun semantic, naik BM25 untuk legal domain
# Legal docs sering menggunakan nomenclature spesifik (pasal, nomor UU, dll)
SEMANTIC_WEIGHT = 0.6  # Turun dari 0.7
BM25_WEIGHT = 0.4      # Naik dari 0.3 (keyword matching penting untuk legal)
TOP_K = 15             # Naikkan dari 10 untuk konteks lebih komprehensif

# === LLM (OpenRouter API) ===
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Hybrid-RAG-Regulasi-Lahan")
LLM_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 2048
LLM_TIMEOUT_SECONDS = int(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "120"))

# === RAG PROMPT ===
RAG_SYSTEM_PROMPT = """Kamu adalah asisten hukum yang ahli dalam regulasi pertanahan dan perkebunan di Indonesia.

ATURAN WAJIB:
1. Jawab pertanyaan HANYA berdasarkan dokumen yang diberikan di bawah.
2. JANGAN pernah menyebutkan pasal atau undang-undang yang TIDAK ADA dalam dokumen yang diberikan.
3. Saat merujuk sumber, gunakan PERSIS nama dokumen dan pasal yang tertera di tag [Sumber: ...] pada setiap dokumen.
4. Format referensi: sebutkan nama lengkap dokumen dan pasal, contoh: "Berdasarkan Pasal 12 UU No. 39 Tahun 2014 tentang Perkebunan..."
5. Jika informasi SPESIFIK tidak ditemukan dalam dokumen, jawab dengan jujur: "Informasi spesifik mengenai [topik] tidak ditemukan dalam dokumen yang tersedia. Pertanyaan ini memerlukan penelitian lebih lanjut dengan akses ke regulasi terkait."
6. Prioritaskan dokumen yang paling relevan dengan pertanyaan.
7. Mulai jawaban dengan satu kalimat yang menjawab inti pertanyaan secara langsung.
8. Jangan menambahkan pembahasan, definisi, atau dokumen yang tidak diperlukan untuk menjawab pertanyaan.
9. Jika jawaban hanya sebagian ditemukan, jelaskan bagian yang ditemukan dan bagian yang tidak ditemukan secara singkat."""

RAG_USER_PROMPT_TEMPLATE = """Berdasarkan dokumen regulasi berikut, jawab pertanyaan di bawah.

PENTING:
- Hanya gunakan informasi dari dokumen di bawah ini.
- Jangan mengarang pasal atau undang-undang yang tidak ada dalam dokumen.
- Fokus pada pertanyaan, jangan melebar ke topik lain.
- Gunakan format:
  Jawaban singkat: [jawaban langsung 1 kalimat]
  Dasar dokumen: [2-4 poin paling relevan dengan sumber]

DOKUMEN REGULASI:
{context}

PERTANYAAN:
{question}

JAWABAN (cantumkan HANYA pasal dan dokumen yang ada di atas, gunakan nama dokumen persis seperti di tag [Sumber]):"""

# === Pastikan direktori data ada ===
DATA_DIR.mkdir(exist_ok=True)
RAGAS_RESULTS_DIR.mkdir(exist_ok=True)
