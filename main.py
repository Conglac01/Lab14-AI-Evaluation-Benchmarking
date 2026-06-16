import asyncio
import json
import os
import time
from collections import Counter
from typing import Dict, List, Tuple

from agent.main_agent import MainAgent
from engine.llm_judge import LLMJudge
from engine.retrieval_eval import RetrievalEvaluator
from engine.runner import BenchmarkRunner


QUALITY_THRESHOLD = 3.5
MIN_HIT_RATE = 0.80
MAX_AVG_LATENCY = 0.25


def load_dataset() -> List[Dict]:
    if not os.path.exists("data/golden_set.jsonl"):
        raise FileNotFoundError("Thiếu data/golden_set.jsonl. Hãy chạy python data/synthetic_gen.py trước.")

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if len(dataset) < 50:
        raise ValueError("Golden dataset phải có ít nhất 50 cases.")
    return dataset


def summarize(results: List[Dict], version: str, elapsed: float) -> Dict:
    total = len(results)
    safe_total = total or 1
    pass_count = sum(1 for result in results if result.get("status") == "pass")
    type_counts = Counter(result.get("metadata", {}).get("type", "unknown") for result in results)
    failure_types = Counter(
        result.get("metadata", {}).get("type", "unknown")
        for result in results
        if result.get("status") != "pass"
    )
    conflict_count = sum(1 for result in results if result["judge"]["conflict_delta"] > 1.0)
    judge_models = results[0]["judge"].get("judge_models", []) if results else []

    metrics = {
        "avg_score": round(sum(result["judge"]["final_score"] for result in results) / safe_total, 3),
        "pass_rate": round(pass_count / safe_total, 3),
        "hit_rate": round(sum(result["ragas"]["retrieval"]["hit_rate"] for result in results) / safe_total, 3),
        "mrr": round(sum(result["ragas"]["retrieval"]["mrr"] for result in results) / safe_total, 3),
        "faithfulness": round(sum(result["ragas"]["faithfulness"] for result in results) / safe_total, 3),
        "relevancy": round(sum(result["ragas"]["relevancy"] for result in results) / safe_total, 3),
        "agreement_rate": round(sum(result["judge"]["agreement_rate"] for result in results) / safe_total, 3),
        "avg_latency_sec": round(sum(result["latency"] for result in results) / safe_total, 4),
        "total_tokens": sum(result["tokens_used"] for result in results),
        "estimated_cost_usd": round(sum(result["estimated_cost_usd"] for result in results), 6),
        "wall_clock_sec": round(elapsed, 3),
        "judge_conflict_count": conflict_count,
    }

    return {
        "metadata": {
            "version": version,
            "total": total,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "case_type_distribution": dict(type_counts),
            "judge_models": judge_models,
        },
        "metrics": metrics,
        "failure_clusters": dict(failure_types),
    }


def release_gate(v1_summary: Dict, v2_summary: Dict) -> Dict:
    v1 = v1_summary["metrics"]
    v2 = v2_summary["metrics"]
    delta_score = round(v2["avg_score"] - v1["avg_score"], 3)
    delta_cost = round(v2["estimated_cost_usd"] - v1["estimated_cost_usd"], 6)

    checks = {
        "quality_threshold": v2["avg_score"] >= QUALITY_THRESHOLD,
        "retrieval_threshold": v2["hit_rate"] >= MIN_HIT_RATE,
        "latency_threshold": v2["avg_latency_sec"] <= MAX_AVG_LATENCY,
        "no_quality_regression": delta_score >= 0,
    }

    return {
        "decision": "APPROVE" if all(checks.values()) else "BLOCK_RELEASE",
        "checks": checks,
        "delta": {
            "avg_score": delta_score,
            "estimated_cost_usd": delta_cost,
            "hit_rate": round(v2["hit_rate"] - v1["hit_rate"], 3),
            "avg_latency_sec": round(v2["avg_latency_sec"] - v1["avg_latency_sec"], 4),
        },
        "cost_reduction_plan": [
            "Target at least 30% eval-cost reduction by caching judge outputs for unchanged cases.",
            "Use cheaper heuristic or small-model judge for easy fact-check cases.",
            "Run full multi-judge only on failures, hard cases, and changed retrieval slices.",
        ],
    }


async def run_benchmark_with_results(agent_version: str) -> Tuple[List[Dict], Dict]:
    dataset = load_dataset()
    print(f"Running benchmark for {agent_version} on {len(dataset)} cases...")

    start = time.perf_counter()
    runner = BenchmarkRunner(MainAgent(version=agent_version), RetrievalEvaluator(), LLMJudge())
    results = await runner.run_all(dataset, batch_size=10)
    elapsed = time.perf_counter() - start
    return results, summarize(results, agent_version, elapsed)


async def main():
    try:
        v1_results, v1_summary = await run_benchmark_with_results("v1")
        v2_results, v2_summary = await run_benchmark_with_results("v2")
    except Exception as exc:
        print(f"Benchmark failed: {exc}")
        return

    gate = release_gate(v1_summary, v2_summary)
    v2_summary["regression"] = {
        "baseline": v1_summary["metrics"],
        "candidate": v2_summary["metrics"],
        "release_gate": gate,
    }

    report_payload = {
        "v1_results": v1_results,
        "v2_results": v2_results,
        "release_gate": gate,
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(report_payload, f, ensure_ascii=False, indent=2)

    print("\n--- Regression Summary ---")
    print(f"V1 avg score: {v1_summary['metrics']['avg_score']}")
    print(f"V2 avg score: {v2_summary['metrics']['avg_score']}")
    print(f"Hit Rate: {v2_summary['metrics']['hit_rate']}")
    print(f"MRR: {v2_summary['metrics']['mrr']}")
    print(f"Agreement Rate: {v2_summary['metrics']['agreement_rate']}")
    print(f"Estimated V2 Cost: ${v2_summary['metrics']['estimated_cost_usd']}")
    print(f"Decision: {gate['decision']}")


if __name__ == "__main__":
    asyncio.run(main())
