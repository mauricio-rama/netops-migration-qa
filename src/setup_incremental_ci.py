import os

from src.validate_incremental import setup_incremental_scenario
import psycopg


def main():
    conn = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "netops_qa"),
        user=os.getenv("DB_USER", "netops_admin"),
        password=os.getenv("DB_PASSWORD", "netops_password"),
    )

    try:
        setup_incremental_scenario(conn)
        print("Incremental scenario initialized successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
