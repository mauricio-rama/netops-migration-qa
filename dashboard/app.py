
import json
from pathlib import Path

import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

REPORT_FILE = Path("reports/migration_quality_report.json")
SCALE_REPORT_FILE = Path("reports/scale_validation_report.json")
INCREMENTAL_REPORT_FILE = Path("reports/incremental_validation_report.json")
GX_REPORT_FILE = Path("reports/great_expectations_report.json")
GX_HTML_FILE = Path("reports/great_expectations/index.html")


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

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


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


# ============================================================
# LOAD REPORTS
# ============================================================

report = load_json(REPORT_FILE)

if report is None:
    st.error(f"Migration quality report not found: {REPORT_FILE}")
    st.stop()

scale_report = load_json(SCALE_REPORT_FILE)
incremental_report = load_json(INCREMENTAL_REPORT_FILE)
gx_report = load_json(GX_REPORT_FILE)


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title("🧪 NetOps Migration Quality Dashboard")
st.caption("Automated Data Migration & Transformation Validation")

st.divider()


# ============================================================
# 1. GENERAL MIGRATION QUALITY
# ============================================================

st.header("📊 General Migration Quality")

total = report["total_validations"]
passed = report["passed"]
failed = report["failed"]
overall_status = report["overall_status"]

quality_score = (passed / total * 100) if total > 0 else 0

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
    st.metric("Quality Score", f"{quality_score:.0f}%")

st.subheader("Validation Summary")

chart_data = pd.DataFrame(
    {
        "Status": ["Passed", "Failed"],
        "Count": [passed, failed],
    }
)

st.bar_chart(chart_data.set_index("Status"))

st.subheader("Validation Results")

validation_data = pd.DataFrame(report.get("validations", []))

if not validation_data.empty:
    if "status" in validation_data.columns:
        validation_data["status"] = validation_data["status"].map(
            display_status
        )

    st.dataframe(
        validation_data,
        use_container_width=True,
        hide_index=True,
    )
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

    st.dataframe(
        scale_data,
        use_container_width=True,
        hide_index=True,
    )
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

    # Use the actual report fields; do not assume expected_delta exists.
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
# 4. GREAT EXPECTATIONS — DATA QUALITY
# ============================================================

st.divider()
st.header("🛡️ Great Expectations — Data Quality")

if gx_report:
    gx_stats = gx_report.get("statistics", {})
    gx_expectations = pd.DataFrame(gx_report.get("expectations", []))

    gx_status = gx_report.get("overall_status", "UNKNOWN")
    gx_total = gx_stats.get("evaluated_expectations", 0)
    gx_passed = gx_stats.get("successful_expectations", 0)
    gx_failed = gx_stats.get("unsuccessful_expectations", 0)
    gx_score = gx_stats.get("success_percent", 0)

    st.caption(f"Table validated: `{gx_report.get('table', 'N/A')}`")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("GX Status", display_status(gx_status))

    with col2:
        st.metric("Expectations Evaluated", gx_total)

    with col3:
        st.metric("Expectations Passed", gx_passed)

    with col4:
        st.metric("Quality Score", f"{gx_score:.0f}%")

    st.subheader("Expectation Results")

    if not gx_expectations.empty:
        gx_expectations["Status"] = gx_expectations["success"].map(
            {True: "✅ PASS", False: "❌ FAIL"}
        )

        gx_expectations = gx_expectations.rename(
            columns={
                "expectation_type": "Expectation",
                "column": "Column",
                "element_count": "Records Evaluated",
                "unexpected_count": "Unexpected Values",
            }
        )

        display_columns = [
            column
            for column in [
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
        st.warning(
            "Great Expectations HTML report not found. "
            "Run `python src/validate_with_gx.py` to generate it."
        )
else:
    st.info(
        "Great Expectations report is not available yet. "
        "Run `python src/validate_with_gx.py` first."
    )

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
# FOOTER
# ============================================================

st.divider()
st.caption(
    "NetOps Migration QA | Data Reconciliation · Data Quality · "
    "Incremental Validation · Scale Testing · Great Expectations"
)
