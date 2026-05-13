import { apiClient } from "@/shared/api/client";

import type { CreatePetPayload, Pet } from "@/entities/pet/model/pet.types";

export type UpdatePetPayload = Partial<CreatePetPayload>;

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

export async function updatePet(petId: number, payload: UpdatePetPayload): Promise<Pet> {
    const response = await apiClient.patch<Pet>(`/pets/${petId}`, payload);

    return response.data;
}