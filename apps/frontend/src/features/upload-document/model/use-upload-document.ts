import { completePetDocumentUpload, createPetDocumentUploadUrl, uploadDocumentFile } from "@/entities/document/api/document.api";
import { useMutation, useQueryClient } from "@tanstack/react-query";

type UploadDocumentValues = {
    petId: number;
    file: File,
    documentTypeId: number;
    customName?: string;
}

export function useUploadDocument() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({
            petId,
            file,
            documentTypeId,
            customName,
        }: UploadDocumentValues) => {
            const uploadUrlResponse = await createPetDocumentUploadUrl(petId, {
                document_type_id: documentTypeId,
                content_type: file.type || "application/octet-stream",
                custom_name: customName?.trim() || undefined,
            });

            await uploadDocumentFile(uploadUrlResponse.upload_url, file);

            return completePetDocumentUpload(petId, {
                document_type_id: documentTypeId,
                object_key: uploadUrlResponse.object_key,
                custom_name: uploadUrlResponse.custom_name,
            });
        },

        onSuccess: (_createdDocument, variables) => {
            void queryClient.invalidateQueries({
                queryKey: ["documents", "list", variables.petId],
            });
        },
    });
}