import json
import subprocess
from datetime import datetime
from pathlib import Path


REPORT_FILE = Path("reports/migration_quality_report.json")
PYTEST_REPORT = Path("reports/pytest_report.json")


def run_tests():
    result = subprocess.run(
        [
            "pytest",
            "-v",
            "--json-report",
            f"--json-report-file={PYTEST_REPORT}"
        ],
        capture_output=True,
        text=True
    )

    return result


def build_report():
    pytest_data = json.loads(
        PYTEST_REPORT.read_text(encoding="utf-8")
    )

    tests = []

    for test in pytest_data["tests"]:
        name = test["nodeid"].split("::")[-1]

        status = test["outcome"].upper()

        tests.append({
            "name": name,
            "status": status
        })

    passed = sum(1 for test in tests if test["status"] == "PASSED")
    failed = sum(1 for test in tests if test["status"] == "FAILED")

    return {
        "execution_timestamp": datetime.now().isoformat(),
        "total_validations": len(tests),
        "passed": passed,
        "failed": failed,
        "overall_status": "PASS" if failed == 0 else "FAIL",
        "validations": tests
    }


def main():
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    run_tests()

    report = build_report()

    REPORT_FILE.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()