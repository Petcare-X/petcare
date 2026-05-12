import { apiClient } from "@/shared/api/client";

import type { AnimalBreed } from "@/entities/pet/model/pet.types";

const DEFAULT_ANIMAL_TYPE_ID = 1;

export async function getDogBreeds(): Promise<AnimalBreed[]> {
    const response = await apiClient.get<AnimalBreed[]>(
        `/animal-types/${DEFAULT_ANIMAL_TYPE_ID}/breeds`,
    );

    return response.data;
}

export { DEFAULT_ANIMAL_TYPE_ID };