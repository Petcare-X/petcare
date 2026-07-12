import { apiClient } from "@/shared/api/client";

import type { AnimalBreed } from "@/entities/pet/model/pet.types";

const DEFAULT_ANIMAL_TYPE_ID = 1;

export async function getDogBreeds(): Promise<AnimalBreed[]> {
    const response = await apiClient.get<AnimalBreed[]>(
        `/admin/animal-types/${DEFAULT_ANIMAL_TYPE_ID}/breeds`,
    );

    return response.data.slice().sort(compareBreedsByName);
}

function compareBreedsByName(first: AnimalBreed, second: AnimalBreed): number {
    const nameComparison = first.animal_breed.trim().localeCompare(
        second.animal_breed.trim(),
        "ru",
        { sensitivity: "base" },
    );

    return nameComparison || first.id - second.id;
}

export { DEFAULT_ANIMAL_TYPE_ID };
