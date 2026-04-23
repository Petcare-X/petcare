import { apiClient } from '@/shared/api/client';

type SignupPayload = {
    name: string,
    email: string,
    phone_number?: string,
    birth_date: string,
    password: string,
    photo_url?: string,
}

type LoginPayload = {
    email: string;
    password: string;
};

type AccessTokenResponse = {
    access_token: string;
    token_type: "bearer";
};

export async function signup(payload: SignupPayload) {
    const response = await apiClient.post<AccessTokenResponse>("/auth/signup", payload);
    return response.data;
}

export async function login(payload: LoginPayload) {
    const response = await apiClient.post<AccessTokenResponse>("/auth/login", payload);
    return response.data;
}

export async function refreshSession() {
    const response = await apiClient.post<AccessTokenResponse>("/auth/refresh");
    return response.data;
}

export async function logout() {
    await apiClient.post("/auth/logout");
}