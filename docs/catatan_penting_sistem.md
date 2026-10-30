# Catatan Penting Sistem Hybrid RAG Regulasi Lahan

## Ringkas Sistem
Sistem ini adalah tanya jawab regulasi pertanahan dan perkebunan Indonesia berbasis Hybrid RAG (Retrieval-Augmented Generation) dengan metadata filtering. Tujuannya memberikan jawaban berbasis pasal yang jelas dan dapat dirujuk sumbernya.

## Teknologi dan Komponen Inti
- Backend API: Flask untuk endpoint query, statistik, dan evaluasi.
- Pipeline RAG: orkestrasi retrieval, konteks, pemanggilan LLM, dan ekstraksi sumber.
- Hybrid Retrieval: gabungan semantic search (Qdrant) dan keyword search (BM25).
- Vector DB: Qdrant untuk penyimpanan embedding dan pencarian semantik.
- LLM: OpenRouter untuk menghasilkan jawaban final berbasis konteks.
- Data: PDF regulasi diproses menjadi chunk per pasal agar presisi.

## Alur Kerja End-to-End
1. User mengirim pertanyaan ke endpoint /api/query.
2. Sistem mengekstrak filter metadata (jenis, topik, tahun) jika tersedia.
3. Pertanyaan diubah ke embedding untuk semantic search di Qdrant.
4. BM25 melakukan pencarian kata kunci pada kumpulan chunk.
5. Skor semantic dan BM25 dinormalisasi lalu digabung dengan bobot.
6. Top-K chunk dipilih dan disusun sebagai konteks.
7. Prompt dikirim ke LLM (OpenRouter) untuk menyusun jawaban.
8. Sistem memetakan jawaban ke sumber pasal yang relevan.
9. Respons JSON dikembalikan berisi jawaban dan daftar sumber.

## Fitur Utama dan Penjelasannya
- Hybrid Retrieval: menyeimbangkan akurasi semantic dengan ketepatan keyword agar hasil lebih stabil.
- Metadata Filtering: menyempitkan ruang pencarian supaya lebih relevan dan cepat.
- Chunking per pasal: memudahkan penelusuran ke pasal sumber dan meningkatkan presisi.
- Citation atau sumber: jawaban selalu membawa rujukan pasal dan dokumen.
- Evaluasi RAGAS: mengukur kualitas retrieval dan jawaban secara terukur.

## Aturan dan Penanganan Ukuran Chunk
- Target chunk adalah per pasal atau per ayat agar konteks tetap utuh namun fokus.
- Jika chunk terlalu panjang, pecah berdasarkan struktur alami (ayat, huruf a/b/c, atau sub-pasal).
- Jika chunk terlalu pendek, gabungkan dengan bagian terdekat yang masih satu topik.
- Rentang ukuran praktis: 300 sampai 700 token per chunk untuk menjaga presisi dan konteks.
- Dampak kualitas: terlalu panjang menurunkan relevansi, terlalu pendek membuat jawaban kurang konteks.

## Output Sistem
Output utama adalah jawaban berbasis dokumen regulasi beserta daftar sumber pasal, metadata filter yang dipakai, dan waktu eksekusi.

## Catatan Penting untuk Presentasi
Sistem ini tidak mengarang jawaban di luar konteks. LLM hanya menyusun jawaban dari potongan regulasi yang ditemukan oleh hybrid retrieval, sehingga jawaban dapat dipertanggungjawabkan.
