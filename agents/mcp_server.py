import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "reports" / "migration_quality_report.json"
GX_REPORT_FILE = PROJECT_ROOT / "reports" / "great_expectations_report.json"

mcp = FastMCP("NetOps Migration QA")


@mcp.tool()
def get_migration_quality() -> dict:
    """Return the latest migration validation report, including passed and failed checks."""
    if not REPORT_FILE.exists():
        return {"error": "Migration quality report not found."}

    with REPORT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@mcp.tool()
def get_data_quality() -> dict:
    """Return the latest Great Expectations data quality report."""
    if not GX_REPORT_FILE.exists():
        return {"error": "Great Expectations report not found."}

    with GX_REPORT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@mcp.tool()
def get_project_status() -> dict:
    """Summarize the latest migration and data quality results."""
    status = {}

    if REPORT_FILE.exists():
        with REPORT_FILE.open("r", encoding="utf-8") as file:
            migration = json.load(file)

        status["migration"] = {
            "overall_status": migration.get("overall_status", "UNKNOWN"),
            "total_validations": migration.get("total_validations", 0),
            "passed": migration.get("passed", 0),
            "failed": migration.get("failed", 0),
            "execution_timestamp": migration.get("execution_timestamp"),
        }
    else:
        status["migration"] = {"overall_status": "REPORT_NOT_FOUND"}

    if GX_REPORT_FILE.exists():
        with GX_REPORT_FILE.open("r", encoding="utf-8") as file:
            quality = json.load(file)

        status["data_quality"] = {
            "overall_status": quality.get("overall_status", "UNKNOWN"),
            "statistics": quality.get("statistics", {}),
            "table": quality.get("table"),
            "execution_timestamp": quality.get("execution_timestamp"),
        }
    else:
        status["data_quality"] = {"overall_status": "REPORT_NOT_FOUND"}

    return status


if __name__ == "__main__":
    mcp.run(transport="stdio")
