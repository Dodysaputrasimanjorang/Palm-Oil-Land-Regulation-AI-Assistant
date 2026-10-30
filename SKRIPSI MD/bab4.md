BAB IV
HASIL DAN PEMBAHASAN

4.1 Gambaran Umum Implementasi Sistem

4.1.1 Deskripsi Sistem

4.1.2 Komponen Utama Sistem

4.1.3 Alur Kerja Sistem End-to-End

4.1.4 Peran Frontend dan Backend

4.1.5 Integrasi Hybrid RAG dalam Sistem

4.2 Hasil Pengolahan Data Regulasi

4.2.1 Kondisi Data Awal

4.2.2 Tahap Ekstraksi Teks PDF

4.2.3 Tahap Pembersihan Teks

4.2.4 Strategi Chunking Regulasi

4.2.5 Penambahan Metadata pada Chunk

4.2.6 Statistik Hasil Pengolahan Data

4.3 Implementasi Metadata Filtering

4.3.1 Konsep Metadata Filtering

4.3.2 Deteksi Metadata dari Pertanyaan

4.3.3 Aturan Filtering Berdasarkan Jenis Regulasi

4.3.4 Aturan Filtering Berdasarkan Topik

4.3.5 Aturan Filtering Berdasarkan Tahun

4.3.6 Dampak Metadata Filtering terhadap Retrieval

4.4 Implementasi Hybrid Retrieval

4.4.1 Konsep Hybrid Retrieval

4.4.2 Semantic Retrieval dengan Qdrant

4.4.3 Keyword Retrieval dengan BM25

4.4.4 Penggabungan Skor Retrieval

4.4.5 Alasan Pemilihan Hybrid Retrieval

4.4.6 Dampak Hybrid Retrieval terhadap Relevansi Konteks

4.5 Penyusunan Konteks dan Generasi Jawaban

4.5.1 Pemilihan Top-K Chunk

4.5.2 Context Building

4.5.3 Penyusunan Prompt untuk LLM

4.5.4 Generasi Jawaban oleh LLM

4.5.5 Pemetaan Jawaban ke Sumber Regulasi

4.6 Hasil Evaluasi Sistem

4.6.1 Metode Evaluasi

4.6.2 Perbandingan Retrieval Antar Metode

4.6.3 Hasil Evaluasi RAGAS

4.6.4 Analisis Nilai Metrik Evaluasi

4.6.5 Interpretasi Kinerja Sistem

4.7 Pembahasan Temuan Utama

4.7.1 Keberhasilan Implementasi Sistem

4.7.2 Kontribusi Preprocessing dan Chunking

4.7.3 Peran Metadata Filtering

4.7.4 Peran Hybrid Retrieval

4.7.5 Kualitas Konteks dan Jawaban

4.7.6 Implikasi Hasil Evaluasi
