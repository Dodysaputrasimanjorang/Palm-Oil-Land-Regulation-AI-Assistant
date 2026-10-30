"""
Flask API Backend untuk Hybrid RAG Regulasi Lahan.
Menggantikan Streamlit, menyediakan REST API untuk frontend HTML/JS/CSS.
"""

import json
import time
import math
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from src.config import DATA_DIR, TOP_K, SEMANTIC_WEIGHT, BM25_WEIGHT

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# ============================================================
# LAZY-LOAD RAG PIPELINE (load saat request pertama)
# ============================================================

_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        print("🔄 Loading RAG Pipeline (first request)...")
        from src.rag_pipeline import RAGPipeline
        _pipeline = RAGPipeline()
    return _pipeline


def _json_safe(value):
    """Recursively convert non-JSON-safe numeric values (NaN/Inf) to 0.0."""
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return 0.0
    return value


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    """Serve the main HTML page."""
    return send_from_directory("static", "index.html")


@app.route("/api/query", methods=["POST"])
def api_query():
    """
    Main RAG query endpoint.

    Request JSON:
        { "question": "...", "top_k": 5, "auto_filter": true }
    
    Response JSON:
        { "question", "answer", "sources", "metadata_filters", "elapsed" }
    """
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Field 'question' wajib diisi."}), 400

    question = data["question"].strip()
    if not question:
        return jsonify({"error": "Pertanyaan tidak boleh kosong."}), 400

    top_k = data.get("top_k", TOP_K)
    auto_filter = data.get("auto_filter", True)

    pipeline = get_pipeline()

    start = time.time()
    result = pipeline.query(question, top_k=top_k, auto_filter=auto_filter)
    elapsed = round(time.time() - start, 2)

    return jsonify({
        "question": result["question"],
        "answer": result["answer"],
        "sources": result["sources"],
        "referenced_sources": result.get("referenced_sources", result["sources"]),
        "metadata_filters": result.get("metadata_filters", {}),
        "elapsed": elapsed,
    })


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Return system statistics."""
    chunks_file = DATA_DIR / "chunks.json"
    if not chunks_file.exists():
        return jsonify({"total_chunks": 0, "total_docs": 0, "docs": []})

    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    doc_set = {}
    pasal_set = set()
    for c in chunks:
        meta = c["metadata"]
        doc_name = meta["dokumen"]
        if doc_name not in doc_set:
            doc_set[doc_name] = {
                "dokumen": doc_name,
                "jenis": meta["jenis"],
                "tahun": meta["tahun"],
                "chunks": 0,
            }
        doc_set[doc_name]["chunks"] += 1
        # Track unique pasal per dokumen
        pasal_set.add((doc_name, meta.get("pasal", "")))

    docs_list = sorted(doc_set.values(), key=lambda d: d["tahun"], reverse=True)

    return jsonify({
        "total_chunks": len(chunks),
        "total_docs": len(doc_set),
        "total_pasal": len(pasal_set),
        "docs": docs_list,
    })


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok"})


@app.route("/api/eval/ragas", methods=["POST"])
def api_eval_ragas():
    """Run RAGAS evaluation and return summary + per-question details."""
    data = request.get_json(silent=True) or {}

    sample_size = int(data.get("sample_size", 5))
    top_k = int(data.get("top_k", TOP_K))
    auto_filter = bool(data.get("auto_filter", True))

    if sample_size <= 0:
        return jsonify({"error": "sample_size harus lebih besar dari 0."}), 400

    try:
        from src.ragas_evaluation import run_ragas_evaluation, save_ragas_results

        pipeline = get_pipeline()
        start = time.time()
        results = run_ragas_evaluation(
            pipeline=pipeline,
            sample_size=sample_size,
            top_k=top_k,
            auto_filter=auto_filter,
        )
        elapsed = round(time.time() - start, 2)
        saved_files = {}
        save_warning = ""
        try:
            saved_files = save_ragas_results(results)
        except Exception as save_exc:
            save_warning = f"Hasil evaluasi tampil, tetapi gagal disimpan ke file: {save_exc}"

        payload = _json_safe({
            "summary": results.get("summary", {}),
            "details": results.get("details", []),
            "generated_at": results.get("generated_at", ""),
            "elapsed": elapsed,
            "files": saved_files,
            "warning": save_warning,
        })
        return jsonify(payload)
    except Exception as exc:
        return jsonify({
            "error": f"Evaluasi RAGAS gagal: {str(exc)}"
        }), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Pre-load pipeline on startup
    get_pipeline()
    app.run(host="0.0.0.0", port=5000, debug=False)
