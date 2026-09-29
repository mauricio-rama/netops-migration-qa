import json
from pathlib import Path

REPORT_FILE = Path("reports/migration_quality_report.json")
CONTEXT_FILE = Path("agents/context/agent_context.json")


def investigate_quality():
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

    validations = report["validations"]

    failed = [
        validation
        for validation in validations
        if validation["status"] == "FAILED"
    ]

    print("=== Data Quality Investigation Agent ===")
    print(f"Project: {context['project']}")
    print(f"Purpose: {context['purpose']}")
    print(f"Total validations: {report['total_validations']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Overall status: {report['overall_status']}")

    print("\nQuality dimensions:")
    for dimension in context["quality_dimensions"]:
        print(f"- {dimension}")

    if not failed:
        print("\nInvestigation result:")
        print("No data-quality issues detected.")
        print("All migration validations passed.")
        return

    print("\nInvestigation result:")
    print("Data-quality issues detected.")

    for validation in failed:
        name = validation["name"]

        if "transformation" in name:
            issue_type = "Transformation rule"
        elif "count" in name:
            issue_type = "Record count reconciliation"
        elif "missing" in name:
            issue_type = "Missing records"
        elif "duplicate" in name:
            issue_type = "Duplicate records"
        elif "mandatory" in name:
            issue_type = "Mandatory fields"
        elif "referential" in name:
            issue_type = "Referential integrity"
        else:
            issue_type = "Unknown data-quality issue"

        print(f"- {issue_type}: {name}")

    print("\nRecommendation:")
    print("Investigate and resolve the failed validations before migration readiness.")


if __name__ == "__main__":
    investigate_quality()