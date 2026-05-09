import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";

import { deleteUser } from "@/entities/user/api/user.api";
import { clearAuthSession, setLoggedOutMarker } from "@/shared/api/auth-session";
import { appRoutes } from "@/shared/constants/routes";

export function useDeleteAccount() {
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    return useMutation({
        mutationFn: deleteUser,
        onSuccess: async () => {
            setLoggedOutMarker();
            clearAuthSession();
            queryClient.clear();

            await navigate({
                to: appRoutes.login,
            });
        },
    });
}