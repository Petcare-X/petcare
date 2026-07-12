import { useMutation, useQueryClient } from "@tanstack/react-query";

import { uploadPetPhoto } from "@/entities/pet/api/pet-photo.api";
import { petQueryKeys } from "@/entities/pet/model/pet.queries";
import type { Pet } from "@/entities/pet/model/pet.types";

export type UploadPetPhotoVariables = {
    petId: number;
    file: File;
};

export function useUploadPetPhoto() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ petId, file }: UploadPetPhotoVariables) =>
            uploadPetPhoto(petId, file),

        onSuccess: (pet, variables) => {
            queryClient.setQueryData<Pet[]>(petQueryKeys.list(), (pets) => {
                if (!pets) {
                    return pets;
                }

                return pets.map((item) => item.id === pet.id ? pet : item);
            });

            void queryClient.invalidateQueries({
                queryKey: petQueryKeys.list(),
            });

            void queryClient.removeQueries({
                queryKey: [...petQueryKeys.all, "photo", variables.petId],
            });
        },
    });
}
