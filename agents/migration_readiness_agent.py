import json
from pathlib import Path


REPORT_FILE = Path("reports/migration_quality_report.json")


def assess_readiness():
    if not REPORT_FILE.exists():
        print("Migration quality report not found.")
        return

    with open(REPORT_FILE, "r", encoding="utf-8") as file:
        report = json.load(file)

    total = report["total_validations"]
    passed = report["passed"]
    failed = report["failed"]
    status = report["overall_status"]

    print("=== Migration Readiness Agent ===")
    print(f"Total validations: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Overall status: {status}")

    if status == "PASS" and failed == 0:
        readiness = "READY"
        recommendation = (
            "Migration can proceed from a data-quality validation perspective."
        )
    else:
        readiness = "NOT READY"
        recommendation = (
            "Migration should not proceed until all validation failures are resolved."
        )

    print("\nMigration readiness:")
    print(f"Status: {readiness}")

    print("\nRecommendation:")
    print(recommendation)


if __name__ == "__main__":
    assess_readiness()
