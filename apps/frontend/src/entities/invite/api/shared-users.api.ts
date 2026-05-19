import { apiClient } from "@/shared/api/client";

export type sharedUsers = {
    pet_id: number;
    pet_name: string;
    shared_with_user_id: number;
    shared_with_user_name: string;
    shared_till: string | null;
}

export async function getSharedUsers(petId: number) {
    const response =  await apiClient.get<sharedUsers[]>(`/shared-users/${petId}`);
    return response.data;
}