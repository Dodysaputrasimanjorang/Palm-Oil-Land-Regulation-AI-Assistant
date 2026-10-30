#!/usr/bin/env python3
"""
Quick test untuk prompt improvements dengan few-shot examples.
Jalankan 3 pertanyaan dan lihat apakah format jawaban sudah sesuai.
"""

import sys
import io
from pathlib import Path

# Fix encoding for Windows PowerShell
if sys.stdout.encoding.lower() in ('cp1252', 'cp850'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rag_pipeline import RAGPipeline
from src.config import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE, BM25_WEIGHT

def main():
    print("\n" + "="*80)
    print("TEST: Few-Shot Prompt Improvements")
    print("="*80)
    
    print(f"\nConfig Check:")
    print(f"  BM25_WEIGHT: {BM25_WEIGHT} (should be 0.45)")
    print(f"  System prompt has few-shot: {'Example 1' in RAG_SYSTEM_PROMPT}")
    print(f"  User prompt has format guide: {'Sumber:' in RAG_USER_PROMPT_TEMPLATE}")
    
    pipeline = RAGPipeline()
    
    test_queries = [
        "Apakah boleh membuka lahan sawit di kawasan hutan lindung?",
        "Apa sanksi pidana bagi pelaku pembakaran lahan perkebunan?",
        "Bagaimana prosedur permohonan izin usaha perkebunan?",
    ]
    
    print("\n" + "-"*80)
    print("TESTING 3 QUERIES")
    print("-"*80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}] {query}")
        
        try:
            result = pipeline.query(query, top_k=15, auto_filter=True)
            answer = result.get("answer", "")
            
            # Check if answer has "Sumber:" at the end
            has_sumber = "Sumber:" in answer
            
            print(f"  Answer (preview): {answer[:150]}...")
            print(f"  Has 'Sumber:' line: {'YES' if has_sumber else 'NO - NEED FIX'}")
            
            if not has_sumber:
                print(f"  Full answer:\n{answer}")
        
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nNext: Run full RAGAS evaluation to see if scores improve")

if __name__ == "__main__":
    main()
