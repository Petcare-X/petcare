import { apiClient } from "@/shared/api/client";

import type { Document } from "../model/document.types";

export async function getPetDocuments(): Promise<Document[]> {
    const response = await apiClient.get<Document[]>("/documents")
    return response.data;
}