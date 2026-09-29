import json
import time
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

OUTPUT_FILE = Path("reports/scale_validation_report.json")


def run_validation():
    start_time = time.perf_counter()

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:

            # 1. Record count reconciliation
            cur.execute("""
                SELECT
                    (SELECT COUNT(*)
                     FROM source_system.customers_1m),
                    (SELECT COUNT(*)
                     FROM target_system.customers_1m)
            """)

            source_count, target_count = cur.fetchone()

            # 2. Transformation validation
            cur.execute("""
                SELECT COUNT(*)
                FROM source_system.customers_1m s
                JOIN target_system.customers_1m t
                    ON s.customer_id = t.customer_id
                WHERE s.first_name || ' ' || s.last_name <> t.full_name
            """)

            transformation_errors = cur.fetchone()[0]

            # 3. Duplicate validation
            cur.execute("""
                SELECT COUNT(*) - COUNT(DISTINCT customer_id)
                FROM target_system.customers_1m
            """)

            duplicate_ids = cur.fetchone()[0]

            # 4. Mandatory fields
            cur.execute("""
                SELECT COUNT(*)
                FROM target_system.customers_1m
                WHERE customer_id IS NULL
                   OR full_name IS NULL
                   OR customer_status IS NULL
                   OR created_at IS NULL
                   OR migration_timestamp IS NULL
            """)

            mandatory_errors = cur.fetchone()[0]

            # 5. Referential integrity
            cur.execute("""
                SELECT COUNT(*)
                FROM target_system.customers_1m t
                LEFT JOIN source_system.customers_1m s
                    ON t.customer_id = s.customer_id
                WHERE s.customer_id IS NULL
            """)

            orphan_records = cur.fetchone()[0]

    elapsed = time.perf_counter() - start_time

    checks = {
        "record_count_reconciliation": source_count == target_count,
        "transformation_rules": transformation_errors == 0,
        "duplicate_detection": duplicate_ids == 0,
        "mandatory_fields": mandatory_errors == 0,
        "referential_integrity": orphan_records == 0,
    }

    overall_status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "generated_at": datetime.now().isoformat(),
        "dataset": "customers_1m",
        "records": {
            "source": source_count,
            "target": target_count,
        },
        "validation_results": {
            "transformation_errors": transformation_errors,
            "duplicate_customer_ids": duplicate_ids,
            "mandatory_field_errors": mandatory_errors,
            "orphan_records": orphan_records,
        },
        "checks": checks,
        "execution_time_seconds": round(elapsed, 4),
        "overall_status": overall_status,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    run_validation()