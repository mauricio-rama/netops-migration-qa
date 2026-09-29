import json
from pathlib import Path

REPORT_FILE = Path("reports/migration_quality_report.json")


def analyze_migration():
    if not REPORT_FILE.exists():
        return "Migration quality report not found."

    with open(REPORT_FILE, "r", encoding="utf-8") as file:
        report = json.load(file)

    total = report["total_validations"]
    passed = report["passed"]
    failed = report["failed"]
    status = report["overall_status"]

    print("\n=== Migration Validation Agent ===")
    print(f"Total validations: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Overall status: {status}")

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
