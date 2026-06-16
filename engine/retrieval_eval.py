import re
from typing import Dict, List, Set


def _tokens(text: str) -> Set[str]:
    return {token for token in re.findall(r"[\w-]+", text.lower()) if len(token) > 2}


class RetrievalEvaluator:
    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    def _overlap_score(self, expected_answer: str, answer: str) -> float:
        expected_tokens = _tokens(expected_answer)
        answer_tokens = _tokens(answer)
        if not expected_tokens:
            return 0.0
        return min(1.0, len(expected_tokens & answer_tokens) / max(8, len(expected_tokens) * 0.35))

    async def score(self, case: Dict, response: Dict) -> Dict:
        expected_ids = case.get("expected_retrieval_ids", [])
        retrieved_ids = response.get("retrieved_ids", [])
        contexts = " ".join(response.get("contexts", []))
        answer = response.get("answer", "")

        hit_rate = self.calculate_hit_rate(expected_ids, retrieved_ids)
        mrr = self.calculate_mrr(expected_ids, retrieved_ids)
        relevancy = self._overlap_score(case.get("expected_answer", ""), answer)
        faithfulness = self._overlap_score(contexts, answer)

        return {
            "faithfulness": round(faithfulness, 3),
            "relevancy": round(relevancy, 3),
            "retrieval": {
                "hit_rate": hit_rate,
                "mrr": round(mrr, 3),
                "expected_ids": expected_ids,
                "retrieved_ids": retrieved_ids,
            },
        }

    async def evaluate_batch(self, dataset: List[Dict], responses: List[Dict]) -> Dict:
        scores = [await self.score(case, response) for case, response in zip(dataset, responses)]
        total = len(scores) or 1
        return {
            "avg_hit_rate": sum(score["retrieval"]["hit_rate"] for score in scores) / total,
            "avg_mrr": sum(score["retrieval"]["mrr"] for score in scores) / total,
        }
