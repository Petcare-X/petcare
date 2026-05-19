import { useQuery } from "@tanstack/react-query";

import { getDogBreeds } from "@/entities/pet/api/animal-reference.api";
import { getPets } from "@/entities/pet/api/pet.api";
import { getPetPhotoDownloadUrl } from "@/entities/pet/api/pet-photo.api";

export const petQueryKeys = {
    all: ["pets"] as const,
    list: () => [...petQueryKeys.all, "list"] as const,
    breeds: () => [...petQueryKeys.all, "breeds"] as const,
    photo: (petId: number, objectKey?: string | null) =>
        [...petQueryKeys.all, "photo", petId, objectKey ?? "none"] as const,
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

export function usePetPhotoQuery(petId: number, objectKey?: string | null) {
    return useQuery({
        queryKey: petQueryKeys.photo(petId, objectKey),
        queryFn: () => getPetPhotoDownloadUrl(petId),
        enabled: petId > 0 && Boolean(objectKey),
        staleTime: 10 * 60_000,
    });
}
