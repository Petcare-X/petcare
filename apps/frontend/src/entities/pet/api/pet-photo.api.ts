import { apiClient } from "@/shared/api/client";

import type { Pet } from "@/entities/pet/model/pet.types";

type PetPhotoDownloadUrlResponse = {
    object_key: string;
    download_url: string;
    expires_in: number;
};

export async function uploadPetPhoto(petId: number, file: File): Promise<Pet> {
    const formData = new FormData();
    formData.append("file", file);

    const completeResponse = await apiClient.post<Pet>(
        `/pets/${petId}/photo`,
        formData,
    );

    return completeResponse.data;
}

export async function getPetPhotoDownloadUrl(petId: number): Promise<string> {
    const response = await apiClient.get<PetPhotoDownloadUrlResponse>(
        `/pets/${petId}/photo/download-url`,
    );

    return response.data.download_url;
}
