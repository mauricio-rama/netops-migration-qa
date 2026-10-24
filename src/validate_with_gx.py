
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


def build_expectation_results(result, table_name):
    """Convert Great Expectations results into dashboard-friendly data."""
    expectation_results = []

    for item in result.results:
        details = item.result or {}
        kwargs = item.expectation_config.kwargs

        expectation_results.append(
            {
                "table": table_name,
                "expectation_type": item.expectation_config.type,
                "column": kwargs.get("column"),
                "column_A": kwargs.get("column_A"),
                "column_B": kwargs.get("column_B"),
                "success": item.success,
                "element_count": details.get("element_count"),
                "unexpected_count": details.get("unexpected_count"),
            }
        )

    return expectation_results


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

    # --------------------------------------------------------
    # 1. Validate the 1-million-record destination table
    # --------------------------------------------------------
    target_asset = datasource.add_table_asset(
        name="target_customers_1m",
        table_name="customers_1m",
        schema_name="target_system",
    )

    target_batch = target_asset.add_batch_definition_whole_table(
        name="target_customers_1m_batch",
    )

    target_suite = gx.ExpectationSuite(
        name="target_customer_quality_suite",
    )

    target_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="customer_id",
        )
    )

    target_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeUnique(
            column="customer_id",
        )
    )

    target_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="full_name",
        )
    )

    target_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="customer_status",
        )
    )

    target_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="created_at",
        )
    )

    target_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="migration_timestamp",
        )
    )

    target_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="customer_status",
            value_set=["ACTIVE", "INACTIVE"],
        )
    )

    target_suite.add_expectation(
        gx.expectations.ExpectColumnPairValuesAToBeGreaterThanB(
            column_A="migration_timestamp",
            column_B="created_at",
            or_equal=True,
        )
    )

    context.suites.add(target_suite)

    target_validation = gx.ValidationDefinition(
        name="target_customer_quality_validation",
        data=target_batch,
        suite=target_suite,
    )

    context.validation_definitions.add(target_validation)
    target_result = target_validation.run()

    # --------------------------------------------------------
    # 2. Validate customer_id uniqueness in the staging table
    # --------------------------------------------------------
    staging_asset = datasource.add_table_asset(
        name="customers_staging",
        table_name="customers_staging",
        schema_name="source_system",
    )

    staging_batch = staging_asset.add_batch_definition_whole_table(
        name="customers_staging_batch",
    )

    staging_suite = gx.ExpectationSuite(
        name="customers_staging_quality_suite",
    )

    staging_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeUnique(
            column="customer_id",
        )
    )

    context.suites.add(staging_suite)

    staging_validation = gx.ValidationDefinition(
        name="customers_staging_quality_validation",
        data=staging_batch,
        suite=staging_suite,
    )

    context.validation_definitions.add(staging_validation)
    staging_result = staging_validation.run()

    # --------------------------------------------------------
    # 3. Consolidate both table results
    # --------------------------------------------------------
    all_expectations = (
        build_expectation_results(
            target_result,
            "target_system.customers_1m",
        )
        + build_expectation_results(
            staging_result,
            "source_system.customers_staging",
        )
    )

    overall_success = target_result.success and staging_result.success

    docs = context.build_data_docs(site_names=["local_site"])
    html_report = docs["local_site"]

    report = {
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "table": "Multiple tables",
        "overall_status": "PASS" if overall_success else "FAIL",
        "success": overall_success,
        "statistics": {
            "evaluated_expectations": len(all_expectations),
            "successful_expectations": sum(
                item["success"] for item in all_expectations
            ),
            "unsuccessful_expectations": sum(
                not item["success"] for item in all_expectations
            ),
            "success_percent": (
                sum(item["success"] for item in all_expectations)
                / len(all_expectations)
                * 100
                if all_expectations
                else 0
            ),
        },
        "table_results": {
            "target_system.customers_1m": {
                "success": target_result.success,
                "statistics": target_result.statistics,
            },
            "source_system.customers_staging": {
                "success": staging_result.success,
                "statistics": staging_result.statistics,
            },
        },
        "expectations": all_expectations,
        "html_report": html_report,
    }

    JSON_REPORT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== GREAT EXPECTATIONS: CONSOLIDATED DATA QUALITY ===")
    print(f"Overall status: {report['overall_status']}")

    for table_name, table_result in report["table_results"].items():
        print(
            f"\nTable: {table_name} | "
            f"Status: {'PASS' if table_result['success'] else 'FAIL'}"
        )

    for item in all_expectations:
        status = "PASS" if item["success"] else "FAIL"
        column = item["column"]

        if item["column_A"] and item["column_B"]:
            column = f"{item['column_A']} >= {item['column_B']}"

        print(
            f"[{status}] {item['expectation_type']} "
            f"| Table: {item['table']} "
            f"| Column: {column} "
            f"| Evaluated: {item['element_count']} "
            f"| Unexpected: {item['unexpected_count']}"
        )

    print(f"\nHTML report: {html_report}")
    print(f"JSON report: {JSON_REPORT_FILE}")

    if not overall_success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
