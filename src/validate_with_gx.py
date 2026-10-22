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
        name="target_customers_1m",
        table_name="customers_1m",
        schema_name="target_system",
    )

    batch_definition = asset.add_batch_definition_whole_table(
        name="target_customers_1m_batch"
    )

    suite = gx.ExpectationSuite(
        name="target_customer_quality_suite"
    )

    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="customer_id"
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

    print("\n=== GREAT EXPECTATIONS: DESTINO ===")
    print("Tabla: target_system.customers_1m")
    print(f"Resultado: {'PASS' if result.success else 'FAIL'}")
    print(f"Estadísticas: {result.statistics}")

    if result.results:
        details = result.results[0].result
        print(f"Registros evaluados: {details.get('element_count')}")
        print(f"Valores inesperados: {details.get('unexpected_count')}")

    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
