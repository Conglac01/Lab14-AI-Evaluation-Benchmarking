# Báo cáo Phân tích Thất bại

## 1. Tổng quan Benchmark
- Hình thức làm bài: 1 thành viên, đảm nhiệm cả Data, AI/Backend, DevOps/Analyst.
- Tổng số cases: 60
- Pass/Fail: 60/0 theo ngưỡng `final_score >= 3`
- Avg LLM-Judge score: 4.958/5.0
- Retrieval Hit Rate: 0.967
- MRR: 0.967
- Faithfulness: 0.902
- Relevancy: 0.998
- Multi-Judge Agreement Rate: 0.995
- Judge models: `gpt-4o-mini-heuristic`, `claude-3-5-sonnet-heuristic`
- Avg latency: 0.0227s/case
- Estimated cost: $0.000814 cho 60 cases
- Regression Gate: APPROVE, V2 tăng 0.042 điểm so với V1

## 2. Phân nhóm lỗi
| Nhóm lỗi | Số lượng | Nguyên nhân dự kiến |
|----------|----------|---------------------|
| Failed cases theo judge threshold | 0 | Không có case dưới ngưỡng 3.0 |
| Retrieval miss nhưng answer vẫn pass | 2 | Case out-of-context/ambiguous không có keyword tài liệu rõ, agent pass nhờ refusal/clarification |
| Cost increase V2 | 1 regression signal | V2 trả lời đầy đủ hơn nên dùng nhiều token hơn V1 |

## 3. Phân tích 5 Whys

### Case #56: Out-of-context refund policy
1. Symptom: Retrieval không lấy đúng `doc_prompt_001`, nhưng câu trả lời vẫn pass vì agent nói không thấy bằng chứng.
2. Why 1: Câu hỏi nói về "chính sách hoàn tiền", không có keyword trực tiếp trong knowledge base.
3. Why 2: Retriever lexical chỉ dựa trên overlap token, chưa có semantic matching cho intent out-of-context.
4. Why 3: Dataset hard case cố tình hỏi ngoài miền để kiểm tra hallucination.
5. Why 4: Pipeline chưa có classifier riêng để nhận diện câu hỏi ngoài phạm vi trước retrieval.
6. Root Cause: Retrieval stage thiếu out-of-domain detector; hiện được bù bằng logic refusal ở generation.

### Case #59: Ambiguous question
1. Symptom: Retrieval miss vì câu "nó có tốt không?" không chứa thực thể rõ ràng.
2. Why 1: Câu hỏi không nói "nó" là metric, judge, release gate hay retrieval.
3. Why 2: Retriever không thể suy luận antecedent nếu không có hội thoại trước đó.
4. Why 3: Agent chưa có memory multi-turn để nối câu hỏi mơ hồ với ngữ cảnh trước.
5. Why 4: Benchmark hiện là single-turn nên ambiguity cần được xử lý bằng clarification.
6. Root Cause: Thiếu module conversation state; response pass vì agent hỏi lại thay vì bịa.

### Regression Signal: V2 cost tăng nhẹ
1. Symptom: Estimated cost tăng từ $0.000720 lên $0.000814.
2. Why 1: V2 trả lời đầy đủ hơn, trích nguồn và liệt kê source IDs.
3. Why 2: Token output tăng từ 4750 lên 5482.
4. Why 3: Prompting ưu tiên faithfulness và auditability hơn độ ngắn.
5. Why 4: Release gate hiện cho phép tăng cost nhỏ nếu quality không regression.
6. Root Cause: Chưa có compression step sau generation để rút gọn câu trả lời mà vẫn giữ citation.

## 4. Kế hoạch cải tiến
- Thêm out-of-domain detector trước retrieval để tăng Hit Rate cho hard cases ngoài phạm vi.
- Thêm semantic reranking hoặc BM25+embedding hybrid để xử lý câu hỏi ít keyword.
- Thêm conversation memory cho ambiguous multi-turn questions.
- Cache judge outputs cho unchanged cases để hướng tới giảm ít nhất 30% chi phí eval.
- Dùng judge nhỏ hoặc heuristic judge cho easy cases, chỉ multi-judge đầy đủ cho hard/fail/regression slices.
- Thêm response compression để giảm ít nhất 30% token eval mà vẫn giữ source IDs.
