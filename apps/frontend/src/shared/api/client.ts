import axios from "axios";

import {
    clearAuthSession,
    getAccessToken,
    hasLoggedOutMarker,
    setAuthSession,
} from "@/shared/api/auth-session";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://пэткер.рф";

type AccessTokenResponse = {
    access_token: string;
    token_type: "bearer";
};

export const apiClient = axios.create({
    baseURL,
    withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
    const token = getAccessToken();

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        const requestUrl = originalRequest?.url ?? "";

        const isAuthRequest =
            requestUrl.includes("/auth/login") ||
            requestUrl.includes("/auth/refresh") ||
            requestUrl.includes("/auth/logout") ||
            requestUrl.includes("/auth/logout-all");


        if (
            !error.response ||
            !originalRequest ||
            error.response.status !== 401 ||
            originalRequest._retry ||
            isAuthRequest ||
            hasLoggedOutMarker()
        ) {
            return Promise.reject(error);
        }

        originalRequest._retry = true;

        try {
            const refreshResponse = await axios.post<AccessTokenResponse>(
                `${baseURL}/auth/refresh`,
                undefined,
                {
                    withCredentials: true,
                },
            );

            setAuthSession(refreshResponse.data);

            originalRequest.headers = originalRequest.headers ?? {};
            originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.access_token}`;

            return apiClient(originalRequest);
        } catch {
            clearAuthSession();
            return Promise.reject(error);
        }
    }
);