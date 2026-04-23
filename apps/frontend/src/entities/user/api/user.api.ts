import { apiClient } from "@/shared/api/client";

type UpdateUserPayload = {
    user_name: string,
    user_photo: string,
    user_email: string,
    user_phone_number: string,
    password: string,
}

type LinkTgPayload = {
    telegram_id: string,
}

export async function updateUser(payload: UpdateUserPayload) {
    const response = await apiClient.patch("/me/data", payload);
    return response.data;
}

export async function linkTelegram(user_id: number, payload: LinkTgPayload) {
    const response = await apiClient.post(`/link-telegram/${user_id}`, payload);
    return response.data;
}