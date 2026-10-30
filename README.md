# 📜 Hybrid RAG Regulasi Lahan

Sistem Tanya-Jawab Regulasi Pertanahan & Perkebunan Indonesia berbasis **Hybrid RAG** (Retrieval-Augmented Generation) dengan **Metadata Filtering**.

## 🎯 Fitur Utama

- **Hybrid Retrieval**: Gabungan BM25 (keyword) + Semantic Search (embedding)
- **Metadata Filtering**: Filter otomatis berdasarkan jenis regulasi, topik, dan tahun
- **29 PDF Regulasi**: UU, PP, Perpres, Permentan, Permen ATR/BPN
- **Chunking per Pasal**: Setiap chunk = 1 pasal (bukan random)
- **LLM via OpenRouter API**: Gemini 2.5 Flash Lite untuk generate jawaban
- **Citation/Sumber**: Setiap jawaban menyertakan referensi pasal & dokumen

## 🏗️ Arsitektur

```
User Question
    ↓
Metadata Filtering (jenis, topik, tahun)
    ↓
Hybrid Retrieval (BM25 + Semantic)
    ↓
Top K Chunks
    ↓
RAG Prompt → LLM (OpenRouter)
    ↓
Jawaban + Sumber Pasal
```

## 📁 Struktur Proyek

```
SKIRPSI/
├── UU/                    # 29 PDF regulasi
├── data/                  # Data hasil processing
│   ├── extracted_texts.json
│   ├── chunks.json
│   └── evaluation_*.json
├── qdrant_db/             # Qdrant vector database
├── config.py              # Konfigurasi utama
├── pdf_extractor.py       # Phase 2-3: Extract + clean PDF
├── chunker.py             # Phase 4-5: Chunking + metadata
├── vector_store.py        # Phase 6: Embedding + Qdrant
├── hybrid_retriever.py    # Phase 7-8: Hybrid search + filter
├── rag_pipeline.py        # Phase 9: RAG + LLM
├── app.py                 # Phase 10: Streamlit UI
├── evaluation.py          # Phase 11: Evaluasi
├── run_pipeline.py        # Jalankan semua dari nol
└── requirements.txt       # Dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Jalankan Pipeline

```bash
python run_pipeline.py
```

### 3. Setup OpenRouter

Buat API key di OpenRouter, lalu atur `.env`:

```
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.5-flash-lite
OPENROUTER_TIMEOUT_SECONDS=120
OPENROUTER_SITE_URL=http://localhost:5000
OPENROUTER_APP_NAME=Hybrid-RAG-Regulasi-Lahan
```

### 4. Jalankan Aplikasi

```bash
streamlit run app.py
```

### 5. Evaluasi

```bash
python evaluation.py
```

### 6. Evaluasi RAGAS (via Website/API)

- Buka website, lalu gunakan panel **Evaluasi RAGAS** di sidebar.
- Atur jumlah sampel, klik **Jalankan Evaluasi**.
- Hasil ringkasan + detail tampil di halaman, dan file hasil tersimpan otomatis ke `data/`.

Endpoint API:

```bash
POST /api/eval/ragas
{
    "sample_size": 5,
    "top_k": 10,
    "auto_filter": true
}
```

## 📊 Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| PDF Processing | pdfplumber |
| Embedding | multilingual-e5-small |
| Vector DB | Qdrant |
| Keyword Search | BM25 (rank-bm25) |
| LLM | Gemini 2.5 Flash Lite via OpenRouter API |
| Frontend | Streamlit |
| Bahasa | Python 3.11+ |

## 📈 Hasil Evaluasi

Perbandingan 3 metode retrieval pada 30 pertanyaan uji:

| Metode | Topic Hit Rate | Doc Hit Rate | Jenis Match |
|--------|---------------|-------------|-------------|
| **Hybrid** | 0.1167 | **0.4000** | 0.1333 |
| Semantic | 0.1167 | 0.4000 | 0.1333 |
| BM25 | 0.1000 | 0.3667 | 0.1333 |

## 📝 Contoh Pertanyaan

- "Apakah boleh membuka lahan sawit di kawasan hutan?"
- "Apa sanksi jika melanggar izin usaha perkebunan?"
- "Bagaimana prosedur sertifikasi ISPO kelapa sawit?"
- "Apa saja syarat untuk mendapatkan HGU?"
- "Bagaimana aturan peremajaan tanaman kelapa sawit?"

## 📚 Dokumen Regulasi (29 PDF)

- UU No. 39/2014 (Perkebunan)
- UU No. 41/1999 (Kehutanan)
- UU No. 32/2009 (Lingkungan Hidup)
- UU No. 26/2007 (Penataan Ruang)
- UU No. 6/2023 (Cipta Kerja)
- PP No. 16/2004 (Penatagunaan Tanah)
- Perpres No. 44/2020 (Sertifikasi ISPO)
- Dan 22 regulasi lainnya







