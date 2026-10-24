
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

REPORT_FILE = PROJECT_ROOT / "reports/migration_quality_report.json"
SCALE_REPORT_FILE = PROJECT_ROOT / "reports/scale_validation_report.json"
INCREMENTAL_REPORT_FILE = (
    PROJECT_ROOT / "reports/incremental_validation_report.json"
)
GX_REPORT_FILE = PROJECT_ROOT / "reports/great_expectations_report.json"
GX_HTML_FILE = PROJECT_ROOT / "reports/great_expectations/index.html"

COPYRIGHT_YEAR = 2026
PROJECT_NAME = "NetOps Migration QA"
AUTHOR_NAME = "Mauricio Ramírez"


st.set_page_config(
    page_title="NetOps Migration Quality",
    page_icon="🧪",
    layout="wide",
)


# ============================================================
# HELPERS
# ============================================================

def load_json(path):
    """Load a JSON report if it exists."""
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as exc:
        st.warning(f"Could not read report {path.name}: {exc}")
        return None


def display_status(value):
    """Display a consistent status label."""
    if isinstance(value, bool):
        return "✅ PASS" if value else "❌ FAIL"

    status = str(value).upper()

    if status in {"PASS", "PASSED", "SUCCESS", "SUCCESSFUL"}:
        return "✅ PASS"

    if status in {"FAIL", "FAILED", "ERROR"}:
        return "❌ FAIL"

    return status


def run_validation():
    """Run the consolidated validation pipeline."""
    try:
        return subprocess.run(
            [sys.executable, "src/run_validation.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, "Validation timed out after 600 seconds."
    except OSError as exc:
        return None, f"{type(exc).__name__}: {exc}"


def format_validation_details(details):
    """Normalize validation details for display."""
    if isinstance(details, (dict, list)):
        return json.dumps(details, indent=2, ensure_ascii=False)

    return str(details) if details else ""


# ============================================================
# LOAD REPORTS
# ============================================================

report = load_json(REPORT_FILE)
scale_report = load_json(SCALE_REPORT_FILE)
incremental_report = load_json(INCREMENTAL_REPORT_FILE)
gx_report = load_json(GX_REPORT_FILE)


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("🧪 NetOps Migration Quality Dashboard")
st.caption(
    "Automated Data Migration, Reconciliation & Transformation Validation"
)

st.write(
    "Run the consolidated quality gate to execute Pytest and Great "
    "Expectations, then refresh the dashboard with the latest reports."
)

if st.button("🔄 Run Validations & Refresh Dashboard", type="primary"):
    with st.spinner("Running Pytest and Great Expectations..."):
        result = run_validation()

    if isinstance(result, tuple):
        st.error(result[1])
    else:
        if result.returncode == 0:
            st.success("All validations passed.")
        else:
            st.error(
                "The quality gate failed. The latest validation report "
                "will still be loaded so you can inspect the failures."
            )

        if result.stdout:
            with st.expander("View validation execution output"):
                st.code(result.stdout, language="text")

        if result.stderr:
            with st.expander("View validation warnings and errors"):
                st.code(result.stderr, language="text")

    st.rerun()

st.divider()


# ============================================================
# 1. GENERAL MIGRATION QUALITY
# ============================================================

st.header("📊 General Migration Quality")

if report is None:
    st.error(f"Migration quality report not found: {REPORT_FILE}")
    st.info("Run the validation pipeline using the button above.")
else:
    total = report.get("total_validations", 0)
    passed = report.get("passed", 0)
    failed = report.get("failed", 0)
    overall_status = report.get("overall_status", "UNKNOWN")
    quality_score = report.get(
        "quality_score",
        (passed / total * 100) if total else 0,
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Validations", total)

    with col2:
        st.metric("Passed", passed)

    with col3:
        st.metric("Failed", failed)

    with col4:
        st.metric("Overall Status", display_status(overall_status))

    with col5:
        st.metric("Quality Score", f"{quality_score:.2f}%")

    # --------------------------------------------------------
    # Validator summaries
    # --------------------------------------------------------
    st.subheader("Validator Summary")

    summaries = report.get("validator_summaries", {})
    summary_columns = st.columns(max(len(summaries), 1))

    for column, (validator_name, summary) in zip(
        summary_columns, summaries.items()
    ):
        with column:
            st.metric(
                f"{validator_name} Status",
                display_status(summary.get("status", "UNKNOWN")),
            )
            st.caption(
                f"{summary.get('passed', 0)} passed · "
                f"{summary.get('failed', 0)} failed · "
                f"{summary.get('total', 0)} total"
            )

    # --------------------------------------------------------
    # Validation chart
    # --------------------------------------------------------
    st.subheader("Validation Summary")

    chart_data = pd.DataFrame(
        {
            "Status": ["Passed", "Failed"],
            "Count": [passed, failed],
        }
    )

    st.bar_chart(chart_data.set_index("Status"))

    # --------------------------------------------------------
    # Consolidated validation results
    # --------------------------------------------------------
    st.subheader("Validation Results")

    validation_data = pd.DataFrame(report.get("validations", []))

    if not validation_data.empty:
        if "status" in validation_data.columns:
            validation_data["status"] = validation_data["status"].map(
                display_status
            )

        preferred_columns = [
            "name",
            "validator",
            "table",
            "column",
            "records_evaluated",
            "unexpected_values",
            "status",
        ]

        visible_columns = [
            column
            for column in preferred_columns
            if column in validation_data.columns
        ]

        st.dataframe(
            validation_data[visible_columns],
            use_container_width=True,
            hide_index=True,
        )

        failed_validations = [
            item
            for item in report.get("validations", [])
            if str(item.get("status", "")).upper() in {"FAIL", "FAILED", "ERROR"}
        ]

        if failed_validations:
            st.subheader("❌ Failure Details")

            for index, item in enumerate(failed_validations, start=1):
                title = (
                    f"{index}. {item.get('validator', 'Validator')} — "
                    f"{item.get('name', 'Unknown validation')}"
                )

                with st.expander(title, expanded=True):
                    if item.get("table"):
                        st.write(f"**Table:** `{item['table']}`")

                    if item.get("column"):
                        st.write(f"**Column:** `{item['column']}`")

                    if item.get("records_evaluated") is not None:
                        st.write(
                            f"**Records evaluated:** "
                            f"{item['records_evaluated']:,}"
                        )

                    if item.get("unexpected_values") is not None:
                        st.write(
                            f"**Unexpected values:** "
                            f"{item['unexpected_values']:,}"
                        )

                    details = format_validation_details(item.get("details"))

                    if details:
                        st.code(details, language="text")
                    else:
                        st.write("No additional failure details were recorded.")
    else:
        st.info("No general validation results are available.")

    st.caption(
        f"Execution timestamp: {report.get('execution_timestamp', 'N/A')}"
    )


# ============================================================
# 2. SCALE VALIDATION
# ============================================================

st.divider()
st.header("🚀 Scale Validation — 1 Million Records")

if scale_report:
    records = scale_report.get("records", {})
    results = scale_report.get("validation_results", {})

    source_records = records.get("source", 0)
    target_records = records.get("target", 0)
    execution_time = scale_report.get("execution_time_seconds", 0)
    scale_status = scale_report.get("overall_status", "UNKNOWN")

    transformation_errors = results.get("transformation_errors", 0)
    duplicate_ids = results.get("duplicate_customer_ids", 0)
    mandatory_errors = results.get("mandatory_field_errors", 0)
    orphan_records = results.get("orphan_records", 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Source Records", f"{source_records:,}")

    with col2:
        st.metric("Target Records", f"{target_records:,}")

    with col3:
        st.metric("Validation Time", f"{execution_time:.2f}s")

    with col4:
        st.metric("Status", display_status(scale_status))

    scale_data = pd.DataFrame(
        {
            "Validation": [
                "Record Count Reconciliation",
                "Transformation Rules",
                "Duplicate Detection",
                "Mandatory Fields",
                "Referential Integrity",
            ],
            "Result": [
                "PASS" if source_records == target_records else "FAIL",
                "PASS" if transformation_errors == 0 else "FAIL",
                "PASS" if duplicate_ids == 0 else "FAIL",
                "PASS" if mandatory_errors == 0 else "FAIL",
                "PASS" if orphan_records == 0 else "FAIL",
            ],
        }
    )

    st.subheader("Scale Validation Results")
    st.dataframe(scale_data, use_container_width=True, hide_index=True)
else:
    st.info("The 1-million-record scale validation report is not available.")


# ============================================================
# 3. INCREMENTAL MIGRATION VALIDATION
# ============================================================

st.divider()
st.header("🔄 Incremental Migration Validation")

if incremental_report:
    validations = incremental_report.get("validations", {})

    delta_validation = validations.get("delta_reconciliation", {})
    transformation_validation = validations.get("transformation_rules", {})
    duplicate_validation = validations.get("duplicate_detection", {})
    count_validation = validations.get("record_count_reconciliation", {})
    referential_validation = validations.get("referential_integrity", {})

    source_records = delta_validation.get("source_records", 0)
    target_records = delta_validation.get("target_records", 0)
    processed_records = delta_validation.get("processed_records", 0)
    inserted_records = incremental_report.get(
        "inserted_records",
        delta_validation.get("inserted_records", 0),
    )

    incremental_status = incremental_report.get("overall_status", "UNKNOWN")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Processed Records", f"{processed_records:,}")

    with col2:
        st.metric("Inserted Records", f"{inserted_records:,}")

    with col3:
        st.metric(
            "Source / Target",
            f"{source_records:,} / {target_records:,}",
        )

    with col4:
        st.metric("Status", display_status(incremental_status))

    st.subheader("Incremental Validation Results")

    incremental_data = pd.DataFrame(
        {
            "Validation": [
                "Delta Reconciliation",
                "Transformation Rules",
                "Duplicate Detection",
                "Record Count Reconciliation",
                "Referential Integrity",
            ],
            "Result": [
                display_status(delta_validation.get("passed", False)),
                display_status(transformation_validation.get("passed", False)),
                display_status(duplicate_validation.get("passed", False)),
                display_status(count_validation.get("passed", False)),
                display_status(referential_validation.get("passed", False)),
            ],
        }
    )

    st.dataframe(
        incremental_data,
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("View incremental report details"):
        st.json(incremental_report)
else:
    st.info("The incremental migration report is not available.")


# ============================================================
# 4. GREAT EXPECTATIONS
# ============================================================

st.divider()
st.header("🛡️ Great Expectations")

if gx_report:
    gx_stats = gx_report.get("statistics", {})
    gx_expectations = pd.DataFrame(gx_report.get("expectations", []))

    gx_status = gx_report.get("overall_status", "UNKNOWN")
    gx_total = gx_stats.get("evaluated_expectations", 0)
    gx_passed = gx_stats.get("successful_expectations", 0)
    gx_failed = gx_stats.get("unsuccessful_expectations", 0)
    gx_score = gx_stats.get("success_percent", 0)

    st.caption(f"Tables validated: `{gx_report.get('table', 'N/A')}`")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("GX Status", display_status(gx_status))

    with col2:
        st.metric("Expectations Evaluated", gx_total)

    with col3:
        st.metric("Expectations Passed", gx_passed)

    with col4:
        st.metric("Quality Score", f"{gx_score:.2f}%")

    table_results = gx_report.get("table_results", {})

    if table_results:
        st.subheader("Results by Table")

        table_summary = pd.DataFrame(
            [
                {
                    "Table": table_name,
                    "Status": display_status(table_result.get("success", False)),
                    "Evaluated": table_result.get("statistics", {}).get(
                        "evaluated_expectations", 0
                    ),
                    "Passed": table_result.get("statistics", {}).get(
                        "successful_expectations", 0
                    ),
                    "Failed": table_result.get("statistics", {}).get(
                        "unsuccessful_expectations", 0
                    ),
                }
                for table_name, table_result in table_results.items()
            ]
        )

        st.dataframe(
            table_summary,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Expectation Results")

    if not gx_expectations.empty:
        gx_expectations["Status"] = gx_expectations["success"].map(
            {True: "✅ PASS", False: "❌ FAIL"}
        )

        gx_expectations = gx_expectations.rename(
            columns={
                "table": "Table",
                "expectation_type": "Expectation",
                "column": "Column",
                "element_count": "Records Evaluated",
                "unexpected_count": "Unexpected Values",
            }
        )

        display_columns = [
            column
            for column in [
                "Table",
                "Expectation",
                "Column",
                "Records Evaluated",
                "Unexpected Values",
                "Status",
            ]
            if column in gx_expectations.columns
        ]

        st.dataframe(
            gx_expectations[display_columns],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No Great Expectations results were found in the JSON report.")

    st.caption(
        f"Last execution: {gx_report.get('execution_timestamp', 'N/A')}"
    )

    if GX_HTML_FILE.exists():
        with GX_HTML_FILE.open("rb") as file:
            html_data = file.read()

        st.download_button(
            label="📄 Download Great Expectations HTML Report",
            data=html_data,
            file_name="great_expectations_report.html",
            mime="text/html",
        )
    else:
        st.info("The Great Expectations HTML report is not available.")
else:
    st.info("The Great Expectations JSON report is not available.")


# ============================================================
# 5. AI-POWERED MIGRATION ANALYSIS
# ============================================================

st.divider()
st.header("🤖 AI-Powered Migration Analysis")

st.write(
    "Use Gemini AI and the MCP server to analyze the latest "
    "migration and data-quality reports."
)

if st.button("🔍 Analyze with AI", type="primary"):
    with st.spinner("Gemini is analyzing migration reports through MCP..."):
        try:
            from agents.gemini_agent import analyze_migration

            analysis = analyze_migration()

            st.session_state["migration_ai_analysis"] = analysis
            st.session_state["migration_ai_error"] = None

        except Exception as exc:
            st.session_state["migration_ai_error"] = (
                f"{type(exc).__name__}: {exc}"
            )

if st.session_state.get("migration_ai_error"):
    st.error(st.session_state["migration_ai_error"])

if st.session_state.get("migration_ai_analysis"):
    st.subheader("AI Analysis Results")
    st.markdown(st.session_state["migration_ai_analysis"])


# ============================================================
# FOOTER / COPYRIGHT
# ============================================================

st.divider()
st.caption(
    f"© {COPYRIGHT_YEAR} {PROJECT_NAME} | "
    f"Developed by {AUTHOR_NAME}. All rights reserved."
)
st.caption(
    "Data Reconciliation · Data Quality · Incremental Validation · "
    "Scale Testing · Great Expectations · AI-assisted Analysis"
)
