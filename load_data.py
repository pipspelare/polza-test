from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg


PATH_SOURCE = Path(__file__).parent
PATH_DATA = PATH_SOURCE / "data"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app:app@localhost:5432/companies",
)

INSERT_SQL = """
INSERT INTO companies (
    id,
    name,
    category,
    city,
    address,
    rating,
    reviews_count,
    site,
    phone
)
VALUES (
    %(id)s,
    %(name)s,
    %(category)s,
    %(city)s,
    %(address)s,
    %(rating)s,
    %(reviews_count)s,
    %(site)s,
    %(phone)s
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    category = EXCLUDED.category,
    city = EXCLUDED.city,
    address = EXCLUDED.address,
    rating = EXCLUDED.rating,
    reviews_count = EXCLUDED.reviews_count,
    site = EXCLUDED.site,
    phone = EXCLUDED.phone;
"""


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None

    result = str(value).strip()
    return result or None


def normalize_rating(value: Any) -> float | None:
    if value is None or value == "":
        return None

    return float(value)


def normalize_reviews_count(value: Any) -> int:
    if value is None or value == "":
        return 0

    return int(value)


def normalize_company(item: dict[str, Any]) -> dict[str, Any]:
    company_id = normalize_text(item.get("id"))

    if not company_id:
        raise ValueError("Company has no id")

    name = normalize_text(item.get("name"))
    category = normalize_text(item.get("category"))
    city = normalize_text(item.get("city"))

    if not name:
        raise ValueError(f"Company {company_id} has no name")

    if not category:
        raise ValueError(f"Company {company_id} has no category")

    if not city:
        raise ValueError(f"Company {company_id} has no city")

    return {
        "id": company_id,
        "name": name,
        "category": category,
        "city": city,
        "address": normalize_text(item.get("address")),
        "rating": normalize_rating(item.get("rating")),
        "reviews_count": normalize_reviews_count(
            item.get("reviews_count")
        ),
        "site": normalize_text(item.get("site")),
        "phone": normalize_text(item.get("phone")),
    }


def read_all_companies() -> list[dict[str, Any]]:
    """
    Читает все JSON-файлы из data и дедуплицирует записи по id.

    Если один и тот же id встречается несколько раз, последняя
    встретившаяся запись заменяет предыдущую.
    """
    companies_by_id: dict[str, dict[str, Any]] = {}

    json_files = sorted(PATH_DATA.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in {PATH_DATA}"
        )

    for file_path in json_files:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(file)

        items = payload.get("items")

        if not isinstance(items, list):
            raise ValueError(
                f"File {file_path} does not contain an items array"
            )

        for item in items:
            if not isinstance(item, dict):
                raise ValueError(
                    f"Invalid company record in {file_path}"
                )

            company = normalize_company(item)
            companies_by_id[company["id"]] = company

    return list(companies_by_id.values())


def load_companies(companies: list[dict[str, Any]]) -> None:
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            for company in companies:
                cursor.execute(INSERT_SQL, company)

        connection.commit()


def main() -> None:
    companies = read_all_companies()

    print(f"Unique records found: {len(companies)}")

    load_companies(companies)

    print("Data loaded successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Load failed: {exc}", file=sys.stderr)
        raise
