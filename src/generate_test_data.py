import random
import string
import time
from pathlib import Path

OUTPUT_FILE = Path("data/customers_1m.csv")
TOTAL_RECORDS = 1_000_000


FIRST_NAMES = [
    "Mauricio",
    "Laura",
    "Carlos",
    "Ana",
    "Jorge",
    "Maria",
    "Luis",
    "Sofia",
    "Diego",
    "Fernanda",
]

LAST_NAMES = [
    "Ramirez",
    "Garcia",
    "Martinez",
    "Lopez",
    "Hernandez",
    "Gonzalez",
    "Rodriguez",
    "Perez",
    "Sanchez",
    "Torres",
]


def random_email(first_name, last_name, customer_id):
    return (
        f"{first_name.lower()}."
        f"{last_name.lower()}."
        f"{customer_id}@example.com"
    )


def generate_data():
    start_time = time.perf_counter()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(
            "customer_id,first_name,last_name,email,status,created_at\n"
        )

        for customer_id in range(100001, 100001 + TOTAL_RECORDS):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)

            email = random_email(
                first_name,
                last_name,
                customer_id
            )

            status = random.choice(
                ["ACTIVE", "ACTIVE", "ACTIVE", "INACTIVE"]
            )

            created_at = "2026-01-01 00:00:00"

            file.write(
                f"{customer_id},"
                f"{first_name},"
                f"{last_name},"
                f"{email},"
                f"{status},"
                f"{created_at}\n"
            )

    elapsed = time.perf_counter() - start_time

    print("=== Synthetic Data Generator ===")
    print(f"Records generated: {TOTAL_RECORDS:,}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Generation time: {elapsed:.2f} seconds")


if __name__ == "__main__":
    generate_data()