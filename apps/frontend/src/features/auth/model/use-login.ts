import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";

import { login } from "@/entities/auth/api/auth.api";
import { setAuthSession } from "@/shared/api/auth-session";
import { petQueryKeys } from "@/entities/pet/model/pet.queries";
import { appRoutes } from "@/shared/constants/routes";

export function useLogin() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: login,
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
            console.error("login failed", error);
        },
    });
};
