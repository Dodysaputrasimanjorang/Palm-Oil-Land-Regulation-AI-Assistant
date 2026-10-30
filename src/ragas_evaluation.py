"""
Evaluasi kualitas RAG menggunakan framework RAGAS.

Output utama:
- summary skor metrik (faithfulness, answer_relevancy, context_precision, context_recall)
- detail skor per pertanyaan
- file hasil evaluasi (JSON + CSV)
"""

import csv
import json
import time
import copy
import math
from datetime import datetime

from .config import (
    RAGAS_RESULTS_DIR,
    TOP_K,
    LLM_MODEL,
    OPENROUTER_BASE_URL,
    OPENROUTER_API_KEY,
    OPENROUTER_SITE_URL,
    OPENROUTER_APP_NAME,
    LLM_TEMPERATURE,
    EMBEDDING_MODEL,
)
from .evaluation import EVAL_QUESTIONS


RAGAS_METRIC_NAMES = [
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
]


def _safe_float(value, default=0.0):
    """Convert numeric value to float safely."""
    try:
        if value is None:
            return default
        numeric = float(value)
        if math.isnan(numeric) or math.isinf(numeric):
            return default
        return numeric
    except Exception:
        return default


def _build_openrouter_headers() -> dict:
    """Build optional headers for OpenRouter attribution."""
    headers = {}
    if OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = OPENROUTER_SITE_URL
    if OPENROUTER_APP_NAME:
        headers["X-Title"] = OPENROUTER_APP_NAME
    return headers


def _prepare_ragas_samples(pipeline, questions: list[dict], top_k: int, auto_filter: bool):
    """Generate question-answer-context samples for RAGAS."""
    samples = []
    latencies = []

    for q in questions:
        started = time.time()

        result = pipeline.query(
            q["question"],
            top_k=top_k,
            auto_filter=auto_filter,
        )
        contexts = [
            context.strip()
            for context in result.get("retrieved_contexts", [])[:top_k]
            if context and context.strip()
        ]

        latencies.append(time.time() - started)
        samples.append({
            # RAGAS v0.2 canonical columns
            "user_input": q["question"],
            "response": result.get("answer", ""),
            "retrieved_contexts": contexts,
            "reference": q.get("ground_truth", ""),
            # Keep legacy aliases for easier debugging
            "question": q["question"],
            "answer": result.get("answer", ""),
            "contexts": contexts,
            "ground_truth": q.get("ground_truth", ""),
        })

    return samples, latencies


def run_ragas_evaluation(
    pipeline,
    sample_size: int = 5,
    top_k: int = TOP_K,
    auto_filter: bool = True,
    questions: list[dict] | None = None,
) -> dict:
    """
    Jalankan evaluasi RAGAS pada subset pertanyaan evaluasi.

    Catatan:
    - RAGAS membutuhkan dependency tambahan (`ragas`, `datasets`)
    - Sebagian metrik membutuhkan evaluator LLM/embedding sesuai konfigurasi environment.
    """
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from ragas.llms import LangchainLLMWrapper
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
        from langchain_openai import ChatOpenAI
        from langchain_huggingface import HuggingFaceEmbeddings
    except Exception as exc:
        raise RuntimeError(
            "Dependency RAGAS belum siap. Pastikan package `ragas`, `datasets`, "
            "`langchain-openai`, dan `langchain-huggingface` terinstall."
        ) from exc

    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY belum diset untuk evaluasi RAGAS.")

    if questions is None:
        questions = EVAL_QUESTIONS

    if sample_size <= 0:
        raise ValueError("sample_size harus > 0")

    selected_questions = questions[: min(sample_size, len(questions))]
    samples, latencies = _prepare_ragas_samples(
        pipeline=pipeline,
        questions=selected_questions,
        top_k=top_k,
        auto_filter=auto_filter,
    )

    dataset = Dataset.from_list(samples)

    # Force RAGAS evaluator to use OpenRouter (avoid OpenAI fallback)
    llm_kwargs = {
        "model": LLM_MODEL,
        "api_key": OPENROUTER_API_KEY,
        "base_url": OPENROUTER_BASE_URL.rstrip("/"),
        "temperature": LLM_TEMPERATURE,
    }
    extra_headers = _build_openrouter_headers()
    if extra_headers:
        llm_kwargs["default_headers"] = extra_headers

    llm_wrapper = LangchainLLMWrapper(ChatOpenAI(**llm_kwargs))
    embedding_wrapper = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    )

    metric_objs = [
        copy.deepcopy(faithfulness),
        copy.deepcopy(answer_relevancy),
        copy.deepcopy(context_precision),
        copy.deepcopy(context_recall),
    ]

    # Hard-bind evaluator to every metric instance to avoid OpenAI fallback.
    for metric in metric_objs:
        if hasattr(metric, "llm"):
            metric.llm = llm_wrapper
        if hasattr(metric, "embeddings"):
            metric.embeddings = embedding_wrapper

    eval_result = evaluate(
        dataset=dataset,
        metrics=metric_objs,
        llm=llm_wrapper,
        embeddings=embedding_wrapper,
    )
    result_df = eval_result.to_pandas()

    summary = {
        "num_questions": len(selected_questions),
        "avg_latency": round(sum(latencies) / len(latencies), 4) if latencies else 0.0,
    }
    for metric_name in RAGAS_METRIC_NAMES:
        if metric_name in result_df.columns:
            summary[metric_name] = round(_safe_float(result_df[metric_name].mean()), 4)
        else:
            summary[metric_name] = 0.0

    details = []
    for idx, q in enumerate(selected_questions):
        row = result_df.iloc[idx] if idx < len(result_df.index) else None
        item = {
            "question_id": q.get("id", idx + 1),
            "question": q.get("question", ""),
            "latency": round(latencies[idx], 4) if idx < len(latencies) else 0.0,
        }
        for metric_name in RAGAS_METRIC_NAMES:
            item[metric_name] = round(_safe_float(row.get(metric_name)) if row is not None else 0.0, 4)
        details.append(item)

    return {
        "summary": summary,
        "details": details,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def save_ragas_results(results: dict, filename_prefix: str = "ragas_eval") -> dict:
    """Simpan hasil evaluasi RAGAS ke JSON dan CSV summary/detail."""
    RAGAS_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_name = f"{filename_prefix}_{timestamp}.json"
    csv_name = f"{filename_prefix}_{timestamp}_details.csv"

    json_path = RAGAS_RESULTS_DIR / json_name
    csv_path = RAGAS_RESULTS_DIR / csv_name

    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(results, jf, ensure_ascii=False, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow([
            "question_id",
            "question",
            "latency",
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall",
        ])
        for row in results.get("details", []):
            writer.writerow([
                row.get("question_id", ""),
                row.get("question", ""),
                row.get("latency", 0.0),
                row.get("faithfulness", 0.0),
                row.get("answer_relevancy", 0.0),
                row.get("context_precision", 0.0),
                row.get("context_recall", 0.0),
            ])

    return {
        "json": str(json_path),
        "csv": str(csv_path),
    }
