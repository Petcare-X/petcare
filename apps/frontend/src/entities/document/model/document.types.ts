export type PetDocument = {
    id: number
    pet_id: number
    document_type_id: number
    document_type_name: string | null
    custom_name: string
    object_key: string
    content_type: string | null
    size_bytes: number | null
    etag: string | null
    uploaded_at: string | null
}

export type DocumentType = {
    id: number;
    document_name: string;
};

export type PetDocumentUploadUrlPayload = {
    document_type_id: number;
    content_type: string;
    custom_name?: string;
};

export type PetDocumentUploadUrlResponse = {
    custom_name: string;
    object_key: string;
    upload_url: string;
    expires_in: number;
};

export type PetDocumentCompletePayload = {
    document_type_id: number;
    object_key: string;
    custom_name?: string;
};

export type PetDocumentDownloadUrlResponse = {
    document_id: number;
    document_type_name?: string;
    custom_name: string;
    object_key: string;
    download_url: string;
    expires_in: number;
}