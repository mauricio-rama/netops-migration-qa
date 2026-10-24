
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

REPORT_FILE = REPORTS_DIR / "migration_quality_report.json"
PYTEST_REPORT = REPORTS_DIR / "pytest_report.json"
GX_REPORT = REPORTS_DIR / "great_expectations_report.json"

VALIDATION_COMMANDS = [
    {
        "name": "Pytest",
        "command": [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "--json-report",
            f"--json-report-file={PYTEST_REPORT}",
            "tests/test_customer_migration.py",
        ],
    },
    {
        "name": "Great Expectations",
        "command": [
            sys.executable,
            "src/validate_with_gx.py",
        ],
    },
]


def run_command(command):
    """Execute a validation command and capture its output."""
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "error": None,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": "",
            "error": f"{type(exc).__name__}: {exc}",
        }


def read_json(path):
    """Read a JSON file, returning None when unavailable or invalid."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def collect_pytest_results():
    """Collect individual test outcomes from the latest Pytest report."""
    data = read_json(PYTEST_REPORT)

    if data is None:
        return [], {
            "status": "ERROR",
            "passed": 0,
            "failed": 0,
            "total": 0,
        }

    tests = []

    for test in data.get("tests", []):
        outcome = test.get("outcome", "unknown").upper()

        if outcome == "PASSED":
            status = "PASS"
        elif outcome in {"FAILED", "ERROR"}:
            status = "FAIL"
        elif outcome in {"SKIPPED", "XFAILED"}:
            status = "SKIPPED"
        else:
            status = outcome

        entry = {
            "name": test.get("nodeid", "Unknown test").split("::")[-1],
            "validator": "Pytest",
            "status": status,
        }

        call_info = test.get("call", {})
        if status == "FAIL":
            entry["details"] = (
                call_info.get("longrepr")
                or test.get("setup", {}).get("longrepr")
                or "Test failed. See Pytest output."
            )

        tests.append(entry)

    passed = sum(item["status"] == "PASS" for item in tests)
    failed = sum(item["status"] == "FAIL" for item in tests)

    return tests, {
        "status": "PASS" if failed == 0 and tests else "FAIL",
        "passed": passed,
        "failed": failed,
        "total": len(tests),
    }


def collect_gx_results():
    """Collect individual expectations from the latest GX JSON report."""
    data = read_json(GX_REPORT)

    if data is None:
        return [], {
            "status": "ERROR",
            "passed": 0,
            "failed": 0,
            "total": 0,
        }

    expectations = []

    for item in data.get("expectations", []):
        status = "PASS" if item.get("success") else "FAIL"

        column = item.get("column")
        if item.get("column_A") and item.get("column_B"):
            column = f'{item["column_A"]} >= {item["column_B"]}'

        entry = {
            "name": item.get("expectation_type", "Unknown expectation"),
            "validator": "Great Expectations",
            "status": status,
            "table": item.get("table", data.get("table", "Unknown")),
            "column": column,
            "records_evaluated": item.get("element_count"),
            "unexpected_values": item.get("unexpected_count"),
        }

        if status == "FAIL":
            entry["details"] = (
                f'Unexpected values: {item.get("unexpected_count", "N/A")}'
            )

        expectations.append(entry)

    passed = sum(item["status"] == "PASS" for item in expectations)
    failed = sum(item["status"] == "FAIL" for item in expectations)

    return expectations, {
        "status": (
            "PASS" if failed == 0 and expectations else "FAIL"
        ),
        "passed": passed,
        "failed": failed,
        "total": len(expectations),
    }


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    command_results = {}

    # Run both validators even if the first one fails.
    for item in VALIDATION_COMMANDS:
        print(f'\n=== Running {item["name"]} ===')
        result = run_command(item["command"])
        command_results[item["name"]] = result

        print(result["stdout"])

        if result["stderr"]:
            print(result["stderr"], file=sys.stderr)

        if result["error"]:
            print(result["error"], file=sys.stderr)

        print(f'Exit code: {result["returncode"]}')

    pytest_tests, pytest_summary = collect_pytest_results()
    gx_tests, gx_summary = collect_gx_results()

    validations = pytest_tests + gx_tests

    passed = sum(item["status"] == "PASS" for item in validations)
    failed = sum(item["status"] == "FAIL" for item in validations)
    total = len(validations)

    # Missing reports or unsuccessful commands must never produce an overall PASS.
    execution_error = any(
        result["returncode"] != 0
        for result in command_results.values()
    )

    overall_status = (
        "PASS"
        if total > 0
        and failed == 0
        and not execution_error
        and pytest_summary["status"] == "PASS"
        and gx_summary["status"] == "PASS"
        else "FAIL"
    )

    report = {
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "total_validations": total,
        "passed": passed,
        "failed": failed,
        "quality_score": round(passed / total * 100, 2) if total else 0,
        "validator_summaries": {
            "Pytest": pytest_summary,
            "Great Expectations": gx_summary,
        },
        "command_results": {
            name: {
                "returncode": result["returncode"],
                "error": result["error"],
            }
            for name, result in command_results.items()
        },
        "validations": validations,
    }

    REPORT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== CONSOLIDATED DATA QUALITY REPORT ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if overall_status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
