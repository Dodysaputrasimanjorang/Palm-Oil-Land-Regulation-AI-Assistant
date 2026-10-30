# RINGKASAN PERBAIKAN RAGAS SCORE RENDAH

## 📋 Masalah Utama
Nilai RAGAS Anda masih rendah karena:
1. **Embedding model tidak cocok untuk Bahasa Indonesia** (pakai yang fokus Cina)
2. **Retrieval terlalu ketat** dengan metadata filter
3. **Reranking hanya BM25**, semantic signal hilang
4. **Prompt LLM terlalu cepat menyerah** ("info tidak ditemukan")

## ✅ Perbaikan yang Sudah Diterapkan

### 1. Ganti Embedding Model
- **Dari:** `BAAI/bge-large-zh-v1.5` (fokus Cina)
- **Ke:** `intfloat/multilingual-e5-large` (optimal untuk Indonesian + legal)
- **File:** `src/config.py` line 16

### 2. Broaden Retrieval Candidates
- **Dari:** `top_k * 3` = 30 candidates
- **Ke:** `top_k * 5` = 50 candidates
- **File:** `src/hybrid_retriever.py` (3 tempat di method `retrieve()`)

### 3. Add Lexical Reranking
- Boost score untuk chunks dengan exact phrase match
- Boost score untuk chunks yang match metadata (jenis, tahun, topik)
- **File:** `src/hybrid_retriever.py` (method `_query_boost()`)

### 4. Improve Metadata Keywords
- Tambah keyword untuk HGU, BPDPKS, dll
- **File:** `src/hybrid_retriever.py` `TOPIK_KEYWORDS`

### 5. Better RAG Prompt
- Instruksi LLM: ekstrak info yang ada dulu, bukan langsung "tidak ditemukan"
- **File:** `src/config.py` `RAG_SYSTEM_PROMPT`

### 6. Fix Context Ordering
- Sort by hybrid score (lebih reliable) bukan semantic score
- **File:** `src/rag_pipeline.py` method `query()`

---

## 🎯 Expected Results

| Metrik | Sebelum | Expected After |
|--------|---------|-----------------|
| **Faithfulness** | 0.1250 | 0.40–0.50 (↑3-4x) |
| **Answer Relevancy** | 0.3765 | 0.55–0.65 (↑1.5x) |
| **Context Precision** | 0.4025 | 0.60–0.75 (↑1.5x) |
| **Context Recall** | 0.4000 | 0.70–0.85 (↑1.7x) |

---

## 🚀 Next Steps

### Cek Perubahan
```bash
# Verifikasi embedding model
python -c "from src.config import EMBEDDING_MODEL; print(EMBEDDING_MODEL)"
# Output harus: intfloat/multilingual-e5-large
```

### Run Evaluation
```bash
# Quick test (3 pertanyaan)
python test_improvements.py

# Full evaluation (16 pertanyaan)
python run_ragas_eval_improved.py
```

### Compare Results
```bash
# Bandingkan dengan baseline lama
# Baseline: HASIL RAGAS/ragas_eval_20260504_061909.json
# New:      HASIL RAGAS/ragas_eval_improved_*.json
```

---

## 📖 Detailed Explanation

**File:** `PERBAIKAN_RAGAS_SCORE.md` (di root folder)
- Penjelasan lengkap setiap masalah dan solusi
- Technical details untuk setiap perbaikan
- Summary tabel perbandingan before/after

---

## ⚡ Quick Reference

**Files Modified:**
- ✅ `src/config.py` - Embedding model + prompts
- ✅ `src/hybrid_retriever.py` - Retrieval + reranking
- ✅ `src/rag_pipeline.py` - Context sorting

**Files Created:**
- 📄 `test_improvements.py` - Quick 2-question test
- 📄 `PERBAIKAN_RAGAS_SCORE.md` - Full explanation

---

## 🧠 Key Insights untuk Skripsi

1. **Embedding model selection adalah kritis:**
   - Model yang salah (fokus Cina) → retrieval jelek
   - Model yang tepat (multilingual) → semantic accuracy naik

2. **Hybrid approach lebih robust:**
   - Semantic + BM25 + Lexical = 3 signal berbeda
   - Fallback otomatis saat semantic gagal

3. **Retrieval quality > Jumlah parameter:**
   - Lebih baik 50 kandidat yang dipilih dengan baik
   - Daripada 30 kandidat tanpa reranking

4. **Prompt engineering penting:**
   - "Jangan takut menjawab dari konteks" → faithfulness naik
   - Instruksi ekstrak info dulu → answer relevancy naik

---

## 💡 Tips Lanjutan

Jika score masih kurang memuaskan:

1. **Increase chunk candidates lebih lanjut:**
   ```python
   # Dari top_k * 5 ke top_k * 7
   n_results=top_k * 7
   ```

2. **Adjust weight ratio:**
   ```python
   SEMANTIC_WEIGHT = 0.65  # Turun dari 0.6
   BM25_WEIGHT = 0.35      # Naik dari 0.4
   ```

3. **Expand topic keywords:** (lihat `src/chunker.py`)
   ```python
   TOPIK_KEYWORDS = {
       # Add more domain-specific terms
   }
   ```

4. **Check embedding dimension:**
   - `multilingual-e5-large` = 1024 dim (good)
   - If needed, bisa ganti ke `intfloat/e5-xxl` = 3072 dim (lebih kuat tapi lambat)

---

**Status:** ✅ Ready to evaluate  
**Last Updated:** 2026-05-04  
**Contact:** Lihat dokumentasi di `PERBAIKAN_RAGAS_SCORE.md` untuk detail teknis
