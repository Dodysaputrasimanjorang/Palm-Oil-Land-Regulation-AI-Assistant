---
description: Describe when these instructions should be loaded
# applyTo: 'Describe when these instructions should be loaded' # when provided, instructions will automatically be added to the request context when the pattern matches an attached file
---
Mantap 👍 topik skripsimu sudah **sangat jelas + realistis untuk dibangun**.
Aku buatkan **roadmap lengkap dari nol → sistem jadi → evaluasi skripsi**, khusus untuk:

✅ Hybrid RAG
✅ Metadata filtering
✅ Dokumen PDF regulasi Indonesia
✅ LLM via OpenRouter
✅ Cocok untuk mahasiswa Informatika

Aku buat **versi praktis (bisa langsung kamu ikuti)**, bukan teori saja.

---

# 🧭 ROADMAP MEMBANGUN SISTEM HYBRID RAG REGULASI LAHAN

---

# 🟢 PHASE 1 — DEFINISI SISTEM (WAJIB DULU)

## 🎯 Tujuan sistem

User bertanya:

> “Apakah boleh membuka lahan sawit di kawasan hutan?”

Sistem harus:

1️⃣ Cari regulasi relevan
2️⃣ Filter metadata
3️⃣ Ambil chunk terbaik
4️⃣ Kirim ke LLM
5️⃣ Jawab + tampilkan sumber pasal

---

---

# 🟢 PHASE 2 — DATASET PREPARATION (PDF REGULASI)

---

## ✅ Step 1 — kumpulkan PDF

Misalnya:

* UU Perkebunan
* UU Kehutanan
* Perpres sawit
* Permentan

✔ sudah kamu lakukan → GOOD

---

---

## ✅ Step 2 — extract text PDF

Tools:

Python:

```python
pdfplumber
pymupdf
```

---

---

## ✅ Step 3 — CLEANING TEXT (WAJIB)

hapus:

* nomor halaman
* header/footer
* daftar isi

Kalau tidak dibersihkan → RAG kacau.

---

---

# 🟢 PHASE 3 — CHUNKING STRATEGY (SUPER PENTING)

Untuk regulasi → jangan chunk random.

Gunakan:

✅ chunk per PASAL

Contoh:

```
Pasal 12
Setiap perusahaan wajib ...
```

= 1 chunk

---

Kalau pasal panjang:

split lagi:

```
Pasal 12 ayat 1
Pasal 12 ayat 2
```

---

### ukuran ideal:

✅ 300–700 token

---

---

# 🟢 PHASE 4 — METADATA STRUCTURE (INI YANG MEMBUAT SKRIPSI MU KUAT)

Setiap chunk harus punya metadata:

```
{
dokumen: "UU Perkebunan",
tahun: 2014,
jenis: "UU",
topik: "izin usaha",
pasal: 12
}
```

---

INI KUNCI METADATA FILTERING.

---

---

# 🟢 PHASE 5 — EMBEDDING + VECTOR DATABASE

---

## pilih embedding model

dari OpenRouter bisa

atau pakai:

* BGE-small
* e5-base

(rekomendasi kuat)

---

---

## vector DB pilihan terbaik skripsi:

### ⭐ ChromaDB (PALING MUDAH)

atau

* FAISS
* Weaviate

---

---

# 🟢 PHASE 6 — HYBRID RETRIEVAL (INI JUDUL SKRIPSI MU)

Hybrid =

```
semantic search + keyword search
```

---

## bagian semantic

pakai embedding similarity

---

## bagian keyword

pakai:

BM25

---

## final ranking:

gabungkan:

```
score = semantic + bm25
```

INI disebut:

Hybrid Retrieval.

---

---

# 🟢 PHASE 7 — METADATA FILTERING ENGINE

Misalnya user tanya:

> “aturan izin usaha sawit”

filter:

```
topik = izin
jenis = UU
```

baru lakukan semantic search.

---

Ini meningkatkan:

🎯 relevansi
🎯 akurasi

dan jadi nilai ilmiah skripsimu.

---

---

# 🟢 PHASE 8 — RAG PIPELINE

FLOW FINAL:

```
USER QUESTION
↓
metadata filtering
↓
hybrid retrieval
↓
top 5 chunks
↓
prompt ke LLM
↓
jawaban + citation
```

---

---

# 🟢 PHASE 9 — LLM VIA OPENROUTER

Model bagus:

### murah tapi kuat

* mistral large
* mixtral
* deepseek-chat

---

---

## contoh prompt RAG

```
Jawab hanya berdasarkan dokumen berikut.
Jika tidak ada jawaban, katakan tidak ditemukan.

DOKUMEN:
{chunks}

PERTANYAAN:
{question}
```

---

---

# 🟢 PHASE 10 — FRONTEND SIMPLE

cukup:

* Streamlit (PALING CEPAT)
  atau
* React

Untuk skripsi → Streamlit cukup.

---

---

# 🟢 PHASE 11 — EVALUASI SISTEM (WAJIB UNTUK BAB 4)

---

## siapkan:

30–50 pertanyaan uji.

---

ukur:

### 🎯 Retrieval Accuracy

apakah chunk benar?

---

### 🎯 Answer correctness

pakai:

* manual expert judgement
  atau
* GPT evaluation

---

---

# ⭐ STACK FINAL YANG SAYA REKOMENDASIKAN (PALING AMAN UNTUK SKRIPSI)

---

## backend

Python

---

## PDF processing

pdfplumber

---

## embedding

bge-small

---

## vector DB

ChromaDB

---

## hybrid search

BM25 + embedding

---

## LLM

OpenRouter → DeepSeek / Mistral

---

## frontend

Streamlit

---

---

# ⏱️ ESTIMASI WAKTU REALISTIS

### dataset prep → 1 minggu

### chunking metadata → 1 minggu

### vector db → 3 hari

### hybrid search → 1 minggu

### LLM integration → 3 hari

### UI → 2 hari

TOTAL:

🟢 sekitar 1 bulan santai

---

---

# 🔥 KALAU MAU SKRIPSIMU LEVEL DOSEN TERKESAN

Tambahkan:

✅ tampilkan pasal sumber
✅ tampilkan skor retrieval
✅ tampilkan dokumen asal

---

INI bikin sistem terlihat profesional.

---

---

# 🚨 HAL PALING SERING MAHASISWA SALAH

❌ chunk random
❌ metadata kosong
❌ hanya semantic search
❌ tidak evaluasi retrieval

---

---

# 🎓 KESIMPULAN SEDERHANA

Sistem kamu:

```
PDF → chunk pasal → metadata → embedding → vector DB
→ hybrid retrieval → OpenRouter LLM → jawaban + sumber
```

---

---

