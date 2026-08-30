"""Create golden dataset script."""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


def create_golden_dataset():
    """Create golden dataset for evaluation."""
    golden = [
        {
            "query": "Find 30-second clips where Messi is drinking from a Pepsi bottle, Adidas logo is visible, Nike is not visible, and the clip is cleared for Germany digital highlights.",
            "expected_intent": {
                "type": "search",
                "talents": ["Messi"],
                "brands": {"required": ["Adidas", "Pepsi"], "excluded": ["Nike"]},
                "actions": ["drinking"],
                "territory": "Germany",
                "usage_type": "digital_highlights",
                "duration": 30,
            },
            "expected_tools": ["vector_search", "bm25_search", "logo_detection", "rights_check", "exclusion_check"],
        },
        {
            "query": "Find clips of Ronaldo scoring goals with visible brand sponsors",
            "expected_intent": {
                "type": "search",
                "talents": ["Ronaldo"],
                "actions": ["scoring"],
                "brands": {"required": [], "excluded": []},
            },
            "expected_tools": ["vector_search", "bm25_search", "talent_match"],
        },
        {
            "query": "Search for sports highlights cleared for USA broadcast",
            "expected_intent": {
                "type": "search",
                "territory": "USA",
                "usage_type": "broadcast",
            },
            "expected_tools": ["vector_search", "rights_check"],
        },
    ]

    path = os.path.join(PROJECT_ROOT, "evaluation", "golden_dataset.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(golden, f, indent=2)

    print(f"Created golden dataset at {path}")


if __name__ == "__main__":
    create_golden_dataset()