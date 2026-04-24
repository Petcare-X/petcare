import { redirect } from "@tanstack/react-router";
import { getAccessToken } from "@/shared/api/auth-session";

export function requireAuth() {
    const token = getAccessToken();

    if(!token) {
        throw redirect({
            to: "/auth/login",
        });
    };
};