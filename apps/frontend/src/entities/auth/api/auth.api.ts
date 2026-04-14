import { apiClient } from '@/shared/api/client';

type LoginPayload = {
    email: string;
    password: string;
};

type AuthTokens = {
    access_token: string;
    refresh_token: string;
    token_type: "bearer";
};

export async function login(payload: LoginPayload) {
    const response = await apiClient.post<AuthTokens>("/auth/login", payload);
    return response.data;
};