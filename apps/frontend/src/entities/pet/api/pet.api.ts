import { apiClient } from "@/shared/api/client";

type PetPayload = {
    id: number;
    pet_name: string;
    pet_photo_object_key: string | null;
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