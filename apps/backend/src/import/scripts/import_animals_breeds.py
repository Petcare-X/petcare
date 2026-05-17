import asyncio
import csv
import sys
from pathlib import Path

from sqlalchemy import select

from src.core.db import AsyncSessionLocal
from src.models import AnimalBreed, AnimalType


def normalize(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


async def import_animal_breeds(csv_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {"animal_type_id", "animal_breed"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(
                "CSV must contain columns: animal_type_id, animal_breed"
            )

        async with AsyncSessionLocal() as session:
            created_count = 0
            skipped_count = 0

            for row_number, row in enumerate(reader, start=2):
                animal_type_id = normalize(row.get("animal_type_id"))
                animal_breed_name = normalize(row.get("animal_breed"))

                if not animal_type_id or not animal_breed_name:
                    print(
                        f"Row {row_number}: skipped, empty animal_type_id or animal_breed"
                    )
                    skipped_count += 1
                    continue

                type_result = await session.execute(
                    select(AnimalType).where(
                        AnimalType.id == int(animal_type_id)))
                
                existing_type = type_result.scalar_one_or_none()

                breed_result = await session.execute(
                    select(AnimalBreed).where(
                        AnimalBreed.animal_type_id == int(animal_type_id),
                        AnimalBreed.animal_breed == animal_breed_name,
                    )
                )
                existing_breed = breed_result.scalar_one_or_none()

                if existing_breed is not None:
                    print(
                        f"Row {row_number}: skipped, breed already exists: "
                        f"{animal_type_id} / {animal_breed_name}")
                    
                    skipped_count += 1
                    continue
                elif existing_type is None:
                    print(
                        f"Row {row_number}: skipped, animal type does not exist: "
                        f"{animal_type_id}")
                    skipped_count += 1
                    continue

                session.add(
                    AnimalBreed(
                        animal_breed=animal_breed_name,
                        animal_type_id=int(animal_type_id),
                    )
                )
                created_count += 1

            await session.commit()

    print(f"Import finished. Created: {created_count}, skipped: {skipped_count}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python src/import/scripts/import_animals_breeds.py <path_to_csv>"
        )

    csv_path = Path(sys.argv[1])
    asyncio.run(import_animal_breeds(csv_path))


if __name__ == "__main__":
    main()