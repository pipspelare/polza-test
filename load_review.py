from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import psycopg


PATH_SOURCE = Path(__file__).parent
PATH_REVIEW = PATH_SOURCE / "review.csv"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app:app@localhost:5432/companies",
)

EXPECTED_COLUMNS = [
    "id",
    "name",
    "category",
    "city",
    "address",
    "rating",
    "reviews_count",
    "site",
    "phone",
]


def load_review() -> None:
    if not PATH_REVIEW.exists():
        raise FileNotFoundError(PATH_REVIEW)

    rows: list[tuple[str | None, ...]] = []
    empty_rows = 0

    with PATH_REVIEW.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=",")

        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(
                f"Unexpected columns: {reader.fieldnames}"
            )

        for row_number, row in enumerate(reader, start=2):
            values = [row.get(column) for column in EXPECTED_COLUMNS]

            if all(
                value is None or not value.strip()
                for value in values
            ):
                empty_rows += 1
                continue

            rows.append(
                tuple(
                    value.strip() if value is not None else None
                    for value in values
                )
            )

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO review_companies (
                    id,
                    name,
                    category,
                    city,
                    address,
                    rating_raw,
                    reviews_count_raw,
                    site_raw,
                    phone
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                """,
                rows,
            )

        connection.commit()

    print(f"Loaded review rows: {len(rows)}")
    print(f"Skipped empty rows: {empty_rows}")


if __name__ == "__main__":
    try:
        load_review()
    except Exception as exc:
        print(f"Review load failed: {exc}", file=sys.stderr)
        raise
