import { useMutation, useQueryClient } from "@tanstack/react-query";

import { DEFAULT_ANIMAL_TYPE_ID } from "@/entities/pet/api/animal-reference.api";
import { createPet } from "@/entities/pet/api/pet.api";
import { uploadPetPhoto } from "@/entities/pet/api/pet-photo.api";
import { petQueryKeys } from "@/entities/pet/model/pet.queries";

export type CreatePetFormValues = {
    name: string;
    breedId: number;
    age: number;
    weight: number;
    sex: "male" | "female";
    isSterylized: boolean;
    healthNotes: string;
    photo: File | null;
};

export function useCreatePet() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (values: CreatePetFormValues) => {
            const pet = await createPet({
                pet_name: values.name,
                pet_date_of_birth: buildDateOfBirth(values.age),
                pet_sex: values.sex,
                animal_type_id: DEFAULT_ANIMAL_TYPE_ID,
                animal_breed_id: values.breedId,
                pedigree: false,
                pet_neck_girth: 20,
                pet_breast_girth: 30,
                pet_length: 40,
                pet_weight: values.weight,
                pet_is_sterylyzed: values.isSterylized,
                pet_special_notes: values.healthNotes.trim() || null,
            });

            if (!values.photo) {
                return pet;
            }

            return uploadPetPhoto(pet.id, values.photo);
        },
        onSuccess: () => {
            void queryClient.invalidateQueries({
                queryKey: petQueryKeys.all,
            });
        },
    });
}

function buildDateOfBirth(age: number): string {
    const today = new Date();
    const dateOfBirth = new Date(
        today.getFullYear() - age,
        today.getMonth(),
        today.getDate(),
    );

    return dateOfBirth.toISOString().slice(0, 10);
}
