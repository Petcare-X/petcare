import asyncio
import csv
import sys
from pathlib import Path

from sqlalchemy import select

from src.core.db import AsyncSessionLocal
from src.models import AnimalType


def normalize(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


async def import_animal_types(csv_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {"animal_name"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(
                "CSV must contain column: animal_name"
            )

        async with AsyncSessionLocal() as session:
            created_count = 0
            skipped_count = 0

            for row_number, row in enumerate(reader, start=2):
                animal_name = normalize(row.get("animal_name"))

                if not animal_name:
                    print(
                        f"Row {row_number}: skipped, empty animal_name"
                    )
                    skipped_count += 1
                    continue

                name_result = await session.execute(
                    select(AnimalType).where(
                        AnimalType.animal_name == animal_name
                    )
                )
                existing_name = name_result.scalar_one_or_none()

                if existing_name is not None:
                    print(
                        f"Row {row_number}: skipped, animal type already exists: "
                        f"{animal_name}"
                    )
                    skipped_count += 1
                    continue

                session.add(
                    AnimalType(
                        animal_name=animal_name,
                    )
                )
                created_count += 1

            await session.commit()

    print(f"Import finished. Created: {created_count}, skipped: {skipped_count}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python src/import/scripts/import_animals_types.py <path_to_csv>"
        )

    csv_path = Path(sys.argv[1])
    asyncio.run(import_animal_types(csv_path))


if __name__ == "__main__":
    main()