import { useQuery } from "@tanstack/react-query";

import { getDogBreeds } from "@/entities/pet/api/animal-reference.api";
import { getPets } from "@/entities/pet/api/pet.api";
import { getPetPhotoDownloadUrl } from "@/entities/pet/api/pet-photo.api";
import type { AnimalBreed, Pet, PetCardView } from "@/entities/pet/model/pet.types";

export const petQueryKeys = {
    all: ["pets"] as const,
    list: () => [...petQueryKeys.all, "list"] as const,
    breeds: () => [...petQueryKeys.all, "breeds"] as const,
    photo: (petId: number) => [...petQueryKeys.all, "photo", petId] as const,
};

export function usePetsQuery() {
    return useQuery({
        queryKey: petQueryKeys.list(),
        queryFn: getPets,
        staleTime: 60_000,
    });
};

export function useDogBreedsQuery() {
    return useQuery({
        queryKey: petQueryKeys.breeds(),
        queryFn: getDogBreeds,
        staleTime: 5 * 60_000,
    });
}

export function usePetPhotoQuery(petId: number, enabled: boolean) {
    return useQuery({
        queryKey: petQueryKeys.photo(petId),
        queryFn: () => getPetPhotoDownloadUrl(petId),
        enabled,
        staleTime: 10 * 60_000,
    });
}

export function mapPetToCardView(pet: Pet, breeds: AnimalBreed[]): PetCardView {
    const breed = breeds.find((item) => item.id === pet.animal_breed_id);

    return {
        id: pet.id,
        name: pet.pet_name,
        breed: breed?.animal_breed ?? "Порода не указана",
        age: formatPetAge(pet.pet_date_of_birth),
        weight: `${pet.pet_weight} кг`,
        photoObjectKey: pet.pet_photo_object_key,
    };
}

function formatPetAge(dateOfBirth: string): string {
    const birthDate = new Date(dateOfBirth);

    if (Number.isNaN(birthDate.getTime())) {
        return "Возраст не указан";
    }

    const today = new Date();
    let years = today.getFullYear() - birthDate.getFullYear();
    const hasBirthdayPassed =
        today.getMonth() > birthDate.getMonth() ||
        (today.getMonth() === birthDate.getMonth() && today.getDate() >= birthDate.getDate());

    if (!hasBirthdayPassed) {
        years -= 1;
    }

    if (years <= 0) {
        return "меньше года";
    }

    const lastDigit = years % 10;
    const lastTwoDigits = years % 100;

    if (lastDigit === 1 && lastTwoDigits !== 11) {
        return `${years} год`;
    }

    if ([2, 3, 4].includes(lastDigit) && ![12, 13, 14].includes(lastTwoDigits)) {
        return `${years} года`;
    }

    return `${years} лет`;
}
