export type Document = {
    id: number
    pet_id: number
    document_type_id: number
    document_type_name: string | null
    custom_name: string
    object_key: string
    content_type: string | null
    size_bytes: number | null
    etag: string | null
    uploaded_at: Date | null
}