"""
Phase 10 — Streamlit Frontend untuk Hybrid RAG Regulasi Lahan.

Fitur:
- Input pertanyaan
- Tampilkan jawaban LLM
- Tampilkan sumber pasal + dokumen
- Tampilkan skor retrieval
- Filter metadata manual (opsional)
"""

import streamlit as st
import json
import time
from pathlib import Path

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RAG Regulasi Lahan",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-card {
        background-color: #f8f9fa;
        border-left: 4px solid #1E3A5F;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .score-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .score-high { background-color: #d4edda; color: #155724; }
    .score-mid { background-color: #fff3cd; color: #856404; }
    .score-low { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# INITIALIZE SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None


# ============================================================
# LOAD RAG PIPELINE (cached)
# ============================================================

@st.cache_resource(show_spinner=True)
def load_pipeline():
    """Load RAG pipeline (only once)."""
    from .rag_pipeline import RAGPipeline
    return RAGPipeline()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/law.png", width=80)
    st.markdown("### ⚙️ Pengaturan")

    # Retrieval settings
    st.markdown("---")
    st.markdown("**Retrieval**")
    top_k = st.slider("Jumlah dokumen (Top-K)", 3, 10, 5)
    semantic_weight = st.slider("Bobot Semantic", 0.0, 1.0, 0.6, 0.1)
    bm25_weight = 1.0 - semantic_weight
    st.caption(f"Bobot BM25: {bm25_weight:.1f}")

    auto_filter = st.checkbox("Metadata filtering otomatis", value=True)

    # Filter manual
    st.markdown("---")
    st.markdown("**Filter Manual (Opsional)**")
    jenis_options = ["Semua", "UU", "PP", "Perpres", "Permentan", "Permen ATR/BPN", "SE"]
    jenis_filter = st.selectbox("Jenis Regulasi", jenis_options)

    tahun_range = st.slider("Rentang Tahun", 1999, 2025, (1999, 2025))

    # Info
    st.markdown("---")
    st.markdown("**📊 Info Sistem**")
    chunks_file = Path("data/chunks.json")
    if chunks_file.exists():
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)
        st.metric("Total Chunks", len(chunks_data))

        # Hitung dokumen unik
        unique_docs = set(c["metadata"]["dokumen"] for c in chunks_data)
        st.metric("Dokumen Regulasi", len(unique_docs))
    else:
        st.warning("Data chunks belum tersedia")

    st.markdown("---")
    st.markdown(
        "🔧 **Tech Stack**\n"
        "- Embedding: multilingual-e5-small\n"
        "- Vector DB: Qdrant\n"
        "- Search: Hybrid (BM25 + Semantic)\n"
        "- LLM: Gemini 2.5 Flash Lite via OpenRouter API"
    )


# ============================================================
# MAIN CONTENT
# ============================================================

st.markdown('<div class="main-header">📜 Hybrid RAG Regulasi Lahan</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Sistem Tanya-Jawab Regulasi Pertanahan & Perkebunan Indonesia '
    'berbasis Hybrid RAG dengan Metadata Filtering</div>',
    unsafe_allow_html=True
)

# ============================================================
# QUESTION INPUT
# ============================================================

col1, col2 = st.columns([5, 1])

with col1:
    question = st.text_input(
        "💬 Masukkan pertanyaan Anda:",
        placeholder="Contoh: Apakah boleh membuka lahan sawit di kawasan hutan?",
        label_visibility="visible",
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    ask_button = st.button("🔍 Tanya", type="primary", use_container_width=True)

# Contoh pertanyaan
with st.expander("💡 Contoh Pertanyaan", expanded=False):
    example_questions = [
        "Apakah boleh membuka lahan sawit di kawasan hutan?",
        "Apa sanksi jika melanggar izin usaha perkebunan?",
        "Bagaimana prosedur sertifikasi ISPO kelapa sawit?",
        "Apa saja syarat untuk mendapatkan HGU?",
        "Bagaimana aturan peremajaan tanaman kelapa sawit?",
        "Apa kewajiban perusahaan perkebunan terhadap lingkungan?",
        "Bagaimana aturan kemitraan perusahaan dengan petani plasma?",
        "Apa saja jenis izin yang dibutuhkan untuk usaha perkebunan sawit?",
    ]
    for eq in example_questions:
        if st.button(eq, key=f"ex_{eq[:30]}"):
            question = eq
            ask_button = True

# ============================================================
# PROCESS QUESTION
# ============================================================

if ask_button and question:
    # Load pipeline
    with st.spinner("🔄 Memuat model dan pipeline..."):
        pipeline = load_pipeline()

    # Modify retriever weights
    pipeline.retriever.retrieve.__defaults__ = (
        top_k,
        semantic_weight,
        bm25_weight,
        auto_filter,
    )

    # Process
    with st.spinner("🔍 Mencari dokumen relevan dan menghasilkan jawaban..."):
        start_time = time.time()
        result = pipeline.query(
            question,
            top_k=top_k,
            auto_filter=auto_filter,
        )
        elapsed = time.time() - start_time

    # Save to history
    st.session_state.history.append(result)

    # ============================================================
    # DISPLAY ANSWER
    # ============================================================

    st.markdown("---")

    # Metrics row
    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        st.metric("⏱️ Waktu Proses", f"{elapsed:.2f}s")
    with mcol2:
        st.metric("📄 Dokumen Ditemukan", len(result["sources"]))
    with mcol3:
        filters = result.get("metadata_filters", {})
        filter_count = len(filters)
        st.metric("🏷️ Filter Aktif", filter_count)

    # Show active filters
    if filters:
        filter_tags = []
        for k, v in filters.items():
            if isinstance(v, list):
                filter_tags.append(f"**{k}**: {', '.join(v)}")
            else:
                filter_tags.append(f"**{k}**: {v}")
        st.info("🏷️ Filter metadata: " + " | ".join(filter_tags))

    # Answer
    st.markdown("### 💡 Jawaban")
    st.markdown(result["answer"])

    # ============================================================
    # DISPLAY SOURCES
    # ============================================================

    st.markdown("---")
    st.markdown("### 📚 Sumber Dokumen")

    for i, src in enumerate(result["sources"]):
        scores = src["scores"]
        hybrid_score = scores["hybrid"]

        # Score badge color
        if hybrid_score > 0.7:
            badge_class = "score-high"
        elif hybrid_score > 0.4:
            badge_class = "score-mid"
        else:
            badge_class = "score-low"

        with st.expander(
            f"📄 [{i+1}] {src['dokumen']} — {src['pasal']} "
            f"(Skor: {hybrid_score:.4f})",
            expanded=(i == 0)
        ):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"**Jenis:** {src['jenis']}")
            with col_b:
                st.markdown(f"**Tahun:** {src['tahun']}")
            with col_c:
                st.markdown(f"**Topik:** {src['topik']}")

            # Score breakdown
            st.markdown("**Skor Retrieval:**")
            score_cols = st.columns(4)
            with score_cols[0]:
                st.metric("Hybrid", f"{hybrid_score:.4f}")
            with score_cols[1]:
                st.metric("Semantic", f"{scores['semantic']:.4f}")
            with score_cols[2]:
                st.metric("BM25", f"{scores['bm25']:.2f}")
            with score_cols[3]:
                sem_norm = scores.get("semantic_norm", 0)
                bm25_norm = scores.get("bm25_norm", 0)
                st.metric("Sem(norm)", f"{sem_norm:.4f}")

            # Preview text
            st.markdown("**Kutipan:**")
            st.text(src["preview"] + "...")

    # ============================================================
    # DISPLAY RETRIEVAL SCORES TABLE
    # ============================================================

    with st.expander("📊 Detail Skor Retrieval", expanded=False):
        import pandas as pd
        score_data = []
        for i, src in enumerate(result["sources"]):
            s = src["scores"]
            score_data.append({
                "No": i + 1,
                "Dokumen": src["dokumen"],
                "Pasal": src["pasal"],
                "Hybrid": round(s["hybrid"], 4),
                "Semantic": round(s["semantic"], 4),
                "BM25": round(s["bm25"], 2),
                "Sem(norm)": round(s.get("semantic_norm", 0), 4),
                "BM25(norm)": round(s.get("bm25_norm", 0), 4),
            })
        df = pd.DataFrame(score_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================
# HISTORY
# ============================================================

if st.session_state.history:
    st.markdown("---")
    with st.expander("📝 Riwayat Pertanyaan", expanded=False):
        for i, h in enumerate(reversed(st.session_state.history)):
            st.markdown(f"**{len(st.session_state.history) - i}.** {h['question']}")
            st.caption(f"Sumber: {len(h['sources'])} dokumen")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 0.8rem;'>"
    "Hybrid RAG Regulasi Lahan v1.0 | "
    "Skripsi — Sistem Tanya-Jawab Regulasi Pertanahan & Perkebunan"
    "</div>",
    unsafe_allow_html=True
)
