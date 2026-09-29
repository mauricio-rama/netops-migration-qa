import json
from pathlib import Path

REPORT_FILE = Path("reports/migration_quality_report.json")
CONTEXT_FILE = Path("agents/context/agent_context.json")


def analyze_migration():
    if not REPORT_FILE.exists():
        print("Migration quality report not found.")
        return

    if not CONTEXT_FILE.exists():
        print("Agent context not found.")
        return

    with open(REPORT_FILE, "r", encoding="utf-8") as file:
        report = json.load(file)

    with open(CONTEXT_FILE, "r", encoding="utf-8") as file:
        context = json.load(file)

    total = report["total_validations"]
    passed = report["passed"]
    failed = report["failed"]
    status = report["overall_status"]

    print("\n=== Migration Validation Agent ===")
    print(f"Project: {context['project']}")
    print(f"Purpose: {context['purpose']}")
    print(f"Total validations: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Overall status: {status}")

    print("\nDecision policy:")
    print(f"Quality gate: {context['decision_policy']['quality_gate']}")
    print(f"AI role: {context['decision_policy']['ai_role']}")
    print(
        "AI can override quality gate: "
        f"{context['decision_policy']['ai_can_override_quality_gate']}"
    )

    if status == "PASS":
        print("\nAgent assessment:")
        print("Migration validation completed successfully.")
        print("No validation failures were detected.")
        print("Migration is ready from a data-quality validation perspective.")
    else:
        print("\nAgent assessment:")
        print("Migration validation detected data-quality issues.")
        print("Migration should NOT be considered ready until failures are resolved.")


if __name__ == "__main__":
    analyze_migration()