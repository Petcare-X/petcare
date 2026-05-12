import { useQuery } from "@tanstack/react-query";

import { getPetDocuments } from "@/entities/document/api/document.api";

const documentsQueryKeys = {
    all: ["documents"] as const,
    list: () => [...documentsQueryKeys.all, "list"] as const,
}

export function useDocumentQueries() {
    return useQuery({
        queryKey: documentsQueryKeys.list(),
        queryFn: getPetDocuments,
        staleTime: 60_000,
    });
}