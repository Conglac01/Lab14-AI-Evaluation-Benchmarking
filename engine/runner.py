import asyncio
import time
from typing import List, Dict


class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge

    async def run_single_test(self, test_case: Dict) -> Dict:
        start_time = time.perf_counter()
        try:
            response = await self.agent.query(test_case["question"])
            latency = time.perf_counter() - start_time
            ragas_scores = await self.evaluator.score(test_case, response)
            judge_result = await self.judge.evaluate_multi_judge(
                test_case["question"],
                response["answer"],
                test_case["expected_answer"],
            )
            tokens_used = response.get("metadata", {}).get("tokens_used", 0)
            estimated_cost_usd = round(tokens_used * 0.00000015, 6)

            return {
                "id": test_case.get("id"),
                "test_case": test_case["question"],
                "expected_answer": test_case["expected_answer"],
                "expected_retrieval_ids": test_case.get("expected_retrieval_ids", []),
                "agent_response": response["answer"],
                "retrieved_ids": response.get("retrieved_ids", []),
                "latency": round(latency, 4),
                "tokens_used": tokens_used,
                "estimated_cost_usd": estimated_cost_usd,
                "ragas": ragas_scores,
                "judge": judge_result,
                "metadata": test_case.get("metadata", {}),
                "status": "fail" if judge_result["final_score"] < 3 else "pass",
            }
        except Exception as exc:
            return {
                "id": test_case.get("id"),
                "test_case": test_case.get("question"),
                "latency": round(time.perf_counter() - start_time, 4),
                "status": "error",
                "error": str(exc),
            }

    async def run_all(self, dataset: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        Chạy song song bằng asyncio.gather với giới hạn batch_size để không bị Rate Limit.
        """
        results = []
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i + batch_size]
            tasks = [self.run_single_test(case) for case in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
        return results
