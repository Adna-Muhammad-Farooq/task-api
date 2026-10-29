
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from triage_service import classify_message

CASES_FILE = Path(__file__).resolve().parent / "cases.json"


def main():
    with open(CASES_FILE, "r", encoding="utf-8") as file:
        cases = json.load(file)

    category_correct = 0
    urgency_correct = 0

    for case in cases:
        print(f"\nTesting case {case['id']}...")

        try:
            result = classify_message(case["text"])

            category_match = (
                result.category.value == case["expected_category"]
            )
            urgency_match = (
                result.urgency.value == case["expected_urgency"]
            )

            category_correct += category_match
            urgency_correct += urgency_match

            print("Expected category:", case["expected_category"])
            print("AI category:", result.category.value)
            print("Expected urgency:", case["expected_urgency"])
            print("AI urgency:", result.urgency.value)

        except Exception as error:
            print("Test failed:", type(error).__name__)

    total = len(cases)

    print("\n--- Evaluation Results ---")
    print(f"Total test cases: {total}")
    print(f"Category accuracy: {category_correct / total * 100:.1f}%")
    print(f"Urgency accuracy: {urgency_correct / total * 100:.1f}%")


if __name__ == "__main__":
    main()
