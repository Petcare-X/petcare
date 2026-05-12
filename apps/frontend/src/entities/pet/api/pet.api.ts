import { apiClient } from "@/shared/api/client";

import type { CreatePetPayload, Pet } from "@/entities/pet/model/pet.types";

export async function getPets(): Promise<Pet[]> {
    const response = await apiClient.get<Pet[]>("/pets", {
        params: {
            offset: 0,
            limit: 50,
        },
    });

    return response.data;
};

export async function createPet(payload: CreatePetPayload): Promise<Pet> {
    const response = await apiClient.post<Pet>("/pets", payload);

    return response.data;
}
