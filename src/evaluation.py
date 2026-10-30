"""
Phase 11 — Evaluation Framework untuk Hybrid RAG.

Evaluasi:
1. Retrieval Accuracy — apakah chunk yang diambil benar/relevan?
2. Answer Correctness — apakah jawaban LLM benar?
3. Perbandingan: Hybrid vs Semantic-only vs BM25-only
"""

import json
import time
import csv
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from .config import DATA_DIR, TOP_K
from .hybrid_retriever import get_retriever, MetadataFilter


# ============================================================
# EVALUATION DATASET
# ============================================================

EVAL_QUESTIONS = [
    {
        "id": 1,
        "question": "Apakah boleh membuka lahan sawit di kawasan hutan lindung?",
        "expected_topics": ["hutan", "kelapa sawit", "lahan"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 41 Tahun 1999 tentang Kehutanan"],
        "ground_truth": "Tidak boleh. Kawasan hutan lindung tidak dapat digunakan untuk kegiatan perkebunan.",
    },
    {
        "id": 2,
        "question": "Apa sanksi pidana bagi pelaku pembakaran lahan perkebunan?",
        "expected_topics": ["sanksi", "pembukaan lahan"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 39 Tahun 2014 tentang Perkebunan"],
        "ground_truth": "Sanksi pidana termasuk penjara dan denda sesuai UU Perkebunan.",
    },
    {
        "id": 3,
        "question": "Apa saja prinsip dan kriteria ISPO?",
        "expected_topics": ["sertifikasi", "kelapa sawit"],
        "expected_jenis": ["Perpres", "Permentan"],
        "expected_docs": ["Perpres No. 44 Tahun 2020 tentang Sertifikasi Perkebunan Kelapa Sawit Berkelanjutan"],
        "ground_truth": "ISPO mencakup prinsip legalitas, manajemen perkebunan, lingkungan, dan tanggung jawab sosial.",
    },
    {
        "id": 4,
        "question": "Berapa luas maksimum lahan perkebunan sawit yang bisa dimiliki satu perusahaan?",
        "expected_topics": ["lahan", "izin usaha", "kelapa sawit"],
        "expected_jenis": ["UU", "Permentan"],
        "expected_docs": ["UU No. 39 Tahun 2014 tentang Perkebunan"],
        "ground_truth": "Luas maksimum diatur dalam peraturan terkait batas luas lahan perkebunan.",
    },
    {
        "id": 5,
        "question": "Bagaimana kewajiban perusahaan perkebunan terhadap plasma/petani?",
        "expected_topics": ["petani", "perkebunan"],
        "expected_jenis": ["UU", "Permentan"],
        "expected_docs": ["UU No. 39 Tahun 2014 tentang Perkebunan"],
        "ground_truth": "Perusahaan wajib memfasilitasi kemitraan dengan pekebun dan masyarakat setempat.",
    },
    {
        "id": 6,
        "question": "Apa saja persyaratan AMDAL untuk usaha perkebunan?",
        "expected_topics": ["lingkungan"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 32 Tahun 2009 tentang Perlindungan dan Pengelolaan Lingkungan Hidup"],
        "ground_truth": "Usaha perkebunan tertentu wajib AMDAL sesuai kriteria yang ditetapkan.",
    },
    {
        "id": 7,
        "question": "Bagaimana mekanisme dana BPDPKS untuk peremajaan sawit rakyat?",
        "expected_topics": ["dana perkebunan", "peremajaan", "kelapa sawit"],
        "expected_jenis": ["Perpres"],
        "expected_docs": ["Perpres No. 61 Tahun 2015 tentang Penghimpunan dan Penggunaan Dana Perkebunan Kelapa Sawit"],
        "ground_truth": "BPDPKS menghimpun dana dari pungutan ekspor CPO untuk peremajaan sawit rakyat.",
    },
    {
        "id": 8,
        "question": "Apa itu kawasan budidaya dan kawasan lindung dalam tata ruang?",
        "expected_topics": ["tata ruang"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 26 Tahun 2007 tentang Penataan Ruang"],
        "ground_truth": "Kawasan budidaya untuk kegiatan ekonomi, kawasan lindung untuk perlindungan alam.",
    },
    {
        "id": 9,
        "question": "Bagaimana aturan penggunaan kawasan hutan untuk kegiatan di luar kehutanan?",
        "expected_topics": ["hutan", "izin usaha"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 41 Tahun 1999 tentang Kehutanan"],
        "ground_truth": "Penggunaan kawasan hutan untuk non-kehutanan memerlukan izin pinjam pakai.",
    },
    {
        "id": 10,
        "question": "Apakah perusahaan sawit wajib menyediakan sarana dan prasarana?",
        "expected_topics": ["perkebunan", "kelapa sawit"],
        "expected_jenis": ["UU", "Permentan"],
        "expected_docs": ["UU No. 39 Tahun 2014 tentang Perkebunan"],
        "ground_truth": "Ya, perusahaan perkebunan wajib menyediakan sarana dan prasarana sesuai regulasi.",
    },
    {
        "id":  11,
        "question": "Bagaimana aturan tentang benih kelapa sawit yang digunakan di perkebunan?",
        "expected_topics": ["kelapa sawit", "perkebunan"],
        "expected_jenis": ["Permentan"],
        "expected_docs": [],
        "ground_truth": "Benih kelapa sawit harus bersertifikat dan berasal dari sumber benih yang diakui.",
    },
    {
        "id": 12,
        "question": "Apa saja larangan dalam usaha perkebunan menurut UU Perkebunan?",
        "expected_topics": ["perkebunan", "sanksi"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 39 Tahun 2014 tentang Perkebunan"],
        "ground_truth": "Larangan meliputi mengerjakan lahan tanpa hak, membakar lahan, dan lainnya.",
    },
    {
        "id": 13,
        "question": "Bagaimana perizinan berusaha di sektor perkebunan menurut UU Cipta Kerja?",
        "expected_topics": ["izin usaha", "perkebunan"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 6 Tahun 2023 tentang Penetapan Perppu Cipta Kerja"],
        "ground_truth": "UU Cipta Kerja menyederhanakan perizinan berusaha di sektor perkebunan.",
    },
    {
        "id": 14,
        "question": "Bagaimana aturan peremajaan tanaman perkebunan kelapa sawit?",
        "expected_topics": ["peremajaan", "kelapa sawit"],
        "expected_jenis": ["Permentan"],
        "expected_docs": ["Permentan No. 18 Tahun 2016 tentang Peremajaan Tanaman Perkebunan"],
        "ground_truth": "Peremajaan dilakukan setelah tanaman melewati masa produktifnya.",
    },
    {
        "id": 15,
        "question": "Apa ketentuan tentang penatagunaan tanah di Indonesia?",
        "expected_topics": ["lahan", "tata ruang"],
        "expected_jenis": ["PP"],
        "expected_docs": ["PP No. 16 Tahun 2004 tentang Penatagunaan Tanah"],
        "ground_truth": "Penatagunaan tanah mengatur penggunaan dan pemanfaatan tanah sesuai rencana tata ruang.",
    },
    {
        "id": 16,
        "question": "Apa saja hak pekebun menurut UU Perkebunan?",
        "expected_topics": ["petani", "perkebunan"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 39 Tahun 2014 tentang Perkebunan"],
        "ground_truth": "Pekebun berhak atas pembinaan, pendampingan, dan akses pembiayaan.",
    },
    {
        "id": 17,
        "question": "Bagaimana aturan tentang konservasi tanah dan air di perkebunan?",
        "expected_topics": ["konservasi", "lingkungan"],
        "expected_jenis": ["UU", "Permentan"],
        "expected_docs": [],
        "ground_truth": "Perkebunan wajib menerapkan teknik konservasi tanah dan air.",
    },
    {
        "id": 18,
        "question": "Apa saja jenis hutan berdasarkan fungsinya menurut UU Kehutanan?",
        "expected_topics": ["hutan"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 41 Tahun 1999 tentang Kehutanan"],
        "ground_truth": "Hutan dibagi menjadi hutan lindung, hutan produksi, dan hutan konservasi.",
    },
    {
        "id": 19,
        "question": "Bagaimana prosedur izin perubahan peruntukan kawasan hutan?",
        "expected_topics": ["hutan", "izin usaha"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 41 Tahun 1999 tentang Kehutanan"],
        "ground_truth": "Perubahan peruntukan kawasan hutan melalui proses RTRWP dan persetujuan DPR.",
    },
    {
        "id": 20,
        "question": "Apa aturan mengenai integrasi sapi-sawit?",
        "expected_topics": ["perkebunan", "kelapa sawit"],
        "expected_jenis": ["Permentan"],
        "expected_docs": ["Permentan No. 105 Tahun 2014"],
        "ground_truth": "Program integrasi sapi-sawit memanfaatkan lahan perkebunan untuk peternakan.",
    },
    {
        "id": 21,
        "question": "Peraturan tentang penyelesaian sengketa lahan perkebunan",
        "expected_topics": ["lahan", "perkebunan"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 39 Tahun 2014 tentang Perkebunan"],
        "ground_truth": "Sengketa lahan perkebunan diselesaikan melalui musyawarah atau pengadilan.",
    },

    {
        "id": 22,
        "question": "Bagaimana aturan mengenai moratorium izin baru di hutan primer?",
        "expected_topics": ["hutan", "moratorium"],
        "expected_jenis": ["Perpres"],
        "expected_docs": [],
        "ground_truth": "Moratorium melarang izin baru di hutan primer dan lahan gambut.",
    },
    {
        "id": 23,
        "question": "Apa kewajiban Pemerintah Daerah dalam pengawasan perkebunan?",
        "expected_topics": ["perkebunan"],
        "expected_jenis": ["UU"],
        "expected_docs": ["UU No. 39 Tahun 2014 tentang Perkebunan"],
        "ground_truth": "Pemda berwenang mengawasi kegiatan usaha perkebunan di wilayahnya.",
    },
    {
        "id": 24,
        "question": "Bagaimana aturan tentang pencegahan kebakaran hutan dan lahan?",
        "expected_topics": ["pembukaan lahan", "lingkungan"],
        "expected_jenis": ["UU"],
        "expected_docs": [],
        "ground_truth": "Setiap orang dilarang membakar hutan dan wajib melakukan pencegahan kebakaran.",
    },
    {
        "id": 25,
        "question": "Apa syarat teknis untuk pembukaan lahan perkebunan baru?",
        "expected_topics": ["pembukaan lahan", "lahan", "izin usaha"],
        "expected_jenis": ["Permentan"],
        "expected_docs": [],
        "ground_truth": "Pembukaan lahan baru harus memenuhi persyaratan teknis termasuk analisis kesesuaian lahan.",
    },
    {
        "id": 26,
        "question": "Bagaimana aturan tentang pengolahan hasil perkebunan kelapa sawit?",
        "expected_topics": ["kelapa sawit", "perkebunan"],
        "expected_jenis": ["UU", "Permentan"],
        "expected_docs": ["UU No. 39 Tahun 2014 tentang Perkebunan"],
        "ground_truth": "Pengolahan hasil perkebunan harus memenuhi standar mutu yang ditetapkan.",
    },
]


# ============================================================
# EVALUATION METRICS
# ============================================================

def evaluate_retrieval_accuracy(results: list[dict], question_data: dict) -> dict:
    """
    Evaluasi akurasi retrieval:
    - Topic Hit Rate: apakah topik yang diharapkan ada di hasil retrieval
    - Document Hit Rate: apakah dokumen yang diharapkan ada di hasil
    - Jenis Match: apakah jenis regulasi cocok
    """
    expected_topics = set(question_data.get("expected_topics", []))
    expected_docs = set(question_data.get("expected_docs", []))
    expected_jenis = set(question_data.get("expected_jenis", []))

    # Kumpulkan topik, dokumen, jenis dari hasil retrieval
    retrieved_topics = set()
    retrieved_docs = set()
    retrieved_jenis = set()

    for r in results:
        meta = r["metadata"]
        # Topik bisa string (comma-separated) atau list
        topik = meta.get("topik", "")
        if isinstance(topik, str):
            for t in topik.split(", "):
                retrieved_topics.add(t.strip())
        elif isinstance(topik, list):
            retrieved_topics.update(topik)

        retrieved_docs.add(meta.get("dokumen", ""))
        retrieved_jenis.add(meta.get("jenis", ""))

    # Hitung hit rates
    topic_hits = len(expected_topics & retrieved_topics)
    topic_hit_rate = topic_hits / len(expected_topics) if expected_topics else 1.0

    doc_hits = len(expected_docs & retrieved_docs)
    doc_hit_rate = doc_hits / len(expected_docs) if expected_docs else 1.0

    jenis_hits = len(expected_jenis & retrieved_jenis)
    jenis_match = jenis_hits / len(expected_jenis) if expected_jenis else 1.0

    return {
        "topic_hit_rate": topic_hit_rate,
        "doc_hit_rate": doc_hit_rate,
        "jenis_match": jenis_match,
        "topic_hits": topic_hits,
        "topic_total": len(expected_topics),
        "doc_hits": doc_hits,
        "doc_total": len(expected_docs),
        "retrieved_topics": list(retrieved_topics),
        "retrieved_docs": list(retrieved_docs),
    }


def run_retrieval_evaluation(
    mode: str = "hybrid",
    top_k: int = TOP_K,
    questions: list[dict] = None,
) -> dict:
    """
    Jalankan evaluasi retrieval untuk semua pertanyaan.
    
    mode: "hybrid" | "semantic" | "bm25"
    """
    if questions is None:
        questions = EVAL_QUESTIONS

    retriever = get_retriever()

    results_all = []
    topic_rates = []
    doc_rates = []
    jenis_rates = []
    latencies = []

    print(f"\n📊 Running {mode.upper()} retrieval evaluation ({len(questions)} questions)...")

    for q in tqdm(questions, desc=f"Evaluating ({mode})"):
        start_time = time.time()

        if mode == "hybrid":
            retrieved = retriever.retrieve(q["question"], top_k=top_k)
        elif mode == "semantic":
            retrieved = retriever.retrieve(
                q["question"], top_k=top_k,
                semantic_weight=1.0, bm25_weight=0.0,
            )
        elif mode == "bm25":
            retrieved = retriever.retrieve(
                q["question"], top_k=top_k,
                semantic_weight=0.0, bm25_weight=1.0,
            )
        else:
            raise ValueError(f"Unknown mode: {mode}")

        elapsed = time.time() - start_time
        latencies.append(elapsed)

        # Evaluate
        metrics = evaluate_retrieval_accuracy(retrieved, q)
        topic_rates.append(metrics["topic_hit_rate"])
        doc_rates.append(metrics["doc_hit_rate"])
        jenis_rates.append(metrics["jenis_match"])

        results_all.append({
            "question_id": q["id"],
            "question": q["question"],
            "mode": mode,
            "latency": elapsed,
            **metrics,
        })

    # Aggregate
    summary = {
        "mode": mode,
        "num_questions": len(questions),
        "avg_topic_hit_rate": sum(topic_rates) / len(topic_rates),
        "avg_doc_hit_rate": sum(doc_rates) / len(doc_rates),
        "avg_jenis_match": sum(jenis_rates) / len(jenis_rates),
        "avg_latency": sum(latencies) / len(latencies),
        "total_latency": sum(latencies),
    }

    return {
        "summary": summary,
        "details": results_all,
    }


def compare_methods(top_k: int = TOP_K) -> dict:
    """
    Bandingkan Hybrid vs Semantic-only vs BM25-only.
    """
    modes = ["hybrid", "semantic", "bm25"]
    all_results = {}

    for mode in modes:
        result = run_retrieval_evaluation(mode=mode, top_k=top_k)
        all_results[mode] = result

    # Print comparison
    print(f"\n{'='*70}")
    print("📊 PERBANDINGAN METODE RETRIEVAL")
    print(f"{'='*70}")
    print(f"{'Metode':<12} {'Topic HR':>10} {'Doc HR':>10} {'Jenis Match':>12} {'Avg Latency':>12}")
    print(f"{'-'*56}")

    for mode in modes:
        s = all_results[mode]["summary"]
        print(
            f"{mode:<12} "
            f"{s['avg_topic_hit_rate']:>10.4f} "
            f"{s['avg_doc_hit_rate']:>10.4f} "
            f"{s['avg_jenis_match']:>12.4f} "
            f"{s['avg_latency']:>11.4f}s"
        )

    return all_results


# ============================================================
# SAVE RESULTS
# ============================================================

def save_evaluation_results(results: dict, filename: str = None):
    """Simpan hasil evaluasi ke file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_{timestamp}.json"

    output_path = DATA_DIR / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Hasil evaluasi disimpan di {output_path}")

    # Juga simpan summary CSV
    csv_path = DATA_DIR / filename.replace(".json", "_summary.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Mode", "Avg Topic HR", "Avg Doc HR", "Avg Jenis Match", "Avg Latency"])
        for mode, data in results.items():
            s = data["summary"]
            writer.writerow([
                mode,
                f"{s['avg_topic_hit_rate']:.4f}",
                f"{s['avg_doc_hit_rate']:.4f}",
                f"{s['avg_jenis_match']:.4f}",
                f"{s['avg_latency']:.4f}",
            ])
    print(f"📊 Summary CSV disimpan di {csv_path}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Bandingkan ketiga metode
    results = compare_methods(top_k=5)

    # Simpan hasil
    save_evaluation_results(results)

    # Detail per pertanyaan untuk hybrid
    print(f"\n{'='*70}")
    print("📋 DETAIL HASIL HYBRID RETRIEVAL")
    print(f"{'='*70}")
    for d in results["hybrid"]["details"]:
        status = "✅" if d["topic_hit_rate"] >= 0.5 else "⚠️"
        print(f"  {status} Q{d['question_id']}: Topic HR={d['topic_hit_rate']:.2f}, "
              f"Doc HR={d['doc_hit_rate']:.2f} | {d['question'][:60]}...")
