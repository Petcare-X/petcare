import { useMutation, useQueryClient } from "@tanstack/react-query";

import { uploadPetPhoto } from "@/entities/pet/api/pet-photo.api";
import { petQueryKeys } from "@/entities/pet/model/pet.queries";

export type UploadPetPhotoVariables = {
    petId: number;
    file: File;
};

export function useUploadPetPhoto() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ petId, file }: UploadPetPhotoVariables) =>
            uploadPetPhoto(petId, file),

        onSuccess: (_pet, variables) => {
            void queryClient.invalidateQueries({
                queryKey: petQueryKeys.list(),
            });

            void queryClient.invalidateQueries({
                queryKey: petQueryKeys.photo(variables.petId),
            });
        },
    });
}