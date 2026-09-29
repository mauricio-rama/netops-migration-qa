import json
from pathlib import Path
from datetime import datetime

REPORT_FILE = Path("reports/migration_quality_report.json")
CONTEXT_FILE = Path("agents/context/agent_context.json")
OUTPUT_FILE = Path("reports/agent_assessment_report.json")


def build_agent_report():
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

    status = report["overall_status"]
    failed = report["failed"]

    failed_validations = [
        validation["name"]
        for validation in report["validations"]
        if validation["status"] == "FAILED"
    ]

    if status == "PASS" and failed == 0:
        investigation_status = "NO_ISSUES"
        readiness = "READY"
        recommendation = (
            "Migration can proceed from a data-quality validation perspective."
        )
    else:
        investigation_status = "ISSUES_DETECTED"
        readiness = "NOT_READY"
        recommendation = (
            "Migration should not proceed until all validation failures are resolved."
        )

    consolidated_report = {
        "generated_at": datetime.now().isoformat(),
        "project": context["project"],
        "purpose": context["purpose"],
        "validation": {
            "total": report["total_validations"],
            "passed": report["passed"],
            "failed": report["failed"],
            "status": status,
            "failed_validations": failed_validations
        },
        "agents": {
            "migration_validation": status,
            "data_quality_investigation": investigation_status,
            "migration_readiness": readiness
        },
        "decision_policy": context["decision_policy"],
        "recommendation": recommendation
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(consolidated_report, file, indent=4)

    print(json.dumps(consolidated_report, indent=4))


if __name__ == "__main__":
    build_agent_report()