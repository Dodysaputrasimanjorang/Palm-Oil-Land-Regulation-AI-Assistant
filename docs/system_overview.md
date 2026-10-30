# Sistem Hybrid RAG — Ringkasan Arsitektur dan Alur

Dokumen ini menjelaskan bagaimana input query user diproses hingga menjadi jawaban lengkap dengan sumber, dan memetakan setiap langkah ke berkas sumber di repositori.

## Gambaran Singkat
- Endpoint HTTP menerima query → `RAGPipeline.query()` → `HybridRetriever.retrieve()` → gabungan semantic (Qdrant) + BM25 → pilih top chunks → susun konteks → panggil LLM (OpenRouter) → keluarkan jawaban + daftar sumber yang dirujuk.

## Alur Data (step-by-step)
1. Terima query
   - File: [server.py](server.py)
   - Endpoint: `POST /api/query` mengirim JSON `{ "question": "..." }`.

2. Orkestrasi RAG
   - File: [src/rag_pipeline.py](src/rag_pipeline.py)
   - Fungsi utama: `RAGPipeline.query(question, top_k, auto_filter)`.
   - Tugas: panggil retriever, bangun konteks, panggil LLM, olah jawaban, ekstrak sumber.

3. Ekstraksi metadata dari query (opsional)
   - File: [src/hybrid_retriever.py](src/hybrid_retriever.py)
   - Fungsi: `MetadataFilter.extract_filters(query)` → mendeteksi `jenis`, `topik`, `tahun` untuk memfilter koleksi.

4. Embedding (Text → Vector)
   - File: [src/vector_store.py](src/vector_store.py)
   - Fungsi: `embed_texts(texts, is_query=...)` menggunakan `SentenceTransformer` (model di `EMBEDDING_MODEL` di [src/config.py](src/config.py)).
   - Catatan: embedding dinormalisasi (cosine) — query di-encode dengan `is_query=True`.

5. Pencarian semantik di Vector DB (Qdrant)
   - File: [src/vector_store.py](src/vector_store.py)
   - Fungsi: `search_similar(query, n_results, where)` → meng-embed query, lalu `client.search(...)` di Qdrant.
   - Output: list `ids`, `documents` (teks chunk), `metadatas`, `distances` (dikembalikan dalam format kompatibel).

6. Pencarian kata kunci (BM25)
   - File: [src/hybrid_retriever.py](src/hybrid_retriever.py)
   - Kelas: `BM25Index` membangun indeks dari `data/chunks.json` dan memberikan skor BM25.

7. Penggabungan skor (Hybrid)
   - File: [src/hybrid_retriever.py](src/hybrid_retriever.py)
   - Metode: normalisasi skor semantic + BM25, lalu gabungkan:
     hybrid = SEMANTIC_WEIGHT * semantic_norm + BM25_WEIGHT * bm25_norm
   - Parameter bobot: `SEMANTIC_WEIGHT`, `BM25_WEIGHT`, `TOP_K` di [src/config.py](src/config.py).

8. Penyusunan konteks untuk LLM
   - File: [src/rag_pipeline.py](src/rag_pipeline.py)
   - Fungsi: `build_context(retrieved_chunks)` men-format setiap chunk dengan tag sumber: `--- Dokumen 1 [Sumber: ...] ---` dll.
   - Prompt template: `RAG_USER_PROMPT_TEMPLATE` dan `RAG_SYSTEM_PROMPT` di [src/config.py](src/config.py).

9. Pemanggilan LLM (OpenRouter)
   - File: [src/rag_pipeline.py](src/rag_pipeline.py)
   - Fungsi: `get_llm_client()` + POST ke endpoint OpenRouter chat completions.
   - Hasil: teks jawaban sintetis dari model.

10. Pemetaan jawaban ke sumber yang direferensikan
    - File: [src/rag_pipeline.py](src/rag_pipeline.py)
    - Fungsi: `extract_referenced_sources(answer, sources)` mencari pola "Dokumen N", nama dokumen, atau teks pasal yang disebut LLM dan memetakan ke sumber yang diambil.

11. Respon akhir
    - File: [server.py](server.py)
    - JSON yang dikembalikan meliputi: `question`, `answer`, `sources`, `referenced_sources`, `metadata_filters`, `elapsed`.

## Poin Penting (Teknis & Kebijakan)
- Tidak ada mekanisme "decode vektor ke teks" — vektor hanya untuk pencarian. Teks yang dikembalikan berasal dari payload chunk (disimpan di Qdrant) dan/atau jawaban LLM berdasarkan konteks tersebut.
- Metadata filter dapat mempersempit ruang pencarian (via `where` → diterjemahkan ke Qdrant Filter); jika terlalu ketat, sistem akan fallback ke pencarian tanpa filter.
- Urutan chunk disusun berdasarkan skor semantic sehingga label "Dokumen 1" konsisten untuk chunk paling relevan.
- Prompting diarahkan agar LLM hanya menggunakan informasi dalam konteks dan mencantumkan nama dokumen/pasal persis.

## Parameter yang sering diubah
- [src/config.py](src/config.py): `EMBEDDING_MODEL`, `SEMANTIC_WEIGHT`, `BM25_WEIGHT`, `TOP_K`, `LLM_MODEL`, `LLM_TEMPERATURE`.

## Contoh cara menjalankan dan menguji (lokal)
Jalankan server (virtualenv aktif):

```bash
python server.py
```

Contoh request ke API:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Apa sanksi membuka lahan di kawasan hutan?", "top_k": 5}'
```

Respons akan berisi `answer` dan daftar `referenced_sources`.

## Referensi ke berkas utama
- Orkestrasi HTTP: [server.py](server.py)
- Pipeline & LLM: [src/rag_pipeline.py](src/rag_pipeline.py)
- Hybrid retrieval: [src/hybrid_retriever.py](src/hybrid_retriever.py)
- Vector DB & embedding: [src/vector_store.py](src/vector_store.py)
- Konfigurasi: [src/config.py](src/config.py)

---
Jika Anda ingin, saya bisa:
- Menambahkan diagram alur sederhana (SVG/mermaid) di dokumen.
- Menjalankan contoh query lokal dan menampilkan output pipeline (jika environment tersedia).
- Menyertakan potongan kode kunci dengan nomor baris.

Tandai jika ingin opsi-opsi tersebut ditambahkan.

## Diagram Alur (Mermaid)

```mermaid
flowchart TD
   A[User: Kirim query ke /api/query] --> B[server.py]
   B --> C[RAGPipeline.query()]
   C --> D[MetadataFilter.extract_filters()]
   C --> E[HybridRetriever.retrieve()]
   E --> F[Semantic search (Qdrant) via search_similar()]
   E --> G[BM25 search via BM25Index.search()]
   F --> H[Combine scores (hybrid) dan pilih top-K]
   G --> H
   H --> I[build_context() → susun "Dokumen 1..N"]
   I --> J[LLM (OpenRouter) ← prompt dengan konteks]
   J --> K[Jawaban sintetis dari LLM]
   K --> L[extract_referenced_sources() → peta ke chunks]
   L --> M[server.py: kembalikan JSON response]
```

## Contoh Respons (ringkas)

Contoh JSON yang dikembalikan oleh endpoint `/api/query`:

```json
{
   "question": "Apa sanksi membuka lahan di kawasan hutan?",
   "answer": "Berdasarkan Pasal 12 UU No. 39 Tahun 2014 tentang Perkebunan, ...",
   "sources": [
      {"dokumen":"UU No. 39 Tahun 2014","pasal":"Pasal 12","retrieval_score":0.92},
      {"dokumen":"PP No. X Tahun 2015","pasal":"Pasal 5","retrieval_score":0.76}
   ],
   "referenced_sources": [
      {"dokumen":"UU No. 39 Tahun 2014","pasal":"Pasal 12"}
   ],
   "metadata_filters": {"topik":["lahan"]},
   "elapsed": 1.45
}
```

---
Dokumen ini telah diperbarui dengan diagram alur dan contoh respons.

## Penjelasan Singkat dengan Bahasa Sederhana untuk Seminar Proposal

Berikut versi yang lebih mudah disampaikan secara lisan:

"Sistem ini bekerja seperti asisten pencari informasi. Saat user mengetik pertanyaan, sistem tidak langsung mencari kata yang sama persis, tetapi mengubah pertanyaan itu menjadi representasi angka atau vektor. Vektor ini dipakai untuk mencari dokumen yang maknanya paling mirip. Setelah itu, sistem juga memakai pencarian kata kunci supaya hasilnya lebih tepat. Hasil dari dua pencarian ini digabung, lalu dipilih beberapa bagian dokumen yang paling relevan. Bagian-bagian itu dimasukkan ke model bahasa untuk disusun menjadi jawaban yang rapi. Jadi, alurnya adalah: pertanyaan user → diubah ke vektor → dicari dokumen yang mirip → diambil konteksnya → dijawab oleh model → ditampilkan beserta sumbernya."

### Versi poin-poin yang lebih singkat
- User memasukkan pertanyaan.
- Sistem mengubah pertanyaan menjadi vektor.
- Vektor dipakai untuk mencari dokumen yang mirip di database.
- Sistem juga mencari kata kunci penting dengan BM25.
- Kedua hasil dicampur agar lebih akurat.
- Dokumen terpilih dijadikan konteks untuk model bahasa.
- Model bahasa menyusun jawaban akhir.
- Jawaban ditampilkan bersama sumber dokumennya.

### Kalimat penutup yang bisa dipakai
"Dengan cara ini, sistem saya tidak hanya mencari kata yang sama, tetapi juga memahami makna pertanyaan, sehingga jawaban yang diberikan lebih relevan dan disertai sumber yang jelas."