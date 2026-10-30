"""
Generate PDF report berisi matrix evaluasi Hybrid RAG Regulasi Lahan.
"""

import json
import sys
from fpdf import FPDF
from pathlib import Path

# Pastikan root project ada di sys.path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Load evaluation data
DATA_DIR = ROOT_DIR / "data"
EVAL_FILE = DATA_DIR / "evaluation_20260216_222921.json"
OUTPUT_DIR = Path(__file__).parent

with open(EVAL_FILE, "r", encoding="utf-8") as f:
    eval_data = json.load(f)


class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Laporan Evaluasi Hybrid RAG - Regulasi Lahan", ln=True, align="C")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 6, "Sistem Retrieval-Augmented Generation untuk Regulasi Pertanahan & Perkebunan Indonesia", ln=True, align="C")
        self.ln(4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Halaman {self.page_no()}/{{nb}}", align="C")


pdf = PDFReport()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# ============================================================
# 1. RINGKASAN PERBANDINGAN METODE
# ============================================================
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "1. Ringkasan Perbandingan Metode Retrieval", ln=True)
pdf.ln(2)

pdf.set_font("Helvetica", "", 9)
pdf.cell(0, 6, "Evaluasi dilakukan terhadap 30 pertanyaan uji terkait regulasi pertanahan dan perkebunan.", ln=True)
pdf.cell(0, 6, "Tiga metode retrieval dibandingkan: Hybrid (Semantic + BM25), Semantic-only, dan BM25-only.", ln=True)
pdf.ln(4)

# Table header
pdf.set_font("Helvetica", "B", 9)
col_widths = [35, 35, 35, 35, 35]
headers = ["Metode", "Topic Hit Rate", "Doc Hit Rate", "Jenis Match", "Avg Latency (s)"]

pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(headers):
    pdf.cell(col_widths[i], 8, h, border=1, align="C", fill=True)
pdf.ln()

# Table data
pdf.set_text_color(0, 0, 0)
modes = ["hybrid", "semantic", "bm25"]
mode_labels = {"hybrid": "Hybrid", "semantic": "Semantic", "bm25": "BM25"}

for mode in modes:
    s = eval_data[mode]["summary"]
    pdf.set_font("Helvetica", "B" if mode == "hybrid" else "", 9)

    if mode == "hybrid":
        pdf.set_fill_color(232, 245, 233)
    else:
        pdf.set_fill_color(255, 255, 255)

    row = [
        mode_labels[mode],
        f"{s['avg_topic_hit_rate']:.4f} ({s['avg_topic_hit_rate']*100:.1f}%)",
        f"{s['avg_doc_hit_rate']:.4f} ({s['avg_doc_hit_rate']*100:.1f}%)",
        f"{s['avg_jenis_match']:.4f} ({s['avg_jenis_match']*100:.1f}%)",
        f"{s['avg_latency']:.4f}",
    ]
    for i, val in enumerate(row):
        pdf.cell(col_widths[i], 7, val, border=1, align="C", fill=True)
    pdf.ln()

pdf.ln(6)

# ============================================================
# 2. PENJELASAN METRIK
# ============================================================
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "2. Penjelasan Metrik Evaluasi", ln=True)
pdf.ln(2)

metrics_info = [
    ("Topic Hit Rate", "Persentase topik yang diharapkan ditemukan dalam hasil retrieval. Semakin tinggi berarti sistem mampu mengambil chunk yang sesuai topik pertanyaan."),
    ("Document Hit Rate", "Persentase dokumen sumber yang diharapkan ditemukan dalam hasil retrieval. Mengukur kemampuan sistem menemukan dokumen regulasi yang tepat."),
    ("Jenis Match", "Persentase kesesuaian jenis regulasi (UU, PP, Perpres, Permentan, dll.) antara yang diharapkan dengan yang ditemukan."),
    ("Average Latency", "Rata-rata waktu (dalam detik) yang dibutuhkan untuk melakukan retrieval per pertanyaan."),
]

for name, desc in metrics_info:
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, f"- {name}:", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, f"  {desc}")
    pdf.ln(1)

pdf.ln(4)

# ============================================================
# 3. DETAIL PER PERTANYAAN (HYBRID)
# ============================================================
pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "3. Detail Evaluasi Per Pertanyaan (Mode Hybrid)", ln=True)
pdf.ln(2)

# Table header
detail_cols = [10, 70, 25, 25, 25, 25]
detail_headers = ["No", "Pertanyaan", "Topic HR", "Doc HR", "Jenis", "Latency"]

pdf.set_font("Helvetica", "B", 8)
pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(detail_headers):
    pdf.cell(detail_cols[i], 7, h, border=1, align="C", fill=True)
pdf.ln()

pdf.set_text_color(0, 0, 0)
pdf.set_font("Helvetica", "", 7)

for d in eval_data["hybrid"]["details"]:
    # Alternate row colors
    if d["question_id"] % 2 == 0:
        pdf.set_fill_color(240, 248, 255)
    else:
        pdf.set_fill_color(255, 255, 255)

    question_text = d["question"]
    if len(question_text) > 55:
        question_text = question_text[:55] + "..."

    row = [
        str(d["question_id"]),
        question_text,
        f"{d['topic_hit_rate']:.2f}",
        f"{d['doc_hit_rate']:.2f}",
        f"{d['jenis_match']:.2f}",
        f"{d['latency']:.3f}s",
    ]

    for i, val in enumerate(row):
        align = "L" if i == 1 else "C"
        pdf.cell(detail_cols[i], 6, val, border=1, align=align, fill=True)
    pdf.ln()

pdf.ln(6)

# ============================================================
# 4. DETAIL PER PERTANYAAN (SEMANTIC)
# ============================================================
pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "4. Detail Evaluasi Per Pertanyaan (Mode Semantic)", ln=True)
pdf.ln(2)

pdf.set_font("Helvetica", "B", 8)
pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(detail_headers):
    pdf.cell(detail_cols[i], 7, h, border=1, align="C", fill=True)
pdf.ln()

pdf.set_text_color(0, 0, 0)
pdf.set_font("Helvetica", "", 7)

for d in eval_data["semantic"]["details"]:
    if d["question_id"] % 2 == 0:
        pdf.set_fill_color(240, 248, 255)
    else:
        pdf.set_fill_color(255, 255, 255)

    question_text = d["question"]
    if len(question_text) > 55:
        question_text = question_text[:55] + "..."

    row = [
        str(d["question_id"]),
        question_text,
        f"{d['topic_hit_rate']:.2f}",
        f"{d['doc_hit_rate']:.2f}",
        f"{d['jenis_match']:.2f}",
        f"{d['latency']:.3f}s",
    ]
    for i, val in enumerate(row):
        align = "L" if i == 1 else "C"
        pdf.cell(detail_cols[i], 6, val, border=1, align=align, fill=True)
    pdf.ln()

pdf.ln(6)

# ============================================================
# 5. DETAIL PER PERTANYAAN (BM25)
# ============================================================
pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "5. Detail Evaluasi Per Pertanyaan (Mode BM25)", ln=True)
pdf.ln(2)

pdf.set_font("Helvetica", "B", 8)
pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(detail_headers):
    pdf.cell(detail_cols[i], 7, h, border=1, align="C", fill=True)
pdf.ln()

pdf.set_text_color(0, 0, 0)
pdf.set_font("Helvetica", "", 7)

for d in eval_data["bm25"]["details"]:
    if d["question_id"] % 2 == 0:
        pdf.set_fill_color(240, 248, 255)
    else:
        pdf.set_fill_color(255, 255, 255)

    question_text = d["question"]
    if len(question_text) > 55:
        question_text = question_text[:55] + "..."

    row = [
        str(d["question_id"]),
        question_text,
        f"{d['topic_hit_rate']:.2f}",
        f"{d['doc_hit_rate']:.2f}",
        f"{d['jenis_match']:.2f}",
        f"{d['latency']:.3f}s",
    ]
    for i, val in enumerate(row):
        align = "L" if i == 1 else "C"
        pdf.cell(detail_cols[i], 6, val, border=1, align=align, fill=True)
    pdf.ln()

pdf.ln(6)

# ============================================================
# 6. CONFUSION-STYLE MATRIX: Dokumen Retrieved vs Expected
# ============================================================
pdf.add_page()
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "6. Matrix Dokumen: Expected vs Retrieved (Hybrid)", ln=True)
pdf.ln(2)

pdf.set_font("Helvetica", "", 9)
pdf.cell(0, 6, "Tabel berikut menunjukkan dokumen yang diharapkan vs yang berhasil ditemukan per pertanyaan.", ln=True)
pdf.ln(3)

# Compact table
matrix_cols = [10, 55, 60, 60]
matrix_headers = ["No", "Pertanyaan", "Expected Doc", "Retrieved Docs (Top 3)"]

pdf.set_font("Helvetica", "B", 7)
pdf.set_fill_color(41, 128, 185)
pdf.set_text_color(255, 255, 255)
for i, h in enumerate(matrix_headers):
    pdf.cell(matrix_cols[i], 7, h, border=1, align="C", fill=True)
pdf.ln()

pdf.set_text_color(0, 0, 0)
pdf.set_font("Helvetica", "", 6)

# Load evaluation questions for expected docs
from src.evaluation import EVAL_QUESTIONS

for idx, d in enumerate(eval_data["hybrid"]["details"]):
    q_data = EVAL_QUESTIONS[idx]
    expected = ", ".join(q_data.get("expected_docs", [])) or "-"
    retrieved = ", ".join(d.get("retrieved_docs", [])[:3]) or "-"

    if len(expected) > 50:
        expected = expected[:50] + "..."
    if len(retrieved) > 50:
        retrieved = retrieved[:50] + "..."

    question_text = d["question"]
    if len(question_text) > 42:
        question_text = question_text[:42] + "..."

    if d["question_id"] % 2 == 0:
        pdf.set_fill_color(240, 248, 255)
    else:
        pdf.set_fill_color(255, 255, 255)

    # Color code: green if doc found, red if not
    hit = d["doc_hit_rate"]

    pdf.cell(matrix_cols[0], 6, str(d["question_id"]), border=1, align="C", fill=True)
    pdf.cell(matrix_cols[1], 6, question_text, border=1, align="L", fill=True)
    pdf.cell(matrix_cols[2], 6, expected, border=1, align="L", fill=True)

    if hit >= 1.0:
        pdf.set_text_color(0, 128, 0)
    elif hit > 0:
        pdf.set_text_color(200, 150, 0)
    else:
        pdf.set_text_color(200, 0, 0)

    pdf.cell(matrix_cols[3], 6, retrieved, border=1, align="L", fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln()

pdf.ln(4)
pdf.set_font("Helvetica", "I", 7)
pdf.set_text_color(0, 128, 0)
pdf.cell(5, 5, "", fill=False)
pdf.cell(30, 5, "= Doc ditemukan", ln=False)
pdf.set_text_color(200, 0, 0)
pdf.cell(30, 5, "= Doc tidak ditemukan", ln=True)
pdf.set_text_color(0, 0, 0)

# ============================================================
# 7. KESIMPULAN
# ============================================================
pdf.ln(6)
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 10, "7. Kesimpulan", ln=True)
pdf.ln(2)

pdf.set_font("Helvetica", "", 9)

hybrid_s = eval_data["hybrid"]["summary"]
semantic_s = eval_data["semantic"]["summary"]
bm25_s = eval_data["bm25"]["summary"]

conclusions = [
    f"1. Mode Hybrid mencapai Topic Hit Rate {hybrid_s['avg_topic_hit_rate']*100:.1f}%, "
    f"Doc Hit Rate {hybrid_s['avg_doc_hit_rate']*100:.1f}%, dan Jenis Match {hybrid_s['avg_jenis_match']*100:.1f}%.",

    f"2. Mode Semantic mencapai Topic Hit Rate {semantic_s['avg_topic_hit_rate']*100:.1f}%, "
    f"Doc Hit Rate {semantic_s['avg_doc_hit_rate']*100:.1f}%, dan Jenis Match {semantic_s['avg_jenis_match']*100:.1f}%.",

    f"3. Mode BM25 mencapai Topic Hit Rate {bm25_s['avg_topic_hit_rate']*100:.1f}%, "
    f"Doc Hit Rate {bm25_s['avg_doc_hit_rate']*100:.1f}%, dan Jenis Match {bm25_s['avg_jenis_match']*100:.1f}%.",

    "4. Metode Hybrid menunjukkan keseimbangan terbaik antara ketiga metrik evaluasi, "
    "menggabungkan kekuatan semantic search (pemahaman makna) dengan BM25 (pencocokan keyword).",

    f"5. Rata-rata latency untuk semua metode sangat rendah (< 0.15 detik), "
    f"menunjukkan sistem responsif untuk penggunaan real-time.",
]

for c in conclusions:
    pdf.multi_cell(0, 5, c)
    pdf.ln(2)

# ============================================================
# SAVE PDF
# ============================================================
output_path = OUTPUT_DIR / "evaluation_matrix_report.pdf"
pdf.output(str(output_path))
print(f"PDF berhasil dibuat: {output_path}")
