BAB III
METODE PENELITIAN
3.1 Jenis dan Pendekatan Penelitian 
Penelitian ini termasuk dalam kategori penelitian rekayasa sistem (engineering research) yang berorientasi pada perancangan, pembangunan, dan pengujian sistem tanya jawab regulasi lahan sawit berbasis Hybrid Retrieval-Augmented Generation (Hybrid RAG) dan metadata filtering. Fokus utama penelitian rekayasa sistem pada kajian ini adalah menghasilkan artefak sistem yang dapat diimplementasikan, diuji secara terstruktur, dan dievaluasi performanya untuk menjawab kebutuhan pengguna terhadap akses informasi regulasi yang cepat, relevan, dan dapat ditelusuri sumber hukumnya.
Dari sisi proses, penelitian dilaksanakan melalui tahapan teknis yang sistematis, meliputi identifikasi kebutuhan, perancangan arsitektur, persiapan data regulasi, pengembangan modul retrieval dan generatif, integrasi komponen, serta pengujian kinerja sistem. Dengan demikian, luaran penelitian tidak terbatas pada model konseptual, tetapi mencakup sistem fungsional yang mampu menerima pertanyaan pengguna, melakukan penelusuran dokumen regulasi, dan menghasilkan jawaban berbasis evidensi dokumen.
Selain sebagai penelitian rekayasa sistem, studi ini juga menerapkan eksperimen evaluatif. Pendekatan eksperimen digunakan untuk menilai efektivitas metode yang diusulkan melalui perbandingan beberapa konfigurasi retrieval, yaitu pendekatan hybrid, semantic-only, dan keyword-only. Eksperimen dilakukan pada kumpulan pertanyaan uji yang merepresentasikan kebutuhan informasi regulasi lahan sawit, sehingga hasil evaluasi dapat menunjukkan kontribusi nyata dari kombinasi metode retrieval dan metadata filtering terhadap kualitas jawaban sistem.
Pendekatan analisis yang digunakan adalah kuantitatif, karena kinerja sistem diukur menggunakan indikator numerik yang terdefinisi secara operasional. Pengukuran kuantitatif diarahkan pada aspek ketepatan temu-kembali, relevansi jawaban, kesesuaian jenis dokumen, serta konsistensi rujukan sumber yang digunakan sistem. Pendekatan kuantitatif ini dipilih agar proses penilaian bersifat objektif, terukur, dan dapat direplikasi.
Untuk memperkuat interpretasi hasil numerik, penelitian ini juga didukung oleh analisis deskriptif. Analisis deskriptif digunakan untuk menjelaskan pola hasil pengujian, mengidentifikasi kecenderungan performa tiap metode, serta menafsirkan faktor-faktor yang memengaruhi peningkatan atau penurunan kinerja sistem. Dengan kombinasi analisis kuantitatif dan deskriptif, penelitian ini diharapkan menghasilkan evaluasi yang tidak hanya menunjukkan nilai metrik, tetapi juga memberikan pemahaman yang komprehensif mengenai efektivitas pendekatan Hybrid RAG dan metadata filtering pada domain regulasi lahan sawit.
3.2 Objek Penelitian
	Objek pada penelitian ini adalah pengembangan sistem tanya jawab regulasi lahan sawit berbasis Hybrid Retrieval-Augmented Generation (Hybrid RAG) dengan dukungan metadata filtering. Sistem dirancang untuk memproses pertanyaan pengguna dalam bahasa alami, menelusuri dokumen regulasi yang relevan melalui kombinasi pencarian semantik dan pencarian berbasis kata kunci, kemudian menghasilkan jawaban yang didasarkan pada konteks dokumen serta disertai rujukan sumber hukum. Dengan demikian, objek penelitian tidak hanya mencakup antarmuka tanya jawab, tetapi juga keseluruhan proses pengelolaan dokumen, retrieval, pembentukan konteks, dan generasi jawaban.
Pengguna sistem dalam penelitian ini adalah pihak yang membutuhkan akses cepat terhadap informasi regulasi lahan sawit, seperti mahasiswa, peneliti, praktisi, dan pemangku kepentingan terkait. Sistem diposisikan sebagai alat bantu penelusuran regulasi untuk meningkatkan efisiensi pencarian informasi, bukan sebagai pengganti pendapat hukum resmi. Oleh karena itu, setiap jawaban yang dihasilkan diarahkan untuk tetap terhubung dengan sumber regulasi yang digunakan, agar pengguna dapat melakukan verifikasi lanjutan pada dokumen asli.
Batas domain penelitian difokuskan pada regulasi Indonesia yang berkaitan dengan lahan dan perkebunan sawit, khususnya dokumen yang telah dikurasi dalam korpus penelitian. Cakupan regulasi meliputi beberapa jenis peraturan, seperti Undang-Undang, Peraturan Pemerintah, Peraturan Presiden, dan Peraturan Menteri yang relevan dengan isu pertanahan, perkebunan, kehutanan, tata ruang, dan lingkungan. Pembatasan domain ini bertujuan agar pengembangan sistem tetap terarah, terukur, dan sesuai dengan tujuan penelitian.
Keluaran sistem pada penelitian ini mencakup: (1) jawaban atas pertanyaan pengguna, (2) daftar sumber regulasi yang dirujuk, (3) informasi metadata yang digunakan pada proses filtering, dan (4) informasi pendukung evaluasi retrieval. Ruang lingkup tersebut menegaskan bahwa penelitian berfokus pada peningkatan relevansi dan ketepatan jawaban berbasis dokumen resmi, sekaligus menjaga keterlacakan sumber sebagai unsur penting dalam domain regulasi.

Tabel 3. 1 Ruang Lingkup Objek Penelitian
Komponen	Deskripsi Ruang Lingkup
Objek utama	Sistem tanya jawab regulasi lahan sawit berbasis Hybrid RAG dan metadata filtering
Fokus sistem	Penelusuran dokumen relevan, pembentukan konteks, dan generasi jawaban berbasis LLM
Pengguna	Mahasiswa, peneliti, praktisi, dan pemangku kepentingan yang memerlukan informasi regulasi
Domain kajian	Regulasi lahan/perkebunan sawit di Indonesia
Cakupan dokumen	Regulasi terkurasi (misalnya UU, PP, Perpres, Permen terkait)
Input sistem	Pertanyaan pengguna dalam bahasa alami
Proses inti	Metadata filtering, hybrid retrieval, context construction, generation
Output sistem	Jawaban, sumber regulasi, metadata terkait, dan data pendukung evaluasi
Batas penggunaan	Sistem sebagai alat bantu informasi, bukan keputusan hukum final
3.3 Data Penelitian 
	Data penelitian pada studi ini berupa dokumen regulasi lahan sawit dan regulasi pendukung yang relevan dengan aspek pertanahan, kehutanan, perkebunan, tata ruang, dan lingkungan di Indonesia. Sumber data utama berasal dari dokumen peraturan resmi yang dikumpulkan dalam format PDF, kemudian diproses menjadi korpus teks terstruktur untuk kebutuhan retrieval dan pembangkitan jawaban.
Proses pengumpulan data dilakukan melalui tiga tahap. Tahap pertama adalah akuisisi dokumen, yaitu menghimpun dokumen regulasi dari sumber resmi dan menyimpannya dalam satu repositori data. Tahap kedua adalah seleksi dokumen, yakni memilih hanya regulasi yang memiliki keterkaitan substansial dengan isu lahan sawit, termasuk jenis peraturan yang relevan (UU, PP, Perpres, Permen, dan dokumen pendukung lain yang masih terkait). Tahap ketiga adalah validasi data, yang mencakup pengecekan keterbacaan PDF, kesesuaian metadata dasar (nama dokumen, jenis, tahun), serta verifikasi hasil ekstraksi teks agar dapat diproses pada tahap chunking dan indexing.

Tabel 3. 2 Daftar Dokumen Regulasi yang Digunakan
No	Nama Dokumen	Jenis	Tahun
1	PP No. 3 Tahun 2022 (salinan)	PP	2022
2	PP No. 3 Tahun 2022	PP	2022

Tabel 3. 3 Statistik Data Penelitian
Indikator	Nilai
Jumlah dokumen regulasi	29
Jumlah total chunk hasil pemrosesan	3.276
Jumlah pasangan unik dokumen–pasal/bagian	2.107

	
 
Gambar 3. 1 Alur Pengumpulan dan Persiapan Data

3.3.1 Identifikasi Kebutuhan Data Regulasi
Tahap awal dalam persiapan data adalah mengidentifikasi jenis regulasi yang relevan dengan domain penelitian, yaitu tata kelola lahan sawit di Indonesia. Penulis menentukan kriteria inklusi data mencakup regulasi primer seperti Undang-Undang hingga regulasi teknis seperti Peraturan Menteri guna memastikan sistem memiliki basis pengetahuan yang komprehensif. Identifikasi ini juga melibatkan pemetaan topik-topik krusial seperti izin usaha, hak guna usaha, sertifikasi ISPO, hingga aspek perlindungan lingkungan hidup yang sering menjadi pertanyaan inti bagi para pemangku kepentingan di sektor perkebunan sawit.

3.3.2 Pengumpulan Dokumen Regulasi (PDF)
Penulis melakukan pengumpulan dokumen dalam format PDF melalui berbagai portal resmi digital milik pemerintah seperti Jaringan Dokumentasi dan Informasi Hukum (JDIH). Dokumen-dokumen ini mencakup berbagai hirarki peraturan mulai dari Undang-Undang (UU), Peraturan Pemerintah (PP), Peraturan Presiden (Perpres), hingga Peraturan Menteri (Permen). Kumpulan file PDF ini bertindak sebagai basis data mentah yang nantinya akan ditransformasi menjadi representasi digital yang dapat diolah oleh sistem guna menjamin bahwa setiap jawaban yang dihasilkan memiliki landasan hukum yang sah dan faktual.

3.3.3 Seleksi Dokumen Relevan
Koleksi dokumen yang telah terkumpul kemudian melalui proses seleksi manual yang ketat untuk memastikan relevansi terhadap ruang lingkup penelitian. Penulis hanya menyertakan regulasi yang memiliki kaitan substansial dengan ekosistem kelapa sawit, misalnya regulasi mengenai batasan luas lahan, tata cara peremajaan tanaman (replanting), hingga mekanisme sanksi administratif bagi pelanggar izin perkebunan. Dokumen yang dianggap terlalu umum atau tidak memiliki keterkaitan langsung dengan isu lahan sawit dikeluarkan dari korpus penelitian untuk menjaga efisiensi proses indexing dan akurasi retrieval.

3.3.4 Validasi Dokumen
Validasi dilakukan untuk memeriksa integritas fisik dan digital dari setiap berkas PDF. Penulis memastikan file tidak dalam kondisi rusak (corrupt) dan teks di dalamnya bukan merupakan hasil pemindaian gambar (image-based PDF) yang tidak dapat dibaca, melainkan file PDF berbasis teks yang siap diekstraksi. Selain itu, Penulis melakukan standardisasi penamaan file dan verifikasi metadata dasar seperti nomor peraturan, tahun penerbitan, dan instansi penerbit untuk memastikan identitas unik setiap regulasi terjaga dengan baik dalam basis data sistem.

3.3.5 Ekstraksi Teks dari PDF
Dokumen PDF yang telah lolos validasi kemudian diproses menggunakan modul ekstraktor teks otomatis dengan pemanfaatan pustaka pemrograman seperti pdfplumber atau PyMuPDF. Proses ini melibatkan konversi data biner dari file PDF menjadi rangkaian karakter teks (plain text) yang dapat dipahami secara komputasional. Ekstraksi dilakukan secara menyeluruh tanpa mengabaikan detail kecil, namun tetap mempertahankan urutan logis dari dokumen asli agar struktur paragraf dan kalimat tetap terjaga bagi kebutuhan analisis Natural Language Processing (NLP) selanjutnya.

3.3.6 Pembersihan Teks (Cleaning)
Teks mentah hasil ekstraksi biasanya masih mengandung elemen non-substansial atau noise yang terbawa dari tata letak PDF. Penulis menerapkan algoritma pembersihan untuk menghapus nomor halaman, header, footer, daftar isi, serta simbol-simbol teknis yang tidak memberikan nilai informasi bagi jawaban. Pembersihan ini sangat krusial agar context window pada Large Language Model (LLM) hanya terisi oleh informasi substansial dari regulasi, sehingga meminimalkan risiko halusinasi atau degradasi kualitas jawaban akibat adanya gangguan teks repetitif.

3.3.7 Chunking Dokumen per Pasal/Ayat
Berbeda dengan sistem RAG umum yang melakukan pemotongan teks berdasarkan jumlah karakter yang acak, Penulis menerapkan strategi chunking berbasis struktur hukum yang presisi. Dokumen dibagi menjadi unit-unit kecil berdasarkan Pasal atau Ayat menggunakan pola ekspresi reguler (regex). Pendekatan ini memastikan bahwa setiap unit informasi (chunk) tetap utuh secara makna hukum, memudahkan sistem dalam merujuk sumber secara spesifik, dan memastikan bahwa tidak ada paragraf hukum yang terpotong di tengah kalimat yang dapat mengakibatkan misinterpretasi konteks oleh AI.

3.3.8 Penambahan Metadata
Setiap unit teks (chunk) yang dihasilkan kemudian diperkaya dengan metadata yang bersifat deskriptif dan operasional. Metadata ini mencakup nama lengkap dokumen, jenis peraturan, tahun, nomor pasal, serta klasifikasi topik otomatis (seperti "Izin", "Hutan", atau "Sertifikasi"). Penambahan metadata ini memungkinkan sistem untuk menjalankan fitur metadata filtering yang bekerja secara cerdas dalam memfilter ruang pencarian sebelum proses retrieval dilakukan, sehingga meningkatkan kecepatan dan relevansi temuan dokumen secara signifikan.

3.3.9 Validasi Hasil Chunk dan Metadata
Setelah proses segmentasi dan anotasi selesai, Penulis melakukan verifikasi akhir terhadap integritas dataset yang dihasilkan. Proses ini bertujuan memastikan bahwa setiap chunk telah terhubung dengan metadata yang benar dan tidak terjadi kehilangan data selama proses transformasi dari PDF ke JSON. Validasi ini menjamin bahwa sistem akan selalu memberikan rujukan sumber yang akurat (traceable) ketika pengguna menanyakan dasar hukum tertentu, serta memastikan format data telah sesuai dengan skema input yang dibutuhkan oleh database vektor dan indeks BM25.

3.3.10 Dataset Siap untuk Indexing dan Evaluasi
Tahap akhir dari persiapan data adalah penyimpanan korpus teks yang telah bersih dan terstruktur dalam format JSON. File ini bertindak sebagai "gold standard" yang siap digunakan untuk proses indexing ke Qdrant Vector Database melalui proses embedding, sekaligus diindeks ke dalam mesin pencarian leksikal BM25. Dengan tersedianya dataset yang matang ini, sistem siap memasuki fase operasional untuk melayani permintaan tanya jawab pengguna sekaligus menyediakan basis data yang konsisten untuk kebutuhan eksperimen dan evaluasi metrik kinerja sistem.

3.4 Tahapan Penelitian
	Tahapan penelitian pada studi ini disusun secara sistematis untuk memastikan proses pengembangan sistem tanya jawab regulasi lahan sawit berlangsung terstruktur, terukur, dan dapat direplikasi. Alur penelitian dimulai dari penguatan landasan ilmiah melalui studi literatur, dilanjutkan dengan pengelolaan data regulasi, perancangan dan implementasi sistem berbasis Hybrid RAG, hingga evaluasi performa sistem secara eksperimen. Setiap tahap dirancang memiliki keterkaitan langsung antara input, proses, dan output sehingga kontribusi tiap tahap terhadap hasil akhir dapat dianalisis secara jelas.
Tahap pertama adalah studi literatur dan perumusan masalah, yaitu menelaah penelitian terdahulu terkait NLP, information retrieval, LLM, dan Retrieval-Augmented Generation untuk menentukan celah penelitian serta arah solusi. Tahap kedua adalah pengumpulan dan seleksi data regulasi, dengan fokus pada dokumen yang relevan terhadap lahan sawit. Tahap ketiga adalah validasi dan praproses data, meliputi ekstraksi teks dari PDF, pembersihan noise dokumen, segmentasi teks per pasal/ayat, serta penyusunan metadata dokumen.
Tahap keempat adalah pembangunan basis pencarian, yaitu pembentukan embedding untuk semantic retrieval, pembuatan indeks BM25 untuk keyword retrieval, serta penyimpanan data pada basis vektor. Tahap kelima adalah perancangan dan integrasi modul sistem, mencakup hybrid retrieval, metadata filtering, konstruksi konteks, dan integrasi LLM pada pipeline RAG. Tahap keenam adalah pengujian sistem, dengan skenario pembanding antar metode retrieval (hybrid, semantic-only, BM25-only). Tahap ketujuh adalah evaluasi dan analisis hasil, yaitu menghitung metrik performa, membandingkan hasil antarmetode, dan menginterpretasikan temuan. Tahap terakhir adalah penarikan kesimpulan dan rekomendasi, yang merangkum efektivitas pendekatan yang diusulkan serta ruang pengembangan lanjutan.
Dengan struktur tahapan tersebut, penelitian tidak hanya menghasilkan artefak sistem, tetapi juga menyediakan kerangka evaluasi yang objektif untuk membuktikan pengaruh Hybrid RAG dan metadata filtering terhadap peningkatan relevansi dan keandalan jawaban regulasi.

Tabel 3. 4 Ringkasan Tiap Tahap Penelitian
No	Tahap	Input	Proses	Output
1	Studi literatur	Referensi ilmiah	Kajian teori dan identifikasi gap	Landasan konseptual penelitian
2	Perumusan penelitian	Hasil studi literatur	Menetapkan rumusan masalah, tujuan, batasan	Rancangan penelitian
3	Pengumpulan data	Sumber dokumen regulasi	Akuisisi dokumen PDF	Korpus awal dokumen
4	Seleksi dan validasi data	Korpus awal	Seleksi relevansi, cek keterbacaan dan kelengkapan	Korpus tervalidasi
5	Praproses data	Korpus tervalidasi	Ekstraksi, cleaning, normalisasi, chunking, metadata	Dataset siap indeks
6	Pembangunan basis retrieval	Dataset siap indeks	Embedding, indexing vector DB, indexing BM25	Basis retrieval siap pakai
7	Integrasi sistem	Basis retrieval + desain sistem	Integrasi hybrid retrieval, metadata filtering, LLM	Sistem QA terintegrasi
8	Pengujian dan evaluasi	Sistem terintegrasi + pertanyaan uji	Uji eksperimen dan perhitungan metrik	Hasil performa sistem
9	Analisis dan kesimpulan	Hasil evaluasi	Interpretasi hasil dan perumusan temuan	Kesimpulan penelitian dan rekomendasi

 
Gambar 3. 2 Flowchart Tahapan Penelitian End-to-End

3.4.1 Tahap I: Dasar Ilmiah (Studi Literatur & Perumusan Masalah)
Pada tahap awal penelitian, Penulis melaksanakan studi literatur secara komprehensif untuk membangun kerangka konseptual yang kokoh. Fokus kajian pustaka diarahkan pada perkembangan teknologi *Retrieval-Augmented Generation* (RAG) yang digabungkan dengan teknik *hybrid retrieval* untuk mengatasi limitasi *Large Language Model* (LLM) dalam hal data yang statis dan potensi halusinasi. Penulis menelaah berbagai jurnal ilmiah, dokumentasi teknis pustaka pemrograman, serta penelitian terdahulu mengenai optimasi *vector database* dan pembobotan *Reciprocal Rank Fusion* (RRF). Melalui tahap ini, Penulis berhasil mengidentifikasi celah penelitian pada spesifisitas domain regulasi hukum Indonesia yang memiliki struktur bahasa formal dan hierarkis, yang kemudian mendasari perumusan masalah mengenai bagaimana meningkatkan relevansi jawaban pada domain regulasi lahan sawit dengan bantuan *metadata filtering*.

3.4.2 Tahap II: Data Akuisisi (Pengumpulan & Seleksi Dokumen)
Tahap kedua berfokus pada penghimpunan aset data primer yang akan menjadi basis pengetahuan sistem. Penulis melakukan pengumpulan dokumen regulasi dalam format PDF dari situs-situs resmi pemerintah seperti JDIH dari berbagai kementerian terkait (Kementerian Pertanian, Kementerian ATR/BPN, serta KLHK). Koleksi data tersebut mencakup berbagai level hierarki hukum mulai dari Undang-Undang, Peraturan Pemerintah, hingga Peraturan Menteri. Setelah terkumpul, Penulis melakukan proses seleksi manual untuk memastikan bahwa setiap dokumen memiliki relevansi langsung dengan tata kelola lahan sawit, mencakup aspek perizinan, sertifikasi ISPO, konversi lahan, hingga aspek perlindungan lingkungan. Langkah ini sangat krusial agar korpus data yang terbentuk tidak terkontaminasi oleh informasi yang tidak relevan yang dapat mendegradasi kualitas *retrieval*.

3.4.3 Tahap III: Preprocessing (Ekstraksi, Cleaning & Normalisasi)
Setelah korpus dokumen terkumpul, Penulis melakukan proses *preprocessing* untuk mengubah data tidak terstruktur (PDF) menjadi format yang dapat diolah secara komputasional. Penulis memanfaatkan pustaka *pdfplumber* dan *PyMuPDF* untuk mengekstraksi rangkaian teks mentah dari file PDF. Dalam proses ini, Penulis menghadapi tantangan *noise* seperti teks pada *header*, *footer*, nomor halaman, dan *watermark* yang sering kali mengganggu integritas makna kalimat. Oleh karena itu, Penulis menerapkan algoritma pembersihan teks untuk membuang elemen-elemen tersebut. Selain itu, Penulis melakukan normalisasi teks seperti konversi ke format UTF-8 yang seragam, penghapusan spasi berlebih, dan perbaikan karakter khusus hasil ekstraksi yang tidak sempurna guna memastikan konsistensi data sebelum masuk ke tahap analisis bahasa alami.

3.4.4 Tahap IV: Data Structuring (Chunking & Penyusunan Metadata)
Penulis menyadari bahwa model bahasa memiliki batasan panjang konteks (*context window*), sehingga teks regulasi yang panjang harus dipecah menjadi unit informasi yang lebih kecil. Penulis menerapkan strategi *structural chunking* yang berorientasi pada struktur dokumen hukum Indonesia, yakni membagi teks berdasarkan unit Pasal dan Ayat menggunakan pola ekspresi reguler (*regex*). Pendekatan ini dipilih agar makna hukum dalam setiap potongan teks tetap utuh dan tidak terpotong di tengah kalimat. Bersamaan dengan proses ini, Penulis menyusun metadata secara sistematis untuk setiap *chunk*, yang mencakup identitas unik dokumen, nomor pasal, tahun terbit, jenis peraturan, dan label topik otomatis. Metadata ini nantinya akan berperan vital dalam fitur *filtering* yang memungkinkan sistem melakukan pra-seleksi dokumen berdasarkan kriteria spesifik sebelum proses pencarian vektor dilakukan.

3.4.5 Tahap V: Basis Retrieval (Embedding, Qdrant & BM25)
Pada tahap pembangunan basis pencarian, Penulis menerapkan pendekatan *hybrid indexing* untuk menangkap dua dimensi informasi: semantik dan leksikal. Penulis menggunakan model embedding *intfloat/multilingual-e5-small* untuk mengubah setiap unit teks (chunk) menjadi representasi vektor numerik yang menangkap kedalaman makna kata dalam konteks multibahasa. Vektor-vektor ini kemudian disimpan dan diindeks ke dalam *Vector Database Qdrant*. Di sisi lain, Penulis juga membangun indeks leksikal berbasis algoritma *Best Matching 25* (BM25) untuk menangani kata kunci teknis hukum yang sering kali unik dan spesifik. Dengan tersedianya dua mekanisme indeks ini, sistem memiliki kemampuan ganda untuk memahami pertanyaan pengguna baik secara maknawi maupun secara harfiah kata kunci yang digunakan.

3.4.6 Tahap VI: Integrasi Modul (Hybrid Retrieval & Metadata Filter)
Penulis melakukan integrasi seluruh komponen pencarian ke dalam satu modul orkestrasi *retrieval*. Inovasi utama pada tahap ini adalah penerapan *Metadata Extraction Filter*, di mana sistem secara otomatis menganalisis pertanyaan pengguna untuk mengekstrak parameter seperti tahun peraturan atau jenis peraturan tertentu. Parameter ini digunakan sebagai filter awal untuk mempersempit ruang pencarian dalam *database*, yang secara signifikan meningkatkan efisiensi komputasi. Setelah filter diterapkan, sistem menjalankan *hybrid searching* yang mengambil hasil dari *Qdrant* dan *BM25*, kemudian menggabungkan skor dari kedua metode tersebut menggunakan algoritma *Reciprocal Rank Fusion* (RRF). Proses ini memastikan bahwa dokumen yang muncul di urutan teratas adalah dokumen yang memang memiliki relevansi tinggi dari sudut pandang semantik maupun kesesuaian kata kunci.

3.4.7 Tahap VII: Pipeline RAG (Context Builder, LLM & Tanya Jawab)
Pada tahap ini, Penulis membangun alur kerja *Retrieval-Augmented Generation* yang mengintegrasikan hasil pencarian dengan model bahasa besar. Penulis merancang komponen *Context Builder* yang bertugas menyeleksi Top-K hasil pencarian terbaik dan menyusunnya menjadi sebuah paket konteks yang rapi bersama instruksi khusus (*system prompt*). Konteks ini kemudian dikirimkan ke *Large Language Model* (LLM) melalui antarmuka API Gemini-2.0-Flash. Penulis menerapkan teknik *grounding* yang ketat, di mana LLM diinstruksikan untuk hanya memberikan jawaban berdasarkan informasi yang ada dalam konteks yang diberikan dan dilarang menggunakan pengetahuan eksternal demi menghindari halusinasi rincian hukum. Hasil akhirnya adalah jawaban sistem yang tidak hanya akurat secara bahasa, tetapi juga memiliki landasan hukum yang dapat dipertanggungjawabkan.

3.4.8 Tahap VIII: Uji Eksperimental (Scenario Testing)
Sistem yang telah dibangun kemudian memasuki fase pengujian empiris. Penulis menyusun serangkaian skenario pengujian menggunakan kumpulan pertanyaan uji (query) yang dirancang untuk mewakili berbagai kompleksitas informasi regulasi lahan sawit. Penulis melakukan pengujian komparatif dengan membagi sistem ke dalam tiga konfigurasi berbeda: sistem yang hanya menggunakan pencarian semantik (*semantic-only*), sistem yang hanya menggunakan kata kunci (*BM25-only*), dan sistem usulan yang menggunakan *Hybrid RAG* dengan *metadata filtering*. Pengujian ini dilakukan secara sistematis untuk merekam performa sistem dalam kondisi yang bervariasi, guna mengumpulkan data primer yang akan digunakan pada tahap analisis metrik.

3.4.9 Tahap IX: Analisis Performa (Evaluasi Metrik & Hasil)
Penulis melakukan analisis mendalam terhadap data hasil pengujian yang telah dikumpulkan. Penulis menghitung metrik performa sistem informasi konvensional seperti *Recall* untuk mengukur kelengkapan dokumen yang ditemukan, serta metrik relevansi jawaban LLM melalui proses anotasi atau evaluasi otomatis. Penulis juga menganalisis korelasi antara penerapan *metadata filtering* dengan peningkatan akurasi retrieval dibandingkan tanpa filter. Analisis deskriptif digunakan untuk menjelaskan mengapa kegagalan atau keberhasilan tertentu terjadi pada *query* yang bersifat ambigu. Hasil analisis ini memberikan gambaran objektif mengenai efektivitas metode yang diusulkan dan sejauh mana sistem mampu memenuhi standar akurasi yang dibutuhkan dalam domain regulasi.

3.4.10 Tahap X: Sintesis Akhir (Kesimpulan & Rekomendasi)
Tahap terakhir dalam perjalanan penelitian ini adalah melakukan sintesis menyeluruh atas seluruh temuan yang ada. Penulis merumuskan kesimpulan yang menjawab pertanyaan penelitian dan membuktikan hipotesis mengenai kontribusi positif strategi *Hybrid RAG* dan *metadata filtering* terhadap kualitas sistem tanya jawab regulasi. Penulis juga merefleksikan proses rekayasa sistem yang telah dilakukan untuk mengidentifikasi batasan-batasan teknis yang masih ada. Sebagai penutup, Penulis memberikan rekomendasi strategis bagi pengembang selanjutnya, seperti penambahan jenis regulasi yang lebih luas, integrasi model bahasa yang lebih mutakhir, atau pengembangan antarmuka pengguna yang lebih intuitif, sehingga penelitian ini dapat memberikan manfaat berkelanjutan bagi kemajuan teknologi informasi hukum di Indonesia.

3.5 Perancangan Sistem
	Perancangan sistem pada penelitian ini disusun untuk memastikan proses tanya jawab regulasi lahan sawit berjalan secara terintegrasi, mulai dari penerimaan pertanyaan pengguna hingga penyajian jawaban berbasis sumber regulasi. Arsitektur yang digunakan menerapkan pendekatan modular agar setiap komponen memiliki fungsi yang jelas, mudah dievaluasi, dan dapat dikembangkan pada penelitian lanjutan. Secara konseptual, sistem dibangun dalam dua lapisan utama, yaitu lapisan persiapan data (offline) dan lapisan layanan tanya jawab (online runtime).
Pada lapisan offline, dokumen regulasi dikumpulkan, diekstraksi, dibersihkan, dipecah menjadi unit chunk per pasal/ayat, lalu diperkaya metadata (jenis regulasi, tahun, dokumen, pasal, topik). Data terstruktur ini kemudian diindeks ke dua mekanisme pencarian: basis vektor untuk semantic retrieval dan indeks BM25 untuk keyword retrieval. Pada lapisan online, sistem menerima pertanyaan pengguna, menerapkan metadata filtering, menjalankan hybrid retrieval, membangun konteks jawaban, lalu mengirim konteks tersebut ke LLM untuk menghasilkan jawaban akhir beserta sumber yang dirujuk. Melalui desain ini, kualitas jawaban tidak hanya ditentukan oleh model generatif, tetapi terutama oleh kualitas konteks dokumen hasil retrieval.
Hubungan antar komponen dirancang dengan prinsip orkestrasi terpusat melalui pipeline RAG. Pipeline bertugas mengatur urutan eksekusi modul dan memastikan setiap tahap saling terhubung secara logis: validasi query, filter metadata, retrieval hibrida, ranking, context construction, generation, dan source mapping. Dengan pola ini, sistem dapat menjaga keseimbangan antara ketepatan istilah hukum (keyword retrieval) dan pemahaman semantik (semantic retrieval), sekaligus mempertahankan keterlacakan sumber jawaban.

Tabel 3. 5 Parameter Sistem
No	Modul	Fungsi Utama	Input	Output
1	Frontend Web	Menyediakan antarmuka tanya jawab dan menampilkan hasil	Pertanyaan pengguna	Request ke backend, tampilan jawaban
2	Backend API	Menangani request/response dan memanggil pipeline	Request dari frontend	Respons terstruktur JSON
3	Orkestrator RAG Pipeline	Mengatur urutan proses runtime end-to-end	Pertanyaan tervalidasi	Jawaban final dan sumber
4	Metadata Filtering	Membatasi ruang pencarian berdasarkan atribut regulasi	Query dan metadata indeks	Kandidat dokumen terfilter
5	Semantic Retrieval	Mengambil chunk berdasarkan kemiripan embedding	Query embedding, vector DB	Kandidat semantik + skor
6	Keyword Retrieval BM25	Mengambil chunk berdasarkan kecocokan istilah	Query tokenized, BM25 index	Kandidat keyword + skor
7	Fusi Skor Hybrid	Menggabungkan skor semantic dan BM25	Skor dua retriever	Peringkat final kandidat
8	Context Builder	Menyusun konteks Top-K untuk prompt LLM	Kandidat teratas	Teks konteks terstruktur
9	LLM Generator	Menghasilkan jawaban berbasis konteks dokumen	Prompt sistem + konteks + pertanyaan	Jawaban teks
10	Source Mapping	Mencocokkan jawaban dengan sumber yang dirujuk	Jawaban dan daftar sumber retrieval	Daftar sumber rujukan final
11	PDF Extraction & Cleaning	Ekstraksi teks dan pembersihan noise dokumen	PDF regulasi	Teks bersih
12	Chunking & Metadata	Segmentasi pasal/ayat dan pemberian metadata	Teks bersih	Chunk terstruktur + metadata
13	Embedding & Vector Indexing	Konversi teks ke vektor dan penyimpanan indeks	Chunk terstruktur	Vector DB siap query
14	BM25 Indexing	Pembangunan indeks keyword untuk retrieval leksikal	Teks chunk	Indeks BM25 siap query


 
![Gambar 3.3 Pipeline Metode yang Diusulkan]

3.5.1 Input Pertanyaan Bahasa Alami
Proses *runtime* sistem dimulai ketika pengguna memasukkan pertanyaan dalam bentuk bahasa alami (*natural language*) melalui antarmuka pengguna berbasis web. Pada tahap ini, sistem menerima string teks mentah yang merepresentasikan kebutuhan informasi spesifik pengguna terkait regulasi lahan sawit, misalnya mengenai tata cara perolehan Hak Guna Usaha (HGU) atau persyaratan sertifikasi ISPO. Pertanyaan ini menjadi data input utama yang bersifat dinamis dan tidak terstruktur. Penulis merancang sistem agar mampu menangani variasi semantik dalam kueri, sehingga pengguna tidak perlu menggunakan terminologi hukum yang kaku untuk mendapatkan informasi yang relevan.

3.5.2 Tahap 1: Metadata Filtering (Extraction)
Setelah pertanyaan diterima, sistem menjalankan modul *Metadata Extraction* yang bekerja menggunakan algoritma pencocokan pola dan kamus entitas hukum. Modul ini bertugas mengidentifikasi parameter spesifik seperti tahun peraturan, jenis peraturan (UU, PP, Permen), atau topik hukum utama (seperti "Izin", "Hutan", atau "Sertifikasi") yang tersirat dalam kueri pengguna. Hasil ekstraksi ini ditransformasikan menjadi skema *filtering* yang diterapkan langsung pada *database* sebelum proses pencarian dilakukan. Dengan menerapkan filter di awal (*pre-filtering*), sistem secara drastis mempersempit ruang pencarian (*search space*) hanya pada dokumen yang memenuhi kriteria administratif, yang secara teoritis meningkatkan presisi dan mengurangi beban komputasi pada tahap retrieval semantik yang lebih berat.

3.5.3 Tahap 2: Hybrid Retrieval (Semantic & Lexical Search)
Ruang pencarian yang telah terfilter kemudian diproses secara paralel oleh dua mesin pencari yang berbeda untuk menangkap dua dimensi relevansi yang berbeda. Jalur pertama adalah *Semantic Search* yang memanfaatkan model embedding *intfloat/multilingual-e5-small* untuk merepresentasikan makna kontekstual kueri ke dalam vektor numerik 384 dimensi, yang kemudian dicocokkan dengan vektor dokumen di *Qdrant*. Jalur kedua adalah *Lexical Search* berbasis algoritma BM25 yang menghitung skor berdasarkan frekuensi dan keunikan kata kunci teknis. Kombinasi ini sangat krusial dalam domain hukum, di mana sistem harus mampu memahami maksud pertanyaan yang bersifat general (semantik) sekaligus tetap akurat dalam menemukan istilah-istilah hukum spesifik yang tidak memiliki sinonim (leksikal).

3.5.4 Tahap 3: RRF Fusion (Scoring & Re-ranking)
Hasil dari kedua jalur pencarian (semantik dan leksikal) menghasilkan dua daftar kandidat dokumen yang memiliki skala skor berbeda dan tidak dapat dibandingkan secara langsung. Penulis menerapkan algoritma *Reciprocal Rank Fusion* (RRF) sebagai mekanisme penggabungan skor yang objektif tanpa memerlukan tuning bobot manual. RRF bekerja dengan memberikan bobot pada dokumen berdasarkan posisi peringkatnya (*rank*) di masing-masing metode menggunakan konstanta penyeimbang ($k=60$). Dokumen yang konsisten muncul di peringkat atas pada kedua metode akan mendapatkan skor gabungan tertinggi. Proses ini memastikan bahwa hasil akhir yang diberikan kepada tahap selanjutnya adalah dokumen yang memiliki soliditas baik dari sisi kedekatan makna maupun ketepatan kata kunci.

3.5.5 Tahap 4: Penentuan Konteks Top-K
Setelah peringkat final terbentuk melalui RRF, sistem melakukan seleksi terhadap sejumlah $K$ potongan teks (*chunks*) terbaik yang memiliki skor tertinggi untuk dijadikan sebagai konteks jawaban. Penulis menetapkan batasan jumlah Top-K yang dinamis untuk memastikan bahwa informasi yang dikirimkan ke model bahasa tetap padat dan relevan tanpa menyebabkan fenomena "*lost in the middle*" pada model bahasa. Potongan-potongan teks terpilih ini disusun secara kronologis atau berdasarkan relevansi skor untuk membentuk sebuah narasi konteks yang koheren. Tahap ini bertindak sebagai jembatan informasi yang memastikan bahwa LLM hanya bekerja dengan data yang benar-benar esensial dari korpus regulasi yang ada.

3.5.6 Tahap 5: Generasi Jawaban menggunakan LLM
Konteks Top-K yang telah terpilih kemudian disisipkan ke dalam sebuah *template prompt* yang dirancang secara teliti (*prompt engineering*). Instruksi sistem (*system prompt*) memaksa model bahasa *Gemini-2.0-Flash* untuk berperan sebagai asisten legal virtual yang objektif. Konfigurasi ini mewajibkan model untuk melakukan sintesis informasi hanya dari teks konteks yang diberikan dan dilarang keras menggunakan pengetahuan internal model yang mungkin sudah kedaluwarsa. Penulis memanfaatkan kemampuan penalaran cepat dari Gemini-2.0-Flash untuk menghasilkan jawaban yang tidak hanya akurat secara faktual, tetapi juga menggunakan gaya bahasa formal yang sesuai dengan standar komunikasi hukum di Indonesia.

3.5.7 Output: Jawaban dan Sumber Rujukan
Hasil akhir yang disajikan kepada pengguna adalah jawaban komprehensif yang disusun dalam format yang mudah dipahami. Fitur utama pada output ini adalah penyertaan rujukan sumber (sitasi) secara otomatis untuk setiap poin jawaban yang diberikan. Sistem memetakan metadata identitas dokumen (Nomor, Tahun, dan Pasal) yang melekat pada setiap *chunk* hasil retrieval ke dalam teks jawaban. Hal ini memberikan nilai transparansi tinggi bagi pengguna, memungkinkan verifikasi silang langsung ke dokumen asli, serta memastikan bahwa sistem memenuhi prinsip akuntabilitas informasi dalam konteks penyediaan data regulasi publik.

Tabel 3. 6 Atribut dan Aturan Metadata Filtering

Atribut Filter	Cara Deteksi dari Query	Aturan Penerapan
jenis	Kata kunci: UU, PP, Perpres, Permentan, Permen ATR	Pencarian dibatasi pada jenis regulasi yang sama
topik	Kata kunci topik: sawit, hutan, izin, lingkungan, ISPO, sanksi, peremajaan, dll.	Kandidat diprioritaskan pada metadata topik yang mengandung topik terkait
tahun	Pola “tahun YYYY”	Pencarian dibatasi pada tahun yang sama
tahun_min	Pola rentang tahun awal	Filter (tahun \ge tahun_min)
tahun_max	Pola rentang tahun akhir	Filter (tahun \le tahun_max)


3.8 Lingkungan Implementasi
Lingkungan implementasi pada penelitian ini mencakup perangkat keras dan perangkat lunak yang digunakan untuk menjalankan seluruh tahapan sistem, mulai dari preprocessing dokumen regulasi, indexing, retrieval, hingga generasi jawaban. Implementasi dirancang agar dapat berjalan pada komputer pengembangan standar tanpa ketergantungan wajib pada GPU. Namun, penggunaan GPU tetap dapat meningkatkan kecepatan proses embedding dan inferensi model, terutama saat pemrosesan data berukuran besar.
Dari sisi perangkat keras, komponen utama yang memengaruhi kinerja sistem adalah prosesor, kapasitas RAM, media penyimpanan, dan konektivitas internet untuk akses API model. Dari sisi perangkat lunak, sistem dibangun menggunakan Python dengan dukungan framework backend, library NLP, library retrieval, dan basis data vektor. Seluruh komponen perangkat lunak dipilih berdasarkan kompatibilitas dengan pipeline Hybrid RAG dan kemudahan replikasi eksperimen.

Tabel 3. 7 Spesifikasi Hardware

Komponen	Spesifikasi yang Digunakan/Disarankan
Prosesor (CPU)	Intel Core i5 Gen 12
Memori (RAM)	8 GB
Penyimpanan	512 GB
GPU	Nvidia Geforce RTX 2050
Sistem Operasi	Windows 11 64-bit 
Koneksi Internet	Diperlukan untuk akses API LLM dan sinkronisasi dependensi

Tabel 3. 8 Software, Framework, dan Library yang Digunakan

Kategori	Tools/Library	Fungsi dalam Sistem
Bahasa Pemrograman	Python 3.11	Implementasi seluruh pipeline sistem
Backend API	Flask, Flask-CORS	Menyediakan layanan API untuk query sistem
Frontend Web	HTML, CSS, JavaScript	Antarmuka pengguna berbasis web
Frontend Alternatif	Streamlit	Antarmuka uji/eksperimen cepat
PDF Processing	pdfplumber, PyMuPDF	Ekstraksi teks dari dokumen regulasi PDF
NLP Embedding	sentence-transformers	Pembentukan embedding teks regulasi
Embedding Model	intfloat/multilingual-e5-small	Representasi semantik untuk retrieval
Vector Database	Qdrant	Penyimpanan embedding dan semantic search
Keyword Retrieval	rank-bm25	Pencarian berbasis kata kunci (BM25)
LLM Client	openai (OpenRouter-compatible)	Integrasi model generatif untuk RAG
Data Processing	pandas, numpy	Pengolahan data dan analisis hasil
Evaluasi/ML Utility	scikit-learn	Dukungan evaluasi dan utilitas analitik
Environment	python-dotenv	Manajemen konfigurasi variabel lingkungan
Utility	tqdm	Monitoring progres proses pipeline

3.9 Teknik Analisis Hasil
Teknik analisis hasil pada penelitian ini digunakan untuk menafsirkan keluaran pengujian sistem Hybrid RAG secara terstruktur, objektif, dan sesuai dengan tujuan penelitian. Analisis dilakukan dengan membandingkan hasil pada beberapa skenario pengujian, yaitu hybrid retrieval, semantic-only retrieval, dan keyword-only retrieval (BM25). Hasil pengujian kemudian diinterpretasikan berdasarkan nilai metrik yang diperoleh, sehingga dapat diketahui sejauh mana sistem mampu menemukan dokumen yang relevan, menghasilkan jawaban yang sesuai konteks, dan menjaga keterlacakan sumber regulasi.
Cara interpretasi hasil dilakukan melalui dua pendekatan utama. Pertama, analisis kuantitatif, yaitu membandingkan nilai metrik evaluasi antar metode untuk melihat metode mana yang memberikan performa terbaik. Kedua, analisis deskriptif, yaitu menjelaskan kecenderungan hasil secara naratif, misalnya mengapa suatu metode memperoleh nilai lebih tinggi pada topik tertentu atau mengapa metadata filtering dapat memperbaiki relevansi retrieval. Dengan cara ini, hasil pengujian tidak hanya dibaca sebagai angka, tetapi juga dipahami secara substantif dalam konteks domain regulasi lahan sawit.
Indikator keberhasilan sistem ditentukan berdasarkan tiga aspek utama. Aspek pertama adalah kualitas retrieval, yang menunjukkan apakah dokumen atau chunk yang diambil sesuai dengan kebutuhan pertanyaan. Aspek kedua adalah relevansi jawaban, yang menunjukkan apakah jawaban yang dihasilkan LLM benar-benar selaras dengan konteks regulasi yang diberikan. Aspek ketiga adalah keandalan sumber, yang menunjukkan apakah jawaban dapat ditelusuri kembali ke dokumen regulasi yang valid. Sistem dianggap semakin baik apabila mampu memberikan nilai metrik yang tinggi pada ketiga aspek tersebut secara konsisten.
Secara operasional, hasil penelitian dinyatakan berhasil apabila metode Hybrid RAG menunjukkan performa yang lebih baik atau setidaknya lebih seimbang dibandingkan semantic-only dan BM25-only pada metrik retrieval dan relevansi jawaban. Selain itu, keberhasilan juga dilihat dari kemampuan sistem dalam mempertahankan konteks regulasi yang benar, menampilkan sumber yang sesuai, dan meminimalkan keluaran yang tidak relevan. Dengan demikian, analisis hasil dalam penelitian ini berfungsi untuk membuktikan efektivitas pendekatan yang diusulkan secara terukur dan dapat dipertanggungjawabkan.


Tabel 3. 9 Kriteria Interpretasi Nilai Metrik
Rentang Nilai	Kategori	Interpretasi
0.00 – 0.33	Rendah	Kinerja sistem masih kurang baik dan perlu peningkatan signifikan
0.34 – 0.66	Sedang	Kinerja sistem cukup, tetapi belum optimal
0.67 – 1.00	Tinggi	Kinerja sistem baik dan menunjukkan hasil yang kuat

3.10 Evaluasi dengan RAGAS
Evaluasi kinerja sistem pada penelitian ini dilakukan menggunakan RAGAS (Retrieval-Augmented Generation Assessment), yaitu kerangka evaluasi khusus untuk sistem RAG yang menilai kualitas *retrieval* dan kualitas jawaban secara terintegrasi. RAGAS dipilih karena menyediakan metrik yang berfokus pada keterkaitan jawaban dengan konteks dokumen, sehingga sesuai dengan kebutuhan domain regulasi yang menuntut akurasi dan keterlacakan sumber.
Penilaian dilakukan pada kumpulan pertanyaan uji yang merepresentasikan kebutuhan informasi regulasi lahan sawit. Setiap pertanyaan disertai konteks hasil *retrieval*, jawaban sistem, serta *ground truth* (jawaban acuan) yang disusun dari dokumen regulasi resmi. Dengan data tersebut, RAGAS menghitung skor metrik untuk menilai apakah jawaban relevan, benar terhadap konteks, dan apakah dokumen yang diambil benar-benar mendukung jawaban.

3.10.1 Alasan Penggunaan RAGAS
RAGAS digunakan karena mampu mengevaluasi sistem RAG secara end-to-end, tidak hanya melihat akurasi *retrieval* tetapi juga memeriksa konsistensi jawaban terhadap konteks. Dalam domain regulasi, kesesuaian jawaban dengan pasal dan dokumen sumber sangat krusial. Dengan metrik RAGAS, evaluasi dapat dilakukan secara terukur untuk menilai apakah sistem mampu menyajikan jawaban yang didukung bukti dokumen dan minim halusinasi.

3.10.2 Komponen Evaluasi RAGAS
RAGAS mengevaluasi dua lapisan utama: kualitas *retrieval* dan kualitas jawaban. Pada penelitian ini, metrik yang digunakan mencakup:
(1) *Context Precision* untuk mengukur seberapa banyak konteks yang relevan terhadap pertanyaan.
(2) *Context Recall* untuk mengukur kelengkapan konteks yang seharusnya diambil.
(3) *Answer Relevancy* untuk menilai kesesuaian jawaban dengan pertanyaan.
(4) *Faithfulness* untuk memastikan jawaban benar-benar didukung oleh konteks yang diberikan.
Metrik ini memberikan gambaran menyeluruh tentang performa sistem dari sisi temu-kembali dan kualitas jawaban berbasis dokumen.

3.10.3 Prosedur Evaluasi RAGAS
Prosedur evaluasi dilakukan dengan menyiapkan dataset uji yang berisi: pertanyaan, konteks hasil *retrieval*, jawaban sistem, dan *ground truth*. Dataset ini kemudian dievaluasi menggunakan modul RAGAS untuk menghasilkan skor per metrik. Skor yang diperoleh dianalisis secara kuantitatif dan didukung analisis deskriptif untuk mengidentifikasi pola keberhasilan maupun kegagalan, misalnya pada pertanyaan yang ambigu atau pada regulasi dengan istilah teknis yang spesifik.

3.10.4 Interpretasi Hasil RAGAS
Nilai metrik RAGAS diinterpretasikan mengikuti skala interpretasi pada Tabel 3.9. Skor yang tinggi menunjukkan bahwa sistem berhasil mengambil konteks relevan dan menghasilkan jawaban yang sesuai serta dapat dipertanggungjawabkan secara dokumen. Sebaliknya, skor rendah menjadi indikator perlunya perbaikan pada strategi *retrieval*, konstruksi konteks, atau *prompting* untuk menjaga akurasi jawaban pada domain regulasi.
