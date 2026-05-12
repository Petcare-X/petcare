import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updatePet, type UpdatePetPayload } from "@/entities/pet/api/pet.api";
import { petQueryKeys } from "@/entities/pet/model/pet.queries";

export type UpdatePetVariables = {
    petId: number;
    payload: UpdatePetPayload;
};

export function useUpdatePet() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ petId, payload }: UpdatePetVariables) => updatePet(petId, payload),
        onSuccess: () => {
            void queryClient.invalidateQueries({
                queryKey: petQueryKeys.list(),
            });
        },
    });
}