import { useMutation, useQueryClient } from "@tanstack/react-query";
import { acceptInvite } from "@/entities/invite/api/invite.api";
import { petQueryKeys } from "@/entities/pet/model/pet.queries";

export function useAcceptInvite() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: acceptInvite,
        onSuccess: () => {
            void queryClient.invalidateQueries({
                queryKey: petQueryKeys.all,
            });
        },
    });
}