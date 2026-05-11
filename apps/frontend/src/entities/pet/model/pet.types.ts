export type Pet = {
    id: number;
    user_id: number | null;
    pet_name: string;
    pet_date_of_birth: string;
    pet_sex: string;
    animal_type_id: number;
    animal_breed_id?: number;
    animal_breed_name?: string;
    pedigree: boolean;
    pet_neck_girth: number;
    pet_breast_girth: number;
    pet_length: number;
    pet_weight: number;
    pet_is_sterylyzed: boolean | null;
    pet_photo_object_key: string | null;
    pet_photo_content_type: string | null;
    pet_photo_size_bytes: number | null;
    pet_photo_etag: string | null;
    pet_photo_uploaded_at: string | null;
    is_shared: boolean;
};

export type CreatePetPayload = {
    pet_name: string;
    pet_date_of_birth: string;
    pet_sex: string;
    animal_type_id: number;
    animal_breed_id?: number;
    animal_breed_name?: string;
    pedigree: boolean;
    pet_neck_girth: number;
    pet_breast_girth: number;
    pet_length: number;
    pet_weight: number;
    pet_is_sterylyzed: boolean | null;
    pet_special_notes?: string | null;
};

export type AnimalBreed = {
    id: number;
    animal_breed: string;
    animal_type_id: number;
};

export type PetCardView = {
    id: number;
    name: string;
    breed: string;
    age: string;
    weight: string;
    photoObjectKey: string | null;
};
