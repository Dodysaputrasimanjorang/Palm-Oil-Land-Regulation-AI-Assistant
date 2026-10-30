#!/usr/bin/env python3
"""
Run full RAGAS evaluation dengan perubahan improvements.
Compare dengan baseline: ragas_eval_20260504_034750.json
"""

import sys
import io
from pathlib import Path
import json

# Fix encoding for Windows PowerShell
if sys.stdout.encoding.lower() in ('cp1252', 'cp850'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.rag_pipeline import RAGPipeline
from src.ragas_evaluation import run_ragas_evaluation, save_ragas_results
from src.evaluation import EVAL_QUESTIONS

def main():
    print("\n" + "="*80)
    print("RUNNING FULL RAGAS EVALUATION WITH IMPROVEMENTS")
    print("="*80)
    
    pipeline = RAGPipeline()
    
    print(f"\nEvaluating {len(EVAL_QUESTIONS[:5])} questions...")
    print("This will take 2-5 minutes...\n")
    
    try:
        results = run_ragas_evaluation(
            pipeline=pipeline,
            sample_size=5,  # Evaluate semua 5 pertanyaan
            top_k=15,  # Gunakan TOP_K yang sudah dinaikkan
            auto_filter=True,
        )
        
        # Display results
        summary = results.get("summary", {})
        
        print("\n" + "="*80)
        print("EVALUATION RESULTS (WITH IMPROVEMENTS)")
        print("="*80)
        
        print(f"\n📊 Summary Metrics:")
        print(f"  Faithfulness:       {summary.get('faithfulness', 0):.4f}")
        print(f"  Answer Relevancy:   {summary.get('answer_relevancy', 0):.4f}")
        print(f"  Context Precision:  {summary.get('context_precision', 0):.4f}")
        print(f"  Context Recall:     {summary.get('context_recall', 0):.4f}")
        print(f"  Average Latency:    {summary.get('avg_latency', 0):.2f}s")
        
        print(f"\n📋 Detailed Scores per Question:")
        for detail in results.get("details", []):
            qid = detail.get("question_id")
            q_text = detail.get("question", "")[:60]
            print(f"\n  Q{qid}: {q_text}...")
            print(f"    Faithfulness:      {detail.get('faithfulness', 0):.4f}")
            print(f"    Answer Relevancy:  {detail.get('answer_relevancy', 0):.4f}")
            print(f"    Context Precision: {detail.get('context_precision', 0):.4f}") 
            print(f"    Context Recall:    {detail.get('context_recall', 0):.4f}")
            print(f"    Latency:           {detail.get('latency', 0):.2f}s")
        
        # Save results
        saved = save_ragas_results(results, "ragas_eval_improved")
        print(f"\n✅ Results saved:")
        print(f"   {saved['json']}")
        print(f"   {saved['csv']}")
        
        # Comparison dengan baseline
        print("\n" + "="*80)
        print("BASELINE COMPARISON")
        print("="*80)
        
        baseline = {
            'faithfulness': 0.3500,
            'answer_relevancy': 0.3731,
            'context_precision': 0.4025,
            'context_recall': 0.6000
        }
        
        print(f"\n{'Metric':<20} {'Before':>12} {'After':>12} {'Change':>12}")
        print("-" * 60)
        
        for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
            before = baseline[metric]
            after = summary.get(metric, 0)
            change = after - before
            pct = (change / before * 100) if before != 0 else 0
            
            print(f"{metric:<20} {before:>12.4f} {after:>12.4f} {pct:>11.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
