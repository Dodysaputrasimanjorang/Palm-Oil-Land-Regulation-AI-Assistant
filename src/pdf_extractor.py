"""
Phase 2 & 3 — Ekstraksi teks dari PDF regulasi + cleaning.
Mendukung pdfplumber dan PyMuPDF.
"""

import re
import json
from pathlib import Path
from tqdm import tqdm
import pdfplumber
import fitz  # PyMuPDF

from .config import PDF_DIR, DATA_DIR, PDF_EXTRACTION_METHOD


# ============================================================
# METADATA MAPPING — identifikasi info dokumen dari nama file
# ============================================================

DOCUMENT_METADATA = {
    "39TAHUN2014UU.pdf": {
        "dokumen": "UU No. 39 Tahun 2014 tentang Perkebunan",
        "jenis": "UU",
        "tahun": 2014,
        "topik_utama": ["perkebunan", "izin usaha", "lahan perkebunan"],
    },
    "UU Nomor 41 Tahun 1999.pdf": {
        "dokumen": "UU No. 41 Tahun 1999 tentang Kehutanan",
        "jenis": "UU",
        "tahun": 1999,
        "topik_utama": ["kehutanan", "kawasan hutan", "izin pemanfaatan hutan"],
    },
    "UU 32 Tahun 2009 (PPLH).pdf": {
        "dokumen": "UU No. 32 Tahun 2009 tentang Perlindungan dan Pengelolaan Lingkungan Hidup",
        "jenis": "UU",
        "tahun": 2009,
        "topik_utama": ["lingkungan hidup", "AMDAL", "izin lingkungan"],
    },
    "UU Nomor 26 Tahun 2007.pdf": {
        "dokumen": "UU No. 26 Tahun 2007 tentang Penataan Ruang",
        "jenis": "UU",
        "tahun": 2007,
        "topik_utama": ["tata ruang", "perencanaan ruang", "pemanfaatan ruang"],
    },
    "uu-no-6-tahun-2023.pdf": {
        "dokumen": "UU No. 6 Tahun 2023 tentang Penetapan Perppu Cipta Kerja",
        "jenis": "UU",
        "tahun": 2023,
        "topik_utama": ["cipta kerja", "perizinan berusaha", "omnibus law"],
    },
    "03-20222.pdf": {
        "dokumen": "PP No. 3 Tahun 2022",
        "jenis": "PP",
        "tahun": 2022,
        "topik_utama": ["peraturan pemerintah"],
    },
    "03-20222 (1).pdf": {
        "dokumen": "PP No. 3 Tahun 2022 (salinan)",
        "jenis": "PP",
        "tahun": 2022,
        "topik_utama": ["peraturan pemerintah"],
    },
    "PP No. 16 Thn 2004.pdf": {
        "dokumen": "PP No. 16 Tahun 2004 tentang Penatagunaan Tanah",
        "jenis": "PP",
        "tahun": 2004,
        "topik_utama": ["penatagunaan tanah", "penggunaan tanah"],
    },
    "2015_Perpres_Nomor_61_Tahun_20151.pdf": {
        "dokumen": "Perpres No. 61 Tahun 2015 tentang Penghimpunan dan Penggunaan Dana Perkebunan Kelapa Sawit",
        "jenis": "Perpres",
        "tahun": 2015,
        "topik_utama": ["dana perkebunan", "kelapa sawit", "BPDPKS"],
    },
    "2016_Perpres_Nomor_24_Tahun_20161.pdf": {
        "dokumen": "Perpres No. 24 Tahun 2016 (Perubahan Perpres 61/2015)",
        "jenis": "Perpres",
        "tahun": 2016,
        "topik_utama": ["dana perkebunan", "kelapa sawit"],
    },
    "2018_Perpres_Nomor_66_Tahun_20181.pdf": {
        "dokumen": "Perpres No. 66 Tahun 2018 (Perubahan Kedua Perpres 61/2015)",
        "jenis": "Perpres",
        "tahun": 2018,
        "topik_utama": ["dana perkebunan", "kelapa sawit"],
    },
    "2020_Perpres_Nomor_44_Tahun_20201.pdf": {
        "dokumen": "Perpres No. 44 Tahun 2020 tentang Sertifikasi Perkebunan Kelapa Sawit Berkelanjutan",
        "jenis": "Perpres",
        "tahun": 2020,
        "topik_utama": ["sertifikasi ISPO", "kelapa sawit berkelanjutan"],
    },
    "Permentan_17-20101.pdf": {
        "dokumen": "Permentan No. 17 Tahun 2010",
        "jenis": "Permentan",
        "tahun": 2010,
        "topik_utama": ["pedoman perkebunan"],
    },
    "Permentan_11-2015_ISPO.pdf": {
        "dokumen": "Permentan No. 11 Tahun 2015 tentang ISPO",
        "jenis": "Permentan",
        "tahun": 2015,
        "topik_utama": ["ISPO", "sertifikasi sawit", "kelapa sawit berkelanjutan"],
    },
    "Permentan_No_105_Tahun_2014.pdf": {
        "dokumen": "Permentan No. 105 Tahun 2014",
        "jenis": "Permentan",
        "tahun": 2014,
        "topik_utama": ["integrasi sapi-sawit", "perkebunan"],
    },
    "Permentan_18-2016_Peremajaan_Kelapa_Sawit_Sawit.pdf": {
        "dokumen": "Permentan No. 18 Tahun 2016 tentang Peremajaan Tanaman Perkebunan",
        "jenis": "Permentan",
        "tahun": 2016,
        "topik_utama": ["peremajaan", "replanting", "kelapa sawit"],
    },
    "Permentan_36_Tahun_2019.pdf": {
        "dokumen": "Permentan No. 36 Tahun 2019",
        "jenis": "Permentan",
        "tahun": 2019,
        "topik_utama": ["perkebunan"],
    },
    "Permentan_38_Tahun_2020.pdf": {
        "dokumen": "Permentan No. 38 Tahun 2020",
        "jenis": "Permentan",
        "tahun": 2020,
        "topik_utama": ["perkebunan"],
    },
    "Permentan_Nomor_19_Tahun_2023_share_JDIH.pdf": {
        "dokumen": "Permentan No. 19 Tahun 2023",
        "jenis": "Permentan",
        "tahun": 2023,
        "topik_utama": ["perkebunan"],
    },
    "Permentan_13-2024_(tte).pdf": {
        "dokumen": "Permentan No. 13 Tahun 2024",
        "jenis": "Permentan",
        "tahun": 2024,
        "topik_utama": ["perkebunan"],
    },
    "Permentan_05-2025_sdh_TTE.pdf": {
        "dokumen": "Permentan No. 5 Tahun 2025",
        "jenis": "Permentan",
        "tahun": 2025,
        "topik_utama": ["perkebunan"],
    },
    "Permentan_No_33_Tahun_2025.pdf": {
        "dokumen": "Permentan No. 33 Tahun 2025",
        "jenis": "Permentan",
        "tahun": 2025,
        "topik_utama": ["perkebunan"],
    },
    "Nomor 10 Tahun 2021.pdf": {
        "dokumen": "Permen ATR/BPN No. 10 Tahun 2021",
        "jenis": "Permen ATR/BPN",
        "tahun": 2021,
        "topik_utama": ["pertanahan", "tata ruang"],
    },
    "Nomor 11 Tahun 2021.pdf": {
        "dokumen": "Permen ATR/BPN No. 11 Tahun 2021",
        "jenis": "Permen ATR/BPN",
        "tahun": 2021,
        "topik_utama": ["pertanahan", "tata ruang"],
    },
    "Nomor 14 Tahun 2021.pdf": {
        "dokumen": "Permen ATR/BPN No. 14 Tahun 2021",
        "jenis": "Permen ATR/BPN",
        "tahun": 2021,
        "topik_utama": ["pertanahan", "tata ruang"],
    },
    "Permen ATR KBPN Nomor 14 Tahun 2022-dikompresi.pdf": {
        "dokumen": "Permen ATR/BPN No. 14 Tahun 2022",
        "jenis": "Permen ATR/BPN",
        "tahun": 2022,
        "topik_utama": ["pertanahan", "tata ruang"],
    },
    "permen-atrbpn-no-5-tahun-2025.pdf": {
        "dokumen": "Permen ATR/BPN No. 5 Tahun 2025",
        "jenis": "Permen ATR/BPN",
        "tahun": 2025,
        "topik_utama": ["pertanahan", "tata ruang"],
    },
    "2023seatrbpn02_se-300.uk.05_iii.pdf": {
        "dokumen": "SE ATR/BPN No. 2 Tahun 2023",
        "jenis": "SE",
        "tahun": 2023,
        "topik_utama": ["surat edaran", "pertanahan"],
    },
    "Pert-14_-09.pdf": {
        "dokumen": "Peraturan Tahun 2009 (Pert-14)",
        "jenis": "Peraturan",
        "tahun": 2009,
        "topik_utama": ["regulasi"],
    },
}


def get_metadata_for_file(filename: str) -> dict:
    """Ambil metadata berdasarkan nama file PDF."""
    if filename in DOCUMENT_METADATA:
        return DOCUMENT_METADATA[filename].copy()

    # Fallback: coba extract info dari nama file
    meta = {
        "dokumen": filename.replace(".pdf", ""),
        "jenis": "Tidak diketahui",
        "tahun": 0,
        "topik_utama": [],
    }
    # Coba extract tahun dari nama file
    year_match = re.search(r"(19|20)\d{2}", filename)
    if year_match:
        meta["tahun"] = int(year_match.group())

    # Coba deteksi jenis
    fname_lower = filename.lower()
    if "uu" in fname_lower or "undang" in fname_lower:
        meta["jenis"] = "UU"
    elif "perpres" in fname_lower:
        meta["jenis"] = "Perpres"
    elif "permentan" in fname_lower:
        meta["jenis"] = "Permentan"
    elif "permen" in fname_lower and "atr" in fname_lower:
        meta["jenis"] = "Permen ATR/BPN"
    elif "pp" in fname_lower:
        meta["jenis"] = "PP"

    return meta


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_text_pdfplumber(pdf_path: Path) -> str:
    """Extract teks dari PDF menggunakan pdfplumber."""
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n\n".join(full_text)


def extract_text_pymupdf(pdf_path: Path) -> str:
    """Extract teks dari PDF menggunakan PyMuPDF."""
    full_text = []
    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text()
        if text:
            full_text.append(text)
    doc.close()
    return "\n\n".join(full_text)


def extract_text(pdf_path: Path, method: str = PDF_EXTRACTION_METHOD) -> str:
    """Extract teks dari PDF dengan method pilihan."""
    if method == "pdfplumber":
        return extract_text_pdfplumber(pdf_path)
    elif method == "pymupdf":
        return extract_text_pymupdf(pdf_path)
    else:
        raise ValueError(f"Unknown extraction method: {method}")


# ============================================================
# TEXT CLEANING (PHASE 3)
# ============================================================

def clean_text(text: str) -> str:
    """
    Bersihkan teks hasil extract PDF.
    - Hapus nomor halaman
    - Hapus header/footer repetitif
    - Hapus daftar isi
    - Normalisasi whitespace
    """
    # Hapus pola nomor halaman umum
    text = re.sub(r"\n\s*-?\s*\d+\s*-?\s*\n", "\n", text)  # - 12 -
    text = re.sub(r"\n\s*Halaman\s+\d+\s*(dari\s+\d+)?\s*\n", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"\n\s*Page\s+\d+\s*(of\s+\d+)?\s*\n", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"\bhal\.?\s*\d+\b", "", text, flags=re.IGNORECASE)

    # Hapus header berulang (contoh umum di regulasi Indonesia)
    text = re.sub(r"(?:www\.hukumonline\.com|www\.bphn\.go\.id|www\.peraturan\.go\.id)[^\n]*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"LEMBARAN NEGARA REPUBLIK INDONESIA[^\n]*\n?", "", text)
    text = re.sub(r"TAMBAHAN LEMBARAN NEGARA[^\n]*\n?", "", text)

    # Hapus daftar isi pattern (baris dengan titik-titik diikuti nomor halaman)
    text = re.sub(r"^.*\.{5,}\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Hapus baris yang hanya berisi angka (sisa nomor halaman)
    text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)

    # Normalisasi multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalisasi spasi berlebih di dalam baris
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Trim setiap baris
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Hapus leading/trailing whitespace keseluruhan
    text = text.strip()

    return text


# ============================================================
# MAIN — Extract semua PDF
# ============================================================

def extract_all_pdfs() -> list[dict]:
    """
    Extract semua PDF di folder UU/.
    Returns list of dict: { filename, text_raw, text_clean, metadata }
    """
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    print(f"📄 Ditemukan {len(pdf_files)} file PDF di {PDF_DIR}")

    results = []
    for pdf_path in tqdm(pdf_files, desc="Extracting PDFs"):
        filename = pdf_path.name
        try:
            raw_text = extract_text(pdf_path)
            cleaned_text = clean_text(raw_text)
            metadata = get_metadata_for_file(filename)

            results.append({
                "filename": filename,
                "text_raw": raw_text,
                "text_clean": cleaned_text,
                "metadata": metadata,
            })
            print(f"  ✅ {filename}: {len(cleaned_text)} chars")
        except Exception as e:
            print(f"  ❌ {filename}: {e}")

    # Simpan raw extracted data
    output_path = DATA_DIR / "extracted_texts.json"
    save_data = [{k: v for k, v in r.items() if k != "text_raw"} for r in results]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Hasil extract disimpan di {output_path}")

    return results


if __name__ == "__main__":
    results = extract_all_pdfs()
    print(f"\n📊 Total dokumen berhasil: {len(results)}")
    for r in results:
        meta = r["metadata"]
        print(f"  • {meta['dokumen']} ({meta['jenis']}, {meta['tahun']}): {len(r['text_clean'])} chars")
