import { useNavigate } from "@tanstack/react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { signup } from "@/entities/auth/api/auth.api";
import { appRoutes } from "@/shared/constants/routes";
import { clearAuthSession } from "@/shared/api/auth-session";

export function UseSignup() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: signup,
        onSuccess: async () => {
            await navigate({
                to: appRoutes.login,
            });
        },
        onError: (error) => {
            clearAuthSession();
            queryClient.clear();
            
            console.error("signup failed", error);
        },
    });
}