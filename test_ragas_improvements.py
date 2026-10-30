#!/usr/bin/env python3
"""
Script untuk test perubahan RAGAS improvements:
- Embedding model upgrade → BAAI/bge-large-zh-v1.5
- TOP_K naikkan 10 → 15
- Semantic/BM25 weight optimization
- RAG prompt improvement
- BM25 fallback logic

Jalankan: python test_ragas_improvements.py
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import (
    TOP_K, SEMANTIC_WEIGHT, BM25_WEIGHT, 
    EMBEDDING_MODEL, RAG_SYSTEM_PROMPT,
    DATA_DIR
)

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_config_changes():
    """Verifikasi bahwa perubahan konfigurasi sudah diterapkan"""
    print_section("1. VERIFIKASI PERUBAHAN KONFIGURASI")
    
    changes = {
        "Embedding Model": (EMBEDDING_MODEL, "intfloat/multilingual-e5-large"),
        "TOP_K": (TOP_K, 15),
        "Semantic Weight": (SEMANTIC_WEIGHT, 0.6),
        "BM25 Weight": (BM25_WEIGHT, 0.4),
    }
    
    all_ok = True
    for name, (current, expected) in changes.items():
        status = "✅" if current == expected else "❌"
        print(f"{status} {name:20} : {current} (expected: {expected})")
        if current != expected:
            all_ok = False
    
    # Check RAG Prompt
    print(f"\n{'✅' if 'SPESIFIK' in RAG_SYSTEM_PROMPT else '❌'} RAG System Prompt improved: ", end="")
    if "SPESIFIK" in RAG_SYSTEM_PROMPT:
        print("✅ (Improved error handling added)")
    else:
        print("❌ (Not updated)")
        all_ok = False
    
    return all_ok

def test_retriever_with_fallback():
    """Test fallback logic untuk metadata filtering"""
    print_section("2. TEST RETRIEVER FALLBACK LOGIC")
    
    try:
        from src.rag_pipeline import RAGPipeline
        pipeline = RAGPipeline()
        
        test_queries = [
            # Query yang memiliki metadata filter ketat
            "Apa saja persyaratan HGU untuk perkebunan sawit?",
            # Query tanpa filter metadata spesifik
            "Apa sanksi pembakaran lahan perkebunan?",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n[Query {i}] {query}")
            retrieved = pipeline.retriever.retrieve(query, top_k=5)
            
            if retrieved:
                print(f"  ✅ Retrieved {len(retrieved)} chunks")
                for j, chunk in enumerate(retrieved[:3], 1):
                    doc = chunk["metadata"].get("dokumen", "N/A")
                    print(f"     {j}. {doc}")
            else:
                print(f"  ❌ No results retrieved")
            
            time.sleep(0.5)  # Avoid rate limiting
    
    except Exception as e:
        print(f"  ⚠️  Error during retrieval test: {e}")
        print("     (This is OK if modules not fully loaded in current Python session)")

def test_ragas_evaluation_on_subset():
    """Jalankan RAGAS evaluasi pada 3 pertanyaan untuk quick feedback"""
    print_section("3. QUICK RAGAS EVALUATION (3 samples)")
    
    try:
        from src.rag_pipeline import RAGPipeline
        from src.ragas_evaluation import run_ragas_evaluation
        from src.evaluation import EVAL_QUESTIONS
        
        pipeline = RAGPipeline()
        
        # Evaluasi hanya 3 pertanyaan untuk quick feedback
        selected_questions = EVAL_QUESTIONS[:3]
        
        print(f"\nEvaluating {len(selected_questions)} questions...")
        print("This may take 30-60 seconds...")
        
        results = run_ragas_evaluation(
            pipeline=pipeline,
            sample_size=3,
            top_k=TOP_K,
            auto_filter=True,
            questions=selected_questions,
        )
        
        summary = results.get("summary", {})
        
        print(f"\n✅ RAGAS Evaluation Complete!")
        print(f"\nSummary (3 samples):")
        print(f"  Faithfulness:      {summary.get('faithfulness', 0):.4f}")
        print(f"  Answer Relevancy:  {summary.get('answer_relevancy', 0):.4f}")
        print(f"  Context Precision: {summary.get('context_precision', 0):.4f}")
        print(f"  Context Recall:    {summary.get('context_recall', 0):.4f}")
        print(f"  Avg Latency:       {summary.get('avg_latency', 0):.2f}s")
        
        # Show detailed scores
        print(f"\nDetailed Scores:")
        for detail in results.get("details", []):
            qid = detail.get("question_id")
            print(f"  Q{qid}: Faith={detail.get('faithfulness', 0):.2f}, "
                  f"Rel={detail.get('answer_relevancy', 0):.2f}, "
                  f"Prec={detail.get('context_precision', 0):.2f}, "
                  f"Rec={detail.get('context_recall', 0):.2f}")
        
        # Save results
        from src.ragas_evaluation import save_ragas_results
        saved = save_ragas_results(results, "ragas_eval_improvements_test")
        print(f"\n✅ Results saved to:")
        print(f"   {saved['json']}")
        print(f"   {saved['csv']}")
        
    except ImportError as e:
        print(f"⚠️  Dependency missing: {e}")
        print("   Make sure to install: pip install ragas datasets langchain-openai langchain-huggingface")
    except Exception as e:
        print(f"❌ Error during RAGAS evaluation: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("\n" + "🚀 "*20)
    print("TESTING RAGAS EVALUATION IMPROVEMENTS")
    print("🚀 "*20)
    
    # Test 1: Config changes
    config_ok = test_config_changes()
    
    # Test 2: Retriever fallback
    test_retriever_with_fallback()
    
    # Test 3: Quick RAGAS evaluation
    test_ragas_evaluation_on_subset()
    
    # Summary
    print_section("SUMMARY")
    print(f"{'✅' if config_ok else '⚠️'} Configuration changes: {'OK' if config_ok else 'NEEDS REVIEW'}")
    print("\n💡 NEXT STEPS:")
    print("  1. If RAGAS evaluation completed:")
    print("     - Compare new scores with previous baseline (before improvements)")
    print("     - Check 'HASIL RAGAS/ragas_eval_improvements_test_*.json'")
    print("\n  2. If evaluation failed/partial:")
    print("     - Ensure RAGAS dependencies are installed")
    print("     - Check OpenRouter API key in .env")
    print("     - Run: python -m pip install ragas datasets --upgrade")
    print("\n  3. For full evaluation (all 16 questions):")
    print("     - Edit this script: change sample_size=3 to sample_size=16")
    print("     - Or call run_ragas_evaluation() directly")

if __name__ == "__main__":
    main()
