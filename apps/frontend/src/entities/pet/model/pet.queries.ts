import { useQuery } from "@tanstack/react-query";
import { getPets } from "@/entities/pet/api/pet.api";

export const petQueryKeys = {
    all: ["pets"] as const,
    list: () => [...petQueryKeys.all, "list"] as const,
};

export function usePetsQuery() {
    return useQuery({
        queryKey: petQueryKeys.list(),
        queryFn: getPets,
        staleTime: 60_000,
    });
};