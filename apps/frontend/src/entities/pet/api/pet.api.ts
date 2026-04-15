import { apiClient } from "@/shared/api/client";

export type Pet = {
    id: number;
    pet_name: string;
    pet_photo_object_key: string | null;
};

export async function getPets() {
    const response = await apiClient.get<Pet[]>("/pets", {
        params: {
            offset: 0,
            limit: 50,
        },
    });

    return response.data;
};