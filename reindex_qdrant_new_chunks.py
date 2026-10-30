"""
Rebuild Qdrant directly from improved chunks.

This script bypasses data/chunks.json so Qdrant can be refreshed from the
latest chunking logic even when the chunks JSON file is stale.
"""

import json
import os
from pathlib import Path

from src.chunker import MAX_CHUNK_TOKENS, chunk_document
from src.vector_store import index_chunks


def main() -> None:
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    extracted_path = Path("data") / "extracted_texts.json"
    if not extracted_path.exists():
        raise FileNotFoundError(
            f"{extracted_path} tidak ditemukan. Jalankan ekstraksi PDF dulu."
        )

    docs = json.loads(extracted_path.read_text(encoding="utf-8"))
    chunks = []
    skipped = 0

    for doc in docs:
        if not doc.get("text_clean"):
            skipped += 1
            continue
        chunks.extend(chunk_document(doc))

    token_counts = [chunk["metadata"]["token_estimate"] for chunk in chunks]
    over_limit = sum(1 for token_count in token_counts if token_count > MAX_CHUNK_TOKENS)

    print(f"Dokumen dilewati karena teks kosong: {skipped}")
    print(f"Chunk baru: {len(chunks)}")
    print(
        "Token stats: "
        f"min={min(token_counts)}, "
        f"max={max(token_counts)}, "
        f"avg={sum(token_counts) // len(token_counts)}, "
        f"over_{MAX_CHUNK_TOKENS}={over_limit}"
    )

    if over_limit:
        raise RuntimeError("Masih ada chunk yang melewati batas token.")

    total = index_chunks(chunks=chunks, reset=True)
    print(f"Qdrant selesai diindex ulang: {total} chunks")


if __name__ == "__main__":
    main()
