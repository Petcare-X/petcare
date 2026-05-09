import { apiClient } from "@/shared/api/client";

import type { 
    PetDocument,
    DocumentType,
    PetDocumentCompletePayload, 
    PetDocumentUploadUrlPayload, 
    PetDocumentUploadUrlResponse, 
    PetDocumentDownloadUrlResponse
} from "../model/document.types";

export async function getPetDocuments(pet_id: number): Promise<PetDocument[]> {
    const response = await apiClient.get<PetDocument[]>(`/pets/${pet_id}/documents`)
    return response.data;
}

export async function getDocumentTypes(): Promise<DocumentType[]> {
    const response = await apiClient.get<DocumentType[]>("/document-types");
    return response.data;
}

export async function createPetDocumentUploadUrl(pet_id: number, payload: PetDocumentUploadUrlPayload): Promise<PetDocumentUploadUrlResponse> {
    const response = await apiClient.post<PetDocumentUploadUrlResponse>(`/pets/${pet_id}/documents/upload-url`, payload);
    return response.data;
}


export async function uploadDocumentFile(uploadUrl: string, file: File): Promise<void> {
    const response = await fetch(uploadUrl, {
        method: "PUT",
        headers: {
            "Content-Type": file.type || "application/octet-stream",
        },
        body: file,
    });

    if (!response.ok) {
        throw new Error("Failed to upload document file")
    }
}

export async function completePetDocumentUpload(pet_id: number, payload: PetDocumentCompletePayload): Promise<PetDocument> {
    const response = await apiClient.post<PetDocument>(`/pets/${pet_id}/documents/complete`, payload);
    return response.data;
}

export async function getPetDocumentDownloadUrl(petId: number, documentRowid: number): Promise<PetDocumentDownloadUrlResponse> {
    const response = await apiClient.get<PetDocumentDownloadUrlResponse>(
        `/pets/${petId}/documents/${documentRowid}/download-url`,
    );

    return response.data;
}