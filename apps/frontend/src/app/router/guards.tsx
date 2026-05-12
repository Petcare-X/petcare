import { redirect } from "@tanstack/react-router";

import { getAuthStatus } from "@/shared/api/auth-session";
import { appRoutes } from "@/shared/constants/routes";


export function ensureAuth() {
    const authStatus = getAuthStatus();

    if (authStatus !== "authenticated") {
        throw redirect({
        to: appRoutes.login,
        });
    }
}

export function redirectIfAuthenticated() {
    const authStatus = getAuthStatus();

    if (authStatus === "authenticated") {
        throw redirect({
        to: appRoutes.home,
        });
    }
}