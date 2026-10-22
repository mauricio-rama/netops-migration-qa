
import json
from datetime import datetime, timezone
from pathlib import Path

import great_expectations as gx


DATABASE_URL = (
    "postgresql+psycopg://netops_admin:netops_password"
    "@localhost:5432/netops_qa"
)

REPORTS_DIR = Path("reports/great_expectations").resolve()
JSON_REPORT_FILE = Path("reports/great_expectations_report.json")

TABLE_NAME = "target_system.customers_1m"


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    JSON_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    context = gx.get_context(mode="ephemeral")

    context.update_data_docs_site(
        site_name="local_site",
        site_config={
            "class_name": "SiteBuilder",
            "show_how_to_buttons": True,
            "store_backend": {
                "class_name": "TupleFilesystemStoreBackend",
                "base_directory": str(REPORTS_DIR),
            },
            "site_index_builder": {
                "class_name": "DefaultSiteIndexBuilder",
            },
        },
    )

    datasource = context.data_sources.add_postgres(
        name="netops_postgres",
        connection_string=DATABASE_URL,
    )

    asset = datasource.add_table_asset(
        name="target_customers_1m",
        table_name="customers_1m",
        schema_name="target_system",
    )

    batch_definition = asset.add_batch_definition_whole_table(
        name="target_customers_1m_batch",
    )

    suite = gx.ExpectationSuite(
        name="target_customer_quality_suite",
    )

    # 1. Customer ID must not be null.
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="customer_id",
        )
    )

    # 2. Customer ID must be unique.
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeUnique(
            column="customer_id",
        )
    )

    # 3. Full name must not be null.
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="full_name",
        )
    )

    # 4. Customer status must not be null.
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="customer_status",
        )
    )

    # 5. Creation timestamp must not be null.
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="created_at",
        )
    )

    # 6. Migration timestamp must not be null.
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="migration_timestamp",
        )
    )

    # 7. Customer status must belong to the approved set.
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="customer_status",
            value_set=["ACTIVE", "INACTIVE"],
        )
    )

    # 8. Migration timestamp must be >= creation timestamp.
    suite.add_expectation(
        gx.expectations.ExpectColumnPairValuesAToBeGreaterThanB(
            column_A="migration_timestamp",
            column_B="created_at",
            or_equal=True,
        )
    )

    context.suites.add(suite)

    validation = gx.ValidationDefinition(
        name="target_customer_quality_validation",
        data=batch_definition,
        suite=suite,
    )

    context.validation_definitions.add(validation)

    result = validation.run()

    docs = context.build_data_docs(site_names=["local_site"])
    html_report = docs["local_site"]

    expectation_results = []

    for item in result.results:
        details = item.result or {}
        kwargs = item.expectation_config.kwargs

        expectation_results.append(
            {
                "expectation_type": item.expectation_config.type,
                "column": kwargs.get("column"),
                "column_A": kwargs.get("column_A"),
                "column_B": kwargs.get("column_B"),
                "success": item.success,
                "element_count": details.get("element_count"),
                "unexpected_count": details.get("unexpected_count"),
            }
        )

    report = {
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "table": TABLE_NAME,
        "overall_status": "PASS" if result.success else "FAIL",
        "success": result.success,
        "statistics": result.statistics,
        "expectations": expectation_results,
        "html_report": html_report,
    }

    JSON_REPORT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== GREAT EXPECTATIONS: DATA QUALITY ===")
    print(f"Table: {TABLE_NAME}")
    print(f"Overall status: {report['overall_status']}")
    print(f"Statistics: {result.statistics}")

    for expectation in expectation_results:
        status = "PASS" if expectation["success"] else "FAIL"

        column_description = expectation["column"]

        if expectation["column_A"] and expectation["column_B"]:
            column_description = (
                f"{expectation['column_A']} >= "
                f"{expectation['column_B']}"
            )

        print(
            f"[{status}] {expectation['expectation_type']} "
            f"| Column: {column_description} "
            f"| Evaluated: {expectation['element_count']} "
            f"| Unexpected: {expectation['unexpected_count']}"
        )

    print(f"\nHTML report: {html_report}")
    print(f"JSON report: {JSON_REPORT_FILE}")

    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
