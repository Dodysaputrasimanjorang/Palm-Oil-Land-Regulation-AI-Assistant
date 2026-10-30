"""
Phase 9 — RAG Pipeline + LLM Integration via OpenRouter API.

Flow:
    User Question → Metadata Filter → Hybrid Retrieval → Top K Chunks
    → Build Prompt → LLM (OpenRouter) → Answer + Citations
"""

import requests
from requests.exceptions import HTTPError

from .config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_SITE_URL,
    OPENROUTER_APP_NAME,
    LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TIMEOUT_SECONDS,
    RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE, TOP_K
)
from .hybrid_retriever import get_retriever

import re

# ============================================================
# LLM CLIENT
# ============================================================

def get_llm_client() -> tuple[str, dict]:
    """Build OpenRouter chat completions endpoint and headers."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY belum diset.")

    base_url = OPENROUTER_BASE_URL.rstrip("/")
    endpoint = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = OPENROUTER_SITE_URL
    if OPENROUTER_APP_NAME:
        headers["X-Title"] = OPENROUTER_APP_NAME

    return endpoint, headers


# ============================================================
# BUILD CONTEXT dari retrieved chunks
# ============================================================

def build_context(
    retrieved_chunks: list[dict],
    max_context_chars: int = 12000,
    max_chunks: int = 6,
) -> str:
    """
    Build context string dari retrieved chunks untuk dimasukkan ke prompt LLM.
    Setiap chunk disertai sumber (dokumen + pasal).
    """
    context_parts = []
    total_chars = 0

    for i, chunk in enumerate(retrieved_chunks[:max_chunks]):
        meta = chunk["metadata"]
        text = chunk["text"]

        # Truncate individual chunk jika terlalu panjang
        if len(text) > 2500:
            text = text[:2500] + "..."

        # Format chunk dengan sumber
        source = f"[Sumber: {meta.get('dokumen', 'N/A')}, {meta.get('pasal', 'N/A')}]"
        topik = meta.get("topik", "")
        if isinstance(topik, list):
            topik = ", ".join(topik)

        formatted = f"--- Dokumen {i+1} {source} ---\nTopik: {topik}\n{text}\n"

        # Cek apakah masih muat
        if total_chars + len(formatted) > max_context_chars:
            break

        context_parts.append(formatted)
        total_chars += len(formatted)

    return "\n".join(context_parts)


# ============================================================
# EXTRACT REFERENCED SOURCES FROM LLM ANSWER
# ============================================================

def extract_referenced_sources(answer: str, sources: list[dict]) -> list[dict]:
    """
    Parse jawaban LLM untuk menemukan dokumen/pasal yang dirujuk,
    lalu cocokkan dengan sources yang di-retrieve.

    Strategi matching (prioritas):
    1. Pola "Dokumen N" — karena konteks ke LLM menggunakan format
       "--- Dokumen 1 [Sumber: ...] ---", LLM sering merujuk "Dokumen 4 dan 5".
    2. Nama dokumen / nomor regulasi (e.g. "UU No. 39 Tahun 2014")
    3. Pasal spesifik (e.g. "Pasal 84 ayat (3)")

    Hasilnya diurutkan berdasarkan kemunculan pertama di jawaban.
    """
    answer_lower = answer.lower()
    matched = []          # list of (position_in_answer, source_index, source)
    used_indices = set()

    # ── Strategy 1: Match "Dokumen N" references ──
    # Find all "Dokumen 1", "Dokumen 2", etc. in the answer
    dokumen_refs = re.finditer(r'dokumen\s+(\d+)', answer_lower)
    for m in dokumen_refs:
        doc_num = int(m.group(1))
        idx = doc_num - 1  # "Dokumen 1" → sources[0]
        if 0 <= idx < len(sources) and idx not in used_indices:
            matched.append((m.start(), idx, sources[idx]))
            used_indices.add(idx)

    # ── Strategy 2: Match by document name / regulation number ──
    for i, src in enumerate(sources):
        if i in used_indices:
            continue

        dokumen = src.get("dokumen", "") or ""
        pasal = src.get("pasal", "") or ""
        pos = -1

        if dokumen and dokumen != "N/A":
            doc_lower = dokumen.lower().strip()

            # Full document name
            idx = answer_lower.find(doc_lower)
            if idx != -1:
                pos = idx

            # Shortened: "UU No. 39 Tahun 2014" etc.
            short_match = re.search(
                r'((?:UU|PP|Perpres|Permen\s*\w*)\s*(?:No\.?\s*)?\d+\s*Tahun\s*\d{4})',
                dokumen, re.IGNORECASE
            )
            if short_match:
                short_name = short_match.group(1).lower().strip()
                idx = answer_lower.find(short_name)
                if idx != -1:
                    pos = idx if pos == -1 else min(pos, idx)

            # Number + year: "No. 39 Tahun 2014" or "Nomor 39 Tahun 2014"
            num_year = re.search(r'No\.?\s*(\d+)\s*Tahun\s*(\d{4})', dokumen, re.IGNORECASE)
            if num_year:
                pattern = rf'(?:No\.?|Nomor)\s*{num_year.group(1)}\s*Tahun\s*{num_year.group(2)}'
                m = re.search(pattern, answer, re.IGNORECASE)
                if m:
                    pos = m.start() if pos == -1 else min(pos, m.start())

            # Also try just the type + number: "UU 39", "PP 3", etc.
            type_num = re.search(
                r'(UU|PP|Perpres|Permentan|Permen\s*ATR/?BPN)\s*(?:No\.?\s*)?(\d+)',
                dokumen, re.IGNORECASE
            )
            if type_num and pos == -1:
                pattern = rf'{re.escape(type_num.group(1))}\s*(?:No\.?\s*)?{type_num.group(2)}'
                m = re.search(pattern, answer, re.IGNORECASE)
                if m:
                    pos = m.start()

        # ── Strategy 3: Match by pasal ──
        if pasal and pasal != "N/A":
            pasal_lower = pasal.lower().strip()
            # Direct match
            idx = answer_lower.find(pasal_lower)
            if idx != -1:
                pos = idx if pos == -1 else min(pos, idx)

            # Match "Pasal NN" pattern from the pasal field
            pasal_nums = re.findall(r'pasal\s+(\d+)', pasal_lower)
            for pnum in pasal_nums:
                # Match "Pasal NN" in the answer (with optional ayat)
                pattern = rf'pasal\s+{pnum}\b'
                m = re.search(pattern, answer_lower)
                if m:
                    found_pos = m.start()
                    pos = found_pos if pos == -1 else min(pos, found_pos)
                    break

        if pos != -1:
            matched.append((pos, i, src))
            used_indices.add(i)

    # Sort by position of first appearance in answer
    matched.sort(key=lambda x: x[0])

    return [item[2] for item in matched]


# ============================================================
# RAG PIPELINE
# ============================================================

class RAGPipeline:
    """
    Pipeline lengkap Hybrid RAG:
    1. Retrieve (hybrid search + metadata filter)
    2. Build context
    3. Query LLM
    4. Return answer + sources
    """

    def __init__(self):
        self.retriever = get_retriever()
        self.llm_client, self.llm_headers = get_llm_client()
        print("✅ RAG Pipeline initialized")

    def query(
        self,
        question: str,
        top_k: int = TOP_K,
        auto_filter: bool = True,
        show_sources: bool = True,
    ) -> dict:
        """
        Proses pertanyaan user melalui RAG pipeline.
        
        Returns:
            {
                "question": str,
                "answer": str,
                "sources": list[dict],  # chunk sources with metadata
                "retrieval_scores": list[dict],
                "metadata_filters": dict,
            }
        """
        print(f"\n🔍 Processing: {question}")

        # Step 1: Hybrid Retrieval
        retrieved = self.retriever.retrieve(
            question, top_k=top_k, auto_filter=auto_filter
        )

        if not retrieved:
            return {
                "question": question,
                "answer": "Maaf, tidak ditemukan dokumen regulasi yang relevan dengan pertanyaan Anda.",
                "sources": [],
                "retrieval_scores": [],
                "metadata_filters": {},
            }

        print(f"  📦 Retrieved {len(retrieved)} chunks")

        # Step 2: Sort retrieved by hybrid score (highest first)
        # Ini memastikan konteks LLM mengikuti ranking gabungan terbaik,
        # bukan hanya semantic score yang bisa gagal saat embedding fallback.
        retrieved = sorted(
            retrieved,
            key=lambda r: r["scores"].get("hybrid", 0.0),
            reverse=True,
        )

        # Step 3: Build context
        context = build_context(retrieved)

        # Step 3: Build prompt
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

        # Step 4: Query LLM
        print(f"  🤖 Querying LLM: {LLM_MODEL}")
        try:
            response = requests.post(
                self.llm_client,
                headers=self.llm_headers,
                json={
                    "model": LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": RAG_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": LLM_TEMPERATURE,
                    "max_tokens": LLM_MAX_TOKENS,
                },
                timeout=LLM_TIMEOUT_SECONDS,
            )
            response.raise_for_status()

            data = response.json()
            message = (
                (data.get("choices") or [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            if isinstance(message, list):
                message = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in message
                )
            answer = str(message).strip()
            if not answer:
                raise ValueError("Respons OpenRouter kosong.")
        except HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            error_detail = ""

            if e.response is not None:
                try:
                    body = e.response.json()
                    error_detail = body.get("error") or str(body)
                except Exception:
                    error_detail = (e.response.text or "").strip()

            if status_code == 401:
                answer = (
                    "Error saat menghubungi LLM: API key OpenRouter tidak valid atau tidak memiliki akses model. "
                    "Periksa OPENROUTER_API_KEY dan hak akses model pada akun OpenRouter Anda."
                )
            elif status_code == 404:
                answer = (
                    f"Error saat menghubungi LLM: model '{LLM_MODEL}' tidak ditemukan di OpenRouter. "
                    "Sesuaikan OPENROUTER_MODEL di file .env dengan model yang tersedia di akun OpenRouter Anda."
                )
            else:
                detail = f" ({error_detail})" if error_detail else ""
                answer = f"Error saat menghubungi LLM: HTTP {status_code}{detail}"

            print(f"  ❌ LLM HTTP Error: {e}")
        except Exception as e:
            answer = f"Error saat menghubungi LLM: {str(e)}"
            print(f"  ❌ LLM Error: {e}")

        # Step 5: Compile sources (deduplicate by dokumen+pasal, keep highest hybrid score)
        sources_raw = []
        for r in retrieved:
            meta = r["metadata"]
            topik = meta.get("topik", "")
            if isinstance(topik, list):
                topik = ", ".join(topik)
            sources_raw.append({
                "dokumen": meta.get("dokumen", "N/A"),
                "pasal": meta.get("pasal", "N/A"),
                "jenis": meta.get("jenis", "N/A"),
                "tahun": meta.get("tahun", 0),
                "topik": topik,
                "preview": r["text"][:200],
                "retrieval_score": r["scores"].get("hybrid", 0.0),
                "semantic_score": r["scores"].get("semantic", 0.0),
                "bm25_score": r["scores"].get("bm25", 0.0),
                "scores": r["scores"],
            })

        # Deduplicate: keep the entry with highest hybrid score per (dokumen, pasal)
        seen = {}
        for src in sources_raw:
            key = (src["dokumen"], src["pasal"])
            if key not in seen or src["scores"]["hybrid"] > seen[key]["scores"]["hybrid"]:
                seen[key] = src
        sources = list(seen.values())
        # Re-sort by hybrid score descending
        sources.sort(key=lambda s: s["scores"]["hybrid"], reverse=True)

        # Extract filters used
        from .hybrid_retriever import MetadataFilter
        filters = MetadataFilter.extract_filters(question) if auto_filter else {}

        # Step 7: Extract only sources actually referenced in the answer
        referenced_sources = extract_referenced_sources(answer, sources)

        # Fallback: if no sources matched, show top sources by score
        if not referenced_sources:
            referenced_sources = sources[:5]

        result = {
            "question": question,
            "answer": answer,
            "sources": sources,                  # all retrieved sources (for score table)
            "referenced_sources": referenced_sources,  # only sources mentioned in answer
            "retrieved_contexts": [r["text"] for r in retrieved],
            "retrieval_scores": [
                {"chunk_id": r["chunk_id"], **r["scores"]}
                for r in retrieved
            ],
            "metadata_filters": filters,
        }

        return result


# ============================================================
# SINGLETON
# ============================================================

_pipeline = None

def get_pipeline() -> RAGPipeline:
    """Get global RAG pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


# ============================================================
# MAIN — Test
# ============================================================

if __name__ == "__main__":
    pipeline = get_pipeline()

    test_questions = [
        "Apakah boleh membuka lahan sawit di kawasan hutan?",
        "Apa sanksi jika melanggar izin usaha perkebunan?",
        "Bagaimana prosedur sertifikasi ISPO kelapa sawit?",
    ]

    for q in test_questions:
        print(f"\n{'='*70}")
        result = pipeline.query(q)
        print(f"\n❓ Pertanyaan: {result['question']}")
        print(f"\n💡 Jawaban:\n{result['answer']}")
        print(f"\n📚 Sumber ({len(result['sources'])} dokumen):")
        for i, src in enumerate(result["sources"]):
            print(f"  [{i+1}] {src['dokumen']} | {src['pasal']}")
            print(f"      Skor hybrid: {src['scores']['hybrid']:.4f}")
        if result["metadata_filters"]:
            print(f"\n🏷️ Filter metadata: {result['metadata_filters']}")
        print(f"{'='*70}")



