import { apiClient } from "@/shared/api/client";

import { User } from "../model/user.types";

export async function getUser(): Promise<User> {
    const response = await apiClient.get<User>("/users/me");
    return response.data;
}

export async function deleteUser(): Promise<{ deleted: boolean }> {
    const response = await apiClient.delete<{ deleted: boolean }>("/users/me");
    return response.data;
}