#!/usr/bin/env python3
"""Quick test of improvement changes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rag_pipeline import RAGPipeline
from src.evaluation import EVAL_QUESTIONS

print("\n" + "="*80)
print("TESTING IMPROVEMENTS: Query + Retrieval Enhancement")
print("="*80)

pipeline = RAGPipeline()

test_questions = EVAL_QUESTIONS[2:4]  # Questions 3-4: HGU and ISPO

for q_obj in test_questions:
    q = q_obj["question"]
    print(f"\n{'─'*80}")
    print(f"Q{q_obj['id']}: {q}")
    print(f"{'─'*80}")
    
    r = pipeline.query(q, top_k=6)
    
    ans = r["answer"]
    if len(ans) > 300:
        ans = ans[:300] + "..."
    print(f"\nAnswer:\n{ans}\n")
    
    print(f"Sources retrieved: {len(r['sources'])}")
    for i, src in enumerate(r["sources"][:5], 1):
        score_hybrid = src["scores"].get("hybrid", 0)
        score_lex = src["scores"].get("lexical_boost", 0)
        score_bm25 = src["scores"].get("bm25", 0)
        
        print(f"  [{i}] {src['dokumen']} | {src['pasal']}")
        print(f"      Scores: hybrid={score_hybrid:.3f} | lex_boost={score_lex:.3f} | bm25={round(score_bm25, 1)}")

print("\n" + "="*80)
print("Test complete. Improvements applied:")
print("  ✅ Embedding model: intfloat/multilingual-e5-large")
print("  ✅ Broader retrieval: top_k * 5 candidates")
print("  ✅ Lexical boost: phrase + metadata matching")
print("  ✅ Better prompt: focus on evidence-backed answers")
print("="*80 + "\n")
