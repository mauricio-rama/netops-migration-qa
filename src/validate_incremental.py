import json
from datetime import datetime
from pathlib import Path

import psycopg


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "netops_qa",
    "user": "netops_admin",
    "password": "netops_password",
}

OUTPUT_FILE = Path("reports/incremental_validation_report.json")


def get_connection():
    return psycopg.connect(**DB_CONFIG)


def setup_incremental_scenario(conn):
    """Reinicia los datos de demostración solo cuando se solicita explícitamente."""
    with conn.cursor() as cur:
        cur.execute("""
            DROP TABLE IF EXISTS target_system.customers_incremental;
            DROP TABLE IF EXISTS source_system.customers_incremental;
            DROP TABLE IF EXISTS migration_control;

            CREATE TABLE migration_control (
                pipeline_name VARCHAR(100) PRIMARY KEY,
                last_processed_timestamp TIMESTAMP NOT NULL
            );

            CREATE TABLE source_system.customers_incremental (
                customer_id BIGINT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255),
                status VARCHAR(20) NOT NULL,
                updated_at TIMESTAMP NOT NULL
            );

            CREATE TABLE target_system.customers_incremental (
                customer_id BIGINT PRIMARY KEY,
                full_name VARCHAR(201) NOT NULL,
                email VARCHAR(255),
                customer_status VARCHAR(20) NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                migration_timestamp TIMESTAMP NOT NULL
            );
        """)

        cur.execute("""
            INSERT INTO migration_control
                (pipeline_name, last_processed_timestamp)
            VALUES
                ('customer_incremental', '2026-01-01 12:00:00');
        """)

        cur.execute("""
            INSERT INTO source_system.customers_incremental
                (customer_id, first_name, last_name, email, status, updated_at)
            VALUES
                (100001, 'Juan', 'Perez', 'juan.perez@example.com', 'ACTIVE', '2026-01-01 08:00:00'),
                (100002, 'Laura', 'Garcia', 'laura.garcia@example.com', 'ACTIVE', '2026-01-01 09:00:00'),
                (100003, 'Carlos', 'Lopez', 'carlos.lopez@example.com', 'ACTIVE', '2026-01-01 10:00:00'),
                (100004, 'Ana', 'Martinez', 'ana.martinez@example.com', 'ACTIVE', '2026-01-01 11:00:00'),
                (100005, 'Luis', 'Hernandez', 'luis.hernandez@example.com', 'ACTIVE', '2026-01-01 12:00:00'),
                (100006, 'Maria', 'Sanchez', 'maria.sanchez@example.com', 'ACTIVE', '2026-01-02 08:00:00'),
                (100007, 'Pedro', 'Ramirez', 'pedro.ramirez@example.com', 'ACTIVE', '2026-01-02 09:00:00'),
                (100008, 'Sofia', 'Torres', 'sofia.torres@example.com', 'ACTIVE', '2026-01-03 10:00:00');
        """)

        cur.execute("""
            INSERT INTO target_system.customers_incremental
                (customer_id, full_name, email, customer_status,
                 updated_at, migration_timestamp)
            SELECT
                customer_id,
                first_name || ' ' || last_name,
                email,
                status,
                updated_at,
                CURRENT_TIMESTAMP
            FROM source_system.customers_incremental
            WHERE updated_at <= '2026-01-01 12:00:00';
        """)

    conn.commit()


def run_incremental_load(conn):
    """Carga registros nuevos o actualizados posteriores al watermark."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("""
                SELECT last_processed_timestamp
                FROM migration_control
                WHERE pipeline_name = 'customer_incremental'
                FOR UPDATE;
            """)

            row = cur.fetchone()

            if row is None:
                raise RuntimeError(
                    "No existe el watermark de customer_incremental"
                )

            last_watermark = row[0]

            cur.execute("""
                SELECT MAX(updated_at)
                FROM source_system.customers_incremental
                WHERE updated_at > %s;
            """, (last_watermark,))

            new_watermark = cur.fetchone()[0]

            if new_watermark is None:
                return 0

            cur.execute("""
                INSERT INTO target_system.customers_incremental (
                    customer_id,
                    full_name,
                    email,
                    customer_status,
                    updated_at,
                    migration_timestamp
                )
                SELECT
                    s.customer_id,
                    s.first_name || ' ' || s.last_name,
                    s.email,
                    s.status,
                    s.updated_at,
                    CURRENT_TIMESTAMP
                FROM source_system.customers_incremental s
                WHERE s.updated_at > %s
                  AND s.updated_at <= %s
                ON CONFLICT (customer_id) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    email = EXCLUDED.email,
                    customer_status = EXCLUDED.customer_status,
                    updated_at = EXCLUDED.updated_at,
                    migration_timestamp = CURRENT_TIMESTAMP
                WHERE target_system.customers_incremental.updated_at
                      IS DISTINCT FROM EXCLUDED.updated_at
                   OR target_system.customers_incremental.full_name
                      IS DISTINCT FROM EXCLUDED.full_name
                   OR target_system.customers_incremental.email
                      IS DISTINCT FROM EXCLUDED.email
                   OR target_system.customers_incremental.customer_status
                      IS DISTINCT FROM EXCLUDED.customer_status;
            """, (last_watermark, new_watermark))

            affected_records = cur.rowcount

            cur.execute("""
                UPDATE migration_control
                SET last_processed_timestamp = %s
                WHERE pipeline_name = 'customer_incremental';
            """, (new_watermark,))

    return affected_records


def validate_delta_count(conn, inserted_records):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM source_system.customers_incremental s
            JOIN target_system.customers_incremental t
                ON s.customer_id = t.customer_id
            WHERE s.updated_at <= (
                SELECT last_processed_timestamp
                FROM migration_control
                WHERE pipeline_name = 'customer_incremental'
            );
        """)

        processed_records = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM source_system.customers_incremental;
        """)
        source_records = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM target_system.customers_incremental;
        """)
        target_records = cur.fetchone()[0]

    return {
        "source_records": source_records,
        "target_records": target_records,
        "processed_records": processed_records,
        "inserted_records": inserted_records,
        "passed": source_records == target_records
    }


def validate_transformations(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) FILTER (
                    WHERE s.first_name || ' ' || s.last_name
                          IS DISTINCT FROM t.full_name
                ) AS name_errors,
                COUNT(*) FILTER (
                    WHERE s.email IS DISTINCT FROM t.email
                ) AS email_errors,
                COUNT(*) FILTER (
                    WHERE s.status IS DISTINCT FROM t.customer_status
                ) AS status_errors,
                COUNT(*) FILTER (
                    WHERE s.updated_at IS DISTINCT FROM t.updated_at
                ) AS timestamp_errors,
                COUNT(*) AS matched_records
            FROM source_system.customers_incremental s
            JOIN target_system.customers_incremental t
                ON s.customer_id = t.customer_id;
        """)

        row = cur.fetchone()
        (
            name_errors,
            email_errors,
            status_errors,
            timestamp_errors,
            matched_records
        ) = row

    total_errors = (
        name_errors
        + email_errors
        + status_errors
        + timestamp_errors
    )

    return {
        "matched_records": matched_records,
        "name_errors": name_errors,
        "email_errors": email_errors,
        "status_errors": status_errors,
        "timestamp_errors": timestamp_errors,
        "transformation_errors": total_errors,
        "passed": matched_records > 0 and total_errors == 0
    }


def validate_duplicates(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT customer_id
                FROM target_system.customers_incremental
                GROUP BY customer_id
                HAVING COUNT(*) > 1
            ) duplicates;
        """)

        duplicate_ids = cur.fetchone()[0]

    return {
        "duplicate_customer_ids": duplicate_ids,
        "passed": duplicate_ids == 0
    }


def validate_record_counts(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                (SELECT COUNT(*)
                 FROM source_system.customers_incremental),
                (SELECT COUNT(*)
                 FROM target_system.customers_incremental);
        """)

        source_count, target_count = cur.fetchone()

    return {
        "source_count": source_count,
        "target_count": target_count,
        "passed": source_count == target_count
    }


def validate_referential_integrity(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM target_system.customers_incremental t
            LEFT JOIN source_system.customers_incremental s
                ON t.customer_id = s.customer_id
            WHERE s.customer_id IS NULL;
        """)

        orphan_records = cur.fetchone()[0]

    return {
        "orphan_records": orphan_records,
        "passed": orphan_records == 0
    }


def main():
    # No reinicia las tablas: ejecuta la carga sobre los datos existentes.
    with get_connection() as conn:
        inserted_records = run_incremental_load(conn)

        delta_validation = validate_delta_count(conn, inserted_records)
        transformation_validation = validate_transformations(conn)
        duplicate_validation = validate_duplicates(conn)
        count_validation = validate_record_counts(conn)
        referential_validation = validate_referential_integrity(conn)

    validations = {
        "delta_reconciliation": delta_validation,
        "transformation_rules": transformation_validation,
        "duplicate_detection": duplicate_validation,
        "record_count_reconciliation": count_validation,
        "referential_integrity": referential_validation
    }

    overall_status = (
        "PASS"
        if all(validation["passed"] for validation in validations.values())
        else "FAIL"
    )

    report = {
        "generated_at": datetime.now().isoformat(),
        "dataset": "customers_incremental",
        "inserted_records": inserted_records,
        "validations": validations,
        "overall_status": overall_status
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()
