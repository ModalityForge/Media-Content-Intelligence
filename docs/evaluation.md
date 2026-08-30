# Evaluation Guide

## Golden Dataset

The golden dataset contains example media queries with expected intents and tool sequences.

Location: `evaluation/golden_dataset.json`

Example entry:
```json
{
  "query": "Find 30-second clips where Messi is drinking from a Pepsi bottle...",
  "expected_intent": {
    "type": "search",
    "talents": ["Messi"],
    "brands": {"required": ["Adidas", "Pepsi"], "excluded": ["Nike"]},
    "actions": ["drinking"],
    "territory": "Germany",
    "usage_type": "digital_highlights",
    "duration": 30
  },
  "expected_tools": ["vector_search", "bm25_search", "logo_detection", "rights_check"]
}
```

## Evaluation Types

### 1. Retrieval Evaluation
- **Metric**: Precision@K
- **Location**: `evaluation/retrieval_eval.py`

### 2. Temporal Evaluation
- **Metric**: Timestamp overlap
- **Location**: `evaluation/temporal_eval.py`

### 3. Brand Safety Evaluation
- **Metric**: Pass rate
- **Location**: `evaluation/brand_safety_eval.py`

### 4. Rights Evaluation
- **Metric**: Rights clearance rate
- **Location**: `evaluation/rights_eval.py`

### 5. Agent Trajectory Evaluation
- **Metric**: Tool sequence correctness
- **Location**: `evaluation/agent_trajectory_eval.py`

## Running Evaluations

```bash
# Run all offline evaluations
python evaluation/offline_eval.py

# Run specific evaluation
python evaluation/retrieval_eval.py

# Run online monitor
python evaluation/online_monitor.py
```

## HITL Review

When confidence is below threshold or critical criteria fail, clips are flagged for Human-In-The-Loop review.

The EvidenceValidatorAgent determines when HITL is needed based on:
- Overall confidence < 0.7
- Critical criteria failures (rights, exclusion)
- Ambiguous evidence