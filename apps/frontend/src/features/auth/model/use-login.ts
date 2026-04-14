import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";

import { login } from "@/entities/auth/api/auth.api";
import { setAuthSession } from "@/shared/api/auth-session";
import { petQueryKeys } from "@/entities/pet/model/pet.queries";

export function useLogin() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: login,
        onSuccess: async (tokens) => {
            setAuthSession(tokens);

            await queryClient.invalidateQueries({
                queryKey: petQueryKeys.all,
            });

            await navigate({to: "/"});
        },
    });
};