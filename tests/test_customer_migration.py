import psycopg


def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname="netops_qa",
        user="netops_admin",
        password="netops_password",
    )


def test_customer_full_name_transformation():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    s.customer_id,
                    s.first_name || ' ' || s.last_name AS expected_full_name,
                    t.full_name AS actual_full_name
                FROM source_system.customers s
                JOIN target_system.customers t
                    ON s.customer_id = t.customer_id
                WHERE s.first_name || ' ' || s.last_name
                      <> t.full_name;
            """)

            transformation_errors = cursor.fetchall()

    assert transformation_errors == [], (
        f"Transformation errors detected: {transformation_errors}"
    )


def test_customer_record_count_reconciliation():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*)
                     FROM source_system.customers) AS source_count,

                    (SELECT COUNT(*)
                     FROM target_system.customers) AS target_count;
            """)

            source_count, target_count = cursor.fetchone()

    assert source_count == target_count, (
        f"Record count mismatch: source={source_count}, "
        f"target={target_count}"
    )


def test_customer_missing_records():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.customer_id
                FROM source_system.customers s
                LEFT JOIN target_system.customers t
                    ON s.customer_id = t.customer_id
                WHERE t.customer_id IS NULL;
            """)

            missing_records = cursor.fetchall()

    assert missing_records == [], (
        f"Missing records detected in target: {missing_records}"
    )


def test_customer_duplicate_records():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    customer_id,
                    COUNT(*) AS duplicate_count
                FROM source_system.customers_staging
                GROUP BY customer_id
                HAVING COUNT(*) > 1;
            """)

            duplicate_records = cursor.fetchall()

    assert duplicate_records == [], (
        f"Duplicate records detected: {duplicate_records}"
    )


def test_customer_mandatory_fields():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    customer_id,
                    first_name,
                    last_name,
                    status,
                    created_at
                FROM source_system.customers_staging
                WHERE customer_id IS NOT NULL
                  AND (
                      first_name IS NULL
                      OR last_name IS NULL
                      OR status IS NULL
                      OR created_at IS NULL
                  );
            """)

            invalid_records = cursor.fetchall()

    assert invalid_records == [], (
        f"Mandatory field NULL detected: {invalid_records}"
    )


def test_customer_referential_integrity():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    o.order_id,
                    o.customer_id
                FROM source_system.customer_orders o
                LEFT JOIN source_system.customers c
                    ON o.customer_id = c.customer_id
                WHERE c.customer_id IS NULL;
            """)

            orphan_records = cursor.fetchall()

    assert orphan_records == [], (
        f"Referential integrity violations detected: {orphan_records}"
    )