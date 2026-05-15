import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deletePetDocument } from "@/entities/document/api/document.api";


export function useDeleteDocument() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ petId, documentId }: { petId: number, documentId: number }) => 
            deletePetDocument(petId, documentId),
        onSuccess: (_data, variables) => {
            queryClient.invalidateQueries({
                queryKey: ["documents", "list", variables.petId],
            });
        },
    });
}