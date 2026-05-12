import { useQuery } from "@tanstack/react-query";

import { getDocumentTypes, getPetDocuments } from "@/entities/document/api/document.api";

const documentsQueryKeys = {
    all: ["documents"] as const,
    list: (petId: number) => [...documentsQueryKeys.all, "list", petId] as const,
    types: () => [...documentsQueryKeys.all, "types"] as const,
}

export function useDocumentTypesQuery() {
    return useQuery({
        queryKey: ["documents", "types"],
        queryFn: getDocumentTypes,
        staleTime: 5 * 60_000,
    });
}

export function usePetDocumentsQuery(petId: number, enabled: boolean = true) {
    return useQuery({
        queryKey: documentsQueryKeys.list(petId),
        queryFn: () => getPetDocuments(petId),
        enabled,
        staleTime: 60_000,
    });
}
