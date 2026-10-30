# Penjelasan Lengkap Sistem Hybrid RAG Regulasi Lahan

Dokumen ini menjelaskan sistem dari awal sampai akhir: tujuan sistem, alur data, fitur yang digunakan, teknologi, serta lokasi file spesifik tempat setiap proses berjalan.

## 1. Gambaran Umum Sistem

Sistem ini adalah aplikasi tanya jawab regulasi pertanahan dan perkebunan Indonesia berbasis Hybrid RAG (Retrieval-Augmented Generation). Pengguna memasukkan pertanyaan hukum, sistem mencari pasal/dokumen regulasi yang relevan, lalu LLM menyusun jawaban berdasarkan konteks yang ditemukan.

Alur besarnya:

```text
PDF regulasi di folder UU/
  -> ekstraksi teks
  -> pembersihan teks
  -> chunking per pasal
  -> embedding
  -> penyimpanan ke Qdrant
  -> pertanyaan user
  -> metadata filtering
  -> semantic search + BM25
  -> penggabungan skor hybrid
  -> konteks dikirim ke LLM OpenRouter
  -> jawaban + sumber pasal ditampilkan di frontend
```

Kondisi data lokal saat dokumen ini dibuat:

- Folder sumber PDF: `UU/`
- Jumlah PDF di folder `UU/`: 28 file
- File chunk hasil proses: `data/chunks.json`
- Total chunk aktif: 4.892 chunk
- Total dokumen unik di chunk: 27 dokumen
- Total pasal unik: 2.053 pasal
- Vector database lokal: `qdrant_db/`
- Collection Qdrant: `regulasi_lahan`
- Dimensi embedding: 384
- Distance metric Qdrant: Cosine

## 2. Struktur Folder Penting

| Folder/File | Fungsi |
|---|---|
| `UU/` | Berisi PDF regulasi mentah yang menjadi sumber pengetahuan sistem. |
| `data/extracted_texts.json` | Hasil ekstraksi dan pembersihan teks dari PDF. |
| `data/chunks.json` | Hasil chunking dokumen menjadi bagian pasal/sub-pasal beserta metadata. |
| `qdrant_db/` | Database vektor lokal Qdrant yang menyimpan embedding dan payload chunk. |
| `src/` | Modul utama backend RAG: konfigurasi, ekstraksi, chunking, vector store, retrieval, pipeline, evaluasi. |
| `static/` | Frontend HTML, CSS, dan JavaScript untuk aplikasi web. |
| `server.py` | Backend Flask REST API dan static file server. |
| `run_pipeline.py` | Script untuk menjalankan pipeline dari PDF sampai index Qdrant. |
| `HASIL RAGAS/` | Output evaluasi RAGAS dalam format JSON dan CSV. |
| `docs/` | Dokumentasi sistem, catatan migrasi, ringkasan, dan file dokumentasi ini. |

## 3. Konfigurasi Utama

Semua konfigurasi inti sistem berada di `src/config.py`.

Lokasi penting:

- Path folder dan file: `src/config.py:13-18`
- Metode ekstraksi PDF: `src/config.py:21`
- Aturan chunking: `src/config.py:24-26`
- Model embedding: `src/config.py:30`
- Nama collection Qdrant: `src/config.py:33`
- Bobot retrieval hybrid dan `TOP_K`: `src/config.py:38-40`
- Konfigurasi OpenRouter/LLM: `src/config.py:43-50`
- Prompt sistem dan template prompt user: `src/config.py:53-73`

Konfigurasi environment disediakan melalui `.env` dan contoh formatnya ada di `.env.example`.

Variabel penting:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.5-flash-lite
OPENROUTER_TIMEOUT_SECONDS=120
OPENROUTER_SITE_URL=http://localhost:5000
OPENROUTER_APP_NAME=Hybrid-RAG-Regulasi-Lahan
QDRANT_COLLECTION_NAME=regulasi_lahan
QDRANT_PATH=./qdrant_db
```

## 4. Proses Awal: PDF Menjadi Teks

Proses ini berjalan di `src/pdf_extractor.py`.

Fungsi utamanya:

- Mapping metadata dokumen: `DOCUMENT_METADATA` di `src/pdf_extractor.py:20`
- Ambil metadata berdasarkan nama file: `get_metadata_for_file()` di `src/pdf_extractor.py:198`
- Ekstraksi memakai pdfplumber: `extract_text_pdfplumber()` di `src/pdf_extractor.py:235`
- Ekstraksi memakai PyMuPDF: `extract_text_pymupdf()` di `src/pdf_extractor.py:246`
- Pemilihan metode ekstraksi: `extract_text()` di `src/pdf_extractor.py:258`
- Pembersihan teks: `clean_text()` di `src/pdf_extractor.py:272`
- Ekstraksi semua PDF: `extract_all_pdfs()` di `src/pdf_extractor.py:317`

Yang dilakukan sistem:

1. Membaca seluruh file `.pdf` dari folder `UU/`.
2. Mengambil teks dari PDF menggunakan metode yang diatur di `src/config.py`.
3. Membersihkan teks dari nomor halaman, header/footer, daftar isi, dan whitespace berlebih.
4. Menambahkan metadata dokumen seperti nama regulasi, jenis regulasi, tahun, dan topik utama.
5. Menyimpan hasil ke `data/extracted_texts.json`.

## 5. Proses Chunking Per Pasal

Proses chunking berjalan di `src/chunker.py`.

Fungsi dan pola penting:

- Regex pendeteksi Pasal: `PASAL_PATTERN` di `src/chunker.py:20`
- Regex pendeteksi BAB: `BAB_PATTERN` di `src/chunker.py:26`
- Regex pendeteksi ayat: `AYAT_PATTERN` di `src/chunker.py:38`
- Estimasi token: `estimate_tokens()` di `src/chunker.py:44`
- Deteksi topik chunk: `detect_topic()` di `src/chunker.py:55`
- Pemecahan teks berdasarkan pasal: `split_by_pasal()` di `src/chunker.py:88`
- Pemecahan chunk panjang: `split_long_chunk()` di `src/chunker.py:132`
- Penggabungan chunk pendek: `merge_short_chunks()` di `src/chunker.py:202`
- Proses satu dokumen: `chunk_document()` di `src/chunker.py:252`
- Proses semua dokumen: `chunk_all_documents()` di `src/chunker.py:302`

Yang dilakukan sistem:

1. Teks bersih dari `data/extracted_texts.json` dibaca kembali.
2. Dokumen dipotong berdasarkan pola `Pasal`.
3. Jika satu pasal terlalu panjang, sistem memecahnya lagi berdasarkan ayat atau baris.
4. Jika chunk terlalu pendek, sistem menggabungkan chunk pendek yang masih berada pada pasal yang sama.
5. Sistem menambahkan metadata lengkap: dokumen, jenis, tahun, pasal, topik, filename, indeks chunk, dan estimasi token.
6. Hasilnya disimpan ke `data/chunks.json`.

Contoh struktur chunk:

```json
{
  "chunk_id": "id_unik",
  "text": "Isi pasal...",
  "metadata": {
    "dokumen": "UU No. 39 Tahun 2014 tentang Perkebunan",
    "jenis": "UU",
    "tahun": 2014,
    "pasal": "Pasal 12",
    "topik": ["perkebunan", "lahan"],
    "filename": "39TAHUN2014UU.pdf",
    "chunk_index": 10,
    "token_estimate": 250
  }
}
```

## 6. Proses Embedding dan Indexing ke Qdrant

Proses embedding dan penyimpanan vektor berjalan di `src/vector_store.py`.

Fungsi penting:

- Load model embedding singleton: `get_embedding_model()` di `src/vector_store.py:36`
- Generate embedding teks/query: `embed_texts()` di `src/vector_store.py:46`
- Membuka Qdrant lokal: `get_qdrant_client()` di `src/vector_store.py:75`
- Membuat collection Qdrant: `ensure_collection()` di `src/vector_store.py:84`
- Memotong teks terlalu panjang: `truncate_text()` di `src/vector_store.py:114`
- Mengubah `chunk_id` menjadi ID numerik Qdrant: `_to_qdrant_point_id()` di `src/vector_store.py:121`
- Index semua chunk: `index_chunks()` di `src/vector_store.py:132`
- Konversi filter metadata ke filter Qdrant: `_where_to_qdrant_filter()` di `src/vector_store.py:222`
- Semantic search: `search_similar()` di `src/vector_store.py:281`

Model embedding yang dipakai:

```text
intfloat/multilingual-e5-small
```

Catatan penting:

- Untuk dokumen, teks diberi prefix `passage:`.
- Untuk pertanyaan user, teks diberi prefix `query:`.
- Embedding dinormalisasi sehingga cocok dengan pencarian cosine similarity.
- Payload yang disimpan ke Qdrant tetap menyimpan teks asli chunk dan metadata, jadi sistem tidak perlu "mendecode" vektor menjadi teks.

## 7. Pipeline Lengkap dari Nol

Script untuk menjalankan semua proses dari awal adalah `run_pipeline.py`.

Lokasi:

- Entry point pipeline: `main()` di `run_pipeline.py:13`

Urutan yang dijalankan:

1. `extract_all_pdfs()` dari `src/pdf_extractor.py`
2. `chunk_all_documents()` dari `src/chunker.py`
3. `index_chunks(chunks, reset=True)` dari `src/vector_store.py`

Perintah:

```bash
python run_pipeline.py
```

Output utama:

- `data/extracted_texts.json`
- `data/chunks.json`
- Index Qdrant di `qdrant_db/collection/regulasi_lahan/`

## 8. Backend API Flask

Backend utama berjalan di `server.py`.

Route penting:

| Endpoint | Method | File/Line | Fungsi |
|---|---|---|---|
| `/` | GET | `server.py:49` | Mengirim `static/index.html`. |
| `/api/query` | POST | `server.py:55` | Endpoint utama tanya jawab RAG. |
| `/api/stats` | GET | `server.py:93` | Mengirim statistik chunk, dokumen, dan pasal. |
| `/api/health` | GET | `server.py:129` | Health check sederhana. |
| `/api/eval/ragas` | POST | `server.py:134` | Menjalankan evaluasi RAGAS dari frontend/API. |

Fitur penting backend:

- Pipeline RAG dibuat secara lazy-load agar model tidak langsung dimuat sebelum dibutuhkan: `get_pipeline()` di `server.py:25`.
- Response JSON dibersihkan dari nilai `NaN`/`Inf` sebelum dikirim: `_json_safe()` di `server.py:34`.
- Static frontend disajikan dari folder `static/`.

Contoh request ke endpoint utama:

```json
{
  "question": "Apa saja syarat untuk mendapatkan HGU?",
  "top_k": 10,
  "auto_filter": true
}
```

Contoh struktur response:

```json
{
  "question": "...",
  "answer": "...",
  "sources": [],
  "referenced_sources": [],
  "metadata_filters": {},
  "elapsed": 1.23
}
```

## 9. Retrieval: Metadata Filter, BM25, Semantic Search, dan Hybrid Score

Retrieval berjalan di `src/hybrid_retriever.py`.

Komponen utama:

- Stopword Bahasa Indonesia: `INDONESIAN_STOPWORDS` di `src/hybrid_retriever.py:23`
- Index BM25: `BM25Index` di `src/hybrid_retriever.py:40`
- Metadata filter: `MetadataFilter` di `src/hybrid_retriever.py:111`
- Hybrid retriever: `HybridRetriever` di `src/hybrid_retriever.py:238`
- Singleton retriever: `get_retriever()` di `src/hybrid_retriever.py:527`

### 9.1 Metadata Filtering

Metadata filtering mendeteksi kata kunci pada pertanyaan user.

Lokasi:

- Keyword jenis regulasi: `MetadataFilter.JENIS_KEYWORDS` di `src/hybrid_retriever.py:116`
- Keyword topik: `MetadataFilter.TOPIK_KEYWORDS` di `src/hybrid_retriever.py:132`
- Ekstraksi filter: `extract_filters()` di `src/hybrid_retriever.py:165`
- Konversi filter untuk vector search: `build_vector_where()` di `src/hybrid_retriever.py:204`

Contoh:

```text
Pertanyaan: "Apa syarat HGU untuk perkebunan sawit?"
Filter terdeteksi: topik = ["hak guna usaha", "kelapa sawit", "perkebunan"]
```

### 9.2 BM25 Keyword Search

BM25 dipakai untuk mencari kecocokan kata kunci eksplisit.

Lokasi:

- Pembuatan index dari `data/chunks.json`: `BM25Index.__init__()` di `src/hybrid_retriever.py:43`
- Tokenisasi Bahasa Indonesia: `BM25Index._tokenize()` di `src/hybrid_retriever.py:52`
- Pencarian BM25: `BM25Index.search()` di `src/hybrid_retriever.py:60`

BM25 penting untuk domain hukum karena pertanyaan sering mengandung istilah spesifik seperti `HGU`, `ISPO`, `Pasal`, `UU`, atau nomor regulasi.

### 9.3 Semantic Search

Semantic search memakai Qdrant dan embedding.

Lokasi:

- Pencarian semantic dipanggil dari `HybridRetriever.retrieve()` di `src/hybrid_retriever.py:348`
- Implementasi detail semantic search ada di `search_similar()` pada `src/vector_store.py:281`

Semantic search membantu ketika kata dalam pertanyaan tidak sama persis dengan isi dokumen, tetapi maknanya berdekatan.

### 9.4 Hybrid Score

Hybrid retrieval menggabungkan:

- Semantic similarity
- BM25 score
- Lexical/query boost tambahan

Lokasi:

- Proses utama retrieval: `HybridRetriever.retrieve()` di `src/hybrid_retriever.py:330`
- Lexical boost: `_query_boost()` di `src/hybrid_retriever.py:271`
- Normalisasi skor dan penggabungan skor: bagian scoring di `src/hybrid_retriever.py:448-489`

Rumus implementasi saat ini:

```text
hybrid_score =
  (semantic_weight * semantic_norm)
  + (bm25_weight * bm25_norm)
  + (0.35 * lexical_boost)
```

Bobot default ada di `src/config.py`:

- `SEMANTIC_WEIGHT = 0.6`
- `BM25_WEIGHT = 0.4`
- `TOP_K = 15`

Catatan: frontend memiliki slider bobot semantic/BM25, tetapi request `/api/query` saat ini hanya mengirim `question`, `top_k`, dan `auto_filter`. Bobot dari slider belum diteruskan ke backend pada implementasi `static/app.js`.

## 10. RAG Pipeline dan LLM OpenRouter

Pipeline tanya jawab utama berada di `src/rag_pipeline.py`.

Fungsi penting:

- Membuat endpoint dan header OpenRouter: `get_llm_client()` di `src/rag_pipeline.py:28`
- Menyusun konteks dari chunk hasil retrieval: `build_context()` di `src/rag_pipeline.py:51`
- Mendeteksi sumber yang benar-benar disebut dalam jawaban: `extract_referenced_sources()` di `src/rag_pipeline.py:93`
- Kelas pipeline utama: `RAGPipeline` di `src/rag_pipeline.py:200`
- Method query utama: `RAGPipeline.query()` di `src/rag_pipeline.py:217`
- Singleton pipeline: `get_pipeline()` di `src/rag_pipeline.py:394`

Alur di `RAGPipeline.query()`:

1. Menerima pertanyaan user.
2. Memanggil `HybridRetriever.retrieve()`.
3. Mengurutkan hasil berdasarkan skor hybrid.
4. Membuat konteks dengan tag sumber, misalnya:

   ```text
   --- Dokumen 1 [Sumber: UU No. 39 Tahun 2014 tentang Perkebunan, Pasal 12] ---
   ```

5. Menggabungkan konteks dan pertanyaan ke prompt.
6. Mengirim request ke OpenRouter Chat Completions API.
7. Mengambil teks jawaban dari response LLM.
8. Menyusun daftar sumber, menghapus duplikasi dokumen/pasal, dan memilih sumber yang dirujuk.
9. Mengembalikan object hasil ke `server.py`.

Prompt yang mengatur perilaku LLM berada di `src/config.py:53-73`. Prompt menekankan bahwa jawaban harus berdasarkan dokumen yang diberikan dan tidak boleh membuat pasal atau undang-undang yang tidak ada pada konteks.

## 11. Frontend Web

Frontend berada di folder `static/`.

File utama:

- Struktur halaman: `static/index.html`
- Styling tampilan: `static/style.css`
- Logika interaksi dan pemanggilan API: `static/app.js`

Bagian penting `static/index.html`:

- Sidebar pengaturan retrieval, statistik sistem, tech stack, dan RAGAS.
- Input pertanyaan user.
- Contoh pertanyaan hukum.
- Area loading.
- Area hasil jawaban.
- Daftar dasar hukum/sumber.
- Detail skor retrieval.
- Panel hasil evaluasi RAGAS.

Bagian penting `static/app.js`:

- Referensi elemen DOM: `static/app.js:8-34`
- Ambil statistik sistem dari `/api/stats`: `loadStats()` di `static/app.js:54`
- Kirim pertanyaan ke `/api/query`: `submitQuestion()` di `static/app.js:82`
- Render jawaban, metrics, filter, sumber, dan tabel skor: `renderResult()` di `static/app.js:121`
- Jalankan evaluasi RAGAS dari frontend: `runRagasEvaluation()` di `static/app.js:268`
- Render hasil RAGAS: `renderRagasResult()` di `static/app.js:301`

Catatan UI:

- Aplikasi web utama saat ini memakai Flask + HTML/CSS/JS.
- File `src/app.py` masih berisi versi frontend Streamlit lama.

## 12. Frontend Streamlit Lama

Versi Streamlit berada di `src/app.py`.

Lokasi penting:
   
- Konfigurasi halaman Streamlit: `src/app.py:19`
- Load pipeline dengan cache: `load_pipeline()` di `src/app.py:83`
- Sidebar pengaturan retrieval: mulai `src/app.py:94`
- Input pertanyaan dan proses query: mulai `src/app.py:143`
- Display jawaban dan sumber: mulai `src/app.py:190`

Status:

- Masih ada di codebase.
- README masih menyebut cara menjalankan Streamlit.
- Namun `server.py` dan folder `static/` menunjukkan aplikasi web utama sudah dimigrasikan menjadi Flask API + frontend statis.

## 13. Evaluasi Retrieval

Evaluasi retrieval klasik berada di `src/evaluation.py`.

Komponen penting:

- Dataset pertanyaan evaluasi: `EVAL_QUESTIONS` di `src/evaluation.py:25`
- Evaluasi akurasi retrieval: `evaluate_retrieval_accuracy()` di `src/evaluation.py:242`
- Jalankan evaluasi per mode: `run_retrieval_evaluation()` di `src/evaluation.py:294`
- Bandingkan hybrid, semantic, dan BM25: `compare_methods()` di `src/evaluation.py:369`
- Simpan hasil evaluasi JSON/CSV: `save_evaluation_results()` di `src/evaluation.py:404`

Metrik yang dipakai:

- Topic Hit Rate
- Document Hit Rate
- Jenis Match
- Latency

Output disimpan di folder `data/` dengan nama seperti:

```text
evaluation_YYYYMMDD_HHMMSS.json
evaluation_YYYYMMDD_HHMMSS_summary.csv
```

## 14. Evaluasi RAGAS

Evaluasi RAGAS berada di `src/ragas_evaluation.py`.

Fungsi penting:

- Daftar metrik RAGAS: `RAGAS_METRIC_NAMES` di `src/ragas_evaluation.py:31`
- Menyiapkan sample RAGAS: `_prepare_ragas_samples()` di `src/ragas_evaluation.py:62`
- Menjalankan evaluasi RAGAS: `run_ragas_evaluation()` di `src/ragas_evaluation.py:100`
- Menyimpan hasil RAGAS: `save_ragas_results()` di `src/ragas_evaluation.py:219`

Metrik RAGAS:

- `faithfulness`
- `answer_relevancy`
- `context_precision`
- `context_recall`

Cara menjalankan:

1. Melalui frontend: panel "Evaluasi RAGAS" di sidebar.
2. Melalui API: `POST /api/eval/ragas`.
3. Melalui script: `run_ragas_eval_improved.py`.

Output disimpan ke `HASIL RAGAS/` sebagai JSON dan CSV detail.

## 15. Script Debug dan Test

File bantu yang ada di root:

| File | Fungsi |
|---|---|
| `debug_retrieval.py` | Mengecek chunk, metadata filtering, semantic search, BM25, dan full retrieval. |
| `check_health.py` | Mengecek endpoint health backend. |
| `check_requests.py` | Mengecek request HTTP sederhana. |
| `test_improvements.py` | Test perubahan/perbaikan sistem. |
| `test_prompt_improvements.py` | Test perubahan prompt. |
| `test_ragas_improvements.py` | Test konfigurasi, retriever, dan RAGAS subset. |
| `run_ragas_eval_improved.py` | Menjalankan evaluasi RAGAS dengan konfigurasi perbaikan dan membandingkan baseline. |

## 16. Fitur yang Digunakan Sistem

Fitur utama sistem:

1. Ekstraksi PDF regulasi
   - Menggunakan `pdfplumber` atau `PyMuPDF`.
   - Lokasi: `src/pdf_extractor.py`.

2. Metadata dokumen
   - Dokumen diberi jenis regulasi, tahun, nama dokumen, dan topik utama.
   - Lokasi: `DOCUMENT_METADATA` di `src/pdf_extractor.py:20`.

3. Chunking berbasis pasal
   - Sistem memotong dokumen berdasarkan struktur regulasi Indonesia, terutama `Pasal`.
   - Lokasi: `src/chunker.py`.

4. Deteksi topik otomatis
   - Chunk diberi topik berdasarkan keyword seperti `izin usaha`, `hutan`, `kelapa sawit`, `lingkungan`, `HGU`, `ISPO`, dan lain-lain.
   - Lokasi: `detect_topic()` di `src/chunker.py:55`.

5. Embedding multilingual
   - Menggunakan `intfloat/multilingual-e5-small`.
   - Lokasi: `src/vector_store.py`.

6. Vector database Qdrant lokal
   - Menyimpan embedding, teks chunk, dan metadata.
   - Lokasi penyimpanan: `qdrant_db/`.

7. Semantic search
   - Mencari chunk berdasarkan kedekatan makna.
   - Lokasi: `search_similar()` di `src/vector_store.py:281`.

8. BM25 keyword search
   - Mencari chunk berdasarkan kata kunci.
   - Lokasi: `BM25Index` di `src/hybrid_retriever.py:40`.

9. Hybrid retrieval
   - Menggabungkan semantic search, BM25, dan lexical boost.
   - Lokasi: `HybridRetriever.retrieve()` di `src/hybrid_retriever.py:330`.

10. Metadata filtering otomatis
    - Mendeteksi jenis regulasi, topik, dan tahun dari pertanyaan.
    - Lokasi: `MetadataFilter` di `src/hybrid_retriever.py:111`.

11. LLM via OpenRouter
    - Menghasilkan jawaban berdasarkan konteks chunk.
    - Lokasi: `src/rag_pipeline.py`.

12. Citation/sumber jawaban
    - Sistem menampilkan dokumen, pasal, jenis, tahun, topik, preview, dan skor retrieval.
    - Lokasi: penyusunan sumber di `src/rag_pipeline.py`, tampilan di `static/app.js`.

13. Web API
    - Flask API untuk query, statistik, health check, dan evaluasi RAGAS.
    - Lokasi: `server.py`.

14. Frontend statis
    - HTML/CSS/JS untuk input pertanyaan, menampilkan jawaban, sumber, skor, dan evaluasi.
    - Lokasi: `static/`.

15. Evaluasi retrieval dan RAGAS
    - Retrieval evaluation di `src/evaluation.py`.
    - RAGAS evaluation di `src/ragas_evaluation.py`.

## 17. Alur Saat User Bertanya

Urutan proses saat user membuka web dan mengirim pertanyaan:

1. User membuka `http://localhost:5000/`.
   - File: `server.py:49`
   - Frontend: `static/index.html`

2. Frontend mengambil statistik sistem.
   - File: `static/app.js:54`
   - Endpoint: `GET /api/stats` di `server.py:93`

3. User mengetik pertanyaan dan klik tombol "AJUKAN".
   - File: `static/app.js:82`
   - Endpoint: `POST /api/query` di `server.py:55`

4. Backend memuat pipeline RAG jika belum pernah dimuat.
   - File: `server.py:25`
   - Kelas pipeline: `RAGPipeline` di `src/rag_pipeline.py:200`

5. Pipeline memanggil retriever.
   - File: `src/rag_pipeline.py:217`
   - Retriever: `HybridRetriever.retrieve()` di `src/hybrid_retriever.py:330`

6. Retriever mendeteksi filter metadata dari pertanyaan.
   - File: `MetadataFilter.extract_filters()` di `src/hybrid_retriever.py:165`

7. Retriever menjalankan semantic search ke Qdrant.
   - Pemanggil: `src/hybrid_retriever.py:348`
   - Implementasi: `search_similar()` di `src/vector_store.py:281`

8. Retriever menjalankan BM25 search.
   - File: `BM25Index.search()` di `src/hybrid_retriever.py:60`

9. Retriever menggabungkan skor dan memilih top-k chunk.
   - File: `src/hybrid_retriever.py:448-489`

10. Pipeline menyusun konteks untuk LLM.
    - File: `build_context()` di `src/rag_pipeline.py:51`

11. Pipeline mengirim prompt ke OpenRouter.
    - File: `src/rag_pipeline.py`, bagian request HTTP di dalam `RAGPipeline.query()`.

12. Pipeline menyusun jawaban dan daftar sumber.
    - File: `extract_referenced_sources()` di `src/rag_pipeline.py:93`

13. Backend mengirim JSON ke frontend.
    - File: `server.py:55`

14. Frontend menampilkan jawaban, filter, dasar hukum, preview sumber, dan skor retrieval.
    - File: `renderResult()` di `static/app.js:121`

## 18. Cara Menjalankan Sistem

Install dependency:

```bash
pip install -r requirements.txt
```

Jalankan pipeline dari awal jika data/index belum ada atau ingin rebuild:

```bash
python run_pipeline.py
```

Jalankan web backend:

```bash
python server.py
```

Buka aplikasi:

```text
http://localhost:5000/
```

Health check:

```text
GET http://localhost:5000/api/health
```

## 19. Catatan Teknis Penting

- Sistem utama saat ini adalah Flask + frontend statis, bukan Streamlit.
- `src/app.py` masih bisa dianggap versi lama/alternatif berbasis Streamlit.
- README masih memiliki beberapa bagian lama yang menyebut Streamlit sebagai cara utama menjalankan aplikasi.
- Qdrant berjalan secara lokal/persistent melalui folder `qdrant_db/`, bukan server Qdrant eksternal.
- Sistem melakukan fallback jika metadata filter terlalu ketat dan tidak menghasilkan dokumen.
- Jawaban LLM tidak dibuat langsung dari database, tetapi dari konteks chunk yang ditemukan retriever.
- Daftar sumber di frontend berasal dari metadata chunk yang sudah disusun di `src/rag_pipeline.py`.

## 20. Ringkasan File dan Tanggung Jawab

| Proses | File Utama | Fungsi/Kelas Utama |
|---|---|---|
| Konfigurasi | `src/config.py` | konstanta path, model, prompt, retrieval, OpenRouter |
| Ekstraksi PDF | `src/pdf_extractor.py` | `extract_all_pdfs()`, `clean_text()` |
| Chunking | `src/chunker.py` | `chunk_all_documents()`, `split_by_pasal()` |
| Embedding | `src/vector_store.py` | `embed_texts()` |
| Vector DB | `src/vector_store.py` | `ensure_collection()`, `index_chunks()`, `search_similar()` |
| BM25 | `src/hybrid_retriever.py` | `BM25Index` |
| Metadata filter | `src/hybrid_retriever.py` | `MetadataFilter` |
| Hybrid retrieval | `src/hybrid_retriever.py` | `HybridRetriever.retrieve()` |
| RAG + LLM | `src/rag_pipeline.py` | `RAGPipeline.query()` |
| API backend | `server.py` | `/api/query`, `/api/stats`, `/api/eval/ragas` |
| Frontend | `static/index.html`, `static/style.css`, `static/app.js` | UI dan request API |
| Retrieval evaluation | `src/evaluation.py` | `compare_methods()` |
| RAGAS evaluation | `src/ragas_evaluation.py` | `run_ragas_evaluation()` |
| Full pipeline script | `run_pipeline.py` | `main()` |

## 21. Kesimpulan

Sistem ini membangun knowledge base regulasi dari PDF, mengubahnya menjadi chunk berbasis pasal, menyimpan representasi vektornya di Qdrant, lalu menggunakan hybrid retrieval untuk mencari pasal yang relevan saat user bertanya. Setelah dokumen relevan ditemukan, sistem menyusun konteks dan mengirimkannya ke LLM melalui OpenRouter agar jawaban akhir lebih rapi, tetap berbasis dokumen, dan dapat ditelusuri kembali ke sumber pasal/regulasi yang digunakan.


