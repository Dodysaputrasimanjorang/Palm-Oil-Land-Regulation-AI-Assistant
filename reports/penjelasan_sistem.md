# Penjelasan Sistem Website Hybrid RAG — Regulasi Pertanahan & Perkebunan Indonesia

---

## Daftar Isi

1. [Gambaran Umum Sistem](#1-gambaran-umum-sistem)
2. [Arsitektur & Tech Stack](#2-arsitektur--tech-stack)
3. [Penjelasan Sidebar](#3-penjelasan-sidebar)
4. [Penjelasan Halaman Utama (Main Content)](#4-penjelasan-halaman-utama-main-content)
5. [Database yang Digunakan](#5-database-yang-digunakan)
6. [Alur Proses Sistem (Pipeline)](#6-alur-proses-sistem-pipeline)
7. [Penentuan Top-K](#7-penentuan-top-k)
8. [Penjelasan Hybrid Search](#8-penjelasan-hybrid-search)
9. [Metadata Filtering](#9-metadata-filtering)
10. [Evaluasi Sistem](#10-evaluasi-sistem)

---

## 1. Gambaran Umum Sistem

Sistem ini adalah **website tanya-jawab hukum** berbasis **Hybrid Retrieval-Augmented Generation (RAG)** yang dirancang untuk menjawab pertanyaan seputar **regulasi pertanahan dan perkebunan di Indonesia**. Sistem menggabungkan pencarian semantik (embedding similarity) dan pencarian keyword (BM25) untuk menemukan pasal-pasal regulasi yang relevan, kemudian mengirimkan konteks tersebut ke LLM (Large Language Model) untuk menghasilkan jawaban hukum yang akurat beserta referensi sumber pasal.

**Contoh penggunaan:**
> Pengguna bertanya: *"Apakah boleh membuka lahan sawit di kawasan hutan?"*
>
> Sistem akan:
> 1. Mencari regulasi yang relevan melalui hybrid search
> 2. Memfilter berdasarkan metadata (topik, jenis regulasi)
> 3. Mengambil chunk/pasal terbaik
> 4. Mengirim konteks ke LLM
> 5. Menampilkan jawaban beserta sumber pasal yang dirujuk

---

## 2. Arsitektur & Tech Stack

| Komponen | Teknologi | Keterangan |
|---|---|---|
| **Backend** | Flask (Python) | REST API server |
| **Frontend** | HTML + CSS + JavaScript (Vanilla) | Single Page Application |
| **Database Vektor** | ChromaDB | Penyimpanan embedding untuk semantic search |
| **Keyword Search** | BM25 (rank_bm25) | Pencarian berbasis kata kunci |
| **Embedding Model** | `intfloat/multilingual-e5-small` | Model embedding multilingual, optimal untuk Bahasa Indonesia |
| **LLM** | Google Gemini 2.5 Flash Lite | Melalui OpenRouter API |
| **PDF Extraction** | pdfplumber + PyMuPDF | Ekstraksi teks dari dokumen PDF regulasi |
| **NLP Framework** | SentenceTransformers | Untuk menghasilkan embedding vektor |

### Struktur File Utama

```
SKIRPSI/
├── server.py                  # Flask API backend
├── run_pipeline.py            # Script untuk menjalankan seluruh pipeline
├── src/
│   ├── config.py              # Konfigurasi utama sistem
│   ├── pdf_extractor.py       # Ekstraksi & cleaning teks PDF
│   ├── chunker.py             # Chunking per pasal regulasi
│   ├── vector_store.py        # Embedding + ChromaDB
│   ├── hybrid_retriever.py    # Hybrid search (BM25 + Semantic)
│   ├── rag_pipeline.py        # RAG pipeline + LLM integration
│   └── evaluation.py          # Framework evaluasi
├── static/
│   ├── index.html             # Halaman utama website
│   ├── style.css              # Styling (Luxury Dark Theme)
│   └── app.js                 # Frontend logic
├── UU/                        # Folder berisi file PDF regulasi
├── data/
│   ├── extracted_texts.json   # Hasil ekstraksi teks PDF
│   └── chunks.json            # Hasil chunking semua dokumen
└── chroma_db/                 # Database ChromaDB (persisten)
```

---

## 3. Penjelasan Sidebar

Sidebar terletak di **sisi kiri** halaman website dan berfungsi sebagai **panel kontrol & informasi sistem**. Sidebar memiliki lebar tetap **280px** dengan tema gelap mewah (dark luxury) menggunakan gradien dari `#111111` ke `#1a1a1a`.

### 3.1 Header Sidebar

```
⚖️ Lex Regulasi
   HYBRID RAG • HUKUM PERTANAHAN
```

- **Logo:** Ikon timbangan keadilan (⚖️) dengan latar emas gradien
- **Judul:** "Lex Regulasi" — nama branding sistem, menggunakan font serif (Playfair Display)
- **Subtitle:** Deskripsi singkat "Hybrid RAG • Hukum Pertanahan" dalam huruf kapital kecil

### 3.2 Pengaturan Retrieval

Bagian ini memungkinkan pengguna **mengatur parameter pencarian** secara real-time:

#### a) Jumlah Dokumen (Top-K)
- **Tipe:** Slider (range input)
- **Rentang:** 3 sampai 10
- **Default:** 10
- **Fungsi:** Menentukan berapa banyak chunk/pasal regulasi yang akan diambil dari database sebagai konteks untuk LLM. Semakin besar nilai Top-K, semakin banyak dokumen yang dipertimbangkan untuk menyusun jawaban.

#### b) Bobot Semantic
- **Tipe:** Slider (range input)
- **Rentang:** 0.0 sampai 1.0 (disajikan sebagai 0–10, dibagi 10)
- **Default:** 1.0 (artinya 100% bobot pada semantic search)
- **Fungsi:** Mengatur seberapa besar kontribusi **pencarian semantik** (embedding similarity) dalam skor akhir hybrid. Ketika bobot semantic = 1.0, bobot BM25 otomatis menjadi 0.0.

#### c) Bobot BM25
- **Tipe:** Tampilan nilai otomatis (dihitung dari `1 - bobot_semantic`)
- **Default:** 0.0
- **Fungsi:** Menunjukkan bobot **pencarian keyword BM25**. Nilai ini selalu merupakan komplemen dari bobot semantic, sehingga total bobot semantic + BM25 = 1.0.

#### d) Metadata Filtering Otomatis
- **Tipe:** Checkbox
- **Default:** Aktif (checked)
- **Fungsi:** Jika diaktifkan, sistem akan secara otomatis mendeteksi **jenis regulasi**, **topik**, dan **tahun** dari pertanyaan pengguna, lalu memfilter database untuk hanya mencari pada dokumen yang relevan. Contoh: jika pengguna bertanya tentang "UU Kehutanan", sistem otomatis memfilter hanya chunk dari dokumen jenis "UU" dengan topik "hutan".

### 3.3 Info Sistem

Menampilkan statistik sistem yang diambil dari endpoint `/api/stats`:

| Statistik | Keterangan |
|---|---|
| **Total Chunks** | Jumlah total potongan pasal/ayat yang tersimpan di database |
| **Dokumen Regulasi** | Jumlah dokumen regulasi (PDF) yang telah diproses |

Data ini dimuat secara otomatis saat halaman pertama kali dibuka melalui panggilan API `GET /api/stats`.

### 3.4 Tech Stack

Daftar teknologi yang digunakan sistem, ditampilkan dengan ikon berlian emas:

- **Embedding:** multilingual-e5-small
- **Database:** ChromaDB
- **Retrieval:** Hybrid (BM25 + Semantic)
- **LLM:** Gemini 2.5 Flash Lite

### 3.5 Sidebar pada Mobile

Pada layar kecil (< 900px), sidebar **disembunyikan** secara default dan dapat dibuka melalui tombol hamburger (☰) di pojok kiri atas. Saat dibuka, sidebar menggeser ke kanan dengan animasi transform dari `-100%` ke `0`.

---

## 4. Penjelasan Halaman Utama (Main Content)

### 4.1 Hero Section

Area pembuka yang berisi:
- **Badge:** "Sistem Pencarian Hukum" dengan titik animasi pulse hijau
- **Judul:** "Regulasi Pertanahan & Perkebunan Indonesia" dengan efek gradien emas
- **Deskripsi:** Penjelasan singkat fungsi sistem

### 4.2 Search Box

Kotak pencarian utama untuk memasukkan pertanyaan hukum:
- **Input teks** dengan placeholder "Tanyakan seputar regulasi pertanahan & perkebunan..."
- **Tombol "AJUKAN"** untuk mengirim pertanyaan
- Mendukung pengiriman dengan tombol **Enter**

### 4.3 Contoh Pertanyaan

Grid berisi **8 contoh pertanyaan hukum** yang bisa diklik langsung:
1. Apakah boleh membuka lahan sawit di kawasan hutan?
2. Apa sanksi jika melanggar izin usaha perkebunan?
3. Bagaimana prosedur sertifikasi ISPO kelapa sawit?
4. Apa saja syarat untuk mendapatkan HGU?
5. Bagaimana aturan peremajaan tanaman kelapa sawit?
6. Apa kewajiban perusahaan perkebunan terhadap lingkungan?
7. Bagaimana aturan kemitraan perusahaan dengan petani plasma?
8. Apa saja jenis izin untuk usaha perkebunan sawit?

### 4.4 Loading State

Saat sistem memproses pertanyaan, muncul animasi spinner dengan pesan: "Menelusuri pasal-pasal regulasi dan menyusun jawaban hukum..."

### 4.5 Result Section

Setelah jawaban diterima, tampil 4 komponen:

#### a) Metrics Row
Tiga kartu metrik:
- **⏱ Waktu Proses** — Berapa detik sistem memproses pertanyaan
- **§ Pasal Ditemukan** — Jumlah pasal/chunk yang ditemukan
- **⚖ Filter Aktif** — Jumlah metadata filter yang digunakan

#### b) Filter Badges
Menampilkan filter metadata yang terdeteksi dari pertanyaan (misalnya "topik: hutan, kelapa sawit" atau "jenis: UU")

#### c) Pendapat Hukum (Answer Card)
Jawaban lengkap dari LLM berdasarkan dokumen regulasi yang ditemukan

#### d) Dasar Hukum (Sources Card)
List sumber hukum yang dirujuk, masing-masing menampilkan:
- Nama dokumen dan pasal
- Skor hybrid (dengan warna: hijau > 0.7, kuning > 0.4, merah < 0.4)
- Metadata: jenis, tahun, topik
- Detail skor: Semantic, BM25, Semantic (normalized), BM25 (normalized)
- Preview isi pasal

#### e) Detail Skor Retrieval
Tabel detail yang bisa dibuka (collapsible) berisi skor lengkap setiap chunk yang diambil.

---

## 5. Database yang Digunakan

### 5.1 ChromaDB — Vector Database

Sistem menggunakan **ChromaDB** sebagai database vektor utama. ChromaDB adalah database vektor open-source yang dirancang khusus untuk menyimpan dan mencari embedding vectors.

**Konfigurasi ChromaDB dalam sistem:**

| Parameter | Nilai | Keterangan |
|---|---|---|
| **Tipe Client** | `PersistentClient` | Data disimpan secara persisten di disk |
| **Direktori Penyimpanan** | `chroma_db/` | Folder di root proyek |
| **Nama Collection** | `regulasi_lahan` | Satu collection untuk semua chunk regulasi |
| **Distance Metric** | `cosine` | Menggunakan cosine similarity untuk mengukur kemiripan vektor |
| **Format File** | SQLite3 (`chroma.sqlite3`) | File database internal ChromaDB |

**Apa yang disimpan di ChromaDB:**

Setiap chunk/pasal yang disimpan memiliki:
- **ID** — Unique identifier chunk (hash MD5 12 karakter)
- **Document** — Teks lengkap isi pasal/ayat
- **Embedding** — Vektor representasi teks (dari model multilingual-e5-small)
- **Metadata** — Informasi terstruktur:
  - `dokumen`: Nama lengkap dokumen regulasi
  - `jenis`: Jenis regulasi (UU, PP, Perpres, Permentan, Permen ATR/BPN)
  - `tahun`: Tahun penerbitan
  - `pasal`: Nomor pasal
  - `topik`: Topik-topik terkait (comma-separated string)
  - `filename`: Nama file PDF sumber
  - `chunk_index`: Indeks urutan chunk dalam dokumen
  - `token_estimate`: Estimasi jumlah token

### 5.2 BM25 Index (In-Memory)

Selain ChromaDB, sistem juga membangun **BM25 index di memori** menggunakan library `rank_bm25` (BM25Okapi). Index ini dibangun dari seluruh chunks yang ada di `chunks.json` dan digunakan untuk pencarian berbasis keyword.

**Proses tokenisasi BM25:**
1. Teks diubah ke lowercase
2. Karakter non-alfanumerik dihapus
3. Teks di-tokenisasi berdasarkan spasi
4. Stopwords Bahasa Indonesia dihapus (41 kata: "yang", "dan", "di", "ini", "itu", "dengan", "untuk", "pada", dll.)
5. Token dengan panjang ≤ 1 karakter dihapus

---

## 6. Alur Proses Sistem (Pipeline)

### 6.1 Pipeline Persiapan Data (Offline — Dilakukan Sekali)

```
PDF Regulasi (UU/) 
    │
    ▼
[Phase 2: PDF Extraction] ──── pdfplumber / PyMuPDF
    │ Hasil: extracted_texts.json
    ▼
[Phase 3: Text Cleaning] ──── Hapus header, footer, nomor halaman, daftar isi
    │
    ▼
[Phase 4: Chunking per Pasal] ──── Regex pattern "Pasal X"
    │ Split per pasal, split pasal panjang per ayat, merge pasal pendek
    ▼
[Phase 5: Metadata Enrichment] ──── Deteksi topik otomatis + metadata dokumen
    │ Hasil: chunks.json
    ▼
[Phase 6: Embedding + Indexing] ──── multilingual-e5-small → ChromaDB
    │ Hasil: chroma_db/
    ▼
Sistem Siap Digunakan
```

#### Detail Setiap Phase:

**Phase 2 — PDF Extraction:**
- Membaca semua file PDF dari folder `UU/`
- Menggunakan `pdfplumber` (default) atau `PyMuPDF` untuk mengekstrak teks
- Metadata dokumen di-mapping dari nama file (29 dokumen regulasi terdaftar)
- Jenis dokumen: UU (5), PP (3), Perpres (4), Permentan (9), Permen ATR/BPN (5), SE (1), Peraturan (1)

**Phase 3 — Text Cleaning:**
- Menghapus nomor halaman (pattern: `- 12 -`, `Halaman X`, `Page X`)
- Menghapus header/footer (URL hukumonline, lembaran negara)
- Menghapus daftar isi (baris dengan titik-titik `......` diikuti nomor)
- Menghapus baris yang hanya berisi angka
- Normalisasi spasi dan newline berlebih

**Phase 4 — Chunking per Pasal:**
- Regulasi di-chunk berdasarkan **pasal**, bukan random
- Menggunakan regex pattern: `^Pasal\s+(\d+[A-Z]?)\s*$`
- Teks sebelum Pasal 1 disimpan sebagai chunk "Preambul"
- Pasal terlalu panjang (> 700 token) dipecah per ayat
- Pasal terlalu pendek (< 50 token) digabung dengan pasal berikutnya

**Phase 5 — Metadata Enrichment:**
- Setiap chunk mendapat metadata: dokumen, jenis, tahun, pasal, topik, filename
- Topik dideteksi otomatis dari isi teks menggunakan keyword matching (16 kategori topik)
- Topik dokumen (dari mapping) digabung dengan topik yang terdeteksi dari teks

**Phase 6 — Embedding + Indexing:**
- Teks di-embed menggunakan `intfloat/multilingual-e5-small`
- Prefix ditambahkan: `"passage: "` untuk dokumen, `"query: "` untuk pertanyaan
- Embedding di-normalize (unit vector)
- Disimpan ke ChromaDB dalam batch 500 dokumen

### 6.2 Pipeline Tanya-Jawab (Online — Setiap Pertanyaan)

```
Pertanyaan Pengguna
    │
    ▼
[Step 1: Metadata Filter Extraction]
    │ Deteksi jenis, topik, tahun dari pertanyaan
    ▼
[Step 2: Semantic Search] ──── ChromaDB (cosine similarity)
    │ Ambil top_k × 3 kandidat (dengan/tanpa metadata filter)
    ▼
[Step 3: BM25 Keyword Search] ──── BM25Okapi
    │ Ambil top_k × 3 kandidat
    ▼
[Step 4: Score Normalization + Fusion]
    │ Normalize skor ke [0, 1] → Weighted sum
    │ hybrid_score = semantic_weight × sem_norm + bm25_weight × bm25_norm
    ▼
[Step 5: Top-K Selection]
    │ Ambil top_k chunk dengan skor hybrid tertinggi
    ▼
[Step 6: Build Context]
    │ Format chunk + sumber → max 12.000 karakter
    ▼
[Step 7: Query LLM] ──── Gemini 2.5 Flash Lite via OpenRouter
    │ System prompt + User prompt (konteks + pertanyaan)
    ▼
[Step 8: Return Response]
    │ Jawaban + daftar sumber + skor retrieval + filter metadata
    ▼
Tampilkan di Frontend
```

#### Detail Langkah Query:

**Step 1 — Metadata Filter Extraction:**
Sistem mendeteksi informasi dari pertanyaan pengguna:
- **Jenis regulasi:** "undang-undang" → UU, "peraturan pemerintah" → PP, "perpres" → Perpres, dll.
- **Topik:** "sawit" → kelapa sawit, "hutan" → hutan, "izin" → izin usaha, dll. (20+ keyword mapping)
- **Tahun:** pattern "tahun 2014" atau range "2014–2020"

**Step 2 — Semantic Search (ChromaDB):**
- Pertanyaan di-embed dengan prefix `"query: "` menggunakan model multilingual-e5-small
- Pencarian cosine similarity di ChromaDB
- Jika metadata filter aktif: cari dengan filter dulu, jika hasilnya 0 → fallback tanpa filter
- Mengambil `top_k × 3` kandidat untuk di-fusi

**Step 3 — BM25 Keyword Search:**
- Pertanyaan di-tokenisasi (lowercase, hapus stopwords)
- Skor BM25 dihitung terhadap seluruh corpus
- Mengambil `top_k × 3` kandidat teratas

**Step 4 — Score Normalization + Weighted Fusion:**
- Skor semantic dan BM25 di-normalize ke rentang [0, 1] menggunakan min-max normalization:
  ```
  norm_score = (score - min_score) / (max_score - min_score)
  ```
- Skor hybrid dihitung:
  ```
  hybrid_score = semantic_weight × normalized_semantic + bm25_weight × normalized_bm25
  ```
- Default: `semantic_weight = 0.7`, `bm25_weight = 0.3`

**Step 5 — Top-K Selection:**
- Semua kandidat diurutkan berdasarkan `hybrid_score` descending
- Diambil `top_k` teratas (default: 10)

**Step 6 — Build Context:**
- Setiap chunk diformat dengan sumber: `[Sumber: Nama Dokumen, Pasal X]`
- Chunk individual dibatasi 3.000 karakter
- Total konteks dibatasi 12.000 karakter

**Step 7 — Query LLM:**
- **Model:** `google/gemini-2.5-flash-lite` via OpenRouter API
- **Temperature:** 0.1 (jawaban konsisten dan faktual)
- **Max Tokens:** 2.048
- **System Prompt:** Instruksi sebagai asisten hukum yang menjawab berdasarkan dokumen, menyertakan referensi pasal
- **User Prompt:** Template berisi konteks dokumen regulasi + pertanyaan pengguna

---

## 7. Penentuan Top-K

### 7.1 Apa itu Top-K?

**Top-K** adalah parameter yang menentukan **berapa banyak chunk (potongan pasal/ayat) yang diambil** dari database sebagai konteks untuk LLM dalam menyusun jawaban. Semakin besar Top-K, semakin banyak informasi yang diberikan ke LLM, namun juga meningkatkan risiko noise (informasi tidak relevan).

### 7.2 Konfigurasi Top-K dalam Sistem

| Parameter | Nilai | Lokasi |
|---|---|---|
| **Default Top-K** | 10 | `src/config.py` → `TOP_K = 10` |
| **Minimum (UI)** | 3 | Slider di sidebar (`min="3"`) |
| **Maximum (UI)** | 10 | Slider di sidebar (`max="10"`) |
| **Kandidat Retrieval** | Top-K × 3 = 30 | Di-retrieve 3× lebih banyak untuk fusion |

### 7.3 Bagaimana Top-K Bekerja dalam Pipeline

```
Pertanyaan User
    │
    ▼
Semantic Search → ambil top_k × 3 kandidat (30 chunk)
BM25 Search     → ambil top_k × 3 kandidat (30 chunk)
    │
    ▼
Gabung semua kandidat unik (bisa 30–60 chunk)
    │
    ▼
Hitung hybrid score untuk setiap kandidat
    │
    ▼
Urutkan berdasarkan hybrid score (descending)
    │
    ▼
Ambil TOP-K teratas (misal 10 chunk) ← Inilah yang dikirim ke LLM
    │
    ▼
Build context (max 12.000 karakter) → Kirim ke LLM
```

### 7.4 Mengapa Top-K = 10 Dipilih sebagai Default?

1. **Cakupan regulasi luas:** Satu pertanyaan hukum bisa melibatkan beberapa pasal dari berbagai UU/PP/Permentan. Top-K = 10 memberikan cakupan yang cukup.
2. **Batasan konteks LLM:** Gemini 2.5 Flash Lite mendukung konteks panjang, namun konteks dibatasi 12.000 karakter agar jawaban tetap fokus.
3. **Trade-off presisi vs recall:** Top-K terlalu kecil (3–5) berisiko melewatkan pasal penting. Top-K terlalu besar (> 15) menambah noise.
4. **Pengaturan fleksibel:** Pengguna bisa mengubah Top-K melalui slider di sidebar (3–10) sesuai kebutuhan.

### 7.5 Pengaruh Top-K terhadap Kualitas Jawaban

| Top-K | Kelebihan | Kekurangan |
|---|---|---|
| **3–5** | Jawaban sangat fokus, proses cepat | Bisa melewatkan pasal penting |
| **7–10** | Keseimbangan antara cakupan dan fokus | Proses sedikit lebih lambat |
| **> 10** | Cakupan maksimal | Risiko informasi noise, LLM bisa kebingungan |

---

## 8. Penjelasan Hybrid Search

### 8.1 Mengapa Hybrid?

Sistem menggunakan **dua metode pencarian** yang saling melengkapi:

| Metode | Kekuatan | Kelemahan |
|---|---|---|
| **Semantic Search** | Menangkap makna/konteks pertanyaan | Kurang baik untuk istilah spesifik (nomor pasal, singkatan) |
| **BM25 (Keyword)** | Akurat untuk kata kunci spesifik | Tidak memahami sinonim atau konteks |

Dengan menggabungkan keduanya, sistem mendapat **manfaat dari kedua pendekatan** — memahami makna pertanyaan sekaligus menangkap kata kunci penting.

### 8.2 Alur Hybrid Search

1. **Semantic Search (ChromaDB):**
   - Pertanyaan di-embed menjadi vektor menggunakan `intfloat/multilingual-e5-small`
   - Dicari chunk dengan cosine similarity tertinggi
   - Skor: `similarity = 1 - cosine_distance`

2. **BM25 Keyword Search:**
   - Pertanyaan di-tokenisasi (lowercase, hapus stopwords Indonesia)
   - Skor BM25Okapi dihitung terhadap seluruh corpus
   - Kata kunci penting (nama UU, istilah hukum) mendapat bobot tinggi

3. **Score Normalization:**
   - Min-max normalization ke rentang [0, 1]:
     ```
     norm = (score - min) / (max - min)
     ```

4. **Weighted Fusion:**
   ```
   hybrid_score = 0.7 × semantic_norm + 0.3 × bm25_norm
   ```
   (default, dapat diubah melalui slider di sidebar)

### 8.3 Contoh Perhitungan

Misalkan untuk chunk "Pasal 26 UU Kehutanan":
- Semantic score = 0.82 → normalized = 0.90
- BM25 score = 12.5 → normalized = 0.75

```
hybrid_score = 0.7 × 0.90 + 0.3 × 0.75
             = 0.63 + 0.225
             = 0.855
```

---

## 9. Metadata Filtering

### 9.1 Cara Kerja

Sebelum pencarian dilakukan, sistem menganalisis pertanyaan pengguna untuk mendeteksi filter metadata:

| Kategori Filter | Contoh Keyword | Nilai Filter |
|---|---|---|
| **Jenis Regulasi** | "undang-undang", "UU" | `jenis: "UU"` |
| | "peraturan pemerintah", "PP" | `jenis: "PP"` |
| | "perpres" | `jenis: "Perpres"` |
| | "permentan" | `jenis: "Permentan"` |
| **Topik** | "sawit", "kelapa sawit" | `topik: "kelapa sawit"` |
| | "hutan", "kehutanan" | `topik: "hutan"` |
| | "izin", "perizinan" | `topik: "izin usaha"` |
| | "sanksi", "pidana", "denda" | `topik: "sanksi"` |
| | "ISPO", "sertifikasi" | `topik: "sertifikasi"` |
| **Tahun** | "tahun 2014" | `tahun: 2014` |
| **Rentang Tahun** | "2014–2020" | `tahun_min: 2014, tahun_max: 2020` |

### 9.2 Fallback Mechanism

Jika filter metadata terlalu ketat dan tidak menghasilkan hasil apapun dari ChromaDB, sistem otomatis melakukan **fallback tanpa filter** agar pengguna tetap mendapat jawaban.

---

## 10. Evaluasi Sistem

Sistem memiliki framework evaluasi yang menguji kinerja retrieval dengan **22 pertanyaan uji** yang mencakup berbagai topik regulasi. Evaluasi membandingkan:

1. **Hybrid Search** (BM25 + Semantic)
2. **Semantic Search saja**
3. **BM25 Search saja**

Metrik yang diukur:
- **Precision@K** — Berapa banyak dari K chunk yang diambil yang benar-benar relevan
- **Recall** — Berapa banyak dokumen relevan yang berhasil ditemukan
- **Topic Hit Rate** — Apakah topik yang diharapkan muncul dalam hasil retrieval
- **Jenis Hit Rate** — Apakah jenis regulasi yang diharapkan muncul dalam hasil

---

*Laporan ini dibuat secara otomatis berdasarkan analisis source code sistem Hybrid RAG Regulasi Pertanahan & Perkebunan Indonesia.*

*Tanggal: 23 Februari 2026*
