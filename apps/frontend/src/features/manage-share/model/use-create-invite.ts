import { useMutation } from "@tanstack/react-query";
import { createInvite } from "@/entities/invite/api/invite.api";

export function useCreateInvite() {
    return useMutation({
        mutationFn: createInvite,
    });
}
