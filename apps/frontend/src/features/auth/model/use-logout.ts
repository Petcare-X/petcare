import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";

import { logout } from "@/entities/auth/api/auth.api";
import { appRoutes } from "@/shared/constants/routes";
import { clearAuthSession, setLoggedOutMarker } from "@/shared/api/auth-session";


export function useLogout() {
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    return useMutation({
        mutationFn: logout,
        onSuccess: async () => {
            setLoggedOutMarker();
            clearAuthSession();
            queryClient.clear();

            await navigate({
                to: appRoutes.login,
            });
        },
        onError: async () => {
            setLoggedOutMarker();
            clearAuthSession();
            queryClient.clear();

            await navigate({
                to: appRoutes.login,
            });
        },
    });
}
