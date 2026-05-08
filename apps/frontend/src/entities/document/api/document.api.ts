import { apiClient } from "@/shared/api/client";

import type { Document, DocumentDownloadUrl } from "../model/document.types";

export async function getPetDocuments(petId: number): Promise<Document[]> {
    const response = await apiClient.get<Document[]>(`/pets/${petId}/documents`);
    return response.data;
}

export async function getPetDocumentDownloadUrl(
    petId: number,
    documentId: number,
): Promise<DocumentDownloadUrl> {
    const response = await apiClient.get<DocumentDownloadUrl>(
        `/pets/${petId}/documents/${documentId}/download-url`,
    );

    return response.data;
}
