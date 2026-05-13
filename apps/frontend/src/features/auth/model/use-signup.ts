import { useNavigate } from "@tanstack/react-router";
import { useMutation } from "@tanstack/react-query";

import { signup } from "@/entities/auth/api/auth.api";
import { appRoutes } from "@/shared/constants/routes";

export function UseSignup() {
    const navigate = useNavigate();

    return useMutation({
        mutationFn: signup,
        onSuccess: async () => {
            await navigate({
                to: appRoutes.login,
            });
        },
        onError: (error) => {
            console.error("signup failed", error);
        },
    });
}