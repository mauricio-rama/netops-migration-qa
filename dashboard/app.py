import json
from pathlib import Path

import streamlit as st
import pandas as pd


REPORT_FILE = Path("reports/migration_quality_report.json")


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
