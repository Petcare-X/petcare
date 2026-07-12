import { useMemo } from "react";

import { useDogBreedsQuery, usePetsQuery } from "@/entities/pet/model/pet.queries";
import type { Pet } from "@/entities/pet/model/pet.types";

export type ChatPetOption = {
    id: number;
    name: string;
    breed: string;
    photoObjectKey: string | null;
};

function mapPetToChatPetOption(pet: Pet, breedNameById: Map<number, string>): ChatPetOption {
    return {
        id: pet.id,
        name: pet.pet_name,
        breed:
            pet.animal_breed_name ??
            (pet.animal_breed_id ?
                breedNameById.get(pet.animal_breed_id) ?? "Порода не указана"
                : "Порода не указана"),
        photoObjectKey: pet.pet_photo_object_key,
    };
};

export function useChatPetOptions() {
    const petsQuery = usePetsQuery();
    const breedsQuery = useDogBreedsQuery();

    const pets = useMemo(() => {
        const breedNameById = new Map(
            (breedsQuery.data ?? []).map((breed) => [breed.id, breed.animal_breed]),
        );

        return (petsQuery.data ?? []).map((pet) =>
            mapPetToChatPetOption(pet, breedNameById),
        );
    }, [petsQuery.data, breedsQuery.data]);

    return {
        pets,
        isLoading: petsQuery.isLoading || breedsQuery.isLoading,
        isError: petsQuery.isError || breedsQuery.isError,
        error: petsQuery.error ?? breedsQuery.error,
    };
}