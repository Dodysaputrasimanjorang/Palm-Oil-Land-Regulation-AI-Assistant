"""
Phase 4 & 5 — Chunking per pasal/ayat + Metadata structure.
Regulasi Indonesia di-chunk berdasarkan pasal, bukan random.
"""

import re
import json
import hashlib
import os
from pathlib import Path
from tqdm import tqdm

from .config import (
    DATA_DIR,
    CHUNKS_FILE,
    MIN_CHUNK_TOKENS,
    MAX_CHUNK_TOKENS,
    OVERLAP_SENTENCES,
)


# ============================================================
# REGEX PATTERNS untuk deteksi struktur regulasi Indonesia
# ============================================================

# Pattern untuk mendeteksi awal Pasal
PASAL_PATTERN = re.compile(
    r"^\s*Pasal\s+(\d+[A-Z]?)\b.*$",
    re.MULTILINE | re.IGNORECASE
)

# Pattern untuk mendeteksi BAB
BAB_PATTERN = re.compile(
    r"^BAB\s+([IVXLCDM]+(?:\s*[A-Z])?)\s*\n+(.+?)$",
    re.MULTILINE | re.IGNORECASE
)

# Pattern untuk mendeteksi Bagian
BAGIAN_PATTERN = re.compile(
    r"^Bagian\s+(Kesatu|Kedua|Ketiga|Keempat|Kelima|Keenam|Ketujuh|Kedelapan|Kesembilan|Kesepuluh|[A-Za-z]+)\s*\n+(.+?)$",
    re.MULTILINE | re.IGNORECASE
)

# Pattern ayat
AYAT_PATTERN = re.compile(r"^\s*\((\d+)\)", re.MULTILINE)

# Pattern huruf (a., b., c., dst)
HURUF_PATTERN = re.compile(r"^([a-z])\.", re.MULTILINE)

# Pattern kalimat sederhana untuk menjaga chunk panjang tetap natural.
SENTENCE_PATTERN = re.compile(r"(?<=[.!?;:])\s+(?=[A-Z0-9(\"])")


def estimate_tokens(text: str) -> int:
    """Estimasi jumlah token (rough: 1 token ≈ 4 chars untuk Bahasa Indonesia)."""
    return len(text) // 4


def normalize_chunk_text(text: str) -> str:
    """Rapikan whitespace tanpa menghilangkan struktur baris regulasi."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def split_sentences(text: str) -> list[str]:
    """Split kalimat dengan fallback per baris untuk teks regulasi hasil PDF."""
    text = normalize_chunk_text(text)
    if not text:
        return []

    sentences = []
    for paragraph in re.split(r"\n{2,}", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        parts = [p.strip() for p in SENTENCE_PATTERN.split(paragraph) if p.strip()]
        if len(parts) == 1 and estimate_tokens(parts[0]) > MAX_CHUNK_TOKENS:
            parts = [p.strip() for p in paragraph.split("\n") if p.strip()]

        sentences.extend(parts)

    return sentences


def split_oversized_unit(text: str, max_tokens: int = MAX_CHUNK_TOKENS) -> list[str]:
    """Fallback terakhir untuk baris/kalimat PDF yang terlalu panjang."""
    text = normalize_chunk_text(text)
    if estimate_tokens(text) <= max_tokens:
        return [text]

    max_chars = max_tokens * 4
    words = text.split()
    parts = []
    current = []

    for word in words:
        if estimate_tokens(word) > max_tokens:
            if current:
                parts.append(" ".join(current).strip())
                current = []
            parts.extend(word[i:i + max_chars] for i in range(0, len(word), max_chars))
            continue

        candidate = " ".join(current + [word])
        if current and estimate_tokens(candidate) > max_tokens:
            parts.append(" ".join(current).strip())
            current = [word]
        else:
            current.append(word)

    if current:
        parts.append(" ".join(current).strip())

    return parts


def split_text_with_overlap(
    text: str,
    max_tokens: int = MAX_CHUNK_TOKENS,
    overlap_sentences: int = OVERLAP_SENTENCES,
) -> list[str]:
    """Pecah teks panjang menjadi chunk berbasis kalimat dengan overlap kecil."""
    sentences = split_sentences(text)
    if not sentences:
        return []

    chunks = []
    current = []

    for sentence in sentences:
        sentence_parts = split_oversized_unit(sentence, max_tokens=max_tokens)
        for sentence_part in sentence_parts:
            candidate = "\n".join(current + [sentence_part])
            if current and estimate_tokens(candidate) > max_tokens:
                chunks.append("\n".join(current).strip())
                overlap = current[-overlap_sentences:] if overlap_sentences > 0 else []
                overlap_candidate = "\n".join(overlap + [sentence_part])
                if overlap and estimate_tokens(overlap_candidate) <= max_tokens:
                    current = overlap + [sentence_part]
                else:
                    current = [sentence_part]
            else:
                current.append(sentence_part)

    if current:
        chunks.append("\n".join(current).strip())

    return chunks


def generate_chunk_id(dokumen: str, pasal: str, idx: int) -> str:
    """Generate unique chunk ID."""
    raw = f"{dokumen}_{pasal}_{idx}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def detect_topic(text: str, pasal_text: str = "") -> list[str]:
    """Deteksi topik dari isi chunk berdasarkan keyword."""
    combined = (text + " " + pasal_text).lower()
    topics = []

    topic_keywords = {
        "izin usaha": ["izin usaha", "perizinan", "izin berusaha", "persetujuan"],
        "lahan": ["lahan", "tanah", "areal", "kawasan"],
        "hutan": ["hutan", "kehutanan", "kawasan hutan", "hutan lindung", "hutan produksi"],
        "kelapa sawit": ["kelapa sawit", "sawit", "minyak sawit", "cpo"],
        "perkebunan": ["perkebunan", "kebun", "tanaman perkebunan", "pekebun"],
        "lingkungan": ["lingkungan", "amdal", "dampak lingkungan", "pencemaran", "kerusakan"],
        "tata ruang": ["tata ruang", "rencana tata ruang", "rtrw", "penataan ruang"],
        "sertifikasi": ["sertifikasi", "ispo", "sertifikat", "standar"],
        "sanksi": ["sanksi", "pidana", "denda", "hukuman", "pelanggaran"],
        "hak guna usaha": ["hak guna usaha", "hgu", "hak atas tanah"],
        "petani": ["petani", "pekebun", "rakyat", "plasma", "kemitraan"],
        "peremajaan": ["peremajaan", "replanting", "penanaman kembali"],
        "dana perkebunan": ["dana perkebunan", "pungutan", "bpdpks", "dana sawit"],
        "pembukaan lahan": ["pembukaan lahan", "pembukaan", "land clearing", "bakar"],
        "konservasi": ["konservasi", "perlindungan", "pelestarian"],
        "moratorium": ["moratorium", "penghentian sementara", "jeda tebang"],
    }

    for topic, keywords in topic_keywords.items():
        for kw in keywords:
            if kw in combined:
                topics.append(topic)
                break

    return topics if topics else ["umum"]


def split_by_pasal(text: str) -> list[dict]:
    """
    Split teks regulasi menjadi chunks berdasarkan Pasal.
    Returns list of { pasal, text, ayat_count }
    """
    # Cari semua posisi Pasal
    matches = list(PASAL_PATTERN.finditer(text))

    if not matches:
        # Jika tidak ada pola Pasal, return seluruh teks sebagai satu chunk
        return [{"pasal": "Umum", "text": text.strip(), "ayat_count": 0}]

    chunks = []

    # Ambil teks sebelum Pasal pertama (jika ada, biasanya preambul/konsiderans)
    preamble = text[:matches[0].start()].strip()
    if preamble and len(preamble) > 100:
        chunks.append({
            "pasal": "Preambul",
            "text": preamble,
            "ayat_count": 0,
        })

    # Proses setiap Pasal
    for i, match in enumerate(matches):
        pasal_num = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        pasal_text = text[start:end].strip()

        # Hitung jumlah ayat
        ayat_matches = AYAT_PATTERN.findall(pasal_text)
        ayat_count = len(ayat_matches)

        chunks.append({
            "pasal": f"Pasal {pasal_num}",
            "text": pasal_text,
            "ayat_count": ayat_count,
        })

    return chunks


def split_long_chunk(chunk: dict, max_tokens: int = MAX_CHUNK_TOKENS) -> list[dict]:
    """
    Split pasal yang terlalu panjang menjadi sub-chunks berdasarkan ayat.
    """
    text = normalize_chunk_text(chunk["text"])
    tokens = estimate_tokens(text)

    if tokens <= max_tokens:
        clean_chunk = chunk.copy()
        clean_chunk["text"] = text
        return [clean_chunk]

    # Coba split per ayat
    ayat_positions = [(m.start(), m.group(1)) for m in AYAT_PATTERN.finditer(text)]

    if not ayat_positions:
        text_parts = split_text_with_overlap(text, max_tokens=max_tokens)
        return [
            {
                "pasal": f"{chunk['pasal']} (bagian {idx})",
                "text": part,
                "ayat_count": 0,
            }
            for idx, part in enumerate(text_parts, start=1)
        ] or [chunk]

    # Split per ayat
    sub_chunks = []
    pasal_header = text[:ayat_positions[0][0]].strip()

    for i, (pos, ayat_num) in enumerate(ayat_positions):
        end_pos = ayat_positions[i + 1][0] if i + 1 < len(ayat_positions) else len(text)
        ayat_text = text[pos:end_pos].strip()

        # Tambahkan header pasal ke setiap sub-chunk agar konteksnya jelas
        full_text = f"{pasal_header}\n{ayat_text}" if pasal_header else ayat_text

        if estimate_tokens(full_text) <= max_tokens:
            sub_chunks.append({
                "pasal": f"{chunk['pasal']} ayat ({ayat_num})",
                "text": normalize_chunk_text(full_text),
                "ayat_count": 1,
            })
            continue

        ayat_parts = split_text_with_overlap(full_text, max_tokens=max_tokens)
        for part_idx, part in enumerate(ayat_parts, start=1):
            sub_chunks.append({
                "pasal": f"{chunk['pasal']} ayat ({ayat_num}) bagian {part_idx}",
                "text": part,
                "ayat_count": 1,
            })

    return sub_chunks


def _pasal_base(pasal: str) -> str:
    """Normalize pasal label to avoid merging different pasal."""
    base = pasal.lower()
    base = re.sub(r"\s+ayat\s+\(\d+\)\s+bagian\s+\d+", "", base)
    base = re.sub(r"\s+ayat\s+\(\d+\)", "", base)
    base = re.sub(r"\s+\(bagian\s+\d+\)", "", base)
    return base.strip()


def merge_short_chunks(
    chunks: list[dict],
    min_tokens: int = MIN_CHUNK_TOKENS,
    max_tokens: int = MAX_CHUNK_TOKENS,
) -> list[dict]:
    """Gabungkan chunks pendek yang berurutan (hanya jika pasal sama)."""
    if not chunks:
        return chunks

    merged = []
    buffer = None

    for chunk in chunks:
        tokens = estimate_tokens(chunk["text"])

        if buffer is None:
            if tokens < min_tokens:
                buffer = chunk.copy()
            else:
                merged.append(chunk)
            continue

        same_pasal = _pasal_base(buffer["pasal"]) == _pasal_base(chunk["pasal"])
        candidate_text = f"{buffer['text']}\n\n{chunk['text']}"
        within_limit = estimate_tokens(candidate_text) <= max_tokens

        if same_pasal and within_limit:
            buffer["text"] = candidate_text
            buffer["pasal"] += f" + {chunk['pasal']}"
            buffer["ayat_count"] = buffer.get("ayat_count", 0) + chunk.get("ayat_count", 0)
            if estimate_tokens(buffer["text"]) >= min_tokens:
                merged.append(buffer)
                buffer = None
            continue

        merged.append(buffer)
        buffer = None
        if tokens < min_tokens:
            buffer = chunk.copy()
        else:
            merged.append(chunk)

    if buffer is not None:
        merged.append(buffer)

    return merged


def detect_bab(text: str, pasal_start: int) -> str:
    """Deteksi BAB untuk suatu posisi pasal."""
    bab_matches = list(BAB_PATTERN.finditer(text[:pasal_start]))
    if bab_matches:
        last_bab = bab_matches[-1]
        bab_num = last_bab.group(1).strip()
        bab_title = last_bab.group(2).strip()
        return f"BAB {bab_num} - {bab_title}"
    return ""


def chunk_document(doc_data: dict) -> list[dict]:
    """
    Proses satu dokumen: chunk per pasal + metadata.
    
    Input: dict dari pdf_extractor { filename, text_clean, metadata }
    Output: list of final chunks dengan metadata lengkap
    """
    text = doc_data["text_clean"]
    metadata = doc_data["metadata"]
    filename = doc_data["filename"]

    # Step 1: Split per pasal
    raw_chunks = split_by_pasal(text)

    # Step 2: Split pasal panjang
    split_chunks = []
    for chunk in raw_chunks:
        split_chunks.extend(split_long_chunk(chunk))

    # Step 3: Merge chunks pendek
    final_chunks = merge_short_chunks(split_chunks)

    # Step 4: Tambahkan metadata lengkap
    results = []
    for idx, chunk in enumerate(final_chunks):
        # Deteksi topik otomatis dari isi chunk
        topics = detect_topic(chunk["text"], chunk["pasal"])

        # Gabungkan topik otomatis dengan topik_utama dokumen
        all_topics = list(set(metadata.get("topik_utama", []) + topics))

        chunk_data = {
            "chunk_id": generate_chunk_id(filename, chunk["pasal"], idx),
            "text": chunk["text"],
            "metadata": {
                "dokumen": metadata["dokumen"],
                "jenis": metadata["jenis"],
                "tahun": metadata["tahun"],
                "pasal": chunk["pasal"],
                "topik": all_topics,
                "filename": filename,
                "chunk_index": idx,
                "token_estimate": estimate_tokens(chunk["text"]),
            },
        }
        results.append(chunk_data)

    return results


def chunk_all_documents(extracted_docs: list[dict] = None) -> list[dict]:
    """
    Chunk semua dokumen yang sudah di-extract.
    Jika extracted_docs=None, baca dari file extracted_texts.json.
    """
    if extracted_docs is None:
        extracted_path = DATA_DIR / "extracted_texts.json"
        if not extracted_path.exists():
            raise FileNotFoundError(
                f"File {extracted_path} tidak ditemukan. Jalankan pdf_extractor.py dulu."
            )
        with open(extracted_path, "r", encoding="utf-8") as f:
            extracted_docs = json.load(f)
        # Tambahkan text_clean dari file (sudah ada di JSON)
        for doc in extracted_docs:
            doc["text_clean"] = doc.get("text_clean", "")

    all_chunks = []
    for doc in tqdm(extracted_docs, desc="Chunking documents"):
        if not doc.get("text_clean"):
            print(f"  ⚠️ Skip {doc['filename']}: teks kosong")
            continue

        doc_chunks = chunk_document(doc)
        all_chunks.extend(doc_chunks)
        print(f"  📦 {doc['metadata']['dokumen']}: {len(doc_chunks)} chunks")

    # Simpan hasil chunking secara atomik agar file lama tidak rusak jika write gagal.
    tmp_chunks_file = CHUNKS_FILE.with_suffix(".json.tmp")
    tmp_chunks_file.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(tmp_chunks_file, CHUNKS_FILE)
    print(f"\n💾 Total {len(all_chunks)} chunks disimpan di {CHUNKS_FILE}")

    # Statistik
    token_counts = [c["metadata"]["token_estimate"] for c in all_chunks]
    if token_counts:
        print(f"📊 Token stats: min={min(token_counts)}, max={max(token_counts)}, "
              f"avg={sum(token_counts)//len(token_counts)}")

    return all_chunks


if __name__ == "__main__":
    chunks = chunk_all_documents()
    print(f"\n✅ Chunking selesai: {len(chunks)} chunks total")
    
    # Tampilkan beberapa contoh
    print("\n📝 Contoh 5 chunk pertama:")
    for c in chunks[:5]:
        meta = c["metadata"]
        preview = c["text"][:100].replace("\n", " ")
        print(f"  [{meta['pasal']}] {meta['dokumen']}")
        print(f"    Topik: {meta['topik']}")
        print(f"    Preview: {preview}...")
        print()
