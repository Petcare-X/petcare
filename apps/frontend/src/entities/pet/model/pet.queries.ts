import { useQuery } from "@tanstack/react-query";

import { getDogBreeds } from "@/entities/pet/api/animal-reference.api";
import { getPets } from "@/entities/pet/api/pet.api";
import { getPetPhotoDownloadUrl } from "@/entities/pet/api/pet-photo.api";

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