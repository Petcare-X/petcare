import { apiClient } from "@/shared/api/client";

type PetPayload = {
    id: number;
    pet_name: string;
    pet_photo_object_key: string | null;
};

type CreatePetPayload = {
    pet_name: string;
    pet_date_of_birth: string;
    animal_type_id: number;
    animal_breed_id: number;
    pedigree: boolean;
    pet_neck_girth: number | null;
    pet_breast_girth: number | null;
    pet_length: number | null;
    pet_weight: number;
    pet_is_sterylyzed: boolean | null;
    pet_photo_object_key: string | null;
};

type UpdatePetPayload = {
    pet_date_of_birth: string;
    animal_type_id: number;
    animal_breed_id: number | null;
    pedigree: boolean;
    pet_neck_girth: number | null;
    pet_breast_girth: number | null;
    pet_length: number | null;
    pet_weight: number;
    pet_is_sterylyzed: boolean | null;
    pet_photo_object_key: string | null;
}

export async function createPet(payload: CreatePetPayload) {
    const response = await apiClient.post("/pets", payload);
    return response.data;
};

export async function getPets() {
    const response = await apiClient.get<PetPayload[]>("/pets", {
        params: {
            offset: 0,
            limit: 50,
        },
    });

    return response.data;
};

export async function updatePet(pet_id: number, payload: UpdatePetPayload) {
    const response = await apiClient.put(`/pets/${pet_id}`, payload);
    return response.data;
}