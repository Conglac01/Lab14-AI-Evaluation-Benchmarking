KNOWLEDGE_BASE = [
    {
        "id": "doc_eval_001",
        "title": "AI Evaluation Overview",
        "text": (
            "AI Evaluation is the engineering process of measuring an AI system with repeatable metrics, "
            "golden datasets, human review, and automated judges. It helps teams know which changes improve "
            "quality and which changes create regressions."
        ),
        "keywords": ["evaluation", "metrics", "golden dataset", "regression"],
    },
    {
        "id": "doc_retrieval_001",
        "title": "Retrieval Hit Rate",
        "text": (
            "Hit Rate checks whether at least one expected document appears in the top-k retrieved documents. "
            "For RAG systems, a low hit rate means the generator may never see the evidence needed to answer."
        ),
        "keywords": ["hit rate", "top-k", "retrieval", "rag"],
    },
    {
        "id": "doc_retrieval_002",
        "title": "Mean Reciprocal Rank",
        "text": (
            "MRR, or Mean Reciprocal Rank, rewards retrieval systems that place the first relevant document "
            "near the top. If the relevant document is ranked first the reciprocal rank is 1.0; if ranked second it is 0.5."
        ),
        "keywords": ["mrr", "reciprocal rank", "retrieval", "ranking", "benchmark"],
    },
    {
        "id": "doc_judge_001",
        "title": "Multi-Judge Consensus",
        "text": (
            "A multi-judge evaluation uses at least two independent scoring models or rubrics. Agreement rate "
            "shows how often judges reach similar conclusions, and conflict handling reduces overreliance on one judge."
        ),
        "keywords": ["multi judge", "agreement rate", "consensus", "rubric", "bất đồng", "judge"],
    },
    {
        "id": "doc_gate_001",
        "title": "Regression Release Gate",
        "text": (
            "A regression release gate compares a new agent against a baseline. The gate can approve a release "
            "when quality improves and cost or latency remain below agreed thresholds."
        ),
        "keywords": ["release gate", "regression", "baseline", "rollback"],
    },
    {
        "id": "doc_cost_001",
        "title": "Evaluation Cost Control",
        "text": (
            "Evaluation cost is estimated from token usage, judge model price, and number of test cases. Teams "
            "can reduce cost with sampling, caching, smaller judges for easy cases, and rerunning only changed slices."
        ),
        "keywords": ["cost", "tokens", "sampling", "caching", "chi phí", "giảm"],
    },
    {
        "id": "doc_async_001",
        "title": "Async Benchmark Runner",
        "text": (
            "Async benchmark runners execute test cases concurrently while respecting rate limits. Batching with "
            "asyncio.gather improves throughput and makes a 50-case evaluation finish quickly."
        ),
        "keywords": ["async", "benchmark", "batching", "latency"],
    },
    {
        "id": "doc_failure_001",
        "title": "Failure Analysis",
        "text": (
            "Failure clustering groups bad answers into patterns such as hallucination, incomplete answer, wrong "
            "retrieval, stale context, or tone mismatch. A 5 Whys analysis then traces each symptom to a root cause."
        ),
        "keywords": ["failure analysis", "5 whys", "hallucination", "clustering"],
    },
    {
        "id": "doc_redteam_001",
        "title": "Red Team Cases",
        "text": (
            "Red team cases include prompt injection, out-of-context questions, ambiguous requests, and conflicting "
            "evidence. The expected behavior is to stay grounded, ask for clarification, or say when the answer is not in the documents."
        ),
        "keywords": ["red team", "prompt injection", "ambiguous", "out-of-context"],
    },
    {
        "id": "doc_prompt_001",
        "title": "Grounded Prompting",
        "text": (
            "A grounded support agent should answer from retrieved context, cite source IDs, avoid unsupported claims, "
            "and explicitly state uncertainty when the evidence is missing."
        ),
        "keywords": ["grounded", "prompting", "sources", "uncertainty"],
    },
]
