# Individual Reflection - Conglac01

## Contribution
- Implemented an offline AI evaluation pipeline that can run without external API keys.
- Built a 60-case golden dataset with retrieval ground-truth IDs and red-team cases.
- Added retrieval metrics, multi-judge consensus, regression comparison, release gate, and cost reporting.

## Technical Notes
- Hit Rate measures whether at least one expected document appears in the retrieved top-k list.
- MRR rewards putting the first relevant document as high as possible in the ranking.
- Agreement Rate estimates whether two independent judges score the answer similarly.

## Lessons Learned
- Retrieval quality must be measured before answer quality because a generator cannot cite evidence it never receives.
- Multi-judge evaluation is more reliable than a single judge, especially for hard or adversarial cases.
- A release gate should block quality regression even when latency or cost improves.
