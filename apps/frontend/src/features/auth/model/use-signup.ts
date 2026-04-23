import { useNavigate } from "@tanstack/react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { signup } from "@/entities/auth/api/auth.api";
import { appRoutes } from "@/shared/constants/routes";
import { clearAuthSession, setAuthSession } from "@/shared/api/auth-session";
import { petQueryKeys } from "@/entities/pet/model/pet.queries";

export function UseSignup() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: signup,
        onSuccess: async (tokens) => {
            setAuthSession(tokens);

            await navigate({
                to: appRoutes.home,
            });

            void queryClient.invalidateQueries({
                queryKey: petQueryKeys.all,
            });
        },
        onError: (error) => {
            clearAuthSession();
            queryClient.clear();
            
            console.error("signup failed", error);
        },
    });
}