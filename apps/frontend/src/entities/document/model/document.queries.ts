import { useQuery } from "@tanstack/react-query";

import { getPetDocuments } from "@/entities/document/api/document.api";

const documentsQueryKeys = {
    all: ["documents"] as const,
    list: (petId?: number) => [...documentsQueryKeys.all, "list", petId] as const,
}

export function useDocumentQueries(petId?: number) {
    return useQuery({
        queryKey: documentsQueryKeys.list(petId),
        queryFn: () => getPetDocuments(petId ?? 0),
        enabled: Boolean(petId),
        staleTime: 60_000,
    });
}
