# Ringkasan Cepat Seminar Proposal

## 1. Inti sistem dalam 1 kalimat
Sistem ini adalah **Hybrid RAG untuk tanya-jawab regulasi pertanahan dan perkebunan Indonesia** yang mencari pasal relevan dengan **semantic search + BM25**, lalu menyusun jawaban dengan **LLM** dan menampilkan **sumber hukum**.

---

## 2. Alur besar yang harus hafal
1. User bertanya.
2. Sistem membaca pertanyaan.
3. Sistem mengekstrak metadata: jenis regulasi, topik, tahun.
4. Sistem melakukan hybrid retrieval:
   - semantic search untuk makna,
   - BM25 untuk kata kunci.
5. Hasil digabung dan diurutkan.
6. Chunk terbaik dipakai sebagai konteks.
7. LLM menyusun jawaban.
8. Jawaban ditampilkan bersama sumber pasal.

---

## 3. Kenapa metode ini dipakai
### Hybrid Retrieval
Karena:
- **semantic search** bagus untuk memahami makna,
- **BM25** bagus untuk istilah hukum spesifik,
- gabungan keduanya membuat hasil lebih akurat.

### Metadata Filtering
Karena:
- mempersempit pencarian,
- mengurangi noise,
- membuat hasil lebih relevan.

### Chunk per Pasal
Karena:
- struktur hukum memang berbasis pasal,
- sumber lebih mudah dilacak,
- lebih cocok untuk jawaban hukum.

---

## 4. Urutan belajar paling efektif
### Tahap 1: Pahami gambaran umum
Baca:
- README
- docs/system_overview.md
- reports/penjelasan_sistem.md

Target: bisa jelaskan sistem dalam 1 menit.

### Tahap 2: Pahami data masuk
Baca:
- run_pipeline.py
- src/pdf_extractor.py
- src/chunker.py

Target: tahu dari mana dokumen datang dan bagaimana jadi chunk.

### Tahap 3: Pahami retrieval
Baca:
- src/vector_store.py
- src/hybrid_retriever.py

Target: tahu bedanya semantic search, BM25, hybrid, dan metadata filtering.

### Tahap 4: Pahami jawaban akhir
Baca:
- src/rag_pipeline.py
- server.py

Target: tahu bagaimana konteks dikirim ke LLM dan bagaimana jawaban keluar.

### Tahap 5: Pahami tampilan
Baca:
- static/index.html
- static/app.js
- static/style.css

Target: tahu alur user dari frontend ke backend.

---

## 5. Kalimat hafalan 30 detik
"Sistem saya adalah hybrid RAG untuk menjawab pertanyaan regulasi pertanahan dan perkebunan. Dokumen PDF regulasi diekstrak lalu dipecah per pasal dan diberi metadata. Saat user bertanya, sistem melakukan metadata filtering, kemudian hybrid retrieval yang menggabungkan semantic search dan BM25 untuk mencari chunk paling relevan. Chunk terpilih dijadikan konteks untuk LLM, lalu jawaban ditampilkan beserta sumber pasalnya."

---

## 6. Kalimat hafalan 1 menit
"Masalah yang saya angkat adalah sulitnya mencari pasal regulasi yang relevan secara cepat dan akurat. Karena itu saya membangun sistem hybrid RAG untuk regulasi pertanahan dan perkebunan. Dokumen PDF diekstrak, dibersihkan, lalu di-chunk per pasal agar struktur hukumnya tetap terjaga. Setiap chunk diberi metadata seperti jenis regulasi, topik, tahun, dan nomor pasal. Ketika user mengajukan pertanyaan, sistem melakukan metadata filtering untuk mempersempit pencarian, lalu memakai hybrid retrieval yang menggabungkan semantic search dan BM25. Hasil terbaik dipakai sebagai konteks untuk LLM, sehingga jawaban yang dihasilkan tetap berbasis dokumen dan disertai sumber hukum yang jelas."

---

## 7. Pertanyaan dosen yang paling mungkin muncul
### Q1. Kenapa tidak pakai semantic search saja?
Jawab:
Karena semantic search bagus untuk makna, tetapi kurang kuat untuk istilah hukum yang spesifik. BM25 membantu menangkap kata kunci penting.

### Q2. Kenapa harus hybrid?
Jawab:
Karena gabungan semantic dan keyword memberi keseimbangan antara pemahaman konteks dan ketepatan istilah.

### Q3. Kenapa chunk per pasal?
Jawab:
Karena dokumen hukum strukturnya memang pasal. Itu membuat retrieval lebih presisi dan sumber lebih mudah dijelaskan.

### Q4. Kenapa perlu metadata filtering?
Jawab:
Agar pencarian tidak terlalu luas dan hasil retrieval lebih relevan dengan pertanyaan user.

### Q5. Output sistem apa?
Jawab:
Jawaban ringkas berbasis dokumen regulasi, disertai sumber pasal dan dokumen yang dirujuk.

---

## 8. Satu gambar mental yang harus diingat
Pertanyaan user → filter metadata → hybrid search → top chunk → konteks → LLM → jawaban + sumber

---

## 9. Checklist sebelum seminar
- [ ] Bisa jelaskan tujuan sistem
- [ ] Bisa jelaskan alur sistem dari awal sampai akhir
- [ ] Bisa bedakan semantic search, BM25, hybrid search
- [ ] Bisa jelaskan kenapa metadata filtering penting
- [ ] Bisa jelaskan kenapa chunk per pasal
- [ ] Bisa menjawab kenapa sistem ini layak untuk skripsi

---

## 10. Pesan penutup
Kalau kamu hafal 3 hal ini saja, kamu sudah aman:
1. **Apa masalahnya**
2. **Bagaimana sistem bekerja**
3. **Kenapa pendekatannya dipilih**

Itu sudah cukup untuk seminar proposal.
