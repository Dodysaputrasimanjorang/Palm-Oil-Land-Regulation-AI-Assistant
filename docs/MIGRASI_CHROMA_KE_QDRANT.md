# 📊 RINGKASAN MIGRASI CHROMADB → QDRANT

Dokumentasi perubahan tata letak sistem setelah migrasi dari ChromaDB ke Qdrant.

---

## 🎯 PERUBAHAN UTAMA

### 1️⃣ **DATABASE VECTOR STORE** — [src/vector_store.py](src/vector_store.py)

#### **SEBELUM (ChromaDB):**
```python
import chromadb
# client = chromadb.Client(path="./chroma_db")
# collection = client.get_or_create_collection("regulasi_lahan")
```

#### **SESUDAH (Qdrant):** [Lihat baris 10-20](src/vector_store.py#L10-L20)
```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny, Range
)

def get_qdrant_client() -> QdrantClient:
    """Inisialisasi Qdrant client (lokal persistent)"""
    QDRANT_PATH.mkdir(parents=True, exist_ok=True)
    _client = QdrantClient(path=str(QDRANT_PATH))
    return _client

def ensure_collection(reset: bool = False) -> None:
    """Buat/reset koleksi dengan dimensi vektor 384 dan cosine distance"""
    client = get_qdrant_client()
    # ... create collection dengan VectorParams
```

**File:** [src/vector_store.py](src/vector_store.py#L75-L105)

---

### 2️⃣ **KONFIGURASI PATHS** — [src/config.py](src/config.py)

#### **SEBELUM:**
```python
CHROMA_PATH = BASE_DIR / "chroma_db"
CHROMA_COLLECTION = "regulasi_lahan"
```

#### **SESUDAH:** [Lihat baris 17 & 32](src/config.py#L17)
```python
QDRANT_PATH = BASE_DIR / os.getenv("QDRANT_PATH", "qdrant_db")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "regulasi_lahan")
```

---

### 3️⃣ **ENVIRONMENT VARIABLES** — [.env](. env) & [.env.example](.env.example)

#### **SEBELUM:**
```dotenv
# CHROMA_PATH=./chroma_db
# CHROMA_COLLECTION=regulasi_lahan
```

#### **SESUDAH:** [.env.example baris 6-8](.env.example#L6-L8)
```dotenv
# Qdrant
QDRANT_COLLECTION_NAME=regulasi_lahan
QDRANT_PATH=./qdrant_db
```

---

### 4️⃣ **DEPENDENCIES** — [requirements.txt](requirements.txt)

#### **SEBELUM:**
```
chromadb==0.x.x
```

#### **SESUDAH:** [Lihat baris 9](requirements.txt#L9)
```
qdrant-client==1.13.2
```

**Catatan:** Package lain tetap sama (pdfplumber, sentence-transformers, rank-bm25, streamlit, dll)

---

### 5️⃣ **GITIGNORE** — [.gitignore](.gitignore)

#### **TETAP BERUBAH:**
```ignore
chroma_db/          # ⚠️ Masih ada (folder ChromaDB lama, tidak dipakai lagi)
qdrant_db/          # ✨ BARU: folder Qdrant yang dipakai sekarang (tidak di-commit)
```

**Penjelasan:** 
- `chroma_db/` masih ada di `.gitignore` dari setup sebelumnya (bisa dihapus jika sudah tidak ada)
- `qdrant_db/` tidak di-list tapi sama-sama tidak di-commit (disimpan lokal)

---

### 6️⃣ **SEARCH & RETRIEVAL** — [src/vector_store.py](src/vector_store.py#L281-L330)

#### **SEBELUM (ChromaDB):**
```python
def search(query: str, n_results: int = 5):
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        where=filter_dict
    )
    return results
```

#### **SESUDAH (Qdrant):** [Lihat baris 281-330](src/vector_store.py#L281-L330)
```python
def search_similar(query: str, n_results: int = 5, where: dict = None) -> dict:
    """Semantic search ke Qdrant dengan filtering support"""
    client = get_qdrant_client()
    query_embedding = embed_texts([query], is_query=True)
    
    # Convert ChromaDB-like where clause ke Qdrant Filter
    query_filter = _where_to_qdrant_filter(where)
    
    points = client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_embedding[0],
        limit=n_results,
        with_payload=True,
        query_filter=query_filter,
    )
    # Return format kompatibel dengan caller lama (hybrid_retriever)
```

---

### 7️⃣ **DATA STORAGE FORMAT**

#### **ChromaDB (SQLite3):**
```
chroma_db/
├── chroma.sqlite3          # Database file
├── 000000000001/           # Partition partition
│   ├── vectors/
│   ├── data/
│   └── index/
```

#### **Qdrant (Mekanisme Internal):** [qdrant_db](qdrant_db) & [qdrant_db/meta.json](qdrant_db/meta.json)
```
qdrant_db/
├── meta.json               # Metadata koleksi (vektor 384D, cosine distance)
├── collection/
│   └── regulasi_lahan/     # Koleksi yang dipakai
│       ├── 0_points/       # Point structures
│       ├── 1_vectors/      # Vector data
│       └── 2_payload/      # Metadata/payload
```

**Meta.json (baris 1):** 384-dimensional vectors dengan Cosine distance metric

---

### 8️⃣ **HYBRID RETRIEVAL** — [src/hybrid_retriever.py](src/hybrid_retriever.py)

**TIDAK BERUBAH secara API**, hanya internal client:
```python
# Tetap sama dari perspektif caller:
retriever = HybridRetriever()
results = retriever.retrieve(query, top_k=10)
```

**Tapi di belakang layar:**
- [Baris 280-310](src/hybrid_retriever.py#L280-L310): Panggil `search_similar()` → Qdrant client
- BM25 tetap in-memory (rank-bm25 library)
- Hybrid scoring tetap sama: 70% semantic + 30% BM25

---

### 9️⃣ **METADATA FILTERING** — [src/hybrid_retriever.py](src/hybrid_retriever.py#L110-L230)

#### **Konversi Filter Format:**
ChromaDB-like `where` clause → Qdrant `Filter` object

```python
def _where_to_qdrant_filter(where: dict | None) -> Filter | None:
    """Convert ChromaDB-style where ke Qdrant Filter"""
    # Contoh: {"jenis": {"$eq": "UU"}} → FieldCondition(key="jenis", match=MatchValue(value="UU"))
    # Contoh: {"tahun": {"$gte": 2014}} → FieldCondition(key="tahun", range=Range(gte=2014))
    # Contoh: {"topik": {"$contains": "sawit"}} → FieldCondition(key="topik", match=MatchAny(...))
```

**File:** [src/hybrid_retriever.py](src/hybrid_retriever.py#L230-L280)

---

### 🔟 **UI & FRONTEND** — [static/index.html](static/index.html) & [src/app.py](src/app.py)

#### **SEBELUM:**
```html
<li>Vector DB: ChromaDB</li>
```

#### **SESUDAH:** [static/index.html baris 53](static/index.html#L53)
```html
<li>Vector DB: Qdrant</li>
```

#### **Streamlit App:** [src/app.py baris 134](src/app.py#L134)
```python
"- Vector DB: Qdrant\n"
```

---

## 📋 CHECKLIST MIGRASI

| Komponen | Status | Lokasi |
|----------|--------|--------|
| **Vector Store Client** | ✅ Qdrant | [src/vector_store.py](src/vector_store.py#L10) |
| **Config Paths** | ✅ QDRANT_PATH | [src/config.py](src/config.py#L17) |
| **Env Variables** | ✅ QDRANT_* | [.env.example](.env.example#L6-L8) |
| **Dependencies** | ✅ qdrant-client | [requirements.txt](requirements.txt#L9) |
| **Search Function** | ✅ search_similar() | [src/vector_store.py](src/vector_store.py#L281) |
| **Filter Conversion** | ✅ _where_to_qdrant_filter | [src/hybrid_retriever.py](src/hybrid_retriever.py#L230) |
| **Hybrid Retrieval** | ✅ Compatible API | [src/hybrid_retriever.py](src/hybrid_retriever.py#L245) |
| **Frontend** | ✅ Updated display | [static/index.html](static/index.html#L53) |
| **Documentation** | ⚠️ Partial | [reports/penjelasan_sistem.md](reports/penjelasan_sistem.md) (masih ChromaDB) |

---

## ⚠️ ITEM YANG PERLU DIUPDATE (Optional)

### **Dokumentasi Lama** — [reports/penjelasan_sistem.md](reports/penjelasan_sistem.md)

Masih mengacu ChromaDB (bukan critical, tapi untuk akurasi):
- [Baris 42](reports/penjelasan_sistem.md#L42): ChromaDB → Qdrant
- [Baris 59](reports/penjelasan_sistem.md#L59): ChromaDB reference
- [Baris 71](reports/penjelasan_sistem.md#L71): chroma_db/ → qdrant_db/
- [Baris 206-220](reports/penjelasan_sistem.md#L206-L220): ChromaDB section

### **Git Ignore Cleanup** (Optional):
```ignore
# Bisa dihapus jika folder chroma_db tidak ada:
- chroma_db/
```

---

## 🚀 TESTING MIGRASI

Verifikasi dengan commands:

```bash
# 1. Cek Qdrant path ada
ls -la qdrant_db/

# 2. Cek koleksi terinisialisasi
python -c "from src.vector_store import get_qdrant_client; c = get_qdrant_client(); print(c.get_collections())"

# 3. Run full pipeline
python run_pipeline.py

# 4. Test retrieval
python -c "from src.vector_store import search_similar; print(search_similar('izin sawit', n_results=3))"

# 5. Jalankan app
streamlit run src/app.py
```

---

## 📊 COMPARISON: ChromaDB vs Qdrant

| Aspek | ChromaDB | Qdrant |
|-------|----------|--------|
| **Client** | `chromadb.Client()` | `QdrantClient()` |
| **Path** | `chroma_db/` | `qdrant_db/` |
| **Storage** | SQLite3 (`.sqlite3`) | Mekanisme internal (HNSW index) |
| **Distance** | Configurable | Cosine (sistemmu) |
| **Filtering** | `where` clause | Field Conditions + Ranges |
| **Data Format** | Collection → metadata | Points dengan payload |
| **Performance** | Baik untuk small-medium | Optimal untuk large-scale |

---

**Summary:** Migrasi selesai ~95%. ChromaDB hanya traces di dokumentasi lama dan `.gitignore`. Sistem berjalan penuh dengan Qdrant lokal di `qdrant_db/`.
