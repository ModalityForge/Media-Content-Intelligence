# Public Evaluation Guide

Author: Prosenjit Banerjee <prosenjit.banerjee@gmail.com>

The public edition evaluates the application contract without publishing a
private golden dataset, downloaded media, or the author's extended evaluation
pipeline.

## Included checks

| Test area | Evidence |
|---|---|
| API | Routes, schemas, health, feedback, traceable search responses |
| Retrieval | Query-sensitive ordering and deterministic local catalog results |
| Agents | Orchestrator and evidence-validator state transitions |
| Security | Input/output guard behavior and publication policy |
| Documentation | Editable diagrams, rendered diagrams, README claims |
| Public boundary | No import dependency on ignored private modules |

Run the complete public suite with:

```bash
pytest
```

## Smoke evaluation with user data

1. Add a few licensed, descriptively named videos under `data/raw/smoke/`.
2. Start the API.
3. issue queries that should match and queries that should not match.
4. Confirm that rankings change with the query and point to real playable files.
5. Inspect evidence-validation fields; absent annotations should require review.

Useful retrieval measures for a user-owned labelled set include Precision@K,
Recall@K, mean reciprocal rank, and nDCG. Rights and evidence decisions should
also be evaluated for false approvals, because a false approval is more severe
than a conservative review request.

## Private evaluation boundary

Golden fixtures, research evaluators, online monitors, and dataset-specific
benchmarks remain local-only. They are not required to run public inference and
must not be inferred to exist in a fresh clone.

