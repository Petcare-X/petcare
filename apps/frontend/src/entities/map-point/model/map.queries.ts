import { useQuery } from "@tanstack/react-query";

import { getClinics, getFriendly, getGroomings } from "../api/map.api";

const MapQueryKeys = {
    all: ["map"] as const,
    clinics: () => [...MapQueryKeys.all, "clinics"] as const,
    friendly: () => [...MapQueryKeys.all, "friendly"] as const,
    groomings: () => [...MapQueryKeys.all, "groomings"] as const,
}

export function useClinicsQuery() {
    return useQuery({
        queryKey: MapQueryKeys.clinics(),
        queryFn: getClinics,
        staleTime: 60_000 * 60 * 24,
    });
}

export function useFriendlyQuery() {
    return useQuery({
        queryKey: MapQueryKeys.friendly(),
        queryFn: getFriendly,
        staleTime: 60_000 * 60 * 24,
    });
}

export function useGroomingsQuery() {
    return useQuery({
        queryKey: MapQueryKeys.groomings(),
        queryFn: getGroomings,
        staleTime: 60_000 * 60 * 24,
    });
}