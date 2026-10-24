
import great_expectations as gx

DATABASE_URL = (
    "postgresql+psycopg://netops_admin:netops_password"
    "@localhost:5432/netops_qa"
)


def main():
    context = gx.get_context(mode="ephemeral")

    datasource = context.data_sources.add_postgres(
        name="netops_postgres",
        connection_string=DATABASE_URL,
    )

    asset = datasource.add_table_asset(
        name="customers_staging",
        table_name="customers_staging",
        schema_name="source_system",
    )

    batch_definition = asset.add_batch_definition_whole_table(
        name="customers_staging_batch",
    )

    suite = gx.ExpectationSuite(
        name="customers_staging_demo_suite",
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeUnique(
            column="customer_id",
        )
    )

    # Register the expectation suite before creating the validation.
    context.suites.add(suite)

    validation = gx.ValidationDefinition(
        name="customers_staging_demo_validation",
        data=batch_definition,
        suite=suite,
    )

    # Register the validation before running it.
    context.validation_definitions.add(validation)

    result = validation.run()

    print("\n=== DEMO: GREAT EXPECTATIONS ===")
    print("Table: source_system.customers_staging")
    print(f"Overall status: {'PASS' if result.success else 'FAIL'}")

    for item in result.results:
        details = item.result or {}
        print(
            f"[{'PASS' if item.success else 'FAIL'}] "
            f"{item.expectation_config.type} "
            f"| Unexpected: {details.get('unexpected_count', 0)}"
        )

    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
