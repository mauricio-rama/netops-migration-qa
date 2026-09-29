import json
from pathlib import Path

import streamlit as st
import pandas as pd


REPORT_FILE = Path("reports/migration_quality_report.json")
SCALE_REPORT_FILE = Path("reports/scale_validation_report.json")


st.set_page_config(
    page_title="NetOps Migration Quality",
    page_icon="🧪",
    layout="wide"
)


st.title("🧪 NetOps Migration Quality Dashboard")
st.caption("Automated Data Migration & Transformation Validation")


if not REPORT_FILE.exists():
    st.error("Migration quality report not found.")
    st.stop()


with open(REPORT_FILE, "r", encoding="utf-8") as file:
    report = json.load(file)

scale_report = None

if SCALE_REPORT_FILE.exists():
    with open(SCALE_REPORT_FILE, "r", encoding="utf-8") as file:
        scale_report = json.load(file)


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
    st.metric("Overall Status", overall_status)

with col5:
    st.metric("Quality Score", f"{quality_score:.0f}%")


st.divider()

st.subheader("Validation Summary")

chart_data = pd.DataFrame(
    {
        "Status": ["Passed", "Failed"],
        "Count": [passed, failed]
    }
)

st.bar_chart(
    chart_data.set_index("Status")
)

st.subheader("Validation Results")


validation_data = pd.DataFrame(report["validations"])

validation_data["status"] = validation_data["status"].replace({
    "PASSED": "✅ PASSED",
    "FAILED": "❌ FAILED"
})


st.dataframe(
    validation_data,
    use_container_width=True,
    hide_index=True
)


st.divider()

st.subheader("Execution Details")

st.write(
    f"**Execution timestamp:** {report['execution_timestamp']}"
)

st.divider()

st.subheader("🚀 1M Record Scale Validation")

if scale_report:
    source_records = scale_report["records"]["source"]
    target_records = scale_report["records"]["target"]

    transformation_errors = scale_report["validation_results"]["transformation_errors"]
    duplicate_ids = scale_report["validation_results"]["duplicate_customer_ids"]
    mandatory_errors = scale_report["validation_results"]["mandatory_field_errors"]
    orphan_records = scale_report["validation_results"]["orphan_records"]

    scale_status = scale_report["overall_status"]
    execution_time = scale_report["execution_time_seconds"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Source Records", f"{source_records:,}")

    with col2:
        st.metric("Target Records", f"{target_records:,}")

    with col3:
        st.metric("Validation Time", f"{execution_time:.2f}s")

    with col4:
        st.metric("Status", scale_status)

    st.write("### Scale Validation Results")

    scale_data = pd.DataFrame(
        {
            "Validation": [
                "Record Count Reconciliation",
                "Transformation Rules",
                "Duplicate Detection",
                "Mandatory Fields",
                "Referential Integrity"
            ],
            "Result": [
                "PASS" if source_records == target_records else "FAIL",
                "PASS" if transformation_errors == 0 else "FAIL",
                "PASS" if duplicate_ids == 0 else "FAIL",
                "PASS" if mandatory_errors == 0 else "FAIL",
                "PASS" if orphan_records == 0 else "FAIL"
            ]
        }
    )

    st.dataframe(
        scale_data,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("1M scale validation report not available yet.")
