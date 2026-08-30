"""Offline evaluation runner."""

import json
import os
from evaluation import retrieval_eval, temporal_eval, brand_safety_eval, rights_eval, agent_trajectory_eval


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


def run_offline_evaluation():
    """Run all offline evaluations."""
    print("Running offline evaluation...")

    golden_path = os.path.join(PROJECT_ROOT, "evaluation", "golden_dataset.json")
    with open(golden_path, "r") as f:
        golden_dataset = json.load(f)

    results = {
        "retrieval": retrieval_eval.evaluate_retrieval_system(),
        "temporal": temporal_eval.evaluate_temporal(),
        "brand_safety": brand_safety_eval.evaluate_brand_safety_system(),
        "rights": rights_eval.evaluate_rights_system(),
        "agent_trajectory": agent_trajectory_eval.evaluate_agent_trajectory(),
    }

    print("\n=== Offline Evaluation Results ===")
    for name, result in results.items():
        print(f"\n{name}: {result}")

    return results


if __name__ == "__main__":
    run_offline_evaluation()